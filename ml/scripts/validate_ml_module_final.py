import json
import sys
from pathlib import Path

import numpy as np


# ============================================================
# IMPORT PATH
# ============================================================

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


# ============================================================
# ML IMPORTS
# ============================================================

from recommender.config import (
    REQUIRED_ARTIFACTS,
    CF_WEIGHT,
    CONTENT_WEIGHT,
    SENTIMENT_WEIGHT,
    validate_required_artifacts,
)

from recommender.artifact_loader import ArtifactLoader
from recommender.hybrid import HybridRecommender


# ============================================================
# CONSTANTS
# ============================================================

PRIMARY_TEST_USER = 1

ADDITIONAL_TEST_USERS = [
    2,
    6,
]

TOP_N = 10

EXPECTED_USER_1_INTERACTIONS = 141
EXPECTED_USER_1_POSITIVES = 83
EXPECTED_USER_1_CANDIDATES = 43_458

# Current validated regression result.
EXPECTED_USER_1_TOP_MOVIE_ID = 922


EXPECTED_RESPONSE_KEYS = {
    "schemaVersion",
    "userId",
    "count",
    "recommendations",
}


EXPECTED_RECOMMENDATION_KEYS = {
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


# ============================================================
# HELPERS
# ============================================================


def section(
    number: int,
    title: str,
) -> None:

    print()
    print(
        f"{number}. {title}"
    )

    print("-" * 100)


def assert_score_range(
    values,
    name: str,
) -> None:

    values = np.asarray(
        values,
        dtype=np.float64,
    )

    assert np.isfinite(
        values
    ).all(), (
        f"{name} contains NaN or infinite values."
    )

    assert (
        values >= 0.0
    ).all(), (
        f"{name} contains values below 0."
    )

    assert (
        values <= 1.0
    ).all(), (
        f"{name} contains values above 1."
    )


# ============================================================
# MAIN
# ============================================================


def main():

    print("=" * 100)
    print("PHASE 3.10 FINAL ML MODULE VALIDATION")
    print("=" * 100)

    # ========================================================
    # 1. REQUIRED ARTIFACTS
    # ========================================================

    section(
        1,
        "REQUIRED ARTIFACTS",
    )

    for name, path in REQUIRED_ARTIFACTS.items():

        status = (
            "PASS"
            if path.exists()
            else "FAIL"
        )

        print(
            f"{status:<5} - "
            f"{name:<30} "
            f"{path}"
        )

    validate_required_artifacts()

    print()
    print(
        "PASS  - All required runtime artifacts exist"
    )

    # ========================================================
    # 2. ARTIFACT LOADER
    # ========================================================

    section(
        2,
        "ARTIFACT LOADER",
    )

    loader = ArtifactLoader()

    movies = loader.movies
    cf_users = loader.cf_user_mapping
    cf_movies = loader.cf_movie_mapping
    cf_seen = loader.cf_seen_movie_indexes
    content_index = loader.content_movie_id_to_index
    sentiment = loader.movie_sentiment

    print(
        f"Movie catalog      : "
        f"{len(movies):,}"
    )

    print(
        f"CF users           : "
        f"{len(cf_users):,}"
    )

    print(
        f"CF mapped movies   : "
        f"{len(cf_movies):,}"
    )

    print(
        f"CF trained movies  : "
        f"{len(cf_seen):,}"
    )

    print(
        f"Content movies     : "
        f"{len(content_index):,}"
    )

    print(
        f"Sentiment movies   : "
        f"{len(sentiment):,}"
    )

    assert len(
        movies
    ) == 87_550

    assert len(
        cf_users
    ) == 200_948

    assert len(
        cf_movies
    ) == 43_864

    assert len(
        cf_seen
    ) == 43_599

    assert len(
        content_index
    ) == 87_550

    assert len(
        sentiment
    ) == 3_769

    assert movies[
        "movieId"
    ].is_unique

    assert cf_users[
        "userId"
    ].is_unique

    assert cf_users[
        "userIndex"
    ].is_unique

    assert cf_movies[
        "movieId"
    ].is_unique

    assert cf_movies[
        "movieIndex"
    ].is_unique

    print(
        "PASS  - Runtime artifact counts correct"
    )

    print(
        "PASS  - Runtime mappings unique"
    )

    # ========================================================
    # 3. HYBRID INITIALIZATION
    # ========================================================

    section(
        3,
        "HYBRID INITIALIZATION",
    )

    hybrid = HybridRecommender()

    print(
        f"Device             : "
        f"{hybrid.cf.device}"
    )

    print(
        f"Users              : "
        f"{hybrid.cf.num_users:,}"
    )

    print(
        f"CF movies          : "
        f"{hybrid.cf.num_movies:,}"
    )

    print(
        f"Embedding dim      : "
        f"{hybrid.cf.embedding_dim}"
    )

    print(
        f"CF weight          : "
        f"{hybrid.cf_weight:.2f}"
    )

    print(
        f"Content weight     : "
        f"{hybrid.content_weight:.2f}"
    )

    print(
        f"Sentiment weight   : "
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

    assert np.isclose(
        hybrid.cf_weight,
        CF_WEIGHT,
    )

    assert np.isclose(
        hybrid.content_weight,
        CONTENT_WEIGHT,
    )

    assert np.isclose(
        hybrid.sentiment_weight,
        SENTIMENT_WEIGHT,
    )

    print(
        "PASS  - Hybrid recommender initialized"
    )

    print(
        "PASS  - Hybrid weights valid"
    )

    # ========================================================
    # 4. COMPONENT VALIDATION
    # ========================================================

    section(
        4,
        "COMPONENT VALIDATION",
    )

    print(
        f"Collaborative users      : "
        f"{hybrid.cf.num_users:,}"
    )

    print(
        f"Collaborative movies     : "
        f"{hybrid.cf.num_movies:,}"
    )

    print(
        f"Content movies           : "
        f"{hybrid.content.num_movies:,}"
    )

    print(
        f"Sentiment movies         : "
        f"{hybrid.sentiment.num_movies:,}"
    )

    print(
        f"History users            : "
        f"{len(hybrid.history.indptr) - 1:,}"
    )

    print(
        f"History interactions     : "
        f"{len(hybrid.history.movie_indexes):,}"
    )

    assert (
        hybrid.cf.num_users
        == 200_948
    )

    assert (
        hybrid.cf.num_movies
        == 43_864
    )

    assert (
        hybrid.content.num_movies
        == 87_550
    )

    assert (
        hybrid.sentiment.num_movies
        == 3_769
    )

    assert (
        len(
            hybrid.history.indptr
        )
        - 1
        == 200_948
    )

    assert (
        len(
            hybrid.history.movie_indexes
        )
        == 31_920_673
    )

    print(
        "PASS  - All runtime components consistent"
    )

    # ========================================================
    # 5. PRIMARY USER HISTORY
    # ========================================================

    section(
        5,
        "PRIMARY USER HISTORY",
    )

    user_id = PRIMARY_TEST_USER

    assert hybrid.has_user(
        user_id
    )

    summary = (
        hybrid.user_summary(
            user_id
        )
    )

    for key, value in summary.items():

        print(
            f"{key:<28}: "
            f"{value}"
        )

    assert (
        summary[
            "interactionCount"
        ]
        == EXPECTED_USER_1_INTERACTIONS
    )

    assert (
        summary[
            "positiveCount"
        ]
        == EXPECTED_USER_1_POSITIVES
    )

    print(
        "PASS  - Primary user history correct"
    )

    # ========================================================
    # 6. FULL HYBRID SCORING
    # ========================================================

    section(
        6,
        "FULL HYBRID SCORING",
    )

    scores = (
        hybrid.score_user(
            user_id
        )
    )

    print(
        f"Candidates         : "
        f"{len(scores):,}"
    )

    print(
        f"CF norm            : "
        f"{scores['cf_norm'].min():.4f} "
        f"to "
        f"{scores['cf_norm'].max():.4f}"
    )

    print(
        f"Content norm       : "
        f"{scores['content_norm'].min():.4f} "
        f"to "
        f"{scores['content_norm'].max():.4f}"
    )

    print(
        f"Sentiment norm     : "
        f"{scores['sentiment_norm'].min():.4f} "
        f"to "
        f"{scores['sentiment_norm'].max():.4f}"
    )

    print(
        f"Hybrid score       : "
        f"{scores['hybrid_score'].min():.4f} "
        f"to "
        f"{scores['hybrid_score'].max():.4f}"
    )

    assert (
        len(scores)
        == EXPECTED_USER_1_CANDIDATES
    )

    assert scores[
        "movieId"
    ].is_unique

    assert_score_range(
        scores["cf_norm"],
        "CF normalized scores",
    )

    assert_score_range(
        scores["content_norm"],
        "Content normalized scores",
    )

    assert_score_range(
        scores["sentiment_norm"],
        "Sentiment normalized scores",
    )

    assert_score_range(
        scores["hybrid_score"],
        "Hybrid scores",
    )

    print(
        "PASS  - Expected candidate count"
    )

    print(
        "PASS  - Candidate IDs unique"
    )

    print(
        "PASS  - All normalized scores valid"
    )

    # ========================================================
    # 7. WATCHED MOVIE EXCLUSION
    # ========================================================

    section(
        7,
        "WATCHED MOVIE EXCLUSION",
    )

    rated_movie_ids = set(
        hybrid.history
        .get_rated_movie_ids(
            user_id
        )
        .tolist()
    )

    candidate_movie_ids = set(
        scores[
            "movieId"
        ].tolist()
    )

    overlap = (
        rated_movie_ids
        & candidate_movie_ids
    )

    print(
        f"Rated movies       : "
        f"{len(rated_movie_ids)}"
    )

    print(
        f"Candidates         : "
        f"{len(candidate_movie_ids):,}"
    )

    print(
        f"Overlap            : "
        f"{len(overlap)}"
    )

    assert not overlap

    print(
        "PASS  - Previously rated movies excluded"
    )

    # ========================================================
    # 8. SCORE FORMULA
    # ========================================================

    section(
        8,
        "HYBRID SCORE FORMULA",
    )

    sample_rows = (
        scores
        .sample(
            n=min(
                100,
                len(scores),
            ),
            random_state=42,
        )
    )

    recalculated = (
        hybrid.cf_weight
        * sample_rows[
            "cf_norm"
        ]
        +
        hybrid.content_weight
        * sample_rows[
            "content_norm"
        ]
        +
        hybrid.sentiment_weight
        * sample_rows[
            "sentiment_norm"
        ]
    )

    assert np.allclose(
        sample_rows[
            "hybrid_score"
        ].to_numpy(),
        recalculated.to_numpy(),
        atol=1e-6,
    )

    print(
        "PASS  - Hybrid formula verified on "
        f"{len(sample_rows)} candidates"
    )

    # ========================================================
    # 9. PUBLIC PHASE 4 PAYLOAD
    # ========================================================

    section(
        9,
        "PUBLIC PHASE 4 PAYLOAD",
    )

    payload = (
        hybrid.recommend_payload(
            user_id=user_id,
            top_n=TOP_N,
        )
    )

    assert (
        set(
            payload.keys()
        )
        == EXPECTED_RESPONSE_KEYS
    )

    assert (
        payload[
            "schemaVersion"
        ]
        == "1.0"
    )

    assert (
        payload[
            "userId"
        ]
        == user_id
    )

    assert (
        payload[
            "count"
        ]
        == TOP_N
    )

    recommendations = (
        payload[
            "recommendations"
        ]
    )

    assert (
        len(
            recommendations
        )
        == TOP_N
    )

    print(
        f"Schema version     : "
        f"{payload['schemaVersion']}"
    )

    print(
        f"User ID            : "
        f"{payload['userId']}"
    )

    print(
        f"Recommendation count: "
        f"{payload['count']}"
    )

    print(
        "PASS  - Public response envelope valid"
    )

    # ========================================================
    # 10. RECOMMENDATION ITEM CONTRACT
    # ========================================================

    section(
        10,
        "RECOMMENDATION ITEM CONTRACT",
    )

    result_movie_ids = []

    previous_score = None

    for expected_rank, item in enumerate(
        recommendations,
        start=1,
    ):

        assert (
            set(
                item.keys()
            )
            == EXPECTED_RECOMMENDATION_KEYS
        )

        assert isinstance(
            item[
                "rank"
            ],
            int,
        )

        assert (
            item[
                "rank"
            ]
            == expected_rank
        )

        assert isinstance(
            item[
                "movieId"
            ],
            int,
        )

        assert isinstance(
            item[
                "title"
            ],
            str,
        )

        assert (
            item[
                "releaseYear"
            ]
            is None
            or isinstance(
                item[
                    "releaseYear"
                ],
                int,
            )
        )

        assert isinstance(
            item[
                "genres"
            ],
            list,
        )

        assert isinstance(
            item[
                "sentimentAvailable"
            ],
            bool,
        )

        for score_name in [
            "score",
            "cfScore",
            "contentScore",
            "sentimentScore",
        ]:

            value = item[
                score_name
            ]

            assert isinstance(
                value,
                float,
            )

            assert np.isfinite(
                value
            )

            assert (
                0.0
                <= value
                <= 1.0
            )

        if previous_score is not None:

            assert (
                item[
                    "score"
                ]
                <= previous_score
            )

        previous_score = (
            item[
                "score"
            ]
        )

        result_movie_ids.append(
            item[
                "movieId"
            ]
        )

    assert (
        len(
            result_movie_ids
        )
        == len(
            set(
                result_movie_ids
            )
        )
    )

    assert not (
        set(
            result_movie_ids
        )
        & rated_movie_ids
    )

    print(
        "PASS  - Item schema valid"
    )

    print(
        "PASS  - Ranks sequential"
    )

    print(
        "PASS  - Scores descending"
    )

    print(
        "PASS  - Recommendation IDs unique"
    )

    print(
        "PASS  - No rated movie leaked into results"
    )

    # ========================================================
    # 11. REGRESSION CHECK
    # ========================================================

    section(
        11,
        "PRIMARY USER REGRESSION CHECK",
    )

    top = recommendations[
        0
    ]

    print(
        f"Top movieId       : "
        f"{top['movieId']}"
    )

    print(
        f"Top title         : "
        f"{top['title']}"
    )

    print(
        f"Top hybrid score  : "
        f"{top['score']:.6f}"
    )

    assert (
        top[
            "movieId"
        ]
        == EXPECTED_USER_1_TOP_MOVIE_ID
    ), (
        "Primary regression result changed. "
        f"Expected movieId "
        f"{EXPECTED_USER_1_TOP_MOVIE_ID}, "
        f"got {top['movieId']}."
    )

    print(
        "PASS  - User 1 top recommendation "
        "matches validated baseline"
    )

    # ========================================================
    # 12. STRICT JSON
    # ========================================================

    section(
        12,
        "STRICT JSON SERIALIZATION",
    )

    json_text = json.dumps(
        payload,
        indent=2,
        allow_nan=False,
    )

    restored = json.loads(
        json_text
    )

    assert (
        restored
        == payload
    )

    print(
        f"JSON characters    : "
        f"{len(json_text):,}"
    )

    print(
        "PASS  - Payload is strict JSON"
    )

    print(
        "PASS  - JSON round trip preserves payload"
    )

    # ========================================================
    # 13. DETERMINISM
    # ========================================================

    section(
        13,
        "REPEATED RECOMMENDATION DETERMINISM",
    )

    second_payload = (
        hybrid.recommend_payload(
            user_id=user_id,
            top_n=TOP_N,
        )
    )

    assert (
        payload
        == second_payload
    )

    print(
        "PASS  - Repeated recommendation "
        "payloads are identical"
    )

    # ========================================================
    # 14. ADDITIONAL USERS
    # ========================================================

    section(
        14,
        "MULTI-USER SMOKE TEST",
    )

    for test_user_id in (
        ADDITIONAL_TEST_USERS
    ):

        assert hybrid.has_user(
            test_user_id
        )

        test_summary = (
            hybrid.user_summary(
                test_user_id
            )
        )

        assert (
            test_summary[
                "interactionCount"
            ]
            > 0
        )

        assert (
            test_summary[
                "positiveCount"
            ]
            > 0
        )

        test_payload = (
            hybrid.recommend_payload(
                user_id=test_user_id,
                top_n=3,
            )
        )

        assert (
            test_payload[
                "count"
            ]
            == 3
        )

        test_ids = [
            item[
                "movieId"
            ]
            for item
            in test_payload[
                "recommendations"
            ]
        ]

        rated = set(
            hybrid.history
            .get_rated_movie_ids(
                test_user_id
            )
            .tolist()
        )

        assert not (
            set(
                test_ids
            )
            & rated
        )

        print(
            f"PASS  - userId "
            f"{test_user_id:<8} "
            f"interactions="
            f"{test_summary['interactionCount']:<5} "
            f"positives="
            f"{test_summary['positiveCount']:<5} "
            f"recommendations={len(test_ids)}"
        )

    # ========================================================
    # 15. ERROR HANDLING
    # ========================================================

    section(
        15,
        "ERROR HANDLING",
    )

    unknown_user_id = (
        999_999_999
    )

    assert not hybrid.has_user(
        unknown_user_id
    )

    try:

        hybrid.recommend_payload(
            user_id=unknown_user_id,
            top_n=10,
        )

        raise AssertionError(
            "Unknown user should have "
            "raised KeyError."
        )

    except KeyError:

        print(
            "PASS  - Unknown user raises KeyError"
        )

    try:

        hybrid.recommend_payload(
            user_id=PRIMARY_TEST_USER,
            top_n=0,
        )

        raise AssertionError(
            "top_n=0 should have raised ValueError."
        )

    except ValueError:

        print(
            "PASS  - Invalid top_n raises ValueError"
        )

    # ========================================================
    # 16. FINAL RESPONSE SAMPLE
    # ========================================================

    section(
        16,
        "FINAL PHASE 4 RESPONSE SAMPLE",
    )

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

        "count": 3,

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

    print("=" * 100)
    print("PHASE 3.10 FINAL ML MODULE VALIDATION PASSED")
    print("=" * 100)

    print()
    print(
        "The ML runtime module is ready for "
        "final packaging and Phase 4 integration."
    )


if __name__ == "__main__":
    main()