package com.marshal.movierecommender.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import com.marshal.movierecommender.entity.UserMovieActivity;

public interface UserMovieActivityRepository
        extends JpaRepository<UserMovieActivity, Integer> {

    List<UserMovieActivity> findByUserId(Integer userId);

    List<UserMovieActivity> findByUserIdAndRatingIsNotNull(
            Integer userId);

    @Query("""
            SELECT a
            FROM UserMovieActivity a
            JOIN FETCH a.movie
            WHERE a.user.id = :userId
              AND a.rating IS NOT NULL
            """)
    List<UserMovieActivity> findRatedActivitiesWithMovie(
            @Param("userId") Integer userId);

    Optional<UserMovieActivity> findByUserIdAndMovieId(
            Integer userId,
            Integer movieId);

    boolean existsByUserIdAndMovieId(
            Integer userId,
            Integer movieId);
    
    void deleteByUserId(Integer userId);
    
    boolean existsByMovieId(Integer movieId);
    
}