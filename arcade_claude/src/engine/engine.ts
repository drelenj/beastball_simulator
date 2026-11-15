// BEASTBALL: ARCADE authoritative engine. Fixed 60 Hz steps, seeded RNG only, no rendering.
// This is a separate TypeScript arcade implementation of the canon, NOT the Python simulator.
import * as C from './constants';
// Deterministic across JS engines: avoid Math.hypot / ** (implementation-dependent rounding).
const hyp = (...v: number[]) => { let s = 0; for (const x of v) s += x * x; return Math.sqrt(s); };
import { Rng } from './rng';
import { Arrow, Athlete, GameEvent, Intent, NO_INTENT, Phase, Settings, TeamData, newStats } from './types';
import { attrsFromOvr, buildLineup, lookFor } from './data';
import { aiThink, aiSteer } from './ai';
import { REACH } from './intercept';

export interface Controller { kind: 'human' | 'ai'; }

export interface TeamState {
  data: TeamData; dir: 1 | -1; score: number; arrowsLeft: number; freezesLeft: number;
  possTime: number; breakdown: { carry: number; thrown: number; half: number; award: number; own: number; points: number };
  human: boolean; selected: number;
}

export interface Ball {
  x: number; y: number; z: number; vx: number; vy: number; vz: number;
  holder: number; lastTouch: number; lastTouchTeam: number;
  passer: number; isShot: boolean; shotTeam: number; releaseDist: number; inFlight: boolean;
  receiver: number; passId: number;   // intended receiver of the pass in flight; id of the current flight (one catch roll per athlete per flight)
}

const dist2 = (ax: number, ay: number, bx: number, by: number) => (ax - bx) * (ax - bx) + (ay - by) * (ay - by);

export class Engine {
  rng: Rng; s: Settings; tick = 0; time = 0;
  teams: [TeamState, TeamState];
  ath: Athlete[] = [];
  ball: Ball;
  arrows: Arrow[] = [];
  events: GameEvent[] = [];
  phase: Phase = 'pregame'; phaseT = 0;
  period = 1; clock: number; playClock = C.PLAY_CLOCK; suddenDeath = false;
  poss = -1; tackleCount = 0; huntActive = false;
  restart: { kind: string; team: number; x: number; y: number; snapper: number } | null = null;
  snapT = 0; winner = -1; possChanges = 0; holderSince = 0;
  breakInfo: { from: number; to: number; len: number; label: string } | null = null;
  flash: { text: string; t: number; team: number } | null = null;
  humanIntent: [Intent | null, Intent | null] = [null, null];
  checkpoints: string[] = [];
  catchFx: { x: number; y: number; z: number; t: number; ok: boolean; team: number }[] = [];

  constructor(home: TeamData, away: TeamData, settings: Settings, human: [boolean, boolean] = [false, false]) {
    this.s = settings;
    this.rng = new Rng(settings.seed);
    this.clock = settings.periodLen;
    const mk = (d: TeamData, dir: 1 | -1, h: boolean): TeamState => ({ data: d, dir, score: 0, arrowsLeft: C.ARROWS_PER_POSS, freezesLeft: C.FREEZES_PER_POSS, possTime: 0, breakdown: { carry: 0, thrown: 0, half: 0, award: 0, own: 0, points: 0 }, human: h, selected: -1 });
    this.teams = [mk(home, 1, human[0]), mk(away, -1, human[1])];
    this.ball = { x: 0, y: 0, z: C.BALL_R, vx: 0, vy: 0, vz: 0, holder: -1, lastTouch: -1, lastTouchTeam: -1, passer: -1, isShot: false, shotTeam: -1, releaseDist: 0, inFlight: false, receiver: -1, passId: 0 };
    [home, away].forEach((td, ti) => {
      const lu = buildLineup(td);
      const add = (p: typeof lu.keeper, role: Athlete['role'], line: number, slotY: number) => {
        const a: Athlete = {
          idx: this.ath.length, team: ti as 0 | 1, d: p, a: attrsFromOvr(p.ovr, p.pos), role, line, slotY,
          x: 0, y: 0, z: 0, vx: 0, vy: 0, facing: 0, intent: NO_INTENT(),
          frozenT: 0, immuneT: 0, recoverT: 0, groundedT: 0, stumbleT: 0, actT: 0, act: '', celebrateT: 0, noCatchT: 0,
          excludedT: 0, dq: false, minors: 0, majors: 0, kzT: 0,
          mem: new Map(), ballMem: { x: 0, y: 0, z: 0, vx: 0, vy: 0, vz: 0, t: -99, holder: -1 }, rolledPass: -1,
          nextThink: 0, tx: 0, ty: 0, aiSprint: false, aiPassAt: 0, plan: NO_INTENT(), lastFire: -99,
          stats: newStats(), look: lookFor(p.id, p.pos),
        };
        this.ath.push(a);
      };
      lu.field.forEach((f) => add(f.p, 'field', f.line, f.slotY));
      add(lu.keeper, 'keeper', -1, 0);
      add(lu.archer, 'archer', -1, 0);
    });
    this.setupHunt();
  }

  // ---------- geometry helpers ----------
  ownGoalX(team: number) { return -C.FIELD_HALF * this.teams[team].dir; }
  oppGoalX(team: number) { return C.FIELD_HALF * this.teams[team].dir; }
  /** distance from own goal along attack axis (0..100) */
  u(team: number, x: number) { return (x - this.ownGoalX(team)) * this.teams[team].dir; }
  xFromU(team: number, u: number) { return this.ownGoalX(team) + u * this.teams[team].dir; }
  active(a: Athlete) { return !a.dq && a.excludedT <= 0; }
  canAct(a: Athlete) { return this.active(a) && a.frozenT <= 0 && a.groundedT <= 0 && a.recoverT <= 0 && a.role !== 'archer'; }
  inKZ(x: number, y: number, goalX: number) { return dist2(x, y, goalX, 0) < C.KEEPER_ZONE_R * C.KEEPER_ZONE_R; }
  keeperImmune(a: Athlete) { return a.role === 'keeper' && this.ball.holder === a.idx && this.inKZ(a.x, a.y, this.ownGoalX(a.team)); }
  ev(type: string, team: number, who: number, text: string, extra: Partial<GameEvent> = {}) {
    this.events.push({ t: this.time, period: this.period, clock: this.clock, type, team, who, text, ...extra });
  }
  say(text: string, team = -1, t = 1.6) { this.flash = { text, t, team }; }

