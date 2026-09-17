package com.marshal.movierecommender.recommendation.service;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;

import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.marshal.movierecommender.recommendation.client.MlRecommendationClient;
import com.marshal.movierecommender.recommendation.dto.MlRecommendationResponse;
import com.marshal.movierecommender.recommendation.dto.MlRecommendedMovie;
import com.marshal.movierecommender.recommendation.dto.RecommendationResponse;
import com.marshal.movierecommender.recommendation.dto.RecommendedMovie;
import com.marshal.movierecommender.recommendation.exception.MlServiceException;
import com.marshal.movierecommender.recommendation.exception.MlUserNotFoundException;

import java.util.Optional;

import com.marshal.movierecommender.entity.Movie;
import com.marshal.movierecommender.repository.MovieRepository;
import com.marshal.movierecommender.repository.UserMovieActivityRepository;
import com.marshal.movierecommender.repository.UserRepository;

@ExtendWith(MockitoExtension.class)
class RecommendationServiceTest {

    @Mock
    private MlRecommendationClient mlRecommendationClient;
    
    @Mock
    private UserRepository userRepository;

    @Mock
    private UserMovieActivityRepository userMovieActivityRepository;

    @Mock
    private MovieRepository movieRepository;


    @InjectMocks
    private RecommendationService recommendationService;


    @Test
    void shouldUseDefaultLimitOfTenWhenLimitIsNull() {

        MlRecommendationResponse mlResponse =
                new MlRecommendationResponse(
                        "1.0",
                        1,
                        0,
                        List.of()
                );


        when(
                mlRecommendationClient
                        .getRecommendations(1, 10)
        ).thenReturn(mlResponse);


        RecommendationResponse response =
                recommendationService
                        .getRecommendations(1, null);


        assertNotNull(response);

        assertEquals(
                1,
                response.userId()
        );

        assertEquals(
                0,
                response.count()
        );


        verify(
                mlRecommendationClient,
                times(1)
        ).getRecommendations(1, 10);
    }
    
    @Test
    void shouldRejectNullUserId() {

        assertThrows(
                com.marshal.movierecommender.recommendation.exception
                        .InvalidRecommendationRequestException.class,
                () ->
                        recommendationService
                                .getRecommendations(null, 10)
        );


        verifyNoInteractions(
                mlRecommendationClient
        );
    }


    @Test
    void shouldRejectZeroUserId() {

        assertThrows(
                com.marshal.movierecommender.recommendation.exception
                        .InvalidRecommendationRequestException.class,
                () ->
                        recommendationService
                                .getRecommendations(0, 10)
        );


        verifyNoInteractions(
                mlRecommendationClient
        );
    }


    @Test
    void shouldRejectNegativeUserId() {

        assertThrows(
                com.marshal.movierecommender.recommendation.exception
                        .InvalidRecommendationRequestException.class,
                () ->
                        recommendationService
                                .getRecommendations(-1, 10)
        );


        verifyNoInteractions(
                mlRecommendationClient
        );
    }
    
    @Test
    void shouldRejectLimitBelowOne() {

        assertThrows(
                com.marshal.movierecommender.recommendation.exception
                        .InvalidRecommendationRequestException.class,
                () ->
                        recommendationService
                                .getRecommendations(1, 0)
        );


        verifyNoInteractions(
                mlRecommendationClient
        );
    }
    
    @Test
    void shouldAcceptMinimumLimitOfOne() {

        MlRecommendationResponse mlResponse =
                new MlRecommendationResponse(
                        "1.0",
                        1,
                        0,
                        List.of()
                );


        when(
                mlRecommendationClient
                        .getRecommendations(1, 1)
        ).thenReturn(mlResponse);


        RecommendationResponse response =
                recommendationService
                        .getRecommendations(1, 1);


        assertNotNull(response);

        verify(
                mlRecommendationClient,
                times(1)
        ).getRecommendations(1, 1);
    }


