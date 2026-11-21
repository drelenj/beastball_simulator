# RB-3.18 verification (Claude; Codex code 380d6fb/0bf2036 was pushed untested)

Branch claude/rb-3-18-verify from codex/rb-3-18-carrier-moves @ 0bf2036. No code changed by Claude.
Status: IMPLEMENTED (Codex) and TESTED (this run). Not ACCEPTED.

- Full suite: pytest -q b1 native -> 613 passed, 23 subtests (pytest.txt).
- Legacy guards (scoring_audit --legacy): identical to the 185b557 reference for native-v0/2, v0/3, rb/2, seeds 1 and 3 (legacy.txt).
- Identity: carry_release_radius_m=0.0, flags OFF, real seed 1 reproduces the ACCEPTED RB-3.16 hashes 93b1f57e.../b9962ddf... exactly.
- Matches via native.rulebook.reach_run, real 1/3/5 + control 1: "rule" = 3 m release-carry rule only (default config); "on" = rule + rb3_carrier_moves_enabled + rb3_handoff_block_enabled. Raw logs gzipped under runs/. Measurement: measure318.py -> measure318.json.

| | real 1 | real 3 | real 5 | control 1 | real team-score median | real possessions/team |
|---|---|---|---|---|---|---|
| rule only | 74-92 | 42-92 | 84-60 | 68-55 | 79 | 215 |
| all ON | 67-92 | 66-80 | 55-51 | 59-80 | 66.5 | 204 |

- Rule only: 0 release-carry goals (nobody releases within 3 m), scores identical to RB-3.16.
- All ON: carry goals 4/6/5/5 (RB-3.16: 4/2/1/2); stretch 3-6 per match, almost all score; trucks ~105-126 per match, 12-15 broken; stiff-arms 82-160; handoffs 239-323; blocks 119-164. Throw points fall (real 5: 77 vs 120), so the median drops below the owner's 75-90 range. The cognition hook is a crude placeholder (Codex), not tactics.
Owner ranges (20 Nov): 75-90 points per team; 100-150 possessions per team.
