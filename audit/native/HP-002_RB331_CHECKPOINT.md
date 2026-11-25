# OWNER BRIEFING

1. **DESIGN COMPLETE, IMPLEMENTED, TESTED.** All eleven field starters have a coach rest window. Targeted catches, interceptions and other recoveries now have separate box-score columns. All 30 scheduled matches finished.
2. The eleven starters averaged **31.90 minutes**. At the fixed 0.52 fatigue scale, teams averaged **1.25 override exits**, below the 2–5 target.
3. Seed 1 had zero carry goals. The full sample recorded **29**. These match logs identify likely drivers and candidate changes. Paired counterfactuals would be needed to establish the effect of each candidate.
4. The maintained suite and replay identities passed. The mean production CPU change was **+2.31%**, which passed the 3% gate.
5. Review pass-lane prediction, goal-mouth approach and the carrier check before takedown commitment. Keep proposed behavior changes separate from this diagnostic.

## Standing gates

 a) pytest -q b1 native, full suite, after the last change.

 b) Legacy hash guards unchanged (six rows).

 c) Determinism.

 d) Compatibility: real seed 1 = 57-76, trace 44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072, state 046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d.

 e) CORE identity (fatigue off): neutral-real seed 1 = 61-80, trace c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256, state c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745.

 f) RB-3.28 identity (fatigue ON, threshold-only rotation): ratings 0.4, Garvian vs Ala seed 1 = 85-86, trace a399f74f81d891c8a0cd4014fc5d10bc5623ad835c448932a94cd50ffac7ac4b, state bc4898a8229d147bd60defdc623db55fac13a3845fb5f29f812198b4bf5f61d4.

 g) Speed: no more than 3% per step on top of RB-3.30 planned mode.

## Build and schedule

- Branch `codex/rb-3-31-diagnosis`, parent `f910ebeca4901ed970561ae30bbb1de7a62dc9bd`.
- Runtime plan and box changes `8bcbbef`, exact archive comparison `6d96105` carrier-specific audit closure `31a4e93` and empty-bucket summary handling `bd98d20`.
- The schedule covers Garvian–Ala seeds 1–10, Yukïma–Isu’Kari seeds 1–5, Mbuya Ïmu–Ala seeds 1–5, and five league pairings at seeds 1–2. Explicit ratings, individuation, hand-set values and the 0.52 fatigue scale are fixed. Commands and measurement definitions are in the [reproduction guide](rb331/README.md).

| Task | Status |
|---|---|
| 1. Plan all eleven | DESIGN COMPLETE, IMPLEMENTED, TESTED |
| 2. Separate secure-control credit | DESIGN COMPLETE, IMPLEMENTED, TESTED |
| 3. Observer diagnosis and soak | DESIGN COMPLETE, IMPLEMENTED, TESTED |

There are six field starters in Wave 1 and five in Wave 2. Each group is split
within one player. The rest windows and energy override are the same as
RB-3.30. Ten-minute periods give the coach a nominal 32-minute plan for every
field starter. Actual changes wait for a dead ball and an eligible substitute.
DreLen's ruling about the eleventh starter is recorded as resolved in
[QUESTIONS.md](../../QUESTIONS.md).

## Verification

`pytest -q b1 native` reported `805 passed, 1 warning, 23 subtests passed in 690.27s (0:11:30)`. All six legacy triplets matched.
Compatibility, CORE, and threshold-only replays matched gates d–f with the
current box-score observer enabled. The planned seed-1 replay reproduced
**64–96** in fresh processes.

- Planned seed-1 config `117f5525293e5a2a24476697e32278ca4fec2cb761a8e8df299e57e2d19410bc`
- Planned seed-1 trace `ab86f8befcf2baca264ab87fabdd39af3e218cb80032eab52b356a089319a08a`
- Planned seed-1 state `e8318c85ba3ae5205861d138f8d4f63e16202dd6d84f4ab8b5df02066e141047`

The production comparison uses four paired 1,500-step samples against the
parent runtime modules. CPU costs are **4.039**
ms/step for RB-3.30 and **4.133** for RB-3.31
(+2.31%). Optional audit recording measured
**4.070** ms/step (+0.76%
against the parent). These are opening windows. The soak separately covers
the later substitution windows.

## Box-score split on the identical RB-3.30 seed-1 game

