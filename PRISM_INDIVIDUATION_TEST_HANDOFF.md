# PRISM individuation independent test handoff

- Branch `codex/rb-3-23-prism-individuation`
- Exact engine and developer-test commit `32ef9dad14ee9407e32d4214edd541867c9b7a6e`
- Authorized parent `eb30f605f24b906777b88d6cb3a552b3584639ef`
- Read-only workbook source Git commit `81f92e3a90f927dcf725191c664dcc01a5996e43`, sheet `All 712 Players`

Use the repository's Python 3.12 environment with the dependencies in `native/requirements.txt`. The runner accepts `--workbook PATH` when the workbook is supplied separately. The canonical Git object is required for the existing NBL fixture tests.

From the repository root:

```bash
git switch --detach 32ef9dad14ee9407e32d4214edd541867c9b7a6e
python -m pytest -q b1 native
python -m pytest -q native/rulebook/test_individuation.py
python -m native.rulebook.scoring_audit --legacy > /tmp/rb323-legacy.txt
diff -u native/evidence/rb3-reach/legacy-hashes.txt /tmp/rb323-legacy.txt
python -m native.rulebook.individuation_run --compatibility --seed 1 --out /tmp/rb323-compat.json
python -m native.rulebook.individuation_run --seed 1 --out /tmp/rb323-a.json
python -m native.rulebook.individuation_run --seed 1 --out /tmp/rb323-b.json
python - <<'PY'
import json
a, b = [json.load(open(file)) for file in ('/tmp/rb323-a.json', '/tmp/rb323-b.json')]
assert a['status'] == b['status'] == 'final'
for key in ('trace_hash', 'state_hash', 'config_digest'):
    assert a[key] == b[key]
    print(key, a[key])
PY
```

Compatibility real seed 1 should reproduce trace `44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072` and state `046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d`. Compare final status as well as hashes. The same-machine bounded benchmark runner is at `audit/native/rb323/benchmark.py` on the evidence commit.

The tests separate individual rating mechanisms from full-match repeatability. The match run uses the canonical workbook's available ratings and declared fallbacks. Independently authored draft ratings are absent from that workbook. The paired tests inject one rating at a time. Suitable independent follow-up is to probe the mechanisms against second scenarios, especially reaction with dense restarts and fatigue late in a period, and compare how often an option-value change becomes a different selected action.
