package com.marshal.movierecommender.recommendation.client;

import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestClientResponseException;

import com.marshal.movierecommender.recommendation.dto.MlRecommendationRequest;
import com.marshal.movierecommender.recommendation.dto.MlRecommendationResponse;
import com.marshal.movierecommender.recommendation.exception.MlServiceException;
import com.marshal.movierecommender.recommendation.exception.MlServiceUnavailableException;
import com.marshal.movierecommender.recommendation.exception.MlUserNotFoundException;
import com.marshal.movierecommender.recommendation.dto.MlPersonalizedRecommendationRequest;
import com.marshal.movierecommender.recommendation.dto.MlPersonalizedRecommendationResponse;
import com.marshal.movierecommender.recommendation.exception.InvalidRecommendationRequestException;
import com.marshal.movierecommender.recommendation.exception.MlMovieNotFoundException;
import com.marshal.movierecommender.recommendation.dto.MlMovieCatalogResponse;
import com.marshal.movierecommender.recommendation.dto.MlMovieCatalogSearchResponse;

@Component
public class MlRecommendationClient {

    private final RestClient restClient;


    public MlRecommendationClient(
            @Qualifier("mlRestClient") RestClient restClient
    ) {
        this.restClient = restClient;
    }


    public MlRecommendationResponse getRecommendations(
            Integer mlUserId,
            Integer limit
    ) {

        MlRecommendationRequest request =
                new MlRecommendationRequest(
                        mlUserId,
                        limit
                );

        try {

            MlRecommendationResponse response =
                    restClient
                            .post()
                            .uri("/api/v1/recommendations")
                            .contentType(MediaType.APPLICATION_JSON)
                            .accept(MediaType.APPLICATION_JSON)
                            .body(request)
                            .retrieve()
                            .body(MlRecommendationResponse.class);


            if (response == null) {
                throw new MlServiceException(
                        "ML recommendation service returned an empty response."
                );
            }

            if (response.recommendations() == null) {
                throw new MlServiceException(
                        "ML recommendation service returned an invalid response."
                );
            }

            return response;


        } catch (ResourceAccessException ex) {

            throw new MlServiceUnavailableException(
                    "ML recommendation service is unavailable.",
                    ex
            );


        } catch (RestClientResponseException ex) {

            if (ex.getStatusCode().value() == 404) {

                throw new MlUserNotFoundException(
                        "ML user " + mlUserId + " was not found."
                );
            }

            throw new MlServiceException(
                    "ML recommendation service returned HTTP "
                            + ex.getStatusCode().value() + ".",
                    ex
            );


        } catch (RestClientException ex) {

            throw new MlServiceException(
                    "Failed to communicate with ML recommendation service.",
                    ex
            );
        }
    }

    
    public MlPersonalizedRecommendationResponse getPersonalizedRecommendations(
            MlPersonalizedRecommendationRequest request
    ) {

        try {

            MlPersonalizedRecommendationResponse response =
                    restClient
                            .post()
                            .uri("/api/v1/recommendations/personalized")
                            .contentType(MediaType.APPLICATION_JSON)
                            .accept(MediaType.APPLICATION_JSON)
                            .body(request)
                            .retrieve()
                            .body(MlPersonalizedRecommendationResponse.class);


            if (response == null) {
                throw new MlServiceException(
                        "ML recommendation service returned an empty response."
                );
            }

            if (response.recommendations() == null) {
                throw new MlServiceException(
                        "ML recommendation service returned an invalid response."
                );
            }

            return response;


        } catch (ResourceAccessException ex) {

            throw new MlServiceUnavailableException(
                    "ML recommendation service is unavailable.",
                    ex
            );


        } catch (RestClientResponseException ex) {

            if (ex.getStatusCode().value() == 400) {
                throw new InvalidRecommendationRequestException(
                        "Personalized recommendation request was rejected."
                );
            }

            throw new MlServiceException(
                    "ML recommendation service returned HTTP "
                            + ex.getStatusCode().value() + ".",
                    ex
            );


        } catch (RestClientException ex) {

            throw new MlServiceException(
                    "Failed to communicate with ML recommendation service.",
                    ex
            );
        }
    }

    public MlMovieCatalogResponse getMovie(
            Integer movieId
    ) {

        try {

            MlMovieCatalogResponse response =
                    restClient
                            .get()
                            .uri(
                                    "/api/v1/movies/{movieId}",
                                    movieId
                            )
                            .accept(MediaType.APPLICATION_JSON)
                            .retrieve()
                            .body(MlMovieCatalogResponse.class);

            if (response == null) {
                throw new MlServiceException(
                        "ML movie catalog returned an empty response."
                );
            }

            return response;

        } catch (ResourceAccessException ex) {

            throw new MlServiceUnavailableException(
                    "ML recommendation service is unavailable.",
                    ex
            );

        } catch (RestClientResponseException ex) {

            if (ex.getStatusCode().value() == 404) {
            	throw new MlMovieNotFoundException(
            	        "ML movie " + movieId + " was not found."
            	);
            }

            throw new MlServiceException(
                    "ML movie catalog returned HTTP "
                            + ex.getStatusCode().value() + ".",
                    ex
            );

        } catch (RestClientException ex) {

            throw new MlServiceException(
                    "Failed to communicate with ML movie catalog.",
                    ex
            );
        }
    }

    
    public MlMovieCatalogSearchResponse searchMovies(
            String query,
            Integer limit
    ) {

        int effectiveLimit =
                limit == null ? 20 : limit;

        try {

            MlMovieCatalogSearchResponse response =
                    restClient
                            .get()
                            .uri(uriBuilder ->
                                    uriBuilder
                                            .path("/api/v1/movie-catalog/search")
                                            .queryParam("query", query)
                                            .queryParam("limit", effectiveLimit)
                                            .build()
                            )
                            .accept(MediaType.APPLICATION_JSON)
                            .retrieve()
                            .body(MlMovieCatalogSearchResponse.class);

            if (response == null) {
                throw new MlServiceException(
                        "ML movie catalog search returned an empty response."
                );
            }

            if (response.movies() == null) {
                throw new MlServiceException(
                        "ML movie catalog search returned an invalid response."
                );
            }

            return response;

        } catch (ResourceAccessException ex) {

            throw new MlServiceUnavailableException(
                    "ML recommendation service is unavailable.",
                    ex
            );

        } catch (RestClientResponseException ex) {

            throw new MlServiceException(
                    "ML movie catalog search returned HTTP "
                            + ex.getStatusCode().value() + ".",
                    ex
            );

        } catch (RestClientException ex) {

            throw new MlServiceException(
                    "Failed to communicate with ML movie catalog.",
                    ex
            );
        }
    }
    
}