import { chromium } from '@playwright/test';
import { existsSync, writeFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { Engine, teams } from '../src/engine.ts';

const browser = await chromium.launch({ headless: true, ...(process.env.CHROMIUM_PATH || existsSync('/usr/bin/chromium') ? { executablePath: process.env.CHROMIUM_PATH || '/usr/bin/chromium' } : {}), args: ['--no-sandbox'] });
const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
const errors = [], failedRequests = [], checks = [];
page.on('pageerror', e => errors.push(e.message));
page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
page.on('requestfailed', r => failedRequests.push(r.url()));
const check = (name, details = {}) => { checks.push({ name, passed: true, ...details }); console.log('PASS', name, details); };
const click = action => page.locator(`[data-action="${action}"]`).last().click();
const snapshot = () => page.evaluate(() => window.beastball.snapshot());
const pause = value => page.evaluate(value => window.beastball.pause(value), value);
const hash = data => createHash('sha256').update(JSON.stringify(data)).digest('hex');
// Deliberate controlled set-plays test actual keyboard -> provider -> motor -> outcome.
async function fixture(kind) {
  await pause(true);
  await page.evaluate(kind => {
    const e = window.beastball.engine();
    e.phase = 'live'; e.restart(0); e.selected = 0;
    for (const p of e.players) { p.x = 10; p.y = 10; p.vx = p.vy = 0; p.down = 999; p.decision = 999; p.protected = p.immune = p.freeze = p.cooldown = 0; p.intention = { move: { x: 0, y: 0 } }; }
    const p = e.players[0]; p.x = 50; p.y = 50; p.down = 0; e.acquire(p); p.protected = p.cooldown = 0;
    if (kind === 'pass') { const t = e.players[1]; t.x = 65; t.y = 50; t.down = 0; }
    if (kind === 'release') { p.x = 80; e.ball.x = 80; }
    if (kind === 'carry') { p.x = 98; e.ball.x = 98; }
    if (kind === 'tackle') { const t = e.players[12]; t.x = 51; t.y = 50; t.down = 0; e.acquire(t); t.protected = t.cooldown = 0; e.selected = 0; }
    if (kind === 'arrow') {
      const t = e.players[12], a = e.players[11]; t.x = 50; t.y = 30; t.down = 0; a.x = 50; a.y = -7; a.down = 0;
      e.acquire(t); t.protected = t.immune = t.cooldown = 0; e.quivers[0] = { spent: 0, loaded: 5, reload: 0, cooldown: 0 }; e.selected = 0;
    }
  }, kind);
  await pause(false);
}

try {
  await page.goto(process.env.BASE_URL || 'http://127.0.0.1:5173');
  await page.waitForFunction(() => !!window.beastball);
  assert.ok(await page.locator('[data-action="play"]').isVisible());
  await click('controls'); assert.ok(await page.getByRole('dialog').isVisible()); await click('close');
  await page.screenshot({ path: 'evidence/menu.png' }); check('Browser launch, main menu and controls');
  await click('watch'); assert.equal(await page.locator('[data-team]').count(), 26);
  await click('slot-away'); await page.locator('#team-search').fill('Xenar'); assert.equal(await page.locator('[data-team]:visible').count(), 1);
  await page.locator('[data-team="xenar-ignite"]').click();
  await page.locator('#clock').selectOption('20'); await page.locator('#seed').fill('202627'); await page.locator('#seed').blur();
  await page.screenshot({ path: 'evidence/selection.png' });
  await click('start'); await page.waitForTimeout(400); await click('pause');
  const frozenTick = (await snapshot()).tick; await page.waitForTimeout(300); assert.equal((await snapshot()).tick, frozenTick);
  check('Both team selections, seed, match start, pause');
  await click('pause');
  for (const speed of ['1', '2', '4', '8']) { await page.locator('#playback').selectOption(speed); await page.waitForTimeout(180); }
  await page.screenshot({ path: 'evidence/match.png' });
  await page.waitForFunction(() => window.beastball.engine().phase === 'final', null, { timeout: 90000 });
  await page.waitForTimeout(150);
  const ai = await snapshot();
  assert.equal(ai.players.length, 24); assert.equal(ai.quarter, 4);
  assert.equal(ai.events.filter(e => e.type === 'quarter').length, 4);
  for (const stats of ai.teamStats) { assert.ok(stats.possessionChanges > 0 && stats.shots > 0 && stats.arrowShots > 0); }
  await page.screenshot({ path: 'evidence/final.png' });
  const reference = new Engine({ home: teams.find(t => t.name === 'Ala Marauders'), away: teams.find(t => t.name === 'Xenar Ignite'), seed: 202627, mode: 'spectator', clockRate: 20 });
  while (reference.phase !== 'final') reference.step();
  assert.equal(hash(ai), hash(reference.result()));
  writeFileSync('evidence/browser-autonomous-match.json', JSON.stringify(ai, null, 2));
  check('Actual rendered AI vs AI match reaches four-quarter final, with speed changes', { score: ai.score, hash: hash(ai), keeperSaves: ai.teamStats.map(s => s.saves), archerShots: ai.teamStats.map(s => s.arrowShots) });
  await click('restart'); await pause(true); await page.evaluate(() => window.beastball.advance(20000));
  assert.equal(hash(await snapshot()), hash(ai)); check('Rematch reproduces every event and statistic');
  await click('select'); await page.locator('#mode').selectOption('human'); await click('start');
  await fixture('move');
  const startX = await page.evaluate(() => window.beastball.engine().players[0].x);
  await page.keyboard.down('d'); await page.waitForTimeout(600); await page.keyboard.up('d'); await pause(true);
  const jogX = await page.evaluate(() => window.beastball.engine().players[0].x);
  assert.ok(jogX > startX + 2);
  await fixture('move'); await page.keyboard.down('Shift'); await page.keyboard.down('d'); await page.waitForTimeout(600); await page.keyboard.up('d'); await page.keyboard.up('Shift'); await pause(true);
  const sprintX = await page.evaluate(() => window.beastball.engine().players[0].x);
  assert.ok(sprintX > jogX + .2); check('Real keyboard movement and sprint', { jogDistance: jogX - startX, sprintDistance: sprintX - startX });
  await fixture('tackle');
  await page.evaluate(() => { const e = window.beastball.engine(); e.players[1].down = 0; e.players[1].x = 53; e.players[1].y = 54; });
  await page.keyboard.press('k'); await page.waitForTimeout(150); await pause(true);
  assert.equal(await page.evaluate(() => window.beastball.engine().selected), 1); check('K switches to a useful nearby defender (set-play)');
  await fixture('pass'); const beforePass = (await snapshot()).teamStats[0].completions;
  await page.keyboard.press('Space'); await page.waitForTimeout(850); await pause(true);
  assert.ok((await snapshot()).teamStats[0].completions > beforePass);
  assert.equal(await page.evaluate(() => window.beastball.engine().selected), 1); check('Space pass, physical catch, automatic control transfer (set-play)');
  await fixture('tackle'); const tacklesBefore = (await snapshot()).teamStats[0].tackles;
  for (let i = 0; i < 6; i++) {
    await page.keyboard.press('j'); await page.waitForTimeout(150);
    if ((await snapshot()).teamStats[0].tackles > tacklesBefore) break;
    await page.waitForTimeout(1100);
  }
  await pause(true); assert.ok((await snapshot()).teamStats[0].tackles > tacklesBefore); check('J resolves legal carrier tackle (set-play)');
  await fixture('release'); const beforeRelease = (await snapshot()).score[0];
  await page.keyboard.press('l'); await page.waitForTimeout(900); await pause(true);
  assert.equal((await snapshot()).score[0], beforeRelease + 3); check('L scores a 3-point goal from actual release flight (set-play)');
  await fixture('carry'); const beforeCarry = (await snapshot()).score[0];
  await page.keyboard.down('d'); await page.keyboard.down('Shift'); await page.waitForTimeout(700); await page.keyboard.up('d'); await page.keyboard.up('Shift'); await pause(true);
  assert.equal((await snapshot()).score[0], beforeCarry + 5); check('Carry across goal plane updates scoreboard by 5 (set-play)');
  await fixture('arrow'); const beforeArrows = (await snapshot()).teamStats[0].arrowHits;
  await page.keyboard.press('e'); await page.waitForTimeout(900); await pause(true);
  assert.ok((await snapshot()).teamStats[0].arrowHits > beforeArrows);
  assert.ok(await page.evaluate(() => window.beastball.engine().players[12].freeze > 0));
  await page.screenshot({ path: 'evidence/archer-freeze.png' }); check('E fires actual Archer projectile and freezes carrier (set-play)');
  await click('pause'); await page.keyboard.press('Escape'); const escTick = (await snapshot()).tick;
  await page.waitForTimeout(200); assert.equal((await snapshot()).tick, escTick); await page.keyboard.press('Escape');
  await click('stats'); assert.ok(await page.getByRole('dialog').isVisible()); await click('close'); check('Escape pause/resume and live statistics');
  await page.setViewportSize({ width: 390, height: 844 });
  await click('pause'); await click('select'); await page.screenshot({ path: 'evidence/mobile-selection.png' });
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1); assert.equal(overflow, false);
  check('390px viewport selection has no horizontal overflow');
  assert.deepEqual(errors, []); assert.deepEqual(failedRequests, []); check('No fatal errors, console errors, or failed requests');
  writeFileSync('evidence/browser-tests.json', JSON.stringify({ checks, errors, failedRequests }, null, 2) + '\n');
} finally { await browser.close(); }
