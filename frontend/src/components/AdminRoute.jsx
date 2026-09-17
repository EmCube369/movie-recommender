import {
    Navigate,
    Outlet
} from "react-router-dom";

import { useAuth } from "../context/AuthContext";


function AdminRoute() {
    const {
        user,
        isAuthenticated,
        authLoading
    } = useAuth();


    if (authLoading) {
        return (
            <div className="flex min-h-[60vh] items-center justify-center">
                <p className="text-gray-400">
                    Checking admin access...
                </p>
            </div>
        );
    }


    if (!isAuthenticated) {
        return (
            <Navigate
                to="/login"
                replace
            />
        );
    }


    if (user?.role !== "ADMIN") {
        return (
            <Navigate
                to="/"
                replace
            />
        );
    }


    return <Outlet />;
}


export default AdminRoute;