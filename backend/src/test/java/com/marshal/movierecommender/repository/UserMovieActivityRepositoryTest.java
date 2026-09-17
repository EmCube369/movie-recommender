package com.marshal.movierecommender.repository;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;

import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest;
import org.springframework.boot.jdbc.test.autoconfigure.AutoConfigureTestDatabase;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.test.context.ActiveProfiles;

import com.marshal.movierecommender.entity.Movie;
import com.marshal.movierecommender.entity.Role;
import com.marshal.movierecommender.entity.User;
import com.marshal.movierecommender.entity.UserMovieActivity;

@DataJpaTest
@ActiveProfiles("test")
@AutoConfigureTestDatabase(
        replace = AutoConfigureTestDatabase.Replace.NONE
)
class UserMovieActivityRepositoryTest {

    @Autowired
    private UserMovieActivityRepository activityRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private MovieRepository movieRepository;

    @Test
    void shouldSaveWatchedMovieWithoutRating() {

        User user = createUser("watched_no_rating_user");
        Movie movie = createMovie(
                "Arrival",
                "Sci-Fi",
                2016,
                7.9
        );

        UserMovieActivity activity =
                new UserMovieActivity();

        activity.setUser(user);
        activity.setMovie(movie);
        activity.setRating(null);

        UserMovieActivity savedActivity =
                activityRepository.saveAndFlush(activity);

        assertThat(savedActivity.getId()).isNotNull();
        assertThat(savedActivity.getUser().getId())
                .isEqualTo(user.getId());
        assertThat(savedActivity.getMovie().getId())
                .isEqualTo(movie.getId());
        assertThat(savedActivity.getRating()).isNull();
    }

    @Test
    void shouldSaveWatchedMovieWithDecimalRating() {

        User user = createUser("decimal_rating_user");
        Movie movie = createMovie(
                "Blade Runner 2049",
                "Sci-Fi",
                2017,
                8.0
        );

        UserMovieActivity activity =
                new UserMovieActivity();

        activity.setUser(user);
        activity.setMovie(movie);
        activity.setRating(4.5);

        UserMovieActivity savedActivity =
                activityRepository.saveAndFlush(activity);

        assertThat(savedActivity.getId()).isNotNull();
        assertThat(savedActivity.getRating())
                .isEqualTo(4.5);
    }

    @Test
    void shouldFindActivitiesByUserId() {

        User user = createUser("activity_list_user");

        Movie movie1 = createMovie(
                "Inception Activity Test",
                "Sci-Fi",
                2010,
                8.8
        );

        Movie movie2 = createMovie(
                "Interstellar Activity Test",
                "Sci-Fi",
                2014,
                8.7
        );

        UserMovieActivity activity1 =
                new UserMovieActivity(
                        null,
                        user,
                        movie1,
                        4.5
                );

        UserMovieActivity activity2 =
                new UserMovieActivity(
                        null,
                        user,
                        movie2,
                        null
                );

        activityRepository.save(activity1);
        activityRepository.save(activity2);
        activityRepository.flush();

        List<UserMovieActivity> activities =
                activityRepository.findByUserId(
                        user.getId()
                );

        assertThat(activities).hasSize(2);

        assertThat(activities)
                .extracting(
                        activity ->
                                activity.getMovie().getTitle()
                )
                .containsExactlyInAnyOrder(
                        "Inception Activity Test",
                        "Interstellar Activity Test"
                );
    }

    @Test
    void shouldFindActivityByUserIdAndMovieId() {

        User user =
                createUser("find_activity_user");

        Movie movie = createMovie(
                "The Prestige Activity Test",
                "Drama",
                2006,
                8.5
        );

        UserMovieActivity activity =
                new UserMovieActivity(
                        null,
                        user,
                        movie,
                        5.0
                );

        activityRepository.saveAndFlush(activity);

        Optional<UserMovieActivity> result =
                activityRepository
                        .findByUserIdAndMovieId(
                                user.getId(),
                                movie.getId()
                        );

        assertThat(result).isPresent();
        assertThat(result.get().getRating())
                .isEqualTo(5.0);
        assertThat(result.get().getMovie().getId())
                .isEqualTo(movie.getId());
    }

    @Test
    void shouldCheckIfUserMovieActivityExists() {

        User user =
                createUser("activity_exists_user");

        Movie movie = createMovie(
                "Memento Activity Test",
                "Thriller",
                2000,
                8.4
        );

        UserMovieActivity activity =
                new UserMovieActivity(
                        null,
                        user,
                        movie,
                        4.0
                );

        activityRepository.saveAndFlush(activity);

        boolean exists =
                activityRepository
                        .existsByUserIdAndMovieId(
                                user.getId(),
                                movie.getId()
                        );

        assertThat(exists).isTrue();
    }

    @Test
    void shouldRejectDuplicateUserMovieActivity() {

        User user =
                createUser("duplicate_activity_user");

        Movie movie = createMovie(
                "Duplicate Activity Movie",
                "Drama",
                2020,
                7.5
        );

        UserMovieActivity firstActivity =
                new UserMovieActivity(
                        null,
                        user,
                        movie,
                        4.0
                );

        activityRepository.saveAndFlush(firstActivity);

        UserMovieActivity secondActivity =
                new UserMovieActivity(
                        null,
                        user,
                        movie,
                        4.5
                );

        assertThatThrownBy(
                () -> activityRepository
                        .saveAndFlush(secondActivity)
        ).isInstanceOf(
                DataIntegrityViolationException.class
        );
    }

    private User createUser(String username) {

        User user = new User();
        user.setUsername(username);
        user.setPassword("test-password");
        user.setRole(Role.USER);

        return userRepository.saveAndFlush(user);
    }

    private Movie createMovie(
            String title,
            String genre,
            Integer releaseYear,
            Double tmdbRating) {

        Movie movie = new Movie();
        movie.setTitle(title);
        movie.setGenre(genre);
        movie.setReleaseYear(releaseYear);
        movie.setTmdbRating(tmdbRating);

        return movieRepository.saveAndFlush(movie);
    }
}