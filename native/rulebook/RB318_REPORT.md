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

## TESTED | match evidence

Base means the archived RB-3.16 match. Each rule-only event log is
byte-identical to its base log. None of these matches or the four enabled
matches scored a release carry. The forced 2.5 m test verifies the rule.
The rule-only config hash changes because the radius is recorded.

Points by method are combined across both teams in this order:
held carry / released carry / 2-point throw band / 3-point throw band /
4-point throw band / own goal / half award / full award. The JSON archive
also gives the team split. Stiff-arm columns are attempts/effects
(delayed reacquisitions/reduced live grips). A single effect can count
in both categories. Truck columns are commands/broken/stopped, so an
unresolved command did not reach a qualifying impact before it ended.

| Build, match | Score A–B | Points by method | Carry attempts/goals | Stretch attempts/goals | Stiff-arm | Truck | Tackles/strips | Possessions A/B |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Base / rule real-seed01 | 74–92 | 20/0/6/69/60/2/3/6 | 118/4 | 0/0 | 0/0 (0/0) | 0/0/0 | 82/12 | 228/226 |
| Base / rule real-seed03 | 42–92 | 10/0/6/60/48/0/1/9 | 99/2 | 0/0 | 0/0 (0/0) | 0/0/0 | 68/24 | 217/217 |
| Base / rule real-seed05 | 84–60 | 5/0/2/54/64/2/5/12 | 111/1 | 0/0 | 0/0 (0/0) | 0/0/0 | 88/20 | 201/201 |
| Base / rule control-seed01 | 68–55 | 10/0/6/45/60/0/2/0 | 92/2 | 0/0 | 0/0 (0/0) | 0/0/0 | 75/17 | 206/206 |
| ON real-seed01 | 67–92 | 20/0/6/48/80/0/5/0 | 107/4 | 3/3 | 82/82 (54/34) | 104/13/1 | 74/17 | 218/217 |
| ON real-seed03 | 66–80 | 30/0/2/36/68/0/4/6 | 91/6 | 4/4 | 121/121 (82/45) | 126/15/3 | 106/22 | 195/194 |
| ON real-seed05 | 55–51 | 25/0/4/33/40/0/4/0 | 99/5 | 6/5 | 86/86 (61/35) | 105/12/1 | 90/16 | 198/200 |
| ON control-seed01 | 59–80 | 25/0/4/42/60/0/2/6 | 68/5 | 5/5 | 160/160 (97/67) | 113/7/3 | 100/22 | 182/181 |

Against the owner target of 76 points per team, the enabled A/B deltas
were −9/+16 (real 1), −10/+4 (real 3), −21/−25 (real 5), and −17/+4
(control 1). The enabled real-roster median was 66.5 across six team scores.
The movements and handoff/block flags were enabled together. The sample
does not isolate any individual move's contribution.

The full radius-zero replay, real seed 1 with both flags OFF, exactly
matched RB-3.16:

- Trace `93b1f57e268ee6c436fae47109e4e2987cfdf7024df5575b6405e119c5ed32d7`
- State `b9962ddfb23dbc96551258ea6c2132565804d22ec1b0c87295e3f3ff37d59854`
- Config `c51d4bbcbc7a9569b1f3d98b3b26779711d8166a1669171b1e47578968f19615`

All six 3,000-step seed 1/3 guards (native-v0/2, native-v0/3, native-rb/2)
matched `185b557` for trace, state and config. Full hashes are in
`native/evidence/rb318/legacy-hashes.txt`. The raw logs are committed in
`native/evidence/rb318/{identity,rule,on}/{real,control}` as gzip files.
`comparison.json` records per-team methods, attempts, outcomes, and hashes.
