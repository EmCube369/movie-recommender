package com.marshal.movierecommender.admin.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.marshal.movierecommender.entity.Movie;
import com.marshal.movierecommender.exception.MovieAlreadyInCatalogException;
import com.marshal.movierecommender.exception.MovieInUseException;
import com.marshal.movierecommender.exception.MovieNotFoundException;
import com.marshal.movierecommender.exception.UnsupportedMlMovieException;
import com.marshal.movierecommender.recommendation.client.MlRecommendationClient;
import com.marshal.movierecommender.recommendation.dto.MlMovieCatalogResponse;
import com.marshal.movierecommender.repository.MovieRepository;
import com.marshal.movierecommender.repository.UserMovieActivityRepository;

@ExtendWith(MockitoExtension.class)
class AdminMovieServiceTest {

    @Mock
    private MovieRepository movieRepository;

    @Mock
    private MlRecommendationClient mlRecommendationClient;

    @Mock
    private UserMovieActivityRepository userMovieActivityRepository;

    @Mock
    private MlMovieCatalogResponse mlMovie;

    private AdminMovieService service;

    @BeforeEach
    void setUp() {

        service = new AdminMovieService(
                movieRepository,
                mlRecommendationClient,
                userMovieActivityRepository
        );
    }

    @Test
    void addMovie_WhenSupported_ShouldSaveMovie() {

        when(movieRepository.existsByMlMovieId(58559))
                .thenReturn(false);

        when(mlRecommendationClient.getMovie(58559))
                .thenReturn(mlMovie);

        when(mlMovie.movieId())
                .thenReturn(58559);

        when(mlMovie.title())
                .thenReturn("The Dark Knight");

        when(mlMovie.releaseYear())
                .thenReturn(2008);

        when(mlMovie.genres())
                .thenReturn(
                        List.of(
                                "Action",
                                "Crime",
                                "Thriller"
                        )
                );

        when(mlMovie.recommendationSupported())
                .thenReturn(true);

        when(movieRepository.save(any(Movie.class)))
                .thenAnswer(invocation ->
                        invocation.getArgument(0)
                );

        Movie result =
                service.addMovie(58559);

        assertEquals(
                58559,
                result.getMlMovieId()
        );

        assertEquals(
                "The Dark Knight",
                result.getTitle()
        );

        assertEquals(
                2008,
                result.getReleaseYear()
        );

        assertEquals(
                "Action, Crime, Thriller",
                result.getGenre()
        );

        verify(movieRepository)
                .save(any(Movie.class));
    }

    @Test
    void addMovie_WhenAlreadyInCatalog_ShouldThrowException() {

        when(movieRepository.existsByMlMovieId(58559))
                .thenReturn(true);

        assertThrows(
                MovieAlreadyInCatalogException.class,
                () -> service.addMovie(58559)
        );

        verify(
                mlRecommendationClient,
                never()
        ).getMovie(58559);

        verify(
                movieRepository,
                never()
        ).save(any());
    }

    @Test
    void addMovie_WhenNotRecommendationSupported_ShouldThrowException() {

        when(movieRepository.existsByMlMovieId(58559))
                .thenReturn(false);

        when(mlRecommendationClient.getMovie(58559))
                .thenReturn(mlMovie);

        when(mlMovie.recommendationSupported())
                .thenReturn(false);

        assertThrows(
                UnsupportedMlMovieException.class,
                () -> service.addMovie(58559)
        );

        verify(
                movieRepository,
                never()
        ).save(any());
    }

    @Test
    void addMovie_WhenReleaseYearMissing_ShouldThrowException() {

        when(movieRepository.existsByMlMovieId(58559))
                .thenReturn(false);

        when(mlRecommendationClient.getMovie(58559))
                .thenReturn(mlMovie);

        when(mlMovie.recommendationSupported())
                .thenReturn(true);

        when(mlMovie.releaseYear())
                .thenReturn(null);

        assertThrows(
                UnsupportedMlMovieException.class,
                () -> service.addMovie(58559)
        );

        verify(
                movieRepository,
                never()
        ).save(any());
    }

    @Test
    void addMovie_WhenGenresEmpty_ShouldUseUnknownGenre() {

        when(movieRepository.existsByMlMovieId(58559))
                .thenReturn(false);

        when(mlRecommendationClient.getMovie(58559))
                .thenReturn(mlMovie);

        when(mlMovie.movieId())
                .thenReturn(58559);

        when(mlMovie.title())
                .thenReturn("The Dark Knight");

        when(mlMovie.releaseYear())
                .thenReturn(2008);

        when(mlMovie.genres())
                .thenReturn(List.of());

        when(mlMovie.recommendationSupported())
                .thenReturn(true);

        when(movieRepository.save(any(Movie.class)))
                .thenAnswer(invocation ->
                        invocation.getArgument(0)
                );

        Movie result =
                service.addMovie(58559);

        assertEquals(
                "Unknown",
                result.getGenre()
        );
    }

    @Test
    void deleteMovie_WhenMovieExistsAndUnused_ShouldDeleteMovie() {

        Movie movie = new Movie();

        movie.setId(10);
        movie.setMlMovieId(58559);
        movie.setTitle("The Dark Knight");
        movie.setGenre("Action, Crime, Thriller");
        movie.setReleaseYear(2008);

        when(movieRepository.findById(10))
                .thenReturn(Optional.of(movie));

        when(userMovieActivityRepository
                .existsByMovieId(10))
                .thenReturn(false);

        service.deleteMovie(10);

        verify(movieRepository)
                .delete(movie);
    }

    @Test
    void deleteMovie_WhenMovieHasUserActivity_ShouldThrowException() {

        Movie movie = new Movie();
        movie.setId(10);

        when(movieRepository.findById(10))
                .thenReturn(Optional.of(movie));

        when(userMovieActivityRepository
                .existsByMovieId(10))
                .thenReturn(true);

        assertThrows(
                MovieInUseException.class,
                () -> service.deleteMovie(10)
        );

        verify(
                movieRepository,
                never()
        ).delete(any());
    }

    @Test
    void deleteMovie_WhenMovieDoesNotExist_ShouldThrowException() {

        when(movieRepository.findById(999))
                .thenReturn(Optional.empty());

        assertThrows(
                MovieNotFoundException.class,
                () -> service.deleteMovie(999)
        );

        verify(
                userMovieActivityRepository,
                never()
        ).existsByMovieId(999);

        verify(
                movieRepository,
                never()
        ).delete(any());
    }
}