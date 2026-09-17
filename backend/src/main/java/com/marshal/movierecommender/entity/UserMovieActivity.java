package com.marshal.movierecommender.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.DecimalMax;
import jakarta.validation.constraints.DecimalMin;


@Entity
@Table(
	name = "user_movie_activity",
	uniqueConstraints = {
		@UniqueConstraint(
			name = "uk_user_movie",
			columnNames = {"user_id", "movie_id"}
		)
	}
)
public class UserMovieActivity {

	@Id
	@GeneratedValue(strategy = GenerationType.IDENTITY)
	private Integer id;

	@ManyToOne(fetch = FetchType.LAZY, optional = false)
	@JoinColumn(name = "user_id", nullable = false)
	private User user;

	@ManyToOne(fetch = FetchType.LAZY, optional = false)
	@JoinColumn(name = "movie_id", nullable = false)
	private Movie movie;

	@DecimalMin(
		value = "1.0",
		message = "Rating must be at least 1.0"
	)
	@DecimalMax(
		value = "5.0",
		message = "Rating cannot be more than 5.0"
	)
	private Double rating;

	public UserMovieActivity() {
	}

	public UserMovieActivity(
			Integer id,
			User user,
			Movie movie,
			Double rating) {

		this.id = id;
		this.user = user;
		this.movie = movie;
		this.rating = rating;
	}

	public Integer getId() {
		return id;
	}

	public void setId(Integer id) {
		this.id = id;
	}

	public User getUser() {
		return user;
	}

	public void setUser(User user) {
		this.user = user;
	}

	public Movie getMovie() {
		return movie;
	}

	public void setMovie(Movie movie) {
		this.movie = movie;
	}

	public Double getRating() {
		return rating;
	}

	public void setRating(Double rating) {
		this.rating = rating;
	}
}