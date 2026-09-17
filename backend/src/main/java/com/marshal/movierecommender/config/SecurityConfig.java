package com.marshal.movierecommender.config;

import static org.springframework.security.config.Customizer.withDefaults;

import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.HttpStatusEntryPoint;
import org.springframework.security.web.context.HttpSessionSecurityContextRepository;
import org.springframework.security.web.context.SecurityContextRepository;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;

@Configuration
@EnableWebSecurity
public class SecurityConfig {

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public AuthenticationManager authenticationManager(
            AuthenticationConfiguration configuration)
            throws Exception {

        return configuration.getAuthenticationManager();
    }

    @Bean
    public SecurityContextRepository securityContextRepository() {
        return new HttpSessionSecurityContextRepository();
    }

    @Bean
    public SecurityFilterChain securityFilterChain(
            HttpSecurity http,
            SecurityContextRepository securityContextRepository)
            throws Exception {

        http
            .cors(withDefaults())

            
            .csrf(csrf -> csrf.disable())

            .securityContext(security -> security
                    .securityContextRepository(
                            securityContextRepository
                    )
            )
            
            .exceptionHandling(exceptions -> exceptions
                    .authenticationEntryPoint(
                            new HttpStatusEntryPoint(
                                    HttpStatus.UNAUTHORIZED
                            )
                    )
            )

            .authorizeHttpRequests(auth -> auth

                    // Registration and login must be public
            		.requestMatchers(
            		        "/api/auth/register",
            		        "/api/auth/login",
            		        "/api/auth/csrf"
            		).permitAll()
            		
            		// Admin-only endpoints
                    .requestMatchers(
                            "/api/admin/**"
                    ).hasRole("ADMIN")

                    // Logged-in users
                    .requestMatchers(
                            "/api/auth/me",
                            "/api/user-movies/**",
                            "/api/recommendations/me"
                    ).authenticated()

                    // Existing public application endpoints
                    .anyRequest().permitAll()
            )

            .logout(logout -> logout
                    .logoutUrl("/api/auth/logout")
                    .invalidateHttpSession(true)
                    .clearAuthentication(true)
                    .deleteCookies("JSESSIONID")
                    .logoutSuccessHandler(
                            (request, response, authentication) -> {
                                response.setStatus(200);
                            }
                    )
            );

        return http.build();
    }
}