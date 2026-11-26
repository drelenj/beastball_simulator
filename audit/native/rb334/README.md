# RB-3.34 carry valuation evidence

Run from the repository root using CPython 3.13.5, NumPy, openpyxl and pytest. The runner embeds the named JSON and CSV box scores in the compressed result and atomically publishes one file per game.

```bash
book=/tmp/rb334-ratings.xlsx
git show 'b284e822fa2f23c820987c795a2d780f16334fc3:audit/arcade/ratings/NBL_2026-27_Opening_Night_Rosters_ratings-0.4_overall-trials.xlsx' > "$book"
python3.13 -m audit.native.rb333.match A6 "$book" /tmp/A6-1.json.gz --seed 1
python3.13 -m audit.native.rb333.match A4 "$book" /tmp/A4.json.gz --diagnostics
python3.13 -m audit.native.rb334.tables audit/native/rb334/evidence audit/native/rb333/evidence /tmp/rb334-tables.md
cmp /tmp/rb334-tables.md audit/native/rb334/TABLES.md
python3.13 -m pytest -q b1 native
python3.13 -m native.rulebook.scoring_audit --legacy
```

A6 uses the A5 lineup, planned rotation, 300 ms decision base and seven-point scoring. Its carry_value switch replaces the carry_seven valuation path. The observer reads the existing decision records and snapshots true state solely for audit. Neither observation changes the decision or consumes match randomness.

The near-goal diagnostic covers holders within 20 m planar distance of goal centre. It classifies the selected Playmaking option before a zone exit override or sub-agent choice. Route carry means the explicit route to the mouth. Continuation includes diversion, evasion, retain, pass and handoff.

Keeper motion uses physical speed at shot release. Target speed is net displacement between the current settle target and the one in force 500 ms earlier, divided by 0.5 s. An accepted non-settle command clears the history. The observer also treats a last settle command older than two base decision intervals as expired.

The non-carrier witness joins each episode to its first admitted command. Its believed holder comes from the defender menu's freshness function. Age comes from the ball course used by that decision. Cause labels infer explanations from the recorded event order. The classes give priority to a handoff by the target, then a still-airborne release by the target, then a remembered belief matching the target. The sample uses offline seed 334.
