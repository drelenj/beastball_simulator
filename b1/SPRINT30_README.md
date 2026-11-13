# PRISM SPRINT-30 (experimental, nothing ACCEPTED)

Primitive end-to-end B1 pipeline: every active athlete (10 field + Keeper + Archer per side) decides from its own
delayed, noisy, FOV-limited PRISM perception; intents become motor commands executed by the frozen B0 physics.

```
pip install scipy numpy
python -m b1.match_run --seed 1 --out /tmp/match_seed1.json     # one full match (about 40 s wall)
python -m b1.match_run --scenario g1 --seed 1                   # carrier / receiver / defender (G1)
python -m b1.match_run --scenario g1_close --seed 3             # defender starts on the lane
python -m unittest b1.test_sprint -v                            # boundary, ownership, determinism
python -m unittest b1.test_m1                                   # existing M1 tests
python -m b1.sprint_evidence 2 3 4                              # regenerate evidence + SPRINT30_TEST_REPORT.md
```

Files: `b1/cognition.py` (pure decisions), `b1/matchport.py` (sensors, ingress, motor hooks, loop),
`b1/registry.py` (PRIMITIVE registry), `b1/test_sprint.py`, `b1/evidence_sprint30/`.
Reports: `SPRINT30_*.md` at the repository root. Start with `SPRINT30_OWNER_BRIEFING.md`.
