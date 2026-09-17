package com.marshal.movierecommender.admin.dto;

public record AdminUserResponse(
        Integer id,
        String username,
        String role
) {
}