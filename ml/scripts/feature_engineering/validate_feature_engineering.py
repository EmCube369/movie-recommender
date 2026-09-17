import pandas as pd
from pathlib import Path
import unicodedata
import re


# =======================================================
# Paths
# =======================================================

BASE_DIR = Path(__file__).resolve().parents[2]

FEATURE_DIR = (
    BASE_DIR
    / "data"
    / "features"
)

CLEAN_DIR = (
    BASE_DIR
    / "data"
    / "cleaned"
)


CONTENT_FILE = (
    FEATURE_DIR
    / "content_features_engineered.csv"
)

CF_DIR = (
    FEATURE_DIR
    / "collaborative"
)

CF_INTERACTIONS_FILE = (
    CF_DIR
    / "cf_interactions.csv"
)

CF_USER_MAPPING_FILE = (
    CF_DIR
    / "cf_user_mapping.csv"
)

CF_MOVIE_MAPPING_FILE = (
    CF_DIR
    / "cf_movie_mapping.csv"
)


SENTIMENT_DIR = (
    FEATURE_DIR
    / "sentiment"
)

TAG_VOCAB_FILE = (
    SENTIMENT_DIR
    / "tag_vocabulary.csv"
)

MOVIE_TAG_FEATURES_FILE = (
    SENTIMENT_DIR
    / "movie_tag_features.csv"
)

MOVIE_TAG_STATS_FILE = (
    SENTIMENT_DIR
    / "movie_tag_stats.csv"
)

RAW_TAGS_FILE = (
    CLEAN_DIR
    / "tags_clean.csv"
)


# =======================================================
# Helper
# =======================================================

