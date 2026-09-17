from pathlib import Path
import pickle

import numpy as np
import pandas as pd


# ======================================================================
# PATHS
# ======================================================================

ML_ROOT = Path(__file__).resolve().parents[1]

PROCESSED_DIR = (
    ML_ROOT
    / "data"
    / "processed"
)

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


MOVIES_PATH = (
    PROCESSED_DIR
    / "movies_clean_final.csv"
)

USER_MAPPING_PATH = (
    CF_FEATURE_DIR
    / "cf_user_mapping.csv"
)

MOVIE_MAPPING_PATH = (
    CF_FEATURE_DIR
    / "cf_movie_mapping.csv"
)

CF_SEEN_PATH = (
    CF_MODEL_DIR
    / "cf_seen_movie_indexes.npy"
)

CONTENT_MAPPING_PATH = (
    CONTENT_DIR
    / "movie_id_to_index.pkl"
)

SENTIMENT_PATH = (
    SENTIMENT_DIR
    / "movie_sentiment_final.csv"
)


# ======================================================================
# SETTINGS
# ======================================================================

NEUTRAL_SENTIMENT = 0.50

POSITIVE_RATING_THRESHOLD = 4.0

NORMAL_TOP_K = 10


# ======================================================================
# START
# ======================================================================

print("=" * 100)
print("3.9.7 EDGE-CASE TESTING")
print("=" * 100)


# ======================================================================
# LOAD ARTIFACTS
# ======================================================================

movies = pd.read_csv(
    MOVIES_PATH,
    low_memory=False,
)

user_mapping = pd.read_csv(
    USER_MAPPING_PATH
)

movie_mapping = pd.read_csv(
    MOVIE_MAPPING_PATH
)

sentiment = pd.read_csv(
    SENTIMENT_PATH,
    low_memory=False,
)


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


seen_movie_indexes = np.unique(
    np.load(
        CF_SEEN_PATH
    ).astype(np.int64)
)


# ======================================================================
# LOOKUPS
# ======================================================================

user_id_to_index = dict(
    zip(
        user_mapping[
            "userId"
        ].astype(int),

        user_mapping[
            "userIndex"
        ].astype(int),
    )
)


movie_id_to_cf_index = dict(
    zip(
        movie_mapping[
            "movieId"
        ].astype(int),

        movie_mapping[
            "movieIndex"
        ].astype(int),
    )
)


movie_id_by_cf_index = np.full(
    len(movie_mapping),
    -1,
    dtype=np.int64,
)


movie_id_by_cf_index[
    movie_mapping[
        "movieIndex"
    ]
    .astype(int)
    .to_numpy()
] = (
    movie_mapping[
        "movieId"
    ]
    .astype(int)
    .to_numpy()
)


seen_movie_index_set = set(
    seen_movie_indexes.tolist()
)