The replay below uses the parent coach plan and reproduces 82–79 and its
exact hashes. The old catches subtotal is preserved under
`flight_balls_secured`. The total over all control events is
`balls_secured`, including pickups and other recoveries outside the old
pass-or-shot subtotal. The flight-only subtotal matches the archived box player by player. All 44 named rows passed the per-player comparison.

| Player | Targets | Old catches | Old drops | Receptions | Interceptions | Other recoveries | All balls secured | New drops |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Royce Voss | 18 | 24 | 1 | 13 | 4 | 13 | 30 | 1 |
| Julian Starhunter | 16 | 27 | 0 | 15 | 2 | 19 | 36 | 0 |

## Soak

All 30 matches finished, passed invariants and closed every restart.
The raw match runs took 5,143.51 process CPU seconds.

| Metric | Result |
|---|---:|
| Eleven field starters' regulation minutes, mean and range | 31.90, 27.16–35.45 |
| Reserve field regulation minutes, mean | 12.80 |
| Planned exits and returns per team per game | 21.37, 21.42 |
| Override exits and returns per team per game | 1.25, 1.03 |
| Median team score | 90 |
| Mean possessions per team | 153.40 |
| Possessions ending in an attempt | 34.42% |
| Ala minus Garvian mean margin ± SE | +22.90 ± 5.60 |
| Ala wins against Garvian | 9/10 |
| Games decided by at most 5 | 16.67% |
| Median absolute margin | 14.5 |
| Team score SD | 16.31 |
| Points from four-point throws | 44.34% |

The 0.52 scale stays fixed. In the parent soak, the unscheduled eleventh
starter accounted for **86 of 156** override exits. Giving that slot a
rest window removes a major source of prior overrides. The individual Stamina
breakdown is in the [aggregate JSON](rb331/evidence/diagnosis.json).

## Turnovers

| Box-score turnover type | Total | Per team per game |
|---|---:|---:|
| interception | 3202 | 53.37 |
| out_of_bounds | 1970 | 32.83 |
| score_restart | 1497 | 24.95 |
| fumble | 740 | 12.33 |
| opponent_control | 733 | 12.22 |
| tackle | 564 | 9.40 |
| zone_violation | 154 | 2.57 |
| play_clock | 81 | 1.35 |
| strip | 71 | 1.18 |
| toss_timeout | 38 | 0.63 |
| turnover | 26 | 0.43 |

The net turnover denominator is the existing ledger. Score restarts are
shown separately. The interception population includes **3678**
secured opposition passes, **482** at restarts.

| Intercepted pass witness | All | Open play |
|---|---:|---:|
| Paired geometry samples | 3678 | 3196 |
| Mean intended distance | 11.52 m | 11.83 m |
| Mean believed / physical / thrown margin | 6.46 / 2.25 / 2.25 m | 6.63 / 2.10 / 2.10 m |
| Believed clear, physically blocked | 1043 | 1020 (31.9%) |
| Throw yaw changes clear to blocked | 7 | 7 |
| Mean absolute initial yaw error | 0.41° | 0.47° |
| Under pressure, believed / physical | 1540 / 1796 | 1524 / 1787 |
| Interceptor in cone / radar | 2510 / 1270 | 2205 / 1146 |
| Absent from latest view | 785 | 704 |
| Never previously perceived | 1 (0.0%) | 1 (0.0%) |
| Mean passer Passing / Playmaking / Vision | 0.76 / 0.76 / 0.76 | 0.76 / 0.76 / 0.76 |

PERCEPTION and DECISION are plausible where the lane looked clear at
release but physical clearance was negative. The yaw-only flips bound one
observable EXECUTION mechanism within the planar proxy. Passing ratings
are descriptive, with no non-intercepted control cohort in this table.
The two visibility conditions overlap. The Passing menu filters variants
using a projected lane in `native/prism_core.py` and
`native/cognition_rb3.py::lane_margin`; the witness compares its inputs
with the state at actual release.

## Carries inside 20 m

| Held segment ending | Attempts | Median closest body distance to goal plane | Closest in group |
|---|---:|---:|---:|
| shot | 1692 | 8.82 m | 0.67 m |
| out_of_bounds | 683 | 0.42 m | 0.01 m |
| stopped_short | 301 | 12.80 m | 0.24 m |
| pass | 195 | 13.60 m | 0.75 m |
| tackle | 193 | 11.50 m | 0.72 m |
| handoff | 93 | 12.50 m | 0.67 m |
| goal | 29 | 0.58 m | 0.01 m |
| zone_violation | 27 | 2.59 m | 0.74 m |
| strip | 22 | 11.83 m | 1.22 m |
| freeze | 11 | 8.89 m | 1.79 m |

