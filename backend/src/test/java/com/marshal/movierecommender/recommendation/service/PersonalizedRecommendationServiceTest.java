package com.marshal.movierecommender.recommendation.service;

import static org.junit.jupiter.api.Assertions.assertEquals;
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
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.marshal.movierecommender.entity.Movie;
import com.marshal.movierecommender.entity.Role;
import com.marshal.movierecommender.entity.User;
import com.marshal.movierecommender.entity.UserMovieActivity;
import com.marshal.movierecommender.recommendation.client.MlRecommendationClient;
import com.marshal.movierecommender.recommendation.dto.MlPersonalizedRecommendationRequest;
import com.marshal.movierecommender.recommendation.dto.MlPersonalizedRecommendationResponse;
import com.marshal.movierecommender.recommendation.dto.MlRecommendedMovie;
import com.marshal.movierecommender.recommendation.dto.RecommendationResponse;
import com.marshal.movierecommender.recommendation.exception.InvalidRecommendationRequestException;
import com.marshal.movierecommender.repository.MovieRepository;
import com.marshal.movierecommender.repository.UserMovieActivityRepository;
import com.marshal.movierecommender.repository.UserRepository;

@ExtendWith(MockitoExtension.class)
class PersonalizedRecommendationServiceTest {

    @Mock
    private MlRecommendationClient mlRecommendationClient;

    @Mock
    private UserRepository userRepository;

    @Mock
    private UserMovieActivityRepository activityRepository;

    @Mock
    private MovieRepository movieRepository;

    @Mock
    private MlPersonalizedRecommendationResponse mlResponse;

    @Mock
    private MlRecommendedMovie mlMovie;

    private RecommendationService service;

    private User user;

    @BeforeEach
    void setUp() {

        service = new RecommendationService(
                mlRecommendationClient,
                userRepository,
                activityRepository,
                movieRepository
        );

        user = new User(
                1,
                "marshal",
                "password",
                Role.USER
        );
    }

    private Movie supportedMovie(
            Integer websiteId,
            Integer mlMovieId) {

        Movie movie = new Movie();
        movie.setId(websiteId);
        movie.setMlMovieId(mlMovieId);

        return movie;
    }

    @Test
    void personalizedRecommendations_WhenValidRatings_ShouldSendRatingsToMl() {

        Movie movie =
                supportedMovie(
                        10,
                        58559
                );

        UserMovieActivity activity =
                new UserMovieActivity(
                        1,
                        user,
                        movie,
                        4.5
                );

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(activityRepository
                .findRatedActivitiesWithMovie(1))
                .thenReturn(List.of(activity));

        when(mlResponse.recommendations())
                .thenReturn(List.of());

        when(mlRecommendationClient
                .getPersonalizedRecommendations(any()))
                .thenReturn(mlResponse);

        RecommendationResponse result =
                service.getPersonalizedRecommendations(
                        "marshal",
                        null
                );

        assertEquals(1, result.userId());
        assertEquals(0, result.count());

        ArgumentCaptor<MlPersonalizedRecommendationRequest> captor =
                ArgumentCaptor.forClass(
                        MlPersonalizedRecommendationRequest.class
                );

        verify(mlRecommendationClient)
                .getPersonalizedRecommendations(
                        captor.capture()
                );

        MlPersonalizedRecommendationRequest request =
                captor.getValue();

        assertEquals(10, request.limit());
        assertEquals(1, request.ratings().size());

        assertEquals(
                58559,
                request.ratings().get(0).movieId()
        );

        assertEquals(
                4.5,
                request.ratings().get(0).rating()
        );
    }

