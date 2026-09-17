import axios from "axios";

const API_URL = "http://localhost:8080";

export const getMovies = () => {
    return axios.get(`${API_URL}/movies`);
}

export const getMoviesById = (id) => {
    return axios.get(`${API_URL}/movies/${id}`);
}

export const addMovie = (movie) => {
    return axios.post(`${API_URL}/movies`, movie);
}

export const updateMovie = (id, movie) => {
    return axios.put(`${API_URL}/movies/${id}`, movie);
}

export const deleteMovie = (id) => {
    return axios.delete(`${API_URL}/movies/${id}`);
}

export const getRecommendations = (userId, limit = 5) => {
    return axios.get(
        `${API_URL}/api/recommendations/users/${userId}`,
        {
            params: {
                limit
            }
        }
    );
}

export const getMyRecommendations = (limit = 10) => {
    return axios.get(
        `${API_URL}/api/recommendations/me`,
        {
            params: {
                limit
            },
            withCredentials: true
        }
    );
};