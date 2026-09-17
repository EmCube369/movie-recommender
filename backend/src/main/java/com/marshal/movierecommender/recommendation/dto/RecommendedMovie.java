package com.marshal.movierecommender.recommendation.dto;

import java.util.List;

public record RecommendedMovie(
        Integer rank,
        Integer movieId,
        Integer mlMovieId,
        String title,
        Integer releaseYear,
        List<String> genres,
        Double score
) {
}