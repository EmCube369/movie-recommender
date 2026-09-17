package com.marshal.movierecommender.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;

import com.marshal.movierecommender.entity.Movie;

public interface MovieRepository extends JpaRepository<Movie, Integer> {

    Optional<Movie> findByMlMovieId(Integer mlMovieId);

    boolean existsByMlMovieId(Integer mlMovieId);
}