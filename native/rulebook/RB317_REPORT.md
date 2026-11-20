# RB-3.17 handoff and blocking

The branch starts from RB-3.16 `9c37fd492f8b121c11d46a7c7a61f5c2499a19d6`.
The two new commands and the belief-based policy are enabled by
`rb3_handoff_block_enabled=true` in `native-rb/3`. OFF is the default and
serializes to the existing effective config, so the historical config digest
stays identical. ON records the flag and has its own digest.

The baseline contact inventory is in `RB317_INVENTORY.md`. The frozen
substrate and the legacy decision code retain their existing paths.

## Motor contracts

- **Handoff.** Exchange takes `round(150 * (1.35 - 0.5 * ball_handling))` ms
  on the integer clock. At execution recheck phase, snap hold, same ball
  generation, legal participation, same team, and the 3-D distance between
  upright or airborne hand anchors. The range is the sum of the two arm
  reaches plus one ball radius (0.1075 m for the baseline ball) as contact
  tolerance. The exchange point divides the anchor segment in proportion
  to the two arm reaches. Exceeding the range aborts the command with the
  ball still with the giver.
- Both participants are already coordinating the exchange. For security,
  use velocity difference at the hand anchors (player velocity, with no
  separately animated arm speed). Energy is `0.5 * ball_mass * speed²`.
  Apply the Native catch capacity and secure curve `1 / (1 + (E/C)^8)`
  using receiver catching and miss fraction based on use of the tolerance.
  On success, committed acquisition makes the receiver the carrier at the
  exchange timestamp, updates possession and dribble bookkeeping, and
  creates no ball flight. On a fumble, the unheld ball starts at the exchange
  point with mean horizontal hand velocity and gravity acting normally.
  Events are `handoff_start`, `handoff_complete`, and `handoff_fumble`.
  The aborted/interrupted starts are in motor outcomes. No throw event or
  pass-attempt statistic is created by the exchange.
- **Block.** The command supplies the opponent and protected point. The
  motor aims at the contact position on the protected side of the target,
  just inside the solver's contact envelope so locomotion does not brake
  short. The offset uses twice the existing 0.08 m locomotion deadband.
  The ordinary C3 solver controls actual overlap, impulses, bracing,
  displacement, and fouls. No new push impulse or restraint is applied.
- While both bodies are in lawful, non-separating contact, calculate
  `power = strength * blocking * sqrt(mass / 220) * (0.5 + 0.5 * fatigue)`,
  the existing legacy block-force strength formula. Let `n` be the
  target-to-blocker contact normal and `u` the target-to-protected-point
  direction. The blocked fraction of positive normal propulsion is
  `max(0, n·u) * power_blocker / (power_blocker + power_target)`.
  Zero combined power gives zero effect. If several blocks qualify, only
  the largest absorbed impulse applies to that propulsion update. The
  effect neither pulls the target back nor cancels propulsion away.
  The request expires after one decision interval, or when replaced.
  Frozen bodies keep their baseline obstacle status. The thaw buffer,
  snap hold, legal contact gate and ball-carrier check all apply to active
  blocks. `block_engaged` and `block_shed` are recorded at committed
  step boundaries. Logged durations therefore describe observable
  engagement windows, not a substep-level force integral.
- **Policy hook.** From public body data and believed tracks, a carrier
  considers handing off to an in-reach teammate moving faster in attack
  direction. The pass value uses the existing maximum lane margin, with
  no flight or pass-range gate. An off-ball field attacker may block the
  nearest perceived defender closing on the believed carrier within 8 m.
  The policy supplies a protected point and the motor derives contact
  placement. Both hooks are disabled during the snap hold.

## Owner questions

- May a handoff carry the ball across the giver's own Keeper Zone boundary
  to a teammate's hands? The flight-specific ZR-T rule has no handover
  witness. This build conservatively refuses that entry and permits normal
  handoffs on either side of the boundary when both players are on the
  same side.
- May the current carrier execute a deliberate blocking command on a
  non-carrier? This build gives that command to off-ball athletes. The
  existing carrier contact mechanics still apply.

## Reproduce

```sh
python -m pytest -q b1 native
python -m native.rulebook.scoring_audit --legacy
python -m native.rulebook.reach_run --block real --seed 1 --outdir /tmp/rb317/off/real
python -m native.rulebook.reach_run --block real --seed 1 --override rb3_handoff_block_enabled=true --outdir /tmp/rb317/on/real
python -m native.rulebook.rb317_report /tmp/rb317
```

Repeat the match commands for seed 3. The runner calls `native.run.run_match`
with the real Garvian Guardians and Ala Apex roster from `81f92e3`.

## TESTED | two seeds per flag setting

| Flag / seed | Points A–B | Possessions A/B | Handoffs start/complete/fumble | Blocks / mean duration | Pass interceptions | Tackles |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| OFF 1 | 74–92 | 228/226 | 0/0/0 | 0 / n/a | 13.47% | 82 |
| OFF 3 | 42–92 | 217/217 | 0/0/0 | 0 / n/a | 18.12% | 68 |
| ON 1 | 59–105 | 207/206 | 356/281/0 | 125 / 114.99 ms | 18.43% | 77 |
| ON 3 | 75–64 | 209/208 | 337/281/0 | 66 / 108.89 ms | 15.00% | 67 |

All four finished in regulation. A handoff attempt is an admitted
`handoff_start`, so the 75 and 56 unmatched starts include refusals or
interruptions before an exchange. No live fumble occurred in these two
enabled matches. The forced large-mismatch test produces one. The block
mean is across all closed windows. Pass interceptions are first opposing
control after an open-play pass release, divided by all such passes.
Tackles count `tackle_count` events. These two seeded comparisons test
functionality. They do not establish an effect on the possession target.

Both OFF windows exactly reproduced their full RB-3.16 match trace, state,
and config hashes. OFF seed 1 trace is
`93b1f57e268ee6c436fae47109e4e2987cfdf7024df5575b6405e119c5ed32d7`
and state is
`b9962ddfb23dbc96551258ea6c2132565804d22ec1b0c87295e3f3ff37d59854`.
The archive contains all four complete gzip logs and all run hashes in
`native/evidence/rb317/{off,on}/real` and `comparison.json`.
All six 3,000-step legacy guards for seeds 1 and 3 matched `185b557`
exactly (trace, state, config) for Native v0/2, v0/3, and RB/2.

The initial enabled run was halted during period 1 on both seeds after
the hook test caught a view builder overwriting the enabled flag.
`25fdfad54368baa8619a9e2a8dbf7b1caf69ea38` corrected the view wiring.
The table includes only the two completed full matches per setting.
