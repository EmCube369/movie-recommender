import sys
from pathlib import Path

import numpy as np
import pandas as pd


# ============================================================
# PATH SETUP
# ============================================================

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


def format_size(path: Path) -> str:
    size = path.stat().st_size

    if size < 1024:
        return f"{size} B"

    if size < 1024 ** 2:
        return f"{size / 1024:.2f} KB"

    if size < 1024 ** 3:
        return f"{size / (1024 ** 2):.2f} MB"

    return f"{size / (1024 ** 3):.2f} GB"


def inspect_csv(path: Path):
    print(f"\nFILE: {path}")
    print(f"Size: {format_size(path)}")

    try:
        df = pd.read_csv(
            path,
            nrows=10,
        )

        print(
            f"Columns: "
            f"{list(df.columns)}"
        )

        print("\nSample:")

        print(
            df.to_string(
                index=False
            )
        )

    except Exception as exc:
        print(
            f"CSV inspection failed: {exc}"
        )


def inspect_npy(path: Path):
    print(f"\nFILE: {path}")
    print(f"Size: {format_size(path)}")

    try:

        arr = np.load(
            path,
            mmap_mode="r",
            allow_pickle=False,
        )

        print(
            f"Shape : {arr.shape}"
        )

        print(
            f"Dtype : {arr.dtype}"
        )

        print(
            f"First values: "
            f"{arr[:10]}"
        )

    except Exception as exc:
        print(
            f"NumPy inspection failed: {exc}"
        )


def inspect_npz(path: Path):
    print(f"\nFILE: {path}")
    print(f"Size: {format_size(path)}")

    try:

        data = np.load(
            path,
            allow_pickle=False,
        )

        print(
            f"Arrays: "
            f"{data.files}"
        )

        for name in data.files:

            arr = data[name]

            print(
                f"  {name:<25} "
                f"shape={arr.shape} "
                f"dtype={arr.dtype}"
            )

    except Exception as exc:
        print(
            f"NPZ inspection failed: {exc}"
        )


def main():
    print("=" * 80)
    print("USER HISTORY ARTIFACT INSPECTION")
    print("=" * 80)

    # ========================================================
    # SEARCH LIKELY DIRECTORIES
    # ========================================================

    search_dirs = [
        ML_ROOT / "data" / "features" / "collaborative",
        ML_ROOT / "data" / "processed",
        ML_ROOT / "models" / "collaborative",
        ML_ROOT / "models" / "hybrid",
        ML_ROOT / "data" / "features" / "hybrid",
    ]

    keywords = (
        "history",
        "interaction",
        "rated",
        "rating",
        "user",
        "seen",
    )

    candidates = []

    print("\n1. SEARCHING FOR POSSIBLE HISTORY ARTIFACTS")
    print("-" * 80)

    for directory in search_dirs:

        if not directory.exists():
            continue

        for path in directory.rglob("*"):

            if not path.is_file():
                continue

            name_lower = path.name.lower()

            if any(
                keyword in name_lower
                for keyword in keywords
            ):
                candidates.append(path)

    candidates = sorted(
        set(candidates)
    )

    if not candidates:
        print(
            "No likely history artifacts found."
        )

    else:

        for path in candidates:
            print(
                f"{path.relative_to(ML_ROOT)!s:<70} "
                f"{format_size(path):>10}"
            )

    # ========================================================
    # INSPECT LIKELY FILES
    # ========================================================

    print("\n2. INSPECTING CANDIDATE ARTIFACTS")
    print("-" * 80)

    for path in candidates:

        suffix = path.suffix.lower()

        # Avoid loading giant CSV files completely.
        if suffix == ".csv":
            inspect_csv(path)

        elif suffix == ".npy":
            inspect_npy(path)

        elif suffix == ".npz":
            inspect_npz(path)

    print()

    print("=" * 80)
    print("USER HISTORY ARTIFACT INSPECTION COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()