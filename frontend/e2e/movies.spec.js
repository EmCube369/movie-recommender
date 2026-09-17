import { test, expect } from "@playwright/test";

const MOVIES_API = "http://localhost:8080/movies";

test.describe("Movies - Real E2E Tests", () => {

    test("should load movies from Spring Boot / MySQL", async ({ page }) => {
        const responsePromise = page.waitForResponse(
            response =>
                response.url() === MOVIES_API &&
                response.request().method() === "GET"
        );

        await page.goto("/movies");

        const response = await responsePromise;

        expect(response.status()).toBe(200);

        await expect(
            page.getByRole("heading", {
                name: "Browse Movies"
            })
        ).toBeVisible();

        await expect(
            page.getByLabel("Search movies")
        ).toBeVisible();
    });


    test("should search a movie that actually exists in the current catalog", async ({ page }) => {
        const responsePromise = page.waitForResponse(
            response =>
                response.url() === MOVIES_API &&
                response.request().method() === "GET"
        );

        await page.goto("/movies");

        const response = await responsePromise;
        expect(response.status()).toBe(200);

        const movies = await response.json();

        expect(Array.isArray(movies)).toBe(true);
        expect(movies.length).toBeGreaterThan(0);

        const targetMovie = movies[0];

        await page
            .getByLabel("Search movies")
            .fill(targetMovie.title);

        await expect(
            page.getByText(
                targetMovie.title,
                { exact: true }
            ).first()
        ).toBeVisible();
    });


    test("should open a real movie details page from the catalog", async ({ page }) => {
        const responsePromise = page.waitForResponse(
            response =>
                response.url() === MOVIES_API &&
                response.request().method() === "GET"
        );

        await page.goto("/movies");

        const response = await responsePromise;
        expect(response.status()).toBe(200);

        const movies = await response.json();

        expect(Array.isArray(movies)).toBe(true);
        expect(movies.length).toBeGreaterThan(0);

        const targetMovie = movies[0];

        await page
            .getByLabel("Search movies")
            .fill(targetMovie.title);

        const movieCard = page
            .locator("article")
            .filter({ hasText: targetMovie.title })
            .first();

        await expect(movieCard).toBeVisible();

        const movieLink = movieCard
            .locator("a")
            .first();

        await expect(movieLink).toBeVisible();

        await movieLink.click();

        await expect(page).toHaveURL(
            new RegExp(`/movies/${targetMovie.id}$`)
        );

        await expect(
            page.getByRole("heading", {
                name: targetMovie.title,
                exact: true
            })
        ).toBeVisible();
    });

});
