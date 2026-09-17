import sys
from pathlib import Path


# ============================================================
# IMPORT PATH
# ============================================================

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


from recommender.collaborative import CollaborativeRecommender


def main():
    print("=" * 70)
    print("COLLABORATIVE MODULE VALIDATION")
    print("=" * 70)

    # ========================================================
    # 1. INITIALIZE
    # ========================================================

    print("\n1. INITIALIZATION")
    print("-" * 70)

    cf = CollaborativeRecommender()

    print(f"Device          : {cf.device}")
    print(f"Users           : {cf.num_users:,}")
    print(f"Movies          : {cf.num_movies:,}")
    print(f"Embedding dim   : {cf.embedding_dim}")
    print(f"Global mean     : {cf.global_mean:.6f}")
    print(f"Best epoch      : {cf.best_epoch}")
    print(
        f"Validation RMSE : "
        f"{cf.validation_rmse:.6f}"
    )

    # ========================================================
    # 2. USER LOOKUP
    # ========================================================

    print("\n2. USER LOOKUP")
    print("-" * 70)

    test_user_id = 1

    assert cf.has_user(test_user_id)

    user_index = cf.get_user_index(
        test_user_id
    )

    print(
        f"PASS  - userId {test_user_id} "
        f"-> userIndex {user_index}"
    )

    # ========================================================
    # 3. CANDIDATE SCORING
    # ========================================================

    print("\n3. CANDIDATE SCORING")
    print("-" * 70)

    scores = cf.score_candidates(
        user_id=test_user_id
    )

    print(
        f"Candidates scored : "
        f"{len(scores):,}"
    )

    print(
        f"Minimum prediction: "
        f"{scores['cf_score'].min():.4f}"
    )

    print(
        f"Maximum prediction: "
        f"{scores['cf_score'].max():.4f}"
    )

    assert len(scores) == 43_599

    assert (
        scores["cf_score"] >= 0.5
    ).all()

    assert (
        scores["cf_score"] <= 5.0
    ).all()

    assert scores["movieId"].is_unique

    print(
        "PASS  - All trained CF candidates "
        "scored successfully"
    )

    print(
        "PASS  - Predictions are within "
        "0.5 to 5.0"
    )

    print(
        "PASS  - Candidate movieIds "
        "are unique"
    )

    # ========================================================
    # 4. TOP RECOMMENDATIONS
    # ========================================================

    print("\n4. TOP RECOMMENDATIONS")
    print("-" * 70)

    recommendations = cf.recommend(
        user_id=test_user_id,
        top_n=10,
    )

    print(
        recommendations.to_string(
            index=False
        )
    )

    assert len(recommendations) == 10

    assert (
        recommendations[
            "cf_score"
        ].is_monotonic_decreasing
    )

    print(
        "\nPASS  - Top-10 ranking "
        "is descending"
    )

    # ========================================================
    # 5. EXCLUSION TEST
    # ========================================================

    print("\n5. EXCLUSION TEST")
    print("-" * 70)

    excluded_movie_ids = (
        recommendations[
            "movieId"
        ]
        .head(3)
        .tolist()
    )

    new_recommendations = cf.recommend(
        user_id=test_user_id,
        top_n=10,
        exclude_movie_ids=excluded_movie_ids,
    )

    overlap = (
        set(excluded_movie_ids)
        & set(
            new_recommendations[
                "movieId"
            ]
        )
    )

    assert not overlap

    print(
        f"Excluded movieIds: "
        f"{excluded_movie_ids}"
    )

    print(
        "PASS  - Excluded movies were "
        "removed from recommendations"
    )

    # ========================================================
    # FINAL
    # ========================================================

    print()

    print("=" * 70)
    print("COLLABORATIVE MODULE VALID")
    print("=" * 70)


if __name__ == "__main__":
    main()