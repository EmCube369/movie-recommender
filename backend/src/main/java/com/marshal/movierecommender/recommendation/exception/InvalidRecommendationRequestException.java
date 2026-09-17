package com.marshal.movierecommender.recommendation.exception;

public class InvalidRecommendationRequestException extends RuntimeException {

	public InvalidRecommendationRequestException(String message) {
		super(message);
	}
}
