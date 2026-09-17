import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = BASE_DIR = Path(__file__).resolve().parents[2]
INTERACTIONS_PATH = (
    BASE_DIR
    / "data"
    / "features"
    / "collaborative"
    / "cf_interactions.csv"
)

SPLIT_DIR = (
    BASE_DIR 
    / "data"
    / "features"
    / "collaborative" 
    / "splits"
)
SPLIT_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 1. LOAD INTERACTIONS WITH MEMORY-EFFICIENT TYPES
# ============================================================

print("=" * 70)
print("LOADING COLLABORATIVE INTERACTIONS")
print("=" * 70)

dtypes = {
    "userIndex": "int32",
    "movieIndex": "int32",
    "rating": "float32",
    "timestamp": "int64"
}

interactions = pd.read_csv(
    INTERACTIONS_PATH,
    dtype=dtypes
)

print(f"Total interactions: {len(interactions):,}")

memory_mb = interactions.memory_usage(deep=True).sum() / (1024 ** 2)
print(f"DataFrame memory: {memory_mb:,.2f} MB")


# ============================================================
# 2. CHECK USER RATING COUNTS
# ============================================================

user_counts = interactions.groupby("userIndex").size()

print("\n" + "=" * 70)
print("USER RATING COUNTS")
print("=" * 70)

print(f"Users: {len(user_counts):,}")
print(f"Minimum ratings per user: {user_counts.min():,}")
print(f"Maximum ratings per user: {user_counts.max():,}")
print(f"Average ratings per user: {user_counts.mean():.2f}")

if user_counts.min() < 3:
    raise ValueError(
        "Some users have fewer than 3 ratings, "
        "so chronological train/validation/test splitting is unsafe."
    )


# ============================================================
# 3. SORT EACH USER'S RATINGS CHRONOLOGICALLY
# ============================================================

print("\nSorting interactions by user and timestamp...")

interactions.sort_values(
    ["userIndex", "timestamp"],
    inplace=True,
    kind="mergesort"
)

interactions.reset_index(drop=True, inplace=True)

print("Sorting complete.")


# ============================================================
# 4. FIND POSITION OF EACH RATING WITHIN EACH USER
# ============================================================

position = (
    interactions
    .groupby("userIndex", sort=False)
    .cumcount()
    .to_numpy(dtype=np.int32)
)

ratings_per_user = (
    interactions
    .groupby("userIndex", sort=False)["userIndex"]
    .transform("size")
    .to_numpy(dtype=np.int32)
)


# ============================================================
# 5. CALCULATE 80 / 10 / 10 BOUNDARIES
# ============================================================

train_end = np.floor(ratings_per_user * 0.80).astype(np.int32)
val_end = np.floor(ratings_per_user * 0.90).astype(np.int32)

train_mask = position < train_end

val_mask = (
    (position >= train_end)
    & (position < val_end)
)

test_mask = position >= val_end


# ============================================================
# 6. CREATE SPLITS
# ============================================================

train = interactions.loc[train_mask]
validation = interactions.loc[val_mask]
test = interactions.loc[test_mask]


# ============================================================
# 7. PRINT SPLIT INFORMATION
# ============================================================

total = len(interactions)

print("\n" + "=" * 70)
print("DATASET SPLIT")
print("=" * 70)

print(
    f"Train      : {len(train):,} "
    f"({len(train) / total * 100:.2f}%)"
)

print(
    f"Validation : {len(validation):,} "
    f"({len(validation) / total * 100:.2f}%)"
)

print(
    f"Test       : {len(test):,} "
    f"({len(test) / total * 100:.2f}%)"
)

print(f"\nTotal      : {len(train) + len(validation) + len(test):,}")


# ============================================================
# 8. VERIFY USERS
# ============================================================

print("\n" + "=" * 70)
print("USER COVERAGE")
print("=" * 70)

print(f"Users in train      : {train['userIndex'].nunique():,}")
print(f"Users in validation : {validation['userIndex'].nunique():,}")
print(f"Users in test       : {test['userIndex'].nunique():,}")


# ============================================================
# 9. VERIFY SPLIT INTEGRITY
# ============================================================

assert len(train) + len(validation) + len(test) == len(interactions)

assert train["userIndex"].nunique() == interactions["userIndex"].nunique()

print("\nSplit integrity checks passed.")


# ============================================================
# 10. SAVE AS NUMPY ARRAYS
# ============================================================
#
# We save only the columns required by the CF model.
# These files will later be memory-mapped by PyTorch.
# ============================================================

def save_split(df, name):

    np.save(
        SPLIT_DIR / f"{name}_users.npy",
        df["userIndex"].to_numpy(dtype=np.int32)
    )

    np.save(
        SPLIT_DIR / f"{name}_movies.npy",
        df["movieIndex"].to_numpy(dtype=np.int32)
    )

    np.save(
        SPLIT_DIR / f"{name}_ratings.npy",
        df["rating"].to_numpy(dtype=np.float32)
    )


print("\nSaving splits...")

save_split(train, "train")
save_split(validation, "validation")
save_split(test, "test")

print("Saved successfully.")


print("\n" + "=" * 70)
print("OUTPUT FILES")
print("=" * 70)

for file in sorted(SPLIT_DIR.glob("*.npy")):
    size_mb = file.stat().st_size / (1024 ** 2)
    print(f"{file.name:<30} {size_mb:>10.2f} MB")