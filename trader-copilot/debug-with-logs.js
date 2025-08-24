const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // Capture all console messages
  const logs = [];
  page.on('console', msg => {
    logs.push(`${msg.type().toUpperCase()}: ${msg.text()}`);
  });
  
  console.log('Loading page...');
  await page.goto('http://localhost:3001');
  await page.waitForTimeout(3000);
  
  console.log('\n=== Console logs after page load ===');
  logs.forEach(log => console.log(log));
  logs.length = 0; // Clear logs
  
  const chatInput = page.locator('input[placeholder*="Ask about market"]');
  const submitBtn = page.locator('button[type="submit"]');
  
  console.log('\n=== Typing into chat input ===');
  await chatInput.fill('test message');
  await page.waitForTimeout(1000);
  
  const inputValue = await chatInput.inputValue();
  const buttonDisabled = await submitBtn.isDisabled();
  
  console.log('Input value:', inputValue);
  console.log('Button disabled:', buttonDisabled);
  
  console.log('\n=== Console logs after typing ===');
  logs.forEach(log => console.log(log));
  
  await browser.close();
})();