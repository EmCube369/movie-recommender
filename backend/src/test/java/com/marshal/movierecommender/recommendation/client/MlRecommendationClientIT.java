package com.marshal.movierecommender.recommendation.client;

import com.marshal.movierecommender.recommendation.config.MlClientConfig;
import com.marshal.movierecommender.recommendation.dto.MlRecommendationResponse;
import com.marshal.movierecommender.recommendation.dto.MlRecommendedMovie;

import org.junit.jupiter.api.Test;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.test.context.TestPropertySource;
import org.springframework.test.context.junit.jupiter.SpringJUnitConfig;

import static org.junit.jupiter.api.Assertions.*;


@SpringJUnitConfig(classes = {
        MlClientConfig.class,
        MlRecommendationClient.class
})
@TestPropertySource(properties = {
        "ml.service.base-url=http://127.0.0.1:8000"
})
class MlRecommendationClientIT {

    @Autowired
    private MlRecommendationClient mlRecommendationClient;


    @Test
    void shouldFetchRecommendationsFromPythonMlService() {

        MlRecommendationResponse response =
                mlRecommendationClient.getRecommendations(1, 5);


        assertNotNull(response);

        assertEquals("1.0", response.schemaVersion());
        assertEquals(1, response.mlUserId());
        assertEquals(5, response.count());

        assertNotNull(response.recommendations());
        assertEquals(5, response.recommendations().size());


        for (int i = 0; i < response.recommendations().size(); i++) {

            MlRecommendedMovie movie =
                    response.recommendations().get(i);

            assertNotNull(movie);

            assertEquals(i + 1, movie.rank());

            assertNotNull(movie.movieId());
            assertNotNull(movie.title());
            assertNotNull(movie.genres());

            assertNotNull(movie.score());
            assertNotNull(movie.cfScore());
            assertNotNull(movie.contentScore());
            assertNotNull(movie.sentimentScore());
            assertNotNull(movie.sentimentAvailable());
        }


        System.out.println();
        System.out.println(
                "=============================================="
        );
        System.out.println(
                "SPRING BOOT -> PYTHON ML CLIENT TEST"
        );
        System.out.println(
                "=============================================="
        );

        System.out.println(
                "Schema version : " + response.schemaVersion()
        );

        System.out.println(
                "ML user ID     : " + response.mlUserId()
        );

        System.out.println(
                "Count          : " + response.count()
        );

        System.out.println();
        System.out.println("Recommendations:");


        for (MlRecommendedMovie movie : response.recommendations()) {

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
                "SPRING BOOT -> PYTHON ML CLIENT TEST PASSED"
        );
    }
}