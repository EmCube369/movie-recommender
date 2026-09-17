package com.marshal.movierecommender.recommendation.client;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;

import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;

import static org.springframework.test.web.client.response.MockRestResponseCreators.withNoContent;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;

import org.springframework.test.web.client.MockRestServiceServer;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;

import com.marshal.movierecommender.recommendation.dto.MlRecommendationResponse;

import com.marshal.movierecommender.recommendation.exception.MlServiceException;
import com.marshal.movierecommender.recommendation.exception.MlServiceUnavailableException;
import com.marshal.movierecommender.recommendation.exception.MlUserNotFoundException;


class MlRecommendationClientTest {

    private MockRestServiceServer mockServer;

    private MlRecommendationClient mlRecommendationClient;


    @BeforeEach
    void setUp() {

        RestClient.Builder builder =
                RestClient.builder()
                        .baseUrl("http://localhost:8000");

        mockServer =
                MockRestServiceServer
                        .bindTo(builder)
                        .build();

        mlRecommendationClient =
                new MlRecommendationClient(
                        builder.build()
                );
    }
    
    @Test
    void shouldThrowMlServiceUnavailableExceptionWhenConnectionFails() {

        mockServer
                .expect(
                        requestTo(
                                "http://localhost:8000/api/v1/recommendations"
                        )
                )
                .andExpect(
                        method(HttpMethod.POST)
                )
                .andRespond(request -> {
                    throw new ResourceAccessException(
                            "Connection refused"
                    );
                });


        MlServiceUnavailableException exception =
                assertThrows(
                        MlServiceUnavailableException.class,
                        () ->
                                mlRecommendationClient
                                        .getRecommendations(
                                                1,
                                                10
                                        )
                );


        assertEquals(
                "ML recommendation service is unavailable.",
                exception.getMessage()
        );


        mockServer.verify();
    }


    @Test
    void shouldReturnRecommendationsWhenMlServiceReturns200() {

        String responseBody = """
                {
                    "schemaVersion": "1.0",
                    "mlUserId": 1,
                    "count": 2,
                    "recommendations": [
                        {
                            "rank": 1,
                            "movieId": 922,
                            "title": "Sunset Boulevard",
                            "releaseYear": 1950,
                            "genres": ["Drama"],
                            "score": 0.806164,
                            "cfScore": 0.784551,
                            "contentScore": 0.844872,
                            "sentimentScore": 0.787886,
                            "sentimentAvailable": true
                        },
                        {
                            "rank": 2,
                            "movieId": 6001,
                            "title": "The King of Comedy",
                            "releaseYear": 1982,
                            "genres": ["Drama", "Comedy"],
                            "score": 0.802498,
                            "cfScore": 0.740118,
                            "contentScore": 0.974292,
                            "sentimentScore": 0.609582,
                            "sentimentAvailable": true
                        }
                    ]
                }
                """;


        mockServer
                .expect(
                        requestTo(
                                "http://localhost:8000/api/v1/recommendations"
                        )
                )
                .andExpect(
                        method(HttpMethod.POST)
                )
                .andRespond(
                        withSuccess(
                                responseBody,
                                MediaType.APPLICATION_JSON
                        )
                );


        MlRecommendationResponse response =
                mlRecommendationClient
                        .getRecommendations(
                                1,
                                2
                        );


        assertNotNull(response);

        assertEquals(
                "1.0",
                response.schemaVersion()
        );

        assertEquals(
                1,
                response.mlUserId()
        );

        assertEquals(
                2,
                response.count()
        );

        assertNotNull(
                response.recommendations()
        );

        assertEquals(
                2,
                response.recommendations().size()
        );

        assertEquals(
                "Sunset Boulevard",
                response
                        .recommendations()
                        .get(0)
                        .title()
        );


        mockServer.verify();
    }


    @Test
    void shouldThrowMlUserNotFoundExceptionWhenMlServiceReturns404() {

        mockServer
                .expect(
                        requestTo(
                                "http://localhost:8000/api/v1/recommendations"
                        )
                )
                .andExpect(
                        method(HttpMethod.POST)
                )
                .andRespond(
                        withStatus(
                                HttpStatus.NOT_FOUND
                        )
                );


        MlUserNotFoundException exception =
                assertThrows(
                        MlUserNotFoundException.class,
                        () ->
                                mlRecommendationClient
                                        .getRecommendations(
                                                999999,
                                                10
                                        )
                );


        assertEquals(
                "ML user 999999 was not found.",
                exception.getMessage()
        );


        mockServer.verify();
    }


    @Test
    void shouldThrowMlServiceExceptionWhenMlServiceReturns500() {

        mockServer
                .expect(
                        requestTo(
                                "http://localhost:8000/api/v1/recommendations"
                        )
                )
                .andExpect(
                        method(HttpMethod.POST)
                )
                .andRespond(
                        withStatus(
                                HttpStatus.INTERNAL_SERVER_ERROR
                        )
                );


        MlServiceException exception =
                assertThrows(
                        MlServiceException.class,
                        () ->
                                mlRecommendationClient
                                        .getRecommendations(
                                                1,
                                                10
                                        )
                );


        assertEquals(
                "ML recommendation service returned HTTP 500.",
                exception.getMessage()
        );


        mockServer.verify();
    }


    @Test
    void shouldThrowMlServiceExceptionWhenResponseBodyIsEmpty() {

        mockServer
                .expect(
                        requestTo(
                                "http://localhost:8000/api/v1/recommendations"
                        )
                )
                .andExpect(
                        method(HttpMethod.POST)
                )
                .andRespond(
                        withNoContent()
                );


        MlServiceException exception =
                assertThrows(
                        MlServiceException.class,
                        () ->
                                mlRecommendationClient
                                        .getRecommendations(
                                                1,
                                                10
                                        )
                );


        assertEquals(
                "ML recommendation service returned an empty response.",
                exception.getMessage()
        );


        mockServer.verify();
    }


    @Test
    void shouldThrowMlServiceExceptionWhenRecommendationsAreNull() {

        String responseBody = """
                {
                    "schemaVersion": "1.0",
                    "mlUserId": 1,
                    "count": 0,
                    "recommendations": null
                }
                """;


        mockServer
                .expect(
                        requestTo(
                                "http://localhost:8000/api/v1/recommendations"
                        )
                )
                .andExpect(
                        method(HttpMethod.POST)
                )
                .andRespond(
                        withSuccess(
                                responseBody,
                                MediaType.APPLICATION_JSON
                        )
                );


        MlServiceException exception =
                assertThrows(
                        MlServiceException.class,
                        () ->
                                mlRecommendationClient
                                        .getRecommendations(
                                                1,
                                                10
                                        )
                );


        assertEquals(
                "ML recommendation service returned an invalid response.",
                exception.getMessage()
        );


        mockServer.verify();
    }
}