# HP-002 — Owner decision sheet D1: closing the remaining canon gates
Claude, 2026-11-12. Status: **DESIGN COMPLETE (proposal). No rule below is canon until you approve it.** Your rulings are recorded exactly as you stated them in section A. Everything in sections B–E is *my recommended answer*, derived from your rulings, your earlier approvals (S1–S8, CE-C1..C3, the Keeper protection statements, ARC-1, RST-1, ZR-1, ZR-2) and observed B0 behavior. Reply **"Approve all"**, or **"Approve all except <IDs>"** and give your answer for those.

## OWNER BRIEFING
1. **Accomplished.** Your possession model resolved four of the five open gate groups (zone-clock resets, ruleset, self-knowledge, and the Keeper "phase" question). It also replaces my earlier possession definitions, so I rebuilt the sheet around it.
2. **What B1 can do now.** No change at runtime. This is design only; nothing is implemented, tested or accepted.
3. **Unproven.** Every answer below is untested. Two of them interact in a way you should see before choosing (P-1 and U4-08).
4. **Blocking.** 37 questions remain: 4 from your possession model, 13 Keeper protection, 1 own-goal meaning, 6 zone geometry, 13 restart/bounce scenarios. Each has a recommended answer.
5. **Recommended action.** Answer **P-1 first** (the uncontested-time number). Then "Approve all" for the rest, or change the few you disagree with.

## A. Your rulings, as I recorded them (confirm the wording)
| ID | Ruling |
|---|---|
| A1 | The offensive team is the team in possession of the ball. The defensive team is the team not in possession. |
| A2 | **Direct possession:** a player on the team has uncontested contact and control of the ball (time threshold: see P-1). |
| A3 | **Passing possession:** the last team to have direct possession. It covers the ball being loose, airborne, or contacted by the opposing team. |
| A4 | Contact is not possession: touching the ball does not equal possessing it. |
| A5 | **U-2 zone clock:** the clock resets on any of: the ball leaving the zone, passing possession changing, a defender touching the ball, a restart, a dead ball. |
| A6 | **R-RS:** B1 runs ruleset **1.0.2**. |
| A7 | **SELF-1:** athletes know their own abilities exactly, as of now (revisitable). |
| A8 | **KP-12 is resolved by A1+A3:** a Keeper's team is on offense exactly while it has passing possession (including while the ball is loose or in the air). |

What A6 and A7 change: under 1.0.2 an arrow hit freezes any eligible player, not only the ball carrier (a Keeper inside his own zone stays protected). B0 stays at 1.0.1 for its frozen evidence; B1 runs 1.0.2. SELF-1 keeps the current exact self-knowledge default.

## B. Questions created by your possession model
| ID | Question | Recommended answer |
|---|---|---|
| **P-1** | How long must control be uncontested before it counts as direct possession? You suggested at least 1 s but worried it is too long. | **0.5 s as a configured parameter, with the tests measuring 0.25 / 0.5 / 1.0 s.** I would escalate to you only if the gameplay differs materially. *Why it matters:* until the threshold passes the other team still holds passing possession, so under U4-08 a Keeper who just caught a shot would be unprotected (and on defense) for that long. At 1 s that is a full second of exposure. **Your number needed.** |
| P-2 | What counts as "contested"? | An opposing athlete is physically engaged with the carrier or the ball (hand-fight, grip, hold, tackle contact), not merely nearby. Starting a contest restarts the timer. A contest alone does not change passing possession. |
| P-3 | Who has passing possession before anyone has had direct possession (the opening scrimmage)? | Nobody (no offense, no defense, no Archer targets) until the first direct possession. This matches the Hunt rule. When a rule **awards** possession (restart after a violation or out of play), the awarded team holds passing possession immediately. |
| P-4 | What replaces "team control" (used by ZR-2, "while his team was in control")? | Keep it as the sub-state of passing possession in which the ball is carried or is on a deliberate pass; it ends on shot release, the ball going loose, a defender's touch, or the other team gaining direct possession. |