  // ---------- restarts ----------
  placeFormation(team: number, ballU: number, attacking: boolean, minU = 0, maxU = 100) {
    for (const a of this.ath) {
      if (a.team !== team || !this.active(a)) continue;
      if (a.role === 'archer') { this.placeArcher(a); continue; }
      let u: number, y: number;
      if (a.role === 'keeper') { u = 3; y = 0; }
      else {
        const base = [18, 30, 42][a.line] + (attacking ? 6 : 0);
        u = Math.max(minU, Math.min(maxU, base + (ballU - 50) * 0.45));
        y = a.slotY * (a.line === 1 ? 34 : 28);
      }
      a.x = this.xFromU(team, u); a.y = y; a.vx = a.vy = 0;
      a.facing = this.teams[team].dir > 0 ? 0 : Math.PI;
    }
  }
  placeArcher(a: Athlete) {
    a.x = this.ownGoalX(a.team) - this.teams[a.team].dir * C.PLATFORM_BACK; a.y = 0; a.z = C.PLATFORM_H;
    a.facing = this.teams[a.team].dir > 0 ? 0 : Math.PI;
  }
  resetTransient() {
    for (const a of this.ath) { a.groundedT = 0; a.stumbleT = 0; a.kzT = 0; a.celebrateT = 0; a.act = ''; a.noCatchT = 0; }
    this.arrows = [];
  }

  setupHunt() {
    this.resetTransient();
    for (const t of [0, 1]) this.placeFormation(t, 50, false, 0, 38);
    // hunters line up on own 40 m line facing the ball
    for (const t of [0, 1]) {
      const fwd = this.ath.filter((a) => a.team === t && a.role === 'field' && this.active(a)).sort((a, b) => b.a.top - a.a.top).slice(0, 2);
      fwd.forEach((a, i) => { a.x = this.xFromU(t, 40); a.y = i ? 6 : -6; });
    }
    Object.assign(this.ball, { x: 0, y: 0, z: C.BALL_R, vx: 0, vy: 0, vz: 0, holder: -1, passer: -1, isShot: false, inFlight: false, lastTouch: -1, lastTouchTeam: -1 });
    this.poss = -1; this.tackleCount = 0; this.playClock = C.PLAY_CLOCK;
    this.restart = { kind: 'hunt', team: -1, x: 0, y: 0, snapper: -1 };
    this.phase = 'set'; this.phaseT = 1.2; this.huntActive = true;
    this.say(this.period > 4 ? (this.suddenDeath ? 'SUDDEN DEATH — FIRST HUNT' : 'OVERTIME — FIRST HUNT') : `PERIOD ${this.period} — FIRST HUNT`);
  }

  /** Scrimmage for `team` at x (snap). kind: scrimmage | contact | tossin */
  setupSnap(kind: string, team: number, x: number, y: number, snapperIdx = -1, tackler = -1) {
    this.resetTransient();
    x = Math.max(-C.FIELD_HALF + 1, Math.min(C.FIELD_HALF - 1, x));
    y = Math.max(-C.FIELD_HALF + 0.5, Math.min(C.FIELD_HALF - 0.5, y));
    const opp = 1 - team;
    if (kind === 'scrimmage') {
      const bu = this.u(team, x);
      this.placeFormation(team, bu, true, 0, bu - 2);
      this.placeFormation(opp, 100 - bu, false, 0, 100 - bu - 5);
    }
    let snapper = snapperIdx >= 0 ? this.ath[snapperIdx] : undefined;
    if (!snapper || !this.active(snapper) || snapper.role === 'archer') {
      snapper = this.ath.filter((a) => a.team === team && a.role === 'field' && this.active(a))
        .sort((a, b) => dist2(a.x, a.y, x, y) - dist2(b.x, b.y, x, y))[0]
        ?? this.ath.find((a) => a.team === team && a.role === 'keeper')!;
    }
    snapper.x = x; snapper.y = y; snapper.vx = snapper.vy = 0;
    snapper.frozenT = 0; snapper.recoverT = 0;
    const clear = kind === 'tossin' ? C.TOSS_IN_CLEAR : 5;
    for (const a of this.ath) {
      if (a.team !== opp || a.role === 'archer' || !this.active(a)) continue;
      const d = Math.sqrt(dist2(a.x, a.y, x, y));
      if (d < clear) {
        const ang = d > 0.01 ? Math.atan2(a.y - y, a.x - x) : (this.teams[opp].dir > 0 ? Math.PI : 0);
        a.x = x + Math.cos(ang) * clear; a.y = y + Math.sin(ang) * clear;
      }
    }
    if (tackler >= 0) { const t = this.ath[tackler]; t.x = x + this.teams[team].dir * 5; t.y = y; }
    for (const a of this.ath) { a.x = Math.max(-C.FIELD_HALF, Math.min(C.FIELD_HALF, a.x)); a.y = Math.max(-C.FIELD_HALF, Math.min(C.FIELD_HALF, a.y)); }
    this.setHolder(snapper.idx, false);
    this.restart = { kind, team, x, y, snapper: snapper.idx };
    this.phase = 'snap'; this.snapT = C.SNAP_LIMIT; this.huntActive = false;
    snapper.aiPassAt = this.time + 0.8 + this.rng.next() * 1.2;
  }

  // ---------- possession ----------
  setHolder(idx: number, viaPlay: boolean) {
    const a = this.ath[idx];
    const b = this.ball;
    b.holder = idx; b.receiver = -1; this.holderSince = this.time; b.lastTouch = idx; b.lastTouchTeam = a.team; b.inFlight = false; b.vx = b.vy = b.vz = 0;
    if (this.poss !== a.team) this.changePossession(a.team, viaPlay ? 'secured' : 'restart');
  }
  changePossession(team: number, why: string) {
    if (this.poss >= 0 && team !== this.poss) {
      this.possChanges++;
      this.ev('possession', team, -1, `${this.teams[team].data.franchise} gain possession (${why})`);
    }
    this.poss = team; this.tackleCount = 0; this.playClock = C.PLAY_CLOCK;
    for (const t of this.teams) { t.arrowsLeft = C.ARROWS_PER_POSS; t.freezesLeft = C.FREEZES_PER_POSS; }
  }

