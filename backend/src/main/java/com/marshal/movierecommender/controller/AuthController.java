package com.marshal.movierecommender.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import com.marshal.movierecommender.dto.AuthResponse;
import com.marshal.movierecommender.dto.RegisterRequest;
import com.marshal.movierecommender.entity.User;
import com.marshal.movierecommender.service.AuthService;

import jakarta.validation.Valid;

import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContext;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.web.context.SecurityContextRepository;
import org.springframework.security.web.csrf.CsrfToken;

import com.marshal.movierecommender.dto.LoginRequest;

import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

@RestController
@RequestMapping("/api/auth")
public class AuthController {

    private final AuthService authService;
    private final AuthenticationManager authenticationManager;
    private final SecurityContextRepository securityContextRepository;

    public AuthController(
    		AuthService authService,
    		AuthenticationManager authenticationManager,
    		SecurityContextRepository securityContextRepository) {
    	
        this.authService = authService;
        this.authenticationManager = authenticationManager;
        this.securityContextRepository = securityContextRepository;
    }

    @PostMapping("/register")
    public ResponseEntity<AuthResponse> register(
            @Valid @RequestBody RegisterRequest request) {

        User user = authService.register(request);

        AuthResponse response =
                new AuthResponse(
                        user.getId(),
                        user.getUsername(),
                        user.getRole().name(),
                        "Registration successful"
                );

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(response);
    }
    
    @PostMapping("/login")
    public ResponseEntity<AuthResponse> login(
            @Valid @RequestBody LoginRequest request,
            HttpServletRequest httpRequest,
            HttpServletResponse httpResponse) {

        Authentication authenticationRequest =
                UsernamePasswordAuthenticationToken
                        .unauthenticated(
                                request.getUsername().trim(),
                                request.getPassword()
                        );

        Authentication authentication =
                authenticationManager.authenticate(
                        authenticationRequest
                );

        SecurityContext securityContext =
                SecurityContextHolder.createEmptyContext();

        securityContext.setAuthentication(authentication);

        SecurityContextHolder.setContext(securityContext);

        securityContextRepository.saveContext(
                securityContext,
                httpRequest,
                httpResponse
        );

        User user = authService.getUserByUsername(
                authentication.getName()
        );

        AuthResponse response =
                new AuthResponse(
                        user.getId(),
                        user.getUsername(),
                        user.getRole().name(),
                        "Login successful"
                );

        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/me")
    public ResponseEntity<AuthResponse> getCurrentUser(
            Authentication authentication) {


        User user = authService.getUserByUsername(
                authentication.getName()
        );

        AuthResponse response =
                new AuthResponse(
                        user.getId(),
                        user.getUsername(),
                        user.getRole().name(),
                        "Authenticated"
                );

        return ResponseEntity.ok(response);
    }
    
    @GetMapping("/csrf")
    public ResponseEntity<Void> csrf(CsrfToken csrfToken) {

        csrfToken.getToken();

        return ResponseEntity.ok().build();
    }
}