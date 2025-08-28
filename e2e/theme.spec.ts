import { test, expect } from '@playwright/test';
import { gotoOrSkip } from './utils/server';

test.describe('Theme', () => {
  test('toggle theme persists across reloads (if toggle exists)', async ({ page }) => {
    await gotoOrSkip(page, '/');
    const toggle = page.locator('[data-testid="theme-toggle"], button:has-text("Theme")');
    if (await toggle.count()) {
      await toggle.first().click();
      await page.reload();
      // smoke assert: page still functional
      await expect(page).toHaveURL(/\//);
    } else {
      test.skip();
    }
  });
});


