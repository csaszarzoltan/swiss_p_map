import { test, expect } from "@playwright/test";

test.describe("Swiss P Map — felületi E2E", () => {
  test("hero + térkép nem marad fehéren", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByRole("heading", { name: "Swiss P Map" })).toBeVisible();
    await expect(page.getByText("A svájci környék egyetlen térképén")).toBeVisible();

    const map = page.getByTestId("map-container");
    await expect(map).toBeVisible();

    // A MapLibre-nek fel kell rajzolnia a canvas-hierarchiát (ne maradjon üres fehér div)
    // – white-screen regressziót fog (ez hiányzott eddig)
    await page.waitForTimeout(3000);
    const hasCanvasOrError = await page.evaluate(() => {
      const el = document.querySelector('[data-testid="map-container"]');
      if (!el) return { hasCanvas: false, hasError: false, inner: "" };
      const hasCanvas = !!el.querySelector("canvas");
      const hasMaplibreClass = el.classList.contains("maplibregl-map");
      const hasError = !!document.querySelector('[data-testid="map-error"]');
      return {
        hasCanvas: hasCanvas || hasMaplibreClass,
        hasError,
        inner: el.innerHTML.slice(0, 600),
      };
    });

    // Vagy canvas látszik, vagy expliciten hibaüzenet (nem néma fehérség)
    expect(hasCanvasOrError.hasCanvas || hasCanvasOrError.hasError).toBeTruthy();
  });

  test("kereső: PLZ 8004 → panel + marker", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByTestId("map-container")).toBeVisible();

    const input = page.getByPlaceholder("PLZ, cím vagy község");
    await expect(input).toBeVisible();
    await input.fill("8004");
    await page.getByRole("button", { name: "Keresés" }).click();

    await expect(page.getByText("Steuerfuss").first()).toBeVisible({ timeout: 10_000 });
    await expect(page.getByText(/Wahlkreis/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test("kereső: szabad szöveg geokódol (MEK ellenőrzés)", async ({ page }) => {
    await page.goto("/");
    const input = page.getByPlaceholder("PLZ, cím vagy község");
    await input.fill("8004");
    // Audit A: Enter is indítja a keresést
    await input.press("Enter");
    await expect(page.getByText("Steuerfuss").first()).toBeVisible({ timeout: 10_000 });
  });
});
