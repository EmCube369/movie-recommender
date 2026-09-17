from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd
import torch
from torch import nn

from recommender.artifact_loader import ArtifactLoader


# ============================================================
# MATRIX FACTORIZATION MODEL
# ============================================================


class MatrixFactorization(nn.Module):
    """
    Matrix factorization model used by the trained collaborative
    filtering checkpoint.

    Prediction:

        global_mean
        + user_bias
        + movie_bias
        + dot(user_embedding, movie_embedding)
    """

    def __init__(
        self,
        num_users: int,
        num_movies: int,
        embedding_dim: int,
        global_mean: float,
    ) -> None:
        super().__init__()

        self.user_embedding = nn.Embedding(
            num_users,
            embedding_dim,
        )

        self.movie_embedding = nn.Embedding(
            num_movies,
            embedding_dim,
        )

        self.user_bias = nn.Embedding(
            num_users,
            1,
        )

        self.movie_bias = nn.Embedding(
            num_movies,
            1,
        )

        # Stored in state_dict, matching the trained checkpoint
        self.register_buffer(
            "global_mean",
            torch.tensor(
                global_mean,
                dtype=torch.float32,
            ),
        )

    def forward(
        self,
        user_indexes: torch.Tensor,
        movie_indexes: torch.Tensor,
    ) -> torch.Tensor:

        user_vectors = self.user_embedding(
            user_indexes
        )

        movie_vectors = self.movie_embedding(
            movie_indexes
        )

        interaction = (
            user_vectors * movie_vectors
        ).sum(dim=1)

        user_bias = (
            self.user_bias(user_indexes)
            .squeeze(-1)
        )

        movie_bias = (
            self.movie_bias(movie_indexes)
            .squeeze(-1)
        )

        predictions = (
            self.global_mean
            + user_bias
            + movie_bias
            + interaction
        )

        return predictions


# ============================================================
# COLLABORATIVE RECOMMENDER
# ============================================================


