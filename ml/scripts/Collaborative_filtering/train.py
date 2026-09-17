from pathlib import Path
import json
import time

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

from model import MatrixFactorization


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = (
    BASE_DIR
    / "data"
    / "features"
    / "collaborative"
)

SPLIT_DIR = DATA_DIR / "splits"

MODEL_DIR = (
    BASE_DIR
    / "models"
    / "collaborative"
)

MODEL_DIR.mkdir(
    parents=True,
    exist_ok=True
)


BATCH_SIZE = 65536
EMBEDDING_DIM = 64

LEARNING_RATE = 0.003
WEIGHT_DECAY = 1e-5

MAX_EPOCHS = 15
PATIENCE = 3

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
# EVALUATION
# ============================================================

def evaluate(
    model,
    loader,
    device
):

    model.eval()

    squared_error_sum = 0.0
    absolute_error_sum = 0.0
    total_examples = 0

    with torch.no_grad():

        for users, movies, ratings in loader:

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

            # Ratings in MovieLens are 0.5 - 5.0
            predictions = torch.clamp(
                predictions,
                MIN_RATING,
                MAX_RATING
            )

            errors = predictions - ratings

            squared_error_sum += (
                torch.sum(errors ** 2).item()
            )

            absolute_error_sum += (
                torch.sum(torch.abs(errors)).item()
            )

            total_examples += ratings.size(0)

    rmse = (
        squared_error_sum
        / total_examples
    ) ** 0.5

    mae = (
        absolute_error_sum
        / total_examples
    )

    return rmse, mae


# ============================================================
# LOAD MAPPINGS
# ============================================================

print("=" * 70)
print("COLLABORATIVE FILTERING TRAINING")
print("=" * 70)

print("Device:", device)

if torch.cuda.is_available():

    print(
        "GPU:",
        torch.cuda.get_device_name(0)
    )


user_mapping = pd.read_csv(
    DATA_DIR / "cf_user_mapping.csv"
)

movie_mapping = pd.read_csv(
    DATA_DIR / "cf_movie_mapping.csv"
)

num_users = len(user_mapping)
num_movies = len(movie_mapping)


print("\nUsers :", f"{num_users:,}")
print("Movies:", f"{num_movies:,}")


# ============================================================
# LOAD TRAIN DATA
# ============================================================

print("\nLoading training data...")

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


# ============================================================
# DETERMINE MOVIES SEEN DURING TRAINING
# ============================================================

seen_movie_indexes = np.unique(
    train_movies
)

np.save(
    MODEL_DIR / "cf_seen_movie_indexes.npy",
    seen_movie_indexes.astype(np.int32)
)


seen_movie_mask = np.zeros(
    num_movies,
    dtype=bool
)

seen_movie_mask[
    seen_movie_indexes
] = True


print(
    "Movies seen during training:",
    f"{len(seen_movie_indexes):,}"
)

print(
    "Cold-start movies:",
    f"{num_movies - len(seen_movie_indexes):,}"
)


# ============================================================
# LOAD VALIDATION DATA
# ============================================================

validation_users = np.load(
    SPLIT_DIR / "validation_users.npy",
    mmap_mode="r"
)

validation_movies = np.load(
    SPLIT_DIR / "validation_movies.npy",
    mmap_mode="r"
)

validation_ratings = np.load(
    SPLIT_DIR / "validation_ratings.npy",
    mmap_mode="r"
)


# ============================================================
# FILTER COLD-START MOVIES FROM VALIDATION
# ============================================================

validation_mask = seen_movie_mask[
    validation_movies
]

validation_users_seen = (
    validation_users[validation_mask]
)

validation_movies_seen = (
    validation_movies[validation_mask]
)

validation_ratings_seen = (
    validation_ratings[validation_mask]
)


print(
    "\nValidation interactions:",
    f"{len(validation_ratings):,}"
)

print(
    "Validation interactions used:",
    f"{len(validation_ratings_seen):,}"
)

print(
    "Cold-start interactions excluded:",
    f"{len(validation_ratings) - len(validation_ratings_seen):,}"
)


# ============================================================
# GLOBAL TRAINING MEAN
# ============================================================

global_mean = float(
    np.mean(train_ratings)
)

print(
    "\nGlobal training mean:",
    f"{global_mean:.4f}"
)


# ============================================================
# CREATE DATASETS
# ============================================================

train_dataset = CollaborativeDataset(
    train_users,
    train_movies,
    train_ratings
)

validation_dataset = CollaborativeDataset(
    validation_users_seen,
    validation_movies_seen,
    validation_ratings_seen
)


# ============================================================
# CREATE DATALOADERS
# ============================================================

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=0,
    pin_memory=True
)

validation_loader = DataLoader(
    validation_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=0,
    pin_memory=True
)


print(
    "\nTraining batches:",
    f"{len(train_loader):,}"
)

print(
    "Validation batches:",
    f"{len(validation_loader):,}"
)


# ============================================================
# CREATE MODEL
# ============================================================

model = MatrixFactorization(
    num_users=num_users,
    num_movies=num_movies,
    embedding_dim=EMBEDDING_DIM,
    global_mean=global_mean
)

model = model.to(device)


# ============================================================
# LOSS + OPTIMIZER
# ============================================================

