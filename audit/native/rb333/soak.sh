#!/usr/bin/env bash
# Run a requested configuration on the pre-existing eight-matchup schedule.
set -euo pipefail
cd "$(dirname "$0")/../../.."
config=${1:?supply RB332, A0, A1, A2, A3, A4, A5 or A5prime}
case "$config" in RB332|A[0-5]|A5prime) ;; "A5'") config=A5prime ;; *) exit 2 ;; esac
out=${OUT:-rb333-soak}
mkdir -p "$out/$config"
# Each invocation is a single lane. Serialize invocations sharing this output
# directory so concurrent resumes cannot duplicate a case.
exec 9>"$out/.runner.lock"
flock 9
workbook=${WORKBOOK:-"$out/ratings-0.4.xlsx"}
if [[ ! -s "$workbook" ]]; then
  git show 'b284e822fa2f23c820987c795a2d780f16334fc3:audit/arcade/ratings/NBL_2026-27_Opening_Night_Rosters_ratings-0.4_overall-trials.xlsx' > "$workbook.tmp"
  mv "$workbook.tmp" "$workbook"
fi
limits=(10 5 5 2 2 2 2 2)
for pair in "${!limits[@]}"; do
  for ((seed=1; seed<=limits[pair]; seed++)); do
    file="$out/$config/$pair-$seed.json.gz"
    [[ -s "$file" ]] && continue
    "${PYTHON:-python3.13}" -m audit.native.rb333.match "$config" "$workbook" "$file" --pair "$pair" --seed "$seed"
  done
done
