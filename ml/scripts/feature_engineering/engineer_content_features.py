import pandas as pd
from pathlib import Path
import re
import unicodedata


# -------------------------------------------------------
# Paths
# -------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "content_feature_base.csv"
)

OUTPUT_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "content_features_engineered.csv"
)


# -------------------------------------------------------
# Load data
# -------------------------------------------------------

print("Loading content feature base...")

df = pd.read_csv(INPUT_FILE)

print(f"Movies loaded: {len(df):,}")


# -------------------------------------------------------
# Helper functions
# -------------------------------------------------------

def normalize_token(text):
    """
    Convert a feature value into a single ML-friendly token
    while preserving Unicode letters and numbers.

    Examples:
        Tom Hanks       -> tomhanks
        Science Fiction -> sciencefiction
        Jean-Claude     -> jeanclaude
    """

    if pd.isna(text):
        return ""

    text = str(text).strip().casefold()

    # Normalize Unicode representation
    text = unicodedata.normalize("NFKC", text)

    # Give & semantic meaning before punctuation removal
    text = text.replace("&", "and")

    # Keep Unicode letters and numbers.
    # Remove spaces and punctuation.
    text = "".join(
        char for char in text
        if char.isalnum()
    )

    return text


def normalize_pipe_features(value, prefix):
    """
    Convert pipe-separated values into prefixed tokens.

    Example:
        Action|Science Fiction

    becomes:
        genre_action genre_sciencefiction
    """

    if pd.isna(value):
        return ""

    value = str(value).strip()

    if not value:
        return ""

    items = value.split("|")

    tokens = []

    for item in items:

        token = normalize_token(item)

        if token:
            tokens.append(f"{prefix}_{token}")

    # Remove duplicates while preserving order
    tokens = list(dict.fromkeys(tokens))

    return " ".join(tokens)


def normalize_text(value):
    """
    Basic cleanup for natural-language fields such
    as overview and tagline.

    We deliberately do NOT remove normal words here.
    """

    if pd.isna(value):
        return ""

    value = str(value).lower()

    value = re.sub(
        r"[\r\n\t]+",
        " ",
        value
    )

    value = re.sub(
        r"\s+",
        " ",
        value
    )

    return value.strip()


# -------------------------------------------------------
# Structured categorical/text features
# -------------------------------------------------------

print("Engineering genres...")

df["genres_tokens"] = df["genres_text"].apply(
    lambda x: normalize_pipe_features(
        x,
        "genre"
    )
)


print("Engineering keywords...")

df["keywords_tokens"] = df["keywords_text"].apply(
    lambda x: normalize_pipe_features(
        x,
        "kw"
    )
)


print("Engineering cast...")

df["cast_tokens"] = df["cast_text"].apply(
    lambda x: normalize_pipe_features(
        x,
        "cast"
    )
)


print("Engineering directors...")

# Director is currently normally one person,
# but using the same pipe-aware function keeps
# the code safe if multiple directors appear.

df["director_tokens"] = df["director_text"].apply(
    lambda x: normalize_pipe_features(
        x,
        "director"
    )
)


# -------------------------------------------------------
# Language feature
# -------------------------------------------------------

df["language_token"] = df["language_text"].apply(
    lambda x: (
        f"lang_{normalize_token(x)}"
        if normalize_token(x)
        else ""
    )
)


# -------------------------------------------------------
# Natural language features
# -------------------------------------------------------

print("Cleaning overview text...")

df["overview_clean"] = df["overview_text"].apply(
    normalize_text
)


print("Cleaning tagline text...")

df["tagline_clean"] = df["tagline_text"].apply(
    normalize_text
)


# -------------------------------------------------------
# Numerical/context feature
# -------------------------------------------------------

# Useful later as an optional temporal feature.

df["release_decade"] = (
    pd.to_numeric(
        df["release_year"],
        errors="coerce"
    )
    // 10
    * 10
)


# -------------------------------------------------------
# Feature availability
# -------------------------------------------------------

engineered_columns = [
    "genres_tokens",
    "keywords_tokens",
    "cast_tokens",
    "director_tokens",
    "language_token",
    "overview_clean",
    "tagline_clean",
]


for column in engineered_columns:

    df[f"has_{column}"] = (
        df[column]
        .fillna("")
        .str.len()
        .gt(0)
    )


df["engineered_feature_count"] = (
    df[engineered_columns]
    .fillna("")
    .ne("")
    .sum(axis=1)
)


# -------------------------------------------------------
# Select final engineered dataset
# -------------------------------------------------------

features = df[
    [
        # Identifiers
        "movieId",
        "tmdbId",
        "title",

        # Engineered structured features
        "genres_tokens",
        "keywords_tokens",
        "cast_tokens",
        "director_tokens",
        "language_token",

        # Natural language
        "overview_clean",
        "tagline_clean",

        # Numerical/context
        "release_year",
        "release_decade",
        "runtime",

        # Ranking signals kept for later
        "popularity",
        "vote_average",
        "vote_count",

        # Metadata flags
        "has_tmdb_metadata",
        "has_content_features",
        "engineered_feature_count",
    ]
].copy()


# -------------------------------------------------------
# Validation
# -------------------------------------------------------

print("\n" + "=" * 70)
print("ENGINEERED CONTENT FEATURE VALIDATION")
print("=" * 70)

print(f"Rows: {len(features):,}")

print(
    f"Unique movie IDs: "
    f"{features['movieId'].nunique():,}"
)

print(
    f"Duplicate movie IDs: "
    f"{features['movieId'].duplicated().sum():,}"
)


print("\nFeature availability:")

for column in engineered_columns:

    count = (
        df[column]
        .fillna("")
        .str.len()
        .gt(0)
        .sum()
    )

    print(
        f"{column:<25} "
        f"{count:>8,}"
    )


print("\nEngineered feature count distribution:")

print(
    features[
        "engineered_feature_count"
    ]
    .value_counts()
    .sort_index()
)


# -------------------------------------------------------
# Sample movie
# -------------------------------------------------------

print("\n" + "=" * 70)
print("SAMPLE ENGINEERED MOVIE")
print("=" * 70)

sample = features.iloc[0]

print(f"Movie: {sample['title']}")

print(
    "\nGenres:\n",
    sample["genres_tokens"]
)

print(
    "\nKeywords:\n",
    sample["keywords_tokens"]
)

print(
    "\nCast:\n",
    sample["cast_tokens"]
)

print(
    "\nDirector:\n",
    sample["director_tokens"]
)

print(
    "\nLanguage:\n",
    sample["language_token"]
)

print(
    "\nOverview:\n",
    sample["overview_clean"]
)


# -------------------------------------------------------
# Save
# -------------------------------------------------------

features.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\nSaved engineered content features to:\n"
    f"{OUTPUT_FILE}"
)