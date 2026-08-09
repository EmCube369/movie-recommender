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
	
	
	public Movie addMovie(Movie movie) {
		return movieRepository.save(movie);
	}
	
	
	public Movie updateMovie(Integer id, Movie updatedMovie) {
		
		Movie existingMovie = movieRepository.findById(id)
				.orElseThrow(() -> new MovieNotFoundException(
				"Movie with id " + id + " not found"));
		
		
			
		existingMovie.setTitle(updatedMovie.getTitle());
		existingMovie.setGenre(updatedMovie.getGenre());
		existingMovie.setReleaseYear(updatedMovie.getReleaseYear());
		existingMovie.setImdbRating(updatedMovie.getImdbRating());
			
		return movieRepository.save(existingMovie);			
	
	}
	
	public void deleteMovie(Integer id) {
		
		if(!movieRepository.existsById(id)) {
			throw new MovieNotFoundException(
					"Movie with id " + id + " not found"
			);
		}
		
		
		movieRepository.deleteById(id);
	}

}
