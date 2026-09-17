package com.marshal.movierecommender.recommendation.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.security.core.Authentication;

import com.marshal.movierecommender.recommendation.dto.RecommendationResponse;
import com.marshal.movierecommender.recommendation.service.RecommendationService;

@RestController
@RequestMapping("/api/recommendations")
public class RecommendationController {

	private final RecommendationService recommendationService;
	
	
	public RecommendationController(
			RecommendationService recommendationService
	) {
		this.recommendationService = recommendationService;
	}
	
	
	@GetMapping("/users/{userId}")
	public ResponseEntity<RecommendationResponse> getRecommendations(
			@PathVariable Integer userId,
			@RequestParam(defaultValue = "10") Integer limit
	) {
		RecommendationResponse response =
				recommendationService.getRecommendations( userId, limit);
		
		return ResponseEntity.ok(response);
	}
	
	@GetMapping("/me")
	public ResponseEntity<RecommendationResponse> getMyRecommendations(
	        Authentication authentication,
	        @RequestParam(defaultValue = "10") Integer limit
	) {

	    RecommendationResponse response =
	            recommendationService
	                    .getPersonalizedRecommendations(
	                            authentication.getName(),
	                            limit
	                    );

	    return ResponseEntity.ok(response);
	}
}
