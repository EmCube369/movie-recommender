from pathlib import Path
import pickle

import numpy as np
import pandas as pd
import torch

from scipy.sparse import load_npz, csr_matrix
from sklearn.preprocessing import normalize


# ======================================================================
# PATHS
# ======================================================================

ML_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = ML_ROOT / "data" / "processed"
CF_FEATURE_DIR = ML_ROOT / "data" / "features" / "collaborative"
CF_MODEL_DIR = ML_ROOT / "models" / "collaborative"
CONTENT_DIR = ML_ROOT / "models" / "content_based"
SENTIMENT_DIR = PROCESSED_DIR / "sentiment"
OUTPUT_DIR = PROCESSED_DIR / "testing"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


MOVIES_PATH = (
    PROCESSED_DIR / "movies_clean_final.csv"
)

INTERACTIONS_PATH = (
    CF_FEATURE_DIR / "cf_interactions.csv"
)

USER_MAPPING_PATH = (
    CF_FEATURE_DIR / "cf_user_mapping.csv"
)

MOVIE_MAPPING_PATH = (
    CF_FEATURE_DIR / "cf_movie_mapping.csv"
)

CF_CHECKPOINT_PATH = (
    CF_MODEL_DIR / "matrix_factorization_best.pt"
)

CF_SEEN_PATH = (
    CF_MODEL_DIR / "cf_seen_movie_indexes.npy"
)

CONTENT_MAPPING_PATH = (
    CONTENT_DIR / "movie_id_to_index.pkl"
)

CONTENT_WEIGHTS_PATH = (
    CONTENT_DIR / "content_weights.pkl"
)

SENTIMENT_PATH = (
    SENTIMENT_DIR / "movie_sentiment_final.csv"
)


CONTENT_MATRIX_PATHS = {
    "genre": CONTENT_DIR / "genre_matrix.npz",
    "keyword": CONTENT_DIR / "keyword_matrix.npz",
    "director": CONTENT_DIR / "director_matrix.npz",
    "cast": CONTENT_DIR / "cast_matrix.npz",
    "overview": CONTENT_DIR / "overview_matrix.npz",
    "tagline": CONTENT_DIR / "tagline_matrix.npz",
}


# ======================================================================
# HYBRID SETTINGS
# ======================================================================

CF_WEIGHT = 0.50
CONTENT_WEIGHT = 0.35
SENTIMENT_WEIGHT = 0.15

CONTENT_NORMALIZATION_MAX = 0.31
NEUTRAL_SENTIMENT = 0.50

POSITIVE_RATING_THRESHOLD = 4.0

TOP_K = 10


TEST_USER_IDS = [
    7382,       # sparse user: 15 ratings
    1,          # 141 ratings
    151,        # 500 ratings
    156429,     # 2000 ratings
]


# ======================================================================
# START
# ======================================================================

print("=" * 110)
print("3.9.5 HYBRID QUALITATIVE RECOMMENDATION TEST")
print("=" * 110)


# ======================================================================
# LOAD CATALOG
# ======================================================================

movies = pd.read_csv(
    MOVIES_PATH,
    low_memory=False,
)


if "title" in movies.columns:
    title_col = "title"
elif "title_x" in movies.columns:
    title_col = "title_x"
else:
    raise ValueError("Movie title column not found.")


if "genres" in movies.columns:
    genre_col = "genres"
elif "movielens_genres" in movies.columns:
    genre_col = "movielens_genres"
else:
    genre_col = None


catalog = (
    movies
    .drop_duplicates("movieId")
    .set_index("movieId")
)


# ======================================================================
# LOAD CF ARTIFACTS
# ======================================================================

print("\nLoading collaborative artifacts...")

user_mapping = pd.read_csv(USER_MAPPING_PATH)
movie_mapping = pd.read_csv(MOVIE_MAPPING_PATH)

checkpoint = torch.load(
    CF_CHECKPOINT_PATH,
    map_location="cpu",
    weights_only=False,
)

state = checkpoint["model_state_dict"]


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

global_mean = float(
    state["global_mean"]
    .detach()
    .cpu()
    .item()
)