    @Test
    void shouldAcceptMaximumLimitOfFifty() {

        MlRecommendationResponse mlResponse =
                new MlRecommendationResponse(
                        "1.0",
                        1,
                        0,
                        List.of()
                );


        when(
                mlRecommendationClient
                        .getRecommendations(1, 50)
        ).thenReturn(mlResponse);


        RecommendationResponse response =
                recommendationService
                        .getRecommendations(1, 50);


        assertNotNull(response);

        verify(
                mlRecommendationClient,
                times(1)
        ).getRecommendations(1, 50);
    }
    
    @Test
    void shouldReturnEmptyRecommendationsWhenMlReturnsEmptyList() {

        MlRecommendationResponse mlResponse =
                new MlRecommendationResponse(
                        "1.0",
                        1,
                        0,
                        List.of()
                );


        when(
                mlRecommendationClient
                        .getRecommendations(1, 10)
        ).thenReturn(mlResponse);


        RecommendationResponse response =
                recommendationService
                        .getRecommendations(1, 10);


        assertNotNull(response);

        assertEquals(
                1,
                response.userId()
        );

        assertEquals(
                0,
                response.count()
        );

        assertNotNull(
                response.recommendations()
        );

        assertTrue(
                response.recommendations().isEmpty()
        );


        verify(
                mlRecommendationClient,
                times(1)
        ).getRecommendations(1, 10);
    }
    
    @Test
    void shouldCalculateCountFromActualRecommendationList() {
    	
    	when(movieRepository.findByMlMovieId(anyInt()))
        .thenReturn(Optional.empty());

        List<MlRecommendedMovie> mlMovies =
                List.of(
                        new MlRecommendedMovie(
                                1,
                                922,
                                "Sunset Boulevard",
                                1950,
                                List.of("Drama"),
                                0.806164,
                                0.784551,
                                0.844872,
                                0.787886,
                                true
                        ),

                        new MlRecommendedMovie(
                                2,
                                6001,
                                "The King of Comedy",
                                1982,
                                List.of("Drama", "Comedy"),
                                0.802498,
                                0.740118,
                                0.974292,
                                0.609582,
                                true
                        )
                );


        MlRecommendationResponse mlResponse =
                new MlRecommendationResponse(
                        "1.0",
                        1,
                        999,
                        mlMovies
                );


        when(
                mlRecommendationClient
                        .getRecommendations(1, 10)
        ).thenReturn(mlResponse);


        RecommendationResponse response =
                recommendationService
                        .getRecommendations(1, 10);


        assertEquals(
                2,
                response.count()
        );

        assertEquals(
                2,
                response.recommendations().size()
        );
    }


    @Test
    void shouldRejectLimitAboveFifty() {

        assertThrows(
                com.marshal.movierecommender.recommendation.exception
                        .InvalidRecommendationRequestException.class,
                () ->
                        recommendationService
                                .getRecommendations(1, 51)
        );


        verifyNoInteractions(
                mlRecommendationClient
        );
    }
    
    @Test
    void shouldPropagateMlServiceException() {

        MlServiceException mlException =
                new MlServiceException(
                        "ML recommendation service returned HTTP 500.",
                        new RuntimeException("ML failure")
                );


        when(
                mlRecommendationClient
                        .getRecommendations(1, 10)
        ).thenThrow(mlException);


        MlServiceException exception =
                assertThrows(
                        MlServiceException.class,
                        () ->
                                recommendationService
                                        .getRecommendations(
                                                1,
                                                10
                                        )
                );


        assertEquals(
                "ML recommendation service returned HTTP 500.",
                exception.getMessage()
        );


        verify(
                mlRecommendationClient,
                times(1)
        ).getRecommendations(1, 10);
    }
    
