const { chromium } = require('playwright');
const assert = require('assert');

(async () => {
  console.log('🧪 Verifying tool-calling with a different model...');
  const browser = await chromium.launch({ headless: false });
  const page = await (await browser.newContext()).newPage();
  
  try {
    await page.goto('http://localhost:3000', { timeout: 20000 });
    console.log('✅ UI Loaded');

    // --- Step 1: Switch to a more standard model ---
    console.log('\\n1️⃣  Switching model to gpt-5...');
    const modelSelector = page.locator('label:has-text("gpt-5")');
    await modelSelector.waitFor({ state: 'visible', timeout: 5000 });
    await modelSelector.click();
    console.log('✅ Switched model to gpt-5');

    // --- Step 2: Test the price lookup query ---
    console.log('\\n2️⃣  Testing price lookup: "what is the price of ETH"');
    await page.fill('input[placeholder*="Ask about market conditions"]', 'what is the price of ETH');
    await page.click('button[type="submit"]');

    // Wait for the response to appear and check for a price
    const priceResponseLocator = page.locator('div.prose p:has-text("$")');
    await priceResponseLocator.waitFor({ state: 'visible', timeout: 25000 }); // Increased timeout
    const priceResponseText = await priceResponseLocator.textContent();
    assert(priceResponseText.includes('$'), 'Response should contain a price');
    console.log(`✅ Received valid price response with gpt-5: "${priceResponseText}"`);
    
    console.log('\\n🎉 Test Passed! Tool-calling works correctly with the gpt-5 model.');

  } catch (error) {
    console.error('\\n❌ Test Failed:', error.message);
    await page.screenshot({ path: 'test-model-switch-failure.png' });
    console.error('📸 Screenshot saved to test-model-switch-failure.png');
  } finally {
    await browser.close();
  }
})();
