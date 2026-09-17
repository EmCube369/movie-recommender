import {
    render,
    screen
} from "@testing-library/react";

import {
    MemoryRouter
} from "react-router-dom";

import {
    beforeEach,
    describe,
    expect,
    it,
    vi
} from "vitest";

import Navbar from "../components/Navbar";
import { useAuth } from "../context/AuthContext";


vi.mock("../context/AuthContext", () => ({
    useAuth: vi.fn()
}));


function renderNavbar() {
    return render(
        <MemoryRouter>
            <Navbar />
        </MemoryRouter>
    );
}


describe("Navbar", () => {

    beforeEach(() => {
        vi.clearAllMocks();
    });


    it("shows the Profile link when the user is logged in", () => {

        useAuth.mockReturnValue({
            user: {
                username: "testuser",
                role: "USER"
            },
            isAuthenticated: true,
            logout: vi.fn()
        });

        renderNavbar();

        expect(
            screen.getByRole("link", {
                name: "Profile"
            })
        ).toHaveAttribute(
            "href",
            "/profile"
        );

        expect(
            screen.getByText("testuser")
        ).toBeInTheDocument();
    });


    it("does not show the Profile link when the user is logged out", () => {

        useAuth.mockReturnValue({
            user: null,
            isAuthenticated: false,
            logout: vi.fn()
        });

        renderNavbar();

        expect(
            screen.queryByRole("link", {
                name: "Profile"
            })
        ).not.toBeInTheDocument();

        expect(
            screen.getByRole("link", {
                name: "Login"
            })
        ).toBeInTheDocument();

        expect(
            screen.getByRole("link", {
                name: "Register"
            })
        ).toBeInTheDocument();
    });

    it("shows the Admin link when the logged-in user is an ADMIN", () => {

        useAuth.mockReturnValue({
            user: {
                username: "admin",
                role: "ADMIN"
            },
            isAuthenticated: true,
            logout: vi.fn()
        });

        render(
            <MemoryRouter>
                <Navbar />
            </MemoryRouter>
        );

        expect(
            screen.getByRole("link", {
                name: "Admin"
            })
        ).toBeInTheDocument();
    });


    it("does not show the Admin link when the logged-in user is a USER", () => {

        useAuth.mockReturnValue({
            user: {
                username: "marshal",
                role: "USER"
            },
            isAuthenticated: true,
            logout: vi.fn()
        });

        render(
            <MemoryRouter>
                <Navbar />
            </MemoryRouter>
        );

        expect(
            screen.queryByRole("link", {
                name: "Admin"
            })
        ).not.toBeInTheDocument();
    });

});