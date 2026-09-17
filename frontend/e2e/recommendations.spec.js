import { test, expect } from "@playwright/test";

const API_URL = "http://localhost:8080";

function uniqueUsername(prefix) {
    return `${prefix}${Date.now()}${Math.floor(Math.random() * 10000)}`;
}

async function registerAndLogin(context, prefix) {
    const username = uniqueUsername(prefix);
    const password = "Playwright123!";

    const registerResponse = await context.request.post(
        `${API_URL}/api/auth/register`,
        {
            data: {
                username,
                password
            }
        }
    );

    expect(registerResponse.status()).toBe(201);

    const loginResponse = await context.request.post(
        `${API_URL}/api/auth/login`,
        {
            data: {
                username,
                password
            }
        }
    );

    expect(loginResponse.status()).toBe(200);

    return username;
}

async function getSupportedCatalogMovie(context) {
    const response = await context.request.get(
        `${API_URL}/movies`
    );

    expect(response.status()).toBe(200);

    const movies = await response.json();

    expect(Array.isArray(movies)).toBe(true);

    const supportedMovie = movies.find(
        movie => movie.mlMovieId != null
    );

    expect(
        supportedMovie,
        "The catalog needs at least one ML-supported movie for this E2E test."
    ).toBeTruthy();

    return supportedMovie;
}


test.describe("Recommendations - Personalized E2E Tests", () => {

    test("should generate real personalized recommendations for a logged-in user", async ({ page, context }) => {
        test.slow();

        await registerAndLogin(
            context,
            "e2erec"
        );

        const movie =
            await getSupportedCatalogMovie(context);

        const ratingResponse =
            await context.request.put(
                `${API_URL}/api/user-movies/${movie.id}/rating`,
                {
                    data: {
                        rating: 5
                    }
                }
            );

        expect(ratingResponse.status()).toBe(200);

        /*
         * This request uses the same session cookie as the browser.
         * Spring Boot reads the logged-in user's saved rating and
         * calls the real Python personalized recommendation endpoint.
         */
        const recommendationResponse =
            await context.request.get(
                `${API_URL}/api/recommendations/me?limit=3`
            );

        expect(
            recommendationResponse.status()
        ).toBe(200);

        const body =
            await recommendationResponse.json();

        expect(
            Array.isArray(body.recommendations)
        ).toBe(true);

        expect(
            body.recommendations.length
        ).toBeGreaterThan(0);

        expect(body.count).toBe(
            body.recommendations.length
        );

        await page.goto("/recommendations");

        await expect(page).toHaveURL(
            /\/recommendations$/
        );

        await expect(
            page.getByRole("heading", {
                name: "Recommendations",
                exact: true
            })
        ).toBeVisible();

        /*
         * Phase 7 recommendations belong to the authenticated user.
         * The old MovieLens User ID input should no longer be present.
         */
        await expect(
            page.getByLabel("User ID")
        ).toHaveCount(0);
    });


    test("should return a controlled error when a logged-in user has no ratings", async ({ page, context }) => {
        await registerAndLogin(
            context,
            "e2eempty"
        );

        const response =
            await context.request.get(
                `${API_URL}/api/recommendations/me?limit=5`
            );

        expect(response.status()).toBe(400);

        const responseText =
            await response.text();

        expect(responseText).toMatch(
            /rate at least one ml-supported movie/i
        );

        /*
         * The user is authenticated, so the frontend route itself
         * must remain accessible instead of redirecting to /login.
         */
        await page.goto("/recommendations");

        await expect(page).toHaveURL(
            /\/recommendations$/
        );

        await expect(
            page.getByRole("heading", {
                name: "Recommendations",
                exact: true
            })
        ).toBeVisible();
    });

});
