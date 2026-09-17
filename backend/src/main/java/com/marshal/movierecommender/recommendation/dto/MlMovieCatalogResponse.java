package com.marshal.movierecommender.recommendation.dto;

import java.util.List;

public record MlMovieCatalogResponse(
        Integer movieId,
        String title,
        Integer releaseYear,
        List<String> genres,
        Double tmdbRating,
        Integer tmdbVoteCount,
        Boolean recommendationSupported
) {
}