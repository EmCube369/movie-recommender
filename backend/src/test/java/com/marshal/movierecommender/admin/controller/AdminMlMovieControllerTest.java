package com.marshal.movierecommender.admin.controller;

import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.marshal.movierecommender.exception.InvalidMovieCatalogRequestException;
import com.marshal.movierecommender.recommendation.client.MlRecommendationClient;
import com.marshal.movierecommender.recommendation.dto.MlMovieCatalogSearchResponse;

@ExtendWith(MockitoExtension.class)
class AdminMlMovieControllerTest {

    @Mock
    private MlRecommendationClient mlRecommendationClient;

    @Mock
    private MlMovieCatalogSearchResponse searchResponse;

    private AdminMlMovieController controller;

    @BeforeEach
    void setUp() {

        controller =
                new AdminMlMovieController(
                        mlRecommendationClient
                );
    }

    @Test
    void searchMovies_WhenQueryIsBlank_ShouldThrowException() {

        assertThrows(
                InvalidMovieCatalogRequestException.class,
                () -> controller.searchMovies(
                        "   ",
                        10
                )
        );

        verify(
                mlRecommendationClient,
                never()
        ).searchMovies(
                org.mockito.ArgumentMatchers.anyString(),
                org.mockito.ArgumentMatchers.anyInt()
        );
    }

    @Test
    void searchMovies_WhenLimitIsBelowOne_ShouldThrowException() {

        assertThrows(
                InvalidMovieCatalogRequestException.class,
                () -> controller.searchMovies(
                        "Batman",
                        0
                )
        );

        verify(
                mlRecommendationClient,
                never()
        ).searchMovies(
                org.mockito.ArgumentMatchers.anyString(),
                org.mockito.ArgumentMatchers.anyInt()
        );
    }

    @Test
    void searchMovies_WhenLimitIsAboveFifty_ShouldThrowException() {

        assertThrows(
                InvalidMovieCatalogRequestException.class,
                () -> controller.searchMovies(
                        "Batman",
                        51
                )
        );

        verify(
                mlRecommendationClient,
                never()
        ).searchMovies(
                org.mockito.ArgumentMatchers.anyString(),
                org.mockito.ArgumentMatchers.anyInt()
        );
    }

    @Test
    void searchMovies_WhenLimitIsNull_ShouldUseDefaultTwenty() {

        when(
                mlRecommendationClient.searchMovies(
                        "Batman",
                        20
                )
        ).thenReturn(searchResponse);

        var response =
                controller.searchMovies(
                        "Batman",
                        null
                );

        assertSame(
                searchResponse,
                response.getBody()
        );

        verify(
                mlRecommendationClient
        ).searchMovies(
                "Batman",
                20
        );
    }

    @Test
    void searchMovies_WhenQueryHasSpaces_ShouldTrimQuery() {

        when(
                mlRecommendationClient.searchMovies(
                        "Batman",
                        10
                )
        ).thenReturn(searchResponse);

        var response =
                controller.searchMovies(
                        "   Batman   ",
                        10
                );

        assertSame(
                searchResponse,
                response.getBody()
        );

        verify(
                mlRecommendationClient
        ).searchMovies(
                "Batman",
                10
        );
    }

    @Test
    void searchMovies_WhenRequestIsValid_ShouldReturnClientResponse() {

        when(
                mlRecommendationClient.searchMovies(
                        "Dark Knight",
                        5
                )
        ).thenReturn(searchResponse);

        var response =
                controller.searchMovies(
                        "Dark Knight",
                        5
                );

        assertSame(
                searchResponse,
                response.getBody()
        );

        verify(
                mlRecommendationClient
        ).searchMovies(
                "Dark Knight",
                5
        );
    }
}