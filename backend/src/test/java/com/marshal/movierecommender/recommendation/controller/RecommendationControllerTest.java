package com.marshal.movierecommender.recommendation.controller;

import com.marshal.movierecommender.recommendation.exception.InvalidRecommendationRequestException;
import com.marshal.movierecommender.recommendation.exception.MlServiceException;
import com.marshal.movierecommender.recommendation.exception.MlServiceUnavailableException;
import com.marshal.movierecommender.recommendation.exception.MlUserNotFoundException;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.setup.MockMvcBuilders;

import com.marshal.movierecommender.exception.GlobalExceptionHandler;
import com.marshal.movierecommender.recommendation.dto.RecommendationResponse;
import com.marshal.movierecommender.recommendation.dto.RecommendedMovie;
import com.marshal.movierecommender.recommendation.service.RecommendationService;


class RecommendationControllerTest {

    private RecommendationService recommendationService;

    private MockMvc mockMvc;


    @BeforeEach
    void setUp() {

        recommendationService =
                mock(RecommendationService.class);

        RecommendationController controller =
                new RecommendationController(
                        recommendationService
                );

        mockMvc = MockMvcBuilders
                .standaloneSetup(controller)
                .setControllerAdvice(
                        new GlobalExceptionHandler()
                )
                .build();
    }
    
    @Test
    void shouldReturn400WhenUserIdIsInvalid()
            throws Exception {

        when(
                recommendationService
                        .getRecommendations(0, 10)
        ).thenThrow(
                new InvalidRecommendationRequestException(
                        "userId must be greater than 0."
                )
        );


        mockMvc.perform(
                get("/api/recommendations/users/0")
        )
        .andExpect(status().isBadRequest())

        .andExpect(
                jsonPath("$.status")
                        .value(400)
        )

        .andExpect(
                jsonPath("$.error")
                        .value(
                                "INVALID_RECOMMENDATION_REQUEST"
                        )
        )

        .andExpect(
                jsonPath("$.message")
                        .value(
                                "userId must be greater than 0."
                        )
        )

        .andExpect(
                jsonPath("$.path")
                        .value(
                                "/api/recommendations/users/0"
                        )
        )

        .andExpect(
                jsonPath("$.timestamp")
                        .exists()
        );


        verify(
                recommendationService,
                times(1)
        ).getRecommendations(0, 10);
    }
    
    @Test
    void shouldReturn400WhenLimitIsInvalid()
            throws Exception {

        when(
                recommendationService
                        .getRecommendations(1, 51)
        ).thenThrow(
                new InvalidRecommendationRequestException(
                        "limit must be between 1 and 50."
                )
        );


        mockMvc.perform(
                get("/api/recommendations/users/1")
                        .param("limit", "51")
        )
        .andExpect(status().isBadRequest())

        .andExpect(
                jsonPath("$.status")
                        .value(400)
        )

        .andExpect(
                jsonPath("$.error")
                        .value(
                                "INVALID_RECOMMENDATION_REQUEST"
                        )
        )

        .andExpect(
                jsonPath("$.message")
                        .value(
                                "limit must be between 1 and 50."
                        )
        )

        .andExpect(
                jsonPath("$.path")
                        .value(
                                "/api/recommendations/users/1"
                        )
        );


        verify(
                recommendationService,
                times(1)
        ).getRecommendations(1, 51);
    }
    
    @Test
    void shouldReturn404WhenMlUserDoesNotExist()
            throws Exception {

        when(
                recommendationService
                        .getRecommendations(999999, 10)
        ).thenThrow(
                new MlUserNotFoundException(
                        "ML user 999999 was not found."
                )
        );


        mockMvc.perform(
                get("/api/recommendations/users/999999")
        )
        .andExpect(status().isNotFound())

        .andExpect(
                jsonPath("$.status")
                        .value(404)
        )

        .andExpect(
                jsonPath("$.error")
                        .value("ML_USER_NOT_FOUND")
        )

        .andExpect(
                jsonPath("$.message")
                        .value(
                                "ML user 999999 was not found."
                        )
        )

        .andExpect(
                jsonPath("$.path")
                        .value(
                                "/api/recommendations/users/999999"
                        )
        );


        verify(
                recommendationService,
                times(1)
        ).getRecommendations(999999, 10);
    }
    
