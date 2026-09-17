package com.marshal.movierecommender.admin.controller;

import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.List;

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

import com.marshal.movierecommender.admin.service.AdminUserService;
import com.marshal.movierecommender.config.SecurityConfig;

@WebMvcTest(AdminUserController.class)
@Import(SecurityConfig.class)
class AdminAuthorizationTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private AdminUserService adminUserService;

    private MockHttpSession authenticatedSession(
            String username,
            String role
    ) {

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
    void getAllUsers_WhenAnonymous_ShouldReturn401()
            throws Exception {

        mockMvc.perform(
                get("/api/admin/users")
        )
        .andExpect(status().isUnauthorized());

        verify(
                adminUserService,
                never()
        ).getAllUsers();
    }

    @Test
    void getAllUsers_WhenUser_ShouldReturn403()
            throws Exception {

        MockHttpSession session =
                authenticatedSession(
                        "normaluser",
                        "USER"
                );

        mockMvc.perform(
                get("/api/admin/users")
                        .session(session)
        )
        .andExpect(status().isForbidden());

        verify(
                adminUserService,
                never()
        ).getAllUsers();
    }

    @Test
    void getAllUsers_WhenAdmin_ShouldReturn200()
            throws Exception {

        given(
                adminUserService.getAllUsers()
        ).willReturn(List.of());

        MockHttpSession session =
                authenticatedSession(
                        "admin",
                        "ADMIN"
                );

        mockMvc.perform(
                get("/api/admin/users")
                        .session(session)
        )
        .andExpect(status().isOk())
        .andExpect(content().json("[]"));

        verify(
                adminUserService
        ).getAllUsers();
    }
}