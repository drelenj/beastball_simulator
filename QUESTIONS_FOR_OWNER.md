Scope notice: original sections describe historical Native v0/2. The Rulebook1.0 section below applies only to native-rb/1 and records its current blocker and limits.

OWNER BRIEFING
1. Native build uses the following smallest working PLACEHOLDERs where implementation or canon detail is incomplete.
2. These are explicit defaults, not accepted canon or evidence of good play.
3. Historical Native v0/2 questions did not block that baseline. The RB section records resolved canon updates and remaining placeholders. Acceptance remains the owner's decision.

| ID | Question / replaceable default | Class and current handling |
|---|---|---|
| Q-HUNT-1 | Centre-circle radius and setup distances are not specified numerically in the build prompt. | CANON detail; PLACEHOLDER keep restarts_v1's 5 m radius, contestants approach physically from legal initial scatter. No assigned formation or role-ranked contestant. |
| Q-HUNT-2 | Exact clock activation within the First Hunt is not specified in the authoritative prompt. | CANON detail; PLACEHOLDER clock runs in the opening phase, including approaches; false start retakes and no Archer until whole ball exits circle. |
| Q-ZONE-1 | Unmarked defenders cannot remain indefinitely, but the permitted grace interval is not stated. | CANON detail; PLACEHOLDER 5 s unmarked residence, inherited duration; marked defenders exempt, Keepers exempt. |
| Q-FLIGHT-1 | Maximum shot finishing-flight duration is not stated. | CANON detail; PLACEHOLDER 10 s safety tail, normally ends on ground/control/out/goal. Only shots get an exception. |
| Q-BOUNDARY-1 | Exact anatomical witnesses for every touching body part need more motor integration. | ENGINEERING; PLACEHOLDER ground body-cylinder envelope with airborne exemption. Native v1 replaces it with support/anatomical witnesses. Goal whole-ball test is separate. |
| Q-COVER-1 | If simultaneous exclusions temporarily leave fewer than 12 eligible among 22, does "available" include excluded athletes? | CANON edge case; PLACEHOLDER excluded athletes are unavailable until their exclusion expires, so fewer than 12 currently eligible causes a forfeit. No unavailable athlete is fielded to hide this case. |
| Q-SIMULT-1 | Simultaneous offsetting minor fouls outside the three specified exact ties have no explicit procedure. | CANON detail; PLACEHOLDER retain B0 neutral offset: record each sanction and restart with existing possession/count, no automatic major classification. |
| Q-HELD-1 | Unresolved physical joint-ball control has no resolution duration in the prompt. | CANON detail; PLACEHOLDER retain B0 one-second held-ball reset/alternating scrimmage; Hunt joint control retakes without a penalty. |
| Q-SENSOR-1 | Native sensor cadence/noise constants are not canon. | ENGINEERING; PLACEHOLDER immutable delayed/noisy cone/occlusion observations with independent per-athlete RNG, no true fallback. Claude replaces/takes ownership. |
| Q-THROW-1 | Full THROW_SPLIT mechanics and arbitrary-speed error calibration are not yet ported. | ENGINEERING; PLACEHOLDER explicit intent speed/height, drag-aware arc, 60-degree moving-release bound, uniform accuracy error. Do not claim full throwing_v1 equivalence. |
| Q-HAND-1 | Full voluntary off-ball hand-fight repertoire is not yet ported. | BEHAVIORAL/ENGINEERING; PLACEHOLDER retained incidental contact physics, intent-gated carrier wraps, no automatic random gripping. Native v1 adds PRISM-owned off-ball actions. |
| Q-CONTACT-1 | B0 automatic containment/descent choices used true-state tactical triggers. | ENGINEERING; disabled in Native. Motor may retain already admitted Keeper commitments; new semantic choices come from decide(). |
| Q-CATCH-1 | CATCH_V2 shared energy kernel is ported; automatic jump/hand-contest overlay is not installed. | ENGINEERING; PLACEHOLDER B0 simultaneous secure-contact handling plus shared threshold kernel. No second Keeper decider. |
| Q-BEHAVIOR-1 | Minimal Hunt claims, restart claims/alignment/wait/snap, dribble and cover policies need replacement. | BEHAVIORAL; PLACEHOLDER procedural decisions in the same view/belief/intent pipeline, canonical admission, no quality claim. Claude owns their later cognition replacements. |

Explicit DEFERRED: breaks, timeouts, Hunt penalties beyond false-start retake, standard scoring, fatigue, injury, rating development, adaptive learning, M2 plan/message content. No implementation of those deferred features is authorized by this baseline.

PH3 implementation limit (ENGINEERING, not a canon escalation): the current defender-marking exemption checks offensive field players. Keeper-as-marker coverage is not established by the conformance test. Native v1 must cover every offensive-player role permitted by the rule. This residence model remains PLACEHOLDER; the five-second attacker rule and field-player marking case are tested.

## Rulebook 1.0 / native-rb/1 scope (supersedes old defaults only for RB)

