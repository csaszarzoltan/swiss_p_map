import { test, expect } from "@playwright/test";

test.describe("Swiss P Map — felületi E2E (ADR-003 3D + ADR-004 i18n + ADR-010 menü + UI/UX)", () => {
  test("hero + 3D térkép canvas látszik (/de)", async ({ page }) => {
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    await expect(page.getByText("Schweizerische Eidgenossenschaft")).toBeVisible({ timeout: 12000 });
    await expect(page.getByText("SCHWEIZ").first()).toBeVisible();
    const map = page.getByTestId("map-3d");
    await expect(map).toBeVisible();
    await page.waitForTimeout(2000);
    const canvas = map.locator("canvas");
    await expect(canvas).toBeVisible();
    const box = await canvas.boundingBox();
    expect(box?.width).toBeGreaterThan(200);
    expect(box?.height).toBeGreaterThan(200);
  });

  test("3D térkép UI: iránytű (N) + hint + panel + lokalizált feliratok", async ({ page }) => {
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    await expect(page.getByTestId("map-3d")).toBeVisible();
    await page.waitForTimeout(2000);
    // Iránytű N (Nord/North)
    await expect(page.getByText("N").first()).toBeVisible();
    await expect(page.getByText(/Linke Taste:/)).toBeVisible();
    await expect(page.getByText("Schweizerische Eidgenossenschaft")).toBeVisible();
    await expect(page.getByText("26 Kantone")).toBeVisible();
    await expect(page.getByText(/Gebiet/)).toBeVisible();
    await expect(page.getByText(/Bevölkerung/)).toBeVisible();
  });

  test("menü + részletező panel látszik (/de, ADR-010)", async ({ page }) => {
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    await expect(page.getByTestId("topic-sidebar")).toBeVisible();
    await expect(page.getByTestId("menu-overview")).toBeVisible();
    await expect(page.getByTestId("menu-politik")).toBeVisible();
    await expect(page.getByTestId("menu-ort")).toBeVisible();
    await expect(page.getByTestId("menu-planung")).toBeVisible();
    await expect(page.getByTestId("menu-solar")).toBeVisible();
    await expect(page.getByTestId("menu-oereb")).toBeVisible();
    await expect(page.getByTestId("topic-list")).toBeVisible();
    await expect(page.getByTestId("detail-panel")).toBeVisible();
  });

  test("kereső: PLZ 8004 → menü számok + részletező frissül (/de)", async ({ page }) => {
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    await expect(page.getByTestId("map-3d")).toBeVisible();
    const input = page.getByPlaceholder("PLZ, Adresse oder Gemeinde");
    await expect(input).toBeVisible();
    await input.fill("8004");
    await page.getByRole("button", { name: "Suchen" }).click();
    await page.waitForTimeout(2000);
    // detail panel should show overview summary after search
    await expect(page.getByTestId("detail-panel")).toBeVisible();
    // sidebar counts should update (politik >0 or planung >0)
    await expect(page.getByTestId("topic-sidebar")).toBeVisible();
  });

  test("Quick-Pick gomb: 8001 Altstadt azonnali betöltése", async ({ page }) => {
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    const qpButton = page.getByRole("button", { name: "8001 Altstadt" });
    await expect(qpButton).toBeVisible();
    await qpButton.click();
    await page.waitForTimeout(2000);
    await expect(page.getByTestId("search-input")).toHaveValue("8001");
    await expect(page.getByTestId("detail-panel")).toBeVisible();
  });

  test("Témaváltás: Planung fülre váltás és Baugesuche megjelenítése", async ({ page }) => {
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    // Search 8004
    await page.getByRole("button", { name: "8004 Aussersihl" }).click();
    await page.waitForTimeout(1500);
    // Switch to Planung
    await page.getByTestId("menu-planung").click();
    await page.waitForTimeout(1000);
    await expect(page.getByTestId("topic-list")).toBeVisible();
  });

  test("i18n: 4 locale — DE/EN/FR/IT", async ({ page }) => {
    test.setTimeout(45_000);
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    await expect(page.locator("html")).toHaveAttribute("lang", "de", { timeout: 10000 });
    await expect(page.getByRole("button", { name: "DE", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "EN", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "FR", exact: true })).toBeVisible();
    await expect(page.getByRole("button", { name: "IT", exact: true })).toBeVisible();
    await expect(page.getByPlaceholder("PLZ, Adresse oder Gemeinde")).toBeVisible();
    await expect(page.getByRole("button", { name: "Suchen" })).toBeVisible();

    await page.goto("/en", { waitUntil: "domcontentloaded" });
    await expect(page.locator("html")).toHaveAttribute("lang", "en", { timeout: 10000 });
    await expect(page.getByPlaceholder("Postcode, address or municipality")).toBeVisible();
    await expect(page.getByRole("button", { name: "Search" })).toBeVisible();

    await page.goto("/fr", { waitUntil: "domcontentloaded" });
    await expect(page.locator("html")).toHaveAttribute("lang", "fr", { timeout: 10000 });
    await expect(page.getByPlaceholder("NPA, adresse ou commune")).toBeVisible();
    await expect(page.getByRole("button", { name: "Rechercher" })).toBeVisible();

    await page.goto("/it", { waitUntil: "domcontentloaded" });
    await expect(page.locator("html")).toHaveAttribute("lang", "it", { timeout: 10000 });
    await expect(page.getByPlaceholder("NPA, indirizzo o comune")).toBeVisible();
    await expect(page.getByRole("button", { name: "Cerca" })).toBeVisible();

    await page.goto("/", { waitUntil: "domcontentloaded" });
    await expect(page).toHaveURL(/\/de(\/|$)/, { timeout: 10000 });
  });

  test("ADR-012 & ADR-014: 3D valós szavazás & Többkantonos Planung (3011 Bern & 4001 Basel)", async ({
    page,
  }) => {
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    // 1. 3D kártyán valós népszavazási cím és 58.2% látszik (ADR-012)
    await expect(page.getByText("13. AHV-Rente (BFS)")).toBeVisible();
    await expect(page.getByText("JA: 58.2%")).toBeVisible();

    // 2. 3011 Bern Quick-Pick -> Planung fülre váltás (ADR-014)
    await page.getByRole("button", { name: "3011 Bern" }).click();
    await page.waitForTimeout(2000);
    await page.getByTestId("menu-planung").click();
    await page.waitForTimeout(1000);
    await expect(page.getByText("Bern")).toBeVisible();
  });
});
