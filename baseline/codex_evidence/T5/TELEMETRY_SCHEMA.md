# T5 Telemetry and Statistical Contract

Schema version: `hp001-t5-v1`.

## Per-run artifacts

| Artifact | Record | Meaning |
|---|---|---|
| `events.jsonl` | `simulation_event` | Lossless wrapper around each historical engine event |
| `decisions.jsonl` | `decision` | Historical `controller_decision`: owner, option/value map, selected intention/target, context, and RNG-state evidence |
| `decisions.jsonl` | `target_selection` | Effective target map returned by the final installed `Policy.targets` chain |
| `decisions.jsonl` | `execution_outcome` | Physical/result event correlated to the latest same-athlete controller decision when available |
| `steps.jsonl` | `execution_step` | Before/after state, new event IDs, and random-stream state hashes for a completed outer `Match.step` |
| `keeper_diagnostic.jsonl` | `keeper_reverse_flight_diagnostic` | Read-only keeper tracker backlog and estimated 5 ms reverse integrations |
| `manifest.json` | `run_manifest` | Configuration, effective flags, provenance, classification, outcome hashes, timing, artifact hashes, and determinism hashes |

JSONL is UTF-8, one compact JSON object per line. Writers use `.partial` files, flush every record, `fsync` at finalization, and atomically rename the completed file.

## Decision semantics

- `decision_owner` identifies the historical controller or the effective policy wrapper chain.
- `information_provider` distinguishes the historical true-state path from an installed PRISM view chain.
- `motor_owner` and `physical_resolution_owner` remain the legacy match execution/Pocket 4 physics path.
- `option_set` and `evaluated_values` come only from values already emitted by `controller_decision` events. The observer does not rerun an option evaluator.
- `target_selection` records the returned effective map. Internal candidate menus are `null` because exposing them would require a behavioral patch.
- `execution_outcome.causal_decision_id` is a correlation to the latest same-athlete controller event, not proof of exclusive causation.
- Historical methods do not expose raw random draws. `available_draws` is therefore empty and explicitly labeled; state hashes before/after steps provide non-consuming stream evidence.

## Random-stream semantics

Engine streams and installed PRISM streams are state-hashed without calling a draw method. The transition hash covers deterministic simulation-owned engine streams at every completed outer step. Final manifests also hash installed PRISM stream states when present.

Python's process-global `random` object auto-seeds nondeterministically at interpreter startup and is not called by the accepted source snapshot. Its absolute state is reported separately; equivalence uses a per-step changed/not-changed signature. Both B0 equivalence runs recorded zero changed steps.

## Termination classes

| Category | Completed configured match | Regulation throughput | Censored | Early termination |
|---|---:|---:|---:|---:|
| `completed_regulation` | yes | yes | no | no |
| `completed_short_regulation` | yes | no | no | no |
| `completed_overtime` | yes | only when configuration is canonical regulation and the policy elects to include it; T5 currently requires category `completed_regulation` | no | no |
| `completed_shootout` | yes | no under current strict estimand | no | no |
| `forfeit` | no | no | no | yes |
| `timeout` | no | no | yes | no |
| `error` | no | no | yes | no |
| `engine_watchdog` / `other_incomplete` | no | no | yes | no |

The strict T5 throughput estimand counts only `completed_regulation`. Forfeits are competing early terminations, not censored matches and not completed matches.

## Confidence intervals and denominators

- Continuous one-arm metrics: two-sided 95% Student-t interval; undefined for `n < 2`.
- Completion proportions: 95% Wilson interval using all planned runs as denominator.
- Paired comparisons: paired-t interval over pairs in which both arms completed regulation.
- Independent comparisons: Welch interval over completed-regulation observations in each arm.
- `n_pairs_planned`, `n_pairs_eligible`, `n_pairs_excluded_forfeit`, and `n_pairs_censored` are emitted in JSON and CSV.
- Configured-duration ordinary completions are summarized separately and never labeled regulation throughput.

## IA-001 and C-7 extension points

Every decision/target record reserves `information_access`, `belief_provenance`, `communication`, and `archer_cognition`. T5 sets `ia001_status` and `c7_full_prism_archer_cognition` to `not_implemented_t5`; it does not enforce a visibility contract or add full PRISM Archer cognition.
