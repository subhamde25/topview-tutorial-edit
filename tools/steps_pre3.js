await page.bringToFront(); await H.fullscreen(page);
await page.mouse.click(300, 720); await page.keyboard.press('Escape'); await page.waitForTimeout(800);
if (await page.getByText('What would you like to create?').isVisible().catch(() => false)) await page.mouse.click(1509, 72);
await page.waitForTimeout(600); await page.mouse.move(1250, 720);
await page.evaluate(() => { document.title = 'PWREC'; });
const sel = await page.getByText('Add to Timeline').isVisible().catch(() => false);
return { sel, vp: await page.evaluate(() => [innerWidth, innerHeight]) };