  // ---------- scoring ----------
  award(team: number, pts: number, kind: string, who: number, text: string, dist = 0) {
    const t = this.teams[team];
    t.score += pts; t.breakdown.points += pts;
    if (kind === 'carry') t.breakdown.carry += pts; else if (kind === 'thrown') t.breakdown.thrown += pts;
    else if (kind === 'half') t.breakdown.half += pts; else if (kind === 'award') t.breakdown.award += pts; else if (kind === 'own') t.breakdown.own += pts;
    if (who >= 0 && this.ath[who].team === team) { this.ath[who].stats.points += pts; if (kind === 'carry' || kind === 'thrown') this.ath[who].stats.goals++; }
    this.ev('score', team, who, text, { pts, kind, dist });
    if (this.suddenDeath) { this.endMatch(); return true; }
    return false;
  }
  goalPoints(kind: 'carry' | 'thrown' | 'own', releaseDist: number) {
    if (this.s.scoring === 'flat') return 2;
    if (kind === 'carry') return 5;
    if (kind === 'own') return 2;
    return releaseDist < 10 ? 2 : releaseDist < 20 ? 3 : 4;
  }

  // ---------- fouls ----------
  foul(a: Athlete, major: boolean, what: string) {
    const name = `${a.d.name} (#${a.d.jersey})`;
    if (major) {
      a.majors++; a.stats.majors++;
      if (a.majors >= 2) { a.dq = true; this.ev('foul', a.team, a.idx, `MAJOR: ${what} — ${name} DISQUALIFIED`); }
      else { a.excludedT = C.MAJOR_EXCL; this.ev('foul', a.team, a.idx, `MAJOR: ${what} — ${name} 120 s exclusion`); }
    } else {
      a.minors++; a.stats.minors++;
      if (a.minors >= 5) { a.dq = true; this.ev('foul', a.team, a.idx, `5th minor: ${what} — ${name} DISQUALIFIED`); }
      else if (a.minors === 4) { a.excludedT = C.MINOR_EXCL; this.ev('foul', a.team, a.idx, `4th minor: ${what} — ${name} 60 s exclusion`); }
      else this.ev('foul', a.team, a.idx, `Minor: ${what} — ${name}`);
    }
    if (!this.active(a)) { if (this.ball.holder === a.idx) this.dropBall(a); a.x = 0; a.y = this.teams[a.team].dir * 0 + (a.team ? 53 : -53); }
    this.say(major ? 'MAJOR FOUL' : 'FOUL', a.team);
  }
  /** Defensive foul against the team in possession. */
  defensiveFoul(a: Athlete, major: boolean, what: string) {
    const off = 1 - a.team;
    const count0 = this.tackleCount === 0;
    this.foul(a, major, what);
    if (this.phase === 'final') return;
    if (count0 && this.poss === off) {
      const full = this.period >= 4;
      const pts = full ? (this.s.scoring === 'flat' ? 2 : 3) : 1;
      const ended = this.award(off, pts, full ? 'award' : 'half', -1, `${this.teams[off].data.franchise}: ${full ? 'full-goal' : 'half-goal'} award (defensive foul at count 0) +${pts}`);
      this.say(full ? 'AWARDED GOAL' : 'HALF GOAL', off);
      if (ended) return;
    }
    const h = this.ball.holder >= 0 ? this.ath[this.ball.holder] : null;
    const bx = h ? h.x : this.ball.x, by = h ? h.y : this.ball.y;
    this.deadBall(1.0, () => this.setupSnap('scrimmage', off, bx, by, h && h.team === off ? h.idx : -1));
  }

  // ---------- dead ball ----------
  pending: (() => void) | null = null;
  deadBall(delay: number, then: () => void) {
    this.phase = 'dead'; this.phaseT = delay; this.pending = then;
    for (const a of this.ath) { a.vx *= 0.3; a.vy *= 0.3; }
  }
  dropBall(a: Athlete) {
    const b = this.ball;
    b.holder = -1; b.x = a.x; b.y = a.y; b.z = 1.0; b.vx = a.vx * 0.5 + this.rng.range(-1, 1); b.vy = a.vy * 0.5 + this.rng.range(-1, 1); b.vz = 1;
    b.inFlight = true; b.isShot = false; b.passer = -1;
    a.noCatchT = 0.6;
  }
  turnover(toTeam: number, x: number, y: number, why: string) {
    this.ev('turnover', toTeam, -1, `Turnover to ${this.teams[toTeam].data.franchise}: ${why}`);
    this.say('TURNOVER', toTeam);
    this.deadBall(1.2, () => this.setupSnap('scrimmage', toTeam, x, y));
  }