Breaks, timeout policy,>5cm review, shorthanded discipline, quotas and forced-injury/substitution mechanics are ratified for RB. They are not deferred in RB. Native v0/2 remains the historical profile above.

| ID | Class | Handling |
|---|---|---|
| RB-PH-1 | ENGINEERING placeholder | Period resets reuse initial legal scatter; no new formation. Added field-roster admission is procedural setup. Twelve non-Archer field-roster slots; the Archer is outside that limit;22 gameday players retained. |
| RB-PH-2 | Team setup placeholder | Reserve Keepers default to A13/B13. Eligible replacements use canonical ID order with named-reserve priority; fallback chooses an available field player. No ratings used. |
| RB-PH-3 | Equipment placeholder explicitly permitted | Torso/thigh cylinder-height band approximates strike panels. Outer/inner thigh cannot be distinguished. Lighter Archer kit is metadata only; no gameplay effect. |
| RB-PH-4 | Missing procedure detail | Fifth-minor DQ uses a60s replacement window; second-major DQ120s. These follow the respective foul-kind exclusion window. |
| RB-PH-5 | Missing procedure detail | A special defensive count+1 offence reuses the existing count1-to-turnover transition on overflow. No new tackle-count domain is invented. |
| RB-PH-6 | Missing review detail | A lost review with no timeout remaining consumes its challenge but does not create a negative timeout balance or future-half debt. |
| RB-PH-8 | Missing restart detail | Correcting a false goal while the recorded ball was still in bounds resumes by scrimmage for the recorded possessing team at the spot; a recorded out-of-bounds ball uses the corrected boundary restart. |
| RB-PH-9 | ENGINEERING ordering | Eligible simultaneous timeout triggers are consumed once each, team order A then B. No extra timeout is granted. |
| RB-PH-10 | Forced injury scope | No injury probability or recovery model is added. Ordinary forced injuries remain unavailable; head-evaluation players can return from the next period. |


RB-PH-11: inherited procedural illegal_release/otherwise unclassified legacy rule inputs currently default to minor adjudication. This is a labelled compatibility placeholder, not a newly ratified offence.
RB-PH-12: later sudden-death periods retain the inherited300s maximum period duration; any score ends them immediately. Their duration beyond the first overtime was not restated numerically in RB-1.

2026-11-15 owner update: RB-BLOCK-1 RESOLVED. Pre-live5m marking foul and its witness are REVOKED and removed with no replacement. Keeper-zone defender marking remains5m. Snap-readiness ordering remains. Repeated dead-ball foul retakes receive a procedural correction/warning without repeated stopped-clock discipline.

RB-PH-7 RESOLVED: recorded-evidence review now operates during period breaks and after final rulings; reversal restores prior state, and a lost halftime review charges the old half. No autonomous challenge policy is defined or invented.

No current canon question blocks RB integration. Remaining RB-PH defaults above are explicit implementation placeholders, not ratified additions.

RB-PH-13 RESOLVED by RB-2 engineering correction: release-distance attempt counters are shot-only. Carry attempts are counted independently, own goals are reported separately, and the complete pass/bounce/restart release ledger remains available without being described as shot attempts.

RB-PH-13 measurement definition completed by RB-2.1: one carry attempt is the first controlled entry of a field carrier's body centre strictly inside the20m Keeper/scoring zone around the attacked goal, once per secure control. The arc is outside; a scored carry not previously observed inside is counted at the goal event. This is an ENGINEERING measurement definition, not a new gameplay rule.

2026-11-16 SCORING BASIS owner ruling: banded scoring is the working canon and the only basis permitted for current measurements. `native-rb/2` uses carry5; throw bands2/3/4; half goal1; full-goal award3; own goal2. Values remain provisional until the self-play experiment reports. Historical flat artifacts are retained only as history and are not measurement evidence.

## Native-RB/3 roster exception, 2026-11-17

Q-RB3-1 RESOLVED by owner workbook `81f92e3`: Zuberi Ibe is listed as a KPR for Güunlekia Serpents, which now has two eligible designated Keepers. All 26 franchises satisfy the 2 KPR, 2 ARC, 18 field selection shape.

Q-FAB1-2 is resolved for native-rb/3: RB-2.1 retains team control during qualifying flight; the Archer's pass-in-flight predicate is restored for this profile. Historical native-v0/3 behavior remains versioned separately.

RB3-ATTR PLACEHOLDERS: eight technical ratings (tackling, blocking, ball_handling, catching, awareness, throw_accuracy, keeper_skill, archery_accuracy) use Opening-day OVR / 100; contact_resistance uses Balance / 100. These values are flagged placeholders until a shared derived-ratings specification replaces them. Touch and the other 17 newly carried ratings remain INERT, default to 0.70 when absent, and are never put into an athlete view.
## native-v0/3 (FAB-1, Claude, 2026-11-15)
These apply to config `native-v0/3` only. None blocks engineering; each has the smallest working default in place.

