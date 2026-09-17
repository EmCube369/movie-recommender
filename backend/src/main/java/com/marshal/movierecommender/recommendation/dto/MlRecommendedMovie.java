package com.marshal.movierecommender.recommendation.dto;

import java.util.List;

public record MlRecommendedMovie(
        Integer rank,
        Integer movieId,
        String title,
        Integer releaseYear,
        List<String> genres,
        Double score,
        Double cfScore,
        Double contentScore,
        Double sentimentScore,
        Boolean sentimentAvailable
) {
}