import numpy as np
import pandas as pd

from hybrid_recommender import HybridRecommender


# ============================================================
# SETTINGS
# ============================================================

TEST_USERS_PER_GROUP = 2
TOP_N = 10


# ============================================================
# INITIALIZE ONCE
# ============================================================

recommender = HybridRecommender(
    cf_weight=0.50,
    content_weight=0.35,
    sentiment_weight=0.15,
)

history = recommender.ranker.history


# ============================================================
# GET USER HISTORY COUNTS
# ============================================================

counts = np.diff(
    np.asarray(
        history.indptr,
        dtype=np.int64,
    )
)

user_mapping = (
    recommender
    .ranker
    .cf
    .user_mapping[
        [
            recommender.ranker.cf.user_id_col,
            recommender.ranker.cf.user_index_col,
        ]
    ]
    .copy()
)

user_mapping.columns = [
    "userId",
    "userIndex",
]

user_mapping["historyCount"] = (
    counts[
        user_mapping["userIndex"].to_numpy(
            dtype=np.int64
        )
    ]
)


# ============================================================
# USER GROUPS
# ============================================================

groups = {
    "LOW HISTORY": (
        user_mapping[
            user_mapping["historyCount"].between(
                15,
                25,
            )
        ]
    ),

    "MEDIUM HISTORY": (
        user_mapping[
            user_mapping["historyCount"].between(
                75,
                150,
            )
        ]
    ),

    "HIGH HISTORY": (
        user_mapping[
            user_mapping["historyCount"].between(
                500,
                1000,
            )
        ]
    ),

    "VERY HIGH HISTORY": (
        user_mapping[
            user_mapping["historyCount"] >= 2000
        ]
    ),
}


# ============================================================
# TEST USERS
# ============================================================

for group_name, group in groups.items():

    print("\n" + "=" * 100)
    print(group_name)
    print("=" * 100)

    if group.empty:
        print("No users found.")
        continue

    # Deterministic selection so reruns use same users.
    sample = (
        group
        .sort_values(
            [
                "historyCount",
                "userId",
            ]
        )
        .head(
            TEST_USERS_PER_GROUP
        )
    )

    for _, user_row in sample.iterrows():

        user_id = int(
            user_row["userId"]
        )

        history_count = int(
            user_row["historyCount"]
        )

        positive_count = len(
            history.get_positive_ratings(
                user_id=user_id,
                minimum_rating=4.0,
            )
        )

        print("\n" + "-" * 100)

        print(
            f"USER {user_id}"
            f" | history={history_count}"
            f" | positive>=4.0={positive_count}"
        )

        print("-" * 100)

        # ----------------------------------------------------
        # Users without positive ratings cannot currently
        # construct a positive content profile.
        # ----------------------------------------------------

        if positive_count == 0:

            print(
                "SKIPPED: no ratings >= 4.0 "
                "for content profile."
            )

            continue

        try:

            recommendations = (
                recommender.recommend_hybrid(
                    user_id=user_id,
                    top_n=TOP_N,
                    minimum_rating=4.0,
                    include_debug=True,
                )
            )

        except Exception as exc:

            print(
                "FAILED:",
                repr(exc),
            )

            continue

        result = pd.DataFrame(
            recommendations
        )

        display_columns = [
            "rank",
            "movieId",
            "title",
            "score",
            "cfScore",
            "contentScore",
            "sentimentScore",
            "hasSentiment",
        ]

        print(
            result[
                display_columns
            ].to_string(
                index=False
            )
        )


print("\n" + "=" * 100)
print("MULTI-USER HYBRID VALIDATION COMPLETE")
print("=" * 100)