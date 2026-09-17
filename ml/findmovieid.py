from recommender.artifact_loader import ArtifactLoader

loader = ArtifactLoader()
movies = loader.movies

result = movies[
    movies["title"].str.contains(
        "Dark Knight",
        case=False,
        na=False
    )
][
    ["movieId", "title", "release_year"]
]

print(result.to_string(index=False))