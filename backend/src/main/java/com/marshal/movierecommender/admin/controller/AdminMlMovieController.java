package com.marshal.movierecommender.admin.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.marshal.movierecommender.exception.InvalidMovieCatalogRequestException;
import com.marshal.movierecommender.recommendation.client.MlRecommendationClient;
import com.marshal.movierecommender.recommendation.dto.MlMovieCatalogSearchResponse;

@RestController
@RequestMapping("/api/admin/ml-movies")
public class AdminMlMovieController {

    private final MlRecommendationClient mlRecommendationClient;

    public AdminMlMovieController(
            MlRecommendationClient mlRecommendationClient
    ) {
        this.mlRecommendationClient =
                mlRecommendationClient;
    }


    @GetMapping("/search")
    public ResponseEntity<MlMovieCatalogSearchResponse>
    searchMovies(
            @RequestParam String query,
            @RequestParam(required = false) Integer limit
    ) {

        if (query == null || query.isBlank()) {
        	throw new InvalidMovieCatalogRequestException(
        	        "Search query cannot be blank."
        	);
        }

        int effectiveLimit =
                limit == null ? 20 : limit;

        if (effectiveLimit < 1 || effectiveLimit > 50) {
        	throw new InvalidMovieCatalogRequestException(
        	        "limit must be between 1 and 50."
        	);
        }

        return ResponseEntity.ok(
                mlRecommendationClient.searchMovies(
                        query.trim(),
                        effectiveLimit
                )
        );
    }
}