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

MOVIES_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "content_features_engineered.csv"
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


# -------------------------------------------------------
# Settings
# -------------------------------------------------------

CHUNK_SIZE = 1_000_000


# -------------------------------------------------------
# Valid movie IDs
# -------------------------------------------------------

print("Loading valid movie IDs...")

movies = pd.read_csv(
    MOVIES_FILE,
    usecols=["movieId"]
)

valid_movie_ids = set(
    movies["movieId"].tolist()
)

print(
    f"Valid movies in catalog: "
    f"{len(valid_movie_ids):,}"
)


# -------------------------------------------------------
# Accumulators
# -------------------------------------------------------

user_counts = None
user_rating_sums = None

movie_counts = None
movie_rating_sums = None

rating_distribution = None

total_rows = 0
invalid_movie_rows = 0

min_timestamp = None
max_timestamp = None


# -------------------------------------------------------
# Process ratings in chunks
# -------------------------------------------------------

print("\nProcessing ratings...")

reader = pd.read_csv(
    RATINGS_FILE,
    chunksize=CHUNK_SIZE
)


for chunk_number, chunk in enumerate(reader, start=1):

    total_rows += len(chunk)

    print(
        f"Chunk {chunk_number}: "
        f"{len(chunk):,} rows "
        f"(total {total_rows:,})"
    )


    # ---------------------------------------------------
    # Validate movie IDs
    # ---------------------------------------------------

    invalid_movie_rows += (
        ~chunk["movieId"].isin(valid_movie_ids)
    ).sum()


    # ---------------------------------------------------
    # User statistics
    # ---------------------------------------------------

    chunk_user_counts = (
        chunk
        .groupby("userId")
        ["rating"]
        .count()
    )

    chunk_user_sums = (
        chunk
        .groupby("userId")
        ["rating"]
        .sum()
    )


    if user_counts is None:

        user_counts = chunk_user_counts
        user_rating_sums = chunk_user_sums

    else:

        user_counts = user_counts.add(
            chunk_user_counts,
            fill_value=0
        )

        user_rating_sums = user_rating_sums.add(
            chunk_user_sums,
            fill_value=0
        )


    # ---------------------------------------------------
    # Movie statistics
    # ---------------------------------------------------

    chunk_movie_counts = (
        chunk
        .groupby("movieId")
        ["rating"]
        .count()
    )

    chunk_movie_sums = (
        chunk
        .groupby("movieId")
        ["rating"]
        .sum()
    )


    if movie_counts is None:

        movie_counts = chunk_movie_counts
        movie_rating_sums = chunk_movie_sums

    else:

        movie_counts = movie_counts.add(
            chunk_movie_counts,
            fill_value=0
        )

        movie_rating_sums = movie_rating_sums.add(
            chunk_movie_sums,
            fill_value=0
        )


    # ---------------------------------------------------
    # Rating distribution
    # ---------------------------------------------------

    chunk_rating_distribution = (
        chunk["rating"]
        .value_counts()
    )


    if rating_distribution is None:

        rating_distribution = (
            chunk_rating_distribution
        )

    else:

        rating_distribution = (
            rating_distribution.add(
                chunk_rating_distribution,
                fill_value=0
            )
        )


    # ---------------------------------------------------
    # Timestamp range
    # ---------------------------------------------------

    chunk_min_timestamp = (
        chunk["timestamp"].min()
    )

    chunk_max_timestamp = (
        chunk["timestamp"].max()
    )


    if (
        min_timestamp is None
        or chunk_min_timestamp < min_timestamp
    ):
        min_timestamp = chunk_min_timestamp


    if (
        max_timestamp is None
        or chunk_max_timestamp > max_timestamp
    ):
        max_timestamp = chunk_max_timestamp


# -------------------------------------------------------
# Convert counts back to integer
# -------------------------------------------------------

user_counts = user_counts.astype("int64")
movie_counts = movie_counts.astype("int64")

rating_distribution = (
    rating_distribution
    .astype("int64")
    .sort_index()
)


# -------------------------------------------------------
# User statistics table
# -------------------------------------------------------

user_stats = pd.DataFrame({
    "rating_count": user_counts,
    "rating_sum": user_rating_sums
})

user_stats["mean_rating"] = (
    user_stats["rating_sum"]
    / user_stats["rating_count"]
)

user_stats = (
    user_stats
    .reset_index()
    .sort_values("userId")
)


# -------------------------------------------------------
# Movie statistics table
# -------------------------------------------------------

movie_stats = pd.DataFrame({
    "rating_count": movie_counts,
    "rating_sum": movie_rating_sums
})

movie_stats["mean_rating"] = (
    movie_stats["rating_sum"]
    / movie_stats["rating_count"]
)

movie_stats = (
    movie_stats
    .reset_index()
    .sort_values("movieId")
)


# -------------------------------------------------------
# Dataset summary
# -------------------------------------------------------

print("\n" + "=" * 70)
print("COLLABORATIVE DATA SUMMARY")
print("=" * 70)

print(
    f"Total ratings: "
    f"{total_rows:,}"
)

print(
    f"Unique users: "
    f"{len(user_stats):,}"
)

print(
    f"Rated movies: "
    f"{len(movie_stats):,}"
)

print(
    f"Ratings referencing invalid movies: "
    f"{invalid_movie_rows:,}"
)


global_mean = (
    user_stats["rating_sum"].sum()
    / total_rows
)

print(
    f"Global mean rating: "
    f"{global_mean:.4f}"
)


# -------------------------------------------------------
# Rating distribution
# -------------------------------------------------------

print("\nRating distribution:")

for rating, count in rating_distribution.items():

    percentage = (
        count / total_rows
    ) * 100

    print(
        f"{rating:>3}: "
        f"{count:>10,} "
        f"({percentage:6.2f}%)"
    )


# -------------------------------------------------------
# User activity distribution
# -------------------------------------------------------

print("\n" + "=" * 70)
print("USER RATING COUNTS")
print("=" * 70)

print(
    user_stats["rating_count"]
    .describe(
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


user_thresholds = [
    5,
    10,
    20,
    50,
    100,
    200,
    500
]

print("\nUsers below thresholds:")

for threshold in user_thresholds:

    count = (
        user_stats["rating_count"]
        < threshold
    ).sum()

    print(
        f"< {threshold:>3} ratings: "
        f"{count:>8,}"
    )


# -------------------------------------------------------
# Movie activity distribution
# -------------------------------------------------------

print("\n" + "=" * 70)
print("MOVIE RATING COUNTS")
print("=" * 70)

print(
    movie_stats["rating_count"]
    .describe(
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


movie_thresholds = [
    2,
    5,
    10,
    20,
    50,
    100,
    500,
    1000
]

print("\nMovies below thresholds:")

for threshold in movie_thresholds:

    count = (
        movie_stats["rating_count"]
        < threshold
    ).sum()

    print(
        f"< {threshold:>4} ratings: "
        f"{count:>8,}"
    )


# -------------------------------------------------------
# Save statistics
# -------------------------------------------------------

USER_OUTPUT = (
    OUTPUT_DIR
    / "user_rating_stats.csv"
)

MOVIE_OUTPUT = (
    OUTPUT_DIR
    / "movie_rating_stats.csv"
)


user_stats.to_csv(
    USER_OUTPUT,
    index=False
)

movie_stats.to_csv(
    MOVIE_OUTPUT,
    index=False
)


print("\nSaved:")

print(USER_OUTPUT)
print(MOVIE_OUTPUT)