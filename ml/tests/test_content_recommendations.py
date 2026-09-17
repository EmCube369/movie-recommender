from pathlib import Path
import pickle
import numpy as np
import pandas as pd

from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity


# ======================================================================
# PATHS
# ======================================================================

ML_ROOT = Path(__file__).resolve().parents[1]

CBF_DIR = ML_ROOT / "models" / "content_based"
OUTPUT_DIR = ML_ROOT / "data" / "processed" / "testing"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ======================================================================
# ARTIFACT PATHS
# ======================================================================

MOVIES_PATH = CBF_DIR / "movies_cbf.csv"
MAPPING_PATH = CBF_DIR / "movie_id_to_index.pkl"
WEIGHTS_PATH = CBF_DIR / "content_weights.pkl"

MATRIX_PATHS = {
    "genre": CBF_DIR / "genre_matrix.npz",
    "keyword": CBF_DIR / "keyword_matrix.npz",
    "director": CBF_DIR / "director_matrix.npz",
    "cast": CBF_DIR / "cast_matrix.npz",
    "overview": CBF_DIR / "overview_matrix.npz",
    "tagline": CBF_DIR / "tagline_matrix.npz",
}


# ======================================================================
# TEST MOVIES
# ======================================================================

TEST_MOVIE_IDS = [
    1,       # Toy Story
    2571,    # The Matrix
    1721,    # Titanic
    58559,   # The Dark Knight
    79132,   # Inception
    858,     # The Godfather
    6377,    # Finding Nemo
    1214,    # Alien
]

TOP_K = 10


# ======================================================================
# LOAD ARTIFACTS
# ======================================================================

print("=" * 100)
print("3.9.2 CONTENT-BASED RECOMMENDATION TEST")
print("=" * 100)


required_paths = [
    MOVIES_PATH,
    MAPPING_PATH,
    WEIGHTS_PATH,
    *MATRIX_PATHS.values(),
]

missing_files = [path for path in required_paths if not path.exists()]

if missing_files:
    print("\nMissing artifacts:")
    for path in missing_files:
        print(path)

    raise FileNotFoundError(
        "One or more content-based artifacts are missing."
    )


movies = pd.read_csv(MOVIES_PATH)

with open(MAPPING_PATH, "rb") as f:
    movie_id_to_index = pickle.load(f)

with open(WEIGHTS_PATH, "rb") as f:
    content_weights = pickle.load(f)


matrices = {
    name: load_npz(path).tocsr()
    for name, path in MATRIX_PATHS.items()
}


# ======================================================================
# ARTIFACT VALIDATION
# ======================================================================

print("\n" + "=" * 100)
print("ARTIFACT VALIDATION")
print("=" * 100)

print(f"Movies: {len(movies):,}")
print(f"Mapping entries: {len(movie_id_to_index):,}")

for name, matrix in matrices.items():
    print(
        f"{name:<10} matrix shape: "
        f"{matrix.shape}"
    )


assert movies["movieId"].is_unique, "Duplicate movieIds in movies_cbf.csv"

assert len(movie_id_to_index) == len(movies), (
    "Mapping size does not match movie catalog size."
)

for name, matrix in matrices.items():
    assert matrix.shape[0] == len(movies), (
        f"{name} matrix row count does not match movie catalog."
    )


expected_weight_keys = set(MATRIX_PATHS.keys())
actual_weight_keys = set(content_weights.keys())

assert actual_weight_keys == expected_weight_keys, (
    f"Unexpected content weight keys.\n"
    f"Expected: {expected_weight_keys}\n"
    f"Actual:   {actual_weight_keys}"
)


weight_sum = sum(content_weights.values())

print("\nContent weights:")

for name, weight in content_weights.items():
    print(f"  {name:<10}: {weight:.4f}")

print(f"\nWeight sum: {weight_sum:.4f}")

assert np.isclose(weight_sum, 1.0), (
    f"Content weights must sum to 1.0, got {weight_sum}"
)


# ======================================================================
# VALIDATE MOVIE MAPPING
# ======================================================================

print("\nValidating movie mapping...")

