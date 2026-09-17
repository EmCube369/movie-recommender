import {
    render,
    screen
} from "@testing-library/react";

import {
    MemoryRouter,
    Route,
    Routes
} from "react-router-dom";

import {
    beforeEach,
    describe,
    expect,
    it,
    vi
} from "vitest";

import ProtectedRoute from "../components/ProtectedRoute";
import { useAuth } from "../context/AuthContext";


vi.mock("../context/AuthContext", () => ({
    useAuth: vi.fn()
}));


function renderProtectedRoute() {
    return render(
        <MemoryRouter initialEntries={["/profile"]}>
            <Routes>

                <Route element={<ProtectedRoute />}>

                    <Route
                        path="/profile"
                        element={
                            <div>
                                Profile Page
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

            </Routes>
        </MemoryRouter>
    );
}


describe("ProtectedRoute", () => {

    beforeEach(() => {
        vi.clearAllMocks();
    });


    it("allows authenticated users to access protected routes", () => {

        useAuth.mockReturnValue({
            isAuthenticated: true,
            authLoading: false
        });

        renderProtectedRoute();

        expect(
            screen.getByText("Profile Page")
        ).toBeInTheDocument();

        expect(
            screen.queryByText("Login Page")
        ).not.toBeInTheDocument();
    });


    it("redirects unauthenticated users to login", () => {

        useAuth.mockReturnValue({
            isAuthenticated: false,
            authLoading: false
        });

        renderProtectedRoute();

        expect(
            screen.getByText("Login Page")
        ).toBeInTheDocument();

        expect(
            screen.queryByText("Profile Page")
        ).not.toBeInTheDocument();
    });

});