import { test, expect } from "@playwright/test";

// SPEC-054: CostOfLivingCalculator full breakdown (mocked backend at page level).
test.describe("SPEC-054 CostOfLivingCalculator", () => {
  const assessment = {
    postcode: "8004",
    income_chf: 120000,
    size_m2: 100,
    housing_chf: 3250,
    tax_chf: 1400,
    health_insurance_chf: 420,
    commute_chf: 180,
    total_monthly_chf: 5250,
    remaining_monthly_chf: 4750,
    trust_state: "modeled_estimate",
    disclaimer: "Indicative estimate based on modelled reference values, not financial or tax advice.",
    source: "BFS reference rents / cantonal tax tables (modeled composite)",
    fetched_at: "2026-09-22T12:50:00Z",
  };

  async function mockCosts(page: import("@playwright/test").Page, mode: "ok" | "error" = "ok") {
    await page.route("**/api/v1/costs/assessment*", async (route) => {
      if (mode === "error") {
        await route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ detail: "down" }) });
        return;
      }
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(assessment) });
    });
  }

  async function openCard(page: import("@playwright/test").Page, locale: string) {
    await page.goto(`/${locale}`, { waitUntil: "domcontentloaded" });
    await expect(page.getByTestId("map-3d")).toBeVisible();
    await page.getByTestId("search-button").click();
    const card = page.getByTestId("cost-of-living-calculator");
    await expect(card).toBeVisible({ timeout: 15000 });
    return card;
  }

  for (const locale of ["de", "en", "fr", "it"]) {
    test(`happy path: breakdown rows + total + trust badge + disclaimer (/${locale})`, async ({ page }) => {
      await mockCosts(page, "ok");
      const card = await openCard(page, locale);
      await expect(card.getByText(/5.250/, { exact: false })).toBeVisible({ timeout: 15000 });
      await expect(card.getByText(/3.250/, { exact: false })).toBeVisible();
      await expect(card.getByText(/1.400/, { exact: false })).toBeVisible();
      await expect(card.getByText("modeled estimate", { exact: false })).toBeVisible();
      await expect(card.getByText(/estimate|Schätzung|estimation|stima/i).last()).toBeVisible();
      await expect(card.getByText("official measurement", { exact: false })).toHaveCount(0);
    });
  }

  test("error: provider outage shows alert, no fake freshness (/de)", async ({ page }) => {
    await mockCosts(page, "error");
    const card = await openCard(page, "de");
    await expect(card.getByText("konnten nicht berechnet werden")).toBeVisible({ timeout: 15000 });
    await expect(card.getByText("official measurement", { exact: false })).toHaveCount(0);
  });
});
