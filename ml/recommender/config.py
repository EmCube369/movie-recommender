from pathlib import Path


# ============================================================
# PROJECT PATHS
# ============================================================

# .../Movie-Recommender/ml
ML_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = ML_ROOT / "data"
MODELS_DIR = ML_ROOT / "models"

PROCESSED_DIR = DATA_DIR / "processed"
FEATURES_DIR = DATA_DIR / "features"


# ============================================================
# MOVIE CATALOG
# ============================================================

MOVIES_FILE = PROCESSED_DIR / "movies_clean_final.csv"


# ============================================================
# COLLABORATIVE FILTERING
# ============================================================

CF_FEATURE_DIR = FEATURES_DIR / "collaborative"
CF_MODEL_DIR = MODELS_DIR / "collaborative"

CF_MODEL_FILE = CF_MODEL_DIR / "matrix_factorization_best.pt"

CF_SEEN_MOVIES_FILE = (
    CF_MODEL_DIR / "cf_seen_movie_indexes.npy"
)

CF_USER_MAPPING_FILE = (
    CF_FEATURE_DIR / "cf_user_mapping.csv"
)

CF_MOVIE_MAPPING_FILE = (
    CF_FEATURE_DIR / "cf_movie_mapping.csv"
)


# ============================================================
# CONTENT-BASED FILTERING
# ============================================================

CONTENT_MODEL_DIR = MODELS_DIR / "content_based"

CONTENT_MOVIE_INDEX_FILE = (
    CONTENT_MODEL_DIR / "movie_id_to_index.pkl"
)

CONTENT_WEIGHTS_FILE = (
    CONTENT_MODEL_DIR / "content_weights.pkl"
)

CONTENT_GENRE_MATRIX_FILE = (
    CONTENT_MODEL_DIR / "genre_matrix.npz"
)

CONTENT_KEYWORD_MATRIX_FILE = (
    CONTENT_MODEL_DIR / "keyword_matrix.npz"
)

CONTENT_DIRECTOR_MATRIX_FILE = (
    CONTENT_MODEL_DIR / "director_matrix.npz"
)

CONTENT_CAST_MATRIX_FILE = (
    CONTENT_MODEL_DIR / "cast_matrix.npz"
)

CONTENT_OVERVIEW_MATRIX_FILE = (
    CONTENT_MODEL_DIR / "overview_matrix.npz"
)

CONTENT_TAGLINE_MATRIX_FILE = (
    CONTENT_MODEL_DIR / "tagline_matrix.npz"
)


# ============================================================
# SENTIMENT
# ============================================================

SENTIMENT_DIR = PROCESSED_DIR / "sentiment"

MOVIE_SENTIMENT_FILE = (
    SENTIMENT_DIR / "movie_sentiment_final.csv"
)

# ============================================================
# HYBRID / USER HISTORY
# ============================================================

HYBRID_MODEL_DIR = MODELS_DIR / "hybrid"

USER_HISTORY_INDPTR_FILE = (
    HYBRID_MODEL_DIR / "user_history_indptr.npy"
)

USER_HISTORY_MOVIE_INDEXES_FILE = (
    HYBRID_MODEL_DIR / "user_history_movie_indexes.npy"
)

USER_HISTORY_RATINGS_FILE = (
    HYBRID_MODEL_DIR / "user_history_ratings.npy"
)


# ============================================================
# HYBRID MODEL WEIGHTS
# ============================================================

CF_WEIGHT = 0.50
CONTENT_WEIGHT = 0.35
SENTIMENT_WEIGHT = 0.15

# ============================================================
# HYBRID NORMALIZATION
# ============================================================

CF_MIN_SCORE = 0.5
CF_MAX_SCORE = 5.0

# Content similarity score at which normalization reaches 1.0.
# Preserves the Phase 3.8 hybrid normalization.
CONTENT_NORMALIZATION_MAX = 0.28


# ============================================================
# RECOMMENDATION SETTINGS
# ============================================================

DEFAULT_TOP_N = 10

# Positive ratings used for building a user's content profile
POSITIVE_RATING_THRESHOLD = 4.0

# Used when a movie has no sentiment data
NEUTRAL_SENTIMENT_SCORE = 0.5


# ============================================================
# REQUIRED RUNTIME ARTIFACTS
# ============================================================

REQUIRED_ARTIFACTS = {
    "movie catalog": MOVIES_FILE,

    "CF model": CF_MODEL_FILE,
    "CF seen movies": CF_SEEN_MOVIES_FILE,
    "CF user mapping": CF_USER_MAPPING_FILE,
    "CF movie mapping": CF_MOVIE_MAPPING_FILE,

    "content movie index": CONTENT_MOVIE_INDEX_FILE,
    "content weights": CONTENT_WEIGHTS_FILE,

    "content genre matrix": CONTENT_GENRE_MATRIX_FILE,
    "content keyword matrix": CONTENT_KEYWORD_MATRIX_FILE,
    "content director matrix": CONTENT_DIRECTOR_MATRIX_FILE,
    "content cast matrix": CONTENT_CAST_MATRIX_FILE,
    "content overview matrix": CONTENT_OVERVIEW_MATRIX_FILE,
    "content tagline matrix": CONTENT_TAGLINE_MATRIX_FILE,

    "movie sentiment": MOVIE_SENTIMENT_FILE,

    "history indptr": USER_HISTORY_INDPTR_FILE,
    "history movie indexes": USER_HISTORY_MOVIE_INDEXES_FILE,
    "history ratings": USER_HISTORY_RATINGS_FILE,
}


def validate_required_artifacts() -> None:
    """
    Verify that the core artifacts required by the recommendation
    system exist.

    Raises:
        FileNotFoundError:
            If one or more required artifacts are missing.
    """

    missing = []

    for name, path in REQUIRED_ARTIFACTS.items():
        if not path.exists():
            missing.append((name, path))

    if missing:
        message = [
            "Required ML artifacts are missing:",
            ""
        ]

        for name, path in missing:
            message.append(f"- {name}: {path}")

        raise FileNotFoundError("\n".join(message))