user_id_to_index = dict(
    zip(
        user_mapping["userId"].astype(int),
        user_mapping["userIndex"].astype(int),
    )
)


num_movies = len(movie_mapping)

movie_id_by_cf_index = np.full(
    num_movies,
    -1,
    dtype=np.int64,
)

movie_id_by_cf_index[
    movie_mapping["movieIndex"].astype(int).to_numpy()
] = (
    movie_mapping["movieId"]
    .astype(int)
    .to_numpy()
)


seen_movie_indexes = np.unique(
    np.load(CF_SEEN_PATH).astype(np.int64)
)


print(f"CF users:  {len(user_mapping):,}")
print(f"CF movies: {len(movie_mapping):,}")
print(
    f"Supported candidates: "
    f"{len(seen_movie_indexes):,}"
)


# ======================================================================
# LOAD CONTENT ARTIFACTS
# ======================================================================

print("\nLoading content artifacts...")


with open(
    CONTENT_MAPPING_PATH,
    "rb",
) as f:
    raw_content_mapping = pickle.load(f)


content_index_by_movie_id = {
    int(movie_id): int(index)
    for movie_id, index
    in raw_content_mapping.items()
}


with open(
    CONTENT_WEIGHTS_PATH,
    "rb",
) as f:
    content_weights = pickle.load(f)


content_matrices = {
    name: load_npz(path).tocsr()
    for name, path
    in CONTENT_MATRIX_PATHS.items()
}


print(
    f"Content movies: "
    f"{len(content_index_by_movie_id):,}"
)

print(
    "Content weights:",
    content_weights,
)


# ======================================================================
# LOAD SENTIMENT
# ======================================================================

print("\nLoading sentiment artifact...")

sentiment = pd.read_csv(
    SENTIMENT_PATH,
    low_memory=False,
)


sentiment["sentimentNormalized"] = np.clip(
    (
        sentiment["adjustedSentimentScore"]
        .astype(float)
        + 1.0
    ) / 2.0,
    0.0,
    1.0,
)


sentiment_lookup = dict(
    zip(
        sentiment["movieId"].astype(int),
        sentiment["sentimentNormalized"].astype(float),
    )
)


print(
    f"Movies with sentiment: "
    f"{len(sentiment_lookup):,}"
)


# ======================================================================
# LOAD TEST USER HISTORIES ONLY
# ======================================================================

print("\nLoading test-user histories...")


valid_users = [
    user_id
    for user_id in TEST_USER_IDS
    if user_id in user_id_to_index
]


target_user_indexes = {
    user_id_to_index[user_id]
    for user_id in valid_users
}


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


test_interactions = pd.concat(
    interaction_parts,
    ignore_index=True,
)


# ======================================================================
# HELPERS
# ======================================================================

def normalize_cf(scores):

    return np.clip(
        (scores - 0.5) / 4.5,
        0.0,
        1.0,
    )


def normalize_content(scores):

    scores = np.asarray(
        scores,
        dtype=np.float32,
    )

    return np.clip(
        scores / CONTENT_NORMALIZATION_MAX,
        0.0,
        1.0,
    )


