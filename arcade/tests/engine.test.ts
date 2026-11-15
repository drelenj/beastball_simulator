import { test } from 'node:test';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { writeFileSync } from 'node:fs';
import { Engine, teams, DT, RULES, blankInput, POSITION_LINE } from '../src/engine';
import { FixedStepper } from '../src/timing';

const settings = { home: teams.find(t => t.name === 'Ala Marauders')!, away: teams.find(t => t.name === 'Xenar Ignite')!, mode: 'spectator' as const, seed: 202627, clockRate: 1 };
const digest = (e: Engine) => createHash('sha256').update(JSON.stringify(e.result())).digest('hex');
function fixture() {
  const e = new Engine({ ...settings, mode: 'human', seed: 1 });
  for (const p of e.players) { p.x = 10; p.y = 10; p.down = 999; p.decision = 999; p.protected = 0; p.intention = { move: { x: 0, y: 0 } }; p.cooldown = 0; }
  const p = e.players[0]; p.x = 50; p.y = 50; p.down = 0;
  e.acquire(p); p.cooldown = 0; p.protected = 0;
  return e;
}
function run(e: Engine, ticks: number, input = blankInput()) { for (let i = 0; i < ticks; i++) e.step(input); }
function full(clockRate: number, speed = 1, fps = 60) {
  const e = new Engine({ ...settings, clockRate }); const scheduler = new FixedStepper();
  let frames = 0;
  while (e.phase !== 'final' && frames++ < 300000) scheduler.advance(1 / fps, speed, () => e.step());
  assert.equal(e.phase, 'final'); return e;
}

