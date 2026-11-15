# NDAGÏ BEASTBALL: ARCADE

A static browser game built alongside the existing Python simulator. Human vs AI and AI vs AI use the same authoritative 60 Hz engine. Original PRISM, Pocket and solver files are unchanged.

## Run

Node.js 22.18+ recommended (Node.js 24 used for validation).

From the repository root:

```sh
npm install
npm run dev
```

Open **http://localhost:5173**. Select **Play the Hunt** or **Watch AI vs AI**, pick both franchises, set the seed and clock, then start. No credentials, services, database or runtime asset downloads are needed.

Alternatively: `cd arcade && npm ci && npm run dev`.

```sh
npm run build                  # root: typecheck and production static build
cd arcade
npm test                       # mechanics + full regulation + replay checks
npm run match -- 202627 1       # full autonomous 4 × 600 s match, save actual events
npm run test:browser            # requires the Vite server on :5173
```

Browser tests use `/usr/bin/chromium` when present, otherwise a Playwright browser. Set `CHROMIUM_PATH` or run `npx playwright install chromium`. Use `BASE_URL` for another server. Python import utilities additionally require `openpyxl` and Pillow, but neither is required to play.

`npm run build` emits `arcade/dist/`; deploy that directory on any static host. No production hosting was provisioned.

## Play

| Input | Action |
|---|---|
| WASD / arrows | Move the controlled home athlete |
| Shift | Sprint |
| Space | Pass to a useful teammate; catches resolve on contact |
| J | Tackle an eligible opposing carrier |
| K | Switch among useful nearby field defenders |
| L | Release toward the attacked goal |
| E | Fire the home Archer at an eligible opposing carrier |
| Escape | Pause / resume |
| V | Ball-following / wide camera |
| R | Open restart confirmation |

Home teammates remain autonomous. Control follows a home catch immediately. In spectator mode both sides are autonomous; use 1×, 2×, 4× or 8× playback. Optional gamepad bindings are implemented (left stick, A pass, B tackle, X switch, Y release, RB Archer, RT sprint, Start pause); physical gamepad hardware was not available for validation. Keyboard is the verified input path. No touch joystick or local two-human mode.

## Rules profile and deliberate simplifications

- Coordinates are meters on a **100 × 100** pitch. Goals are vertical semicircles of radius **6 m**, Keeper Zones **20 m**, penalty marks **25 m**, center circle **8 m**, with separate sideline Archer lanes. Oblique rendering does not alter world distances.
- Uses the repository Pocket v1.0 scoring path: controlled carry **5**, release **3**, including outside releases; own goals use the release value. Scoring requires an actual goal-plane crossing inside the semicircle. Source: `../Beastball Pocket 2 0(1).py`, `Engine.goal`, original path before `release_territories` overrides (around line 1889). The later v0.3 flat 2-point self-play experiment is **not** this profile.
- Four quarters of **600 live seconds** and a **45-second possession clock**. Regulation uses real simulation seconds. Arcade/Quick accelerate only the match clock by 6×/20×; movement, possession, freeze and reload timers retain simulation seconds. Celebrations and quarter breaks stop both live clocks. Playback speed advances complete fixed steps; it changes no rules or seed state.
- Ten canonical starting field athletes, one Keeper and one Archer per side. Formation comes from the workbook; placement uses the Defender / Ranger / Attacker taxonomy in `../positional_tendencies_v1.py`, with the existing position support-lead table reused. All 24 participate. Keeper steering, carrier tackles, catches and saves are resolved by the shared engine.
- Archer v1.0 baseline: **20 per quarter**, **5 loaded**, **5-second reload**, **5-second freeze**, **10-second subsequent arrow immunity**, **10–70 m** range. Carrier-only freeze eligibility and protected own-zone Keepers follow the Pocket 1.0.1 path. Hits on other bodies block the projectile but do not freeze. Quarter breaks replenish ammunition. Both AI Archers run independently. Human E fires the home Archer. Later per-possession arrow experiments are separate.
- First tackle retains possession via a **simplified protected recovery**; second tackle turns over. Recovery uses a 3 m exclusion disc and two seconds of post-recovery protection. Full contact scrimmage alignment, snap/offside procedures, continuous grip physics and foul adjudication are not ported.
- Carrier five-second Keeper Zone occupancy is enforced. Other athletes' occupancy/marking residence is simplified. Ball release height/flight, catch reach, body separation, sprinting, fatigue and contact are arcade approximations, not PRISM-certified physiology or canon caps. AI reads current visible state and current velocities; there is no hidden future-state access.
- No fouls, penalties, disciplinary substitutions, injuries, season progression, overtime or shootouts. Ties are final draws. No kicking. Pass selection is contextual; human-directed passing reticles are not implemented.
- The isolated adapter preserves intention → motor → outcome. It does not claim to run the Python PRISM perception or experimental contact solver in JavaScript.

