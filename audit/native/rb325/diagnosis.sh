#!/usr/bin/env bash
# Run from the pinned RB-3.24 checkout. Workers are capped at two.
set -euo pipefail
if test $# -ne 3; then
    printf 'Usage: %s PYTHON RB325_AUDIT_DIR EVIDENCE_DIR\n' "$0" >&2
    exit 2
fi
if test "$(git rev-parse HEAD)" != 3edfaad1ae5d50407c16e22dceca6ad92f9d9ae6; then
    printf 'Select the pinned RB-3.24 checkout before running diagnosis.\n' >&2
    exit 2
fi
python_run=$1
audit=$2
evidence=$3
mkdir -p "$evidence"

run_case() {
    local case=$1 seed=$2 output
    output="$evidence/$case-$seed.json"
    if test -s "$output"; then return; fi
    printf 'Starting %s seed %s\n' "$case" "$seed"
    "$python_run" "$audit/ablate.py" "$case" "$seed" "$output"
}

paired_case() {
    run_case "$1" 1 & local a=$!
    run_case "$1" 3 & local b=$!
    wait "$a"
    wait "$b"
}

for layer in off on perception recognition inference strategy motor execution; do
    paired_case "$layer"
done

# Shot count is the primary endpoint. A change of at least 15% between
# paired layer totals and the off totals gets a follow-up for each hook.
follow=$("$python_run" - "$evidence" <<'PY'
import json,sys
from pathlib import Path
where=Path(sys.argv[1])
def shots(case):
    return sum(sum(json.loads((where/f'{case}-{seed}.json').read_text())['shots'].values()) for seed in (1,3))
base=shots('off')
hooks={'perception':'vision radar clarity recognition_error', 'recognition':'focus reaction',
       'inference':'instinct anticipation', 'strategy':'strategy', 'motor':'reflex_save reflex_cadence steering',
       'execution':'fatigue touch archery'}
print(' '.join(hs for layer,hs in hooks.items() if abs(shots(layer)-base)/base>=.15))
PY
)
for hook in reflex_catch without-reflex_catch $follow; do
    paired_case "$hook"
done
