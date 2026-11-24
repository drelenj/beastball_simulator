# RB-3.24 reproduction

Run from the repository root with the project's Python 3.12 environment, pytest, NumPy, openpyxl and the pinned workbook Git object `81f92e3`. Write outputs outside the committed evidence directory.

```bash
export PYTHONPATH=.
EVIDENCE=/tmp/rb324-evidence
mkdir -p "$EVIDENCE"
python -m pytest -q b1 native
python -m native.rulebook.scoring_audit --legacy > "$EVIDENCE/legacy.txt"
diff -u native/evidence/rb3-reach/legacy-hashes.txt "$EVIDENCE/legacy.txt"
python -m native.rulebook.individuation_run --compatibility --seed 1 --out "$EVIDENCE/compatibility.json"
for roster in neutral-real control; do
    for mode in off on; do
        python -m native.prism_lab --match "$mode" --roster "$roster" --out "$EVIDENCE/$roster-$mode.json"
    done
done
python -m native.prism_lab --out "$EVIDENCE/lab.json"
python audit/native/rb324/summarize_lab.py "$EVIDENCE/lab.json" "$EVIDENCE/sweep.csv"
python audit/native/rb324/playmaking_threshold.py --out "$EVIDENCE/playmaking-threshold.json"
```

Run `audit/native/rb324/bench.py --mode off --seed 1 --out FILE` using the RB-3.22 checkout as current directory and this script's absolute path. Run it using `--mode on` from RB-3.24. Both execute 1,500 steps using the original NBL roster. Repeat seed 1 in a fresh process for determinism. Alternate mode order over seeds 1 and 3 when timing.

`rating-sweep.csv` is the summary for 20 matched scenarios per rating and level. A change can be a changed detection, preparation opportunity, command, or physical quantity. Read the evidence-scope column before interpreting the count. Empty counts mean the probe measured a mapped parameter only. The gzip includes the per-seed outputs. `playmaking-threshold.json` adds a focused stress case in which the policy bias makes the initial decision close, and it holds that bias constant across the paired rating sweep.
