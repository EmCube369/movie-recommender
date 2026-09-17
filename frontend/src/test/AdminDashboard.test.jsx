import {
    fireEvent,
    render,
    screen,
    waitFor
} from "@testing-library/react";

import { MemoryRouter } from "react-router-dom";
import {
    afterEach,
    beforeEach,
    describe,
    expect,
    it,
    vi
} from "vitest";

import AdminDashboard from "../pages/AdminDashboard";

import { getMovies } from "../services/movieService";

import {
    addAdminMovie,
    deleteAdminMovie,
    searchMlMovies,
    getAdminUsers,
    deleteAdminUser
} from "../services/adminService";

import { useAuth } from "../context/AuthContext";


vi.mock("../services/movieService", () => ({
    getMovies: vi.fn()
}));


vi.mock("../services/adminService", () => ({
    addAdminMovie: vi.fn(),
    deleteAdminMovie: vi.fn(),
    searchMlMovies: vi.fn(),
    getAdminUsers: vi.fn(),
    deleteAdminUser: vi.fn()
}));


vi.mock("../context/AuthContext", () => ({
    useAuth: vi.fn()
}));


function renderDashboard() {

    return render(
        <MemoryRouter>
            <AdminDashboard />
        </MemoryRouter>
    );
}


describe("AdminDashboard", () => {

    beforeEach(() => {

        vi.clearAllMocks();

        useAuth.mockReturnValue({
            user: {
                username: "admin",
                role: "ADMIN"
            }
        });

        getMovies.mockResolvedValue({
            data: [
                {
                    id: 10,
                    mlMovieId: 79132,
                    title: "Inception",
                    genre: "Sci-Fi",
                    releaseYear: 2010,
                    tmdbRating: 8.8
                }
            ]
        });

        getAdminUsers.mockResolvedValue({
            data: [
                {
                    id: 1,
                    username: "admin",
                    role: "ADMIN"
                },
                {
                    id: 2,
                    username: "marshal",
                    role: "USER"
                }
            ]
        });

        window.confirm = vi.fn(() => true);
    });


    afterEach(() => {
        vi.restoreAllMocks();
    });


    it("loads and displays movies and users", async () => {

        renderDashboard();

        expect(
            await screen.findByText("Inception")
        ).toBeInTheDocument();

        expect(
            await screen.findByText("marshal")
        ).toBeInTheDocument();

        expect(getMovies)
            .toHaveBeenCalledTimes(1);

        expect(getAdminUsers)
            .toHaveBeenCalledTimes(1);
    });


    it("protects admin accounts from deletion", async () => {

        renderDashboard();

        await screen.findByText("marshal");

        const protectedButtons =
            screen.getAllByRole(
                "button",
                {
                    name: "Protected"
                }
            );

        expect(protectedButtons.length)
            .toBeGreaterThanOrEqual(1);

        expect(protectedButtons[0])
            .toBeDisabled();

        expect(
            screen.getByRole(
                "button",
                {
                    name: "Delete User"
                }
            )
        ).toBeEnabled();
    });


    it("deletes a normal user", async () => {

        deleteAdminUser.mockResolvedValue({});

        renderDashboard();

        await screen.findByText("marshal");

        fireEvent.click(
            screen.getByRole(
                "button",
                {
                    name: "Delete User"
                }
            )
        );

        await waitFor(() => {
            expect(deleteAdminUser)
                .toHaveBeenCalledWith(2);
        });

        expect(
            await screen.findByText(
                'User "marshal" was deleted.'
            )
        ).toBeInTheDocument();
    });


    it("searches the ML catalog and adds a movie", async () => {

        searchMlMovies.mockResolvedValue({
            data: {
                movies: [
                    {
                        movieId: 58559,
                        title: "The Dark Knight",
                        releaseYear: 2008,
                        genres: [
                            "Action",
                            "Crime",
                            "Thriller"
                        ],
                        recommendationSupported: true
                    }
                ]
            }
        });

        addAdminMovie.mockResolvedValue({
            data: {
                id: 20,
                mlMovieId: 58559,
                title: "The Dark Knight",
                genre: "Action, Crime, Thriller",
                releaseYear: 2008,
                tmdbRating: 9.0
            }
        });

        renderDashboard();

        await screen.findByText("Inception");

        fireEvent.click(
            screen.getByRole(
                "button",
                {
                    name: "Add Movie"
                }
            )
        );

        fireEvent.change(
            screen.getByLabelText(
                "Search ML movies"
            ),
            {
                target: {
                    value: "  Dark Knight  "
                }
            }
        );

        fireEvent.click(
            screen.getByRole(
                "button",
                {
                    name: "Search"
                }
            )
        );

        await waitFor(() => {
            expect(searchMlMovies)
                .toHaveBeenCalledWith(
                    "Dark Knight",
                    20
                );
        });

        expect(
            await screen.findByText(
                "The Dark Knight"
            )
        ).toBeInTheDocument();

        fireEvent.click(
            screen.getByRole(
                "button",
                {
                    name: "Add"
                }
            )
        );

        await waitFor(() => {
            expect(addAdminMovie)
                .toHaveBeenCalledWith(
                    58559
                );
        });

        expect(
            await screen.findByText(
                '"The Dark Knight" was added to the catalog.'
            )
        ).toBeInTheDocument();
    });


    it("removes a movie from the catalog", async () => {

        deleteAdminMovie.mockResolvedValue({});

        renderDashboard();

        await screen.findByText("Inception");

        fireEvent.click(
            screen.getByRole(
                "button",
                {
                    name: "Remove"
                }
            )
        );

        await waitFor(() => {
            expect(deleteAdminMovie)
                .toHaveBeenCalledWith(10);
        });

        expect(
            await screen.findByText(
                '"Inception" was removed from the catalog.'
            )
        ).toBeInTheDocument();
    });


    it("shows validation error for an empty ML search", async () => {

        renderDashboard();

        await screen.findByText("Inception");

        fireEvent.click(
            screen.getByRole(
                "button",
                {
                    name: "Add Movie"
                }
            )
        );

        fireEvent.click(
            screen.getByRole(
                "button",
                {
                    name: "Search"
                }
            )
        );

        expect(
            screen.getByText(
                "Enter a movie title to search."
            )
        ).toBeInTheDocument();

        expect(searchMlMovies)
            .not.toHaveBeenCalled();
    });

    it("shows movie catalog load error and retries", async () => {

        getMovies
            .mockRejectedValueOnce(
                new Error("Catalog unavailable")
            )
            .mockResolvedValueOnce({
                data: []
            });

        renderDashboard();

        expect(
            await screen.findByText(
                "We couldn't load the movie catalog."
            )
        ).toBeInTheDocument();

        const retryButtons =
            screen.getAllByRole(
                "button",
                {
                    name: "Retry"
                }
            );

        fireEvent.click(retryButtons[0]);

        await waitFor(() => {
            expect(getMovies)
                .toHaveBeenCalledTimes(2);
        });
    });


    it("shows user load error and retries", async () => {

        getAdminUsers
            .mockRejectedValueOnce(
                new Error("Users unavailable")
            )
            .mockResolvedValueOnce({
                data: []
            });

        renderDashboard();

        expect(
            await screen.findByText(
                "We couldn't load registered users."
            )
        ).toBeInTheDocument();

        const retryButtons =
            screen.getAllByRole(
                "button",
                {
                    name: "Retry"
                }
            );

        fireEvent.click(
            retryButtons[
            retryButtons.length - 1
            ]
        );

        await waitFor(() => {
            expect(getAdminUsers)
                .toHaveBeenCalledTimes(2);
        });
    });


    it("shows movie deletion error returned by backend", async () => {

        deleteAdminMovie.mockRejectedValue({
            response: {
                data: {
                    message:
                        "Movie cannot be removed because users have activity for it."
                }
            }
        });

        renderDashboard();

        await screen.findByText("Inception");

        fireEvent.click(
            screen.getByRole(
                "button",
                {
                    name: "Remove"
                }
            )
        );

        expect(
            await screen.findByText(
                "Movie cannot be removed because users have activity for it."
            )
        ).toBeInTheDocument();

        expect(
            screen.getByText("Inception")
        ).toBeInTheDocument();
    });


    it("shows user deletion error returned by backend", async () => {

        deleteAdminUser.mockRejectedValue({
            response: {
                data: {
                    message:
                        "Failed to delete user account."
                }
            }
        });

        renderDashboard();

        await screen.findByText("marshal");

        fireEvent.click(
            screen.getByRole(
                "button",
                {
                    name: "Delete User"
                }
            )
        );

        expect(
            await screen.findByText(
                "Failed to delete user account."
            )
        ).toBeInTheDocument();

        expect(
            screen.getByText("marshal")
        ).toBeInTheDocument();
    });


    it("shows ML movie search error", async () => {

        searchMlMovies.mockRejectedValue({
            response: {
                data: {
                    message:
                        "Recommendation catalog unavailable."
                }
            }
        });

        renderDashboard();

        await screen.findByText("Inception");

        fireEvent.click(
            screen.getByRole(
                "button",
                {
                    name: "Add Movie"
                }
            )
        );

        fireEvent.change(
            screen.getByLabelText(
                "Search ML movies"
            ),
            {
                target: {
                    value: "Batman"
                }
            }
        );

        fireEvent.click(
            screen.getByRole(
                "button",
                {
                    name: "Search"
                }
            )
        );

        expect(
            await screen.findByText(
                "Recommendation catalog unavailable."
            )
        ).toBeInTheDocument();

        expect(searchMlMovies)
            .toHaveBeenCalledWith(
                "Batman",
                20
            );
    });

});