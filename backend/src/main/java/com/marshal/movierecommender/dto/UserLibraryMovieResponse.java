package com.marshal.movierecommender.dto;

public class UserLibraryMovieResponse {
	
	private Integer movieId;
	private String title;
	private String genre;
	private Integer releaseYear;
	private Double tmdbRating;
	private Double rating;
	
	public UserLibraryMovieResponse(
			Integer movieId,
			String title,
			String genre,
			Integer releaseYear,
			Double tmdbRating,
			Double rating) {

        this.movieId = movieId;
        this.title = title;
        this.genre = genre;
        this.releaseYear = releaseYear;
        this.tmdbRating = tmdbRating;
        this.rating = rating;
    }

	public Integer getMovieId() {
		return movieId;
	}

	public String getTitle() {
		return title;
	}

	public String getGenre() {
		return genre;
	}

	public Integer getReleaseYear() {
		return releaseYear;
	}

	public Double getTmdbRating() {
	    return tmdbRating;
	}

	public Double getRating() {
		return rating;
	}
	
	
	

}
