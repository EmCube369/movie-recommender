package com.marshal.movierecommender.recommendation.exception;

public class MlMovieNotFoundException extends RuntimeException {

    public MlMovieNotFoundException(String message) {
        super(message);
    }
}