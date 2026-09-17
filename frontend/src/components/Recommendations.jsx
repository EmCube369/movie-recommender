import { useState } from "react";
import { getRecommendations } from "../services/movieService";

function Recommendations() {
    const [userId, setUserId] = useState("1");
    const [limit, setLimit] = useState("5");

    const [recommendations, setRecommendations] = useState([]);
    const [resultUserId, setResultUserId] = useState(null);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [hasSearched, setHasSearched] = useState(false);

    const fetchRecommendations = async () => {
        setLoading(true);
        setError("");
        setRecommendations([]);
        setResultUserId(null);
        setHasSearched(true);

        try {
            const response = await getRecommendations(
                Number(userId),
                Number(limit)
            );

            setRecommendations(
                response.data.recommendations ?? []
            );

            setResultUserId(response.data.userId);
        } catch (error) {
            console.error(
                "Error fetching recommendations:",
                error
            );

            setRecommendations([]);
            setResultUserId(null);

            if (error.response?.status === 404) {
                setError(
                    "No recommendation profile was found for this user."
                );
            } else if (error.response?.status === 400) {
                setError(
                    "The recommendation request is invalid. Check the user ID and number of movies."
                );
            } else {
                setError(
                    "We couldn't generate recommendations right now. Please try again."
                );
            }
        } finally {
            setLoading(false);
        }
    };


    const handleSubmit = (e) => {
        e.preventDefault();
        fetchRecommendations();
    };


    return (
        <section className="py-6 sm:py-8">

            {/* Page Header */}
            <div className="mb-8">

                <p className="mb-2 text-sm font-semibold uppercase tracking-widest text-blue-400">
                    Hybrid Recommendation System
                </p>

                <h1 className="text-3xl font-bold text-white sm:text-4xl">
                    Recommendations
                </h1>

                <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-400 sm:text-base">
                    Get personalized movie recommendations generated
                    using collaborative filtering, content-based
                    filtering, and sentiment analysis.
                </p>

            </div>


            {/* Recommendation Controls */}
            <form
                onSubmit={handleSubmit}
                className="mb-8 rounded-2xl border border-slate-800 bg-slate-900/70 p-5 sm:p-6"
            >

                <div className="grid gap-5 md:grid-cols-[1fr_1fr_auto] md:items-end">

                    {/* User ID */}
                    <div>
                        <label
                            htmlFor="user-id"
                            className="mb-2 block text-sm font-medium text-slate-300"
                        >
                            User ID
                        </label>

                        <input
                            id="user-id"
                            type="number"
                            value={userId}
                            onChange={(e) =>
                                setUserId(e.target.value)
                            }
                            min="1"
                            required
                            disabled={loading}
                            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
                        />
                    </div>


                    {/* Recommendation Limit */}
                    <div>
                        <label
                            htmlFor="recommendation-limit"
                            className="mb-2 block text-sm font-medium text-slate-300"
                        >
                            Number of Movies
                        </label>

                        <input
                            id="recommendation-limit"
                            type="number"
                            value={limit}
                            onChange={(e) =>
                                setLimit(e.target.value)
                            }
                            min="1"
                            required
                            disabled={loading}
                            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
                        />
                    </div>


                    {/* Submit */}
                    <button
                        type="submit"
                        disabled={loading}
                        className="rounded-xl bg-blue-600 px-6 py-3 font-semibold text-white transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                        {loading
                            ? "Generating..."
                            : "Get Recommendations"}
                    </button>

                </div>

            </form>


            {/* Loading */}
            {loading && (
                <div className="rounded-2xl border border-slate-800 bg-slate-900/60 px-6 py-14 text-center">

                    <div className="mx-auto h-9 w-9 animate-spin rounded-full border-4 border-slate-700 border-t-blue-500" />

                    <h2 className="mt-5 text-xl font-semibold text-white">
                        Generating recommendations
                    </h2>

                    <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-400">
                        The hybrid model is analyzing your movie
                        preferences and ranking suitable movies.
                    </p>

                </div>
            )}


            {/* Error */}
            {!loading && error && (
                <div className="rounded-2xl border border-red-900/60 bg-red-950/20 px-6 py-14 text-center">

                    <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-red-500/10 text-xl text-red-400">
                        !
                    </div>

                    <h2 className="mt-4 text-xl font-semibold text-white">
                        Unable to generate recommendations
                    </h2>

                    <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-400">
                        {error}
                    </p>

                    <button
                        type="button"
                        onClick={fetchRecommendations}
                        className="mt-6 rounded-xl bg-blue-600 px-5 py-3 font-semibold text-white transition hover:bg-blue-500"
                    >
                        Try Again
                    </button>

                </div>
            )}


            {/* Results */}
            {!loading &&
                !error &&
                hasSearched &&
                recommendations.length > 0 && (

                    <div>

                        {/* Results Header */}
                        <div className="mb-5 flex flex-col gap-2 sm:flex-row sm:items-end sm:justify-between">

                            <div>
                                <p className="text-sm font-semibold uppercase tracking-widest text-blue-400">
                                    Personalized Results
                                </p>

                                <h2 className="mt-1 text-2xl font-bold text-white">
                                    Recommended For You
                                </h2>
                            </div>

                            <p className="text-sm text-slate-400">
                                User{" "}
                                <span className="font-semibold text-white">
                                    {resultUserId}
                                </span>
                                {" · "}
                                {recommendations.length} movies
                            </p>

                        </div>


                        {/* Recommendation Grid */}
                        <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">

                            {recommendations.map((movie) => (

                                <article
                                    key={movie.movieId}
                                    className="flex h-full flex-col rounded-2xl border border-slate-800 bg-slate-900/80 p-5 transition hover:-translate-y-1 hover:border-slate-700 hover:shadow-xl"
                                >

                                    {/* Rank + Score */}
                                    <div className="mb-5 flex items-center justify-between gap-3">

                                        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-600 text-sm font-bold text-white">
                                            #{movie.rank}
                                        </span>

                                        <span className="text-sm font-semibold text-amber-400">
                                            Score{" "}
                                            {movie.score != null
                                                ? Number(
                                                    movie.score
                                                ).toFixed(3)
                                                : "N/A"}
                                        </span>

                                    </div>


                                    {/* Title */}
                                    <h3 className="text-xl font-semibold leading-snug text-white">
                                        {movie.title || "Untitled Movie"}
                                    </h3>


                                    {/* Genres */}
                                    <div className="mt-4 flex flex-wrap gap-2">

                                        {movie.genres?.length > 0 ? (
                                            movie.genres.map((genre) => (
                                                <span
                                                    key={genre}
                                                    className="rounded-full border border-blue-500/30 bg-blue-500/10 px-3 py-1 text-xs font-medium text-blue-300"
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


                                    {/* Release Year */}
                                    <div className="mt-auto pt-6">

                                        <p className="text-sm text-slate-500">
                                            Release Year
                                        </p>

                                        <p className="mt-1 font-medium text-slate-300">
                                            {movie.releaseYear ?? "N/A"}
                                        </p>

                                    </div>

                                </article>

                            ))}

                        </div>

                    </div>
                )}


            {/* Empty Results */}
            {!loading &&
                !error &&
                hasSearched &&
                recommendations.length === 0 && (

                    <div className="rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 px-6 py-14 text-center">

                        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-slate-800 text-xl">
                            🎬
                        </div>

                        <h2 className="mt-4 text-xl font-semibold text-white">
                            No recommendations available
                        </h2>

                        <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-slate-400">
                            No suitable movies were returned for this
                            user. Try another user ID or request again.
                        </p>

                    </div>
                )}

        </section>
    );
}

export default Recommendations;