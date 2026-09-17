from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd
from scipy import sparse

from recommender.artifact_loader import ArtifactLoader


class ContentBasedRecommender:
    """
    Runtime content-based recommendation component.

    Uses the six precomputed TF-IDF sparse matrices:

        genre
        keyword
        director
        cast
        overview
        tagline
    """

    def __init__(
        self,
        loader: ArtifactLoader | None = None,
    ) -> None:

        self.loader = (
            loader
            if loader is not None
            else ArtifactLoader()
        )

        self.weights = {
            key: float(value)
            for key, value
            in self.loader.content_weights.items()
        }

        self.matrices = (
            self.loader.content_matrices
        )

        self.movie_id_to_index = (
            self.loader.content_movie_id_to_index
        )

        self.index_to_movie_id = (
            self.loader.content_index_to_movie_id
        )

        self.num_movies = len(
            self.movie_id_to_index
        )

        self._validate()

    # ========================================================
    # VALIDATION
    # ========================================================

    def _validate(self) -> None:

        required_features = {
            "genre",
            "keyword",
            "director",
            "cast",
            "overview",
            "tagline",
        }

        if set(self.weights) != required_features:
            raise ValueError(
                "Unexpected content weights. "
                f"Expected {required_features}, "
                f"got {set(self.weights)}"
            )

        if set(self.matrices) != required_features:
            raise ValueError(
                "Content matrix set does not "
                "match expected feature set."
            )

        total_weight = sum(
            self.weights.values()
        )

        if not np.isclose(
            total_weight,
            1.0,
        ):
            raise ValueError(
                "Content weights must sum to 1.0. "
                f"Current total: {total_weight}"
            )

        for name, matrix in self.matrices.items():

            if not sparse.isspmatrix_csr(
                matrix
            ):
                raise TypeError(
                    f"{name} matrix is not CSR."
                )

            if matrix.shape[0] != self.num_movies:
                raise ValueError(
                    f"{name} matrix row count "
                    f"does not match content mapping."
                )

    # ========================================================
    # LOOKUPS
    # ========================================================

    def has_movie(
        self,
        movie_id: int,
    ) -> bool:

        return (
            int(movie_id)
            in self.movie_id_to_index
        )

    def get_movie_index(
        self,
        movie_id: int,
    ) -> int:

        movie_id = int(movie_id)

        try:

            return int(
                self.movie_id_to_index[
                    movie_id
                ]
            )

        except KeyError as exc:

            raise KeyError(
                f"Unknown content movieId: "
                f"{movie_id}"
            ) from exc

    # ========================================================
    # FEATURE SIMILARITY
    # ========================================================

    @staticmethod
    def _row_similarity(
        matrix,
        source_index: int,
    ) -> np.ndarray:
        """
        Calculate cosine-like similarity against all movies.

        The saved TF-IDF matrices are already normalized, so
        sparse dot product gives cosine similarity.
        """

        source = matrix[
            source_index
        ]

        scores = (
            matrix
            @ source.T
        )

        return (
            scores
            .toarray()
            .ravel()
            .astype(np.float32)
        )

    # ========================================================
    # MOVIE-TO-MOVIE SIMILARITY
    # ========================================================

    def score_similar_movies(
        self,
        movie_id: int,
    ) -> pd.DataFrame:

        source_index = (
            self.get_movie_index(
                movie_id
            )
        )

        final_scores = np.zeros(
            self.num_movies,
            dtype=np.float32,
        )

        feature_scores = {}

        for name, matrix in self.matrices.items():

            scores = self._row_similarity(
                matrix=matrix,
                source_index=source_index,
            )

            feature_scores[name] = scores

            final_scores += (
                self.weights[name]
                * scores
            )

        movie_ids = np.fromiter(
            (
                self.index_to_movie_id[
                    index
                ]
                for index in range(
                    self.num_movies
                )
            ),
            dtype=np.int64,
            count=self.num_movies,
        )

        result = pd.DataFrame(
            {
                "movieId": movie_ids,
                "contentIndex": np.arange(
                    self.num_movies,
                    dtype=np.int64,
                ),
                "content_score": final_scores,
            }
        )

        for name, scores in feature_scores.items():
            result[
                f"{name}_score"
            ] = scores

        return result

    def similar_movies(
        self,
        movie_id: int,
        top_n: int = 10,
    ) -> pd.DataFrame:

        if top_n <= 0:
            raise ValueError(
                "top_n must be greater than 0."
            )

        scores = self.score_similar_movies(
            movie_id
        )

        # Do not recommend the query movie itself
        scores = scores[
            scores["movieId"]
            != int(movie_id)
        ]

        top = (
            scores
            .nlargest(
                top_n,
                "content_score",
            )
            .reset_index(drop=True)
        )

        metadata_columns = [
            column
            for column in [
                "movieId",
                "title",
                "release_year",
                "genres",
            ]
            if column
            in self.loader.movies.columns
        ]

        return top.merge(
            self.loader.movies[
                metadata_columns
            ],
            on="movieId",
            how="left",
        )

    # ========================================================
    # USER PROFILE
    # ========================================================

    @staticmethod
    def _build_profile(
        matrix,
        movie_indexes: np.ndarray,
    ):
        """
        Build a user's profile as the mean vector of their
        positively-rated movies.
        """

        profile = matrix[
            movie_indexes
        ].mean(axis=0)

        return sparse.csr_matrix(
            profile
        )

    @staticmethod
    def _profile_similarity(
        matrix,
        profile,
    ) -> np.ndarray:

        profile_norm = sparse.linalg.norm(
            profile
        )

        if profile_norm == 0:
            return np.zeros(
                matrix.shape[0],
                dtype=np.float32,
            )

        # Saved TF-IDF rows are normalized.
        # Normalize the averaged profile separately.

        normalized_profile = (
            profile / profile_norm
        )

        scores = (
            matrix
            @ normalized_profile.T
        )

        return (
            np.asarray(
                scores.toarray()
            )
            .ravel()
            .astype(np.float32)
        )

    # ========================================================
    # PERSONALIZED CONTENT SCORING
    # ========================================================

    def score_profile(
        self,
        positive_movie_ids: Iterable[int],
        exclude_movie_ids: Iterable[int] | None = None,
    ) -> pd.DataFrame:
        """
        Build a content profile from positively-rated movie IDs
        and score the full catalog against that profile.

        User-history lookup stays outside this component.
        """

        positive_indexes = []

        for movie_id in positive_movie_ids:

            movie_id = int(movie_id)

            index = (
                self.movie_id_to_index.get(
                    movie_id
                )
            )

            if index is not None:
                positive_indexes.append(
                    int(index)
                )

        if not positive_indexes:
            raise ValueError(
                "No supplied positive movies exist "
                "in the content catalog."
            )

        positive_indexes = np.asarray(
            sorted(
                set(
                    positive_indexes
                )
            ),
            dtype=np.int64,
        )

        final_scores = np.zeros(
            self.num_movies,
            dtype=np.float32,
        )

        for name, matrix in self.matrices.items():

            profile = self._build_profile(
                matrix,
                positive_indexes,
            )

            scores = self._profile_similarity(
                matrix,
                profile,
            )

            final_scores += (
                self.weights[name]
                * scores
            )

        movie_ids = np.fromiter(
            (
                self.index_to_movie_id[
                    index
                ]
                for index in range(
                    self.num_movies
                )
            ),
            dtype=np.int64,
            count=self.num_movies,
        )

        result = pd.DataFrame(
            {
                "movieId": movie_ids,
                "contentIndex": np.arange(
                    self.num_movies,
                    dtype=np.int64,
                ),
                "content_score": final_scores,
            }
        )

        # ----------------------------------------------------
        # Exclude supplied movies
        # ----------------------------------------------------

        exclusion = {
            int(movie_id)
            for movie_id
            in positive_movie_ids
        }

        if exclude_movie_ids is not None:
            exclusion.update(
                int(movie_id)
                for movie_id
                in exclude_movie_ids
            )

        if exclusion:

            result = result[
                ~result[
                    "movieId"
                ].isin(exclusion)
            ]

        return result.reset_index(
            drop=True
        )

    def recommend_from_profile(
        self,
        positive_movie_ids: Iterable[int],
        top_n: int = 10,
        exclude_movie_ids: Iterable[int] | None = None,
    ) -> pd.DataFrame:

        if top_n <= 0:
            raise ValueError(
                "top_n must be greater than 0."
            )

        scores = self.score_profile(
            positive_movie_ids=positive_movie_ids,
            exclude_movie_ids=exclude_movie_ids,
        )

        top = (
            scores
            .nlargest(
                top_n,
                "content_score",
            )
            .reset_index(drop=True)
        )

        metadata_columns = [
            column
            for column in [
                "movieId",
                "title",
                "release_year",
                "genres",
            ]
            if column
            in self.loader.movies.columns
        ]

        return top.merge(
            self.loader.movies[
                metadata_columns
            ],
            on="movieId",
            how="left",
        )