# Handoff packet HP-001 / T1 — evidence artifacts and canonicalization script (Claude → Codex)
Source revision: baseline commit `2abe497ca82588cb2d8c871a7aab61daaae95c12` (= `main`, tag `baseline-p4-2026-11-05`). Evidence branch: `claude/t1-b0-evidence` (head 2ff61b3 + this packet). Fixture restoration: separate branch `claude/restore-fixtures` (one commit on 2abe497, awaiting DreLen's merge).
DreLen's decisions (2026-11-05): B0-P4-DEFAULT preserved as executed (KEEPER_STEP_FRAC=0.5, THROW_SPLIT=1, RULES_V03=0; kicking present = documented historical canon discrepancy); B1 must eliminate kicking, implementation decided in the rules/decision-ownership audit; **overall T1 stays open until your canonical hash comparison and your remaining repository verification are reconciled**; T2 not started.

## What you are asked to do (T1 closure)
1. **Byte-level comparison in your environment.** Check out `claude/t1-b0-evidence` (or copy `tools/t1_capture.py` onto a clean 2abe497 checkout). From the repo root, with no PRISM/HAND/CATCH environment overrides, for seeds 1–5 and modes `short` and `reg`:
   `python3 tools/t1_capture.py <seed> <short|reg> <out.json>` — one fresh process per game; compare `log_sha256`, `result_sha256`, `score`, `n_events` with `baseline/b0_claude_env/MANIFEST.json` (`runs[]`). Record Python/NumPy versions.
2. **If you instead hash your own serialized logs:** `python3 tools/t1_canon_hash.py --selftest` must print `OK` (same digest on every platform), then `python3 tools/t1_canon_hash.py <log.json|log.jsonl>`. Verified here: the seed-1 short log serialized with `json.dump(..., default=str)` and re-hashed gives 0cc709124037… = manifest. Caveat in the script header: the serialization must preserve values (a writer that turns 5.0 into 5 or rounds floats changes the hash).
3. **Close your 54-file gap:** compare your 373 verified blob hashes against `baseline/b0_claude_env/commit_tree_2abe497.txt` (`git ls-tree -r 2abe497`, 427 entries), or use a real git checkout.
4. **Report discrepancies, do not repair them.** If hashes differ across environments, record which seeds/modes, the first differing event, and the Python/NumPy versions; do not change the simulation.

## Artifact index (paths relative to repo root on `claude/t1-b0-evidence`)
| Artifact | Purpose |
|---|---|
| `baseline/b0_claude_env/T1_EVIDENCE_PACKET.md` | first packet, sections 1–9 incl. cross-check with your REPORT.md and the THROW_SPLIT erratum |
| `baseline/b0_claude_env/T1_COMPLETION_ADDENDUM.md` | conditional-acceptance response: inventory, fixtures, kicking finding, status table |
| `baseline/b0_claude_env/MANIFEST.json` | environment, commands, source hashes, all 20 runs with log/result hashes |
| `baseline/b0_claude_env/runs/*.json` | one record per game (flags, scores, event counts, hashes, wall time) |
| `baseline/b0_claude_env/source_patch.diff` | the three effective source-patch lines (same content as `b0_effective_patches.txt`) |
| `baseline/b0_claude_env/runtime_install_inventory.txt`, `inventory/pristine.json`, `inventory/installed.json` | measured wrapper inventory (30 wrapped core attributes with chains) and the 86 environment keys read |
| `baseline/b0_claude_env/tests2/*.log`, `tests2_summary.txt` | the 17 test files run as scripts |
| `baseline/b0_claude_env/commit_tree_2abe497.txt` | full tree with blob hashes |
| `baseline/b0_claude_env/env_flags_read.txt`, `env_flags_nonzero_defaults.txt` | static flag lists (superseded by the measured reads for B0 purposes) |
| `tools/t1_capture.py` | single-game capture + canonical hash (authoritative) |
| `tools/t1_canon_hash.py` | standalone canonicaliser with self-test (this packet) |
| `tools/t1_runtime_inventory.py`, `tools/t1_run_tests.py`, `tools/t1_reg.sh`, `tools/t1_tests2.sh` | the scripts used |

## Known facts you need (confirmed by Claude)
- Short seed-1 expected: score 7–3, 3789 events, log sha256 prefix 0cc709124037. Regulation seed-1: 49–50, 27323 events, prefix 9194161ec278 (full hashes in MANIFEST).
- Scores already agree between your REPORT.md (Py 3.12.14/NumPy 2.3.5) and mine (Py 3.13.16/NumPy 2.5.3) for all 10 runs; byte equality is what remains.
- The three restored fixtures (hashes in `baseline/FIXTURE_PROVENANCE.md` on `claude/restore-fixtures`) make the three previously failing test files pass in a throwaway copy; rerun them on that branch and report.

## Out of scope
T2–T6, kicking/rules v0.3 audit, any behaviour change, recalibration, native rewrite.
