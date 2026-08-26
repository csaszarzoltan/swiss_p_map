import { test, expect } from "@playwright/test";

test.describe("Swiss P Map — felületi E2E (ADR-003 3D + ADR-004 i18n)", () => {
  test("hero + 3D térkép canvas látszik (/de)", async ({ page }) => {
    await page.goto("/de", { waitUntil: "networkidle" });
    await expect(page.getByText("Schweizerische Eidgenossenschaft")).toBeVisible({ timeout: 12000 });
    await expect(page.getByText("SCHWEIZ").first()).toBeVisible();
    const map = page.getByTestId("map-3d");
    await expect(map).toBeVisible();
    await page.waitForTimeout(2500);
    const canvas = map.locator("canvas");
    await expect(canvas).toBeVisible();
    const box = await canvas.boundingBox();
    expect(box?.width).toBeGreaterThan(200);
    expect(box?.height).toBeGreaterThan(200);
  });

  test("3D térkép UI: iránytű + hint + panel látszik", async ({ page }) => {
    await page.goto("/de", { waitUntil: "networkidle" });
    await expect(page.getByTestId("map-3d")).toBeVisible();
    await page.waitForTimeout(3500);
    await expect(page.getByText("É").first()).toBeVisible();
    await expect(page.getByText(/Linke Taste:/)).toBeVisible();
    await expect(page.getByText("Schweizerische Eidgenossenschaft")).toBeVisible();
    await expect(page.getByText("26 Kantone")).toBeVisible();
  });

  test("kereső: PLZ 8004 → panel jelenik meg (/de, Steuerfuss/Wahlkreis)", async ({ page }) => {
    await page.goto("/de", { waitUntil: "networkidle" });
    await expect(page.getByTestId("map-3d")).toBeVisible();
    const input = page.getByPlaceholder("PLZ, Adresse oder Gemeinde");
    await expect(input).toBeVisible();
    await input.fill("8004");
    await page.getByRole("button", { name: "Suchen" }).click();
    await expect(page.getByText("STEUERFUSS").first()).toBeVisible({ timeout: 10_000 });
  });

  test("i18n: 4 locale — DE/EN/FR/IT", async ({ page }) => {
    test.setTimeout(45_000);
    // /de — DE button is immediate, Map3D title needs lazy init
    await page.goto("/de", { waitUntil: "commit" });
    await expect(page.locator("html")).toHaveAttribute("lang", "de", { timeout: 10000 });
    await expect(page.getByRole("button", { name: "DE", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "EN", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "FR", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "IT", exact: true })).toBeVisible();
    await expect(page.getByText("Schweizerische Eidgenossenschaft")).toBeVisible({ timeout: 15000 });

    // /en — SearchPanel + Map3D title (both need provider, wait for Map3D)
    await page.goto("/en", { waitUntil: "commit" });
    await expect(page.locator("html")).toHaveAttribute("lang", "en", { timeout: 10000 });
    await expect(page.getByText("Swiss Confederation")).toBeVisible({ timeout: 15000 });
    await expect(page.getByPlaceholder("Postcode, address or municipality")).toBeVisible();

    // /fr
    await page.goto("/fr", { waitUntil: "commit" });
    await expect(page.locator("html")).toHaveAttribute("lang", "fr", { timeout: 10000 });
    await expect(page.getByText("Confédération suisse")).toBeVisible({ timeout: 15000 });
    await expect(page.getByPlaceholder("NPA, adresse ou commune")).toBeVisible();

    // /it
    await page.goto("/it", { waitUntil: "commit" });
    await expect(page.locator("html")).toHaveAttribute("lang", "it", { timeout: 10000 });
    await expect(page.getByText("Confederazione Svizzera")).toBeVisible({ timeout: 15000 });
    await expect(page.getByPlaceholder("NPA, indirizzo o comune")).toBeVisible();

    // / redirects to /de
    await page.goto("/", { waitUntil: "commit" });
    await expect(page).toHaveURL(/\/de(\/|$)/, { timeout: 10000 });
  });
});
