const T = []; const t0 = Date.now(); const mark = (s) => T.push([((Date.now() - t0) / 1000).toFixed(2), s]);
H.pos.set(page, { x: 1250, y: 720 });
await page.waitForTimeout(1200);
mark('to play'); await H.move(page, 900, 520, 900); await page.waitForTimeout(300);
mark('click play'); await H.click(page, 768, 432, { ms: 700, post: 400 });
await H.move(page, 900, 640, 900); await page.waitForTimeout(4200);
mark('select node'); await H.click(page, 985, 315, { ms: 800, post: 900 });
const dlP = page.waitForEvent('download', { timeout: 20000 }).catch(() => null);
const tb = await page.evaluate(() => { const t = [...document.querySelectorAll('*')].find(e => e.children.length === 0 && e.textContent.trim() === 'Add to Timeline'); return t ? t.getBoundingClientRect().y : null; });
mark('toolbar y=' + tb);
mark('hover download'); await H.move(page, 1079, 246, 1000); await page.waitForTimeout(900);
mark('click download'); await H.click(page, 1079, 246, { ms: 80, pre: 100, post: 600 });
const dl = await dlP; let saved = null;
if (dl) { saved = 'C:/Users/deysu/Downloads/New folder/drive-download-20261018T195157Z-1-001/.claude/worktrees/video-editing-test-019d4d/marcus-ai-test/raw/t1_matcha_' + dl.suggestedFilename(); await dl.saveAs(saved); }
await page.waitForTimeout(800);
mark('hover regenerate'); await H.move(page, 278, 246, 1300); await page.waitForTimeout(2200);
mark('away'); await H.move(page, 640, 650, 900); await page.waitForTimeout(1500);
mark('end');
return { T, saved };
