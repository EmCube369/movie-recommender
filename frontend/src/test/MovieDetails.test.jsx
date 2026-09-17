import {
    render,
    screen,
    within,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import {
    MemoryRouter,
    Route,
    Routes,
} from "react-router-dom";
import {
    beforeEach,
    describe,
    expect,
    it,
    vi,
} from "vitest";

import MovieDetails from "../pages/MovieDetails";
import { getMoviesById } from "../services/movieService";

vi.mock("../context/AuthContext", () => ({
    useAuth: vi.fn(() => ({
        isAuthenticated: false,
        authLoading: false,
    })),
}));

vi.mock("../services/movieService", () => ({
    getMoviesById: vi.fn(),
}));

vi.mock("../services/userMovieService", () => ({
    getMovieActivity: vi.fn(),
    markMovieWatched: vi.fn(),
    rateMovie: vi.fn(),
}));

const mockMovie = {
    id: 10,
    title: "Inception",
    genre: "Sci-Fi",
    releaseYear: 2010,
    tmdbRating: 8.8,
};

function renderMovieDetails(id = "10") {
    return render(
        <MemoryRouter initialEntries={[`/movies/${id}`]}>
            <Routes>
                <Route
                    path="/movies/:id"
                    element={<MovieDetails />}
                />
            </Routes>
        </MemoryRouter>
    );
}

describe("Movie Details Page", () => {
    beforeEach(() => {
        vi.clearAllMocks();

        getMoviesById.mockResolvedValue({
            data: mockMovie,
        });
    });

    it("fetches the movie using the route ID", async () => {
        renderMovieDetails("10");

        await screen.findByRole("heading", {
            level: 1,
            name: "Inception",
        });

        expect(getMoviesById).toHaveBeenCalledTimes(1);
        expect(getMoviesById).toHaveBeenCalledWith("10");
    });

    it("renders the movie details correctly", async () => {
        renderMovieDetails();

        expect(
            await screen.findByRole("heading", {
                level: 1,
                name: "Inception",
            })
        ).toBeInTheDocument();

        expect(
            screen.getAllByText("Sci-Fi").length
        ).toBeGreaterThan(0);

        expect(
            screen.getAllByText("2010").length
        ).toBeGreaterThan(0);

        const ratingLabel =
            screen.getByText("TMDB Rating");

        const ratingSection =
            ratingLabel.closest("div");

        expect(ratingSection).not.toBeNull();
        expect(ratingSection).toHaveTextContent("8.8");
        expect(ratingSection).toHaveTextContent("/ 10");
    });

    it("shows the loading state while movie details are being fetched", () => {
        getMoviesById.mockReturnValue(
            new Promise(() => { })
        );

        renderMovieDetails();

        expect(
            screen.getByRole("heading", {
                level: 1,
                name: "Loading movie details",
            })
        ).toBeInTheDocument();

        expect(
            screen.queryByText("Inception")
        ).not.toBeInTheDocument();
    });

    it("shows the not-found state for a 404 response", async () => {
        const consoleErrorSpy = vi
            .spyOn(console, "error")
            .mockImplementation(() => { });

        getMoviesById.mockRejectedValue({
            response: {
                status: 404,
            },
        });

        renderMovieDetails();

        expect(
            await screen.findByRole("heading", {
                level: 1,
                name: "Movie not found",
            })
        ).toBeInTheDocument();

        expect(
            screen.queryByText("Inception")
        ).not.toBeInTheDocument();

        consoleErrorSpy.mockRestore();
    });

    it("shows an error message when the API request fails", async () => {
        const consoleErrorSpy = vi
            .spyOn(console, "error")
            .mockImplementation(() => { });

        getMoviesById.mockRejectedValue(
            new Error("Movie API unavailable")
        );

        renderMovieDetails();

        expect(
            await screen.findByRole("heading", {
                level: 1,
                name: "Unable to load movie",
            })
        ).toBeInTheDocument();

        expect(
            screen.getByText(
                "We couldn't load the movie details. Please try again."
            )
        ).toBeInTheDocument();

        consoleErrorSpy.mockRestore();
    });

    it("retries loading after an error", async () => {
        const user = userEvent.setup();

        const consoleErrorSpy = vi
            .spyOn(console, "error")
            .mockImplementation(() => { });

        getMoviesById
            .mockRejectedValueOnce(
                new Error("Temporary failure")
            )
            .mockResolvedValueOnce({
                data: mockMovie,
            });

        renderMovieDetails();

        await screen.findByRole("heading", {
            level: 1,
            name: "Unable to load movie",
        });

        await user.click(
            screen.getByRole("button", {
                name: "Retry",
            })
        );

        expect(
            await screen.findByRole("heading", {
                level: 1,
                name: "Inception",
            })
        ).toBeInTheDocument();

        expect(getMoviesById).toHaveBeenCalledTimes(2);

        consoleErrorSpy.mockRestore();
    });

    it("displays N/A when TMDB Rating is missing", async () => {
        getMoviesById.mockResolvedValue({
            data: {
                ...mockMovie,
                tmdbRating: null,
            },
        });

        renderMovieDetails();

        await screen.findByRole("heading", {
            level: 1,
            name: "Inception",
        });

        const ratingLabel =
            screen.getByText("TMDB Rating");

        const ratingSection =
            ratingLabel.closest("div");

        expect(ratingSection).not.toBeNull();
        expect(
            within(ratingSection).getByText("N/A")
        ).toBeInTheDocument();
    });

    it("renders back navigation to the movies page", async () => {
        renderMovieDetails();

        await screen.findByRole("heading", {
            level: 1,
            name: "Inception",
        });

        const backLink = screen.getByRole("link", {
            name: /back to movies/i,
        });

        expect(backLink).toHaveAttribute(
            "href",
            "/movies"
        );
    });
});
