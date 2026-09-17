import pandas as pd

df = pd.read_csv(
    "data/cleaned/movies_clean_final.csv"
)

movie = df[
    df["title"].str.contains(
        "Batman: The Dark Knight Returns",
        case=False,
        na=False
    )
]

print(
    movie[
        [
            "movieId",
            "title",
            "release_year",
            "vote_average",
            "vote_count",
            "imdb_id",
            "tmdbId"
        ]
    ].to_string(index=False)
)