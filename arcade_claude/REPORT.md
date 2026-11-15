# BEASTBALL: ARCADE (Claude Code build): report

Branch `claude/arcade-1` (also mirrored to the session branch `claude/hopeful-noether-x954z7`). All work is in `arcade_claude/`. The simulator (`core_src/` etc.) and accepted baselines were not touched. There is no `b1/` or `native/` in this checkout.

## OWNER BRIEFING

**1. What got done.** I built a playable browser game:
- 2.5D Beastball with all 24 athletes per match: 10 field players, a Keeper and an Archer per side.
- Real NBL opening-night rosters (26 franchises, 712 players).
- All 26 Drive logos, turned into small sprites, plus a colour palette per team.
- A fixed-step, seeded engine shared by Human vs AI, AI vs AI and local Human vs Human.

Status: IMPLEMENTED and TESTED (the 16 browser checks listed below). Acceptance is for the owner (DreLen).

**2. What the game can do now.**
- **Screens:** menu, team select (26 logos), mode / scoring / clock / seed options, match, skippable period-break screens, final score with stats, rematch, pause, restart, controls screen.
- **Spectator mode:** 1x / 2x / 4x / 8x, ball camera or follow-an-athlete camera.
- **Play:** passing and catching, interceptions, grounding tackles (first one gives a Contact Scrimmage, the second is a turnover), goals.
- **Keepers:** make saves.
- **Archers:** fire 250 m/s arrows within the 15-arrow / 5-freeze per-possession limits. A hit freezes the athlete for 5 s, then a 3 m / 2 s recovery, then 10 s of immunity, shown with red and amber helmet lights.
- **Clocks and rules:** game clock and 30 s play clock, the Keeper Zone 5 s rule, fouls with exclusions, half-goal / full-goal awards.
- **Match structure:** four periods, overtime and sudden death.
- **Scoring:** flat by default, with the banded scale as a switch.

**3. Simplified or unproven.**
- Attributes and position behaviours are **ARCADE PLACEHOLDERS** derived from the single OVR.
- There is no dribble action, so the one-dribble rule cannot happen. There is also no kicking action.
- Carry goals are implemented but never happened in the test matches.
- Fouls are reduced to: holding (AI, random), delay of game, and majors for contact with a frozen or immune player.
- Sprites are simple procedural figures (about 45 px tall at default zoom).
- AI balance has not been tuned:
  - the stronger roster wins heavily (Ala Marauders, average starter OVR 89.6, beat Xenar Ignite, 71.0, by 14-0);
  - Archers fire about 200 arrows per match.

**4. Blocking.** Nothing blocks play. One reproducibility limit:
- A fixed seed gives the same result within one JavaScript runtime. Two headless runs in Node match exactly, and so do the browser runs at 1x, 8x, 32x and 64x.
- The Node headless run and the Chromium run drift apart late in the match (from about the 46th game-minute checkpoint), most likely because of tiny maths-library differences between the two engine versions. With seed 20261115 both still end 14-0, but the final state hashes differ.

**5. Recommended action.**
- Play one Human vs AI match (`npm install && npm run dev`).
- Decide whether the AI should be more even between teams, and whether to add a dribble action.
- If exact Node-to-browser identity matters, run the full-length check inside the browser (already done here) or replace the remaining maths-library calls with deterministic versions.

---

## Evidence

### Launch

```
cd arcade_claude && npm install && npm run dev      # http://localhost:5173
npm run build                                        # static build to dist/ (verified: builds, 253 KB JS)
```

There is no hosted preview URL; the build is static and can go on any static host.

### Architecture (as built)

- `src/engine/engine.ts` is the authoritative engine: 60 Hz fixed steps (`DT = 1/60`), seeded mulberry32 RNG only, and no DOM. Rendering (`src/render.ts`) only reads its state.
- `HumanController` (`src/main.ts`, keyboard and gamepad) and `AIController` (`src/engine/ai.ts`) both produce athlete **intents**. The engine turns intent into motion (acceleration-limited to OVR-derived top speed), throws (ballistic ball with gravity and bounce), tackles, catches and arrows.
- There is no separate result generator. Every goal, tackle, interception, arrow hit and possession change comes from the simulated play.
- **Information boundary:** each AI athlete keeps its own memory, updated only by its perception: a 200° view cone with sweeping gaze, a range from the OVR placeholder, and 6 m proximity. Archers have a wider elevated view. Decisions read only that memory plus public referee state (phase, possession call, tackle count, clocks). No hidden or future state is used.
- This is a separate TypeScript arcade implementation of the canon. **Arcade results are not simulator evidence.**

