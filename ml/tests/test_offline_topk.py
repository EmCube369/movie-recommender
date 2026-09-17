from pathlib import Path
from collections import defaultdict
import pickle

import numpy as np
import pandas as pd
import torch

from scipy.sparse import load_npz, csr_matrix
from sklearn.preprocessing import normalize


# ======================================================================
# CONFIGURATION
# ======================================================================

RANDOM_SEED = 42

NUM_EVAL_USERS = 500
INITIAL_USER_SAMPLE = 2000
NUM_NEGATIVES = 1000

TOP_K = 10

RELEVANCE_THRESHOLD = 4.0
POSITIVE_PROFILE_THRESHOLD = 4.0

MIN_TRAIN_INTERACTIONS = 10

CF_WEIGHT = 0.50
CONTENT_WEIGHT = 0.35
SENTIMENT_WEIGHT = 0.15

NEUTRAL_SENTIMENT = 0.50

# Final Phase 3.8 content normalization.
CONTENT_NORMALIZATION_MAX = 0.31


# ======================================================================
# PATHS
# ======================================================================

ML_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = ML_ROOT / "data" / "processed"

CF_FEATURE_DIR = (
    ML_ROOT
    / "data"
    / "features"
    / "collaborative"
)

CF_MODEL_DIR = (
    ML_ROOT
    / "models"
    / "collaborative"
)

CONTENT_DIR = (
    ML_ROOT
    / "models"
    / "content_based"
)

SENTIMENT_DIR = (
    PROCESSED_DIR
    / "sentiment"
)