  // ---------- actions ----------
  throwBall(a: Athlete, tx: number, ty: number, tz: number, speed: number, isShot: boolean, receiver = -1) {
    const b = this.ball;
    const err = (1 - a.a.acc) * (isShot ? 1.6 : 1.2) * (a.intent.sprint ? 1.4 : 1);
    const d0 = Math.sqrt(dist2(a.x, a.y, tx, ty));
    tx += this.rng.gauss() * err * (0.4 + d0 * 0.05); ty += this.rng.gauss() * err * (0.4 + d0 * 0.05); tz += this.rng.gauss() * err * 0.35;
    const sx = a.x + Math.cos(a.facing) * 0.4, sy = a.y + Math.sin(a.facing) * 0.4, sz = 1.8;
    const dx = tx - sx, dy = ty - sy, dh = Math.sqrt(dx * dx + dy * dy), dz = tz - sz;
    // choose flight time so horizontal speed ~ speed; solve vz for gravity
    const T = Math.max(0.12, dh / speed);
    const vz = dz / T + 0.5 * C.G * T;
    Object.assign(b, { holder: -1, x: sx, y: sy, z: sz, vx: dx / T, vy: dy / T, vz, inFlight: true, passer: a.idx, isShot, shotTeam: a.team, lastTouch: a.idx, lastTouchTeam: a.team });
    b.receiver = receiver; b.passId++;
    b.releaseDist = Math.sqrt(dist2(a.x, a.y, this.oppGoalX(a.team), 0));
    a.act = 'throw'; a.actT = 0.35; a.noCatchT = 0.35;
    if (!isShot) { a.stats.passAtt++; }
    if (this.phase === 'snap') { this.phase = 'live'; this.ev('snap', a.team, a.idx, `${a.d.name} snaps`); }
    if (receiver >= 0) this.ath[receiver].aiPassAt = this.time; // receiver expectation (public cue: call for ball)
  }
  passTo(a: Athlete, r: Athlete) {
    const d = Math.sqrt(dist2(a.x, a.y, r.x, r.y));
    // snappy, flat passes: fast release, low arc (flight ~0.35 s at 10 m, ~0.6 s at 20 m)
    const speed = Math.max(15, Math.min(a.a.throwV * 1.3, 13 + d * 0.95));
    const T = d / speed;
    this.throwBall(a, r.x + r.vx * T * 0.9, r.y + r.vy * T * 0.9, 1.3, speed, false, r.idx);
  }
  shoot(a: Athlete) {
    const gx = this.oppGoalX(a.team);
    const ty = this.rng.range(-1.9, 1.9), tz = this.rng.range(0.5, 1.9);
    const d = Math.sqrt(dist2(a.x, a.y, gx, 0));
    this.throwBall(a, gx + Math.sign(gx) * 0.6, ty, tz, a.a.throwV * 1.3, true);
    this.ev('shot', a.team, a.idx, `${a.d.name} shoots from ${d.toFixed(1)} m`, { dist: d });
  }
  tryTackle(a: Athlete) {
    if (a.stumbleT > 0 || a.actT > 0) return;
    const b = this.ball;
    if (b.holder < 0) return;
    const c = this.ath[b.holder];
    if (c.team === a.team) return;
    const d = Math.sqrt(dist2(a.x, a.y, c.x, c.y));
    if (d > 1.5) return;
    a.act = 'tackle'; a.actT = 0.45;
    if (c.frozenT > 0 || c.recoverT > 0) { this.defensiveFoul(a, true, 'contact with a frozen player'); return; }
    if (this.keeperImmune(c)) { this.defensiveFoul(a, true, 'contact with an immune Keeper'); return; }
    const closing = Math.max(0, ((c.x - a.x) * a.vx + (c.y - a.y) * a.vy) / (d + 0.01));
    const p = Math.max(0.2, Math.min(0.92, 0.5 + (a.a.tackle - c.a.strength) * 0.8 + closing * 0.02 - (c.intent.sprint ? 0.05 : 0)));
    if (this.rng.chance(p)) {
      a.stats.tackles++;
      c.groundedT = 1.4; c.act = 'tackled'; c.actT = 1.4; c.vx *= 0.2; c.vy *= 0.2;
      this.tackleCount++;
      this.ev('tackle', a.team, a.idx, `${a.d.name} grounds ${c.d.name} (tackle ${this.tackleCount})`);
      if (this.tackleCount >= 2) {
        c.stats.turnovers++;
        this.say('BIG HIT — TURNOVER', a.team);
        this.turnover(a.team, c.x, c.y, 'second grounding tackle');
      } else {
        this.say('TACKLE!', a.team, 1.0);
        const cx = c.x, cy = c.y;
        this.deadBall(1.2, () => this.setupSnap('contact', c.team, cx, cy, c.idx, a.idx));
      }
    } else {
      a.stumbleT = 0.9; a.vx *= 0.3; a.vy *= 0.3;
    }
  }
  fireArrow(archer: Athlete, target: Athlete) {
    const t = this.teams[archer.team];
    if (t.arrowsLeft <= 0 || t.freezesLeft <= 0 || archer.actT > 0) return;
    if (!this.arrowLegal(archer, target)) return;
    t.arrowsLeft--; archer.stats.arrows++;
    const d = Math.sqrt(dist2(archer.x, archer.y, target.x, target.y) + (C.PLATFORM_H - 1.2) * (C.PLATFORM_H - 1.2));
    const tof = d / C.ARROW_SPEED;
    const sigma = 0.3 + (1 - archer.a.archery) * 0.8 + d * 0.011;
    const ax = target.x + target.vx * tof + this.rng.gauss() * sigma, ay = target.y + target.vy * tof + this.rng.gauss() * sigma, az = 1.2;
    const dx = ax - archer.x, dy = ay - archer.y, dz = az - C.PLATFORM_H, n = Math.sqrt(dx * dx + dy * dy + dz * dz);
    this.arrows.push({ team: archer.team, x: archer.x, y: archer.y, z: C.PLATFORM_H + 1.2, vx: dx / n * C.ARROW_SPEED, vy: dy / n * C.ARROW_SPEED, vz: dz / n * C.ARROW_SPEED, target: target.idx, life: n / C.ARROW_SPEED + 0.05, tx: ax, ty: ay, resolved: false });
    archer.act = 'throw'; archer.actT = 0.9;
    this.ev('arrow', archer.team, archer.idx, `${archer.d.name} fires at ${target.d.name}`);
  }
  arrowLegal(archer: Athlete, target: Athlete) {
    if (this.phase !== 'live' || this.huntActive) return false;
    if (target.team === archer.team || !this.active(target) || target.role === 'archer') return false;
    if (target.frozenT > 0 || target.immuneT > 0 || target.recoverT > 0) return false;
    // target must be in the Archer's own half
    return this.u(archer.team, target.x) < 50;
  }

