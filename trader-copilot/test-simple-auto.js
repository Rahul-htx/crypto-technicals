const { chromium } = require('playwright');

async function testSimpleAuto() {
  console.log('🧪 Testing Auto-Refresh UI Elements...\n');
  
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Navigate to the app
    await page.goto('http://localhost:3000');
    console.log('✅ Navigated to app');

    // Wait a bit for everything to load
    await page.waitForTimeout(3000);

    // Look for the auto button with more flexible selector
    const autoButton = page.locator('button:has-text("Auto")').first();
    const buttonExists = await autoButton.count() > 0;
    
    if (buttonExists) {
      console.log('✅ Auto-refresh button found');
      
      const buttonText = await autoButton.textContent();
      console.log(`📊 Button text: "${buttonText}"`);
      
      const isAutoEnabled = buttonText.includes('🟢');
      console.log(`🔄 Auto-refresh status: ${isAutoEnabled ? 'ENABLED' : 'DISABLED'}`);
      
      // Test clicking the button
      console.log('\n🖱️  Testing button toggle...');
      await autoButton.click();
      await page.waitForTimeout(1000);
      
      const newButtonText = await autoButton.textContent();
      console.log(`📊 After click: "${newButtonText}"`);
      
      const isNowEnabled = newButtonText.includes('🟢');
      console.log(`🔄 Auto-refresh now: ${isNowEnabled ? 'ENABLED' : 'DISABLED'}`);
      
      // Check console for auto-refresh messages
      console.log('\n🔍 Waiting for auto-refresh activity...');
      
      // Listen for console messages
      page.on('console', msg => {
        if (msg.text().includes('Auto-refresh') || msg.text().includes('🔄')) {
          console.log(`📝 Console: ${msg.text()}`);
        }
      });
      
      // Wait for potential auto-refresh activity
      await page.waitForTimeout(15000);
      
    } else {
      console.log('❌ Auto-refresh button not found');
      
      // Debug: show what buttons are available
      const allButtons = await page.locator('button').all();
      console.log(`🔍 Found ${allButtons.length} buttons on page`);
      
      for (let i = 0; i < Math.min(allButtons.length, 5); i++) {
        const buttonText = await allButtons[i].textContent();
        console.log(`   Button ${i + 1}: "${buttonText}"`);
      }
    }

    console.log('\n✅ Test completed');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testSimpleAuto().catch(console.error);
