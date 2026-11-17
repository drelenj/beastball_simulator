# HP-002: independent V6 review of native-v0/3 (claude/native-v0-3-handoff-69stxd @ 3fa2aea)
Claude (cognition/PRISM lead; did not write FAB-1, which was a separate session), 17 Nov 2026. Status: REVIEW COMPLETE. v0/3 is IMPLEMENTED and TESTED by the author's account and by my reruns; nothing is ACCEPTED. This closes acceptance item V6 (the earlier reviewer agent stopped on a usage limit and returned nothing).

Verified by running: full suite 255 passed (23 subtests); native-v0/2 seed 1 full match replays the Native PRISM 0 hashes exactly (trace 3840682e, state 411abb0a, digest f31b44a1, score 58-77), so every v0/3 change is gated; read of the port, rules, config and restart-metric diffs against a1b1313; cognition_v3.py (275 lines) imports only dataclasses, math and cognition and has an AST purity test plus two poison tests; per-seed soak JSON read directly (10 of 10 final, summary matches). Not verified: I did not re-run the 10 soak seeds, the B0 blob count, parallel replay, or read every test body.

## Findings
| ID | Sev | Finding | Fix |
| --- | --- | --- | --- |
| R-1 | Medium (plausible, not reproduced) | `p.native_intent` is assigned on every accepted intent and never cleared. Hold authorisation (`native_wrap_authorized`, `c3_contain`) and carrier escape effort read it, so a takedown or run-through intent outlives its situation until that athlete's next accepted decision. The cadence bounds this to about 500 ms for athletes who decide every tick, but athletes with no view (grounded, frozen, inactive) keep the old intent indefinitely. No test targets it. | Clear or expire native_intent on dead ball, grounding, freeze and after one decision interval; add a test. |
| R-2 | Medium (integration) | v0/3 is a separate line from RB-2.1: 25 arrows per match (canon 15 per possession), no own goal (author discloses), carry attempt defined independently of RB-2.1's definition. RB-2.1 lacks v0/3's contact and restarts. Same finding as ATTR-1 A-1. | Merge the lines (RB-2.1 rules + v0/3 cognition + ATTR mapping) and keep one carry-attempt definition. |
| R-3 | Low | Carry-attempt placeholder: key is (carrier, control_time) within 20 m; 575 attempts and 0 carry goals in 10 matches. Fine as a counter, but it counts every new control, so fumble recoveries inflate it. Disclosed as PLACEHOLDER. | Align with the RB-2.1 definition when merging. |
| R-4 | Low | Banded branch keeps an unreachable `distance is None` fallback of 2 points, and non-shot releases that score are paid by distance band but not counted as shot attempts (disclosed; consistent with RB-2.1). | None required; remove the dead branch. |
| R-5 | Low | The Archer no longer releases during a pass in flight (Q-FAB1-2) is outside the three named FAB-1 items. It is disclosed and tested. | Keep disclosed; owner may confirm. |

## Verdicts (the author's eight questions)
1. Gating of every hunk: PASS (v0/2 replay identical; changes behind is_v3 or the scoring field).
2. Own-body view fields: PASS (own_held, own_balance_load, own_hold_target are the athlete's own body only).
3. Engine contact hooks and stale intents: PASS WITH FINDINGS (R-1).
4. cognition_v3 correctness and information boundary: PASS (pure, AST-tested; I did not review every constant; all decision constants are PRIMITIVE and unsearched, as disclosed).
5. Restart "eligible" denominator: PASS. Raw and eligible rates are both reported; raw timeout mean about 1.2% over 10 seeds (v0/2: 25.6% in seed 1).
6. Remaining arrow literals: PASS (v0/2 literal 29 kept only for the frozen profile; v0/3 uses config speed).
7. Test strength: PASS WITH FINDINGS (R-1 untested; poison and purity tests are meaningful).
8. Honesty of status and questions files: PASS.

## What the soak data say (measurement, not quality)
From the 10 committed seeds: groundings mean 70.6 per match (v0/2 seed 1: 6); tackle-count events 69.1; restart timeouts about 1.2%; arrows released about 177 and archery_target fouls 13.5 per match; fouls 23 per match; match points total mean 58.1, which is about 29 per team against the 80-85 target; possession events about 151 per match, roughly 75 per team against about 100. These come from placeholder behaviour and a different arrow accounting from RB-1, so they are not comparable with RB-1 figures.

## Verdict
Conformance PASS WITH FINDINGS. FAB-1a, 1b and 1c work as claimed. Recommend accepting v0/3 as the contact and restart cognition source for the merged line, after R-1 is fixed.