for movie_id, index in movie_id_to_index.items():

    mapped_movie_id = int(movies.iloc[index]["movieId"])

    assert int(movie_id) == mapped_movie_id, (
        f"Mapping mismatch: movieId {movie_id} points to row "
        f"{index}, which contains movieId {mapped_movie_id}"
    )

print("Movie mapping validation passed.")


# ======================================================================
# CONTENT SCORE FUNCTION
# ======================================================================

def calculate_content_scores(seed_movie_id):
    """
    Calculate weighted content similarity between one seed movie
    and every movie in the catalog.
    """

    seed_movie_id = int(seed_movie_id)

    if seed_movie_id not in movie_id_to_index:
        raise ValueError(
            f"movieId {seed_movie_id} is not available "
            f"in the content-based mapping."
        )

    seed_index = movie_id_to_index[seed_movie_id]

    component_scores = {}

    weighted_score = np.zeros(
        len(movies),
        dtype=np.float32
    )

    for feature_name, matrix in matrices.items():

        similarity = cosine_similarity(
            matrix[seed_index],
            matrix
        ).ravel().astype(np.float32)

        component_scores[feature_name] = similarity

        weighted_score += (
            content_weights[feature_name] * similarity
        )

    return seed_index, weighted_score, component_scores


# ======================================================================
# RECOMMENDATION FUNCTION
# ======================================================================

def recommend_similar_movies(seed_movie_id, top_k=10):

    seed_index, scores, component_scores = (
        calculate_content_scores(seed_movie_id)
    )

    seed_movie_id = int(seed_movie_id)

    # Never recommend the seed movie itself.
    scores[seed_index] = -1.0

    # Get slightly more candidates before final selection.
    candidate_count = min(
        top_k + 20,
        len(scores)
    )

    candidate_indexes = np.argpartition(
        scores,
        -candidate_count
    )[-candidate_count:]

    candidate_indexes = candidate_indexes[
        np.argsort(scores[candidate_indexes])[::-1]
    ]

    selected_indexes = candidate_indexes[:top_k]

    results = movies.iloc[selected_indexes].copy()

    results["contentScore"] = scores[selected_indexes]

    results["genreSim"] = (
        component_scores["genre"][selected_indexes]
    )

    results["keywordSim"] = (
        component_scores["keyword"][selected_indexes]
    )

    results["directorSim"] = (
        component_scores["director"][selected_indexes]
    )

    results["castSim"] = (
        component_scores["cast"][selected_indexes]
    )

    results["overviewSim"] = (
        component_scores["overview"][selected_indexes]
    )

    results["taglineSim"] = (
        component_scores["tagline"][selected_indexes]
    )

    return results.reset_index(drop=True)


# ======================================================================
# AUTOMATED VALIDATION
# ======================================================================

def validate_recommendations(seed_movie_id, recommendations):

    failures = []

    seed_movie_id = int(seed_movie_id)

    # --------------------------------------------------------------
    # Correct number of recommendations
    # --------------------------------------------------------------

    if len(recommendations) != TOP_K:
        failures.append(
            f"Expected {TOP_K} recommendations, "
            f"got {len(recommendations)}."
        )

    # --------------------------------------------------------------
    # Seed must not appear
    # --------------------------------------------------------------

    if seed_movie_id in recommendations["movieId"].astype(int).values:
        failures.append(
            "Seed movie appears in its own recommendations."
        )

    # --------------------------------------------------------------
    # No duplicate recommendations
    # --------------------------------------------------------------

    if recommendations["movieId"].duplicated().any():
        failures.append(
            "Duplicate movieIds found."
        )

    # --------------------------------------------------------------
    # Scores must be finite
    # --------------------------------------------------------------

    scores = recommendations["contentScore"].to_numpy()

    if not np.isfinite(scores).all():
        failures.append(
            "Non-finite content scores found."
        )

    # --------------------------------------------------------------
    # Content similarity should be within [0, 1]
    # --------------------------------------------------------------

    if np.any(scores < 0) or np.any(scores > 1.000001):
        failures.append(
            "Content scores outside expected [0, 1] range."
        )

    # --------------------------------------------------------------
    # Scores must be descending
    # --------------------------------------------------------------

    if len(scores) > 1:

        if not np.all(scores[:-1] >= scores[1:] - 1e-8):
            failures.append(
                "Recommendations are not sorted "
                "by descending content score."
            )

    return failures


