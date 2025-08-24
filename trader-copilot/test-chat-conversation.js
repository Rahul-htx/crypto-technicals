const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log('🔍 Testing chat conversation functionality...');
  await page.goto('http://localhost:3000');
  await page.waitForTimeout(3000); // Wait for full load
  
  // Test 1: Check if chat input is available
  console.log('\n=== CHAT INPUT TEST ===');
  const chatInput = page.locator('input[placeholder*="Ask about market"]');
  const submitBtn = page.locator('button[type="submit"]');
  
  if (await chatInput.isVisible()) {
    console.log('✅ Chat input found');
  } else {
    console.log('❌ Chat input not found');
    await browser.close();
    return;
  }
  
  // Test 2: Type a test message
  console.log('\n=== SENDING TEST MESSAGE ===');
  const testMessage = 'Hello, can you help me analyze Bitcoin?';
  
  await chatInput.fill(testMessage);
  await page.waitForTimeout(500);
  
  // Check if submit button is enabled
  const isEnabled = !(await submitBtn.isDisabled());
  console.log('Submit button enabled:', isEnabled);
  
  if (!isEnabled) {
    console.log('❌ Submit button is disabled, cannot send message');
    await browser.close();
    return;
  }
  
  // Test 3: Submit the message and wait for response
  console.log('Submitting message:', testMessage);
  await submitBtn.click();
  
  // Wait for user message to appear
  await page.waitForTimeout(1000);
  
  // Check if user message appears in chat
  const userMessage = page.locator('text=' + testMessage).first();
  if (await userMessage.isVisible()) {
    console.log('✅ User message appeared in chat');
  } else {
    console.log('❌ User message did not appear in chat');
  }
  
  // Test 4: Wait for AI response (with longer timeout)
  console.log('\n=== WAITING FOR AI RESPONSE ===');
  console.log('Waiting up to 30 seconds for AI response...');
  
  try {
    // Look for thinking indicator first
    const thinkingIndicator = page.locator('text="Thinking..."');
    if (await thinkingIndicator.isVisible()) {
      console.log('✅ "Thinking..." indicator appeared');
      
      // Wait for thinking to disappear (response received)
      await thinkingIndicator.waitFor({ state: 'hidden', timeout: 30000 });
      console.log('✅ "Thinking..." indicator disappeared');
    }
    
    // Look for any response from the bot
    await page.waitForTimeout(2000); // Give time for response to render
    
    // Count total messages (should be at least 2: user + bot)
    const allMessages = page.locator('[role="presentation"]:has-text("' + testMessage + '"), .bg-muted:not(:has-text("Thinking..."))');
    const messageCount = await allMessages.count();
    
    console.log('Total messages found:', messageCount);
    
    if (messageCount >= 2) {
      console.log('✅ AI response received');
      
      // Try to get the AI response text
      const botMessages = page.locator('.bg-muted:not(:has-text("Thinking..."))');
      const botMessageCount = await botMessages.count();
      
      if (botMessageCount > 0) {
        const firstBotResponse = await botMessages.first().textContent();
        console.log('First AI response preview:', firstBotResponse?.substring(0, 100) + '...');
      }
      
    } else {
      console.log('❌ No AI response received after 30 seconds');
    }
    
  } catch (error) {
    console.log('❌ Timeout waiting for AI response:', error.message);
  }
  
  // Test 5: Check for any console errors
  console.log('\n=== CONSOLE ERRORS CHECK ===');
  const logs = [];
  page.on('console', msg => {
    if (msg.type() === 'error') {
      logs.push(msg.text());
    }
  });
  
  await page.waitForTimeout(2000);
  
  if (logs.length > 0) {
    console.log('Console errors found:');
    logs.forEach(log => console.log('  ❌', log));
  } else {
    console.log('✅ No console errors detected');
  }
  
  // Test 6: Check network requests
  console.log('\n=== NETWORK REQUESTS CHECK ===');
  let chatRequestMade = false;
  
  page.on('request', request => {
    if (request.url().includes('/api/chat')) {
      chatRequestMade = true;
      console.log('✅ Chat API request detected:', request.method());
    }
  });
  
  // Send another quick test message to trigger network monitoring
  await chatInput.fill('What time is it?');
  await submitBtn.click();
  await page.waitForTimeout(3000);
  
  if (chatRequestMade) {
    console.log('✅ Chat API requests are being made');
  } else {
    console.log('❌ No chat API requests detected');
  }
  
  console.log('\n=== FINAL CHAT TEST SUMMARY ===');
  console.log('🎯 Chat conversation test completed');
  console.log('Check the browser window for visual confirmation');
  
  // Keep browser open for manual inspection
  console.log('\nBrowser will stay open for 10 seconds for manual inspection...');
  await page.waitForTimeout(10000);
  
  await browser.close();
})();