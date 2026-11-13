# HP-002 — Rules and mechanics profile audit (what is actually ON in B1 matches)
Claude, 2026-11-13. Subject: branch `experiment/emergence-1` head 761dca5 (contains B0, SPRINT-45 and Emergence-1). Status: audit evidence, not a rules decision.

## How this was checked
1. Ran a real B1 match (seed 1, 10 s proxy) with every `os.environ` / `getenv` read logged: **85 names read, with the value each one returned**.
2. Dumped the match's effective configuration: **52 `pocket` settings, 119 engine `assume` values, the engine's feature flags**.
3. Read the owner's rules document `RULES_FLOW_v0.3.md` (tags: [C] canon) and the source of `rules_v03.py`, the code that implements it.
4. "Not verified" means I did not read or run it.

## Headline
Most of RULES_FLOW v0.3 is implemented in `rules_v03.py` behind one switch, `RULES_V03`, whose default is **off**. B1 matches never turn it on. So they run the older B0 rules, not the v0.3 canon. The older Pocket scoring and archery limits differ from canon too. The B1 profile `B0-P4-DEFAULT` was a freeze profile for comparing B0 with B1, never "the Beastball profile".

## A. Canon in RULES_FLOW v0.3 vs what B1 matches run
| Canon item [C] | In code | In B1 matches | Evidence |
|---|---|---|---|
| Flat scoring: every goal 2, half goal 1, Carry tracked | `rules_v03` step 1 (`RV03_FLAT`) | **OFF**: inner 3, release 2, outside 1, Carry 4 | pocket `inner_points`=3 `release_points`=2 `outside_points`=1 `carry_value`=4 |
| Defender marking distance 5 m (Keeper Zone) | `rules_v03` step 1 | **OFF**: 3.0 m | pocket `marking_distance`=3.0 |
| Minor fouls change tackle count; half goal Q1-Q3, full goal Q4/OT | `rules_v03` step 1 | **OFF** | `RULES_V03`=0 |
| Major/minor ladder per player (4th minor 60 s, 5th DQ; majors 120 s / DQ) | `rules_v03` step 1 | **OFF** | `RULES_V03`=0 |
| Always 12 on the field (substitute covers every exclusion); forfeit below 12 of 22 | `rules_v03` step 2 | **OFF** | `RULES_V03`=0 |
| Archers: 25 arrows and at most 5 freezes per possession | `rules_v03` step 2 | **OFF**: arrow limit 30, no freeze cap, quiver does not refill per possession | pocket `arrow_limit`=30; env `FREEZE_CAP`=0, `QUIVER_POSS`=0 |
| Contact Scrimmage after a tackle (snap window, 5 m penalties, offside line) | `rules_v03` step 3 (`RV03_SCRIM`) | **OFF**: live recovery used | `RULES_V03`=0 |
| No kicking: kick releases become throws, shots use passing skill | `rules_v03` (`RV03_NOKICK`) | **OFF**: engine shot model uses the kicking attribute | `core_src/match.py make_shot`: skill = (kicking + ball_handling)/2 |
| Keeper Zone: attackers 5 s residence, expiry = turnover | engine (E kept) | ON | engine zone residence 5000 ms |
| Keeper may stay indefinitely | engine | ON (not re-verified in play) | not verified |
| Possession clock 45 s | engine | ON | pocket `play_clock`=45 |
| Freeze 5 s, post-freeze immunity 10 s | engine | ON | engine freeze: freeze_until = now+5000, immune_until = now+15000 |
| Throw split: Throw Power / Throw Accuracy / Touch (4 Nov) | engine | ON | env `THROW_SPLIT`=1 |
| League-average rating 0.7 | engine | ON | env `PRISM_RATING_CENTER`=.7; ratings 70 / 70 |
| First Hunt opening procedure | not found | **Not implemented** (document says "not yet implemented") | not verified beyond the document |
| Offside against the scrimmage line | partly inside the scrimmage step | OFF with the scrimmage | not verified |
| Off-ball contact legality (legal band, no gripping, intent) | spec only; `HAND_FIGHT` switch for hand fighting | **OFF** | env `HAND_FIGHT`=0 |
| Dribble once per possession (throw ahead and replay) | "rule without a decision" | **Not implemented** | RULES_FLOW amendment |
| Recovery protection 3 m / 2 s after a freeze | engine | not verified | not verified |
| Fatigue | engine has `fatigue_rate` | **OFF**: 0.0 | assume `fatigue_rate`=0.0 |

