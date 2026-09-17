package com.marshal.movierecommender.exception;

public class MovieInUseException extends RuntimeException {

    public MovieInUseException(String message) {
        super(message);
    }
}