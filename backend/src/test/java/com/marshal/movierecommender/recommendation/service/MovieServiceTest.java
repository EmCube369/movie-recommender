package com.marshal.movierecommender.recommendation.service;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;


import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.marshal.movierecommender.entity.Movie;
import com.marshal.movierecommender.exception.MovieNotFoundException;
import com.marshal.movierecommender.repository.MovieRepository;
import com.marshal.movierecommender.service.MovieService;

@ExtendWith(MockitoExtension.class)
class MovieServiceTest {
	
	@Mock
	private MovieRepository movieRepository;
	
	@InjectMocks
	private MovieService movieService;
	
	private Movie movie;
	
	@BeforeEach
	void setUp() {
		movie = new Movie();
		movie.setId(1);
		movie.setTitle("Inception");
		movie.setGenre("Sci-Fi");
		movie.setReleaseYear(2010);
		movie.setTmdbRating(8.8);
	}
	
	
	@Test
	void getAllMovies_ShouldReturnAllMovies() {
		
		// Arrange
		Movie movie2 = new Movie();
		movie2.setId(2);
		movie2.setTitle("Interstellar");
		movie2.setGenre("Sci-Fi");
		movie2.setReleaseYear(2014);
		movie2.setTmdbRating(8.7);
		
		List<Movie> movies = List.of(movie, movie2);
		
		when(movieRepository.findAll()).thenReturn(movies);
		
		
		// Act
	    List<Movie> result = movieService.getAllMovies();

	    // Assert
	    assertNotNull(result);
	    assertEquals(2, result.size());

	    assertEquals("Inception", result.get(0).getTitle());
	    assertEquals("Interstellar", result.get(1).getTitle());

	    verify(movieRepository, times(1)).findAll();
	}
	
	@Test
	void getMovieById_WhenMovieExists_ShouldReturnMovie() {

	    // Arrange
	    when(movieRepository.findById(1))
	            .thenReturn(Optional.of(movie));

	    // Act
	    Movie result = movieService.getMovieById(1);

	    // Assert
	    assertNotNull(result);
	    assertEquals(1, result.getId());
	    assertEquals("Inception", result.getTitle());
	    assertEquals("Sci-Fi", result.getGenre());
	    assertEquals(2010, result.getReleaseYear());
	    assertEquals(8.8, result.getTmdbRating());

	    verify(movieRepository, times(1)).findById(1);
	}
	
	@Test
	void getMovieById_WhenMovieDoesNotExist_ShouldThrowException() {

	    // Arrange
	    when(movieRepository.findById(999))
	            .thenReturn(Optional.empty());

	    // Act & Assert
	    MovieNotFoundException exception = assertThrows(
	            MovieNotFoundException.class,
	            () -> movieService.getMovieById(999)
	    );

	    assertEquals(
	            "Movie with id 999 not found",
	            exception.getMessage()
	    );

	    verify(movieRepository, times(1)).findById(999);
	}
	
//	@Test
//	void addMovie_ShouldSaveAndReturnMovie() {
//
//	    // Arrange
//	    when(movieRepository.save(movie))
//	            .thenReturn(movie);
//
//	    // Act
//	    Movie result = movieService.addMovie(movie);
//
//	    // Assert
//	    assertNotNull(result);
//	    assertEquals(1, result.getId());
//	    assertEquals("Inception", result.getTitle());
//	    assertEquals("Sci-Fi", result.getGenre());
//	    assertEquals(2010, result.getReleaseYear());
//	    assertEquals(8.8, result.getImdbRating());
//
//	    verify(movieRepository, times(1)).save(movie);
//	}
//	
//	@Test
//	void updateMovie_WhenMovieExists_ShouldUpdateAndReturnMovie() {
//
//	    // Arrange
//	    Movie updatedMovie = new Movie();
//	    updatedMovie.setTitle("Inception Updated");
//	    updatedMovie.setGenre("Sci-Fi|Thriller");
//	    updatedMovie.setReleaseYear(2010);
//	    updatedMovie.setImdbRating(9.0);
//
//	    when(movieRepository.findById(1))
//	            .thenReturn(Optional.of(movie));
//
//	    when(movieRepository.save(any(Movie.class)))
//	            .thenAnswer(invocation -> invocation.getArgument(0));
//
//	    // Act
//	    Movie result = movieService.updateMovie(1, updatedMovie);
//
//	    // Assert
//	    assertNotNull(result);
//	    assertEquals(1, result.getId());
//	    assertEquals("Inception Updated", result.getTitle());
//	    assertEquals("Sci-Fi|Thriller", result.getGenre());
//	    assertEquals(2010, result.getReleaseYear());
//	    assertEquals(9.0, result.getImdbRating());
//
//	    verify(movieRepository, times(1)).findById(1);
//	    verify(movieRepository, times(1)).save(any(Movie.class));
//	}
	
//	@Test
//	void updateMovie_WhenMovieDoesNotExist_ShouldThrowException() {
//
//	    // Arrange
//	    Movie updatedMovie = new Movie();
//	    updatedMovie.setTitle("Updated Movie");
//	    updatedMovie.setGenre("Drama");
//	    updatedMovie.setReleaseYear(2020);
//	    updatedMovie.setImdbRating(8.0);
//
//	    when(movieRepository.findById(999))
//	            .thenReturn(Optional.empty());
//
//	    // Act & Assert
//	    MovieNotFoundException exception = assertThrows(
//	            MovieNotFoundException.class,
//	            () -> movieService.updateMovie(999, updatedMovie)
//	    );
//
//	    assertEquals(
//	            "Movie with id 999 not found",
//	            exception.getMessage()
//	    );
//
//	    verify(movieRepository, times(1)).findById(999);
//
//	    verify(movieRepository, never())
//	            .save(any(Movie.class));
//	}
//	
//	@Test
//	void deleteMovie_WhenMovieExists_ShouldDeleteMovie() {
//
//	    // Arrange
//	    when(movieRepository.existsById(1))
//	            .thenReturn(true);
//
//	    // Act
//	    movieService.deleteMovie(1);
//
//	    // Assert
//	    verify(movieRepository, times(1)).existsById(1);
//	    verify(movieRepository, times(1)).deleteById(1);
//	}
//	
//	@Test
//	void deleteMovie_WhenMovieDoesNotExist_ShouldThrowException() {
//
//	    // Arrange
//	    when(movieRepository.existsById(999))
//	            .thenReturn(false);
//
//	    // Act & Assert
//	    MovieNotFoundException exception = assertThrows(
//	            MovieNotFoundException.class,
//	            () -> movieService.deleteMovie(999)
//	    );
//
//	    assertEquals(
//	            "Movie with id 999 not found",
//	            exception.getMessage()
//	    );
//
//	    verify(movieRepository, times(1)).existsById(999);
//	    verify(movieRepository, never()).deleteById(anyInt());
//	}
	
	

}
