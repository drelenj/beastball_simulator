# RB-3.30 reproduction

Run from the repository root in the Python environment used for the maintained
suite, with pytest and openpyxl installed. The pinned ratings 0.4 workbook uses
SHA-256 `47b48af7a19035428d517582370fa1782b542980c783edf3dfb20619cf437fba`.

```bash
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
work=$(mktemp -d)
book='audit/arcade/ratings/NBL_2026-27_Opening_Night_Rosters_ratings-0.4_overall-trials.xlsx'
git show "b284e822fa2f23c820987c795a2d780f16334fc3:$book" > "$work/ratings.xlsx"
bash audit/native/rb330/batch.sh "$work/ratings.xlsx" "$work"
python -m audit.native.rb330.analysis "$work"
```

Two batch lanes may share an output directory. The case locks prevent workers
from running the same matchup and seed. A successful case renames its gzip
result into place. The runner outputs the named seed-1 box score in both formats.
The match report measures player minutes on the regulation clock, and all scores
and per-possession statistics include overtime if played.

```bash
pytest -q b1 native
python -m native.rulebook.scoring_audit --legacy > "$work/legacy.txt"
diff -u native/evidence/rb3-reach/legacy-hashes.txt "$work/legacy.txt"
for mode in compatibility core benchmark; do
    python -m audit.native.rb330.verify "$mode" --workbook "$work/ratings.xlsx" --out "$work/$mode.json"
done
for variant in R1 R2 PLANNED; do
    python -m audit.native.rb330.match --variant "$variant" --workbook "$work/ratings.xlsx" \
        --seed 1 --out "$work/$variant.json.gz" --box "$work/$variant"
done
```

R1 is the historical threshold-only mode. Planned rotation is opt-in through
`--fatigue-rotation --rotation-rhythm PLANNED` in the normal runner.
The coach plan is built from the same OVR 0.422 roster order used at kickoff.
Rest windows use cumulative live time and apply at an open dead-ball restart.
The existing rulebook remains responsible for admission, injuries and exclusions.

`native-box/2` adds `player_name`, `team_name` and `legacy_position` to
the player rows and keeps the original ID and side columns. Workbook labels are
display metadata and are excluded from the roster digest and athlete views.
Synthetic rosters display their IDs and have a blank legacy position. The
existing reconciliation covers points, goals, half-goal awards, turnovers,
possessions and carry attempts.

A tackle attempt requires explicit takedown intent driving an actual carrier
hold. The observer joins the drive to the kernel's published hold start and
counts that engagement once, including a wrap later converted to a drive. A
success requires that hold to end in a grounding credited to the same defender
by the rulebook. A standalone tackle command, an uncommitted physics trial, a
containment-only hold and contact without an engagement earn no attempt credit.
The independent counted-grounding column remains available.
