import json

from hybrid_ranker import HybridRanker


# ============================================================
# HYBRID RECOMMENDER
# ============================================================

class HybridRecommender:

    def __init__(
        self,
        cf_weight=0.50,
        content_weight=0.35,
        sentiment_weight=0.15,
    ):

        print("=" * 70)
        print("INITIALIZING HYBRID RECOMMENDER")
        print("=" * 70)

        # Load everything ONCE.
        #
        # In Phase 4, the Python recommendation service should
        # create one HybridRecommender instance when the service
        # starts, not once per HTTP request.
        self.ranker = HybridRanker(
            cf_weight=cf_weight,
            content_weight=content_weight,
            sentiment_weight=sentiment_weight,
        )

        print("\nHybrid recommender ready.")

    # ========================================================
    # FINAL PUBLIC RECOMMENDATION METHOD
    # ========================================================

    def recommend_hybrid(
        self,
        user_id,
        top_n=10,
        minimum_rating=4.0,
        include_debug=False,
    ):

        # ----------------------------------------------------
        # INPUT VALIDATION
        # ----------------------------------------------------

        if not isinstance(user_id, int):
            raise TypeError(
                "user_id must be an integer."
            )

        if not isinstance(top_n, int):
            raise TypeError(
                "top_n must be an integer."
            )

        if top_n <= 0:
            raise ValueError(
                "top_n must be greater than 0."
            )

        if top_n > 100:
            raise ValueError(
                "top_n cannot exceed 100."
            )

        # ----------------------------------------------------
        # CHECK USER
        # ----------------------------------------------------

        try:
            self.ranker.history.get_user_index(
                user_id
            )

        except ValueError as exc:

            raise ValueError(
                f"User {user_id} is not available in "
                f"the trained collaborative model."
            ) from exc

        # ----------------------------------------------------
        # GENERATE FINAL RANKING
        # ----------------------------------------------------

        ranked = self.ranker.get_top_candidates(
            user_id=user_id,
            top_n=top_n,
            minimum_rating=minimum_rating,
        )

        title_column = (
            self.ranker.title_column
        )

        # ----------------------------------------------------
        # PUBLIC API RESULT
        # ----------------------------------------------------

        recommendations = []

        for rank, (_, dataframe_row) in enumerate(
            ranked.iterrows(),
            start=1,
        ):

            recommendation = {
                "rank": int(rank),
                "movieId": int(
                    dataframe_row["movieId"]
                ),
                "title": (
                    None
                    if dataframe_row[
                        title_column
                    ] != dataframe_row[
                        title_column
                    ]
                    else str(
                        dataframe_row[
                            title_column
                        ]
                    )
                ),
                "score": round(
                    float(
                        dataframe_row[
                            "hybrid_score"
                        ]
                    ),
                    6,
                ),
            }

            # ------------------------------------------------
            # DEBUG / EXPLAINABILITY INFORMATION
            # ------------------------------------------------

            if include_debug:

                recommendation.update(
                    {
                        "cfScore": round(
                            float(
                                dataframe_row[
                                    "cf_normalized"
                                ]
                            ),
                            6,
                        ),

                        "contentScore": round(
                            float(
                                dataframe_row[
                                    "content_normalized"
                                ]
                            ),
                            6,
                        ),

                        "sentimentScore": round(
                            float(
                                dataframe_row[
                                    "sentiment_normalized"
                                ]
                            ),
                            6,
                        ),

                        "hasSentiment": bool(
                            dataframe_row[
                                "has_sentiment"
                            ]
                        ),

                        "source": str(
                            dataframe_row[
                                "recommendation_source"
                            ]
                        ),
                    }
                )

            recommendations.append(
                recommendation
            )

        return recommendations


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    recommender = HybridRecommender(
        cf_weight=0.50,
        content_weight=0.35,
        sentiment_weight=0.15,
    )

    test_user_id = 1

    recommendations = (
        recommender.recommend_hybrid(
            user_id=test_user_id,
            top_n=10,
            minimum_rating=4.0,
            include_debug=True,
        )
    )

    print("\n" + "=" * 70)
    print(
        f"FINAL HYBRID RECOMMENDATIONS "
        f"FOR USER {test_user_id}"
    )
    print("=" * 70)

    print(
        json.dumps(
            recommendations,
            indent=2,
            ensure_ascii=False,
        )
    )