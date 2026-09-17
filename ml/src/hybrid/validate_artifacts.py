from pathlib import Path
import json
import pickle

import numpy as np
import pandas as pd
import scipy.sparse as sp
import torch


# ============================================================
# PATHS
# ============================================================

ML_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = ML_ROOT / "data"
MODELS_DIR = ML_ROOT / "models"

CF_FEATURE_DIR = DATA_DIR / "features" / "collaborative"
CF_MODEL_DIR = MODELS_DIR / "collaborative"

CBF_MODEL_DIR = MODELS_DIR / "content_based"

SENTIMENT_DIR = DATA_DIR / "processed" / "sentiment"

MOVIES_PATH = DATA_DIR / "processed" / "movies_clean_final.csv"


# ============================================================
# HELPERS
# ============================================================

def section(title):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def check_file(path):
    if not path.exists():
        raise FileNotFoundError(f"Missing artifact: {path}")

    size_mb = path.stat().st_size / (1024 * 1024)
    print(f"[OK] {path.name:<40} {size_mb:>10.2f} MB")


# ============================================================
# 1. REQUIRED FILE CHECK
# ============================================================

section("1. REQUIRED ARTIFACT FILES")

required_files = [
    # Common
    MOVIES_PATH,

    # Collaborative
    CF_MODEL_DIR / "matrix_factorization_best.pt",
    CF_MODEL_DIR / "cf_seen_movie_indexes.npy",
    CF_MODEL_DIR / "training_metadata.json",
    CF_FEATURE_DIR / "cf_user_mapping.csv",
    CF_FEATURE_DIR / "cf_movie_mapping.csv",
    CF_FEATURE_DIR / "cf_interactions.csv",

    # Content-based
    CBF_MODEL_DIR / "movies_cbf.csv",
    CBF_MODEL_DIR / "movie_id_to_index.pkl",
    CBF_MODEL_DIR / "content_weights.pkl",

    CBF_MODEL_DIR / "genre_matrix.npz",
    CBF_MODEL_DIR / "keyword_matrix.npz",
    CBF_MODEL_DIR / "cast_matrix.npz",
    CBF_MODEL_DIR / "director_matrix.npz",
    CBF_MODEL_DIR / "overview_matrix.npz",
    CBF_MODEL_DIR / "tagline_matrix.npz",

    CBF_MODEL_DIR / "genre_tfidf.pkl",
    CBF_MODEL_DIR / "keyword_tfidf.pkl",
    CBF_MODEL_DIR / "cast_tfidf.pkl",
    CBF_MODEL_DIR / "director_tfidf.pkl",
    CBF_MODEL_DIR / "overview_tfidf.pkl",
    CBF_MODEL_DIR / "tagline_tfidf.pkl",

    # Sentiment
    SENTIMENT_DIR / "movie_sentiment_final.csv",
    SENTIMENT_DIR / "sentiment_metadata.json",
]

for path in required_files:
    check_file(path)

print("\nAll required files exist.")


# ============================================================
# 2. MASTER MOVIE CATALOG
# ============================================================

section("2. MASTER MOVIE CATALOG")

movies = pd.read_csv(MOVIES_PATH)

print("Rows:", len(movies))
print("Columns:", len(movies.columns))
print("Unique movieId:", movies["movieId"].nunique())
print("Duplicate movieId:", movies["movieId"].duplicated().sum())


# ============================================================
# 3. COLLABORATIVE ARTIFACTS
# ============================================================

section("3. COLLABORATIVE FILTERING")

cf_users = pd.read_csv(CF_FEATURE_DIR / "cf_user_mapping.csv")
cf_movies = pd.read_csv(CF_FEATURE_DIR / "cf_movie_mapping.csv")

seen_movie_indexes = np.load(
    CF_MODEL_DIR / "cf_seen_movie_indexes.npy",
    allow_pickle=True
)

with open(CF_MODEL_DIR / "training_metadata.json", "r") as f:
    cf_metadata = json.load(f)

print("CF users:", len(cf_users))
print("CF movies:", len(cf_movies))
print("Seen movie index artifact shape:", seen_movie_indexes.shape)

print("\nTraining metadata:")
for key, value in cf_metadata.items():
    print(f"  {key}: {value}")


