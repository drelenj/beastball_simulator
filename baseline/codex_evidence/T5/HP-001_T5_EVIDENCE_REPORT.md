# HP-001 T5 — Experiment Runner and Telemetry Infrastructure

Status: complete; awaiting T5 review. No T6 or native work begun.

Baseline: `B0-P4-DEFAULT`, accepted source commit `2abe497ca82588cb2d8c871a7aab61daaae95c12`.

## Executive finding

T5 delivers a deterministic, headless, fresh-process experiment runner; independent and paired resumable batches; bounded termination and recovery; JSONL event/decision/step telemetry; CSV/JSON statistical summaries; configuration/environment provenance; behavior-neutral B0 verification; and a read-only reproduction of the seed-2 keeper reverse-flight pathology.

The historical source snapshot and T1–T4 evidence were not edited. The runner is a separate directory and does not patch engine behavior.

## Requirements disposition

| # | Requirement | Disposition and evidence |
|---:|---|---|
| 1 | Explicit headless configuration, seeds, flags, streams, provenance | Implemented in `common.py:90-166`, `run_match.py:178-207`, run manifests, and `schemas/experiment.schema.json` |
| 2 | Independent/paired, bounded, resumable, recovery | `run_batch.py:22-205`; wall bounds in `run_match.py:251-339`; failure demo records error+timeout and second invocation launches 0 |
| 3 | JSONL, CSV, JSON | Four JSONL channels per run, JSON manifests/state/statistics, `runs.csv`, `arm_summary.csv`, and `comparisons.csv` |
| 4 | Ownership, options, intentions, outcomes, random evidence | `run_match.py:64-161`; full B0 sample contains 8,233 decision/target/outcome rows; raw draws explicitly unavailable, state checkpoints retained |
| 5 | Correct completion/forfeit/timeout/error distinctions | `common.py:198-232`; completed regulation, short/overtime, forfeit, timeout, and error all represented in tests/raw samples |
| 6 | Confidence intervals and denominators | `analyze_batch.py:17-63, 118-217`; t, Welch, paired-t, Wilson; censored/forfeit/eligible counts explicit |
| 7 | Instrumentation neutrality | Short control/full pair passes every score/result/event/hash/RNG/schedule check; regulation event telemetry exactly matches accepted T1 seed 1 |
| 8 | Preserve T1–T4; disclose path differences | Preservation hashes below; `EXECUTION_PATH_AND_LIMITS.md` and every run manifest disclose differences |
| 9 | Read-only keeper diagnostic | `common.py:272-306`; 70 s bounded seed-2 capture reproduces T4 critical state and stack without algorithm/clock changes |
| 10 | IA-001 and C-7-ready schema only | Reserved fields in `decision.schema.json`; every record says `not_implemented_t5` |
| 11 | Commands, tests, samples, raw outputs, docs, packet | Included in `README.md`, this report, `schemas/`, `examples/`, `tests/`, and `sample_runs/` |

## Configuration and isolation

Each run declares an immutable run ID, experiment/arm ID, integer seed, duration mode, feature flags, disabled systems, ball shape, telemetry level, wall/engine bounds, and diagnostic switches. Before importing the engine, the runner removes every controlled Pocket/PRISM/rule flag from the inherited environment and applies only the declared allow-listed map. Unknown flags and nonhistorical random-stream overrides are rejected.

The batch runner materializes a resolved seed × arm plan, writes every run config, launches a fresh Python process with `PYTHONHASHSEED=0`, and commits batch state after each subprocess. Existing terminal manifests are skipped. Explicit retry categories archive the prior run under `attempts/` before relaunch.

Environment captured by the reference runs:

| Field | Value |
|---|---|
| Python | CPython 3.12.14 |
| Platform | Linux 6.18.57 x86_64, glibc 2.41 |
| Logical CPUs visible | 9 |
| CPU affinity | 0–8 |
| Hash seed | `PYTHONHASHSEED=0` |
| Engine seed policy | config seed; derived streams remain historical |
| Source provenance | SHA-256 for 18 engine/config/roster files in every successful manifest |

## Behavior-neutrality evidence

### Full telemetry versus control, B0 short seed 1

