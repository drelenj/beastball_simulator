# RB-3.33 seed-1 ladder

Use CPython 3.13.5 with numpy, openpyxl and pytest. From the repository root, export the exact input workbook and run a single arm with the following commands.

```bash
book=/tmp/rb333-ratings.xlsx
git show 'b284e822fa2f23c820987c795a2d780f16334fc3:audit/arcade/ratings/NBL_2026-27_Opening_Night_Rosters_ratings-0.4_overall-trials.xlsx' > "$book"
python3.13 -m audit.native.rb333.match A5 "$book" /tmp/A5.json.gz
```

The historical combined arm is named RB332. The fast cadence arm is named A5prime. Every match uses planned rotation at 0.58, explicit ratings, hand-set values and the same 22-player squads. The command also accepts a pair index and seed. The named JSON box score is the `box` field of each compressed result, and the ready-to-write CSV is its `box_csv` field.

Rebuild and compare the tables without running a match.

```bash
python3.13 -m audit.native.rb333.tables audit/native/rb333/evidence /tmp/rb333-tables.md
cmp /tmp/rb333-tables.md audit/native/rb333/TABLES.md
```

The separate soak entry point is `audit/native/rb333/soak.sh CONFIG`. It accepts WORKBOOK, OUT and PYTHON environment overrides. By default it extracts the pinned workbook and uses one simulation process. An operating-system file lock prevents duplicate workers on the same output path. The writer atomically renames each completed match and the runner skips completed files on resume.

## Measurement definitions

- Counts divide the whole-game number by two. Percentages divide pooled event totals. Scores and signed margins retain their team attribution. No sampling error is estimated from one game.
- Turnovers follow the existing possession ledger, including its score-restart category. A dropped targeted pass is an observable contact followed by failure to secure. The ledger can subsequently award the ball to either team. Deflections going out are a subset of the boundary events. These event diagnostics can overlap the turnover categories.
- A boundary with the carrier's body crossing is categorized as body. All other boundaries, including the held ball reaching a line before its carrier, go in the ball category. The goal-mouth check uses the end line, half-disc and whole-ball radius when height is recorded. A crossing outside the mouth width rules out a goal at every height. Ambiguous records without height get their own count.
- Pass completion uses the existing ledger, including snaps and tosses. The Catching groups use the intended receiver's explicit roster rating, targeted receptions and targeted drops. The speed and miss distributions use recorded targeted release vectors and aims. Lateral miss is the perpendicular error at the intended range implied by the launch yaw. Interception, deflection and subsequent receiver movement are excluded from that geometric measurement.
- A commitment episode starts at an admitted takedown. Adjacent renewals against the same target form one episode. Driving-hold success uses the narrower witnessed-engagement denominator. The strength split reads the *target's roster Strength* through the target ID. It describes the carrier only where the target really held the ball. It is neither the tackler's Strength nor fatigue-adjusted force.
- Keeper reach uses the existing physical envelope. No-commit and touch-without-save counts apply to reachable on-target shots. Unset incidence uses the release-time speed against the same physical set threshold. A projection mismatch is excluded from the reachable-share denominator.
- CPU time covers creation, box-ledger and diagnostic observation, and play to the final whistle. Offline joins and compression are excluded. A5 and A5prime sample the running Python frame every 50 ms of process CPU time.
