#!/usr/bin/env bash
# One lane of the A6 soak. Usage: bash audit/native/a6soak/soak.sh LANE   (LANE = 0 or 1)
# Safe to stop and restart: finished games are skipped.
set -euo pipefail
cd "$(dirname "$0")/../../.."
lane=${1:?give lane 0 or 1}
out=audit/native/a6soak
book=$out/ratings-0.4.xlsx
if [[ ! -s "$book" ]]; then
  git show 'b284e822fa2f23c820987c795a2d780f16334fc3:audit/arcade/ratings/NBL_2026-27_Opening_Night_Rosters_ratings-0.4_overall-trials.xlsx' > "$book.tmp"
  mv "$book.tmp" "$book"
fi
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
exec "${PYTHON:-python3.13}" -m audit.native.a6soak.run play "$out" "$book" "$lane" 2 2>&1 | tee -a "$out/lane$lane.log"
