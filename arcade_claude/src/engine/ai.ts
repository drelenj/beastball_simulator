// AIController: produces athlete INTENTS from what that athlete can perceive.
// Information boundary: decisions read only the athlete's own memory (limited view cone and
// range, last-known positions) plus public referee information (phase, possession call,
// tackle count, clocks, score). No hidden or future state.
import * as C from './constants';
// Deterministic across JS engines: avoid Math.hypot / ** (implementation-dependent rounding).
const hyp = (...v: number[]) => { let s = 0; for (const x of v) s += x * x; return Math.sqrt(s); };
import type { Engine } from './engine';
import { Athlete, Intent, NO_INTENT } from './types';
import { REACH, TRAJ_DT, ballTraj, interceptAt } from './intercept';

const FOV = (200 * Math.PI) / 180;
const STALE = 3.0;

function angDiff(a: number, b: number) { let d = a - b; while (d > Math.PI) d -= 2 * Math.PI; while (d < -Math.PI) d += 2 * Math.PI; return Math.abs(d); }

export function perceive(e: Engine, a: Athlete) {
  const range = a.role === 'archer' ? 90 : a.a.view + 20;
  const fov = a.role === 'archer' ? Math.PI * 1.1 : FOV;
  const sees = (x: number, y: number) => {
    const dx = x - a.x, dy = y - a.y, d = hyp(dx, dy);
    if (d < 6) return true; // proximity (peripheral/hearing)
    if (d > range) return false;
    // head scan: athletes sweep their gaze around their body facing
    const gaze = a.facing + Math.sin(e.time * 1.7 + a.idx * 1.3) * 0.9;
    return angDiff(Math.atan2(dy, dx), gaze) < fov / 2;
  };
  for (const o of e.ath) {
    if (o.idx === a.idx || !e.active(o)) { if (!e.active(o)) a.mem.delete(o.idx); continue; }
    if (sees(o.x, o.y)) a.mem.set(o.idx, { x: o.x, y: o.y, vx: o.vx, vy: o.vy, t: e.time, frozen: o.frozenT > 0 || o.recoverT > 0 || o.immuneT > 0 });
  }
  const b = e.ball;
  const holder = b.holder >= 0 ? e.ath[b.holder] : null;
  const bx = holder ? holder.x : b.x, by = holder ? holder.y : b.y;
  if (b.holder === a.idx || sees(bx, by)) {
    a.ballMem = { x: b.x, y: b.y, z: b.z, vx: holder ? holder.vx : b.vx, vy: holder ? holder.vy : b.vy, vz: holder ? 0 : b.vz, t: e.time, holder: b.holder };
  }
}

interface Seen { idx: number; x: number; y: number; vx: number; vy: number; team: number; frozen: boolean; role: string; age: number }
function seen(e: Engine, a: Athlete): Seen[] {
  const out: Seen[] = [];
  for (const [idx, m] of a.mem) {
    const age = e.time - m.t;
    if (age > STALE) continue;
    const o = e.ath[idx];
    const k = Math.min(age, 1);
    out.push({ idx, x: m.x + m.vx * k, y: m.y + m.vy * k, vx: m.vx, vy: m.vy, team: o.team, frozen: m.frozen, role: o.role, age });
  }
  return out;
}
function ballGuess(e: Engine, a: Athlete) {
  const m = a.ballMem; const age = Math.min(1.5, e.time - m.t);
  return { x: m.x + m.vx * age, y: m.y + m.vy * age, z: m.z, holder: e.time - m.t < STALE ? m.holder : -2, age };
}

function setTarget(a: Athlete, x: number, y: number, sprint: boolean) {
  a.tx = Math.max(-C.FIELD_HALF + 0.5, Math.min(C.FIELD_HALF - 0.5, x));
  a.ty = Math.max(-C.FIELD_HALF + 0.5, Math.min(C.FIELD_HALF - 0.5, y));
  a.aiSprint = sprint;
}

