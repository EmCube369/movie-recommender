package com.marshal.movierecommender.exception;

public class MovieAlreadyInCatalogException extends RuntimeException {

    public MovieAlreadyInCatalogException(String message) {
        super(message);
    }
}