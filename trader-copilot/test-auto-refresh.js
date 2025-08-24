const { chromium } = require('playwright');

async function testAutoRefresh() {
  console.log('🧪 Testing Auto-Refresh Functionality...\n');
  
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    // Navigate to the app
    await page.goto('http://localhost:3000');
    console.log('✅ Navigated to app');

    // Wait for the page to load
    await page.waitForSelector('[data-testid="price-ticker"], .font-medium:has-text("Live Prices")', { timeout: 10000 });
    console.log('✅ Price ticker loaded');

    // Check if Auto button exists and is enabled by default
    const autoButton = page.locator('button:has-text("Auto")');
    await autoButton.waitFor({ timeout: 5000 });
    console.log('✅ Auto-refresh button found');

    // Get initial state
    const initialState = await autoButton.textContent();
    console.log(`📊 Initial auto-refresh state: ${initialState}`);

    // Check for Auto vs Manual state
    const isAutoEnabled = initialState.includes('🟢 Auto');
    console.log(`🔄 Auto-refresh initially: ${isAutoEnabled ? 'ENABLED' : 'DISABLED'}`);

    // Get initial timestamp
    const timeElement = page.locator('text=/Updated.*CT/');
    await timeElement.waitFor({ timeout: 5000 });
    const initialTime = await timeElement.textContent();
    console.log(`⏰ Initial timestamp: ${initialTime}`);

    // Get initial hash
    const hashBadge = page.locator('.text-xs').first();
    const initialHash = await hashBadge.textContent();
    console.log(`🏷️  Initial hash: ${initialHash}`);

    if (isAutoEnabled) {
      console.log('\n⏰ Waiting 15 seconds for auto-refresh to trigger...');
      
      // Wait and check if data updates automatically
      let hasUpdated = false;
      let attempts = 0;
      const maxAttempts = 3;
      
      while (!hasUpdated && attempts < maxAttempts) {
        await page.waitForTimeout(15000); // Wait 15 seconds
        attempts++;
        
        try {
          const newTime = await timeElement.textContent();
          const newHash = await hashBadge.textContent();
          
          console.log(`📊 Check ${attempts}/3:`);
          console.log(`   Time: ${newTime}`);
          console.log(`   Hash: ${newHash}`);
          
          if (newTime !== initialTime || newHash !== initialHash) {
            hasUpdated = true;
            console.log('✅ Auto-refresh detected! Data updated automatically');
          } else {
            console.log('⏳ No update yet, continuing to wait...');
          }
        } catch (error) {
          console.log(`⚠️  Check failed: ${error.message}`);
        }
      }
      
      if (!hasUpdated) {
        console.log('⚠️  Auto-refresh may not be working - no automatic updates detected');
      }
    }

    // Test manual toggle
    console.log('\n🔄 Testing manual toggle...');
    await autoButton.click();
    await page.waitForTimeout(1000);
    
    const newState = await autoButton.textContent();
    console.log(`🎛️  After toggle: ${newState}`);
    
    const isNowAuto = newState.includes('🟢 Auto');
    console.log(`🔄 Auto-refresh now: ${isNowAuto ? 'ENABLED' : 'DISABLED'}`);

    // Test manual refresh button
    console.log('\n🔄 Testing manual refresh...');
    const refreshButton = page.locator('button', { has: page.locator('svg') }).last();
    await refreshButton.click();
    console.log('✅ Manual refresh button clicked');
    
    // Wait for refresh to complete
    await page.waitForTimeout(3000);
    
    const finalTime = await timeElement.textContent();
    const finalHash = await hashBadge.textContent();
    console.log(`⏰ Final timestamp: ${finalTime}`);
    console.log(`🏷️  Final hash: ${finalHash}`);

    console.log('\n🎉 Auto-refresh test completed!');

  } catch (error) {
    console.error('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testAutoRefresh().catch(console.error);
