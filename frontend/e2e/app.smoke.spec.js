import { test, expect } from "@playwright/test";

test.describe("Movie Recommender - E2E Smoke Tests", () => {
    test("home page should load successfully", async ({ page }) => {
        await page.goto("/");

        await expect(page).toHaveURL("http://localhost:5173/");

        await expect(
            page.getByText(/movie recommendation system/i)
        ).toBeVisible();
    });

    test("should navigate from Home to Movies", async ({ page }) => {
        await page.goto("/");

        const nav = page.getByRole(
            "navigation",
            { name: "Main navigation" }
        );

        await nav
            .getByRole("link", {
                name: "Movies",
                exact: true
            })
            .click();

        await expect(page).toHaveURL(/\/movies$/);
    });

    test("should protect the Recommendations page from logged-out users", async ({ page }) => {
        await page.goto("/recommendations");

        await expect(page).toHaveURL(/\/login$/);

        await expect(
            page.getByRole("heading", {
                name: /welcome back/i
            })
        ).toBeVisible();
    });
});
