import { Engine } from './engine/engine';
import { TEAMS, COLORS, teamByName, defaultSettings } from './engine/match';
import { DT } from './engine/constants';
import { Intent, NO_INTENT, Settings } from './engine/types';
import { Renderer, fmtClock } from './render';
import { touch, consumeTouchEdges, detectTouch, initTouch } from './touch';

const $ = (id: string) => document.getElementById(id)!;
const canvas = $('c') as HTMLCanvasElement;
const ctx = canvas.getContext('2d')!;
const R = new Renderer(ctx);
const logoUrl = (slug: string, size: 128 | 256) => `./logos/${slug}_${size}.webp`;
for (const t of TEAMS) {
  const c = COLORS[t.franchise];
  const img = new Image(); img.src = logoUrl(c.slug, 128); R.logos[c.slug + '_128'] = img;
}

type Mode = 'hva' | 'ava' | 'hvh';
const app = {
  engine: null as Engine | null, mode: 'hva' as Mode, home: 'Ala Marauders', away: 'Xenar Ignite',
  settings: defaultSettings(), pick: 0 as 0 | 1, speed: 1, paused: false, acc: 0, wallT: 0, lastEv: 0, flashShown: '',
};
(window as any).__arcade = app;

function resize() { R.dpr = Math.min(window.devicePixelRatio || 1, 2); canvas.width = Math.round(window.innerWidth * R.dpr); canvas.height = Math.round(window.innerHeight * R.dpr); }
window.addEventListener('resize', resize); resize();

function show(id: string | null) {
  document.querySelectorAll('.screen').forEach((s) => s.classList.toggle('on', s.id === id));
}

// ---------------- team select ----------------
const grid = $('teamGrid');
for (const t of TEAMS) {
  const c = COLORS[t.franchise];
  const d = document.createElement('div'); d.className = 'team'; d.dataset.name = t.franchise; d.title = `${t.franchise} (${t.formation})`;
  d.innerHTML = `<img src="${logoUrl(c.slug, 128)}" alt="${c.abbr}" /><span style="color:${c.primary === '#000000' ? '#fff' : c.primary};text-shadow:0 0 2px #000">${c.abbr}</span>`;
  d.addEventListener('click', (ev) => { if (ev.shiftKey || app.pick === 1) app.away = t.franchise; else app.home = t.franchise; refreshSelect(); });
  d.addEventListener('contextmenu', (ev) => { ev.preventDefault(); app.away = t.franchise; refreshSelect(); });
  grid.appendChild(d);
}
function setPick(p: 0 | 1) { app.pick = p; $('pickH').classList.toggle('on', p === 0); $('pickA').classList.toggle('on', p === 1); }
$('pickH').onclick = () => setPick(0); $('pickA').onclick = () => setPick(1);
($('selL0') as HTMLElement).onclick = () => setPick(0); ($('selL1') as HTMLElement).onclick = () => setPick(1);
function refreshSelect() {
  grid.querySelectorAll('.team').forEach((el) => { const n = (el as HTMLElement).dataset.name; el.classList.toggle('selH', n === app.home); el.classList.toggle('selA', n === app.away); });
  ($('selL0') as HTMLImageElement).src = logoUrl(COLORS[app.home].slug, 256); $('selN0').textContent = app.home;
  ($('selL1') as HTMLImageElement).src = logoUrl(COLORS[app.away].slug, 256); $('selN1').textContent = app.away;
}
function openSelect(mode: Mode) { app.mode = mode; ($('optMode') as HTMLSelectElement).value = mode; refreshSelect(); show('scrSelect'); }
$('mPlay').onclick = () => openSelect('hva');
$('mWatch').onclick = () => openSelect('ava');
$('mHvH').onclick = () => openSelect('hvh');
let controlsReturn = 'scrMenu';
$('mControls').onclick = () => { controlsReturn = 'scrMenu'; show('scrControls'); };
$('ctrlBack').onclick = () => show(controlsReturn);
$('selBack').onclick = () => show('scrMenu');
$('selStart').onclick = () => {
  app.mode = ($('optMode') as HTMLSelectElement).value as Mode;
  const pl = Number(($('optClock') as HTMLSelectElement).value);
  app.settings = { seed: Number(($('optSeed') as HTMLInputElement).value) || 1, scoring: ($('optScoring') as HTMLSelectElement).value as Settings['scoring'], periodLen: pl, otLen: pl === 600 ? 300 : pl / 2 };
  startMatch();
};

