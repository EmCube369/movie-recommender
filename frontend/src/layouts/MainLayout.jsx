import { Outlet } from "react-router-dom";
import Navbar from "../components/Navbar";

function MainLayout() {
    return (
        <div className="min-h-screen bg-gray-950 text-gray-100">

            {/* Keyboard Skip Link */}
            <a
                href="#main-content"
                className="sr-only z-50 rounded-lg bg-blue-600 px-4 py-3 font-semibold text-white
                           focus:not-sr-only focus:fixed focus:left-4 focus:top-4
                           focus:outline-none focus:ring-2 focus:ring-blue-400
                           focus:ring-offset-2 focus:ring-offset-gray-950"
            >
                Skip to main content
            </a>

            <Navbar />

            <main
                id="main-content"
                tabIndex="-1"
                className="mx-auto w-full max-w-7xl px-4 py-6 sm:px-6 sm:py-8 lg:px-8"
            >
                <Outlet />
            </main>

        </div>
    );
}

export default MainLayout;