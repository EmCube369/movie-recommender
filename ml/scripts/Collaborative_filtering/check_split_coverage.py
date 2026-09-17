import numpy as np
from pathlib import Path


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

SPLIT_DIR = (
    BASE_DIR
    / "data"
    / "features"
    / "collaborative"
    / "splits"
)


# ============================================================
# LOAD MOVIE ARRAYS
# ============================================================

train_movies = np.load(
    SPLIT_DIR / "train_movies.npy",
    mmap_mode="r"
)

validation_movies = np.load(
    SPLIT_DIR / "validation_movies.npy",
    mmap_mode="r"
)

test_movies = np.load(
    SPLIT_DIR / "test_movies.npy",
    mmap_mode="r"
)


# ============================================================
# UNIQUE MOVIES
# ============================================================

train_unique = np.unique(train_movies)
validation_unique = np.unique(validation_movies)
test_unique = np.unique(test_movies)


print("=" * 70)
print("MOVIE COVERAGE")
print("=" * 70)

print(
    "Unique movies in train      :",
    f"{len(train_unique):,}"
)

print(
    "Unique movies in validation :",
    f"{len(validation_unique):,}"
)

print(
    "Unique movies in test       :",
    f"{len(test_unique):,}"
)


# ============================================================
# UNSEEN MOVIES
# ============================================================

unseen_validation_movies = np.setdiff1d(
    validation_unique,
    train_unique
)

unseen_test_movies = np.setdiff1d(
    test_unique,
    train_unique
)


print("\n" + "=" * 70)
print("COLD-START MOVIES")
print("=" * 70)

print(
    "Validation movies unseen in train:",
    f"{len(unseen_validation_movies):,}"
)

print(
    "Test movies unseen in train      :",
    f"{len(unseen_test_movies):,}"
)


# ============================================================
# COUNT AFFECTED INTERACTIONS
# ============================================================

validation_unseen_mask = np.isin(
    validation_movies,
    unseen_validation_movies
)

test_unseen_mask = np.isin(
    test_movies,
    unseen_test_movies
)


validation_unseen_count = int(
    validation_unseen_mask.sum()
)

test_unseen_count = int(
    test_unseen_mask.sum()
)


print("\n" + "=" * 70)
print("AFFECTED INTERACTIONS")
print("=" * 70)

print(
    "Validation interactions with unseen movies:",
    f"{validation_unseen_count:,}",
    f"({validation_unseen_count / len(validation_movies) * 100:.4f}%)"
)

print(
    "Test interactions with unseen movies      :",
    f"{test_unseen_count:,}",
    f"({test_unseen_count / len(test_movies) * 100:.4f}%)"
)


# ============================================================
# EXAMPLES
# ============================================================

if len(unseen_validation_movies) > 0:

    print("\nExample unseen validation movieIndexes:")
    print(unseen_validation_movies[:20])


if len(unseen_test_movies) > 0:

    print("\nExample unseen test movieIndexes:")
    print(unseen_test_movies[:20])