## C. Keeper protection (U-1) — KP-12 resolved by A8
Basis: your statements (cannot be contacted on offense inside his zone; loses immunities once he leaves; never an Archer target; stays indefinitely; no other player gets this protection) plus B0 (no freeze inside own zone in any phase).
| ID | Aspect | Recommended answer |
|---|---|---|
| KP-01 | Incidental arrow in own zone, offense | No freeze. Impact is inert (B0). |
| KP-02 | Incidental arrow in own zone, defense | No freeze (B0). |
| KP-03 | Incidental arrow outside own zone, offense | Freezable like any eligible player. |
| KP-04 | Incidental arrow outside own zone, defense | Freezable. |
| KP-05 | Tackle in own zone, defense | Ordinary tackle rules apply; the no-contact protection exists only on offense. |
| KP-06 | Tackle outside own zone, offense | Ordinary tackle rules apply; protection ends when he leaves the zone. |
| KP-07 | Tackle outside own zone, defense | Ordinary rules. |
| KP-08 | Keeper-initiated contact in own zone, offense | Ordinary contact rules apply to him; his own contact does not make him contactable by others. |
| KP-09 | Other contact (block, screen, incidental), own zone, defense | Ordinary contact rules. |
| KP-10 | Same, outside zone, offense | Ordinary rules. |
| KP-11 | Same, outside zone, defense | Ordinary rules. |
| KP-13 | Which immunities exist | Exactly two, both only while inside his own zone: (a) no opponent-initiated contact while his team is on offense; (b) no freeze, in any phase. Plus the standing rule that Archers never target Keepers. |
| KP-14 | Persistence after leaving | None. Protection depends on the Keeper's position at the instant of contact; it returns on re-entry. |
| KP-OG | "Not eligible to score except own goals" | Reading: a Keeper cannot score for his team; a ball he puts into his own goal counts for the opponents. |

## D. Zone geometry (U-3)
Consistent with your 9 October ruling (a line belongs to the farther territory, so the Keeper Zone arc is outside).
| ID | Question | Recommended answer |
|---|---|---|
| G-1 | Athlete reference point | Body center. |
| G-2 | Ball reference | Ground position only; an airborne ball over the zone counts as in the zone (vertical cylinder). |
| G-3 | Edge | Inside means distance < R; a point exactly on the arc is outside. |
| G-4 | Boundary arc, end line, goal opening | The zone is the field area with distance < R from the goal center; the goal opening is part of it; the arc itself is outside (G-3). |
| G-5 | Radius | A configured value, default 20 m, identical for both teams. |
| G-6 | Which predicate each rule uses | Keeper protection and Archer legal range: athlete in zone (body center). ZR-T first touch and ZR-1 clock: ball in zone. ZR-C carrier crossing: the carrier's body center. |

## E. Restarts, bounces and out of play (U-4)
Throughout, "touch" and "possession" are separate (A4), and passing possession changes only when the other team gets direct possession (A3).
| ID | Scenario | Recommended answer |
|---|---|---|
| U4-01 | Bounce pass released outside, bounces outside, enters zone, teammate touches first | A bounce pass is still a deliberate pass; the ground contact does not end control. Violation (ZR-T). |
| U4-02 | First ground contact inside the zone | The landing counts as entering. A teammate's first touch afterwards is a violation. |
| U4-03 | Released inside, bounces out, returns | Violation on a teammate's first touch after re-entry, if no defender touched it meanwhile. |
| U4-04 | Release at the instant of crossing or from the arc | The state at the release instant decides, using the pre-event snapshot. On the arc counts as outside (G-3). A carrier already inside while still holding the ball triggers ZR-C at the crossing. |
| U4-05 | Release under hand contact | A release the athlete committed (an unforced B0 `release` pass or shot) is deliberate. A stripped or forced release is a loose ball. A defender's tip is a defender touch. |
| U4-06 | Defender touches the pass in the air without gaining control | Control (TC) ends at the touch; passing possession stays with the passer's team; a later teammate touch is not a first-touch violation. |
| U4-07 | Team regains control inside its own zone after a deflection | The origin is inside, the zone clock restarts (A5), and ZR-C applies to a later carry out and back in. |
| U4-08 | Keeper catches the opponent's shot inside his zone | Passing possession stays with the shooter's team until the Keeper's team has direct possession (P-1). Then it flips and the clock starts at 0 (A5). Keeper protection starts at the flip. |
| U4-09 | Ball out of play | Passing possession is unchanged until the restart; the restart awards it per the existing out-of-play restart rule. |
| U4-10 | Dead ball, timeout, period break | The zone clock resets to 0 and does not run until the ball is live. |
| U4-11 | Ball over the zone when 5 s expire | Counts as in the zone (G-2). |
| U4-12 | Offense and defender touch in the same instant | Counted as a defender touch: no first-touch violation, the ball is contested, passing possession is unchanged. |
| U4-13 | After a zone-violation restart (RST-1) | Passing possession goes to the opposing team; origin outside (center line); zone clock 0 and not running. |

## F. After you answer
1. I record your answers, the full transition table and the new contract hash.
2. Codex implements 1.0.2 in the B1 path and the possession model (direct and passing possession) as the rules-state layer.
3. Keeper, Archer and zone behavior replace their primitives in milestone order, each with a test that can fail.
Nothing in this sheet blocks the current M1 review.
