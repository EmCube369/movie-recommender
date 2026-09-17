import { Link } from "react-router-dom";


function MovieCard({ movie }) {
    return (
        <article
            className="group flex h-full flex-col overflow-hidden
                       rounded-2xl border border-slate-800
                       bg-slate-900/80 transition
                       hover:-translate-y-1
                       hover:border-slate-700
                       hover:shadow-xl
                       motion-reduce:transform-none
                       motion-reduce:transition-none"
        >

            <Link
                to={`/movies/${movie.id}`}
                className="flex flex-1 flex-col p-5
                           focus-visible:outline-none
                           focus-visible:ring-2
                           focus-visible:ring-inset
                           focus-visible:ring-blue-500"
            >

                <div className="mb-5 flex items-start
                                justify-between gap-3">

                    <span
                        className="max-w-full rounded-full
                                   border border-blue-500/30
                                   bg-blue-500/10 px-3 py-1
                                   text-xs font-medium text-blue-300"
                    >
                        {movie.genre || "Unknown"}
                    </span>

                    <span
                        className="shrink-0 text-sm font-semibold text-amber-400"
                    >
                        TMDB {movie.tmdbRating ?? "N/A"}
                    </span>

                </div>


                <h2
                    className="wrap-break-word text-xl font-semibold
                               leading-snug text-white transition
                               group-hover:text-blue-300
                               motion-reduce:transition-none"
                >
                    {movie.title}
                </h2>


                <div className="mt-auto pt-6">

                    <p className="text-sm text-slate-500">
                        Release Year
                    </p>

                    <p className="mt-1 font-medium text-slate-300">
                        {movie.releaseYear ?? "N/A"}
                    </p>

                </div>

            </Link>

        </article>
    );
}


export default MovieCard;