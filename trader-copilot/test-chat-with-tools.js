const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log('🔍 Testing chat with tools enabled...');
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(3000);
  
  const chatInput = page.locator('input[placeholder*="Ask about market"]');
  const submitBtn = page.locator('button[type="submit"]');
  
  console.log('Sending message that should trigger tools...');
  await chatInput.fill('Can you get the latest Bitcoin market data?');
  await page.waitForTimeout(500);
  await submitBtn.click();
  
  console.log('Waiting for user message...');
  await page.waitForTimeout(2000);
  
  console.log('Waiting for AI response with tool usage...');
  const thinkingIndicator = page.locator('text="Thinking..."');
  
  if (await thinkingIndicator.isVisible()) {
    console.log('✅ AI is thinking (processing tools)...');
    
    // Wait longer for tool execution
    await page.waitForTimeout(20000); // Give it 20 seconds for tool usage
    
    const stillThinking = await thinkingIndicator.isVisible();
    if (!stillThinking) {
      console.log('✅ AI finished processing');
      
      // Look for assistant response
      const assistantMessages = page.locator('.bg-muted:not(:has-text("Thinking..."))');
      const count = await assistantMessages.count();
      
      if (count > 0) {
        const response = await assistantMessages.first().textContent();
        console.log('✅ AI Response received:', response?.substring(0, 200) + '...');
        
        // Check if response contains Bitcoin data
        if (response?.toLowerCase().includes('bitcoin') || response?.toLowerCase().includes('btc')) {
          console.log('✅ Response appears to contain Bitcoin data');
        } else {
          console.log('⚠️ Response might not contain expected Bitcoin data');
        }
      } else {
        console.log('❌ No AI response content found');
      }
    } else {
      console.log('⚠️ AI still thinking after 20 seconds');
    }
  } else {
    console.log('❌ No thinking indicator appeared');
  }
  
  console.log('\nBrowser staying open for inspection...');
  await page.waitForTimeout(10000);
  
  await browser.close();
})();