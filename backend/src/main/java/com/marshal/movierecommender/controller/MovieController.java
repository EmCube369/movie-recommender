package com.marshal.movierecommender.controller;

import java.util.List;


import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.marshal.movierecommender.entity.Movie;
import com.marshal.movierecommender.service.MovieService;


@RestController
@RequestMapping("/movies")
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
	
}