## B. Settings in B1 matches that are not canon or not decided
- 2 x 120 s match, not the 4 x 600 s league profile (period_seconds in the profile; 4 x 600 s never run in B1).
- Both teams rated 70 with the same Keeper height (3.2004 m = 10.5 ft); rosters differ per side (known).
- `ball_speed` 40, `pass_speed` 27 (single fixed values in the engine; B1 admits passes at 27 m/s with a 2 m/s upward component; B0's pass planning is bypassed: assume `c1_pass_planning`=1 but B1 submit does not use it).
- `reversal_rule`=0, `contact_roster`=0, `defense_A/B`=0, `ctrl_*` legacy controller values present but trapped from B1 cognition.
- Zone: inner zone radius 15, Keeper zone radius 20 (matches decision record R=20).
- Ruleset: B1 sets `ruleset` = 1.0.2 on its instance (verified in `matchport.py`); the env read still says 1.0.1 (default).

## C. B0's old PRISM perception layers are all OFF in B1 matches
`PRISM`, `PRISM_FIELD`, `PRISM_DEF`, `PRISM_OFFBALL`, `PRISM_TEAMVIEW`, `PRISM_FREEVIEW`, `PRISM_KEEPER`, `PRISM_MANEUVERS`, `PRISM_DRIVE`, `PRISM_BOUNDED`, `PRISM_JUDGE_DEF` = 0 in the logged run. B1's own sensor, belief and decision code replace them; this is intended (no legacy tactical controller). The weeks of PRISM v0.2-v0.7 work on B0's side is therefore not running; its ideas live on in B1's design, not its code path.
Only these B0 PRISM switches default on: `PRISM_CATCHERS`, `PRISM_BALLVIEW`, `PRISM_CARRIER_BELIEF`, `PRISM_REIDENT`.

## D. Engine mechanics ON (assume flags, verified in the logged run)
Contact kernel (`c3`, `c3b`, `c3c`), carry rules (`c4b`), zone engine (`c4_zone`, `c4c`, `c4c2`), catch model v1 (`c1_catch_model`=1; `CATCH_V2`=0), Keeper behaviour (`ctrl_keeper`, `keeper_*`), block and bounce options (`BLOCK_OPTION`, `BOUNCE_OPTION` default on).

## E. Why "passes one speed, two shot corners"
- **Pass:** the engine uses one configured speed (`pocket.pass_speed`) and its own planner works out lead and arc. B1's `pass-release-v1` throws directly at the believed receiver position at that speed with a fixed 2 m/s upward component: **no lead, no arc**.
- **Shot:** the engine's shot model aims one point: x at the goal line, y = 50 +/- (3.5 + 0.6 x skill) on the side away from the Keeper, height 2.8 + 0.3 x skill. B1 exposes only left/right.

## F. Not verified
Recovery protection values; offside details; Keeper-may-stay-indefinitely in play; every `pocket` and `assume` value against canon; whether each of the 119 `assume` values matches an owner decision; the 4 x 600 s league profile.

## G. Recommendation (owner decides what is canon for the experiment)
1. Define one named **experiment profile** file: every switch listed with its value, canon source, and "implemented / unimplemented". The match prints it at start and writes it into every trace and result row; a test fails on drift.
2. Candidate v1 experiment profile (my recommendation): flat scoring; everything else as today, until the owner chooses more. Then add `RULES_V03` bundle pieces one at a time and compare.
3. Owner decision needed: which RULES_FLOW v0.3 items are part of the experiment profile (scoring is already stated for the self-play experiment; marking 5 m, foul ladder, always-12, 25 arrows/5 freezes, scrimmage and no-kicking are tagged canon in the document but are not in the experiment-scoring section).
4. Engineering: implement First Hunt, offside, dribble, off-ball contact legality; restore pass lead and arc as athlete choices; expose shot height and speed.