The pool contains **3246** attempts. **1180**
came within 3 m of the plane and **793** within 1 m.
Whole-ball mouth geometry and release distance govern the score. Perpendicular
distance to the plane alone does not establish legal carry scoring.
Seed 1 had 119 attempts, 62 ending in a shot,
21 out of bounds, and zero carry goals. The pooled
scoring ledger recorded 29 carry goals.

The soak measured 0 stretch starts,
0 stretch goals and
0 logged stretch ends. After carries
ended with shots, the follow-up outcome counts were {'on_target_not_scored': 68, 'goal': 922, 'keeper_save': 263, 'off_target': 441}.
The maintained tests confirm a held ball crossing legally gives five points
and a release inside 3 m gives five points. Exactly 3 m uses the throw band.
The scenario tests are `test_stretch_scores_while_ball_stays_in_hand`
and `test_release_carry_radius` in
[native/rulebook/test_rb318.py](../../native/rulebook/test_rb318.py).

## Committed takedowns

The intent episode denominator includes no-contact commits. The box-score
denominator requires a witnessed takedown drive during an engagement.
The former gives **2139/20012**
(10.7%); the latter gives
**2578/10565** (24.4%).
The accepted-episode join also records fewer successes than the physical
hold ledger. Its per-rating rates are bounded by the observed commitment
windows, with unresolved grips kept visible. The physical hold ledger is the
more direct comparison for the cited 80–90% gridiron and rugby reference.
The definitions would still need to be aligned for a cross-sport comparison.

| Episode outcome | Count | Median commit to outcome | Target was actual carrier at commit |
|---|---:|---:|---:|
| no_contact | 8521 | 291 ms | 1519 |
| grip_unresolved | 4093 | 651 ms | 3915 |
| contact_without_confirmed_grip | 3299 | 291 ms | 2643 |
| takedown | 2139 | 642 ms | 2040 |
| grip_lost | 1073 | 478 ms | 1047 |
| released_first | 773 | 145 ms | 770 |
| maneuver | 114 | 262.5 ms | 111 |

| Rating | Workbook band | Takedowns / commits | Rate |
|---|---|---:|---:|
| tackling | .65–.79 | 1041/9817 | 10.6% |
| tackling | <0.65 | 206/1973 | 10.4% |
| tackling | ≥.80 | 892/8222 | 10.8% |
| evasion | .65–.79 | 1111/10205 | 10.9% |
| evasion | <0.65 | 299/2763 | 10.8% |
| evasion | ≥.80 | 729/7044 | 10.3% |
| strength | .65–.79 | 984/8259 | 11.9% |
| strength | ≥.80 | 1155/11753 | 9.8% |
| balance | .65–.79 | 833/8698 | 9.6% |
| balance | ≥.80 | 1306/11314 | 11.5% |

Explicit maneuver breaks were {'stiff_arm_effect': 113, 'truck_broken': 6}. Nearby failed-commit
maneuver intents by type were {'hurdle': 895, 'stiff_arm': 439, 'spin': 498, 'truck': 200, 'juke': 155}. The latter
indicate timing overlap. The logs do not prove that a nearby maneuver caused
the failure. Grip loss is an EXECUTION witness. An unresolved sustained grip
can reflect either continued selection or insufficient force.

## Archers

| Measure | Result |
|---|---:|
| Defensive possessions | 9204 |
| Arrows per defensive possession | 1.63 |
| Body hits per defensive possession | 0.95 |
| Freezes per defensive possession | 0.46 |
| Defensive possessions with a freeze | 3529 (38.3%) |
| Turnovers within three seconds of a relevant freeze | 807 / 7583 (10.6%) |
| Relevant-freeze possessions followed by such a turnover | 807 / 1201 (67.2%) |
| Offense points per possession with / without a freeze | 0.45 / 0.60 |
| Peak charged arrows / freezes in quota epoch | 8 / 5 |
| Quota epochs reaching 15 arrows / 5 freezes | 0 / 7 of 9148 |

RULES account for charges, refunds and per-possession limits. The hit count
and number of epochs below the limits suggest opportunity, aiming decisions
and execution explain more of the observed volume than quota saturation. The points-per-possession
split is observational because long possessions can both produce more
scoring chances and leave more time for an Archer to freeze someone.

## Keepers

