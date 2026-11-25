#!/usr/bin/env bash
set -euo pipefail
book=$1
out=$2
scale=${3:-.52}
pyrun=${PYTHON:-python}
mkdir -p "$out"
export TMPDIR
TMPDIR=$(mktemp -d /dev/shm/rb330-tests.XXXXXX)
trap 'rmdir "$TMPDIR" 2>/dev/null || true' EXIT
"$pyrun" -m pytest -q b1 native 2>&1 | tee "$out/pytest.txt"
"$pyrun" -m native.rulebook.scoring_audit --legacy > "$out/legacy.txt"
diff -u native/evidence/rb3-reach/legacy-hashes.txt "$out/legacy.txt"
for mode in compatibility core benchmark; do
    "$pyrun" -m audit.native.rb330.verify "$mode" --workbook "$book" --scale "$scale" --out "$out/$mode.json"
done
for mode in R1 R2 PLANNED; do
    "$pyrun" -m audit.native.rb330.match --workbook "$book" --variant "$mode" --scale "$scale" \
        --seed 1 --out "$out/$mode-replay.json.gz"
done
"$pyrun" -m audit.native.rb330.check identities "$out" | tee "$out/identities.txt"
