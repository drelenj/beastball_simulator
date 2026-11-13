# HP-002 — M1 acceptance record
Recorded by Claude, 2026-11-13 (owner statement made 2026-11-12 23:59 America/Chicago).

**Status: M1 ACCEPTED by the owner (DreLen), on the owner's decision.** The owner's words: "M1 is accepted".

## What was accepted
Codex branch `b1/m1-decision-outcome`, commit **4b19719** (G1 after review R6): single-slice decision-to-outcome pipeline plus the governed three-athlete scenario `m1-carrier-pass-or-carry-v2`, pass-release-v1 provisional contract, event-derived failure causes with `unknown`.
Independent evidence: reviews R1-R7 on `claude/hp002-audit`. R7 reproduced 25 tests, the 100-seed matrix hash 3f61f1e6... and the 800-seed lane study counts.

## Caveats accepted with it (carry-forward)
1. "A sharper defender defends better" is **not** shown (net interceptions 76 vs 98; effect only conditional on lane selection). It becomes an M2 behavioral acceptance item: mechanism plus net outcome over at least 800 seeds.
2. Half of C3's failures (32 of 63) are `unknown`; positive evidence is wanted later.
3. Pass-release-v1 is an engineering draft; its 60 degree bound is a provisional default to be confirmed from traces.
4. The lane option and carry-versus-pass values are provisional policy, not a behavioral-quality claim.
5. BLK-01..05 full text was never seen by the reviewer; the owner's acceptance stands over that gap.
6. `b1/preservation.py` inventory guard fails on a clean checkout (23 files never committed): engineering fix pending.

## What this does not do
- M2 is **not** started or authorized by this record; it needs separate owner authorization.
- `experiment/prism-sprint-30` and `experiment/prism-sprint-45` stay experiments; neither is merged or accepted. SPRINT-45 findings (R8) are inputs for M2/M3 planning only.
- B0 (2abe497) remains frozen.

## Addendum 2026-11-13: BLK-01..05 checked against the governing text (owner pasted it)
Evidence is on commit 4b19719; checked by Claude against the table in the readiness plan.
| Gate | Result | Basis |
|---|---|---|
| BLK-01 hidden state | MET | poison/perturbation tests (suite + my probes) leave decisions identical; cognition imports only dataclasses/math |
| BLK-02 no retarget | MOSTLY MET | legacy controller trapped at runtime (test asserts the trap fires); receiver change rejected; no static call-graph test |
| BLK-03 two ports, replay | MOSTLY MET | CommandIngress and PhysicalExecutionPort exist; command replay independent of cognition tested; outcome fixtures are episode-level (completion, interception, grounding seeds), not separate fixed-command fixtures per path |
| BLK-04 order independence | MET for the M1 slice | batch permutation test; only two resources in M1 |
| BLK-05 frozen B0 | PARTIAL | B1 is a separate package and B0 files are unchanged, but the port calls the B0 loader's install in a dedicated process, and the baseline guard fails on a clean checkout (23 uncommitted files); no CI |
The owner accepted M1 with these partial items open. They are engineering follow-ups, not canon.

## Addendum: change to carry-forward item 1
Owner direction (2026-11-13): decision and outcome quality cannot be defined in advance because the best way to play is the thing being discovered. Therefore M2 acceptance tests judge **function** (boundary, ownership, determinism, ratings changing behavior through an observed mechanism), not whether any decision is "better". "Sharper defends better" is withdrawn as an acceptance item; quality is measured only by game-level results (score, wins) in many-match comparison.
