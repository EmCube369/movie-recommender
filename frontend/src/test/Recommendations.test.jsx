import { render, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import Recommendations from "../components/Recommendations";
import { getRecommendations } from "../services/movieService";

vi.mock("../services/movieService", () => ({
    getMovies: vi.fn(),
    getMoviesById: vi.fn(),
    addMovie: vi.fn(),
    updateMovie: vi.fn(),
    deleteMovie: vi.fn(),
    getRecommendations: vi.fn(),
}));

const mockRecommendations = [
    {
        rank: 1,
        movieId: 922,
        title: "Sunset Boulevard",
        releaseYear: 1950,
        genres: ["Drama"],
        score: 0.806164,
    },
    {
        rank: 2,
        movieId: 6001,
        title: "The King of Comedy",
        releaseYear: 1982,
        genres: ["Drama", "Comedy"],
        score: 0.802498,
    },
    {
        rank: 3,
        movieId: 6669,
        title: "Ikiru",
        releaseYear: 1952,
        genres: ["Drama"],
        score: 0.790747,
    },
];

function renderRecommendations() {
    return render(
        <MemoryRouter>
            <Recommendations />
        </MemoryRouter>
    );
}

async function submitRecommendations() {
    const user = userEvent.setup();

    await user.click(
        screen.getByRole("button", {
            name: /get recommendations/i,
        })
    );

    return user;
}

describe("Recommendations Component", () => {

    beforeEach(() => {
        vi.clearAllMocks();

        getRecommendations.mockResolvedValue({
            data: {
                userId: 1,
                count: 3,
                recommendations: mockRecommendations,
            },
        });
    });

    it("renders recommendation controls without calling the API immediately", () => {
        renderRecommendations();

        expect(
            screen.getByRole("heading", {
                level: 1,
                name: "Recommendations",
            })
        ).toBeInTheDocument();

        expect(
            screen.getByLabelText("User ID")
        ).toHaveValue(1);

        expect(
            screen.getByLabelText("Number of Movies")
        ).toHaveValue(5);

        expect(getRecommendations).not.toHaveBeenCalled();
    });

    it("calls the recommendation API with the submitted values", async () => {
        renderRecommendations();

        await submitRecommendations();

        expect(getRecommendations).toHaveBeenCalledTimes(1);
        expect(getRecommendations).toHaveBeenCalledWith(1, 5);

        expect(
            await screen.findByText("Sunset Boulevard")
        ).toBeInTheDocument();
    });

    it("shows the generating state while recommendations are being fetched", async () => {
        getRecommendations.mockReturnValue(
            new Promise(() => { })
        );

        renderRecommendations();

        await submitRecommendations();

        expect(
            screen.getByRole("button", {
                name: /generating/i,
            })
        ).toBeDisabled();
    });

    it("renders recommendations returned by the API", async () => {
        renderRecommendations();

        await submitRecommendations();

        expect(
            await screen.findByRole("heading", {
                level: 2,
                name: "Recommended For You",
            })
        ).toBeInTheDocument();

        expect(
            screen.getByText("Sunset Boulevard")
        ).toBeInTheDocument();

        expect(
            screen.getByText("The King of Comedy")
        ).toBeInTheDocument();

        expect(
            screen.getByText("Ikiru")
        ).toBeInTheDocument();
    });

    it("renders recommendation information correctly", async () => {
        renderRecommendations();

        await submitRecommendations();

        const title = await screen.findByRole("heading", {
            level: 3,
            name: "The King of Comedy",
        });

        const card = title.closest("article");

        expect(card).not.toBeNull();

        expect(
            within(card).getByText("Drama")
        ).toBeInTheDocument();

        expect(
            within(card).getByText("Comedy")
        ).toBeInTheDocument();

        expect(
            within(card).getByText("1982")
        ).toBeInTheDocument();

        expect(
            within(card).getByText("Score 0.802")
        ).toBeInTheDocument();
    });

    it("does not treat recommendation cards as movie detail links", async () => {
        renderRecommendations();

        await submitRecommendations();
        await screen.findByText("Sunset Boulevard");

        expect(
            screen.queryByRole("link", {
                name: /sunset boulevard/i,
            })
        ).not.toBeInTheDocument();
    });

    it("shows an empty state when no recommendations are returned", async () => {
        getRecommendations.mockResolvedValue({
            data: {
                userId: 1,
                count: 0,
                recommendations: [],
            },
        });

        renderRecommendations();
        await submitRecommendations();

        expect(
            await screen.findByRole("heading", {
                level: 2,
                name: "No recommendations available",
            })
        ).toBeInTheDocument();

        expect(
            screen.queryByText("Sunset Boulevard")
        ).not.toBeInTheDocument();
    });

    it("shows the unknown-user error returned by the recommendation flow", async () => {
        const consoleErrorSpy = vi
            .spyOn(console, "error")
            .mockImplementation(() => { });

        getRecommendations.mockRejectedValue({
            response: {
                status: 404,
            },
        });

        renderRecommendations();
        await submitRecommendations();

        expect(
            await screen.findByText(
                "No recommendation profile was found for this user."
            )
        ).toBeInTheDocument();

        consoleErrorSpy.mockRestore();
    });

    it("shows a generic error when recommendation loading fails", async () => {
        const consoleErrorSpy = vi
            .spyOn(console, "error")
            .mockImplementation(() => { });

        getRecommendations.mockRejectedValue(
            new Error("Recommendation service unavailable")
        );

        renderRecommendations();
        await submitRecommendations();

        expect(
            await screen.findByText(
                "We couldn't generate recommendations right now. Please try again."
            )
        ).toBeInTheDocument();

        expect(
            screen.queryByText("Sunset Boulevard")
        ).not.toBeInTheDocument();

        expect(
            screen.getByRole("heading", {
                level: 2,
                name: "Unable to generate recommendations",
            })
        ).toBeInTheDocument();

        expect(
            screen.getByRole("button", {
                name: "Try Again",
            })
        ).toBeInTheDocument();

        consoleErrorSpy.mockRestore();
    });

});
