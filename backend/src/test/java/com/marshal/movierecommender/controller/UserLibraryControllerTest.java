package com.marshal.movierecommender.controller;

import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.List;

import org.junit.jupiter.api.BeforeEach;
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
import com.marshal.movierecommender.entity.Movie;
import com.marshal.movierecommender.entity.Role;
import com.marshal.movierecommender.entity.User;
import com.marshal.movierecommender.entity.UserMovieActivity;
import com.marshal.movierecommender.service.UserMovieActivityService;

@WebMvcTest(UserMovieActivityController.class)
@Import(SecurityConfig.class)
class UserLibraryControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private UserMovieActivityService activityService;

    private User user;
    private Movie movie;

    @BeforeEach
    void setUp() {

        user = new User(
                1,
                "marshal",
                "password",
                Role.USER
        );

        movie = new Movie();
        movie.setId(10);
        movie.setTitle("Inception");
        movie.setGenre("Sci-Fi");
        movie.setReleaseYear(2010);
        movie.setTmdbRating(8.8);
        movie.setMlMovieId(79132);
    }

    private MockHttpSession authenticatedSession() {

        var authentication =
                new UsernamePasswordAuthenticationToken(
                        "marshal",
                        null,
                        List.of(
                                new SimpleGrantedAuthority(
                                        "ROLE_USER"
                                )
                        )
                );

        SecurityContext securityContext =
                SecurityContextHolder.createEmptyContext();

        securityContext.setAuthentication(authentication);

        MockHttpSession session =
                new MockHttpSession();

        session.setAttribute(
                HttpSessionSecurityContextRepository
                        .SPRING_SECURITY_CONTEXT_KEY,
                securityContext
        );

        return session;
    }

    @Test
    void getLibrary_WhenActivitiesExist_ShouldReturnLibrary()
            throws Exception {

        UserMovieActivity activity =
                new UserMovieActivity(
                        5,
                        user,
                        movie,
                        4.5
                );

        given(
                activityService.getUserLibrary("marshal")
        ).willReturn(List.of(activity));

        mockMvc.perform(
                get("/api/user-movies")
                        .session(authenticatedSession())
        )
        .andExpect(status().isOk())
        .andExpect(jsonPath("$[0].movieId").value(10))
        .andExpect(jsonPath("$[0].title").value("Inception"))
        .andExpect(jsonPath("$[0].genre").value("Sci-Fi"))
        .andExpect(jsonPath("$[0].releaseYear").value(2010))
        .andExpect(jsonPath("$[0].tmdbRating").value(8.8))
        .andExpect(jsonPath("$[0].rating").value(4.5));

        verify(activityService)
                .getUserLibrary("marshal");
    }

    @Test
    void getLibrary_WhenLibraryIsEmpty_ShouldReturnEmptyList()
            throws Exception {

        given(
                activityService.getUserLibrary("marshal")
        ).willReturn(List.of());

        mockMvc.perform(
                get("/api/user-movies")
                        .session(authenticatedSession())
        )
        .andExpect(status().isOk())
        .andExpect(content().json("[]"));

        verify(activityService)
                .getUserLibrary("marshal");
    }

    @Test
    void removeActivity_WhenActivityExists_ShouldReturn204()
            throws Exception {

        given(
                activityService.removeActivity(
                        "marshal",
                        10
                )
        ).willReturn(true);

        mockMvc.perform(
                delete("/api/user-movies/10")
                        .session(authenticatedSession())
        )
        .andExpect(status().isNoContent());

        verify(activityService)
                .removeActivity(
                        "marshal",
                        10
                );
    }

    @Test
    void removeActivity_WhenActivityDoesNotExist_ShouldReturn404()
            throws Exception {

        given(
                activityService.removeActivity(
                        "marshal",
                        10
                )
        ).willReturn(false);

        mockMvc.perform(
                delete("/api/user-movies/10")
                        .session(authenticatedSession())
        )
        .andExpect(status().isNotFound());

        verify(activityService)
                .removeActivity(
                        "marshal",
                        10
                );
    }
}