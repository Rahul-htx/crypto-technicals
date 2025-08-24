const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log('🔍 Testing chat auth debug...');
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(3000);
  
  const chatInput = page.locator('input[placeholder*="Ask about market"]');
  const submitBtn = page.locator('button[type="submit"]');
  
  await chatInput.fill('test auth debug');
  await page.waitForTimeout(500);
  await submitBtn.click();
  
  console.log('Message sent, check server logs for auth debug info');
  
  await page.waitForTimeout(3000);
  await browser.close();
})();