from pathlib import Path

import numpy as np
import pandas as pd
import torch


# ======================================================================
# PATHS
# ======================================================================

ML_ROOT = Path(__file__).resolve().parents[1]

CF_MODEL_DIR = ML_ROOT / "models" / "collaborative"
CF_FEATURE_DIR = ML_ROOT / "data" / "features" / "collaborative"
PROCESSED_DIR = ML_ROOT / "data" / "processed"
OUTPUT_DIR = PROCESSED_DIR / "testing"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


CHECKPOINT_PATH = (
    CF_MODEL_DIR / "matrix_factorization_best.pt"
)

SEEN_MOVIES_PATH = (
    CF_MODEL_DIR / "cf_seen_movie_indexes.npy"
)

USER_MAPPING_PATH = (
    CF_FEATURE_DIR / "cf_user_mapping.csv"
)

MOVIE_MAPPING_PATH = (
    CF_FEATURE_DIR / "cf_movie_mapping.csv"
)

INTERACTIONS_PATH = (
    CF_FEATURE_DIR / "cf_interactions.csv"
)

MOVIES_PATH = (
    PROCESSED_DIR / "movies_clean_final.csv"
)


# ======================================================================
# TEST SETTINGS
# ======================================================================

TEST_USER_IDS = [
    7382,       # ~15 ratings
    1,          # 141 ratings
    151,        # 500 ratings
    156429,     # ~2000 ratings
]

TOP_K = 10

RATING_MIN = 0.5
RATING_MAX = 5.0


# ======================================================================
# START
# ======================================================================

print("=" * 100)
print("3.9.3 COLLABORATIVE FILTERING RECOMMENDATION TEST")
print("=" * 100)


# ======================================================================
# CHECK FILES
# ======================================================================

required_files = [
    CHECKPOINT_PATH,
    SEEN_MOVIES_PATH,
    USER_MAPPING_PATH,
    MOVIE_MAPPING_PATH,
    INTERACTIONS_PATH,
    MOVIES_PATH,
]

missing_files = [
    path
    for path in required_files
    if not path.exists()
]

if missing_files:

    print("\nMissing required files:")

    for path in missing_files:
        print(path)

    raise FileNotFoundError(
        "One or more collaborative filtering artifacts are missing."
    )


# ======================================================================
# LOAD MAPPINGS
# ======================================================================

print("\n" + "=" * 100)
print("LOADING MAPPINGS")
print("=" * 100)

user_mapping = pd.read_csv(USER_MAPPING_PATH)
movie_mapping = pd.read_csv(MOVIE_MAPPING_PATH)


print(f"Users:  {len(user_mapping):,}")
print(f"Movies: {len(movie_mapping):,}")


required_user_columns = {
    "userId",
    "userIndex",
}

required_movie_columns = {
    "movieId",
    "movieIndex",
}


assert required_user_columns.issubset(user_mapping.columns), (
    f"Missing user mapping columns. "
    f"Found: {user_mapping.columns.tolist()}"
)

assert required_movie_columns.issubset(movie_mapping.columns), (
    f"Missing movie mapping columns. "
    f"Found: {movie_mapping.columns.tolist()}"
)


assert user_mapping["userId"].is_unique
assert user_mapping["userIndex"].is_unique

assert movie_mapping["movieId"].is_unique
assert movie_mapping["movieIndex"].is_unique


# ======================================================================
# CHECK CONTIGUOUS INDEXES
# ======================================================================

user_indexes = np.sort(
    user_mapping["userIndex"].to_numpy()
)

movie_indexes = np.sort(
    movie_mapping["movieIndex"].to_numpy()
)


users_contiguous = np.array_equal(
    user_indexes,
    np.arange(len(user_mapping))
)

movies_contiguous = np.array_equal(
    movie_indexes,
    np.arange(len(movie_mapping))
)


print(f"User indexes contiguous:  {users_contiguous}")
print(f"Movie indexes contiguous: {movies_contiguous}")


assert users_contiguous, (
    "User indexes are not contiguous."
)

assert movies_contiguous, (
    "Movie indexes are not contiguous."
)


# ======================================================================
# LOAD CHECKPOINT
# ======================================================================

