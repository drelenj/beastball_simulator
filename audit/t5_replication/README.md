# T5 equivalence replication (Claude environment, 2026-11-08)
Ran Codex's unmodified T5 `run_match.py` (control: telemetry none; instrumented: telemetry full) for B0 short seed 1 against the accepted source snapshot, then `verify_equivalence.py`.
Environment: CPython 3.13.18 (Codex reference: 3.12.14). Result: all 10 equivalence checks true. Event hash, execution-schedule hash, simulation-RNG transition hash, final RNG bundle and python-global signature equal the values in Codex's T5 report (computed there under 3.12.14). Event hash also equals the accepted T1 short_s1 hash recorded from my environment (3.13.16).
Also: T5 unit suite 15/15 pass here. Not re-run: T5 regulation run, batch/resume/failure demos, schema validation, keeper diagnostic.
Limit: this replicates a pass-through observer; it does not certify any future instrumentation (see spec §8).