    @Test
    void shouldPropagateMlUserNotFoundException() {

        when(
                mlRecommendationClient
                        .getRecommendations(999999, 10)
        ).thenThrow(
                new MlUserNotFoundException(
                        "ML user 999999 was not found."
                )
        );


        MlUserNotFoundException exception =
                assertThrows(
                        MlUserNotFoundException.class,
                        () ->
                                recommendationService
                                        .getRecommendations(
                                                999999,
                                                10
                                        )
                );


        assertEquals(
                "ML user 999999 was not found.",
                exception.getMessage()
        );


        verify(
                mlRecommendationClient,
                times(1)
        ).getRecommendations(999999, 10);
    }
    
    @Test
    void shouldConvertMlResponseToPublicRecommendationResponse() {
    	
    	Movie sunsetBoulevard = new Movie();
    	sunsetBoulevard.setId(101);
    	sunsetBoulevard.setMlMovieId(922);

    	Movie kingOfComedy = new Movie();
    	kingOfComedy.setId(102);
    	kingOfComedy.setMlMovieId(6001);

    	when(movieRepository.findByMlMovieId(922))
    	        .thenReturn(Optional.of(sunsetBoulevard));

    	when(movieRepository.findByMlMovieId(6001))
    	        .thenReturn(Optional.of(kingOfComedy));

        List<MlRecommendedMovie> mlMovies = List.of(

                new MlRecommendedMovie(
                        1,
                        922,
                        "Sunset Boulevard",
                        1950,
                        List.of("Drama"),
                        0.806164,
                        0.784551,
                        0.844872,
                        0.787886,
                        true
                ),

                new MlRecommendedMovie(
                        2,
                        6001,
                        "The King of Comedy",
                        1982,
                        List.of("Drama", "Comedy"),
                        0.802498,
                        0.740118,
                        0.974292,
                        0.609582,
                        true
                )
        );


        MlRecommendationResponse mlResponse =
                new MlRecommendationResponse(
                        "1.0",
                        1,
                        2,
                        mlMovies
                );


        when(
                mlRecommendationClient.getRecommendations(1, 2)
        ).thenReturn(mlResponse);


        RecommendationResponse response =
                recommendationService.getRecommendations(1, 2);


        assertNotNull(response);

        assertEquals(1, response.userId());
        assertEquals(2, response.count());

        assertNotNull(response.recommendations());
        assertEquals(2, response.recommendations().size());


        RecommendedMovie first =
                response.recommendations().get(0);

        assertEquals(1, first.rank());
        assertEquals(101, first.movieId());
        assertEquals(922, first.mlMovieId());
        assertEquals(
                "Sunset Boulevard",
                first.title()
        );
        assertEquals(1950, first.releaseYear());
        assertEquals(
                List.of("Drama"),
                first.genres()
        );
        assertEquals(
                0.806164,
                first.score(),
                0.000001
        );


        RecommendedMovie second =
                response.recommendations().get(1);

        assertEquals(2, second.rank());
        assertEquals(102, second.movieId());
        assertEquals(6001, second.mlMovieId());
        assertEquals(
                "The King of Comedy",
                second.title()
        );


        verify(
                mlRecommendationClient,
                times(1)
        ).getRecommendations(1, 2);


        verifyNoMoreInteractions(
                mlRecommendationClient
        );


        System.out.println();
        System.out.println(
                "=============================================="
        );
        System.out.println(
                "RECOMMENDATION SERVICE TEST"
        );
        System.out.println(
                "=============================================="
        );

        System.out.println(
                "User ID : " + response.userId()
        );

        System.out.println(
                "Count   : " + response.count()
        );

        System.out.println();
        System.out.println("Public recommendations:");

        for (RecommendedMovie movie
                : response.recommendations()) {

            System.out.printf(
                    "%d. %s (%s) - score=%.6f%n",
                    movie.rank(),
                    movie.title(),
                    movie.releaseYear(),
                    movie.score()
            );
        }

        System.out.println();
        System.out.println(
                "RECOMMENDATION SERVICE TEST PASSED"
        );
    }
}