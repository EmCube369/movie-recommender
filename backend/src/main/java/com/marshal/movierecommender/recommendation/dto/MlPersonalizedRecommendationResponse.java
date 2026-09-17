package com.marshal.movierecommender.recommendation.dto;

import java.util.List;

public record MlPersonalizedRecommendationResponse(
        String schemaVersion,
        Integer count,
        List<MlRecommendedMovie> recommendations
) {
}