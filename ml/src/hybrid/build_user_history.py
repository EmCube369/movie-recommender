from pathlib import Path
import json

import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

ML_ROOT = Path(__file__).resolve().parents[2]

CF_DIR = (
    ML_ROOT
    / "data"
    / "features"
    / "collaborative"
)

INTERACTIONS_PATH = (
    CF_DIR
    / "cf_interactions.csv"
)

USER_MAPPING_PATH = (
    CF_DIR
    / "cf_user_mapping.csv"
)

MOVIE_MAPPING_PATH = (
    CF_DIR
    / "cf_movie_mapping.csv"
)

OUTPUT_DIR = (
    ML_ROOT
    / "models"
    / "hybrid"
)

INDPTR_PATH = (
    OUTPUT_DIR
    / "user_history_indptr.npy"
)

MOVIE_INDEXES_PATH = (
    OUTPUT_DIR
    / "user_history_movie_indexes.npy"
)

METADATA_PATH = (
    OUTPUT_DIR
    / "user_history_metadata.json"
)

RATINGS_PATH = (
    OUTPUT_DIR
    / "user_history_ratings.npy"
)


# ============================================================
# SETTINGS
# ============================================================

CHUNK_SIZE = 1_000_000


# ============================================================
# LOAD MAPPINGS
# ============================================================

print("=" * 70)
print("BUILDING COMPACT USER HISTORY")
print("=" * 70)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

user_mapping = pd.read_csv(
    USER_MAPPING_PATH
)

movie_mapping = pd.read_csv(
    MOVIE_MAPPING_PATH
)

num_users = len(
    user_mapping
)

num_movies = len(
    movie_mapping
)

print(f"Users : {num_users:,}")
print(f"Movies: {num_movies:,}")


# ============================================================
# PASS 1
#
# Count interactions belonging to each user.
# ============================================================

print("\n" + "=" * 70)
print("PASS 1 — COUNT USER INTERACTIONS")
print("=" * 70)

user_counts = np.zeros(
    num_users,
    dtype=np.int64,
)

total_interactions = 0
chunk_number = 0

for chunk in pd.read_csv(
    INTERACTIONS_PATH,
    usecols=["userIndex"],
    dtype={
        "userIndex": np.int32,
    },
    chunksize=CHUNK_SIZE,
):

    chunk_number += 1

    users = chunk[
        "userIndex"
    ].to_numpy(
        dtype=np.int32,
        copy=False,
    )

    if len(users) == 0:
        continue

    if users.min() < 0:
        raise ValueError(
            "Negative userIndex found."
        )

    if users.max() >= num_users:
        raise ValueError(
            f"userIndex {users.max()} exceeds "
            f"mapping size {num_users}."
        )

    user_counts += np.bincount(
        users,
        minlength=num_users,
    )

    total_interactions += len(users)

    print(
        f"Chunk {chunk_number}: "
        f"{total_interactions:,} interactions"
    )


# ============================================================
# BUILD INDPTR
# ============================================================

indptr = np.zeros(
    num_users + 1,
    dtype=np.int64,
)

np.cumsum(
    user_counts,
    out=indptr[1:],
)

if int(indptr[-1]) != total_interactions:
    raise RuntimeError(
        "Interaction count mismatch."
    )

np.save(
    INDPTR_PATH,
    indptr,
)

print(
    f"\nTotal interactions: "
    f"{total_interactions:,}"
)


# ============================================================
# PREALLOCATE MOVIE INDEX ARRAY
#
# open_memmap writes directly to the .npy file instead of
# keeping the whole output array in RAM.
# ============================================================

history_movie_indexes = (
    np.lib.format.open_memmap(
        MOVIE_INDEXES_PATH,
        mode="w+",
        dtype=np.int32,
        shape=(total_interactions,),
    )
)

history_ratings = (
    np.lib.format.open_memmap(
        RATINGS_PATH,
        mode="w+",
        dtype=np.float32,
        shape=(total_interactions,),
    )
)

write_positions = (
    indptr[:-1].copy()
)


# ============================================================
# PASS 2
#
# Place every movieIndex inside its user's slice.
# ============================================================

print("\n" + "=" * 70)
print("PASS 2 — WRITE USER HISTORIES")
print("=" * 70)

written = 0
chunk_number = 0

