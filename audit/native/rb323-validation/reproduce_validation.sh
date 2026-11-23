#!/usr/bin/env bash
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
PY="${PYTHON:-./.venv/bin/python}"
SITE="${OPENPYXL_SITE_PACKAGES:-/opt/codex/runtimes/codex-primary-runtime/dependencies/python/lib/python3.12/site-packages}"
export PYTHONPATH=".${PYTHONPATH:+:${PYTHONPATH}}:${SITE}"
OUT=audit/native/rb323-validation/evidence
mkdir -p "$OUT"

"$PY" -m pytest -q native/rulebook/test_individuation.py | tee "$OUT/focused-pytest.txt"
"$PY" -m pytest -q b1 native | tee "$OUT/full-pytest.txt"
"$PY" -m native.rulebook.scoring_audit --legacy > "$OUT/legacy-hashes.txt"
diff -u native/evidence/rb3-reach/legacy-hashes.txt "$OUT/legacy-hashes.txt"
"$PY" -m native.rulebook.individuation_run --compatibility --seed 1 --out "$OUT/compatibility-real.json"
"$PY" -m native.rulebook.individuation_run --seed 1 --out "$OUT/individuation-a.json"
"$PY" -m native.rulebook.individuation_run --seed 1 --out "$OUT/individuation-b.json"
"$PY" audit/native/rb323/benchmark.py --steps 1500 --out "$OUT/benchmark.json"
"$PY" audit/native/rb323-validation/benchmark_resource.py
"$PY" audit/native/rb323-validation/build_validation_tables.py
"$PY" audit/native/rb323-validation/compare_replays.py | tee "$OUT/replay-comparison.txt"
"$PY" - <<'PY'
import json
from pathlib import Path
base = Path('audit/native/rb323-validation/evidence')
a, b = (json.loads((base / f'individuation-{name}.json').read_text()) for name in ('a', 'b'))
assert a['status'] == b['status'] == 'final'
for key in ('trace_hash', 'state_hash', 'config_digest'):
    assert a[key] == b[key], key
    print(key, a[key])
PY