class CollaborativeRecommender:
    """
    Runtime wrapper around the trained collaborative filtering
    matrix-factorization model.
    """

    MIN_RATING = 0.5
    MAX_RATING = 5.0
    NEW_USER_REGULARIZATION = 5.0

    def __init__(
        self,
        loader: ArtifactLoader | None = None,
        device: str | torch.device | None = None,
    ) -> None:

        self.loader = (
            loader
            if loader is not None
            else ArtifactLoader()
        )

        self.device = self._resolve_device(
            device
        )

        self.model = self._load_model()

    # ========================================================
    # DEVICE
    # ========================================================

    @staticmethod
    def _resolve_device(
        device: str | torch.device | None,
    ) -> torch.device:

        if device is None:
            return torch.device(
                "cuda"
                if torch.cuda.is_available()
                else "cpu"
            )

        resolved = torch.device(device)

        if (
            resolved.type == "cuda"
            and not torch.cuda.is_available()
        ):
            raise RuntimeError(
                "CUDA was requested but is not available."
            )

        return resolved

    # ========================================================
    # MODEL LOADING
    # ========================================================

    def _load_model(
        self,
    ) -> MatrixFactorization:

        checkpoint = (
            self.loader.load_cf_checkpoint(
                self.device
            )
        )

        required_keys = {
            "model_state_dict",
            "num_users",
            "num_movies",
            "embedding_dim",
            "global_mean",
        }

        missing = (
            required_keys
            - set(checkpoint.keys())
        )

        if missing:
            raise ValueError(
                "CF checkpoint is missing keys: "
                f"{sorted(missing)}"
            )

        num_users = int(
            checkpoint["num_users"]
        )

        num_movies = int(
            checkpoint["num_movies"]
        )

        embedding_dim = int(
            checkpoint["embedding_dim"]
        )

        global_mean = float(
            checkpoint["global_mean"]
        )

        # ----------------------------------------------------
        # Validate checkpoint against current mappings
        # ----------------------------------------------------

        if (
            num_users
            != len(self.loader.cf_user_mapping)
        ):
            raise ValueError(
                "CF checkpoint user count does not "
                "match current user mapping."
            )

        if (
            num_movies
            != len(self.loader.cf_movie_mapping)
        ):
            raise ValueError(
                "CF checkpoint movie count does not "
                "match current movie mapping."
            )

        # ----------------------------------------------------
        # Construct exact architecture
        # ----------------------------------------------------

        model = MatrixFactorization(
            num_users=num_users,
            num_movies=num_movies,
            embedding_dim=embedding_dim,
            global_mean=global_mean,
        )

        model.load_state_dict(
            checkpoint["model_state_dict"],
            strict=True,
        )

        model.to(self.device)
        model.eval()

        self.num_users = num_users
        self.num_movies = num_movies
        self.embedding_dim = embedding_dim
        self.global_mean = global_mean

        self.validation_rmse = (
            checkpoint.get(
                "validation_rmse"
            )
        )

        self.best_epoch = (
            checkpoint.get("epoch")
        )

        return model

    # ========================================================
    # USER CHECKS
    # ========================================================

    def has_user(
        self,
        user_id: int,
    ) -> bool:

        return (
            int(user_id)
            in self.loader.user_id_to_index
        )

    def get_user_index(
        self,
        user_id: int,
    ) -> int:

        user_id = int(user_id)

        try:
            return self.loader.user_id_to_index[
                user_id
            ]

        except KeyError as exc:

            raise KeyError(
                f"Unknown CF userId: {user_id}"
            ) from exc

    # ========================================================
    # MOVIE CHECKS
    # ========================================================

    def has_movie(
        self,
        movie_id: int,
    ) -> bool:

        return (
            int(movie_id)
            in self.loader.movie_id_to_cf_index
        )
    
    def is_recommendation_supported_movie(
        self,
        movie_id: int,
    ) -> bool:

        return (
            int(movie_id)
            in self.loader.cf_supported_movie_ids
        )

    def get_movie_index(
        self,
        movie_id: int,
    ) -> int:

        movie_id = int(movie_id)

        try:
            return (
                self.loader.movie_id_to_cf_index[
                    movie_id
                ]
            )

        except KeyError as exc:

            raise KeyError(
                f"Unknown CF movieId: {movie_id}"
            ) from exc

    # ========================================================
    # NEW USER PREDICTION
    # ========================================================

    def infer_new_user_profile(
        self,
        ratings: Iterable[tuple[int, float]],
        regularization: float = NEW_USER_REGULARIZATION,
    ) -> tuple[np.ndarray, float, np.ndarray]:
        """
        Estimate a temporary CF user vector and user bias from
        explicitly supplied movie ratings.

        The trained model itself is not modified.

        Returns:
            user_vector
            user_bias
            supported_rated_movie_ids
        """

        if regularization <= 0:
            raise ValueError(
                "regularization must be greater than 0."
            )

        normalized_ratings = []
        seen_movie_ids = set()

        for movie_id, rating in ratings:

            movie_id = int(movie_id)
            rating = float(rating)

            if movie_id in seen_movie_ids:
                raise ValueError(
                    f"Duplicate movieId in ratings: {movie_id}"
                )

            seen_movie_ids.add(movie_id)

            if (
                rating < self.MIN_RATING
                or rating > self.MAX_RATING
            ):
                raise ValueError(
                    f"Rating for movieId {movie_id} must be "
                    f"between {self.MIN_RATING} and "
                    f"{self.MAX_RATING}."
                )

            movie_index = (
                self.loader.movie_id_to_cf_index.get(
                    movie_id
                )
            )

            # A movie may exist in the content catalog but not in
            # the trained collaborative-filtering model.
            if movie_index is None:
                continue

            normalized_ratings.append(
                (
                    movie_id,
                    int(movie_index),
                    rating,
                )
            )

        if not normalized_ratings:
            raise ValueError(
                "None of the supplied rated movies are supported "
                "by the collaborative-filtering model."
            )

        movie_ids = np.asarray(
            [
                movie_id
                for movie_id, _, _
                in normalized_ratings
            ],
            dtype=np.int64,
        )

        movie_indexes = np.asarray(
            [
                movie_index
                for _, movie_index, _
                in normalized_ratings
            ],
            dtype=np.int64,
        )

        rating_values = np.asarray(
            [
                rating
                for _, _, rating
                in normalized_ratings
            ],
            dtype=np.float64,
        )

        # --------------------------------------------------------
        # Read the already-trained movie factors
        # --------------------------------------------------------

        movie_index_tensor = torch.as_tensor(
            movie_indexes,
            dtype=torch.long,
            device=self.device,
        )

        with torch.inference_mode():

            movie_vectors = (
                self.model
                .movie_embedding(
                    movie_index_tensor
                )
                .detach()
                .cpu()
                .numpy()
                .astype(np.float64)
            )

            movie_biases = (
                self.model
                .movie_bias(
                    movie_index_tensor
                )
                .squeeze(-1)
                .detach()
                .cpu()
                .numpy()
                .astype(np.float64)
            )

        # --------------------------------------------------------
        # rating - global_mean - movie_bias
        #
        # should approximately equal:
        #
        # user_bias + user_vector dot movie_vector
        # --------------------------------------------------------

        target = (
            rating_values
            - float(self.global_mean)
            - movie_biases
        )

        # Add one final column for the temporary user bias.
        design_matrix = np.column_stack(
            [
                movie_vectors,
                np.ones(
                    len(movie_vectors),
                    dtype=np.float64,
                ),
            ]
        )

        # --------------------------------------------------------
        # Ridge regression:
        #
        # (X^T X + lambda I)^-1 X^T y
        # --------------------------------------------------------

        identity = np.eye(
            design_matrix.shape[1],
            dtype=np.float64,
        )

        parameters = np.linalg.solve(
            (
                design_matrix.T
                @ design_matrix
            )
            + regularization * identity,
            design_matrix.T @ target,
        )

        user_vector = (
            parameters[:-1]
            .astype(np.float32)
        )

        user_bias = float(
            parameters[-1]
        )

        return (
            user_vector,
            user_bias,
            movie_ids,
        )

    # ========================================================
    # LOW-LEVEL PREDICTION
    # ========================================================

    @torch.inference_mode()
    def predict_indexes(
        self,
        user_index: int,
        movie_indexes: np.ndarray | Iterable[int],
        clamp: bool = True,
    ) -> np.ndarray:
        """
        Predict ratings for one user across multiple CF movie
        indexes.
        """

        movie_indexes = np.asarray(
            list(movie_indexes)
            if not isinstance(
                movie_indexes,
                np.ndarray,
            )
            else movie_indexes,
            dtype=np.int64,
        )

        if movie_indexes.ndim != 1:
            raise ValueError(
                "movie_indexes must be a 1D array."
            )

        if len(movie_indexes) == 0:
            return np.empty(
                0,
                dtype=np.float32,
            )

        if (
            movie_indexes.min() < 0
            or movie_indexes.max()
            >= self.num_movies
        ):
            raise ValueError(
                "One or more CF movie indexes "
                "are out of range."
            )

        if (
            user_index < 0
            or user_index >= self.num_users
        ):
            raise ValueError(
                f"CF user index out of range: "
                f"{user_index}"
            )

        movie_tensor = torch.as_tensor(
            movie_indexes,
            dtype=torch.long,
            device=self.device,
        )

        user_tensor = torch.full(
            size=(len(movie_indexes),),
            fill_value=int(user_index),
            dtype=torch.long,
            device=self.device,
        )

        predictions = self.model(
            user_tensor,
            movie_tensor,
        )

        if clamp:
            predictions = torch.clamp(
                predictions,
                min=self.MIN_RATING,
                max=self.MAX_RATING,
            )

        return (
            predictions
            .detach()
            .cpu()
            .numpy()
            .astype(np.float32)
        )
    

    @torch.inference_mode()
    def predict_new_user_indexes(
        self,
        user_vector: np.ndarray,
        user_bias: float,
        movie_indexes: np.ndarray | Iterable[int],
        clamp: bool = True,
    ) -> np.ndarray:
        """
        Predict ratings for a temporary website-user profile.
        """

        movie_indexes = np.asarray(
            list(movie_indexes)
            if not isinstance(
                movie_indexes,
                np.ndarray,
            )
            else movie_indexes,
            dtype=np.int64,
        )

        if movie_indexes.ndim != 1:
            raise ValueError(
                "movie_indexes must be a 1D array."
            )

        if len(movie_indexes) == 0:
            return np.empty(
                0,
                dtype=np.float32,
            )

        if (
            movie_indexes.min() < 0
            or movie_indexes.max() >= self.num_movies
        ):
            raise ValueError(
                "One or more CF movie indexes are out of range."
            )

        user_vector = np.asarray(
            user_vector,
            dtype=np.float32,
        )

        if user_vector.shape != (
            self.embedding_dim,
        ):
            raise ValueError(
                "Temporary user vector has incorrect shape."
            )

        movie_tensor = torch.as_tensor(
            movie_indexes,
            dtype=torch.long,
            device=self.device,
        )

        user_vector_tensor = torch.as_tensor(
            user_vector,
            dtype=torch.float32,
            device=self.device,
        )

        movie_vectors = self.model.movie_embedding(
            movie_tensor
        )

        movie_biases = (
            self.model.movie_bias(
                movie_tensor
            )
            .squeeze(-1)
        )

        predictions = (
            self.model.global_mean
            + float(user_bias)
            + movie_biases
            + (
                movie_vectors
                * user_vector_tensor
            ).sum(dim=1)
        )

        if clamp:
            predictions = torch.clamp(
                predictions,
                min=self.MIN_RATING,
                max=self.MAX_RATING,
            )

        return (
            predictions
            .detach()
            .cpu()
            .numpy()
            .astype(np.float32)
        )

    # ========================================================
    # MOVIE-ID PREDICTION
    # ========================================================

    def predict_movies(
        self,
        user_id: int,
        movie_ids: Iterable[int],
    ) -> pd.DataFrame:
        """
        Predict CF scores for explicitly supplied MovieLens
        movieIds.

        Movies not present in the CF mapping are ignored.
        """

        user_index = self.get_user_index(
            user_id
        )

        valid_movie_ids = []
        movie_indexes = []

        for movie_id in movie_ids:

            movie_id = int(movie_id)

            movie_index = (
                self.loader.movie_id_to_cf_index.get(
                    movie_id
                )
            )

            if movie_index is None:
                continue

            valid_movie_ids.append(
                movie_id
            )

            movie_indexes.append(
                movie_index
            )

        if not movie_indexes:

            return pd.DataFrame(
                columns=[
                    "movieId",
                    "movieIndex",
                    "cf_score",
                ]
            )

        predictions = self.predict_indexes(
            user_index=user_index,
            movie_indexes=np.asarray(
                movie_indexes,
                dtype=np.int64,
            ),
        )

        return pd.DataFrame(
            {
                "movieId": valid_movie_ids,
                "movieIndex": movie_indexes,
                "cf_score": predictions,
            }
        )

    # ========================================================
    # ALL SUPPORTED CANDIDATES
    # ========================================================

    def score_candidates(
        self,
        user_id: int,
        exclude_movie_ids: Iterable[int] | None = None,
    ) -> pd.DataFrame:
        """
        Score all movies supported by the trained CF model.

        Uses cf_seen_movie_indexes.npy so cold-start/unseen
        movie indexes are not treated as valid CF candidates.
        """

        user_index = self.get_user_index(
            user_id
        )

        candidate_indexes = (
            self.loader
            .cf_seen_movie_indexes
            .astype(
                np.int64,
                copy=False,
            )
        )

        # ----------------------------------------------------
        # Optional exclusion
        # ----------------------------------------------------

        if exclude_movie_ids is not None:

            excluded_indexes = {
                self.loader
                .movie_id_to_cf_index[
                    int(movie_id)
                ]

                for movie_id
                in exclude_movie_ids

                if int(movie_id)
                in self.loader.movie_id_to_cf_index
            }

            if excluded_indexes:

                exclusion_array = np.fromiter(
                    excluded_indexes,
                    dtype=np.int64,
                )

                keep_mask = ~np.isin(
                    candidate_indexes,
                    exclusion_array,
                )

                candidate_indexes = (
                    candidate_indexes[
                        keep_mask
                    ]
                )

        # ----------------------------------------------------
        # Predict
        # ----------------------------------------------------

        predictions = self.predict_indexes(
            user_index=user_index,
            movie_indexes=candidate_indexes,
        )

        # ----------------------------------------------------
        # Convert indexes back to movieIds
        # ----------------------------------------------------

        movie_ids = np.fromiter(
            (
                self.loader
                .cf_index_to_movie_id[
                    int(index)
                ]

                for index
                in candidate_indexes
            ),
            dtype=np.int64,
            count=len(candidate_indexes),
        )

        return pd.DataFrame(
            {
                "movieId": movie_ids,
                "movieIndex": candidate_indexes,
                "cf_score": predictions,
            }
        )


    def score_new_user_candidates(
        self,
        ratings: Iterable[tuple[int, float]],
    ) -> pd.DataFrame:
        """
        Score all CF-supported candidate movies for a website user
        whose profile is supplied as explicit ratings.
        """

        ratings = list(ratings)

        if not ratings:
            raise ValueError(
                "At least one rating is required."
            )

        (
            user_vector,
            user_bias,
            supported_rated_movie_ids,
        ) = self.infer_new_user_profile(
            ratings
        )

        candidate_indexes = (
            self.loader
            .cf_seen_movie_indexes
            .astype(
                np.int64,
                copy=False,
            )
        )

        # --------------------------------------------------------
        # Exclude every movie rated by the website user, not just
        # the ones used for the temporary CF profile.
        # --------------------------------------------------------

        all_rated_movie_ids = {
            int(movie_id)
            for movie_id, _
            in ratings
        }

        excluded_indexes = {
            self.loader.movie_id_to_cf_index[
                movie_id
            ]
            for movie_id
            in all_rated_movie_ids
            if movie_id
            in self.loader.movie_id_to_cf_index
        }

        if excluded_indexes:

            exclusion_array = np.fromiter(
                excluded_indexes,
                dtype=np.int64,
            )

            keep_mask = ~np.isin(
                candidate_indexes,
                exclusion_array,
            )

            candidate_indexes = (
                candidate_indexes[
                    keep_mask
                ]
            )

        predictions = (
            self.predict_new_user_indexes(
                user_vector=user_vector,
                user_bias=user_bias,
                movie_indexes=candidate_indexes,
            )
        )

        movie_ids = np.fromiter(
            (
                self.loader
                .cf_index_to_movie_id[
                    int(index)
                ]
                for index
                in candidate_indexes
            ),
            dtype=np.int64,
            count=len(candidate_indexes),
        )

        return pd.DataFrame(
            {
                "movieId": movie_ids,
                "movieIndex": candidate_indexes,
                "cf_score": predictions,
            }
        )

        # ----------------------------------------------------
        # Optional exclusion
        # ----------------------------------------------------

        if exclude_movie_ids is not None:

            excluded_indexes = {
                self.loader
                .movie_id_to_cf_index[
                    int(movie_id)
                ]

                for movie_id
                in exclude_movie_ids

                if int(movie_id)
                in self.loader.movie_id_to_cf_index
            }

            if excluded_indexes:

                exclusion_array = np.fromiter(
                    excluded_indexes,
                    dtype=np.int64,
                )

                keep_mask = ~np.isin(
                    candidate_indexes,
                    exclusion_array,
                )

                candidate_indexes = (
                    candidate_indexes[
                        keep_mask
                    ]
                )

        # ----------------------------------------------------
        # Predict
        # ----------------------------------------------------

        predictions = self.predict_indexes(
            user_index=user_index,
            movie_indexes=candidate_indexes,
        )

        # ----------------------------------------------------
        # Convert indexes back to movieIds
        # ----------------------------------------------------

        movie_ids = np.fromiter(
            (
                self.loader
                .cf_index_to_movie_id[
                    int(index)
                ]

                for index
                in candidate_indexes
            ),
            dtype=np.int64,
            count=len(candidate_indexes),
        )

        return pd.DataFrame(
            {
                "movieId": movie_ids,
                "movieIndex": candidate_indexes,
                "cf_score": predictions,
            }
        )

    # ========================================================
    # TOP-N RECOMMENDATIONS
    # ========================================================

    def recommend(
        self,
        user_id: int,
        top_n: int = 10,
        exclude_movie_ids: Iterable[int] | None = None,
    ) -> pd.DataFrame:
        """
        Return the highest-scoring collaborative filtering
        recommendations for a user.
        """

        if top_n <= 0:
            raise ValueError(
                "top_n must be greater than 0."
            )

        scores = self.score_candidates(
            user_id=user_id,
            exclude_movie_ids=exclude_movie_ids,
        )

        top = (
            scores
            .nlargest(
                top_n,
                "cf_score",
            )
            .reset_index(drop=True)
        )

        # Add movie metadata
        movie_columns = [
            column
            for column in [
                "movieId",
                "title",
                "release_year",
                "genres",
            ]
            if column in self.loader.movies.columns
        ]

        top = top.merge(
            self.loader.movies[
                movie_columns
            ],
            on="movieId",
            how="left",
        )

        return top