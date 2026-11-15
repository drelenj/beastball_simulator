# TACTICS-0: personnel profiles (amended D2)
Claude (Fable), 2026-11-15. Status: **DESIGN COMPLETE**. Not IMPLEMENTED, not TESTED, not ACCEPTED. Generated from `audit/tactics/tools/tactics_src.py` by `build.py`.

## OWNER BRIEFING
1. **Accomplished.** For each of the eight styles, every slot now states the rating bands it needs, how candidates are ranked, and what happens when a weaker player fills it: a graceful degrade or a failure. A general rule assigns any supplied roster to any style by rating band.
2. **What the simulator can do now.** Nothing with this. Native v0/3 gives every athlete the same body and rating, so a slot's bands change nothing yet.
3. **Unimplemented or unproven.** Every band is a reasoned first value against a PLACEHOLDER envelope. "Failure" and "graceful" are predictions about play, not observations. The staffing figures are arithmetic on the bands, not results.
4. **Blocking.** The attribute step (`ATTRIBUTE_STEP_SPEC.md`). Until ratings reach the engine no profile can be tested.
5. **Recommended action.** None for the owner beyond the envelope itself: confirm or replace the usual ranges when you are ready to make them canon.

## 1. Scope
- By the owner amendment of 14 Nov 2026 22:42 this file replaces roster fit. The Ala and Xenar rosters were not read. There are no named players, no roster fit scores and no "best styles for a team".
- **Design envelope (PLACEHOLDER, not canon):** ratings 0 to 1, typical professionals 0.60 to 1.00 on every rating; heights about 2.40 to 2.95 m; masses about 155 to 285 kg. Canon: a speed rating of 1.0 is 44.704 m/s. All bands below are written against this envelope.
- **Bands.** ELITE 0.90 or more; KEY 0.85 or more; SUPPORT 0.75 to 0.80; BASE 0.70. A slot has one KEY rating, or two where the method needs both in one body. Body gates sit near the middle of the range.
- **Failure or graceful.** A slot is marked FAILURE when the style's method stops existing without it: the number given is how many in-band players the slot needs for the method to exist at all (usually a pair, or one). Every other shortfall is graceful: the style still runs and does that job less well, roughly in proportion to the shortfall.
- **Keeper and Archer** are fixed roles by canon and are filled only from the roster's Keepers and Archers.

## 2. Assignment rule: assign by rating band from a supplied roster
Input: any roster table with an id, a role (field, keeper, archer), the ratings on a 0 to 1 scale, height and mass. The rule is the same for every style and every roster.

1. Keeper and Archer slots take the highest-scoring athlete of that role.
2. Field slot instances are taken in the style's slot order, which is its priority order.
3. An athlete is **in band** for a slot if he meets every minimum.
4. In-band placement is a maximum matching between instances and in-band athletes, so no in-band placement is lost to an earlier choice. Candidates are tried in descending slot score; ties go to roster order.
5. Slot score is the weighted sum in the "Ranked by" column, with height and mass rescaled onto the 0.60 to 1.00 band.
6. An instance still empty takes the highest-scoring unassigned field athlete and is flagged **under band**, with each shortfall listed.
7. Status: **BROKEN** if any FAILURE slot has fewer in-band players than it needs; **FULL** if every instance is in band; otherwise **DEGRADED**.
8. The rest are the bench. A substitute takes the slot of the athlete he replaces.

Reference implementation: `audit/tactics/tools/roster_tools.py`, function `assign`. It is deterministic. It reports the shortfalls; it produces no fit score.

## 3. Profiles by style

{{PROFILES}}

## 4. Which style is most tolerant of an average roster
Two pieces of arithmetic, then a judgement.

**Arithmetic.** {{N_STAFF}} rosters were drawn from the seeded generator of the test plan (18 field athletes, 2 Keepers, 2 Archers; every rating independent and uniform on 0.60 to 1.00; height and mass uniform on the envelope) and assigned to each style. "All-average roster" is a roster where every rating is exactly 0.80 and every body is mid-range.

{{STAFFING}}

What the arithmetic shows:
- **No style is fully in band on the all-average roster.** Each has at least one slot gated at 0.85 or more, and an all-0.80 roster meets none of those. Every style as written needs above-average players in its defining job.
- By the share of random rosters that do not break, the order is the order of the table. {{TOP_ARITH}} breaks least often.
- The styles that break most often are those that need two heavy, strong specialists (Carry Train, Zone Lock) or that hang on one of only two Archers (Archer's Anvil).
- These rates come from a generator in which ratings are independent. Real rosters have correlated ratings (a strong player is often heavy), which would raise the rates for the power styles. The rates describe the bands under that generator and nothing else.

**Judgement (a hypothesis, to be tested in stage 3 of the test plan).** I expect **Long Count** to be the most tolerant of an average roster, although it is not first in the table:
- It has one FAILURE slot, and on the all-average roster that slot is short by 0.05 on a single rating (ball handling 0.80 against 0.85), with the other two bands met.
- Its method is low-risk by construction: short passes into open lanes, no contact sought, three players behind the ball. A handler slightly under band loses a few more passes; nothing collapses in one play.
- It has the highest share of rosters fully in band and the most field slots in band on average.
- {{TOP_ARITH}} breaks less often by count, but its method is the least forgiving of a slow player when it is staffed thin: one late exit from the zone is a turnover, not a slightly worse possession.

Least tolerant, by the same reasoning: **Archer's Anvil** (one athlete carries the method and a roster has two candidates) and **Zone Lock** (the door needs two players who are strong, heavy and sound tacklers at once, and a broken wrap is a free run at goal).

## 5. Limits
- Bands are first values. Whether 0.85 is the right gate for any job depends on how the attribute step maps ratings to bodies and skills, and all of that except speed is PLACEHOLDER.
- FAILURE and graceful are predictions. Stage 3 of the test plan weakens one slot at a time to check them.
- Stamina is gated for one slot (HOUND) but cannot matter in Native v0/3, where fatigue is off.
- Keeper bodies use the same envelope as everyone else. Older project notes give Keepers a larger body range; that is an open question (Q-TAC-5).
