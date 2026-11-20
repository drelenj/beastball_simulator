# RB-3.16 soak (claude/soak-rb-3-16 from 9c37fd4)

TESTED measurements only. Not ACCEPTED. Baseline: claude/rb-3-16-merge @ 9c37fd4 (provisional).

## OWNER BRIEFING

1. **Accomplished (TESTED).** Determinism gate passed: real seed 1 reproduced trace `93b1f57e268ee6c436fae47109e4e2987cfdf7024df5575b6405e119c5ed32d7` and state `b9962ddfb23dbc96551258ea6c2132565804d22ec1b0c87295e3f3ff37d59854` exactly. All 13 matches (real seeds 1-10, control seeds 1-3) finished with status `final`. No failures, no step-cap hits, no kills.
2. **What it shows (TESTED).** Real-roster team scores: median 75, mean 76.5, sample sd 18.0, p5-p95 50.5-104.0 across 20 team-games. The owner canon is median 76, sd 12.7, p5-p95 59-102. The median matches; the spread is wider than canon. Possessions are about 216 per team (target about 100). About 23% of possessions end in an attempt (target about 50%). Shot outcome shares, medians across the 10 real seeds: 53.8% scored, 27.9% keeper, 8.9% own, 8.6% out/award, 3.3% field. Points come mostly from releases (totals across all 13 matches: 711 A, 923 B). Carry points total 45 (A) and 130 (B); carry goals per match are 0 to 4.
3. **Unproven.** Ten real-roster games and three control games are a small sample. Interception rate (median 17.7%) and within-3 m count (median 7.5) are single-match measurements, not calibrated against any target. Carry outcome by type (tackled / grounded / turnover / stopped short) is not in the engine report and is not reported. Zone events: 8 `zone_foul_diagnosis` records in real matches and 8 in control; the foul-reason count for `zone_unmarked` is 19 across all 13 matches. These two counts are not reconciled here.
4. **Blocking.** Nothing blocks the run. The team-score spread (sd 18 vs canon 12.7) and the possession and attempt rates are measured departures from the canon targets; they are reported, not interpreted.
5. **Recommended action.** Owner to review the spread and the possession/attempt rates against the canon targets. Owner to decide whether the 10-game real sample is enough for a spread comparison. Owner to reconcile the zone diagnosis count (16) with the zone_unmarked foul count (19). No code change proposed.

## Determinism gate
| run | trace_hash | state_hash | result |
|---|---|---|---|
| real seed 1 (this run) | 93b1f57e268ee6c436fae47109e4e2987cfdf7024df5575b6405e119c5ed32d7 | b9962ddfb23dbc96551258ea6c2132565804d22ec1b0c87295e3f3ff37d59854 | exact match |

## Tables and files
- Per-match table, real and control summaries, foul reasons: `native/evidence/rb316-soak/SUMMARY_TABLE.md`.
- Machine-readable per match: `native/evidence/rb316-soak/measure316_table.json`; team-score statistics: `measure316_summary.json`.
- Result files: `native/evidence/rb316-soak/real/real-seedNN.json`, `native/evidence/rb316-soak/control/control-seedNN.json`.
- Raw engine logs (gzipped): `native/evidence/rb316-soak/real/raw-real-seedNN.json.gz`, `native/evidence/rb316-soak/control/raw-control-seedNN.json.gz`.
- Harness: `python -m native.rulebook.reach_run` (native/run.py::run_match, native-rb/3, roster ref 81f92e3).
- Measurement: `tools/measure316_soak.py` (definitions as in native/evidence/rb316/measure.py; keeper = each team's first role-keeper in roster order, which matches the measure.py ids on the real roster) and `tools/rb316_tables.py`.

## Recompute
```
python3 native/evidence/rb316-soak/tools/measure316_soak.py native/evidence/rb316-soak
python3 native/evidence/rb316-soak/tools/rb316_tables.py native/evidence/rb316-soak
```
Checked: recompute from the gzipped logs reproduces `measure316_table.json` and `SUMMARY_TABLE.md` byte for byte.
