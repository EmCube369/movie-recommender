package com.marshal.movierecommender.repository;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.boot.jdbc.test.autoconfigure.AutoConfigureTestDatabase;
import org.springframework.test.context.ActiveProfiles;

import com.marshal.movierecommender.entity.Movie;

@DataJpaTest
@ActiveProfiles("test")
@AutoConfigureTestDatabase(
        replace = AutoConfigureTestDatabase.Replace.NONE
)
class MovieRepositoryTest {

    @Autowired
    private MovieRepository movieRepository;

    @Test
    void shouldSaveMovie() {

        Movie movie = new Movie();
        movie.setTitle("Inception");
        movie.setGenre("Sci-Fi");
        movie.setReleaseYear(2010);
        movie.setTmdbRating(8.8);

        Movie savedMovie = movieRepository.saveAndFlush(movie);

        assertThat(savedMovie.getId()).isNotNull();
        assertThat(savedMovie.getTitle()).isEqualTo("Inception");
        assertThat(savedMovie.getGenre()).isEqualTo("Sci-Fi");
        assertThat(savedMovie.getReleaseYear()).isEqualTo(2010);
        assertThat(savedMovie.getTmdbRating()).isEqualTo(8.8);
    }

    @Test
    void shouldFindMovieById() {

        Movie movie = new Movie();
        movie.setTitle("Interstellar");
        movie.setGenre("Sci-Fi");
        movie.setReleaseYear(2014);
        movie.setTmdbRating(8.7);

        Movie savedMovie = movieRepository.saveAndFlush(movie);

        Optional<Movie> result =
                movieRepository.findById(savedMovie.getId());

        assertThat(result).isPresent();
        assertThat(result.get().getTitle())
                .isEqualTo("Interstellar");
        assertThat(result.get().getReleaseYear())
                .isEqualTo(2014);
    }

    @Test
    void shouldFindAllMovies() {

        Movie movie1 = new Movie();
        movie1.setTitle("The Dark Knight");
        movie1.setGenre("Action");
        movie1.setReleaseYear(2008);
        movie1.setTmdbRating(9.0);

        Movie movie2 = new Movie();
        movie2.setTitle("The Prestige");
        movie2.setGenre("Drama");
        movie2.setReleaseYear(2006);
        movie2.setTmdbRating(8.5);

        movieRepository.save(movie1);
        movieRepository.save(movie2);
        movieRepository.flush();

        List<Movie> movies = movieRepository.findAll();

        assertThat(movies).hasSize(2);

        assertThat(movies)
                .extracting(Movie::getTitle)
                .containsExactlyInAnyOrder(
                        "The Dark Knight",
                        "The Prestige"
                );
    }

    @Test
    void shouldUpdateMovie() {

        Movie movie = new Movie();
        movie.setTitle("Batman Begins");
        movie.setGenre("Action");
        movie.setReleaseYear(2005);
        movie.setTmdbRating(8.2);

        Movie savedMovie = movieRepository.saveAndFlush(movie);

        savedMovie.setTmdbRating(8.3);

        movieRepository.saveAndFlush(savedMovie);

        Optional<Movie> updatedMovie =
                movieRepository.findById(savedMovie.getId());

        assertThat(updatedMovie).isPresent();
        assertThat(updatedMovie.get().getTmdbRating())
                .isEqualTo(8.3);
    }

    @Test
    void shouldDeleteMovie() {

        Movie movie = new Movie();
        movie.setTitle("Memento");
        movie.setGenre("Thriller");
        movie.setReleaseYear(2000);
        movie.setTmdbRating(8.4);

        Movie savedMovie = movieRepository.saveAndFlush(movie);

        Integer movieId = savedMovie.getId();

        movieRepository.delete(savedMovie);
        movieRepository.flush();

        Optional<Movie> deletedMovie =
                movieRepository.findById(movieId);

        assertThat(deletedMovie).isEmpty();
    }
}