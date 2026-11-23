
  const ctx = page.context();
  const cursorScript = () => {
    if (window.__fcInstalled) return; window.__fcInstalled = true;
    const add = () => {
      if (!document.body) return requestAnimationFrame(add);
      const c = document.createElement('div');
      c.id = '__fc';
      c.style.cssText = 'position:fixed;left:0;top:0;width:30px;height:30px;z-index:2147483647;pointer-events:none;will-change:transform;transform:translate(-100px,-100px)';
      c.innerHTML = '<svg width="30" height="30" viewBox="0 0 24 24"><path d="M4 2 L4 19 L8.5 14.8 L11.6 21.6 L14.4 20.4 L11.4 13.7 L17.5 13.7 Z" fill="#fff" stroke="#111" stroke-width="1.3" stroke-linejoin="round"/></svg>';
      document.body.appendChild(c);
      const st = document.createElement('style');
      st.textContent = '@keyframes __fcr{from{transform:translate(-50%,-50%) scale(.2);opacity:.9}to{transform:translate(-50%,-50%) scale(1);opacity:0}}';
      document.head.appendChild(st);
      const pos = window.__fcPos || { x: -100, y: -100 };
      c.style.transform = `translate(${pos.x}px,${pos.y}px)`;
      addEventListener('mousemove', e => { window.__fcPos = { x: e.clientX, y: e.clientY }; c.style.transform = `translate(${e.clientX - 3}px,${e.clientY - 2}px)`; }, true);
      addEventListener('mousedown', e => {
        const r = document.createElement('div');
        r.style.cssText = `position:fixed;left:${e.clientX}px;top:${e.clientY}px;width:46px;height:46px;border-radius:50%;border:3px solid rgba(140,120,255,.95);background:rgba(140,120,255,.25);z-index:2147483646;pointer-events:none;animation:__fcr .45s ease-out forwards`;
        document.body.appendChild(r); setTimeout(() => r.remove(), 500);
      }, true);
    };
    add();
  };
  if (!(await page.evaluate(() => !!window.__fcInstalled).catch(() => false))) await ctx.addInitScript(cursorScript);
  for (const p of ctx.pages()) await p.evaluate(cursorScript).catch(() => {});

  const ease = t => t < .5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  const H = {};
  H.pos = new WeakMap();
  H.move = async (p, x, y, ms = 700) => {
    const from = H.pos.get(p) || { x: 768, y: 430 };
    const n = Math.max(8, Math.round(ms / 16));
    for (let i = 1; i <= n; i++) { const k = ease(i / n); await p.mouse.move(from.x + (x - from.x) * k, from.y + (y - from.y) * k); await p.waitForTimeout(16); }
    H.pos.set(p, { x, y });
  };
  H.center = async (loc) => { const b = await loc.boundingBox(); if (!b) throw new Error('no box'); return [b.x + b.width / 2, b.y + b.height / 2]; };
  H.click = async (p, x, y, { ms = 700, pre = 300, post = 500, dbl = false } = {}) => {
    await H.move(p, x, y, ms); await p.waitForTimeout(pre);
    await p.mouse.down(); await p.waitForTimeout(80); await p.mouse.up();
    if (dbl) { await p.waitForTimeout(60); await p.mouse.down({ clickCount: 2 }); await p.waitForTimeout(60); await p.mouse.up({ clickCount: 2 }); }
    await p.waitForTimeout(post);
  };
  H.clickLoc = async (p, loc, opts) => { const [x, y] = await H.center(loc); await H.click(p, x, y, opts); };
  H.type = async (p, text, delay = 28) => { await p.keyboard.type(text, { delay }); };
  H.fullscreen = async (p) => {
    const s = await p.context().newCDPSession(p);
    const { windowId } = await s.send('Browser.getWindowForTarget');
    await s.send('Browser.setWindowBounds', { windowId, bounds: { windowState: 'normal' } }).catch(() => {});
    await s.send('Browser.setWindowBounds', { windowId, bounds: { windowState: 'fullscreen' } });
    await p.bringToFront(); await p.waitForTimeout(800);
    return p.evaluate(() => [innerWidth, innerHeight, devicePixelRatio]);
  };
  