import {
    useEffect,
    useState
} from "react";

import { Link } from "react-router-dom";

import { getMovies } from "../services/movieService";
import {
    addAdminMovie,
    deleteAdminMovie,
    searchMlMovies,
    getAdminUsers,
    deleteAdminUser
} from "../services/adminService";
import { useAuth } from "../context/AuthContext";



function AdminDashboard() {

    const { user } = useAuth();

    const [users, setUsers] = useState([]);
    const [usersLoading, setUsersLoading] = useState(true);
    const [usersError, setUsersError] = useState("");
    const [userActionError, setUserActionError] = useState("");
    const [userSuccess, setUserSuccess] = useState("");

    const [deletingUserId, setDeletingUserId] = useState(null);

    const [movies, setMovies] = useState([]);
    const [moviesLoading, setMoviesLoading] = useState(true);
    const [moviesError, setMoviesError] = useState("");
    const [movieActionError, setMovieActionError] = useState("");
    const [movieSuccess, setMovieSuccess] = useState("");

    const [deletingMovieId, setDeletingMovieId] = useState(null);
    const [showMovieSearch, setShowMovieSearch] = useState(false);

    const [mlSearchQuery, setMlSearchQuery] = useState("");
    const [mlSearchResults, setMlSearchResults] = useState([]);

    const [mlSearchLoading, setMlSearchLoading] = useState(false);
    const [mlSearchError, setMlSearchError] = useState("");

    const [addingMlMovieId, setAddingMlMovieId] = useState(null);
    const [hasMlSearched, setHasMlSearched] = useState(false);

    const focusClasses =
        "focus-visible:outline-none focus-visible:ring-2 " +
        "focus-visible:ring-blue-500 focus-visible:ring-offset-2 " +
        "focus-visible:ring-offset-slate-950";


    const loadUsers = async () => {
        setUsersLoading(true);
        setUsersError("");

        try {
            const response = await getAdminUsers();

            setUsers(response.data);
        } catch (error) {
            console.error(
                "Error loading admin users:",
                error
            );

            setUsersError(
                "We couldn't load registered users."
            );
        } finally {
            setUsersLoading(false);
        }
    };


    useEffect(() => {
        let active = true;

        getAdminUsers()
            .then((response) => {
                if (!active) {
                    return;
                }

                setUsers(response.data);
                setUsersError("");
            })
            .catch((error) => {
                if (!active) {
                    return;
                }

                console.error(
                    "Error loading admin users:",
                    error
                );

                setUsersError(
                    "We couldn't load registered users."
                );
            })
            .finally(() => {
                if (active) {
                    setUsersLoading(false);
                }
            });

        return () => {
            active = false;
        };
    }, []);

    const loadMovies = async () => {
        setMoviesLoading(true);
        setMoviesError("");

        try {
            const response = await getMovies();

            setMovies(response.data);
        } catch (error) {
            console.error(
                "Error loading admin movie catalog:",
                error
            );

            setMoviesError(
                "We couldn't load the movie catalog."
            );
        } finally {
            setMoviesLoading(false);
        }
    };


    useEffect(() => {
        let active = true;

        getMovies()
            .then((response) => {
                if (!active) {
                    return;
                }

                setMovies(response.data);
                setMoviesError("");
            })
            .catch((error) => {
                if (!active) {
                    return;
                }

                console.error(
                    "Error loading admin movie catalog:",
                    error
                );

                setMoviesError(
                    "We couldn't load the movie catalog."
                );
            })
            .finally(() => {
                if (active) {
                    setMoviesLoading(false);
                }
            });

        return () => {
            active = false;
        };
    }, []);

    const handleDeleteUser = async (targetUser) => {

        setUserActionError("");
        setUserSuccess("");

        const confirmed = window.confirm(
            `Delete user "${targetUser.username}"? ` +
            "Their movie activity and ratings will also be removed."
        );

        if (!confirmed) {
            return;
        }

        setDeletingUserId(targetUser.id);
        setUserActionError("");
        setUserSuccess("");

        try {
            await deleteAdminUser(targetUser.id);

            setUsers((currentUsers) =>
                currentUsers.filter(
                    (currentUser) =>
                        currentUser.id !== targetUser.id
                )
            );

            setUserSuccess(
                `User "${targetUser.username}" was deleted.`
            );
        } catch (error) {
            console.error(
                "Error deleting admin user:",
                error
            );

            setUserActionError(
                error.response?.data?.message ??
                "Failed to delete the user."
            );
        } finally {
            setDeletingUserId(null);
        }
    };


    const handleDeleteMovie = async (movie) => {

        setMovieActionError("");
        setMovieSuccess("");

        const confirmed = window.confirm(
            `Remove "${movie.title}" from the catalog?`
        );

        if (!confirmed) {
            return;
        }

        setDeletingMovieId(movie.id);
        setMovieActionError("");
        setMovieSuccess("");

        try {
            await deleteAdminMovie(movie.id);

            setMovies((currentMovies) =>
                currentMovies.filter(
                    (currentMovie) =>
                        currentMovie.id !== movie.id
                )
            );

            setMovieSuccess(
                `"${movie.title}" was removed from the catalog.`
            );
        } catch (error) {
            console.error(
                "Error deleting admin movie:",
                error
            );

            setMovieActionError(
                error.response?.data?.message ??
                "Failed to remove the movie."
            );
        } finally {
            setDeletingMovieId(null);
        }
    };

    const handleMlMovieSearch = async (event) => {
        event.preventDefault();

        setHasMlSearched(true);
        setMovieActionError("");
        setMovieSuccess("");

        const query = mlSearchQuery.trim();

        if (!query) {
            setMlSearchError(
                "Enter a movie title to search."
            );

            setMlSearchResults([]);
            return;
        }


        setMlSearchLoading(true);
        setMlSearchError("");
        setMovieSuccess("");

        try {
            const response = await searchMlMovies(
                query,
                20
            );

            setMlSearchResults(
                response.data.movies ?? []
            );
        } catch (error) {
            console.error(
                "Error searching ML movie catalog:",
                error
            );

            setMlSearchResults([]);

            setMlSearchError(
                error.response?.data?.message ??
                "Failed to search the recommendation catalog."
            );
        } finally {
            setMlSearchLoading(false);
        }
    };

    const handleToggleMovieSearch = () => {
        setShowMovieSearch((current) => {
            const next = !current;

            if (!next) {
                setMlSearchQuery("");
                setMlSearchResults([]);
                setMlSearchError("");
                setHasMlSearched(false);
            }

            return next;
        });
    };

    const handleAddMovie = async (mlMovie) => {
        setAddingMlMovieId(mlMovie.movieId);
        setMovieActionError("");
        setMovieSuccess("");

        try {
            const response = await addAdminMovie(
                mlMovie.movieId
            );

            const newMovie = response.data;

            setMovies((currentMovies) => [
                ...currentMovies,
                newMovie
            ]);

            setMovieSuccess(
                `"${newMovie.title}" was added to the catalog.`
            );
        } catch (error) {
            console.error(
                "Error adding admin movie:",
                error
            );

            setMovieActionError(
                error.response?.data?.message ??
                "Failed to add the movie."
            );
        } finally {
            setAddingMlMovieId(null);
        }
    };

    return (
        <section className="py-6 sm:py-8">

            {/* Page Header */}
            <div className="mb-8">

                <p className="mb-2 text-sm font-semibold uppercase
                              tracking-widest text-blue-400">
                    Administration
                </p>

                <h1 className="text-3xl font-bold text-white sm:text-4xl">
                    Admin Dashboard
                </h1>

                <p className="mt-3 max-w-2xl text-sm leading-6
                              text-slate-400 sm:text-base">
                    Manage the application movie catalog and
                    registered users.
                </p>

            </div>


            {/* Management Overview */}
            <div className="mb-10 grid gap-5 md:grid-cols-2">

                {/* Movie Management */}
                <a
                    href="#movie-management"
                    className={`group rounded-2xl border border-slate-800
                                bg-slate-900/80 p-6 transition
                                hover:border-blue-500/50
                                hover:bg-slate-900
                                motion-reduce:transition-none
                                ${focusClasses}`}
                >

                    <div className="flex items-start justify-between gap-4">

                        <div>
                            <p className="text-sm font-semibold uppercase
                                          tracking-widest text-blue-400">
                                Catalog
                            </p>

                            <h2 className="mt-2 text-xl font-semibold text-white">
                                Movie Management
                            </h2>

                            <p className="mt-3 text-sm leading-6 text-slate-400">
                                Search recommendation-supported movies,
                                add them to the application catalog,
                                and remove unused catalog movies.
                            </p>

                            <p className="mt-4 text-sm font-medium text-slate-300">
                                {moviesLoading
                                    ? "Loading catalog..."
                                    : `${movies.length} ${movies.length === 1 ? "movie" : "movies"
                                    } in catalog`}
                            </p>

                        </div>

                        <span
                            aria-hidden="true"
                            className="text-2xl text-slate-500
                                       transition group-hover:text-blue-400
                                       motion-reduce:transition-none"
                        >
                            →
                        </span>

                    </div>

                </a>


                {/* User Management */}
                <a
                    href="#user-management"
                    className={`group rounded-2xl border border-slate-800
                                bg-slate-900/80 p-6 transition
                                hover:border-blue-500/50
                                hover:bg-slate-900
                                motion-reduce:transition-none
                                ${focusClasses}`}
                >

                    <div className="flex items-start justify-between gap-4">

                        <div>
                            <p className="text-sm font-semibold uppercase
                                          tracking-widest text-blue-400">
                                Accounts
                            </p>

                            <h2 className="mt-2 text-xl font-semibold text-white">
                                User Management
                            </h2>

                            <p className="mt-3 text-sm leading-6 text-slate-400">
                                View registered users and perform
                                basic account management.
                            </p>

                            <p className="mt-4 text-sm font-medium text-slate-300">
                                {usersLoading
                                    ? "Loading users..."
                                    : `${users.length} registered ${users.length === 1 ? "user" : "users"
                                    }`}
                            </p>
                        </div>

                        <span
                            aria-hidden="true"
                            className="text-2xl text-slate-500
                                       transition group-hover:text-blue-400
                                       motion-reduce:transition-none"
                        >
                            →
                        </span>

                    </div>

                </a>

            </div>


            {/* Movie Management Section */}
            <section
                id="movie-management"
                aria-labelledby="movie-management-heading"
                className="scroll-mt-24"
            >

                <div className="mb-5">

                    <p className="text-sm font-semibold uppercase
                                  tracking-widest text-blue-400">
                        Movie Catalog
                    </p>

                    <h2
                        id="movie-management-heading"
                        className="mt-1 text-2xl font-bold text-white"
                    >
                        Movie Management
                    </h2>

                    <p className="mt-2 max-w-2xl text-sm leading-6
                                  text-slate-400">
                        Manage movies available to users in the application.
                    </p>

                </div>


                <div
                    aria-busy={moviesLoading}
                    className="rounded-2xl border border-slate-800
                            bg-slate-900/70 p-5 sm:p-6"
                >

                    <div className="flex flex-col gap-4
                                    sm:flex-row sm:items-center
                                    sm:justify-between">

                        <div>
                            <h3 className="text-lg font-semibold text-white">
                                Application Catalog
                            </h3>

                            <p className="mt-1 text-sm text-slate-400">
                                Current movies available in the website.
                            </p>
                        </div>

                        <button
                            type="button"
                            onClick={handleToggleMovieSearch}
                            className={`rounded-xl bg-blue-600 px-5 py-3
                                        text-sm font-semibold text-white
                                        transition-colors hover:bg-blue-500
                                        ${focusClasses}`}
                        >
                            {showMovieSearch
                                ? "Close Search"
                                : "Add Movie"}
                        </button>

                    </div>

                    {showMovieSearch && (

                        <div className="mt-6 rounded-2xl border border-blue-500/20 bg-slate-950/50 p-5">

                            <div className="mb-5">

                                <h4 className="text-lg font-semibold text-white">
                                    Add from Recommendation Catalog
                                </h4>

                                <p className="mt-1 text-sm leading-6 text-slate-400">
                                    Search the ML movie dataset and add a supported
                                    movie to the website catalog.
                                </p>

                            </div>


                            {/* Search Form */}
                            <form
                                onSubmit={handleMlMovieSearch}
                                className="flex flex-col gap-3 sm:flex-row"
                            >

                                <div className="flex-1">

                                    <label
                                        htmlFor="admin-ml-movie-search"
                                        className="sr-only"
                                    >
                                        Search ML movies
                                    </label>

                                    <input
                                        id="admin-ml-movie-search"
                                        type="search"
                                        value={mlSearchQuery}
                                        onChange={(event) =>
                                            setMlSearchQuery(
                                                event.target.value
                                            )
                                        }
                                        placeholder="Search by movie title..."
                                        disabled={mlSearchLoading}
                                        className="w-full rounded-xl border
                                                border-slate-700 bg-slate-950
                                                px-4 py-3 text-white outline-none
                                                placeholder:text-slate-500
                                                focus:border-blue-500
                                                focus:ring-2
                                                focus:ring-blue-500/30
                                                disabled:opacity-60"
                                    />

                                </div>


                                <button
                                    type="submit"
                                    disabled={mlSearchLoading}
                                    className={`rounded-xl bg-blue-600 px-6 py-3
                                                font-semibold text-white
                                                transition-colors hover:bg-blue-500
                                                disabled:cursor-not-allowed
                                                disabled:opacity-50
                                                ${focusClasses}`}
                                >
                                    {mlSearchLoading
                                        ? "Searching..."
                                        : "Search"}
                                </button>

                            </form>


                            {/* Search Error */}
                            {mlSearchError && (
                                <div
                                    role="alert"
                                    className="mt-4 rounded-xl border
                                                border-red-500/30 bg-red-500/10
                                                px-4 py-3"
                                >
                                    <p className="text-sm text-red-300">
                                        {mlSearchError}
                                    </p>
                                </div>
                            )}


                            {/* Search Results */}
                            {!mlSearchLoading &&
                                !mlSearchError &&
                                mlSearchResults.length > 0 && (

                                    <div className="mt-5 overflow-hidden
                                                    rounded-xl border
                                                    border-slate-800">

                                        <div className="border-b border-slate-800
                                                        bg-slate-900/70
                                                        px-4 py-3">

                                            <p className="text-sm text-slate-400">
                                                {mlSearchResults.length} results
                                            </p>

                                        </div>


                                        <div className="divide-y divide-slate-800">

                                            {mlSearchResults.map((mlMovie) => {

                                                const alreadyAdded =
                                                    movies.some(
                                                        (movie) =>
                                                            movie.mlMovieId ===
                                                            mlMovie.movieId
                                                    );

                                                const adding =
                                                    addingMlMovieId ===
                                                    mlMovie.movieId;

                                                return (
                                                    <div
                                                        key={mlMovie.movieId}
                                                        className="flex flex-col gap-4
                                                                    p-4 sm:flex-row
                                                                    sm:items-center
                                                                    sm:justify-between"
                                                    >

                                                        {/* Movie Information */}
                                                        <div className="min-w-0">

                                                            <h5 className="font-semibold
                                                                        text-white">
                                                                {mlMovie.title}
                                                            </h5>


                                                            <div className="mt-2 flex
                                                    flex-wrap gap-2">

                                                                <span className="rounded-full
                                                         border
                                                         border-slate-700
                                                         px-2.5 py-1
                                                         text-xs
                                                         text-slate-300">
                                                                    {mlMovie.releaseYear ??
                                                                        "Year N/A"}
                                                                </span>


                                                                <span className="rounded-full
                                                         border
                                                         border-blue-500/30
                                                         bg-blue-500/10
                                                         px-2.5 py-1
                                                         text-xs
                                                         text-blue-300">
                                                                    ML #{mlMovie.movieId}
                                                                </span>


                                                                {mlMovie.genres?.map(
                                                                    (genre) => (
                                                                        <span
                                                                            key={genre}
                                                                            className="rounded-full
                                                               border
                                                               border-slate-700
                                                               px-2.5 py-1
                                                               text-xs
                                                               text-slate-300"
                                                                        >
                                                                            {genre}
                                                                        </span>
                                                                    )
                                                                )}

                                                            </div>

                                                        </div>


                                                        {/* Add */}
                                                        <button
                                                            type="button"
                                                            onClick={() =>
                                                                handleAddMovie(
                                                                    mlMovie
                                                                )
                                                            }
                                                            disabled={
                                                                alreadyAdded ||
                                                                adding
                                                            }
                                                            className={`shrink-0 rounded-lg
                                                                        bg-blue-600 px-4 py-2
                                                                        text-sm font-semibold
                                                                        text-white transition
                                                                        hover:bg-blue-500
                                                                        disabled:cursor-not-allowed
                                                                        disabled:bg-slate-700
                                                                        disabled:text-slate-400
                                                                        ${focusClasses}`}
                                                        >
                                                            {alreadyAdded
                                                                ? "Already Added"
                                                                : adding
                                                                    ? "Adding..."
                                                                    : "Add"}
                                                        </button>

                                                    </div>
                                                );
                                            })}

                                        </div>

                                    </div>
                                )}


                            {/* No Results */}
                            {!mlSearchLoading &&
                                !mlSearchError &&
                                mlSearchQuery.trim() !== "" &&
                                mlSearchResults.length === 0 && (

                                    <div className="mt-5 rounded-xl border
                                                    border-dashed border-slate-700
                                                    px-6 py-8 text-center">

                                        <p className="text-sm text-slate-400">
                                            No movies found for this search.
                                        </p>

                                    </div>
                                )}

                        </div>
                    )}


                    {/* Success */}
                    {movieSuccess && (
                        <div
                            role="status"
                            className="mt-6 rounded-xl border border-green-500/30
                   bg-green-500/10 px-4 py-3"
                        >
                            <p className="text-sm text-green-300">
                                {movieSuccess}
                            </p>
                        </div>
                    )}


                    {/* Action Error */}
                    {movieActionError && (
                        <div
                            role="alert"
                            className="mt-6 rounded-xl border border-red-500/30
                   bg-red-500/10 px-4 py-3"
                        >
                            <p className="text-sm text-red-300">
                                {movieActionError}
                            </p>
                        </div>
                    )}


                    {/* Loading */}
                    {moviesLoading && (
                        <div
                            role="status"
                            className="mt-6 rounded-xl border border-slate-800
                   bg-slate-950/40 px-6 py-10 text-center"
                        >
                            <p className="text-sm text-slate-400">
                                Loading movie catalog...
                            </p>
                        </div>
                    )}


                    {/* Load Error */}
                    {!moviesLoading && moviesError && (
                        <div
                            role="alert"
                            className="mt-6 rounded-xl border border-red-500/30
                   bg-red-500/10 px-6 py-8 text-center"
                        >
                            <p className="text-sm text-red-300">
                                {moviesError}
                            </p>

                            <button
                                type="button"
                                onClick={loadMovies}
                                className={`mt-4 rounded-lg border border-red-500/40
                        px-4 py-2 text-sm font-semibold
                        text-red-200 hover:bg-red-500/10
                        ${focusClasses}`}
                            >
                                Retry
                            </button>
                        </div>
                    )}


                    {/* Empty Catalog */}
                    {!mlSearchLoading &&
                        !mlSearchError &&
                        hasMlSearched &&
                        mlSearchResults.length === 0 && (

                            <div className="mt-6 rounded-xl border border-dashed
                                            border-slate-700 bg-slate-950/40
                                            px-6 py-10 text-center">

                                <h4 className="font-semibold text-white">
                                    Catalog is empty
                                </h4>

                                <p className="mt-2 text-sm text-slate-400">
                                    Add a recommendation-supported movie
                                    to begin building the catalog.
                                </p>

                            </div>
                        )}


                    {/* Movie List */}
                    {!moviesLoading &&
                        !moviesError &&
                        movies.length > 0 && (

                            <div className="mt-6 overflow-hidden rounded-xl
                        border border-slate-800">

                                <div className="border-b border-slate-800
                            bg-slate-950/60 px-4 py-3">

                                    <p className="text-sm text-slate-400">
                                        {movies.length}{" "}
                                        {movies.length === 1
                                            ? "movie"
                                            : "movies"}{" "}
                                        in catalog
                                    </p>

                                </div>


                                <div className="divide-y divide-slate-800">

                                    {movies.map((movie) => {

                                        const deleting =
                                            deletingMovieId === movie.id;

                                        return (
                                            <div
                                                key={movie.id}
                                                className="flex flex-col gap-4 p-4
                                                            sm:flex-row sm:items-center
                                                            sm:justify-between"
                                            >

                                                {/* Movie */}
                                                <div className="min-w-0">

                                                    <Link
                                                        to={`/movies/${movie.id}`}
                                                        className={`font-semibold text-white
                                                transition-colors
                                                hover:text-blue-400
                                                ${focusClasses}`}
                                                    >
                                                        {movie.title}
                                                    </Link>

                                                    <div className="mt-2 flex flex-wrap gap-2">

                                                        <span className="rounded-full
                                                     border border-slate-700
                                                     px-2.5 py-1 text-xs
                                                     text-slate-300">
                                                            {movie.genre ||
                                                                "Unknown Genre"}
                                                        </span>

                                                        <span className="rounded-full
                                                     border border-slate-700
                                                     px-2.5 py-1 text-xs
                                                     text-slate-300">
                                                            {movie.releaseYear ??
                                                                "Year N/A"}
                                                        </span>

                                                        {movie.mlMovieId != null && (
                                                            <span className="rounded-full
                                                         border border-blue-500/30
                                                         bg-blue-500/10
                                                         px-2.5 py-1 text-xs
                                                         text-blue-300">
                                                                ML #{movie.mlMovieId}
                                                            </span>
                                                        )}

                                                    </div>

                                                </div>


                                                {/* Delete */}
                                                <button
                                                    type="button"
                                                    onClick={() =>
                                                        handleDeleteMovie(movie)
                                                    }
                                                    disabled={deleting}
                                                    className={`shrink-0 rounded-lg border
                                                                border-red-900/70
                                                                px-4 py-2 text-sm
                                                                font-medium text-red-300
                                                                transition-colors
                                                                hover:bg-red-950/40
                                                                disabled:cursor-not-allowed
                                                                disabled:opacity-50
                                                                ${focusClasses}`}
                                                >
                                                    {deleting
                                                        ? "Removing..."
                                                        : "Remove"}
                                                </button>

                                            </div>
                                        );
                                    })}

                                </div>

                            </div>
                        )}

                </div>

            </section>


            {/* Divider */}
            <div className="my-10 border-t border-slate-800" />


            {/* User Management Section */}
            <section
                id="user-management"
                aria-labelledby="user-management-heading"
                className="scroll-mt-24"
            >

                <div className="mb-5">

                    <p className="text-sm font-semibold uppercase
                                  tracking-widest text-blue-400">
                        Registered Users
                    </p>

                    <h2
                        id="user-management-heading"
                        className="mt-1 text-2xl font-bold text-white"
                    >
                        User Management
                    </h2>

                    <p className="mt-2 max-w-2xl text-sm leading-6
                                  text-slate-400">
                        View and manage user accounts registered
                        in the application.
                    </p>

                </div>


                <div
                    aria-busy={usersLoading}
                    className="rounded-2xl border border-slate-800
                            bg-slate-900/70 p-5 sm:p-6"
                >

                    <div>
                        <h3 className="text-lg font-semibold text-white">
                            Users
                        </h3>

                        <p className="mt-1 text-sm text-slate-400">
                            Basic account management for registered users.
                        </p>
                    </div>


                    {/* Success */}
                    {userSuccess && (
                        <div
                            role="status"
                            className="mt-6 rounded-xl border border-green-500/30
                   bg-green-500/10 px-4 py-3"
                        >
                            <p className="text-sm text-green-300">
                                {userSuccess}
                            </p>
                        </div>
                    )}


                    {/* Action Error */}
                    {userActionError && (
                        <div
                            role="alert"
                            className="mt-6 rounded-xl border border-red-500/30
                   bg-red-500/10 px-4 py-3"
                        >
                            <p className="text-sm text-red-300">
                                {userActionError}
                            </p>
                        </div>
                    )}


                    {/* Loading */}
                    {usersLoading && (
                        <div
                            role="status"
                            className="mt-6 rounded-xl border border-slate-800
                                     bg-slate-950/40 px-6 py-10 text-center"
                        >
                            <p className="text-sm text-slate-400">
                                Loading users...
                            </p>
                        </div>
                    )}


                    {/* Load Error */}
                    {!usersLoading && usersError && (
                        <div
                            role="alert"
                            className="mt-6 rounded-xl border border-red-500/30
                                     bg-red-500/10 px-6 py-8 text-center"
                        >
                            <p className="text-sm text-red-300">
                                {usersError}
                            </p>

                            <button
                                type="button"
                                onClick={loadUsers}
                                className={`mt-4 rounded-lg border
                                            border-red-500/40 px-4 py-2
                                            text-sm font-semibold text-red-200
                                            hover:bg-red-500/10
                                            ${focusClasses}`}
                            >
                                Retry
                            </button>
                        </div>
                    )}


                    {/* Empty */}
                    {!usersLoading &&
                        !usersError &&
                        users.length === 0 && (

                            <div className="mt-6 rounded-xl border border-dashed
                        border-slate-700 bg-slate-950/40
                        px-6 py-10 text-center">

                                <p className="text-sm text-slate-400">
                                    No registered users found.
                                </p>

                            </div>
                        )}


                    {/* User List */}
                    {!usersLoading &&
                        !usersError &&
                        users.length > 0 && (

                            <div className="mt-6 overflow-hidden rounded-xl
                        border border-slate-800">

                                <div className="border-b border-slate-800
                            bg-slate-950/60 px-4 py-3">

                                    <p className="text-sm text-slate-400">
                                        {users.length} registered{" "}
                                        {users.length === 1
                                            ? "user"
                                            : "users"}
                                    </p>

                                </div>


                                <div className="divide-y divide-slate-800">

                                    {users.map((account) => {

                                        const deleting =
                                            deletingUserId === account.id;

                                        const isCurrentAdmin =
                                            account.username === user?.username;

                                        const isAdmin =
                                            account.role === "ADMIN";

                                        const deletionBlocked =
                                            isCurrentAdmin || isAdmin;

                                        return (
                                            <div
                                                key={account.id}
                                                className="flex flex-col gap-4 p-4
                                                            sm:flex-row sm:items-center
                                                            sm:justify-between"
                                            >

                                                <div>

                                                    <div className="flex flex-wrap
                                                items-center gap-2">

                                                        <h4 className="font-semibold text-white">
                                                            {account.username}
                                                        </h4>

                                                        {isCurrentAdmin && (
                                                            <span className="rounded-full
                                                                            border border-blue-500/30
                                                                            bg-blue-500/10
                                                                            px-2.5 py-1 text-xs
                                                                            text-blue-300">
                                                                You
                                                            </span>
                                                        )}

                                                    </div>


                                                    <div className="mt-2 flex flex-wrap gap-2">

                                                        <span className="rounded-full
                                                                        border border-slate-700
                                                                        px-2.5 py-1 text-xs
                                                                        text-slate-400">
                                                            ID #{account.id}
                                                        </span>


                                                        <span
                                                            className={`rounded-full border
                                                    px-2.5 py-1 text-xs
                                                    ${isAdmin
                                                                    ? "border-amber-500/30 bg-amber-500/10 text-amber-300"
                                                                    : "border-blue-500/30 bg-blue-500/10 text-blue-300"
                                                                }`}
                                                        >
                                                            {account.role}
                                                        </span>

                                                    </div>

                                                </div>


                                                <button
                                                    type="button"
                                                    onClick={() =>
                                                        handleDeleteUser(account)
                                                    }
                                                    disabled={
                                                        deleting ||
                                                        deletionBlocked
                                                    }
                                                    title={
                                                        isCurrentAdmin
                                                            ? "You cannot delete your own account."
                                                            : isAdmin
                                                                ? "Admin accounts cannot be deleted."
                                                                : undefined
                                                    }
                                                    className={`shrink-0 rounded-lg border
                                                                border-red-900/70
                                                                px-4 py-2 text-sm
                                                                font-medium text-red-300
                                                                transition-colors
                                                                hover:bg-red-950/40
                                                                disabled:cursor-not-allowed
                                                                disabled:border-slate-700
                                                                disabled:text-slate-600
                                                                disabled:hover:bg-transparent
                                                                ${focusClasses}`}
                                                >
                                                    {deleting
                                                        ? "Deleting..."
                                                        : deletionBlocked
                                                            ? "Protected"
                                                            : "Delete User"}
                                                </button>

                                            </div>
                                        );
                                    })}

                                </div>

                            </div>
                        )}

                </div>

            </section>

        </section>
    );
}


export default AdminDashboard;