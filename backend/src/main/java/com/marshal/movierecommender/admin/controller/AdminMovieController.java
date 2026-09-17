package com.marshal.movierecommender.admin.controller;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.marshal.movierecommender.admin.dto.AdminAddMovieRequest;
import com.marshal.movierecommender.admin.service.AdminMovieService;
import com.marshal.movierecommender.entity.Movie;

import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/admin/movies")
public class AdminMovieController {

    private final AdminMovieService adminMovieService;

    public AdminMovieController(
            AdminMovieService adminMovieService
    ) {
        this.adminMovieService = adminMovieService;
    }


    @PostMapping
    public ResponseEntity<Movie> addMovie(
            @Valid @RequestBody AdminAddMovieRequest request
    ) {

        Movie movie =
                adminMovieService.addMovie(
                        request.mlMovieId()
                );

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(movie);
    }


    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteMovie(
            @PathVariable Integer id
    ) {

        adminMovieService.deleteMovie(id);

        return ResponseEntity
                .noContent()
                .build();
    }
}