package com.marshal.movierecommender.dto;

public class UserMovieActivityResponse {

    private Integer movieId;
    private boolean watched;
    private Double rating;

    public UserMovieActivityResponse() {
    }

    public UserMovieActivityResponse(
            Integer movieId,
            boolean watched,
            Double rating) {

        this.movieId = movieId;
        this.watched = watched;
        this.rating = rating;
    }

    public Integer getMovieId() {
        return movieId;
    }

    public void setMovieId(Integer movieId) {
        this.movieId = movieId;
    }

    public boolean isWatched() {
        return watched;
    }

    public void setWatched(boolean watched) {
        this.watched = watched;
    }

    public Double getRating() {
        return rating;
    }

    public void setRating(Double rating) {
        this.rating = rating;
    }
}