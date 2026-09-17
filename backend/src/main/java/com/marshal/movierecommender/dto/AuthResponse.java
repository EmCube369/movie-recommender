package com.marshal.movierecommender.dto;

public class AuthResponse {

    private Integer id;
    private String username;
    private String role;
    private String message;

    public AuthResponse() {
    }

    public AuthResponse(
            Integer id,
            String username,
            String role,
            String message) {

        this.id = id;
        this.username = username;
        this.role = role;
        this.message = message;
    }

    public Integer getId() {
        return id;
    }

    public String getUsername() {
        return username;
    }

    public String getRole() {
        return role;
    }

    public String getMessage() {
        return message;
    }
}