import { test, expect } from "@playwright/test";

// SPEC-051: VotingVisualCard live states (mocked backend at page level).
test.describe("SPEC-051 VotingVisualCard", () => {
  const proposals = {
    items: [
      { id: 6801, title: "Kommende eidgenössische Vorlage", vote_date: "2026-11-29", status: "upcoming", source: "Bundeskanzlei / BFS VoteInfo" },
      { id: 6670, title: "13. AHV-Rente", vote_date: "2024-03-03", status: "final", source: "Bundeskanzlei / BFS VoteInfo" },
    ],
  };
  const analysis6801 = {
    proposal: proposals.items[0],
    pro_arguments: ["Offizielle Pro-Argumente"],
    contra_arguments: ["Offizielle Contra-Argumente"],
    polls: [{ institute: "Demo Institut", sample_size: 1200, margin_percent: 2.8, yes_percent: 52, fieldwork_date: "2026-08-20" }],
    local_yes_percent: null, cantonal_yes_percent: null, national_yes_percent: null,
  };
  const analysis6670 = {
    proposal: proposals.items[1],
    pro_arguments: ["Pro AHV"],
    contra_arguments: ["Contra AHV"],
    polls: [],
    local_yes_percent: 61.2, cantonal_yes_percent: 59.8, national_yes_percent: 58.2,
  };

  async function mockVotes(page: import("@playwright/test").Page) {
    await page.route("**/api/v1/votes/proposals", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(proposals) });
    });
    await page.route("**/api/v1/votes/proposals/6801/analysis", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(analysis6801) });
    });
    await page.route("**/api/v1/votes/proposals/6670/analysis", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(analysis6670) });
    });
  }

  test("happy path: live poll bar + Pro/Contra + trust badge + proposal switch (/de)", async ({ page }) => {
    await mockVotes(page);
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    // search so LocalInformationHub + ResidentCivicPanels render
    await expect(page.getByTestId("map-3d")).toBeVisible();
    await page.getByTestId("search-button").click();
    const card = page.getByTestId("voting-visual-card");
    await expect(card).toBeVisible({ timeout: 15000 });
    await expect(card.getByText("Ja: 52 %")).toBeVisible({ timeout: 10000 });
    await expect(card.getByText("modeled estimate")).toBeVisible();
    await expect(card.getByText("Demo Institut").first()).toBeVisible();
    // switch to final proposal -> official publication badge + national result
    await card.getByLabel("Vorlage").selectOption("6670");
    await expect(card.getByText("official publication")).toBeVisible({ timeout: 10000 });
    await expect(card.getByText(/National 58.2/)).toBeVisible();
  });

  test("error state: proposals 500 shows alert, no fake freshness (/de)", async ({ page }) => {
    await page.route("**/api/v1/votes/proposals", async (route) => {
      await route.fulfill({ status: 500, contentType: "application/json", body: "{}" });
    });
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    await expect(page.getByTestId("map-3d")).toBeVisible();
    await page.getByTestId("search-button").click();
    const card = page.getByTestId("voting-visual-card");
    await expect(card).toBeVisible({ timeout: 15000 });
    await expect(card.getByText("Abstimmungen konnten nicht geladen werden.")).toBeVisible({ timeout: 10000 });
  });

  test("empty state: no proposals (/en)", async ({ page }) => {
    await page.route("**/api/v1/votes/proposals", async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ items: [] }) });
    });
    await page.goto("/en", { waitUntil: "domcontentloaded" });
    await expect(page.getByTestId("map-3d")).toBeVisible();
    await page.getByTestId("search-button").click();
    const card = page.getByTestId("voting-visual-card");
    await expect(card).toBeVisible({ timeout: 15000 });
    await expect(card.getByText("No vote proposals available.")).toBeVisible({ timeout: 10000 });
  });
});
