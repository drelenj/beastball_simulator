# RB-3.29 evidence and reproduction

Use the repository Python environment with openpyxl. Run the commands from the repository root. The ratings 0.4 workbook is pinned to `b284e822fa2f23c820987c795a2d780f16334fc3` and has SHA-256 `47b48af7a19035428d517582370fa1782b542980c783edf3dfb20619cf437fba`.

```bash
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
work=$(mktemp -d)
book='audit/arcade/ratings/NBL_2026-27_Opening_Night_Rosters_ratings-0.4_overall-trials.xlsx'
git show "b284e822fa2f23c820987c795a2d780f16334fc3:$book" > "$work/ratings.xlsx"
bash audit/native/rb329/batch.sh "$work/ratings.xlsx" "$work"
python audit/native/rb329/analysis.py "$work" --out "$work/summary"
```

At most two batch lanes may share the output directory. Cases are claimed in restart-safe output directories, with a per-match temporary file renamed after completion. The workbook supplies explicit ratings and `OVR 0.422` selection metadata. Individuation is on and DRILL is off.

```bash
python -m native.rulebook.individuation_run --workbook "$work/ratings.xlsx" \
    --technical explicit --fatigue-rotation --rotation-rhythm R1 --seed 1 \
    --box-score "$work/box" --out "$work/result.json"
pytest -q b1 native
python -m native.rulebook.scoring_audit --legacy > "$work/legacy.txt"
diff -u native/evidence/rb3-reach/legacy-hashes.txt "$work/legacy.txt"
python -m native.rulebook.individuation_run --compatibility --seed 1 \
    --box-score "$work/compat-box" --out "$work/compat.json"
```

Use `native.oracle.matches.match_build(1)` for the neutral-real CORE identity. Enable stats on its driver before playing. The timing pairs run `audit/native/rb329/match.py --steps 1500` both with and without `--stats-off` for seeds 1 and 3 in reversed order.

## Box-score format

`native-box/1` has 44 player rows, one unassigned credit row per team and two team total rows. JSON also contains the possession and scoreboard timelines. CSV includes the three row types, with dictionaries and lists as JSON in their columns. Team-only rows retain foul-award and own-goal points, or a turnover with no identified actor. A full-goal award counts toward the engine's goal counter. Half-goal awards have their own counter.

- Playing time is sampled on the live clock for the active lineup. Stints span contiguous on-field live time, including a continuing stint on either side of an intermission. Distance integrates sampled horizontal speed over live intervals. The same samples give peak speed and time strictly above 80% of that match peak. The energy minimum is sampled at physical step boundaries.
- Shot bands use scored ball events and the engine shot-attempt ledger. A release inside 3 m classified as a carry stays with the carry attempt. Carries are observed at the same engine method that increments the carry counter. Stretch starts and committed handoffs use their dedicated engine events.
- Pass attempts include released restart passes and ordinary passes. A teammate's first secure control completes the pass, with completion by actual recipient. Initial declared targets are recorded separately. A target's unsecured touch counts as a drop once per flight. An opponent's first secure control on a pass is an interception. Passes defended count opposition touches without secure control. An assist is the last completed pass to the eventual scorer in the same attacking sequence.
- Tackles attempted count admitted tackle commands. Tackles made use adjudicated tackle counts, and takedowns use counted C3 groundings. Explicit blocks and incidental physical blocking events have separate columns. Forced loose releases and failed handoffs count as fumbles. Strips use committed strip events.
- Keeper shots faced count opposing shot releases during a Keeper's assignment. Saves credit Keeper contact on a shot that ends without a goal. Goals against by band come from recorded scoring events and the Keeper responsible at the goal. Arrow hits count geometry impacts on players. Freezes count committed freezes. Illegal arrows count Archer target fouls.
- The observer reconciles points, goals, half-goal awards, turnovers, possession count, terminal attempts and carry attempts. Its turnover counts include the engine's score-restart increments. A turnover uses the actual restart reason or a witnessed loss preceding opposing passive control. Unknown player credit stays with the team.
- A possession starts on the established RB-3.27 passive-possession marker. Scores at the instant of an ordinary change are allocated before the new possession. Points for the other team during a possession are reported separately. Team scoring rate for margin decomposition uses the full scoreboard divided by possessions, so its accounting includes those points.

## Rotation and analysis

R1 retains the original config fingerprint and physics. R2 and R3 scale sprint drain and bench recovery to 0.50 and 0.33. R2M and R3M apply those rates and require two complete possessions for an incoming athlete before an elective fatigue-driven exit or a starter return that would replace him. A partial possession already underway at admission is excluded. Required rulebook substitutions retain their existing authority.

The margin decomposition uses the identity `margin = Δpossessions × mean points per possession + Δpoints per possession × mean possessions`. It reports both variances and twice their covariance. Within and between matchup variances use game weighting. The Overall slope uses the eight matchup means with equal weight on each matchup. CSV rows carry the longest unanswered scoreboard run and three-possession streak counts per side. The latter count distinct scoring runs in each team's own possession sequence.
