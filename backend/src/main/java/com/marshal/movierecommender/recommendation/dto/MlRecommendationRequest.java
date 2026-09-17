package com.marshal.movierecommender.recommendation.dto;

public record MlRecommendationRequest (
		Integer mlUserId,
		Integer limit
) {
	
}