function formationSpot(e: Engine, a: Athlete, ballX: number, attacking: boolean) {
  const bu = e.u(a.team, ballX);
  const base = attacking ? [32, 52, 68][a.line] : [16, 28, 40][a.line];
  let u = base + (bu - 50) * (attacking ? 0.5 : 0.4);
  u = Math.max(4, Math.min(attacking ? 78 : 70, u));
  const y = a.slotY * (a.line === 1 ? 32 : 26);
  return { x: e.xFromU(a.team, u), y };
}

export function aiThink(e: Engine, a: Athlete) {
  perceive(e, a);
  a.plan = NO_INTENT();
  if (a.role === 'archer') { archerThink(e, a); return; }
  if (!e.canAct(a)) { setTarget(a, a.x, a.y, false); return; }
  const b = ballGuess(e, a);
  if (e.phase === 'snap') {
    if (e.ball.holder === a.idx) {
      if (e.time >= a.aiPassAt) { const r = bestPass(e, a, true); if (r >= 0) a.plan.pass = r; else a.facing += 2.0; /* turn to look for a receiver */ }
      setTarget(a, a.x, a.y, false);
    } else {
      const spot = formationSpot(e, a, b.x, e.poss === a.team);
      setTarget(a, spot.x, spot.y, false);
      if (a.role === 'keeper') keeperThink(e, a, b);
    }
    return;
  }
  if (e.ball.holder === a.idx) { carrierThink(e, a); return; }
  if (a.role === 'keeper') { keeperThink(e, a, b); return; }
  const holderTeam = b.holder >= 0 ? e.ath[b.holder].team : -1;
  if (holderTeam === a.team) supportThink(e, a, b);
  else if (holderTeam >= 0) defendThink(e, a, b);
  else looseThink(e, a, b);
}

function opponentsNear(list: Seen[], a: Athlete, x: number, y: number) {
  let m = 99;
  for (const s of list) if (s.team !== a.team && s.role !== 'archer' && !s.frozen) m = Math.min(m, hyp(s.x - x, s.y - y));
  return m;
}

function bestPass(e: Engine, a: Athlete, snap = false): number {
  const list = seen(e, a);
  let best = -1, bestS = -1e9;
  for (const t of list) {
    if (t.team !== a.team || t.role === 'archer' || t.frozen) continue;
    const o = e.ath[t.idx];
    if (!e.canAct(o)) continue;
    const d = hyp(t.x - a.x, t.y - a.y);
    if (d < 4 || d > 38) continue;
    const gain = e.u(a.team, t.x) - e.u(a.team, a.x);
    const open = Math.min(9, opponentsNear(list, a, t.x, t.y));
    // passing-lane safety: closest seen opponent to segment
    let lane = 9;
    for (const s of list) {
      if (s.team === a.team || s.role === 'archer') continue;
      const sx = t.x - a.x, sy = t.y - a.y, L = sx * sx + sy * sy;
      let k = ((s.x - a.x) * sx + (s.y - a.y) * sy) / L; k = Math.max(0, Math.min(1, k));
      lane = Math.min(lane, hyp(a.x + sx * k - s.x, a.y + sy * k - s.y));
    }
    const kz = e.inKZ(t.x, t.y, e.oppGoalX(a.team)) ? -2 : 0;
    const sc = gain * (snap ? 0.03 : 0.16) + open * 0.3 + Math.min(lane, 5) * 0.45 - Math.abs(d - 16) * 0.04 + kz;
    if (sc > bestS) { bestS = sc; best = t.idx; }
  }
  return bestS > (snap ? -99 : 1.6) ? best : -1;
}

