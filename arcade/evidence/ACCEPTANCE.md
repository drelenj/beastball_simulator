# Acceptance report

Validated in Node.js 24 and headless system Chromium on 2026-11-15. All commands ran in the actual cloned project. The browser used the Vite server at http://localhost:5173.

## Build and launch

- Root command `npm install` succeeded, including the arcade dependency install.
- Root `npm run build` passed TypeScript checks and produced the static `arcade/dist` bundle.
- `npm run dev` serves the game at port 5173; the development server was left running.
- `npm test` in arcade: **13 tests, 13 passed**. See `engine-tests.txt`.
- `npm run test:browser`: **14 checks passed**, **0 console/page errors**, **0 failed requests**. See `browser-tests.json` and `browser-tests.txt`.

## Actual rendered autonomous match

Ala Marauders vs Xenar Ignite; canonical workbook starting XII, seed 202627, Quick match clock (20×), same engine as Human vs AI. Completed four quarters with no keyboard input. Playback changed through 1×, 2×, 4× and 8× while the game ran.

- Final score: **15–27**.
- Both teams fielded 10 field athletes + Keeper + Archer.
- Both gained possession, attempted releases and scored from physical ball / carrier crossings.
- Keeper saves: **1 / 2**.
- Archer shots: **15 / 14**.
- Four First Hunts, quarter breaks, final statistics, same-team rematch and team-selection return verified.
- Complete browser result SHA-256: `aa2e78e2a5ab6a0515d155f95e0f7e627b60d7d95cadd32a98ed8b553c4858c5`. Identical to the headless result and to rematch, including every recorded event and statistic.

## Regulation autonomous match and repeatability

Same canonical matchup, seed 202627, clock rate 1. Ran **144,000 live fixed steps = 2,400 live seconds**, four complete 10-minute quarters, plus dead-ball celebrations / breaks. No score generation separate from game physics.

- Final: **225–306**.
- Keeper saves: **54 / 32**.
- Archer shots: **80 / 80**; actual freezes: **1 / 4**.
- Both teams passed, caught, tackled, scored, gained possession and recovered the ball.
- Replayed at 8× / 30 FPS with **identical complete result hash**: `eb59fd59379b8ead50399492beef76ae3a0faa9fac8a664921ce864c28be29a6`.
- Additionally, seven Quick-clock frame schedules at 30/60/144 FPS and 1×/2×/4×/8× produced the identical hash `aa2e78e2a5ab6a0515d155f95e0f7e627b60d7d95cadd32a98ed8b553c4858c5`. See `determinism.json`.
- Calling step after finalization leaves scores, clocks, statistics, events and state unchanged.

## Human input and mechanics

Chromium used real keyboard events through the app's input provider. Controlled set-plays position athletes to isolate outcomes; these are not represented as autonomous match evidence.

- WASD movement, immediate acceleration, Shift sprint, K useful-defender switch.
- Space pass, actual flight, catch, possession transfer and automatic control transfer.
- J legal carrier tackle; separate engine tests verify first recovery, protection and second-tackle turnover.
- L release goal adds 3; controlled carry across the goal plane adds 5.
- E launches an Archer projectile, impacts a carrier, drops the ball and creates a freeze. Engine tests check five-second freeze, subsequent immunity, preservation across restarts, reload and quarter allocation.
- Keeper physical save, wide goal rejection, own-goal value, sideline turnovers, 45-second turnover and five-second carrier-zone expiry covered in resolved engine fixtures.
- Escape pause/resume, main menu, controls dialog, both-side selection, seed, match start, stats, rematch, and 390px selection layout verified.
- Gamepad code exists, but physical hardware was not available; it is not claimed as hardware-verified.

## Data and preservation

26 NBL franchises / 712 unchanged source players / 12 canonical projected starters per side. Original workbook IDs, names, position, opening-day OVR, opening roles, formation, readiness and development retained. Primary-sheet vs team-sheet 674-rating conflict recorded, with primary-sheet precedence. Twenty official local logo mappings have source filenames, Drive IDs, hashes, dimensions and alpha metadata in `src/logos.json`. Six ambiguous/unavailable franchise logos remain temporary monograms. Field numerals are temporary bibs because the workbook contains no jersey-number column.

Original Pocket, PRISM, Python tests and experimental baseline files are untouched. New root package scripts and gitignore entries only add browser launch support. Checkpoint commit `d19c49ad64fd6d641cfae8d119f2831967191521` preceded asset/verification polish. The README details the v1.0 arcade rules profile, source scoring path, deliberate simplifications and known limitations.

## Remaining limitations

Full foul / penalty / discipline / injury / substitution / contact-scrimmage systems are not ported. Noncarrier zone residence is simplified. Physics and fatigue are arcade approximations; no claim of canonical physiology or full PRISM browser execution. Scores and contact rates need balancing, Archer hit rates vary, and loose-ball packs sometimes bunch. Tied games end as draws. Human input streams are not saved for deterministic human replays. No local Human vs Human, touch controls, public deployment, or verified physical gamepad. Browser URL is local to the execution environment.
