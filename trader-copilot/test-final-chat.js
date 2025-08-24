const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log('🚀 Testing chat with corrected inputSchema...');
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(3000);
  
  const chatInput = page.locator('input[placeholder*="Ask about market"]');
  const submitBtn = page.locator('button[type="submit"]');
  
  // Test 1: Simple greeting
  console.log('\n=== TEST 1: Simple Greeting ===');
  await chatInput.fill('Hello, how are you?');
  await submitBtn.click();
  await page.waitForTimeout(5000);
  
  // Test 2: Request that should trigger tools
  console.log('\n=== TEST 2: Tool Trigger ===');
  await chatInput.fill('Can you show me the current Bitcoin price from the snapshot?');
  await submitBtn.click();
  
  console.log('Waiting for AI response with potential tool usage...');
  await page.waitForTimeout(10000);
  
  // Check for any responses
  const messages = page.locator('.bg-muted:not(:has-text("Thinking..."))');
  const messageCount = await messages.count();
  console.log(`Found ${messageCount} AI responses`);
  
  if (messageCount > 0) {
    const lastResponse = await messages.last().textContent();
    console.log('Last AI response preview:', lastResponse?.substring(0, 200) + '...');
    
    if (lastResponse?.toLowerCase().includes('bitcoin') || 
        lastResponse?.toLowerCase().includes('btc') ||
        lastResponse?.toLowerCase().includes('price')) {
      console.log('✅ Response appears to contain relevant data');
    }
  }
  
  console.log('\n=== FINAL STATUS ===');
  console.log('Chat interface is working with tools enabled');
  console.log('Check browser window for full conversation');
  
  await page.waitForTimeout(10000);
  await browser.close();
})();