function carrierThink(e: Engine, a: Athlete) {
  const list = seen(e, a);
  const gx = e.oppGoalX(a.team);
  const dGoal = hyp(gx - a.x, a.y);
  const pressure = opponentsNear(list, a, a.x, a.y);
  const q = (a.d.ovr - 40) / 60;
  if (a.role === 'keeper') {
    if (e.time - e.holderSince > 0.6) { const r = bestPass(e, a, true); if (r >= 0) { a.plan.pass = r; return; } }
    setTarget(a, a.x, a.y, false); return;
  }
  const shootRange = 14 + 9 * q + (a.d.pos === 'STR' ? 4 : 0) + (a.d.pos === 'PFD' ? 2 : 0);
  const angleOk = Math.abs(a.y) < Math.max(4, Math.abs(gx - a.x) * 0.9);
  const kz = e.inKZ(a.x, a.y, gx);
  const rng = e.rng;
  // keeper position (if seen) affects carry-in choice
  const keeper = list.find((s) => s.team !== a.team && s.role === 'keeper');
  const keeperOff = !keeper || hyp(keeper.x - gx, keeper.y) > 4;
  if (dGoal < 6 && keeperOff && pressure > 2) { setTarget(a, gx + Math.sign(gx) * 2, 0, true); return; } // carry goal attempt
  if ((dGoal < shootRange && angleOk && rng.chance(0.18 + (shootRange - dGoal) * 0.04)) || (kz && a.kzT > 2.5) || (e.playClock < 4 && dGoal < 30)) {
    a.plan.shoot = true; return;
  }
  const mustMove = pressure < 3.2 || (e.tackleCount === 1 && pressure < 5) || e.playClock < 8;
  const r = bestPass(e, a);
  if (r >= 0 && (mustMove ? rng.chance(0.7) : rng.chance(0.06))) { a.plan.pass = r; return; }
  // advance with avoidance
  let ax = 0, ay = 0;
  for (const s of list) {
    if (s.team === a.team || s.role === 'archer' || s.frozen) continue;
    const dx = a.x - s.x, dy = a.y - s.y, d = hyp(dx, dy);
    if (d < 10) { ax += dx / d * (10 - d); ay += dy / d * (10 - d); }
  }
  const dir = e.teams[a.team].dir;
  const tyGoal = -a.y * 0.25;
  setTarget(a, a.x + dir * 10 + ax * 0.25, a.y + tyGoal + ay * 0.6, true);
  if (kz && a.kzT > 1.5) setTarget(a, gx, 0, true);
}

function supportThink(e: Engine, a: Athlete, b: { x: number; y: number }) {
  const list = seen(e, a);
  const bu = e.u(a.team, b.x);
  const lineAhead = [-6, 8, 18][a.line] ?? 6;
  let u = Math.max(6, Math.min(79, bu + lineAhead));
  let y = a.slotY * 30 + (b.y * 0.25);
  const x0 = e.xFromU(a.team, u);
  // get open: move away from nearest seen opponent
  let ox = 0, oy = 0;
  for (const s of list) {
    if (s.team === a.team || s.role === 'archer') continue;
    const dx = x0 - s.x, dy = y - s.y, d = hyp(dx, dy);
    if (d < 7 && d > 0.01) { ox += dx / d * (7 - d); oy += dy / d * (7 - d); }
  }
  let tx = x0 + ox * 0.5, ty = y + oy * 0.6;
  // stay out of the opponent Keeper Zone (5 s limit)
  const gx = e.oppGoalX(a.team);
  const d = hyp(tx - gx, ty);
  if (d < C.KEEPER_ZONE_R + 1) { tx = gx + (tx - gx) / d * (C.KEEPER_ZONE_R + 1); ty = ty / d * (C.KEEPER_ZONE_R + 1); }
  setTarget(a, tx, ty, hyp(tx - a.x, ty - a.y) > 8);
}

