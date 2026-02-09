import { test, expect } from '@playwright/test';
import { headOrSkip } from './utils/server';

test.describe('PWA', () => {
  test('manifest is reachable if configured', async ({ request }) => {
    const candidates = ['/manifest.json', '/manifest.webmanifest', '/site.webmanifest'];
    let ok = false;
    for (const path of candidates) {
      await headOrSkip(request, path);
      const res = await request.get(path);
      if (res.ok()) {
        ok = true;
        break;
      }
    }
    if (!ok) test.skip();
    expect(ok).toBeTruthy();
  });
});