function startMatch() {
  const human: [boolean, boolean] = app.mode === 'hva' ? [true, false] : app.mode === 'hvh' ? [true, true] : [false, false];
  app.engine = new Engine(teamByName(app.home), teamByName(app.away), { ...app.settings }, human);
  app.acc = 0; app.paused = false; app.lastEv = 0; app.speed = 1; setSpeed(1);
  R.cam.mode = 'ball'; R.cam.follow = -1; ($('specCam') as HTMLButtonElement).textContent = 'Cam: Ball';
  for (const t of [0, 1]) { const c = COLORS[[app.home, app.away][t]]; ($(`hl${t}`) as HTMLImageElement).src = logoUrl(c.slug, 128); $(`hn${t}`).textContent = c.abbr; $(`hs${t}`).style.borderBottom = `4px solid ${c.primary}`; }
  $('hud').classList.add('on'); $('ticker').style.display = 'block'; $('help').style.display = 'block'; document.body.classList.add('playing');
  $('spec').style.display = app.mode === 'ava' ? 'block' : 'none';
  $('help').innerHTML = app.mode === 'ava' ? 'Spectator · <b>1-4</b> speed · <b>C</b> camera · <b>N</b> next athlete · <b>Esc</b> pause'
    : '<b>WASD</b> move · <b>Shift</b> sprint · <b>Space</b> pass/snap · <b>J</b> tackle · <b>K</b> switch · <b>L</b> shoot · <b>E</b> archer · <b>Esc</b> pause';
  show(null);
}

// ---------------- pause / break / final ----------------
function pause(on: boolean) { if (!app.engine) return; app.paused = on; show(on ? 'scrPause' : null); ($('specPause') as HTMLButtonElement).textContent = on ? 'Resume' : 'Pause'; }
$('pResume').onclick = () => pause(false);
const urlQ = new URLSearchParams(location.search);
touch.enabled = detectTouch(urlQ.get('touch') === '1');
const setTouchUi = () => document.body.classList.toggle('touch', touch.enabled);
setTouchUi();
initTouch({ onPause: () => { if (app.engine && app.engine.phase !== 'final' && app.engine.phase !== 'break') pause(!app.paused); }, onFirstTouch: () => { if (!touch.enabled) { touch.enabled = true; setTouchUi(); } } });
// a first touch on a hybrid device (e.g. touchscreen laptop) also turns the touch UI on
window.addEventListener('touchstart', () => { if (!touch.enabled) { touch.enabled = true; setTouchUi(); } }, { passive: true, once: true });
$('pRestart').onclick = () => startMatch();
$('pControls').onclick = () => { controlsReturn = 'scrPause'; show('scrControls'); };
$('pMenu').onclick = toMenu;
$('fiMenu').onclick = toMenu;
$('fiRematch').onclick = () => startMatch();
$('brSkip').onclick = () => { app.engine?.resumeFromBreak(); show(null); };
function toMenu() { app.engine = null; document.body.classList.remove('playing'); $('hud').classList.remove('on'); $('ticker').style.display = 'none'; $('help').style.display = 'none'; $('spec').style.display = 'none'; show('scrMenu'); }

