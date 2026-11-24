# Review: RB-3.27 DRILL v1, learned values, ratings 0.4 soak (codex/rb-3-27-drill-values @ b91440d), 24 Nov 2026

Claude (lead reviewer). Status: verification TESTED; nothing ACCEPTED.

## Reproduced independently (fresh worktree at b91440d)
- Compatibility real seed 1: 57-76, 32,528 steps, trace 44399b08...c072, state 046ea55b...865d.
- Learned values ON (drill-v1.json sha256 a19e9c04...), neutral-real seed 1: 61-75, 31,976 steps, trace 4da6c2ad...642d, state 4f5c1f65...9b67 (= anchor/real-1 and determinism repeat). (A first rerun used roster mode "real" by mistake and is not comparable.)
- Soak table recomputed from evidence/matches.csv (below).

## Soak, ratings 0.4, individuation on, starters by OVR 0.422
| Values | Median team | Mean (sd) | Possessions | Attempt share | Ala - Garvian (10 seeds) |
|---|---|---|---|---|---|
| Hand-set | 89.5 | 90.3 (19.9) | 153.2 | 0.35 | +27.0 (SE 5.8), 9/10 |
| DRILL v1 | 81.5 | 79.7 (20.5) | 161.6 | 0.19 | +34.9 (SE 7.8), 10/10 |
Starters (OVR 0.422, field): Ala 86.9, Garvian 78.0; bodies nearly equal (height 2.45 / 2.46 m, mass 263 / 274 kg); Garvian faster (speed 84.3 vs 77.1).
Anchor (learned ON, all 0.70): median 66, possessions 153.2 - outside the owner's ranges.

## Findings
1. Possession-end scoring with the opponent term removed the ties (Passing 27 -> 2, Takedown 30 -> 5).
2. DRILL v1 makes play worse: attempts halve (0.35 -> 0.19), possessions rise. The shot-conversion table is worse than the pooled baseline on held-out data (MSE 0.287 vs 0.250), so shot values are unreliable.
3. GAUGE: Finishing regret falls with rating (-0.095, 1.76 SE, near pass); Playmaking regret still rises (+0.093, 1.4 SE). The learned carrier values still do not track rollout truth well enough.
4. Real ratings (hand-set values) put scoring at the top of the owner's range; possessions slightly above 150; score spread about 20 per team against 12.7 in the pro season.

## Recommended (lead)
- Keep DRILL v1 opt-in. Next DRILL work: report per-option agreement of artifact values with held-out rollouts; richer features and more data for shot and carrier values; then iterate (fit, play with learned values, re-mine, refit) until values stabilise.
- Owner questions: (1) is +27 a fair margin for a 9-point Overall gap? (2) make ratings 0.4 + individuation (hand-set values) the default playing build?
