package com.marshal.movierecommender.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;

@Entity
@Table(name = "movies")
public class Movie {
	
	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Integer id;
	
	@NotBlank(message = "Title cannot be blank")
	@Size(max = 255, message = "Title cannot exceed 255 characters")
	private String title;
	
	@NotBlank(message = "genre cannot be blank")
	@Size(max = 100, message = "Title cannot exceed 100 characters")
	private String genre;
	
	@NotNull(message = "Release year cannot be null")
	@Min(value = 1888, message = "Release year must be 1888 or later")
	private Integer releaseYear;
	
	@NotNull(message = "IMDb rating cannot be null")
	@DecimalMin(value = "0.0", message = "IMDb rating cannot be less than 0")
	@DecimalMax(value = "10.0", message = "IMDb rating cannot be more than 10")
	private Double imdbRating;
	
	public Movie() {
	}
	
	public Movie(Integer id, String title, String genre, Integer releaseYear,
			 Double imdbRating) {
		this.id = id;
		this.title = title;
		this.genre = genre;
		this.releaseYear = releaseYear;
		this.imdbRating = imdbRating;
	}

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public String getTitle() {
		return title;
	}

	public void setTitle(String title) {
		this.title = title;
	}

	public String getGenre() {
		return genre;
	}

	public void setGenre(String genre) {
		this.genre = genre;
	}

	public Integer getReleaseYear() {
		return releaseYear;
	}

	public void setReleaseYear(Integer releaseYear) {
		this.releaseYear = releaseYear;
	}

	public Double getImdbRating() {
		return imdbRating;
	}

	public void setImdbRating(Double imdbRating) {
		this.imdbRating = imdbRating;
	}
	
	

}
