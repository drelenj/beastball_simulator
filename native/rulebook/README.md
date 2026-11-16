# RB-1 integration

Engine/rules source freeze:881d212 on codex/rulebook-1, based on Native v0/2 a1b1313. Accepted files, frozen B0 and cognition are unchanged. Rules live here; the earlier Native substrate/driver profile hooks remain isolated.

The owner revoked the pre-live5m marking foul on2026-11-15. It has been removed without replacement. Keeper-zone defender marking remains5m. Existing readiness ordering and dead-progress watchdog remain. Repeated dead-ball fouls receive procedural correction/warning without repeat retakes/exclusions.

Config:RulebookConfig(), native-rb/1, flat default. RulebookConfig(scoring='banded') enables provisional configured bands; no environment flags.

Commands:
- `.venv/bin/python -m pytest -q b1 native`
- `.venv/bin/python -m native.rulebook.reproduce_blocker` verifies progress past the historical blocker in4000 steps, not a full match. It writes to the operating-system temporary directory unless `--out` is supplied.
- `.venv/bin/python -m native.rulebook.check_replay` checks100-step serial/parallel/M2-absent replay. It writes to the operating-system temporary directory unless `--out` is supplied.
- `.venv/bin/python -m native.rulebook.run --seed 2 --max-steps 1000 --out /tmp/rb-window.json`

All full-match attempts must be reserved in evidence/FULL_MATCH_BUDGET.json before execution. The budget includes failed/stopped attempts and conservatively counts every batch reservation. Final validation is seeds2,6,7,8,9,10 plus a serial/parallel seed2 replay. Do not start more batches after the required evidence is complete. See RB1_REPORT.md and NATIVE_RB_1_MANIFEST.json for final results and exact seed history; historical failed logs are retained.

Strike panels remain an explicitly permitted cylinder-height placeholder; no inner/outer-thigh anatomy is claimed. Injury source is a forced hook only. No autonomous review policy, message content or plan content is authored.
