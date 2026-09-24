import { test, expect, type Page } from "@playwright/test";

// ADR-023/B: watch-zone notification UI + Einsprachefrist countdown, live in the
// browser through LocalInformationHub.
// REQ-A1 (consent gate) / REQ-A3 (source+trust on every event) /
// REQ-B1/B2 (countdown, expired never open, due_soon <= 3 days) / REQ-B3
// (disclaimer next to the deadline) / SPEC-060 REQ-060-003 (loading/empty/error).
// Backend is mocked at page level so the run is hermetic.
test.describe("ADR-023/B WatchEventsCard", () => {
  const STAMP = "2026-09-24T09:00:00+00:00";
  // localized REQ-B3 warning text, read from the shipped messages (the UI must
  // never leak the raw backend German string into en/fr/it)
  const msg_disclaimer: Record<string, string> = {
    de: "Keine Rechtsberatung",
    en: "Not legal advice",
    fr: "Pas un avis juridique",
    it: "Non è consulenza legale",
  };
  const briefing = {
    postcode: "8004",
    locality: "Zürich",
    generated_at: STAMP,
    editorial_note: "Karte als Analysewerkzeug.",
    items: [
      { id: "planning", category: "planning", title: "Bauvorhaben", summary: "Baugesuche.", importance: "urgent", status: "current_data", source: "Amtsblatt", source_url: "https://amtsblattportal.ch/", map_layer: "planning" },
    ],
  };
  const deadlines = {
    count: 2,
    status: "success",
    rule: "deadline = publication_date + 20 Tage (Standardfrist, ADR-023)",
    disclaimer: "Keine Rechtsberatung; ersetzt weder anwaltliche Beratung noch Vertretung.",
    source: "Kantonale E-Amtsblätter",
    trust_state: "official_publication",
    fetched_at: STAMP,
    zone_id: null,
    postcode: "8004",
    items: [
      { baugesuch_id: "zh-8004-77", zone_id: "", postcode: "8004", municipality: "Zürich", title: "Neubau Mehrfamilienhaus", publication_date: "2026-09-10", deadline: "2026-09-30", days_left: 6, state: "open", source_url: "https://amtsblattportal.ch/de/publications/77", source: "Kantonale E-Amtsblätter", trust_state: "official_publication", disclaimer: "Keine Rechtsberatung; ersetzt weder anwaltliche Beratung noch Vertretung.", rule: "deadline = publication_date + 20 Tage (Standardfrist, ADR-023)" },
      { baugesuch_id: "zh-8004-88", zone_id: "", postcode: "8004", municipality: "Zürich", title: "Abbruch Garage", publication_date: "2026-08-28", deadline: "2026-09-17", days_left: -7, state: "expired", source_url: "https://amtsblattportal.ch/de/publications/88", source: "Kantonale E-Amtsblätter", trust_state: "official_publication", disclaimer: "Keine Rechtsberatung.", rule: "deadline = publication_date + 20 Tage (Standardfrist, ADR-023)" },
    ],
  };
  const events = {
    count: 1,
    status: "success",
    source: "Kantonale E-Amtsblätter",
    trust_state: "official_publication",
    fetched_at: STAMP,
    items: [
      { event_id: "zone-8004:zh-8004-77:new_permit", zone_id: "zone-8004", baugesuch_id: "zh-8004-77", kind: "new_permit", distance_m: 412.7, title: "Neubau Mehrfamilienhaus", postcode: "8004", canton: "ZH", publication_date: "2026-09-10", deadline: "2026-09-30", days_left: 6, state: "open", source_url: "https://amtsblattportal.ch/de/publications/77", source: "Kantonale E-Amtsblätter", trust_state: "official_publication", fetched_at: STAMP, delivery: [{ channel: "email", status: "queued_pending_opt_in", detail: "confirmation_pending" }] },
    ],
  };

  async function mockAll(page: Page, mode: "ok" | "empty" | "error" = "ok") {
    // ADR-022 restore chain (must succeed so the hub gets a postcode).
    await page.route("**/api/v1/place/**", (r) => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ postcode: "8004", municipality: "Zürich", canton: "ZH", steuerfuss_percent: 119.0, noise_db_day: 62.5, oev_class: "A", gwr_building_count: 3420, solar_kwh_m2: 1208.0, solar_class: "sehr gut", oereb_zone: "Kernzone", risk_level: null, risk_reason: null }) }));
    await page.route("**/api/v1/politics/representatives*", (r) => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ district_name: "Wahlkreis 4+5", postcode: "8004", canton: "ZH", representatives: [] }) }));
    await page.route("**/api/v1/planning/baugesuche*", (r) => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) }));
    await page.route("**/api/v1/local/briefing*", (r) => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(briefing) }));
    // Sibling widget + page-level endpoints that share this page: mock with
    // endpoint-appropriate shapes (never a generic blob — DetailPanel maps
    // over hazards/segments and would crash the whole page tree).
    await page.route("**/api/v1/votes/proposals", (r) => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) }));
    await page.route("**/api/v1/weather/forecast*", (r) => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ postcode: "8004", current_temp_c: 12, current_condition: "clear", observed_at: STAMP, days: [], source: "Open-Meteo", trust_state: "source_pending", fetched_at: STAMP, cache_ttl_seconds: 900 }) }));
    await page.route("**/api/v1/weather/alerts*", (r) => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "source_pending", items: [], source: "MeteoSwiss", official_url: "https://www.meteoswiss.admin.ch/", fetched_at: STAMP, note: "mock" }) }));
    await page.route("**/api/v1/municipal/waste-calendar*", (r) => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ postcode: "8004", events: [], source: "Municipal", source_url: "https://example.com/", fetched_at: STAMP, trust_state: "source_pending" }) }));
    await page.route("**/api/v1/costs/assessment*", (r) => r.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ status: "source_pending", items: [] }) }));
    // Everything the page fires but this card does not assert on: abort so
    // the restore chain's DetailPanel sections stay in their pending state
    // instead of crashing on a wrong shape (SPEC-045 pattern).
    for (const path of ["**/api/v1/property/prices*", "**/api/v1/tax/comparison*", "**/api/v1/hazard/assessment*", "**/api/v1/heritage/isos*", "**/api/v1/climate/**", "**/api/v1/education/**", "**/api/v1/energy/**", "**/api/v1/environment/**", "**/api/v1/healthcare/**", "**/api/v1/connectivity/**", "**/api/v1/ai/summary", "**/api/v1/planning/radius*"]) {
      await page.route(path, (r) => r.abort());
    }
    await page.route("**/api/v1/watch/events*", async (route) => {
      if (mode === "error") { await route.fulfill({ status: 503, contentType: "application/json", body: "{}" }); return; }
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(mode === "empty" ? { ...events, count: 0, items: [], status: "empty", trust_state: "source_pending" } : events) });
    });
    await page.route("**/api/v1/watch/deadlines*", async (route) => {
      if (mode === "error") { await route.fulfill({ status: 503, contentType: "application/json", body: "{}" }); return; }
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(mode === "empty" ? { ...deadlines, count: 0, items: [], status: "source_pending", trust_state: "source_pending" } : deadlines) });
    });
    await page.route("**/api/v1/watch/zones", async (route) => {
      if (route.request().method() !== "POST") { await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ count: 0, items: [] }) }); return; }
      await route.fulfill({ status: 200, contentType: "application/json", body: route.request().postData() ?? "{}" });
    });
  }

  async function openHub(page: Page, locale: string) {
    await page.goto(`/${locale}`, { waitUntil: "domcontentloaded" });
    await page.waitForLoadState("networkidle").catch(() => {});
    // SPEC-053/045 pattern: SearchPanel defaults the query to 8004, so a real
    // search click is what gives the hub (and this card) its postcode.
    const btn = page.getByTestId("search-button");
    await expect(btn).toBeVisible({ timeout: 20000 });
    await expect(btn).toBeEnabled({ timeout: 10000 });
    await btn.click();
    const card = page.getByTestId("watch-events-card");
    await expect(card).toBeVisible({ timeout: 15000 });
    return card;
  }

  test("happy path: events + countdown + disclaimer in the hub (/de)", async ({ page }) => {
    await mockAll(page, "ok");
    const card = await openHub(page, "de");

    // REQ-A3: event row carries distance, kind and a source trust badge
    const ev = card.getByTestId("watch-event-zone-8004:zh-8004-77:new_permit");
    await expect(ev).toBeVisible();
    await expect(ev.getByText("413 m entfernt")).toBeVisible();
    await expect(ev.getByText("Neues Baugesuch")).toBeVisible();
    await expect(ev.getByText("official publication")).toBeVisible();
    await expect(ev.getByRole("link")).toHaveAttribute("href", "https://amtsblattportal.ch/de/publications/77");

    // REQ-B1/B2: open deadline vs expired deadline with distinct states
    const open = card.getByTestId("watch-deadline-zh-8004-77");
    await expect(open).toHaveAttribute("data-state", "open");
    await expect(open.getByText("noch 6 Tage")).toBeVisible();
    const expired = card.getByTestId("watch-deadline-zh-8004-88");
    await expect(expired).toHaveAttribute("data-state", "expired");
    await expect(expired.getByText("abgelaufen", { exact: false }).first()).toBeVisible();
    await expect(expired.getByText("seit 7 Tagen abgelaufen")).toBeVisible();
    await expect(expired.getByText("offen")).toHaveCount(0);

    // REQ-B3: disclaimer next to the countdown, inside the same row
    await expect(open.getByText("Keine Rechtsberatung", { exact: false })).toBeVisible();
    await expect(open.getByText("Regel", { exact: false })).toBeVisible();
  });

  // One fresh page load per locale: the hub is keyed by postcode, so an
  // in-app locale switch reuses the previous payload (sibling specs navigate
  // per locale the same way).
  const localeExpectations: Array<[string, string, string, string]> = [
    ["de", "Einsprachefristen", "Zone beobachten", "noch 6 Tage"],
    ["en", "Appeal deadlines", "Watch zone", "6 days left"],
    ["fr", "Délais de recours", "Surveiller la zone", "encore 6 jours"],
    ["it", "Termini di ricorso", "Sorveglia zona", "ancora 6 giorni"],
  ];
  for (const [locale, deadlinesTitle, submit, countdown] of localeExpectations) {
    test(`i18n: the card is fully localized (/${locale})`, async ({ page }) => {
      await mockAll(page, "ok");
      const card = await openHub(page, locale);
      await expect(card.getByText(deadlinesTitle)).toBeVisible();
      await expect(card.getByText(submit)).toBeVisible();
      await expect(card.getByText(countdown)).toBeVisible();
      if (locale !== "de") {
        await expect(card.getByText(msg_disclaimer[locale], { exact: false }).first()).toBeVisible();
        await expect(card.getByText("Noch keine Einwilligung", { exact: false })).toHaveCount(0);
      }
    });
  }

  test("i18n: expired wording is localized too (/en)", async ({ page }) => {
    await mockAll(page, "ok");
    const card = await openHub(page, "en");
    const expired = card.getByTestId("watch-deadline-zh-8004-88");
    await expect(expired).toHaveAttribute("data-state", "expired");
    await expect(expired.getByText("expired 7 days ago")).toBeVisible();
  });

  test("empty state: no new events, no invented countdown (/de)", async ({ page }) => {
    await mockAll(page, "empty");
    const card = await openHub(page, "de");
    await expect(card.getByTestId("watch-empty")).toBeVisible();
    await expect(card.getByTestId("watch-empty")).toContainText("Keine neuen Ereignisse");
    await expect(card.locator('[data-testid^="watch-deadline-"]')).toHaveCount(0);
    await expect(card.locator('[data-testid^="watch-event-"]')).toHaveCount(0);
  });

  test("error state: provider outage is an explicit alert, nothing invented (/de)", async ({ page }) => {
    await mockAll(page, "error");
    const card = await openHub(page, "de");
    await expect(card.getByRole("alert")).toBeVisible({ timeout: 15000 });
    await expect(card.getByText("Meldungen konnten nicht geladen werden.")).toBeVisible();
    await expect(card.locator('[data-testid^="watch-deadline-"]')).toHaveCount(0);
  });

  test("REQ-A1 consent gate: submit stays disabled and explains why, then posts a real zone (/de)", async ({ page }) => {
    await mockAll(page, "ok");
    const card = await openHub(page, "de");
    const submit = card.getByTestId("watch-submit");
    await expect(submit).toBeVisible();
    await expect(submit).toBeDisabled();
    // gate order is consent -> channel -> address: the first missing item wins
    await expect(card.getByTestId("watch-consent-reason")).toContainText("Einwilligung");

    // consent given but no channel left -> its own reason
    const channelEmail = card.locator('input[name="watch-channel"][value="email"]');
    const consentBox = card.locator('input[name="watch-consent"]');
    await channelEmail.check();
    await consentBox.check();
    await channelEmail.uncheck();
    await expect(card.getByTestId("watch-consent-reason")).toContainText("Kanal");
    await expect(submit).toBeDisabled();

    // a real email + consent unblocks and the POST carries consent + channel
    await channelEmail.check();
    await card.locator('input[name="watch-email"]').fill("resident@example.ch");
    await expect(card.getByTestId("watch-consent-reason")).toHaveCount(0);
    await expect(submit).toBeEnabled();

    const [request] = await Promise.all([
      page.waitForRequest((r) => r.url().includes("/api/v1/watch/zones") && r.method() === "POST"),
      submit.click(),
    ]);
    const body = JSON.parse(request.postData() ?? "{}");
    expect(body.consent).toBe(true);
    expect(body.channels).toEqual(["email"]);
    expect(body.email).toBe("resident@example.ch");
    expect(body.zone_id).toBe("zone-8004");
    expect(body.radius_m).toBe(500);
    await expect(card.getByTestId("watch-submit-status")).toContainText("Zone gespeichert");
  });

  test("a11y: countdown colour is not the only signal and the card is keyboard reachable (/de)", async ({ page }) => {
    await mockAll(page, "ok");
    const card = await openHub(page, "de");
    const open = card.getByTestId("watch-deadline-zh-8004-77");
    const expired = card.getByTestId("watch-deadline-zh-8004-88");
    // the state badge carries the tone class difference AND a textual state
    const openBadge = open.locator("span.font-bold").first();
    const expiredBadge = expired.locator("span.font-bold").first();
    expect(await openBadge.getAttribute("class")).not.toEqual(await expiredBadge.getAttribute("class"));
    await expect(openBadge).toHaveText("offen");
    await expect(expiredBadge).toHaveText("abgelaufen");
    await expect(open).toHaveAttribute("data-state", "open");
    await expect(expired).toHaveAttribute("data-state", "expired");
    // keyboard reachability: fill the REQ-A1 gate first (an enabled submit is
    // tab-reachable; a disabled one is correctly skipped by the browser), then
    // check consent -> submit focus order
    const emailBox = card.locator('input[name="watch-email"]');
    await emailBox.fill("resident@example.ch");
    const consentBox = card.locator('input[name="watch-consent"]');
    await consentBox.check();
    await expect(card.getByTestId("watch-submit")).toBeEnabled();
    await consentBox.focus();
    await expect(consentBox).toBeFocused();
    await page.keyboard.press("Tab");
    await expect(card.getByTestId("watch-submit")).toBeFocused();
  });
});
