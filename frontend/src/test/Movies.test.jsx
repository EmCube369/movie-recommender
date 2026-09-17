import {
    render,
    screen,
    within,
} from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import Movies from "../pages/Movies";
import {
    getMovies,
} from "../services/movieService";

vi.mock("../services/movieService", () => ({
    getMovies: vi.fn(),
}));

vi.mock("../context/AuthContext", () => ({
    useAuth: () => ({
        isAuthenticated: false,
        authLoading: false,
    }),
}));

const mockMovies = [
    {
        id: 1,
        title: "Inception",
        genre: "Sci-Fi",
        releaseYear: 2010,
        tmdbRating: 8.8,
    },
    {
        id: 2,
        title: "The Dark Knight",
        genre: "Action",
        releaseYear: 2008,
        tmdbRating: 9.0,
    },
    {
        id: 3,
        title: "Interstellar",
        genre: "Sci-Fi",
        releaseYear: 2014,
        tmdbRating: null,
    },
];

function renderMovies() {
    return render(
        <MemoryRouter>
            <Movies />
        </MemoryRouter>
    );
}

function getMovieCard(title) {
    const movieLink = screen.getByRole("link", {
        name: new RegExp(title, "i"),
    });

    return movieLink.closest("article");
}

describe("Movies Page", () => {

    beforeEach(() => {
        vi.clearAllMocks();

        getMovies.mockResolvedValue({
            data: mockMovies,
        });
    });

    it("fetches and renders the movies page", async () => {
        renderMovies();

        expect(
            screen.getByText("Loading movies")
        ).toBeInTheDocument();

        expect(
            await screen.findByText("Inception")
        ).toBeInTheDocument();

        expect(
            screen.getByRole("heading", {
                level: 1,
                name: "Browse Movies",
            })
        ).toBeInTheDocument();

        expect(getMovies).toHaveBeenCalledTimes(1);
    });

    it("renders movies returned by the API", async () => {
        renderMovies();

        expect(
            await screen.findByText("Inception")
        ).toBeInTheDocument();

        expect(
            screen.getByText("The Dark Knight")
        ).toBeInTheDocument();

        expect(
            screen.getByText("Interstellar")
        ).toBeInTheDocument();
    });

    it("renders movie information correctly", async () => {
        renderMovies();

        await screen.findByText("The Dark Knight");

        const card = getMovieCard("The Dark Knight");

        expect(card).not.toBeNull();
        expect(within(card).getByText("Action")).toBeInTheDocument();
        expect(within(card).getByText("2008")).toBeInTheDocument();
        expect(
            within(card).getByText(/TMDB\s*9/)
        ).toBeInTheDocument();
    });

    it("displays N/A when TMDB rating is missing", async () => {
        renderMovies();

        await screen.findByText("Interstellar");

        const card = getMovieCard("Interstellar");

        expect(
            within(card).getByText(/TMDB\s*N\/A/)
        ).toBeInTheDocument();
    });

    it("renders movie detail links with the correct IDs", async () => {
        renderMovies();

        const inceptionLink = await screen.findByRole("link", {
            name: /inception/i,
        });

        const darkKnightLink = screen.getByRole("link", {
            name: /the dark knight/i,
        });

        expect(inceptionLink).toHaveAttribute(
            "href",
            "/movies/1"
        );

        expect(darkKnightLink).toHaveAttribute(
            "href",
            "/movies/2"
        );
    });

    it("filters movies by search term", async () => {
        const user = userEvent.setup();

        renderMovies();
        await screen.findByText("Inception");

        const searchInput = screen.getByRole("textbox", {
            name: /search movies/i,
        });

        await user.type(searchInput, "dark");

        expect(
            screen.getByText("The Dark Knight")
        ).toBeInTheDocument();

        expect(
            screen.queryByText("Inception")
        ).not.toBeInTheDocument();

        expect(
            screen.queryByText("Interstellar")
        ).not.toBeInTheDocument();
    });

    it("searches movies case-insensitively", async () => {
        const user = userEvent.setup();

        renderMovies();
        await screen.findByText("Inception");

        await user.type(
            screen.getByRole("textbox", {
                name: /search movies/i,
            }),
            "INCEPTION"
        );

        expect(
            screen.getByText("Inception")
        ).toBeInTheDocument();

        expect(
            screen.queryByText("The Dark Knight")
        ).not.toBeInTheDocument();
    });

    it("filters movies by genre", async () => {
        const user = userEvent.setup();

        renderMovies();
        await screen.findByText("Inception");

        await user.selectOptions(
            screen.getByRole("combobox", {
                name: "Genre",
            }),
            "Sci-Fi"
        );

        expect(screen.getByText("Inception")).toBeInTheDocument();
        expect(screen.getByText("Interstellar")).toBeInTheDocument();
        expect(screen.queryByText("The Dark Knight")).not.toBeInTheDocument();
    });

    it("applies search and genre filters together", async () => {
        const user = userEvent.setup();

        renderMovies();
        await screen.findByText("Inception");

        await user.selectOptions(
            screen.getByRole("combobox", {
                name: "Genre",
            }),
            "Sci-Fi"
        );

        await user.type(
            screen.getByRole("textbox", {
                name: /search movies/i,
            }),
            "inter"
        );

        expect(screen.getByText("Interstellar")).toBeInTheDocument();
        expect(screen.queryByText("Inception")).not.toBeInTheDocument();
        expect(screen.queryByText("The Dark Knight")).not.toBeInTheDocument();
    });

    it("clears active filters", async () => {
        const user = userEvent.setup();

        renderMovies();
        await screen.findByText("Inception");

        await user.type(
            screen.getByRole("textbox", {
                name: /search movies/i,
            }),
            "dark"
        );

        await user.click(
            screen.getByRole("button", {
                name: "Clear filters",
            })
        );

        expect(screen.getByText("Inception")).toBeInTheDocument();
        expect(screen.getByText("The Dark Knight")).toBeInTheDocument();
        expect(screen.getByText("Interstellar")).toBeInTheDocument();
    });

    it("shows loading state while movies are being fetched", () => {
        getMovies.mockReturnValue(
            new Promise(() => { })
        );

        renderMovies();

        expect(
            screen.getByRole("heading", {
                level: 1,
                name: "Browse Movies",
            })
        ).toBeInTheDocument();

        expect(
            screen.getByText("Loading movies")
        ).toBeInTheDocument();

        expect(
            screen.queryByRole("textbox", {
                name: /search movies/i,
            })
        ).not.toBeInTheDocument();
    });

    it("shows an error message when loading movies fails", async () => {
        const consoleErrorSpy = vi
            .spyOn(console, "error")
            .mockImplementation(() => { });

        getMovies.mockRejectedValue(
            new Error("Backend unavailable")
        );

        renderMovies();

        expect(
            await screen.findByText(
                "We couldn't load the movie library. Please try again."
            )
        ).toBeInTheDocument();

        expect(
            screen.getByRole("heading", {
                level: 1,
                name: "Browse Movies",
            })
        ).toBeInTheDocument();

        expect(
            screen.getByRole("button", {
                name: "Retry",
            })
        ).toBeInTheDocument();

        consoleErrorSpy.mockRestore();
    });

    it("retries loading movies after an error", async () => {
        const user = userEvent.setup();

        const consoleErrorSpy = vi
            .spyOn(console, "error")
            .mockImplementation(() => { });

        getMovies
            .mockRejectedValueOnce(
                new Error("Temporary failure")
            )
            .mockResolvedValueOnce({
                data: mockMovies,
            });

        renderMovies();

        await screen.findByText(
            "We couldn't load the movie library. Please try again."
        );

        await user.click(
            screen.getByRole("button", {
                name: "Retry",
            })
        );

        expect(
            await screen.findByText("Inception")
        ).toBeInTheDocument();

        expect(getMovies).toHaveBeenCalledTimes(2);

        consoleErrorSpy.mockRestore();
    });


});