    @Test
    void shouldReturn503WhenMlServiceIsUnavailable()
            throws Exception {

        when(
                recommendationService
                        .getRecommendations(1, 10)
        ).thenThrow(
                new MlServiceUnavailableException(
                        "ML recommendation service is unavailable.",
                        new RuntimeException(
                                "Connection refused"
                        )
                )
        );


        mockMvc.perform(
                get("/api/recommendations/users/1")
        )
        .andExpect(
                status().isServiceUnavailable()
        )

        .andExpect(
                jsonPath("$.status")
                        .value(503)
        )

        .andExpect(
                jsonPath("$.error")
                        .value(
                                "ML_SERVICE_UNAVAILABLE"
                        )
        )

        .andExpect(
                jsonPath("$.message")
                        .value(
                                "ML recommendation service is unavailable."
                        )
        )

        .andExpect(
                jsonPath("$.path")
                        .value(
                                "/api/recommendations/users/1"
                        )
        );


        verify(
                recommendationService,
                times(1)
        ).getRecommendations(1, 10);
    }
    
    @Test
    void shouldReturn502WhenMlServiceReturnsError()
            throws Exception {

        when(
                recommendationService
                        .getRecommendations(1, 10)
        ).thenThrow(
                new MlServiceException(
                        "ML recommendation service returned HTTP 500."
                )
        );


        mockMvc.perform(
                get("/api/recommendations/users/1")
        )
        .andExpect(
                status().isBadGateway()
        )

        .andExpect(
                jsonPath("$.status")
                        .value(502)
        )

        .andExpect(
                jsonPath("$.error")
                        .value("ML_SERVICE_ERROR")
        )

        .andExpect(
                jsonPath("$.message")
                        .value(
                                "ML recommendation service returned HTTP 500."
                        )
        )

        .andExpect(
                jsonPath("$.path")
                        .value(
                                "/api/recommendations/users/1"
                        )
        );


        verify(
                recommendationService,
                times(1)
        ).getRecommendations(1, 10);
    }
    
    @Test
    void shouldReturn400WhenUserIdIsNotInteger()
            throws Exception {

        mockMvc.perform(
                get(
                        "/api/recommendations/users/{userId}",
                        "abc"
                )
        )
        .andExpect(status().isBadRequest())

        .andExpect(
                jsonPath("$.status")
                        .value(400)
        )

        .andExpect(
                jsonPath("$.error")
                        .value(
                                "INVALID_PARAMETER_TYPE"
                        )
        )

        .andExpect(
                jsonPath("$.message")
                        .value(
                                "Parameter 'userId' must be a valid integer."
                        )
        )

        .andExpect(
                jsonPath("$.path")
                        .value(
                                "/api/recommendations/users/abc"
                        )
        )

        .andExpect(
                jsonPath("$.timestamp")
                        .exists()
        );


        verifyNoInteractions(
                recommendationService
        );
    }
    
    
    
    @Test
    void shouldUseDefaultLimitOfTen() throws Exception {

        RecommendationResponse response =
                new RecommendationResponse(
                        1,
                        0,
                        List.of()
                );


        when(
                recommendationService
                        .getRecommendations(1, 10)
        ).thenReturn(response);


        mockMvc.perform(
                get("/api/recommendations/users/1")
        )
        .andExpect(status().isOk())

        .andExpect(
                jsonPath("$.userId")
                        .value(1)
        );


        verify(
                recommendationService,
                times(1)
        ).getRecommendations(1, 10);
    }
    
