import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getMoviesById } from "../services/movieService";
import { useAuth } from "../context/AuthContext";
import {
    getMovieActivity,
    markMovieWatched,
    rateMovie
} from "../services/userMovieService";


function MovieDetails() {
    const { id } = useParams();

    const {
        user,
        isAuthenticated,
        authLoading
    } = useAuth();

    const [movie, setMovie] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [notFound, setNotFound] = useState(false);

    const [watched, setWatched] = useState(false);
    const [userRating, setUserRating] = useState(null);

    const [activityOwnerId, setActivityOwnerId] = useState(null);
    const [activityMovieId, setActivityMovieId] = useState(null);
    const [activityError, setActivityError] = useState("");

    const [savingWatched, setSavingWatched] = useState(false);
    const [savingRating, setSavingRating] = useState(false);

    const focusClasses =
        "focus-visible:outline-none focus-visible:ring-2 " +
        "focus-visible:ring-blue-500 focus-visible:ring-offset-2 " +
        "focus-visible:ring-offset-slate-950";


    const activityLoading =
        !authLoading &&
        isAuthenticated &&
        movie !== null &&
        (
            activityOwnerId !== user?.id ||
            activityMovieId !== id
        );


    useEffect(() => {
        let active = true;

        getMoviesById(id)
            .then((response) => {
                if (!active) {
                    return;
                }

                setMovie(response.data);
                setError("");
                setNotFound(false);
            })
            .catch((error) => {
                if (!active) {
                    return;
                }

                console.error(
                    "Error fetching movie:",
                    error
                );

                if (error.response?.status === 404) {
                    setMovie(null);
                    setError("");
                    setNotFound(true);
                } else {
                    setMovie(null);
                    setNotFound(false);

                    setError(
                        "We couldn't load the movie details. Please try again."
                    );
                }
            })
            .finally(() => {
                if (active) {
                    setLoading(false);
                }
            });

        return () => {
            active = false;
        };
    }, [id]);

    useEffect(() => {
        if (
            authLoading ||
            !isAuthenticated ||
            !user ||
            !movie
        ) {
            return;
        }

        let active = true;

        getMovieActivity(id)
            .then((response) => {
                if (!active) {
                    return;
                }

                setWatched(response.data.watched);
                setUserRating(response.data.rating);
                setActivityError("");

                setActivityOwnerId(user.id);
                setActivityMovieId(id);
            })
            .catch((error) => {
                if (!active) {
                    return;
                }

                console.error(
                    "Error fetching movie activity:",
                    error
                );

                setWatched(false);
                setUserRating(null);

                setActivityError(
                    "We couldn't load your activity for this movie."
                );

                setActivityOwnerId(user.id);
                setActivityMovieId(id);
            });

        return () => {
            active = false;
        };
    }, [
        id,
        movie,
        user,
        isAuthenticated,
        authLoading
    ]);

    const handleRetry = async () => {
        setLoading(true);
        setError("");
        setNotFound(false);

        try {
            const response = await getMoviesById(id);

            setMovie(response.data);
            setError("");
            setNotFound(false);
        } catch (error) {
            console.error(
                "Error fetching movie:",
                error
            );

            if (error.response?.status === 404) {
                setMovie(null);
                setError("");
                setNotFound(true);
            } else {
                setMovie(null);
                setNotFound(false);

                setError(
                    "We couldn't load the movie details. Please try again."
                );
            }
        } finally {
            setLoading(false);
        }
    };

    const handleMarkWatched = async () => {
        setSavingWatched(true);
        setActivityError("");

        try {
            const response = await markMovieWatched(id);

            setWatched(response.data.watched);
            setUserRating(response.data.rating);
        } catch (error) {
            console.error(
                "Error marking movie as watched:",
                error
            );

            setActivityError(
                "We couldn't mark this movie as watched. Please try again."
            );
        } finally {
            setSavingWatched(false);
        }
    };

    const handleRating = async (rating) => {
        setSavingRating(true);
        setActivityError("");

        try {
            const response = await rateMovie(
                id,
                rating
            );

            setWatched(response.data.watched);
            setUserRating(response.data.rating);
        } catch (error) {
            console.error(
                "Error rating movie:",
                error
            );

            setActivityError(
                "We couldn't save your rating. Please try again."
            );
        } finally {
            setSavingRating(false);
        }
    };

    if (loading) {
        return (
            <section className="py-6 sm:py-8">

                <Link
                    to="/movies"
                    className={`mb-8 inline-flex rounded-md px-1 py-1
                        items-center text-sm font-medium text-slate-400
                        transition-colors hover:text-white
                        motion-reduce:transition-none
                        ${focusClasses}`}
                >
                    ← Back to Movies
                </Link>

                <div
                    role="status"
                    aria-live="polite"
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
                        Loading movie details
                    </h1>

                    <p className="mt-2 text-sm text-slate-400">
                        Fetching information about this movie...
                    </p>

                </div>

            </section>
        );
    }


    if (notFound) {
        return (
            <section className="py-6 sm:py-8">

                <Link
                    to="/movies"
                    className={`mb-8 inline-flex rounded-md px-1 py-1
                        items-center text-sm font-medium text-slate-400
                        transition-colors hover:text-white
                        motion-reduce:transition-none
                        ${focusClasses}`}
                >
                    ← Back to Movies
                </Link>

                <div
                    role="status"
                    aria-live="polite"
                    className="rounded-2xl border border-slate-800
                            bg-slate-900/60 px-6 py-16 text-center"
                >

                    <div
                        aria-hidden="true"
                        className="mx-auto flex h-12 w-12 items-center justify-center
                                    rounded-full bg-slate-800 text-xl text-slate-300"
                    >
                        ?
                    </div>

                    <h1 className="mt-4 text-xl font-semibold text-white">
                        Movie not found
                    </h1>

                    <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-400">
                        The movie you're looking for doesn't exist
                        or may have been removed.
                    </p>

                    <Link
                        to="/movies"
                        className={`mt-6 inline-block rounded-xl bg-blue-600
                        px-5 py-3 font-semibold text-white
                        transition-colors hover:bg-blue-500
                        motion-reduce:transition-none
                        ${focusClasses}`}
                    >
                        Browse Movies
                    </Link>

                </div>

            </section>
        );
    }


    if (error) {
        return (
            <section className="py-6 sm:py-8">

                <Link
                    to="/movies"
                    className={`mb-8 inline-flex rounded-md px-1 py-1
                        items-center text-sm font-medium text-slate-400
                        transition-colors hover:text-white
                        motion-reduce:transition-none
                        ${focusClasses}`}
                >
                    ← Back to Movies
                </Link>

                <div
                    role="alert"
                    className="rounded-2xl border border-red-900/60
                            bg-red-950/20 px-6 py-14 text-center"
                >

                    <div
                        aria-hidden="true"
                        className="mx-auto flex h-12 w-12 items-center justify-center
                        rounded-full bg-red-500/10 text-xl text-red-400"
                    >
                        !
                    </div>

                    <h1 className="mt-4 text-xl font-semibold text-white">
                        Unable to load movie
                    </h1>

                    <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-400">
                        {error}
                    </p>

                    <div className="mt-6 flex flex-col justify-center gap-3 sm:flex-row">

                        <button
                            type="button"
                            onClick={handleRetry}
                            className={`rounded-xl bg-blue-600 px-5 py-3
                            font-semibold text-white transition-colors
                            hover:bg-blue-500 motion-reduce:transition-none
                            ${focusClasses}`}
                        >
                            Retry
                        </button>

                        <Link
                            to="/movies"
                            className={`rounded-xl border border-slate-700
                            bg-slate-900 px-5 py-3 font-semibold
                            text-slate-300 transition-colors
                            hover:border-slate-600 hover:bg-slate-800
                            hover:text-white motion-reduce:transition-none
                            ${focusClasses}`}
                        >
                            Back to Movies
                        </Link>

                    </div>

                </div>

            </section>
        );
    }


    return (
        <section className="py-6 sm:py-8">

            {/* Back Navigation */}
            <Link
                to="/movies"
                className={`mb-8 inline-flex rounded-md px-1 py-1
                    items-center text-sm font-medium text-slate-400
                    transition-colors hover:text-white
                    motion-reduce:transition-none
                    ${focusClasses}`}
            >
                ← Back to Movies
            </Link>


            {/* Movie Header */}
            <div className="mb-8">

                <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-blue-400">
                    Movie Details
                </p>

                <h1 className="max-w-4xl wrap-break-word text-3xl font-bold leading-tight text-white sm:text-4xl lg:text-5xl">
                    {movie.title}
                </h1>


                {/* Quick Metadata */}
                <div className="mt-5 flex flex-wrap items-center gap-3">

                    <span className="max-w-full wrap-break-word rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1.5 text-sm font-medium text-blue-300">
                        {movie.genre || "Unknown Genre"}
                    </span>

                    <span className="rounded-full border border-slate-700 bg-slate-900 px-3 py-1.5 text-sm text-slate-300">
                        {movie.releaseYear ?? "Year N/A"}
                    </span>

                    <span className="rounded-full border border-amber-500/30 bg-amber-500/10 px-3 py-1.5 text-sm font-semibold text-amber-400">
                        ★ {movie.tmdbRating ?? "N/A"}
                    </span>

                </div>

            </div>


            {/* Details Card */}
            <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/80">

                <div className="border-b border-slate-800 px-5 py-5 sm:px-6">

                    <h2 className="text-xl font-semibold text-white">
                        Movie Information
                    </h2>

                    <p className="mt-1 text-sm text-slate-400">
                        Basic information about this movie.
                    </p>

                </div>


                <div className="grid md:grid-cols-3">

                    {/* Genre */}
                    <div className="min-w-0 border-b border-slate-800 p-5 sm:p-6 md:border-b-0 md:border-r">

                        <p className="text-sm font-medium text-slate-500">
                            Genre
                        </p>

                        <p className="mt-2 wrap-break-word text-lg font-semibold text-white">
                            {movie.genre || "Not available"}
                        </p>

                    </div>


                    {/* Release Year */}
                    <div className="min-w-0 border-b border-slate-800 p-5 sm:p-6 md:border-b-0 md:border-r">

                        <p className="text-sm font-medium text-slate-500">
                            Release Year
                        </p>

                        <p className="mt-2 text-lg font-semibold text-white">
                            {movie.releaseYear ?? "Not available"}
                        </p>

                    </div>


                    {/* TMDB Rating */}
                    <div className="min-w-0 p-5 sm:p-6">

                        <p className="text-sm font-medium text-slate-500">
                            TMDB Rating
                        </p>

                        <div className="mt-2 flex items-center gap-2">

                            <span
                                aria-hidden="true"
                                className="text-lg font-semibold text-amber-400"
                            >
                                ★
                            </span>

                            <span className="text-lg font-semibold text-white">
                                {movie.tmdbRating ?? "N/A"}
                            </span>

                            {movie.tmdbRating != null && (
                                <span className="text-sm text-slate-500">
                                    / 10
                                </span>
                            )}

                        </div>

                    </div>

                </div>

            </div>

            {/* User Activity */}
            <div className="mt-6 overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/80">

                <div className="border-b border-slate-800 px-5 py-5 sm:px-6">

                    <h2 className="text-xl font-semibold text-white">
                        Your Activity
                    </h2>

                    <p className="mt-1 text-sm text-slate-400">
                        Track movies you've watched and rate them.
                    </p>

                </div>


                <div className="p-5 sm:p-6">

                    {authLoading ? (

                        <div
                            role="status"
                            className="py-5 text-sm text-slate-400"
                        >
                            Checking your account...
                        </div>

                    ) : !isAuthenticated ? (

                        <div>

                            <p className="text-sm leading-6 text-slate-400">
                                Log in to mark this movie as watched
                                and give it a rating.
                            </p>

                            <Link
                                to="/login"
                                className={`mt-4 inline-flex rounded-xl bg-blue-600
                    px-5 py-2.5 font-semibold text-white
                    transition-colors hover:bg-blue-500
                    motion-reduce:transition-none
                    ${focusClasses}`}
                            >
                                Log In
                            </Link>

                        </div>

                    ) : activityLoading ? (

                        <div
                            role="status"
                            className="flex items-center gap-3 py-5
                text-sm text-slate-400"
                        >

                            <div
                                aria-hidden="true"
                                className="h-5 w-5 animate-spin rounded-full
                    border-2 border-slate-700
                    border-t-blue-500
                    motion-reduce:animate-none"
                            />

                            Loading your activity...

                        </div>

                    ) : (

                        <div className="space-y-7">

                            {activityError && (
                                <div
                                    role="alert"
                                    className="rounded-xl border border-red-900/60
                        bg-red-950/20 px-4 py-3
                        text-sm text-red-300"
                                >
                                    {activityError}
                                </div>
                            )}


                            {/* Watched */}
                            <div>

                                <p className="mb-3 text-sm font-medium text-slate-400">
                                    Watch Status
                                </p>

                                <button
                                    type="button"
                                    onClick={handleMarkWatched}
                                    disabled={watched || savingWatched}
                                    className={`rounded-xl px-5 py-2.5
                        font-semibold transition-colors
                        motion-reduce:transition-none
                        disabled:cursor-not-allowed
                        ${focusClasses}
                        ${watched
                                            ? "border border-emerald-500/30 bg-emerald-500/10 text-emerald-300"
                                            : "bg-blue-600 text-white hover:bg-blue-500 disabled:opacity-60"
                                        }`}
                                >
                                    {savingWatched
                                        ? "Saving..."
                                        : watched
                                            ? "✓ Watched"
                                            : "Mark as Watched"}
                                </button>

                            </div>


                            {/* Rating */}
                            <div>

                                <p className="text-sm font-medium text-slate-400">
                                    Your Rating
                                </p>

                                <div
                                    className="mt-3 flex flex-wrap gap-2"
                                    aria-label="Rate this movie from 1 to 5"
                                >

                                    {[1, 2, 3, 4, 5].map((value) => (

                                        <button
                                            key={value}
                                            type="button"
                                            onClick={() =>
                                                handleRating(value)
                                            }
                                            disabled={savingRating}
                                            aria-label={`Rate ${value} out of 5`}
                                            aria-pressed={
                                                userRating === value
                                            }
                                            className={`flex h-11 w-11
                                items-center justify-center
                                rounded-xl border text-xl
                                transition-colors
                                motion-reduce:transition-none
                                disabled:cursor-not-allowed
                                disabled:opacity-60
                                ${focusClasses}
                                ${userRating >= value
                                                    ? "border-amber-500/40 bg-amber-500/10 text-amber-400"
                                                    : "border-slate-700 bg-slate-950 text-slate-500 hover:border-slate-600 hover:text-slate-300"
                                                }`}
                                        >
                                            ★
                                        </button>

                                    ))}

                                </div>


                                <p className="mt-3 text-sm text-slate-500">

                                    {savingRating
                                        ? "Saving your rating..."
                                        : userRating != null
                                            ? `Your rating: ${userRating} / 5`
                                            : "Choose a rating from 1 to 5 stars."}

                                </p>

                            </div>

                        </div>

                    )}

                </div>

            </div>

        </section>
    );
}

export default MovieDetails;