def predict_cf_scores(
    user_index,
    candidate_indexes,
):

    candidate_tensor = torch.from_numpy(
        candidate_indexes.astype(np.int64)
    ).long()


    user_vector = user_embedding[
        user_index
    ]


    scores = (
        global_mean
        + user_bias[user_index]
        + movie_bias[candidate_tensor]
        + torch.mv(
            movie_embedding[candidate_tensor],
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


def make_rank_array(scores):

    order = np.argsort(
        scores
    )[::-1]

    ranks = np.empty(
        len(scores),
        dtype=np.int32,
    )

    ranks[order] = np.arange(
        1,
        len(scores) + 1,
    )

    return ranks


def get_user_history(user_id):

    user_index = user_id_to_index[
        user_id
    ]

    history = test_interactions[
        test_interactions["userIndex"]
        == user_index
    ].copy()


    history["movieId"] = (
        movie_id_by_cf_index[
            history["movieIndex"]
            .astype(int)
            .to_numpy()
        ]
    )


    return history


# ======================================================================
# CONTENT USER PROFILE
# ======================================================================

def calculate_personalized_content_scores(
    positive_history,
    candidate_movie_ids,
):

    positive_history = (
        positive_history[
            positive_history["movieId"].isin(
                content_index_by_movie_id
            )
        ]
        .copy()
    )

    if positive_history.empty:

        return np.zeros(
            len(candidate_movie_ids),
            dtype=np.float32,
        )


    positive_content_indexes = np.array(
        [
            content_index_by_movie_id[
                int(movie_id)
            ]
            for movie_id
            in positive_history["movieId"]
        ],
        dtype=np.int64,
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


    ratings = (
        positive_history["rating"]
        .to_numpy(dtype=np.float32)
    )


    # Exact Phase 3.8 preference weighting:
    #
    # 4.0 -> 1.0
    # 4.5 -> 1.5
    # 5.0 -> 2.0
    rating_weights = (
        ratings - 3.0
    )


    final_scores = np.zeros(
        len(candidate_movie_ids),
        dtype=np.float32,
    )


    for feature_name, matrix in content_matrices.items():

        liked_vectors = matrix[
            positive_content_indexes
        ]


        weighted_vectors = (
            liked_vectors.multiply(
                rating_weights[:, None]
            )
        )


        profile = weighted_vectors.sum(
            axis=0
        )


        profile = csr_matrix(
            profile
        )


        # Exact Phase 3.8 profile normalization.
        profile = normalize(
            profile,
            norm="l2",
        )


        # Exact Phase 3.8 scoring method.
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


        final_scores += (
            float(
                content_weights[
                    feature_name
                ]
            )
            * similarities
        )


    return final_scores


# ======================================================================
# USER TASTE SUMMARY
# ======================================================================

def print_user_taste(
    positive_history,
):

    print(
        f"Positive ratings (>= {POSITIVE_RATING_THRESHOLD}): "
        f"{len(positive_history):,}"
    )


    if genre_col is None:
        return


    genre_counts = {}


    for movie_id in positive_history["movieId"]:

        if movie_id not in catalog.index:
            continue

        genres = catalog.loc[
            movie_id,
            genre_col,
        ]

        if pd.isna(genres):
            continue


        for genre in str(genres).split("|"):

            genre = genre.strip()

            if not genre:
                continue

            genre_counts[genre] = (
                genre_counts.get(
                    genre,
                    0,
                )
                + 1
            )


    top_genres = sorted(
        genre_counts.items(),
        key=lambda x: x[1],
        reverse=True,
    )[:6]


    if top_genres:

        print(
            "Most common liked genres:",
            ", ".join(
                f"{genre} ({count})"
                for genre, count
                in top_genres
            ),
        )


# ======================================================================
# GENERATE HYBRID RECOMMENDATIONS
# ======================================================================

def recommend_hybrid(
    user_id,
):

    user_index = user_id_to_index[
        user_id
    ]


    history = get_user_history(
        user_id
    )


    rated_indexes = set(
        history[
            "movieIndex"
        ]
        .astype(int)
        .tolist()
    )


    positive_history = history[
        history["rating"]
        >= POSITIVE_RATING_THRESHOLD
    ].copy()


    candidate_indexes = np.array(
        [
            index
            for index in seen_movie_indexes
            if index not in rated_indexes
        ],
        dtype=np.int64,
    )


    candidate_movie_ids = (
        movie_id_by_cf_index[
            candidate_indexes
        ]
    )


    # --------------------------------------------------------------
    # All CF movies should exist in content catalog.
    # --------------------------------------------------------------

    content_supported_mask = np.array(
        [
            int(movie_id)
            in content_index_by_movie_id
            for movie_id
            in candidate_movie_ids
        ],
        dtype=bool,
    )


    candidate_indexes = (
        candidate_indexes[
            content_supported_mask
        ]
    )

    candidate_movie_ids = (
        candidate_movie_ids[
            content_supported_mask
        ]
    )


    # --------------------------------------------------------------
    # CF
    # --------------------------------------------------------------

    cf_raw = predict_cf_scores(
        user_index,
        candidate_indexes,
    )

    cf_norm = normalize_cf(
        cf_raw
    )


    # --------------------------------------------------------------
    # CONTENT
    # --------------------------------------------------------------

    content_raw = (
        calculate_personalized_content_scores(
            positive_history,
            candidate_movie_ids,
        )
    )

    content_norm = normalize_content(
        content_raw
    )


    # --------------------------------------------------------------
    # SENTIMENT
    # --------------------------------------------------------------

    sentiment_norm = np.array(
        [
            sentiment_lookup.get(
                int(movie_id),
                NEUTRAL_SENTIMENT,
            )
            for movie_id
            in candidate_movie_ids
        ],
        dtype=np.float32,
    )


    has_sentiment = np.array(
        [
            int(movie_id)
            in sentiment_lookup
            for movie_id
            in candidate_movie_ids
        ],
        dtype=bool,
    )


    # --------------------------------------------------------------
    # HYBRID
    # --------------------------------------------------------------

    cf_contribution = (
        CF_WEIGHT
        * cf_norm
    )

    content_contribution = (
        CONTENT_WEIGHT
        * content_norm
    )

    sentiment_contribution = (
        SENTIMENT_WEIGHT
        * sentiment_norm
    )


    hybrid_score = (
        cf_contribution
        + content_contribution
        + sentiment_contribution
    )


    # Same ranking if sentiment were neutral for every movie.
    neutral_hybrid_score = (
        cf_contribution
        + content_contribution
        + SENTIMENT_WEIGHT
        * NEUTRAL_SENTIMENT
    )


    # --------------------------------------------------------------
    # RANKS
    # --------------------------------------------------------------

    cf_rank = make_rank_array(
        cf_norm
    )

    core_rank = make_rank_array(
        neutral_hybrid_score
    )

    hybrid_rank = make_rank_array(
        hybrid_score
    )


    results = pd.DataFrame(
        {
            "movieId": candidate_movie_ids,
            "cfRaw": cf_raw,
            "cfNorm": cf_norm,
            "contentRaw": content_raw,
            "contentNorm": content_norm,
            "sentimentNorm": sentiment_norm,
            "hasSentiment": has_sentiment,
            "cfContribution": cf_contribution,
            "contentContribution": content_contribution,
            "sentimentContribution": sentiment_contribution,
            "neutralHybridScore": neutral_hybrid_score,
            "hybridScore": hybrid_score,
            "cfRank": cf_rank,
            "coreRank": core_rank,
            "hybridRank": hybrid_rank,
        }
    )


    results["title"] = (
        results["movieId"]
        .map(
            catalog[
                title_col
            ].to_dict()
        )
        .fillna("<unknown>")
    )


    if genre_col is not None:

        results["genres"] = (
            results["movieId"]
            .map(
                catalog[
                    genre_col
                ].to_dict()
            )
            .fillna("")
        )

    else:

        results["genres"] = ""


    results["sentimentDelta"] = (
        results["sentimentContribution"]
        - SENTIMENT_WEIGHT
        * NEUTRAL_SENTIMENT
    )


    results["sentimentRankChange"] = (
        results["coreRank"]
        - results["hybridRank"]
    )


    results = results.sort_values(
        "hybridScore",
        ascending=False,
    ).reset_index(drop=True)


    results["rank"] = np.arange(
        1,
        len(results) + 1,
    )


    return (
        results,
        history,
        positive_history,
    )


# ======================================================================
# RUN TESTS
# ======================================================================

all_top_results = []

top_sets = {}

overall_pass = True


for user_id in valid_users:

    print(
        "\n"
        + "=" * 110
    )

    print(
        f"USER {user_id}"
    )

    print(
        "=" * 110
    )


    results, history, positive_history = (
        recommend_hybrid(
            user_id
        )
    )


    print(
        f"History size: "
        f"{len(history):,}"
    )

    print_user_taste(
        positive_history
    )


    top = results.head(
        TOP_K
    ).copy()


    # --------------------------------------------------------------
    # STRUCTURAL CHECKS
    # --------------------------------------------------------------

    failures = []


    rated_ids = set(
        history[
            "movieId"
        ]
        .astype(int)
        .tolist()
    )


    recommended_ids = set(
        top[
            "movieId"
        ]
        .astype(int)
        .tolist()
    )


    if rated_ids & recommended_ids:

        failures.append(
            "Already-rated movie recommended."
        )


    if top["movieId"].duplicated().any():

        failures.append(
            "Duplicate recommendations."
        )


    if not np.isfinite(
        top["hybridScore"]
    ).all():

        failures.append(
            "Non-finite hybrid score."
        )


    if (
        (
            top["hybridScore"] < 0
        )
        | (
            top["hybridScore"] > 1
        )
    ).any():

        failures.append(
            "Hybrid score outside [0,1]."
        )


    scores = top[
        "hybridScore"
    ].to_numpy()


    if not np.all(
        scores[:-1]
        >= scores[1:] - 1e-8
    ):

        failures.append(
            "Hybrid ranking not descending."
        )


    contribution_sum = (
        top["cfContribution"]
        + top["contentContribution"]
        + top["sentimentContribution"]
    )


    if not np.allclose(
        contribution_sum,
        top["hybridScore"],
        atol=1e-6,
    ):

        failures.append(
            "Hybrid contributions do not sum "
            "to final score."
        )


    if failures:

        overall_pass = False

        print("\nStructural checks:")

        for failure in failures:
            print(
                f"  FAIL - {failure}"
            )

    else:

        print("\nStructural checks:")
        print(
            "  PASS - rated movies excluded"
        )
        print(
            "  PASS - no duplicates"
        )
        print(
            "  PASS - scores finite"
        )
        print(
            "  PASS - scores within [0,1]"
        )
        print(
            "  PASS - sorted descending"
        )
        print(
            "  PASS - component contributions "
            "sum correctly"
        )


    # --------------------------------------------------------------
    # DISPLAY TOP 10
    # --------------------------------------------------------------

    print(
        "\nTop hybrid recommendations:"
    )


    display_columns = [
        "rank",
        "movieId",
        "title",
        "genres",
        "cfNorm",
        "contentNorm",
        "sentimentNorm",
        "hybridScore",
        "cfRank",
        "coreRank",
        "sentimentRankChange",
    ]


    print(
        top[
            display_columns
        ].to_string(
            index=False,
            formatters={
                "cfNorm":
                    lambda x: f"{x:.4f}",
                "contentNorm":
                    lambda x: f"{x:.4f}",
                "sentimentNorm":
                    lambda x: f"{x:.4f}",
                "hybridScore":
                    lambda x: f"{x:.4f}",
            },
        )
    )


    # --------------------------------------------------------------
    # CF VS HYBRID
    # --------------------------------------------------------------

    cf_top_ids = set(
        results
        .nsmallest(
            TOP_K,
            "cfRank",
        )["movieId"]
        .astype(int)
    )


    hybrid_top_ids = set(
        top[
            "movieId"
        ]
        .astype(int)
    )


    cf_overlap = len(
        cf_top_ids
        & hybrid_top_ids
    )


    # --------------------------------------------------------------
    # PRE-SENTIMENT VS FINAL
    # --------------------------------------------------------------

    core_top_ids = set(
        results
        .nsmallest(
            TOP_K,
            "coreRank",
        )["movieId"]
        .astype(int)
    )


    core_overlap = len(
        core_top_ids
        & hybrid_top_ids
    )


    print(
        "\nRanking comparison:"
    )

    print(
        f"CF-only vs Hybrid Top-{TOP_K} overlap: "
        f"{cf_overlap}/{TOP_K}"
    )

    print(
        f"Core (CF+Content) vs Hybrid overlap: "
        f"{core_overlap}/{TOP_K}"
    )


    # --------------------------------------------------------------
    # SENTIMENT COVERAGE IN TOP 10
    # --------------------------------------------------------------

    sentiment_count = int(
        top["hasSentiment"].sum()
    )


    print(
        f"Top-{TOP_K} movies with real sentiment: "
        f"{sentiment_count}/{TOP_K}"
    )


    # --------------------------------------------------------------
    # BIGGEST SENTIMENT MOVERS
    # --------------------------------------------------------------

    sentiment_movers = (
        results[
            results["hasSentiment"]
        ]
        .assign(
            absoluteRankChange=lambda df:
                df["sentimentRankChange"].abs()
        )
        .sort_values(
            "absoluteRankChange",
            ascending=False,
        )
        .head(5)
    )


    print(
        "\nLargest sentiment-driven rank changes:"
    )


    print(
        sentiment_movers[
            [
                "movieId",
                "title",
                "sentimentNorm",
                "coreRank",
                "hybridRank",
                "sentimentRankChange",
            ]
        ].to_string(
            index=False,
            formatters={
                "sentimentNorm":
                    lambda x: f"{x:.4f}",
            },
        )
    )


    # --------------------------------------------------------------
    # SAVE
    # --------------------------------------------------------------

    top.insert(
        0,
        "userId",
        user_id,
    )


    all_top_results.append(
        top
    )


    top_sets[user_id] = (
        hybrid_top_ids
    )


# ======================================================================
# PERSONALIZATION ACROSS USERS
# ======================================================================

print(
    "\n"
    + "=" * 110
)

print(
    "HYBRID PERSONALIZATION TEST"
)

print(
    "=" * 110
)


user_ids = list(
    top_sets.keys()
)


for i in range(
    len(user_ids)
):

    for j in range(
        i + 1,
        len(user_ids),
    ):

        a = user_ids[i]
        b = user_ids[j]

        overlap = len(
            top_sets[a]
            & top_sets[b]
        )

        union = (
            top_sets[a]
            | top_sets[b]
        )

        jaccard = (
            overlap / len(union)
            if union
            else 0
        )

        print(
            f"User {a:<8} vs User {b:<8} | "
            f"overlap {overlap}/{TOP_K} | "
            f"Jaccard {jaccard:.3f}"
        )


# ======================================================================
# USER 1 PHASE 3.8 REGRESSION
# ======================================================================

print(
    "\n"
    + "=" * 110
)

print(
    "USER 1 PHASE 3.8 REGRESSION CHECK"
)

print(
    "=" * 110
)


if 1 in valid_users:

    user1_results, _, _ = (
        recommend_hybrid(1)
    )

    user1_top = user1_results.iloc[
        0
    ]


    print(
        f"Top result: "
        f"{user1_top['title']}"
    )

    print(
        f"Hybrid score: "
        f"{user1_top['hybridScore']:.4f}"
    )


    expected_title = (
        "Sunset Boulevard"
    )

    expected_score = 0.7854


    if (
        expected_title.lower()
        in str(
            user1_top["title"]
        ).lower()
    ):

        print(
            "PASS - Top movie matches "
            "Phase 3.8."
        )

    else:

        print(
            "WARNING - Top movie differs "
            "from Phase 3.8."
        )


    if np.isclose(
        float(
            user1_top["hybridScore"]
        ),
        expected_score,
        atol=0.01,
    ):

        print(
            "PASS - Hybrid score approximately "
            "matches Phase 3.8."
        )

    else:

        print(
            "WARNING - Hybrid score differs "
            "from Phase 3.8."
        )


# ======================================================================
# SAVE RESULTS
# ======================================================================

if all_top_results:

    final_output = pd.concat(
        all_top_results,
        ignore_index=True,
    )


    output_path = (
        OUTPUT_DIR
        / "hybrid_qualitative_test_results.csv"
    )


    final_output.to_csv(
        output_path,
        index=False,
    )


    print(
        "\nSaved:"
    )

    print(
        output_path
    )


# ======================================================================
# FINAL
# ======================================================================

print(
    "\n"
    + "=" * 110
)

print(
    "3.9.5 AUTOMATED TEST RESULT"
)

print(
    "=" * 110
)


if overall_pass:

    print(
        "PASS - All structural hybrid "
        "recommendation tests passed."
    )

else:

    print(
        "FAIL - One or more structural "
        "hybrid tests failed."
    )


print(
    "\nNOTE:"
    "\nThe automated result is not the final "
    "3.9.5 verdict."
    "\nRecommendation relevance, personalization, "
    "and ranking changes must also be inspected."
)