print("\n" + "=" * 100)
print("CHECKPOINT VALIDATION")
print("=" * 100)

checkpoint = torch.load(
    CHECKPOINT_PATH,
    map_location="cpu",
    weights_only=False,
)


print("Checkpoint keys:")
print(list(checkpoint.keys()))


required_checkpoint_keys = {
    "model_state_dict",
    "num_users",
    "num_movies",
    "embedding_dim",
    "global_mean",
}

missing_checkpoint_keys = (
    required_checkpoint_keys -
    set(checkpoint.keys())
)

assert not missing_checkpoint_keys, (
    f"Missing checkpoint keys: "
    f"{missing_checkpoint_keys}"
)


state = checkpoint["model_state_dict"]

num_users = int(checkpoint["num_users"])
num_movies = int(checkpoint["num_movies"])
embedding_dim = int(checkpoint["embedding_dim"])
checkpoint_global_mean = float(
    checkpoint["global_mean"]
)


print(f"\nnum_users:     {num_users:,}")
print(f"num_movies:    {num_movies:,}")
print(f"embedding_dim: {embedding_dim}")
print(f"global_mean:   {checkpoint_global_mean:.6f}")

if "epoch" in checkpoint:
    print(f"best epoch:    {checkpoint['epoch']}")

if "validation_rmse" in checkpoint:
    print(
        f"validation RMSE: "
        f"{checkpoint['validation_rmse']:.6f}"
    )


# ======================================================================
# VALIDATE CHECKPOINT SHAPES
# ======================================================================

required_state_keys = {
    "user_embedding.weight",
    "movie_embedding.weight",
    "user_bias.weight",
    "movie_bias.weight",
    "global_mean",
}

missing_state_keys = (
    required_state_keys -
    set(state.keys())
)

assert not missing_state_keys, (
    f"Missing state tensors: {missing_state_keys}"
)


user_embedding = (
    state["user_embedding.weight"]
    .detach()
    .cpu()
    .float()
)

movie_embedding = (
    state["movie_embedding.weight"]
    .detach()
    .cpu()
    .float()
)

user_bias = (
    state["user_bias.weight"]
    .detach()
    .cpu()
    .float()
    .reshape(-1)
)

movie_bias = (
    state["movie_bias.weight"]
    .detach()
    .cpu()
    .float()
    .reshape(-1)
)

state_global_mean = float(
    state["global_mean"]
    .detach()
    .cpu()
    .item()
)


print("\nState tensor shapes:")
print(
    "user_embedding:",
    tuple(user_embedding.shape)
)

print(
    "movie_embedding:",
    tuple(movie_embedding.shape)
)

print(
    "user_bias:",
    tuple(user_bias.shape)
)

print(
    "movie_bias:",
    tuple(movie_bias.shape)
)

print(
    "state global mean:",
    state_global_mean
)


assert user_embedding.shape == (
    num_users,
    embedding_dim,
)

assert movie_embedding.shape == (
    num_movies,
    embedding_dim,
)

assert len(user_bias) == num_users
assert len(movie_bias) == num_movies


assert num_users == len(user_mapping), (
    "Checkpoint user count does not match "
    "user mapping."
)

assert num_movies == len(movie_mapping), (
    "Checkpoint movie count does not match "
    "movie mapping."
)


assert np.isclose(
    checkpoint_global_mean,
    state_global_mean,
    atol=1e-6,
), (
    "Checkpoint global mean differs from "
    "model state global mean."
)


print("\nCheckpoint integrity passed.")


# ======================================================================
# LOAD TRAIN-SUPPORTED MOVIE INDEXES
# ======================================================================

seen_movie_indexes = np.load(
    SEEN_MOVIES_PATH
).astype(np.int64)


seen_movie_indexes = np.unique(
    seen_movie_indexes
)


assert len(seen_movie_indexes) > 0

assert seen_movie_indexes.min() >= 0
assert seen_movie_indexes.max() < num_movies


print(
    "\nCF-supported movie indexes:",
    f"{len(seen_movie_indexes):,}"
)


# ======================================================================
# BUILD ID LOOKUPS
# ======================================================================

user_id_to_index = dict(
    zip(
        user_mapping["userId"].astype(int),
        user_mapping["userIndex"].astype(int),
    )
)