### Canon implemented

| Rule | Status |
|---|---|
| 100 x 100 m field; goal semicircle r 3 m at the end line; quadrant net; whole ball must cross inside the semicircle | IMPLEMENTED |
| Keeper Zone < 20 m from goal centre; Archer platform 5 m high, 5 m back, centred on the goal plane; centre circle 10 m; 40 m scrimmage lines; no extra marks | IMPLEMENTED |
| 12 on field (10 + KPR + ARC) from "Projected starter"; formation string places the 10 field players | IMPLEMENTED (bench is loaded but substitutions are not used) |
| 4 x 600 s; clock stops on dead balls; First Hunt at each period and OT; 30 s play clock carried through a tackle, fresh after score or turnover; expiry is a turnover at the spot or own 40 m line | IMPLEMENTED |
| OT 300 s, then sudden death (any score wins) | IMPLEMENTED; TESTED (an HvA browser match ended in sudden death) |
| Breaks 2 / 10 / 2 min as skippable screens; ends exchanged | IMPLEMENTED (ends are exchanged at **every** break, which is my reading of the rule) |
| Optional accelerated clock: visible setting, off by default | IMPLEMENTED (4 x 120 s or 4 x 60 s; HUD shows "ACCEL CLOCK") |
| Tackles: first grounding gives a Contact Scrimmage (carrier snaps, tackler 5 m back, snap within 10 s); second is a turnover | IMPLEMENTED |
| Goal, then scrimmage at the conceding team's 40 m line, count 0; out of play gives a toss-in at the crossing point with opponents at least 3 m away | IMPLEMENTED |
| Flat scoring default (goal 2, half goal 1); banded switch (carry 5; thrown < 10 / 10-20 / >= 20 m gives 2 / 3 / 4; half 1; award 3; own goal 2) | IMPLEMENTED; banded TESTED headless (2 / 3 / 4-point goals observed) |
| Defensive minor at tackle count 0: half goal in P1-3, full goal in P4 and OT | IMPLEMENTED (observed) |
| Fouls: majors give 120 s exclusion then DQ; 4th minor gives 60 s, 5th gives DQ; delay of game counts as an offence minor (tackle count +1) | IMPLEMENTED, **simplified** (see list below) |
| Keeper immunity in the KZ while playing the ball; attacker 5 s KZ limit (turnover at the 20 m line); defenders kept within 5 m of an attacker (AI behaviour, not enforced) | IMPLEMENTED / partly simplified |
| Archer: 250 m/s; 15 arrows and 5 freezes per team possession, reset on turnover; 5 s freeze, 3 m / 2 s recovery, 10 s immunity; no shots at frozen or immune players, outside own half, or during a Hunt; no reload rule | IMPLEMENTED; HUD ammo counter |
| Speed scale: rating x 44.704 m/s | IMPLEMENTED (OVR to rating is an ARCADE PLACEHOLDER, 0.17-0.215, about 7.6-9.6 m/s) |

### Simplifications and incomplete items

- **ARCADE PLACEHOLDERS (not canon):** OVR to attributes (`src/engine/data.ts:attrsFromOvr`), position to behaviour line (`LINE_PREF`), jersey numbers (hashed from Player ID, because the workbook has none).
- **No dribble or kick actions**, so the one-dribble and kicking rules never trigger. The dribble counter is not implemented.
- **Fouls:**
  - A human J press only tackles the ball carrier, so off-ball majors cannot be committed by accident.
  - Majors arise from contact with a frozen athlete or an immune Keeper.
  - AI holding minors are skill-weighted random events.
  - "Contact after the whistle" is not modelled.
  - Excluded or disqualified athletes are not replaced (the team plays short).
- **Defender Keeper Zone rule:** AI positioning respects it, but breaches are not penalised.
- **Archer aim for humans:** E auto-aims, at the carrier or the opponent nearest the ball.
- **Carry goals:** the AI attempts them when close to an empty goal mouth. None happened in the test matches.
- **Balance:** not tuned. OVR differences dominate, and Archers fire often (about 200 arrows, about 33% hit rate).

### Rosters

