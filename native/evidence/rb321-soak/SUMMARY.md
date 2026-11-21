# RB-3.21 soak for acceptance decision (claude/soak-rb-3-21 from eb788ec)

TESTED measurements only. Not ACCEPTED. Provisional code, measured on the owner's acceptance-decision soak plan.

## OWNER BRIEFING

1. **Accomplished (TESTED).** Gate passed: real seed 1 with the three RB-3.21 overrides reproduced trace `44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072` and state `046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d` exactly. All 13 matches (real seeds 1-10, control seeds 1-3) finished with status `final`. None hit the step cap or needed killing.
2. **What it shows (TESTED).** Real roster, 20 team-games:
   - Median team score **84.5** (inside the 75-90 range), mean **89.1**, sample sd **21.9** (pro reference 12.7), p5 / p95 **61.8 / 121.2**.
   - The median hides a split. Garvian (slot A) has a per-team median of **68.5** and Ala Apex (slot B) **108.5**, both outside the 75-90 per-team range. Ala won 9 of 10 real games, the same pattern as RB-3.16 (9 of 10).
   - Possessions: mean **151.9** per team, median 150.5, range 143-163. The 100-150 range is exceeded in **10 of 20** team-matches; in **6 of 10** matches at least one team is above 150.
   - Shot conversion median 49.7%. Points are mostly from releases; carry points median 22.5 per match (both teams).
3. **Unproven.** Ten real and three control matches is a small sample. Two measures are definition-limited: "restart throw lost ≤5 s" uses the earlier RB-3.11 definition (any quota reset by the other team within 5 seconds), which fires on ordinary possession changes; and about 12% of possession spans end with no classifiable terminating event. The control block has identical teams but only three matches. No acceptance standard is applied here.
4. **Blocking.** The per-team split (Garvian 68.5 vs Ala 108.5) and the team-score sd (21.9 vs 12.7) are measured departures from the owner ranges. Owner to decide whether they block acceptance. No code change proposed.
5. **Recommended action.** Owner to review the per-team split against the 75-90 range and the sd against the pro reference, and to decide whether the possession count (mean 151.9, 10 of 20 team-matches above 150) is acceptable. Owner to decide whether a larger real-roster sample is needed before acceptance.

## Files
- Per match and summaries: `native/evidence/rb321-soak/SUMMARY_TABLE.md`; machine-readable: `rb321_table.json`, `rb321_summary.json`.
- Result JSON: `native/evidence/rb321-soak/real/real-seedNN.json`, `native/evidence/rb321-soak/control/control-seedNN.json`.
- Raw logs (gzipped, with overrides): `native/evidence/rb321-soak/real/raw-real-seedNN.json.gz`, `native/evidence/rb321-soak/control/raw-control-seedNN.json.gz`.
- Gate: `native/evidence/rb321-soak/real/real-seed01.json` against `native/evidence/rb321/hashes.txt`.

## Recompute
```
python3 native/evidence/rb321-soak/tools/rb321_measure.py native/evidence/rb321-soak
python3 native/evidence/rb321-soak/tools/rb321_tables.py native/evidence/rb321-soak
```
Harness: `python -m native.rulebook.reach_run --block {real|control} --seed N --override rb3_carrier_moves_enabled=true --override rb3_handoff_block_enabled=true --override rb319_ball_in_play_enabled=true --outdir <dir>`.