| Invariant | Control | Full telemetry | Equal |
|---|---:|---:|:---:|
| Score | A 7–3 B | A 7–3 B | yes |
| Result | A, overtime | A, overtime | yes |
| Events | 3,789 | 3,789 | yes |
| Canonical event hash | `0cc709124037857276e6f86091047269e791ca0b85e86abb572ee6a6635465cf` | same | yes |
| Completed outer steps | 5,277 | 5,277 | yes |
| Execution-schedule hash | `9c0272b3a6a2682c88730cf502b09f79ccd2f7e94c2e69e04a11d4268bbd1742` | same | yes |
| Simulation RNG transitions | `d9466face5d23694c55b869acfd5ed19ee340925ad4047e3e3fc32b184b962e3` | same | yes |
| Final simulation RNG bundle | `1e5ec00dfce57ceef17deac211aeb8b0b8b301958417933d745bb13ab60a44ad` | same | yes |
| Python-global changed steps | 0 | 0 | yes |

The instrumented run also agrees with the accepted T1 short seed-1 fixture for score, event count, and canonical event hash. Its raw payload contains 3,789 event rows, 5,277 step rows, and 8,233 decision/target/outcome rows.

Python's global RNG has a different absolute hash across fresh interpreters because the standard library auto-seeds it from process entropy. The accepted source does not call it. T5 therefore compares its zero-consumption signature, while deterministic engine-owned streams are compared by exact state and transition hash.

### Regulation preservation, B0 seed 1

The regulation events run completed normally in 177.790 wall seconds and exactly matches the accepted T1 fixture:

| Invariant | Observed / accepted |
|---|---|
| Classification | `completed_regulation` |
| Score | A 49–50 B |
| Events | 27,323 |
| Canonical hash | `9194161ec278b5293a31eabb75e34ecf0852ceaf0446f470feffe9d077e61079` |

This run is the only T5 sample eligible for regulation-match throughput. Short, overtime, forfeit, timeout, and error cases are not counted as equivalent regulation matches.

## Telemetry findings and boundaries

The full B0 sample records historical `controller_decision` option values such as `carry`, `continue`, `pass`, and `shoot`; the selected intention; controller and motor ownership; effective movement-target maps; and correlated outcome events. The observer never reevaluates options. When internal data are not emitted by the historical runtime, the field is explicitly `null` or labeled unavailable.

Available random evidence is state-based. Engine/PRISM RNG objects expose `getstate`, so T5 hashes state without consuming a draw. Historical decision methods do not expose individual raw draws; `available_draws` is empty rather than inferred.

IA-001 and C-7 fields are extension points only. T5 preserves the T2 information-access findings as future B1 inputs and does not enforce or migrate them.

## Statistical demonstrations

### Independent B0 short seeds 1–3

All three runs completed the configured short match: two in short regulation and one in overtime. They are ordinary configured completions, not regulation-throughput observations.

| Metric | n / denominator | Estimate | 95% CI |
|---|---:|---:|---:|
| Configured-match completion | 3 / 3 planned | 1.000 | Wilson [0.4385, 1.0000] |
| Total score, configured completions | n=3 | 8.000 | t [3.6973, 12.3027] |
| Event count, configured completions | n=3 | 3,248.667 | t [2,079.484, 4,417.850] |
| Completed regulation | 0 / 3 planned | 0.000 | Wilson [~0, 0.5615] |
| Regulation matches/hour | 0 eligible | undefined | undefined |

### Paired B0 versus full PRISM, short seed 1

B0 completed in overtime; full PRISM ended by forfeit at 19.237 live seconds, A 5–0 B, 214 events. The comparison correctly reports:

- planned pairs: 1;
- eligible completed-regulation pairs: 0;
- pairs excluded for forfeit: 1;
- censored pairs: 0;
- score/event/wall difference and confidence intervals: undefined, not fabricated from the forfeit.

These demonstrations validate the estimand logic; they are not PRISM correctness or performance conclusions.

## Failure recovery and resume

`failure_recovery_demo` deliberately produced one handled pre-import error and one 0.05 s in-step timeout. Both received manifests, the batch continued, and the batch summary reported `{error: 1, timeout: 1}`. Repeating the same command reported `launched_this_invocation: 0`; both state entries became `resumed_skip`. No failed run was recast as a completion.

## Keeper reverse-flight diagnostic

