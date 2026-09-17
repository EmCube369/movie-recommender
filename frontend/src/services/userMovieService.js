import axios from "axios";

const API_URL = "http://localhost:8080";

export const getMovieActivity = (movieId) => {
    return axios.get(
        `${API_URL}/api/user-movies/${movieId}`,
        {
            withCredentials: true
        }
    );
};

export const markMovieWatched = (movieId) => {
    return axios.post(
        `${API_URL}/api/user-movies/${movieId}/watched`,
        {},
        {
            withCredentials: true
        }
    );
};

export const rateMovie = (movieId, rating) => {
    return axios.put(
        `${API_URL}/api/user-movies/${movieId}/rating`,
        {
            rating
        },
        {
            withCredentials: true
        }
    );
};

export const getUserLibrary = () => {
    return axios.get(
        `${API_URL}/api/user-movies`,
        {
            withCredentials: true
        }
    );
};

export const removeMovieActivity = (movieId) => {
    return axios.delete(
        `${API_URL}/api/user-movies/${movieId}`,
        {
            withCredentials: true
        }
    );
};