import { test, expect } from "@playwright/test";

// SPEC-052: WeatherVisualWidget live states (mocked backend at page level).
test.describe("SPEC-052 WeatherVisualWidget", () => {
  const forecast = {
    postcode: "8004",
    current_temp_c: 17.8,
    current_condition: "partly_cloudy",
    observed_at: "2026-09-22T12:45",
    days: [
      { date: "2026-09-22", temp_min_c: 9.2, temp_max_c: 20.7, precip_prob_pct: 0, condition: "partly_cloudy" },
      { date: "2026-09-23", temp_min_c: 9.1, temp_max_c: 22.2, precip_prob_pct: 3, condition: "mostly_clear" },
      { date: "2026-09-24", temp_min_c: 12.0, temp_max_c: 20.4, precip_prob_pct: 8, condition: "overcast" },
      { date: "2026-09-25", temp_min_c: 6.6, temp_max_c: 20.2, precip_prob_pct: 0, condition: "mostly_clear" },
      { date: "2026-09-26", temp_min_c: 7.6, temp_max_c: 24.8, precip_prob_pct: 0, condition: "clear" },
      { date: "2026-09-27", temp_min_c: 11.0, temp_max_c: 26.0, precip_prob_pct: 4, condition: "mostly_clear" },
      { date: "2026-09-28", temp_min_c: 12.3, temp_max_c: 23.4, precip_prob_pct: 10, condition: "rain" },
    ],
    source: "Open-Meteo / MeteoSwiss ICON",
    trust_state: "modeled_estimate",
    fetched_at: "2026-09-22T12:50:00Z",
    cache_ttl_seconds: 900,
  };
  const alertsPending = {
    status: "source_pending", items: [],
    source: "MeteoSwiss Naturgefahren",
    official_url: "https://www.meteoschweiz.admin.ch/warnungen",
    fetched_at: "2026-09-22T12:50:00Z", note: "pending",
  };

  async function mockWeather(page: import("@playwright/test").Page, mode: "ok" | "empty" | "error" = "ok") {
    await page.route("**/api/v1/weather/forecast*", async (route) => {
      if (mode === "error") { await route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ detail: { trust_state: "source_pending" } }) }); return; }
      const body = mode === "empty" ? { ...forecast, days: [] } : forecast;
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
    });
    await page.route("**/api/v1/weather/alerts*", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(alertsPending) });
    });
  }

  for (const locale of ["de", "en", "fr", "it"]) {
    test(`happy path: 7-day trend + trust badge + alerts pending (/${locale})`, async ({ page }) => {
      await mockWeather(page, "ok");
      await page.goto(`/${locale}`, { waitUntil: "domcontentloaded" });
      const w = page.getByTestId("weather-visual-widget");
      await expect(w).toBeVisible({ timeout: 15000 });
      await expect(w.getByRole("list", { name: /.+/ })).toBeVisible({ timeout: 15000 });
      await expect(w.getByRole("listitem")).toHaveCount(7, { timeout: 15000 });
      await expect(w.getByText("modeled estimate", { exact: false })).toBeVisible();
      await expect(w.getByRole("link", { name: /.+/ }).first()).toHaveAttribute("href", /https:\/\//);
    });
  }

  test("empty: no days shows empty state (/de)", async ({ page }) => {
    await mockWeather(page, "empty");
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    await expect(page.getByTestId("weather-visual-widget")).toContainText("Keine Wetterdaten", { timeout: 15000 });
  });

  test("error: provider outage shows source_pending, no fake official data (/de)", async ({ page }) => {
    await mockWeather(page, "error");
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    const w = page.getByTestId("weather-visual-widget");
    await expect(w).toContainText("konnten nicht geladen", { timeout: 15000 });
    await expect(w.getByText("source pending", { exact: false })).toBeVisible();
    await expect(w.getByText("official measurement", { exact: false })).toHaveCount(0);
  });
});
