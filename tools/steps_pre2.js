// Unrecorded: open Home in a new tab (canvas tab keeps rendering), clear popups.
const np = await ctx.newPage();
await np.goto('https://www.topview.ai/home'); await np.waitForTimeout(4000);
await np.bringToFront();
for (let i = 0; i < 8; i++) {
  await np.waitForTimeout(1800);
  const g = np.getByRole('button', { name: 'Got it' }); if (await g.isVisible().catch(() => false)) { await g.click().catch(() => {}); continue; }
  const d = np.locator('[role=dialog]'); if (await d.count()) { const btns = d.first().locator('button'); const m = await btns.count(); let best = null; for (let k = 0; k < m; k++) { const b = await btns.nth(k).boundingBox(); if (!b) continue; const s = (b.x + b.width) - b.y * 3; if (!best || s > best.s) best = { s, k }; } if (best) await btns.nth(best.k).click().catch(() => {}); continue; }
  const cl = np.getByRole('button', { name: 'Close' }); const n = await cl.count(); for (let k = 0; k < n; k++) { if (await cl.nth(k).isVisible().catch(() => false)) await cl.nth(k).click().catch(() => {}); }
}
await np.evaluate(() => { document.title = 'PWREC'; window.scrollTo(0, 0); });
await np.mouse.move(700, 400);
return { pages: ctx.pages().map(p => p.url()) };
