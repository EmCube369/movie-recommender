import sys
from pathlib import Path

import numpy as np


ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


from recommender.content_based import (
    ContentBasedRecommender,
)


def main():

    print("=" * 80)
    print("CONTENT-BASED MODULE VALIDATION")
    print("=" * 80)

    # ========================================================
    # 1. INITIALIZATION
    # ========================================================

    print("\n1. INITIALIZATION")
    print("-" * 80)

    content = ContentBasedRecommender()

    print(
        f"Content movies : "
        f"{content.num_movies:,}"
    )

    print(
        f"Weights        : "
        f"{content.weights}"
    )

    print(
        f"Weight total   : "
        f"{sum(content.weights.values()):.4f}"
    )

    assert content.num_movies == 87_550

    assert np.isclose(
        sum(content.weights.values()),
        1.0,
    )

    print(
        "PASS  - Content module initialized"
    )

    # ========================================================
    # 2. MATRIX CHECKS
    # ========================================================

    print("\n2. CONTENT MATRICES")
    print("-" * 80)

    for name, matrix in content.matrices.items():

        print(
            f"{name:<10} "
            f"shape={matrix.shape} "
            f"nnz={matrix.nnz:,}"
        )

        assert (
            matrix.shape[0]
            == content.num_movies
        )

    print(
        "PASS  - All matrix row counts match"
    )

    # ========================================================
    # 3. MOVIE LOOKUP
    # ========================================================

    print("\n3. MOVIE LOOKUP")
    print("-" * 80)

    test_movie_id = 1

    assert content.has_movie(
        test_movie_id
    )

    index = content.get_movie_index(
        test_movie_id
    )

    print(
        f"PASS  - movieId {test_movie_id} "
        f"-> contentIndex {index}"
    )

    # ========================================================
    # 4. MOVIE SIMILARITY
    # ========================================================

    print("\n4. MOVIE-TO-MOVIE SIMILARITY")
    print("-" * 80)

    recommendations = (
        content.similar_movies(
            movie_id=test_movie_id,
            top_n=10,
        )
    )

    print(
        recommendations[
            [
                column
                for column in [
                    "movieId",
                    "title",
                    "content_score",
                    "genre_score",
                    "keyword_score",
                    "director_score",
                    "cast_score",
                    "overview_score",
                    "tagline_score",
                ]
                if column
                in recommendations.columns
            ]
        ].to_string(
            index=False
        )
    )

    assert len(recommendations) == 10

    assert (
        recommendations[
            "movieId"
        ]
        != test_movie_id
    ).all()

    assert (
        recommendations[
            "content_score"
        ].is_monotonic_decreasing
    )

    print(
        "\nPASS  - Query movie excluded"
    )

    print(
        "PASS  - Similarity ranking descending"
    )

    # ========================================================
    # 5. PROFILE TEST
    # ========================================================

    print("\n5. PROFILE SCORING")
    print("-" * 80)

    # Small reproducible example profile
    profile_movies = [
        1,
        260,
        1196,
        1210,
        2571,
    ]

    profile_movies = [
        movie_id
        for movie_id
        in profile_movies
        if content.has_movie(movie_id)
    ]

    print(
        f"Profile movieIds: "
        f"{profile_movies}"
    )

    profile_recommendations = (
        content.recommend_from_profile(
            positive_movie_ids=profile_movies,
            top_n=10,
        )
    )

    print()

    print(
        profile_recommendations[
            [
                "movieId",
                "title",
                "content_score",
            ]
        ].to_string(
            index=False
        )
    )

    overlap = (
        set(profile_movies)
        & set(
            profile_recommendations[
                "movieId"
            ]
        )
    )

    assert not overlap

    assert (
        profile_recommendations[
            "content_score"
        ].is_monotonic_decreasing
    )

    print(
        "\nPASS  - Profile source movies excluded"
    )

    print(
        "PASS  - Personalized content ranking descending"
    )

    # ========================================================
    # FINAL
    # ========================================================

    print()

    print("=" * 80)
    print("CONTENT-BASED MODULE VALID")
    print("=" * 80)


if __name__ == "__main__":
    main()