sentiment["sentimentNormalized"] = np.clip(
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


if "title" in movies.columns:

    title_col = "title"

elif "title_x" in movies.columns:

    title_col = "title_x"

else:

    raise ValueError(
        "Movie title column not found."
    )


title_lookup = (
    movies[
        [
            "movieId",
            title_col,
        ]
    ]
    .drop_duplicates(
        "movieId"
    )
    .set_index(
        "movieId"
    )[
        title_col
    ]
    .to_dict()
)


# ======================================================================
# TEST RESULT STORAGE
# ======================================================================

test_results = []

overall_pass = True


def record_test(
    name,
    passed,
    detail,
):

    global overall_pass

    status = (
        "PASS"
        if passed
        else "FAIL"
    )


    print(
        f"{status:<5} - "
        f"{name}: "
        f"{detail}"
    )


    test_results.append(
        {
            "test": name,
            "status": status,
            "detail": detail,
        }
    )


    if not passed:
        overall_pass = False


# ======================================================================
# SAFE PRODUCTION-LIKE HELPERS
# ======================================================================

def resolve_user_index(
    user_id,
):

    if user_id is None:
        raise ValueError(
            "userId cannot be None."
        )


    if isinstance(
        user_id,
        bool,
    ):

        raise ValueError(
            "userId must be an integer."
        )


    try:

        user_id = int(
            user_id
        )

    except (
        TypeError,
        ValueError,
    ):

        raise ValueError(
            "userId must be an integer."
        )


    if (
        user_id
        not in user_id_to_index
    ):

        raise ValueError(
            f"Unknown userId: "
            f"{user_id}"
        )


    return (
        user_id_to_index[
            user_id
        ]
    )


def get_sentiment_score(
    movie_id,
):

    return float(
        sentiment_lookup.get(
            int(movie_id),
            NEUTRAL_SENTIMENT,
        )
    )


def get_supported_cf_index(
    movie_id,
):

    movie_id = int(
        movie_id
    )


    if (
        movie_id
        not in movie_id_to_cf_index
    ):

        return None


    movie_index = (
        movie_id_to_cf_index[
            movie_id
        ]
    )


    if (
        movie_index
        not in seen_movie_index_set
    ):

        return None


    return movie_index


def validate_top_k(
    top_k,
    candidate_count,
):

    if isinstance(
        top_k,
        bool,
    ):

        raise ValueError(
            "top_k must be a positive integer."
        )


    if not isinstance(
        top_k,
        (
            int,
            np.integer,
        ),
    ):

        raise ValueError(
            "top_k must be a positive integer."
        )


    if top_k <= 0:

        raise ValueError(
            "top_k must be greater than zero."
        )


    return min(
        int(top_k),
        int(candidate_count),
    )


def build_candidate_indexes(
    rated_movie_indexes,
):

    rated_movie_indexes = set(
        int(index)

        for index
        in rated_movie_indexes
    )


    return np.array(
        [
            movie_index

            for movie_index
            in seen_movie_indexes

            if movie_index
            not in rated_movie_indexes
        ],
        dtype=np.int64,
    )


def get_positive_history(
    ratings,
):

    ratings = np.asarray(
        ratings,
        dtype=np.float32,
    )


    return (
        ratings
        >= POSITIVE_RATING_THRESHOLD
    )


def safe_empty_content_scores(
    positive_count,
    candidate_count,
):

    if positive_count == 0:

        return np.zeros(
            candidate_count,
            dtype=np.float32,
        )


    raise RuntimeError(
        "This helper is only for "
        "the empty-profile edge case."
    )


# ======================================================================
# 1. KNOWN SPARSE USER
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "1. KNOWN SPARSE USER"
)

print(
    "=" * 100
)


sparse_user_id = 7382


try:

    sparse_index = resolve_user_index(
        sparse_user_id
    )

    record_test(
        "Sparse known user",
        True,
        (
            f"userId {sparse_user_id} "
            f"resolved to userIndex "
            f"{sparse_index}"
        ),
    )

except Exception as exc:

    record_test(
        "Sparse known user",
        False,
        str(exc),
    )


# ======================================================================
# 2. UNKNOWN USER
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "2. UNKNOWN USER"
)

print(
    "=" * 100
)


unknown_user_id = (
    int(
        user_mapping[
            "userId"
        ].max()
    )
    + 1_000_000
)


try:

    resolve_user_index(
        unknown_user_id
    )


    record_test(
        "Unknown user rejection",
        False,
        (
            "Unknown user was "
            "incorrectly accepted."
        ),
    )


except ValueError as exc:

    record_test(
        "Unknown user rejection",
        True,
        str(exc),
    )


# ======================================================================
# 3. INVALID USER INPUTS
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "3. INVALID USER INPUT"
)

print(
    "=" * 100
)


invalid_user_inputs = [
    None,
    "not-a-user",
    True,
]


