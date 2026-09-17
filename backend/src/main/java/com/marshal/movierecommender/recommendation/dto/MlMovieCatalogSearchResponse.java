package com.marshal.movierecommender.recommendation.dto;

import java.util.List;

public record MlMovieCatalogSearchResponse(
        Integer count,
        List<MlMovieCatalogResponse> movies
) {
}