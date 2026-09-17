package com.marshal.movierecommender.recommendation.integration;

import static org.junit.jupiter.api.Assertions.*;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.HashSet;
import java.util.List;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.TestMethodOrder;
import org.junit.jupiter.api.MethodOrderer;
import org.junit.jupiter.api.Order;

import com.marshal.movierecommender.recommendation.dto.RecommendationResponse;
import com.marshal.movierecommender.recommendation.dto.RecommendedMovie;

import tools.jackson.databind.json.JsonMapper;


@TestMethodOrder(MethodOrderer.OrderAnnotation.class)
class RecommendationEndToEndIT {

    private static final String SPRING_BASE_URL =
            "http://127.0.0.1:8080";

    private static final HttpClient HTTP_CLIENT =
            HttpClient.newBuilder()
                    .connectTimeout(Duration.ofSeconds(5))
                    .build();

    private static final JsonMapper JSON_MAPPER =
            JsonMapper.builder().build();


    // ================================================================
    // HTTP HELPER
    // ================================================================

    private HttpResponse<String> get(String path)
            throws Exception {

        HttpRequest request =
                HttpRequest.newBuilder()
                        .uri(
                                URI.create(
                                        SPRING_BASE_URL + path
                                )
                        )
                        .timeout(Duration.ofSeconds(15))
                        .GET()
                        .build();

        return HTTP_CLIENT.send(
                request,
                HttpResponse.BodyHandlers.ofString()
        );
    }


    private RecommendationResponse parseRecommendations(
            HttpResponse<String> response
    ) throws Exception {

        return JSON_MAPPER.readValue(
                response.body(),
                RecommendationResponse.class
        );
    }


    // ================================================================
    // 1. KNOWN USER - FULL END TO END
    // ================================================================

    @Test
    @Order(1)
    void knownUserShouldReturnRecommendationsEndToEnd()
            throws Exception {

        long start = System.nanoTime();

        HttpResponse<String> response =
                get(
                        "/api/recommendations/users/1"
                        + "?limit=5"
                );

        double elapsedMs =
                (System.nanoTime() - start)
                        / 1_000_000.0;


        assertEquals(
                200,
                response.statusCode()
        );


        RecommendationResponse body =
                parseRecommendations(response);


        assertNotNull(body);

        assertEquals(
                1,
                body.userId()
        );

        assertEquals(
                5,
                body.count()
        );

        assertNotNull(
                body.recommendations()
        );

        assertEquals(
                5,
                body.recommendations().size()
        );


        // Verify ranking is sequential.
        for (int i = 0;
             i < body.recommendations().size();
             i++) {

            RecommendedMovie movie =
                    body.recommendations().get(i);

            assertEquals(
                    i + 1,
                    movie.rank()
            );

            assertNotNull(movie.movieId());
            assertNotNull(movie.title());
            assertNotNull(movie.genres());
            assertNotNull(movie.score());

            assertTrue(
                    Double.isFinite(movie.score())
            );
        }


        // No duplicate movies.
        List<Integer> movieIds =
                body.recommendations()
                        .stream()
                        .map(RecommendedMovie::movieId)
                        .toList();

        assertEquals(
                movieIds.size(),
                new HashSet<>(movieIds).size()
        );


        // Verify the current validated ML artifacts reached Spring
        // without changing the ranking.
        assertEquals(
                List.of(
                        922,
                        6001,
                        6669,
                        1244,
                        3736
                ),
                movieIds
        );


        assertEquals(
                "Sunset Boulevard",
                body.recommendations()
                        .get(0)
                        .title()
        );


        // Internal ML scores must not leak through the public API.
        assertFalse(
                response.body().contains("\"cfScore\"")
        );

        assertFalse(
                response.body().contains("\"contentScore\"")
        );

        assertFalse(
                response.body().contains("\"sentimentScore\"")
        );

        assertFalse(
                response.body().contains(
                        "\"sentimentAvailable\""
                )
        );


        System.out.println();
        System.out.println(
                "=============================================="
        );

        System.out.println(
                "1. KNOWN USER END-TO-END TEST"
        );

        System.out.println(
                "=============================================="
        );

        System.out.printf(
                "HTTP status : %d%n",
                response.statusCode()
        );

        System.out.printf(
                "Time        : %.2f ms%n",
                elapsedMs
        );

        for (RecommendedMovie movie
                : body.recommendations()) {

            System.out.printf(
                    "%d. %s (%s) - %.6f%n",
                    movie.rank(),
                    movie.title(),
                    movie.releaseYear(),
                    movie.score()
            );
        }

        System.out.println(
                "PASS - Full Spring -> Python path works"
        );
    }


