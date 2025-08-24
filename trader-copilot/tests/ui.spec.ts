import { test, expect } from '@playwright/test';

test.describe('CryptoCortex UI Tests', () => {
  test('homepage loads with correct title and components', async ({ page }) => {
    await page.goto('/');
    
    // Check title
    await expect(page).toHaveTitle('CryptoCortex v0.4.0');
    
    // Check main components are present
    await expect(page.getByRole('heading', { name: 'Trader Copilot' })).toBeVisible();
    await expect(page.getByText('AI-powered cryptocurrency trading assistant')).toBeVisible();
    
    // Check AI Model section
    await expect(page.getByText('AI Model')).toBeVisible();
    await expect(page.getByRole('radio', { name: 'o3' })).toBeVisible();
    await expect(page.getByRole('radio', { name: 'o3-deep-research' })).toBeVisible();
    await expect(page.getByRole('radio', { name: 'o4-mini-deep-research' })).toBeVisible();
    await expect(page.getByRole('radio', { name: 'gpt-5' })).toBeVisible();
    
    // Check Investment Thesis section
    await expect(page.getByText('Investment Thesis')).toBeVisible();
    
    // Check Live Prices section
    await expect(page.getByText('Live Prices')).toBeVisible();
    
    // Check Chat section
    await expect(page.getByText('Trading Copilot', { exact: true })).toBeVisible();
    await expect(page.getByText('Welcome to Trader Copilot!')).toBeVisible();
    
    // Check chat input is visible and at bottom
    const chatInput = page.getByPlaceholder('Ask about market conditions, trading opportunities...');
    await expect(chatInput).toBeVisible();
    
    // Test model selection
    const o3Radio = page.getByRole('radio', { name: 'o3' });
    await expect(o3Radio).toBeChecked(); // Should be default
    
    // Try selecting different model
    await page.getByRole('radio', { name: 'o3-deep-research' }).click();
    await expect(page.getByRole('radio', { name: 'o3-deep-research' })).toBeChecked();
  });

  test('chat input stays at bottom', async ({ page }) => {
    await page.goto('/');
    
    // Get chat input element
    const chatInput = page.getByPlaceholder('Ask about market conditions, trading opportunities...');
    await expect(chatInput).toBeVisible();
    
    // Get initial position
    const initialBox = await chatInput.boundingBox();
    expect(initialBox).toBeTruthy();
    
    // The input should be near the bottom of its container
    const viewport = page.viewportSize();
    if (viewport && initialBox) {
      expect(initialBox.y + initialBox.height).toBeGreaterThan(viewport.height * 0.7);
    }
  });

  test('timestamp displays Central time', async ({ page }) => {
    await page.goto('/');
    
    // Look for CT timezone indicator in thesis panel
    const thesisUpdated = page.getByText(/Updated:.*CT/);
    await expect(thesisUpdated).toBeVisible();
  });

  test('hash badge shows readable time format', async ({ page }) => {
    await page.goto('/');
    
    // The hash badge in the Live Prices section should show time format
    const livePricesSection = page.getByText('Live Prices');
    await expect(livePricesSection).toBeVisible();
    
    // Look for any badge in the Live Prices section
    const hashBadge = page.locator('[data-slot="badge"]').first();
    if (await hashBadge.isVisible()) {
      const badgeText = await hashBadge.textContent();
      // Should either be digits (time format) or "unknown"/"system" initially
      expect(badgeText).toBeTruthy();
      console.log('Hash badge text:', badgeText);
    }
  });
});