import sys
import pickle
from pathlib import Path

import numpy as np
from scipy import sparse


# ============================================================
# IMPORT PATH
# ============================================================

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


from recommender.config import CONTENT_MODEL_DIR
from recommender.artifact_loader import ArtifactLoader


def format_size(path: Path) -> str:
    size = path.stat().st_size

    if size < 1024:
        return f"{size} B"

    if size < 1024 ** 2:
        return f"{size / 1024:.2f} KB"

    if size < 1024 ** 3:
        return f"{size / (1024 ** 2):.2f} MB"

    return f"{size / (1024 ** 3):.2f} GB"


def main():
    print("=" * 80)
    print("CONTENT-BASED ARTIFACT INSPECTION")
    print("=" * 80)

    loader = ArtifactLoader()

    # ========================================================
    # 1. DIRECTORY CONTENTS
    # ========================================================

    print("\n1. CONTENT MODEL DIRECTORY")
    print("-" * 80)

    files = sorted(
        path
        for path in CONTENT_MODEL_DIR.iterdir()
        if path.is_file()
    )

    print(f"Directory: {CONTENT_MODEL_DIR}")
    print(f"Files    : {len(files)}")

    for path in files:
        print(
            f"{path.name:<45} "
            f"{format_size(path):>12}"
        )

    # ========================================================
    # 2. MOVIE ID -> CONTENT INDEX
    # ========================================================

    print("\n2. CONTENT MOVIE INDEX")
    print("-" * 80)

    movie_id_to_index = (
        loader.content_movie_id_to_index
    )

    print(
        f"Mapping type  : "
        f"{type(movie_id_to_index)}"
    )

    print(
        f"Movies        : "
        f"{len(movie_id_to_index):,}"
    )

    values = np.fromiter(
        movie_id_to_index.values(),
        dtype=np.int64,
        count=len(movie_id_to_index),
    )

    print(
        f"Index minimum : "
        f"{values.min()}"
    )

    print(
        f"Index maximum : "
        f"{values.max()}"
    )

    print(
        f"Unique indexes: "
        f"{len(np.unique(values)):,}"
    )

    print("\nFirst 10 mappings:")

    for movie_id, index in list(
        movie_id_to_index.items()
    )[:10]:
        print(
            f"  movieId {movie_id:<8} "
            f"-> contentIndex {index}"
        )

    # ========================================================
    # 3. CONTENT WEIGHTS
    # ========================================================

    print("\n3. CONTENT WEIGHTS")
    print("-" * 80)

    weights = loader.content_weights

    total_weight = 0.0

    for name, weight in weights.items():

        print(
            f"{name:<15}: "
            f"{float(weight):.4f}"
        )

        total_weight += float(weight)

    print(
        f"\nTotal weight   : "
        f"{total_weight:.4f}"
    )

    # ========================================================
    # 4. SPARSE MATRICES
    # ========================================================

    print("\n4. SPARSE MATRIX ARTIFACTS")
    print("-" * 80)

    npz_files = [
        path
        for path in files
        if path.suffix.lower() == ".npz"
    ]

    if not npz_files:
        print("No .npz files found.")

    for path in npz_files:

        print(f"\n{path.name}")

        try:

            matrix = sparse.load_npz(path)

            print(
                f"  Type     : "
                f"{type(matrix).__name__}"
            )

            print(
                f"  Format   : "
                f"{matrix.getformat()}"
            )

            print(
                f"  Shape    : "
                f"{matrix.shape}"
            )

            print(
                f"  Dtype    : "
                f"{matrix.dtype}"
            )

            print(
                f"  Non-zero : "
                f"{matrix.nnz:,}"
            )

            rows, columns = matrix.shape

            total_cells = rows * columns

            density = (
                matrix.nnz / total_cells
                if total_cells
                else 0.0
            )

            print(
                f"  Density  : "
                f"{density:.10f}"
            )

            if rows == len(movie_id_to_index):

                print(
                    "  Row check: PASS"
                )

            else:

                print(
                    "  Row check: WARNING "
                    f"({rows:,} != "
                    f"{len(movie_id_to_index):,})"
                )

        except Exception as exc:

            print(
                f"  Could not load as "
                f"SciPy sparse matrix: {exc}"
            )

    # ========================================================
    # 5. PICKLE ARTIFACTS
    # ========================================================

    print("\n5. PICKLE ARTIFACTS")
    print("-" * 80)

    pkl_files = [
        path
        for path in files
        if path.suffix.lower() == ".pkl"
    ]

    for path in pkl_files:

        print(f"\n{path.name}")

        try:

            with open(path, "rb") as file:
                obj = pickle.load(file)

            print(
                f"  Type: "
                f"{type(obj)}"
            )

            if isinstance(obj, dict):

                print(
                    f"  Entries: "
                    f"{len(obj):,}"
                )

                print(
                    f"  First keys: "
                    f"{list(obj.keys())[:10]}"
                )

            if hasattr(obj, "vocabulary_"):

                vocabulary = getattr(
                    obj,
                    "vocabulary_"
                )

                print(
                    f"  Vocabulary size: "
                    f"{len(vocabulary):,}"
                )

            if hasattr(obj, "idf_"):

                idf = getattr(
                    obj,
                    "idf_"
                )

                print(
                    f"  IDF shape: "
                    f"{np.asarray(idf).shape}"
                )

        except Exception as exc:

            print(
                f"  ERROR loading pickle: "
                f"{exc}"
            )

    # ========================================================
    # 6. MAPPING VALIDATION
    # ========================================================

    print("\n6. CONTENT MAPPING VALIDATION")
    print("-" * 80)

    expected = np.arange(
        len(movie_id_to_index),
        dtype=np.int64,
    )

    actual = np.sort(values)

    if np.array_equal(
        expected,
        actual,
    ):

        print(
            "PASS  - Content indexes are "
            "contiguous from 0"
        )

    else:

        print(
            "WARNING - Content indexes "
            "are not contiguous"
        )

    assert (
        len(movie_id_to_index)
        == len(loader.movies)
    ), (
        "Content movie mapping count "
        "does not match movie catalog."
    )

    print(
        "PASS  - Content mapping count "
        "matches movie catalog"
    )

    # ========================================================
    # FINAL
    # ========================================================

    print()

    print("=" * 80)
    print("CONTENT ARTIFACT INSPECTION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()