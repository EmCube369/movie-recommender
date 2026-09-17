import torch
import torch.nn as nn


class MatrixFactorization(nn.Module):

    def __init__(
        self,
        num_users,
        num_movies,
        embedding_dim=64,
        global_mean=0.0
    ):
        super().__init__()

        # -----------------------------------------------------
        # LATENT EMBEDDINGS
        # -----------------------------------------------------

        self.user_embedding = nn.Embedding(
            num_users,
            embedding_dim
        )

        self.movie_embedding = nn.Embedding(
            num_movies,
            embedding_dim
        )

        # -----------------------------------------------------
        # USER / MOVIE BIASES
        # -----------------------------------------------------

        self.user_bias = nn.Embedding(
            num_users,
            1
        )

        self.movie_bias = nn.Embedding(
            num_movies,
            1
        )

        # -----------------------------------------------------
        # GLOBAL MEAN
        # -----------------------------------------------------

        self.register_buffer(
            "global_mean",
            torch.tensor(
                global_mean,
                dtype=torch.float32
            )
        )

        # -----------------------------------------------------
        # INITIALIZATION
        # -----------------------------------------------------

        nn.init.normal_(
            self.user_embedding.weight,
            mean=0.0,
            std=0.01
        )

        nn.init.normal_(
            self.movie_embedding.weight,
            mean=0.0,
            std=0.01
        )

        nn.init.zeros_(
            self.user_bias.weight
        )

        nn.init.zeros_(
            self.movie_bias.weight
        )


    def forward(self, users, movies):

        # User latent vectors
        user_vectors = self.user_embedding(users)

        # Movie latent vectors
        movie_vectors = self.movie_embedding(movies)

        # Dot product between user and movie vectors
        interaction = (
            user_vectors * movie_vectors
        ).sum(dim=1)

        # Bias terms
        user_bias = (
            self.user_bias(users)
            .squeeze(1)
        )

        movie_bias = (
            self.movie_bias(movies)
            .squeeze(1)
        )

        # Final predicted rating
        prediction = (
            self.global_mean
            + user_bias
            + movie_bias
            + interaction
        )

        return prediction