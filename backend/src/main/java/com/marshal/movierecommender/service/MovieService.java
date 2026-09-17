package com.marshal.movierecommender.service;


import java.util.List;

import org.springframework.stereotype.Service;
import com.marshal.movierecommender.entity.Movie;
import com.marshal.movierecommender.exception.MovieNotFoundException;
import com.marshal.movierecommender.repository.MovieRepository;

@Service
public class MovieService {
	
	public final MovieRepository movieRepository;

	MovieService(MovieRepository movieRepository) {
		this.movieRepository = movieRepository;
	}
	
	public List<Movie> getAllMovies() {
		return movieRepository.findAll();
	}
	
	public Movie getMovieById(Integer id) {
		return movieRepository.findById(id)
				.orElseThrow(() -> new MovieNotFoundException(
						"Movie with id " + id + " not found"));
	}
	
}
