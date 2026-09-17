import pandas as pd
from pathlib import Path
import unicodedata
import re


# -------------------------------------------------------
# Paths
# -------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

TAGS_FILE = (
    BASE_DIR
    / "data"
    / "cleaned"
    / "tags_clean.csv"
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
    / "sentiment"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


TAG_VOCAB_FILE = (
    OUTPUT_DIR
    / "tag_vocabulary.csv"
)

MOVIE_TAG_FEATURES_FILE = (
    OUTPUT_DIR
    / "movie_tag_features.csv"
)

MOVIE_TAG_STATS_FILE = (
    OUTPUT_DIR
    / "movie_tag_stats.csv"
)


# -------------------------------------------------------
# Tag normalization
# -------------------------------------------------------

def normalize_tag(value):
    """
    Normalize tag text while preserving its natural
    language structure.

    Examples:

        "  Very Funny  " -> "very funny"
        "SCI-FI"         -> "sci-fi"

    Unlike cast/director tokens, spaces are preserved
    because these may later be analyzed as natural text.
    """

    if pd.isna(value):
        return ""

    text = str(value)

    # Unicode-safe normalization
    text = unicodedata.normalize(
        "NFKC",
        text
    )

    # Unicode-aware lowercase
    text = text.casefold()

    # Remove line breaks / tabs
    text = re.sub(
        r"[\r\n\t]+",
        " ",
        text
    )

    # Collapse repeated whitespace
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# -------------------------------------------------------
# Load movie catalog
# -------------------------------------------------------

print("Loading movie catalog...")

movies = pd.read_csv(
    MOVIES_FILE,
    usecols=[
        "movieId",
        "title",
    ]
)

valid_movie_ids = set(
    movies["movieId"]
    .astype(int)
    .tolist()
)

print(
    f"Movies in catalog: "
    f"{len(valid_movie_ids):,}"
)


# -------------------------------------------------------
# Load tags
# -------------------------------------------------------

print("\nLoading tags...")

tags = pd.read_csv(
    TAGS_FILE,
    usecols=[
        "userId",
        "movieId",
        "tag",
    ],
    dtype={
        "userId": "int32",
        "movieId": "int32",
        "tag": "string",
    },
)

original_rows = len(tags)

print(
    f"Tag rows loaded: "
    f"{original_rows:,}"
)


# -------------------------------------------------------
# Validate movie IDs
# -------------------------------------------------------

invalid_mask = (
    ~tags["movieId"]
    .isin(valid_movie_ids)
)

invalid_rows = (
    invalid_mask.sum()
)

print(
    f"Tags referencing invalid movies: "
    f"{invalid_rows:,}"
)

if invalid_rows > 0:

    raise ValueError(
        "Tag data contains movie IDs that are "
        "not present in the final movie catalog."
    )


# -------------------------------------------------------
# Normalize tags
# -------------------------------------------------------

print("\nNormalizing tag text...")

tags["tag_clean"] = (
    tags["tag"]
    .apply(normalize_tag)
)


# -------------------------------------------------------
# Validate normalization
# -------------------------------------------------------

empty_after_cleaning = (
    tags["tag_clean"]
    .eq("")
    .sum()
)

print(
    f"Empty tags after normalization: "
    f"{empty_after_cleaning:,}"
)


if empty_after_cleaning > 0:

    tags = tags[
        tags["tag_clean"].ne("")
    ].copy()


# -------------------------------------------------------
# Build global tag vocabulary
# -------------------------------------------------------

print("\nBuilding tag vocabulary...")


tag_vocabulary = (
    tags
    .groupby(
        "tag_clean",
        as_index=False
    )
    .agg(
        event_count=(
            "movieId",
            "size"
        ),
        movie_count=(
            "movieId",
            "nunique"
        ),
        user_count=(
            "userId",
            "nunique"
        ),
    )
)


# Stable ordering gives stable tagIndex values
tag_vocabulary = (
    tag_vocabulary
    .sort_values("tag_clean")
    .reset_index(drop=True)
)


tag_vocabulary.insert(
    0,
    "tagIndex",
    range(len(tag_vocabulary))
)


# -------------------------------------------------------
# Build movie-tag features
# -------------------------------------------------------

print(
    "Building movie-tag frequency features..."
)


movie_tag_features = (
    tags
    .groupby(
        [
            "movieId",
            "tag_clean",
        ],
        as_index=False
    )
    .agg(
        tag_event_count=(
            "userId",
            "size"
        ),
        tag_user_count=(
            "userId",
            "nunique"
        ),
    )
)


# Attach compact tag index
movie_tag_features = (
    movie_tag_features
    .merge(
        tag_vocabulary[
            [
                "tagIndex",
                "tag_clean",
            ]
        ],
        on="tag_clean",
        how="left",
        validate="many_to_one",
    )
)


movie_tag_features = (
    movie_tag_features[
        [
            "movieId",
            "tagIndex",
            "tag_clean",
            "tag_event_count",
            "tag_user_count",
        ]
    ]
    .sort_values(
        [
            "movieId",
            "tagIndex",
        ]
    )
    .reset_index(drop=True)
)


# -------------------------------------------------------
# Build per-movie tag statistics
# -------------------------------------------------------

print(
    "Building movie tag statistics..."
)


movie_tag_stats = (
    tags
    .groupby(
        "movieId",
        as_index=False
    )
    .agg(
        tag_event_count=(
            "tag_clean",
            "size"
        ),
        unique_tag_count=(
            "tag_clean",
            "nunique"
        ),
        tagging_user_count=(
            "userId",
            "nunique"
        ),
    )
)


# Add title for inspection
movie_tag_stats = (
    movie_tag_stats
    .merge(
        movies,
        on="movieId",
        how="left",
        validate="one_to_one",
    )
)


movie_tag_stats = (
    movie_tag_stats[
        [
            "movieId",
            "title",
            "tag_event_count",
            "unique_tag_count",
            "tagging_user_count",
        ]
    ]
    .sort_values("movieId")
    .reset_index(drop=True)
)


# -------------------------------------------------------
# Validation
# -------------------------------------------------------

print("\n" + "=" * 70)
print("SENTIMENT / TAG FEATURE VALIDATION")
print("=" * 70)


print(
    f"Original tag events: "
    f"{original_rows:,}"
)

print(
    f"Usable tag events: "
    f"{len(tags):,}"
)

print(
    f"Movies with tags: "
    f"{tags['movieId'].nunique():,}"
)

print(
    f"Unique normalized tags: "
    f"{len(tag_vocabulary):,}"
)

print(
    f"Unique movie-tag pairs: "
    f"{len(movie_tag_features):,}"
)


print(
    "\nTag events per movie:"
)

print(
    movie_tag_stats[
        "tag_event_count"
    ]
    .describe(
        percentiles=[
            0.25,
            0.50,
            0.75,
            0.90,
            0.95,
            0.99,
        ]
    )
)


print(
    "\nUnique tags per movie:"
)

print(
    movie_tag_stats[
        "unique_tag_count"
    ]
    .describe(
        percentiles=[
            0.25,
            0.50,
            0.75,
            0.90,
            0.95,
            0.99,
        ]
    )
)


# -------------------------------------------------------
# Most common tags
# -------------------------------------------------------

print("\n" + "=" * 70)
print("TOP 20 TAGS")
print("=" * 70)


top_tags = (
    tag_vocabulary
    .sort_values(
        "event_count",
        ascending=False
    )
    .head(20)
)


print(
    top_tags[
        [
            "tag_clean",
            "event_count",
            "movie_count",
            "user_count",
        ]
    ]
    .to_string(index=False)
)


# -------------------------------------------------------
# Most tagged movies
# -------------------------------------------------------

print("\n" + "=" * 70)
print("TOP 10 MOST TAGGED MOVIES")
print("=" * 70)


print(
    movie_tag_stats
    .sort_values(
        "tag_event_count",
        ascending=False
    )
    .head(10)
    .to_string(index=False)
)


# -------------------------------------------------------
# Save
# -------------------------------------------------------

tag_vocabulary.to_csv(
    TAG_VOCAB_FILE,
    index=False
)

movie_tag_features.to_csv(
    MOVIE_TAG_FEATURES_FILE,
    index=False
)

movie_tag_stats.to_csv(
    MOVIE_TAG_STATS_FILE,
    index=False
)


print("\nSaved:")

print(TAG_VOCAB_FILE)
print(MOVIE_TAG_FEATURES_FILE)
print(MOVIE_TAG_STATS_FILE)