# RB-1: blocked integration checkpoint

Base:a1b131379845322bbc9970ad667a6d68dec10dd7, Native v0/2. No FAB-1 dependency was awaited. Cognition and accepted files are unchanged. Rules/engine changes live here; Native substrate/run contain only explicit profile/driver hooks.

Config:RulebookConfig(), version native-rb/1, flat default; RulebookConfig(scoring='banded') enables the provisional configured bands. No environment flags.

Run conformance:`.venv/bin/python -m pytest -q b1 native`.
Bounded blocker reproduction:`.venv/bin/python -m native.rulebook.reproduce_blocker`.
Bounded serial/parallel/null replay:`.venv/bin/python -m native.rulebook.check_replay`.
CLI example for short windows:`.venv/bin/python -m native.rulebook.run --seed 1 --max-steps 1000 --out /tmp/rb-window.json`.

Do not start full RB batches while RB-BLOCK-1 persists. All full attempts must be reserved in evidence/FULL_MATCH_BUDGET.json before execution, including failed full attempts. Current use:2/20, both successful Native v0/2 preservation replays;0 full RB attempts. Tests with bounded steps or forced scenario clocks are not full matches.

The placeholder ball-centred witness for ratified5m pre-live marking and unchanged restart intents conflict. Existing snap readiness is now checked before marking admission. Minimal regression:test_boundary.py::test_restart_intent_inside_placeholder_ball_clearance. The full bounded reproduction trips the existing120s dead-progress watchdog. No artificial release/winner, weakened foul rule or external repositioning hides it.

Forced rules/scenarios and short replay are evidence of those cases only. This is not a completed RB baseline. See RB1_REPORT.md, RB1_RULE_MATRIX.json and NATIVE_RB_1_MANIFEST.json.
