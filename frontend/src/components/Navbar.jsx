import {
    useEffect,
    useRef,
    useState
} from "react";

import {
    Link,
    NavLink,
    useNavigate
} from "react-router-dom";

import { useAuth } from "../context/AuthContext";


function Navbar() {
    const [menuOpen, setMenuOpen] = useState(false);

    const menuButtonRef = useRef(null);

    const navigate = useNavigate();

    const {
        user,
        isAuthenticated,
        logout
    } = useAuth();

    const focusClasses =
        "focus-visible:outline-none focus-visible:ring-2 " +
        "focus-visible:ring-blue-500 focus-visible:ring-offset-2 " +
        "focus-visible:ring-offset-gray-900";


    const getNavLinkClass = ({ isActive }) =>
        `rounded-md px-3 py-2 text-sm font-medium transition-colors
        motion-reduce:transition-none sm:text-base
        ${focusClasses}
        ${isActive
            ? "bg-gray-800 text-white"
            : "text-gray-300 hover:bg-gray-800 hover:text-white"
        }`;


    const getMobileNavLinkClass = ({ isActive }) =>
        `block rounded-lg px-4 py-3 text-sm font-medium transition-colors
        motion-reduce:transition-none
        ${focusClasses}
        ${isActive
            ? "bg-gray-800 text-white"
            : "text-gray-300 hover:bg-gray-800 hover:text-white"
        }`;


    const closeMenu = () => {
        setMenuOpen(false);
    };

    const handleLogout = async () => {
        await logout();

        closeMenu();

        navigate("/");
    };


    /*
     * Allow keyboard users to close
     * the mobile navigation with Escape.
     */
    useEffect(() => {
        if (!menuOpen) {
            return;
        }

        const handleEscape = (event) => {
            if (event.key === "Escape") {
                setMenuOpen(false);

                menuButtonRef.current?.focus();
            }
        };

        document.addEventListener(
            "keydown",
            handleEscape
        );

        return () => {
            document.removeEventListener(
                "keydown",
                handleEscape
            );
        };
    }, [menuOpen]);


    return (
        <header className="border-b border-gray-800 bg-gray-900">

            <nav
                className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8"
                aria-label="Main navigation"
            >

                <div className="flex h-16 items-center justify-between">

                    {/* Logo */}
                    <Link
                        to="/"
                        onClick={closeMenu}
                        className={`rounded-md text-lg font-bold text-white sm:text-xl ${focusClasses}`}
                    >
                        Movie
                        <span className="text-red-500">
                            Recommender
                        </span>
                    </Link>


                    {/* Desktop Navigation */}
                    <div className="hidden items-center gap-1 sm:flex sm:gap-2">

                        <NavLink
                            to="/"
                            end
                            className={getNavLinkClass}
                        >
                            Home
                        </NavLink>

                        <NavLink
                            to="/movies"
                            className={getNavLinkClass}
                        >
                            Movies
                        </NavLink>

                        <NavLink
                            to="/recommendations"
                            className={getNavLinkClass}
                        >
                            Recommendations
                        </NavLink>

                        {!isAuthenticated ? (
                            <>
                                <NavLink
                                    to="/login"
                                    className={getNavLinkClass}
                                >
                                    Login
                                </NavLink>

                                <NavLink
                                    to="/register"
                                    className={getNavLinkClass}
                                >
                                    Register
                                </NavLink>
                            </>
                        ) : (
                            <>

                                {user?.role === "ADMIN" && (
                                    <NavLink
                                        to="/admin"
                                        className={getNavLinkClass}
                                    >
                                        Admin
                                    </NavLink>
                                )}

                                <NavLink
                                    to="/profile"
                                    className={getNavLinkClass}
                                >
                                    Profile
                                </NavLink>

                                <span className="px-3 py-2 text-sm text-gray-400 sm:text-base">
                                    {user?.username}
                                </span>

                                <button
                                    type="button"
                                    onClick={handleLogout}
                                    className={`rounded-md px-3 py-2 text-sm font-medium
                                        text-gray-300 transition-colors hover:bg-gray-800
                                        hover:text-white motion-reduce:transition-none
                                        sm:text-base ${focusClasses}`}
                                >
                                    Logout
                                </button>
                            </>
                        )}

                    </div>


                    {/* Mobile Menu Button */}
                    <button
                        ref={menuButtonRef}
                        type="button"
                        onClick={() =>
                            setMenuOpen(
                                (current) => !current
                            )
                        }
                        aria-label={
                            menuOpen
                                ? "Close navigation menu"
                                : "Open navigation menu"
                        }
                        aria-expanded={menuOpen}
                        aria-controls="mobile-navigation"
                        className={`flex h-11 w-11 items-center justify-center rounded-lg
                                   border border-gray-700 text-gray-300 transition-colors
                                   hover:bg-gray-800 hover:text-white
                                   motion-reduce:transition-none sm:hidden
                                   ${focusClasses}`}
                    >
                        <span aria-hidden="true">
                            {menuOpen ? "✕" : "☰"}
                        </span>
                    </button>

                </div>


                {/* Mobile Navigation */}
                {menuOpen && (
                    <div
                        id="mobile-navigation"
                        className="space-y-1 border-t border-gray-800 py-3 sm:hidden"
                    >

                        <NavLink
                            to="/"
                            end
                            onClick={closeMenu}
                            className={getMobileNavLinkClass}
                        >
                            Home
                        </NavLink>

                        <NavLink
                            to="/movies"
                            onClick={closeMenu}
                            className={getMobileNavLinkClass}
                        >
                            Movies
                        </NavLink>

                        <NavLink
                            to="/recommendations"
                            onClick={closeMenu}
                            className={getMobileNavLinkClass}
                        >
                            Recommendations
                        </NavLink>

                        {!isAuthenticated ? (
                            <>
                                <NavLink
                                    to="/login"
                                    onClick={closeMenu}
                                    className={getMobileNavLinkClass}
                                >
                                    Login
                                </NavLink>

                                <NavLink
                                    to="/register"
                                    onClick={closeMenu}
                                    className={getMobileNavLinkClass}
                                >
                                    Register
                                </NavLink>
                            </>
                        ) : (
                            <>

                                {user?.role === "ADMIN" && (
                                    <NavLink
                                        to="/admin"
                                        onClick={closeMenu}
                                        className={getMobileNavLinkClass}
                                    >
                                        Admin
                                    </NavLink>
                                )}

                                <NavLink
                                    to="/profile"
                                    onClick={closeMenu}
                                    className={getMobileNavLinkClass}
                                >
                                    Profile
                                </NavLink>

                                <div className="px-4 py-3 text-sm text-gray-400">
                                    Signed in as{" "}
                                    <span className="font-medium text-white">
                                        {user?.username}
                                    </span>
                                </div>

                                <button
                                    type="button"
                                    onClick={handleLogout}
                                    className={`block w-full rounded-lg px-4 py-3 text-left
                                        text-sm font-medium text-gray-300 transition-colors
                                        hover:bg-gray-800 hover:text-white
                                        motion-reduce:transition-none ${focusClasses}`}
                                >
                                    Logout
                                </button>
                            </>
                        )}

                    </div>
                )}

            </nav>

        </header>
    );
}

export default Navbar;