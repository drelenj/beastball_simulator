# RB-3.28 reproduction

Use Python from the simulator environment with openpyxl. Run from the repository root. Each batch lane runs one match at a time.

```bash
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
work=$(mktemp -d)
ref=b284e822fa2f23c820987c795a2d780f16334fc3
name='audit/arcade/ratings/NBL_2026-27_Opening_Night_Rosters_ratings-0.4_overall-trials.xlsx'
git show "$ref:$name" > "$work/ratings-0.4.xlsx"
bash audit/native/rb328/batch.sh "$work/ratings-0.4.xlsx" "$work" off
bash audit/native/rb328/batch.sh "$work/ratings-0.4.xlsx" "$work" on
python audit/native/rb328/report.py "$work" --out "$work/report"
```

For one game, use the normal match CLI with the ratings workbook. Omit the fatigue switch to reproduce the earlier CORE path.

```bash
python -m native.rulebook.individuation_run --workbook "$work/ratings-0.4.xlsx" \
    --technical explicit --fatigue-rotation --seed 1 --out "$work/match.json"
pytest -q b1 native
python -m native.rulebook.scoring_audit --legacy > "$work/legacy.txt"
diff -u native/evidence/rb3-reach/legacy-hashes.txt "$work/legacy.txt"
python -m native.rulebook.individuation_run --compatibility --seed 1 --out "$work/compatibility.json"
python audit/native/rb327/match.py --seed 1 --out "$work/core.json"
```

The matched windows use `audit/native/rb328/match.py --benchmark --steps 1500` on the explicit ratings 0.4 roster. Use sequential runs and reverse the order across seed pairs. A fresh process with the same input reproduces the full match hashes. Minute summaries assign time to the admitted lineup and use regulation clock time. Raw records also include total playing time with overtime.

The final evidence checker also compares the fatigue-off results with the RB-3.27 committed evidence. Preserve the result filenames used by the scripts.

```bash
python audit/native/rb328/match.py --workbook "$work/ratings-0.4.xlsx"     --on --seed 1 --out "$work/replay-1.json"
python audit/native/rb328/verify.py "$work"
```