Exact full-PRISM input flags: `PRISM_I=1`, `PRISM_OFFBALL=1`, `PRISM_TEAMVIEW=1`, `PRISM_FREEVIEW=1`, `PRISM_JSPLIT=1`, `CATCH_V2=1`, `PRISM_KEEPER=1`, `HAND_FIGHT=1`, `PRISM_OFFACT=1`; seed 2; short duration; 70 s wall bound.

The timeout stack landed in the unchanged path `prism_keeper_v0.step:98` → `ball_at:87` → `back:47-50`. The interrupted mid-step state reproduces the T4 critical state:

| Field | Value |
|---|---:|
| Score | A 3–7 B |
| Live clock | 120,000 ms |
| Simulation clock | 294,964 ms |
| Period / phase | 2 / opening |
| Historical engine step count | 1,361 |
| Largest tracker backlog | 9,253 samples (`A12`) |
| Largest estimated reverse work | 171,237,869 iterations at 5 ms |

The committed partial log stops at the prior completed outer boundary: `now=174964 ms`, 1,128 events, hash `b3558460bea390c920c0bb8b45a445c8a2a4f167176419b1ead5d2007a8d1dcc`. T4's 1,133-event partial capture included mid-step emissions; T5 deliberately excludes those uncommitted events and preserves the mid-step scalar/tracker state separately. This is an evidence-boundary difference, not a changed engine outcome.

No algorithm, observation semantics, sample clock, or game clock was repaired or altered.

## Validation

| Check | Result |
|---|---|
| Python compile | pass |
| Unit suite | 15/15 pass |
| Draft 2020-12 validation | 24 files, 0 failures across completed, forfeit, timeout, and error cases |
| Short B0 paired equivalence | all 10 checks pass |
| Accepted T1 short fixture | score/count/hash pass |
| Accepted T1 regulation fixture | score/count/hash pass |
| Resume demonstration | second invocation launched 0 runs |

## Preserved evidence hashes

Recomputed after T5 implementation:

| Accepted artifact | SHA-256 |
|---|---|
| `T1_CLOSURE_REPORT.md` | `687cbefd47e233d123d52eaa2fccd4a1f2e207ed717786dc3f2dde143ef11eb6` |
| `HP-001_T2_EVIDENCE_REPORT.md` | `fd2cf9eeba67081d8c087123ee1dd6bb2aa9a7153b9fb07a71fce35a9c160eee` |
| `HP-001_T2_EVIDENCE_PACKET.zip` | `a40744b655f5783865434ba1f62da1162fde4ce1404514611a2035339d6b4982` |
| T3 accepted report | `aa8efd9a20942803c18c6d8302b04c92fd77509177163017a5861c8b27adb6b7` |
| `HP-001_T3_EVIDENCE_PACKET.zip` | `8d9f93436eec5ef19ba6562ec3eb09d9f37ef1f3e7dc8516c92ddb72d09ee61c` |
| `HP-001_T4_EVIDENCE_PACKET.zip` | `634ac16eb6a5c2e4cfa806bc8bab721e510a9c3725ce13759ab64e9630380b82` |

## Ambiguities and limits requiring later-stage decisions

1. A forfeit is terminal but is neither an ordinary completion nor censoring; downstream analyses must choose an explicit competing-risk estimand if forfeits themselves become outcomes of interest.
2. The strict throughput policy counts only `completed_regulation`; overtime/shootout inclusion would be a future protocol change, not silently inferred.
3. Internal option menus and raw draws cannot be captured completely without changing historical methods. T5 records only emitted values, returned targets, and state checkpoints.
4. Outcome correlation is latest-same-athlete, not a verified causal chain.
5. `SIGALRM` bounds Python execution on this environment; portability to Windows/native workers requires a process-level timeout implementation.
6. The experiment pathway mirrors construction and stepping but omits original expanded-measurement postprocessing. Engine summary and raw events are retained; consumers needing legacy expanded fields must compute them outside the timed/behavioral run.
7. T5 validates infrastructure, not PRISM correctness, physical magnitude, information-access compliance, formation-free behavior, or native parity.

## Conclusion

All T5 deliverables are present and behavior preservation is demonstrated at both accepted seed-1 short and regulation baselines. The packet stops here for review. T6 is not started.
