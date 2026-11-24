# ORACLE DRILL reproduction

Use the repository's Python 3.12 environment with NumPy, openpyxl and pytest. Run from the repository root and write fresh output to a separate directory.

```bash
export PYTHONPATH=.
mkdir -p /tmp/rb326-review
python -m pytest -q b1 native
python audit/native/rb326/reaction.py
python -m native.rulebook.scoring_audit --legacy > /tmp/rb326-review/legacy.txt
diff -u native/evidence/rb3-reach/legacy-hashes.txt /tmp/rb326-review/legacy.txt
python audit/native/rb325/run_core.py --seed 1 --out /tmp/rb326-review/core-seed1.json
python -m native.rulebook.individuation_run --compatibility --seed 1 --out /tmp/rb326-review/off-seed1.json
```

## Scenario and continuation

```bash
python -m native.oracle run --scene native/oracle/scenes/carrier_cut.json \
  --force A:0 carrier 0 --stop possession --out /tmp/rb326-review/scene.json
python -m native.oracle run --scene native/oracle/scenes/late_receiver.json \
  --stop pass_caught --max-ms 3000 --out /tmp/rb326-review/late.json
python -m native.oracle prepare --scene native/oracle/scenes/carrier_cut.json \
  --athlete A:0 --stage carrier --snapshot /tmp/rb326-review/carrier.snapshot.gz
python -m native.oracle grade /tmp/rb326-review/carrier.snapshot.gz \
  --stage carrier --samples 20 --out /tmp/rb326-review/carrier-options.json
python -m native.oracle verify-replay --mode core --directory /tmp/rb326-review/snapshots \
  --out /tmp/rb326-review/resume-core.json
python -m native.oracle verify-replay --mode off --directory /tmp/rb326-review/snapshots \
  --out /tmp/rb326-review/resume-off.json
```

The graduation tests compare uninterrupted and fresh-process final fingerprints from steps 4,000, 14,000 and 25,000. Use `--steps` for other landmarks. CORE uses the canonical real bodies with neutral ratings. Off uses the unmodified canonical roster. Snapshot files use Python serialization for trusted local captures. The scene input uses JSON.

An authored scene takes a roster preset or two sets of roster rows. Supply clocks, score and ends under `state`, positions, velocities and headings under `players`, and the remaining Ball fields under `ball`. A dead-ball scene can specify a restart and its procedural rule record. The omitted fields use the seeded build's defaults. The authored example lets the carrier infer a defender at x=71 with truth at x=73. The late-receiver example starts at delivery of a flight with 0.30 seconds of nominal horizontal travel. Initial authored track changes apply to the named observer's delivered frame.

Full snapshots retain the live graph, historical events, transport state, random streams and trace bytes. The smaller drill snapshots retain active rule witnesses at their original event indices and start a branch trace tied to the original prefix fingerprint. Use the full format for exact match continuation. A prepared snapshot retains the already delivered view and starts from that specific actor's turn within the tick.

## Drill and Gauge

```bash
for seed in 1 2 3; do
  python -m native.oracle.mine --seed "$seed" --directory /tmp/rb326-review/mined
done
python -m native.oracle.drill --mined /tmp/rb326-review/mined \
  --out /tmp/rb326-review/drill --artifact /tmp/rb326-review/drill-v0.json --workers 2
```

Keep simultaneous matches and rollout workers at two or fewer. The miner emits compressed per-seed decision logs with the delivered beliefs, option values, owners and selected actions. It samples carrier moments by distance and pressure, and samples the three commitment stages by a stable hash of the match and decision identity. Each branch has a deterministic seed derived from the moment, option index and replicate. The rollout output keeps scores, results, event counts, fingerprints and CPU cost for every replicate.

Possession horizons end at a score, turnover or period end. The sub-agent horizons follow the action witness through control, a ruling, invalidated motor commitment or ended hold. Points are scoreboard changes at the stopping tick. The raw reason counts include any administrative time caps. The fitted tables use all labels from the training moments, with seed 3 reserved as a match-level holdout. The comparison baseline is the pooled training mean. Binary-table mean squared errors are Brier scores.

The Gauge uses the same entropy at all three Playmaking levels. Belief regret is against the athlete's hand-set estimate before the choice error. The summary also records regret against the estimate after applying the error. Maximizing that last estimate gives zero regret by construction. The artifact and every other ORACLE input stay in the offline package.
