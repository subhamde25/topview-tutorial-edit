await page.bringToFront(); await H.fullscreen(page);
await page.mouse.click(1503, 28); await page.waitForTimeout(1200);
await page.evaluate(() => { [...document.querySelectorAll('*')].filter(e => e.scrollHeight > e.clientHeight + 50 && getComputedStyle(e).overflowY !== 'visible').forEach(e => e.scrollTop = e.scrollHeight); document.title = 'PWREC'; });
await page.waitForTimeout(800); await page.mouse.move(1300, 420);
const f = await page.evaluate(() => { const e = [...document.querySelectorAll('*')].find(x => x.children.length === 0 && /vid_20261122_113703_01/.test(x.textContent)); if (!e) return null; const r = e.getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; });
return { f, vids: await page.locator('video').count() };
