const T = []; const t0 = Date.now(); const mark = (s) => T.push([((Date.now() - t0) / 1000).toFixed(2), s]);
const URL = 'https://www.drbronner.com/products/peppermint-pure-castile-liquid-soap';
H.pos.set(page, { x: 700, y: 400 });
mark('home'); await page.waitForTimeout(1200);
const am = page.getByText('AI Marketer', { exact: true }).first(); const [ax, ay] = await H.center(am);
mark('click ai marketer');
const popP = ctx.waitForEvent('page', { timeout: 8000 }).catch(() => null);
await H.click(page, ax, ay, { ms: 1000, post: 300 });
let mp = await popP; if (!mp) mp = page;
await mp.bringToFront(); await mp.waitForLoadState('domcontentloaded'); await mp.waitForTimeout(3500);
H.pos.set(mp, { x: ax, y: ay }); await mp.mouse.move(ax, ay);
await H.move(mp, 760, 300, 900); await mp.waitForTimeout(800);
mark('url to video'); await H.clickLoc(mp, mp.getByText('URL to Video').first(), { ms: 800, post: 1800 });
const urlIn = mp.getByPlaceholder(/product page URL/i);
mark('url field'); await H.clickLoc(mp, urlIn, { ms: 800, post: 300 }); await H.type(mp, URL, 18); await mp.waitForTimeout(500);
const aud = mp.getByPlaceholder(/Who should this ad speak to/i);
mark('audience'); await H.clickLoc(mp, aud, { ms: 700, post: 300 }); await H.type(mp, 'Eco-conscious adults who love natural, plant-based soap', 20); await mp.waitForTimeout(400);
const ksp = mp.getByPlaceholder(/What benefit should stand out/i);
mark('selling point'); await H.clickLoc(mp, ksp, { ms: 700, post: 300 }); await H.type(mp, 'Organic, 18-in-1 uses, refreshing peppermint', 20); await mp.waitForTimeout(500);
mark('natural lifestyle'); await H.clickLoc(mp, mp.getByText('Natural lifestyle', { exact: true }).first(), { ms: 900, post: 800 });
// scroll the settings column to duration + aspect
const [nx, ny] = await H.center(mp.getByText('Natural lifestyle', { exact: true }).first());
for (let i = 0; i < 10; i++) { await mp.mouse.wheel(0, 50); await mp.waitForTimeout(30); }
await mp.waitForTimeout(700);
const rng = mp.locator('[role=dialog] input[type=range], input[type=range]').last();
let durInfo = 'none';
if (await rng.count()) {
  const si = await rng.evaluate(s => { const r = s.getBoundingClientRect(); return { v: +s.value, min: +s.min, max: +s.max, x: r.x, y: r.y + r.height / 2, w: r.width }; });
  const target = si.min + Math.round((8 - 4) / 26 * (si.max - si.min));
  const xAt = v => si.x + 9 + (v - si.min) / (si.max - si.min) * (si.w - 18);
  mark('duration'); await H.move(mp, xAt(si.v), si.y, 800); await mp.waitForTimeout(250); await mp.mouse.down(); await H.move(mp, xAt(target), si.y, 800); await mp.mouse.up(); await mp.waitForTimeout(500);
  durInfo = JSON.stringify({ si, target, now: await rng.evaluate(s => s.value) });
}
const a169 = mp.getByText('16:9', { exact: true }).last();
mark('16:9'); await H.clickLoc(mp, a169, { ms: 800, post: 800 });
const durLabel = await mp.evaluate(() => [...document.querySelectorAll('*')].filter(e => e.children.length === 0 && /^(Auto|\d+s)$/.test(e.textContent.trim())).map(e => e.textContent.trim()).join(','));
const start = mp.getByText('Start creating').first(); const [sx, sy] = await H.center(start);
mark('hover start'); await H.move(mp, sx, sy, 900); await mp.waitForTimeout(1200);
const enabled = await start.evaluate(e => { const b = e.closest('button'); return b ? !b.disabled : true; });
mark('start enabled=' + enabled + ' dur=' + durLabel);
return { T, durInfo, durLabel, enabled, url: mp.url() };
