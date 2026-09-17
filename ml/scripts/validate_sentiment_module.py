import sys
from pathlib import Path

import numpy as np


# ============================================================
# IMPORT PATH
# ============================================================

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


from recommender.sentiment import SentimentRecommender


def main():

    print("=" * 80)
    print("SENTIMENT MODULE VALIDATION")
    print("=" * 80)

    # ========================================================
    # 1. INITIALIZATION
    # ========================================================

    print("\n1. INITIALIZATION")
    print("-" * 80)

    sentiment = SentimentRecommender()

    print(
        f"Sentiment movies : "
        f"{sentiment.num_movies:,}"
    )

    print(
        f"Normalized range : "
        f"{sentiment.minimum_score:.4f} "
        f"to "
        f"{sentiment.maximum_score:.4f}"
    )

    print(
        f"Neutral fallback : "
        f"{sentiment.neutral_score:.4f}"
    )

    assert sentiment.num_movies == 3_769

    assert 0.0 <= sentiment.minimum_score <= 1.0
    assert 0.0 <= sentiment.maximum_score <= 1.0

    print(
        "PASS  - Sentiment module initialized"
    )

    # ========================================================
    # 2. NORMALIZATION TEST
    # ========================================================

    print("\n2. NORMALIZATION")
    print("-" * 80)

    test_cases = [
        (-1.0, 0.0),
        (-0.5, 0.25),
        (0.0, 0.5),
        (0.5, 0.75),
        (1.0, 1.0),
    ]

    for adjusted, expected in test_cases:

        result = (
            sentiment.normalize_adjusted_score(
                adjusted
            )
        )

        print(
            f"{adjusted:>5.2f} "
            f"-> "
            f"{result:.4f}"
        )

        assert np.isclose(
            result,
            expected,
        )

    print(
        "PASS  - Sentiment normalization correct"
    )

    # ========================================================
    # 3. KNOWN MOVIE
    # ========================================================

    print("\n3. KNOWN SENTIMENT MOVIE")
    print("-" * 80)

    test_movie_id = 1

    assert sentiment.has_sentiment(
        test_movie_id
    )

    details = (
        sentiment.get_movie_sentiment(
            test_movie_id
        )
    )

    for key, value in details.items():
        print(
            f"{key:<30}: {value}"
        )

    expected = (
        details[
            "adjustedSentimentScore"
        ]
        + 1.0
    ) / 2.0

    assert np.isclose(
        details["sentiment_score"],
        expected,
    )

    print(
        "PASS  - Known movie sentiment lookup correct"
    )

    # ========================================================
    # 4. FALLBACK TEST
    # ========================================================

    print("\n4. NEUTRAL FALLBACK")
    print("-" * 80)

    unknown_movie_id = 999999999

    assert not sentiment.has_sentiment(
        unknown_movie_id
    )

    fallback_score = (
        sentiment.get_score(
            unknown_movie_id
        )
    )

    no_fallback = (
        sentiment.get_score(
            unknown_movie_id,
            fallback=False,
        )
    )

    print(
        f"Unknown movie       : "
        f"{unknown_movie_id}"
    )

    print(
        f"Fallback score      : "
        f"{fallback_score}"
    )

    print(
        f"Without fallback    : "
        f"{no_fallback}"
    )

    assert np.isclose(
        fallback_score,
        0.5,
    )

    assert no_fallback is None

    print(
        "PASS  - Neutral fallback works"
    )

    # ========================================================
    # 5. FULL DATASET RANGE
    # ========================================================

    print("\n5. FULL SENTIMENT RANGE")
    print("-" * 80)

    expected_min = (
        -0.532931 + 1.0
    ) / 2.0

    expected_max = (
        0.809527 + 1.0
    ) / 2.0

    print(
        f"Expected approx min : "
        f"{expected_min:.4f}"
    )

    print(
        f"Actual min          : "
        f"{sentiment.minimum_score:.4f}"
    )

    print(
        f"Expected approx max : "
        f"{expected_max:.4f}"
    )

    print(
        f"Actual max          : "
        f"{sentiment.maximum_score:.4f}"
    )

    assert np.isclose(
        sentiment.minimum_score,
        expected_min,
        atol=1e-4,
    )

    assert np.isclose(
        sentiment.maximum_score,
        expected_max,
        atol=1e-4,
    )

    print(
        "PASS  - Full normalized range matches "
        "Phase 3 sentiment behavior"
    )

    # ========================================================
    # 6. BATCH SCORING
    # ========================================================

    print("\n6. BATCH SCORING")
    print("-" * 80)

    test_movie_ids = [
        1,
        2,
        6,
        unknown_movie_id,
    ]

    batch = sentiment.score_movies(
        test_movie_ids
    )

    print(
        batch.to_string(
            index=False
        )
    )

    assert len(batch) == 4

    assert (
        batch[
            "sentiment_score"
        ]
        .between(
            0.0,
            1.0,
        )
        .all()
    )

    unknown_row = batch[
        batch["movieId"]
        == unknown_movie_id
    ].iloc[0]

    assert not bool(
        unknown_row[
            "has_sentiment"
        ]
    )

    assert np.isclose(
        unknown_row[
            "sentiment_score"
        ],
        0.5,
    )

    print(
        "\nPASS  - Batch sentiment scoring works"
    )

    # ========================================================
    # FINAL
    # ========================================================

    print()

    print("=" * 80)
    print("SENTIMENT MODULE VALID")
    print("=" * 80)


if __name__ == "__main__":
    main()