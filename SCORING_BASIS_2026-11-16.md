# Scoring basis — owner ruling, 16 Nov 2026

Status: working canon for measurement. Point values remain provisional until the self-play experiment reports.

| Score | Points |
|---|---:|
| Carry | 5 |
| Thrown goal, release under10m | 2 |
| Thrown goal, release10m up to20m | 3 |
| Thrown goal, release20m or more | 4 |
| Half goal | 1 |
| Full-goal award | 3 |
| Own goal | 2 |

Implementation requirements:

- `native-rb/2` accepts only `scoring="banded"`.
- Flat scoring is retained only inside historical artifacts and legacy replay profiles. It is not a measurement basis.
- Current runners, soaks, self-play harnesses and new evidence use the banded configuration by default.
- Release-band measurement counts athlete-declared shots only. Each band reports attempts, goals, points, success rate and points per attempt.
- Carries use an independent attempt/goal/points counter. Own goals and the complete release ledger are separate.

This ruling resolves the scoring-basis conflict identified as Q1 in `HP-002: Ideal Beastball as measurable targets v0`. It does not ratify any number marked PROPOSED in that document and does not claim the current implementation meets its target ranges.
