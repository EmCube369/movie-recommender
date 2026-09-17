import {
    useEffect,
    useState
} from "react";

import { getMovies } from "../services/movieService";

import MovieCard from "../components/MovieCard";


function Movies() {
    const [movies, setMovies] = useState([]);
    const [loading, setLoading] = useState(true);
    const [loadError, setLoadError] = useState("");

    const [searchTerm, setSearchTerm] = useState("");
    const [selectedGenre, setSelectedGenre] = useState("");


    const loadMovies = async () => {
        setLoading(true);
        setLoadError("");

        try {
            const response = await getMovies();

            setMovies(response.data);
        } catch (error) {
            console.error(
                "Error fetching movies:",
                error
            );

            setLoadError(
                "We couldn't load the movie library. Please try again."
            );
        } finally {
            setLoading(false);
        }
    };


    useEffect(() => {
        let active = true;

        const fetchMovies = async () => {
            try {
                const response = await getMovies();

                if (!active) {
                    return;
                }

                setMovies(response.data);
                setLoadError("");
            } catch (error) {
                if (!active) {
                    return;
                }

                console.error(
                    "Error fetching movies:",
                    error
                );

                setLoadError(
                    "We couldn't load the movie library. Please try again."
                );
            } finally {
                if (active) {
                    setLoading(false);
                }
            }
        };

        fetchMovies();

        return () => {
            active = false;
        };
    }, []);


    const genres = [
        ...new Set(
            movies
                .map((movie) => movie.genre)
                .filter(Boolean)
        )
    ].sort();


    const filteredMovies = movies.filter((movie) => {
        const matchesSearch = movie.title
            .toLowerCase()
            .includes(searchTerm.toLowerCase());

        const matchesGenre =
            selectedGenre === "" ||
            movie.genre === selectedGenre;

        return matchesSearch && matchesGenre;
    });


    const hasActiveFilters =
        searchTerm.trim() !== "" ||
        selectedGenre !== "";


    if (loading) {
        return (
            <section className="py-6 sm:py-8">

                <div className="mb-8">

                    <p className="mb-2 text-sm font-semibold uppercase
                                  tracking-widest text-blue-400">
                        Movie Library
                    </p>

                    <h1 className="text-3xl font-bold text-white sm:text-4xl">
                        Browse Movies
                    </h1>

                </div>


                <div
                    role="status"
                    aria-live="polite"
                    className="rounded-2xl border border-slate-800
                               bg-slate-900/60 px-6 py-16
                               text-center"
                >

                    <div
                        aria-hidden="true"
                        className="mx-auto h-9 w-9 animate-spin
                                   rounded-full border-4
                                   border-slate-700 border-t-blue-500
                                   motion-reduce:animate-none"
                    />

                    <h2 className="mt-5 text-lg font-semibold text-white">
                        Loading movies
                    </h2>

                    <p className="mt-2 text-sm text-slate-400">
                        Fetching the movie library...
                    </p>

                </div>

            </section>
        );
    }


    if (loadError) {
        return (
            <section className="py-6 sm:py-8">

                <div className="mb-8">

                    <p className="mb-2 text-sm font-semibold uppercase
                                  tracking-widest text-blue-400">
                        Movie Library
                    </p>

                    <h1 className="text-3xl font-bold text-white sm:text-4xl">
                        Browse Movies
                    </h1>

                </div>


                <div
                    role="alert"
                    className="rounded-2xl border border-red-900/60
                               bg-red-950/20 px-6 py-14 text-center"
                >

                    <div className="mx-auto flex h-12 w-12
                                    items-center justify-center
                                    rounded-full bg-red-500/10
                                    text-xl text-red-400">
                        !
                    </div>

                    <h2 className="mt-4 text-xl font-semibold text-white">
                        Unable to load movies
                    </h2>

                    <p className="mx-auto mt-2 max-w-md text-sm
                                  leading-6 text-slate-400">
                        {loadError}
                    </p>

                    <button
                        type="button"
                        onClick={loadMovies}
                        className="mt-6 rounded-xl bg-blue-600
                                   px-5 py-3 font-semibold text-white
                                   transition-colors hover:bg-blue-500
                                   focus-visible:outline-none
                                   focus-visible:ring-2
                                   focus-visible:ring-blue-500
                                   focus-visible:ring-offset-2
                                   focus-visible:ring-offset-slate-950
                                   motion-reduce:transition-none"
                    >
                        Retry
                    </button>

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
                    Movie Library
                </p>

                <h1 className="text-3xl font-bold text-white sm:text-4xl">
                    Browse Movies
                </h1>

                <p className="mt-3 max-w-2xl text-sm leading-6
                              text-slate-400 sm:text-base">
                    Search the movie collection, explore different
                    genres, and open a movie to view its details.
                </p>

            </div>


            {/* Empty Catalog */}
            {movies.length === 0 ? (

                <div className="rounded-2xl border border-dashed
                                border-slate-700 bg-slate-900/40
                                px-6 py-16 text-center">

                    <div className="mx-auto flex h-12 w-12
                                    items-center justify-center
                                    rounded-full bg-blue-500/10
                                    text-2xl">
                        🎬
                    </div>

                    <h2 className="mt-4 text-xl font-semibold text-white">
                        No movies available yet
                    </h2>

                    <p className="mx-auto mt-2 max-w-md text-sm
                                  leading-6 text-slate-400">
                        The movie catalog is currently empty.
                    </p>

                </div>

            ) : (
                <>

                    {/* Search + Filters */}
                    <div className="mb-8 rounded-2xl border
                                    border-slate-800 bg-slate-900/70
                                    p-4 sm:p-5">

                        <div className="flex flex-col gap-4 md:flex-row">

                            <div className="min-w-0 flex-1">

                                <label
                                    htmlFor="movie-search"
                                    className="mb-2 block text-sm
                                               font-medium text-slate-300"
                                >
                                    Search movies
                                </label>

                                <input
                                    id="movie-search"
                                    type="text"
                                    placeholder="Search by title..."
                                    value={searchTerm}
                                    onChange={(event) =>
                                        setSearchTerm(
                                            event.target.value
                                        )
                                    }
                                    className="w-full rounded-xl border
                                               border-slate-700
                                               bg-slate-950 px-4 py-3
                                               text-white outline-none
                                               transition
                                               placeholder:text-slate-500
                                               focus-visible:border-blue-500
                                               focus-visible:ring-2
                                               focus-visible:ring-blue-500/30
                                               motion-reduce:transition-none"
                                />

                            </div>


                            <div className="md:w-64">

                                <label
                                    htmlFor="genre-filter"
                                    className="mb-2 block text-sm
                                               font-medium text-slate-300"
                                >
                                    Genre
                                </label>

                                <select
                                    id="genre-filter"
                                    value={selectedGenre}
                                    onChange={(event) =>
                                        setSelectedGenre(
                                            event.target.value
                                        )
                                    }
                                    className="w-full rounded-xl border
                                               border-slate-700
                                               bg-slate-950 px-4 py-3
                                               text-white outline-none
                                               transition
                                               focus-visible:border-blue-500
                                               focus-visible:ring-2
                                               focus-visible:ring-blue-500/30
                                               motion-reduce:transition-none"
                                >

                                    <option value="">
                                        All Genres
                                    </option>

                                    {genres.map((genre) => (
                                        <option
                                            key={genre}
                                            value={genre}
                                        >
                                            {genre}
                                        </option>
                                    ))}

                                </select>

                            </div>

                        </div>


                        <div className="mt-4 flex flex-col gap-3
                                        border-t border-slate-800 pt-4
                                        sm:flex-row sm:items-center
                                        sm:justify-between">

                            <p className="text-sm text-slate-400">
                                Showing{" "}
                                <span className="font-semibold text-white">
                                    {filteredMovies.length}
                                </span>{" "}
                                of{" "}
                                <span className="font-semibold text-white">
                                    {movies.length}
                                </span>{" "}
                                movies
                            </p>


                            {hasActiveFilters && (
                                <button
                                    type="button"
                                    onClick={() => {
                                        setSearchTerm("");
                                        setSelectedGenre("");
                                    }}
                                    className="self-start text-sm
                                               font-semibold text-blue-400
                                               transition hover:text-blue-300
                                               focus-visible:outline-none
                                               focus-visible:ring-2
                                               focus-visible:ring-blue-500
                                               focus-visible:ring-offset-2
                                               focus-visible:ring-offset-slate-950
                                               sm:self-auto"
                                >
                                    Clear filters
                                </button>
                            )}

                        </div>

                    </div>


                    {/* Movie Grid */}
                    {filteredMovies.length > 0 ? (

                        <div className="grid grid-cols-1 gap-5
                                        sm:grid-cols-2
                                        lg:grid-cols-3
                                        xl:grid-cols-4">

                            {filteredMovies.map((movie) => (
                                <MovieCard
                                    key={movie.id}
                                    movie={movie}
                                />
                            ))}

                        </div>

                    ) : (

                        <div className="rounded-2xl border border-dashed
                                        border-slate-700 bg-slate-900/40
                                        px-6 py-14 text-center">

                            <h2 className="text-xl font-semibold text-white">
                                No movies match your search
                            </h2>

                            <p className="mt-2 text-sm text-slate-400">
                                Try a different title or genre,
                                or clear the current filters.
                            </p>

                            <button
                                type="button"
                                onClick={() => {
                                    setSearchTerm("");
                                    setSelectedGenre("");
                                }}
                                className="mt-5 rounded-xl border
                                           border-slate-700 bg-slate-800
                                           px-4 py-2.5 text-sm
                                           font-semibold text-white
                                           transition
                                           hover:border-slate-600
                                           hover:bg-slate-700
                                           focus-visible:outline-none
                                           focus-visible:ring-2
                                           focus-visible:ring-blue-500
                                           focus-visible:ring-offset-2
                                           focus-visible:ring-offset-slate-950"
                            >
                                Clear filters
                            </button>

                        </div>
                    )}

                </>
            )}

        </section>
    );
}


export default Movies;