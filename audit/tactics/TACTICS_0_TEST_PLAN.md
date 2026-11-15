# TACTICS-0: test plan (not run)
Claude (Fable), 2026-11-15. Branch `claude/tactics-0`.
Status: **DESIGN COMPLETE**. Nothing in this plan has been run. Not IMPLEMENTED, not TESTED, not ACCEPTED.

## OWNER BRIEFING
1. **Accomplished.** A plan for testing the eight styles once the attribute step and the playbook exist: a check that each style is actually being played, a round-robin of all 28 pairings plus 8 self-pairings, a confirmation stage on fresh seeds, and a personnel stage that weakens one slot at a time. Rosters are drawn at random from the usual ranges by a seeded generator and are the same for both teams.
2. **What the simulator can do now.** It cannot run this plan. Native v0/3 has no ratings per athlete and no slots.
3. **Unimplemented or unproven.** The whole plan, several of its metrics (the first and second tackle split is not recorded today), and its cost: about 2,900 full matches if every stage runs in full.
4. **Blocking.** The attribute step (Codex), the playbook interface (Codex and Claude), and the instrumentation in section 5.
5. **Recommended action.** None now. When the two builds pass their tests, approve stage 0 first; it costs 16 short windows and decides whether the rest is worth running.

## 1. Gates before anything runs
| Gate | Condition |
| --- | --- |
| G-1 | Attribute step built; tests AT-1 to AT-16 pass (`ATTRIBUTE_STEP_SPEC.md`) |
| G-2 | Playbook stages P1 and P2 built; tests IB-1 to IB-14 pass (`TACTIC_INTERFACE.md`) |
| G-3 | Every parameter tagged NEEDS ENGINE WORK is either built or listed as **inactive** for the run. A style run with inactive parameters is reported as "reduced form", by name |
| G-4 | The metrics of section 5 are recorded by the harness |
| G-5 | `tactics_0.json` is frozen: its SHA-256 is recorded and no value changes between stages |

Reduced form matters most for Carry Train (lead blocking), First Strike and Arc Siege (release speed and long passes), and Zone Lock and Carry Train (tackle count in the view).

## 2. Rosters
By the owner amendment of 14 Nov 2026 22:42 the test uses randomly drawn rosters from the usual ranges, not Ala and Xenar.

- **Generator.** `audit/tactics/tools/roster_tools.py`, `generate(seed)`, version `tactics0-roster-gen/1`. 22 athletes: 18 field, 2 Keepers, 2 Archers. Every rating independent and uniform on 0.60 to 1.00; height uniform on 2.40 to 2.95 m; mass uniform on 155 to 285 kg. All PLACEHOLDER (the envelope is not canon).
- **Same for both teams.** In every match both teams field the **same generated roster**. Each team assigns it to its own style by the rating-band rule. The only difference between the teams is the style, so no result can come from one side having better players.
- **Check values.** First 16 hex digits of the SHA-256 of the roster as compact sorted JSON: seed 1001 `a1b7239693dc5d21`, 1002 `677f7422bdc7cfb0`, 1003 `fa11a670f9c704d5`, 1004 `86a1e9b788504b2b`, 2001 `9dbadb35588fbfff`.
- **Random rosters often break a style.** On seeds 1001 to 1004 each style is BROKEN on between zero and four of the four rosters. That is intended for stage 1: it tests styles on rosters nobody chose for them. Every result is reported with the staffing status of both teams. Stage 3 tests staffed rosters separately.
- Independent ratings are unrealistic. A second generator with correlated ratings is a possible later stage, not part of this plan.

## 3. Stages
A full match is 4 x 600 s and took 85 to 90 s to compute on Native v0/3. Cost after the attribute step is unknown.

| Stage | Purpose | Design | Matches |
| --- | --- | --- | --- |
| 0 | Is each style being played at all | Each style against the neutral plan, 2 rosters (1001, 1002), 1 match seed, **600 s window** | 16 short windows |
| 1 | Round-robin | 28 pairings and 8 self-pairings; 12 rosters (1001 to 1012) x 1 match seed x both sides | 36 x 24 = 864 |
| 2 | Confirmation on rosters not seen before, with both styles staffed | Every pairing with a prediction, and every other pairing whose stage 1 interval excludes zero; for each pairing the first 24 generated rosters from seed 2001 up on which neither style is BROKEN, 1 match seed x both sides | up to 28 x 48 = 1,344 |
| 3 | Personnel profiles | Each style against the neutral plan under about 5 roster conditions; 3 rosters x 3 match seeds x both sides | about 8 x 5 x 18 = 720 |

**Stage 0** reads only the signature marks of section 4. A style whose marks are absent is fixed or withdrawn before stage 1; its outcome is not read.

**Stage 1 seed count:** 12 rosters per pairing, one match seed each, each played from both sides. Rosters, not match seeds, are the independent unit, so the budget goes to rosters. The 8 self-pairings (a style against itself) have a true difference of zero; the standard deviation of their block values is the noise floor.

**Stage 1 mostly tests understaffed styles.** Under this generator Carry Train, Zone Lock and Archer's Anvil are BROKEN on most random rosters, and the 19 predictions were reasoned for staffed styles. Stage 1 therefore answers "what happens on rosters nobody chose", and its results are split by staffing status. The predictions are scored on stage 2, where both styles are staffed.

