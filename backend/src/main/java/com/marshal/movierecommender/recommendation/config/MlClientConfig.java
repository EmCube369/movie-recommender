package com.marshal.movierecommender.recommendation.config;

import java.time.Duration;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;


@Configuration
public class MlClientConfig {

    @Bean
    public RestClient mlRestClient(
            @Value("${ml.service.base-url}") String baseUrl
    ) {

        SimpleClientHttpRequestFactory requestFactory =
                new SimpleClientHttpRequestFactory();

        requestFactory.setConnectTimeout(
                Duration.ofSeconds(3)
        );

        requestFactory.setReadTimeout(
                Duration.ofSeconds(10)
        );


        return RestClient.builder()
                .baseUrl(baseUrl)
                .requestFactory(requestFactory)
                .build();
    }
}