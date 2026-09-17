import sys
from pathlib import Path

import pandas as pd


# ============================================================
# IMPORT PATH
# ============================================================

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


from recommender.artifact_loader import ArtifactLoader
from recommender.config import MOVIE_SENTIMENT_FILE


def main():
    print("=" * 80)
    print("SENTIMENT ARTIFACT INSPECTION")
    print("=" * 80)

    loader = ArtifactLoader()

    # ========================================================
    # 1. FILE
    # ========================================================

    print("\n1. SENTIMENT FILE")
    print("-" * 80)

    print(f"Path: {MOVIE_SENTIMENT_FILE}")
    print(
        f"Size: "
        f"{MOVIE_SENTIMENT_FILE.stat().st_size / (1024 ** 2):.2f} MB"
    )

    # ========================================================
    # 2. DATASET
    # ========================================================

    print("\n2. DATASET SUMMARY")
    print("-" * 80)

    sentiment = loader.movie_sentiment

    print(f"Rows          : {len(sentiment):,}")
    print(f"Columns       : {len(sentiment.columns):,}")
    print(
        f"Unique movies : "
        f"{sentiment['movieId'].nunique():,}"
    )

    print("\nColumns:")

    for column in sentiment.columns:
        print(
            f"  {column:<30} "
            f"dtype={sentiment[column].dtype}"
        )

    # ========================================================
    # 3. SAMPLE ROWS
    # ========================================================

    print("\n3. SAMPLE ROWS")
    print("-" * 80)

    print(
        sentiment
        .head(10)
        .to_string(index=False)
    )

    # ========================================================
    # 4. NUMERIC COLUMN RANGES
    # ========================================================

    print("\n4. NUMERIC COLUMN RANGES")
    print("-" * 80)

    numeric_columns = (
        sentiment
        .select_dtypes(
            include="number"
        )
        .columns
    )

    for column in numeric_columns:

        series = sentiment[column]

        print(
            f"{column:<30} "
            f"min={series.min():.6f} "
            f"max={series.max():.6f} "
            f"mean={series.mean():.6f} "
            f"missing={series.isna().sum():,}"
        )

    # ========================================================
    # 5. DATA QUALITY
    # ========================================================

    print("\n5. DATA QUALITY")
    print("-" * 80)

    duplicate_movies = (
        sentiment["movieId"]
        .duplicated()
        .sum()
    )

    print(
        f"Duplicate movieIds : "
        f"{duplicate_movies:,}"
    )

    print(
        f"Missing movieIds   : "
        f"{sentiment['movieId'].isna().sum():,}"
    )

    assert duplicate_movies == 0

    assert (
        sentiment["movieId"]
        .isna()
        .sum()
        == 0
    )

    print(
        "PASS  - Sentiment movieIds are valid"
    )

    # ========================================================
    # 6. CATALOG COVERAGE
    # ========================================================

    print("\n6. CATALOG COVERAGE")
    print("-" * 80)

    catalog = loader.movies

    sentiment_ids = set(
        sentiment["movieId"]
        .astype(int)
    )

    catalog_ids = set(
        catalog["movieId"]
        .astype(int)
    )

    matched = (
        sentiment_ids
        & catalog_ids
    )

    missing_from_catalog = (
        sentiment_ids
        - catalog_ids
    )

    coverage = (
        len(matched)
        / len(catalog_ids)
        * 100
    )

    print(
        f"Catalog movies          : "
        f"{len(catalog_ids):,}"
    )

    print(
        f"Sentiment movies        : "
        f"{len(sentiment_ids):,}"
    )

    print(
        f"Matched sentiment movies: "
        f"{len(matched):,}"
    )

    print(
        f"Missing from catalog    : "
        f"{len(missing_from_catalog):,}"
    )

    print(
        f"Catalog coverage        : "
        f"{coverage:.4f}%"
    )

    assert not missing_from_catalog

    print(
        "PASS  - All sentiment movies exist "
        "in the catalog"
    )

    # ========================================================
    # FINAL
    # ========================================================

    print()

    print("=" * 80)
    print("SENTIMENT ARTIFACT INSPECTION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()