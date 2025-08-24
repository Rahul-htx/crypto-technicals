const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log('🔍 Testing basic chat without tools...');
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(3000);
  
  const chatInput = page.locator('input[placeholder*="Ask about market"]');
  const submitBtn = page.locator('button[type="submit"]');
  
  console.log('Sending test message...');
  await chatInput.fill('Hello, can you help me?');
  await page.waitForTimeout(500);
  await submitBtn.click();
  
  // Wait for user message to appear
  console.log('Waiting for user message...');
  await page.waitForTimeout(2000);
  
  // Look for user message
  const userMsg = page.locator('text="Hello, can you help me?"');
  if (await userMsg.isVisible()) {
    console.log('✅ User message appeared');
  } else {
    console.log('❌ User message not visible');
  }
  
  // Wait for AI response (look for thinking indicator first)
  console.log('Waiting for AI response...');
  const thinkingIndicator = page.locator('text="Thinking..."');
  
  if (await thinkingIndicator.isVisible()) {
    console.log('✅ AI is thinking...');
    
    // Wait for response to complete
    await page.waitForTimeout(15000); // Give it 15 seconds
    
    // Check if thinking disappeared
    const stillThinking = await thinkingIndicator.isVisible();
    if (!stillThinking) {
      console.log('✅ AI finished thinking');
      
      // Look for any assistant message
      const assistantMessages = page.locator('.bg-muted:not(:has-text("Thinking..."))');
      const count = await assistantMessages.count();
      
      if (count > 0) {
        const response = await assistantMessages.first().textContent();
        console.log('✅ AI Response received:', response?.substring(0, 100) + '...');
      } else {
        console.log('❌ No AI response content found');
      }
    } else {
      console.log('⚠️ AI still thinking after 15 seconds');
    }
  } else {
    console.log('❌ No thinking indicator appeared');
  }
  
  console.log('\nBrowser staying open for 5 seconds...');
  await page.waitForTimeout(5000);
  
  await browser.close();
})();