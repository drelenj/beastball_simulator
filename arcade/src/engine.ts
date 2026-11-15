import league from './league.json';

export const DT = 1 / 60;
export const RULES = Object.freeze({ pitch: 100, goalRadius: 6, keeperZone: 20, penalty: 25, center: 8,
  possession: 45, quarter: 600, carry: 5, release: 3, arrows: 20, loaded: 5, reload: 5, freeze: 5, immunity: 10 });
export type Team = (typeof league.teams)[number];
export type RosterPlayer = Team['players'][number];
export const teams: Team[] = league.teams;
// Project source: positional_tendencies_v1.py GROUP and POS.att_lead.
// This is the existing Beastball position taxonomy, shared by NBL position codes.
export const POSITION_LINE: Record<string, number> = { TRP: 0, GRD: 0, PFD: 1, HNT: 1, TRK: 1, SEN: 1, PDR: 2, STR: 2, SCT: 2 };
const SUPPORT_LEAD: Record<string, number> = { PDR: 10, STR: 18, SCT: 9, PFD: -5, HNT: 0, TRK: 1, SEN: -11, TRP: -9, GRD: -18 };
export type Side = 0 | 1;
export type Mode = 'human' | 'spectator';
export type Phase = 'live' | 'goal' | 'break' | 'final';
export interface Vec { x: number; y: number }
export interface Intent { move: Vec; sprint?: boolean; pass?: boolean; shoot?: boolean; tackle?: boolean; fire?: boolean }
export interface Input { x: number; y: number; sprint: boolean; pass: boolean; shoot: boolean; tackle: boolean; fire: boolean; switch: boolean }
export const blankInput = (): Input => ({ x: 0, y: 0, sprint: false, pass: false, shoot: false, tackle: false, fire: false, switch: false });
export interface PlayerStats { points: number; carries: number; releaseGoals: number; shots: number; passes: number; completions: number; tackleAttempts: number; tackles: number; turnovers: number; saves: number; arrowShots: number; arrowHits: number }
export interface TeamStats extends PlayerStats { possessionTime: number; possessionChanges: number; recoveries: number }
const stats = (): PlayerStats => ({ points: 0, carries: 0, releaseGoals: 0, shots: 0, passes: 0, completions: 0, tackleAttempts: 0, tackles: 0, turnovers: 0, saves: 0, arrowShots: 0, arrowHits: 0 });
export interface Athlete extends Vec { id: number; side: Side; data: RosterPlayer; role: 'field' | 'keeper' | 'archer'; bib: number; vx: number; vy: number; home: Vec; freeze: number; immune: number; protected: number; down: number; cooldown: number; decision: number; intention: Intent; stamina: number; zoneTime: number; animation: number; action: string; stats: PlayerStats }
export interface Ball extends Vec { z: number; vx: number; vy: number; vz: number; carrier: number | null; lastSide: Side; passer: number | null; shooter: number | null; kind: 'loose' | 'pass' | 'shot'; age: number; ignore: number | null }
export interface Arrow extends Vec { z: number; vx: number; vy: number; side: Side; archer: number; age: number; target: number }
export interface Quiver { spent: number; loaded: number; reload: number; cooldown: number }
export interface GameEvent { tick: number; type: string; side: Side | null; player: number | null; text: string; points?: number }
export interface Settings { home: Team; away: Team; mode: Mode; seed: number; clockRate: number }
export const clamp = (v: number, min: number, max: number) => Math.max(min, Math.min(max, v));
export const distance = (a: Vec, b: Vec) => Math.hypot(a.x - b.x, a.y - b.y);
const toward = (a: Vec, b: Vec): Vec => { const d = distance(a, b); return d < .01 ? { x: 0, y: 0 } : { x: (b.x - a.x) / d, y: (b.y - a.y) / d }; };
const segmentDistance = (p: Vec, a: Vec, b: Vec) => {
  const dx = b.x - a.x, dy = b.y - a.y;
  const t = clamp(((p.x - a.x) * dx + (p.y - a.y) * dy) / (dx * dx + dy * dy || 1), 0, 1);
  return Math.hypot(p.x - a.x - t * dx, p.y - a.y - t * dy);
};

