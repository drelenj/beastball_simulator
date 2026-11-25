#!/usr/bin/env bash
# Run one soak mode serially. Run at most two lanes together.
set -euo pipefail
workbook=$1
out=$2
mode=$3
python_bin=${PYTHON:-python}
flags=()
case "$mode" in
    on) flags=(--on) ;;
    off) ;;
    *) exit 2 ;;
esac
for pair in {0..5}; do
    count=2
    if [[ $pair == 0 ]]; then count=10; fi
    for ((seed=1; seed<=count; seed++)); do
        file="$out/$mode/$pair-$seed.json"
        if [[ ! -s $file ]]; then
            "$python_bin" audit/native/rb328/match.py --workbook "$workbook" --pair "$pair" \
                "${flags[@]}" --seed "$seed" --out "$file"
        fi
    done
done
