# SPRINT-45 canon notes: decision-sheet rows vs `b1/possession.py`

Source: `audit/HP-002_OWNER_DECISION_SHEET_D1.md` sections C, D, E (rows quoted) and
`audit/HP-002_OWNER_DECISIONS_D1_RECORD.md` (owner answers; derived table R-01..R-22 is DESIGN COMPLETE in the record).
Status words here: IMPLEMENTED (in `b1/possession.py`, unit-tested in `b1/test_possession.py`) / NOT IMPLEMENTED. Nothing is ACCEPTED.
`possession.py` only answers queries and records ledger entries; whether the runtime calls it and enforces anything is outside this module.

## Rules-state rows
- IMPLEMENTED + unit-tested: R-01..R-10, R-11 (ZR-C), R-12 (ZR-T), R-13 (ZR-1), R-14, R-15/R-16 (query `keeper_protected`), R-17 (query `freeze_legal`), R-18, R-19, R-20, R-21, R-22; P-1 at 250/500/1000 ms; P-3; C-1, C-2, C-3.
- Violations (ZR-1, ZR-C, ZR-T) are RECORDED with `restart: RST-1`, not enforced by the module.
- PRIMITIVE: "touching the ball" is whatever the caller passes in (`touching`, `touch` events).
- PRIMITIVE: ZR-C uses the ball ground position when the caller gives no `holder_xy` (G-6 asks for the carrier's body centre); the ledger entry is flagged `primitive_ball_proxy`.
- PRIMITIVE: `loose_ground` and `loose_airborne` are not distinguished (no height input).
- PRIMITIVE: `origin` (outside/inside own zone) is not a public field; it is tracked only as the pass/carry crossing state.
- UnresolvedOutcome is raised for: unknown event kinds, `freeze_legal` under a ruleset other than 1.0.2, `freeze_legal` for a role other than field/keeper (Archer eligibility is not in the record).

## C. Keeper protection (U-1)
| ID | Sheet row (quoted) | Status |
|---|---|---|
| KP-01 | Incidental arrow in own zone, offense: "No freeze. Impact is inert (B0)." | IMPLEMENTED as query (`freeze_legal` false for Keeper in own zone); arrow impact itself is engine |
| KP-02 | Incidental arrow in own zone, defense: "No freeze (B0)." | IMPLEMENTED as query |
| KP-03 | Incidental arrow outside own zone, offense: "Freezable like any eligible player." | IMPLEMENTED as query |
| KP-04 | Incidental arrow outside own zone, defense: "Freezable." | IMPLEMENTED as query |
| KP-05 | Tackle in own zone, defense: "Ordinary tackle rules apply; the no-contact protection exists only on offense." | IMPLEMENTED as query (`keeper_protected` false without passive possession) |
| KP-06 | Tackle outside own zone, offense: "Ordinary tackle rules apply; protection ends when he leaves the zone." | IMPLEMENTED as query |
| KP-07 | Tackle outside own zone, defense: "Ordinary rules." | IMPLEMENTED as query |
| KP-08 | Keeper-initiated contact in own zone, offense: "Ordinary contact rules apply to him; his own contact does not make him contactable by others." | NOT IMPLEMENTED (no contact-initiator input) |
| KP-09 | Other contact (block, screen, incidental), own zone, defense: "Ordinary contact rules." | IMPLEMENTED as query (not protected) |
| KP-10 | Same, outside zone, offense: "Ordinary rules." | IMPLEMENTED as query |
| KP-11 | Same, outside zone, defense: "Ordinary rules." | IMPLEMENTED as query |
| KP-12 | Resolved by A8: "a Keeper's team is on offense exactly while it has passive possession (including while the ball is loose or in the air)." | IMPLEMENTED (`phase`, `keeper_protected` use passive possession) |
| KP-13 | "Exactly two, both only while inside his own zone: (a) no opponent-initiated contact while his team is on offense; (b) no freeze, in any phase. Plus the standing rule that Archers never target Keepers." | (a), (b) IMPLEMENTED as queries; "Archers never target Keepers" NOT IMPLEMENTED here (cognition/runtime) |
| KP-14 | Persistence after leaving: "None. Protection depends on the Keeper's position at the instant of contact; it returns on re-entry." | IMPLEMENTED (queries are stateless in position) |
| KP-OG | "a Keeper cannot score for his team; a ball he puts into his own goal counts for the opponents." | NOT IMPLEMENTED (scoring is the B0 engine) |

## D. Zone geometry (U-3)
| ID | Sheet row (quoted) | Status |
|---|---|---|
| G-1 | Athlete reference point: "Body center." | IMPLEMENTED if the caller passes body-centre coordinates |
| G-2 | Ball reference: "Ground position only; an airborne ball over the zone counts as in the zone (vertical cylinder)." | IMPLEMENTED (`ball_xy` only) |
| G-3 | Edge: "Inside means distance < R; a point exactly on the arc is outside." | IMPLEMENTED, tested at exactly R |
| G-4 | "The zone is the field area with distance < R from the goal center; the goal opening is part of it; the arc itself is outside (G-3)." | IMPLEMENTED as the distance test; field-area clipping NOT checked |
| G-5 | Radius: "A configured value, default 20 m, identical for both teams." | IMPLEMENTED (`RulesConfig.keeper_zone_radius`) |
| G-6 | "Keeper protection and Archer legal range: athlete in zone (body center). ZR-T first touch and ZR-1 clock: ball in zone. ZR-C carrier crossing: the carrier's body center." | IMPLEMENTED; ZR-C falls back to the ball position without `holder_xy` (PRIMITIVE) |

## E. Restarts, bounces, out of play (U-4)
| ID | Sheet row (quoted) | Status |
|---|---|---|
| U4-01 | "A bounce pass is still a deliberate pass; the ground contact does not end control. Violation (ZR-T)." | IMPLEMENTED (ground contact is not an event; pass stays under watch) |
| U4-02 | "The landing counts as entering. A teammate's first touch afterwards is a violation." | IMPLEMENTED (ball ground position entering the zone) |
| U4-03 | "Violation on a teammate's first touch after re-entry, if no defender touched it meanwhile." | IMPLEMENTED, tested |
| U4-04 | "The state at the release instant decides, using the pre-event snapshot. On the arc counts as outside (G-3). A carrier already inside while still holding the ball triggers ZR-C at the crossing." | IMPLEMENTED with the ball position passed in the release step (PRIMITIVE: caller must pass the pre-event position) |
| U4-05 | "A release the athlete committed ... is deliberate. A stripped or forced release is a loose ball. A defender's tip is a defender touch." | IMPLEMENTED as event kinds (`pass_release`/`shot_release`, `loose`, `touch`); classifying engine events is the caller's job |
| U4-06 | "Control (TC) ends at the touch; passive possession stays with the passer's team; a later teammate touch is not a first-touch violation." | IMPLEMENTED, tested |
| U4-07 | "The origin is inside, the zone clock restarts (A5), and ZR-C applies to a later carry out and back in." | IMPLEMENTED (crossing state starts at control), carry-out-and-back not separately tested |
| U4-08 | "Passive possession stays with the shooter's team until the Keeper's team has direct possession (P-1). Then it flips and the clock starts at 0 (A5). Keeper protection starts at the flip." | IMPLEMENTED, tested (R-21) |
| U4-09 | "Passive possession is unchanged until the restart; the restart awards it per the existing out-of-play restart rule." | IMPLEMENTED (who is awarded comes from the caller/engine) |
| U4-10 | "The zone clock resets to 0 and does not run until the ball is live." | IMPLEMENTED, tested |
| U4-11 | Ball over the zone when 5 s expire: "Counts as in the zone (G-2)." | IMPLEMENTED (ground position only) |
| U4-12 | "Counted as a defender touch: no first-touch violation, the ball is contested, passive possession is unchanged." | IMPLEMENTED, tested (R-22) |
| U4-13 | "Passive possession goes to the opposing team; origin outside (center line); zone clock 0 and not running." | IMPLEMENTED for possession and clock (R-19, `rst1` flag on `restart_awarded`); restart placement NOT IMPLEMENTED |