  // ---------- main step ----------
  step() {
    if (this.phase === 'final' || this.phase === 'break' || this.phase === 'pregame') return;
    const dt = C.DT;
    this.tick++; this.time += dt;
    if (this.tick % 3600 === 0) this.checkpoints.push(this.hash());
    if (this.catchFx.length) { for (const f of this.catchFx) f.t -= dt; this.catchFx = this.catchFx.filter((f) => f.t > 0); }
    if (this.flash) { this.flash.t -= dt; if (this.flash.t <= 0) this.flash = null; }

    if (this.phase === 'dead') {
      this.phaseT -= dt;
      for (const a of this.ath) this.timers(a, dt);
      this.moveAll(dt, true);
      this.ballPhysics(dt, false);
      if (this.phaseT <= 0 && this.pending) { const p = this.pending; this.pending = null; p(); }
      return;
    }
    if (this.phase === 'set') {
      this.phaseT -= dt;
      if (this.phaseT <= 0) { this.phase = 'live'; this.ev('whistle', -1, -1, 'First Hunt: whistle'); }
      return;
    }

    // intents
    for (const a of this.ath) {
      if (!this.active(a)) { a.intent = NO_INTENT(); continue; }
      const t = this.teams[a.team];
      const hi = this.humanIntent[a.team];
      if (t.human && hi && a.idx === t.selected) a.intent = hi;
      else if (t.human && hi && a.role === 'archer' && hi.fire >= 0) a.intent = { ...NO_INTENT(), fire: hi.fire };
      else {
        if (this.time >= a.nextThink) { aiThink(this, a); a.nextThink = this.time + a.a.react * (0.8 + this.rng.next() * 0.4); }
        a.intent = aiSteer(this, a);
      }
    }
    if (this.humanIntent[0]) this.humanIntent[0] = { ...this.humanIntent[0], pass: -1, shoot: false, tackle: false, fire: -1 };
    if (this.humanIntent[1]) this.humanIntent[1] = { ...this.humanIntent[1], pass: -1, shoot: false, tackle: false, fire: -1 };

    // actions (fixed order: team 0 then 1, by index => deterministic)
    for (const a of this.ath) {
      if (this.phase !== 'live' && this.phase !== 'snap') break;
      if (!this.active(a)) continue;
      const it = a.intent;
      if (a.role === 'archer') { if (it.fire >= 0) this.fireArrow(a, this.ath[it.fire]); continue; }
      if (!this.canAct(a)) continue;
      if (this.ball.holder === a.idx && a.actT <= 0) {
        if (it.shoot && this.phase === 'live') this.shoot(a);
        else if (it.pass >= 0) this.passTo(a, this.ath[it.pass]);
      } else if (it.tackle && this.phase === 'live') this.tryTackle(a);
    }
    if (this.phase !== 'live' && this.phase !== 'snap') return;

    for (const a of this.ath) this.timers(a, dt);
    this.moveAll(dt, false);
    this.arrowsStep(dt);
    if (this.phase !== 'live' && this.phase !== 'snap') return;
    this.ballPhysics(dt, true);
    if (this.phase !== 'live' && this.phase !== 'snap') return;
    this.rules(dt);
  }

  timers(a: Athlete, dt: number) {
    if (a.excludedT > 0) { a.excludedT -= dt; if (a.excludedT <= 0) { a.excludedT = 0; a.x = 0; a.y = a.team ? 49 : -49; this.ev('return', a.team, a.idx, `${a.d.name} returns from exclusion`); } }
    if (a.frozenT > 0) {
      a.frozenT -= dt;
      if (a.frozenT <= 0) { a.frozenT = 0; a.recoverT = C.RECOVERY_TIME; }
    } else if (a.recoverT > 0) {
      a.recoverT -= dt;
      const v = C.RECOVERY_DIST / C.RECOVERY_TIME;
      a.vx = -this.teams[a.team].dir * v; a.vy = 0;
      if (a.recoverT <= 0) { a.recoverT = 0; a.immuneT = C.IMMUNE_TIME; }
    } else if (a.immuneT > 0) a.immuneT = Math.max(0, a.immuneT - dt);
    if (a.groundedT > 0) a.groundedT = Math.max(0, a.groundedT - dt);
    if (a.stumbleT > 0) a.stumbleT = Math.max(0, a.stumbleT - dt);
    if (a.actT > 0) { a.actT -= dt; if (a.actT <= 0) { a.actT = 0; a.act = ''; } }
    if (a.noCatchT > 0) a.noCatchT -= dt;
    if (a.celebrateT > 0) a.celebrateT -= dt;
  }

  moveAll(dt: number, dead: boolean) {
    for (const a of this.ath) {
      if (!this.active(a) || a.role === 'archer') continue;
      if (a.frozenT > 0) { a.vx = a.vy = 0; continue; }
      if (a.recoverT > 0) { a.x += a.vx * dt; a.y += a.vy * dt; this.clampField(a); continue; }
      const snapper = this.phase === 'snap' && this.ball.holder === a.idx;
      let tvx = 0, tvy = 0;
      if (!dead && a.groundedT <= 0 && !snapper) {
        const it = a.intent; const m = hyp(it.mx, it.my);
        if (m > 0.05) {
          let sp = a.a.top * (it.sprint ? 1 : 0.68) * (this.ball.holder === a.idx ? 0.94 : 1);
          if (a.stumbleT > 0) sp *= 0.3;
          tvx = it.mx / Math.max(1, m) * sp; tvy = it.my / Math.max(1, m) * sp;
        }
      }
      const acc = (dead ? 8 : a.a.accel) * dt;
      const dvx = tvx - a.vx, dvy = tvy - a.vy, dv = hyp(dvx, dvy);
      if (dv > acc) { a.vx += dvx / dv * acc; a.vy += dvy / dv * acc; } else { a.vx = tvx; a.vy = tvy; }
      a.x += a.vx * dt; a.y += a.vy * dt;
      const sp = hyp(a.vx, a.vy);
      if (sp > 0.6) a.facing = Math.atan2(a.vy, a.vx);
      else if (this.ball.holder !== a.idx && a.ballMem.t > -50) a.facing = Math.atan2(a.ballMem.y - a.y, a.ballMem.x - a.x);
      if (this.ball.holder !== a.idx) this.clampField(a, 2.5);
    }
    // simple separation so athletes do not overlap (deterministic order)
    for (let i = 0; i < this.ath.length; i++) {
      const a = this.ath[i]; if (!this.active(a) || a.role === 'archer') continue;
      for (let j = i + 1; j < this.ath.length; j++) {
        const b = this.ath[j]; if (!this.active(b) || b.role === 'archer') continue;
        const dx = b.x - a.x, dy = b.y - a.y, d2 = dx * dx + dy * dy;
        if (d2 < 0.49 && d2 > 1e-6) { const d = Math.sqrt(d2), push = (0.7 - d) / 2; a.x -= dx / d * push; a.y -= dy / d * push; b.x += dx / d * push; b.y += dy / d * push; }
      }
    }
  }
  clampField(a: Athlete, margin = 0) {
    const L = C.FIELD_HALF + margin;
    a.x = Math.max(-L, Math.min(L, a.x)); a.y = Math.max(-L, Math.min(L, a.y));
  }

