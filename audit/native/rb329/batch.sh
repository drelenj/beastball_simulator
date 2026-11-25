#!/usr/bin/env bash
# Two invocations may share an output directory.
set -euo pipefail
book=$1
out=$2
python_bin=${PYTHON:-python}
variants=(R1 R2 R3 R2M R3M)
run() {
    local variant=$1 pair=$2 seed=$3
    mkdir -p "$out/$variant"
    local leaf="$out/$variant/$pair-$seed"
    if [[ -s "$leaf.json.gz" ]] || ! mkdir "$leaf.lock" 2>/dev/null; then return; fi
    (
        trap 'rmdir "$leaf.lock"' EXIT
        files=()
        if [[ $pair == 0 && $seed == 1 ]]; then files=(--box "$out/boxes/$variant"); fi
        "$python_bin" audit/native/rb329/match.py --workbook "$book" --variant "$variant" \
            --pair "$pair" --seed "$seed" --out "$leaf.json.gz" "${files[@]}"
    )
}
for variant in "${variants[@]}"; do run "$variant" 0 1; done
for variant in "${variants[@]}"; do
    for pair in {0..7}; do
        case $pair in
            0) count=10 ;;
            1|2) count=5 ;;
            *) count=2 ;;
        esac
        for ((seed=1;seed<=count;seed++)); do run "$variant" "$pair" "$seed"; done
    done
done
