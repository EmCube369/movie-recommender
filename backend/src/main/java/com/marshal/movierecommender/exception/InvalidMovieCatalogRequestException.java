package com.marshal.movierecommender.exception;

public class InvalidMovieCatalogRequestException
        extends RuntimeException {

    public InvalidMovieCatalogRequestException(
            String message
    ) {
        super(message);
    }
}