| Slice | Faced | On target with Keeper active | Saves | Saves / faced | Saves / on target | Goals | Goals touched |
|---|---:|---:|---:|---:|---:|---:|---:|
| All | 2805 | 2035 | 394 | 14.0% | 19.4% | 1486 | 109 |
| 2-point distance | 584 | 399 | 74 | 12.7% | 18.5% | 321 | 29 |
| 3-point distance | 1110 | 864 | 187 | 16.8% | 21.6% | 618 | 52 |
| 4-point distance | 1111 | 772 | 133 | 12.0% | 17.2% | 547 | 28 |
| Aim offset 1–2 m | 66 | 59 | 9 | 13.6% | 15.3% | 41 | 0 |
| Aim offset <1 m | 53 | 47 | 16 | 30.2% | 34.0% | 24 | 5 |
| Aim offset ≥2 m | 2686 | 1929 | 369 | 13.7% | 19.1% | 1421 | 104 |

On-target is an unobstructed trajectory estimate, with recorded goals
included. The ≥2 m offset group accounts for
2686 of 2805
shots faced. The Keeper touched 109 of
1486 goals in this shot sample. The wide release-time
offsets and low touch count make getting to the ball a stronger initial
hypothesis than failing to secure it after touch. DECISION places the Keeper
and selects the response. EXECUTION governs reach, reaction and contact.
The offset split does not isolate those effects.

## Leading causes and candidate changes

| Area | Evidence and likely cause | Candidate change and class |
|---|---|---|
| Turnovers 1 | 1020 open-play interceptions had a believed-clear but physically blocked lane. Stale or incomplete lane geometry is a PERCEPTION and DECISION hypothesis. | **BEHAVIORAL**. Test valuing passes against predicted release-time margin, including view age and uncertainty. |
| Turnovers 2 | Boundaries cost 32.83 turnovers per team per game. Margin to the boundary is a DECISION and EXECUTION hypothesis. | **BEHAVIORAL**. Test scoring and passing evaluations that price playable in-bounds landing space. |
| Turnovers 3 | Fumbles cost 12.33 per team per game. Ball security on loose releases is an EXECUTION hypothesis. | **BEHAVIORAL**. Compare high-speed and contact secures using fixed geometry before proposing a control adjustment. |
| Carry scoring 1 | Shots end 1692 held attempts in the pool and 62 in seed 1. The offense often chooses a throw before a carrying score is available. DECISION. | **BEHAVIORAL**. Trial a goal-mouth carry option scored against the shot with identical initial conditions. |
| Carry scoring 2 | 683 carries ended at a boundary. Boundaries can terminate runs even at small perpendicular goal-plane distances. RULES set the legal mouth and DECISION chooses the approach. | **BEHAVIORAL**. Compare goal-mouth routes to straight goal-plane progress without changing the mouth. |
| Carry scoring 3 | There were 0 stretch starts across 3246 carries; seed 1 had 0. The carrier menu admits stretch only when no shot option exists. DECISION with EXECUTION limits. | **BEHAVIORAL**. Log feasible stretch windows explicitly and test choosing a viable stretch within existing reach and safety limits. |
| Tackle success 1 | 7967 commits started without confirmed actual carrier identity, including 7002 no-contact episodes. PERCEPTION and DECISION. | **BEHAVIORAL**. Compare a commitment check using fresher visible possession evidence and an alternative pursuit action when uncertain. |
| Tackle success 2 | 3299 contact episodes lacked confirmed threshold grip. Grip mechanics and entry angle are EXECUTION hypotheses. | **BEHAVIORAL**. Run matched grip tests by closing angle, reach and tackling rating before adjusting hold acquisition. |
| Tackle success 3 | 4093 episodes ended with a known grip and no witnessed resolution, and 1073 had confirmed grip loss. Commitment continuity and break force are DECISION and EXECUTION hypotheses. | **BEHAVIORAL**. Test maintaining a legal takedown selection through an existing grip while instrumenting separate release and grip-break causes. |

## Evidence

- [Named planned seed-1 box score JSON](rb331/evidence/boxes/planned-seed01.json) and [CSV](rb331/evidence/boxes/planned-seed01.csv)
- [Archived match before/after](rb331/evidence/box-before-after.json), [soak and diagnosis aggregates](rb331/evidence/diagnosis.json) and [per-match witnesses](rb331/evidence/runs)
- [Test output](rb331/evidence/pytest.txt), [legacy hashes](rb331/evidence/legacy.txt) and [benchmark](rb331/evidence/benchmark.json)
