import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import Home from "../pages/Home";

function renderHome() {
    return render(
        <MemoryRouter>
            <Home />
        </MemoryRouter>
    );
}

describe("Home Page", () => {

    it("renders the redesigned hero heading", () => {
        renderHome();

        expect(
            screen.getByRole("heading", {
                level: 1,
                name: /find movies you'll enjoy watching/i,
            })
        ).toBeInTheDocument();
    });

    it("renders the home page description", () => {
        renderHome();

        expect(
            screen.getByText(
                /browse movies, explore their details, and discover personalized recommendations/i
            )
        ).toBeInTheDocument();
    });

    it("renders the main hero actions", () => {
        renderHome();

        expect(
            screen.getByRole("link", {
                name: "Browse Movies",
            })
        ).toHaveAttribute("href", "/movies");

        expect(
            screen.getByRole("link", {
                name: "Learn More",
            })
        ).toHaveAttribute("href", "#features");
    });

    it("renders the feature section", () => {
        renderHome();

        expect(
            screen.getByRole("heading", {
                level: 2,
                name: "What you can do",
            })
        ).toBeInTheDocument();

        expect(
            screen.getByRole("heading", {
                level: 3,
                name: "Browse Movies",
            })
        ).toBeInTheDocument();

        expect(
            screen.getByRole("heading", {
                level: 3,
                name: "View Movie Details",
            })
        ).toBeInTheDocument();

        expect(
            screen.getByRole("heading", {
                level: 3,
                name: "Personalized Recommendations",
            })
        ).toBeInTheDocument();
    });

});
