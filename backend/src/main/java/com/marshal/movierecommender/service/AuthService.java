package com.marshal.movierecommender.service;

import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import com.marshal.movierecommender.dto.RegisterRequest;
import com.marshal.movierecommender.entity.Role;
import com.marshal.movierecommender.entity.User;
import com.marshal.movierecommender.exception.UsernameAlreadyExistsException;
import com.marshal.movierecommender.repository.UserRepository;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    public AuthService(
            UserRepository userRepository,
            PasswordEncoder passwordEncoder) {

        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
    }

    public User register(RegisterRequest request) {

        String username = request.getUsername().trim();

        if (userRepository.existsByUsername(username)) {

            throw new UsernameAlreadyExistsException(
                    "Username already exists"
            );
        }

        User user = new User();

        user.setUsername(username);

        user.setPassword(
                passwordEncoder.encode(
                        request.getPassword()
                )
        );

        user.setRole(Role.USER);

        return userRepository.save(user);
    }
    
    public User getUserByUsername(String username) {

        return userRepository
                .findByUsername(username)
                .orElseThrow(() ->
                        new IllegalStateException(
                                "Authenticated user not found"
                        )
                );
    }
}