# ============================================================
# 4. INSPECT PYTORCH CHECKPOINT
# ============================================================

section("4. COLLABORATIVE MODEL CHECKPOINT")

checkpoint_path = CF_MODEL_DIR / "matrix_factorization_best.pt"

checkpoint = torch.load(
    checkpoint_path,
    map_location="cpu",
    weights_only=False
)

print("Checkpoint Python type:", type(checkpoint))

if isinstance(checkpoint, dict):
    print("\nCheckpoint keys:")

    for key in checkpoint.keys():
        print(" ", key)

    if "model_state_dict" in checkpoint:
        state_dict = checkpoint["model_state_dict"]

        print("\nModel state_dict tensors:")

        for key, value in state_dict.items():
            if hasattr(value, "shape"):
                print(f"  {key:<40} {tuple(value.shape)}")

    elif all(hasattr(v, "shape") for v in checkpoint.values()):
        print("\nCheckpoint appears to be a raw state_dict.")

        for key, value in checkpoint.items():
            print(f"  {key:<40} {tuple(value.shape)}")

else:
    print("Checkpoint may contain the complete PyTorch model.")


# ============================================================
# 5. CONTENT-BASED ARTIFACTS
# ============================================================

section("5. CONTENT-BASED FILTERING")

movies_cbf = pd.read_csv(
    CBF_MODEL_DIR / "movies_cbf.csv"
)

with open(CBF_MODEL_DIR / "movie_id_to_index.pkl", "rb") as f:
    movie_id_to_index = pickle.load(f)

with open(CBF_MODEL_DIR / "content_weights.pkl", "rb") as f:
    content_weights = pickle.load(f)

print("CBF movies:", len(movies_cbf))
print("movie_id_to_index entries:", len(movie_id_to_index))
print("Content weights:", content_weights)

matrix_names = [
    "genre",
    "keyword",
    "cast",
    "director",
    "overview",
    "tagline",
]

for name in matrix_names:
    matrix = sp.load_npz(
        CBF_MODEL_DIR / f"{name}_matrix.npz"
    )

    print(
        f"{name:<10}"
        f" shape={matrix.shape}"
        f" nnz={matrix.nnz:,}"
    )


# ============================================================
# 6. SENTIMENT ARTIFACTS
# ============================================================

section("6. SENTIMENT ANALYSIS")

sentiment = pd.read_csv(
    SENTIMENT_DIR / "movie_sentiment_final.csv"
)

with open(SENTIMENT_DIR / "sentiment_metadata.json", "r") as f:
    sentiment_metadata = json.load(f)

print("Sentiment movies:", len(sentiment))
print("Unique movieId:", sentiment["movieId"].nunique())
print("Duplicate movieId:", sentiment["movieId"].duplicated().sum())

print("\nSentiment columns:")
for column in sentiment.columns:
    print(" ", column)

print("\nSentiment metadata:")
for key, value in sentiment_metadata.items():
    print(f"  {key}: {value}")


# ============================================================
# 7. CROSS-MODEL MOVIE COVERAGE
# ============================================================

section("7. CROSS-MODEL COVERAGE")

catalog_ids = set(movies["movieId"])
cf_ids = set(cf_movies["movieId"])
cbf_ids = set(movies_cbf["movieId"])
sentiment_ids = set(sentiment["movieId"])

print(f"Master catalog : {len(catalog_ids):,}")
print(f"CF movies      : {len(cf_ids):,}")
print(f"CBF movies     : {len(cbf_ids):,}")
print(f"Sentiment      : {len(sentiment_ids):,}")

print()
print(
    "CF ∩ CBF:",
    f"{len(cf_ids & cbf_ids):,}"
)

print(
    "CF ∩ Sentiment:",
    f"{len(cf_ids & sentiment_ids):,}"
)

print(
    "CBF ∩ Sentiment:",
    f"{len(cbf_ids & sentiment_ids):,}"
)

print(
    "All three:",
    f"{len(cf_ids & cbf_ids & sentiment_ids):,}"
)


# ============================================================
# FINAL
# ============================================================

section("ARTIFACT VALIDATION COMPLETE")

print("All required hybrid recommendation artifacts were found.")
print("No model training was performed.")