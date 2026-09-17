import sys
from pathlib import Path

import numpy as np


ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


from recommender.hybrid import HybridRecommender


def main():

    print("=" * 90)
    print("HYBRID MODULE VALIDATION")
    print("=" * 90)

    # ========================================================
    # 1. INITIALIZATION
    # ========================================================

    print("\n1. INITIALIZATION")
    print("-" * 90)

    hybrid = HybridRecommender()

    print(
        f"Device           : "
        f"{hybrid.cf.device}"
    )

    print(
        f"CF weight        : "
        f"{hybrid.cf_weight:.2f}"
    )

    print(
        f"Content weight   : "
        f"{hybrid.content_weight:.2f}"
    )

    print(
        f"Sentiment weight : "
        f"{hybrid.sentiment_weight:.2f}"
    )

    total_weight = (
        hybrid.cf_weight
        + hybrid.content_weight
        + hybrid.sentiment_weight
    )

    assert np.isclose(
        total_weight,
        1.0,
    )

    print(
        "PASS  - Hybrid module initialized"
    )

    # ========================================================
    # 2. NORMALIZATION
    # ========================================================

    print("\n2. NORMALIZATION")
    print("-" * 90)

    cf_test = hybrid.normalize_cf(
        np.array(
            [
                0.5,
                1.0,
                5.0,
            ]
        )
    )

    print(
        f"CF 0.5 -> "
        f"{cf_test[0]:.4f}"
    )

    print(
        f"CF 1.0 -> "
        f"{cf_test[1]:.4f}"
    )

    print(
        f"CF 5.0 -> "
        f"{cf_test[2]:.4f}"
    )

    assert np.isclose(
        cf_test[0],
        0.0,
    )

    assert np.isclose(
        cf_test[1],
        1.0 / 9.0,
        atol=1e-6,
    )

    assert np.isclose(
        cf_test[2],
        1.0,
    )

    content_test = (
        hybrid.normalize_content(
            np.array(
                [
                    0.0,
                    0.28,
                ]
            )
        )
    )

    print(
        f"Content 0.00 -> "
        f"{content_test[0]:.4f}"
    )

    print(
        f"Content 0.28 -> "
        f"{content_test[1]:.4f}"
    )

    assert np.isclose(
        content_test[0],
        0.0,
    )

    assert np.isclose(
        content_test[1],
        1.0,
    )

    print(
        "PASS  - Hybrid normalization correct"
    )

    # ========================================================
    # 3. USER HISTORY
    # ========================================================

    print("\n3. USER HISTORY")
    print("-" * 90)

    user_id = 1

    summary = hybrid.user_summary(
        user_id
    )

    for key, value in summary.items():
        print(
            f"{key:<25}: {value}"
        )

    assert (
        summary[
            "interactionCount"
        ]
        == 141
    )

    assert (
        summary[
            "positiveCount"
        ]
        == 83
    )

    print(
        "PASS  - User history available"
    )

    # ========================================================
    # 4. FULL HYBRID SCORING
    # ========================================================

    print("\n4. FULL HYBRID SCORING")
    print("-" * 90)

    scores = hybrid.score_user(
        user_id
    )

    print(
        f"Candidates         : "
        f"{len(scores):,}"
    )

    print(
        f"CF norm range      : "
        f"{scores['cf_norm'].min():.4f} "
        f"to "
        f"{scores['cf_norm'].max():.4f}"
    )

    print(
        f"Content norm range : "
        f"{scores['content_norm'].min():.4f} "
        f"to "
        f"{scores['content_norm'].max():.4f}"
    )

    print(
        f"Sentiment range    : "
        f"{scores['sentiment_norm'].min():.4f} "
        f"to "
        f"{scores['sentiment_norm'].max():.4f}"
    )

    print(
        f"Hybrid range       : "
        f"{scores['hybrid_score'].min():.4f} "
        f"to "
        f"{scores['hybrid_score'].max():.4f}"
    )

    assert len(scores) == 43_458

    assert (
        scores[
            "movieId"
        ].is_unique
    )

    assert (
        scores[
            "hybrid_score"
        ]
        .between(
            0.0,
            1.0,
        )
        .all()
    )

    print(
        "PASS  - Expected 43,458 candidates"
    )

    print(
        "PASS  - Candidate movieIds unique"
    )

    print(
        "PASS  - Hybrid scores within 0–1"
    )

    # ========================================================
    # 5. WATCHED-MOVIE EXCLUSION
    # ========================================================

    print("\n5. WATCHED-MOVIE EXCLUSION")
    print("-" * 90)

    rated = set(
        hybrid.history
        .get_rated_movie_ids(
            user_id
        )
        .tolist()
    )

    candidates = set(
        scores[
            "movieId"
        ].tolist()
    )

    overlap = (
        rated
        & candidates
    )

    assert not overlap

    print(
        f"Rated movies      : "
        f"{len(rated)}"
    )

    print(
        f"Candidate overlap : "
        f"{len(overlap)}"
    )

    print(
        "PASS  - Previously rated movies excluded"
    )

    # ========================================================
    # 6. TOP-10
    # ========================================================

    print("\n6. TOP HYBRID RECOMMENDATIONS")
    print("-" * 90)

    recommendations = (
        hybrid.recommend(
            user_id=user_id,
            top_n=10,
        )
    )

    display_columns = [
        column
        for column in [
            "movieId",
            "title",
            "cf_norm",
            "content_norm",
            "sentiment_norm",
            "has_sentiment",
            "hybrid_score",
        ]
        if column
        in recommendations.columns
    ]

    print(
        recommendations[
            display_columns
        ].to_string(
            index=False
        )
    )

    assert len(
        recommendations
    ) == 10

    assert (
        recommendations[
            "hybrid_score"
        ]
        .is_monotonic_decreasing
    )

    assert not (
        set(
            recommendations[
                "movieId"
            ]
        )
        & rated
    )

    print(
        "\nPASS  - Top-10 sorted descending"
    )

    print(
        "PASS  - Top-10 contains no rated movies"
    )

    # ========================================================
    # 7. SCORE FORMULA
    # ========================================================

    print("\n7. HYBRID SCORE FORMULA")
    print("-" * 90)

    first = (
        recommendations.iloc[0]
    )

    expected = (
        hybrid.cf_weight
        * first["cf_norm"]
        +
        hybrid.content_weight
        * first["content_norm"]
        +
        hybrid.sentiment_weight
        * first["sentiment_norm"]
    )

    print(
        f"Stored score      : "
        f"{first['hybrid_score']:.6f}"
    )

    print(
        f"Calculated score  : "
        f"{expected:.6f}"
    )

    assert np.isclose(
        first[
            "hybrid_score"
        ],
        expected,
        atol=1e-6,
    )

    print(
        "PASS  - Hybrid score formula correct"
    )

    # ========================================================
    # FINAL
    # ========================================================

    print()

    print("=" * 90)
    print("HYBRID MODULE VALID")
    print("=" * 90)


if __name__ == "__main__":
    main()