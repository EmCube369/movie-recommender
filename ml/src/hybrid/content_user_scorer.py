from pathlib import Path
import pickle

import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.preprocessing import normalize

from user_history import UserHistory


# ============================================================
# PATHS
# ============================================================

ML_ROOT = Path(__file__).resolve().parents[2]

CBF_DIR = ML_ROOT / "models" / "content_based"

MOVIES_PATH = (
    ML_ROOT
    / "data"
    / "processed"
    / "movies_clean_final.csv"
)


# ============================================================
# CONTENT USER SCORER
# ============================================================

class ContentUserScorer:

    def __init__(
        self,
        user_history=None,
    ):

        print("Loading content-based artifacts...")

        self.movies = pd.read_csv(
            CBF_DIR / "movies_cbf.csv"
        )

        with open(
            CBF_DIR / "movie_id_to_index.pkl",
            "rb",
        ) as f:
            self.movie_id_to_index = pickle.load(f)

        with open(
            CBF_DIR / "content_weights.pkl",
            "rb",
        ) as f:
            self.content_weights = pickle.load(f)

        self.matrices = {
            "genre": sp.load_npz(
                CBF_DIR / "genre_matrix.npz"
            ),
            "keyword": sp.load_npz(
                CBF_DIR / "keyword_matrix.npz"
            ),
            "director": sp.load_npz(
                CBF_DIR / "director_matrix.npz"
            ),
            "cast": sp.load_npz(
                CBF_DIR / "cast_matrix.npz"
            ),
            "overview": sp.load_npz(
                CBF_DIR / "overview_matrix.npz"
            ),
            "tagline": sp.load_npz(
                CBF_DIR / "tagline_matrix.npz"
            ),
        }

        self.history = (
            user_history
            if user_history is not None
            else UserHistory()
        )

        print(
            f"Content movies: {len(self.movies):,}"
        )

        print(
            "Content weights:",
            self.content_weights,
        )
   

    # ========================================================
    # LOAD ONE USER'S RATINGS
    # ========================================================

    def load_user_ratings(
        self,
        user_id,
        minimum_rating=4.0,
    ):

        print(
            f"\nLoading positive ratings for user {user_id}..."
        )

        # --------------------------------------------------------
        # Retrieve ratings directly from compact memory-mapped
        # user-history artifacts.
        # --------------------------------------------------------

        ratings = (
            self.history.get_positive_ratings(
                user_id=user_id,
                minimum_rating=minimum_rating,
            )
        )

        if ratings.empty:
            raise ValueError(
                f"No ratings >= {minimum_rating} "
                f"found for user {user_id}."
            )

        # --------------------------------------------------------
        # Only keep movies supported by the content model.
        # --------------------------------------------------------

        ratings = ratings[
            ratings["movieId"].isin(
                self.movie_id_to_index
            )
        ].copy()

        ratings = (
            ratings
            .sort_values(
                "rating",
                ascending=False,
            )
            .reset_index(drop=True)
        )

        print(
            f"Positive CBF-compatible movies: "
            f"{len(ratings):,}"
        )

        return ratings[
            [
                "movieId",
                "rating",
            ]
        ]

    # ========================================================
    # BUILD USER PROFILE
    # ========================================================

    def build_user_profiles(
        self,
        user_ratings,
    ):

        movie_indexes = np.array(
            [
                self.movie_id_to_index[int(movie_id)]
                for movie_id
                in user_ratings["movieId"]
            ],
            dtype=np.int64,
        )

        ratings = user_ratings[
            "rating"
        ].to_numpy(dtype=np.float32)

        # Convert 4.0 - 5.0 ratings into preference weights.
        #
        # 4.0 -> 1.0
        # 4.5 -> 1.5
        # 5.0 -> 2.0
        rating_weights = ratings - 3.0

        profiles = {}

        for feature_name, matrix in self.matrices.items():

            liked_vectors = matrix[
                movie_indexes
            ]

            weighted_vectors = liked_vectors.multiply(
                rating_weights[:, None]
            )

            profile = weighted_vectors.sum(
                axis=0
            )

            profile = sp.csr_matrix(profile)

            # Normalize so cosine similarity can be
            # calculated with a dot product.
            profile = normalize(
                profile,
                norm="l2",
            )

            profiles[feature_name] = profile

        return profiles

    # ========================================================
    # SCORE ALL MOVIES
    # ========================================================

    def score_all_movies(
        self,
        profiles,
    ):

        total_score = np.zeros(
            len(self.movies),
            dtype=np.float32,
        )

        component_scores = {}

        for feature_name, matrix in self.matrices.items():

            profile = profiles[
                feature_name
            ]

            similarity = (
                matrix @ profile.T
            ).toarray().ravel()

            similarity = similarity.astype(
                np.float32
            )

            component_scores[
                feature_name
            ] = similarity

            weight = self.content_weights[
                feature_name
            ]

            total_score += (
                similarity * weight
            )

        result = pd.DataFrame(
            {
                "movieId":
                    self.movies["movieId"].to_numpy(),
                "content_score":
                    total_score,
            }
        )

        return result, component_scores

    # ========================================================
    # GET TOP PERSONALIZED CONTENT CANDIDATES
    # ========================================================

    def get_top_candidates(
        self,
        user_id,
        top_n=20,
        minimum_rating=4.0,
    ):

        user_ratings = self.load_user_ratings(
            user_id=user_id,
            minimum_rating=minimum_rating,
        )

        profiles = self.build_user_profiles(
            user_ratings
        )

        scores, _ = self.score_all_movies(
            profiles
        )

        # -----------------------------------------------
        # Remove movies already used in user profile
        # -----------------------------------------------

        rated_movie_ids = set(
            user_ratings["movieId"]
        )

        scores = scores[
            ~scores["movieId"].isin(
                rated_movie_ids
            )
        ]

        scores = scores.sort_values(
            "content_score",
            ascending=False,
        ).head(top_n)

        return scores.reset_index(
            drop=True
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    scorer = ContentUserScorer()

    test_user_id = 1

    candidates = scorer.get_top_candidates(
        user_id=test_user_id,
        top_n=20,
        minimum_rating=4.0,
    )

    # Add movie titles for inspection
    catalog = pd.read_csv(
        MOVIES_PATH,
        low_memory=False,
    )

    title_column = (
        "title_x"
        if "title_x" in catalog.columns
        else "title"
    )

    candidates = candidates.merge(
        catalog[
            ["movieId", title_column]
        ],
        on="movieId",
        how="left",
    )

    print("\n" + "=" * 80)
    print(
        f"TOP PERSONALIZED CONTENT CANDIDATES "
        f"FOR USER {test_user_id}"
    )
    print("=" * 80)

    print(
        candidates[
            [
                "movieId",
                title_column,
                "content_score",
            ]
        ].to_string(
            index=False
        )
    )