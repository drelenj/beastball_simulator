# Review: RB-3.26 ORACLE harness, DRILL v0, GAUGE pilot (codex/rb-3-26-oracle-drill @ 14b393d), 24 Nov 2026

Claude (lead reviewer). Status: verification TESTED; nothing ACCEPTED.

## Reproduced independently (fresh worktree at 14b393d)
- Compatibility real seed 1: 57-76, 32,528 steps, trace 44399b08...c072, state 046ea55b...865d (gate d).
- New CORE (after the Reaction tick fix) neutral-real seed 1: 61-80, 32,509 steps, trace c1a578db...a256, state c517e00f...2745 (= Codex).
- GAUGE table recomputed from gauge.jsonl.gz: true regret 0.542 / 0.551 / 0.568 at Playmaking 0.40 / 0.70 / 1.00 (SE 0.021 each); belief regret 0.0138 / 0.0021 / 0. Paired by moment, 1.00 minus 0.40 = +0.025 (SE 0.015).

## Findings
1. The rating mechanism works; the values it serves are wrong. Higher Playmaking follows the hand-set values more faithfully (choices that differ from the hand-set best: 4.9% at 0.40, 1.8% at 0.70, 0 at 1.00). The hand-set best is significantly worse than the rollout best (more than 2 SE) in 14 of 60 carrier moments.
2. Decision error is small: a 0.40 player loses 0.014 points per decision by his own values, against 0.55 lost to wrong values. Decision ratings barely change choices yet.
3. Passing and Takedown rollouts carry no signal: every option ties in 28 of 30 Passing and 30 of 30 Takedown moments, because the points-only horizon ends before anyone scores. Finishing has signal: hand-set aim significantly worse in 13 of 30.
4. Cost: median 21 s per carrier decision, 5-8 s per sub-agent decision (better than the design estimate).
5. Held-out (seed 3): shot and tackle tables beat the pooled baseline slightly; pass completion and field-position tables did worse. Too few moments.

## Recommended (lead decisions, ENGINEERING / BEHAVIORAL)
- Score every rollout as points plus the expected points of the end state (or run sub-agent rollouts to the end of possession), so short horizons stop tying.
- Mine more moments (seeds 1-10) before fitting tables again.
- Load DRILL carrier values into PRISM as an opt-in versioned artifact, then rerun GAUGE: the pass condition is lower true regret at higher Playmaking.
- After that, calibrate the decision-error spread so ratings matter by a measured amount.
