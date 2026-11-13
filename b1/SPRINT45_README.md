# PRISM SPRINT-45 Round 2 (experimental, nothing ACCEPTED)

```
pip install scipy numpy pytest
python -m b1.match_run --seed 1 --out /tmp/match_seed1.json     # full match, ruleset 1.0.2, P-1 = 500 ms
python -m b1.match_run --seed 1 --p1-ms 250 --max-ms 60000      # P-1 threshold variant
python -m b1.match_run --scenario g1 --seed 1                   # carrier / receiver / defender
python3 -m pytest -q b1                                         # all tests (Base A, Round 1, Round 2, possession)
python -m b1.sprint45_evidence 2 3 4 && python -m b1.sprint45_reports
```

New in Round 2: `b1/possession.py` (rules-state layer), `b1/test_possession.py`, `b1/test_sprint45.py`,
`b1/sprint45/` (canon notes, review findings), `b1/evidence_sprint45/`. Reports: `SPRINT45_*.md` at the root.