**Stage 3 conditions** for each style, both teams always holding the same roster and the opponent playing the neutral plan:
- *Staffed:* the first generated rosters (seeds from 30001 up) on which the style's status is FULL.
- *One failure slot weakened:* the staffed roster with the gated ratings of the players in one FAILURE slot set to 0.70. One condition per FAILURE slot.
- *One graceful slot weakened:* the same for the style's largest graceful slot.
- *All-average:* every rating 0.80, every body mid-range.

## 4. Is the style being played (stage 0 and every later stage)
Each style lists signature marks in `tactics_0.json` (`signature`), for example: Arc Siege releases 60% or more of its attempts from 20 m or more; Zone Waves keeps 2 to 3 attackers in the zone with a 95th-percentile visit of 4.0 s or less; Long Count's possessions last 20 s or more. These thresholds are intentions written before any run. If stage 0 shows a threshold was simply set wrong, it is changed once, before stage 1, and the change is recorded.

## 5. Metrics
Per team, per match, from the event log.

| Group | Metrics |
| --- | --- |
| Result | Points under the flat scoring in force; the same events rescored on the provisional scale; margin; winner; overtime |
| Goals | By method (carry, throw) and release-distance band (under 10 m, 10 to 20 m, 20 m or more): attempts, goals, success rate. Half-goal and full-goal awards. Own goals |
| Possession | Number of possessions; duration (mean, median); share of live time; time to first attempt; play-clock expiries; share of attempts with 8 s or less left |
| Ball movement | Passes attempted and completed by length (under 10, 10 to 20, 20 to 34, 34 m or more); share of advance by carry; dribbles; drops, interceptions, strips |
| Tackles | First tackles and second tackles, with distance from the attacked goal; wraps and takedowns chosen; hold-up durations; grips broken; share made in the opponent's half |
| Keeper Zone | Attacker entries; visit length (median, 95th percentile); attackers inside over time; residence turnovers; unmarked-defender fouls; attempts released inside |
| Archer | Arrows and freezes per opposing possession; freezes on the ball holder; balls dropped on a freeze and who recovered them; illegal-target fouls; possessions that hit the 15 or 5 limit; arrows in the first 8 s |
| Restarts | Awarded, released and timed out, by kind (tackle scrimmage, 40 m scrimmage, toss-in); what happened within 8 s of release; Hunt wins |
| Turnovers | By cause: second tackle, play clock, zone residence, interception, loose ball (after a freeze, other), boundary, foul, own-zone violation |
| Fouls | Minor and major by reason; exclusions |
| Coordination | Mean distance from own anchor; double claims; for rotations, time with both partners in or both out; share of decisions whose source is the plan |
| Run health | Invariants, crashes, stalls, runtime |

Not recorded today and needed: first and second tackle split; turnover cause; release distance per attempt; visit length per zone entry; decision source.

## 6. Reading the results
**Unit.** One block is one roster, played from both sides; its value for a pairing X against Y is X's mean margin over the two matches. **Margin is the one primary outcome.** Report its mean over blocks with a 95% interval from a bootstrap over rosters (12 in stage 1, 24 in stage 2) and the win share. With 12 rosters the stage 1 interval is rough and is used only to choose what goes to stage 2. Every other metric of section 5 is descriptive: reported, never tested, because testing dozens of metrics per pairing would produce signals by chance.

**Rules.**
1. **Played before scored.** No outcome is read for a style whose signature marks are absent in that stage.
2. **A difference counts only if** its stage 2 interval excludes zero, with the same sign as stage 1, and its mean is larger than twice the standard deviation of the self-pairing block values divided by the square root of the number of blocks. With 28 pairings some stage 1 signals will be chance; stage 2 on fresh rosters is there to catch them.
3. **Say what was measured.** The sentence form is: "X outscored Y by d (interval) points per match on these rosters and seeds, under mapping `attr-map/1`, flat scoring, and this playbook weight." Every figure carries those conditions.
4. **Words not used:** optimal, balanced, best, dominant, proven, emergent. Nothing in this plan can establish any of them. The values in `tactics_0.json` were never searched, so a result is about these values, not about the idea behind the style.
5. **A loss has three possible causes** that this test cannot separate: the style was poorly expressed by the cognition, its numbers are poorly chosen, or the method is weak. Say so each time.
6. **Predictions scorecard.** On stage 2 (both styles staffed), of the 19 predicted pairings, count those that agree, disagree, and cannot be told apart from zero. It grades the reasoning in `TACTICS_0.md`, not the styles.
7. **Both scorings.** A result that changes sign between flat and provisional scoring is reported as depending on the scoring.
8. **Rosters.** Report each pairing by roster as well. If the sign differs between rosters, the finding is "depends on the roster". Report staffing status beside every result.
9. **Personnel (stage 3).** A FAILURE label is supported if weakening that slot removes the signature marks or costs clearly more margin than weakening a graceful slot. The tolerance judgement (Long Count) is supported if its all-average margin falls least from its staffed margin. Either can be refuted.
10. **Stop a stage** if more than 2% of matches crash or stall, or if restart timeouts exceed 10%; fix and restart the stage from its first seed.

## 7. What this plan cannot show
- That any style is the right way to play, or that the eight are evenly matched.
- How a style would do with searched parameters, with human-like coordination, or under different placeholders for ratings.
- Anything about Ala or Xenar.