movie_id_by_index = np.full(
    num_movies,
    -1,
    dtype=np.int64,
)

movie_id_by_index[
    movie_mapping["movieIndex"].astype(int).to_numpy()
] = (
    movie_mapping["movieId"]
    .astype(int)
    .to_numpy()
)


# ======================================================================
# LOAD MOVIE TITLES
# ======================================================================

movies = pd.read_csv(
    MOVIES_PATH,
    low_memory=False,
)


if "title" in movies.columns:
    title_column = "title"

elif "title_x" in movies.columns:
    title_column = "title_x"

else:
    raise ValueError(
        "Could not find movie title column."
    )


movie_title_lookup = (
    movies[
        ["movieId", title_column]
    ]
    .drop_duplicates("movieId")
    .set_index("movieId")[title_column]
    .to_dict()
)


# ======================================================================
# RESOLVE TEST USERS
# ======================================================================

print("\n" + "=" * 100)
print("TEST USER VALIDATION")
print("=" * 100)


valid_test_users = []

for user_id in TEST_USER_IDS:

    if user_id not in user_id_to_index:

        print(
            f"WARNING - userId {user_id} "
            f"is not present in CF mapping."
        )

        continue

    user_index = user_id_to_index[user_id]

    valid_test_users.append(
        (user_id, user_index)
    )

    print(
        f"userId {user_id:<8} "
        f"-> userIndex {user_index}"
    )


assert len(valid_test_users) >= 2, (
    "Need at least two valid test users."
)


target_user_indexes = {
    user_index
    for _, user_index in valid_test_users
}


# ======================================================================
# LOAD ONLY TEST USERS' INTERACTIONS
# ======================================================================

print("\n" + "=" * 100)
print("LOADING TEST USER HISTORIES")
print("=" * 100)

interaction_parts = []


for chunk in pd.read_csv(
    INTERACTIONS_PATH,
    usecols=[
        "userIndex",
        "movieIndex",
        "rating",
    ],
    chunksize=1_000_000,
):

    subset = chunk[
        chunk["userIndex"].isin(
            target_user_indexes
        )
    ]

    if not subset.empty:
        interaction_parts.append(
            subset.copy()
        )


if not interaction_parts:
    raise RuntimeError(
        "No interactions found for test users."
    )


test_interactions = pd.concat(
    interaction_parts,
    ignore_index=True,
)


test_interactions["userIndex"] = (
    test_interactions["userIndex"]
    .astype(np.int64)
)

test_interactions["movieIndex"] = (
    test_interactions["movieIndex"]
    .astype(np.int64)
)

test_interactions["rating"] = (
    test_interactions["rating"]
    .astype(np.float32)
)


print(
    "Loaded test interactions:",
    f"{len(test_interactions):,}"
)


# ======================================================================
# USER HISTORY LOOKUP
# ======================================================================

rated_movies_by_user = {}

for user_id, user_index in valid_test_users:

    history = test_interactions[
        test_interactions["userIndex"]
        == user_index
    ]

    rated_movie_indexes = set(
        history["movieIndex"]
        .astype(int)
        .tolist()
    )

    rated_movies_by_user[user_id] = (
        rated_movie_indexes
    )

    print(
        f"userId {user_id:<8} | "
        f"history: {len(history):,} ratings"
    )


# ======================================================================
# COLLABORATIVE SCORE FUNCTION
# ======================================================================

def predict_cf_scores(
    user_index,
    candidate_movie_indexes,
):
    """
    Matrix-factorization prediction:

    global_mean
    + user_bias
    + movie_bias
    + dot(user_embedding, movie_embedding)
    """

    candidate_movie_indexes = np.asarray(
        candidate_movie_indexes,
        dtype=np.int64,
    )

    candidate_tensor = torch.from_numpy(
        candidate_movie_indexes
    ).long()


    user_vector = user_embedding[
        user_index
    ]


    candidate_vectors = movie_embedding[
        candidate_tensor
    ]


    dot_products = torch.mv(
        candidate_vectors,
        user_vector,
    )


    scores = (
        state_global_mean
        + user_bias[user_index]
        + movie_bias[candidate_tensor]
        + dot_products
    )


    scores = torch.clamp(
        scores,
        min=RATING_MIN,
        max=RATING_MAX,
    )


    return (
        scores
        .detach()
        .cpu()
        .numpy()
        .astype(np.float32)
    )


