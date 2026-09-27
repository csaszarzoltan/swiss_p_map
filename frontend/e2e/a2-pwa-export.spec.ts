import { test, expect } from "@playwright/test";

/**
 * A2: PWA offline + Export audit-csomag (SPEC-027 / SPEC-020).
 * - PWA: navigator.serviceWorker.ready + offline szimulacio (page.route abort)
 *        -> PwaStatus Offline · Cache + aria-live
 * - Export: DetailPanel Export gomb (data-testid=export-button, format valaszto, a11y)
 */

test.describe("A2 — PWA offline + Export audit-csomag", () => {
  test("PWA sw.js + manifest.json icons (192+512) + PwaStatus aria-live", async ({ page }) => {
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    // sw.js reachable
    const swRes = await page.request.get("/sw.js");
    expect(swRes.ok()).toBeTruthy();
    const swText = await swRes.text();
    expect(swText).toContain("CACHE");
    expect(swText).toContain("fetch");
    // manifest has icons 192+512
    const mfRes = await page.request.get("/manifest.json");
    expect(mfRes.ok()).toBeTruthy();
    const manifest = await mfRes.json();
    const sizes = (manifest.icons ?? []).map((i: { sizes: string }) => i.sizes);
    expect(sizes).toContain("192x192");
    expect(sizes).toContain("512x512");
    // PwaStatus role=status aria-live=polite
    const pwa = page.locator('[role="status"][aria-live="polite"]').first();
    await expect(pwa).toBeVisible({ timeout: 8000 });
    await expect(pwa).toHaveAttribute("aria-live", "polite");
  });

  test("PwaStatus offline szimulacio -> Offline cached (route abort)", async ({ page }) => {
    await page.goto("/de", { waitUntil: "networkidle", timeout: 20000 });
    await page.waitForTimeout(1500);
    const pwa = page.locator('[role="status"][aria-live="polite"]').first();
    await expect(pwa).toBeVisible({ timeout: 8000 });
    // Simulate offline by aborting API routes + dispatching offline event
    await page.route("**/api/**", (route) => route.abort());
    await page.evaluate(() => window.dispatchEvent(new Event("offline")));
    await page.waitForTimeout(800);
    await expect(pwa).toContainText(/Offline/i, { timeout: 4000 });
    // Back online
    await page.unroute("**/api/**");
    await page.evaluate(() => window.dispatchEvent(new Event("online")));
    await page.waitForTimeout(400);
    await expect(pwa).toContainText(/Online/i, { timeout: 4000 });
  });

  test("DetailPanel Export gomb (a11y, format valaszto, keyboard)", async ({ page }) => {
    await page.goto("/de", { waitUntil: "domcontentloaded" });
    // Search 8004 to hydrate DetailPanel (export button requires place)
    await page.getByRole("button", { name: "8004 Aussersihl" }).click();
    await page.waitForTimeout(2000);
    const exportBtn = page.getByTestId("export-button");
    await expect(exportBtn).toBeVisible({ timeout: 8000 });
    await expect(exportBtn).toHaveAttribute("aria-label", /.+/);
    const formatSelect = page.getByTestId("export-format-select");
    await expect(formatSelect).toBeVisible();
    await expect(formatSelect).toHaveAttribute("aria-label", /.+/);
    // Keyboard: tab to export button + activate
    await exportBtn.focus();
    await expect(exportBtn).toBeFocused();
    // Default json, switch to csv
    await formatSelect.selectOption("csv");
    await expect(formatSelect).toHaveValue("csv");
    await formatSelect.selectOption("json");
    await expect(formatSelect).toHaveValue("json");
    // Click triggers download (anchor) + toast
    await exportBtn.click();
    await expect(page.getByRole("status").filter({ hasText: /Export/i }).first()).toBeVisible({ timeout: 3000 });
  });

  test("Export API direct: json+csv content-disposition (smoke via page.request)", async ({ page }) => {
    // Already covered in unit/e2e python, but verify from browser context too
    const jsonRes = await page.request.get("http://127.0.0.1:8310/api/v1/place/8004/export?format=json");
    expect(jsonRes.status()).toBe(200);
    expect(jsonRes.headers()["content-disposition"]).toContain('filename="swiss-p-map-8004.json"');
    const csvRes = await page.request.get("http://127.0.0.1:8310/api/v1/place/8004/export?format=csv");
    expect(csvRes.status()).toBe(200);
    expect(csvRes.headers()["content-disposition"]).toContain('filename="swiss-p-map-8004.csv"');
    expect(csvRes.headers()["content-type"]).toContain("text/csv");
  });
});
