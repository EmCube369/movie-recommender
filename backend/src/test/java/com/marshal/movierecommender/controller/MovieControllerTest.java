package com.marshal.movierecommender.controller;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.BDDMockito.given;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.never;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.put;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.List;

import org.junit.jupiter.api.Test;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import com.marshal.movierecommender.entity.Movie;
import com.marshal.movierecommender.exception.MovieNotFoundException;
import com.marshal.movierecommender.service.MovieService;

@WebMvcTest(MovieController.class)
class MovieControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private MovieService movieService;

//    @Test
//    void getAllMovies_shouldReturnMoviesAndStatus200() throws Exception {
//
//        // Arrange
//        List<Movie> movies = List.of(
//                new Movie(
//                        1,
//                        "Inception",
//                        "Sci-Fi",
//                        2010,
//                        8.8
//                ),
//                new Movie(
//                        2,
//                        "Interstellar",
//                        "Sci-Fi",
//                        2014,
//                        8.7
//                )
//        );
//
//        given(movieService.getAllMovies())
//                .willReturn(movies);
//
//        // Act + Assert
//        mockMvc.perform(get("/movies"))
//                .andExpect(status().isOk())
//                .andExpect(content()
//                        .contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
//
//                .andExpect(jsonPath("$.length()").value(2))
//
//                .andExpect(jsonPath("$[0].id").value(1))
//                .andExpect(jsonPath("$[0].title").value("Inception"))
//                .andExpect(jsonPath("$[0].genre").value("Sci-Fi"))
//                .andExpect(jsonPath("$[0].releaseYear").value(2010))
//                .andExpect(jsonPath("$[0].imdbRating").value(8.8))
//
//                .andExpect(jsonPath("$[1].id").value(2))
//                .andExpect(jsonPath("$[1].title").value("Interstellar"))
//                .andExpect(jsonPath("$[1].genre").value("Sci-Fi"))
//                .andExpect(jsonPath("$[1].releaseYear").value(2014))
//                .andExpect(jsonPath("$[1].imdbRating").value(8.7));
//
//        verify(movieService, times(1))
//                .getAllMovies();
//    }
    
    @Test
    void getAllMovies_whenNoMovies_shouldReturnEmptyListAndStatus200()
            throws Exception {

        // Arrange
        given(movieService.getAllMovies())
                .willReturn(List.of());

        // Act + Assert
        mockMvc.perform(get("/movies"))
                .andExpect(status().isOk())
                .andExpect(content()
                        .contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
                .andExpect(jsonPath("$.length()").value(0));

        verify(movieService, times(1))
                .getAllMovies();
    }
    
//    @Test
//    void getMovieById_whenMovieExists_shouldReturnMovieAndStatus200()
//            throws Exception {
//
//        // Arrange
//        Movie movie = new Movie(
//                1,
//                "Inception",
//                "Sci-Fi",
//                2010,
//                8.8
//        );
//
//        given(movieService.getMovieById(1))
//                .willReturn(movie);
//
//        // Act + Assert
//        mockMvc.perform(get("/movies/{id}", 1))
//                .andExpect(status().isOk())
//                .andExpect(content()
//                        .contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
//
//                .andExpect(jsonPath("$.id").value(1))
//                .andExpect(jsonPath("$.title").value("Inception"))
//                .andExpect(jsonPath("$.genre").value("Sci-Fi"))
//                .andExpect(jsonPath("$.releaseYear").value(2010))
//                .andExpect(jsonPath("$.imdbRating").value(8.8));
//
//        verify(movieService, times(1))
//                .getMovieById(1);
//    }
    
    @Test
    void getMovieById_whenMovieDoesNotExist_shouldReturn404()
            throws Exception {

        // Arrange
        given(movieService.getMovieById(99))
                .willThrow(
                        new MovieNotFoundException(
                                "Movie not found with id: 99"
                        )
                );

        // Act + Assert
        mockMvc.perform(get("/movies/{id}", 99))
                .andExpect(status().isNotFound())
                .andExpect(content()
                        .contentTypeCompatibleWith(MediaType.APPLICATION_JSON))

                .andExpect(jsonPath("$.status").value(404))
                .andExpect(jsonPath("$.message")
                        .value("Movie not found with id: 99"));

        verify(movieService, times(1))
                .getMovieById(99);
    }
    
//    @Test
//    void addMovie_whenValidMovie_shouldReturnCreatedMovieAndStatus201()
//            throws Exception {
//
//        // Arrange
//        Movie savedMovie = new Movie(
//                3,
//                "The Matrix",
//                "Sci-Fi",
//                1999,
//                8.7
//        );
//
//        given(movieService.addMovie(any(Movie.class)))
//                .willReturn(savedMovie);
//
//        String requestBody = """
//                {
//                    "title": "The Matrix",
//                    "genre": "Sci-Fi",
//                    "releaseYear": 1999,
//                    "imdbRating": 8.7
//                }
//                """;
//
//        // Act + Assert
//        mockMvc.perform(post("/movies")
//                        .contentType(MediaType.APPLICATION_JSON)
//                        .content(requestBody))
//
//                .andExpect(status().isCreated())
//                .andExpect(content()
//                        .contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
//
//                .andExpect(jsonPath("$.id").value(3))
//                .andExpect(jsonPath("$.title").value("The Matrix"))
//                .andExpect(jsonPath("$.genre").value("Sci-Fi"))
//                .andExpect(jsonPath("$.releaseYear").value(1999))
//                .andExpect(jsonPath("$.imdbRating").value(8.7));
//
//        verify(movieService, times(1))
//                .addMovie(any(Movie.class));
//    }
    
//    @Test
//    void addMovie_whenTitleIsBlank_shouldReturn400()
//            throws Exception {
//
//        String requestBody = """
//                {
//                    "title": "",
//                    "genre": "Sci-Fi",
//                    "releaseYear": 1999,
//                    "imdbRating": 8.7
//                }
//                """;
//
//        mockMvc.perform(post("/movies")
//                        .contentType(MediaType.APPLICATION_JSON)
//                        .content(requestBody))
//
//                .andExpect(status().isBadRequest())
//                .andExpect(content()
//                        .contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
//
//                .andExpect(jsonPath("$.title")
//                        .value("Title cannot be blank"));
//
//        verify(movieService, never())
//                .addMovie(any(Movie.class));
//    }
    
//    @Test
//    void updateMovie_whenMovieExists_shouldReturnUpdatedMovieAndStatus200()
//            throws Exception {
//
//        // Arrange
//        Movie updatedMovie = new Movie(
//                1,
//                "Inception Updated",
//                "Sci-Fi",
//                2010,
//                9.0
//        );
//
//        given(movieService.updateMovie(
//                org.mockito.ArgumentMatchers.eq(1),
//                any(Movie.class)))
//                .willReturn(updatedMovie);
//
//        String requestBody = """
//                {
//                    "title": "Inception Updated",
//                    "genre": "Sci-Fi",
//                    "releaseYear": 2010,
//                    "imdbRating": 9.0
//                }
//                """;
//
//        // Act + Assert
//        mockMvc.perform(put("/movies/{id}", 1)
//                        .contentType(MediaType.APPLICATION_JSON)
//                        .content(requestBody))
//
//                .andExpect(status().isOk())
//                .andExpect(content()
//                        .contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
//
//                .andExpect(jsonPath("$.id").value(1))
//                .andExpect(jsonPath("$.title").value("Inception Updated"))
//                .andExpect(jsonPath("$.genre").value("Sci-Fi"))
//                .andExpect(jsonPath("$.releaseYear").value(2010))
//                .andExpect(jsonPath("$.imdbRating").value(9.0));
//
//        verify(movieService, times(1))
//                .updateMovie(
//                        org.mockito.ArgumentMatchers.eq(1),
//                        any(Movie.class));
//    }
    
//    @Test
//    void updateMovie_whenMovieDoesNotExist_shouldReturn404()
//            throws Exception {
//
//        // Arrange
//        given(movieService.updateMovie(eq(99), any(Movie.class)))
//                .willThrow(
//                        new MovieNotFoundException(
//                                "Movie not found with id: 99"
//                        )
//                );
//
//        String requestBody = """
//                {
//                    "title": "Unknown Movie",
//                    "genre": "Drama",
//                    "releaseYear": 2000,
//                    "imdbRating": 7.5
//                }
//                """;
//
//        // Act + Assert
//        mockMvc.perform(put("/movies/{id}", 99)
//                        .contentType(MediaType.APPLICATION_JSON)
//                        .content(requestBody))
//
//                .andExpect(status().isNotFound())
//                .andExpect(content()
//                        .contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
//
//                .andExpect(jsonPath("$.status").value(404))
//                .andExpect(jsonPath("$.message")
//                        .value("Movie not found with id: 99"));
//
//        verify(movieService, times(1))
//                .updateMovie(eq(99), any(Movie.class));
//    }
    
//    @Test
//    void deleteMovie_whenMovieExists_shouldReturn204()
//            throws Exception {
//
//        mockMvc.perform(delete("/movies/{id}", 1))
//                .andExpect(status().isNoContent())
//                .andExpect(content().string(""));
//
//        verify(movieService, times(1))
//                .deleteMovie(1);
//    }
//    
//    @Test
//    void deleteMovie_whenMovieDoesNotExist_shouldReturn404()
//            throws Exception {
//
//        // Arrange
//        doThrow(
//                new MovieNotFoundException(
//                        "Movie not found with id: 99"
//                )
//        )
//        .when(movieService)
//        .deleteMovie(99);
//
//        // Act + Assert
//        mockMvc.perform(delete("/movies/{id}", 99))
//                .andExpect(status().isNotFound())
//                .andExpect(content()
//                        .contentTypeCompatibleWith(MediaType.APPLICATION_JSON))
//
//                .andExpect(jsonPath("$.status").value(404))
//                .andExpect(jsonPath("$.message")
//                        .value("Movie not found with id: 99"));
//
//        verify(movieService, times(1))
//                .deleteMovie(99);
//    }
//    
//    @Test
//    void addMovie_whenGenreIsBlank_shouldReturn400()
//            throws Exception {
//
//        String requestBody = """
//                {
//                    "title": "Inception",
//                    "genre": "",
//                    "releaseYear": 2010,
//                    "imdbRating": 8.8
//                }
//                """;
//
//        mockMvc.perform(post("/movies")
//                        .contentType(MediaType.APPLICATION_JSON)
//                        .content(requestBody))
//                .andExpect(status().isBadRequest())
//                .andExpect(jsonPath("$.genre")
//                        .value("Genre cannot be blank"));
//
//        verify(movieService, never())
//                .addMovie(any(Movie.class));
//    }
    
//    @Test
//    void addMovie_whenReleaseYearIsTooOld_shouldReturn400()
//            throws Exception {
//
//        String requestBody = """
//                {
//                    "title": "Old Movie",
//                    "genre": "Drama",
//                    "releaseYear": 1800,
//                    "imdbRating": 7.0
//                }
//                """;
//
//        mockMvc.perform(post("/movies")
//                        .contentType(MediaType.APPLICATION_JSON)
//                        .content(requestBody))
//                .andExpect(status().isBadRequest())
//                .andExpect(jsonPath("$.releaseYear")
//                        .value("Release year must be 1888 or later"));
//
//        verify(movieService, never())
//                .addMovie(any(Movie.class));
//    }
//    
//    @Test
//    void addMovie_whenImdbRatingIsBelowZero_shouldReturn400()
//            throws Exception {
//
//        String requestBody = """
//                {
//                    "title": "Test Movie",
//                    "genre": "Drama",
//                    "releaseYear": 2020,
//                    "imdbRating": -1.0
//                }
//                """;
//
//        mockMvc.perform(post("/movies")
//                        .contentType(MediaType.APPLICATION_JSON)
//                        .content(requestBody))
//                .andExpect(status().isBadRequest())
//                .andExpect(jsonPath("$.imdbRating")
//                        .value("IMDb rating cannot be less than 0"));
//
//        verify(movieService, never())
//                .addMovie(any(Movie.class));
//    }
//    
//    @Test
//    void addMovie_whenImdbRatingIsAboveTen_shouldReturn400()
//            throws Exception {
//
//        String requestBody = """
//                {
//                    "title": "Test Movie",
//                    "genre": "Drama",
//                    "releaseYear": 2020,
//                    "imdbRating": 11.0
//                }
//                """;
//
//        mockMvc.perform(post("/movies")
//                        .contentType(MediaType.APPLICATION_JSON)
//                        .content(requestBody))
//                .andExpect(status().isBadRequest())
//                .andExpect(jsonPath("$.imdbRating")
//                        .value("IMDb rating cannot be more than 10"));
//
//        verify(movieService, never())
//                .addMovie(any(Movie.class));
//    }
//    
//    @Test
//    void addMovie_whenRequiredFieldsAreMissing_shouldReturn400()
//            throws Exception {
//
//        String requestBody = """
//                {
//                    "title": "Incomplete Movie",
//                    "genre": "Drama"
//                }
//                """;
//
//        mockMvc.perform(post("/movies")
//                        .contentType(MediaType.APPLICATION_JSON)
//                        .content(requestBody))
//                .andExpect(status().isBadRequest())
//                .andExpect(jsonPath("$.releaseYear")
//                        .value("Release year cannot be null"))
//                .andExpect(jsonPath("$.imdbRating")
//                        .value("IMDb rating cannot be null"));
//
//        verify(movieService, never())
//                .addMovie(any(Movie.class));
//    }
//    
//    @Test
//    void updateMovie_whenRequestIsInvalid_shouldReturn400()
//            throws Exception {
//
//        String requestBody = """
//                {
//                    "title": "",
//                    "genre": "Drama",
//                    "releaseYear": 2020,
//                    "imdbRating": 8.0
//                }
//                """;
//
//        mockMvc.perform(put("/movies/{id}", 1)
//                        .contentType(MediaType.APPLICATION_JSON)
//                        .content(requestBody))
//                .andExpect(status().isBadRequest())
//                .andExpect(jsonPath("$.title")
//                        .value("Title cannot be blank"));
//
//        verify(movieService, never())
//                .updateMovie(eq(1), any(Movie.class));
//    }
    
    @Test
    void getMovieById_whenIdIsNotInteger_shouldReturn400()
            throws Exception {

        mockMvc.perform(get("/movies/{id}", "abc"))
                .andExpect(status().isBadRequest())
                .andExpect(content()
                        .contentTypeCompatibleWith(MediaType.APPLICATION_JSON))

                .andExpect(jsonPath("$.status").value(400))
                .andExpect(jsonPath("$.error")
                        .value("INVALID_PARAMETER_TYPE"))
                .andExpect(jsonPath("$.message")
                        .value("Parameter 'id' must be a valid integer."))
                .andExpect(jsonPath("$.path")
                        .value("/movies/abc"))
                .andExpect(jsonPath("$.timestamp").exists());

        verify(movieService, never())
                .getMovieById(any(Integer.class));
    }
    
}