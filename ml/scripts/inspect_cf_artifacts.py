import sys
from pathlib import Path

import numpy as np
import torch


# ============================================================
# IMPORT PATH
# ============================================================

ML_ROOT = Path(__file__).resolve().parents[1]

if str(ML_ROOT) not in sys.path:
    sys.path.insert(0, str(ML_ROOT))


from recommender.artifact_loader import ArtifactLoader


def main():
    print("=" * 70)
    print("COLLABORATIVE ARTIFACT INSPECTION")
    print("=" * 70)

    loader = ArtifactLoader()

    # ========================================================
    # 1. CHECKPOINT
    # ========================================================

    print("\n1. CF CHECKPOINT")
    print("-" * 70)

    checkpoint = loader.load_cf_checkpoint("cpu")

    print(f"Checkpoint type: {type(checkpoint)}")

    if isinstance(checkpoint, dict):

        print("\nCheckpoint keys:")

        for key in checkpoint.keys():
            value = checkpoint[key]

            if isinstance(value, torch.Tensor):
                print(
                    f"  {key:<30} "
                    f"Tensor shape={tuple(value.shape)} "
                    f"dtype={value.dtype}"
                )

            elif isinstance(value, dict):
                print(
                    f"  {key:<30} "
                    f"dict ({len(value):,} entries)"
                )

            else:
                print(
                    f"  {key:<30} "
                    f"{type(value).__name__}: {value}"
                )

    # ========================================================
    # 2. STATE DICT INSPECTION
    # ========================================================

    print("\n2. MODEL STATE")
    print("-" * 70)

    state_dict = None

    if isinstance(checkpoint, dict):

        if "model_state_dict" in checkpoint:
            state_dict = checkpoint["model_state_dict"]

        elif "state_dict" in checkpoint:
            state_dict = checkpoint["state_dict"]

        elif all(
            isinstance(value, torch.Tensor)
            for value in checkpoint.values()
        ):
            state_dict = checkpoint

    if state_dict is None:

        print(
            "Could not automatically identify a model state_dict."
        )

    else:

        print(f"State entries: {len(state_dict):,}")

        for name, tensor in state_dict.items():

            if isinstance(tensor, torch.Tensor):

                print(
                    f"{name:<40} "
                    f"shape={tuple(tensor.shape)} "
                    f"dtype={tensor.dtype}"
                )

            else:

                print(
                    f"{name:<40} "
                    f"type={type(tensor).__name__}"
                )

    # ========================================================
    # 3. SEEN MOVIE INDEXES
    # ========================================================

    print("\n3. CF SEEN MOVIE INDEXES")
    print("-" * 70)

    seen = loader.cf_seen_movie_indexes

    print(f"Shape       : {seen.shape}")
    print(f"Dtype       : {seen.dtype}")
    print(f"Count       : {len(seen):,}")

    if len(seen) > 0:

        print(f"Minimum     : {seen.min()}")
        print(f"Maximum     : {seen.max()}")
        print(
            f"Unique      : "
            f"{len(np.unique(seen)):,}"
        )

        print(
            f"First 10    : "
            f"{seen[:10].tolist()}"
        )

    # ========================================================
    # 4. CF MAPPING RANGES
    # ========================================================

    print("\n4. CF MAPPING RANGES")
    print("-" * 70)

    users = loader.cf_user_mapping
    movies = loader.cf_movie_mapping

    print(
        f"User indexes : "
        f"{users['userIndex'].min()} -> "
        f"{users['userIndex'].max()}"
    )

    print(
        f"Movie indexes: "
        f"{movies['movieIndex'].min()} -> "
        f"{movies['movieIndex'].max()}"
    )

    print(
        f"Users        : "
        f"{len(users):,}"
    )

    print(
        f"Movies       : "
        f"{len(movies):,}"
    )

    print()
    print("=" * 70)
    print("CF ARTIFACT INSPECTION COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    main()