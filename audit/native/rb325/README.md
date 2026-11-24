# RB-3.25 reproduction

Use the pinned roster workbook in Git and the project Python 3.12 environment. Run from the repository root. Write new outputs outside the committed evidence directory.

```bash
export PYTHONPATH=.
mkdir -p /tmp/rb325-review
python -m pytest -q b1 native
python -m native.rulebook.scoring_audit --legacy > /tmp/rb325-review/legacy.txt
diff -u native/evidence/rb3-reach/legacy-hashes.txt /tmp/rb325-review/legacy.txt
python -m native.rulebook.individuation_run --compatibility --seed 1 --out /tmp/rb325-review/off.json
python audit/native/rb325/run_core.py --seed 1 --out /tmp/rb325-review/core.json
python audit/native/rb325/sweep.py /tmp/rb325-review/sweep.json /tmp/rb325-review/sweep.csv
```

Use `run_core.py --seed N` for the all-0.70 real bodies anchor and `--roster control` for the uniform anchor. Pass `--roster real --steps 1500` for the timed window on the unmodified roster. Use `audit/native/rb324/bench.py --mode off` from the exact RB-3.22 worktree for the matched comparison. Run the seed order baseline 1, CORE 1, CORE 3, baseline 3, CORE 1 repeat.

Use the exact RB-3.24 checkout at `3edfaad1ae5d50407c16e22dceca6ad92f9d9ae6` as current and import directory for `ablate.py`. The evidence script lives in RB-3.25 and receives a case, seed, and output path. Cases are declared in its `LAYERS` map. The `off` and `on` controls use the original profiles. Isolated cases enable the named switch in the original module, with spectator instrumentation for possession and passes. The source anchor checks reject a different engine layout. `without-<hook>` drops that hook from the union of layer switches. A combined switch can require signals produced by another layer, so a leave-one-out run may reveal dependencies that a one-layer-only run misses.

`report_metrics.py FILE...` prints the per-team stats. Pass completion counts a same-team first control after an open-play pass. The next release, restart, boundary, period or goal closes the witness. A completed bounce counts as a pass in that report. Terminal attempt share is measured with the official RB-3.1 possession convention and carries observed at their scoring-attempt witness.

`sweep.csv` compares all levels against the matched 0.70 seed. The scope column distinguishes direct execution, modeled thresholds, and near-tie choices through the production selector. Decision entropy describes choice frequency across the 20 seeds. It carries no claim about correctness.