    @Test
    void personalizedRecommendations_ShouldIgnoreMovieWithoutMlMovieId() {

        Movie supported =
                supportedMovie(
                        10,
                        58559
                );

        Movie unsupported =
                supportedMovie(
                        11,
                        null
                );

        UserMovieActivity supportedActivity =
                new UserMovieActivity(
                        1,
                        user,
                        supported,
                        5.0
                );

        UserMovieActivity unsupportedActivity =
                new UserMovieActivity(
                        2,
                        user,
                        unsupported,
                        5.0
                );

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(activityRepository
                .findRatedActivitiesWithMovie(1))
                .thenReturn(
                        List.of(
                                supportedActivity,
                                unsupportedActivity
                        )
                );

        when(mlResponse.recommendations())
                .thenReturn(List.of());

        when(mlRecommendationClient
                .getPersonalizedRecommendations(any()))
                .thenReturn(mlResponse);

        service.getPersonalizedRecommendations(
                "marshal",
                5
        );

        ArgumentCaptor<MlPersonalizedRecommendationRequest> captor =
                ArgumentCaptor.forClass(
                        MlPersonalizedRecommendationRequest.class
                );

        verify(mlRecommendationClient)
                .getPersonalizedRecommendations(
                        captor.capture()
                );

        assertEquals(
                1,
                captor.getValue().ratings().size()
        );

        assertEquals(
                58559,
                captor.getValue()
                        .ratings()
                        .get(0)
                        .movieId()
        );
    }

    @Test
    void personalizedRecommendations_WhenNoRatings_ShouldThrowException() {

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(activityRepository
                .findRatedActivitiesWithMovie(1))
                .thenReturn(List.of());

        assertThrows(
                InvalidRecommendationRequestException.class,
                () -> service.getPersonalizedRecommendations(
                        "marshal",
                        10
                )
        );

        verify(
                mlRecommendationClient,
                never()
        ).getPersonalizedRecommendations(any());
    }

    @Test
    void personalizedRecommendations_WhenOnlyUnsupportedMoviesRated_ShouldThrowException() {

        Movie movie =
                supportedMovie(
                        10,
                        null
                );

        UserMovieActivity activity =
                new UserMovieActivity(
                        1,
                        user,
                        movie,
                        5.0
                );

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(activityRepository
                .findRatedActivitiesWithMovie(1))
                .thenReturn(List.of(activity));

        assertThrows(
                InvalidRecommendationRequestException.class,
                () -> service.getPersonalizedRecommendations(
                        "marshal",
                        10
                )
        );

        verify(
                mlRecommendationClient,
                never()
        ).getPersonalizedRecommendations(any());
    }

    @Test
    void personalizedRecommendations_WhenNoRatingIsFourOrHigher_ShouldThrowException() {

        Movie movie =
                supportedMovie(
                        10,
                        58559
                );

        UserMovieActivity activity =
                new UserMovieActivity(
                        1,
                        user,
                        movie,
                        3.5
                );

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(activityRepository
                .findRatedActivitiesWithMovie(1))
                .thenReturn(List.of(activity));

        assertThrows(
                InvalidRecommendationRequestException.class,
                () -> service.getPersonalizedRecommendations(
                        "marshal",
                        10
                )
        );

        verify(
                mlRecommendationClient,
                never()
        ).getPersonalizedRecommendations(any());
    }

    @Test
    void personalizedRecommendations_WhenUserDoesNotExist_ShouldThrowException() {

        when(userRepository.findByUsername("missinguser"))
                .thenReturn(Optional.empty());

        assertThrows(
                InvalidRecommendationRequestException.class,
                () -> service.getPersonalizedRecommendations(
                        "missinguser",
                        10
                )
        );

        verify(
                activityRepository,
                never()
        ).findRatedActivitiesWithMovie(any());

        verify(
                mlRecommendationClient,
                never()
        ).getPersonalizedRecommendations(any());
    }

    @Test
    void personalizedRecommendations_WhenUsernameBlank_ShouldThrowException() {

        assertThrows(
                InvalidRecommendationRequestException.class,
                () -> service.getPersonalizedRecommendations(
                        "   ",
                        10
                )
        );

        verify(
                userRepository,
                never()
        ).findByUsername(any());
    }

