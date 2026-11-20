# RB-3.16 control side-bias (claude/soak-rb-3-16-control from 9c37fd4)

TESTED measurements only. Not ACCEPTED. Both control teams have identical ratings, so any A/B difference is side/slot bias.

## OWNER BRIEFING

1. **Accomplished (TESTED).** Gate passed: control seed 1 reproduced trace `c251c06f…` and state `4a3cbc5c…` exactly. Twenty new control games (seeds 4-23) ran with `python -m native.rulebook.reach_run --block control`; with seeds 1-3 that makes 23 games. All 23 finished with status `final`. None hit the step cap or needed killing.
2. **What it shows (TESTED).** Over 23 identical-rating games, slot B scores **+1.5 points** more than slot A (A mean 61.6, B mean 63.1). The sd of the per-game difference is 22.7, the paired t is **0.31**, and the 95% interval is **−8.3 to +11.3**. B won 11 games, A won 12. Possessions are equal in both slots (204.1 each). Shots and shots scored are close (A 30.2 / 13.3 scored, B 29.6 / 13.8 scored).
3. **Unproven.** The earlier +20.7 figure came from three games; across 23 it is essentially zero. The interval still allows a side effect of up to about 11 points in either direction, which is wide. The coin flip went to B in 15 of 23 games; whether it affects results was not tested, and the binomial result is not significant on its own.
4. **Blocking.** Nothing blocks the run.
5. **Recommended action.** No side bias is established, so the per-period breakdown was not run (the rule was |t| > 2). The earlier swap result (slot B +6.0 on the real roster) is therefore not confirmed as a side effect by this control. Owner to decide whether the real-roster swap difference needs a larger sample. No code change proposed.

## Per-seed table
Table with score, B − A, possessions, shots, shots scored, coin flip winner: `native/evidence/rb316-control/CONTROL_BIAS.md`.

## Summary (23 games)
| measure | value |
|---|---|
| slot A mean points | 61.6 |
| slot B mean points | 63.1 |
| mean difference B − A | +1.48 (sd 22.71) |
| paired t (n = 23) | 0.31 |
| 95% interval | −8.34 to +11.30 |
| B wins / A wins | 11 / 12 |
| coin flip winner B / A | 15 / 8 |

## Files
- Result JSON: `native/evidence/rb316-control/control/control-seedNN.json`.
- Raw logs (gzipped): `native/evidence/rb316-control/control/raw-control-seedNN.json.gz`. Seeds 1 and 4-23 were run here; seeds 2 and 3 were copied from `claude/soak-rb-3-16` @ 409135f (same harness and commit).
- Tables: `CONTROL_BIAS.md`, `control_bias.json`.
- Recompute: `python3 native/evidence/rb316-control/tools/control_bias.py native/evidence/rb316-control`.
