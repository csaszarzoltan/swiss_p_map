import { test, expect } from "@playwright/test";

test.describe("Swiss P Map — felületi E2E (ADR-003 3D)", () => {
  test("hero + 3D térkép canvas látszik", async ({ page }) => {
    await page.goto("/");

    await expect(page.getByText("Svájci Államszövetség")).toBeVisible();
    await expect(page.getByText("SVÁJC").first()).toBeVisible();

    const map = page.getByTestId("map-3d");
    await expect(map).toBeVisible();

    await page.waitForTimeout(2500);
    // Three.js must have appended a canvas — proves the 3D scene initialized (no white screen)
    const canvas = map.locator("canvas");
    await expect(canvas).toBeVisible();
    const box = await canvas.boundingBox();
    expect(box?.width).toBeGreaterThan(200);
    expect(box?.height).toBeGreaterThan(200);
  });

  test("3D térkép UI: iránytű + hint + panel látszik", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByTestId("map-3d")).toBeVisible();
    await page.waitForTimeout(1500);

    // The compass, hint and glassmorphism panel are deterministic — no geometry dependency
    await expect(page.getByText("É").first()).toBeVisible();
    await expect(page.getByText(/Bal gomb: Forgatás/)).toBeVisible();
    await expect(page.getByText("Svájci Államszövetség")).toBeVisible();
    await expect(page.getByText("26 Kanton")).toBeVisible();
  });

  test("kereső: PLZ 8004 → panel jelenik meg", async ({ page }) => {
    await page.goto("/");
    await expect(page.getByTestId("map-3d")).toBeVisible();

    const input = page.getByPlaceholder("PLZ, cím vagy község");
    await expect(input).toBeVisible();
    await input.fill("8004");
    await page.getByRole("button", { name: "Keresés" }).click();

    await expect(page.getByText("Steuerfuss").first()).toBeVisible({ timeout: 10_000 });
  });
});
