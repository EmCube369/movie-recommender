import json
import sys
from pathlib import Path


# ============================================================
# IMPORT PATH
# ============================================================

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


from recommender.hybrid import HybridRecommender
from recommender.result import (
    RecommendationResult,
    RecommendationResponse,
)


def main():

    print("=" * 90)
    print("RECOMMENDATION RESULT FORMAT VALIDATION")
    print("=" * 90)

    # ========================================================
    # 1. INITIALIZE
    # ========================================================

    print("\n1. INITIALIZATION")
    print("-" * 90)

    hybrid = HybridRecommender()

    print(
        "PASS  - Hybrid recommender initialized"
    )

    # ========================================================
    # 2. TYPED RESULTS
    # ========================================================

    print("\n2. TYPED RECOMMENDATIONS")
    print("-" * 90)

    results = (
        hybrid.recommend_results(
            user_id=1,
            top_n=10,
        )
    )

    assert len(results) == 10

    assert all(
        isinstance(
            result,
            RecommendationResult,
        )
        for result in results
    )

    for expected_rank, result in enumerate(
        results,
        start=1,
    ):

        assert (
            result.rank
            == expected_rank
        )

    print(
        f"Results : {len(results)}"
    )

    print(
        "PASS  - RecommendationResult objects generated"
    )

    print(
        "PASS  - Ranking is sequential"
    )

    # ========================================================
    # 3. RESPONSE OBJECT
    # ========================================================

    print("\n3. RESPONSE OBJECT")
    print("-" * 90)

    response = (
        hybrid.recommend_response(
            user_id=1,
            top_n=10,
        )
    )

    assert isinstance(
        response,
        RecommendationResponse,
    )

    assert response.user_id == 1
    assert response.count == 10
    assert response.schema_version == "1.0"

    print(
        f"Schema version : "
        f"{response.schema_version}"
    )

    print(
        f"User ID        : "
        f"{response.user_id}"
    )

    print(
        f"Count          : "
        f"{response.count}"
    )

    print(
        "PASS  - RecommendationResponse valid"
    )

    # ========================================================
    # 4. JSON PAYLOAD
    # ========================================================

    print("\n4. JSON PAYLOAD")
    print("-" * 90)

    payload = (
        hybrid.recommend_payload(
            user_id=1,
            top_n=10,
        )
    )

    expected_top_keys = {
        "schemaVersion",
        "userId",
        "count",
        "recommendations",
    }

    assert (
        set(payload.keys())
        == expected_top_keys
    )

    assert payload["userId"] == 1
    assert payload["count"] == 10

    print(
        f"Top-level keys: "
        f"{list(payload.keys())}"
    )

    print(
        "PASS  - Top-level response schema correct"
    )

    # ========================================================
    # 5. ITEM SCHEMA
    # ========================================================

    print("\n5. RECOMMENDATION ITEM SCHEMA")
    print("-" * 90)

    required_item_keys = {
        "rank",
        "movieId",
        "title",
        "releaseYear",
        "genres",
        "score",
        "cfScore",
        "contentScore",
        "sentimentScore",
        "sentimentAvailable",
    }

    for recommendation in payload[
        "recommendations"
    ]:

        assert (
            set(
                recommendation.keys()
            )
            == required_item_keys
        )

        assert isinstance(
            recommendation["rank"],
            int,
        )

        assert isinstance(
            recommendation["movieId"],
            int,
        )

        assert isinstance(
            recommendation["title"],
            str,
        )

        assert (
            recommendation[
                "releaseYear"
            ]
            is None
            or isinstance(
                recommendation[
                    "releaseYear"
                ],
                int,
            )
        )

        assert isinstance(
            recommendation["genres"],
            list,
        )

        assert isinstance(
            recommendation["score"],
            float,
        )

        assert isinstance(
            recommendation["cfScore"],
            float,
        )

        assert isinstance(
            recommendation[
                "contentScore"
            ],
            float,
        )

        assert isinstance(
            recommendation[
                "sentimentScore"
            ],
            float,
        )

        assert isinstance(
            recommendation[
                "sentimentAvailable"
            ],
            bool,
        )

    print(
        "PASS  - Every recommendation follows "
        "the stable schema"
    )

    # ========================================================
    # 6. SCORE RANGE
    # ========================================================

    print("\n6. SCORE VALIDATION")
    print("-" * 90)

    for recommendation in payload[
        "recommendations"
    ]:

        for key in [
            "score",
            "cfScore",
            "contentScore",
            "sentimentScore",
        ]:

            score = recommendation[
                key
            ]

            assert (
                0.0
                <= score
                <= 1.0
            )

    print(
        "PASS  - All public scores are normalized to 0–1"
    )

    # ========================================================
    # 7. JSON SERIALIZATION
    # ========================================================

    print("\n7. JSON SERIALIZATION")
    print("-" * 90)

    # allow_nan=False is intentional.
    #
    # If NumPy NaN accidentally leaks into the API result,
    # this test will fail.
    json_text = json.dumps(
        payload,
        indent=2,
        allow_nan=False,
    )

    restored = json.loads(
        json_text
    )

    assert restored[
        "userId"
    ] == 1

    assert restored[
        "count"
    ] == 10

    print(
        "PASS  - Payload serializes as strict JSON"
    )

    # ========================================================
    # 8. SAMPLE
    # ========================================================

    print("\n8. PHASE 4 RESPONSE SAMPLE")
    print("-" * 90)

    sample = {
        "schemaVersion": (
            payload[
                "schemaVersion"
            ]
        ),

        "userId": (
            payload[
                "userId"
            ]
        ),

        "count": (
            payload[
                "count"
            ]
        ),

        "recommendations": (
            payload[
                "recommendations"
            ][:3]
        ),
    }

    print(
        json.dumps(
            sample,
            indent=2,
            allow_nan=False,
        )
    )

    # ========================================================
    # FINAL
    # ========================================================

    print()

    print("=" * 90)
    print("RECOMMENDATION RESULT FORMAT VALID")
    print("=" * 90)


if __name__ == "__main__":
    main()