for chunk in pd.read_csv(
    INTERACTIONS_PATH,
    usecols=[
        "userIndex",
        "movieIndex",
        "rating",
    ],
    dtype={
        "userIndex": np.int32,
        "movieIndex": np.int32,
        "rating": np.float32,
    },
    chunksize=CHUNK_SIZE,
):

    chunk_number += 1

    users = chunk[
        "userIndex"
    ].to_numpy(
        dtype=np.int32,
        copy=False,
    )

    movies = chunk[
        "movieIndex"
    ].to_numpy(
        dtype=np.int32,
        copy=False,
    )

    ratings = chunk[
        "rating"
    ].to_numpy(
        dtype=np.float32,
        copy=False,
    )

    # --------------------------------------------------------
    # Group the current chunk by userIndex.
    #
    # This makes the build robust even if the CSV is not
    # perfectly ordered by user.
    # --------------------------------------------------------

    order = np.argsort(
        users,
        kind="stable",
    )

    users_sorted = users[
        order
    ]

    movies_sorted = movies[
        order
    ]

    ratings_sorted = ratings[
        order
    ]

    unique_users, starts, counts = (
        np.unique(
            users_sorted,
            return_index=True,
            return_counts=True,
        )
    )

    for user_index, start, count in zip(
        unique_users,
        starts,
        counts,
    ):

        user_index = int(
            user_index
        )

        start = int(
            start
        )

        count = int(
            count
        )

        destination = int(
            write_positions[
                user_index
            ]
        )

        history_movie_indexes[
            destination:
            destination + count
        ] = movies_sorted[
            start:
            start + count
        ]

        history_ratings[
            destination:
            destination + count
        ] = ratings_sorted[
            start:
            start + count
        ]

        write_positions[
            user_index
        ] += count

    written += len(chunk)

    print(
        f"Chunk {chunk_number}: "
        f"{written:,} interactions written"
    )


# ============================================================
# FLUSH FILE
# ============================================================

history_movie_indexes.flush()
history_ratings.flush()


# ============================================================
# VALIDATION
# ============================================================

print("\n" + "=" * 70)
print("VALIDATION")
print("=" * 70)

expected_positions = (
    indptr[1:]
)

if not np.array_equal(
    write_positions,
    expected_positions,
):
    raise RuntimeError(
        "User-history write positions "
        "do not match expected boundaries."
    )

if written != total_interactions:
    raise RuntimeError(
        "Written interaction total "
        "does not match counted total."
    )

print(
    "All interactions written:",
    f"{written:,}",
)

print(
    "Users with interactions:",
    f"{np.count_nonzero(user_counts):,}",
)

print(
    "Minimum interactions:",
    int(user_counts.min()),
)

print(
    "Maximum interactions:",
    int(user_counts.max()),
)

print(
    "Median interactions:",
    float(
        np.median(user_counts)
    ),
)


# ============================================================
# TEST USER 1
# ============================================================

user_id_to_index = dict(
    zip(
        user_mapping["userId"],
        user_mapping["userIndex"],
    )
)

test_user_id = 1

test_user_index = int(
    user_id_to_index[
        test_user_id
    ]
)

start = int(
    indptr[
        test_user_index
    ]
)

end = int(
    indptr[
        test_user_index + 1
    ]
)

test_history = (
    history_movie_indexes[
        start:end
    ]
)

test_ratings = (
    history_ratings[
        start:end
    ]
)

test_positive_mask = (
    test_ratings >= 4.0
)

test_positive_movies = (
    test_history[
        test_positive_mask
    ]
)

print(
    f"\nUser {test_user_id}"
    f" -> userIndex {test_user_index}"
)

print(
    "Rated movies:",
    len(test_history),
)

print(
    "Positive movies >= 4.0:",
    len(test_positive_movies),
)


# ============================================================
# SAVE METADATA
# ============================================================

metadata = {
    "num_users": int(
        num_users
    ),
    "num_movies": int(
        num_movies
    ),
    "total_interactions": int(
        total_interactions
    ),
    "history_format": (
        "CSR-style indptr + movieIndex + rating arrays"
    ),
    "indptr_dtype": "int64",
    "movie_index_dtype": "int32",
    "rating_dtype": "float32",
}

with open(
    METADATA_PATH,
    "w",
    encoding="utf-8",
) as f:

    json.dump(
        metadata,
        f,
        indent=2,
    )


# ============================================================
# FILE SIZES
# ============================================================

indptr_mb = (
    INDPTR_PATH.stat().st_size
    / (1024 ** 2)
)

movies_mb = (
    MOVIE_INDEXES_PATH.stat().st_size
    / (1024 ** 2)
)

ratings_mb = (
    RATINGS_PATH.stat().st_size
    / (1024 ** 2)
)

print("\n" + "=" * 70)
print("USER HISTORY ARTIFACT COMPLETE")
print("=" * 70)

print(
    f"indptr file : "
    f"{indptr_mb:.2f} MB"
)

print(
    f"movie file  : "
    f"{movies_mb:.2f} MB"
)

print(
    f"ratings file: "
    f"{ratings_mb:.2f} MB"
)

print(
    f"Saved to    : "
    f"{OUTPUT_DIR}"
)

print(
    "\nCompact user-history artifacts "
    "passed validation."
)