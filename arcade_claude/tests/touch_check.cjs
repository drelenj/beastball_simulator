// Touch acceptance checks: emulated iPhone (landscape, DPR 3, touch only). Real CDP touch events,
// including two simultaneous fingers (stick + action button).
const { chromium } = require('playwright');
const BASE = process.env.BASE || 'http://localhost:5173/';
const SHOTS = process.env.SHOTS || '.';
const results = []; const log = (n, ok, i) => { results.push({ n, ok, i }); console.log((ok ? 'PASS ' : 'FAIL ') + n + ' :: ' + JSON.stringify(i)); };
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 844, height: 390 }, deviceScaleFactor: 3, hasTouch: true, isMobile: true, userAgent: 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1' });
  const p = await ctx.newPage(); const errs = [];
  p.on('pageerror', (e) => errs.push(String(e))); p.on('console', (m) => { if (m.type() === 'error') errs.push(m.text()); });
  const cdp = await ctx.newCDPSession(p);
  const touchEv = (type, pts) => cdp.send('Input.dispatchTouchEvent', { type, touchPoints: pts.map(([id, x, y]) => ({ id, x, y })) });
  const E = (f, a) => p.evaluate(f, a);
  await p.goto(BASE); await p.waitForTimeout(800);
  log('touch UI detected on phone-like device', await E(() => document.body.classList.contains('touch')), {});
  await p.tap('#mPlay');
  // pick HOME then AWAY with the on-screen toggle (no Shift on a phone)
  await p.tap('#pickH'); await p.tap('.team[data-name="Ala Marauders"]');
  await p.tap('#pickA'); await p.tap('.team[data-name="Xenar Ignite"]');
  const sel = await E(() => ({ h: document.getElementById('selN0').textContent, a: document.getElementById('selN1').textContent }));
  log('team select by touch (HOME / AWAY toggle)', sel.h === 'Ala Marauders' && sel.a === 'Xenar Ignite', sel);
  await p.screenshot({ path: SHOTS + '/touch_select.png' });
  await p.selectOption('#optClock', '60');
  await p.tap('#selStart'); await p.waitForTimeout(1500);
  const vis = await E(() => { const r = (id) => { const e = document.getElementById(id); const b = e.getBoundingClientRect(); return e.offsetParent !== null && b.width > 0; };
    return { pass: r('tPass'), shoot: r('tShoot'), tackle: r('tTackle'), sw: r('tSwitch'), fire: r('tFire'), sprint: r('tSprint'), pause: r('tPause'), zone: r('tzone'), canvasW: document.querySelector('canvas').width, dpr: window.devicePixelRatio }; });
  log('touch controls visible in match; canvas is retina-sharp', Object.entries(vis).filter(([k]) => !['canvasW', 'dpr'].includes(k)).every(([, v]) => v) && vis.canvasW === 844 * 2, vis);
  await p.screenshot({ path: SHOTS + '/touch_match.png' });

  // --- joystick: drag right/down => selected athlete moves that way; outer ring => sprint
  const snap = () => E(() => { const e = window.__arcade.engine; const a = e.ath[e.teams[0].selected]; return { i: a.idx, x: a.x, y: a.y, v: Math.hypot(a.vx, a.vy), top: a.a.top, phase: e.phase }; });
  let s0 = await snap();
  // if our athlete is the snapper, release first with the PASS button
  if (s0.phase === 'snap') { await p.tap('#tPass'); await p.waitForTimeout(600); s0 = await snap(); }
  await touchEv('touchStart', [[1, 120, 300]]);
  await touchEv('touchMove', [[1, 120 + 30, 300 + 20]]); await p.waitForTimeout(700);
  const mid = await snap();
  const stickOn = await E(() => document.getElementById('stick').classList.contains('on'));
  await touchEv('touchMove', [[1, 120 + 75, 300]]); await p.waitForTimeout(900);
  const fast = await snap();
  const sprintLit = await E(() => document.getElementById('stick').classList.contains('sprint'));
  await touchEv('touchEnd', []); await p.waitForTimeout(500);
  const rest = await E(() => ({ mx: 0, stick: document.getElementById('stick').classList.contains('on') }));
  const dx = mid.x - s0.x, dy = mid.y - s0.y;
  log('joystick drag moves the athlete (right/down, jog speed)', mid.i === s0.i ? (dx > 0.3 && dy > 0.1) : mid.v > 0.5, { s0: [s0.x, s0.y], mid: [mid.x, mid.y], v: mid.v, stickOn });
  log('stick pushed to outer ring sprints', sprintLit && fast.v > fast.top * 0.68 * 1.1, { v: fast.v, jogCap: +(fast.top * 0.68).toFixed(2), sprintLit });
  log('releasing the stick stops input and parks the stick', !rest.stick, rest);

  // --- two fingers: hold stick with finger 1, tap PASS with finger 2 (multi-touch)
  const stats = () => E(() => { const A = window.__arcade.engine.ath.filter((a) => a.team === 0); return { att: A.reduce((n, a) => n + a.stats.passAtt, 0), tk: A.reduce((n, a) => n + a.stats.tackles, 0), poss: window.__arcade.engine.poss, holderTeam: (() => { const e = window.__arcade.engine; return e.ball.holder >= 0 ? e.ath[e.ball.holder].team : -1; })() }; });
  const btn = async (id) => { const r = await E((id) => { const b = document.getElementById(id).getBoundingClientRect(); return [b.x + b.width / 2, b.y + b.height / 2]; }, id); return r; };
  let multi = false, passDone = false, tackleDone = false, cycles = 0;
  await touchEv('touchStart', [[1, 120, 300]]); await touchEv('touchMove', [[1, 150, 300]]);
  const [px, py] = await btn('tPass'); const [kx, ky] = await btn('tTackle');
  const a0 = await stats();
  for (let k = 0; k < 900 && !(passDone && tackleDone); k++) {
    cycles++;
    const st = await E(() => { const e = window.__arcade.engine; const sel = e.ath[e.teams[0].selected]; const h = e.ball.holder >= 0 ? e.ath[e.ball.holder] : null; return { phase: e.phase, mine: !!h && h.team === 0, ph: e.phase, sel: [sel.x, sel.y], tgt: h ? [h.x, h.y] : [e.ball.x, e.ball.y], over: e.phase === 'final' || e.phase === 'break' }; });
    if (st.over) break;
    if (st.mine && passDone) { await p.waitForTimeout(150); continue; } // wait for the AI to win the ball back, then tackle
    if (st.mine) { // second finger taps PASS while finger 1 still holds the stick
      await touchEv('touchStart', [[1, 150, 300], [2, px, py]]); await p.waitForTimeout(80); await touchEv('touchEnd', [[1, 150, 300]]);
      multi = true; await p.waitForTimeout(500); const s2 = await stats(); passDone = s2.att > a0.att; continue;
    }
    // opponent carries the ball: harness puts the selected athlete next to the carrier (stick movement is covered above),
    // then finger 2 taps the real TACKLE button while finger 1 keeps holding the stick
    const opp = await E(() => { const e = window.__arcade.engine; const h = e.ball.holder >= 0 ? e.ath[e.ball.holder] : null; if (!h || h.team === 0 || e.phase !== "live") return false; const a = e.ath[e.teams[0].selected]; a.x = h.x - 0.9; a.y = h.y; a.vx = a.vy = 0; return true; });
    if (opp) { await touchEv('touchStart', [[1, 150, 300], [2, kx, ky]]); await p.waitForTimeout(60); await touchEv('touchEnd', [[1, 150, 300]]); await p.waitForTimeout(250); const s3 = await stats(); tackleDone = s3.tk > a0.tk; await touchEv('touchStart', [[1, 150, 300]]); continue; }
    await p.waitForTimeout(120);
  }
  await touchEv('touchEnd', []);
  const a1 = await stats();
  log('multi-touch: stick held while PASS tapped with a second finger', multi && a1.att > a0.att, { a0, a1, cycles });
  log('multi-touch: TACKLE button tapped with a second finger grounds a carrier (athlete placed beside carrier by harness)', a1.tk > a0.tk, { a0, a1 });
  await p.screenshot({ path: SHOTS + '/touch_play.png' });

  // --- other buttons do not crash; SWITCH, ARCHER, SHOOT, SPRINT hold
  for (const id of ['tSwitch', 'tFire', 'tShoot']) await p.tap('#' + id);
  const fired = await E(() => window.__arcade.engine.ath.filter((a) => a.team === 0 && a.role === 'archer')[0].stats.arrows);
  log('SWITCH / ARCHER / SHOOT buttons respond without error', errs.length === 0, { archerArrowsSoFar: fired, errs: errs.slice(0, 3) });

  // --- pause button and resume
  await p.tap('#tPause'); await p.waitForTimeout(300);
  log('II pauses; pause screen reachable by touch', await p.isVisible('#scrPause'), {});
  await p.tap('#pResume'); await p.waitForTimeout(300);
  log('resume returns to the match', !(await p.isVisible('#scrPause')) && (await E(() => window.__arcade.paused === false)), {});

  // --- run to final on accelerated clock; break + final screens usable by touch
  await E(() => { window.__arcade.speed = 8; });
  for (let k = 0; k < 400; k++) {
    const ph = await E(() => window.__arcade.engine.phase);
    if (ph === 'final') break;
    if (ph === 'break') await p.tap('#brSkip');
    await p.waitForTimeout(500);
  }
  await p.waitForTimeout(500);
  log('final screen shown; Rematch button works by touch', await p.isVisible('#scrFinal'), {});
  await p.screenshot({ path: SHOTS + '/touch_final.png' });
  await p.tap('#fiRematch'); await p.waitForTimeout(700);
  log('rematch by touch starts a fresh match', await E(() => window.__arcade.engine.teams[0].score === 0 && window.__arcade.engine.phase !== 'final'), {});

  // --- portrait: still playable, rotate hint shown
  await p.setViewportSize({ width: 390, height: 844 }); await p.waitForTimeout(600);
  const portrait = await E(() => ({ hint: getComputedStyle(document.getElementById('rotate')).display, w: innerWidth }));
  await p.screenshot({ path: SHOTS + '/touch_portrait.png' });
  log('portrait shows the rotate hint', portrait.hint === 'block', portrait);
  log('no console or page errors', errs.length === 0, errs.slice(0, 5));
  require('fs').writeFileSync(SHOTS + '/touch_results.json', JSON.stringify(results, null, 1));
  await b.close();
})();