test('all 712 original athletes, 26 franchises and 24 correct starting athletes per match', () => {
  assert.equal(teams.length, 26); assert.equal(teams.reduce((n, t) => n + t.players.length, 0), 712);
  for (const t of teams) {
    const e = new Engine({ ...settings, home: t });
    assert.equal(e.players.length, 24);
    const ps = e.players.filter(p => p.side === 0);
    assert.equal(ps.filter(p => p.role === 'field').length, 10);
    assert.equal(ps.filter(p => p.role === 'keeper').length, 1);
    assert.equal(ps.filter(p => p.role === 'archer').length, 1);
    assert.ok(ps.every(p => p.data['Opening-night role'] === 'Projected starter'));
    assert.deepEqual(new Set(ps.map(p => p.data['Player ID'])), new Set(t.starters));
    const formationOrder = ps.filter(p => p.role === 'field').sort((a, b) => a.home.x - b.home.x);
    const groups = formationOrder.map(p => POSITION_LINE[p.data.Position]);
    assert.deepEqual(groups, [...groups].sort());
  }
  assert.equal(settings.home.players.find(p => p.Player === 'Kamasi Sinella')!['Opening-day OVR'], 90);
  assert.equal(settings.away.players.find(p => p.Player === 'Xavier Flameguard')!['Opening-day OVR'], 71);
});
test('human intention produces immediate acceleration, sprint and braking', () => {
  const jog = fixture(), sprint = fixture();
  const i = { ...blankInput(), x: 1 }; jog.step(i); assert.ok(jog.players[0].vx > 0);
  run(jog, 59, i); run(sprint, 60, { ...i, sprint: true });
  assert.ok(sprint.players[0].x > jog.players[0].x + .4);
  const speed = jog.players[0].vx; jog.step(); assert.ok(jog.players[0].vx < speed);
});
test('pass flight resolves a catch and transfers possession and selection', () => {
  const e = fixture(), target = e.players[1]; target.x = 65; target.y = 50; target.down = 0;
  e.step({ ...blankInput(), pass: true });
  assert.equal(e.ball.kind, 'pass'); assert.equal(e.ball.carrier, null); assert.equal(e.teamStats[0].passes, 1);
  run(e, 60); assert.equal(e.ball.carrier, target.id); assert.equal(e.selected, target.id);
  assert.equal(e.teamStats[0].completions, 1); assert.ok(e.events.some(x => x.type === 'catch'));
});
test('legal tackles preserve first recovery, protect it, and turn over on second', () => {
  const e = fixture(), defender = e.players[12], carrier = e.players[0];
  defender.x = 51; defender.y = 50; defender.down = 0;
  for (let n = 0; n < 20 && !e.recovery; n++) { defender.cooldown = 0; e.tackle(defender); }
  assert.ok(e.recovery); assert.equal(e.tackles, 1); assert.equal(e.ball.carrier, null);
  run(e, 70); assert.equal(e.ball.carrier, carrier.id); assert.ok(carrier.protected > 0);
  const attempts = defender.stats.tackleAttempts; defender.cooldown = 0; e.tackle(defender); assert.equal(defender.stats.tackleAttempts, attempts);
  carrier.protected = 0; defender.x = carrier.x + 1; defender.y = carrier.y;
  for (let n = 0; n < 20 && e.owner === 0; n++) { defender.cooldown = 0; e.tackle(defender); }
  assert.equal(e.owner, 1); assert.ok(e.events.some(x => x.text.includes('SECOND TACKLE')));
});
test('goal crossings award 5 carry / 3 release; own goals award release value', () => {
  const carry = fixture(); carry.players[0].x = 99.9; carry.players[0].vx = 10;
  for (let n = 0; n < 60 && carry.phase === 'live'; n++) carry.step({ ...blankInput(), x: 1 });
  assert.equal(carry.score[0], 5); assert.equal(carry.players[0].stats.points, 5);
  const release = fixture(); release.players[0].x = 78; release.release(release.players[0], true);
  for (let n = 0; n < 120 && release.phase === 'live'; n++) release.step();
  assert.equal(release.score[0], 3); assert.equal(release.teamStats[0].releaseGoals, 1);
  const own = fixture(); own.players[0].x = .1; own.players[0].vx = -10;
  for (let n = 0; n < 60 && own.phase === 'live'; n++) own.step({ ...blankInput(), x: -1 });
  assert.deepEqual(own.score, [0, 3]);
});
test('wide shots and side boundaries do not score', () => {
  const e = fixture(); Object.assign(e.ball, { x: 99.9, y: 70, z: 2, vx: 40, vy: 0, vz: 0, carrier: null, kind: 'shot', shooter: 0 });
  e.step(); assert.deepEqual(e.score, [0, 0]); assert.equal(e.owner, 1);
  const side = fixture(); side.players[0].y = 99.9; side.players[0].vy = 20; side.step({ ...blankInput(), y: 1 });
  assert.equal(side.owner, 1); assert.ok(side.events.some(x => x.text.includes('SIDELINE')));
});
test('Keeper catches an actual incoming scoring flight', () => {
  const e = fixture(), keeper = e.players[22]; keeper.x = 98; keeper.y = 50; keeper.down = 0;
  Object.assign(e.ball, { x: 95, y: 50, z: 2, vx: 35, vy: 0, vz: 0, carrier: null, lastSide: 0, kind: 'shot', shooter: 0, age: 1 });
  run(e, 12); assert.equal(e.ball.carrier, keeper.id); assert.equal(keeper.stats.saves, 1); assert.equal(e.owner, 1);
});
test('Archer projectile freezes carrier, displaces ball and grants timed immunity', () => {
  const e = fixture(), p = e.players[0], archer = e.players[23]; p.y = 70; archer.x = 50; archer.y = 107; archer.down = 0;
  e.quivers[1].cooldown = 0; e.fire(1); assert.equal(e.arrows.length, 1); assert.equal(e.quivers[1].loaded, 4);
  run(e, 45); assert.ok(p.freeze > 4); assert.ok(p.immune > 14); assert.equal(e.ball.carrier, null);
  assert.equal(archer.stats.arrowHits, 1); assert.equal(e.teamStats[1].arrowShots, 1);
  const immune = p.immune; run(e, 320); assert.equal(p.freeze, 0); assert.ok(p.immune > 0 && p.immune < immune);
  run(e, 600); assert.equal(p.immune, 0);
});
test('quivers reload in five seconds and never exceed 20 arrows a quarter', () => {
  const e = fixture(), q = e.quivers[0]; q.loaded = 0; q.spent = 5; q.cooldown = 999;
  e.step(); assert.equal(q.reload, RULES.reload); run(e, 301); assert.equal(q.loaded, 5);
  q.loaded = 0; q.spent = 20; q.reload = 0; run(e, 320); assert.equal(q.loaded, 0); assert.equal(q.reload, 0);
});
test('freezes and immunity survive possession restarts; frozen athletes cannot receive a restart', () => {
  const e = fixture(), p = e.players[12]; p.freeze = 4; p.immune = 14; p.down = 0;
  e.restart(1); assert.equal(p.freeze, 4); assert.equal(p.immune, 14);
  assert.notEqual(e.ball.carrier, p.id); assert.ok(e.carrier && e.carrier.freeze <= 0);
});
test('possession and Keeper Zone occupancy expire with turnovers', () => {
  const e = fixture(); run(e, 2701); assert.ok(e.events.some(x => x.text.includes('45 SECONDS')));
  const zone = fixture(); zone.players[0].x = 90; run(zone, 301); assert.ok(zone.events.some(x => x.text.includes('FIVE SECONDS')));
});
test('full regulation Ala Marauders vs Xenar Ignite match completes from physical events', () => {
  const e = full(1);
  assert.equal(e.events.filter(x => x.type === 'quarter').length, 4); assert.equal(e.liveTicks, 144000);
  for (const s of e.teamStats) {
    assert.ok(s.points > 0 && s.possessionTime > 0 && s.possessionChanges > 0);
    assert.ok(s.shots > 0 && s.saves > 0 && s.arrowShots > 0 && s.tackles > 0);
    assert.equal(s.points, 5 * s.carries + 3 * s.releaseGoals);
    assert.ok(s.arrowShots <= 80);
  }
  assert.deepEqual(e.events.filter(x => x.type === 'goal').reduce((a, ev) => { a[ev.side!] += ev.points!; return a; }, [0, 0]), e.score);
  const before = digest(e); run(e, 1000); assert.equal(digest(e), before);
  const replay = full(1, 8, 30);
  assert.equal(digest(replay), before);
  writeFileSync('evidence/regulation-match.json', JSON.stringify(e.result(), null, 2) + '\n');
  writeFileSync('evidence/regulation-summary.json', JSON.stringify({ seed: e.settings.seed, score: e.score, liveTicks: e.liveTicks, quarters: 4, sha256: before, replayAt8x30Fps: digest(replay), teamStats: e.teamStats }, null, 2) + '\n');
});
test('same seed produces identical complete events and results at 30 / 60 / 144 FPS and 1× / 2× / 4× / 8×', () => {
  const baseline = full(20), hash = digest(baseline);
  const checks = [{ speed: 1, fps: 60, hash }];
  for (const [speed, fps] of [[1, 30], [1, 144], [2, 60], [4, 144], [8, 30], [8, 60]]) {
    const e = full(20, speed, fps); assert.equal(digest(e), hash); checks.push({ speed, fps, hash: digest(e) });
  }
  writeFileSync('evidence/determinism.json', JSON.stringify({ seed: settings.seed, clockRate: 20, score: baseline.score, checks }, null, 2) + '\n');
});