    @Test
    void shouldReturn400WhenLimitIsNotInteger()
            throws Exception {

        mockMvc.perform(
                get("/api/recommendations/users/1")
                        .param("limit", "abc")
        )
        .andExpect(status().isBadRequest())

        .andExpect(
                jsonPath("$.status")
                        .value(400)
        )

        .andExpect(
                jsonPath("$.error")
                        .value("INVALID_PARAMETER_TYPE")
        )

        .andExpect(
                jsonPath("$.message")
                        .value(
                                "Parameter 'limit' must be a valid integer."
                        )
        )

        .andExpect(
                jsonPath("$.path")
                        .value(
                                "/api/recommendations/users/1"
                        )
        )

        .andExpect(
                jsonPath("$.timestamp")
                        .exists()
        );


        verifyNoInteractions(
                recommendationService
        );
    }
    
    

//
//    @Test
//    void shouldReturnRecommendations() throws Exception {
//
//        RecommendationResponse response =
//                new RecommendationResponse(
//                        1,
//                        2,
//                        List.of(
//                                new RecommendedMovie(
//                                        1,
//                                        922,
//                                        "Sunset Boulevard",
//                                        1950,
//                                        List.of("Drama"),
//                                        0.806164
//                                ),
//
//                                new RecommendedMovie(
//                                        2,
//                                        6001,
//                                        "The King of Comedy",
//                                        1982,
//                                        List.of(
//                                                "Drama",
//                                                "Comedy"
//                                        ),
//                                        0.802498
//                                )
//                        )
//                );
//
//
//        when(
//                recommendationService
//                        .getRecommendations(1, 2)
//        ).thenReturn(response);
//
//
//        mockMvc.perform(
//                get("/api/recommendations/users/1")
//                        .param("limit", "2")
//        )
//        .andExpect(status().isOk())
//
//        .andExpect(
//                jsonPath("$.userId")
//                        .value(1)
//        )
//
//        .andExpect(
//                jsonPath("$.count")
//                        .value(2)
//        )
//
//        .andExpect(
//                jsonPath("$.recommendations.length()")
//                        .value(2)
//        )
//
//        .andExpect(
//                jsonPath("$.recommendations[0].rank")
//                        .value(1)
//        )
//
//        .andExpect(
//                jsonPath("$.recommendations[0].movieId")
//                        .value(922)
//        )
//
//        .andExpect(
//                jsonPath("$.recommendations[0].title")
//                        .value("Sunset Boulevard")
//        )
//
//        .andExpect(
//                jsonPath("$.recommendations[0].releaseYear")
//                        .value(1950)
//        )
//
//        .andExpect(
//                jsonPath("$.recommendations[0].genres[0]")
//                        .value("Drama")
//        )
//
//        .andExpect(
//                jsonPath("$.recommendations[0].score")
//                        .value(0.806164)
//        )
//
//        .andExpect(
//                jsonPath(
//                        "$.recommendations[0].cfScore"
//                ).doesNotExist()
//        )
//
//        .andExpect(
//                jsonPath(
//                        "$.recommendations[0].contentScore"
//                ).doesNotExist()
//        )
//
//        .andExpect(
//                jsonPath(
//                        "$.recommendations[0].sentimentScore"
//                ).doesNotExist()
//        )
//        .andExpect(
//                jsonPath(
//                        "$.recommendations[0].sentimentAvailable"
//                ).doesNotExist()
//        );
//
//
//        verify(
//                recommendationService,
//                times(1)
//        ).getRecommendations(1, 2);
//
//
//        verifyNoMoreInteractions(
//                recommendationService
//        );
//
//
//        System.out.println();
//        System.out.println(
//                "=============================================="
//        );
//        System.out.println(
//                "RECOMMENDATION CONTROLLER TEST"
//        );
//        System.out.println(
//                "=============================================="
//        );
//
//        System.out.println(
//                "Endpoint : GET "
//                + "/api/recommendations/users/1?limit=2"
//        );
//
//        System.out.println("Status   : 200 OK");
//        System.out.println("Count    : 2");
//
//        System.out.println();
//        System.out.println(
//                "RECOMMENDATION CONTROLLER TEST PASSED"
//        );
//    }
}