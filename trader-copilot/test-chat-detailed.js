const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  // Capture console logs and errors
  const logs = [];
  page.on('console', msg => {
    logs.push(`[${msg.type()}] ${msg.text()}`);
  });
  
  page.on('pageerror', error => {
    logs.push(`[PAGE ERROR] ${error.message}`);
  });
  
  console.log('🔍 Testing detailed chat functionality...');
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(3000);
  
  console.log('\n=== CHECKING PAGE LOAD ===');
  const chatInput = page.locator('input[placeholder*="Ask about market"]');
  const submitBtn = page.locator('button[type="submit"]');
  
  const inputVisible = await chatInput.isVisible();
  const btnVisible = await submitBtn.isVisible();
  
  console.log('Chat input visible:', inputVisible);
  console.log('Submit button visible:', btnVisible);
  
  if (!inputVisible || !btnVisible) {
    console.log('❌ Chat interface not properly loaded');
    console.log('Console logs:', logs);
    await browser.close();
    return;
  }
  
  console.log('\n=== TESTING MESSAGE SEND ===');
  await chatInput.fill('test message');
  await page.waitForTimeout(500);
  
  const isEnabled = !(await submitBtn.isDisabled());
  console.log('Submit button enabled:', isEnabled);
  
  if (!isEnabled) {
    console.log('❌ Submit button not enabled');
    await browser.close();
    return;
  }
  
  // Click and wait
  console.log('Clicking submit...');
  await submitBtn.click();
  
  // Wait longer and check for any changes
  await page.waitForTimeout(5000);
  
  console.log('\n=== CONSOLE LOGS ===');
  logs.forEach(log => console.log(log));
  
  console.log('\n=== MESSAGE ELEMENTS CHECK ===');
  const messageElements = page.locator('[role="presentation"], .bg-muted, .bg-blue-600');
  const messageCount = await messageElements.count();
  console.log('Message elements found:', messageCount);
  
  if (messageCount > 0) {
    for (let i = 0; i < messageCount; i++) {
      const text = await messageElements.nth(i).textContent();
      console.log(`Message ${i + 1}:`, text?.substring(0, 50) + '...');
    }
  }
  
  console.log('\nBrowser staying open for manual inspection...');
  await page.waitForTimeout(10000);
  
  await browser.close();
})();