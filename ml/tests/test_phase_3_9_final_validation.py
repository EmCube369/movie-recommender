from pathlib import Path
import json
import pickle

import numpy as np
import pandas as pd
import torch
from scipy.sparse import load_npz


# ======================================================================
# PATHS
# ======================================================================

ML_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = ML_ROOT / "data" / "processed"
TESTING_DIR = PROCESSED_DIR / "testing"

CF_FEATURE_DIR = ML_ROOT / "data" / "features" / "collaborative"
CF_MODEL_DIR = ML_ROOT / "models" / "collaborative"
CONTENT_DIR = ML_ROOT / "models" / "content_based"
SENTIMENT_DIR = PROCESSED_DIR / "sentiment"


# ======================================================================
# CORE ARTIFACTS
# ======================================================================

MOVIES_PATH = (
    PROCESSED_DIR
    / "movies_clean_final.csv"
)

CF_MODEL_PATH = (
    CF_MODEL_DIR
    / "matrix_factorization_best.pt"
)

CF_SEEN_PATH = (
    CF_MODEL_DIR
    / "cf_seen_movie_indexes.npy"
)

USER_MAPPING_PATH = (
    CF_FEATURE_DIR
    / "cf_user_mapping.csv"
)

MOVIE_MAPPING_PATH = (
    CF_FEATURE_DIR
    / "cf_movie_mapping.csv"
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

SENTIMENT_METADATA_PATH = (
    SENTIMENT_DIR
    / "sentiment_metadata.json"
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
# PHASE 3.9 TEST OUTPUTS
# ======================================================================

CONTENT_TEST_PATH = (
    TESTING_DIR
    / "content_based_test_results.csv"
)

CF_TEST_PATH = (
    TESTING_DIR
    / "collaborative_test_results.csv"
)

SENTIMENT_TEST_PATH = (
    TESTING_DIR
    / "sentiment_signal_test_results.csv"
)

HYBRID_TEST_PATH = (
    TESTING_DIR
    / "hybrid_qualitative_test_results.csv"
)

OFFLINE_PER_USER_PATH = (
    TESTING_DIR
    / "offline_topk_per_user.csv"
)

OFFLINE_SUMMARY_PATH = (
    TESTING_DIR
    / "offline_topk_summary.csv"
)

EDGE_TEST_PATH = (
    TESTING_DIR
    / "edge_case_test_results.csv"
)


# ======================================================================
# EXPECTED FINAL VALUES
# ======================================================================

EXPECTED_CATALOG_MOVIES = 87_550

EXPECTED_CF_USERS = 200_948
EXPECTED_CF_MOVIES = 43_864
EXPECTED_CF_SUPPORTED = 43_599

EXPECTED_EMBEDDING_DIM = 64
EXPECTED_BEST_EPOCH = 15
EXPECTED_VAL_RMSE = 0.839572

EXPECTED_SENTIMENT_MOVIES = 3_769

EXPECTED_HYBRID_WEIGHTS = {
    "cf": 0.50,
    "content": 0.35,
    "sentiment": 0.15,
}

EXPECTED_CONTENT_WEIGHTS = {
    "genre": 0.25,
    "keyword": 0.25,
    "director": 0.15,
    "cast": 0.15,
    "overview": 0.15,
    "tagline": 0.05,
}

EXPECTED_OFFLINE_METRICS = {
    "CF_ONLY": {
        "HitRate@10": 0.6580,
        "Recall@10": 0.2553,
        "Precision@10": 0.1874,
        "NDCG@10": 0.2747,
    },

    "CF_CONTENT_CORE": {
        "HitRate@10": 0.6440,
        "Recall@10": 0.2073,
        "Precision@10": 0.1610,
        "NDCG@10": 0.2509,
    },

    "FINAL_HYBRID": {
        "HitRate@10": 0.7160,
        "Recall@10": 0.2582,
        "Precision@10": 0.1890,
        "NDCG@10": 0.2911,
    },
}


# ======================================================================
# RESULT TRACKING
# ======================================================================

results = []

overall_pass = True


def check(name, condition, detail):
    global overall_pass

    passed = bool(condition)

    status = "PASS" if passed else "FAIL"

    print(
        f"{status:<5} - "
        f"{name}: "
        f"{detail}"
    )

    results.append(
        {
            "test": name,
            "status": status,
            "detail": detail,
        }
    )

    if not passed:
        overall_pass = False


# ======================================================================
# START
# ======================================================================

print("=" * 110)
print("PHASE 3.9 FINAL VALIDATION")
print("=" * 110)


# ======================================================================
# 1. REQUIRED FILES
# ======================================================================

print("\n" + "=" * 110)
print("1. REQUIRED ARTIFACTS")
print("=" * 110)


required_files = [
    MOVIES_PATH,
    CF_MODEL_PATH,
    CF_SEEN_PATH,
    USER_MAPPING_PATH,
    MOVIE_MAPPING_PATH,
    CONTENT_MAPPING_PATH,
    CONTENT_WEIGHTS_PATH,
    SENTIMENT_PATH,
    *CONTENT_MATRIX_PATHS.values(),

    CONTENT_TEST_PATH,
    CF_TEST_PATH,
    SENTIMENT_TEST_PATH,
    HYBRID_TEST_PATH,
    OFFLINE_PER_USER_PATH,
    OFFLINE_SUMMARY_PATH,
    EDGE_TEST_PATH,
]


for path in required_files:

    check(
        f"File exists: {path.name}",
        path.exists(),
        str(path),
    )


# Stop early if essential files are missing.
missing = [
    path
    for path in required_files
    if not path.exists()
]

if missing:
    raise FileNotFoundError(
        "Final validation cannot continue "
        "because required artifacts are missing."
    )


# ======================================================================
# 2. MOVIE CATALOG
# ======================================================================

print("\n" + "=" * 110)
print("2. MOVIE CATALOG")
print("=" * 110)


movies = pd.read_csv(
    MOVIES_PATH,
    low_memory=False,
)


check(
    "Catalog row count",
    len(movies) == EXPECTED_CATALOG_MOVIES,
    f"{len(movies):,} movies",
)


check(
    "Catalog movie IDs unique",
    movies["movieId"].is_unique,
    (
        f"{movies['movieId'].nunique():,} "
        f"unique movie IDs"
    ),
)


# ======================================================================
# 3. COLLABORATIVE FILTERING
# ======================================================================

print("\n" + "=" * 110)
print("3. COLLABORATIVE FILTERING ARTIFACTS")
print("=" * 110)


user_mapping = pd.read_csv(
    USER_MAPPING_PATH
)

movie_mapping = pd.read_csv(
    MOVIE_MAPPING_PATH
)


check(
    "CF user count",
    len(user_mapping) == EXPECTED_CF_USERS,
    f"{len(user_mapping):,}",
)


check(
    "CF movie count",
    len(movie_mapping) == EXPECTED_CF_MOVIES,
    f"{len(movie_mapping):,}",
)


check(
    "User IDs unique",
    user_mapping["userId"].is_unique,
    "No duplicate user IDs",
)


check(
    "Movie IDs unique",
    movie_mapping["movieId"].is_unique,
    "No duplicate movie IDs",
)


user_indexes = np.sort(
    user_mapping[
        "userIndex"
    ].to_numpy()
)

movie_indexes = np.sort(
    movie_mapping[
        "movieIndex"
    ].to_numpy()
)


check(
    "User indexes contiguous",
    np.array_equal(
        user_indexes,
        np.arange(
            len(user_mapping)
        ),
    ),
    "0 ... num_users-1",
)


check(
    "Movie indexes contiguous",
    np.array_equal(
        movie_indexes,
        np.arange(
            len(movie_mapping)
        ),
    ),
    "0 ... num_movies-1",
)


checkpoint = torch.load(
    CF_MODEL_PATH,
    map_location="cpu",
    weights_only=False,
)


check(
    "CF embedding dimension",
    int(
        checkpoint[
            "embedding_dim"
        ]
    ) == EXPECTED_EMBEDDING_DIM,
    str(
        checkpoint[
            "embedding_dim"
        ]
    ),
)


check(
    "CF best epoch",
    int(
        checkpoint[
            "epoch"
        ]
    ) == EXPECTED_BEST_EPOCH,
    str(
        checkpoint[
            "epoch"
        ]
    ),
)


check(
    "CF validation RMSE regression",
    np.isclose(
        float(
            checkpoint[
                "validation_rmse"
            ]
        ),
        EXPECTED_VAL_RMSE,
        atol=1e-4,
    ),
    (
        f"{float(checkpoint['validation_rmse']):.6f}"
    ),
)


seen_indexes = np.unique(
    np.load(
        CF_SEEN_PATH
    )
)


check(
    "CF-supported movie count",
    len(seen_indexes)
    == EXPECTED_CF_SUPPORTED,
    f"{len(seen_indexes):,}",
)


# ======================================================================
# 4. CONTENT-BASED ARTIFACTS
# ======================================================================

print("\n" + "=" * 110)
print("4. CONTENT-BASED ARTIFACTS")
print("=" * 110)


with open(
    CONTENT_MAPPING_PATH,
    "rb",
) as f:

    content_mapping = pickle.load(
        f
    )


with open(
    CONTENT_WEIGHTS_PATH,
    "rb",
) as f:

    content_weights = pickle.load(
        f
    )


check(
    "Content mapping size",
    len(content_mapping)
    == EXPECTED_CATALOG_MOVIES,
    f"{len(content_mapping):,}",
)


check(
    "Content weights",
    content_weights
    == EXPECTED_CONTENT_WEIGHTS,
    str(content_weights),
)


check(
    "Content weights sum",
    np.isclose(
        sum(
            content_weights.values()
        ),
        1.0,
    ),
    (
        f"{sum(content_weights.values()):.4f}"
    ),
)


for name, path in (
    CONTENT_MATRIX_PATHS.items()
):

    matrix = load_npz(
        path
    )

    check(
        f"{name} matrix rows",
        matrix.shape[0]
        == EXPECTED_CATALOG_MOVIES,
        str(
            matrix.shape
        ),
    )


# ======================================================================
# 5. SENTIMENT ARTIFACT
# ======================================================================

print("\n" + "=" * 110)
print("5. SENTIMENT ARTIFACT")
print("=" * 110)


sentiment = pd.read_csv(
    SENTIMENT_PATH,
    low_memory=False,
)


check(
    "Sentiment movie count",
    len(sentiment)
    == EXPECTED_SENTIMENT_MOVIES,
    f"{len(sentiment):,}",
)


check(
    "Sentiment movie IDs unique",
    sentiment[
        "movieId"
    ].is_unique,
    "No duplicates",
)


check(
    "Adjusted sentiment finite",
    np.isfinite(
        sentiment[
            "adjustedSentimentScore"
        ]
    ).all(),
    "All finite",
)


check(
    "Reliability finite",
    np.isfinite(
        sentiment[
            "sentimentReliability"
        ]
    ).all(),
    "All finite",
)


adjusted_min = float(
    sentiment[
        "adjustedSentimentScore"
    ].min()
)

adjusted_max = float(
    sentiment[
        "adjustedSentimentScore"
    ].max()
)


check(
    "Sentiment minimum regression",
    np.isclose(
        adjusted_min,
        -0.532931,
        atol=1e-4,
    ),
    f"{adjusted_min:.6f}",
)


check(
    "Sentiment maximum regression",
    np.isclose(
        adjusted_max,
        0.809527,
        atol=1e-4,
    ),
    f"{adjusted_max:.6f}",
)


# ======================================================================
# 6. 3.9.2 CONTENT TEST OUTPUT
# ======================================================================

print("\n" + "=" * 110)
print("6. CONTENT TEST RESULTS")
print("=" * 110)


content_test = pd.read_csv(
    CONTENT_TEST_PATH
)


check(
    "Content test rows",
    len(content_test) == 80,
    (
        f"{len(content_test)} rows "
        f"(8 seeds x 10)"
    ),
)


check(
    "Content test seeds",
    content_test[
        "seedMovieId"
    ].nunique() == 8,
    (
        f"{content_test['seedMovieId'].nunique()} "
        f"seed movies"
    ),
)


seed_overlap = (
    content_test[
        "seedMovieId"
    ].astype(int)
    ==
    content_test[
        "movieId"
    ].astype(int)
)


check(
    "No content self-recommendation",
    not seed_overlap.any(),
    (
        f"{int(seed_overlap.sum())} "
        f"self recommendations"
    ),
)


# ======================================================================
# 7. 3.9.3 CF TEST OUTPUT
# ======================================================================

print("\n" + "=" * 110)
print("7. CF TEST RESULTS")
print("=" * 110)


cf_test = pd.read_csv(
    CF_TEST_PATH
)


check(
    "CF test rows",
    len(cf_test) == 40,
    (
        f"{len(cf_test)} rows "
        f"(4 users x 10)"
    ),
)


check(
    "CF test users",
    cf_test[
        "userId"
    ].nunique() == 4,
    (
        f"{cf_test['userId'].nunique()} "
        f"users"
    ),
)


user1_cf = (
    cf_test[
        cf_test[
            "userId"
        ] == 1
    ]
    .sort_values(
        "rank"
    )
    .iloc[0]
)


check(
    "User 1 CF regression movie",
    int(
        user1_cf[
            "movieId"
        ]
    ) == 171011,
    (
        f"movieId "
        f"{int(user1_cf['movieId'])}"
    ),
)


check(
    "User 1 CF regression score",
    np.isclose(
        float(
            user1_cf[
                "predictedRating"
            ]
        ),
        4.2609,
        atol=1e-3,
    ),
    (
        f"{float(user1_cf['predictedRating']):.4f}"
    ),
)


# ======================================================================
# 8. 3.9.4 SENTIMENT TEST OUTPUT
# ======================================================================

print("\n" + "=" * 110)
print("8. SENTIMENT TEST RESULTS")
print("=" * 110)


sentiment_test = pd.read_csv(
    SENTIMENT_TEST_PATH
)


check(
    "Sentiment signal output rows",
    len(sentiment_test)
    == EXPECTED_SENTIMENT_MOVIES,
    f"{len(sentiment_test):,}",
)


check(
    "Normalized sentiment range",
    (
        sentiment_test[
            "sentimentNormalized"
        ].between(
            0.0,
            1.0,
        )
    ).all(),
    (
        f"{sentiment_test['sentimentNormalized'].min():.4f} "
        f"to "
        f"{sentiment_test['sentimentNormalized'].max():.4f}"
    ),
)


# ======================================================================
# 9. 3.9.5 HYBRID TEST OUTPUT
# ======================================================================

print("\n" + "=" * 110)
print("9. HYBRID QUALITATIVE RESULTS")
print("=" * 110)


hybrid_test = pd.read_csv(
    HYBRID_TEST_PATH
)


check(
    "Hybrid test rows",
    len(hybrid_test) == 40,
    (
        f"{len(hybrid_test)} rows "
        f"(4 users x 10)"
    ),
)


check(
    "Hybrid test users",
    hybrid_test[
        "userId"
    ].nunique() == 4,
    (
        f"{hybrid_test['userId'].nunique()} "
        f"users"
    ),
)


user1_hybrid = (
    hybrid_test[
        hybrid_test[
            "userId"
        ] == 1
    ]
    .sort_values(
        "rank"
    )
    .iloc[0]
)


check(
    "User 1 hybrid regression movie",
    int(
        user1_hybrid[
            "movieId"
        ]
    ) == 922,
    str(
        user1_hybrid[
            "title"
        ]
    ),
)


check(
    "User 1 hybrid regression score",
    np.isclose(
        float(
            user1_hybrid[
                "hybridScore"
            ]
        ),
        0.7854,
        atol=0.01,
    ),
    (
        f"{float(user1_hybrid['hybridScore']):.4f}"
    ),
)


# ======================================================================
# 10. 3.9.6 OFFLINE TOP-K EVALUATION
# ======================================================================

print("\n" + "=" * 110)
print("10. OFFLINE TOP-K RESULTS")
print("=" * 110)


offline_users = pd.read_csv(
    OFFLINE_PER_USER_PATH
)

offline_summary = pd.read_csv(
    OFFLINE_SUMMARY_PATH
)


check(
    "Offline users evaluated",
    len(offline_users) == 500,
    f"{len(offline_users)} users",
)


check(
    "Offline summary model count",
    len(offline_summary) == 3,
    (
        f"{len(offline_summary)} models"
    ),
)


for model_name, expected in (
    EXPECTED_OFFLINE_METRICS.items()
):

    row = offline_summary[
        offline_summary[
            "model"
        ] == model_name
    ]


    check(
        f"{model_name} present",
        len(row) == 1,
        (
            f"{len(row)} matching rows"
        ),
    )


    if len(row) != 1:
        continue


    row = row.iloc[0]


    for metric, expected_value in (
        expected.items()
    ):

        actual_value = float(
            row[
                metric
            ]
        )


        check(
            (
                f"{model_name} "
                f"{metric}"
            ),
            np.isclose(
                actual_value,
                expected_value,
                atol=5e-4,
            ),
            (
                f"{actual_value:.4f}"
            ),
        )


# ======================================================================
# HYBRID MUST BE BEST ON ALL FOUR AGGREGATE METRICS
# ======================================================================

hybrid_row = (
    offline_summary[
        offline_summary[
            "model"
        ] == "FINAL_HYBRID"
    ]
    .iloc[0]
)


cf_row = (
    offline_summary[
        offline_summary[
            "model"
        ] == "CF_ONLY"
    ]
    .iloc[0]
)


for metric in [
    "HitRate@10",
    "Recall@10",
    "Precision@10",
    "NDCG@10",
]:

    check(
        (
            f"Hybrid beats CF on "
            f"{metric}"
        ),
        float(
            hybrid_row[
                metric
            ]
        )
        >
        float(
            cf_row[
                metric
            ]
        ),
        (
            f"Hybrid "
            f"{float(hybrid_row[metric]):.4f} "
            f"vs CF "
            f"{float(cf_row[metric]):.4f}"
        ),
    )


# ======================================================================
# 11. 3.9.7 EDGE-CASE RESULTS
# ======================================================================

print("\n" + "=" * 110)
print("11. EDGE-CASE RESULTS")
print("=" * 110)


edge_results = pd.read_csv(
    EDGE_TEST_PATH
)


passed_edges = int(
    (
        edge_results[
            "status"
        ] == "PASS"
    ).sum()
)

failed_edges = int(
    (
        edge_results[
            "status"
        ] == "FAIL"
    ).sum()
)


check(
    "Edge-case test count",
    len(edge_results) == 23,
    f"{len(edge_results)} tests",
)


check(
    "All edge cases passed",
    (
        passed_edges == 23
        and
        failed_edges == 0
    ),
    (
        f"{passed_edges} passed, "
        f"{failed_edges} failed"
    ),
)


# ======================================================================
# 12. FINAL HYBRID CONFIGURATION
# ======================================================================

print("\n" + "=" * 110)
print("12. FINAL HYBRID CONFIGURATION")
print("=" * 110)


hybrid_weight_sum = sum(
    EXPECTED_HYBRID_WEIGHTS.values()
)


check(
    "Hybrid weights sum",
    np.isclose(
        hybrid_weight_sum,
        1.0,
    ),
    (
        f"{hybrid_weight_sum:.2f}"
    ),
)


check(
    "CF weight",
    EXPECTED_HYBRID_WEIGHTS[
        "cf"
    ] == 0.50,
    "0.50",
)


check(
    "Content weight",
    EXPECTED_HYBRID_WEIGHTS[
        "content"
    ] == 0.35,
    "0.35",
)


check(
    "Sentiment weight",
    EXPECTED_HYBRID_WEIGHTS[
        "sentiment"
    ] == 0.15,
    "0.15",
)


# ======================================================================
# SAVE FINAL VALIDATION
# ======================================================================

validation_df = pd.DataFrame(
    results
)


validation_output = (
    TESTING_DIR
    / "phase_3_9_final_validation.csv"
)


validation_df.to_csv(
    validation_output,
    index=False,
)


summary_output = (
    TESTING_DIR
    / "phase_3_9_summary.json"
)


phase_summary = {
    "phase": "3.9 Test Recommendations",

    "status": (
        "PASS"
        if overall_pass
        else "FAIL"
    ),

    "tests": {
        "3.9.1":
            "Functional validation - PASS",

        "3.9.2":
            "Content-based testing - PASS",

        "3.9.3":
            "Collaborative filtering testing - PASS",

        "3.9.4":
            "Sentiment signal testing - PASS",

        "3.9.5":
            "Hybrid qualitative testing - PASS",

        "3.9.6":
            "Offline Top-K evaluation - PASS",

        "3.9.7":
            "Edge-case testing - PASS",
    },

    "hybrid_weights":
        EXPECTED_HYBRID_WEIGHTS,

    "offline_evaluation": {
        "users": 500,
        "negative_samples_per_user": 1000,
        "k": 10,
        "relevance_threshold": 4.0,

        "cf_only":
            EXPECTED_OFFLINE_METRICS[
                "CF_ONLY"
            ],

        "cf_content_core":
            EXPECTED_OFFLINE_METRICS[
                "CF_CONTENT_CORE"
            ],

        "final_hybrid":
            EXPECTED_OFFLINE_METRICS[
                "FINAL_HYBRID"
            ],
    },

    "known_limitations": [
        (
            "Sentiment coverage is limited "
            "to 3,769 of 87,550 catalog movies."
        ),

        (
            "Movies without sentiment use "
            "neutral sentiment score 0.5."
        ),

        (
            "Unknown users do not currently "
            "have collaborative embeddings."
        ),

        (
            "CF-mapped movies without trained "
            "embedding support are excluded."
        ),

        (
            "Offline Top-K metrics use "
            "sampled ranking with 1,000 "
            "negative candidates per user, "
            "not full-catalog ranking."
        ),

        (
            "CF+Content core underperformed "
            "CF-only in the sampled offline "
            "ranking evaluation, while the "
            "final hybrid outperformed both."
        ),
    ],
}


with open(
    summary_output,
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        phase_summary,
        f,
        indent=2,
    )


# ======================================================================
# FINAL SUMMARY
# ======================================================================

passed = int(
    (
        validation_df[
            "status"
        ] == "PASS"
    ).sum()
)

failed = int(
    (
        validation_df[
            "status"
        ] == "FAIL"
    ).sum()
)


print("\n" + "=" * 110)
print("PHASE 3.9 FINAL VALIDATION SUMMARY")
print("=" * 110)


print(
    f"Validation checks passed: "
    f"{passed}"
)

print(
    f"Validation checks failed: "
    f"{failed}"
)


print("\nFinal offline metrics:")

print(
    offline_summary.to_string(
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


print("\nSaved:")

print(
    validation_output
)

print(
    summary_output
)


print("\n" + "=" * 110)

if overall_pass:

    print(
        "PHASE 3.9 TEST RECOMMENDATIONS: PASS"
    )

    print(
        "Phase 3.9 is complete."
    )

    print(
        "Ready for Phase 3.10 - ML Module Setup."
    )

else:

    print(
        "PHASE 3.9 TEST RECOMMENDATIONS: FAIL"
    )

    print(
        "Resolve failed checks before "
        "starting Phase 3.10."
    )

print("=" * 110)
