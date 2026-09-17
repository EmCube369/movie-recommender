package com.marshal.movierecommender.security;

import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.mock.web.MockHttpSession;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.authority.SimpleGrantedAuthority;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import com.marshal.movierecommender.config.SecurityConfig;
import com.marshal.movierecommender.controller.UserMovieActivityController;
import com.marshal.movierecommender.recommendation.controller.RecommendationController;
import com.marshal.movierecommender.recommendation.dto.RecommendationResponse;
import com.marshal.movierecommender.recommendation.service.RecommendationService;
import com.marshal.movierecommender.service.UserMovieActivityService;

@WebMvcTest({
        UserMovieActivityController.class,
        RecommendationController.class
})
@Import(SecurityConfig.class)
class UserAuthorizationTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private UserMovieActivityService activityService;

    @MockitoBean
    private RecommendationService recommendationService;

    private MockHttpSession authenticatedSession(
            String username,
            String role) {

        var authentication =
                new UsernamePasswordAuthenticationToken(
                        username,
                        null,
                        List.of(
                                new SimpleGrantedAuthority(
                                        "ROLE_" + role
                                )
                        )
                );

        SecurityContext securityContext =
                SecurityContextHolder.createEmptyContext();

        securityContext.setAuthentication(authentication);

        MockHttpSession session = new MockHttpSession();

        session.setAttribute(
                HttpSessionSecurityContextRepository
                        .SPRING_SECURITY_CONTEXT_KEY,
                securityContext
        );

        return session;
    }

    @Test
    void userMovieActivity_WhenAnonymous_ShouldReturn401()
            throws Exception {

        mockMvc.perform(
                get("/api/user-movies/1")
        )
        .andExpect(status().isUnauthorized());

        verify(
                activityService,
                never()
        ).getActivity(
                org.mockito.ArgumentMatchers.anyString(),
                org.mockito.ArgumentMatchers.anyInt()
        );
    }

    @Test
    void userMovieActivity_WhenUser_ShouldReturn200()
            throws Exception {

        given(
                activityService.getActivity(
                        "normaluser",
                        1
                )
        ).willReturn(Optional.empty());

        MockHttpSession session =
                authenticatedSession(
                        "normaluser",
                        "USER"
                );

        mockMvc.perform(
                get("/api/user-movies/1")
                        .session(session)
        )
        .andExpect(status().isOk());

        verify(
                activityService
        ).getActivity(
                "normaluser",
                1
        );
    }

    @Test
    void personalizedRecommendations_WhenAnonymous_ShouldReturn401()
            throws Exception {

        mockMvc.perform(
                get("/api/recommendations/me")
        )
        .andExpect(status().isUnauthorized());

        verify(
                recommendationService,
                never()
        ).getPersonalizedRecommendations(
                org.mockito.ArgumentMatchers.anyString(),
                org.mockito.ArgumentMatchers.anyInt()
        );
    }

    @Test
    void personalizedRecommendations_WhenUser_ShouldReturn200()
            throws Exception {

        RecommendationResponse response =
                new RecommendationResponse(
                        1,
                        0,
                        List.of()
                );

        given(
                recommendationService
                        .getPersonalizedRecommendations(
                                "normaluser",
                                10
                        )
        ).willReturn(response);

        MockHttpSession session =
                authenticatedSession(
                        "normaluser",
                        "USER"
                );

        mockMvc.perform(
                get("/api/recommendations/me")
                        .session(session)
        )
        .andExpect(status().isOk());

        verify(
                recommendationService
        ).getPersonalizedRecommendations(
                "normaluser",
                10
        );
    }
}