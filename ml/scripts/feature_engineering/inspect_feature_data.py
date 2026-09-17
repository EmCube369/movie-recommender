import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "cleaned"


files = {
    "Movies": "movies_clean_final.csv",
    "Ratings": "ratings_clean.csv",
    "Tags": "tags_clean.csv",
    "Duplicate Mapping": "duplicate_movie_mapping.csv",
    "TMDB Metadata": "tmdb_metadata.csv",
    "TMDB Skipped": "tmdb_skipped_clean.csv",
}


for name, filename in files.items():

    path = DATA_DIR / filename

    print("\n" + "=" * 70)
    print(name)
    print("=" * 70)

    df = pd.read_csv(path)

    print(f"File: {filename}")
    print(f"Shape: {df.shape}")

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes)

    print("\nFirst 3 rows:")
    print(df.head(3))

    print("\nMissing values:")
    print(df.isnull().sum())