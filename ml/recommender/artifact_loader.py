from __future__ import annotations

import pickle
from functools import cached_property
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from scipy import sparse

from recommender.config import (
    MOVIES_FILE,
    CF_MODEL_FILE,
    CF_SEEN_MOVIES_FILE,
    CF_USER_MAPPING_FILE,
    CF_MOVIE_MAPPING_FILE,
    CONTENT_MOVIE_INDEX_FILE,
    CONTENT_WEIGHTS_FILE,
    MOVIE_SENTIMENT_FILE,
    validate_required_artifacts,
    CONTENT_GENRE_MATRIX_FILE,
    CONTENT_KEYWORD_MATRIX_FILE,
    CONTENT_DIRECTOR_MATRIX_FILE,
    CONTENT_CAST_MATRIX_FILE,
    CONTENT_OVERVIEW_MATRIX_FILE,
    CONTENT_TAGLINE_MATRIX_FILE,
    USER_HISTORY_INDPTR_FILE,
    USER_HISTORY_MOVIE_INDEXES_FILE,
    USER_HISTORY_RATINGS_FILE,
)


class ArtifactLoader:
    """
    Central loader for runtime ML artifacts.

    Artifacts are loaded lazily and cached so repeated accesses
    do not reload large files from disk.
    """

    def __init__(self) -> None:
        validate_required_artifacts()

    # ============================================================
    # GENERIC LOADERS
    # ============================================================

    @staticmethod
    def _load_pickle(path: Path) -> Any:
        with open(path, "rb") as file:
            return pickle.load(file)

    @staticmethod
    def _load_csv(path: Path) -> pd.DataFrame:
        return pd.read_csv(path)

    @staticmethod
    def _load_numpy(path: Path) -> np.ndarray:
        return np.load(
            path,
            allow_pickle=False,
        )
    
    @staticmethod
    def _load_sparse_matrix(path: Path):
        return sparse.load_npz(path).tocsr()
    
    @staticmethod
    def _load_numpy_memmap(path: Path) -> np.ndarray:
        """
        Load a NumPy array using memory mapping.

        Useful for large runtime arrays because the full artifact
        does not need to be copied into RAM immediately.
        """
        return np.load(
            path,
            mmap_mode="r",
            allow_pickle=False,
        )

    # ============================================================
    # MOVIE CATALOG
    # ============================================================

    @cached_property
    def movies(self) -> pd.DataFrame:
        print("Loading movie catalog...")

        df = self._load_csv(MOVIES_FILE)

        if "movieId" not in df.columns:
            raise ValueError(
                "Movie catalog does not contain required column: movieId"
            )

        if df["movieId"].duplicated().any():
            raise ValueError(
                "Movie catalog contains duplicate movieId values."
            )

        return df

    # ============================================================
    # COLLABORATIVE FILTERING
    # ============================================================

    @cached_property
    def cf_user_mapping(self) -> pd.DataFrame:
        print("Loading CF user mapping...")

        df = self._load_csv(
            CF_USER_MAPPING_FILE
        )

        required = {
            "userId",
            "userIndex",
        }

        if not required.issubset(df.columns):
            raise ValueError(
                f"CF user mapping must contain columns: {required}"
            )

        return df

    @cached_property
    def cf_movie_mapping(self) -> pd.DataFrame:
        print("Loading CF movie mapping...")

        df = self._load_csv(
            CF_MOVIE_MAPPING_FILE
        )

        required = {
            "movieId",
            "movieIndex",
        }

        if not required.issubset(df.columns):
            raise ValueError(
                f"CF movie mapping must contain columns: {required}"
            )

        return df

    @cached_property
    def cf_seen_movie_indexes(self) -> np.ndarray:
        print("Loading CF seen-movie indexes...")

        return self._load_numpy(
            CF_SEEN_MOVIES_FILE
        )

    def load_cf_checkpoint(
        self,
        device: str | torch.device = "cpu",
    ) -> Any:
        """
        Load the saved collaborative filtering checkpoint.

        Model construction will be handled later by
        collaborative.py.
        """

        print(
            f"Loading CF checkpoint on {device}..."
        )

        return torch.load(
            CF_MODEL_FILE,
            map_location=device,
            weights_only=False,
        )

    # ============================================================
    # CONTENT-BASED FILTERING
    # ============================================================

    @cached_property
    def content_movie_id_to_index(self) -> dict:
        print("Loading content movie index...")

        mapping = self._load_pickle(
            CONTENT_MOVIE_INDEX_FILE
        )

        if not isinstance(mapping, dict):
            raise TypeError(
                "movie_id_to_index.pkl must contain a dictionary."
            )

        return mapping

    @cached_property
    def content_weights(self) -> dict:
        print("Loading content weights...")

        weights = self._load_pickle(
            CONTENT_WEIGHTS_FILE
        )

        if not isinstance(weights, dict):
            raise TypeError(
                "content_weights.pkl must contain a dictionary."
            )

        return weights
    
    @cached_property
    def content_genre_matrix(self):
        print("Loading genre content matrix...")

        return self._load_sparse_matrix(
            CONTENT_GENRE_MATRIX_FILE
        )


    @cached_property
    def content_keyword_matrix(self):
        print("Loading keyword content matrix...")

        return self._load_sparse_matrix(
            CONTENT_KEYWORD_MATRIX_FILE
        )


    @cached_property
    def content_director_matrix(self):
        print("Loading director content matrix...")

        return self._load_sparse_matrix(
            CONTENT_DIRECTOR_MATRIX_FILE
        )


    @cached_property
    def content_cast_matrix(self):
        print("Loading cast content matrix...")

        return self._load_sparse_matrix(
            CONTENT_CAST_MATRIX_FILE
        )


    @cached_property
    def content_overview_matrix(self):
        print("Loading overview content matrix...")

        return self._load_sparse_matrix(
            CONTENT_OVERVIEW_MATRIX_FILE
        )


    @cached_property
    def content_tagline_matrix(self):
        print("Loading tagline content matrix...")

        return self._load_sparse_matrix(
            CONTENT_TAGLINE_MATRIX_FILE
        )


    @cached_property
    def content_matrices(self) -> dict:
        return {
            "genre": self.content_genre_matrix,
            "keyword": self.content_keyword_matrix,
            "director": self.content_director_matrix,
            "cast": self.content_cast_matrix,
            "overview": self.content_overview_matrix,
            "tagline": self.content_tagline_matrix,
        }


    @cached_property
    def content_index_to_movie_id(self) -> dict[int, int]:
        return {
            int(index): int(movie_id)
            for movie_id, index
            in self.content_movie_id_to_index.items()
        }

    # ============================================================
    # SENTIMENT
    # ============================================================

    @cached_property
    def movie_sentiment(self) -> pd.DataFrame:
        print("Loading movie sentiment...")

        df = self._load_csv(
            MOVIE_SENTIMENT_FILE
        )

        if "movieId" not in df.columns:
            raise ValueError(
                "Movie sentiment artifact does not contain movieId."
            )

        if df["movieId"].duplicated().any():
            raise ValueError(
                "Movie sentiment artifact contains duplicate movieId values."
            )

        return df
    
    # ============================================================
    # USER HISTORY
    # ============================================================

    @cached_property
    def user_history_indptr(self) -> np.ndarray:
        print("Loading user history indptr...")

        return self._load_numpy_memmap(
            USER_HISTORY_INDPTR_FILE
        )


    @cached_property
    def user_history_movie_indexes(self) -> np.ndarray:
        print("Loading user history movie indexes...")

        return self._load_numpy_memmap(
            USER_HISTORY_MOVIE_INDEXES_FILE
        )


    @cached_property
    def user_history_ratings(self) -> np.ndarray:
        print("Loading user history ratings...")

        return self._load_numpy_memmap(
            USER_HISTORY_RATINGS_FILE
        )

    # ============================================================
    # CONVENIENCE MAPPINGS
    # ============================================================

    @cached_property
    def user_id_to_index(self) -> dict[int, int]:
        return dict(
            zip(
                self.cf_user_mapping[
                    "userId"
                ].astype(int),

                self.cf_user_mapping[
                    "userIndex"
                ].astype(int),
            )
        )

    @cached_property
    def movie_id_to_cf_index(self) -> dict[int, int]:
        return dict(
            zip(
                self.cf_movie_mapping[
                    "movieId"
                ].astype(int),

                self.cf_movie_mapping[
                    "movieIndex"
                ].astype(int),
            )
        )

    @cached_property
    def cf_index_to_movie_id(self) -> dict[int, int]:
        return dict(
            zip(
                self.cf_movie_mapping[
                    "movieIndex"
                ].astype(int),

                self.cf_movie_mapping[
                    "movieId"
                ].astype(int),
            )
        )
    
    @cached_property
    def cf_supported_movie_ids(self) -> set[int]:
        """
        MovieLens movieIds that are valid recommendation
        candidates for the trained collaborative-filtering model.
        """

        return {
            int(
                self.cf_index_to_movie_id[
                    int(movie_index)
                ]
            )
            for movie_index
            in self.cf_seen_movie_indexes
        }