criterion = nn.MSELoss()

optimizer = torch.optim.Adam(
    model.parameters(),
    lr=LEARNING_RATE,
    weight_decay=WEIGHT_DECAY
)


# ============================================================
# TRAINING STATE
# ============================================================

best_validation_rmse = float("inf")

epochs_without_improvement = 0

history = []


# ============================================================
# TRAINING LOOP
# ============================================================

print("\n" + "=" * 70)
print("STARTING TRAINING")
print("=" * 70)


for epoch in range(
    1,
    MAX_EPOCHS + 1
):

    epoch_start = time.time()

    model.train()

    training_squared_error = 0.0
    training_examples = 0


    for batch_number, (
        users,
        movies,
        ratings
    ) in enumerate(
        train_loader,
        start=1
    ):

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


        # --------------------------------------------
        # FORWARD PASS
        # --------------------------------------------

        predictions = model(
            users,
            movies
        )

        loss = criterion(
            predictions,
            ratings
        )


        # --------------------------------------------
        # BACKPROPAGATION
        # --------------------------------------------

        optimizer.zero_grad(
            set_to_none=True
        )

        loss.backward()

        optimizer.step()


        # --------------------------------------------
        # TRAINING RMSE
        # --------------------------------------------

        batch_errors = (
            predictions.detach()
            - ratings
        )

        training_squared_error += (
            torch.sum(
                batch_errors ** 2
            ).item()
        )

        training_examples += (
            ratings.size(0)
        )


        # --------------------------------------------
        # PROGRESS
        # --------------------------------------------

        if (
            batch_number % 50 == 0
            or batch_number == len(train_loader)
        ):

            print(
                f"Epoch {epoch:02d} "
                f"| Batch "
                f"{batch_number:03d}/"
                f"{len(train_loader)}"
            )


    # ========================================================
    # TRAINING METRIC
    # ========================================================

    train_rmse = (
        training_squared_error
        / training_examples
    ) ** 0.5


    # ========================================================
    # VALIDATION
    # ========================================================

    validation_rmse, validation_mae = evaluate(
        model,
        validation_loader,
        device
    )


    elapsed = (
        time.time()
        - epoch_start
    )


    print(
        "\n"
        f"Epoch {epoch:02d} completed\n"
        f"Train RMSE      : {train_rmse:.4f}\n"
        f"Validation RMSE : {validation_rmse:.4f}\n"
        f"Validation MAE  : {validation_mae:.4f}\n"
        f"Time            : {elapsed:.1f} seconds"
    )


    # ========================================================
    # SAVE HISTORY
    # ========================================================

    history.append({
        "epoch": epoch,
        "train_rmse": train_rmse,
        "validation_rmse": validation_rmse,
        "validation_mae": validation_mae,
        "seconds": elapsed
    })


    # ========================================================
    # BEST MODEL CHECKPOINT
    # ========================================================

    if validation_rmse < best_validation_rmse:

        best_validation_rmse = (
            validation_rmse
        )

        epochs_without_improvement = 0


        torch.save(
            {
                "model_state_dict":
                    model.state_dict(),

                "num_users":
                    num_users,

                "num_movies":
                    num_movies,

                "embedding_dim":
                    EMBEDDING_DIM,

                "global_mean":
                    global_mean,

                "validation_rmse":
                    best_validation_rmse,

                "epoch":
                    epoch
            },

            MODEL_DIR
            / "matrix_factorization_best.pt"
        )


        print(
            "Best model saved."
        )


    else:

        epochs_without_improvement += 1

        print(
            "No validation improvement "
            f"({epochs_without_improvement}/"
            f"{PATIENCE})"
        )


    print("-" * 70)


    # ========================================================
    # EARLY STOPPING
    # ========================================================

    if (
        epochs_without_improvement
        >= PATIENCE
    ):

        print(
            "\nEarly stopping triggered."
        )

        break


# ============================================================
# SAVE TRAINING HISTORY
# ============================================================

history_df = pd.DataFrame(
    history
)

history_df.to_csv(
    MODEL_DIR
    / "training_history.csv",
    index=False
)


# ============================================================
# SAVE METADATA
# ============================================================

metadata = {

    "num_users": num_users,

    "num_movies": num_movies,

    "embedding_dim":
        EMBEDDING_DIM,

    "global_mean":
        global_mean,

    "batch_size":
        BATCH_SIZE,

    "learning_rate":
        LEARNING_RATE,

    "weight_decay":
        WEIGHT_DECAY,

    "best_validation_rmse":
        best_validation_rmse,

    "movies_seen_during_training":
        int(len(seen_movie_indexes)),

    "cold_start_movies":
        int(
            num_movies
            - len(seen_movie_indexes)
        )
}


with open(
    MODEL_DIR
    / "training_metadata.json",
    "w"
) as file:

    json.dump(
        metadata,
        file,
        indent=4
    )


print("\n" + "=" * 70)
print("TRAINING COMPLETE")
print("=" * 70)

print(
    "Best validation RMSE:",
    f"{best_validation_rmse:.4f}"
)

print(
    "Model:",
    MODEL_DIR
    / "matrix_factorization_best.pt"
)

print(
    "History:",
    MODEL_DIR
    / "training_history.csv"
)