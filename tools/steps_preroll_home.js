// Unrecorded: land on Home, clear every popup, park the cursor.
await page.goto('https://www.topview.ai/home'); await page.waitForTimeout(3500);
await H.fullscreen(page);
for (let i = 0; i < 3; i++) {
  for (const name of ['Got it']) { const b = page.getByRole('button', { name }); if (await b.isVisible().catch(() => false)) await b.click().catch(() => {}); }
  const dlgClose = page.locator('[role=dialog] button').filter({ hasText: '' });
  const x = page.locator('[role=dialog] button:has(svg)').first(); if (await x.isVisible().catch(() => false)) await x.click().catch(() => {});
  const closes = page.getByRole('button', { name: 'Close' }); const n = await closes.count();
  for (let k = 0; k < n; k++) { const c = closes.nth(k); if (await c.isVisible().catch(() => false)) await c.click().catch(() => {}); }
  await page.keyboard.press('Escape'); await page.waitForTimeout(700);
}
await page.evaluate(() => { document.title = 'PWREC'; window.scrollTo(0, 0); });
await H.move(page, 820, 470, 300);
const vis = await page.locator('[role=dialog]').count();
return { vp: await page.evaluate(() => [innerWidth, innerHeight]), dialogs: vis };
