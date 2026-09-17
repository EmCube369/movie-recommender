import pandas as pd
from pathlib import Path


# -------------------------------------------------------
# Paths
# -------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

RATINGS_FILE = (
    BASE_DIR
    / "data"
    / "cleaned"
    / "ratings_clean.csv"
)

MOVIE_STATS_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "collaborative"
    / "movie_rating_stats.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "features"
    / "collaborative"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

INTERACTIONS_FILE = (
    OUTPUT_DIR
    / "cf_interactions.csv"
)

USER_MAPPING_FILE = (
    OUTPUT_DIR
    / "cf_user_mapping.csv"
)

MOVIE_MAPPING_FILE = (
    OUTPUT_DIR
    / "cf_movie_mapping.csv"
)


# -------------------------------------------------------
# Settings
# -------------------------------------------------------

CHUNK_SIZE = 1_000_000

MIN_MOVIE_RATINGS = 5


# -------------------------------------------------------
# Load movie statistics
# -------------------------------------------------------

print("Loading movie statistics...")

movie_stats = pd.read_csv(
    MOVIE_STATS_FILE
)


eligible_movies = movie_stats[
    movie_stats["rating_count"]
    >= MIN_MOVIE_RATINGS
].copy()


eligible_movie_ids = set(
    eligible_movies["movieId"]
    .astype(int)
    .tolist()
)


print(
    f"Movies with >= {MIN_MOVIE_RATINGS} ratings: "
    f"{len(eligible_movie_ids):,}"
)


# -------------------------------------------------------
# First pass
#
# Determine which users remain after movie filtering
# and calculate exact retained interaction counts.
# -------------------------------------------------------

print("\nFirst pass: analyzing filtered interactions...")


filtered_user_counts = None

total_rows = 0
retained_rows = 0


reader = pd.read_csv(
    RATINGS_FILE,
    chunksize=CHUNK_SIZE,
    usecols=[
        "userId",
        "movieId",
        "rating",
        "timestamp",
    ]
)


for chunk_number, chunk in enumerate(
    reader,
    start=1
):

    total_rows += len(chunk)

    filtered = chunk[
        chunk["movieId"].isin(
            eligible_movie_ids
        )
    ]

    retained_rows += len(filtered)


    chunk_user_counts = (
        filtered
        .groupby("userId")
        ["rating"]
        .count()
    )


    if filtered_user_counts is None:

        filtered_user_counts = (
            chunk_user_counts
        )

    else:

        filtered_user_counts = (
            filtered_user_counts.add(
                chunk_user_counts,
                fill_value=0
            )
        )


    print(
        f"Chunk {chunk_number}: "
        f"{total_rows:,} ratings processed"
    )


filtered_user_counts = (
    filtered_user_counts
    .astype("int64")
)


# -------------------------------------------------------
# Interaction statistics
# -------------------------------------------------------

removed_rows = (
    total_rows - retained_rows
)

retention_percentage = (
    retained_rows
    / total_rows
    * 100
)


print("\n" + "=" * 70)
print("COLLABORATIVE FILTERING RESULT")
print("=" * 70)

print(
    f"Original ratings: "
    f"{total_rows:,}"
)

print(
    f"Retained ratings: "
    f"{retained_rows:,}"
)

print(
    f"Removed ratings: "
    f"{removed_rows:,}"
)

print(
    f"Retention: "
    f"{retention_percentage:.4f}%"
)

print(
    f"Active users after filtering: "
    f"{len(filtered_user_counts):,}"
)

print(
    f"Movies after filtering: "
    f"{len(eligible_movie_ids):,}"
)


# -------------------------------------------------------
# User distribution after filtering
# -------------------------------------------------------

print("\nUser rating counts after movie filtering:")

print(
    filtered_user_counts.describe(
        percentiles=[
            0.01,
            0.05,
            0.10,
            0.25,
            0.50,
            0.75,
            0.90,
            0.95,
            0.99,
        ]
    )
)


print("\nUsers below selected interaction counts:")

for threshold in [
    5,
    10,
    20
]:

    count = (
        filtered_user_counts
        < threshold
    ).sum()

    print(
        f"< {threshold:>2}: "
        f"{count:,}"
    )


# -------------------------------------------------------
# Build user mapping
# -------------------------------------------------------

print("\nCreating user mapping...")


