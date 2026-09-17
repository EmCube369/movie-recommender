package com.marshal.movierecommender.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertSame;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.marshal.movierecommender.entity.Movie;
import com.marshal.movierecommender.entity.Role;
import com.marshal.movierecommender.entity.User;
import com.marshal.movierecommender.entity.UserMovieActivity;
import com.marshal.movierecommender.repository.MovieRepository;
import com.marshal.movierecommender.repository.UserMovieActivityRepository;
import com.marshal.movierecommender.repository.UserRepository;

import org.springframework.security.core.userdetails.UsernameNotFoundException;

import com.marshal.movierecommender.exception.MovieNotFoundException;

@ExtendWith(MockitoExtension.class)
class UserMovieActivityServiceTest {

    @Mock
    private UserMovieActivityRepository activityRepository;

    @Mock
    private UserRepository userRepository;

    @Mock
    private MovieRepository movieRepository;

    private UserMovieActivityService service;

    private User user;
    private Movie movie;

    @BeforeEach
    void setUp() {

        service = new UserMovieActivityService(
                activityRepository,
                userRepository,
                movieRepository
        );

        user = new User(
                1,
                "marshal",
                "password",
                Role.USER
        );

        movie = new Movie();
        movie.setId(10);
        movie.setTitle("Inception");
        movie.setGenre("Sci-Fi");
        movie.setReleaseYear(2010);
        movie.setTmdbRating(8.8);
        movie.setMlMovieId(79132);
    }

    @Test
    void markWatched_WhenNoActivityExists_ShouldCreateActivity() {

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(movieRepository.findById(10))
                .thenReturn(Optional.of(movie));

        when(activityRepository
                .findByUserIdAndMovieId(1, 10))
                .thenReturn(Optional.empty());

        when(activityRepository.save(any(UserMovieActivity.class)))
                .thenAnswer(invocation ->
                        invocation.getArgument(0)
                );

        UserMovieActivity result =
                service.markWatched(
                        "marshal",
                        10
                );

        assertSame(user, result.getUser());
        assertSame(movie, result.getMovie());
        assertNull(result.getRating());

        verify(activityRepository)
                .save(any(UserMovieActivity.class));
    }

    @Test
    void markWatched_WhenActivityAlreadyExists_ShouldReturnExistingActivity() {

        UserMovieActivity existing =
                new UserMovieActivity(
                        5,
                        user,
                        movie,
                        4.5
                );

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(movieRepository.findById(10))
                .thenReturn(Optional.of(movie));

        when(activityRepository
                .findByUserIdAndMovieId(1, 10))
                .thenReturn(Optional.of(existing));

        UserMovieActivity result =
                service.markWatched(
                        "marshal",
                        10
                );

        assertSame(existing, result);
        assertEquals(4.5, result.getRating());

        verify(activityRepository, never())
                .save(any(UserMovieActivity.class));
    }

    @Test
    void rateMovie_WhenActivityExists_ShouldUpdateRating() {

        UserMovieActivity existing =
                new UserMovieActivity(
                        5,
                        user,
                        movie,
                        3.0
                );

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(movieRepository.findById(10))
                .thenReturn(Optional.of(movie));

        when(activityRepository
                .findByUserIdAndMovieId(1, 10))
                .thenReturn(Optional.of(existing));

        when(activityRepository.save(existing))
                .thenReturn(existing);

        UserMovieActivity result =
                service.rateMovie(
                        "marshal",
                        10,
                        4.5
                );

        assertEquals(4.5, result.getRating());

        verify(activityRepository)
                .save(existing);
    }

    @Test
    void rateMovie_WhenActivityDoesNotExist_ShouldCreateActivity() {

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(movieRepository.findById(10))
                .thenReturn(Optional.of(movie));

        when(activityRepository
                .findByUserIdAndMovieId(1, 10))
                .thenReturn(Optional.empty());

        when(activityRepository.save(any(UserMovieActivity.class)))
                .thenAnswer(invocation ->
                        invocation.getArgument(0)
                );

        UserMovieActivity result =
                service.rateMovie(
                        "marshal",
                        10,
                        5.0
                );

        assertSame(user, result.getUser());
        assertSame(movie, result.getMovie());
        assertEquals(5.0, result.getRating());
    }

    @Test
    void rateMovie_WhenRatingBelowOne_ShouldThrowException() {

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> service.rateMovie(
                                "marshal",
                                10,
                                0.5
                        )
                );

        assertEquals(
                "Rating must be between 1 and 5",
                exception.getMessage()
        );

