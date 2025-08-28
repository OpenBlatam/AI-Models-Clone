import { test, expect } from '@playwright/test';
import { gotoOrSkip } from './utils/server';

test.describe('Navigation', () => {
  test('root loads and shows home UI', async ({ page }) => {
    await gotoOrSkip(page, '/');
    await expect(page).toHaveTitle(/Blatam|Expo|React/i);
  });
});


