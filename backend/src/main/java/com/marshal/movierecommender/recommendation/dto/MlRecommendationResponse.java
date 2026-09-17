package com.marshal.movierecommender.recommendation.dto;

import java.util.List;

public record MlRecommendationResponse(
        String schemaVersion,
        Integer mlUserId,
        Integer count,
        List<MlRecommendedMovie> recommendations
) {
}