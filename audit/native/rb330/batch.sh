#!/usr/bin/env bash
set -euo pipefail
book=$1
out=$2
scale=${3:-.52}
pyrun=${PYTHON:-python}
for pair in {0..7}; do
    case "$pair" in
        0) games=10 ;;
        1|2) games=5 ;;
        *) games=2 ;;
    esac
    for ((seed=1; seed<=games; seed++)); do
        path="$out/runs/$pair-$seed.json.gz"
        mkdir -p "$out/runs"
        [[ ! -f "$path" ]] || continue
        mkdir "$path.lock" 2>/dev/null || continue
        trap 'rmdir "$path.lock"' EXIT
        args=()
        if [[ "$pair:$seed" == 0:1 ]]; then
            args+=(--box "$out/boxes/planned-seed01")
        fi
        "$pyrun" -m audit.native.rb330.match --workbook "$book" --scale "$scale" \
            --pair "$pair" --seed "$seed" --out "$path" "${args[@]}"
        rmdir "$path.lock"
        trap - EXIT
    done
done