  arrowsStep(dt: number) {
    for (const ar of this.arrows) {
      if (ar.resolved) { ar.life -= dt; continue; }
      const px = ar.x, py = ar.y;
      ar.x += ar.vx * dt; ar.y += ar.vy * dt; ar.z += ar.vz * dt; ar.life -= dt;
      // closest approach to target body segment this step
      const t = this.ath[ar.target];
      const sx = ar.x - px, sy = ar.y - py, sl = sx * sx + sy * sy;
      let k = sl > 0 ? ((t.x - px) * sx + (t.y - py) * sy) / sl : 0; k = Math.max(0, Math.min(1, k));
      const cx = px + sx * k, cy = py + sy * k;
      const hit = dist2(cx, cy, t.x, t.y) < 0.42 * 0.42 && ar.z < 2.2 + 1.0;
      if (hit || ar.life <= 0 || ar.z <= 0) {
        ar.resolved = true; ar.life = 0.25;
        const archer = this.ath.find((a) => a.team === ar.team && a.role === 'archer')!;
        if (hit && t.frozenT <= 0 && t.immuneT <= 0 && t.recoverT <= 0 && this.active(t) && this.teams[ar.team].freezesLeft > 0) {
          this.teams[ar.team].freezesLeft--;
          archer.stats.arrowHits++;
          t.frozenT = C.FREEZE_TIME; t.vx = t.vy = 0; t.act = 'frozen';
          ar.x = t.x; ar.y = t.y;
          this.ev('freeze', ar.team, archer.idx, `ARROW HIT: ${t.d.name} frozen 5 s`);
          this.say('ARROW HIT — FROZEN', ar.team, 1.2);
          if (this.ball.holder === t.idx) this.dropBall(t);
        }
      }
    }
    this.arrows = this.arrows.filter((a) => a.life > 0);
  }

  ballPhysics(dt: number, live: boolean) {
    const b = this.ball;
    if (b.holder >= 0) {
      const h = this.ath[b.holder];
      const px = b.x;
      b.x = h.x + Math.cos(h.facing) * 0.35; b.y = h.y + Math.sin(h.facing) * 0.35; b.z = 1.1;
      if (live && this.phase === 'live') this.checkCarryGoal(h, px);
      return;
    }
    const px = b.x, py = b.y, pz = b.z;
    b.vz -= C.G * dt;
    b.x += b.vx * dt; b.y += b.vy * dt; b.z += b.vz * dt;
    if (b.z < C.BALL_R) {
      b.z = C.BALL_R;
      if (Math.abs(b.vz) > 1.2) { b.vz = -b.vz * 0.45; b.vx *= 0.75; b.vy *= 0.75; }
      else { b.vz = 0; b.vx *= Math.max(0, 1 - 2.2 * dt); b.vy *= Math.max(0, 1 - 2.2 * dt); b.inFlight = false; }
      b.isShot = b.isShot && hyp(b.vx, b.vy) > 4;
    }
    if (!live) return;
    // goal plane crossing
    for (const gx of [-C.FIELD_HALF, C.FIELD_HALF]) {
      if ((px - gx) * (b.x - gx) < 0 || (b.x === gx && px !== gx)) {
        const k = (gx - px) / (b.x - px);
        const cy = py + (b.y - py) * k, cz = pz + (b.z - pz) * k;
        if (hyp(cy, cz) <= C.GOAL_R - C.BALL_R) { this.goalScored(gx, -1, cy, cz); return; }
        // keeper/ net miss -> out of play behind
      }
    }
    if (Math.abs(b.x) > C.FIELD_HALF + 0.3 || Math.abs(b.y) > C.FIELD_HALF + 0.3) { this.outOfPlay(px, py); return; }
    this.catches(px, py, pz);
  }

