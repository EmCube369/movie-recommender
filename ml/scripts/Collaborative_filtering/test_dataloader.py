import numpy as np
import torch
from pathlib import Path
from torch.utils.data import Dataset, DataLoader


BASE_DIR = Path(__file__).resolve().parents[2]
SPLIT_DIR = (
    BASE_DIR
    / "data"
    / "features"
    / "collaborative"
    / "splits"
)

device = torch.device(
    "cuda" if torch.cuda.is_available() else "cpu"
)


# ============================================================
# LOAD MEMORY-MAPPED ARRAYS
# ============================================================

train_users = np.load(
    SPLIT_DIR / "train_users.npy",
    mmap_mode="r"
)

train_movies = np.load(
    SPLIT_DIR / "train_movies.npy",
    mmap_mode="r"
)

train_ratings = np.load(
    SPLIT_DIR / "train_ratings.npy",
    mmap_mode="r"
)


print("=" * 70)
print("TRAIN ARRAYS")
print("=" * 70)

print("Users   :", train_users.shape, train_users.dtype)
print("Movies  :", train_movies.shape, train_movies.dtype)
print("Ratings :", train_ratings.shape, train_ratings.dtype)


# ============================================================
# DATASET
# ============================================================

class CollaborativeDataset(Dataset):

    def __init__(self, users, movies, ratings):
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


train_dataset = CollaborativeDataset(
    train_users,
    train_movies,
    train_ratings
)


# ============================================================
# DATALOADER
# ============================================================

BATCH_SIZE = 65536

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0,
    pin_memory=True
)


print("\n" + "=" * 70)
print("DATALOADER")
print("=" * 70)

print("Dataset size :", f"{len(train_dataset):,}")
print("Batch size   :", f"{BATCH_SIZE:,}")
print("Batches      :", f"{len(train_loader):,}")


# ============================================================
# GET ONE BATCH
# ============================================================

users, movies, ratings = next(iter(train_loader))

print("\nCPU batch:")
print("Users   :", users.shape, users.dtype, users.device)
print("Movies  :", movies.shape, movies.dtype, movies.device)
print("Ratings :", ratings.shape, ratings.dtype, ratings.device)


# ============================================================
# SEND BATCH TO GPU
# ============================================================

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


print("\n" + "=" * 70)
print("GPU BATCH")
print("=" * 70)

print("Users   :", users.shape, users.dtype, users.device)
print("Movies  :", movies.shape, movies.dtype, movies.device)
print("Ratings :", ratings.shape, ratings.dtype, ratings.device)