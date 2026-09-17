package com.marshal.movierecommender.recommendation.service;

import java.util.List;

import org.springframework.stereotype.Service;

import com.marshal.movierecommender.recommendation.client.MlRecommendationClient;
import com.marshal.movierecommender.recommendation.dto.MlRecommendationResponse;
import com.marshal.movierecommender.recommendation.dto.MlRecommendedMovie;
import com.marshal.movierecommender.recommendation.dto.RecommendationResponse;
import com.marshal.movierecommender.recommendation.dto.RecommendedMovie;
import com.marshal.movierecommender.recommendation.exception.InvalidRecommendationRequestException;
import com.marshal.movierecommender.entity.User;
import com.marshal.movierecommender.entity.UserMovieActivity;
import com.marshal.movierecommender.repository.UserMovieActivityRepository;
import com.marshal.movierecommender.repository.UserRepository;
import com.marshal.movierecommender.recommendation.dto.MlPersonalizedRecommendationRequest;
import com.marshal.movierecommender.recommendation.dto.MlPersonalizedRecommendationResponse;
import com.marshal.movierecommender.recommendation.dto.MlUserRating;
import com.marshal.movierecommender.entity.Movie;
import com.marshal.movierecommender.repository.MovieRepository;

@Service
public class RecommendationService {

	private final MlRecommendationClient mlRecommendationClient;
	private final UserRepository userRepository;
	private final UserMovieActivityRepository userMovieActivityRepository;
	private final MovieRepository movieRepository;
	private static final double POSITIVE_RATING_THRESHOLD = 4.0;


	public RecommendationService(
	        MlRecommendationClient mlRecommendationClient,
	        UserRepository userRepository,
	        UserMovieActivityRepository userMovieActivityRepository,
	        MovieRepository movieRepository
	) {
	    this.mlRecommendationClient = mlRecommendationClient;
	    this.userRepository = userRepository;
	    this.userMovieActivityRepository = userMovieActivityRepository;
	    this.movieRepository = movieRepository;
	}


    public RecommendationResponse getRecommendations(
            Integer mlUserId,
            Integer limit
    ) {

        if (mlUserId == null || mlUserId <= 0) {
            throw new InvalidRecommendationRequestException(
                    "userId must be greater than 0."
            );
        }

        int effectiveLimit =
                limit == null ? 10 : limit;

        if (effectiveLimit < 1 || effectiveLimit > 50) {
            throw new InvalidRecommendationRequestException(
                    "limit must be between 1 and 50."
            );
        }


        MlRecommendationResponse mlResponse =
                mlRecommendationClient.getRecommendations(
                        mlUserId,
                        effectiveLimit
                );


        List<RecommendedMovie> recommendations =
                mlResponse.recommendations()
                        .stream()
                        .map(this::toRecommendedMovie)
                        .toList();


        return new RecommendationResponse(
                mlResponse.mlUserId(),
                recommendations.size(),
                recommendations
        );
    }

    
    public RecommendationResponse getPersonalizedRecommendations(
            String username,
            Integer limit
    ) {

        if (username == null || username.isBlank()) {
            throw new InvalidRecommendationRequestException(
                    "Authenticated username is required."
            );
        }

        int effectiveLimit =
                limit == null ? 10 : limit;

        if (effectiveLimit < 1 || effectiveLimit > 50) {
            throw new InvalidRecommendationRequestException(
                    "limit must be between 1 and 50."
            );
        }

        User user =
                userRepository
                        .findByUsername(username)
                        .orElseThrow(() ->
                                new InvalidRecommendationRequestException(
                                        "Authenticated user was not found."
                                )
                        );

        List<UserMovieActivity> activities =
                userMovieActivityRepository
                        .findRatedActivitiesWithMovie(
                                user.getId()
                        );

        List<MlUserRating> ratings =
                activities
                        .stream()
                        .filter(activity ->
                                activity
                                        .getMovie()
                                        .getMlMovieId() != null
                        )
                        .map(activity ->
                                new MlUserRating(
                                        activity
                                                .getMovie()
                                                .getMlMovieId(),
                                        activity.getRating()
                                )
                        )
                        .toList();

        if (ratings.isEmpty()) {
            throw new InvalidRecommendationRequestException(
                    "Rate at least one ML-supported movie before requesting recommendations."
            );
        }
        
        boolean hasPositiveRating =
                ratings
                        .stream()
                        .anyMatch(rating ->
                                rating.rating() >= POSITIVE_RATING_THRESHOLD
                        );

        if (!hasPositiveRating) {
            throw new InvalidRecommendationRequestException(
                    "Rate at least one ML-supported movie 4 stars or higher before requesting recommendations."
            );
        }

        MlPersonalizedRecommendationRequest request =
                new MlPersonalizedRecommendationRequest(
                        ratings,
                        effectiveLimit
                );

        MlPersonalizedRecommendationResponse mlResponse =
                mlRecommendationClient
                        .getPersonalizedRecommendations(
                                request
                        );

        List<RecommendedMovie> recommendations =
                mlResponse
                        .recommendations()
                        .stream()
                        .map(this::toRecommendedMovie)
                        .toList();

        return new RecommendationResponse(
                user.getId(),
                recommendations.size(),
                recommendations
        );
    }
    
    
    private RecommendedMovie toRecommendedMovie(
            MlRecommendedMovie movie
    ) {

        Integer mlMovieId =
                movie.movieId();

        Integer websiteMovieId =
                movieRepository
                        .findByMlMovieId(mlMovieId)
                        .map(Movie::getId)
                        .orElse(null);

        return new RecommendedMovie(
                movie.rank(),
                websiteMovieId,
                mlMovieId,
                movie.title(),
                movie.releaseYear(),
                movie.genres(),
                movie.score()
        );
    }
}