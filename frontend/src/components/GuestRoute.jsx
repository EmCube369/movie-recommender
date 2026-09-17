import {
    Navigate,
    Outlet
} from "react-router-dom";

import { useAuth } from "../context/AuthContext";


function GuestRoute() {
    const {
        isAuthenticated,
        authLoading
    } = useAuth();


    if (authLoading) {
        return (
            <div className="flex min-h-[60vh] items-center justify-center">
                <p className="text-gray-400">
                    Checking authentication...
                </p>
            </div>
        );
    }


    if (isAuthenticated) {
        return (
            <Navigate
                to="/"
                replace
            />
        );
    }


    return <Outlet />;
}

export default GuestRoute;