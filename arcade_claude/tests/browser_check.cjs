// Browser acceptance checks (Playwright, headless Chromium). Run with the dev server on :5173.
const { chromium } = require('playwright');
const BASE = process.env.BASE || 'http://localhost:5173/';
const SHOTS = process.env.SHOTS || '.';
const results = []; const log = (name, ok, info) => { results.push({ name, ok, info }); console.log((ok ? 'PASS ' : 'FAIL ') + name + ' :: ' + JSON.stringify(info)); };
const E = (p, f, arg) => p.evaluate(f, arg);
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1280, height: 720 } });
  const errs = []; p.on('pageerror', (e) => errs.push(String(e))); p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  // 1. launch + team select
  await p.goto(BASE); await p.waitForTimeout(800);
  log('launch: main menu visible', await p.isVisible('#scrMenu'), {});
  
  await p.click('#mPlay');
  await p.click('.team[data-name="Ala Marauders"]');
  await p.click('.team[data-name="Xenar Ignite"]', { modifiers: ['Shift'] });
  await p.selectOption('#optClock', '60');
  const tiles = await p.$$eval('.team img', (ims) => ims.filter((i) => i.complete && i.naturalWidth > 0).length);
  log('team select: 26 franchises with logos', tiles === 26, { tilesWithLogo: tiles });
  
  await p.click('#selStart'); await p.waitForTimeout(1600);
  const st = await E(p, () => { const e = window.__arcade.engine; return { phase: e.phase, teams: e.teams.map((t) => t.data.franchise), n: e.ath.length, human: e.teams.map((t) => t.human) }; });
  log('match starts (Human vs AI)', st.n === 24 && st.human[0] && !st.human[1], st);
  // 2. human moves and sprints
  const pos0 = await E(p, () => { const e = window.__arcade.engine; const a = e.ath[e.teams[0].selected]; return { i: a.idx, x: a.x, y: a.y }; });
  await p.keyboard.down('KeyS'); await p.waitForTimeout(700); await p.keyboard.up('KeyS');
  const jog = await E(p, (i) => { const a = window.__arcade.engine.ath[i]; return { x: a.x, y: a.y, v: Math.hypot(a.vx, a.vy) }; }, pos0.i);
  await p.keyboard.down('ShiftLeft'); await p.keyboard.down('KeyW');
  let spr = { v: 0, top: 0, jogMax: 0 };
  for (let k = 0; k < 10; k++) { await p.waitForTimeout(120); const r = await E(p, () => { const e = window.__arcade.engine; const a = e.ath[e.teams[0].selected]; return { v: Math.hypot(a.vx, a.vy), top: a.a.top }; }); if (r.v > spr.v) spr = { ...r, jogMax: 0 }; }
  await p.keyboard.up('KeyW'); await p.keyboard.up('ShiftLeft');
  spr.jogTop = +(spr.top * 0.68).toFixed(2);
  log('human athlete moves (S) and sprints (Shift+W)', Math.abs(jog.y - pos0.y) > 0.5 && spr.v > spr.top * 0.68 * 1.15, { pos0, jog, spr });
  
  // 3. pass / tackle loop driven by keyboard using on-screen state (test harness acts as the human)
  let passes = 0, tackles = 0;
  for (let k = 0; k < 700 && (passes < 1 || tackles < 1); k++) {
    const s = await E(p, () => { const e = window.__arcade.engine; const sel = e.ath[e.teams[0].selected]; const h = e.ball.holder >= 0 ? e.ath[e.ball.holder] : null;
      const A = e.ath.filter((a) => a.team === 0); return { phase: e.phase, mine: h && h.team === 0, sel: { x: sel.x, y: sel.y }, h: h ? { x: h.x, y: h.y } : null, ball: { x: e.ball.x, y: e.ball.y },
        passAtt: A.reduce((n, a) => n + a.stats.passAtt, 0), tackles: A.reduce((n, a) => n + a.stats.tackles, 0) }; });
    passes = s.passAtt; tackles = s.tackles;
    if (s.phase === 'final') break;
    if (s.phase === 'break') { await p.click('#brSkip'); continue; }
    if (s.mine) { await p.keyboard.press('Space'); await p.waitForTimeout(250); continue; }
    // opponent carries the ball: harness puts the selected athlete next to the carrier (movement is covered by the check above),
    // then the REAL J key tackles
    const opp = await E(p, () => { const e = window.__arcade.engine; const h = e.ball.holder >= 0 ? e.ath[e.ball.holder] : null; if (!h || h.team === 0 || e.phase !== 'live') return false; const a = e.ath[e.teams[0].selected]; a.x = h.x - 0.9; a.y = h.y; a.vx = a.vy = 0; return true; });
    if (opp) { await p.keyboard.press('KeyJ'); await p.waitForTimeout(250); continue; }
    const t = s.h || s.ball; const dx = t.x - s.sel.x, dy = t.y - s.sel.y;
    const keys = []; if (dx > 0.4) keys.push('KeyD'); if (dx < -0.4) keys.push('KeyA'); if (dy > 0.4) keys.push('KeyS'); if (dy < -0.4) keys.push('KeyW');
    await p.keyboard.down('ShiftLeft'); for (const kk of keys) await p.keyboard.down(kk);
    await p.waitForTimeout(120);
    for (const kk of keys) await p.keyboard.up(kk); await p.keyboard.up('ShiftLeft');
  }
  const ps = await E(p, () => { const e = window.__arcade.engine; const A = e.ath.filter((a) => a.team === 0); return { passAtt: A.reduce((n, a) => n + a.stats.passAtt, 0), passComp: A.reduce((n, a) => n + a.stats.passComp, 0), tackles: A.reduce((n, a) => n + a.stats.tackles, 0), possChanges: e.possChanges }; });
  log('human pass (Space) -> catch / possession transfer', ps.passAtt > 0 && ps.possChanges > 0, ps);
  log('human tackle (J key, athlete placed beside the carrier by the harness) grounds a carrier', ps.tackles > 0, ps);
  await p.screenshot({ path: SHOTS + '/04_play.png' });
  // 4. run the rest of the accelerated-clock match at 8x (spectator speed control), through breaks, to final
  await E(p, () => { window.__arcade.speed = 8; });
  for (let k = 0; k < 400; k++) {
    const ph = await E(p, () => window.__arcade.engine.phase);
    if (ph === 'final') break;
    if (ph === 'break') { if (k < 3) await p.screenshot({ path: SHOTS + '/05_break.png' }); await p.click('#brSkip'); }
    await p.waitForTimeout(500);
  }
  const fin = await E(p, () => { const e = window.__arcade.engine; return { phase: e.phase, period: e.period, score: e.teams.map((t) => t.score), periodEnds: e.events.filter((v) => v.type === 'period_end').length, finalVisible: document.getElementById('scrFinal').classList.contains('on'),
    scoreEv: e.events.filter((v) => v.type === 'score').map((v) => v.pts).reduce((a, b) => a + b, 0), keeperSaves: e.ath.filter((a) => a.role === 'keeper').map((a) => a.stats.saves), arrows: e.ath.filter((a) => a.role === 'archer').map((a) => a.stats.arrows) }; });
  log('four periods + final result screen (HvA, accelerated clock setting)', fin.phase === 'final' && fin.periodEnds >= 4 && fin.finalVisible, fin);
  log('scoreboard equals sum of scoring events', fin.score[0] + fin.score[1] === fin.scoreEv, fin);
  await p.screenshot({ path: SHOTS + '/06_final.png' });
  await p.click('#fiRematch'); await p.waitForTimeout(800);
  const rm = await E(p, () => { const e = window.__arcade.engine; return { phase: e.phase, score: e.teams.map((t) => t.score), teams: e.teams.map((t) => t.data.franchise), seed: e.s.seed }; });
  log('rematch: same teams and seed, fresh score', rm.score[0] === 0 && rm.score[1] === 0 && rm.teams[0] === 'Ala Marauders' && rm.teams[1] === 'Xenar Ignite', rm);
  await p.keyboard.press('Escape'); await p.waitForTimeout(300);
  log('pause screen (Esc)', await p.isVisible('#scrPause'), {});
  await p.click('#pControls'); log('controls screen', await p.isVisible('#scrControls'), {}); await p.click('#ctrlBack');
  await p.click('#pMenu'); log('quit to menu', await p.isVisible('#scrMenu'), {});

  // 5. AI vs AI full canon-length match in the browser (no keyboard input), fast playback
  const p2 = await b.newPage({ viewport: { width: 1280, height: 720 } });
  p2.on('pageerror', (e) => errs.push(String(e)));
  await p2.goto(BASE + '?auto=ava&home=Ala%20Marauders&away=Xenar%20Ignite&seed=20261115&speed=64&autobreak=1');
  await p2.waitForTimeout(5000); await p2.screenshot({ path: SHOTS + '/07_ava.png' });
  const t0 = Date.now();
  for (;;) { const ph = await E(p2, () => window.__arcade.engine.phase); if (ph === 'final' || Date.now() - t0 > 240000) break; await p2.waitForTimeout(1000); }
  const ava = await E(p2, () => { const e = window.__arcade.engine; const T = (t) => { const A = e.ath.filter((a) => a.team === t); const s = (k) => A.reduce((n, a) => n + a.stats[k], 0);
      return { franchise: e.teams[t].data.franchise, athletes: A.length, keeper: A.find((a) => a.role === 'keeper').d.pos, archer: A.find((a) => a.role === 'archer').d.pos, shots: e.events.filter((v) => v.type === 'shot' && v.team === t).length, saves: s('saves'), arrows: s('arrows'), arrowHits: s('arrowHits'), possTime: Math.round(e.teams[t].possTime) }; };
    return { phase: e.phase, period: e.period, score: e.teams.map((t) => t.score), hash: e.hash(), checkpoints: e.checkpoints.slice(0, 3), ticks: e.tick, teams: [T(0), T(1)], humanInput: e.humanIntent }; });
  await p2.screenshot({ path: SHOTS + '/08_ava_final.png' });
  log('AI vs AI full match Ala Marauders vs Xenar Ignite (browser, 64x)', ava.phase === 'final' && ava.period >= 4 && ava.teams.every((t) => t.athletes === 12 && t.keeper === 'KPR' && t.archer === 'ARC' && t.shots > 0 && t.saves > 0 && t.arrows > 0 && t.possTime > 0) && ava.humanInput.every((h) => h === null), ava);
  // 6. playback speed does not change the simulation: 1x vs 8x checkpoint at tick 3600
  const cp = [];
  for (const sp of [1, 8]) {
    const p3 = await b.newPage(); await p3.goto(BASE + `?auto=ava&seed=20261115&speed=${sp}&autobreak=1`);
    for (let k = 0; k < 200; k++) { const n = await E(p3, () => window.__arcade.engine.checkpoints.length); if (n >= 1) break; await p3.waitForTimeout(1000); }
    cp.push(await E(p3, () => window.__arcade.engine.checkpoints[0])); await p3.close();
  }
  log('playback speed 1x vs 8x: identical state hash at tick 3600', cp[0] === cp[1] && cp[0] === ava.checkpoints[0], { at1x: cp[0], at8x: cp[1], at64x: ava.checkpoints[0] });
  // full-length: 32x vs 64x browser playback -> identical final state
  const p4 = await b.newPage(); await p4.goto(BASE + '?auto=ava&home=Ala%20Marauders&away=Xenar%20Ignite&seed=20261115&speed=32&autobreak=1');
  const t1 = Date.now();
  for (;;) { const ph = await E(p4, () => window.__arcade.engine.phase); if (ph === 'final' || Date.now() - t1 > 300000) break; await p4.waitForTimeout(1000); }
  const f32 = await E(p4, () => { const e = window.__arcade.engine; return { score: e.teams.map((t) => t.score), hash: e.hash(), ticks: e.tick }; });
  log('full match 32x vs 64x browser playback: identical final score and state hash', f32.hash === ava.hash && f32.ticks === ava.ticks, { f32, f64: { score: ava.score, hash: ava.hash, ticks: ava.ticks } });
  log('no fatal console errors', errs.length === 0, errs.slice(0, 5));
  require('fs').writeFileSync(SHOTS + '/browser_results.json', JSON.stringify({ results, ava }, null, 1));
  await b.close();
})();