    @Test
    void personalizedRecommendations_WhenLimitInvalid_ShouldThrowException() {

        assertThrows(
                InvalidRecommendationRequestException.class,
                () -> service.getPersonalizedRecommendations(
                        "marshal",
                        0
                )
        );

        assertThrows(
                InvalidRecommendationRequestException.class,
                () -> service.getPersonalizedRecommendations(
                        "marshal",
                        51
                )
        );

        verify(
                userRepository,
                never()
        ).findByUsername(any());
    }
    
    @Test
    void personalizedRecommendations_ShouldMapMlMovieIdToWebsiteMovieId() {

        Movie ratedMovie =
                supportedMovie(
                        10,
                        58559
                );

        UserMovieActivity activity =
                new UserMovieActivity(
                        1,
                        user,
                        ratedMovie,
                        5.0
                );

        Movie catalogMovie = new Movie();
        catalogMovie.setId(25);
        catalogMovie.setMlMovieId(91529);
        catalogMovie.setTitle("The Dark Knight Rises");

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(activityRepository
                .findRatedActivitiesWithMovie(1))
                .thenReturn(List.of(activity));

        when(mlMovie.rank())
                .thenReturn(1);

        when(mlMovie.movieId())
                .thenReturn(91529);

        when(mlMovie.title())
                .thenReturn("The Dark Knight Rises");

        when(mlMovie.releaseYear())
                .thenReturn(2012);

        when(mlMovie.genres())
                .thenReturn(
                        List.of(
                                "Action",
                                "Crime",
                                "Drama"
                        )
                );

        when(mlMovie.score())
                .thenReturn(0.91);

        when(mlResponse.recommendations())
                .thenReturn(List.of(mlMovie));

        when(mlRecommendationClient
                .getPersonalizedRecommendations(any()))
                .thenReturn(mlResponse);

        when(movieRepository.findByMlMovieId(91529))
                .thenReturn(Optional.of(catalogMovie));

        RecommendationResponse result =
                service.getPersonalizedRecommendations(
                        "marshal",
                        10
                );

        assertEquals(1, result.count());

        assertEquals(
                25,
                result.recommendations()
                        .get(0)
                        .movieId()
        );

        assertEquals(
                91529,
                result.recommendations()
                        .get(0)
                        .mlMovieId()
        );

        assertEquals(
                "The Dark Knight Rises",
                result.recommendations()
                        .get(0)
                        .title()
        );

        verify(movieRepository)
                .findByMlMovieId(91529);
    }


    @Test
    void personalizedRecommendations_WhenRecommendedMovieNotInCatalog_ShouldUseNullWebsiteMovieId() {

        Movie ratedMovie =
                supportedMovie(
                        10,
                        58559
                );

        UserMovieActivity activity =
                new UserMovieActivity(
                        1,
                        user,
                        ratedMovie,
                        5.0
                );

        when(userRepository.findByUsername("marshal"))
                .thenReturn(Optional.of(user));

        when(activityRepository
                .findRatedActivitiesWithMovie(1))
                .thenReturn(List.of(activity));

        when(mlMovie.rank())
                .thenReturn(1);

        when(mlMovie.movieId())
                .thenReturn(99999);

        when(mlMovie.title())
                .thenReturn("ML Only Movie");

        when(mlMovie.releaseYear())
                .thenReturn(2020);

        when(mlMovie.genres())
                .thenReturn(List.of("Drama"));

        when(mlMovie.score())
                .thenReturn(0.85);

        when(mlResponse.recommendations())
                .thenReturn(List.of(mlMovie));

        when(mlRecommendationClient
                .getPersonalizedRecommendations(any()))
                .thenReturn(mlResponse);

        when(movieRepository.findByMlMovieId(99999))
                .thenReturn(Optional.empty());

        RecommendationResponse result =
                service.getPersonalizedRecommendations(
                        "marshal",
                        10
                );

        assertEquals(1, result.count());

        assertEquals(
                null,
                result.recommendations()
                        .get(0)
                        .movieId()
        );

        assertEquals(
                99999,
                result.recommendations()
                        .get(0)
                        .mlMovieId()
        );

        verify(movieRepository)
                .findByMlMovieId(99999);
    }
}