package com.marshal.movierecommender.repository;

import org.springframework.data.jpa.repository.JpaRepository;

import com.marshal.movierecommender.entity.Movie;

public interface MovieRepository extends JpaRepository<Movie, Integer> {

}
