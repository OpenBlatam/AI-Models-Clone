import { test, expect } from '@playwright/test';
import { gotoOrSkip } from './utils/server';

test.describe('Locale', () => {
  test('language switcher toggles UI language if present', async ({ page }) => {
    await gotoOrSkip(page, '/');
    const toggle = page.locator('[data-testid="locale-switcher"], [aria-label*="language" i]');
    if (await toggle.count() === 0) test.skip();
    const before = await page.textContent('body');
    await toggle.first().click();
    await page.waitForTimeout(300);
    const after = await page.textContent('body');
    expect(before).not.toBe(after);
  });
});


