package com.marshal.movierecommender.recommendation.dto;

import java.util.List;

public record MlPersonalizedRecommendationRequest(
        List<MlUserRating> ratings,
        Integer limit
) {
}