function defendThink(e: Engine, a: Athlete, b: { x: number; y: number; holder: number }) {
  const list = seen(e, a);
  const carrier = list.find((s) => s.idx === b.holder) ?? { x: b.x, y: b.y, vx: 0, vy: 0, frozen: false, idx: b.holder } as Seen;
  // am I among my team's two closest (as I perceive teammates) to the carrier?
  const myD = hyp(carrier.x - a.x, carrier.y - a.y);
  let closer = 0;
  for (const s of list) if (s.team === a.team && s.role === 'field' && !s.frozen && hyp(carrier.x - s.x, carrier.y - s.y) < myD) closer++;
  const chasers = a.d.pos === 'TRK' || a.d.pos === 'HNT' ? 2 : 1;
  const c = e.ath[b.holder];
  const immune = c && (c.role === 'keeper' && e.inKZ(carrier.x, carrier.y, e.oppGoalX(a.team)));
  if (closer < chasers + (a.line === 2 ? 0 : 0) && !carrier.frozen && !immune) {
    const lead = Math.min(1, myD / (a.a.top + 0.1));
    setTarget(a, carrier.x + carrier.vx * lead, carrier.y + carrier.vy * lead, true);
    if (myD < 1.45) a.plan.tackle = true;
    return;
  }
  // mark: goal-side of the nearest seen attacker to my zone spot
  const spot = formationSpot(e, a, b.x, false);
  let mark: Seen | null = null, md = 1e9;
  for (const s of list) {
    if (s.team === a.team || s.role !== 'field' || s.idx === b.holder) continue;
    const d = hyp(s.x - spot.x, s.y - spot.y);
    if (d < md && d < 18) { md = d; mark = s; }
  }
  const og = e.ownGoalX(a.team);
  let tx = spot.x, ty = spot.y;
  if (mark) { const dx = og - mark.x, dy = -mark.y, d = hyp(dx, dy) || 1; tx = mark.x + dx / d * 1.6; ty = mark.y + dy / d * 1.6; }
  // defenders may stay in their own Keeper Zone only within 5 m of an attacker
  const dd = hyp(tx - og, ty);
  if (dd < C.KEEPER_ZONE_R && !(mark && hyp(mark.x - tx, mark.y - ty) < 5)) { tx = og + (tx - og) / (dd || 1) * C.KEEPER_ZONE_R; ty = ty / (dd || 1) * C.KEEPER_ZONE_R; }
  setTarget(a, tx, ty, hyp(tx - a.x, ty - a.y) > 6);
}

function looseThink(e: Engine, a: Athlete, b: { x: number; y: number; z: number }) {
  // Predict the flight of the ball from what this athlete last saw, then run onto the earliest point
  // on that flight they can reach (not just where it lands): fast, flat passes must be met in the air.
  const list = seen(e, a);
  const m = a.ballMem;
  const age = Math.min(1.2, e.time - m.t);
  const traj = ballTraj({ x: m.x, y: m.y, z: m.z, vx: m.vx, vy: m.vy, vz: m.vz }, 2.4);
  const k0 = Math.round(age / TRAJ_DT);
  const speed = a.a.top * 0.85;
  const mine = interceptAt(traj, k0, a.x, a.y, speed, REACH.field);
  // the pass call (who threw it, who it is for) is public: the receiver hears it
  const intended = e.ball.receiver === a.idx;
  const passerTeam = e.ball.passer >= 0 ? e.ath[e.ball.passer].team : -1;
  if (intended) { setTarget(a, mine.x, mine.y, true); return; }
  if (passerTeam === a.team && e.ball.receiver >= 0) { // a teammate is receiving: support, do not crowd the ball
    const spot = formationSpot(e, a, mine.x, true); setTarget(a, spot.x, spot.y, false); return;
  }
  // loose or opposing ball: the two quickest players (as this athlete perceives them) go for it
  let quicker = 0;
  for (const s of list) {
    if (s.team !== a.team || s.role === 'archer' || s.frozen) continue;
    const r = interceptAt(traj, k0, s.x, s.y, speed, REACH.field);
    if (r.t < mine.t - 0.05) quicker++;
  }
  if (quicker < 2) { setTarget(a, mine.x, mine.y, true); return; }
  const spot = formationSpot(e, a, mine.x, e.poss === a.team);
  setTarget(a, (spot.x * 2 + mine.x) / 3, (spot.y * 2 + mine.y) / 3, false);
}

