import pandas as pd
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    BASE_DIR
    / "data"
    / "features"
    / "content_feature_base.csv"
)


df = pd.read_csv(INPUT_FILE)


columns = [
    "genres_text",
    "keywords_text",
    "cast_text",
    "director_text",
]


for column in columns:

    print("\n" + "=" * 70)
    print(column.upper())
    print("=" * 70)

    values = (
        df.loc[
            df[column].notna()
            & (df[column].astype(str).str.strip() != ""),
            column
        ]
        .head(20)
    )

    for value in values:
        print(repr(value))