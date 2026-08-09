package com.marshal.movierecommender.controller;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.marshal.movierecommender.entity.Movie;
import com.marshal.movierecommender.service.MovieService;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/movies")
public class MovieController {
	
	private final MovieService movieService;
	
	public MovieController(MovieService movieService) {
		this.movieService = movieService;
	}
	
	@GetMapping
	public ResponseEntity<List<Movie>> getAllMovies() {
		return ResponseEntity.ok(movieService.getAllMovies());
	}
	
	@GetMapping("/{id}")
	public ResponseEntity<Movie> getMovieById(@PathVariable Integer id) {
		return ResponseEntity.ok(movieService.getMovieById(id));
	}
	
	@PostMapping
	public ResponseEntity<Movie> addMovie(@Valid @RequestBody Movie movie) {
		Movie savedMovie = movieService.addMovie(movie);
		
		return ResponseEntity.status(HttpStatus.CREATED).body(savedMovie);
	}
	
	@PutMapping("/{id}")
	public ResponseEntity<Movie> updateMovie(@PathVariable Integer id, @Valid @RequestBody Movie movie) {
		Movie updatedMovie = movieService.updateMovie(id, movie);
		
		return ResponseEntity.ok(updatedMovie);
	}
	
	@DeleteMapping("/{id}")
	public ResponseEntity<Void> deleteMovie(@PathVariable Integer id) {
		movieService.deleteMovie(id);
		
		return ResponseEntity.noContent().build();
	}
	
}