for invalid_user in (
    invalid_user_inputs
):

    try:

        resolve_user_index(
            invalid_user
        )


        record_test(
            (
                "Invalid user input "
                f"{repr(invalid_user)}"
            ),
            False,
            "Input was accepted.",
        )


    except ValueError as exc:

        record_test(
            (
                "Invalid user input "
                f"{repr(invalid_user)}"
            ),
            True,
            str(exc),
        )


# ======================================================================
# 4. MISSING SENTIMENT FALLBACK
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "4. MISSING SENTIMENT"
)

print(
    "=" * 100
)


supported_movie_ids = (
    movie_id_by_cf_index[
        seen_movie_indexes
    ]
)


missing_sentiment_candidates = [
    int(movie_id)

    for movie_id
    in supported_movie_ids

    if int(movie_id)
    not in sentiment_lookup
]


assert (
    len(
        missing_sentiment_candidates
    )
    > 0
)


missing_sentiment_movie_id = (
    missing_sentiment_candidates[
        0
    ]
)


missing_sentiment_score = (
    get_sentiment_score(
        missing_sentiment_movie_id
    )
)


missing_title = title_lookup.get(
    missing_sentiment_movie_id,
    "<unknown>",
)


record_test(
    "Neutral sentiment fallback",
    np.isclose(
        missing_sentiment_score,
        0.5,
    ),
    (
        f"movieId "
        f"{missing_sentiment_movie_id} "
        f"({missing_title}) -> "
        f"{missing_sentiment_score:.4f}"
    ),
)


# ======================================================================
# 5. REAL SENTIMENT VALUE
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "5. REAL SENTIMENT VALUE"
)

print(
    "=" * 100
)


real_sentiment_movie_id = None


for movie_id in supported_movie_ids:

    movie_id = int(
        movie_id
    )


    if (
        movie_id
        in sentiment_lookup
        and
        not np.isclose(
            sentiment_lookup[
                movie_id
            ],
            0.5,
        )
    ):

        real_sentiment_movie_id = (
            movie_id
        )

        break


assert (
    real_sentiment_movie_id
    is not None
)


real_sentiment_score = (
    get_sentiment_score(
        real_sentiment_movie_id
    )
)


record_test(
    "Existing sentiment lookup",
    (
        0.0
        <= real_sentiment_score
        <= 1.0
        and
        not np.isclose(
            real_sentiment_score,
            0.5,
        )
    ),
    (
        f"movieId "
        f"{real_sentiment_movie_id} "
        f"({title_lookup.get(real_sentiment_movie_id, '<unknown>')}) "
        f"-> {real_sentiment_score:.4f}"
    ),
)


# ======================================================================
# 6. CATALOG MOVIE NOT IN CF
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "6. CONTENT/CATALOG-ONLY MOVIE"
)

print(
    "=" * 100
)


catalog_movie_ids = set(
    movies[
        "movieId"
    ]
    .astype(int)
    .tolist()
)


cf_movie_ids = set(
    movie_mapping[
        "movieId"
    ]
    .astype(int)
    .tolist()
)


catalog_only_ids = (
    catalog_movie_ids
    - cf_movie_ids
)


assert (
    len(
        catalog_only_ids
    )
    > 0
)


catalog_only_movie_id = int(
    next(
        iter(
            catalog_only_ids
        )
    )
)


catalog_only_cf_index = (
    get_supported_cf_index(
        catalog_only_movie_id
    )
)


record_test(
    "Catalog-only movie exclusion",
    catalog_only_cf_index is None,
    (
        f"movieId "
        f"{catalog_only_movie_id} "
        f"({title_lookup.get(catalog_only_movie_id, '<unknown>')}) "
        f"is not CF-recommendable."
    ),
)


# ======================================================================
# 7. CF-MAPPED BUT UNTRAINED MOVIE
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "7. CF-MAPPED BUT UNTRAINED MOVIE"
)

print(
    "=" * 100
)


