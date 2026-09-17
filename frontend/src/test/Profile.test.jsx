import {
    fireEvent,
    render,
    screen,
    waitFor
} from "@testing-library/react";

import { MemoryRouter } from "react-router-dom";
import { beforeEach, describe, expect, it, vi } from "vitest";

import Profile from "../pages/Profile";
import { useAuth } from "../context/AuthContext";

import {
    getUserLibrary,
    rateMovie,
    removeMovieActivity
} from "../services/userMovieService";


vi.mock("../context/AuthContext", () => ({
    useAuth: vi.fn()
}));

vi.mock("../services/userMovieService", () => ({
    getUserLibrary: vi.fn(),
    rateMovie: vi.fn(),
    removeMovieActivity: vi.fn()
}));


const movie = {
    movieId: 1,
    title: "Inception",
    genre: "Sci-Fi",
    releaseYear: 2010,
    tmdbRating: 8.8,
    rating: 4
};


function renderProfile() {
    return render(
        <MemoryRouter>
            <Profile />
        </MemoryRouter>
    );
}


describe("Profile", () => {

    beforeEach(() => {
        vi.clearAllMocks();

        useAuth.mockReturnValue({
            user: {
                username: "testuser",
                role: "USER"
            }
        });
    });


    it("shows the logged-in user's account information", async () => {

        getUserLibrary.mockResolvedValue({
            data: []
        });

        renderProfile();

        expect(
            await screen.findByText("testuser")
        ).toBeInTheDocument();

        expect(
            screen.getByText("USER")
        ).toBeInTheDocument();
    });


    it("loads and displays movies from the user's library", async () => {

        getUserLibrary.mockResolvedValue({
            data: [movie]
        });

        renderProfile();

        expect(
            await screen.findByText("Inception")
        ).toBeInTheDocument();

        expect(
            screen.getByText("Sci-Fi")
        ).toBeInTheDocument();

        expect(
            screen.getByText("2010")
        ).toBeInTheDocument();

        expect(
            screen.getByText(/8\.8/)
        ).toBeInTheDocument();
    });


    it("shows the empty state when the user has no movies", async () => {

        getUserLibrary.mockResolvedValue({
            data: []
        });

        renderProfile();

        expect(
            await screen.findByText("Your library is empty")
        ).toBeInTheDocument();

        expect(
            screen.getByRole("link", {
                name: "Browse Movies"
            })
        ).toHaveAttribute(
            "href",
            "/movies"
        );
    });


    it("shows the user's existing rating", async () => {

        getUserLibrary.mockResolvedValue({
            data: [movie]
        });

        renderProfile();

        expect(
            await screen.findByText("4 / 5")
        ).toBeInTheDocument();
    });


    it("allows the user to change a movie rating", async () => {

        getUserLibrary.mockResolvedValue({
            data: [movie]
        });

        rateMovie.mockResolvedValue({
            data: {
                movieId: 1,
                watched: true,
                rating: 5
            }
        });

        renderProfile();

        await screen.findByText("Inception");

        fireEvent.click(
            screen.getByRole("button", {
                name: "Rate 5 out of 5"
            })
        );

        await waitFor(() => {
            expect(rateMovie).toHaveBeenCalledWith(
                1,
                5
            );
        });

        expect(
            await screen.findByText("5 / 5")
        ).toBeInTheDocument();
    });


    it("removes a movie from the library", async () => {

        getUserLibrary.mockResolvedValue({
            data: [movie]
        });

        removeMovieActivity.mockResolvedValue({});

        renderProfile();

        expect(
            await screen.findByText("Inception")
        ).toBeInTheDocument();

        fireEvent.click(
            screen.getByRole("button", {
                name: "Remove from Library"
            })
        );

        await waitFor(() => {
            expect(
                removeMovieActivity
            ).toHaveBeenCalledWith(1);
        });

        await waitFor(() => {
            expect(
                screen.queryByText("Inception")
            ).not.toBeInTheDocument();
        });

        expect(
            screen.getByText("Your library is empty")
        ).toBeInTheDocument();
    });


    it("shows an error when the library cannot be loaded", async () => {

        getUserLibrary.mockRejectedValue(
            new Error("Request failed")
        );

        renderProfile();

        expect(
            await screen.findByText(
                "We couldn't load your movie library. Please try again."
            )
        ).toBeInTheDocument();

        expect(
            screen.getByRole("button", {
                name: "Retry"
            })
        ).toBeInTheDocument();
    });


    it("loads the library when retry succeeds", async () => {

        getUserLibrary
            .mockRejectedValueOnce(
                new Error("Request failed")
            )
            .mockResolvedValueOnce({
                data: [movie]
            });

        renderProfile();

        const retryButton =
            await screen.findByRole(
                "button",
                {
                    name: "Retry"
                }
            );

        fireEvent.click(retryButton);

        expect(
            await screen.findByText("Inception")
        ).toBeInTheDocument();

        expect(
            getUserLibrary
        ).toHaveBeenCalledTimes(2);
    });

});