const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log('Loading page...');
  await page.goto('http://localhost:3001');
  await page.waitForTimeout(3000);
  
  const chatInput = page.locator('input[placeholder*="Ask about market"]');
  const submitBtn = page.locator('button[type="submit"]');
  
  // Check initial state
  console.log('=== INITIAL STATE ===');
  const initialValue = await chatInput.inputValue();
  const initialDisabled = await submitBtn.isDisabled();
  console.log('Input value:', JSON.stringify(initialValue));
  console.log('Button disabled:', initialDisabled);
  
  // Type text
  console.log('\n=== TYPING TEXT ===');
  await chatInput.fill('Hello world');
  await page.waitForTimeout(500); // Wait for React state update
  
  // Check after typing  
  const afterValue = await chatInput.inputValue();
  const afterDisabled = await submitBtn.isDisabled();
  console.log('Input value:', JSON.stringify(afterValue));
  console.log('Button disabled:', afterDisabled);
  
  // Check if React has processed the change
  await page.waitForTimeout(1000);
  const finalDisabled = await submitBtn.isDisabled();
  console.log('Button disabled (after 1s wait):', finalDisabled);
  
  // Check console errors
  const logs = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      logs.push('ERROR: ' + msg.text());
    }
  });
  
  setTimeout(() => {
    if (logs.length > 0) {
      console.log('\n=== CONSOLE ERRORS ===');
      logs.forEach(log => console.log(log));
    } else {
      console.log('\n=== NO CONSOLE ERRORS ===');
    }
  }, 100);
  
  await browser.close();
})();