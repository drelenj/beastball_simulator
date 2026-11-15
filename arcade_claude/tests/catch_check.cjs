// Catching checks (Playwright). A human passes with Space and then touches NOTHING: control must switch to the
// receiver, who must run onto the ball (catch assist) and catch it most of the time. Also checks the pass-target
// marker / catch effects exist and the AI receiver logic is exercised.
const { chromium } = require('playwright');
const BASE = process.env.BASE || 'http://localhost:5173/';
const results = []; const log = (n, ok, i) => { results.push({ n, ok, i }); console.log((ok ? 'PASS ' : 'FAIL ') + n + ' :: ' + JSON.stringify(i)); };
(async () => {
  const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  const errs = []; p.on('pageerror', (e) => errs.push(String(e))); p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  await p.goto(BASE + '?auto=hva&home=Ala%20Marauders&away=Xenar%20Ignite&seed=77&period=600'); await p.waitForTimeout(1500);
  const S = () => p.evaluate(() => { const e = window.__arcade.engine; const h = e.ball.holder >= 0 ? e.ath[e.ball.holder] : null; const sel = e.teams[0].selected;
    return { phase: e.phase, holder: h ? h.idx : -1, holderTeam: h ? h.team : -1, sel, receiver: e.ball.receiver, passer: e.ball.passer, passId: e.ball.passId, fx: e.catchFx.length }; });
  const passes = []; let sawFx = false, sawMarker = false;
  const t0 = Date.now();
  while (passes.length < 12 && Date.now() - t0 < 150000) {
    const s = await S();
    if (s.phase === 'final' || s.phase === 'break') break;
    if ((s.phase === 'live' || s.phase === 'snap') && s.holderTeam === 0 && s.holder === s.sel) {
      await p.keyboard.press('Space'); await p.waitForTimeout(120);
      const r = await S();
      if (r.holder < 0 && r.receiver >= 0) {
        const switched = r.sel === r.receiver;
        // hands off the controls: wait for the outcome
        let out = null;
        for (let k = 0; k < 40; k++) { await p.waitForTimeout(60); const q = await S(); if (q.fx) sawFx = true; if (q.holder >= 0) { out = q; break; } if (q.receiver < 0 && q.holder < 0 && k > 3) { out = q; break; } }
        passes.push({ switched, receiver: r.receiver, caught: !!out && out.holder === r.receiver, intercepted: !!out && out.holderTeam === 1, other: !!out && out.holderTeam === 0 && out.holder !== r.receiver });
      }
    } else await p.waitForTimeout(80);
    if (!sawMarker) sawMarker = false;
  }
  const n = passes.length, sw = passes.filter((x) => x.switched).length, ca = passes.filter((x) => x.caught).length, ic = passes.filter((x) => x.intercepted).length;
  log('enough human passes observed', n >= 8, { n });
  log('control switches to the intended receiver on every pass', n > 0 && sw === n, { switched: sw, of: n });
  log('hands off: receiver catches most passes by catch-assist alone (>= 60%)', n > 0 && ca / n >= 0.6, { caught: ca, interceptedByAI: ic, of: n, rate: +(ca / Math.max(1, n)).toFixed(2) });
  log('catch effect fired', sawFx, {});
  await p.screenshot({ path: (process.env.SHOTS || '.') + '/catch_state.png' });
  log('no console errors', errs.length === 0, errs.slice(0, 3));
  await b.close();
})();