function statsTable(e: Engine) {
  const rows: [string, (t: number) => string | number][] = [
    ['Score', (t) => e.teams[t].score],
    ['Thrown goal pts', (t) => e.teams[t].breakdown.thrown], ['Carry goal pts', (t) => e.teams[t].breakdown.carry],
    ['Half-goal / award pts', (t) => e.teams[t].breakdown.half + e.teams[t].breakdown.award], ['Own-goal pts received', (t) => e.teams[t].breakdown.own],
    ['Shots', (t) => e.events.filter((v) => v.type === 'shot' && v.team === t).length],
    ['Passes (comp/att)', (t) => { const A = e.ath.filter((a) => a.team === t); return `${A.reduce((n, a) => n + a.stats.passComp, 0)}/${A.reduce((n, a) => n + a.stats.passAtt, 0)}`; }],
    ['Tackles', (t) => e.ath.filter((a) => a.team === t).reduce((n, a) => n + a.stats.tackles, 0)],
    ['Interceptions', (t) => e.ath.filter((a) => a.team === t).reduce((n, a) => n + a.stats.interceptions, 0)],
    ['Turnovers', (t) => e.ath.filter((a) => a.team === t).reduce((n, a) => n + a.stats.turnovers, 0)],
    ['Keeper saves', (t) => e.ath.filter((a) => a.team === t).reduce((n, a) => n + a.stats.saves, 0)],
    ['Arrows (hits/shots)', (t) => { const a = e.ath.find((x) => x.team === t && x.role === 'archer')!; return `${a.stats.arrowHits}/${a.stats.arrows}`; }],
    ['Fouls (minor/major)', (t) => { const A = e.ath.filter((a) => a.team === t); return `${A.reduce((n, a) => n + a.stats.minors, 0)}/${A.reduce((n, a) => n + a.stats.majors, 0)}`; }],
    ['Possession time', (t) => fmtClock(e.teams[t].possTime)],
  ];
  return `<tr><th></th><th>${COLORS[e.teams[0].data.franchise].abbr}</th><th>${COLORS[e.teams[1].data.franchise].abbr}</th></tr>` +
    rows.map(([n, f]) => `<tr><td>${n}</td><td>${f(0)}</td><td>${f(1)}</td></tr>`).join('') + `<tr><td>Possession changes</td><td colspan="2">${e.possChanges}</td></tr>`;
}
function showBreak(e: Engine) {
  const bi = e.breakInfo!;
  $('brTitle').textContent = bi.label;
  ($('brL0') as HTMLImageElement).src = logoUrl(COLORS[e.teams[0].data.franchise].slug, 256);
  ($('brL1') as HTMLImageElement).src = logoUrl(COLORS[e.teams[1].data.franchise].slug, 256);
  $('brScore').textContent = `${e.teams[0].score} - ${e.teams[1].score}`;
  $('brInfo').textContent = `Break ${bi.len / 60} min (skippable). Next: ${bi.to <= 4 ? 'Period ' + bi.to : bi.to === 5 ? 'Overtime (300 s)' : 'Sudden death — any score wins'}. Ends exchanged.`;
  $('brStats').innerHTML = statsTable(e);
  show('scrBreak');
}
function showFinal(e: Engine) {
  const c0 = COLORS[e.teams[0].data.franchise], c1 = COLORS[e.teams[1].data.franchise];
  ($('fiL0') as HTMLImageElement).src = logoUrl(c0.slug, 256); ($('fiL1') as HTMLImageElement).src = logoUrl(c1.slug, 256);
  $('fiN0').textContent = e.teams[0].data.franchise; $('fiN1').textContent = e.teams[1].data.franchise;
  $('fiScore').textContent = `${e.teams[0].score} - ${e.teams[1].score}`;
  $('fiInfo').textContent = `${e.winner >= 0 ? e.teams[e.winner].data.franchise + ' win' : 'Draw'} · ${e.periodName() === 'P4' ? 'Regulation' : e.periodName() === 'OT' ? 'after overtime' : 'in sudden death'} · seed ${e.s.seed} · ${e.s.scoring} scoring · state ${e.hash()}`;
  $('fiStats').innerHTML = statsTable(e);
  const top = [...e.ath].sort((a, b) => b.stats.points - a.stats.points || b.stats.tackles - a.stats.tackles).slice(0, 8);
  $('fiTop').innerHTML = '<tr><th>Athlete</th><th>Team</th><th>Pos</th><th>OVR</th><th>Pts</th><th>Tkl</th><th>Pass</th><th>Saves</th><th>Arrows</th></tr>' +
    top.map((a) => `<tr><td>#${a.d.jersey} ${a.d.name}</td><td>${COLORS[e.teams[a.team].data.franchise].abbr}</td><td>${a.d.pos}</td><td>${a.d.ovr}</td><td>${a.stats.points}</td><td>${a.stats.tackles}</td><td>${a.stats.passComp}/${a.stats.passAtt}</td><td>${a.stats.saves}</td><td>${a.stats.arrowHits}/${a.stats.arrows}</td></tr>`).join('');
  show('scrFinal');
}