function keeperThink(e: Engine, a: Athlete, b: { x: number; y: number; holder: number }) {
  const og = e.ownGoalX(a.team);
  const dir = e.teams[a.team].dir;
  const dB = hyp(b.x - og, b.y);
  const list = seen(e, a);
  const holderTeam = b.holder >= 0 ? e.ath[b.holder].team : -1;
  // loose ball in my zone and I am closest (as perceived)? go get it
  if (holderTeam < 0 && dB < C.KEEPER_ZONE_R && e.phase === 'live') {
    const myD = hyp(b.x - a.x, b.y - a.y);
    if (opponentsNear(list, a, b.x, b.y) > myD * 0.9) { setTarget(a, b.x, b.y, true); return; }
  }
  if (holderTeam >= 0 && holderTeam !== a.team && dB < 9 && e.phase === 'live') {
    const c = list.find((s) => s.idx === b.holder);
    if (c && !c.frozen) { setTarget(a, c.x, c.y, true); if (hyp(c.x - a.x, c.y - a.y) < 1.45) a.plan.tackle = true; return; }
  }
  const r = Math.min(3.2, 0.8 + dB * 0.06);
  const ang = Math.atan2(b.y, (b.x - og) * dir);
  setTarget(a, og + dir * Math.max(0.6, Math.cos(ang) * r), Math.sin(ang) * r, dB < 25);
}

function archerThink(e: Engine, a: Athlete) {
  const t = e.teams[a.team];
  if (e.phase !== 'live' || e.huntActive || t.arrowsLeft <= 0 || t.freezesLeft <= 0) return;
  if (e.time - a.lastFire < 2.2 + (1 - a.a.archery) * 1.5) return;
  const list = seen(e, a);
  const b = ballGuess(e, a);
  const holderTeam = b.holder >= 0 ? e.ath[b.holder].team : -1;
  let best: Seen | null = null, bestS = 0;
  for (const s of list) {
    if (s.team === a.team || s.role === 'archer' || s.frozen) continue;
    if (e.u(a.team, s.x) >= 50) continue; // own half only
    const dBall = hyp(s.x - b.x, s.y - b.y);
    let sc = 0;
    if (s.idx === b.holder) sc = 3 + (50 - e.u(a.team, s.x)) * 0.04;
    else if (holderTeam !== a.team && dBall < 14) sc = 1.4 - dBall * 0.05;
    else if (holderTeam === a.team && dBall < 4) sc = 1.2; // defender pressuring our carrier
    else if (holderTeam < 0 && dBall < 8) sc = 1.1;
    if (s.role === 'keeper' && e.inKZ(s.x, s.y, e.oppGoalX(a.team))) sc *= 0.3;
    if (sc > bestS) { bestS = sc; best = s; }
  }
  if (!best) return;
  const p = bestS >= 3 ? (e.u(a.team, best.x) < 35 ? 0.4 : 0.15) : 0.04;
  if (e.rng.chance(p)) { a.plan.fire = best.idx; a.lastFire = e.time; }
}

/** Per-step steering: turns the plan + target into an intent (motor command comes from engine). */
export function aiSteer(e: Engine, a: Athlete): Intent {
  const it = NO_INTENT();
  it.pass = a.plan.pass; it.shoot = a.plan.shoot; it.tackle = a.plan.tackle; it.fire = a.plan.fire;
  a.plan.pass = -1; a.plan.shoot = false; a.plan.fire = -1;
  // keep tackle intent while closing (reaction-limited retry)
  if (a.role === 'archer') return it;
  const dx = a.tx - a.x, dy = a.ty - a.y, d = hyp(dx, dy);
  if (d > 0.4) { const s = Math.min(1, d / 2.5); it.mx = dx / d * s; it.my = dy / d * s; }
  it.sprint = a.aiSprint;
  return it;
}
