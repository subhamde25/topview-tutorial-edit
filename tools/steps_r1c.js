// RECORDED take 1: Home -> Canvas -> new project -> Video node -> T1 settings -> prompt -> Generate.
const P = 'A cinematic slow-motion shot of a Japanese tea master pouring matcha in a dimly lit room, steam rising, shallow depth of field, warm golden light from a paper lantern, 4K film grain.';
const T = []; const t0 = Date.now(); const mark = (s) => T.push([((Date.now() - t0) / 1000).toFixed(2), s]);
const topmost = async (loc) => { const n = await loc.count(); let best = null; for (let i = 0; i < n; i++) { const b = await loc.nth(i).boundingBox(); if (b && b.width > 0 && (!best || b.y < best.b.y)) best = { i, b }; } return best ? loc.nth(best.i) : null; };
const lowest = async (loc) => { const n = await loc.count(); let best = null; for (let i = 0; i < n; i++) { const b = await loc.nth(i).boundingBox(); if (b && b.width > 0 && (!best || b.y > best.b.y)) best = { i, b }; } return best ? loc.nth(best.i) : null; };
const fp = await page.evaluate(() => window.__fcPos || { x: 768, y: 430 }); H.pos.set(page, fp);
await page.waitForTimeout(1000);
const rng = page.locator('input[type=range]').first();
const si = await rng.evaluate(s => { const r = s.getBoundingClientRect(); return { v: +s.value, max: +s.max, x: r.x, y: r.y + r.height / 2, w: r.width }; });
const xAt = v => si.x + 9 + v / si.max * (si.w - 18);
mark('duration'); await H.move(page, xAt(si.v), si.y, 700); await page.waitForTimeout(300); await page.mouse.down();
await H.move(page, xAt(6), si.y, 900); await page.mouse.up(); await page.waitForTimeout(300);
for (let k = 0; k < 30; k++) { const v = await rng.evaluate(s => +s.value); if (v === 6) break; await rng.focus(); await page.keyboard.press(v > 6 ? 'ArrowLeft' : 'ArrowRight'); }
await page.waitForTimeout(600);
mark('16:9'); await H.clickLoc(page, await topmost(page.getByText('16:9', { exact: true })), { ms: 700, post: 900 });
// prompt
const box = page.locator('textarea, [contenteditable=true]').last(); const bb = await box.boundingBox();
mark('click prompt'); await H.click(page, bb.x + 120, bb.y + 20, { ms: 800, post: 500 });
if (await page.getByText('Aspect Ratio').isVisible().catch(() => false)) { await H.click(page, bb.x + 120, bb.y + 20, { ms: 200, post: 400 }); }
mark('type'); await H.type(page, P, 22);
await page.waitForTimeout(900);
const gen = page.getByRole('button', { name: /Generate/ }).last();
mark('hover generate'); const [gx, gy] = await H.center(gen); await H.move(page, gx, gy, 900); await page.waitForTimeout(1600);
const genText = await gen.innerText().catch(() => '');
const chipNow = await (await lowest(page.getByText(/Topview T1/))).innerText().catch(() => '');
const okSet = /16:9/.test(chipNow) && /1080p/.test(chipNow) && /10s/.test(chipNow) && /22/.test(genText);
mark('settings ' + chipNow.replace(/\s+/g, ' ') + ' | ' + genText.replace(/\s+/g, ' ') + ' ok=' + okSet);
if (!okSet) return { T, aborted: true };
mark('click generate'); await H.click(page, gx, gy, { ms: 100, pre: 100, post: 600 });
await H.move(page, gx - 300, gy - 260, 1200); await page.waitForTimeout(5000);
mark('end');
return { T, url: page.url() };