| ID | Question / replaceable default | Class and current handling |
|---|---|---|
| Q-FAB1-1 | Canon gives arrow speed as 250 m/s and as "about 5.6 times a 100 mph (44.7 m/s) top speed". The engine's fastest player runs 27 m/s, so the two readings differ: 250 m/s (ratio 9.26) or 151 m/s (ratio 5.59). Which is the invariant? | CANON; PLACEHOLDER 250 m/s as confirmed (`arrow_speed_ratio = 250/27`). One number changes it: `--arrow-speed-ratio 5.59`. |
| Q-FAB1-2 | Does a team keep "team control" while its pass is in flight? The rules layer as built says no, so an arrow released at an opposing field player during a pass is an `archery_target` minor (and a half goal at tackle count 0). Under native-v0/2 this produced 64 such fouls and 62 foul awards in seed 1. | CANON, rules layer is Codex's; PLACEHOLDER the v0/3 Archer does not choose a release during a pass in flight. If canon keeps team control in flight, the rules check widens and this Archer predicate is reverted. |
| Q-FAB1-3 | A defender may hold a carrier up (wrap) or bring him down (takedown); a carrier may run through, brace or dodge. The values that choose between them are unsearched (commit to a takedown inside a believed 6 m gap; brace above 0.7 balance load; dodge with 0.3 s or more of warning). | BEHAVIORAL; PRIMITIVE functional defaults, no quality claim. Brace has no physical benefit in the present engine beyond not prying at the grip (engine fidelity is Codex's). |
| Q-FAB1-4 | Restart claims: the believed-nearest teammate claims, and each athlete delays his own claim by 25 ms per metre from the spot. Two nearest teammates stand 8 m from the spot so a legal throw exists. With no believed target the taker throws to legal space only in the last 1.5 s. | BEHAVIORAL; PRIMITIVE / PLACEHOLDER defaults replacing Q-BEHAVIOR-1 for restarts under v0/3. Hunt claims, dribble and cover policies stay as in v0/2. |
| Q-FAB1-5 | A toss timeout on the goal line is followed by a scrimmage placed 0.5 m from the goal line, leaving the defence half a metre of legal ground. | CANON / rules detail for Codex (RB-1): where does a turnover scrimmage go when the spot is on or near a goal line? Unchanged here; v0/3 athletes stand in the half metre. |
## ATTR-1 / attr-map/1

ATTR-1 implements the owner-ratified proportional speed curve and records the following replaceable engineering choices. None blocks implementation.

| ID | Class | Current handling |
|---|---|---|
| Q-ATTR-1 | PLACEHOLDER input aliasing | `name`, `position`, `archetype`, and `overall` are accepted only as ignored columns. They never supply ID, role, ratings, or digest content. Known generator metadata is also ignored. |
| Q-ATTR-2 | PLACEHOLDER body envelope | Height 2.40–2.95 m and mass 155–285 kg generate warning counts only. Engine height 1.4–3.6576 m and positive mass are enforced. |
| Q-ATTR-3 | Owner-kept acceleration effect | Mapped acceleration means a roughly 40 m/s athlete needs about four seconds and 80 m to approach top speed. No tuning was made. |
| Q-ATTR-4 | PLACEHOLDER uniform throw error | Requested angular SD is converted to a uniform half-width of `sqrt(3) * SD`; this preserves the specified standard deviation. |
| Q-ATTR-5 | Existing generator compatibility | Current generated CSVs lack required `id`; some express ratings as 0–100 and one uses `role` for lineup status. ATTR rejects them explicitly. A generator/export adapter must emit canonical `id`, fixed role and 0–1 ratings; it may retain labels because the loader ignores them. |
| Q-ATTR-6 | Inert ratings | Stamina is inert while fatigue is off. Keeper skill and Archer accuracy are stored but inert in the active Native path: shared catching uses catching, and athlete-owned Archer execution is exact ballistic release. Sensitivity evidence reports them as INERT. |

## RB-3.3 provisional (claude/rb-3-3-archer-flip, 17 Nov 2026)
| ID | Question / replaceable default | Class and current handling |
|---|---|---|
| Q-RB33-1 | After the first overtime period (decided by a second coin flip), who starts later overtime periods? | CANON; PLACEHOLDER: the starting team alternates each later overtime period. |
| Q-RB33-2 | Most remaining illegal arrows (14 of 19 in a 600 s seed-1 window) are released while the target team's pass is in flight; the rules layer gives no team control then, so each is an archery_target minor and, at tackle count 0, a foul award. Every DQ'd Archer reaches 5 minors this way. | CANON (same as Q-FAB1-2): does a team keep team control while its pass is in flight? Archer cognition left unchanged as instructed. |
| Q-RB33-3 | Q-HELD-1 for period starts is resolved by the coin-flip snap40. Q-HELD-1 for unresolved joint control in open play is unchanged. | Resolved for period starts only. |
| Q-RB33-4 | Restart timeouts rise sharply once a team has about 20 DQs (seed 1: 13, 22, 184, 376 per period). | ENGINEERING/BEHAVIORAL follow-up; cause not isolated. Matches still finish. |
