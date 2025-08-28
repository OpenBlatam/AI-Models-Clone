import { test, expect } from '@playwright/test';
import { gotoOrSkip } from './utils/server';

test.describe('Accessibility basics', () => {
  test('has main landmarks if present', async ({ page }) => {
    await gotoOrSkip(page, '/');
    const main = page.locator('main');
    if (await main.count()) {
      await expect(main.first()).toBeVisible();
    } else {
      test.skip();
    }
  });

  test('all images have alt if images exist', async ({ page }) => {
    await gotoOrSkip(page, '/');
    const imgs = page.locator('img');
    const count = await imgs.count();
    if (count === 0) test.skip();
    for (let i = 0; i < count; i++) {
      await expect(imgs.nth(i)).toHaveAttribute('alt', /.+/);
    }
  });
});


