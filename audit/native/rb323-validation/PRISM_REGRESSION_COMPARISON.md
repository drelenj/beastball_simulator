# RB-3.22 compatibility regression comparison

Target implementation: `d1845d022625ddaf6d0f9d5ddc5e60179c63be34`.

## Exact full-match compatibility run

Command:

```bash
PYTHONPATH=/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages ./.venv/bin/python -m native.rulebook.individuation_run --compatibility --seed 1 --out audit/native/rb323-validation/evidence/compatibility-real.json
```

Observed result: final, seed 1, score A 57–B 76, 32,528 steps, 260/260 restarts closed (100%). It exactly matches the committed RB-3.22 compatibility fixture on status, score, steps, trace hash, state hash, and config digest.

| Field | Independent run | RB-3.22 gate | Match |
|---|---|---|---|
| Trace | `44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072` | same | yes |
| State | `046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d` | same | yes |
| Config | `3d66214c927b42abf493bfe93c9d7ef85675364f54b5e6a9f245daadc4799550` | same | yes |
| Score / steps | 57–76 / 32,528 | same | yes |

Legacy profile gate: `native.rulebook.scoring_audit --legacy` emitted all six archived rows (Native v0/2, Native v0/3, Native RB/2; seeds 1 and 3) byte-identically. The raw command output is `evidence/legacy-hashes.txt`; `diff -u native/evidence/rb3-reach/legacy-hashes.txt ...` exited 0.

The complete regression suite independently passed: `pytest -q b1 native` returned 699 passed, 1 warning, and 23 subtests passed in 799.27 s. New-mode seed 1 is intentionally behavior-changing. Two independent full real runs scored 67–123, each took 34,354 steps, and closed 280/280 restarts. Both produced trace `da8e42307e99a2bab2d7925c5903664fd617d19b9b441a1ce49530ff3b1f219d`, state `291c0baff747503c522643fc0c86f57b0403365c6f1bda481c51eb8a08a20d14`, config `51362523dadf2ddcfd41a2af08b3e7da9f579f2819511df309dd00436ab44c4b`; both match the implementation's two committed seed-1 files exactly. Raw results are `evidence/individuation-real-seed1.json` and `evidence/individuation-real-seed1-repeat.json`.

The independent 1,500-step paired benchmark measured median CPU 4.843 ms/step compatibility vs 4.622 ms/step enabled; peak RSS across that process was 102,772 KiB. Perception-only cost and per-mode memory were not isolated.

The compatibility real seed confirms regulation outcome, event trace, and final state for the full fixture. An independent full compatibility control-profile run was not repeated; the implementation's control fixture remains available, and the full test suite is still running at the time this document was drafted.
