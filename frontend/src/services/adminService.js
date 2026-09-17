import axios from "axios";

const API_URL = "http://localhost:8080/api/admin";


export const searchMlMovies = (
    query,
    limit = 20
) => {
    return axios.get(
        `${API_URL}/ml-movies/search`,
        {
            params: {
                query,
                limit
            },
            withCredentials: true
        }
    );
};


export const addAdminMovie = (mlMovieId) => {
    return axios.post(
        `${API_URL}/movies`,
        {
            mlMovieId
        },
        {
            withCredentials: true
        }
    );
};


export const deleteAdminMovie = (movieId) => {
    return axios.delete(
        `${API_URL}/movies/${movieId}`,
        {
            withCredentials: true
        }
    );
};


export const getAdminUsers = () => {
    return axios.get(
        `${API_URL}/users`,
        {
            withCredentials: true
        }
    );
};


export const getAdminUser = (userId) => {
    return axios.get(
        `${API_URL}/users/${userId}`,
        {
            withCredentials: true
        }
    );
};


export const deleteAdminUser = (userId) => {
    return axios.delete(
        `${API_URL}/users/${userId}`,
        {
            withCredentials: true
        }
    );
};