        verify(activityRepository, never())
                .save(any());
    }

    @Test
    void rateMovie_WhenRatingAboveFive_ShouldThrowException() {

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> service.rateMovie(
                                "marshal",
                                10,
                                5.5
                        )
                );

        assertEquals(
                "Rating must be between 1 and 5",
                exception.getMessage()
        );

        verify(activityRepository, never())
                .save(any());
    }

    @Test
    void rateMovie_WhenRatingIsNull_ShouldThrowException() {

        assertThrows(
                IllegalArgumentException.class,
                () -> service.rateMovie(
                        "marshal",
                        10,
                        null
                )
        );

        verify(activityRepository, never())
                .save(any());
    }
    
    @Test
    void markWatched_WhenUserDoesNotExist_ShouldThrowException() {

        when(userRepository.findByUsername("missinguser"))
                .thenReturn(Optional.empty());

        UsernameNotFoundException exception =
                assertThrows(
                        UsernameNotFoundException.class,
                        () -> service.markWatched(
                                "missinguser",
                                10
                        )
                );

        assertEquals(
                "User not found: missinguser",
                exception.getMessage()
        );

        verify(movieRepository, never())
                .findById(any());

        verify(activityRepository, never())
                .save(any());
    }


    @Test
    void markWatched_WhenMovieDoesNotExist_ShouldThrowException() {

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(movieRepository.findById(999))
                .thenReturn(Optional.empty());

        MovieNotFoundException exception =
                assertThrows(
                        MovieNotFoundException.class,
                        () -> service.markWatched(
                                "marshal",
                                999
                        )
                );

        assertEquals(
                "Movie not found with id: 999",
                exception.getMessage()
        );

        verify(activityRepository, never())
                .save(any());
    }


    @Test
    void getActivity_WhenActivityExists_ShouldReturnActivity() {

        UserMovieActivity existing =
                new UserMovieActivity(
                        5,
                        user,
                        movie,
                        4.0
                );

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(movieRepository.findById(10))
                .thenReturn(Optional.of(movie));

        when(activityRepository
                .findByUserIdAndMovieId(1, 10))
                .thenReturn(Optional.of(existing));

        Optional<UserMovieActivity> result =
                service.getActivity(
                        "marshal",
                        10
                );

        assertEquals(true, result.isPresent());
        assertSame(existing, result.get());
    }


    @Test
    void getActivity_WhenNoActivityExists_ShouldReturnEmpty() {

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(movieRepository.findById(10))
                .thenReturn(Optional.of(movie));

        when(activityRepository
                .findByUserIdAndMovieId(1, 10))
                .thenReturn(Optional.empty());

        Optional<UserMovieActivity> result =
                service.getActivity(
                        "marshal",
                        10
                );

        assertEquals(true, result.isEmpty());
    }


    @Test
    void getActivity_WhenMovieDoesNotExist_ShouldThrowException() {

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(movieRepository.findById(999))
                .thenReturn(Optional.empty());

        assertThrows(
                MovieNotFoundException.class,
                () -> service.getActivity(
                        "marshal",
                        999
                )
        );

        verify(activityRepository, never())
                .findByUserIdAndMovieId(
                        any(),
                        any()
                );
    }
    
    @Test
    void getUserLibrary_WhenActivitiesExist_ShouldReturnLibrary() {

        UserMovieActivity activity =
                new UserMovieActivity(
                        5,
                        user,
                        movie,
                        4.5
                );

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(activityRepository.findByUserId(1))
                .thenReturn(List.of(activity));

        List<UserMovieActivity> result =
                service.getUserLibrary("marshal");

        assertEquals(1, result.size());
        assertSame(activity, result.get(0));

        verify(activityRepository)
                .findByUserId(1);
    }


    @Test
    void getUserLibrary_WhenNoActivitiesExist_ShouldReturnEmptyList() {

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(activityRepository.findByUserId(1))
                .thenReturn(List.of());

        List<UserMovieActivity> result =
                service.getUserLibrary("marshal");

        assertEquals(0, result.size());

        verify(activityRepository)
                .findByUserId(1);
    }


    @Test
    void getUserLibrary_WhenUserDoesNotExist_ShouldThrowException() {

        when(userRepository.findByUsername("missinguser"))
                .thenReturn(Optional.empty());

        assertThrows(
                UsernameNotFoundException.class,
                () -> service.getUserLibrary("missinguser")
        );

        verify(activityRepository, never())
                .findByUserId(any());
    }


    @Test
    void removeActivity_WhenActivityExists_ShouldDeleteAndReturnTrue() {

        UserMovieActivity existing =
                new UserMovieActivity(
                        5,
                        user,
                        movie,
                        4.0
                );

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(activityRepository
                .findByUserIdAndMovieId(1, 10))
                .thenReturn(Optional.of(existing));

        boolean result =
                service.removeActivity(
                        "marshal",
                        10
                );

        assertEquals(true, result);

        verify(activityRepository)
                .delete(existing);
    }


    @Test
    void removeActivity_WhenActivityDoesNotExist_ShouldReturnFalse() {

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(activityRepository
                .findByUserIdAndMovieId(1, 10))
                .thenReturn(Optional.empty());

        boolean result =
                service.removeActivity(
                        "marshal",
                        10
                );

        assertEquals(false, result);

        verify(activityRepository, never())
                .delete(any());
    }


    @Test
    void removeActivity_WhenUserDoesNotExist_ShouldThrowException() {

        when(userRepository.findByUsername("missinguser"))
                .thenReturn(Optional.empty());

        assertThrows(
                UsernameNotFoundException.class,
                () -> service.removeActivity(
                        "missinguser",
                        10
                )
        );

        verify(activityRepository, never())
                .findByUserIdAndMovieId(
                        any(),
                        any()
                );

        verify(activityRepository, never())
                .delete(any());
    }
    
}