def normalize_tag(value):

    if pd.isna(value):
        return ""

    text = str(value)

    text = unicodedata.normalize(
        "NFKC",
        text
    )

    text = text.casefold()

    text = re.sub(
        r"[\r\n\t]+",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


def check_contiguous(series):
    """
    Check that indices are:
        0, 1, 2, 3 ... n-1
    """

    values = (
        series
        .sort_values()
        .reset_index(drop=True)
    )

    expected = pd.Series(
        range(len(values)),
        dtype=values.dtype
    )

    return values.equals(expected)


# =======================================================
# 1. Content features
# =======================================================

print("\n" + "=" * 70)
print("1. CONTENT FEATURES")
print("=" * 70)


content = pd.read_csv(
    CONTENT_FILE
)


catalog_movie_ids = set(
    content["movieId"]
    .astype(int)
    .tolist()
)


print(
    f"Rows: "
    f"{len(content):,}"
)

print(
    f"Unique movie IDs: "
    f"{content['movieId'].nunique():,}"
)

print(
    f"Duplicate movie IDs: "
    f"{content['movieId'].duplicated().sum():,}"
)

print(
    f"Movies with zero engineered text features: "
    f"{(content['engineered_feature_count'] == 0).sum():,}"
)

print(
    f"Movies with at least one engineered feature: "
    f"{(content['engineered_feature_count'] > 0).sum():,}"
)


# =======================================================
# 2. Collaborative mappings
# =======================================================

print("\n" + "=" * 70)
print("2. COLLABORATIVE MAPPINGS")
print("=" * 70)


users = pd.read_csv(
    CF_USER_MAPPING_FILE
)

cf_movies = pd.read_csv(
    CF_MOVIE_MAPPING_FILE
)


print(
    f"Users: "
    f"{len(users):,}"
)

print(
    f"Unique user IDs: "
    f"{users['userId'].nunique():,}"
)

print(
    f"Unique user indexes: "
    f"{users['userIndex'].nunique():,}"
)

print(
    f"User indexes contiguous: "
    f"{check_contiguous(users['userIndex'])}"
)


print(
    f"\nCF movies: "
    f"{len(cf_movies):,}"
)

print(
    f"Unique movie IDs: "
    f"{cf_movies['movieId'].nunique():,}"
)

print(
    f"Unique movie indexes: "
    f"{cf_movies['movieIndex'].nunique():,}"
)

print(
    f"Movie indexes contiguous: "
    f"{check_contiguous(cf_movies['movieIndex'])}"
)


invalid_cf_movies = (
    ~cf_movies["movieId"]
    .isin(catalog_movie_ids)
).sum()


print(
    f"CF movies missing from catalog: "
    f"{invalid_cf_movies:,}"
)


# =======================================================
# 3. Collaborative interactions
# =======================================================

print("\n" + "=" * 70)
print("3. COLLABORATIVE INTERACTIONS")
print("=" * 70)


CHUNK_SIZE = 1_000_000

interaction_count = 0

missing_values = 0

invalid_users = 0
invalid_movies = 0

rating_min = None
rating_max = None

timestamp_min = None
timestamp_max = None


max_user_index = len(users) - 1
max_movie_index = len(cf_movies) - 1


reader = pd.read_csv(
    CF_INTERACTIONS_FILE,
    chunksize=CHUNK_SIZE
)


for chunk_number, chunk in enumerate(
    reader,
    start=1
):

    interaction_count += len(chunk)

    missing_values += (
        chunk.isna()
        .sum()
        .sum()
    )


    invalid_users += (
        (chunk["userIndex"] < 0)
        |
        (chunk["userIndex"] > max_user_index)
    ).sum()


    invalid_movies += (
        (chunk["movieIndex"] < 0)
        |
        (chunk["movieIndex"] > max_movie_index)
    ).sum()


    chunk_rating_min = (
        chunk["rating"].min()
    )

    chunk_rating_max = (
        chunk["rating"].max()
    )


    if (
        rating_min is None
        or chunk_rating_min < rating_min
    ):
        rating_min = chunk_rating_min


    if (
        rating_max is None
        or chunk_rating_max > rating_max
    ):
        rating_max = chunk_rating_max


    chunk_timestamp_min = (
        chunk["timestamp"].min()
    )

    chunk_timestamp_max = (
        chunk["timestamp"].max()
    )


    if (
        timestamp_min is None
        or chunk_timestamp_min < timestamp_min
    ):
        timestamp_min = chunk_timestamp_min


    if (
        timestamp_max is None
        or chunk_timestamp_max > timestamp_max
    ):
        timestamp_max = chunk_timestamp_max


    print(
        f"Validated chunk {chunk_number}: "
        f"{interaction_count:,} interactions"
    )


print(
    f"\nInteractions: "
    f"{interaction_count:,}"
)

print(
    f"Missing values: "
    f"{missing_values:,}"
)

print(
    f"Invalid user indexes: "
    f"{invalid_users:,}"
)

print(
    f"Invalid movie indexes: "
    f"{invalid_movies:,}"
)

print(
    f"Rating range: "
    f"{rating_min} - {rating_max}"
)

print(
    f"Timestamp range: "
    f"{timestamp_min} - {timestamp_max}"
)


# =======================================================
# 4. Tag vocabulary
# =======================================================

print("\n" + "=" * 70)
print("4. TAG VOCABULARY")
print("=" * 70)


tag_vocab = pd.read_csv(
    TAG_VOCAB_FILE
)


print(
    f"Unique tags: "
    f"{len(tag_vocab):,}"
)

print(
    f"Duplicate normalized tags: "
    f"{tag_vocab['tag_clean'].duplicated().sum():,}"
)

print(
    f"Duplicate tag indexes: "
    f"{tag_vocab['tagIndex'].duplicated().sum():,}"
)

print(
    f"Tag indexes contiguous: "
    f"{check_contiguous(tag_vocab['tagIndex'])}"
)


empty_vocab_tags = (
    tag_vocab["tag_clean"]
    .fillna("")
    .str.strip()
    .eq("")
    .sum()
)


print(
    f"Empty normalized tags: "
    f"{empty_vocab_tags:,}"
)


# =======================================================
# 5. Movie-tag features
# =======================================================

print("\n" + "=" * 70)
print("5. MOVIE-TAG FEATURES")
print("=" * 70)


movie_tags = pd.read_csv(
    MOVIE_TAG_FEATURES_FILE
)


movie_tag_stats = pd.read_csv(
    MOVIE_TAG_STATS_FILE
)


print(
    f"Movie-tag pairs: "
    f"{len(movie_tags):,}"
)


duplicate_pairs = (
    movie_tags[
        [
            "movieId",
            "tagIndex",
        ]
    ]
    .duplicated()
    .sum()
)


print(
    f"Duplicate movie-tag pairs: "
    f"{duplicate_pairs:,}"
)


invalid_tag_movie_ids = (
    ~movie_tags["movieId"]
    .isin(catalog_movie_ids)
).sum()


print(
    f"Movie-tag rows with invalid movie ID: "
    f"{invalid_tag_movie_ids:,}"
)


valid_tag_indexes = set(
    tag_vocab["tagIndex"]
    .astype(int)
    .tolist()
)


invalid_tag_indexes = (
    ~movie_tags["tagIndex"]
    .isin(valid_tag_indexes)
).sum()


print(
    f"Invalid tag indexes: "
    f"{invalid_tag_indexes:,}"
)


print(
    f"Movies with tag stats: "
    f"{len(movie_tag_stats):,}"
)

print(
    f"Duplicate movie stats: "
    f"{movie_tag_stats['movieId'].duplicated().sum():,}"
)


# =======================================================
# 6. Tag event-count consistency
# =======================================================

print("\n" + "=" * 70)
print("6. TAG COUNT CONSISTENCY")
print("=" * 70)


vocab_event_total = int(
    tag_vocab[
        "event_count"
    ].sum()
)


movie_tag_event_total = int(
    movie_tags[
        "tag_event_count"
    ].sum()
)


movie_stats_event_total = int(
    movie_tag_stats[
        "tag_event_count"
    ].sum()
)


print(
    f"Vocabulary event total: "
    f"{vocab_event_total:,}"
)

print(
    f"Movie-tag event total: "
    f"{movie_tag_event_total:,}"
)

print(
    f"Movie-stats event total: "
    f"{movie_stats_event_total:,}"
)


print(
    "All tag event totals match: "
    f"{vocab_event_total == movie_tag_event_total == movie_stats_event_total}"
)


# =======================================================
# 7. Find tags removed during normalization
# =======================================================

print("\n" + "=" * 70)
print("7. TAGS REMOVED DURING NORMALIZATION")
print("=" * 70)


raw_tags = pd.read_csv(
    RAW_TAGS_FILE,
    usecols=[
        "userId",
        "movieId",
        "tag",
    ]
)


raw_tags["tag_clean"] = (
    raw_tags["tag"]
    .apply(normalize_tag)
)


removed_tags = raw_tags[
    raw_tags["tag_clean"].eq("")
]


print(
    f"Removed tag rows: "
    f"{len(removed_tags):,}"
)


if len(removed_tags) > 0:

    print(
        removed_tags[
            [
                "userId",
                "movieId",
                "tag",
            ]
        ]
        .to_string(index=False)
    )


# =======================================================
# 8. Cross-component coverage
# =======================================================

print("\n" + "=" * 70)
print("8. CROSS-COMPONENT COVERAGE")
print("=" * 70)


cf_movie_ids = set(
    cf_movies["movieId"]
    .astype(int)
    .tolist()
)


tagged_movie_ids = set(
    movie_tag_stats["movieId"]
    .astype(int)
    .tolist()
)


content_feature_ids = set(
    content.loc[
        content[
            "engineered_feature_count"
        ] > 0,
        "movieId"
    ]
    .astype(int)
    .tolist()
)


print(
    f"Catalog movies: "
    f"{len(catalog_movie_ids):,}"
)

print(
    f"Movies with content features: "
    f"{len(content_feature_ids):,}"
)

print(
    f"Movies usable by CF: "
    f"{len(cf_movie_ids):,}"
)

print(
    f"Movies with tags: "
    f"{len(tagged_movie_ids):,}"
)


print(
    f"\nContent + CF: "
    f"{len(content_feature_ids & cf_movie_ids):,}"
)

print(
    f"Content + tags: "
    f"{len(content_feature_ids & tagged_movie_ids):,}"
)



# -------------------------------------------------------
# Cross-component intersections
# -------------------------------------------------------

content_cf_count = len(
    content_feature_ids
    & cf_movie_ids
)

content_tags_count = len(
    content_feature_ids
    & tagged_movie_ids
)

cf_tags_count = len(
    cf_movie_ids
    & tagged_movie_ids
)

all_three_count = len(
    content_feature_ids
    & cf_movie_ids
    & tagged_movie_ids
)


print(
    f"\nContent + CF: "
    f"{content_cf_count:,}"
)

print(
    f"Content + tags: "
    f"{content_tags_count:,}"
)

print(
    f"CF + tags: "
    f"{cf_tags_count:,}"
)

print(
    f"All three: "
    f"{all_three_count:,}"
)

# =======================================================
# Final result
# =======================================================

print("\n" + "=" * 70)
print("FEATURE ENGINEERING VALIDATION COMPLETE")
print("=" * 70)

print(
    "If duplicate/invalid counts are zero, "
    "index mappings are contiguous, and tag totals "
    "match, the feature datasets are ready."
)