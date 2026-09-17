import axios from "axios";

const API_URL = "http://localhost:8080/api/auth";

export const register = (username, password) => {
    return axios.post(
        `${API_URL}/register`,
        {
            username,
            password
        },
        {
            withCredentials: true
        }
    );
};

export const login = (username, password) => {
    return axios.post(
        `${API_URL}/login`,
        {
            username,
            password
        },
        {
            withCredentials: true
        }
    );
};

export const getCurrentUser = () => {
    return axios.get(
        `${API_URL}/me`,
        {
            withCredentials: true
        }
    );
};

export const logout = () => {
    return axios.post(
        `${API_URL}/logout`,
        {},
        {
            withCredentials: true
        }
    );
};

