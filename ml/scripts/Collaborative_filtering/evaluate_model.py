from pathlib import Path

import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader

from model import MatrixFactorization


# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

SPLIT_DIR = (
    BASE_DIR
    / "data"
    / "features"
    / "collaborative"
    / "splits"
)

MODEL_DIR = (
    BASE_DIR
    / "models"
    / "collaborative"
)

MODEL_PATH = (
    MODEL_DIR
    / "matrix_factorization_best.pt"
)

BATCH_SIZE = 65536

MIN_RATING = 0.5
MAX_RATING = 5.0


device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# DATASET
# ============================================================

class CollaborativeDataset(Dataset):

    def __init__(
        self,
        users,
        movies,
        ratings
    ):
        self.users = users
        self.movies = movies
        self.ratings = ratings

    def __len__(self):
        return len(self.ratings)

    def __getitem__(self, index):

        return (
            int(self.users[index]),
            int(self.movies[index]),
            np.float32(self.ratings[index])
        )


# ============================================================
# LOAD CHECKPOINT
# ============================================================

print("=" * 70)
print("FINAL COLLABORATIVE FILTERING EVALUATION")
print("=" * 70)

print("Device:", device)

if torch.cuda.is_available():
    print(
        "GPU:",
        torch.cuda.get_device_name(0)
    )


checkpoint = torch.load(
    MODEL_PATH,
    map_location=device,
    weights_only=False
)


print("\nBest model checkpoint:")
print(
    "Epoch              :",
    checkpoint["epoch"]
)

print(
    "Validation RMSE    :",
    f"{checkpoint['validation_rmse']:.4f}"
)

print(
    "Embedding dimension:",
    checkpoint["embedding_dim"]
)


# ============================================================
# RECREATE MODEL
# ============================================================

model = MatrixFactorization(
    num_users=checkpoint["num_users"],
    num_movies=checkpoint["num_movies"],
    embedding_dim=checkpoint["embedding_dim"],
    global_mean=checkpoint["global_mean"]
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model = model.to(device)

model.eval()


# ============================================================
# LOAD TEST DATA
# ============================================================

test_users = np.load(
    SPLIT_DIR / "test_users.npy",
    mmap_mode="r"
)

test_movies = np.load(
    SPLIT_DIR / "test_movies.npy",
    mmap_mode="r"
)

test_ratings = np.load(
    SPLIT_DIR / "test_ratings.npy",
    mmap_mode="r"
)


print(
    "\nTotal test interactions:",
    f"{len(test_ratings):,}"
)


# ============================================================
# REMOVE COLD-START MOVIES
# ============================================================

seen_movies = np.load(
    MODEL_DIR
    / "cf_seen_movie_indexes.npy"
)


seen_movie_mask = np.zeros(
    checkpoint["num_movies"],
    dtype=bool
)

seen_movie_mask[seen_movies] = True


test_mask = seen_movie_mask[
    test_movies
]


filtered_users = test_users[
    test_mask
]

filtered_movies = test_movies[
    test_mask
]

filtered_ratings = test_ratings[
    test_mask
]


excluded = (
    len(test_ratings)
    - len(filtered_ratings)
)


print(
    "Evaluated interactions:",
    f"{len(filtered_ratings):,}"
)

print(
    "Cold-start excluded:",
    f"{excluded:,}"
)

print(
    "Cold-start percentage:",
    f"{excluded / len(test_ratings) * 100:.4f}%"
)


# ============================================================
# DATALOADER
# ============================================================

test_dataset = CollaborativeDataset(
    filtered_users,
    filtered_movies,
    filtered_ratings
)

test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
    pin_memory=True
)


# ============================================================
# EVALUATE
# ============================================================

squared_error_sum = 0.0
absolute_error_sum = 0.0
total_examples = 0


with torch.no_grad():

    for users, movies, ratings in test_loader:

        users = users.to(
            device,
            dtype=torch.long,
            non_blocking=True
        )

        movies = movies.to(
            device,
            dtype=torch.long,
            non_blocking=True
        )

        ratings = ratings.to(
            device,
            dtype=torch.float32,
            non_blocking=True
        )


        predictions = model(
            users,
            movies
        )


        predictions = torch.clamp(
            predictions,
            MIN_RATING,
            MAX_RATING
        )


        errors = (
            predictions
            - ratings
        )


        squared_error_sum += (
            torch.sum(
                errors ** 2
            ).item()
        )


        absolute_error_sum += (
            torch.sum(
                torch.abs(errors)
            ).item()
        )


        total_examples += (
            ratings.size(0)
        )


# ============================================================
# FINAL METRICS
# ============================================================

test_rmse = (
    squared_error_sum
    / total_examples
) ** 0.5


test_mae = (
    absolute_error_sum
    / total_examples
)


print("\n" + "=" * 70)
print("FINAL TEST RESULTS")
print("=" * 70)

print(
    "Test RMSE:",
    f"{test_rmse:.4f}"
)

print(
    "Test MAE :",
    f"{test_mae:.4f}"
)

print(
    "Ratings evaluated:",
    f"{total_examples:,}"
)