all_cf_indexes = set(
    range(
        len(
            movie_mapping
        )
    )
)


untrained_cf_indexes = (
    all_cf_indexes
    - seen_movie_index_set
)


assert (
    len(
        untrained_cf_indexes
    )
    > 0
)


untrained_index = int(
    next(
        iter(
            untrained_cf_indexes
        )
    )
)


untrained_movie_id = int(
    movie_id_by_cf_index[
        untrained_index
    ]
)


resolved_untrained_index = (
    get_supported_cf_index(
        untrained_movie_id
    )
)


record_test(
    "Untrained CF movie exclusion",
    resolved_untrained_index is None,
    (
        f"movieId "
        f"{untrained_movie_id} "
        f"({title_lookup.get(untrained_movie_id, '<unknown>')}) "
        f"has CF mapping but no trained "
        f"movie embedding support."
    ),
)


# ======================================================================
# 8. CONTENT COVERAGE FOR SUPPORTED CF MOVIES
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "8. CONTENT COVERAGE"
)

print(
    "=" * 100
)


unsupported_content_ids = [
    int(movie_id)

    for movie_id
    in supported_movie_ids

    if int(movie_id)
    not in content_index_by_movie_id
]


record_test(
    "CF candidate content coverage",
    (
        len(
            unsupported_content_ids
        )
        == 0
    ),
    (
        f"{len(unsupported_content_ids):,} "
        f"CF-supported movies missing "
        f"content mapping."
    ),
)


# ======================================================================
# 9. USER WITH NO POSITIVE RATINGS
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "9. NO POSITIVE RATINGS"
)

print(
    "=" * 100
)


synthetic_ratings = np.array(
    [
        0.5,
        1.0,
        2.0,
        2.5,
        3.0,
        3.5,
    ],
    dtype=np.float32,
)


positive_mask = (
    get_positive_history(
        synthetic_ratings
    )
)


positive_count = int(
    positive_mask.sum()
)


fallback_content = (
    safe_empty_content_scores(
        positive_count,
        5,
    )
)


record_test(
    "No-positive-history handling",
    (
        positive_count == 0
        and
        np.allclose(
            fallback_content,
            0.0,
        )
    ),
    (
        "No liked movies -> "
        "content component safely "
        "falls back to zero scores."
    ),
)


# ======================================================================
# 10. POSITIVE RATING BOUNDARY
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "10. POSITIVE RATING BOUNDARY"
)

print(
    "=" * 100
)


boundary_ratings = np.array(
    [
        3.5,
        4.0,
        4.5,
        5.0,
    ],
    dtype=np.float32,
)


boundary_mask = (
    get_positive_history(
        boundary_ratings
    )
)


expected_boundary = np.array(
    [
        False,
        True,
        True,
        True,
    ]
)


record_test(
    "Positive threshold boundary",
    np.array_equal(
        boundary_mask,
        expected_boundary,
    ),
    (
        "3.5 excluded; "
        "4.0, 4.5 and 5.0 included."
    ),
)


# ======================================================================
# 11. ALL MOVIES ALREADY RATED
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "11. NO REMAINING CANDIDATES"
)

print(
    "=" * 100
)


all_rated = set(
    seen_movie_indexes.tolist()
)


remaining_candidates = (
    build_candidate_indexes(
        all_rated
    )
)


record_test(
    "All candidates already rated",
    (
        len(
            remaining_candidates
        )
        == 0
    ),
    (
        "Candidate builder returns "
        "an empty set instead of "
        "recommending previously rated movies."
    ),
)


# ======================================================================
# 12. NORMAL TOP-K
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "12. TOP-K BOUNDARIES"
)

print(
    "=" * 100
)


resolved_k = validate_top_k(
    10,
    100,
)


record_test(
    "Normal top_k",
    resolved_k == 10,
    (
        f"Requested 10 from 100 "
        f"candidates -> {resolved_k}"
    ),
)


