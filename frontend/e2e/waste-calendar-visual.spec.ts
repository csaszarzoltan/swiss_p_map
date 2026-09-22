import { test, expect } from "@playwright/test";

// SPEC-053: WasteCalendarVisual live backend data + real .ics export.
// Fully hermetic: all backend endpoints mocked at page level (pattern shared
// with SPEC-051/SPEC-052), so no backend port dependency.
test.describe("SPEC-053 WasteCalendarVisual", () => {
  const place = {
    postcode: "8004", municipality: "Zürich", canton: "ZH",
    steuerfuss_percent: 119.0, noise_db_day: 62.5, oev_class: "A",
    gwr_building_count: 3420, solar_kwh_m2: 1208.0, solar_class: "sehr gut",
    oereb_zone: "Kernzone",
  };
  const politics = {
    district_name: "Wahlkreis 4+5", postcode: "8004", canton: "ZH",
    representatives: [{ id: "zh-8004-1", name: "Muster Anna", party: "SP", wahlkreis: "Wahlkreis 4+5" }],
  };
  const briefing = {
    postcode: "8004", locality: "Zürich", generated_at: "2026-09-22T07:00:00Z",
    items: [{ id: "demo", category: "environment", title: "Demo", summary: "Demo summary", importance: "normal", status: "current_data", source: "Demo", source_url: "https://example.com", map_layer: null }],
    editorial_note: "Demo note",
  };
  const waste = {
    postcode: "8004",
    events: [
      { waste_type: "Kehricht", collection_date: "2026-09-24", days_until: 2 },
      { waste_type: "Bio", collection_date: "2026-09-26", days_until: 4 },
      { waste_type: "Papier", collection_date: "2026-09-28", days_until: 6 },
      { waste_type: "Karton", collection_date: "2026-10-05", days_until: 13 },
    ],
    source: "Municipal waste calendar",
    source_url: "https://www.zh.ch/de/umwelt-tiere/abfall.html",
    fetched_at: "2026-09-22T07:00:00Z",
    trust_state: "official_publication",
  };
  const ics = "BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//swiss-p-map//waste-calendar//EN\r\nBEGIN:VEVENT\r\nUID:8004-Kehricht-20260924@swiss-p-map\r\nDTSTART;VALUE=DATE:20260924\r\nSUMMARY:Kehricht (8004)\r\nEND:VEVENT\r\nEND:VCALENDAR\r\n";

  async function mockAll(page: import("@playwright/test").Page, mode: "ok" | "empty" | "error" = "ok") {
    await page.route("**/api/v1/place/**", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(place) });
    });
    await page.route("**/api/v1/politics/representatives*", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(politics) });
    });
    await page.route("**/api/v1/planning/baugesuche*", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
    });
    await page.route("**/api/v1/local/briefing*", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(briefing) });
    });
    await page.route("**/api/v1/votes/proposals", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
    });
    await page.route("**/api/v1/weather/forecast*", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ postcode: "8004", days: [] }) });
    });
    await page.route("**/api/v1/weather/alerts*", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "source_pending", items: [] }) });
    });
    await page.route("**/api/v1/municipal/waste-calendar?*", async (route) => {
      if (mode === "error") { await route.fulfill({ status: 500, contentType: "application/json", body: "{}" }); return; }
      const body = mode === "empty" ? { ...waste, events: [] } : waste;
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(body) });
    });
    await page.route("**/api/v1/municipal/waste-calendar.ics?*", async (route) => {
      await route.fulfill({ status: 200, contentType: "text/calendar", body: ics });
    });
  }

  async function openCard(page: import("@playwright/test").Page) {
    await page.waitForLoadState("networkidle").catch(() => {});
    const btn = page.getByTestId("search-button");
    await expect(btn).toBeVisible({ timeout: 20000 });
    await expect(btn).toBeEnabled({ timeout: 10000 });
    await btn.click();
    const card = page.getByTestId("waste-calendar-visual");
    await expect(card).toBeVisible({ timeout: 20000 });
    return card;
  }

  test("happy path: relative countdowns + trust badge + real .ics link (/de)", async ({ page }) => {
    await mockAll(page, "ok");
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    const card = await openCard(page);
    await expect(card.getByRole("listitem")).toHaveCount(4, { timeout: 10000 });
    await expect(card.getByText("Kehricht")).toBeVisible();
    await expect(card.getByText(/in 2 Tagen/)).toBeVisible();
    await expect(card.getByText("official publication")).toBeVisible();
    const link = card.getByRole("link", { name: /.ics exportieren/ });
    await expect(link).toHaveAttribute("href", /waste-calendar\.ics\?postcode=8004/);
  });

  for (const locale of ["en", "fr", "it"]) {
    test(`happy path countdown localized (/${locale})`, async ({ page }) => {
      await mockAll(page, "ok");
      await page.goto(`/${locale}`, { waitUntil: "domcontentloaded" });
      const card = await openCard(page);
      await expect(card.getByRole("listitem")).toHaveCount(4, { timeout: 10000 });
      await expect(card.getByRole("link", { name: /.+/ })).toHaveAttribute("href", /waste-calendar\.ics/);
    });
  }

  test("empty: no events shows empty state (/de)", async ({ page }) => {
    await mockAll(page, "empty");
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    const card = await openCard(page);
    await expect(card).toContainText("Keine Abfuhrtermine", { timeout: 10000 });
  });

  test("error: backend 500 shows alert, no stale mock dates (/de)", async ({ page }) => {
    await mockAll(page, "error");
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    const card = await openCard(page);
    await expect(card).toContainText("konnte nicht geladen werden", { timeout: 10000 });
    await expect(card.getByText("Papier · in 6 Tagen")).toHaveCount(0);
  });
});
