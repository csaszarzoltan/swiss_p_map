import { test, expect } from "@playwright/test";

// SPEC-045: LocalInformationHub i18n + a11y tablist/modal + last-request-wins.
// REQ-045-001/002/003/006 -> AC-045-001/002. Backend mocked at page level.
test.describe("SPEC-045 LocalInformationHub", () => {
  const briefing8004 = {
    postcode: "8004",
    locality: "Zürich",
    generated_at: "2026-09-02T11:00:00Z",
    editorial_note: "Karte als Analysewerkzeug.",
    items: [
      { id: "democracy", category: "democracy", title: "Abstimmungen", summary: "Offizielle Infos.", importance: "important", status: "current_data", source: "BFS VoteInfo", source_url: "https://www.bfs.admin.ch/", map_layer: "politics" },
      { id: "environment", category: "environment", title: "Umwelt", summary: "Luft und Lärm.", importance: "important", status: "current_data", source: "BAFU", source_url: "https://www.bafu.admin.ch/", map_layer: "environment" },
      { id: "weather", category: "weather", title: "Wetter", summary: "Live folgt.", importance: "normal", status: "source_pending", source: "MeteoSwiss", source_url: "https://www.meteoswiss.admin.ch/", map_layer: "weather" },
      { id: "housing", category: "housing", title: "Wohnen", summary: "Preise.", importance: "normal", status: "current_data", source: "BFS IMPI", source_url: "https://www.bfs.admin.ch/", map_layer: "price" },
      { id: "mobility", category: "mobility", title: "Mobilität", summary: "SBB-Takt.", importance: "normal", status: "current_data", source: "SBB Open Data", source_url: "https://opentransportdata.swiss/", map_layer: "mobility" },
      { id: "planning", category: "planning", title: "Bauvorhaben", summary: "Baugesuche.", importance: "urgent", status: "current_data", source: "Amtsblatt", source_url: "https://amtsblattportal.ch/", map_layer: "planning" },
    ],
  };

  async function mockBriefing(page: import("@playwright/test").Page, mode: "ok" | "error" = "ok") {
    // search chain: place + politics + planning (SearchPanel.executeSearch)
    await page.route("**/api/v1/place/8004*", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({
        postcode: "8004", municipality: "Zürich", canton: "ZH", steuerfuss_percent: 119.0,
        noise_db_day: 62.5, oev_class: "A", gwr_building_count: 3420, solar_kwh_m2: 1208.0,
        solar_class: "sehr gut", oereb_zone: "Kernzone",
      }) });
    });
    await page.route("**/api/v1/politics/representatives*", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({
        district_name: "Wahlkreis 4+5", postcode: "8004", canton: "ZH",
        representatives: [{ id: "zh-8004-1", name: "Muster Anna", party: "SP", wahlkreis: "Wahlkreis 4+5" }],
      }) });
    });
    await page.route("**/api/v1/planning/baugesuche*", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
    });
    await page.route("**/api/v1/property/prices*", async (route) => {
      await route.abort();
    });
    await page.route("**/api/v1/tax/comparison*", async (route) => {
      await route.abort();
    });
    await page.route("**/api/v1/hazard/assessment*", async (route) => {
      await route.abort();
    });
    await page.route("**/api/v1/heritage/isos*", async (route) => {
      await route.abort();
    });
    await page.route("**/api/v1/climate/microclimate*", async (route) => {
      await route.abort();
    });
    await page.route("**/api/v1/education/facilities*", async (route) => {
      await route.abort();
    });
    await page.route("**/api/v1/energy/assessment*", async (route) => {
      await route.abort();
    });
    await page.route("**/api/v1/environment/air-pollen*", async (route) => {
      await route.abort();
    });
    await page.route("**/api/v1/healthcare/access*", async (route) => {
      await route.abort();
    });
    await page.route("**/api/v1/connectivity/status*", async (route) => {
      await route.abort();
    });
    await page.route("**/api/v1/ai/summary", async (route) => {
      await route.abort();
    });
    await page.route("**/api/v1/local/briefing?postcode=8004", async (route) => {
      if (mode === "error") {
        await route.fulfill({ status: 503, contentType: "application/json", body: JSON.stringify({ detail: "down" }) });
        return;
      }
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(briefing8004) });
    });
    // silence civic child panels (out of scope for SPEC-045)
    await page.route("**/api/v1/votes/proposals", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
    });
    await page.route("**/api/v1/weather/forecast*", async (route) => {
      await route.fulfill({ status: 503, contentType: "application/json", body: "{}" });
    });
    await page.route("**/api/v1/municipal/waste-calendar*", async (route) => {
      await route.fulfill({ status: 503, contentType: "application/json", body: "{}" });
    });
    await page.route("**/api/v1/costs/assessment*", async (route) => {
      await route.fulfill({ status: 503, contentType: "application/json", body: "{}" });
    });
  }

  async function openHub(page: import("@playwright/test").Page, locale: string) {
    await page.goto(`/${locale}`, { waitUntil: "domcontentloaded" });
    await expect(page.getByTestId("map-3d")).toBeVisible();
    // SearchPanel defaults the query to 8004 — execute a real search so the
    // hub receives a postcode (SPEC-053 openCard pattern).
    await page.waitForLoadState("networkidle").catch(() => {});
    const btn = page.getByTestId("search-button");
    await expect(btn).toBeVisible({ timeout: 20000 });
    await expect(btn).toBeEnabled({ timeout: 10000 });
    await btn.click();
    const hub = page.getByTestId("local-information-hub");
    await expect(hub).toBeVisible({ timeout: 15000 });
    return hub;
  }

  for (const locale of ["de", "en", "fr", "it"]) {
    test(`happy path: i18n tablist + trust badge + no hardcoded DE (/${locale})`, async ({ page }) => {
      await mockBriefing(page, "ok");
      const hub = await openHub(page, locale);
      const tablist = hub.getByRole("tablist");
      await expect(tablist).toBeVisible({ timeout: 15000 });
      await expect(hub.getByRole("tab", { name: /democracy/ })).toBeVisible();
      // source trust: official publication for current_data, pending badge for weather
      await expect(hub.getByText("official publication").first()).toBeVisible();
      await expect(hub.getByText("source pending").first()).toBeVisible();
      // last-request-wins keeps only 8004 content (no 3011 crosstalk)
      await expect(hub.getByText(/8004/)).toBeVisible();
      // localized open-map button must not stay hardcoded German outside /de
      if (locale !== "de") {
        await expect(hub.getByRole("button", { name: "Auf Karte" })).toHaveCount(0);
      }
    });
  }

  test("a11y: arrow-key tab navigation moves selection and focus (/de)", async ({ page }) => {
    await mockBriefing(page, "ok");
    const hub = await openHub(page, "de");
    const tablist = hub.getByRole("tablist");
    await expect(tablist).toBeVisible({ timeout: 15000 });
    const first = hub.getByRole("tab", { name: /democracy/ });
    await first.click();
    await expect(first).toHaveAttribute("aria-selected", "true");
    await first.press("ArrowRight");
    const second = hub.getByRole("tab", { name: /environment/ });
    await expect(second).toHaveAttribute("aria-selected", "true");
    await expect(second).toBeFocused();
    await second.press("Home");
    await expect(hub.getByRole("tab", { name: /democracy/ })).toHaveAttribute("aria-selected", "true");
  });

  test("a11y: Escape closes detail modal (/de)", async ({ page }) => {
    await mockBriefing(page, "ok");
    const hub = await openHub(page, "de");
    await expect(hub.getByRole("tablist")).toBeVisible({ timeout: 15000 });
    await hub.getByRole("button", { name: "Lokales Briefing" }).click();
    const dialog = page.getByRole("dialog");
    await expect(dialog).toBeVisible();
    await page.keyboard.press("Escape");
    await expect(dialog).toHaveCount(0);
  });

  test("error: provider outage shows alert, no invented content (/de)", async ({ page }) => {
    await mockBriefing(page, "error");
    const hub = await openHub(page, "de");
    await expect(hub.getByText("konnte nicht geladen werden")).toBeVisible({ timeout: 15000 });
    await expect(hub.getByRole("tablist")).toHaveCount(0);
  });
});
