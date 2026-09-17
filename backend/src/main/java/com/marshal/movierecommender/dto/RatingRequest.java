package com.marshal.movierecommender.dto;

import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.NotNull;

public class RatingRequest {

    @NotNull(message = "Rating is required")
    @DecimalMin(
        value = "1.0",
        message = "Rating must be at least 1"
    )
    @DecimalMax(
        value = "5.0",
        message = "Rating cannot be more than 5"
    )
    private Double rating;

    public RatingRequest() {
    }

    public RatingRequest(Double rating) {
        this.rating = rating;
    }

    public Double getRating() {
        return rating;
    }

    public void setRating(Double rating) {
        this.rating = rating;
    }
}