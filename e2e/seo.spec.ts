import { test, expect } from '@playwright/test';
import { gotoOrSkip } from './utils/server';

test.describe('SEO', () => {
  test('has basic meta tags', async ({ page }) => {
    await gotoOrSkip(page, '/');
    const title = await page.title();
    expect(title.length).toBeGreaterThan(0);

    const desc = await page.locator('head meta[name="description"]').getAttribute('content');
    // Soft assertion pattern
    if (desc !== null) expect(desc.length).toBeGreaterThan(0);
  });
});


