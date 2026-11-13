# HP-002 — Review R7 of Codex G1 R6 response (commit 4b19719)
Claude, 2026-11-13. Clean checkout of 4b19719 (parent 77604e1).

## OWNER BRIEFING
1. **Accomplished.** Codex fixed every R6 item and reported its own results honestly, including the ones that went against it. I reproduced them: 25 tests pass, the 100-seed matrix hash matches (3f61f1e6...), all six replays are deterministic, and the 800-seed lane study reproduces every count (my 582 s run).
2. **What B1 can do now.** A defender whose Judgment rating continuously changes how deeply it covers the pass lane (no on/off threshold), a carrier whose pass direction is corrected at release under a written contract (with a 60 degree reject rule), and failure causes derived from recorded events, with unexplained cases labeled `unknown`.
3. **What the evidence shows, and does not.** Rating-driven decisions do reach outcomes through a visible mechanism: when both defenders choose the lane option (107 paired seeds), the sharper one intercepts more (45 vs 28; gained 32, lost 15; exact p = 0.019). But overall the sharper defender is **not better**: 76 interceptions vs 98 across 800 seeds (gained 57, lost 79, p about 0.07), and at the moment of release it stands about 0.8 m *farther* from the pass lane on average. Codex says exactly this and claims no net improvement. "Sharper means better defending" is not shown, and I would not claim it.
4. **Blocking M1.** Nothing mechanical. The two flags Codex's matrix reports as false (BA-M1-2 and BA-M1-3) fail because of how those two criteria were worded, not because of a defect: see Gates. A behavioral decision is needed on how to treat "sharper is better" (my recommendation below). BLK-01..05 full text still unseen by me.
5. **Recommended action.** See below.

## Verified (TESTED by me)
25 tests pass (21 s); B0 manifest clean. Matrix hash 3f61f1e6... equal (219 s). Lane study: all counts and the comparison block equal Codex's (C4 98 intercepted, C5 76; matched 107 / 28 / 45 / 32 / 15; p 0.0186). My `study_hash` differs (964bdce... vs a3a68939...) because Codex's committed summary combines two 400-seed ranges and mine is a single 800-seed pass; the comparison blocks are identical, so this is an ordering artifact, not a discrepancy in results.
Unknown counts in the 100-seed matrix: C0-C2 0; C3 32 of 63 failures; C4 2; C5 3.

## Findings
**H1 CLOSED. H4 CLOSED provisionally.** Contract pass-release-v1 is implemented with the correction angle recorded, the 60 degree `rejected_geometry` bound and MR-1..5 tests; the engine does not add carrier velocity, so recompute-before-throw is correct. The 60 degree value remains my provisional default.
**H2 CLOSED as designed.** Residuals are now `unknown`. The matrix flag `BA-M1-2_all_failures_traceable` is false only because unknown > 0; my R5 wording asked to *allow* unknown, so the criterion text, not the code, is wrong. Clarified criterion: every named cause is backed by a recorded-event predicate, unknown counts are reported, and the unknown branch is reachable. Follow-up (not a gate): half of C3's failures are unexplained and deserve positive evidence later.
**H3 CLOSED as mechanism, OPEN as quality.** The matrix flag is false at 100 seeds because that study is underpowered; the 800-seed study supports the mechanism by Codex's pre-stated rule (at least 100 matched seeds, more gains than losses, p < 0.05). Caveat: the matched analysis conditions on both defenders choosing the lane, a post-treatment selection, so it shows the option matters when used, not that the sharper defender is better overall. The lane option is selected in only about 20% of seeds. Net effect is negative (p about 0.07).
**Observation.** The lane option wins on value essentially whenever it is enabled (`10.08 - .01*d` vs pursuit `10 - .01*d`), so selection depends on the `enable_lane_option` flag plus belief geometry, not on a competition between options. Acceptable as a provisional M1 policy; not a behavioral-quality claim.

## Gates
BLK-01..05 unchanged from R3. BA-M1-1 pass. BA-M1-2 pass under the clarified criterion. BA-M1-3 pass as *causal propagation of a rating-driven decision to outcomes through an observed mechanism*; monotonic quality not shown. BA-M1-4 pass. BA-M1-5 pass (reproduced). BA-M1-6 pass (219 s matrix, 582 s study).
**My verdict: M1 behaviorally sign-off recommended, with the caveats above. I do not declare it ACCEPTED** (the formal gate rests on BLK-01..05 text I have not seen, and acceptance is the owner's).

## Carry-forward to M2
1. Rating-to-quality monotonicity ("sharper defends better") becomes an M2 behavioral acceptance item, tested as a mechanism plus a net outcome over at least 800 seeds.
2. Positive evidence for C3 unknowns.
3. Contract pass-release-v1 bound confirmed or replaced from traces.
