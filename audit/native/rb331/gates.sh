#!/usr/bin/env bash
set -euo pipefail
book=$1
out=$2
pyrun=${PYTHON:-python}
mkdir -p "$out"
export TMPDIR
TMPDIR=$(mktemp -d /dev/shm/rb331-tests.XXXXXX)
trap 'rmdir "$TMPDIR" 2>/dev/null || true' EXIT
"$pyrun" -m pytest -q b1 native 2>&1 | tee "$out/pytest.txt"
"$pyrun" -m native.rulebook.scoring_audit --legacy > "$out/legacy.txt"
diff -u native/evidence/rb3-reach/legacy-hashes.txt "$out/legacy.txt"
for mode in compatibility core; do
    "$pyrun" -m audit.native.rb330.verify "$mode" --out "$out/$mode.json"
done
"$pyrun" -m audit.native.rb331.match --variant R1 --workbook "$book" --seed 1 \
    --no-diagnosis --out "$out/R1-replay.json.gz"
"$pyrun" -m audit.native.rb331.benchmark run --workbook "$book" --out "$out/benchmark.json"
"$pyrun" -m audit.native.rb331.match --workbook "$book" --seed 1 --out "$out/PLANNED-replay.json.gz"
"$pyrun" -m audit.native.rb331.box_compare --workbook "$book" --out "$out/box-before-after.json"
