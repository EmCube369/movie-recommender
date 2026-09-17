import {
    useEffect,
    useState
} from "react";

import {
    getCurrentUser,
    login as loginRequest,
    logout as logoutRequest
} from "../services/authService";

import { AuthContext } from "./AuthContext";


export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [authLoading, setAuthLoading] = useState(true);


    useEffect(() => {
        const loadCurrentUser = async () => {
            try {
                const response = await getCurrentUser();

                setUser(response.data);
            } catch {
                setUser(null);
            } finally {
                setAuthLoading(false);
            }
        };

        loadCurrentUser();
    }, []);


    const login = async (username, password) => {
        const response = await loginRequest(
            username,
            password
        );

        setUser(response.data);

        return response.data;
    };


    const logout = async () => {
        try {
            await logoutRequest();
        } finally {
            setUser(null);
        }
    };


    const value = {
        user,
        authLoading,
        isAuthenticated: user !== null,
        login,
        logout
    };


    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}