/** Providers propose intentions; only Engine applies motion, contacts and rules. */
export class HumanController {
  intent(input: Input): Intent {
    const d = Math.hypot(input.x, input.y) || 1;
    return { move: { x: input.x / d, y: input.y / d }, sprint: input.sprint, pass: input.pass, shoot: input.shoot, tackle: input.tackle, fire: input.fire };
  }
}
export class AIController {
  intent(e: Engine, p: Athlete): Intent {
    const dir = e.direction(p.side), carrier = e.carrier;
    const ownGoal = e.ownGoal(p.side), goal = e.attackGoal(p.side);
    const out: Intent = { move: { x: 0, y: 0 } };
    if (p.role === 'archer') {
      out.move = toward(p, { x: clamp(e.ball.x, 12, 88), y: p.side === 0 ? -7 : 107 });
      out.fire = carrier?.side !== p.side && !!carrier;
      return out;
    }
    if (p.role === 'keeper') {
      if (carrier?.id === p.id) { out.pass = true; return out; }
      const threat = Math.abs(e.ball.x - ownGoal);
      const target = { x: ownGoal + dir * clamp(threat * .16, 1.8, 7), y: clamp(50 + (e.ball.y - 50) * .48, 42, 58) };
      if (!carrier && threat < 18) { target.x = clamp(e.ball.x, ownGoal === 0 ? .5 : 82, ownGoal === 0 ? 18 : 99.5); target.y = clamp(e.ball.y, 34, 66); }
      if (carrier && carrier.side !== p.side && threat < 10 && Math.abs(carrier.y - 50) < 12) {
        target.x = carrier.x; target.y = carrier.y; out.tackle = distance(p, carrier) < 2.8;
      }
      out.move = distance(p, target) > .5 ? toward(p, target) : { x: 0, y: 0 };
      out.sprint = true;
      return out;
    }
    if (carrier?.id === p.id) {
      const opponents = e.players.filter(q => q.side !== p.side && q.role !== 'archer' && q.freeze <= 0 && distance(p, q) < 28);
      const pressure = opponents.filter(q => distance(p, q) < 7).length;
      const dGoal = distance(p, { x: goal, y: 50 });
      // A visible current-state passing lane: no future world or hidden opponent state.
      const target = e.passTarget(p);
      const progress = target ? (target.x - p.x) * dir : 0;
      if (p.cooldown <= 0 && e.ball.age > .55) {
        const shotRange = p.data.Position === 'SCT' ? 30 : POSITION_LINE[p.data.Position] === 0 ? 18 : 25;
        out.shoot = dGoal < shotRange && Math.abs(p.y - 50) < 23 && (pressure > 0 || dGoal > 12 || p.stamina < .35);
        out.pass = !out.shoot && !!target && ((pressure > 0 && progress > -9) || (progress > 8 && e.random() < .5));
      }
      let dx = (goal - p.x) / Math.max(dGoal, 1), dy = (50 - p.y) / Math.max(dGoal, 1);
      for (const q of opponents) {
        const d = distance(p, q);
        if (d < 8 && (q.x - p.x) * dir > -1) {
          dy += (p.y >= q.y ? 1 : -1) * (8 - d) * .2;
          dx -= (q.x - p.x) / Math.max(d, 1) * (8 - d) * .05;
        }
      }
      const m = Math.hypot(dx, dy) || 1;
      out.move = { x: dx / m, y: dy / m }; out.sprint = true;
      return out;
    }
    if (!carrier) {
      const candidates = e.players.filter(q => q.side === p.side && q.role === 'field' && q.freeze <= 0).sort((a, b) => distance(a, e.ball) - distance(b, e.ball) || a.id - b.id);
      if (candidates.slice(0, 3).includes(p)) {
        // Extrapolate only the ball's presently visible velocity.
        out.move = toward(p, { x: clamp(e.ball.x + e.ball.vx * .12, 1, 99), y: clamp(e.ball.y + e.ball.vy * .12, 1, 99) }); out.sprint = true; return out;
      }
    }
    if (carrier && carrier.side !== p.side) {
      const defenders = e.players.filter(q => q.side === p.side && q.role === 'field' && q.freeze <= 0).sort((a, b) => distance(a, carrier) - distance(b, carrier) || a.id - b.id);
      if (defenders.slice(0, 3).includes(p)) {
        const react = .13 + (100 - p.data['Opening-day OVR']) * .002;
        out.move = toward(p, { x: carrier.x + carrier.vx * react, y: carrier.y + carrier.vy * react });
        out.sprint = true; out.tackle = distance(p, carrier) < 2.7; return out;
      }
      const mark = e.players.filter(q => q.side !== p.side && q.role === 'field')[p.bib % 10];
      const target = { x: clamp((mark.x + carrier.x) * .5 + dir * -4, 4, 96), y: mark.y * .7 + carrier.y * .3 };
      out.move = distance(p, target) > 1.2 ? toward(p, target) : { x: 0, y: 0 }; out.sprint = true; return out;
    }
    // Position-specific support lanes, anchored by the canonical formation.
    const advance = carrier ? (carrier.x - 50) * dir : 0;
    const attackBias = SUPPORT_LEAD[p.data.Position] ?? 0;
    const target = { x: clamp(p.home.x + dir * (advance * .6 + attackBias + 14), 7, 93), y: clamp(p.home.y * .62 + e.ball.y * .38, 8, 92) };
    if (carrier) target.x = clamp(carrier.x + dir * (attackBias + (p.bib % 3) * 3), 8, 92);
    out.move = distance(p, target) > 1.5 ? toward(p, target) : { x: 0, y: 0 };
    out.sprint = distance(p, target) > 15;
    return out;
  }
}

