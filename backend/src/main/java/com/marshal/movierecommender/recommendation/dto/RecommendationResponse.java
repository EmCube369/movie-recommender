package com.marshal.movierecommender.recommendation.dto;

import java.util.List;

public record RecommendationResponse (
		Integer userId,
		Integer count,
		List<RecommendedMovie> recommendations
) {

}
