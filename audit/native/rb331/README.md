# RB-3.31 diagnosis reproduction

Run from the repository root in the maintained Python environment with pytest
and openpyxl. The rating source is the ratings 0.4 workbook at
`b284e822fa2f23c820987c795a2d780f16334fc3`, with SHA-256
`47b48af7a19035428d517582370fa1782b542980c783edf3dfb20619cf437fba`.

```bash
export PYTHONPATH="$PWD${PYTHONPATH:+:$PYTHONPATH}"
work=$(mktemp -d)
name='audit/arcade/ratings/NBL_2026-27_Opening_Night_Rosters_ratings-0.4_overall-trials.xlsx'
git show "b284e822fa2f23c820987c795a2d780f16334fc3:$name" > "$work/ratings.xlsx"
bash audit/native/rb331/gates.sh "$work/ratings.xlsx" "$work"
bash audit/native/rb331/batch.sh "$work/ratings.xlsx" "$work"
python -m audit.native.rb331.summarize "$work"
```

At most two lanes run at once across the gates and the soak. The batch runner
accepts a shared output path and claims individual cases with directory locks.
The reproduction uses explicit technical ratings, OVR 0.422 roster ordering,
individuation, hand-set play values and a planned fatigue scale of 0.52.

## Witness definitions

- **Secures and drops.** The JSON and CSV schema is `native-box/3`. A
  committed control event goes into exactly one category. Receptions are
  targeted teammate passes, interceptions are opponent passes, and all other
  secures are other recoveries. Other recoveries include shot pickups,
  untargeted receptions and handoffs. `balls_secured` sums the categories.
  `flight_balls_secured` retains the prior catch subtotal (pass or shot from
  a different athlete). A drop is a targeted touch that does not become a
  secure by that player before the flight closes. Unresolved flights in
  partial windows remain unresolved.
- **Interceptions.** The latest actionable view and delivered history are
  recorded at release. The view's lane to the submitted aim is compared to
  two physical snapshots using the same planar margin formula, one aimed at
  the submitted location and one rotated to the actual initial heading.
  The true snapshots extrapolate the release-time opponents using their
  center velocity and acquisition radius. The diagnostic is a planar
  clearance proxy and ignores changes in player motion after release,
  projectile height and spin. Radar and cone membership use true release-time
  geometry. The never-perceived denominator is lifetime delivery to the
  passer before release, including directly delivered frame tracks and
  retained tracks. It includes periods when the interceptor was off the
  field. The targeted comparison uses a separate latest-view measure.
- **Carries.** The population is existing engine attempt starts inside the
  20 m radial zone. Distance is the minimum perpendicular distance from the
  carrier and the held ball to the scoring plane sampled at carrier-follow
  updates. A legal release ends the held segment. The shot follow-up is kept
  separately and an actual scored release below 3 m is a carry goal. A
  whitespace-free match event ID marks each witnessed boundary. A freeze of
  another player does not end a held segment. Exact scoring is covered by
  the existing plane and within-3 m scenario tests.
- **Takedowns.** An accepted takedown intent starts an episode. Adjacent
  renewals against the same target are grouped, ending with a different
  intent, expiry, a whistle or the witnessed outcome. These episodes include
  no-contact commitments. The narrower box-score denominator starts at a
  witnessed driving hold. Contact and confirmed grip use the C3 collision,
  hold and grip witnesses and the simulation's grip threshold. Instances
  above threshold with an unresolved outcome are kept separate. The
  maneuver outcome requires an explicit break by truck or stiff arm. Nearby
  maneuver intents are associations and logged separately. Skill bins use the
  unmodified workbook ratings, so they describe associations across differing
  opponents and situations. The durations are observed intervals that can
  include time to expiry and adjudication.
- **Archers.** Possession statistics use the existing possession ledger and
  attribute arrow impacts and freezes to the arrow's release possession.
  Maximum charged arrows use the independent rulebook quota reset, charge and
  refund stream. A relevant freeze hits the carrier or the intended receiver
  of an in-flight or admitted pending pass. The three-second measure includes
  only change-of-side turnovers and reports both the all-turnovers and the
  relevant-freeze-possessions denominators. Points per possession are the
  offense's points in its own possession.
- **Keepers.** A shot faces the opposing active Keeper at release. On-target
  status uses the unobstructed ball-material trajectory and whole-ball fit at
  the goal plane, or a recorded goal. A save means an on-target shot touched
  or secured by the Keeper without scoring. Deflected off-target shots remain
  separate from on-target stops. Aim offset is absolute lateral distance
  between submitted aim and the Keeper's release-time y coordinate. Band is
  the potential throw band based on the release distance, including shots
  within 3 m in the 2-point release-distance group for this analysis. The
  underlying scoring rule still credits qualifying close releases as carries.
- **Units of evidence.** The per-match results include score, match hashes,
  possession rows and diagnostic event witnesses. Each run can be reproduced
  with `python -m audit.native.rb331.match`. The strike attribution and
  comparisons are observational, with no causal counterfactual simulation.

The exact RB-3.30 before/after box comparison imports its parent planned
rotation implementation, uses the current observer and checks the resulting
trajectory against the archived replay. Historical catches equal the new
flight-only subtotal player by player. Names are roster display metadata.
