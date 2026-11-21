# RB-3.18 phase 1

Based on `efff882a33ce138a3a6705807d9bf32d78ebcbff`. Engine implementation
`380d6fb`. All new gameplay applies only to RB/3. The default radius is
3.0 m and both policy flags default OFF. Radius zero and both flags OFF
omit the new keys from the effective config to preserve legacy identity.

## IMPLEMENTED | Rules and motors

- **Release carry.** A legal goal with scoring-team deliberate release
  provenance and a planar release distance strictly below 3.0 m gets
  5 points, `method=carry`, `release_carry=true` and its measured release
  distance. The existing whole-ball crossing, own-goal and Keeper rules
  are checked first. Close releases use carry counters rather than shot
  bands, with the existing one-attempt-per-holding rule. At exactly 3.0 m
  and beyond, throw bands still apply.
- **Stretch.** The held-ball offset grows linearly to 0.9 times arm reach
  in `round(200 * (1.35 - .5 * ball_handling))` ms. Ordinary carry offset
  is .35 + .35 times reach, so only the positive difference is available
  for extension. The carrier must be upright, including while under a grip.
  The existing swept whole-ball goal test still adjudicates the crossing.
  Stretch uses the C3 strip hazard with a multiplier ramping from 1 to the
  existing wind-up exposure factor (4) at full extension, with no extra RNG
  draw. Events are `stretch_start`, `stretch_end`, and `stretch_goal`.
- **Stiff-arm.** A legal front/side push acts only if the opponent's body
  surface is within the carrier's arm reach. Power comes from the RB-3.17
  formula using ball handling for the carrier's push skill and blocking
  for the opponent's resistance. Apply equal and opposite normal impulse
  up to the C3 traction limit `µ * carrier_mass * g * contact_time`,
  multiplied by the carrier's share of combined power. Divide impulse by
  the tackler's full grip impulse capacity to get the reduction in current
  grip. If zero grip remains, use C3's existing reaction delay before the
  target can start another grip. Events are `stiff_arm` and
  `stiff_arm_effect` (impulse, grip before/after and reacquisition delay).
- **Truck.** At a fresh C3 body impact, compare strength-weighted closing
  momentum along the contact normal. Add the current grip's impulse
  capacity over C3 contact time to the tackler's side. A win requires
  strictly greater drive and positive net forward momentum. Use the
  ordinary equal-and-opposite collision impulse with zero restitution for
  that impact, so the carrier keeps reduced forward speed. Remove only the
  winning carrier's shock from that impact and break that tackler's grip.
  Other holds still act. A loss follows the ordinary collision and tackle
  path. Events are `truck`, `truck_broken`, and `truck_stopped`.
- **Legality.** These actions require live play after the snap hold.
  Pushes and trucks use existing legal contact, frozen-obstacle and thaw
  protection, with no grip initiated by the carrier. A successful
  handoff into the giving side's own zone now completes first and applies
  the pass-equivalent ZR-T award, without a ball-flight or pass event.
- **Policy.** Stretch is considered inside the mouth width and within
  own arm reach plus 1 m of the plane. Otherwise the hook uses the
  nearest closing front/side defender. It prefers a truck within the
  existing 300 ms reaction interval when believed momentum wins, then an
  in-reach stiff-arm. Own strength/mass are available from own-body
  fields. Opponent mass is estimated from public height using the control
  body's volume scaling and opponent strength uses a 0.70 prior. The
  engine adjudicates actual impact. No ratings of opponents enter the view.

**Owner question.** This phase uses the ordinary upright hand anchor and
extends straight toward the plane, without an independent lateral or
vertical reach command. If downward or sideward stretch is intended,
it needs a separate motor direction convention. Juke, spin and hurdle
remain phase 2.

## Reproduce

```sh
python -m pytest -q b1 native
python -m native.rulebook.scoring_audit --legacy
python -m native.rulebook.reach_run --block real --seed 1 --override carry_release_radius_m=0.0 --outdir /tmp/rb318/identity/real
python -m native.rulebook.reach_run --block real --seed 1 --outdir /tmp/rb318/rule/real
python -m native.rulebook.reach_run --block real --seed 1 --override rb3_carrier_moves_enabled=true --override rb3_handoff_block_enabled=true --outdir /tmp/rb318/on/real
python -m native.rulebook.rb318_report /tmp/rb318
```

Repeat the last two match commands for real seeds 3 and 5 and control seed 1.
Use the output directory corresponding to the block. Real rosters are
Garvian Guardians and Ala Apex at roster ref `81f92e3`.
