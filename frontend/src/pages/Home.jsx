import { Link } from "react-router-dom";

function Home() {

    const primaryButtonClasses =
        "rounded-lg bg-red-600 px-5 py-3 text-center font-medium text-white " +
        "transition-colors hover:bg-red-700 " +
        "focus-visible:outline-none focus-visible:ring-2 " +
        "focus-visible:ring-red-500 focus-visible:ring-offset-2 " +
        "focus-visible:ring-offset-gray-950 " +
        "motion-reduce:transition-none";


    const secondaryButtonClasses =
        "rounded-lg border border-gray-700 px-5 py-3 text-center " +
        "font-medium text-gray-200 transition-colors " +
        "hover:border-gray-600 hover:bg-gray-800 hover:text-white " +
        "focus-visible:outline-none focus-visible:ring-2 " +
        "focus-visible:ring-blue-500 focus-visible:ring-offset-2 " +
        "focus-visible:ring-offset-gray-950 " +
        "motion-reduce:transition-none";


    return (
        <div className="space-y-14">

            {/* Hero Section */}
            <section
                className="overflow-hidden rounded-2xl border border-gray-800
                           bg-linear-to-br from-gray-900 to-gray-950"
            >
                <div className="grid gap-10 px-6 py-12 sm:px-10 sm:py-14
                                lg:grid-cols-2 lg:items-center">

                    {/* Hero Text */}
                    <div>

                        <p className="mb-3 text-xs font-semibold uppercase
                                      tracking-wider text-red-500 sm:text-sm">
                            Movie Recommendation System
                        </p>

                        <h1 className="text-3xl font-bold leading-tight text-white
                                       sm:text-4xl lg:text-5xl">
                            Find movies you&apos;ll enjoy watching
                        </h1>

                        <p className="mt-5 max-w-xl text-base leading-7
                                      text-gray-400 sm:text-lg">
                            Browse movies, explore their details, and discover
                            personalized recommendations based on your preferences.
                        </p>


                        {/* Hero Actions */}
                        <div className="mt-8 flex flex-col gap-3 sm:flex-row">

                            <Link
                                to="/movies"
                                className={primaryButtonClasses}
                            >
                                Browse Movies
                            </Link>

                            <a
                                href="#features"
                                className={secondaryButtonClasses}
                            >
                                Learn More
                            </a>

                        </div>

                    </div>


                    {/* Recommendation Info */}
                    <div className="rounded-xl border border-gray-800
                                    bg-gray-900/70 p-6">

                        <h2 className="text-lg font-semibold text-white">
                            How recommendations work
                        </h2>

                        <p className="mt-2 text-sm leading-6 text-gray-400">
                            MovieRecommender combines different recommendation
                            signals to rank movies that may match your interests.
                        </p>


                        <div className="mt-6 space-y-4">

                            {/* Step 1 */}
                            <div className="flex items-start gap-3">

                                <div
                                    className="flex h-8 w-8 shrink-0 items-center
                                               justify-center rounded-full
                                               bg-red-600/20 text-sm font-semibold
                                               text-red-400"
                                    aria-hidden="true"
                                >
                                    1
                                </div>

                                <div>
                                    <h3 className="font-medium text-white">
                                        User Preferences
                                    </h3>

                                    <p className="text-sm text-gray-400">
                                        Learn from movie rating patterns.
                                    </p>
                                </div>

                            </div>


                            {/* Step 2 */}
                            <div className="flex items-start gap-3">

                                <div
                                    className="flex h-8 w-8 shrink-0 items-center
                                               justify-center rounded-full
                                               bg-red-600/20 text-sm font-semibold
                                               text-red-400"
                                    aria-hidden="true"
                                >
                                    2
                                </div>

                                <div>
                                    <h3 className="font-medium text-white">
                                        Movie Similarity
                                    </h3>

                                    <p className="text-sm text-gray-400">
                                        Compare movie genres and content features.
                                    </p>
                                </div>

                            </div>


                            {/* Step 3 */}
                            <div className="flex items-start gap-3">

                                <div
                                    className="flex h-8 w-8 shrink-0 items-center
                                               justify-center rounded-full
                                               bg-red-600/20 text-sm font-semibold
                                               text-red-400"
                                    aria-hidden="true"
                                >
                                    3
                                </div>

                                <div>
                                    <h3 className="font-medium text-white">
                                        Hybrid Ranking
                                    </h3>

                                    <p className="text-sm text-gray-400">
                                        Combine preference, similarity, and
                                        sentiment signals for final ranking.
                                    </p>
                                </div>

                            </div>

                        </div>

                    </div>

                </div>
            </section>


            {/* Features Section */}
            <section
                id="features"
                className="scroll-mt-6 pt-4"
                aria-labelledby="features-heading"
            >

                <div className="mb-6">

                    <h2
                        id="features-heading"
                        className="text-2xl font-bold text-white sm:text-3xl"
                    >
                        What you can do
                    </h2>

                    <p className="mt-2 text-gray-400">
                        Explore the movie catalog and discover recommendations
                        made for you.
                    </p>

                </div>


                <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">

                    {/* Feature 1 */}
                    <div
                        className="rounded-xl border border-gray-800
                                   bg-gray-900 p-5 sm:min-h-32 sm:p-6"
                    >
                        <h3 className="text-lg font-semibold text-white">
                            Browse Movies
                        </h3>

                        <p className="mt-2 text-sm leading-6 text-gray-400">
                            Search the movie catalog and filter movies by genre.
                        </p>
                    </div>


                    {/* Feature 2 */}
                    <div
                        className="rounded-xl border border-gray-800
                                   bg-gray-900 p-5 sm:min-h-32 sm:p-6"
                    >
                        <h3 className="text-lg font-semibold text-white">
                            View Movie Details
                        </h3>

                        <p className="mt-2 text-sm leading-6 text-gray-400">
                            Check movie information such as genre, release year,
                            and TMDB rating.
                        </p>
                    </div>


                    {/* Feature 3 */}
                    <div
                        className="rounded-xl border border-gray-800 bg-gray-900
                                   p-5 sm:col-span-2 sm:min-h-32 sm:p-6
                                   lg:col-span-1"
                    >
                        <h3 className="text-lg font-semibold text-white">
                            Personalized Recommendations
                        </h3>

                        <p className="mt-2 text-sm leading-6 text-gray-400">
                            Discover movies ranked using a hybrid recommendation
                            system.
                        </p>
                    </div>

                </div>

            </section>

        </div>
    );
}

export default Home;