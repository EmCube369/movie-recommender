import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getMyRecommendations } from "../services/movieService";


function Recommendations() {
    const [recommendations, setRecommendations] = useState([]);

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");


    useEffect(() => {
        let active = true;

        getMyRecommendations(10)
            .then((response) => {
                if (!active) {
                    return;
                }

                setRecommendations(
                    response.data.recommendations ?? []
                );
            })
            .catch((error) => {
                if (!active) {
                    return;
                }

                console.error(
                    "Error fetching personalized recommendations:",
                    error
                );

                setRecommendations([]);

                if (
                    error.response?.status === 400 &&
                    error.response?.data?.message
                ) {
                    setError(
                        error.response.data.message
                    );
                } else if (
                    error.response?.status === 401 ||
                    error.response?.status === 403
                ) {
                    setError(
                        "Your session has expired. Please log in again."
                    );
                } else {
                    setError(
                        "Failed to load recommendations. Please try again."
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
    }, []);


    if (loading) {
        return (
            <section className="py-6 sm:py-8">

                <div className="mb-8">
                    <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-blue-400 sm:text-sm">
                        Hybrid Recommendation System
                    </p>

                    <h1 className="text-3xl font-bold text-white sm:text-4xl">
                        Recommendations
                    </h1>
                </div>


                <div
                    role="status"
                    aria-live="polite"
                    className="rounded-2xl border border-slate-800
                               bg-slate-900/60 px-6 py-16 text-center"
                >
                    <p className="text-slate-400">
                        Generating recommendations for you...
                    </p>
                </div>

            </section>
        );
    }


    return (
        <section className="py-6 sm:py-8">

            {/* Page Header */}
            <div className="mb-8">

                <p className="mb-2 text-xs font-semibold uppercase tracking-widest text-blue-400 sm:text-sm">
                    Hybrid Recommendation System
                </p>

                <h1 className="text-3xl font-bold text-white sm:text-4xl">
                    Recommendations
                </h1>

                <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
                    Personalized recommendations based on movies
                    you have rated.
                </p>

            </div>


            {/* Error / Not Enough Ratings */}
            {error && (
                <div
                    role="alert"
                    className="rounded-2xl border border-amber-500/30
                               bg-amber-500/10 px-6 py-10 text-center"
                >

                    <h2 className="text-xl font-semibold text-white">
                        We need a little more from you
                    </h2>

                    <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-slate-300">
                        {error}
                    </p>

                    <Link
                        to="/movies"
                        className="mt-6 inline-flex rounded-xl bg-blue-600
                                   px-5 py-3 font-semibold text-white
                                   transition-colors hover:bg-blue-500
                                   focus-visible:outline-none
                                   focus-visible:ring-2
                                   focus-visible:ring-blue-500
                                   focus-visible:ring-offset-2
                                   focus-visible:ring-offset-slate-950"
                    >
                        Browse Movies
                    </Link>

                </div>
            )}


            {/* Recommendations */}
            {!error && recommendations.length > 0 && (

                <div aria-labelledby="recommendations-heading">

                    <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">

                        <div>
                            <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">
                                Personalized Results
                            </p>

                            <h2
                                id="recommendations-heading"
                                className="mt-1 text-2xl font-bold text-white"
                            >
                                Recommended For You
                            </h2>
                        </div>

                        <p className="text-sm text-slate-400">
                            {recommendations.length} movies
                        </p>

                    </div>


                    <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">

                        {recommendations.map((movie) => (

                            <article
                                key={`${movie.rank}-${movie.title}`}
                                className="flex h-full flex-col rounded-2xl
                                           border border-slate-800
                                           bg-slate-900/80 p-5"
                            >

                                <div className="mb-5 flex items-center justify-between gap-3">

                                    <span
                                        aria-label={`Rank ${movie.rank}`}
                                        className="flex h-9 w-9 items-center justify-center
                                                   rounded-full bg-blue-600 text-sm
                                                   font-bold text-white"
                                    >
                                        <span aria-hidden="true">
                                            #{movie.rank}
                                        </span>
                                    </span>

                                    <span className="text-sm font-semibold text-amber-400">
                                        Score{" "}
                                        {movie.score != null
                                            ? Number(movie.score).toFixed(3)
                                            : "N/A"}
                                    </span>

                                </div>


                                <h3 className="wrap-break-word text-xl font-semibold leading-snug text-white">
                                    {movie.title}
                                </h3>


                                <div className="mt-4 flex flex-wrap gap-2">

                                    {movie.genres?.length > 0 ? (
                                        movie.genres.map((genre) => (

                                            <span
                                                key={genre}
                                                className="rounded-full border
                                                           border-blue-500/30
                                                           bg-blue-500/10
                                                           px-3 py-1 text-xs
                                                           font-medium text-blue-300"
                                            >
                                                {genre}
                                            </span>

                                        ))
                                    ) : (
                                        <span className="text-sm text-slate-500">
                                            Genre unavailable
                                        </span>
                                    )}

                                </div>


                                <div className="mt-auto pt-6">

                                    <p className="text-sm text-slate-500">
                                        Release Year
                                    </p>

                                    <p className="mt-1 font-medium text-slate-300">
                                        {movie.releaseYear ?? "N/A"}
                                    </p>


                                    {movie.movieId != null && (
                                        <Link
                                            to={`/movies/${movie.movieId}`}
                                            className="mt-5 inline-flex text-sm
                                                       font-semibold text-blue-400
                                                       hover:text-blue-300
                                                       focus-visible:outline-none
                                                       focus-visible:underline"
                                        >
                                            View movie details →
                                        </Link>
                                    )}

                                </div>

                            </article>

                        ))}

                    </div>

                </div>
            )}


            {/* Successful request but no results */}
            {!error && recommendations.length === 0 && (

                <div
                    role="status"
                    className="rounded-2xl border border-dashed border-slate-700
                               bg-slate-900/40 px-6 py-14 text-center"
                >

                    <h2 className="text-xl font-semibold text-white">
                        No recommendations available yet
                    </h2>

                    <p className="mt-2 text-sm text-slate-400">
                        Rate some movies and come back to get personalized recommendations.
                    </p>

                    <Link
                        to="/movies"
                        className="mt-6 inline-flex rounded-xl bg-blue-600
                                   px-5 py-3 font-semibold text-white
                                   hover:bg-blue-500"
                    >
                        Browse Movies
                    </Link>

                </div>
            )}

        </section>
    );
}


export default Recommendations;