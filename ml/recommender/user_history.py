from __future__ import annotations

import numpy as np
import pandas as pd

from recommender.artifact_loader import ArtifactLoader
from recommender.config import POSITIVE_RATING_THRESHOLD


class UserHistory:
    """
    Runtime access to compact user-rating history.

    History is stored in CSR-style arrays:

        indptr
        movie_indexes
        ratings

    Movie indexes are collaborative-filtering movie indexes.
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

        self.indptr = (
            self.loader.user_history_indptr
        )

        self.movie_indexes = (
            self.loader.user_history_movie_indexes
        )

        self.ratings = (
            self.loader.user_history_ratings
        )

        self._validate()

    # ========================================================
    # VALIDATION
    # ========================================================

    def _validate(self) -> None:

        expected_pointer_count = (
            len(self.loader.cf_user_mapping)
            + 1
        )

        if len(self.indptr) != expected_pointer_count:
            raise ValueError(
                "User-history indptr length mismatch. "
                f"Expected {expected_pointer_count:,}, "
                f"got {len(self.indptr):,}."
            )

        if (
            len(self.movie_indexes)
            != len(self.ratings)
        ):
            raise ValueError(
                "History movie-index and rating arrays "
                "have different lengths."
            )

        if int(self.indptr[0]) != 0:
            raise ValueError(
                "History indptr must begin at 0."
            )

        if (
            int(self.indptr[-1])
            != len(self.movie_indexes)
        ):
            raise ValueError(
                "Final history indptr does not match "
                "interaction count."
            )

        if np.any(
            self.indptr[1:]
            < self.indptr[:-1]
        ):
            raise ValueError(
                "History indptr is not monotonically increasing."
            )

    # ========================================================
    # USER LOOKUP
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

            return int(
                self.loader.user_id_to_index[
                    user_id
                ]
            )

        except KeyError as exc:

            raise KeyError(
                f"Unknown userId: {user_id}"
            ) from exc

    # ========================================================
    # HISTORY SLICE
    # ========================================================

    def _get_slice(
        self,
        user_index: int,
    ) -> slice:

        if (
            user_index < 0
            or user_index
            >= len(self.indptr) - 1
        ):
            raise IndexError(
                f"User index out of range: "
                f"{user_index}"
            )

        start = int(
            self.indptr[user_index]
        )

        end = int(
            self.indptr[user_index + 1]
        )

        return slice(
            start,
            end,
        )

    # ========================================================
    # RAW HISTORY
    # ========================================================

    def get_movie_indexes(
        self,
        user_id: int,
    ) -> np.ndarray:

        user_index = self.get_user_index(
            user_id
        )

        history_slice = self._get_slice(
            user_index
        )

        return np.asarray(
            self.movie_indexes[
                history_slice
            ],
            dtype=np.int32,
        )

    def get_ratings(
        self,
        user_id: int,
    ) -> np.ndarray:

        user_index = self.get_user_index(
            user_id
        )

        history_slice = self._get_slice(
            user_index
        )

        return np.asarray(
            self.ratings[
                history_slice
            ],
            dtype=np.float32,
        )

    # ========================================================
    # MOVIE IDS
    # ========================================================

    def get_rated_movie_ids(
        self,
        user_id: int,
    ) -> np.ndarray:

        movie_indexes = (
            self.get_movie_indexes(
                user_id
            )
        )

        movie_ids = np.fromiter(
            (
                self.loader
                .cf_index_to_movie_id[
                    int(index)
                ]

                for index
                in movie_indexes
            ),
            dtype=np.int64,
            count=len(movie_indexes),
        )

        return movie_ids

    # ========================================================
    # POSITIVE MOVIES
    # ========================================================

    def get_positive_movie_ids(
        self,
        user_id: int,
        min_rating: float = POSITIVE_RATING_THRESHOLD,
    ) -> np.ndarray:

        movie_indexes = (
            self.get_movie_indexes(
                user_id
            )
        )

        ratings = self.get_ratings(
            user_id
        )

        positive_mask = (
            ratings >= float(min_rating)
        )

        positive_indexes = (
            movie_indexes[
                positive_mask
            ]
        )

        return np.fromiter(
            (
                self.loader
                .cf_index_to_movie_id[
                    int(index)
                ]

                for index
                in positive_indexes
            ),
            dtype=np.int64,
            count=len(positive_indexes),
        )

    # ========================================================
    # INTERACTION COUNT
    # ========================================================

    def interaction_count(
        self,
        user_id: int,
    ) -> int:

        user_index = self.get_user_index(
            user_id
        )

        return int(
            self.indptr[
                user_index + 1
            ]
            - self.indptr[
                user_index
            ]
        )

    # ========================================================
    # FULL USER HISTORY TABLE
    # ========================================================

    def get_history(
        self,
        user_id: int,
    ) -> pd.DataFrame:

        movie_indexes = (
            self.get_movie_indexes(
                user_id
            )
        )

        ratings = self.get_ratings(
            user_id
        )

        movie_ids = self.get_rated_movie_ids(
            user_id
        )

        history = pd.DataFrame(
            {
                "movieId": movie_ids,
                "movieIndex": movie_indexes,
                "rating": ratings,
            }
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

        return history.merge(
            self.loader.movies[
                metadata_columns
            ],
            on="movieId",
            how="left",
        )

    # ========================================================
    # SUMMARY
    # ========================================================

    def summary(
        self,
        user_id: int,
        positive_threshold: float = POSITIVE_RATING_THRESHOLD,
    ) -> dict:

        ratings = self.get_ratings(
            user_id
        )

        positive_count = int(
            np.sum(
                ratings
                >= positive_threshold
            )
        )

        return {
            "userId": int(user_id),
            "interactionCount": int(
                len(ratings)
            ),
            "positiveCount": positive_count,
            "positiveThreshold": float(
                positive_threshold
            ),
            "meanRating": (
                float(ratings.mean())
                if len(ratings)
                else None
            ),
        }