import sys
from pathlib import Path

import numpy as np
import pandas as pd
import torch


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = (
    BASE_DIR
    / "data"
    / "features"
    / "collaborative"
)

SPLIT_DIR = DATA_DIR / "splits"


# Allow importing model.py
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.append(str(SCRIPT_DIR))

from model import MatrixFactorization


# ============================================================
# DEVICE
# ============================================================

device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print("=" * 70)
print("DEVICE")
print("=" * 70)

print(device)

if torch.cuda.is_available():
    print(torch.cuda.get_device_name(0))


# ============================================================
# MODEL DIMENSIONS
# ============================================================

user_mapping = pd.read_csv(
    DATA_DIR / "cf_user_mapping.csv"
)

movie_mapping = pd.read_csv(
    DATA_DIR / "cf_movie_mapping.csv"
)

num_users = len(user_mapping)
num_movies = len(movie_mapping)


print("\n" + "=" * 70)
print("MODEL DIMENSIONS")
print("=" * 70)

print("Users :", f"{num_users:,}")
print("Movies:", f"{num_movies:,}")


# ============================================================
# TRAIN GLOBAL MEAN
# ============================================================

train_ratings = np.load(
    SPLIT_DIR / "train_ratings.npy",
    mmap_mode="r"
)

global_mean = float(
    np.mean(train_ratings)
)


print("\nGlobal training mean:")
print(f"{global_mean:.4f}")


# ============================================================
# CREATE MODEL
# ============================================================

EMBEDDING_DIM = 64

model = MatrixFactorization(
    num_users=num_users,
    num_movies=num_movies,
    embedding_dim=EMBEDDING_DIM,
    global_mean=global_mean
)

model = model.to(device)


print("\n" + "=" * 70)
print("MODEL")
print("=" * 70)

print(model)


# ============================================================
# PARAMETER COUNT
# ============================================================

total_parameters = sum(
    p.numel()
    for p in model.parameters()
)

trainable_parameters = sum(
    p.numel()
    for p in model.parameters()
    if p.requires_grad
)


print("\n" + "=" * 70)
print("PARAMETERS")
print("=" * 70)

print(
    "Total parameters    :",
    f"{total_parameters:,}"
)

print(
    "Trainable parameters:",
    f"{trainable_parameters:,}"
)


# ============================================================
# TEST FORWARD PASS
# ============================================================

test_users = torch.tensor(
    [0, 1, 2, 3],
    dtype=torch.long,
    device=device
)

test_movies = torch.tensor(
    [0, 10, 20, 30],
    dtype=torch.long,
    device=device
)


with torch.no_grad():

    predictions = model(
        test_users,
        test_movies
    )


print("\n" + "=" * 70)
print("FORWARD PASS TEST")
print("=" * 70)

print("Predictions:")
print(predictions)

print()

print(
    "Shape:",
    predictions.shape
)

print(
    "Device:",
    predictions.device
)


# ============================================================
# GPU MEMORY
# ============================================================

if torch.cuda.is_available():

    print("\n" + "=" * 70)
    print("GPU MEMORY")
    print("=" * 70)

    allocated = (
        torch.cuda.memory_allocated()
        / 1024 ** 2
    )

    reserved = (
        torch.cuda.memory_reserved()
        / 1024 ** 2
    )

    print(
        f"Allocated: {allocated:.2f} MB"
    )

    print(
        f"Reserved : {reserved:.2f} MB"
    )