OUTPUT_DIR = (
    PROCESSED_DIR
    / "testing"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ======================================================================
# MAIN ARTIFACT PATHS
# ======================================================================

USER_MAPPING_PATH = (
    CF_FEATURE_DIR
    / "cf_user_mapping.csv"
)

MOVIE_MAPPING_PATH = (
    CF_FEATURE_DIR
    / "cf_movie_mapping.csv"
)

CF_MODEL_PATH = (
    CF_MODEL_DIR
    / "matrix_factorization_best.pt"
)

CF_SEEN_PATH = (
    CF_MODEL_DIR
    / "cf_seen_movie_indexes.npy"
)

CONTENT_MAPPING_PATH = (
    CONTENT_DIR
    / "movie_id_to_index.pkl"
)

CONTENT_WEIGHTS_PATH = (
    CONTENT_DIR
    / "content_weights.pkl"
)

SENTIMENT_PATH = (
    SENTIMENT_DIR
    / "movie_sentiment_final.csv"
)


CONTENT_MATRIX_PATHS = {
    "genre":
        CONTENT_DIR / "genre_matrix.npz",

    "keyword":
        CONTENT_DIR / "keyword_matrix.npz",

    "director":
        CONTENT_DIR / "director_matrix.npz",

    "cast":
        CONTENT_DIR / "cast_matrix.npz",

    "overview":
        CONTENT_DIR / "overview_matrix.npz",

    "tagline":
        CONTENT_DIR / "tagline_matrix.npz",
}


# ======================================================================
# FIND SPLIT FILES
# ======================================================================

def resolve_split_file(split, kind):
    """
    Resolve split .npy files without assuming the exact
    naming convention used during Phase 3.6.
    """

    possible_names = {
        "user": [
            f"{split}_user_indexes.npy",
            f"{split}_user_indices.npy",
            f"{split}_user_idx.npy",
            f"{split}_users.npy",
        ],

        "movie": [
            f"{split}_movie_indexes.npy",
            f"{split}_movie_indices.npy",
            f"{split}_movie_idx.npy",
            f"{split}_movies.npy",
        ],

        "rating": [
            f"{split}_ratings.npy",
            f"{split}_rating.npy",
        ],
    }


    all_npy_files = list(
        CF_FEATURE_DIR.rglob("*.npy")
    )


    # --------------------------------------------------------------
    # Try exact filename first.
    # --------------------------------------------------------------

    for expected_name in possible_names[kind]:

        exact_matches = [
            path
            for path in all_npy_files
            if path.name.lower()
            == expected_name.lower()
        ]

        if len(exact_matches) == 1:
            return exact_matches[0]

        if len(exact_matches) > 1:

            raise RuntimeError(
                f"Multiple files found for "
                f"{split}/{kind}:\n"
                + "\n".join(
                    str(path)
                    for path
                    in exact_matches
                )
            )


    # --------------------------------------------------------------
    # Loose fallback.
    # --------------------------------------------------------------

    kind_tokens = {
        "user": ["user"],
        "movie": ["movie"],
        "rating": ["rating"],
    }


    loose_matches = []


    for path in all_npy_files:

        stem = path.stem.lower()

        if split.lower() not in stem:
            continue

        if any(
            token in stem
            for token in kind_tokens[kind]
        ):

            loose_matches.append(
                path
            )


    if len(loose_matches) == 1:
        return loose_matches[0]


    if len(loose_matches) > 1:

        raise RuntimeError(
            f"Could not uniquely resolve "
            f"{split}/{kind}.\n"
            f"Candidates:\n"
            + "\n".join(
                str(path)
                for path
                in loose_matches
            )
        )


    raise FileNotFoundError(
        f"Could not find {split} {kind} "
        f"split file under:\n"
        f"{CF_FEATURE_DIR}"
    )


# ======================================================================
# RESOLVE TRAIN / VALIDATION / TEST
# ======================================================================

TRAIN_USER_PATH = resolve_split_file(
    "train",
    "user",
)

TRAIN_MOVIE_PATH = resolve_split_file(
    "train",
    "movie",
)

TRAIN_RATING_PATH = resolve_split_file(
    "train",
    "rating",
)


VAL_USER_PATH = resolve_split_file(
    "val",
    "user",
)

VAL_MOVIE_PATH = resolve_split_file(
    "val",
    "movie",
)

VAL_RATING_PATH = resolve_split_file(
    "val",
    "rating",
)


TEST_USER_PATH = resolve_split_file(
    "test",
    "user",
)

TEST_MOVIE_PATH = resolve_split_file(
    "test",
    "movie",
)

TEST_RATING_PATH = resolve_split_file(
    "test",
    "rating",
)


# ======================================================================
# START
# ======================================================================

print("=" * 110)
print("3.9.6 OFFLINE TOP-K RECOMMENDATION EVALUATION")
print("=" * 110)

print("\nEvaluation settings:")

print(
    f"Target users:          "
    f"{NUM_EVAL_USERS:,}"
)

print(
    f"Negative samples/user: "
    f"{NUM_NEGATIVES:,}"
)

print(
    f"Top-K:                 "
    f"{TOP_K}"
)

print(
    f"Relevant rating:       "
    f">= {RELEVANCE_THRESHOLD}"
)

print(
    f"Random seed:           "
    f"{RANDOM_SEED}"
)


# ======================================================================
# SHOW SPLIT PATHS
# ======================================================================

print("\nResolved split files:")

print(
    "Train users:  ",
    TRAIN_USER_PATH
)

print(
    "Train movies: ",
    TRAIN_MOVIE_PATH
)

print(
    "Train ratings:",
    TRAIN_RATING_PATH
)

print(
    "Val users:    ",
    VAL_USER_PATH
)

print(
    "Val movies:   ",
    VAL_MOVIE_PATH
)

print(
    "Val ratings:  ",
    VAL_RATING_PATH
)

print(
    "Test users:   ",
    TEST_USER_PATH
)

print(
    "Test movies:  ",
    TEST_MOVIE_PATH
)

print(
    "Test ratings: ",
    TEST_RATING_PATH
)


# ======================================================================
# MEMORY-MAP SPLITS
# ======================================================================

train_users = np.load(
    TRAIN_USER_PATH,
    mmap_mode="r",
)

train_movies = np.load(
    TRAIN_MOVIE_PATH,
    mmap_mode="r",
)

train_ratings = np.load(
    TRAIN_RATING_PATH,
    mmap_mode="r",
)


val_users = np.load(
    VAL_USER_PATH,
    mmap_mode="r",
)

val_movies = np.load(
    VAL_MOVIE_PATH,
    mmap_mode="r",
)

val_ratings = np.load(
    VAL_RATING_PATH,
    mmap_mode="r",
)


test_users = np.load(
    TEST_USER_PATH,
    mmap_mode="r",
)

test_movies = np.load(
    TEST_MOVIE_PATH,
    mmap_mode="r",
)

test_ratings = np.load(
    TEST_RATING_PATH,
    mmap_mode="r",
)


assert (
    len(train_users)
    == len(train_movies)
    == len(train_ratings)
)

assert (
    len(val_users)
    == len(val_movies)
    == len(val_ratings)
)

assert (
    len(test_users)
    == len(test_movies)
    == len(test_ratings)
)


print("\nSplit sizes:")

print(
    f"Train: {len(train_users):,}"
)

print(
    f"Val:   {len(val_users):,}"
)

print(
    f"Test:  {len(test_users):,}"
)


# ======================================================================
# LOAD MAPPINGS
# ======================================================================

print("\nLoading mappings...")


user_mapping = pd.read_csv(
    USER_MAPPING_PATH
)

movie_mapping = pd.read_csv(
    MOVIE_MAPPING_PATH
)


num_users = len(
    user_mapping
)

num_movies = len(
    movie_mapping
)


user_id_by_index = np.full(
    num_users,
    -1,
    dtype=np.int64,
)

user_id_by_index[
    user_mapping[
        "userIndex"
    ].astype(int).to_numpy()
] = (
    user_mapping[
        "userId"
    ].astype(int).to_numpy()
)


movie_id_by_index = np.full(
    num_movies,
    -1,
    dtype=np.int64,
)

movie_id_by_index[
    movie_mapping[
        "movieIndex"
    ].astype(int).to_numpy()
] = (
    movie_mapping[
        "movieId"
    ].astype(int).to_numpy()
)


print(
    f"Users:  {num_users:,}"
)

print(
    f"Movies: {num_movies:,}"
)


# ======================================================================
# LOAD CF MODEL
# ======================================================================

print("\nLoading collaborative model...")


checkpoint = torch.load(
    CF_MODEL_PATH,
    map_location="cpu",
    weights_only=False,
)

state = checkpoint[
    "model_state_dict"
]


user_embedding = (
    state[
        "user_embedding.weight"
    ]
    .detach()
    .cpu()
    .float()
)

movie_embedding = (
    state[
        "movie_embedding.weight"
    ]
    .detach()
    .cpu()
    .float()
)

user_bias = (
    state[
        "user_bias.weight"
    ]
    .detach()
    .cpu()
    .float()
    .reshape(-1)
)

movie_bias = (
    state[
        "movie_bias.weight"
    ]
    .detach()
    .cpu()
    .float()
    .reshape(-1)
)

global_mean = float(
    state[
        "global_mean"
    ]
    .detach()
    .cpu()
    .item()
)


print(
    f"Global mean: "
    f"{global_mean:.6f}"
)

print(
    f"Best epoch: "
    f"{checkpoint.get('epoch')}"
)


# ======================================================================
# LOAD CONTENT ARTIFACTS
# ======================================================================

print("\nLoading content artifacts...")


with open(
    CONTENT_MAPPING_PATH,
    "rb",
) as f:

    raw_content_mapping = (
        pickle.load(f)
    )


content_index_by_movie_id = {
    int(movie_id): int(index)
    for movie_id, index
    in raw_content_mapping.items()
}


with open(
    CONTENT_WEIGHTS_PATH,
    "rb",
) as f:

    content_weights = (
        pickle.load(f)
    )


content_matrices = {
    name:
        load_npz(path).tocsr()

    for name, path
    in CONTENT_MATRIX_PATHS.items()
}


print(
    f"Content movies: "
    f"{len(content_index_by_movie_id):,}"
)


# ======================================================================
# LOAD SENTIMENT
# ======================================================================

print("\nLoading sentiment...")


sentiment = pd.read_csv(
    SENTIMENT_PATH,
    low_memory=False,
)


sentiment[
    "sentimentNormalized"
] = np.clip(
    (
        sentiment[
            "adjustedSentimentScore"
        ].astype(float)
        + 1.0
    )
    / 2.0,
    0.0,
    1.0,
)


sentiment_lookup = dict(
    zip(
        sentiment[
            "movieId"
        ].astype(int),

        sentiment[
            "sentimentNormalized"
        ].astype(float),
    )
)


print(
    f"Sentiment movies: "
    f"{len(sentiment_lookup):,}"
)


# ======================================================================
# BUILD SUPPORTED MOVIE SET
# ======================================================================

cf_supported_indexes = np.unique(
    np.load(
        CF_SEEN_PATH
    ).astype(np.int64)
)


supported_indexes_list = []


for movie_index in cf_supported_indexes:

    movie_id = int(
        movie_id_by_index[
            movie_index
        ]
    )

    if (
        movie_id
        in content_index_by_movie_id
    ):

        supported_indexes_list.append(
            int(movie_index)
        )


supported_movie_indexes = np.asarray(
    supported_indexes_list,
    dtype=np.int64,
)


supported_mask = np.zeros(
    num_movies,
    dtype=bool,
)

supported_mask[
    supported_movie_indexes
] = True


print(
    "\nFully supported candidate movies: "
    f"{len(supported_movie_indexes):,}"
)


# ======================================================================
# FIND USERS WITH RELEVANT TEST ITEMS
# ======================================================================

print("\nFinding eligible test users...")


test_supported = (
    supported_mask[
        np.asarray(
            test_movies,
            dtype=np.int64,
        )
    ]
)


test_relevant_mask = (
    (
        np.asarray(
            test_ratings
        )
        >= RELEVANCE_THRESHOLD
    )
    &
    test_supported
)


eligible_users = np.unique(
    np.asarray(
        test_users[
            test_relevant_mask
        ],
        dtype=np.int64,
    )
)


print(
    f"Users with >=1 supported "
    f"relevant test movie: "
    f"{len(eligible_users):,}"
)


# ======================================================================
# SAMPLE INITIAL USER POOL
# ======================================================================

rng = np.random.default_rng(
    RANDOM_SEED
)


eligible_users = (
    eligible_users.copy()
)

rng.shuffle(
    eligible_users
)


initial_count = min(
    INITIAL_USER_SAMPLE,
    len(eligible_users),
)


candidate_users = (
    eligible_users[
        :initial_count
    ]
)


print(
    f"Initial sampled users: "
    f"{len(candidate_users):,}"
)


# ======================================================================
# COLLECT INTERACTIONS FOR TARGET USERS
# ======================================================================

def collect_user_interactions(
    users_array,
    movies_array,
    ratings_array,
    target_users,
    chunk_size=2_000_000,
):

    """
    Read a large memory-mapped split in chunks and
    retain interactions only for target users.
    """

    target_users = np.asarray(
        target_users,
        dtype=np.int64,
    )


    movie_parts = defaultdict(
        list
    )

    rating_parts = defaultdict(
        list
    )


    total = len(
        users_array
    )


    for start in range(
        0,
        total,
        chunk_size,
    ):

        end = min(
            start + chunk_size,
            total,
        )


        chunk_users = np.asarray(
            users_array[
                start:end
            ],
            dtype=np.int64,
        )


        mask = np.isin(
            chunk_users,
            target_users,
        )


        if not mask.any():
            continue


        filtered_users = (
            chunk_users[
                mask
            ]
        )


        filtered_movies = np.asarray(
            movies_array[
                start:end
            ],
            dtype=np.int64,
        )[
            mask
        ]


        filtered_ratings = np.asarray(
            ratings_array[
                start:end
            ],
            dtype=np.float32,
        )[
            mask
        ]


        unique_users = np.unique(
            filtered_users
        )


        for user_index in unique_users:

            user_mask = (
                filtered_users
                == user_index
            )


            movie_parts[
                int(user_index)
            ].append(
                filtered_movies[
                    user_mask
                ].copy()
            )


            rating_parts[
                int(user_index)
            ].append(
                filtered_ratings[
                    user_mask
                ].copy()
            )


    result = {}


    for user_index in target_users:

        user_index = int(
            user_index
        )


        if (
            user_index
            not in movie_parts
        ):

            result[
                user_index
            ] = (
                np.empty(
                    0,
                    dtype=np.int64,
                ),
                np.empty(
                    0,
                    dtype=np.float32,
                ),
            )

            continue


        result[
            user_index
        ] = (
            np.concatenate(
                movie_parts[
                    user_index
                ]
            ),

            np.concatenate(
                rating_parts[
                    user_index
                ]
            ),
        )


    return result


print(
    "\nCollecting training histories..."
)

train_history = (
    collect_user_interactions(
        train_users,
        train_movies,
        train_ratings,
        candidate_users,
    )
)


print(
    "Collecting validation histories..."
)

val_history = (
    collect_user_interactions(
        val_users,
        val_movies,
        val_ratings,
        candidate_users,
    )
)


print(
    "Collecting test histories..."
)

test_history = (
    collect_user_interactions(
        test_users,
        test_movies,
        test_ratings,
        candidate_users,
    )
)


# ======================================================================
# FINAL USER FILTER
# ======================================================================

final_users = []


for user_index in candidate_users:

    user_index = int(
        user_index
    )


    train_movie_idx, train_rating = (
        train_history[
            user_index
        ]
    )


    test_movie_idx, test_rating = (
        test_history[
            user_index
        ]
    )


    if (
        len(train_movie_idx)
        < MIN_TRAIN_INTERACTIONS
    ):

        continue


    train_positive_count = (
        train_rating
        >= POSITIVE_PROFILE_THRESHOLD
    ).sum()


    if train_positive_count == 0:
        continue


    relevant_test = (
        test_movie_idx[
            (
                test_rating
                >= RELEVANCE_THRESHOLD
            )
            &
            supported_mask[
                test_movie_idx
            ]
        ]
    )


    if len(
        np.unique(
            relevant_test
        )
    ) == 0:

        continue


    final_users.append(
        user_index
    )


    if (
        len(final_users)
        >= NUM_EVAL_USERS
    ):

        break


if not final_users:

    raise RuntimeError(
        "No evaluable users found."
    )


print(
    "\nFinal evaluation users: "
    f"{len(final_users):,}"
)


if (
    len(final_users)
    < NUM_EVAL_USERS
):

    print(
        "WARNING - fewer users available "
        "than requested."
    )


# ======================================================================
# SCORE HELPERS
# ======================================================================

def normalize_cf(scores):

    return np.clip(
        (
            scores - 0.5
        )
        / 4.5,
        0.0,
        1.0,
    )


def normalize_content(
    scores,
):

    return np.clip(
        scores
        / CONTENT_NORMALIZATION_MAX,
        0.0,
        1.0,
    )


def predict_cf(
    user_index,
    candidate_movie_indexes,
):

    candidate_tensor = (
        torch.from_numpy(
            candidate_movie_indexes
            .astype(np.int64)
        )
        .long()
    )


    user_vector = (
        user_embedding[
            user_index
        ]
    )


    scores = (
        global_mean
        + user_bias[
            user_index
        ]
        + movie_bias[
            candidate_tensor
        ]
        + torch.mv(
            movie_embedding[
                candidate_tensor
            ],
            user_vector,
        )
    )


    scores = torch.clamp(
        scores,
        0.5,
        5.0,
    )


    return (
        scores
        .detach()
        .cpu()
        .numpy()
        .astype(np.float32)
    )


# ======================================================================
# CONTENT PROFILE FROM TRAINING DATA ONLY
# ======================================================================

def predict_content(
    train_movie_indexes,
    train_rating_values,
    candidate_movie_indexes,
):

    positive_mask = (
        train_rating_values
        >= POSITIVE_PROFILE_THRESHOLD
    )


    positive_cf_indexes = (
        train_movie_indexes[
            positive_mask
        ]
    )


    positive_ratings = (
        train_rating_values[
            positive_mask
        ]
    )


    positive_movie_ids = (
        movie_id_by_index[
            positive_cf_indexes
        ]
    )


    valid_positive_mask = np.array(
        [
            int(movie_id)
            in content_index_by_movie_id

            for movie_id
            in positive_movie_ids
        ],
        dtype=bool,
    )


    positive_movie_ids = (
        positive_movie_ids[
            valid_positive_mask
        ]
    )


    positive_ratings = (
        positive_ratings[
            valid_positive_mask
        ]
    )


    if len(
        positive_movie_ids
    ) == 0:

        return np.zeros(
            len(
                candidate_movie_indexes
            ),
            dtype=np.float32,
        )


    positive_content_indexes = np.array(
        [
            content_index_by_movie_id[
                int(movie_id)
            ]

            for movie_id
            in positive_movie_ids
        ],
        dtype=np.int64,
    )


    candidate_movie_ids = (
        movie_id_by_index[
            candidate_movie_indexes
        ]
    )


    candidate_content_indexes = np.array(
        [
            content_index_by_movie_id[
                int(movie_id)
            ]

            for movie_id
            in candidate_movie_ids
        ],
        dtype=np.int64,
    )


    # --------------------------------------------------------------
    # Exact Phase 3.8 preference weighting.
    #
    # 4.0 -> 1.0
    # 4.5 -> 1.5
    # 5.0 -> 2.0
    # --------------------------------------------------------------

    rating_weights = (
        positive_ratings.astype(
            np.float32
        )
        - 3.0
    )


    total_score = np.zeros(
        len(
            candidate_movie_indexes
        ),
        dtype=np.float32,
    )


    for feature_name, matrix in (
        content_matrices.items()
    ):

        liked_vectors = (
            matrix[
                positive_content_indexes
            ]
        )


        weighted_vectors = (
            liked_vectors.multiply(
                rating_weights[
                    :,
                    None
                ]
            )
        )


        profile = (
            weighted_vectors.sum(
                axis=0
            )
        )


        profile = csr_matrix(
            profile
        )


        profile = normalize(
            profile,
            norm="l2",
        )


        similarities = (
            matrix[
                candidate_content_indexes
            ]
            @ profile.T
        ).toarray().ravel()


        similarities = (
            similarities.astype(
                np.float32
            )
        )


        total_score += (
            float(
                content_weights[
                    feature_name
                ]
            )
            * similarities
        )


    return total_score


# ======================================================================
# SENTIMENT
# ======================================================================

def predict_sentiment(
    candidate_movie_indexes,
):

    movie_ids = (
        movie_id_by_index[
            candidate_movie_indexes
        ]
    )


    return np.asarray(
        [
            sentiment_lookup.get(
                int(movie_id),
                NEUTRAL_SENTIMENT,
            )

            for movie_id
            in movie_ids
        ],
        dtype=np.float32,
    )


# ======================================================================
# RANKING METRICS
# ======================================================================

def get_top_k_positions(
    scores,
    k,
):

    k = min(
        k,
        len(scores),
    )


    top_positions = np.argpartition(
        scores,
        -k,
    )[
        -k:
    ]


    top_positions = (
        top_positions[
            np.argsort(
                scores[
                    top_positions
                ]
            )[::-1]
        ]
    )


    return top_positions


def calculate_metrics(
    candidate_movie_indexes,
    scores,
    relevant_movie_indexes,
    k,
):

    relevant_set = set(
        int(movie_index)
        for movie_index
        in relevant_movie_indexes
    )


    top_positions = (
        get_top_k_positions(
            scores,
            k,
        )
    )


    top_movies = (
        candidate_movie_indexes[
            top_positions
        ]
    )


    relevance_vector = np.array(
        [
            1
            if int(movie_index)
            in relevant_set
            else 0

            for movie_index
            in top_movies
        ],
        dtype=np.int32,
    )


    hits = int(
        relevance_vector.sum()
    )


    hit_rate = (
        1.0
        if hits > 0
        else 0.0
    )


    recall = (
        hits
        / len(relevant_set)
    )


    precision = (
        hits
        / k
    )


    discounts = (
        1.0
        / np.log2(
            np.arange(
                2,
                len(
                    relevance_vector
                )
                + 2,
            )
        )
    )


    dcg = float(
        (
            relevance_vector
            * discounts
        ).sum()
    )


    ideal_hits = min(
        len(relevant_set),
        k,
    )


    ideal_relevance = np.ones(
        ideal_hits,
        dtype=np.float32,
    )


    ideal_discounts = (
        1.0
        / np.log2(
            np.arange(
                2,
                ideal_hits + 2,
            )
        )
    )


    idcg = float(
        (
            ideal_relevance
            * ideal_discounts
        ).sum()
    )


    ndcg = (
        dcg / idcg
        if idcg > 0
        else 0.0
    )


    return {
        "hits": hits,
        "hitRate": hit_rate,
        "recall": recall,
        "precision": precision,
        "ndcg": ndcg,
    }


# ======================================================================
# EVALUATION LOOP
# ======================================================================

print(
    "\n"
    + "=" * 110
)

print(
    "RUNNING OFFLINE RANKING EVALUATION"
)

print(
    "=" * 110
)


rows = []


for position, user_index in enumerate(
    final_users,
    start=1,
):

    user_index = int(
        user_index
    )


    train_movie_idx, train_rating = (
        train_history[
            user_index
        ]
    )


    val_movie_idx, _ = (
        val_history[
            user_index
        ]
    )


    test_movie_idx, test_rating = (
        test_history[
            user_index
        ]
    )


    # --------------------------------------------------------------
    # Relevant held-out test movies.
    # --------------------------------------------------------------

    relevant_mask = (
        (
            test_rating
            >= RELEVANCE_THRESHOLD
        )
        &
        supported_mask[
            test_movie_idx
        ]
    )


    relevant_movies = np.unique(
        test_movie_idx[
            relevant_mask
        ]
    ).astype(
        np.int64
    )


    # --------------------------------------------------------------
    # Movies the user has interacted with anywhere in
    # train/validation/test.
    #
    # We use these ONLY to avoid sampling false negatives.
    # They are NOT used to build the profile.
    # --------------------------------------------------------------

    known_movies = np.unique(
        np.concatenate(
            [
                train_movie_idx,
                val_movie_idx,
                test_movie_idx,
            ]
        )
    )


    negative_pool = np.setdiff1d(
        supported_movie_indexes,
        known_movies,
        assume_unique=False,
    )


    if len(
        negative_pool
    ) == 0:

        continue


    negative_count = min(
        NUM_NEGATIVES,
        len(
            negative_pool
        ),
    )


    sampled_negatives = rng.choice(
        negative_pool,
        size=negative_count,
        replace=False,
    )


    candidate_movie_indexes = (
        np.concatenate(
            [
                relevant_movies,
                sampled_negatives,
            ]
        )
        .astype(
            np.int64
        )
    )


    # --------------------------------------------------------------
    # CF
    # --------------------------------------------------------------

    cf_raw = predict_cf(
        user_index,
        candidate_movie_indexes,
    )


    cf_norm = normalize_cf(
        cf_raw
    )


    # --------------------------------------------------------------
    # Content built ONLY from training history.
    # --------------------------------------------------------------

    content_raw = predict_content(
        train_movie_idx,
        train_rating,
        candidate_movie_indexes,
    )


    content_norm = (
        normalize_content(
            content_raw
        )
    )


    # --------------------------------------------------------------
    # Sentiment
    # --------------------------------------------------------------

    sentiment_norm = (
        predict_sentiment(
            candidate_movie_indexes
        )
    )


    # --------------------------------------------------------------
    # Core and Hybrid
    # --------------------------------------------------------------

    core_score = (
        CF_WEIGHT
        * cf_norm
        +
        CONTENT_WEIGHT
        * content_norm
        +
        SENTIMENT_WEIGHT
        * NEUTRAL_SENTIMENT
    )


    hybrid_score = (
        CF_WEIGHT
        * cf_norm
        +
        CONTENT_WEIGHT
        * content_norm
        +
        SENTIMENT_WEIGHT
        * sentiment_norm
    )


    # --------------------------------------------------------------
    # Metrics
    # --------------------------------------------------------------

    cf_metrics = (
        calculate_metrics(
            candidate_movie_indexes,
            cf_norm,
            relevant_movies,
            TOP_K,
        )
    )


    core_metrics = (
        calculate_metrics(
            candidate_movie_indexes,
            core_score,
            relevant_movies,
            TOP_K,
        )
    )


    hybrid_metrics = (
        calculate_metrics(
            candidate_movie_indexes,
            hybrid_score,
            relevant_movies,
            TOP_K,
        )
    )


    user_id = int(
        user_id_by_index[
            user_index
        ]
    )


    rows.append(
        {
            "userId":
                user_id,

            "userIndex":
                user_index,

            "trainInteractions":
                len(
                    train_movie_idx
                ),

            "trainPositive":
                int(
                    (
                        train_rating
                        >= POSITIVE_PROFILE_THRESHOLD
                    ).sum()
                ),

            "relevantTestMovies":
                len(
                    relevant_movies
                ),

            "candidateCount":
                len(
                    candidate_movie_indexes
                ),

            # CF
            "cfHits":
                cf_metrics["hits"],

            "cfHitRate":
                cf_metrics["hitRate"],

            "cfRecall":
                cf_metrics["recall"],

            "cfPrecision":
                cf_metrics["precision"],

            "cfNDCG":
                cf_metrics["ndcg"],

            # Core
            "coreHits":
                core_metrics["hits"],

            "coreHitRate":
                core_metrics["hitRate"],

            "coreRecall":
                core_metrics["recall"],

            "corePrecision":
                core_metrics["precision"],

            "coreNDCG":
                core_metrics["ndcg"],

            # Hybrid
            "hybridHits":
                hybrid_metrics["hits"],

            "hybridHitRate":
                hybrid_metrics["hitRate"],

            "hybridRecall":
                hybrid_metrics["recall"],

            "hybridPrecision":
                hybrid_metrics["precision"],

            "hybridNDCG":
                hybrid_metrics["ndcg"],
        }
    )


    if (
        position % 50 == 0
        or position
        == len(final_users)
    ):

        print(
            f"Evaluated "
            f"{position:,}/"
            f"{len(final_users):,} users"
        )


# ======================================================================
# BUILD PER-USER RESULTS
# ======================================================================

results = pd.DataFrame(
    rows
)


if results.empty:

    raise RuntimeError(
        "No evaluation results produced."
    )


# ======================================================================
# SUMMARY
# ======================================================================

def metric_summary(
    prefix,
):

    return {
        "HitRate@10":
            results[
                f"{prefix}HitRate"
            ].mean(),

        "Recall@10":
            results[
                f"{prefix}Recall"
            ].mean(),

        "Precision@10":
            results[
                f"{prefix}Precision"
            ].mean(),

        "NDCG@10":
            results[
                f"{prefix}NDCG"
            ].mean(),
    }


cf_summary = metric_summary(
    "cf"
)

core_summary = metric_summary(
    "core"
)

hybrid_summary = metric_summary(
    "hybrid"
)


summary = pd.DataFrame(
    [
        {
            "model": "CF_ONLY",
            **cf_summary,
        },

        {
            "model": "CF_CONTENT_CORE",
            **core_summary,
        },

        {
            "model": "FINAL_HYBRID",
            **hybrid_summary,
        },
    ]
)


# ======================================================================
# PRINT SUMMARY
# ======================================================================

print(
    "\n"
    + "=" * 110
)

print(
    "OFFLINE TOP-K RESULTS"
)

print(
    "=" * 110
)


print(
    summary.to_string(
        index=False,
        formatters={
            "HitRate@10":
                lambda x: f"{x:.4f}",

            "Recall@10":
                lambda x: f"{x:.4f}",

            "Precision@10":
                lambda x: f"{x:.4f}",

            "NDCG@10":
                lambda x: f"{x:.4f}",
        },
    )
)


# ======================================================================
# DELTAS
# ======================================================================

print(
    "\nHybrid change vs CF-only:"
)


for metric in [
    "HitRate@10",
    "Recall@10",
    "Precision@10",
    "NDCG@10",
]:

    cf_value = (
        cf_summary[
            metric
        ]
    )

    hybrid_value = (
        hybrid_summary[
            metric
        ]
    )


    absolute_change = (
        hybrid_value
        - cf_value
    )


    if cf_value != 0:

        relative_change = (
            absolute_change
            / cf_value
            * 100
        )

        print(
            f"{metric:<14}: "
            f"{absolute_change:+.4f} "
            f"({relative_change:+.2f}%)"
        )

    else:

        print(
            f"{metric:<14}: "
            f"{absolute_change:+.4f}"
        )


print(
    "\nHybrid change vs CF+Content core:"
)


for metric in [
    "HitRate@10",
    "Recall@10",
    "Precision@10",
    "NDCG@10",
]:

    core_value = (
        core_summary[
            metric
        ]
    )

    hybrid_value = (
        hybrid_summary[
            metric
        ]
    )


    absolute_change = (
        hybrid_value
        - core_value
    )


    if core_value != 0:

        relative_change = (
            absolute_change
            / core_value
            * 100
        )

        print(
            f"{metric:<14}: "
            f"{absolute_change:+.4f} "
            f"({relative_change:+.2f}%)"
        )

    else:

        print(
            f"{metric:<14}: "
            f"{absolute_change:+.4f}"
        )


# ======================================================================
# ADDITIONAL STATISTICS
# ======================================================================

print(
    "\n"
    + "=" * 110
)

print(
    "EVALUATION DATA SUMMARY"
)

print(
    "=" * 110
)


print(
    f"Users evaluated:       "
    f"{len(results):,}"
)

print(
    f"Average train history: "
    f"{results['trainInteractions'].mean():.2f}"
)

print(
    f"Average train likes:   "
    f"{results['trainPositive'].mean():.2f}"
)

print(
    f"Average relevant test: "
    f"{results['relevantTestMovies'].mean():.2f}"
)

print(
    f"Average candidates:    "
    f"{results['candidateCount'].mean():.2f}"
)


# ======================================================================
# WIN / LOSS ANALYSIS
# ======================================================================

hybrid_ndcg_better = (
    results[
        "hybridNDCG"
    ]
    >
    results[
        "cfNDCG"
    ]
).sum()


hybrid_ndcg_equal = (
    np.isclose(
        results[
            "hybridNDCG"
        ],
        results[
            "cfNDCG"
        ],
    )
).sum()


hybrid_ndcg_worse = (
    results[
        "hybridNDCG"
    ]
    <
    results[
        "cfNDCG"
    ]
).sum()


print(
    "\nHybrid NDCG vs CF per user:"
)

print(
    f"Better: {hybrid_ndcg_better:,}"
)

print(
    f"Equal:  {hybrid_ndcg_equal:,}"
)

print(
    f"Worse:  {hybrid_ndcg_worse:,}"
)


# ======================================================================
# SAVE RESULTS
# ======================================================================

per_user_output = (
    OUTPUT_DIR
    / "offline_topk_per_user.csv"
)

summary_output = (
    OUTPUT_DIR
    / "offline_topk_summary.csv"
)


results.to_csv(
    per_user_output,
    index=False,
)

summary.to_csv(
    summary_output,
    index=False,
)


print(
    "\nSaved:"
)

print(
    per_user_output
)

print(
    summary_output
)


# ======================================================================
# FINAL
# ======================================================================

print(
    "\n"
    + "=" * 110
)

print(
    "3.9.6 OFFLINE TOP-K EVALUATION COMPLETE"
)

print(
    "=" * 110
)


print(
    "\nIMPORTANT:"
)

print(
    "These are sampled-ranking metrics, "
    "not full-catalog ranking metrics."
)

print(
    "User profiles were created from "
    "TRAIN interactions only."
)

print(
    "Relevant ground truth came from "
    "held-out TEST ratings >= 4.0."
)

print(
    "Validation/test interaction identities "
    "were used only to avoid sampling "
    "known movies as false negatives."
)