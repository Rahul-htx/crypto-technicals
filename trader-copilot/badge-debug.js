const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log('Loading page to debug badge elements...');
  await page.goto('http://localhost:3001');
  await page.waitForTimeout(5000);
  
  // Find all badges on the page
  const badges = page.locator('[data-slot="badge"]');
  const badgeCount = await badges.count();
  console.log(`Found ${badgeCount} badge elements:`);
  
  for (let i = 0; i < badgeCount; i++) {
    const badgeText = await badges.nth(i).textContent();
    const badgeClass = await badges.nth(i).getAttribute('class');
    console.log(`Badge ${i + 1}: "${badgeText}" (class: ${badgeClass})`);
  }
  
  // Specifically look at the Live Prices section
  console.log('\n--- Live Prices Section ---');
  const livePricesHeading = page.locator('h3:has-text("Live Prices")');
  const livePricesCard = livePricesHeading.locator('..').locator('..');
  const livePricesBadge = livePricesCard.locator('[data-slot="badge"]').first();
  
  if (await livePricesBadge.isVisible()) {
    const text = await livePricesBadge.textContent();
    console.log(`Live Prices badge: "${text}"`);
  } else {
    console.log('Live Prices badge not found');
  }
  
  await browser.close();
})();