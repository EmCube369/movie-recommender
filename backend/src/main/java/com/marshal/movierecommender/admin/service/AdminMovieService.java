package com.marshal.movierecommender.admin.service;

import org.springframework.stereotype.Service;

import com.marshal.movierecommender.entity.Movie;
import com.marshal.movierecommender.exception.MovieAlreadyInCatalogException;
import com.marshal.movierecommender.exception.MovieInUseException;
import com.marshal.movierecommender.exception.MovieNotFoundException;
import com.marshal.movierecommender.exception.UnsupportedMlMovieException;
import com.marshal.movierecommender.recommendation.client.MlRecommendationClient;
import com.marshal.movierecommender.recommendation.dto.MlMovieCatalogResponse;
import com.marshal.movierecommender.repository.MovieRepository;
import com.marshal.movierecommender.repository.UserMovieActivityRepository;

@Service
public class AdminMovieService {

    private final MovieRepository movieRepository;
    private final MlRecommendationClient mlRecommendationClient;
    private final UserMovieActivityRepository userMovieActivityRepository;

    public AdminMovieService(
            MovieRepository movieRepository,
            MlRecommendationClient mlRecommendationClient,
            UserMovieActivityRepository userMovieActivityRepository
    ) {
        this.movieRepository = movieRepository;
        this.mlRecommendationClient = mlRecommendationClient;
        this.userMovieActivityRepository = userMovieActivityRepository;
    }


    public Movie addMovie(Integer mlMovieId) {

        if (movieRepository.existsByMlMovieId(mlMovieId)) {
            throw new MovieAlreadyInCatalogException(
                    "Movie with ML movie ID "
                            + mlMovieId
                            + " is already in the catalog."
            );
        }

        MlMovieCatalogResponse mlMovie =
                mlRecommendationClient.getMovie(
                        mlMovieId
                );

        if (!mlMovie.recommendationSupported()) {
            throw new UnsupportedMlMovieException(
                    "Movie with ML movie ID "
                            + mlMovieId
                            + " is not supported by the recommendation system."
            );
        }

        if (mlMovie.releaseYear() == null) {
            throw new UnsupportedMlMovieException(
                    "Movie with ML movie ID "
                            + mlMovieId
                            + " does not contain a release year."
            );
        }

        String genre =
                mlMovie.genres() == null
                || mlMovie.genres().isEmpty()
                        ? "Unknown"
                        : String.join(
                                ", ",
                                mlMovie.genres()
                        );

        Movie movie = new Movie();

        movie.setMlMovieId(
                mlMovie.movieId()
        );

        movie.setTitle(
                mlMovie.title()
        );

        movie.setGenre(
                genre
        );

        movie.setReleaseYear(
                mlMovie.releaseYear()
        );

        movie.setTmdbRating(
                mlMovie.tmdbRating()
        );

        return movieRepository.save(
                movie
        );
    }

    public void deleteMovie(Integer id) {

        Movie movie = movieRepository
                .findById(id)
                .orElseThrow(() ->
                        new MovieNotFoundException(
                                "Movie with id "
                                        + id
                                        + " not found"
                        )
                );

        if (userMovieActivityRepository.existsByMovieId(id)) {
            throw new MovieInUseException(
                    "Movie with id "
                            + id
                            + " cannot be deleted because users have activity for it."
            );
        }

        movieRepository.delete(movie);
    }
    
}