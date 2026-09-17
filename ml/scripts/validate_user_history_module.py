import sys
from pathlib import Path

import numpy as np


ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


from recommender.user_history import UserHistory


def main():

    print("=" * 80)
    print("USER HISTORY MODULE VALIDATION")
    print("=" * 80)

    # ========================================================
    # 1. INITIALIZATION
    # ========================================================

    print("\n1. INITIALIZATION")
    print("-" * 80)

    history = UserHistory()

    print(
        f"Users        : "
        f"{len(history.indptr) - 1:,}"
    )

    print(
        f"Interactions : "
        f"{len(history.movie_indexes):,}"
    )

    print(
        f"Ratings      : "
        f"{len(history.ratings):,}"
    )

    assert (
        len(history.indptr)
        == 200_949
    )

    assert (
        len(history.movie_indexes)
        == 31_920_673
    )

    assert (
        len(history.ratings)
        == 31_920_673
    )

    print(
        "PASS  - Compact history loaded"
    )

    # ========================================================
    # 2. USER 1
    # ========================================================

    print("\n2. USER 1 HISTORY")
    print("-" * 80)

    user_id = 1

    assert history.has_user(
        user_id
    )

    count = history.interaction_count(
        user_id
    )

    movie_indexes = (
        history.get_movie_indexes(
            user_id
        )
    )

    movie_ids = (
        history.get_rated_movie_ids(
            user_id
        )
    )

    ratings = history.get_ratings(
        user_id
    )

    print(
        f"Interaction count : "
        f"{count}"
    )

    print(
        f"Movie indexes     : "
        f"{len(movie_indexes)}"
    )

    print(
        f"Movie IDs         : "
        f"{len(movie_ids)}"
    )

    print(
        f"Ratings           : "
        f"{len(ratings)}"
    )

    print(
        f"Mean rating       : "
        f"{ratings.mean():.6f}"
    )

    assert count == 141

    assert len(movie_indexes) == 141
    assert len(movie_ids) == 141
    assert len(ratings) == 141

    assert np.isclose(
        ratings.mean(),
        3.5319149,
        atol=1e-5,
    )

    print(
        "PASS  - User 1 history matches mapping"
    )

    # ========================================================
    # 3. POSITIVE HISTORY
    # ========================================================

    print("\n3. POSITIVE HISTORY")
    print("-" * 80)

    positive_movie_ids = (
        history.get_positive_movie_ids(
            user_id=1,
            min_rating=4.0,
        )
    )

    positive_count_direct = int(
        np.sum(
            ratings >= 4.0
        )
    )

    print(
        f"Positive movie count : "
        f"{len(positive_movie_ids)}"
    )

    print(
        f"Direct rating count  : "
        f"{positive_count_direct}"
    )

    assert (
        len(positive_movie_ids)
        == positive_count_direct
    )

    print(
        "PASS  - Positive-history filtering correct"
    )

    # ========================================================
    # 4. MOVIE-ID ROUND TRIP
    # ========================================================

    print("\n4. MOVIE INDEX ROUND TRIP")
    print("-" * 80)

    for movie_index, movie_id in zip(
        movie_indexes[:10],
        movie_ids[:10],
    ):

        mapped_index = (
            history.loader
            .movie_id_to_cf_index[
                int(movie_id)
            ]
        )

        assert (
            mapped_index
            == int(movie_index)
        )

    print(
        "PASS  - Movie index/movieId conversion correct"
    )

    # ========================================================
    # 5. SUMMARY
    # ========================================================

    print("\n5. USER SUMMARY")
    print("-" * 80)

    summary = history.summary(
        user_id=1
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
        == positive_count_direct
    )

    # ========================================================
    # 6. HISTORY TABLE
    # ========================================================

    print("\n6. HISTORY SAMPLE")
    print("-" * 80)

    table = history.get_history(
        user_id=1
    )

    print(
        table
        .head(10)
        .to_string(
            index=False
        )
    )

    assert len(table) == 141

    print(
        "\nPASS  - User history table generated"
    )

    # ========================================================
    # FINAL
    # ========================================================

    print()

    print("=" * 80)
    print("USER HISTORY MODULE VALID")
    print("=" * 80)


if __name__ == "__main__":
    main()