// ---------------- spectator ----------------
function setSpeed(s: number) { app.speed = s; document.querySelectorAll('#spec [data-speed]').forEach((b) => b.classList.toggle('on', Number((b as HTMLElement).dataset.speed) === s)); }
document.querySelectorAll('#spec [data-speed]').forEach((b) => (b as HTMLElement).onclick = () => setSpeed(Number((b as HTMLElement).dataset.speed)));
$('specPause').onclick = () => pause(!app.paused);
$('specCam').onclick = () => toggleCam();
$('specNext').onclick = () => nextFollow();
function toggleCam() { R.cam.mode = R.cam.mode === 'ball' ? 'athlete' : 'ball'; if (R.cam.mode === 'athlete' && R.cam.follow < 0) nextFollow(); ($('specCam') as HTMLButtonElement).textContent = R.cam.mode === 'ball' ? 'Cam: Ball' : 'Cam: Athlete'; }
function nextFollow() { const e = app.engine; if (!e) return; R.cam.follow = (R.cam.follow + 1) % e.ath.length; if (e.ath[R.cam.follow].role === 'archer') R.cam.follow = (R.cam.follow + 1) % e.ath.length; R.cam.mode = 'athlete'; ($('specCam') as HTMLButtonElement).textContent = 'Cam: Athlete'; }

// ---------------- input (HumanController) ----------------
const keys = new Set<string>();
const pressed = new Set<string>();
window.addEventListener('keydown', (ev) => {
  if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(ev.code) && app.engine) ev.preventDefault();
  if (!keys.has(ev.code)) pressed.add(ev.code);
  keys.add(ev.code);
  if (ev.code === 'Escape' && app.engine && app.engine.phase !== 'final' && app.engine.phase !== 'break') pause(!app.paused);
  if (app.mode === 'ava' && app.engine) {
    if (ev.code === 'Digit1') setSpeed(1); if (ev.code === 'Digit2') setSpeed(2); if (ev.code === 'Digit3') setSpeed(4); if (ev.code === 'Digit4') setSpeed(8);
    if (ev.code === 'KeyC') toggleCam(); if (ev.code === 'KeyN') nextFollow();
  }
});
window.addEventListener('keyup', (ev) => keys.delete(ev.code));
window.addEventListener('blur', () => keys.clear());

interface Binding { up: string[]; down: string[]; left: string[]; right: string[]; sprint: string[]; pass: string[]; tackle: string[]; sw: string[]; shoot: string[]; fire: string[] }
const P1: Binding = { up: ['KeyW'], down: ['KeyS'], left: ['KeyA'], right: ['KeyD'], sprint: ['ShiftLeft'], pass: ['Space'], tackle: ['KeyJ'], sw: ['KeyK'], shoot: ['KeyL'], fire: ['KeyE'] };
const P1solo: Binding = { ...P1, up: ['KeyW', 'ArrowUp'], down: ['KeyS', 'ArrowDown'], left: ['KeyA', 'ArrowLeft'], right: ['KeyD', 'ArrowRight'], sprint: ['ShiftLeft', 'ShiftRight'] };
const P2: Binding = { up: ['ArrowUp'], down: ['ArrowDown'], left: ['ArrowLeft'], right: ['ArrowRight'], sprint: ['ControlRight'], pass: ['Enter', 'NumpadEnter'], tackle: ['Period'], sw: ['Comma'], shoot: ['Slash'], fire: ['Quote'] };
const padPrev: Record<number, boolean[]> = {};

function readPad(i: number) {
  const pads = navigator.getGamepads ? navigator.getGamepads() : [];
  const p = pads && pads[i];
  if (!p) return null;
  const prev = padPrev[i] || [];
  const btn = (k: number) => !!p.buttons[k]?.pressed;
  const edge = (k: number) => btn(k) && !prev[k];
  const res = { mx: Math.abs(p.axes[0]) > 0.2 ? p.axes[0] : 0, my: Math.abs(p.axes[1]) > 0.2 ? p.axes[1] : 0, sprint: btn(5) || btn(7), pass: edge(0), tackle: edge(1), shoot: edge(2), sw: edge(3), fire: edge(4), pause: edge(9) };
  if (btn(12)) res.my = -1; if (btn(13)) res.my = 1; if (btn(14)) res.mx = -1; if (btn(15)) res.mx = 1;
  padPrev[i] = p.buttons.map((b) => b.pressed);
  return res;
}

