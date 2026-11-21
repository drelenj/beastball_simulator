# RB-3.16 merge evidence (PROVISIONAL; claude/rb-3-16-merge; merge commit 304cc84)

Merge of codex/rb-3-reach @ b9932db (R-1 arm reach = arm span / 2, one per-athlete release clock, keeper reaction gate, off-ball top speed)
and claude/rb-3-15-shot-quality @ 9fc4f51 (S-1 aim away from the keeper, S-2 shot lane, own release delay).
Lead integration fixes: port.py view fields (Codex release clock + Sonnet body_height); RB-3.15 keeper model aligned to arm reach
(hand point .62 x height, coverage .9 x arm reach; fallback = control arm reach 1.26431); test_rb315 fixtures moved to arm reach.

Status: IMPLEMENTED and TESTED (4 matches). Not ACCEPTED.

- Full suite: pytest -q b1 native -> 586 passed, 23 subtests (pytest.txt).
- Legacy hash guards (native.rulebook.scoring_audit --legacy): identical to codex/rb-3-reach legacy-hashes.txt (185b557 reference) for native-v0/2, v0/3, rb/2, seeds 1 and 3 (legacy.txt).
- Matches: native.rulebook.reach_run, real seeds 1/3/5 and control 1; raw logs runs/{real,control}/raw-*.json.gz; result files beside them.
- Measurement: measure.py (same definitions as audit/analysis/scoring); measure_rb316.json vs measure_r1.json (R-1 corrected run).

| Match | R-1 score | RB-3.16 score | Shots scored / keeper / field (%) | Possessions per team | Tackles | Carry goals |
|---|---|---|---|---|---|---|
| real 1 | 43-66 | 74-92 | 54.7 / 25.0 / 1.6 | 227 | 82 | 4 |
| real 3 | 57-88 | 42-92 | 44.3 / 28.6 / 5.7 | 217 | 68 | 2 |
| real 5 | 51-60 | 84-60 | 51.6 / 29.0 / 3.2 | 201 | 88 | 1 |
| control 1 | 59-83 | 68-55 | 44.3 / 18.0 / 11.5 | 206 | 75 | 2 |

Real-roster team scores: median 79 (owner target 76, NBL median); mean 74; sample sd ~18 over 6 team-games (pro sd 12.7) - too few games to judge spread.
Open: possessions ~200-228 per team (target ~100); ~20% of possessions end in an attempt (target ~50%); points almost all from throws (allowed: split left to emerge).
