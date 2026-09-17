package com.marshal.movierecommender.service;

import java.util.List;
import java.util.Optional;

import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.stereotype.Service;

import com.marshal.movierecommender.entity.Movie;
import com.marshal.movierecommender.entity.User;
import com.marshal.movierecommender.entity.UserMovieActivity;
import com.marshal.movierecommender.exception.MovieNotFoundException;
import com.marshal.movierecommender.repository.MovieRepository;
import com.marshal.movierecommender.repository.UserMovieActivityRepository;
import com.marshal.movierecommender.repository.UserRepository;

@Service
public class UserMovieActivityService {

    private final UserMovieActivityRepository activityRepository;
    private final UserRepository userRepository;
    private final MovieRepository movieRepository;

    public UserMovieActivityService(
            UserMovieActivityRepository activityRepository,
            UserRepository userRepository,
            MovieRepository movieRepository) {

        this.activityRepository = activityRepository;
        this.userRepository = userRepository;
        this.movieRepository = movieRepository;
    }

    public UserMovieActivity markWatched(
            String username,
            Integer movieId) {

        User user = getUser(username);
        Movie movie = getMovie(movieId);

        Optional<UserMovieActivity> existingActivity =
                activityRepository.findByUserIdAndMovieId(
                        user.getId(),
                        movieId);

        if (existingActivity.isPresent()) {
            return existingActivity.get();
        }

        UserMovieActivity activity =
                new UserMovieActivity();

        activity.setUser(user);
        activity.setMovie(movie);
        activity.setRating(null);

        return activityRepository.save(activity);
    }

    public UserMovieActivity rateMovie(
            String username,
            Integer movieId,
            Double rating) {

        if (rating == null || rating < 1.0 || rating > 5.0) {
            throw new IllegalArgumentException(
                    "Rating must be between 1 and 5");
        }

        User user = getUser(username);
        Movie movie = getMovie(movieId);

        UserMovieActivity activity =
                activityRepository
                    .findByUserIdAndMovieId(
                        user.getId(),
                        movieId)
                    .orElseGet(() -> {
                        UserMovieActivity newActivity =
                                new UserMovieActivity();

                        newActivity.setUser(user);
                        newActivity.setMovie(movie);

                        return newActivity;
                    });

        activity.setRating(rating);

        return activityRepository.save(activity);
    }

    public Optional<UserMovieActivity> getActivity(
            String username,
            Integer movieId) {

        User user = getUser(username);

        // Validate that the movie actually exists
        getMovie(movieId);

        return activityRepository.findByUserIdAndMovieId(
                user.getId(),
                movieId);
    }
    
    public List<UserMovieActivity> getUserLibrary(
            String username) {

        User user = getUser(username);

        return activityRepository.findByUserId(
                user.getId());
    }

    private User getUser(String username) {

        return userRepository
                .findByUsername(username)
                .orElseThrow(() ->
                        new UsernameNotFoundException(
                                "User not found: " + username));
    }

    private Movie getMovie(Integer movieId) {

        return movieRepository
                .findById(movieId)
                .orElseThrow(() ->
                        new MovieNotFoundException(
                                "Movie not found with id: "
                                + movieId));
    }
    
    public boolean removeActivity(
            String username,
            Integer movieId) {

        User user = getUser(username);

        Optional<UserMovieActivity> activity =
                activityRepository.findByUserIdAndMovieId(
                        user.getId(),
                        movieId);

        if (activity.isEmpty()) {
            return false;
        }

        activityRepository.delete(activity.get());

        return true;
    }
}