function humanControl(e: Engine, team: 0 | 1, b: Binding, padIdx: number) {
  const T = e.teams[team];
  const any = (ks: string[]) => ks.some((k) => keys.has(k));
  const hit = (ks: string[]) => ks.some((k) => pressed.has(k));
  const pad = readPad(padIdx);
  if (pad?.pause && e.phase !== 'final') pause(!app.paused);
  const tc = team === 0 && touch.enabled ? touch : null;
  let mx = (any(b.right) ? 1 : 0) - (any(b.left) ? 1 : 0), my = (any(b.down) ? 1 : 0) - (any(b.up) ? 1 : 0);
  if (pad && (pad.mx || pad.my)) { mx = pad.mx; my = pad.my; }
  if (tc && (tc.mx || tc.my)) { mx = tc.mx; my = tc.my; }
  // auto selection: carrier when we have the ball; otherwise keep / pick nearest to carrier on possession change
  const holder = e.ball.holder >= 0 ? e.ath[e.ball.holder] : null;
  const fieldMates = e.ath.filter((a) => a.team === team && a.role !== 'archer' && e.active(a));
  const nearestTo = (x: number, y: number) => fieldMates.filter((a) => a.frozenT <= 0).sort((p, q) => Math.hypot(p.x - x, p.y - y) - Math.hypot(q.x - x, q.y - y))[0] ?? fieldMates[0];
  const sel = T.selected >= 0 ? e.ath[T.selected] : null;
  const lastPoss = (T as any)._lastPoss;
  if (holder && holder.team === team) T.selected = holder.idx;
  else if (!sel || !e.active(sel) || sel.role === 'archer' || sel.frozenT > 0 || lastPoss !== e.poss) {
    const tgt = holder ?? e.ball; T.selected = nearestTo(tgt.x, tgt.y).idx;
  }
  (T as any)._lastPoss = e.poss;
  if (hit(b.sw) || pad?.sw || tc?.sw) {
    const others = fieldMates.filter((a) => a.idx !== T.selected && a.frozenT <= 0 && a.role !== 'keeper').sort((p, q) => Math.hypot(p.x - e.ball.x, p.y - e.ball.y) - Math.hypot(q.x - e.ball.x, q.y - e.ball.y));
    if (others[0] && !(holder && holder.team === team)) T.selected = others[0].idx;
  }
  const me = e.ath[T.selected];
  const it: Intent = { ...NO_INTENT(), mx, my, sprint: any(b.sprint) || !!pad?.sprint || !!tc?.sprintBtn || !!tc?.stickSprint };
  if ((hit(b.pass) || pad?.pass || tc?.pass) && holder === me) {
    // pass to the open teammate closest to the pushed direction (or facing)
    const dir = (mx || my) ? Math.atan2(my, mx) : me.facing;
    let best = -1, bs = -1e9;
    for (const a of fieldMates) {
      if (a.idx === me.idx || a.frozenT > 0 || a.groundedT > 0) continue;
      const dx = a.x - me.x, dy = a.y - me.y, d = Math.hypot(dx, dy);
      if (d < 3 || d > 45) continue;
      const cos = (dx * Math.cos(dir) + dy * Math.sin(dir)) / d;
      const sc = cos * 3 - d * 0.03;
      if (sc > bs) { bs = sc; best = a.idx; }
    }
    it.pass = best;
  }
  if ((hit(b.shoot) || pad?.shoot || tc?.shoot) && holder === me) it.shoot = true;
  if (hit(b.tackle) || pad?.tackle || tc?.tackle) it.tackle = true;
  if (hit(b.fire) || pad?.fire || tc?.fire) {
    const archer = e.ath.find((a) => a.team === team && a.role === 'archer')!;
    const cands = e.ath.filter((o) => e.arrowLegal(archer, o));
    const pick = cands.find((o) => o.idx === e.ball.holder) ?? cands.sort((p, q) => Math.hypot(p.x - e.ball.x, p.y - e.ball.y) - Math.hypot(q.x - e.ball.x, q.y - e.ball.y))[0];
    if (pick) it.fire = pick.idx;
  }
  const prev = e.humanIntent[team];
  if (prev) { if (it.pass < 0) it.pass = prev.pass; it.shoot = it.shoot || prev.shoot; it.tackle = it.tackle || prev.tackle; if (it.fire < 0) it.fire = prev.fire; }
  e.humanIntent[team] = it;
}

