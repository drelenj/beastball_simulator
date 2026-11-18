# RB-3.8 mass soak (claude/soak-rb-3-8 from 185b557)

Measurements only. Nothing here is ACCEPTED. Baseline: claude/rb-3-8-drop-freeze-recovery @ 185b557 (owner ACCEPTED).

## OWNER BRIEFING

1. **Accomplished (TESTED).** Determinism gate passed: real seed 1 reproduced trace `2579828021cf33701a0d433038a0e9e8858d5ddc06c98223f3ff1e13a53c04c9` and state `e272f807ecbde2e7d2b46d2bd97d433a9084f183ee0b12b1b3fb9b94d0a9a341` exactly. All 13 matches (real seeds 1-10, control seeds 1-3) ran to `final`. No failures, no non-finishing matches, no timeouts.
2. **What it can show now (TESTED).** Per match: score, play vs foul-award points, possessions, attempts, carry goals, DQs, legal-arrow rate, restart timeouts and completion, foul counts by reason, and every `zone_unmarked` call. Raw engine logs are saved for every match.
3. **Unproven.** The control block has only 3 seeds. The `zone_unmarked` count is not zero: 6 calls across the 10 real seeds, 0 to 2 per match. Freeze-recovery occurrences are zero in every raw log and in every foul reason. Carry outcome by type (tackled, grounded, turnover, stopped short) is not recorded in the engine report; only counts are.
4. **Blocking.** Nothing blocks this run. The only open point is the non-zero `zone_unmarked` count, which is reported as measured.
5. **Recommended action.** Owner to review the six `zone_unmarked` calls listed below (their diagnosis records are in the raw logs). Owner to decide whether three control seeds are enough. No rule or code change proposed here.

## Determinism gate
| run | trace_hash | state_hash | result |
|---|---|---|---|
| real seed 1 (this run) | 2579828021cf33701a0d433038a0e9e8858d5ddc06c98223f3ff1e13a53c04c9 | e272f807ecbde2e7d2b46d2bd97d433a9084f183ee0b12b1b3fb9b94d0a9a341 | exact match |

Control seed 1 and real seed 3 also reproduced the RB-3.8 reference hashes.

## Zone_unmarked calls (all six)
| match | fouler | team | period | live ms |
|---|---|---|---|---|
| real-seed02 | B:NBL24-01-10 | B | 4 | 2139459 |
| real-seed03 | A:NBL24-07-10 | A | 3 | 1719539 |
| real-seed05 | A:NBL24-07-03 | A | 2 | 1164502 |
| real-seed05 | A:NBL24-07-17 | A | 4 | 2378590 |
| real-seed09 | B:NBL24-01-04 | B | 4 | 2087791 |
| real-seed10 | B:NBL24-01-22 | B | 3 | 1445245 |

## Tables
Per-match table, foul counts by reason, and min / median / max summaries for real (n=10) and control (n=3): `native/evidence/rb38-soak/SUMMARY_TABLE.md`. Machine-readable: `native/evidence/rb38-soak/soak_table.json`.

## Files
- `real/`, `control/`: per-match result JSON (`*-seedNN.json`) and gzipped raw engine logs (`raw-*.json.gz`).
- `tools/soak_driver3.py`: runner (native/run.py::run_match, step cap 200,000).
- `tools/rb38_soak_report.py`: rebuilds `SUMMARY_TABLE.md` and `soak_table.json` from the logs; reads the gzipped files directly.
- `tools/rb38_report.py`: the 185b557 report script, kept unchanged.
