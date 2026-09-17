from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ML_ROOT = Path(__file__).resolve().parents[2]

HYBRID_MODEL_DIR = (
    ML_ROOT
    / "models"
    / "hybrid"
)

CF_FEATURE_DIR = (
    ML_ROOT
    / "data"
    / "features"
    / "collaborative"
)

INDPTR_PATH = (
    HYBRID_MODEL_DIR
    / "user_history_indptr.npy"
)

MOVIE_INDEXES_PATH = (
    HYBRID_MODEL_DIR
    / "user_history_movie_indexes.npy"
)

USER_MAPPING_PATH = (
    CF_FEATURE_DIR
    / "cf_user_mapping.csv"
)

MOVIE_MAPPING_PATH = (
    CF_FEATURE_DIR
    / "cf_movie_mapping.csv"
)

RATINGS_PATH = (
    HYBRID_MODEL_DIR
    / "user_history_ratings.npy"
)

# ============================================================
# USER HISTORY
# ============================================================

class UserHistory:

    def __init__(self):

        print("Loading compact user history...")

        # ----------------------------------------------------
        # MEMORY-MAPPED HISTORY
        # ----------------------------------------------------

        self.indptr = np.load(
            INDPTR_PATH,
            mmap_mode="r",
        )

        self.movie_indexes = np.load(
            MOVIE_INDEXES_PATH,
            mmap_mode="r",
        )

        self.ratings = np.load(
            RATINGS_PATH,
            mmap_mode="r",
        )

        # ----------------------------------------------------
        # MAPPINGS
        # ----------------------------------------------------

        user_mapping = pd.read_csv(
            USER_MAPPING_PATH
        )

        movie_mapping = pd.read_csv(
            MOVIE_MAPPING_PATH
        )

        self.user_id_to_index = dict(
            zip(
                user_mapping["userId"],
                user_mapping["userIndex"],
            )
        )

        # ----------------------------------------------------
        # Build fast movieIndex -> movieId lookup.
        #
        # movieIndex is contiguous from 0 ... num_movies-1.
        # ----------------------------------------------------

        movie_mapping = movie_mapping.sort_values(
            "movieIndex"
        )

        expected_indexes = np.arange(
            len(movie_mapping),
            dtype=np.int64,
        )

        actual_indexes = movie_mapping[
            "movieIndex"
        ].to_numpy(
            dtype=np.int64
        )

        if not np.array_equal(
            actual_indexes,
            expected_indexes,
        ):
            raise ValueError(
                "movieIndex mapping is not contiguous."
            )
        
        if len(self.movie_indexes) != len(self.ratings):
            raise ValueError(
                "Movie-history and rating-history lengths do not match."
            )

        self.movie_ids_by_index = movie_mapping[
            "movieId"
        ].to_numpy(
            dtype=np.int64
        )

        print(
            f"History users: "
            f"{len(self.indptr) - 1:,}"
        )

        print(
            f"History interactions: "
            f"{len(self.movie_indexes):,}"
        )

    # ========================================================
    # USER INDEX
    # ========================================================

    def get_user_index(
        self,
        user_id,
    ):

        if user_id not in self.user_id_to_index:
            raise ValueError(
                f"Unknown userId: {user_id}"
            )

        return int(
            self.user_id_to_index[user_id]
        )

    # ========================================================
    # RATED MOVIE INDEXES
    # ========================================================

    def get_rated_movie_indexes(
        self,
        user_id,
    ):

        user_index = self.get_user_index(
            user_id
        )

        start = int(
            self.indptr[user_index]
        )

        end = int(
            self.indptr[user_index + 1]
        )

        return np.asarray(
            self.movie_indexes[
                start:end
            ],
            dtype=np.int64,
        )

    # ========================================================
    # RATED MOVIE IDS
    # ========================================================

    def get_rated_movie_ids(
        self,
        user_id,
    ):

        movie_indexes = (
            self.get_rated_movie_indexes(
                user_id
            )
        )

        return self.movie_ids_by_index[
            movie_indexes
        ]

    # ========================================================
    # FILTER DATAFRAME
    # ========================================================

    def filter_rated_movies(
        self,
        dataframe,
        user_id,
    ):

        rated_movie_ids = (
            self.get_rated_movie_ids(
                user_id
            )
        )

        before = len(
            dataframe
        )

        result = dataframe[
            ~dataframe["movieId"].isin(
                rated_movie_ids
            )
        ].copy()

        removed = (
            before - len(result)
        )

        return (
            result,
            len(rated_movie_ids),
            removed,
        )
    
    # ========================================================
    # USER RATINGS
    # ========================================================

    def get_ratings(
        self,
        user_id,
    ):

        user_index = self.get_user_index(
            user_id
        )

        start = int(
            self.indptr[user_index]
        )

        end = int(
            self.indptr[user_index + 1]
        )

        return np.asarray(
            self.ratings[
                start:end
            ],
            dtype=np.float32,
        )


    # ========================================================
    # COMPLETE USER HISTORY
    # ========================================================

    def get_user_ratings(
        self,
        user_id,
    ):

        movie_ids = self.get_rated_movie_ids(
            user_id
        )

        ratings = self.get_ratings(
            user_id
        )

        if len(movie_ids) != len(ratings):
            raise RuntimeError(
                "Movie IDs and ratings are misaligned."
            )

        return pd.DataFrame(
            {
                "movieId": movie_ids,
                "rating": ratings,
            }
        )


    # ========================================================
    # POSITIVE USER RATINGS
    # ========================================================

    def get_positive_ratings(
        self,
        user_id,
        minimum_rating=4.0,
    ):

        ratings = self.get_user_ratings(
            user_id
        )

        ratings = ratings[
            ratings["rating"] >= minimum_rating
        ].copy()

        return (
            ratings
            .sort_values(
                "rating",
                ascending=False,
            )
            .reset_index(drop=True)
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    history = UserHistory()

    test_user_id = 1

    indexes = (
        history.get_rated_movie_indexes(
            test_user_id
        )
    )

    movie_ids = (
        history.get_rated_movie_ids(
            test_user_id
        )
    )

    positive = history.get_positive_ratings(
        test_user_id,
        minimum_rating=4.0,
    )

    print("\n" + "=" * 70)
    print(
        f"USER {test_user_id} HISTORY"
    )
    print("=" * 70)

    print(
        "Rated movie count:",
        len(movie_ids),
    )

    print(
        "\nFirst 20 movie indexes:"
    )

    print(
        indexes[:20]
    )

    print(
        "\nFirst 20 movie IDs:"
    )

    print(
        movie_ids[:20]
    )

    print(
        "Positive ratings >= 4.0:",
        len(positive),
    )