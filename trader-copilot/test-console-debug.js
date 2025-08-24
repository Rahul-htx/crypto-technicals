const { chromium } = require('playwright');

async function testConsoleDebug() {
  console.log('🧪 Testing Console Messages and API Calls...\n');
  
  const browser = await chromium.launch({ headless: false });
  const context = await browser.newContext();
  const page = await context.newPage();

  // Capture all console messages
  page.on('console', msg => {
    console.log(`📝 Console [${msg.type()}]: ${msg.text()}`);
  });

  // Capture network requests
  page.on('request', request => {
    if (request.url().includes('/api/')) {
      console.log(`🌐 Request: ${request.method()} ${request.url()}`);
    }
  });

  page.on('response', response => {
    if (response.url().includes('/api/')) {
      console.log(`📡 Response: ${response.status()} ${response.url()}`);
    }
  });

  try {
    // Navigate to the app
    await page.goto('http://localhost:3000');
    console.log('✅ Navigated to app');

    // Wait for page to load
    await page.waitForTimeout(5000);
    
    console.log('\n🔍 Waiting for auto-refresh activity (20 seconds)...');
    await page.waitForTimeout(20000);

  } catch (error) {
    console.error('❌ Test failed:', error.message);
  } finally {
    await browser.close();
  }
}

testConsoleDebug().catch(console.error);
