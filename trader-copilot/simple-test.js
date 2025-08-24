const { chromium } = require('@playwright/test');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  console.log('Loading page...');
  await page.goto('http://localhost:3001');
  await page.waitForTimeout(5000); // Wait for everything to load
  
  // Check timestamp
  try {
    const timestamp = page.locator('text=/Updated.*CT/').first();
    if (await timestamp.isVisible()) {
      const text = await timestamp.textContent();
      console.log('✅ Found timestamp:', text);
    } else {
      console.log('❌ No timestamp found');
    }
  } catch (e) {
    console.log('⚠️ Timestamp check failed:', e.message);
  }
  
  // Check hash badge 
  try {
    const hashBadge = page.locator('[data-slot="badge"]').first();
    const badgeText = await hashBadge.textContent();
    console.log('Hash badge:', badgeText);
  } catch (e) {
    console.log('⚠️ Hash badge check failed:', e.message);
  }
  
  // Check if chat input is enabled after typing
  try {
    const chatInput = page.locator('input[placeholder*="Ask about market"]');
    const submitBtn = page.locator('button[type="submit"]');
    
    console.log('Testing chat input...');
    
    // Initially button should be disabled
    const initialDisabled = await submitBtn.isDisabled();
    console.log('Submit button initially disabled:', initialDisabled);
    
    // Type something
    await chatInput.fill('Hello test');
    await page.waitForTimeout(100); // Small delay for state update
    
    // Now button should be enabled
    const afterTypingDisabled = await submitBtn.isDisabled();
    console.log('Submit button disabled after typing:', afterTypingDisabled);
    
    if (!afterTypingDisabled) {
      console.log('✅ Chat functionality working - button enabled after typing');
    } else {
      console.log('❌ Chat functionality not working - button still disabled');
    }
    
  } catch (e) {
    console.log('⚠️ Chat test failed:', e.message);
  }
  
  await browser.close();
  console.log('Test completed');
})();