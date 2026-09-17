import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

import {
    getUserLibrary,
    rateMovie,
    removeMovieActivity
} from "../services/userMovieService";


function Profile() {
    const { user } = useAuth();

    const [library, setLibrary] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    const [updatingMovieId, setUpdatingMovieId] = useState(null);
    const [removingMovieId, setRemovingMovieId] = useState(null);

    const focusClasses =
        "focus-visible:outline-none focus-visible:ring-2 " +
        "focus-visible:ring-blue-500 focus-visible:ring-offset-2 " +
        "focus-visible:ring-offset-slate-950";


    useEffect(() => {
        let active = true;

        getUserLibrary()
            .then((response) => {
                if (!active) {
                    return;
                }

                setLibrary(response.data);
                setError("");
            })
            .catch((error) => {
                if (!active) {
                    return;
                }

                console.error(
                    "Error loading user library:",
                    error
                );

                setError(
                    "We couldn't load your movie library. Please try again."
                );
            })
            .finally(() => {
                if (active) {
                    setLoading(false);
                }
            });

        return () => {
            active = false;
        };
    }, []);


    const handleRetry = async () => {
        setLoading(true);
        setError("");

        try {
            const response = await getUserLibrary();

            setLibrary(response.data);
        } catch (error) {
            console.error(
                "Error loading user library:",
                error
            );

            setError(
                "We couldn't load your movie library. Please try again."
            );
        } finally {
            setLoading(false);
        }
    };


    const handleRating = async (
        movieId,
        rating
    ) => {

        setUpdatingMovieId(movieId);
        setError("");

        try {
            const response = await rateMovie(
                movieId,
                rating
            );

            setLibrary((currentLibrary) =>
                currentLibrary.map((movie) =>
                    movie.movieId === movieId
                        ? {
                            ...movie,
                            rating: response.data.rating
                        }
                        : movie
                )
            );
        } catch (error) {
            console.error(
                "Error updating rating:",
                error
            );

            setError(
                "We couldn't update your rating. Please try again."
            );
        } finally {
            setUpdatingMovieId(null);
        }
    };


    const handleRemove = async (movieId) => {
        setRemovingMovieId(movieId);
        setError("");

        try {
            await removeMovieActivity(movieId);

            setLibrary((currentLibrary) =>
                currentLibrary.filter(
                    (movie) =>
                        movie.movieId !== movieId
                )
            );
        } catch (error) {
            console.error(
                "Error removing movie activity:",
                error
            );

            setError(
                "We couldn't remove this movie from your library."
            );
        } finally {
            setRemovingMovieId(null);
        }
    };


    if (loading) {
        return (
            <section className="py-6 sm:py-8">

                <div
                    role="status"
                    className="rounded-2xl border border-slate-800
                               bg-slate-900/60 px-6 py-16 text-center"
                >

                    <div
                        aria-hidden="true"
                        className="mx-auto h-9 w-9 animate-spin rounded-full
                                   border-4 border-slate-700 border-t-blue-500
                                   motion-reduce:animate-none"
                    />

                    <h1 className="mt-5 text-xl font-semibold text-white">
                        Loading your profile
                    </h1>

                    <p className="mt-2 text-sm text-slate-400">
                        Fetching your movie library...
                    </p>

                </div>

            </section>
        );
    }


    return (
        <section className="py-6 sm:py-8">

            {/* Page Header */}
            <div className="mb-8">

                <p className="mb-2 text-sm font-semibold uppercase
                              tracking-widest text-blue-400">
                    Your Account
                </p>

                <h1 className="text-3xl font-bold text-white
                               sm:text-4xl">
                    Profile
                </h1>

                <p className="mt-3 max-w-2xl text-sm leading-6
                              text-slate-400 sm:text-base">
                    View your account and manage the movies
                    you've watched and rated.
                </p>

            </div>


            {/* User Information */}
            <div className="mb-8 overflow-hidden rounded-2xl
                            border border-slate-800
                            bg-slate-900/80">

                <div className="border-b border-slate-800
                                px-5 py-5 sm:px-6">

                    <h2 className="text-xl font-semibold text-white">
                        Account Information
                    </h2>

                </div>

                <div className="grid sm:grid-cols-2">

                    <div className="border-b border-slate-800
                                    p-5 sm:border-b-0
                                    sm:border-r sm:p-6">

                        <p className="text-sm font-medium text-slate-500">
                            Username
                        </p>

                        <p className="mt-2 text-lg font-semibold text-white">
                            {user?.username}
                        </p>

                    </div>

                    <div className="p-5 sm:p-6">

                        <p className="text-sm font-medium text-slate-500">
                            Role
                        </p>

                        <p className="mt-2 text-lg font-semibold text-white">
                            {user?.role ?? "USER"}
                        </p>

                    </div>

                </div>

            </div>


            {/* Library */}
            <div>

                <div className="mb-5 flex flex-col gap-2
                                sm:flex-row sm:items-end
                                sm:justify-between">

                    <div>

                        <h2 className="text-2xl font-bold text-white">
                            My Library
                        </h2>

                        <p className="mt-1 text-sm text-slate-400">
                            {library.length}{" "}
                            {library.length === 1
                                ? "movie"
                                : "movies"}{" "}
                            watched
                        </p>

                    </div>

                </div>


                {error && (
                    <div
                        role="alert"
                        className="mb-6 rounded-xl border
                                   border-red-900/60 bg-red-950/20
                                   px-4 py-4 text-sm text-red-300"
                    >
                        <p>{error}</p>

                        <button
                            type="button"
                            onClick={handleRetry}
                            className={`mt-3 rounded-lg border
                                       border-red-800 px-3 py-2
                                       font-medium text-red-200
                                       transition-colors
                                       hover:bg-red-900/30
                                       motion-reduce:transition-none
                                       ${focusClasses}`}
                        >
                            Retry
                        </button>
                    </div>
                )}


                {!error && library.length === 0 ? (

                    <div className="rounded-2xl border border-slate-800
                                    bg-slate-900/60 px-6 py-14
                                    text-center">

                        <h3 className="text-xl font-semibold text-white">
                            Your library is empty
                        </h3>

                        <p className="mx-auto mt-2 max-w-md
                                      text-sm leading-6 text-slate-400">
                            Mark movies as watched to add them
                            to your library.
                        </p>

                        <Link
                            to="/movies"
                            className={`mt-6 inline-flex rounded-xl
                                       bg-blue-600 px-5 py-3
                                       font-semibold text-white
                                       transition-colors
                                       hover:bg-blue-500
                                       motion-reduce:transition-none
                                       ${focusClasses}`}
                        >
                            Browse Movies
                        </Link>

                    </div>

                ) : (

                    <div className="space-y-4">

                        {library.map((movie) => {

                            const updating =
                                updatingMovieId === movie.movieId;

                            const removing =
                                removingMovieId === movie.movieId;

                            return (
                                <article
                                    key={movie.movieId}
                                    className="rounded-2xl border
                                               border-slate-800
                                               bg-slate-900/80 p-5
                                               sm:p-6"
                                >

                                    <div className="flex flex-col gap-6
                                                    lg:flex-row
                                                    lg:items-center
                                                    lg:justify-between">

                                        {/* Movie Information */}
                                        <div className="min-w-0">

                                            <Link
                                                to={`/movies/${movie.movieId}`}
                                                className={`rounded-md
                                                           text-xl font-semibold
                                                           text-white
                                                           transition-colors
                                                           hover:text-blue-400
                                                           motion-reduce:transition-none
                                                           ${focusClasses}`}
                                            >
                                                {movie.title}
                                            </Link>

                                            <div className="mt-3 flex
                                                            flex-wrap gap-2">

                                                <span className="rounded-full
                                                                 border
                                                                 border-blue-500/30
                                                                 bg-blue-500/10
                                                                 px-3 py-1
                                                                 text-sm
                                                                 text-blue-300">
                                                    {movie.genre ||
                                                        "Unknown Genre"}
                                                </span>

                                                <span className="rounded-full
                                                                 border
                                                                 border-slate-700
                                                                 bg-slate-950
                                                                 px-3 py-1
                                                                 text-sm
                                                                 text-slate-300">
                                                    {movie.releaseYear ??
                                                        "Year N/A"}
                                                </span>

                                                <span className="rounded-full
                                                                 border
                                                                 border-amber-500/30
                                                                 bg-amber-500/10
                                                                 px-3 py-1
                                                                 text-sm
                                                                 text-amber-400">
                                                    IMDb ★{" "}
                                                    {movie.tmdbRating ??
                                                        "N/A"}
                                                </span>

                                            </div>

                                        </div>


                                        {/* Rating + Remove */}
                                        <div className="shrink-0">

                                            <p className="mb-2 text-sm
                                                          font-medium
                                                          text-slate-400">
                                                Your Rating
                                            </p>

                                            <div className="flex flex-wrap
                                                            gap-2">

                                                {[1, 2, 3, 4, 5].map(
                                                    (value) => (

                                                        <button
                                                            key={value}
                                                            type="button"
                                                            onClick={() =>
                                                                handleRating(
                                                                    movie.movieId,
                                                                    value
                                                                )
                                                            }
                                                            disabled={
                                                                updating ||
                                                                removing
                                                            }
                                                            aria-label={
                                                                `Rate ${value} out of 5`
                                                            }
                                                            aria-pressed={
                                                                movie.rating ===
                                                                value
                                                            }
                                                            className={`flex
                                                                        h-10 w-10
                                                                        items-center
                                                                        justify-center
                                                                        rounded-lg
                                                                        border
                                                                        text-lg
                                                                        transition-colors
                                                                        disabled:cursor-not-allowed
                                                                        disabled:opacity-50
                                                                        motion-reduce:transition-none
                                                                        ${focusClasses}
                                                                        ${movie.rating >= value
                                                                    ? "border-amber-500/40 bg-amber-500/10 text-amber-400"
                                                                    : "border-slate-700 bg-slate-950 text-slate-500 hover:border-slate-600 hover:text-slate-300"
                                                                }`}
                                                        >
                                                            ★
                                                        </button>

                                                    )
                                                )}

                                            </div>

                                            <p className="mt-2 text-sm
                                                          text-slate-500">
                                                {updating
                                                    ? "Saving rating..."
                                                    : movie.rating != null
                                                        ? `${movie.rating} / 5`
                                                        : "Not rated"}
                                            </p>

                                            <button
                                                type="button"
                                                onClick={() =>
                                                    handleRemove(
                                                        movie.movieId
                                                    )
                                                }
                                                disabled={
                                                    removing ||
                                                    updating
                                                }
                                                className={`mt-4 rounded-lg
                                                            border
                                                            border-red-900/70
                                                            px-4 py-2
                                                            text-sm
                                                            font-medium
                                                            text-red-300
                                                            transition-colors
                                                            hover:bg-red-950/40
                                                            disabled:cursor-not-allowed
                                                            disabled:opacity-50
                                                            motion-reduce:transition-none
                                                            ${focusClasses}`}
                                            >
                                                {removing
                                                    ? "Removing..."
                                                    : "Remove from Library"}
                                            </button>

                                        </div>

                                    </div>

                                </article>
                            );
                        })}

                    </div>

                )}

            </div>

        </section>
    );
}

export default Profile;