## Data provenance

**Roster:** supplied `NBL_2026-27_Opening_Night_Rosters_CANON_OVR.xlsx`, **All 712 Players** worksheet. Exactly 26 NBL franchises and 712 registered athletes. All sixteen source fields are retained verbatim in `src/league.json`, including Player ID, name, franchise, position, opening-day OVR, opening-night role, formation, readiness and development. Starting XII come from `Projected starter` roles and include exactly one KPR and ARC. Opening-day OVR influences motion, passing error, catching, tackling, reaction cadence and Archer error. No skill-specific canonical ratings were fabricated.

**Workbook conflict:** team worksheets disagree with the primary worksheet on **674 opening-day ratings**. The user-designated primary worksheet wins. `evidence/roster-crosscheck.json` records each difference. The primary sheet rates Kamasi Sinella 90 and Xavier Flameguard 71; those are the displayed values. Original IDs are retained even when a transferred player's ID includes another franchise code. No jersey numbers were supplied; on-field numerals are explicitly temporary lineup bibs.

**Logos:** authenticated downloads from the supplied [official NBL Drive folder](https://drive.google.com/drive/folders/1Y8JhgMbo1-yZD6Z7tOaM7AQliE4CqiFN). Twenty uniquely identified franchise logos are local WebP images. `src/logos.json` records Drive IDs, original filenames, original paths, SHA-256 hashes, dimensions, alpha presence, optimized paths and mapping decisions. Optimization preserves aspect ratio and existing alpha; opaque source backgrounds are intentionally retained. Logos appear in selection, scoreboard, quarter breaks, and final score. Six franchises use temporary monograms. The Priya image says **ARPAGU**, while the workbook says **Arpaqu**; it remains unmapped. Four UUID filenames plus one color-only filename are also unmapped. Uniform colors are arcade presentation choices, not asserted canonical palettes.

`python scripts/import_rosters.py /path/to/workbook.xlsx` reproduces the roster import and cross-check. `scripts/import_logos.py` reproduces optimization when original files are available at the manifest's source paths.

The only other repository accessible under the project owner was `drelenj/Beast` (empty). No unrelated Beastball repository or third-party reference implementation was imported. Yuka, STS2, football and MuJoCo were not needed; there is no copied external source or related copyright obligation. Vite/TypeScript/tsx/Playwright retain their dependency licenses. Project logo/art rights remain with their source owners; this work grants no new asset license.

## Architecture

- `src/engine.ts`: authoritative world; seeded PRNG; HumanController / AIController; intentions, movement, ballistics, contacts, rules, quivers, event statistics, quarters and finalization.
- `src/timing.ts`: fixed-step accumulator shared by the browser and determinism tests.
- `src/renderer.ts`: canvas oblique projection, animated athletes, shadows, goals, pitch, stadium, arrows, freeze states and ball camera; observes engine state.
- `src/main.ts`: menus, configuration, keyboard/gamepad intents, HUD, pause, spectator speeds, sound, final statistics, JSON replay export.
- `tests/engine.test.ts`: meaningful resolved-mechanics tests plus full seeded match and render-rate/playback invariance.
- `tests/browser.mjs`: real Chromium flow, autonomous rendered match, identical rematch and keyboard set-play checks. Controlled fixtures are clearly identified in test output.

Matches export actual events and per-athlete/per-team points, carry/release goal counts, release attempts, pass attempts/completions, tackle attempts/successes, turnovers, Keeper saves, Archer shots/hits, possession gains and possession time. Final-state steps are immutable. The seed/settings reproduce AI matches; a human replay additionally requires the human input stream (not recorded in this first release).

## Known limitations

Scores and contact frequency are high and need play balancing. Archer hit rates can be low and asymmetric, especially in Quick mode; both sides still fire and resolve the same projectile rules. Visible on-pitch numbers are temporary bibs. Players may bunch during loose-ball contests. Very small screens have a readable selection screen but desktop keyboard is required to play. Stadium graphics and athletes are original procedural art; this is an arcade adaptation, not a complete canon rules/physics port. Evidence and the acceptance report distinguish tested behavior from optional unverified input support.