  /**
   * Catch resolution. The ball path of this step is swept against every athlete's reach (so fast balls
   * cannot tunnel), each athlete gets ONE catch roll per flight, and the intended receiver has a longer
   * reach and a much better chance than a defender trying to intercept.
   */
  catches(px: number, py: number, pz: number) {
    const b = this.ball;
    if (b.holder >= 0) return;
    const sp = hyp(b.vx, b.vy, b.vz);
    const sx = b.x - px, sy = b.y - py, sz = b.z - pz, sl = sx * sx + sy * sy;
    let best: Athlete | null = null, bestScore = 1e9, bestD = 0, bestZ = 0;
    for (const a of this.ath) {
      if (!this.canAct(a) || a.noCatchT > 0 || a.stumbleT > 0 || a.rolledPass === b.passId) continue;
      const keeper = a.role === 'keeper';
      const intended = a.idx === b.receiver;
      const reachH = (keeper ? REACH.keeper : REACH.field) + (intended ? REACH.intendedBonus : 0), reachZ = keeper ? REACH.zKeeper : REACH.z;
      let k = sl > 1e-9 ? ((a.x - px) * sx + (a.y - py) * sy) / sl : 1; k = Math.max(0, Math.min(1, k));
      const cx = px + sx * k, cy = py + sy * k, cz = pz + sz * k;
      if (cz > reachZ || cz < -0.2) continue;
      const d = Math.sqrt(dist2(a.x, a.y, cx, cy));
      if (d >= reachH) continue;
      const score = d - (intended ? 0.6 : 0);   // the target of the pass gets first claim on it
      if (score < bestScore) { best = a; bestScore = score; bestD = d; bestZ = cz; }
    }
    if (!best) return;
    const a = best;
    a.rolledPass = b.passId;
    const intended = a.idx === b.receiver;
    const passer = b.passer >= 0 ? this.ath[b.passer] : null;
    const ownPass = !!passer && passer.team === a.team && !b.isShot;
    const ground = bestZ < 0.35 && sp < 8;
    let p: number;
    if (ground) p = 0.9 + a.a.catchS * 0.08;
    else if (ownPass) {
      // a teammate's pass: reliable, worse when the throw is very hard, off-line, or the receiver is marked
      let covered = 0;
      for (const o of this.ath) if (o.team !== a.team && o.role !== 'archer' && this.canAct(o) && dist2(o.x, o.y, a.x, a.y) < 1.8 * 1.8) { covered = 1; break; }
      p = (intended ? 0.8 : 0.62) + a.a.catchS * (intended ? 0.18 : 0.3) - Math.max(0, sp - 27) * 0.015 - Math.max(0, bestD - 0.8) * 0.1 - covered * 0.12;
      p = Math.max(0.55, p);
    } else {
      p = a.a.catchS - Math.max(0, sp - (b.isShot ? 16 : 27)) * 0.02 - bestD * 0.15;
      if (b.isShot && a.team !== b.shotTeam) p = a.role === 'keeper' ? a.a.catchS * 0.85 : p * 0.6;
      else if (!b.isShot) p *= 0.8; // interceptions are harder than catching your own side's pass
    }
    if (this.rng.chance(Math.max(0.05, Math.min(0.97, p)))) {
      const wasShot = b.isShot && b.shotTeam !== a.team;
      if (passer && passer.idx !== a.idx && !b.isShot) {
        if (passer.team === a.team) { passer.stats.passComp++; if (intended) this.ev('catch', a.team, a.idx, `${a.d.name} catches the pass`); }
        else { a.stats.interceptions++; passer.stats.turnovers++; this.ev('interception', a.team, a.idx, `${a.d.name} intercepts`); this.say('INTERCEPTED', a.team, 1.1); }
      }
      if (wasShot && a.role === 'keeper') { a.stats.saves++; this.ev('save', a.team, a.idx, `${a.d.name} saves`); this.say('KEEPER SAVE', a.team, 1.1); }
      else if (wasShot) this.ev('block', a.team, a.idx, `${a.d.name} blocks the shot`);
      if (this.huntActive && this.poss < 0) this.ev('hunt', a.team, a.idx, `${a.d.name} wins the First Hunt`);
      b.passer = -1; b.isShot = false;
      a.act = 'catch'; a.actT = 0.4;
      this.catchFx.push({ x: a.x, y: a.y, z: Math.max(0.8, bestZ), t: 0.4, ok: true, team: a.team });
      this.setHolder(a.idx, true);
    } else {
      // dropped: the ball pops off the hands; everybody else gets a fresh chance at it
      a.noCatchT = 0.4; b.passId++; b.receiver = -1;
      this.catchFx.push({ x: a.x, y: a.y, z: Math.max(0.8, bestZ), t: 0.55, ok: false, team: a.team });
      if (b.isShot && a.role === 'keeper' && a.team !== b.shotTeam) { a.stats.saves++; this.ev('save', a.team, a.idx, `${a.d.name} parries`); this.say('PARRIED', a.team, 1.0); b.isShot = false; }
      else if (ownPass) this.ev('drop', a.team, a.idx, `${a.d.name} drops the pass`);
      b.vx = -b.vx * 0.2 + this.rng.range(-2, 2); b.vy = b.vy * 0.25 + this.rng.range(-2.5, 2.5); b.vz = Math.abs(b.vz) * 0.3 + 1.5;
      b.lastTouch = a.idx; b.lastTouchTeam = a.team;
    }
  }

  checkCarryGoal(h: Athlete, px: number) {
    const b = this.ball;
    for (const gx of [-C.FIELD_HALF, C.FIELD_HALF]) {
      if ((px - gx) * (b.x - gx) < 0) {
        if (Math.abs(b.y) <= C.GOAL_R - C.BALL_R && b.z <= C.GOAL_R - C.BALL_R) { this.goalScored(gx, h.idx, b.y, b.z); return; }
      }
    }
    if (Math.abs(h.x) > C.FIELD_HALF || Math.abs(h.y) > C.FIELD_HALF) { b.lastTouch = h.idx; b.lastTouchTeam = h.team; this.outOfPlay(h.x, h.y); }
  }

  goalScored(gx: number, carrier: number, y: number, z: number) {
    const b = this.ball;
    const defending = this.ownGoalX(0) === gx ? 0 : 1;
    const scoring = 1 - defending;
    const toucher = carrier >= 0 ? carrier : b.lastTouch;
    const tTeam = carrier >= 0 ? this.ath[carrier].team : b.lastTouchTeam;
    let kind: 'carry' | 'thrown' | 'own' = carrier >= 0 ? 'carry' : 'thrown';
    if (tTeam === defending) kind = 'own';
    const pts = this.goalPoints(kind, b.releaseDist);
    const who = kind === 'own' ? -1 : toucher;
    const name = toucher >= 0 ? this.ath[toucher].d.name : 'unknown';
    const desc = kind === 'carry' ? 'carried goal' : kind === 'own' ? `own goal (${name})` : `thrown goal from ${b.releaseDist.toFixed(1)} m`;
    if (b.isShot === false && kind === 'thrown') { /* deflected/pass into goal still counts as thrown */ }
    const ended = this.award(scoring, pts, kind, who, `GOAL ${this.teams[scoring].data.franchise}: ${name} — ${desc} +${pts}`, kind === 'carry' ? 0 : b.releaseDist);
    this.say(`GOAL! +${pts}`, scoring, 2.2);
    for (const a of this.ath) if (a.team === scoring && a.role !== 'archer') a.celebrateT = 2.2;
    b.holder = -1; b.vx *= 0.1; b.vy *= 0.1; b.x = gx; b.y = y; b.z = Math.max(C.BALL_R, z);
    if (ended) return;
    this.deadBall(2.4, () => this.setupSnap('scrimmage', defending, this.xFromU(defending, C.SCRIM_LINE), 0));
  }

