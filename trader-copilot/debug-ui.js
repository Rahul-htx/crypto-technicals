// Simple debug script to test the actual UI state
const playwright = require('@playwright/test');

(async () => {
  const { chromium } = playwright;
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  await page.goto('http://localhost:3001');
  await page.waitForTimeout(3000); // Wait for page to load
  
  // Check what the hash badge actually shows
  const hashBadge = page.locator('[data-slot="badge"]').first();
  if (await hashBadge.isVisible()) {
    const badgeText = await hashBadge.textContent();
    console.log('Hash badge text:', badgeText);
  }
  
  // Check for timestamp text
  const timestampText = page.getByText(/Updated:.*CT/);
  if (await timestampText.isVisible()) {
    const text = await timestampText.textContent();
    console.log('Timestamp text:', text);
  } else {
    console.log('No timestamp found');
  }
  
  // Check if there are any console errors
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  
  // Take a screenshot
  await page.screenshot({ path: 'debug-screenshot.png' });
  
  await browser.close();
})();