# ======================================================================
# RECOMMENDATION FUNCTION
# ======================================================================

def recommend_for_user(
    user_id,
    top_k=10,
):

    if user_id not in user_id_to_index:
        raise ValueError(
            f"Unknown userId: {user_id}"
        )


    user_index = (
        user_id_to_index[user_id]
    )


    rated_indexes = (
        rated_movies_by_user[user_id]
    )


    candidate_indexes = np.array(
        [
            idx
            for idx in seen_movie_indexes
            if idx not in rated_indexes
        ],
        dtype=np.int64,
    )


    if len(candidate_indexes) == 0:
        raise RuntimeError(
            f"No candidate movies for "
            f"userId {user_id}"
        )


    scores = predict_cf_scores(
        user_index,
        candidate_indexes,
    )


    candidate_count = min(
        top_k,
        len(scores),
    )


    top_positions = np.argpartition(
        scores,
        -candidate_count,
    )[-candidate_count:]


    top_positions = top_positions[
        np.argsort(
            scores[top_positions]
        )[::-1]
    ]


    selected_indexes = (
        candidate_indexes[
            top_positions
        ]
    )

    selected_scores = (
        scores[
            top_positions
        ]
    )


    movie_ids = (
        movie_id_by_index[
            selected_indexes
        ]
    )


    results = pd.DataFrame(
        {
            "movieIndex": selected_indexes,
            "movieId": movie_ids,
            "predictedRating": selected_scores,
        }
    )


    results["title"] = (
        results["movieId"]
        .map(movie_title_lookup)
        .fillna("<title unavailable>")
    )


    results.insert(
        0,
        "rank",
        np.arange(
            1,
            len(results) + 1
        ),
    )


    return results


# ======================================================================
# VALIDATION FUNCTION
# ======================================================================

def validate_cf_recommendations(
    user_id,
    recommendations,
):

    failures = []


    if len(recommendations) != TOP_K:

        failures.append(
            f"Expected {TOP_K} recommendations, "
            f"got {len(recommendations)}."
        )


    if recommendations[
        "movieId"
    ].duplicated().any():

        failures.append(
            "Duplicate movie recommendations found."
        )


    scores = recommendations[
        "predictedRating"
    ].to_numpy()


    if not np.isfinite(scores).all():

        failures.append(
            "Non-finite prediction values found."
        )


    if np.any(scores < RATING_MIN - 1e-6):

        failures.append(
            "Prediction below 0.5 found."
        )


    if np.any(scores > RATING_MAX + 1e-6):

        failures.append(
            "Prediction above 5.0 found."
        )


    if len(scores) > 1:

        if not np.all(
            scores[:-1]
            >= scores[1:] - 1e-8
        ):

            failures.append(
                "Recommendations are not "
                "sorted descending."
            )


    rated_indexes = (
        rated_movies_by_user[user_id]
    )


    recommended_indexes = set(
        recommendations[
            "movieIndex"
        ]
        .astype(int)
        .tolist()
    )


    overlap = (
        rated_indexes
        & recommended_indexes
    )


    if overlap:

        failures.append(
            "One or more already-rated movies "
            "were recommended."
        )


    return failures


# ======================================================================
# RUN TESTS
# ======================================================================

all_results = []

top_movie_sets = {}

overall_pass = True


