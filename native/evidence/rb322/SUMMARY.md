# RB-3.22 evidence (claude/rb-3-22-defaults-talent; base eb788ec, owner ACCEPTED RB-3.21)

## OWNER BRIEFING
1. Accomplished (IMPLEMENTED, TESTED): the accepted RB-3.21 baseline is now the RB/3 default (carrier moves, handoffs/blocks,
   ball in play, exact bounce, ball material, carry release radius 3.0), each still switchable. A roster "talent source" option for
   diagnosis: rb322_technical_source ('ovr' default | 'neutral' = .784 for every technical skill) and rb322_physical_source
   ('roster' default | 'neutral' = the league mean of each of the nine physical ratings over all 712 players; bodies unchanged);
   starters are still picked by OVR, so the same 22 play.
2. Can do now: a plain run (no overrides) is the RB-3.21 game: real seed 1 reproduces the RB-3.21 soak gate hashes exactly.
   Every switch off reproduces RB-3.16 exactly. reach_run takes --override 'rb322_technical_source="neutral"' and/or
   --override 'rb322_physical_source="neutral"'.
3. Unproven: the talent smoke is one match per mode (below); the decomposition soak is Haiku's.
4. Blocking: nothing.
5. Recommended: run the decomposition soak with the three modes.

## Smoke (real seed 1; raw logs runs/<mode>/real/raw-real-seed01.json.gz)
| mode | score | possessions per team | trace / state |
|---|---|---|---|
| default (no overrides) | 57-76 | 144.5 | 44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072 / 046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d (= RB-3.21 soak gate) |
| technical neutral | 123-73 | 145.0 | 78e4f85baa76085e421b509873126aa9593b4266e19d99ad982f3a1233697d31 / e4254dd7e52ed84276ac98dd03d8eb33e554456a8f915663eb2cd82b841691c4 |
| physical neutral | 88-116 | 157.5 | 61a0cfba2207093dde3e9ec40b70b6ec54315c3cc1fa9595943e110066ee2884 / 70defaeeed84839db643f26a84d412fbfc9127c1df26c0189b52716593661f5a |
| all switches off (identity) | 74-92 | 227.0 | 93b1f57e268ee6c436fae47109e4e2987cfdf7024df5575b6405e119c5ed32d7 / b9962ddfb23dbc96551258ea6c2132565804d22ec1b0c87295e3f3ff37d59854 (= RB-3.16) |

## Constants
- NEUTRAL_TECHNICAL = .784 (native/nbl_roster.py; league mean Opening-day OVR / 100, the lead's figure).
- Physical neutral: per-rating mean over all 712 rows of 'All 712 Players' (speed, strength, jump, acceleration, agility, balance,
  throw power, stamina, durability), /100; contact_resistance follows balance as before (PLACEHOLDER unchanged).

## Tests and guards
- Full suite after the last change: 662 passed.
- New: native/rulebook/test_rb322.py (defaults and switchability, record labels, neutral values exact for both franchises,
  same starters, bodies unchanged, determinism, real seed 1 default = RB-3.21 gate, all-off = RB-3.16).
- Updated because they encoded the old OFF defaults: test_rb312.carrier_scene pins its scene to the B-5 rules (tactics and ball-in-play
  off in that view); test_rb319's default-record test now checks the switch-off record.
- native-v0/2, native-v0/3, native-rb/2: all six rows of native/evidence/rb3-reach/legacy-hashes.txt reproduced.
