from pathlib import Path

import numpy as np
import pandas as pd
import torch

from model import MatrixFactorization


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = (
    BASE_DIR
    / "data"
    / "features"
    / "collaborative"
)

MODEL_DIR = (
    BASE_DIR
    / "models"
    / "collaborative"
)

MODEL_PATH = (
    MODEL_DIR
    / "matrix_factorization_best.pt"
)

MOVIES_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "movielens"
    / "movies.csv"
)

movies_catalog = pd.read_csv(MOVIES_PATH)


# ============================================================
# DEVICE
# ============================================================

device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# LOAD MODEL
# ============================================================

checkpoint = torch.load(
    MODEL_PATH,
    map_location=device,
    weights_only=False
)


model = MatrixFactorization(
    num_users=checkpoint["num_users"],
    num_movies=checkpoint["num_movies"],
    embedding_dim=checkpoint["embedding_dim"],
    global_mean=checkpoint["global_mean"]
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(device)

model.eval()


# ============================================================
# LOAD MAPPINGS
# ============================================================

user_mapping = pd.read_csv(
    DATA_DIR / "cf_user_mapping.csv"
)

movie_mapping = pd.read_csv(
    DATA_DIR / "cf_movie_mapping.csv"
)


# ============================================================
# MOVIES THAT ACTUALLY LEARNED CF EMBEDDINGS
# ============================================================

seen_movie_indexes = np.load(
    MODEL_DIR / "cf_seen_movie_indexes.npy"
)


# ============================================================
# FIND MOVIES ALREADY RATED BY USER
# ============================================================

def get_rated_movies(user_index):

    rated_movies = set()

    interactions_path = (
        DATA_DIR / "cf_interactions.csv"
    )

    # Read in chunks rather than loading all ~32M rows again.
    for chunk in pd.read_csv(
        interactions_path,
        usecols=[
            "userIndex",
            "movieIndex"
        ],
        dtype={
            "userIndex": "int32",
            "movieIndex": "int32"
        },
        chunksize=1_000_000
    ):

        matches = chunk[
            chunk["userIndex"]
            == user_index
        ]

        rated_movies.update(
            matches["movieIndex"].tolist()
        )

    return rated_movies


# ============================================================
# INSPECT FUNCTION
# ============================================================

def get_user_history(user_id, top_n=15):

    user_row = user_mapping[
        user_mapping["userId"] == user_id
    ]

    if user_row.empty:
        raise ValueError(
            f"User ID {user_id} does not exist."
        )

    user_index = int(
        user_row.iloc[0]["userIndex"]
    )

    history_parts = []

    interactions_path = (
        DATA_DIR / "cf_interactions.csv"
    )

    for chunk in pd.read_csv(
        interactions_path,
        usecols=[
            "userIndex",
            "movieIndex",
            "rating"
        ],
        dtype={
            "userIndex": "int32",
            "movieIndex": "int32",
            "rating": "float32"
        },
        chunksize=1_000_000
    ):

        matches = chunk[
            chunk["userIndex"] == user_index
        ]

        if not matches.empty:
            history_parts.append(matches)

    history = pd.concat(
        history_parts,
        ignore_index=True
    )

    history = history.merge(
        movie_mapping[
            [
                "movieId",
                "movieIndex"
            ]
        ],
        on="movieIndex",
        how="left"
    )

    history = history.merge(
        movies_catalog[
            [
                "movieId",
                "title",
                "genres"
            ]
        ],
        on="movieId",
        how="left"
    )

    history = history.sort_values(
        "rating",
        ascending=False
    )

    return history[
        [
            "movieId",
            "title",
            "genres",
            "rating"
        ]
    ].head(top_n)

# ============================================================
# RECOMMENDATION FUNCTION
# ============================================================

def recommend_for_user(
    user_id,
    top_n=10
):

    # --------------------------------------------------------
    # FIND INTERNAL USER INDEX
    # --------------------------------------------------------

    user_row = user_mapping[
        user_mapping["userId"]
        == user_id
    ]

    if user_row.empty:

        raise ValueError(
            f"User ID {user_id} "
            "does not exist in the CF dataset."
        )


    user_index = int(
        user_row.iloc[0]["userIndex"]
    )


    print(
        f"User ID    : {user_id}"
    )

    print(
        f"User index : {user_index}"
    )


    # --------------------------------------------------------
    # FIND ALREADY-RATED MOVIES
    # --------------------------------------------------------

    rated_movies = get_rated_movies(
        user_index
    )


    print(
        "Movies already rated:",
        len(rated_movies)
    )


    # --------------------------------------------------------
    # CREATE CANDIDATE MOVIE SET
    # --------------------------------------------------------

    candidate_movies = np.array(
        [
            movie_index
            for movie_index
            in seen_movie_indexes

            if movie_index
            not in rated_movies
        ],
        dtype=np.int64
    )


    print(
        "Candidate movies:",
        len(candidate_movies)
    )


    # --------------------------------------------------------
    # PREDICT IN BATCHES
    # --------------------------------------------------------

    scores = []

    PREDICTION_BATCH_SIZE = 65536


    with torch.no_grad():

        for start in range(
            0,
            len(candidate_movies),
            PREDICTION_BATCH_SIZE
        ):

            end = (
                start
                + PREDICTION_BATCH_SIZE
            )


            movie_batch_np = (
                candidate_movies[
                    start:end
                ]
            )


            movie_batch = torch.tensor(
                movie_batch_np,
                dtype=torch.long,
                device=device
            )


            user_batch = torch.full(
                (
                    len(movie_batch_np),
                ),
                user_index,
                dtype=torch.long,
                device=device
            )


            predictions = model(
                user_batch,
                movie_batch
            )


            scores.append(
                predictions
                .cpu()
                .numpy()
            )


    scores = np.concatenate(
        scores
    )


    # --------------------------------------------------------
    # FIND TOP-N
    # --------------------------------------------------------

    top_indices = np.argsort(
        scores
    )[::-1][:top_n]


    top_movie_indexes = (
        candidate_movies[
            top_indices
        ]
    )

    top_scores = (
        scores[
            top_indices
        ]
    )


    # --------------------------------------------------------
    # MAP movieIndex → movieId
    # --------------------------------------------------------

    recommendations = pd.DataFrame({

        "movieIndex":
            top_movie_indexes,

        "predicted_score":
            top_scores
    })


    recommendations = (
        recommendations.merge(
            movie_mapping[
                [
                    "movieIndex",
                    "movieId",
                    "rating_count",
                    "mean_rating"
                ]
            ],
            on="movieIndex",
            how="left"
        )
    )

    recommendations = recommendations.merge(
        movies_catalog[
            [
                "movieId",
                "title",
                "genres"
            ]
        ],
        on="movieId",
        how="left"
    )


    # --------------------------------------------------------
    # DISPLAY SCORE ON MOVIELENS SCALE
    # --------------------------------------------------------

    recommendations[
        "predicted_rating"
    ] = np.clip(
        recommendations[
            "predicted_score"
        ],
        0.5,
        5.0
    )


    # return recommendations[
    #     [
    #         "movieId",
    #         "movieIndex",
    #         "predicted_rating",
    #         "rating_count",
    #         "mean_rating"
    #     ]
    # ]

    return recommendations[
        [
            "movieId",
            "title",
            "genres",
            "predicted_rating",
            "rating_count",
            "mean_rating"
        ]
    ]


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    USER_ID = 1

    history = get_user_history(
        USER_ID,
        top_n=15
    )

    print("\n" + "=" * 70)
    print(f"HIGHEST-RATED MOVIES FOR USER {USER_ID}")
    print("=" * 70)

    print(
        history.to_string(
            index=False
        )
    )


    recommendations = recommend_for_user(
        USER_ID,
        top_n=10
    )

    print("\n" + "=" * 70)
    print(f"TOP RECOMMENDATIONS FOR USER {USER_ID}")
    print("=" * 70)

    print(
        recommendations.to_string(
            index=False
        )
    )