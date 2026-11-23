await page.goto('https://www.topview.ai/home'); await page.waitForTimeout(2500);
const vp = await H.fullscreen(page);
await page.evaluate(() => { document.title = 'PWREC Topview'; });
await H.move(page, 400, 300, 600); await H.move(page, 900, 500, 600);
return vp;
