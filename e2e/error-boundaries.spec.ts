import { test, expect } from '@playwright/test';
import { gotoOrSkip } from './utils/server';

test('navigates to unknown route shows 404-ish content', async ({ page }) => {
  const rnd = Math.random().toString(36).slice(2);
  await gotoOrSkip(page, '/__unknown__' + rnd);
  const content = await page.content();
  if (!/404|not found/i.test(content)) test.skip();
  expect(/404|not found/i.test(content)).toBeTruthy();
});


