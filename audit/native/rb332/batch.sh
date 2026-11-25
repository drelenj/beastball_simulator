#!/usr/bin/env bash
set -euo pipefail
book=$1
out=$2
shift 2
pyrun=${PYTHON:-python}
for pair in {0..7}; do
    case "$pair" in
        0) games=10 ;;
        1|2) games=5 ;;
        *) games=2 ;;
    esac
    for ((seed=1; seed<=games; seed++)); do
        for arm in "$@"; do
            mkdir -p "$out/$arm"
            dest="$out/$arm/$pair-$seed.json.gz"
            [[ ! -f "$dest" ]] || continue
            mkdir "$dest.lock" 2>/dev/null || continue
            trap 'rmdir "$dest.lock"' EXIT
            if [[ -f "$dest" ]]; then
                rmdir "$dest.lock"
                trap - EXIT
                continue
            fi
            args=()
            if [[ "$pair:$seed" == 0:1 && "$arm" != archive ]]; then
                args+=(--box "$out/$arm/box-seed01")
            fi
            "$pyrun" -m audit.native.rb332.match --workbook "$book" --arm "$arm" \
                --pair "$pair" --seed "$seed" --out "$dest" "${args[@]}"
            rmdir "$dest.lock"
            trap - EXIT
        done
    done
done
