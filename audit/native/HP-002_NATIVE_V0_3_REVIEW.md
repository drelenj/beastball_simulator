# HP-002: independent review of native-v0/3 (FAB-1) — NOT COMPLETED
Claude (author of FAB-1), 2026-11-15. This file records the state of acceptance item V6. I am the author and do not grade my own work.

## Status
V6 is **not met**. A separate reviewer agent, which did not write the change, was started on `git diff a1b1313 c521c49` with instructions to look for ungated effects on native-v0/2, information-boundary leaks, any automatic takedown, cognition bugs, a flattering restart metric, weak or vacuous tests, and overstated claims. It stopped on the account usage limit before reporting. No findings were returned, so none are recorded here and none should be inferred.

## What a reviewer still has to do
1. Read `git diff a1b1313 c521c49` (code) and `NATIVE_V0_3_MANIFEST.json`, `native/evidence/v0-3/` (evidence).
2. Answer the eight questions in the reviewer brief: gating of every hunk; own-body view fields; engine contact hooks and stale intents; correctness of `native/cognition_v3.py`; soundness of the "eligible" restart denominator; remaining arrow literals; test strength and matrix mapping; honesty of status and questions files.
3. Record findings in this file as R-1.. with severity and evidence.

## Points the author already knows a reviewer should press on
- An athlete's intent persists until his next decision (500 ms): a takedown or run-through intent can outlive the situation it was chosen for.
- The restart "eligible" subset excludes 34 of 2328 tosses as not reachable; the unfiltered rates are reported beside it.
- The v0/3 Archer change (no release during a pass in flight) is outside the three named FAB-1 items; it is disclosed as Q-FAB1-2.
- Decision constants in `native/cognition_v3.py` are unsearched defaults; "two nearest teammates stand 8 m from the spot" is close to a prescribed arrangement.
- The first/second tackle split is not in the run results.
