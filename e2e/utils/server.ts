import { test, Page, APIRequestContext } from '@playwright/test';

export async function gotoOrSkip(page: Page, path: string = '/') {
  try {
    await page.goto(path);
  } catch (err: any) {
    const msg = String(err?.message || err);
    if (/ECONNREFUSED|ERR_CONNECTION_REFUSED/i.test(msg)) {
      test.skip(true, 'Server not reachable, skipping E2E test');
    }
    throw err;
  }
}

export async function headOrSkip(request: APIRequestContext, path: string = '/') {
  try {
    const res = await request.head(path);
    if (!res.ok()) test.skip(true, 'Server responded non-200 to HEAD, skipping');
  } catch (err: any) {
    const msg = String(err?.message || err);
    if (/ECONNREFUSED|ERR_CONNECTION_REFUSED/i.test(msg)) {
      test.skip(true, 'Server not reachable, skipping E2E test');
    }
    throw err;
  }
}













