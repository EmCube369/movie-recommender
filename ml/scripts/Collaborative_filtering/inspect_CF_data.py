import pandas as pd
from pathlib import Path

BASE_DIR = BASE_DIR = Path(__file__).resolve().parents[2]

INTERACTIONS_PATH = (
    BASE_DIR
    / "data"
    / "features"
    / "collaborative"
    / "cf_interactions.csv"
)
USER_MAPPING_PATH = (
    BASE_DIR
    / "data"
    / "features"
    / "collaborative"
    / "cf_user_mapping.csv"
)
MOVIE_MAPPING_PATH = (
    BASE_DIR
    / "data"
    / "features"
    / "collaborative"
    / "cf_movie_mapping.csv"
)


print("=" * 70)
print("COLLABORATIVE FILTERING DATA")
print("=" * 70)


# ------------------------------------------------------------
# 1. Interactions
# ------------------------------------------------------------

interactions_sample = pd.read_csv(
    INTERACTIONS_PATH,
    nrows=10
)

print("\nINTERACTIONS")
print("-" * 70)

print("Columns:")
print(interactions_sample.columns.tolist())

print("\nSample:")
print(interactions_sample)

print("\nData types:")
print(interactions_sample.dtypes)


# ------------------------------------------------------------
# 2. User mapping
# ------------------------------------------------------------

user_mapping = pd.read_csv(USER_MAPPING_PATH)

print("\n" + "=" * 70)
print("USER MAPPING")
print("=" * 70)

print("Shape:", user_mapping.shape)
print("Columns:", user_mapping.columns.tolist())
print(user_mapping.head())


# ------------------------------------------------------------
# 3. Movie mapping
# ------------------------------------------------------------

movie_mapping = pd.read_csv(MOVIE_MAPPING_PATH)

print("\n" + "=" * 70)
print("MOVIE MAPPING")
print("=" * 70)

print("Shape:", movie_mapping.shape)
print("Columns:", movie_mapping.columns.tolist())
print(movie_mapping.head())


# ------------------------------------------------------------
# 4. Model dimensions
# ------------------------------------------------------------

num_users = len(user_mapping)
num_movies = len(movie_mapping)

print("\n" + "=" * 70)
print("MODEL DIMENSIONS")
print("=" * 70)

print(f"Number of users : {num_users:,}")
print(f"Number of movies: {num_movies:,}")