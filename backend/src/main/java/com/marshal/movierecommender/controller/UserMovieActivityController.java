package com.marshal.movierecommender.controller;

import java.security.Principal;
import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.marshal.movierecommender.dto.RatingRequest;
import com.marshal.movierecommender.dto.UserLibraryMovieResponse;
import com.marshal.movierecommender.dto.UserMovieActivityResponse;
import com.marshal.movierecommender.entity.UserMovieActivity;
import com.marshal.movierecommender.service.UserMovieActivityService;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/user-movies")
public class UserMovieActivityController {

    private final UserMovieActivityService activityService;

    public UserMovieActivityController(
            UserMovieActivityService activityService) {

        this.activityService = activityService;
    }

    @PostMapping("/{movieId}/watched")
    public ResponseEntity<UserMovieActivityResponse> markWatched(
            @PathVariable Integer movieId,
            Principal principal) {

        UserMovieActivity activity =
                activityService.markWatched(
                        principal.getName(),
                        movieId);

        return ResponseEntity.ok(
                toResponse(activity));
    }

    @PutMapping("/{movieId}/rating")
    public ResponseEntity<UserMovieActivityResponse> rateMovie(
            @PathVariable Integer movieId,
            @Valid @RequestBody RatingRequest request,
            Principal principal) {

        UserMovieActivity activity =
                activityService.rateMovie(
                        principal.getName(),
                        movieId,
                        request.getRating());

        return ResponseEntity.ok(
                toResponse(activity));
    }

    @GetMapping("/{movieId}")
    public ResponseEntity<UserMovieActivityResponse> getActivity(
            @PathVariable Integer movieId,
            Principal principal) {

        return activityService
                .getActivity(
                        principal.getName(),
                        movieId)
                .map(activity ->
                        ResponseEntity.ok(
                                toResponse(activity)))
                .orElseGet(() ->
                        ResponseEntity.ok(
                                new UserMovieActivityResponse(
                                        movieId,
                                        false,
                                        null)));
    }

    private UserMovieActivityResponse toResponse(
            UserMovieActivity activity) {

        return new UserMovieActivityResponse(
                activity.getMovie().getId(),
                true,
                activity.getRating());
    }
    
    @GetMapping
    public ResponseEntity<List<UserLibraryMovieResponse>> getLibrary(
            Principal principal) {

        List<UserLibraryMovieResponse> library =
                activityService
                    .getUserLibrary(principal.getName())
                    .stream()
                    .map(this::toLibraryResponse)
                    .toList();

        return ResponseEntity.ok(library);
    }
    
    private UserLibraryMovieResponse toLibraryResponse(
            UserMovieActivity activity) {

        return new UserLibraryMovieResponse(
                activity.getMovie().getId(),
                activity.getMovie().getTitle(),
                activity.getMovie().getGenre(),
                activity.getMovie().getReleaseYear(),
                activity.getMovie().getTmdbRating(),
                activity.getRating());
    }
    
    @DeleteMapping("/{movieId}")
    public ResponseEntity<Void> removeActivity(
            @PathVariable Integer movieId,
            Principal principal) {

        boolean removed =
                activityService.removeActivity(
                        principal.getName(),
                        movieId);

        if (!removed) {
            return ResponseEntity.notFound().build();
        }

        return ResponseEntity.noContent().build();
    }
}