export class Engine {
  settings: Settings; players: Athlete[] = []; ball!: Ball; arrows: Arrow[] = [];
  score = [0, 0]; teamStats: TeamStats[] = [{ ...stats(), possessionTime: 0, possessionChanges: 0, recoveries: 0 }, { ...stats(), possessionTime: 0, possessionChanges: 0, recoveries: 0 }];
  quivers: Quiver[] = []; events: GameEvent[] = [];
  tick = 0; liveTicks = 0; quarter = 1; clock = RULES.quarter as number; possessionClock = RULES.possession as number;
  phase: Phase = 'live'; phaseTime = 0; owner: Side | null = null; tackles = 0; selected = 0;
  recovery: { player: number; time: number; x: number; y: number } | null = null;
  rng: number; ai = new AIController(); human = new HumanController();
  constructor(settings: Settings) {
    this.settings = settings; this.rng = settings.seed >>> 0 || 1;
    [settings.home, settings.away].forEach((team, s) => {
      const side = s as Side;
      const roster = team.starters.map(id => team.players.find(p => p['Player ID'] === id)!);
      const field = roster.filter(p => !['ARC', 'KPR'].includes(p.Position));
      const ordered = [...field, roster.find(p => p.Position === 'KPR')!, roster.find(p => p.Position === 'ARC')!];
      if (field.length !== 10 || ordered.some(p => !p)) throw new Error(`Invalid starting lineup: ${team.name}`);
      ordered.forEach((data, i) => {
        this.players.push({ id: this.players.length, side, data, bib: i + 1, role: i === 10 ? 'keeper' : i === 11 ? 'archer' : 'field', x: 0, y: 0, vx: 0, vy: 0, home: { x: 0, y: 0 }, freeze: 0, immune: 0, protected: 0, down: 0, cooldown: 0, decision: 0, intention: { move: { x: 0, y: 0 } }, stamina: 1, zoneTime: 0, animation: 0, action: '', stats: stats() });
      });
    });
    this.newQuarter();
  }
  random() { let t = this.rng += 0x6D2B79F5; t = Math.imul(t ^ t >>> 15, t | 1); t ^= t + Math.imul(t ^ t >>> 7, t | 61); this.rng >>>= 0; return ((t ^ t >>> 14) >>> 0) / 4294967296; }
  get carrier() { return this.ball?.carrier === null ? undefined : this.players[this.ball?.carrier]; }
  direction(side: Side) { return (side === 0 ? 1 : -1) * (this.quarter <= 2 ? 1 : -1); }
  ownGoal(side: Side) { return this.direction(side) === 1 ? 0 : 100; }
  attackGoal(side: Side) { return 100 - this.ownGoal(side); }
  emit(type: string, text: string, side: Side | null = null, player: number | null = null, points?: number) {
    this.events.push({ tick: this.tick, type, text, side, player, ...(points === undefined ? {} : { points }) });
  }
  add(p: Athlete, key: keyof PlayerStats, amount = 1) { p.stats[key] += amount; this.teamStats[p.side][key] += amount; }
  setupFormation(resetEffects = false) {
    for (const side of [0, 1] as Side[]) {
      const t = side === 0 ? this.settings.home : this.settings.away;
      const lines = t.formation.split(/[–-]/).map(Number); let i = 0;
      const field = this.players.filter(p => p.side === side && p.role === 'field')
        .sort((a, b) => POSITION_LINE[a.data.Position] - POSITION_LINE[b.data.Position] || a.id - b.id);
      for (let l = 0; l < 3; l++) for (let j = 0; j < lines[l]; j++) {
        const p = field[i++];
        p.home = { x: this.ownGoal(side) + this.direction(side) * (22 + l * 13), y: 15 + 70 * (j + .5) / lines[l] };
      }
      this.players[side * 12 + 10].home = { x: this.ownGoal(side) + this.direction(side) * 3, y: 50 };
      this.players[side * 12 + 11].home = { x: 50, y: side === 0 ? -7 : 107 };
    }
    for (const p of this.players) {
      p.x = p.home.x; p.y = p.home.y; p.vx = p.vy = 0; p.zoneTime = 0;
      if (resetEffects) p.freeze = p.immune = p.down = 0;
      p.protected = .7; p.cooldown = .4; p.decision = 0; p.action = ''; p.intention = { move: { x: 0, y: 0 } };
    }
  }
  newQuarter() {
    this.clock = RULES.quarter; this.possessionClock = RULES.possession; this.tackles = 0;
    this.quivers = [{ spent: 0, loaded: 5, reload: 0, cooldown: 1 }, { spent: 0, loaded: 5, reload: 0, cooldown: 1 }];
    this.setupFormation(true); this.owner = null; this.recovery = null; this.arrows = [];
    this.ball = { x: 50, y: 50, z: .22, vx: 0, vy: 0, vz: 0, carrier: null, lastSide: 0, passer: null, shooter: null, kind: 'loose', age: 0, ignore: null };
    for (const side of [0, 1] as Side[]) {
      const hunter = this.players[side * 12]; hunter.x = 50 - this.direction(side) * 5; hunter.y = 50;
    }
    this.selected = 0; this.emit('quarter', `Q${this.quarter} · FIRST HUNT`);
  }
  setOwner(side: Side) {
    if (this.owner !== side) {
      if (this.owner !== null) {
        this.teamStats[this.owner].turnovers++;
        this.emit('turnover', 'POSSESSION CHANGE', side);
      }
      this.owner = side; this.tackles = 0; this.possessionClock = RULES.possession;
      this.teamStats[side].possessionChanges++;
    }
  }
  acquire(p: Athlete) {
    const b = this.ball, pass = b.kind === 'pass' && b.passer !== null && p.id !== b.passer;
    if (pass && this.players[b.passer!].side === p.side) { this.add(this.players[b.passer!], 'completions'); this.emit('catch', `${p.data.Player} · CATCH`, p.side, p.id); }
    else if (b.kind !== 'loose' && b.lastSide !== p.side) this.emit('interception', `${p.data.Player} · INTERCEPTION`, p.side, p.id);
    if (p.role === 'keeper' && b.kind === 'shot' && b.lastSide !== p.side) { this.add(p, 'saves'); this.emit('save', `${p.data.Player} · KEEPER SAVE`, p.side, p.id); p.action = 'save'; p.animation = .6; }
    if (b.kind === 'loose') this.teamStats[p.side].recoveries++;
    this.setOwner(p.side); b.carrier = p.id; b.lastSide = p.side; b.kind = 'loose'; b.age = 0; b.passer = null; b.shooter = null;
    b.vx = b.vy = b.vz = 0; p.cooldown = Math.max(.4, p.cooldown); p.protected = Math.max(p.protected, .35);
    if (p.side === 0 && this.settings.mode === 'human') this.selected = p.id;
  }
  restart(side: Side, x?: number, y = 50) {
    this.setupFormation(); this.arrows = []; this.recovery = null;
    this.owner = null; this.setOwner(side);
    const p = this.players.find(p => p.side === side && p.role === 'field' && p.freeze <= 0 && p.down <= 0)
      ?? this.players[side * 12 + 10];
    p.x = x === undefined ? this.ownGoal(side) + this.direction(side) * 40 : clamp(x, 1, 99); p.y = clamp(y, 5, 95);
    for (const q of this.players) if (q.id !== p.id && q.role === 'field' && distance(q, p) < 7) q.x = clamp(p.x - this.direction(q.side) * 8, 2, 98);
    this.ball = { x: p.x, y: p.y, z: 1.3, vx: 0, vy: 0, vz: 0, carrier: null, lastSide: side, passer: null, shooter: null, kind: 'loose', age: 0, ignore: null };
    this.acquire(p); p.protected = 2;
  }
  turnover(reason: string) {
    const prev = this.owner ?? this.ball.lastSide, next = (1 - prev) as Side;
    const x = this.ball.x, y = this.ball.y;
    this.teamStats[prev].turnovers++;
    if (this.carrier) this.carrier.stats.turnovers++;
    this.emit('turnover', reason, next);
    const spot = this.direction(next) > 0 ? Math.max(40, x) : Math.min(60, x);
    this.restart(next, spot, y);
  }
  passTarget(p: Athlete) {
    const candidates = this.players.filter(q => q.side === p.side && q.role === 'field' && q.id !== p.id && q.freeze <= 0 && q.down <= 0 && distance(q, p) > 4 && distance(q, p) < 45);
    const rank = (q: Athlete) => {
      const open = Math.min(16, ...this.players.filter(d => d.side !== p.side && d.role !== 'archer').map(d => distance(d, q)));
      return open * 1.8 + (q.x - p.x) * this.direction(p.side) * .65 - Math.abs(q.y - 50) * .1;
    };
    return candidates.sort((a, b) => rank(b) - rank(a) || a.id - b.id)[0];
  }
  release(p: Athlete, shoot: boolean) {
    if (this.ball.carrier !== p.id || p.cooldown > 0 || p.freeze > 0 || p.down > 0) return;
    const target = shoot ? { x: this.attackGoal(p.side) + this.direction(p.side), y: 50 + (this.random() - .5) * 7 } : this.passTarget(p);
    if (!target) return;
    const rating = p.data['Opening-day OVR'] / 100;
    const d = distance(p, target), flight = Math.max(.23, d / (shoot ? 38 + rating * 7 : 30 + rating * 5));
    const lead = !shoot && 'vx' in target ? target as Athlete : null;
    const error = (1 - rating) * (shoot ? 5 : 2.2);
    const tx = target.x + (lead?.vx ?? 0) * flight * .65 + (this.random() - .5) * error;
    const ty = target.y + (lead?.vy ?? 0) * flight * .65 + (this.random() - .5) * error;
    const z = 1.6, endZ = shoot ? 1.8 + this.random() * 2 : 1.5;
    Object.assign(this.ball, { x: p.x, y: p.y, z, vx: (tx - p.x) / flight, vy: (ty - p.y) / flight, vz: (endZ - z) / flight + 4.905 * flight, carrier: null, lastSide: p.side, passer: shoot ? null : p.id, shooter: shoot ? p.id : null, kind: shoot ? 'shot' : 'pass', age: 0, ignore: p.id });
    this.add(p, shoot ? 'shots' : 'passes'); p.cooldown = .7; p.action = 'throw'; p.animation = .45;
    this.emit(shoot ? 'shot' : 'pass', `${p.data.Player} · ${shoot ? 'RELEASE' : 'PASS'}`, p.side, p.id);
  }
  tackle(p: Athlete) {
    const c = this.carrier;
    if (!c || c.side === p.side || c.role === 'archer' || p.role === 'archer' || p.cooldown > 0 || c.protected > 0 || p.freeze > 0 || p.down > 0 || distance(p, c) > 2.5) return;
    // Keeper protection: no offensive tackle of a Keeper in their own zone.
    if (c.role === 'keeper' && distance(c, { x: this.ownGoal(c.side), y: 50 }) <= 20) return;
    this.add(p, 'tackleAttempts'); p.cooldown = 1.1; p.animation = .4; p.action = 'tackle';
    const chance = clamp(.65 + (p.data['Opening-day OVR'] - c.data['Opening-day OVR']) * .006 + (c.stamina < .35 ? .12 : 0), .3, .9);
    if (this.random() > chance) return;
    this.add(p, 'tackles'); this.emit('tackle', `${p.data.Player} · BIG TACKLE`, p.side, p.id);
    c.down = .8; c.vx = c.vy = 0; this.ball.carrier = null;
    this.ball.x = c.x; this.ball.y = c.y; this.ball.z = .22; this.ball.vx = this.ball.vy = this.ball.vz = 0; this.ball.kind = 'loose'; this.ball.age = 0;
    this.tackles++;
    if (this.tackles >= 2) this.turnover('SECOND TACKLE · TURNOVER');
    else this.recovery = { player: c.id, time: 1.1, x: c.x, y: c.y };
  }
  fire(side: Side) {
    const p = this.players[side * 12 + 11], q = this.quivers[side], target = this.carrier;
    if (!target || target.side === side || target.freeze > 0 || target.immune > 0 || target.protected > 0 || p.freeze > 0 || q.loaded <= 0 || q.reload > 0 || q.cooldown > 0) return;
    if (target.role === 'keeper' && distance(target, { x: this.ownGoal(target.side), y: 50 }) <= RULES.keeperZone) return;
    const range = distance(p, target); if (range < 10 || range > 70) return;
    // Tuned arcade arrow speed, not a canonical physical performance limit.
    const speed = 62;
    const rx = target.x - p.x, ry = target.y - p.y;
    const a = target.vx ** 2 + target.vy ** 2 - speed ** 2;
    const b = 2 * (rx * target.vx + ry * target.vy), c = range ** 2;
    const discriminant = b * b - 4 * a * c;
    const roots = discriminant >= 0 && Math.abs(a) > .001
      ? [(-b + Math.sqrt(discriminant)) / (2 * a), (-b - Math.sqrt(discriminant)) / (2 * a)].filter(t => t > 0)
      : [];
    const time = roots.length ? Math.min(...roots) : range / speed;
    const error = (100 - p.data['Opening-day OVR']) * .055;
    const aim = { x: target.x + target.vx * time + (this.random() - .5) * error, y: target.y + target.vy * time + (this.random() - .5) * error };
    const v = toward(p, aim);
    this.arrows.push({ x: p.x, y: p.y, z: 1.4, vx: v.x * speed, vy: v.y * speed, side, archer: p.id, age: 0, target: target.id });
    this.add(p, 'arrowShots'); q.loaded--; q.spent++; q.cooldown = 2.2; p.action = 'throw'; p.animation = .4;
    this.emit('arrow', `${p.data.Player} · ARROW`, side, p.id);
  }
  goal(side: Side, carried: boolean, player: number | null) {
    const points = carried ? RULES.carry : RULES.release;
    this.score[side] += points;
    if (player !== null) { this.add(this.players[player], 'points', points); this.add(this.players[player], carried ? 'carries' : 'releaseGoals'); }
    else { this.teamStats[side].points += points; this.teamStats[side].releaseGoals++; }
    this.emit('goal', `${carried ? 'CARRY' : 'RELEASE'} GOAL · +${points}`, side, player, points);
    this.phase = 'goal'; this.phaseTime = 1.8; this.ball.carrier = null; this.ball.vx = this.ball.vy = this.ball.vz = 0;
  }
  switchPlayer() {
    const c = this.carrier;
    if (c?.side === 0) { this.selected = c.id; return; }
    const useful = this.players.filter(p => p.side === 0 && p.role === 'field' && p.freeze <= 0 && p.down <= 0).sort((a, b) => distance(a, this.ball) - distance(b, this.ball) || a.id - b.id);
    if (useful.length) this.selected = useful[(useful.findIndex(p => p.id === this.selected) + 1) % Math.min(4, useful.length)].id;
  }
  step(input = blankInput()) {
    if (this.phase === 'final') return;
    this.tick++;
    if (this.phase !== 'live') {
      this.phaseTime -= DT;
      if (this.phaseTime <= 0) {
        if (this.phase === 'goal') { const last = this.events.findLast(e => e.type === 'goal')!; this.restart((1 - last.side!) as Side); this.phase = 'live'; }
        else { this.phase = 'live'; this.newQuarter(); }
      }
      return;
    }
    this.liveTicks++;
    this.clock = Math.max(0, RULES.quarter - this.quarterLiveTicks() * DT * this.settings.clockRate);
    if (this.owner !== null) { this.possessionClock -= DT; this.teamStats[this.owner].possessionTime += DT; }
    if (input.switch) this.switchPlayer();
    if (this.settings.mode === 'human' && !this.carrier && this.players[this.selected].freeze > 0) this.switchPlayer();
    for (const q of this.quivers) {
      q.cooldown = Math.max(0, q.cooldown - DT);
      if (q.reload > 0) { q.reload = Math.max(0, q.reload - DT); if (q.reload === 0) q.loaded = Math.min(5, RULES.arrows - q.spent); }
      if (q.loaded === 0 && q.spent < RULES.arrows && q.reload === 0) q.reload = RULES.reload;
    }
    for (const p of this.players) {
      for (const key of ['freeze', 'immune', 'protected', 'down', 'cooldown', 'animation'] as const) p[key] = Math.max(0, p[key] - DT);
      p.decision -= DT;
      if (this.settings.mode === 'human' && p.id === this.selected) p.intention = this.human.intent(input);
      else if (p.decision <= 0) { p.intention = this.ai.intent(this, p); p.decision = .12 + (100 - p.data['Opening-day OVR']) * .002; }
      if (p.freeze > 0 || p.down > 0) { p.vx = p.vy = 0; continue; }
      this.motor(p);
      if (p.intention.pass) this.release(p, false);
      if (p.intention.shoot) this.release(p, true);
      if (p.intention.tackle) this.tackle(p);
      if (p.role === 'archer' && p.intention.fire && !(p.side === 0 && this.settings.mode === 'human')) this.fire(p.side);
    }
    if (input.fire && this.settings.mode === 'human') this.fire(0);
    this.collisions(); this.updateBall(); this.updateArrows();
    if (this.recovery) {
      this.recovery.time -= DT;
      if (this.recovery.time <= 0) {
        const p = this.players[this.recovery.player]; p.down = 0; this.acquire(p); p.protected = 2; this.recovery = null;
        this.emit('recovery', 'FIRST TACKLE · PROTECTED RECOVERY', p.side, p.id);
      }
    }
    if (this.possessionClock <= 0 && this.phase === 'live') this.turnover('45 SECONDS · TURNOVER');
    if (this.clock <= 0) {
      this.quarterStartLive = this.liveTicks;
      if (this.quarter === 4) { this.phase = 'final'; this.emit('final', 'FULL TIME'); }
      else { this.quarter++; this.phase = 'break'; this.phaseTime = 3; this.emit('break', `END OF Q${this.quarter - 1}`); }
    }
  }
  private quarterStartLive = 0;
  private quarterLiveTicks() { return this.liveTicks - this.quarterStartLive; }
  private motor(p: Athlete) {
    const m = p.intention.move, rating = p.data['Opening-day OVR'] / 100;
    const roleSpeed = p.role === 'keeper' ? .82 : p.role === 'archer' ? .65 : ['SCT', 'PDR', 'STR'].includes(p.data.Position) ? 1.06 : 1;
    const sprint = p.intention.sprint && p.stamina > .12;
    const speed = (13.5 + rating * 5) * roleSpeed * (sprint ? 1.28 : 1) * (.8 + .2 * p.stamina);
    const acceleration = 34 + rating * 9;
    p.vx += clamp(m.x * speed - p.vx, -acceleration * DT, acceleration * DT);
    p.vy += clamp(m.y * speed - p.vy, -acceleration * DT, acceleration * DT);
    p.x += p.vx * DT; p.y += p.vy * DT;
    p.stamina = clamp(p.stamina + (sprint && Math.hypot(p.vx, p.vy) > 4 ? -.013 : .025) * DT, .05, 1);
    if (p.role === 'archer') { p.x = clamp(p.x, 5, 95); p.y = p.side === 0 ? -7 : 107; }
    else {
      if (this.ball.carrier === p.id && (p.y < -.22 || p.y > 100.22)) {
        this.turnover('SIDELINE · TURNOVER'); return;
      }
      p.y = clamp(p.y, .1, 99.9);
      // A controlled whole-ball crossing of the actual goal plane is a carry.
      if (this.ball.carrier === p.id) {
        const goal = this.attackGoal(p.side), crossed = this.direction(p.side) > 0 ? p.x > 100.22 : p.x < -.22;
        const ownCrossed = this.direction(p.side) > 0 ? p.x < -.22 : p.x > 100.22;
        if (ownCrossed) {
          if (Math.hypot(p.y - 50, 1.3) < RULES.goalRadius - .22) this.goal((1 - p.side) as Side, false, null);
          else this.turnover('OWN END LINE · TURNOVER');
          return;
        }
        if (crossed) {
          if (Math.hypot(p.y - 50, 1.3) < RULES.goalRadius - .22) this.goal(p.side, true, p.id);
          else this.turnover('END LINE · TURNOVER');
        }
        if (this.phase === 'live' && distance(p, { x: goal, y: 50 }) < 20) { p.zoneTime += DT; if (p.zoneTime > 5) this.turnover('KEEPER ZONE · FIVE SECONDS'); }
        else p.zoneTime = 0;
      }
      p.x = clamp(p.x, -.3, 100.3);
    }
  }
  private collisions() {
    for (let i = 0; i < this.players.length; i++) for (let j = i + 1; j < this.players.length; j++) {
      const a = this.players[i], b = this.players[j];
      if (a.role === 'archer' || b.role === 'archer' || a.down > 0 || b.down > 0) continue;
      const d = distance(a, b), r = 1.15;
      if (d < r && d > .001) {
        const dx = (a.x - b.x) / d * (r - d) * .5, dy = (a.y - b.y) / d * (r - d) * .5;
        if (a.freeze <= 0) { a.x += dx; a.y += dy; }
        if (b.freeze <= 0) { b.x -= dx; b.y -= dy; }
      }
      if (this.recovery) {
        for (const p of [a, b]) if (p.side !== this.players[this.recovery.player].side && distance(p, this.recovery) < 3) {
          const v = toward(this.recovery, p); p.x = this.recovery.x + v.x * 3; p.y = this.recovery.y + v.y * 3;
        }
      }
    }
  }
  private updateBall() {
    const b = this.ball; b.age += DT;
    if (this.carrier) { b.x = this.carrier.x; b.y = this.carrier.y; b.z = 1.5; return; }
    if (this.recovery || this.phase !== 'live') return;
    const before = { x: b.x, y: b.y }, oldZ = b.z;
    b.x += b.vx * DT; b.y += b.vy * DT; b.z += b.vz * DT; b.vz -= 9.81 * DT;
    if (b.z < .22) { b.z = .22; b.vz = Math.abs(b.vz) > 1.8 ? -b.vz * .48 : 0; b.vx *= .82; b.vy *= .82; if (Math.hypot(b.vx, b.vy) < 1) b.vx = b.vy = 0; }
    const candidates = this.players.filter(p => p.role !== 'archer' && p.freeze <= 0 && p.down <= 0 && !(p.id === b.ignore && b.age < .35) && !(p.id === b.ignore && b.age < 1.2 && b.kind !== 'loose'))
      .filter(p => segmentDistance(p, before, b) < (p.role === 'keeper' ? 2.5 : 1.55) && Math.min(b.z, oldZ) < (p.role === 'keeper' ? 5.4 : 3.3))
      .sort((a, c) => distance(a, before) - distance(c, before) || a.id - c.id);
    for (const p of candidates) {
      if (this.owner !== null && p.side !== this.owner && p.protected > 0) continue;
      if (p.cooldown > .8) continue;
      const chance = b.kind === 'loose' ? 1 : clamp(.62 + p.data['Opening-day OVR'] * .003 - (b.kind === 'shot' && p.role !== 'keeper' ? .32 : 0), .2, .96);
      if (this.random() < chance) { this.acquire(p); return; }
      p.cooldown = .95; // one catch attempt per contact, not a fresh lottery every frame
      p.action = 'save'; p.animation = .4;
    }
    if (b.x < -.22 || b.x > 100.22) {
      const gx = b.x < 0 ? 0 : 100;
      const t = clamp((gx - before.x) / (b.x - before.x || 1), 0, 1);
      const gy = before.y + (b.y - before.y) * t, gz = oldZ + (b.z - oldZ) * t;
      const side = this.attackGoal(0) === gx ? 0 : 1;
      if (Math.hypot(gy - 50, gz) <= RULES.goalRadius - .22) this.goal(side, false, b.lastSide === side ? b.shooter ?? b.passer : null);
      else this.turnover('RELEASE WIDE · TURNOVER');
      return;
    }
    if (b.y < 0 || b.y > 100) this.turnover('SIDELINE · TURNOVER');
  }
  private updateArrows() {
    this.arrows = this.arrows.filter(a => {
      if (this.phase !== 'live') return false;
      const old = { x: a.x, y: a.y }; a.x += a.vx * DT; a.y += a.vy * DT; a.age += DT;
      const hit = this.players.filter(p => p.role !== 'archer' && segmentDistance(p, old, a) < .95).sort((p, q) => distance(p, old) - distance(q, old))[0];
      if (hit) {
        if (hit.side !== a.side && this.ball.carrier === hit.id && hit.immune <= 0 && hit.protected <= 0 && !(hit.role === 'keeper' && distance(hit, { x: this.ownGoal(hit.side), y: 50 }) <= 20)) {
          hit.freeze = RULES.freeze; hit.immune = RULES.freeze + RULES.immunity; hit.vx = hit.vy = 0;
          this.add(this.players[a.archer], 'arrowHits'); this.emit('freeze', `${hit.data.Player} · FROZEN 5s`, a.side, hit.id);
          Object.assign(this.ball, { carrier: null, x: hit.x, y: hit.y, z: .22, vx: (this.random() - .5) * 6, vy: (this.random() - .5) * 6, vz: 2, kind: 'loose', age: 0, ignore: hit.id, passer: null, shooter: null });
        }
        return false;
      }
      return a.age < 2.5 && a.x > -10 && a.x < 110 && a.y > -12 && a.y < 112;
    });
  }
  result() {
    return { seed: this.settings.seed, teams: [this.settings.home.name, this.settings.away.name], score: this.score, phase: this.phase, quarter: this.quarter, tick: this.tick, liveTicks: this.liveTicks, teamStats: this.teamStats, players: this.players.map(p => ({ id: p.data['Player ID'], name: p.data.Player, side: p.side, role: p.role, stats: p.stats })), events: this.events };
  }
}
