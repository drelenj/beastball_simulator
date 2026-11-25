# RB-3.32 paired trials

Run in the repository Python environment with pytest and openpyxl. The workbook
is ratings 0.4 at `b284e822fa2f23c820987c795a2d780f16334fc3` with
SHA-256 `47b48af7a19035428d517582370fa1782b542980c783edf3dfb20619cf437fba`.

```bash
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
work=$(mktemp -d)
name='audit/arcade/ratings/NBL_2026-27_Opening_Night_Rosters_ratings-0.4_overall-trials.xlsx'
git show "b284e822fa2f23c820987c795a2d780f16334fc3:$name" > "$work/ratings.xlsx"
bash audit/native/rb332/gates.sh "$work/ratings.xlsx" "$work"
bash audit/native/rb332/batch.sh "$work/ratings.xlsx" "$work" \
    off pass_clearance carry_finish fresh_takedown boundary_guard combined archive
python -m audit.native.rb332.compare "$work" --out "$work/paired.json"
```

Two batch lanes can share an output directory. The maximum is two active
simulation or test processes across the full verification. Checkpoint files
are written on game completion. All trial arms use explicit ratings, eleven
planned starters, individuation, hand-set values and fatigue scale 0.58.
There is a separate legacy identity and historical forecast stratum at 0.52.
The historical stratum checks each reproduced trajectory against RB-3.31
before evaluating any lane. It does not contribute to paired effects.

## Methods

- **Pass clearance.** Predicted low-arc travel time includes release wind-up
  and the public first-order drag approximation. Defender envelopes use
  relative motion, observed arm reach or an own-body fallback, reachable
  acceleration and age uncertainty. An old sighting expands the envelope.
  An athlete with no track contributes uncertainty, without a fabricated
  position. Clearance is evaluated on the horizontal plane and takes no
  credit for an assumed inability to jump. The carrier values the selected
  teammate lane with its nominal delivery. Passing evaluates each speed,
  height and wait candidate and keeps its existing rating-controlled
  uncertainty. The historical diagnostic reapplies the screen to the
  already-identified believed-clear population using the admitted decision
  view, selected speed/height and deliberate wait.
  It measures flags on past interceptions, not prevented interceptions.
- **Carry finish.** For a carrier within 20 m of goal center, the strategy
  scores direct and single-bend goal-mouth routes using actual own-body
  speed, acceleration, estimated travel time, perceived opponents' approach
  times and the remaining own zone time. The provisional estimate weights
  the five-point reward by the route's chance of reaching in time. Shot
  value multiplies its scoring band by a bounded clearance/distance
  estimate. Other options receive a bounded continuation value mapped
  from their prior utility. Finishing can offer a stretch alongside a shot
  when it has a believed reachable mouth point and imminent contact. Ball
  Handling and the existing motor determine the outcome.
- **Takedown evidence.** A fresh visible or radar ball course must share a
  sample time with a plausible body track, be above loose-ball height,
  have compatible velocity, and unambiguously fit one nearby athlete.
  The cutoff is the observer's Reaction interval. This is an inference
  from local evidence rather than the public possession signal or the
  engine carrier ID. When evidence is missing, pursuit and marking stay
  available. The rulebook still adjudicates contact.
- **Boundary audit.** Record the live carrier before dispatch clears it.
  Separate the carrier's body crossing from a still-held ball crossing
  while his body stays in bounds.
  Untouched trajectories attributable to a pass or shot are grouped by
  release type, with intended receiver, aim, release yaw, observed exit
  and projected first ground point when available. A subsequent touch
  puts the trajectory in the deflection group. Remaining outs use the
  loose-ball group. Carry exit pressure and boundary distance come from
  the last delivered carrier view. These are event groups. Compare
  boundary turnover counts separately from the box score. The separately
  switchable guard preserves the lateral route but holds depth for an off-mouth
  end-line approach using own velocity, braking distance and held-ball offset.
  A whole-ball mouth check exempts a safe finish. The guard runs exclusively
  in carrier decisions and leaves ball-flight adjudication in place.
- **Keeper audit.** The unobstructed shot must cross the goal plane within
  the ball-radius-adjusted opening. The reachable envelope uses the
  release-time body, jump and arm reach, the motor's actual reach factor
  and the keeper reaction delay including Reflex and set state. The motor
  planner receives the true path only inside the offline witness. It
  has a zero extra-attempt margin. This is a physical upper bound before
  sensor/decision delays and later traffic. For misses report observed
  save intent timing, offset direction and touch without save, leaving
  remaining execution unclassified when the record is insufficient.
- **Paired effect.** Deltas are ON minus OFF over identical matchup/seed
  cases. Standard errors use paired bootstrap samples stratified by
  matchup (1,000 draws, fixed bootstrap seed). Rates use pooled
  numerators and denominators within each paired population. Report
  completed case counts, particularly when an arm is still running.
