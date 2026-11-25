#!/usr/bin/env bash
set -euo pipefail
book=$1
out=$2
pyrun=${PYTHON:-python}
mkdir -p "$out"
export TMPDIR
TMPDIR=$(mktemp -d /dev/shm/rb332-tests.XXXXXX)
trap 'rmdir "$TMPDIR" 2>/dev/null || true' EXIT
"$pyrun" -m pytest -q b1 native 2>&1 | tee "$out/pytest.txt"
"$pyrun" -m native.rulebook.scoring_audit --legacy > "$out/legacy.txt"
diff -u native/evidence/rb3-reach/legacy-hashes.txt "$out/legacy.txt"
"$pyrun" -m audit.native.rb332.gates --workbook "$book" --out "$out"
