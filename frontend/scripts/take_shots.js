const { chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');

async function main() {
  const outDir = path.join(__dirname, '../../docs/screenshots');
  if (!fs.existsSync(outDir)) {
    fs.mkdirSync(outDir, { recursive: true });
  }

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1440, height: 950 } });

  console.log('1. Loading home page...');
  await page.goto('http://127.0.0.1:3410/de', { waitUntil: 'domcontentloaded' });
  await page.waitForTimeout(3000);
  await page.screenshot({ path: path.join(outDir, '01_initial_de.png'), fullPage: true });

  console.log('2. Searching 8004...');
  const input = page.getByPlaceholder('PLZ, Adresse oder Gemeinde');
  await input.fill('8004');
  await page.getByRole('button', { name: 'Suchen' }).click();
  await page.waitForTimeout(3000);
  await page.screenshot({ path: path.join(outDir, '02_search_8004_de.png'), fullPage: true });

  console.log('3. Topic: Politik...');
  await page.getByTestId('menu-politik').click();
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(outDir, '03_topic_politik.png'), fullPage: true });

  console.log('4. Topic: Planung...');
  await page.getByTestId('menu-planung').click();
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(outDir, '04_topic_planung.png'), fullPage: true });

  console.log('5. Mobile view...');
  await page.setViewportSize({ width: 390, height: 844 });
  await page.waitForTimeout(1500);
  await page.screenshot({ path: path.join(outDir, '05_mobile_planung.png'), fullPage: true });

  await browser.close();
  console.log('All screenshots saved in docs/screenshots/');
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
