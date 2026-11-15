import './style.css';
import { Engine, teams, Team, DT, Input, blankInput, PlayerStats } from './engine';
import { Renderer } from './renderer';
import { FixedStepper } from './timing';
import logoManifest from './logos.json';

const app = document.querySelector<HTMLDivElement>('#app')!;
const escape = (s: string) => s.replace(/[&<>"']/g, x => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[x]!));
const logoIds = new Set(logoManifest.assets.filter(a => !a.status.startsWith('unmapped')).map(a => a.teamId));
const logo = (t: Team, cls = '') => logoIds.has(t.id) ? `<img class="team-logo ${cls}" src="${import.meta.env.BASE_URL}logos/${t.id}.webp" alt="${escape(t.name)} official logo"/>` : `<span class="team-monogram ${cls}" style="--team:${t.color}" title="Official logo not yet verified">${escape(t.name.split(' ').map(w => w[0]).slice(0, 2).join(''))}</span>`;
let home = teams.find(t => t.name === 'Ala Marauders')!, away = teams.find(t => t.name === 'Xenar Ignite')!;
let mode: 'human' | 'spectator' = 'human', seed = 202627, clockRate = 6;
let game = new Engine({ home, away, mode: 'spectator', seed, clockRate: 6 });
let screen: 'menu' | 'select' | 'match' = 'menu', slot: 'home' | 'away' = 'home';
let paused = false, playback = 1, last = performance.now(), hudTime = 0;
const stepper = new FixedStepper();
let overlay = '', eventIndex = 0, sound = false, audioContext: AudioContext | null = null;
let renderer: Renderer;
const keys = new Set<string>(); let edges = blankInput();
const touch = { x: 0, y: 0, sprint: false };
const controls = `<div class="control-grid"><span><kbd>W A S D</kbd> / <kbd>STICK</kbd> Move</span><span><kbd>Shift</kbd> / <kbd>SPRINT</kbd> Sprint</span><span><kbd>Space</kbd> / <kbd>PASS</kbd> Pass / catch automatically</span><span><kbd>J</kbd> / <kbd>TACKLE</kbd> Tackle carrier</span><span><kbd>K</kbd> / <kbd>SWITCH</kbd> Switch defender</span><span><kbd>L</kbd> / <kbd>RELEASE</kbd> Release at goal</span><span><kbd>E</kbd> / <kbd>ARCHER</kbd> Fire Archer</span><span><kbd>Esc</kbd> Pause / resume</span><span><kbd>V</kbd> Wide / ball camera</span><span><kbd>R</kbd> Reload match confirmation</span></div>`;
const touchControls = `<div class="touch-controls" aria-label="Touch game controls"><div class="touch-stick" data-touch-stick role="group" aria-label="Movement joystick"><span class="touch-stick-knob"></span><small>MOVE</small></div><div class="touch-actions"><button type="button" data-touch-action="pass" aria-label="Pass">PASS</button><button type="button" class="touch-primary" data-touch-action="shoot" aria-label="Release at goal">RELEASE</button><button type="button" data-touch-action="tackle" aria-label="Tackle">TACKLE</button><button type="button" data-touch-action="switch" aria-label="Switch athlete">SWITCH</button><button type="button" data-touch-action="fire" aria-label="Fire Archer">ARCHER</button><button type="button" class="touch-sprint" data-touch-action="sprint" aria-label="Hold to sprint">SPRINT<small>HOLD</small></button></div></div>`;
const brand = `<a class="brand" href="#" data-action="menu" aria-label="Beastball main menu"><span class="brand-symbol">N<span>↗</span></span><span>NDAGÏ<span>BEASTBALL / ARCADE</span></span></a>`;
function shell(content: string, className: string) {
  app.innerHTML = `<div class="shell ${className}"><canvas id="pitch" aria-label="Live 2.5D Beastball pitch"></canvas>${content}</div>`;
  renderer = new Renderer(document.querySelector<HTMLCanvasElement>('#pitch')!);
  stepper.reset(); last = performance.now();
}
function resetInputs() {
  keys.clear(); edges = blankInput(); touch.x = 0; touch.y = 0; touch.sprint = false;
  document.querySelector<HTMLElement>('.touch-stick-knob')?.style.removeProperty('transform');
  document.querySelectorAll('.touch-active').forEach(el => el.classList.remove('touch-active'));
}
function installTouchControls() {
  const stick = document.querySelector<HTMLElement>('[data-touch-stick]');
  if (!stick) return;
  const knob = stick.querySelector<HTMLElement>('.touch-stick-knob')!;
  let pointer: number | null = null;
  const moveStick = (ev: PointerEvent) => {
    if (ev.pointerId !== pointer) return;
    const rect = stick.getBoundingClientRect(), radius = rect.width * .32;
    let dx = ev.clientX - (rect.left + rect.width / 2), dy = ev.clientY - (rect.top + rect.height / 2);
    const distance = Math.hypot(dx, dy);
    if (distance > radius) { dx *= radius / distance; dy *= radius / distance; }
    touch.x = Math.abs(dx / radius) < .08 ? 0 : dx / radius;
    touch.y = Math.abs(dy / radius) < .08 ? 0 : dy / radius;
    knob.style.transform = `translate(${dx}px, ${dy}px)`;
  };
  const releaseStick = (ev: PointerEvent) => {
    if (ev.pointerId !== pointer) return;
    pointer = null; touch.x = 0; touch.y = 0; knob.style.transform = 'translate(0, 0)';
    stick.classList.remove('touch-active');
  };
  stick.addEventListener('pointerdown', ev => {
    ev.preventDefault(); pointer = ev.pointerId; stick.setPointerCapture(ev.pointerId);
    stick.classList.add('touch-active'); moveStick(ev);
  });
  stick.addEventListener('pointermove', moveStick);
  stick.addEventListener('pointerup', releaseStick);
  stick.addEventListener('pointercancel', releaseStick);
  stick.addEventListener('lostpointercapture', releaseStick);
  for (const button of document.querySelectorAll<HTMLButtonElement>('[data-touch-action]')) {
    const action = button.dataset.touchAction!;
    const release = (ev: PointerEvent) => {
      if (button.hasPointerCapture(ev.pointerId)) button.releasePointerCapture(ev.pointerId);
      button.classList.remove('touch-active');
      if (action === 'sprint') touch.sprint = false;
    };
    button.addEventListener('pointerdown', ev => {
      ev.preventDefault(); button.setPointerCapture(ev.pointerId); button.classList.add('touch-active');
      if (action === 'sprint') touch.sprint = true;
      else if (action === 'pass') edges.pass = true;
      else if (action === 'shoot') edges.shoot = true;
      else if (action === 'tackle') edges.tackle = true;
      else if (action === 'switch') edges.switch = true;
      else if (action === 'fire') edges.fire = true;
    });
    button.addEventListener('pointerup', release);
    button.addEventListener('pointercancel', release);
    button.addEventListener('lostpointercapture', () => {
      button.classList.remove('touch-active');
      if (action === 'sprint') touch.sprint = false;
    });
  }
}
function menu() {
  screen = 'menu'; paused = false; overlay = ''; resetInputs();
  game = new Engine({ home, away, mode: 'spectator', seed, clockRate: 6 });
  shell(`<div class="menu-shade"></div><header class="topbar">${brand}<div class="status-light"><i></i> NBL 2026–27 · OPENING NIGHT</div><button class="icon-button" data-action="sound" aria-label="Toggle sound">${sound ? 'SOUND ON' : 'SOUND OFF'}</button></header>
    <main class="hero"><div class="eyebrow"><span>THE HUNT STARTS HERE</span><b>VOL. 01 / NBL</b></div><h1>INSTINCT.<br/>IMPACT.<br/><em>BEASTBALL.</em></h1><p>Twelve athletes. One hundred meters.<br/>Carry, release, and let your Archer change the game.</p><div class="hero-actions"><button class="button primary" data-action="play">PLAY THE HUNT <span>↗</span></button><button class="button secondary" data-action="watch">WATCH AI VS AI <span>▶</span></button></div><button class="text-button" data-action="controls">LEARN THE CONTROLS <span>→</span></button><div class="hero-facts"><span><b>26</b> NBL FRANCHISES</span><span><b>712</b> CANONICAL ATHLETES</span><span><b>2.5D</b> ARCADE ACTION</span></div></main>
    <aside class="live-card"><span class="eyebrow"><i class="live-dot"></i> LIVE ENGINE PREVIEW</span><div>${logo(home)}<span>VS</span>${logo(away)}</div><h3>${escape(home.name)}<br/><span>${escape(away.name)}</span></h3><p>Autonomous teams. Every outcome on the pitch.</p></aside><footer class="menu-footer"><span>ORIGINAL SPORT. ARCADE INSTINCT.</span><span>LOCAL PLAY · NO ACCOUNT REQUIRED</span><button data-action="about">RULES & PROVENANCE ↗</button></footer><div id="modal"></div>`, 'menu-screen');
}
function select() {
  screen = 'select'; paused = false; overlay = ''; resetInputs();
  shell(`<div class="selection-backdrop"></div><header class="topbar">${brand}<div class="breadcrumb">01 / CONFIGURE THE HUNT</div><button class="text-button" data-action="menu">← MAIN MENU</button></header><main class="selection-layout"><section class="selection-main"><div class="section-heading"><div><div class="eyebrow">OFFICIAL NBL / 2026–27</div><h1>CHOOSE YOUR <em>INSTINCT.</em></h1></div><span class="pill">26 TEAMS</span></div><div class="matchup-slots"><button data-action="slot-home" class="matchup-slot ${slot === 'home' ? 'active' : ''}">${logo(home)}<span><small>HOME · ${mode === 'human' ? 'YOU' : 'AI'}</small><strong>${escape(home.name)}</strong><small>${home.formation} · ${Math.round(home.players.filter(p => home.starters.includes(p['Player ID'])).reduce((a, p) => a + p['Opening-day OVR'], 0) / 12)} OVR</small></span><b>↗</b></button><span class="vs">VS</span><button data-action="slot-away" class="matchup-slot ${slot === 'away' ? 'active' : ''}">${logo(away)}<span><small>AWAY · AI</small><strong>${escape(away.name)}</strong><small>${away.formation} · ${Math.round(away.players.filter(p => away.starters.includes(p['Player ID'])).reduce((a, p) => a + p['Opening-day OVR'], 0) / 12)} OVR</small></span><b>↗</b></button></div><div class="team-filter"><span>SELECT ${slot.toUpperCase()} FRANCHISE</span><input id="team-search" type="search" placeholder="Search 26 franchises…" aria-label="Search franchises"/></div><div class="team-grid">${teams.map((t, i) => `<button class="team-card ${home.id === t.id ? 'home-selected' : ''} ${away.id === t.id ? 'away-selected' : ''}" data-team="${t.id}" style="--team:${t.color}" aria-label="Select ${escape(t.name)}">${logo(t)}<span class="team-index">${String(i + 1).padStart(2, '0')}</span><strong>${escape(t.name)}</strong><small>${t.formation} <span>${t.players.length} ATHLETES</span></small>${home.id === t.id ? '<b class="chosen">HOME</b>' : away.id === t.id ? '<b class="chosen">AWAY</b>' : ''}</button>`).join('')}</div><p class="data-note">All 712 Players worksheet · Opening-day OVR · Verified projected starters. Monograms indicate logos awaiting verification.</p></section><aside class="selection-sidebar"><div class="eyebrow">MATCH SETUP</div><label>CONFIGURATION<select id="mode"><option value="human" ${mode === 'human' ? 'selected' : ''}>Human vs AI</option><option value="spectator" ${mode === 'spectator' ? 'selected' : ''}>AI vs AI · Spectator</option></select></label><label>MATCH CLOCK<select id="clock"><option value="6" ${clockRate === 6 ? 'selected' : ''}>Arcade · ~7 minutes (6× clock)</option><option value="20" ${clockRate === 20 ? 'selected' : ''}>Quick hunt · ~2 minutes (20× clock)</option><option value="1" ${clockRate === 1 ? 'selected' : ''}>Regulation · 4 × 10 minutes</option></select></label><label>REPLAY SEED<input id="seed" type="number" min="1" max="4294967295" value="${seed}"/></label><div class="lineup-heading"><span>${slot === 'home' ? 'HOME' : 'AWAY'} STARTING XII</span><small>OVR</small></div><div class="lineup">${(slot === 'home' ? home : away).players.filter(p => (slot === 'home' ? home : away).starters.includes(p['Player ID'])).map(p => `<div><span class="position ${p.Position === 'ARC' || p.Position === 'KPR' ? 'special' : ''}">${p.Position}</span><span title="${escape(p['Player ID'])}">${escape(p.Player)}</span><b>${p['Opening-day OVR']}</b></div>`).join('')}</div><p class="data-note">10 field athletes + Keeper + Archer.<br/>On-pitch numbers are temporary bibs; the source does not supply jersey numbers.</p><button class="button primary start" data-action="start">START MATCH <span>↗</span></button></aside></main><div id="modal"></div>`, 'select-screen');
  document.querySelector('#team-search')!.addEventListener('input', ev => {
    const query = (ev.target as HTMLInputElement).value.toLocaleLowerCase();
    document.querySelectorAll<HTMLButtonElement>('[data-team]').forEach(el => el.hidden = !el.textContent!.toLocaleLowerCase().includes(query));
  });
  document.querySelector('#mode')!.addEventListener('change', ev => { mode = (ev.target as HTMLSelectElement).value as typeof mode; select(); });
  document.querySelector('#clock')!.addEventListener('change', ev => clockRate = Number((ev.target as HTMLSelectElement).value));
  document.querySelector('#seed')!.addEventListener('change', ev => { seed = Math.max(1, Number((ev.target as HTMLInputElement).value) >>> 0); });
}
function start() {
  game = new Engine({ home, away, mode, seed, clockRate }); screen = 'match'; paused = false; playback = 1; overlay = ''; eventIndex = 0; resetInputs();
  shell(`<div class="match-interface"><header class="match-top"><div class="compact-brand">N<span>↗</span><small>BEASTBALL<br/>ARCADE</small></div><div class="scoreboard"><div class="score-team home">${logo(home)}<span>${escape(home.name)}<small>HOME ${mode === 'human' ? '/ YOU' : '/ AI'}</small></span><strong id="score-home">0</strong></div><div class="clock-block"><span id="period">Q1</span><b id="clock-value">10:00</b><small id="phase-value">FIRST HUNT</small></div><div class="score-team away"><strong id="score-away">0</strong><span>${escape(away.name)}<small>AWAY / AI</small></span>${logo(away)}</div></div><button class="icon-button pause-button" data-action="pause" aria-label="Pause match">Ⅱ</button></header><div class="match-meta"><span><i class="live-dot"></i> ${mode === 'spectator' ? 'AI VS AI / SPECTATOR' : 'HUMAN VS AI / YOU CONTROL HOME'}</span><div class="possession"><span id="possession-team">FIRST HUNT</span><strong id="possession-clock">45</strong><small>POSSESSION</small></div><span>SEED ${seed} <b>·</b> ${clockRate === 1 ? 'REGULATION' : `${clockRate}× MATCH CLOCK`}</span></div><div id="event-banner" aria-live="polite"></div><div class="match-bottom"><div id="athlete-panel"></div><div class="match-tools"><button data-action="camera" title="V to toggle camera">◎ BALL CAM</button><button data-action="stats">▤ STATS</button><button data-action="controls">? CONTROLS</button><button data-action="sound">${sound ? '♪ SOUND ON' : '♪ SOUND OFF'}</button>${mode === 'spectator' ? `<label class="speed-label">PLAYBACK <select id="playback" aria-label="Playback speed"><option value="1">1×</option><option value="2">2×</option><option value="4">4×</option><option value="8">8×</option></select></label>` : ''}</div></div><div class="control-strip">${mode === 'human' ? '<span><kbd>WASD</kbd> MOVE</span><span><kbd>SHIFT</kbd> SPRINT</span><span><kbd>SPACE</kbd> PASS</span><span><kbd>J</kbd> TACKLE</span><span><kbd>K</kbd> SWITCH</span><span><kbd>L</kbd> RELEASE</span><span><kbd>E</kbd> ARCHER</span>' : '<span>AUTONOMOUS PLAY · BOTH TEAMS SHARE ONE ENGINE</span><span>FIXED STEP 60 HZ · SPEED DOES NOT CHANGE THE RULES</span>'}</div>${mode === 'human' ? touchControls : ''}</div><div id="state-overlay"></div><div id="modal"></div>`, 'match-screen');
  document.querySelector('#playback')?.addEventListener('change', ev => { playback = Number((ev.target as HTMLSelectElement).value); });
  installTouchControls();
  updateHUD();
}
const formatClock = (n: number) => `${Math.floor(Math.max(0, Math.ceil(n)) / 60)}:${String(Math.max(0, Math.ceil(n)) % 60).padStart(2, '0')}`;
function updateHUD() {
  if (screen !== 'match') return;
  const text = (id: string, value: string) => { document.getElementById(id)!.textContent = value; };
  text('score-home', String(game.score[0])); text('score-away', String(game.score[1])); text('period', `Q${Math.min(4, game.quarter)}`); text('clock-value', formatClock(game.clock));
  text('phase-value', game.phase === 'final' ? 'FULL TIME' : game.phase === 'break' ? 'QUARTER BREAK' : game.phase === 'goal' ? 'GOAL!' : game.tackles ? '1 TACKLE' : 'LIVE PLAY');
  text('possession-team', game.owner === null ? 'FIRST HUNT' : (game.owner === 0 ? home : away).name.toUpperCase());
  text('possession-clock', String(Math.max(0, Math.ceil(game.possessionClock))));
  document.querySelector('.possession')!.classList.toggle('urgent', game.possessionClock < 10);
  const player = mode === 'human' ? game.players[game.selected] : game.carrier ?? game.players[0];
  const q = game.quivers[mode === 'human' ? 0 : player.side];
  const state = player.freeze > 0 ? `FROZEN · ${player.freeze.toFixed(1)}s` : player.down > 0 ? 'RECOVERING' : player.immune > 0 ? 'ARROW IMMUNITY' : player.id === game.ball.carrier ? 'BALL CARRIER' : mode === 'human' ? 'CONTROLLED ATHLETE' : 'FOLLOWING THE HUNT';
  const panel = document.querySelector('#athlete-panel')!;
  panel.innerHTML = `<span class="athlete-bib" style="--team:${(player.side === 0 ? home : away).color}">${player.bib}</span><div><small>${state} <b>·</b> ${player.data.Position} <b>·</b> ${player.data['Opening-day OVR']} OVR</small><strong>${escape(player.data.Player)}</strong><span class="stamina"><i style="width:${player.stamina * 100}%"></i></span></div><div class="quiver"><small>ARCHER</small><strong>${q.reload > 0 ? `↻ ${q.reload.toFixed(1)}s` : `${q.loaded} <em>/ ${20 - q.spent}</em>`}</strong><span>LOADED / QUARTER LEFT</span></div>`;
  const highlighted = game.events.findLast(e => ['goal', 'tackle', 'freeze', 'turnover', 'save', 'quarter'].includes(e.type));
  const banner = document.querySelector<HTMLDivElement>('#event-banner')!;
  if (highlighted && (game.tick - highlighted.tick) * DT < 2) {
    banner.innerHTML = `<span class="event-tag">${highlighted.type === 'goal' ? 'THE HUNT DELIVERS' : highlighted.type.toUpperCase()}</span><b>${escape(highlighted.text)}</b>`;
    banner.className = highlighted.type === 'goal' ? 'visible goal-banner' : 'visible';
  } else banner.className = '';
  const nextOverlay = paused ? 'pause' : game.phase === 'final' ? 'final' : game.phase === 'break' ? `break${game.quarter}` : '';
  if (overlay !== nextOverlay) {
    overlay = nextOverlay;
    const node = document.querySelector('#state-overlay')!;
    if (!overlay) node.innerHTML = '';
    else if (overlay === 'pause') node.innerHTML = `<div class="state-shade"><section class="state-card"><div class="eyebrow">TAKE A BREATH</div><h1>HUNT <em>PAUSED.</em></h1><p>${escape(home.name)} ${game.score[0]} — ${game.score[1]} ${escape(away.name)}</p><button class="button primary" data-action="pause">RESUME MATCH <span>▶</span></button><button class="button secondary" data-action="restart">RESTART SAME SEED ↻</button><button class="text-button" data-action="select">TEAM SELECTION →</button><button class="text-button" data-action="menu">MAIN MENU →</button></section></div>`;
    else if (overlay === 'final') node.innerHTML = `<div class="state-shade final-shade"><section class="final-card"><div class="eyebrow">THE FINAL HORN / SEED ${seed}</div><h1>HUNT <em>COMPLETE.</em></h1><div class="final-matchup"><div>${logo(home)}<strong>${escape(home.name)}</strong></div><b>${game.score[0]}<span>:</span>${game.score[1]}</b><div>${logo(away)}<strong>${escape(away.name)}</strong></div></div><div class="winner">${game.score[0] === game.score[1] ? 'DRAW · HONORS SHARED' : escape((game.score[0] > game.score[1] ? home : away).name.toUpperCase()) + ' WIN THE HUNT'}</div>${statTable()}<div class="final-actions"><button class="button primary" data-action="restart">REMATCH · SAME SEED ↻</button><button class="button secondary" data-action="select">CHOOSE TEAMS ↗</button><button class="text-button" data-action="stats">PLAYER STATS →</button><button class="text-button" data-action="menu">MAIN MENU →</button><button class="text-button" data-action="export">EXPORT MATCH JSON ↓</button></div></section></div>`;
    else node.innerHTML = `<div class="quarter-shade"><section class="quarter-card"><div class="eyebrow">END OF QUARTER ${game.quarter - 1}</div><h1>RESET. <em>RELOAD.</em></h1><div class="quarter-matchup">${logo(home)}<b>${game.score[0]} — ${game.score[1]}</b>${logo(away)}</div><p>Next First Hunt in 3 simulation seconds.<br/>20 arrows replenished per side.${game.quarter === 3 ? ' Teams change ends at halftime.' : ''}</p><button class="text-button" data-action="pause">PAUSE BREAK Ⅱ</button></section></div>`;
  }
}
function statTable() {
  const a = game.teamStats[0], b = game.teamStats[1];
  const rows = [['Carry goals · 5 pts', a.carries, b.carries], ['Release goals · 3 pts', a.releaseGoals, b.releaseGoals], ['Release attempts', a.shots, b.shots], ['Passes completed / attempted', `${a.completions} / ${a.passes}`, `${b.completions} / ${b.passes}`], ['Tackles made / attempted', `${a.tackles} / ${a.tackleAttempts}`, `${b.tackles} / ${b.tackleAttempts}`], ['Keeper saves', a.saves, b.saves], ['Archer hits / shots', `${a.arrowHits} / ${a.arrowShots}`, `${b.arrowHits} / ${b.arrowShots}`], ['Turnovers', a.turnovers, b.turnovers], ['Possession gains', a.possessionChanges, b.possessionChanges], ['Possession time (live)', formatClock(a.possessionTime), formatClock(b.possessionTime)]];
  return `<div class="stat-table">${rows.map(([label, left, right]) => `<div><b>${left}</b><span>${label}</span><b>${right}</b></div>`).join('')}</div>`;
}
function modal(title: string, content: string) {
  if (screen === 'match' && game.phase !== 'final') paused = true;
  resetInputs();
  document.querySelector('#modal')!.innerHTML = `<div class="modal-shade"><section class="modal-card" role="dialog" aria-modal="true" aria-label="${escape(title)}"><button class="close" data-action="close" aria-label="Close dialog">×</button><div class="eyebrow">NDAGÏ / BEASTBALL ARCADE</div><h2>${title}</h2>${content}<button class="button secondary" data-action="close">BACK TO THE HUNT →</button></section></div>`;
  updateHUD(); document.querySelector<HTMLButtonElement>('.close')?.focus();
}
function showStats() {
  modal('THE NUMBERS BEHIND THE HUNT', `<div class="stats-teams"><span>${escape(home.name)}</span><span>${escape(away.name)}</span></div>${statTable()}<h3>INDIVIDUAL PERFORMANCE</h3><div class="player-stats"><table><thead><tr><th>Athlete</th><th>Role</th><th>Pts</th><th>Pass</th><th>Tkl</th><th>Save</th><th>Arrow</th></tr></thead><tbody>${game.players.map(p => `<tr><td><span style="color:${(p.side === 0 ? home : away).color}">●</span> ${escape(p.data.Player)}</td><td>${p.data.Position}</td><td>${p.stats.points}</td><td>${p.stats.completions}/${p.stats.passes}</td><td>${p.stats.tackles}/${p.stats.tackleAttempts}</td><td>${p.stats.saves}</td><td>${p.stats.arrowHits}/${p.stats.arrowShots}</td></tr>`).join('')}</tbody></table></div><p class="data-note">All statistics are recorded from resolved gameplay events. Pass, tackle, and arrow columns show successes / attempts.</p>`);
}
function about() {
  modal('A SPORT OF ITS OWN.', `<p>A 100 × 100 m pitch. Ten field athletes, one Keeper, and one Archer per side. Four 10-minute quarters; 45-second possessions. Carry the ball across the goal plane for <b>5 points</b>, or release it through the semicircular goal for <b>3 points</b>. No kicking.</p><p>First tackle: protected recovery. Second tackle: turnover. Attackers have five seconds inside the Keeper Zone. The Keeper defends a 6 m semicircular goal; the zone extends 20 m. A free release scores only when its visible flight crosses the goal.</p><p>Archers operate in assigned sideline lanes: 20 arrows per quarter, five loaded, five-second reload. Only eligible carriers can be frozen: five seconds frozen, followed by ten seconds of arrow immunity. Keepers are protected from arrows in their own zone. Archer range is 10–70 m.</p><h3>ROSTERS & ASSETS</h3><p>All 26 NBL franchises and 712 registered players come from the supplied <b>NBL_2026-27_Opening_Night_Rosters_CANON_OVR.xlsx</b>, “All 712 Players.” Opening-day OVR is displayed verbatim and influences arcade skills. Starting lineups use the opening-night roles. The primary and team worksheets disagree on 674 ratings; the primary sheet wins. Original IDs, formation, readiness and development fields are preserved in the data.</p><p>20 official local logos, including Ala Marauders and Xenar Ignite, from the supplied Google Drive folder. Six franchise marks are explicitly temporary monograms; five opaque filenames and the Priya Arpagu / Arpaqu spelling discrepancy remain unmapped. Jersey numbers were absent; rendered numbers are temporary bibs. Team colors and motion coefficients are arcade presentation choices.</p><h3>ARCADE ADAPTER</h3><p>This isolated engine uses the v1.0 5/3 scoring path in the repository’s Pocket engine. Later v0.3 flat-scoring experiments are separate. The original Python and PRISM systems are preserved. Full foul adjudication, injuries, substitutions, penalties, and support-foot tracking are not implemented. Contact recovery is simplified. Human and AI providers share one 60 Hz engine. Match-clock acceleration shortens quarters; possession, freeze and reload timers retain simulation seconds.</p><p class="data-note">Arrow speed, acceleration, fatigue, and AI choices are tuned for arcade play, not certified canonical physics. Original procedural graphics; no Tecmo artwork or external reference code imported.</p>`);
}
function tone(type: string) {
  if (!sound) return;
  try {
    audioContext ??= new AudioContext(); const now = audioContext.currentTime;
    const osc = audioContext.createOscillator(), gain = audioContext.createGain(); osc.connect(gain); gain.connect(audioContext.destination);
    osc.type = type === 'tackle' ? 'triangle' : 'sine'; const freq = type === 'goal' ? 660 : type === 'freeze' ? 1040 : type === 'tackle' ? 100 : 330;
    osc.frequency.setValueAtTime(freq, now); osc.frequency.exponentialRampToValueAtTime(freq * (type === 'goal' ? 1.5 : .55), now + .18);
    gain.gain.setValueAtTime(.045, now); gain.gain.exponentialRampToValueAtTime(.001, now + .23); osc.start(); osc.stop(now + .24);
  } catch { /* Sound remains optional on browsers that restrict audio. */ }
}
document.addEventListener('click', ev => {
  const el = (ev.target as HTMLElement).closest<HTMLElement>('[data-action], [data-team]'); if (!el) return;
  ev.preventDefault();
  if (el.dataset.team) { const t = teams.find(t => t.id === el.dataset.team)!; if (slot === 'home') home = t; else away = t; select(); return; }
  const action = el.dataset.action;
  if (action === 'menu') menu();
  if (action === 'select') select();
  if (action === 'play') { mode = 'human'; select(); }
  if (action === 'watch') { mode = 'spectator'; select(); }
  if (action === 'slot-home') { slot = 'home'; select(); }
  if (action === 'slot-away') { slot = 'away'; select(); }
  if (action === 'start' || action === 'restart') start();
  if (action === 'pause') { paused = !paused; resetInputs(); updateHUD(); }
  if (action === 'camera') { renderer.wide = !renderer.wide; el.textContent = renderer.wide ? '◎ WIDE CAM' : '◎ BALL CAM'; }
  if (action === 'controls') modal('PLAY BY INSTINCT.', `${controls}<p>On a phone, drag the left stick to move and hold Sprint while steering. The right buttons pass, release, tackle, switch defenders, and fire the Archer. Touch buttons use the same contextual actions and game engine as keyboard controls.</p><p>Carry through the illuminated semicircle for 5 points. Release for 3. Pass chooses an open teammate; catches happen automatically on contact. Tackle only affects an opposing carrier. Move defenders to open your Archer's lane.</p><p>When your team catches the ball, control immediately follows the carrier. Teammates keep supporting you autonomously. A connected gamepad supports left stick, A pass, B tackle, X switch, Y release, RB Archer, RT sprint, Start pause.</p><p class="data-note">Spectator playback changes how many fixed steps run per rendered frame. Seed and clock settings determine the replay. Human vs human is not included.</p>`);
  if (action === 'about') about();
  if (action === 'stats') showStats();
  if (action === 'close') { document.querySelector('#modal')!.innerHTML = ''; if (screen === 'match' && game.phase !== 'final') paused = false; resetInputs(); updateHUD(); }
  if (action === 'sound') { sound = !sound; el.textContent = sound ? '♪ SOUND ON' : '♪ SOUND OFF'; if (sound) tone('goal'); }
  if (action === 'export') {
    const url = URL.createObjectURL(new Blob([JSON.stringify(game.result(), null, 2)], { type: 'application/json' }));
    const a = document.createElement('a'); a.href = url; a.download = `beastball-${seed}.json`; a.click(); URL.revokeObjectURL(url);
  }
});
document.addEventListener('keydown', ev => {
  if ((ev.target as HTMLElement).matches('input, select, textarea')) return;
  const k = ev.code;
  if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Escape'].includes(k)) ev.preventDefault();
  if (keys.has(k)) return; keys.add(k);
  if (screen !== 'match') return;
  if (k === 'Escape') {
    if (document.querySelector('#modal')!.innerHTML) { document.querySelector<HTMLElement>('[data-action="close"]')!.click(); return; }
    paused = !paused; resetInputs(); updateHUD(); return;
  }
  if (k === 'KeyV') renderer.wide = !renderer.wide;
  if (k === 'KeyR') { paused = true; modal('START A FRESH HUNT?', '<p>Restart this match from the same seed and selected teams.</p><button class="button primary" data-action="restart">RESTART MATCH ↻</button>'); }
  if (k === 'Space') edges.pass = true;
  if (k === 'KeyL') edges.shoot = true;
  if (k === 'KeyJ') edges.tackle = true;
  if (k === 'KeyK') edges.switch = true;
  if (k === 'KeyE') edges.fire = true;
});
document.addEventListener('keyup', ev => keys.delete(ev.code));
window.addEventListener('blur', () => { resetInputs(); if (screen === 'match' && game.phase !== 'final') { paused = true; updateHUD(); } });
document.addEventListener('visibilitychange', () => {
  if (document.hidden && screen === 'match' && game.phase !== 'final') { resetInputs(); paused = true; updateHUD(); }
});
let gamepadPrevious: boolean[] = [], gamepadPauseHeld = false;
function input(): Input {
  const i = { ...edges };
  const keyboardX = Number(keys.has('KeyD') || keys.has('ArrowRight')) - Number(keys.has('KeyA') || keys.has('ArrowLeft'));
  const keyboardY = Number(keys.has('KeyS') || keys.has('ArrowDown')) - Number(keys.has('KeyW') || keys.has('ArrowUp'));
  i.x = keyboardX || touch.x; i.y = keyboardY || touch.y;
  i.sprint = keys.has('ShiftLeft') || keys.has('ShiftRight') || touch.sprint;
  const pad = navigator.getGamepads?.()[0];
  if (pad) {
    if (Math.abs(pad.axes[0]) > .18) i.x = pad.axes[0]; if (Math.abs(pad.axes[1]) > .18) i.y = pad.axes[1];
    const b = pad.buttons.map(x => x.pressed), press = (n: number) => b[n] && !gamepadPrevious[n];
    i.pass ||= press(0); i.tackle ||= press(1); i.switch ||= press(2); i.shoot ||= press(3); i.fire ||= press(5); i.sprint ||= b[7];
    gamepadPrevious = b;
  }
  edges = blankInput(); return i;
}
function frame(now: number) {
  const elapsed = Math.min(.1, (now - last) / 1000); last = now;
  const startPressed = navigator.getGamepads?.()[0]?.buttons[9]?.pressed ?? false;
  if (screen === 'match' && startPressed && !gamepadPauseHeld) { paused = !paused; resetInputs(); updateHUD(); }
  gamepadPauseHeld = startPressed;
  if (screen !== 'select' && !paused && game.phase !== 'final') {
    const speed = screen === 'match' ? playback : 1;
    let nextInput = stepper.accumulator + elapsed * speed + 1e-10 >= DT ? input() : blankInput();
    stepper.advance(elapsed, speed, () => {
      game.step(screen === 'match' ? nextInput : blankInput());
      nextInput = { ...nextInput, pass: false, shoot: false, tackle: false, fire: false, switch: false };
    });
    for (const ev of game.events.slice(eventIndex)) if (['goal', 'tackle', 'freeze', 'save'].includes(ev.type) && screen === 'match') tone(ev.type);
    eventIndex = game.events.length;
  }
  renderer.draw(game, elapsed, screen !== 'match');
  hudTime += elapsed; if (hudTime > .08) { updateHUD(); hudTime = 0; }
  if (screen === 'menu' && game.phase === 'final') game = new Engine({ home, away, mode: 'spectator', seed, clockRate: 6 });
  requestAnimationFrame(frame);
}

// Inspection and exact-step hooks for acceptance testing. No alternative simulator.
declare global { interface Window { beastball: { engine: () => Engine; snapshot: () => ReturnType<Engine['result']>; advance: (ticks: number) => void; pause: (value: boolean) => void } } }
window.beastball = {
  engine: () => game, snapshot: () => game.result(),
  advance: ticks => { for (let n = 0; n < ticks; n++) game.step(); updateHUD(); },
  pause: value => { paused = value; updateHUD(); },
};
menu(); requestAnimationFrame(frame);
