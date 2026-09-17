import {
    Navigate,
    Outlet,
    useLocation
} from "react-router-dom";

import { useAuth } from "../context/AuthContext";


function ProtectedRoute() {
    const location = useLocation();

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


    if (!isAuthenticated) {
        return (
            <Navigate
                to="/login"
                replace
                state={{
                    from: location
                }}
            />
        );
    }


    return <Outlet />;
}

export default ProtectedRoute;