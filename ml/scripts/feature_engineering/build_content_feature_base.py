import pandas as pd
from pathlib import Path


# -------------------------------------------------------
# Paths
# -------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = BASE_DIR / "data" / "cleaned" / "movies_clean_final.csv"
OUTPUT_DIR = BASE_DIR / "data" / "features"
OUTPUT_FILE = OUTPUT_DIR / "content_feature_base.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# -------------------------------------------------------
# Load data
# -------------------------------------------------------

print("Loading movies...")

movies = pd.read_csv(INPUT_FILE)

print(f"Movies loaded: {len(movies):,}")


# -------------------------------------------------------
# Validate required columns
# -------------------------------------------------------

required_columns = [
    "movieId",
    "title",
    "movielens_genres",
    "genres",
    "keywords",
    "overview",
    "tagline",
    "cast",
    "director",
    "original_language",
    "release_year",
    "runtime",
    "popularity",
    "vote_average",
    "vote_count",
    "tmdbId",
    "has_content_features",
]

missing_columns = [
    column
    for column in required_columns
    if column not in movies.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )


# -------------------------------------------------------
# Basic text cleaning function
# -------------------------------------------------------

def clean_text(series):
    return (
        series
        .fillna("")
        .astype(str)
        .str.replace(r"[\r\n\t]+", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )


# -------------------------------------------------------
# Create genre feature
# -------------------------------------------------------

# Prefer TMDB genres.
# If TMDB genres are missing, fall back to MovieLens genres.

movies["genres_text"] = movies["genres"]

missing_tmdb_genres = (
    movies["genres_text"].isna()
    | (movies["genres_text"].astype(str).str.strip() == "")
)

movies.loc[
    missing_tmdb_genres,
    "genres_text"
] = movies.loc[
    missing_tmdb_genres,
    "movielens_genres"
]

movies["genres_text"] = clean_text(
    movies["genres_text"]
)

# MovieLens sometimes uses this value
movies["genres_text"] = movies["genres_text"].replace(
    "(no genres listed)",
    ""
)


# -------------------------------------------------------
# Clean textual features
# -------------------------------------------------------

movies["keywords_text"] = clean_text(
    movies["keywords"]
)

movies["overview_text"] = clean_text(
    movies["overview"]
)

movies["tagline_text"] = clean_text(
    movies["tagline"]
)

movies["cast_text"] = clean_text(
    movies["cast"]
)

movies["director_text"] = clean_text(
    movies["director"]
)

movies["language_text"] = clean_text(
    movies["original_language"]
)


# -------------------------------------------------------
# Feature availability indicators
# -------------------------------------------------------

text_feature_columns = [
    "genres_text",
    "keywords_text",
    "overview_text",
    "tagline_text",
    "cast_text",
    "director_text",
    "language_text",
]

for column in text_feature_columns:
    indicator_name = f"has_{column}"

    movies[indicator_name] = (
        movies[column].str.len() > 0
    )


# Number of useful text fields available for each movie
movies["available_content_fields"] = (
    movies[text_feature_columns]
    .ne("")
    .sum(axis=1)
)


# -------------------------------------------------------
# TMDB metadata availability
# -------------------------------------------------------

movies["has_tmdb_metadata"] = (
    movies["tmdbId"].notna()
)


# -------------------------------------------------------
# Select feature-engineering dataset
# -------------------------------------------------------

feature_base = movies[
    [
        "movieId",
        "tmdbId",
        "title",

        "genres_text",
        "keywords_text",
        "overview_text",
        "tagline_text",
        "cast_text",
        "director_text",
        "language_text",

        "release_year",
        "runtime",

        "popularity",
        "vote_average",
        "vote_count",

        "has_tmdb_metadata",
        "has_content_features",
        "available_content_fields",

        "has_genres_text",
        "has_keywords_text",
        "has_overview_text",
        "has_tagline_text",
        "has_cast_text",
        "has_director_text",
        "has_language_text",
    ]
].copy()


# -------------------------------------------------------
# Validation
# -------------------------------------------------------

print("\nValidation")
print("-" * 60)

print(
    f"Rows: {len(feature_base):,}"
)

print(
    f"Unique movie IDs: "
    f"{feature_base['movieId'].nunique():,}"
)

print(
    f"Duplicate movie IDs: "
    f"{feature_base['movieId'].duplicated().sum():,}"
)

print(
    f"Movies with TMDB metadata: "
    f"{feature_base['has_tmdb_metadata'].sum():,}"
)

print(
    f"Movies marked with content features: "
    f"{feature_base['has_content_features'].sum():,}"
)


print("\nFeature availability:")
print(
    feature_base[
        [
            "has_genres_text",
            "has_keywords_text",
            "has_overview_text",
            "has_tagline_text",
            "has_cast_text",
            "has_director_text",
            "has_language_text",
        ]
    ]
    .sum()
)


print("\nAvailable content field distribution:")
print(
    feature_base[
        "available_content_fields"
    ]
    .value_counts()
    .sort_index()
)


# -------------------------------------------------------
# Save
# -------------------------------------------------------

feature_base.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\nFeature base saved to:\n{OUTPUT_FILE}"
)