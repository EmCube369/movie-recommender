package com.marshal.movierecommender.admin.service;

import java.util.List;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import com.marshal.movierecommender.admin.dto.AdminUserResponse;
import com.marshal.movierecommender.entity.User;
import com.marshal.movierecommender.exception.UserNotFoundException;
import com.marshal.movierecommender.repository.UserRepository;
import com.marshal.movierecommender.entity.Role;
import com.marshal.movierecommender.exception.AdminUserDeletionException;
import com.marshal.movierecommender.repository.UserMovieActivityRepository;

@Service
public class AdminUserService {

    private final UserRepository userRepository;
    private final UserMovieActivityRepository userMovieActivityRepository;

    public AdminUserService(
            UserRepository userRepository,
            UserMovieActivityRepository userMovieActivityRepository
    ) {
        this.userRepository = userRepository;
        this.userMovieActivityRepository =
                userMovieActivityRepository;
    }


    public List<AdminUserResponse> getAllUsers() {

        return userRepository
                .findAll()
                .stream()
                .map(this::toResponse)
                .toList();
    }


    public AdminUserResponse getUserById(
            Integer id
    ) {

        User user = userRepository
                .findById(id)
                .orElseThrow(() ->
                        new UserNotFoundException(
                                "User with id "
                                        + id
                                        + " not found."
                        )
                );

        return toResponse(user);
    }


    private AdminUserResponse toResponse(
            User user
    ) {

        return new AdminUserResponse(
                user.getId(),
                user.getUsername(),
                user.getRole().name()
        );
    }
    
    @Transactional
    public void deleteUser(
            Integer userId,
            String currentUsername
    ) {

        User targetUser = userRepository
                .findById(userId)
                .orElseThrow(() ->
                        new UserNotFoundException(
                                "User with id "
                                        + userId
                                        + " not found."
                        )
                );

        if (targetUser.getUsername().equals(currentUsername)) {
            throw new AdminUserDeletionException(
                    "You cannot delete your own account."
            );
        }

        if (targetUser.getRole() == Role.ADMIN) {
            throw new AdminUserDeletionException(
                    "Admin accounts cannot be deleted through this endpoint."
            );
        }

        userMovieActivityRepository
                .deleteByUserId(userId);

        userRepository.delete(targetUser);
    }
}