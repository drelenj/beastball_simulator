# RB-3.15 evidence (PROVISIONAL, claude/rb-3-15-shot-quality; code 271510c; baseline RB-3.14 3ba853a)

## OWNER BRIEFING
1. Accomplished (IMPLEMENTED, TESTED): S-1 aim away from the keeper (9 y offsets x 3 heights, keeper advanced over own release delay + flight, best keeper margin, none below 0.3 m); S-2 shot lane (RB-3.14 release-time lane check to the aim, field defenders only); interim shot value +1.5 x min(margin, 2); athlete's own release delay exposed in the view and used for passes and shots. Full suite 569 passed (7 new in test_rb315.py; one RB-3.14 test fixture updated to set own_release_ms); hashes of native-v0/2, v0/3, native-rb/2 identical to 185b557.
2. Can do now: shots aim near a post away from the keeper and switch sides with him; a keeper covering the whole mouth or a field defender in the lane means no shot is offered. Clean conversion batch (12 m, set keeper, no defenders, 50 shots): S-1 aim 8 scored / 42 keeper; old aim 4 scored / 46 keeper (batch_e.txt).
3. Scoring target NOT approached: points per team (real) 27.2 -> 21.3 (target 76). Shots per team fell 31.7 -> 14.2 (offered shots are now rare), conversion per shot rose 12.6% -> 27%; field-defender takes 66 -> 3, keeper takes 73 -> 40 (still 47% of offered shots). Control match 10-13 -> 45-20. Carry goals unchanged (3/2/3, control 0). Not tuned.
4. Blocking: BEHAVIORAL questions for Claude in QUESTIONS_FOR_CLAUDE.md (keeper reach definition, fewer shots offered, port release delay mismatch). No owner questions.
5. Recommended: lead decides question 2 (shot availability vs quality) and 1 (keeper reach), then expected-points valuation; the keeper's take rate looks engine-bound (Codex audit).

## Before/after (RB-3.14 -> RB-3.15), real 1/3/5, control 1
| metric | RB-3.14 | RB-3.15 |
|---|---|---|
| scores | 24-16, 30-43, 15-35, 10-13 | 15-30, 20-17, 19-27, 45-20 |
| points per team (real mean) | 27.2 | 21.3 |
| shots (real, 3 matches) | 57/58/75 = 190 | 36/29/20 = 85 |
| shot outcomes real: scored / keeper / field defender / own recovery / out | 24 / 73 / 66 / 22 / 5 | 23 / 40 / 3 / 11 / 7 (+1 other) |
| conversion per shot (real) | 12.6% | 27.1% |
| carry goals | 3/6/2/0 | 3/2/3/0 |
| open-play completion | .678/.676/.639/.611 | .637/.625/.600/.713 |
| possessions per team | 173.5/178.5/185/181 | 180/156/159.5/170 |
| share ending in attempt | .242/.238/.243/.210 | .175/.164/.141/.203 |
| intercept rate | .23/.21/.26/.27 | .25/.28/.31/.17 |
Shots by band and outcome per match: diag_shots.txt; passes/interceptions: diag_extra.txt (keeper takes classified by keeper ids = players with any keeper_contact).

## Constants: B-5/RB-3.15 tables at the top of the shot section in native/cognition_rb3.py.
## Per-match hashes (trace / state)
- real1 15-30 steps 35664: 4a83913cd2ef20e07a8e98699a655ee3f59d2d20d45e7a3804970366bd9ecd3a / dad70c2b8470e8bcec6da77f7f55fb5af845621f16876298d16df291089a71e6
- real3 20-17 steps 34150: c2d20f5260e6f40223d134cbf0f5751cef7a7e9b5b68bd09f490e8e07b9bd94e / 5d4b0d7c116a6f752a82b27795c232350e6d4a3bfa03410810282d2adc8c7179
- real5 19-27 steps 33272: 13a2ee8086146e0781f4d882d30f0957e8c8e962a5c66f0aa96a280d609aed8b / 16d096a463fb4b40997d8c562266d7079563c433790222b3c3a90e62cf9693a5
- control1 45-20 steps 36677: f8d54e63a4ced24a2999c5d5135965961009e60aecd99de9d9a4fe3391bae978 / cadb5a9156ea29ad4bed51706f612e77c4665cf25b4da7420e6b9132f1752590
Raw logs: native/evidence/rb315/runs/{real,control}/raw-*.json