# ======================================================================
# RUN TESTS
# ======================================================================

all_results = []

overall_pass = True


for seed_movie_id in TEST_MOVIE_IDS:

    print("\n" + "=" * 100)

    if seed_movie_id not in movie_id_to_index:

        print(
            f"SKIPPED: movieId {seed_movie_id} "
            f"is not in content mapping."
        )

        overall_pass = False
        continue

    seed_index = movie_id_to_index[seed_movie_id]

    seed_title = movies.iloc[seed_index]["title"]

    print(f"SEED: {seed_title}")
    print(f"movieId: {seed_movie_id}")
    print("=" * 100)

    recommendations = recommend_similar_movies(
        seed_movie_id,
        TOP_K
    )

    failures = validate_recommendations(
        seed_movie_id,
        recommendations
    )

    display_columns = [
        "movieId",
        "title",
        "contentScore",
        "genreSim",
        "keywordSim",
        "directorSim",
        "castSim",
        "overviewSim",
        "taglineSim",
    ]

    print(
        recommendations[display_columns].to_string(
            index=False
        )
    )

    print("\nAutomated checks:")

    if failures:

        overall_pass = False

        for failure in failures:
            print(f"  FAIL - {failure}")

    else:

        print("  PASS - returned Top-K recommendations")
        print("  PASS - seed movie excluded")
        print("  PASS - no duplicate recommendations")
        print("  PASS - all scores finite")
        print("  PASS - scores within expected range")
        print("  PASS - scores sorted descending")


    # --------------------------------------------------------------
    # Save results
    # --------------------------------------------------------------

    recommendations.insert(
        0,
        "seedMovieId",
        seed_movie_id
    )

    recommendations.insert(
        1,
        "seedTitle",
        seed_title
    )

    recommendations.insert(
        2,
        "rank",
        np.arange(1, len(recommendations) + 1)
    )

    all_results.append(recommendations)


# ======================================================================
# TOY STORY REGRESSION CHECK
# ======================================================================

print("\n" + "=" * 100)
print("TOY STORY REGRESSION CHECK")
print("=" * 100)

toy_story_results = recommend_similar_movies(
    1,
    TOP_K
)

toy_story_top = toy_story_results.iloc[0]

print(f"Top result: {toy_story_top['title']}")
print(f"Score: {toy_story_top['contentScore']:.6f}")


toy_story_title_pass = (
    "toy story 2"
    in str(toy_story_top["title"]).lower()
)

toy_story_score_pass = np.isclose(
    float(toy_story_top["contentScore"]),
    0.558876,
    atol=1e-4
)


if toy_story_title_pass:
    print("PASS - Toy Story 2 remains the top recommendation.")
else:
    print(
        "WARNING - Toy Story 2 is no longer "
        "the top recommendation."
    )


if toy_story_score_pass:
    print(
        "PASS - Toy Story score matches "
        "the Phase 3.9 baseline."
    )
else:
    print(
        "WARNING - Toy Story top score differs "
        "from the Phase 3.9 baseline."
    )


# ======================================================================
# SAVE COMPLETE TEST OUTPUT
# ======================================================================

if all_results:

    final_results = pd.concat(
        all_results,
        ignore_index=True
    )

    output_path = (
        OUTPUT_DIR /
        "content_based_test_results.csv"
    )

    final_results.to_csv(
        output_path,
        index=False
    )

    print("\nSaved:")
    print(output_path)


# ======================================================================
# FINAL RESULT
# ======================================================================

print("\n" + "=" * 100)
print("3.9.2 AUTOMATED TEST RESULT")
print("=" * 100)

if overall_pass:
    print("PASS - All structural content recommendation tests passed.")
else:
    print("FAIL - One or more structural tests failed.")

print(
    "\nNOTE:"
    "\nAutomated checks only verify technical correctness."
    "\nWe still need to inspect whether the recommended movies "
    "are semantically relevant to each seed movie."
)