# HP-002: Ideal Beastball as measurable targets (v0, DESIGN COMPLETE as a draft only)
Claude, 16 Nov 2026. Purpose: tear down from the ideal. Each target is a number a run can fail. Nothing here is implemented, tested or accepted, and no number marked PROPOSED is canon until the owner sets it.
Scoring basis (owner, 16 Nov 2026): the banded scale is the working canon for now and ALL tests and measurements run on banded scoring: carry 5; throws 2/3/4 by release distance; half goal 1; full-goal award 3; own goal 2. Flat scoring is not used for targets.
Class tags: CANON = owner decides. ENG = engineering resolves with evidence. BEH = behavioral default, tested.
Source: OWNER = stated by DreLen. PROPOSED = my placeholder range for the owner to set or strike.

## A. Flow
| # | Target | Source | Class | Evidence today |
| --- | --- | --- | --- | --- |
| T1 | About 100 possessions per team per match | OWNER | CANON | Not measured |
| T2 | About half of possessions end in a scoring attempt | OWNER | CANON | Not measured; Native seed 1 has 435 arrows but few shots |
| T3 | Average team score 80-85 under banded scoring | OWNER | CANON | Not measured; see Q1 |
| T4 | Most points come from play, not penalty awards (PROPOSED: at least 85%) | PROPOSED | CANON | About 22% (penalty awards about 78%, RB-1 seed 6) |
| T5 | Restart timeouts rare (PROPOSED: under 5% of restarts) | PROPOSED | BEH | 25.6% (Native v0, seed 1) |

## B. Contact
| # | Target | Source | Class | Evidence today |
| --- | --- | --- | --- | --- |
| T6 | Tackles to ground per team per match in the dozens, not single digits (PROPOSED: set from T1 and the tackle-count rule) | PROPOSED | CANON | 6 groundings in 2400 s (Native seed 1) |
| T7 | A strong, balanced carrier can escape a wrap that has not grounded him; outcomes decided by mass, velocity, grip and body part, with no special rule | OWNER | ENG | Contact module exists in duel lab, not in Native full matches |
| T8 | A single defender can ground a carrier in open space (strip, ankle wrap, drag, hit-stick) | OWNER | ENG | Not demonstrated in Native |

## C. Archer and Keeper
| # | Target | Source | Class | Evidence today |
| --- | --- | --- | --- | --- |
| T9 | Arrow speed 250 m/s, fixed | OWNER | CANON | Native v0/2: 29 m/s (F-1) |
| T10 | Legal arrows are the large majority (PROPOSED: at least 90% of released arrows) | PROPOSED | BEH | About one third legal (RB-1) |
| T11 | Archer uses most of a possession's 15 arrows and 5 freezes only when targets exist | PROPOSED | BEH | Not measured |
| T12 | Keeper stops are decided by net size, Keeper height (9-12 ft) and reach, not a Keeper-only boost | OWNER | ENG | Keeper reach vs 3 m goal open (3.4-4.3 m standing reach) |

## D. Bodies and ratings
| # | Target | Source | Class | Evidence today |
| --- | --- | --- | --- | --- |
| T13 | Top speed = rating x 44.704 m/s | OWNER | CANON | Native placeholder 27 m/s |
| T14 | Ratings are the only knobs; same rating means the same output at any size; size matters through physics | OWNER | ENG | ATTR-1 branch, not reviewed |
| T15 | Starters play about 32 of 40 minutes; sub out at energy 0.6, return at 0.75; Keeper at least 36 | OWNER | ENG | No fatigue layer found |

## E. Integrity and cognition
| # | Target | Source | Class | Evidence today |
| --- | --- | --- | --- | --- |
| T16 | Same seed gives identical event hash | OWNER (determinism gates) | ENG | PASS in reviews |
| T17 | Athletes read only their own view (no hidden ratings, no coach ranking) | OWNER | ENG | PASS (RB-1, Native R10) |
| T18 | Minors, majors, DQs are rare (PROPOSED: DQs under 1 per match) | PROPOSED | BEH | 17-27 DQs per match (RB-1) |

## Derivation chain (two examples)
- T4 and T18 need legal Archers (T10) and a live tackle game (T6): penalties are 78% of points today because arrows are mostly illegal and no tackle game generates normal outcomes. Fix order: Archer legal-target cognition, then tackle decision, then re-measure T4.
- T1 and T2 need short, decisive possessions: restart timeouts (T5), the 30 s clock and tackle-count turnover all feed possession count. Measure possessions before tuning anything else.

## Open owner questions
- Q1 (CANON, narrowed): the flat-scoring conflict is gone now that banded is the basis. About 50 attempts per team and 80-85 points needs about 1.6-1.7 points per attempt, which banded values (2/3/4 throws, 5 carry) can reach if conversion and long-throw share are healthy. Open: confirm 80-85 is the intended target under banded, and note it will be measured by points per attempt split by band (carry, throw distance, half goal, award).
- Q2 (CANON): set or strike each PROPOSED number (T4, T5, T6, T10, T11, T18).

## Slice 0 (proposed first test)
One contact duel (T7, T8) and one Archer with legal-target knowledge (T9, T10), each run over 200 seeds, ratings only. Pass means the mechanic produces the target behavior at plausible rates; fail names the value to revisit. No full match until both pass.