- **Source:** `NBL_2026-27_Opening_Night_Rosters_CANON_OVR.xlsx` from `origin/claude/hp002-audit:audit/arcade/`.
- **Export:** `scripts/export_rosters.py` writes `data/rosters.json`.
- **Coverage:** 26 franchises, 712 players. Canon fields are copied verbatim: ID, name, position, age, YOE, pre-camp / change / **opening-day OVR** (the one displayed and used), camp score, readiness, familiarity, role, formation, salary, development.
- **Starter check:** every franchise has exactly 12 Projected starters with 1 KPR and 1 ARC. "Registered" and starter counts match the League Overview sheet. No problems were found.

### Logos (Drive folder `1Y8JhgMbo1-yZD6Z7tOaM7AQliE4CqiFN`)

- **Access:** I downloaded the 26 files through the Google Drive connector. The originals are kept only in git-ignored `arcade_claude/.scratch/logos_src/` and are **not committed**.
- **Mapping:** **26 MAPPED, 0 UNMAPPED, 0 REPLACEMENT, 0 TEMPORARY.** 21 matched by the team name in the file name. 5 Drive files have no team in their name; I matched those by the team name printed on the logo itself, and `data/logos_manifest.json` records this in each entry's `match` field:
  - Ashkara Ignivars (`ccd19833-….png`)
  - Bibi Nupi Barbarians (`drebenzi_Color_scheme_is_Deep_maroon_Gold_and_Brown…png`)
  - Kalundu Shockwave (`1E16C4E0-….png`)
  - Khemara Sunscourge (`f0daed4b-….png`)
  - Zafiren Tidewings (`cc471768-….png`)

  Please confirm these five.
- **Spelling:** the Priya file and logo say "ARPAGU"; the workbook says "Arpaqu".
- **Outputs:** `assets/logos/<slug>_128.webp` (in-game, longest side 128) and `<slug>_256.webp` (matchup, break and final screens).
  - Transparent; aspect ratio preserved.
  - Uniform backgrounds are removed by flood fill.
  - Kalundu and Yukïma have textured backgrounds; those are kept and given a rounded-square mask.
- **Sizes:** largest file 25,376 B (under 25 KB). 128 set: 298,676 B. 256 set: 596,912 B. **Whole logo set: 895,588 B (under 1 MB).**
- **Readability:** all 26 are readable at 128 px, so no REPLACEMENT crests were needed.
- **Palette:** `data/team_colors.json` covers **26 franchises**:
  - primary, secondary and accent colours, extracted from each logo by `scripts/extract_logos.py` (median-cut quantisation, ranked by saturation, outline white/black penalised);
  - a jersey number colour chosen for contrast on the primary (lowest 4.2:1, Lykessia);
  - a 3-letter abbreviation.

  Colours are used on uniforms, scoreboard, team select, Keeper Zones, period-break and final screens.
- **Reproducible:** `python3 -I scripts/extract_logos.py` reads `scripts/logo_sources.json` (franchise, Drive id, source file name). If the folder is ever re-downloaded, drop it into `arcade_claude/assets/logos_raw/`.

### Athlete sprites

- **Drawing:** procedural Canvas drawing (`src/sprites.ts`), original art, **0 bytes of image assets** (code about 10 KB).
- **Shared body sheets** are parameterised and tinted at runtime: 3 builds x 4 skin tones (a range of brown tones) x 4 hair options (short, fade, locs, braids) x 4 face options (clean, beard, moustache, full beard). Height varies by ±8% and the build leans by position. Every athlete is a Black man, and appearance is fixed per Player ID.
- **Kit:**
  - compact padded helmet with a clear visor;
  - low-profile shoulder pads;
  - jersey and shorts in team colours, with the number on the torso strike panel and strike panels on the thighs;
  - red (frozen) and amber (immune) helmet lights.
- **Keepers and Archers:**
  - Keepers wear an accent-coloured jersey with a primary stripe and gloves.
  - Archers wear a lighter jersey, carry a bow and stand on the platform.
- **Animations:** idle, run, sprint, throw, catch, tackle, tackled (on the ground), frozen (ice tint), celebrate.
- **Limits:** faces are minimal at game scale, and there is no close-up gallery screen.

### Tests run (all on 2026-11-15, this branch)

Browser checks: `node tests/browser_check.cjs` (Playwright and headless Chromium against the dev server). The log is `tests/evidence/browser_check.log` and the data is `tests/evidence/browser_results.json`. **16 / 16 PASS:**