  outOfPlay(x: number, y: number) {
    const b = this.ball;
    const toTeam = b.lastTouchTeam >= 0 ? 1 - b.lastTouchTeam : (this.poss >= 0 ? 1 - this.poss : 0);
    const cx = Math.max(-C.FIELD_HALF, Math.min(C.FIELD_HALF, x)), cy = Math.max(-C.FIELD_HALF, Math.min(C.FIELD_HALF, y));
    b.holder = -1; b.vx = b.vy = b.vz = 0; b.x = cx; b.y = cy;
    this.ev('out', toTeam, -1, `Out of play — toss-in ${this.teams[toTeam].data.franchise}`);
    this.say('OUT OF PLAY', toTeam, 1.0);
    this.deadBall(1.0, () => this.setupSnap('tossin', toTeam, cx, cy));
  }

  rules(dt: number) {
    const b = this.ball;
    if (this.phase === 'snap') {
      this.snapT -= dt;
      if (this.snapT <= 0) {
        // delay of game: offence minor => tackle count +1
        const s = this.ath[b.holder];
        this.foul(s, false, 'delay of game');
        this.tackleCount++;
        if (this.tackleCount >= 2) { this.turnover(1 - s.team, s.x, s.y, 'delay of game at tackle count 1'); return; }
        this.setupSnap(this.restart?.kind ?? 'scrimmage', s.team, s.x, s.y, this.active(s) ? s.idx : -1);
      }
      return;
    }
    // live: clocks
    this.clock -= dt;
    if (this.poss >= 0) this.teams[this.poss].possTime += dt;
    if (this.huntActive && hyp(b.x, b.y) > C.CENTRE_CIRCLE_R) this.huntActive = false;
    if (this.poss >= 0 && !this.huntActive) {
      this.playClock -= dt;
      if (this.playClock <= 0) {
        const opp = 1 - this.poss;
        const bx = b.holder >= 0 ? this.ath[b.holder].x : b.x, by = b.holder >= 0 ? this.ath[b.holder].y : b.y;
        // scrimmage at the spot or the new team's own 40 m line, whichever is closer to the goal it attacks
        const uSpot = this.u(opp, bx);
        const x = uSpot >= C.SCRIM_LINE ? bx : this.xFromU(opp, C.SCRIM_LINE);
        if (b.holder >= 0) this.ath[b.holder].stats.turnovers++;
        this.turnover(opp, x, uSpot >= C.SCRIM_LINE ? by : 0, 'play clock expired');
        return;
      }
    }
    // keeper zone: attackers at most 5 s at a time
    if (this.poss >= 0) {
      const def = 1 - this.poss, gx = this.ownGoalX(def);
      for (const a of this.ath) {
        if (a.team !== this.poss || !this.active(a) || a.role !== 'field') { a.kzT = 0; continue; }
        if (this.inKZ(a.x, a.y, gx)) {
          a.kzT += dt;
          if (a.kzT > C.KZ_ATTACKER_LIMIT) {
            this.turnover(def, this.xFromU(def, 20), 0, `${a.d.name} over 5 s in the Keeper Zone`);
            if (b.holder >= 0) this.ath[b.holder].stats.turnovers++;
            return;
          }
        } else a.kzT = 0;
      }
    }
    // occasional holding minor by a tight-marking defender (AI only, skill dependent)
    if (this.poss >= 0 && b.holder >= 0 && this.tick % 30 === 0) {
      for (const a of this.ath) {
        if (a.team === this.poss || a.role !== 'field' || !this.canAct(a) || this.teams[a.team].human && a.idx === this.teams[a.team].selected) continue;
        for (const o of this.ath) {
          if (o.team !== this.poss || o.idx === b.holder || !this.canAct(o)) continue;
          if (dist2(a.x, a.y, o.x, o.y) < 1.0 && this.rng.chance(0.006 * (1.2 - a.a.tackle))) { this.defensiveFoul(a, false, `holding ${o.d.name} (non-carrier)`); return; }
        }
      }
    }
    if (this.clock <= 0 && !this.suddenDeath) this.endPeriod();
  }

  endPeriod() {
    this.clock = 0;
    const [a, b] = [this.teams[0].score, this.teams[1].score];
    this.ev('period_end', -1, -1, `End of ${this.periodName()} ${a}-${b}`);
    if (this.period >= 4 && a !== b) { this.endMatch(); return; }
    const from = this.period;
    if (this.period === 4) { this.period = 5; this.clock = this.s.otLen; }
    else if (this.period === 5) { this.period = 6; this.suddenDeath = true; this.clock = 0; }
    else { this.period++; this.clock = this.s.periodLen; }
    const len = from === 2 ? C.BREAK_HALF : C.BREAK_SHORT;
    this.breakInfo = { from, to: this.period, len, label: from === 2 ? 'HALFTIME' : from >= 4 ? 'BEFORE OVERTIME' : `END OF PERIOD ${from}` };
    this.phase = 'break';
  }
  /** Called by UI (or headless) to finish the break: ends exchanged, First Hunt. */
  resumeFromBreak() {
    if (this.phase !== 'break') return;
    for (const t of this.teams) t.dir = (t.dir * -1) as 1 | -1;
    for (const a of this.ath) if (a.role === 'archer') this.placeArcher(a);
    this.breakInfo = null;
    this.setupHunt();
  }
  endMatch() {
    this.phase = 'final';
    const [a, b] = [this.teams[0].score, this.teams[1].score];
    this.winner = a > b ? 0 : b > a ? 1 : -1;
    this.ev('final', this.winner, -1, `FINAL ${this.teams[0].data.franchise} ${a} - ${b} ${this.teams[1].data.franchise}`);
    this.say('FINAL', this.winner, 99);
  }
  periodName() { return this.period <= 4 ? `P${this.period}` : this.period === 5 ? 'OT' : 'SD'; }

  /** Deterministic state hash for reproducibility checks. */
  hash(): string {
    let h = 2166136261;
    const mix = (v: number) => { h ^= Math.round(v * 1000) | 0; h = Math.imul(h, 16777619); };
    mix(this.tick); mix(this.teams[0].score); mix(this.teams[1].score); mix(this.ball.x); mix(this.ball.y); mix(this.ball.z);
    for (const a of this.ath) { mix(a.x); mix(a.y); mix(a.vx); mix(a.vy); }
    mix(this.rng.state());
    return (h >>> 0).toString(16).padStart(8, '0');
  }
}
