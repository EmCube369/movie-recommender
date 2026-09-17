import { render, screen } from "@testing-library/react";
import {
    MemoryRouter,
    Route,
    Routes
} from "react-router-dom";

import { beforeEach, describe, expect, it, vi } from "vitest";

import AdminRoute from "../components/AdminRoute";
import { useAuth } from "../context/AuthContext";


vi.mock("../context/AuthContext", () => ({
    useAuth: vi.fn()
}));


function renderAdminRoute() {

    return render(
        <MemoryRouter initialEntries={["/admin"]}>
            <Routes>

                <Route element={<AdminRoute />}>
                    <Route
                        path="/admin"
                        element={
                            <div>
                                Admin Page
                            </div>
                        }
                    />
                </Route>

                <Route
                    path="/login"
                    element={
                        <div>
                            Login Page
                        </div>
                    }
                />

                <Route
                    path="/"
                    element={
                        <div>
                            Home Page
                        </div>
                    }
                />

            </Routes>
        </MemoryRouter>
    );
}


describe("AdminRoute", () => {

    beforeEach(() => {
        vi.clearAllMocks();
    });


    it("shows loading state while authentication is loading", () => {

        useAuth.mockReturnValue({
            user: null,
            isAuthenticated: false,
            authLoading: true
        });

        renderAdminRoute();

        expect(
            screen.getByText("Checking admin access...")
        ).toBeInTheDocument();
    });


    it("redirects unauthenticated users to login", () => {

        useAuth.mockReturnValue({
            user: null,
            isAuthenticated: false,
            authLoading: false
        });

        renderAdminRoute();

        expect(
            screen.getByText("Login Page")
        ).toBeInTheDocument();

        expect(
            screen.queryByText("Admin Page")
        ).not.toBeInTheDocument();
    });


    it("redirects authenticated USER to home", () => {

        useAuth.mockReturnValue({
            user: {
                username: "marshal",
                role: "USER"
            },
            isAuthenticated: true,
            authLoading: false
        });

        renderAdminRoute();

        expect(
            screen.getByText("Home Page")
        ).toBeInTheDocument();

        expect(
            screen.queryByText("Admin Page")
        ).not.toBeInTheDocument();
    });


    it("allows authenticated ADMIN to access admin route", () => {

        useAuth.mockReturnValue({
            user: {
                username: "admin",
                role: "ADMIN"
            },
            isAuthenticated: true,
            authLoading: false
        });

        renderAdminRoute();

        expect(
            screen.getByText("Admin Page")
        ).toBeInTheDocument();
    });

});