// RECORDED take 1: Home -> Canvas -> new project -> Video node -> T1 settings -> prompt -> Generate.
const P = 'A cinematic slow-motion shot of a Japanese tea master pouring matcha in a dimly lit room, steam rising, shallow depth of field, warm golden light from a paper lantern, 4K film grain.';
const T = []; const t0 = Date.now(); const mark = (s) => T.push([((Date.now() - t0) / 1000).toFixed(2), s]);
const topmost = async (loc) => { const n = await loc.count(); let best = null; for (let i = 0; i < n; i++) { const b = await loc.nth(i).boundingBox(); if (b && b.width > 0 && (!best || b.y < best.b.y)) best = { i, b }; } return best ? loc.nth(best.i) : null; };
const lowest = async (loc) => { const n = await loc.count(); let best = null; for (let i = 0; i < n; i++) { const b = await loc.nth(i).boundingBox(); if (b && b.width > 0 && (!best || b.y > best.b.y)) best = { i, b }; } return best ? loc.nth(best.i) : null; };
H.pos.set(page, { x: 955, y: 295 });
mark('home'); await page.waitForTimeout(1500);
await H.move(page, 700, 180, 900); await page.waitForTimeout(400);
mark('click canvas'); await H.clickLoc(page, page.getByText('Canvas', { exact: true }).first(), { ms: 900, post: 2500 });
// smooth scroll down to My Projects
const cnp = page.getByText('Create New Project').first(); await cnp.waitFor({ timeout: 15000 });
await H.move(page, 880, 450, 500);
for (let i = 0; i < 40; i++) { const b = await cnp.boundingBox(); if (!b || b.y < 560) break; await page.mouse.wheel(0, 60); await page.waitForTimeout(25); }
await page.waitForTimeout(700);
mark('create project'); await H.clickLoc(page, cnp, { ms: 800, post: 500 });
await page.waitForURL(/canvas\/[0-9a-f]{8}/, { timeout: 20000 });
await page.getByText('Setting up your workspace').waitFor({ state: 'hidden', timeout: 30000 }).catch(() => {});
await page.waitForTimeout(2500);
H.pos.set(page, H.pos.get(page) || { x: 768, y: 430 });
const fam = page.getByText('Already familiar'); if (await fam.isVisible().catch(() => false)) { await H.clickLoc(page, fam, { ms: 600, post: 600 }); }
if (await page.getByText('What would you like to create?').isVisible().catch(() => false)) { await H.click(page, 1509, 72, { ms: 700, post: 900 }); }
await page.waitForTimeout(600);
mark('dblclick canvas'); await H.click(page, 560, 330, { ms: 800, pre: 400, post: 900, dbl: true });
const vid = page.getByText('Video', { exact: true }); const vItem = await topmost(vid);
await H.move(page, (await H.center(vItem))[0] - 10, (await H.center(vItem))[1] - 30, 500);
mark('pick video'); await H.clickLoc(page, vItem, { ms: 450, post: 1500 });
// settings chip at bottom of the prompt panel
const chip = await lowest(page.getByText(/Topview T1/));
mark('open settings'); await H.clickLoc(page, chip, { ms: 800, post: 900 });
const modelDd = await topmost(page.getByText('Topview T1', { exact: true }));
mark('model dropdown'); await H.clickLoc(page, modelDd, { ms: 600, post: 1000 });
await page.waitForTimeout(400); await page.keyboard.press('Escape').catch(() => {}); await page.waitForTimeout(300);
if (!(await page.getByText('Aspect Ratio').isVisible().catch(() => false))) { await H.clickLoc(page, await lowest(page.getByText(/Topview T1/)), { ms: 500, post: 800 }); }
// resolution
const resLabel = page.getByText('Resolution', { exact: true }); const rb = await resLabel.boundingBox();
mark('resolution'); await H.click(page, rb.x + 100, rb.y + 39, { ms: 600, post: 800 });
mark('1080p'); await H.clickLoc(page, await lowest(page.getByText('1080p', { exact: true })), { ms: 500, post: 700 });
// duration slider -> 10s
const si = await page.evaluate(() => { const s = document.querySelector('[role=slider]'); let t = s.parentElement; while (t && t.getBoundingClientRect().width < 300) t = t.parentElement; const r = t.getBoundingClientRect(), h = s.getBoundingClientRect(); return { v: +s.getAttribute('aria-valuenow'), min: +s.getAttribute('aria-valuemin'), max: +s.getAttribute('aria-valuemax'), hx: h.x + h.width / 2, hy: h.y + h.height / 2, l: r.left, w: r.width }; });
const tx = si.l + (10 - si.min) / (si.max - si.min) * si.w;
mark('duration'); await H.move(page, si.hx, si.hy, 600); await page.waitForTimeout(250); await page.mouse.down();
if (Math.abs(si.hx - tx) < 30) { await H.move(page, si.hx + 120, si.hy, 450); }
await H.move(page, tx, si.hy, 700); await page.mouse.up(); await page.waitForTimeout(400);
for (let k = 0; k < 30; k++) { const v = await page.evaluate(() => +document.querySelector('[role=slider]').getAttribute('aria-valuenow')); if (v === 10) break; await page.keyboard.press(v > 10 ? 'ArrowLeft' : 'ArrowRight'); }
await page.waitForTimeout(500);
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