// ---------------- HUD ----------------
function hud(e: Engine) {
  for (const t of [0, 1]) {
    const T = e.teams[t];
    $(`hsc${t}`).textContent = String(T.score);
    $(`ha${t}`).textContent = `ARROWS ${T.arrowsLeft}/15 · FREEZE ${T.freezesLeft}/5`;
    ($(`hp${t}`) as HTMLElement).style.visibility = e.poss === t ? 'visible' : 'hidden';
  }
  $('hper').textContent = e.period <= 4 ? `PERIOD ${e.period}` : e.period === 5 ? 'OVERTIME' : 'SUDDEN DEATH';
  $('hclk').textContent = e.suddenDeath ? 'SD' : fmtClock(Math.ceil(e.clock));
  const snap = e.phase === 'snap' ? ` · SNAP ${Math.ceil(e.snapT)}` : '';
  $('hplay').textContent = `PLAY ${Math.ceil(e.playClock)} · TACKLE ${e.tackleCount}${snap}${e.huntActive ? ' · HUNT' : ''}${e.s.periodLen !== 600 ? ' · ACCEL CLOCK' : ''}`;
  const f = $('flash');
  if (e.flash && e.phase !== 'final') { f.style.display = 'block'; f.textContent = e.flash.text; f.style.color = e.flash.team >= 0 ? COLORS[e.teams[e.flash.team].data.franchise].primary : '#fff'; }
  else f.style.display = 'none';
  if (e.events.length !== app.lastEv) {
    app.lastEv = e.events.length;
    const ev = e.events.filter((v) => !['possession', 'shot', 'arrow'].includes(v.type)).slice(-6);
    $('ticker').innerHTML = ev.map((v) => `<div>${v.period <= 4 ? 'P' + v.period : v.period === 5 ? 'OT' : 'SD'} ${fmtClock(v.clock)} · ${v.text}</div>`).join('');
  }
}

// ---------------- main loop ----------------
const q = new URLSearchParams(location.search);
let last = performance.now();
function frame(now: number) {
  const dtReal = Math.min(0.1, (now - last) / 1000); last = now;
  app.wallT += dtReal;
  const e = app.engine;
  if (e) {
    if (!app.paused && e.phase !== 'break' && e.phase !== 'final') {
      if (app.mode !== 'ava') {
        humanControl(e, 0, app.mode === 'hvh' ? P1 : P1solo, 0);
        if (app.mode === 'hvh') humanControl(e, 1, P2, 1);
      }
      app.acc += dtReal * app.speed;
      let n = 0;
      while (app.acc >= DT && n < 1000) {
        e.step(); app.acc -= DT; n++;
        if (n === 1) pressed.clear();
        if ((e.phase as string) === 'break' || (e.phase as string) === 'final') { app.acc = 0; break; }
      }
      if ((e.phase as string) === 'break') { if (q.get('autobreak')) e.resumeFromBreak(); else showBreak(e); }
      if ((e.phase as string) === 'final') showFinal(e);
    }
    R.cam.update(e, canvas.width / R.dpr, canvas.height / R.dpr, dtReal);
    const sel = e.teams.filter((t) => t.human).map((t) => t.selected);
    R.draw(e, [COLORS[e.teams[0].data.franchise], COLORS[e.teams[1].data.franchise]], app.wallT, sel);
    hud(e);
  } else {
    ctx.setTransform(1, 0, 0, 1, 0, 0); ctx.fillStyle = "#0b0e16"; ctx.fillRect(0, 0, canvas.width, canvas.height);
  }
  pressed.clear(); consumeTouchEdges();
  requestAnimationFrame(frame);
}
requestAnimationFrame(frame);

// URL helpers for testing: ?auto=ava&home=..&away=..&seed=..&speed=..
if (q.get('auto')) {
  app.mode = q.get('auto') as Mode; app.home = q.get('home') || app.home; app.away = q.get('away') || app.away;
  app.settings = { ...defaultSettings(Number(q.get('seed') || 20261115)), periodLen: Number(q.get('period') || 600) };
  app.settings.otLen = app.settings.periodLen === 600 ? 300 : app.settings.periodLen / 2;
  startMatch(); if (q.get('speed')) setSpeed(Number(q.get('speed')));
}
