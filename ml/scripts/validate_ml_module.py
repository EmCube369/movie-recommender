import sys
from pathlib import Path


# ============================================================
# PYTHON IMPORT PATH SETUP
# ============================================================

# This resolves to:
# D:\Movie-Recommender\ml
ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


# ============================================================
# IMPORT ML MODULE
# ============================================================

from recommender.config import (
    REQUIRED_ARTIFACTS,
    validate_required_artifacts,
)

from recommender.artifact_loader import ArtifactLoader


# ============================================================
# MAIN VALIDATION
# ============================================================

def main():
    print("=" * 70)
    print("ML MODULE VALIDATION")
    print("=" * 70)

    # ========================================================
    # 1. REQUIRED ARTIFACTS
    # ========================================================

    print("\n1. REQUIRED ARTIFACTS")
    print("-" * 70)

    for name, path in REQUIRED_ARTIFACTS.items():

        status = "PASS" if path.exists() else "FAIL"

        print(
            f"{status:<5} - "
            f"{name:<25} "
            f"{path}"
        )

    # Raises FileNotFoundError if something is missing
    validate_required_artifacts()

    # ========================================================
    # 2. ARTIFACT LOADER
    # ========================================================

    print("\n2. ARTIFACT LOADER")
    print("-" * 70)

    loader = ArtifactLoader()

    movies = loader.movies

    user_mapping = loader.cf_user_mapping
    movie_mapping = loader.cf_movie_mapping
    seen_movies = loader.cf_seen_movie_indexes

    content_index = loader.content_movie_id_to_index
    content_weights = loader.content_weights

    sentiment = loader.movie_sentiment

    print(f"Movies             : {len(movies):,}")
    print(f"CF users           : {len(user_mapping):,}")
    print(f"CF movies          : {len(movie_mapping):,}")
    print(f"CF seen indexes    : {len(seen_movies):,}")
    print(f"Content movies     : {len(content_index):,}")
    print(f"Content weights    : {content_weights}")
    print(f"Sentiment movies   : {len(sentiment):,}")

    # ========================================================
    # 3. RUNTIME MAPPINGS
    # ========================================================

    print("\n3. RUNTIME MAPPINGS")
    print("-" * 70)

    user_id_to_index = loader.user_id_to_index
    movie_id_to_cf_index = loader.movie_id_to_cf_index
    cf_index_to_movie_id = loader.cf_index_to_movie_id

    print(
        f"userId -> index     : "
        f"{len(user_id_to_index):,}"
    )

    print(
        f"movieId -> CF index : "
        f"{len(movie_id_to_cf_index):,}"
    )

    print(
        f"CF index -> movieId : "
        f"{len(cf_index_to_movie_id):,}"
    )

    # ========================================================
    # 4. BASIC CONSISTENCY CHECKS
    # ========================================================

    print("\n4. BASIC CONSISTENCY CHECKS")
    print("-" * 70)

    # Movie catalog uniqueness
    assert movies["movieId"].is_unique, (
        "Movie catalog contains duplicate movieId values."
    )

    print("PASS  - Movie catalog movieIds are unique")

    # CF user mapping
    assert user_mapping["userId"].is_unique, (
        "CF user mapping contains duplicate userId values."
    )

    assert user_mapping["userIndex"].is_unique, (
        "CF user mapping contains duplicate userIndex values."
    )

    print("PASS  - CF user mapping is unique")

    # CF movie mapping
    assert movie_mapping["movieId"].is_unique, (
        "CF movie mapping contains duplicate movieId values."
    )

    assert movie_mapping["movieIndex"].is_unique, (
        "CF movie mapping contains duplicate movieIndex values."
    )

    print("PASS  - CF movie mapping is unique")

    # Mapping lengths
    assert len(user_id_to_index) == len(user_mapping), (
        "userId -> index mapping size mismatch."
    )

    print("PASS  - User runtime mapping size matches")

    assert len(movie_id_to_cf_index) == len(movie_mapping), (
        "movieId -> CF index mapping size mismatch."
    )

    assert len(cf_index_to_movie_id) == len(movie_mapping), (
        "CF index -> movieId mapping size mismatch."
    )

    print("PASS  - Movie runtime mapping sizes match")

    # Content mapping
    assert len(content_index) > 0, (
        "Content movie index is empty."
    )

    print("PASS  - Content movie index is not empty")

    # Content weights
    assert len(content_weights) > 0, (
        "Content weights are empty."
    )

    print("PASS  - Content weights are not empty")

    # Sentiment uniqueness
    assert sentiment["movieId"].is_unique, (
        "Sentiment artifact contains duplicate movieId values."
    )

    print("PASS  - Sentiment movieIds are unique")

    # ========================================================
    # 5. CACHE CHECK
    # ========================================================

    print("\n5. LOADER CACHE CHECK")
    print("-" * 70)

    # cached_property should return the exact same object
    movies_again = loader.movies
    user_mapping_again = loader.cf_user_mapping

    assert movies is movies_again, (
        "Movie catalog was reloaded instead of cached."
    )

    assert user_mapping is user_mapping_again, (
        "CF user mapping was reloaded instead of cached."
    )

    print("PASS  - Artifact caching works")

    # ========================================================
    # FINAL
    # ========================================================

    print()
    print("=" * 70)
    print("ML ARTIFACT LOADER VALID")
    print("=" * 70)


if __name__ == "__main__":
    main()