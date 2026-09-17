package com.marshal.movierecommender.admin.dto;

import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;

public record AdminAddMovieRequest(

        @NotNull(message = "ML movie ID is required")
        @Positive(message = "ML movie ID must be greater than 0")
        Integer mlMovieId

) {
}