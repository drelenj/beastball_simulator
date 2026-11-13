# HP-002 — Owner decisions D1: record and derived rules-state table
Claude, 2026-11-12. Records the owner's answers of 2026-11-12 19:48 (America/Chicago) to `audit/HP-002_OWNER_DECISION_SHEET_D1.md`. Status of the owner rulings: **CANON (owner-approved)**. Status of section 3 (derived transition table): **DESIGN COMPLETE, not implemented, not tested, not accepted.**

## OWNER BRIEFING
1. **Accomplished.** Every canon gate that was blocking M3 and M4 is now answered: Keeper protection (U-1), zone clock (U-2), zone geometry (U-3), restarts and bounces (U-4), ruleset (R-RS = 1.0.2) and self-knowledge (SELF-1 = exact). I recorded them and derived the rules-state transition table from them.
2. **What B1 can do now.** No change at runtime. Nothing here is implemented, tested or accepted.
3. **Unproven.** The derived table has never been run. It also rests on one number (0.5 s) that the tests must check.
4. **Blocking.** No canon decision blocks the next step. Engineering is next: Codex implements the possession and rules-state layer and ruleset 1.0.2 in the B1 path; I review it.
5. **Recommended action.** Approve the three derived consequences in section 2 (or veto them). Then relay this record to Codex.

## 1. Owner answers, as stated
| Item | Owner answer |
|---|---|
| A3 | "Passive possession" replaces "passing possession" in all later mentions. Same mechanics, only the name. |
| P-1 | "your recommendation": 0.5 s uncontested time as a configured parameter; tests measure 0.25 / 0.5 / 1.0 s; escalate only for a material gameplay difference. |
| P-2 | "contested is touching the actual game ball. Anytime players from opposing teams are simultaneously touching the game ball, it is contested." (**overrides my recommendation**, which was based on physical engagement) |
| P-3 | my recommendation: no passive possession until the first direct possession; a rule-awarded restart sets it immediately to the awarded team. |
| P-4 | my recommendation: team control (TC) is the sub-state of passive possession in which the ball is carried or on a deliberate pass. |
| U-1 | my recommendations KP-01..KP-14 and KP-OG as listed in sheet D1 §C. |
| U-3 | my recommendations G-1..G-6 as listed in sheet D1 §D. |
| U-4 | my recommendations U4-01..U4-13 as listed in sheet D1 §E. |
| A1–A8 | Not objected to; recorded as confirmed (A3 renamed). |

## 2. Consequences I derived from your answers (please veto any you disagree with)
- **C-1.** Contest lapses direct possession; it does not change passive possession. While opposing players are both touching the ball nobody has direct possession and the 0.5 s timer is at 0. Passive possession stays with the last team that had direct possession. It flips only when the other team has uncontested control for 0.5 s.
- **C-2.** Because contested means touching the ball, body contact alone does not contest. A tackle on a carrier who is not touched at the ball does not reset the timer. (A held ball that a defender touches is contested immediately.)
- **C-3.** U4-12 (same-instant touches) is now simply a case of P-2: contested, no first-touch violation, passive possession unchanged. U4-05 stays as recommended; "hand-fight" is no longer a rule term.

## 3. Derived rules-state contract (DESIGN COMPLETE)
**Public state:** `ball_status` ∈ {carried, pass_in_flight, shot_in_flight, loose_ground, loose_airborne, out_of_play, restart_pending}; `direct_possession` (team, holder, or none); `passive_possession` (PP: team or none); `contested` (bool); `uncontested_ms`; `team_control` (TC); `origin` (outside/inside own zone); `last_toucher`; per-team `zone_clock_ms` and running flag; `phase(team)` = offense iff PP is that team, else defense (none: neither).
**Parameters:** `direct_possession_threshold_ms` = 500 (tested at 250/500/1000), `keeper_zone_radius` = 20, `ruleset` = 1.0.2.
| Row | State → event | Result |
|---|---|---|
| R-01 | Opening scrimmage, ball live, no direct possession yet | PP = none; no offense/defense; Archer target set empty (Hunt rule) |
| R-02 | A player secures the ball; no opposing player touching it | `uncontested_ms` runs; DP and PP unchanged until threshold |
| R-03 | `uncontested_ms` ≥ 500 for team X | DP = X; if PP was not X, PP = X and zone clocks reset (A5) |
| R-04 | Opposing players simultaneously touching the ball | `contested` = true; DP = none; `uncontested_ms` = 0; PP unchanged |
| R-05 | Contest ends, one team alone touching | `uncontested_ms` restarts at 0; R-03 applies |
| R-06 | Carrier releases a pass | TC kept (deliberate pass); DP = none; PP unchanged |
| R-07 | Shot released | TC = none; PP unchanged (shooter's team) |
| R-08 | Defender touches ball without a contest lasting | TC ends; zone clock resets (A5); PP unchanged |
| R-09 | Fumble, strip, drop | ball loose; TC none; DP none; PP unchanged |
| R-10 | Opponent has uncontested control for 500 ms | PP flips (R-03); zone clocks reset |
| R-11 | Carrier crosses from outside into own zone, TC held | ZR-C violation → RST-1 |
| R-12 | Deliberate pass enters own zone from outside (incl. bounce pass, U4-01/02/03) and a teammate touches first | ZR-T violation → RST-1; a defender first: none |
| R-13 | Ball in own zone, own team has PP, 5 s without a reset | ZR-1 violation → RST-1 |
| R-14 | Ball leaves the zone / PP changes / defender touch / restart / dead ball | zone clock reset to 0 (A5) |
| R-15 | Keeper's team has PP and Keeper inside own zone | opponent-initiated contact prohibited; no freeze (KP) |
| R-16 | Keeper outside own zone, or his team lacks PP | ordinary contact rules; freezable outside the zone |
| R-17 | Arrow hits an eligible non-Keeper | freeze under ruleset 1.0.2 (any eligible player) |
| R-18 | Ball out of play | PP unchanged until the restart awards it; restart sets PP to the awarded team at once (P-3) |
| R-19 | RST-1 restart | PP = opposing team; origin = outside; zone clock 0 and stopped |
| R-20 | Dead ball, timeout, period break | zone clock reset to 0 and stopped until live |
| R-21 | Keeper catches opponent shot inside own zone | PP stays with shooter's team until R-03 passes; then flips; Keeper protection begins at the flip |
| R-22 | Same-instant touches by both teams | R-04 (contested); no ZR-T violation |

## 4. Engineering follow-ups (no owner decision)
1. Codex: implement the possession and rules-state layer, ruleset 1.0.2 in the B1 path (B0 stays 1.0.1), contract hash and conformance profile `v1-m3` replacing the "unresolved" policies.
2. Define "touching the ball" from the engine's ball-contact events; note the B0 engine tracks carrying and catches, not simultaneous touches, so a touch-event source needs checking (engineering, not canon).
3. Tests: one per row R-01..R-22, plus the 250/500/1000 ms sensitivity run.
4. The sprint's Keeper and Archer primitives are replaced against this contract in milestone order.