1. Launch: main menu visible.
2. Team select: 26 franchise tiles with loaded logos.
3. Human vs AI match starts with 24 athletes.
4. Human athlete moves (S) and sprints (Shift+W): sprint 8.16 m/s against 6.55 m/s jog cap.
5. Human pass (Space): 6 attempted / 5 completed, possession change.
6. Human tackle (J) grounds a carrier.
7. HvA with the 60 s accelerated clock (visible setting) plays all 4 periods plus OT and sudden death; the final screen shows.
8. Scoreboard equals the sum of scoring events.
9. Rematch keeps the same teams and seed and resets the score to 0-0.
10. Pause (Esc) works.
11. Controls screen works.
12. Quit to menu works.
13. **AI vs AI full canon-length match, Ala Marauders vs Xenar Ignite, from workbook data, no keyboard input (human intents null), at 64x:** final 14-0 after 4 periods.
    - 12 athletes each, Keeper = KPR and Archer = ARC on both sides.
    - Shots 51 / 8.
    - Keeper saves 8 / 31.
    - Arrows 191 (66 hits) / 208 (69 hits).
    - Possession 1215 s / 1178 s.
14. Playback 1x, 8x and 64x give the identical state hash at tick 3600 (`6f01359c`).
15. Full match at 32x and at 64x gives the identical final score and state hash (`e98a1db1`, 181,227 ticks).
16. No console errors or page errors.

Headless runs (`npx tsx scripts/headless.ts`, about 3 s per full match):
- Seed 20261115, two runs: identical output (14-0, hash `4ef72461`), saved in `tests/evidence/headless_marauders_xenar_seed20261115.json`.
- Other seeds: 7 gave 19-2, 99 gave 7-8 (Xenar win), 2026 gave 16-2.
- Banded scoring, Ala Apex vs Kalundu Shockwave: 19-8, with 2, 3 and 4-point thrown goals.

Screenshots: `tests/evidence/04_play.png` (gameplay, tackle), `07_ava.png` (AI vs AI), `06_final.png` (final with stats).

### Known issues

- Node headless and Chromium diverge late in a match (state hash differs from about the 46th checkpoint; same final score for seed 20261115). Reproducibility holds within one runtime.
- If a human player never snaps, delay-of-game minors pile up. The browser test showed 38 minors for the human side while the bot sat idle at 8x. This follows the rules, but the result is harsh.
- The final and break screens can be taller than a 720 px window (now scrollable).
- Arrows resolve in under 0.3 s, so the tracer is brief; hits read mainly through the 'ARROW HIT' banner, the ice tint and the red helmet light.

---

## Addendum: touch controls and phone hosting

- **Hosting:** `.github/workflows/arcade-pages.yml` builds `arcade_claude/` and publishes `dist/` to GitHub Pages on pushes to `claude/arcade-1` (Pages source set to GitHub Actions). Live at `https://drelenj.github.io/beastball_simulator/`.
- **Touch controls** (`src/touch.ts`, shown only on touch devices or with `?touch=1`):
  - left thumb: floating joystick, push to the outer ring to sprint;
  - right thumb: PASS (also the snap), SHOOT, TACKLE, SWITCH, ARCHER, and a SPRINT hold button;
  - II button pauses;
  - Home/Away picker on team select (replaces Shift-click);
  - retina-sharp canvas (DPR capped at 2), iOS meta tags, pinch and double-tap zoom blocked during play, rotate hint in portrait.
- Touch drives team 0 only, so Human vs Human is still a keyboard/gamepad mode.
- **Tests:** `node tests/touch_check.cjs` (emulated iPhone, landscape, DPR 3, real CDP touch events including two simultaneous fingers): 14/14 PASS. Desktop suite re-run after the change: 16/16 PASS. Not tested on a physical iPhone.

## Addendum: throw and pass feel

- Passes fly at `min(1.3 x throwV, 13 + 0.95 x distance)` m/s (was `min(throwV, 9 + 0.55 x distance)`): about 0.35 s at 10 m and 0.6 s at 20 m, on a low arc. Shots are 1.3x faster. In-flight speeds measured in the browser: 29-31 m/s.
- The ball is drawn as a round ball with rotating seams to show spin, plus a speed trail.
- Catch speed penalty retuned (passes 27 m/s threshold, shots 16 m/s) so faster balls stay catchable.
- Effect over 8 headless matches (before -> after): pass completion 69% -> 72%, goals/match 6.1 -> 9.1, saves 35 -> 43, tackles/match 171 -> 143. Scoring is higher and carriers release the ball sooner; unchanged from this: determinism (same seed, same result).
- The human-tackle checks now place the athlete beside an opponent carrier (labelled in the test name) and use the real J key / TACKLE button, because chasing a carrier in real time became unreliable once opponents pass faster.