    // ================================================================
    // 2. SPARSE KNOWN USER
    // ================================================================

    @Test
    @Order(2)
    void sparseKnownUserShouldWorkEndToEnd()
            throws Exception {

        HttpResponse<String> response =
                get(
                        "/api/recommendations/users/7382"
                        + "?limit=5"
                );


        assertEquals(
                200,
                response.statusCode()
        );


        RecommendationResponse body =
                parseRecommendations(response);


        assertEquals(
                7382,
                body.userId()
        );

        assertEquals(
                5,
                body.count()
        );

        assertEquals(
                5,
                body.recommendations().size()
        );


        System.out.println();
        System.out.println(
                "PASS - Sparse known user 7382 works"
        );
    }


    // ================================================================
    // 3. DEFAULT LIMIT
    // ================================================================

    @Test
    @Order(3)
    void defaultLimitShouldBeTen()
            throws Exception {

        HttpResponse<String> response =
                get(
                        "/api/recommendations/users/1"
                );


        assertEquals(
                200,
                response.statusCode()
        );


        RecommendationResponse body =
                parseRecommendations(response);


        assertEquals(
                10,
                body.count()
        );

        assertEquals(
                10,
                body.recommendations().size()
        );


        System.out.println();
        System.out.println(
                "PASS - Default limit is 10"
        );
    }


    // ================================================================
    // 4. INVALID USER
    // ================================================================

    @Test
    @Order(4)
    void invalidUserShouldReturn400()
            throws Exception {

        HttpResponse<String> response =
                get(
                        "/api/recommendations/users/0"
                        + "?limit=5"
                );


        assertEquals(
                400,
                response.statusCode()
        );

        assertTrue(
                response.body().contains(
                        "\"error\":\"INVALID_RECOMMENDATION_REQUEST\""
                )
        );


        System.out.println();
        System.out.println(
                "PASS - Invalid user returns 400"
        );
    }


    // ================================================================
    // 5. INVALID LIMIT
    // ================================================================

    @Test
    @Order(5)
    void invalidLimitShouldReturn400()
            throws Exception {

        HttpResponse<String> response =
                get(
                        "/api/recommendations/users/1"
                        + "?limit=51"
                );


        assertEquals(
                400,
                response.statusCode()
        );

        assertTrue(
                response.body().contains(
                        "\"error\":\"INVALID_RECOMMENDATION_REQUEST\""
                )
        );


        System.out.println();
        System.out.println(
                "PASS - Invalid limit returns 400"
        );
    }


    // ================================================================
    // 6. INVALID PARAMETER TYPE
    // ================================================================

    @Test
    @Order(6)
    void nonNumericUserShouldReturn400()
            throws Exception {

        HttpResponse<String> response =
                get(
                        "/api/recommendations/users/abc"
                        + "?limit=5"
                );


        assertEquals(
                400,
                response.statusCode()
        );

        assertTrue(
                response.body().contains(
                        "\"error\":\"INVALID_PARAMETER_TYPE\""
                )
        );


        System.out.println();
        System.out.println(
                "PASS - Non-numeric user returns 400"
        );
    }


    // ================================================================
    // 7. UNKNOWN ML USER
    // ================================================================

    @Test
    @Order(7)
    void unknownMlUserShouldReturn404()
            throws Exception {

        HttpResponse<String> response =
                get(
                        "/api/recommendations/users/999999999"
                        + "?limit=5"
                );


        assertEquals(
                404,
                response.statusCode()
        );

        assertTrue(
                response.body().contains(
                        "\"error\":\"ML_USER_NOT_FOUND\""
                )
        );


        System.out.println();
        System.out.println(
                "PASS - Unknown ML user returns 404"
        );
    }


    // ================================================================
    // 8. REPEATED REQUEST CONSISTENCY
    // ================================================================

    @Test
    @Order(8)
    void repeatedRequestsShouldRemainConsistent()
            throws Exception {

        HttpResponse<String> firstResponse =
                get(
                        "/api/recommendations/users/1"
                        + "?limit=5"
                );

        HttpResponse<String> secondResponse =
                get(
                        "/api/recommendations/users/1"
                        + "?limit=5"
                );


        assertEquals(
                200,
                firstResponse.statusCode()
        );

        assertEquals(
                200,
                secondResponse.statusCode()
        );


        RecommendationResponse first =
                parseRecommendations(firstResponse);

        RecommendationResponse second =
                parseRecommendations(secondResponse);


        assertEquals(
                first.recommendations(),
                second.recommendations()
        );


        System.out.println();
        System.out.println(
                "PASS - Repeated rankings and scores "
                + "are consistent"
        );
    }
}