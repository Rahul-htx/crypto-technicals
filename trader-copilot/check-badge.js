const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log('Loading page...');
  await page.goto('http://localhost:3001');
  
  // Wait longer for initial data load
  console.log('Waiting for data to load...');
  await page.waitForTimeout(5000);
  
  // Check hash badge immediately
  const hashBadge = page.locator('[data-slot="badge"]').first();
  const initialBadgeText = await hashBadge.textContent();
  console.log('Initial hash badge:', initialBadgeText);
  
  // Try clicking refresh button
  console.log('Clicking refresh button...');
  const refreshBtn = page.locator('button').filter({ has: page.locator('svg.lucide-refresh-cw') });
  await refreshBtn.click();
  
  // Wait for refresh to complete
  await page.waitForTimeout(3000);
  
  const afterRefreshBadgeText = await hashBadge.textContent();
  console.log('After refresh hash badge:', afterRefreshBadgeText);
  
  // Check if prices loaded
  const pricesText = page.locator('text="No price data available"');
  const hasPricesError = await pricesText.isVisible();
  console.log('No price data error visible:', hasPricesError);
  
  // Check if there are actual price displays
  const priceElements = page.locator('text=/\\$[0-9,]+/');
  const priceCount = await priceElements.count();
  console.log('Number of price elements found:', priceCount);
  
  if (priceCount > 0) {
    const firstPrice = await priceElements.first().textContent();
    console.log('First price found:', firstPrice);
  }
  
  await browser.close();
})();