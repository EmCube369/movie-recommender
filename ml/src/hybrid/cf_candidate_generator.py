from pathlib import Path

import numpy as np
import pandas as pd
import torch


# ============================================================
# PATHS
# ============================================================

ML_ROOT = Path(__file__).resolve().parents[2]

CF_MODEL_DIR = ML_ROOT / "models" / "collaborative"
CF_FEATURE_DIR = ML_ROOT / "data" / "features" / "collaborative"

MODEL_PATH = CF_MODEL_DIR / "matrix_factorization_best.pt"
SEEN_MOVIES_PATH = CF_MODEL_DIR / "cf_seen_movie_indexes.npy"

USER_MAPPING_PATH = CF_FEATURE_DIR / "cf_user_mapping.csv"
MOVIE_MAPPING_PATH = CF_FEATURE_DIR / "cf_movie_mapping.csv"


# ============================================================
# HELPERS
# ============================================================

def find_column(df, candidates):
    """
    Find a column using several possible names.
    """

    for column in candidates:
        if column in df.columns:
            return column

    raise ValueError(
        f"Could not find any of {candidates}. "
        f"Available columns: {list(df.columns)}"
    )


# ============================================================
# COLLABORATIVE CANDIDATE GENERATOR
# ============================================================

class CollaborativeCandidateGenerator:

    def __init__(self):

        print("Loading collaborative artifacts...")

        # ----------------------------------------------------
        # MAPPINGS
        # ----------------------------------------------------

        self.user_mapping = pd.read_csv(USER_MAPPING_PATH)
        self.movie_mapping = pd.read_csv(MOVIE_MAPPING_PATH)

        self.user_id_col = find_column(
            self.user_mapping,
            [
                "userId",
                "user_id",
            ],
        )

        self.user_index_col = find_column(
            self.user_mapping,
            [
                "user_index",
                "userIndex",
                "user_idx",
            ],
        )

        self.movie_id_col = find_column(
            self.movie_mapping,
            [
                "movieId",
                "movie_id",
            ],
        )

        self.movie_index_col = find_column(
            self.movie_mapping,
            [
                "movie_index",
                "movieIndex",
                "movie_idx",
            ],
        )

        # ----------------------------------------------------
        # LOOKUP TABLES
        # ----------------------------------------------------

        self.user_id_to_index = dict(
            zip(
                self.user_mapping[self.user_id_col],
                self.user_mapping[self.user_index_col],
            )
        )

        self.movie_index_to_id = dict(
            zip(
                self.movie_mapping[self.movie_index_col],
                self.movie_mapping[self.movie_id_col],
            )
        )

        # ----------------------------------------------------
        # TRAINED MOVIE INDEXES
        # ----------------------------------------------------

        self.trained_movie_indexes = np.load(
            SEEN_MOVIES_PATH
        ).astype(np.int64)

        # ----------------------------------------------------
        # LOAD MODEL CHECKPOINT
        # ----------------------------------------------------

        checkpoint = torch.load(
            MODEL_PATH,
            map_location="cpu",
            weights_only=False,
        )

        state = checkpoint["model_state_dict"]

        self.user_embedding = (
            state["user_embedding.weight"]
            .detach()
            .cpu()
            .float()
        )

        self.movie_embedding = (
            state["movie_embedding.weight"]
            .detach()
            .cpu()
            .float()
        )

        self.user_bias = (
            state["user_bias.weight"]
            .detach()
            .cpu()
            .float()
            .squeeze(1)
        )

        self.movie_bias = (
            state["movie_bias.weight"]
            .detach()
            .cpu()
            .float()
            .squeeze(1)
        )

        self.global_mean = float(
            state["global_mean"]
            .detach()
            .cpu()
        )

        self.num_users = checkpoint["num_users"]
        self.num_movies = checkpoint["num_movies"]
        self.embedding_dim = checkpoint["embedding_dim"]

        print("Collaborative model loaded.")
        print(f"Users: {self.num_users:,}")
        print(f"Movies: {self.num_movies:,}")
        print(f"Embedding dimension: {self.embedding_dim}")
        print(
            f"Movies trained by CF: "
            f"{len(self.trained_movie_indexes):,}"
        )

    # ========================================================
    # SCORE ALL TRAINED CF MOVIES
    # ========================================================

    def score_movies_for_user(self, user_id):

        if user_id not in self.user_id_to_index:
            raise ValueError(
                f"User {user_id} is not present in the CF model."
            )

        user_index = int(
            self.user_id_to_index[user_id]
        )

        # ----------------------------------------------------
        # USER COMPONENTS
        # ----------------------------------------------------

        user_vector = self.user_embedding[user_index]

        user_bias = self.user_bias[user_index]

        # ----------------------------------------------------
        # ONLY USE MOVIES THAT WERE ACTUALLY TRAINED
        # ----------------------------------------------------

        movie_indexes_tensor = torch.from_numpy(
            self.trained_movie_indexes
        ).long()

        movie_vectors = self.movie_embedding[
            movie_indexes_tensor
        ]

        movie_biases = self.movie_bias[
            movie_indexes_tensor
        ]

        # ----------------------------------------------------
        # MATRIX FACTORIZATION PREDICTION
        #
        # prediction =
        # global mean
        # + user bias
        # + movie bias
        # + user/movie latent dot product
        # ----------------------------------------------------

        interaction_scores = torch.mv(
            movie_vectors,
            user_vector,
        )

        predictions = (
            self.global_mean
            + user_bias
            + movie_biases
            + interaction_scores
        )

        # MovieLens rating scale
        predictions = torch.clamp(
            predictions,
            min=0.5,
            max=5.0,
        )

        predictions = predictions.numpy()

        # ----------------------------------------------------
        # RESULT DATAFRAME
        # ----------------------------------------------------

        movie_ids = [
            self.movie_index_to_id[int(movie_index)]
            for movie_index
            in self.trained_movie_indexes
        ]

        result = pd.DataFrame(
            {
                "movieId": movie_ids,
                "movie_index": self.trained_movie_indexes,
                "cf_score": predictions,
            }
        )

        result = result.sort_values(
            "cf_score",
            ascending=False,
        ).reset_index(drop=True)

        return result

    # ========================================================
    # TOP CANDIDATES
    # ========================================================

    def get_top_candidates(
        self,
        user_id,
        top_n=100,
    ):

        scores = self.score_movies_for_user(
            user_id
        )

        return scores.head(top_n).copy()


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    recommender = CollaborativeCandidateGenerator()

    test_user_id = 1

    candidates = recommender.get_top_candidates(
        user_id=test_user_id,
        top_n=20,
    )

    print("\n" + "=" * 70)
    print(
        f"TOP CF CANDIDATES FOR USER {test_user_id}"
    )
    print("=" * 70)

    print(
        candidates.to_string(
            index=False
        )
    )


# movies = pd.read_csv(
#     ML_ROOT / "data" / "processed" / "movies_clean_final.csv",
#     usecols=["movieId", "title_x"],
# )

# print(
#     candidates.merge(movies, on="movieId", how="left")
#     [["movieId", "title_x", "cf_score"]]
#     .to_string(index=False)
# )