# PRISM EMERGENCE-1 (experimental, nothing ACCEPTED)

Parametrized athletes -> many paired matches -> search -> description of what emerged.
Quality is measured only by match results. Flags below may differ slightly; `--help` on each module is authoritative.

```
pip install scipy numpy pytest
python -m b1.match_run --seed 1                                    # one full 2 x 120 s match
python -m b1.emergence.harness --seeds 1 --period-s 45             # one paired proxy match (sides swapped)
python -m b1.emergence.search --minutes 15 --pop 6 --out b1/emergence/results/search   # evolutionary search
python -m b1.emergence.readout b1/emergence/results/heldout.jsonl --out /tmp/readout.md  # emergence read-out
python3 -m pytest -q b1                                            # all tests
```

## Files

| File | Purpose |
|---|---|
| `params.py` | `PolicyParams`: small bounded dataclass (option weights, risk, positioning weights, Archer eagerness). Fixed per team before a match, validated, logged in every result. |
| `positioning.py` | PRIMITIVE belief-driven positioning: scores candidate points from the athlete's own view/belief with weights from `PolicyParams`. Replaces the `home` slot-grid. |
| `harness.py` | Tournament harness: team A params vs team B params over paired seeds with sides swapped, parallel across cores, one JSONL row per match (params, seed, score, winner, trace hash, metrics). |
| `search.py` | Small-population round-robin search with mutation; held-out comparison against the baseline. |
| `metrics.py` | Compact descriptive metrics per match (width, depth, centroid-to-ball distance, passes, press distance, possession share, shots, arrows, turnovers, restarts). |
| `readout.py` | Baseline-vs-evolved comparison with paired gains/losses and exact sign-test p-values. |
| `results/` | JSONL results, search log, a few readable traces. |
| `ENGINE_CONSTRAINTS.md` | Engine-owned choices and primitives that limit what can emerge. |
| `OWN_BR_FOR_POSITIONING.md` | Boundary and ownership checks for the new code. |

The search uses a shorter proxy match (labeled in every row); proxy rankings are only indicative until confirmed on full-length matches.
Reports are `EMERGENCE1_*.md` at the repository root.