user_mapping = pd.DataFrame({
    "userId": sorted(
        filtered_user_counts.index
        .astype(int)
        .tolist()
    )
})


user_mapping["userIndex"] = range(
    len(user_mapping)
)


user_mapping["rating_count"] = (
    user_mapping["userId"]
    .map(
        filtered_user_counts
        .to_dict()
    )
    .astype("int64")
)


# -------------------------------------------------------
# Build movie mapping
# -------------------------------------------------------

print("Creating movie mapping...")


movie_mapping = (
    eligible_movies[
        [
            "movieId",
            "rating_count",
            "mean_rating",
        ]
    ]
    .copy()
    .sort_values("movieId")
    .reset_index(drop=True)
)


movie_mapping["movieIndex"] = range(
    len(movie_mapping)
)


# Reorder columns

movie_mapping = movie_mapping[
    [
        "movieId",
        "movieIndex",
        "rating_count",
        "mean_rating",
    ]
]


# -------------------------------------------------------
# Save mappings
# -------------------------------------------------------

user_mapping.to_csv(
    USER_MAPPING_FILE,
    index=False
)

movie_mapping.to_csv(
    MOVIE_MAPPING_FILE,
    index=False
)


print(
    f"\nSaved user mapping:\n"
    f"{USER_MAPPING_FILE}"
)

print(
    f"\nSaved movie mapping:\n"
    f"{MOVIE_MAPPING_FILE}"
)


# -------------------------------------------------------
# Create lookup dictionaries
# -------------------------------------------------------

user_to_index = dict(
    zip(
        user_mapping["userId"],
        user_mapping["userIndex"],
    )
)


movie_to_index = dict(
    zip(
        movie_mapping["movieId"],
        movie_mapping["movieIndex"],
    )
)


# -------------------------------------------------------
# Remove old output if script is rerun
# -------------------------------------------------------

if INTERACTIONS_FILE.exists():

    INTERACTIONS_FILE.unlink()


# -------------------------------------------------------
# Second pass
#
# Create model-ready interaction dataset.
# -------------------------------------------------------

print(
    "\nSecond pass: "
    "creating model-ready interactions..."
)


reader = pd.read_csv(
    RATINGS_FILE,
    chunksize=CHUNK_SIZE,
    usecols=[
        "userId",
        "movieId",
        "rating",
        "timestamp",
    ]
)


written_rows = 0
first_chunk = True


for chunk_number, chunk in enumerate(
    reader,
    start=1
):

    filtered = chunk[
        chunk["movieId"].isin(
            eligible_movie_ids
        )
    ].copy()


    # Convert MovieLens IDs to
    # contiguous model indices

    filtered["userIndex"] = (
        filtered["userId"]
        .map(user_to_index)
        .astype("int32")
    )


    filtered["movieIndex"] = (
        filtered["movieId"]
        .map(movie_to_index)
        .astype("int32")
    )


    filtered["rating"] = (
        filtered["rating"]
        .astype("float32")
    )


    # Keep timestamp so we can later perform
    # temporal train / validation / test splits.

    interactions = filtered[
        [
            "userIndex",
            "movieIndex",
            "rating",
            "timestamp",
        ]
    ]


    interactions.to_csv(
        INTERACTIONS_FILE,
        mode="w" if first_chunk else "a",
        header=first_chunk,
        index=False,
    )


    written_rows += len(
        interactions
    )

    first_chunk = False


    print(
        f"Chunk {chunk_number}: "
        f"{written_rows:,} interactions written"
    )


# -------------------------------------------------------
# Final validation
# -------------------------------------------------------

print("\n" + "=" * 70)
print("FINAL COLLABORATIVE FEATURE VALIDATION")
print("=" * 70)


print(
    f"Interactions expected: "
    f"{retained_rows:,}"
)

print(
    f"Interactions written: "
    f"{written_rows:,}"
)

print(
    f"Users: "
    f"{len(user_mapping):,}"
)

print(
    f"Movies: "
    f"{len(movie_mapping):,}"
)

print(
    f"User index range: "
    f"0 - {len(user_mapping) - 1:,}"
)

print(
    f"Movie index range: "
    f"0 - {len(movie_mapping) - 1:,}"
)


if written_rows != retained_rows:

    raise ValueError(
        "Interaction row count mismatch."
    )


print("\nCollaborative feature engineering completed.")

print(
    f"\nInteractions:\n"
    f"{INTERACTIONS_FILE}"
)