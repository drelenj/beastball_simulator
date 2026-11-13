# HP-002 — Review R6 of Codex G1 v2 (commit 77604e1)
Claude, 2026-11-13. Clean checkout of 77604e1 (parent c083ae9).

## OWNER BRIEFING
1. **Accomplished.** Codex addressed all four R5 findings. The defender now interferes with passes (about 10% interceptions in the lane scenario, up from 1 in 400 earlier), failure causes come from recorded physical events, and the carrier no longer fires passes from a stale position. I reproduced everything: 21 tests pass, the 600-episode matrix hash matches exactly, all six replays are deterministic, and my boundary probe shows no hidden-state leak.
2. **What B1 can do now.** Three athletes (carrier, defender, receiver) run through the full pipeline in the real engine. Passes complete, drop, get intercepted or get disturbed by physics. The defender can choose to cover the pass lane from its own belief.
3. **Unproven.** The one claim still not shown is the point of H3: that a *sharper* defender plays measurably better. On the 100 seeds Codex ran, interceptions went 8 to 11. I ran 400 fresh seeds per condition: 41 to 44, which is within noise (a sign test on who gained and who lost interceptions gives p of about 0.8). The "35 paired differences" is not evidence of a quality effect: even C0 and C1 differ in 100/100 execution hashes, and on fresh seeds 171 of 400 pairs end differently, in both directions. The mechanism does exist (in 3 of 12 seeds I traced, the sharp defender chose the lane option and all three were intercepted), but it fires in a minority of runs and is a step on a hand-set constant.
4. **Blocking M1 acceptance.** One narrow item (H3), plus small corrections to the report. This is not a rebuild.
5. **Recommended action.** Relay the R6 block to Codex. Nothing for you to decide. I will also write the moving-release contract that Codex's report cites as "approved" (it is only a draft entry in my action-resource table; this is my spec gap, not an owner canon item).

## Verified (TESTED by me)
- 21 tests pass (`pytest b1`, 12 s). Frozen B0 inventory manifest regenerated clean.
- Matrix: `matrix_hash` f9afc5f4... equal; all acceptance flags and all six determinism replays true; 204 s wall.
- C0/C1/C2: 82 completed / 18 incomplete each. C3: 31 / 63 / 2 intercepted / 3 grounded / 1 reach. C4: 56 / 36 / 8. C5: 55 / 32 / 11 / 2 reach. Failure-cause counts per condition as in the report; zero unknown.
- Boundary: core.py imports only dataclasses, math. Probe (`m1_review_probe2.py`): poisoning hidden attributes of B0 and A1 leaves the decision identical; moving the carrier changes it. No leak found.

## Findings
**H1 CLOSED.** Defender matters physically: C4 intercepts 8% on seeds 1-100 and 10.3% on 101-500 (41/400). `test_defender_tracks_released_ball_from_belief` confirms post-release ball pursuit comes from belief decisions.
**H2 CLOSED with one residual.** Causes are event-derived and `unknown` is reachable (test passes `{}`, a thin test but the branch is real). Residual: `pass_accuracy_failure` is a by-elimination label (32 of 63 C3 failures; the evidence shows the aim was near A1 but cannot say why the flight missed). That reintroduces H2 in smaller form. Either split it with positive evidence or label those `unknown`.
**H3 NOT SHOWN (narrow).** Evidence on fresh seeds 101-500: C4 intercepts 41, C5 44; gained 37, lost 34, p about 0.81; completed 250 vs 244; paired endpoint differences 171/400. The BA-M1-3 flag passes because it requires only `c4 != c5 and paired > 0`, which holds for any perturbation. Mechanism: lane option value is `8.9 + 1.2*judgment - .01*distance` versus carrier pursuit `10 - .01*distance`, so at judgment 0.7 it never wins and at 0.9 it wins only when the lane point is at least 2 m closer than the carrier. That is a step function placed to switch at about 0.9, and C5 also raises all JUDGE ratings to 0.9 plus the config judgment, so the report's "only Judgment/Reaction changes" is not accurate. Provisional policy is acceptable for M1; the effect must be *demonstrated at mechanism level*, not inferred from outcome counts.
**H4 CONDITIONALLY CLOSED.** The carrier now recomputes the pass direction at the release tick from the authoritative release origin to the semantic aim (own-body position; target and receiver unchanged). This respects "Motor Control cannot change type, target or receiver". But the report and conformance file call it an "approved separable bundle"; O4 v3.5 is a draft and lists locomotion + ball_control_release only as `YES*` pending an action-specific contract that does not exist yet. I will write it. Side effect worth knowing: C3 completions went from 0 to 31, caused by this change alone.

## Asks for Codex
1. Mechanism-level BA-M1-3 evidence: fraction of seeds where B0 selects the lane option in C4 vs C5; B0 distance to the pass lane at release; interception rate conditional on the lane option being used. Show a directional effect with the seed count stated, or soften the claim. Preferably make the judgment effect continuous rather than a step.
2. Split or relabel `pass_accuracy_failure`.
3. Correct the report: "approved separable bundles" (draft, pending contract), "isolates only Judgment/Reaction", and the 35 paired differences as evidence of quality.
4. Keep: B0 frozen, no legacy override, determinism. Do not start M2.

## Gates
BLK-01..05 unchanged from R3. BA-M1-1 pass; BA-M1-2 pass with residual; BA-M1-3 mechanism present, outcome effect not distinguishable from noise; BA-M1-4 pass; BA-M1-5 pass (reproduced); BA-M1-6 pass (204 s). **M1 NOT YET ACCEPTED (one narrow item).**