# ======================================================================
# 13. TOP-K LARGER THAN CANDIDATE SET
# ======================================================================

resolved_large_k = (
    validate_top_k(
        100,
        7,
    )
)


record_test(
    "top_k larger than candidates",
    resolved_large_k == 7,
    (
        "Requested 100 from "
        "7 candidates -> returns 7."
    ),
)


# ======================================================================
# 14. ZERO / NEGATIVE TOP-K
# ======================================================================

for invalid_k in [
    0,
    -1,
]:

    try:

        validate_top_k(
            invalid_k,
            100,
        )


        record_test(
            f"Invalid top_k {invalid_k}",
            False,
            "Invalid value accepted.",
        )


    except ValueError as exc:

        record_test(
            f"Invalid top_k {invalid_k}",
            True,
            str(exc),
        )


# ======================================================================
# 15. NON-INTEGER TOP-K
# ======================================================================

for invalid_k in [
    5.5,
    "10",
    None,
    True,
]:

    try:

        validate_top_k(
            invalid_k,
            100,
        )


        record_test(
            (
                "Non-integer top_k "
                f"{repr(invalid_k)}"
            ),
            False,
            "Invalid value accepted.",
        )


    except ValueError as exc:

        record_test(
            (
                "Non-integer top_k "
                f"{repr(invalid_k)}"
            ),
            True,
            str(exc),
        )


# ======================================================================
# 16. CANDIDATE SET HAS NO DUPLICATES
# ======================================================================

print(
    "\n"
    + "=" * 100
)

print(
    "13. CANDIDATE INTEGRITY"
)

print(
    "=" * 100
)


sample_rated_indexes = set(
    seen_movie_indexes[
        :100
    ].tolist()
)


candidate_indexes = (
    build_candidate_indexes(
        sample_rated_indexes
    )
)


candidate_unique = (
    len(
        candidate_indexes
    )
    ==
    len(
        np.unique(
            candidate_indexes
        )
    )
)


rated_overlap = (
    set(
        candidate_indexes.tolist()
    )
    &
    sample_rated_indexes
)


record_test(
    "Candidate uniqueness",
    candidate_unique,
    (
        f"{len(candidate_indexes):,} "
        f"candidate indexes are unique."
    ),
)


record_test(
    "Rated candidate exclusion",
    len(rated_overlap) == 0,
    (
        f"Overlap with rated movies: "
        f"{len(rated_overlap)}"
    ),
)


# ======================================================================
# SAVE RESULTS
# ======================================================================

results_df = pd.DataFrame(
    test_results
)


output_path = (
    OUTPUT_DIR
    / "edge_case_test_results.csv"
)


results_df.to_csv(
    output_path,
    index=False,
)


# ======================================================================
# SUMMARY
# ======================================================================

passed_count = int(
    (
        results_df[
            "status"
        ]
        == "PASS"
    ).sum()
)


failed_count = int(
    (
        results_df[
            "status"
        ]
        == "FAIL"
    ).sum()
)


print(
    "\n"
    + "=" * 100
)

print(
    "3.9.7 EDGE-CASE TEST SUMMARY"
)

print(
    "=" * 100
)


print(
    f"Tests passed: {passed_count}"
)

print(
    f"Tests failed: {failed_count}"
)


print(
    "\nSaved:"
)

print(
    output_path
)


print(
    "\n"
    + "=" * 100
)

print(
    "3.9.7 FINAL RESULT"
)

print(
    "=" * 100
)


if overall_pass:

    print(
        "PASS - All edge-case tests passed."
    )

else:

    print(
        "FAIL - One or more edge-case tests failed."
    )


print(
    "\nProduction note:"
)

print(
    "Unknown users are intentionally rejected "
    "because the current CF model has no "
    "embedding for unseen users."
)

print(
    "A new-user/cold-start fallback can be "
    "added when the ML module/API is packaged."
)