for user_id, user_index in valid_test_users:

    print(
        "\n"
        + "=" * 100
    )

    print(
        f"USER {user_id}"
    )

    print(
        f"userIndex: {user_index}"
    )

    print(
        f"History size: "
        f"{len(rated_movies_by_user[user_id]):,}"
    )

    print(
        "=" * 100
    )


    recommendations = recommend_for_user(
        user_id,
        TOP_K,
    )


    failures = validate_cf_recommendations(
        user_id,
        recommendations,
    )


    print(
        recommendations[
            [
                "rank",
                "movieId",
                "title",
                "predictedRating",
            ]
        ].to_string(
            index=False,
            formatters={
                "predictedRating":
                    lambda x: f"{x:.4f}"
            },
        )
    )


    print("\nAutomated checks:")


    if failures:

        overall_pass = False

        for failure in failures:
            print(
                f"  FAIL - {failure}"
            )

    else:

        print(
            "  PASS - returned Top-K recommendations"
        )

        print(
            "  PASS - already-rated movies excluded"
        )

        print(
            "  PASS - no duplicate recommendations"
        )

        print(
            "  PASS - all predictions finite"
        )

        print(
            "  PASS - predictions within [0.5, 5.0]"
        )

        print(
            "  PASS - recommendations sorted descending"
        )


    top_movie_sets[user_id] = set(
        recommendations[
            "movieId"
        ]
        .astype(int)
        .tolist()
    )


    recommendations.insert(
        0,
        "userId",
        user_id,
    )


    all_results.append(
        recommendations
    )


# ======================================================================
# PERSONALIZATION TEST
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "PERSONALIZATION / USER DIFFERENCE TEST"
)

print(
    "=" * 100
)


user_ids = list(
    top_movie_sets.keys()
)


personalization_pass = True


for i in range(
    len(user_ids)
):

    for j in range(
        i + 1,
        len(user_ids),
    ):

        user_a = user_ids[i]
        user_b = user_ids[j]


        set_a = top_movie_sets[user_a]
        set_b = top_movie_sets[user_b]


        overlap = (
            set_a & set_b
        )


        overlap_count = len(
            overlap
        )


        union = (
            set_a | set_b
        )


        jaccard = (
            overlap_count / len(union)
            if union
            else 0.0
        )


        print(
            f"User {user_a:<8} "
            f"vs User {user_b:<8} | "
            f"Top-{TOP_K} overlap: "
            f"{overlap_count}/{TOP_K} | "
            f"Jaccard: {jaccard:.3f}"
        )


        if set_a == set_b:

            personalization_pass = False


if personalization_pass:

    print(
        "\nPASS - Users do not receive "
        "identical Top-K lists."
    )

else:

    print(
        "\nFAIL - At least two users received "
        "identical Top-K recommendations."
    )

    overall_pass = False


# ======================================================================
# USER 1 REGRESSION CHECK
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "USER 1 REGRESSION CHECK"
)

print(
    "=" * 100
)


if 1 in top_movie_sets:

    user1_results = recommend_for_user(
        1,
        TOP_K,
    )


    top_row = user1_results.iloc[0]


    print(
        f"Top movieId: "
        f"{int(top_row['movieId'])}"
    )

    print(
        f"Top title: "
        f"{top_row['title']}"
    )

    print(
        f"Prediction: "
        f"{top_row['predictedRating']:.4f}"
    )


    expected_movie_id = 171011

    expected_prediction = 4.2609


    movie_match = (
        int(top_row["movieId"])
        == expected_movie_id
    )


    score_match = np.isclose(
        float(
            top_row["predictedRating"]
        ),
        expected_prediction,
        atol=1e-3,
    )


    if movie_match:

        print(
            "PASS - Top movie matches "
            "previous CF result."
        )

    else:

        print(
            "WARNING - Top movie differs "
            "from previous CF result."
        )


    if score_match:

        print(
            "PASS - Prediction matches "
            "previous CF baseline."
        )

    else:

        print(
            "WARNING - Prediction differs "
            "from previous CF baseline."
        )


# ======================================================================
# SAVE RESULTS
# ======================================================================

if all_results:

    final_results = pd.concat(
        all_results,
        ignore_index=True,
    )


    output_path = (
        OUTPUT_DIR
        / "collaborative_test_results.csv"
    )


    final_results.to_csv(
        output_path,
        index=False,
    )


    print("\nSaved:")
    print(output_path)


# ======================================================================
# FINAL
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "3.9.3 AUTOMATED TEST RESULT"
)

print(
    "=" * 100
)


if overall_pass:

    print(
        "PASS - All collaborative "
        "recommendation tests passed."
    )

else:

    print(
        "FAIL - One or more collaborative "
        "recommendation tests failed."
    )


print(
    "\nNOTE:"
    "\nThis test validates recommendation behavior."
    "\nOffline ranking accuracy will be tested "
    "separately in the Top-K evaluation step."
)