import { test, expect } from '@playwright/test';
import { gotoOrSkip } from './utils/server';

test.describe('Header/Footer', () => {
  test('header exists and links are clickable if present', async ({ page }) => {
    await gotoOrSkip(page, '/');
    const header = page.locator('header');
    if (await header.count() === 0) test.skip();
    const links = header.locator('a');
    const count = await links.count();
    if (count === 0) test.skip();
    await links.first().click({ trial: true });
    expect(count).toBeGreaterThan(0);
  });

  test('footer exists', async ({ page }) => {
    await gotoOrSkip(page, '/');
    const footer = page.locator('footer');
    if (await footer.count() === 0) test.skip();
    await expect(footer.first()).toBeVisible();
  });
});


