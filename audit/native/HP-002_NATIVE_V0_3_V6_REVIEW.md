# HP-002: V6 independent review of native-v0/3 (claude/native-v0-3-handoff-69stxd @ 3fa2aea)
Claude (reviewer; did not author FAB-1), 16 Nov 2026. Status: V6 COMPLETE. v0/3 is IMPLEMENTED and TESTED; nothing is ACCEPTED.
Verified by running: full suite 255 passed (23 subtests); native-v0/2 seed 1 full match replays exactly (trace 3840682e..., state 411abb0a..., digest f31b44a1...), so v0/3 is gated off v0/2; native-v0/3 seed 1 full match reproduces the committed banded ten-seed row (trace b8b7bdb1..., state dff1f9ae..., digest 791cea68..., score 37-39, 82 groundings, invariants passed). Read: the diff of rules.py, port.py, cognition.py, config.py scoring hunks and cognition_v3.py contact and restart decisions. Not verified: the other nine seeds, serial-vs-parallel and null-vs-absent M2 on v0/3, the full poison-test strength.

## Findings
| ID | Sev | Finding | Fix |
| --- | --- | --- | --- |
| R-1 | Medium | V7 manifest is stale. NATIVE_V0_3_MANIFEST.json holds the flat-basis config digest 2e906666... and fixed-seed hashes from c521c49 (seed 1: cacf2405.../d688fcbb...). Current HEAD is banded (digest 791cea68...), seed 1 is b8b7bdb1.../dff1f9ae.... The ten-seed table is current; the manifest is not. | Regenerate the manifest at HEAD. |
| R-2 | Medium (integration) | v0/3 sits on the v0/2 rules layer: no team control during a pass in flight, no own goal, 25 arrows per match, none of RB-2.1. The v0/3 Archer rule "no release while a pass is in flight" (Q-FAB1-2) is a workaround for that gap and must be removed when merged with RB-2.1, where team control in flight is implemented. | Merge plan in the ATTR-2 request; restore the Archer's pass-in-flight predicate under RB-2.1. |
| R-3 | Medium (BEHAVIORAL) | Carries never score: 575 carry attempts, 0 goals, 0 points in 10 matches. The canon 5-point carry is dead in play, so the banded scale is effectively throws + half goals + awards. | Behavioral item for the cognition lead: a carrier deciding to run the ball into the goal. Report as a measured gap, not a tuning request. |
| R-4 | Low | Contact and takedown intents persist until the athlete's next decision (500 ms), so a takedown can outlive the situation. Bounded by the engine's physics and by the target-match check in the hold authorisation; not probed. | Add a stale-intent test (intent expires on target change or after one decision interval). |
| R-5 | Low | Restart arrangement constants (the two nearest teammates stand 8 m from the spot) are close to a prescribed formation. Author disclosed. | Keep as PLACEHOLDER; list in the behavior register. |
| R-6 | Low | Throw intent speed is hard-coded min(27, own max throw speed), so Throw Power has no effect (also noted for ATTR-1, A-5). | ATTR-2 scope. |

## What v0/3 actually fixes (measured over the committed banded 10-seed table; v0/3 body, 27 m/s placeholder)
Groundings about 71 per match (v0/2 seed 1: 6); restart timeouts 1.2% of restarts (v0/2: 25.6%); arrows released about 177 per match with about 41 freezes and 95 misses; 0 majors, about 23 minors per match; all 10 seeds final, no stall. Penalty awards (half goals and full awards) were 154 of 581 points (about 27%; RB-1 had about 78%).

## Measured against the target list (v0/3 baseline, not RB-2.1; placeholders apply)
Total points per match 55-76 (both teams), about 29 per team vs 80-85: NOT MET. Shot attempts 221 in 10 matches (about 11 per team per match) vs about 50: NOT MET. Turnovers about 406 per match (about 200 per team) vs about 100 possessions per team: the possession count is about twice the target and attempts about a fifth of it. Points from play about 73% vs at least 85%: NOT MET but far better than RB-1. Restart timeouts under 5%: MET. Legal-arrow share and DQs not reported in this table.

## Verdict
V1 PASS. V2 PASS for seed 1 (rest not rerun). V3 PASS by tests (not independently probed). V4 PASS. V5 PASS. V7 FAIL until R-1 is fixed. Recommend accepting v0/3 as the contact and restart cognition layer to be merged into the combined line, with R-1 to R-3 recorded.
