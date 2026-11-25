# OWNER BRIEFING

1. **IMPLEMENTED.** RB-3.28 adds an optional energy reserve and dead-ball fatigue rotation.
2. With the switch on, the engine reduces tired athletes’ physical and technical outputs and rests eligible field players. Rested starters return to their own slots. The match uses the ratings 0.4 workbook and hand-set decision values.
3. The starter-minute target, speed gate and paired 40-match results are being measured.
4. No canon question is pending. Calibration and verification are in progress.
5. Review the measured minutes and existing competition benchmarks before making the fatigue switch a default.

## Revisions and status

- Branch `codex/rb-3-28-fatigue-rotation`
- Lead-verified parent `b91440df56a8b3234d476630e6e949eb2c9f2202`
- Core implementation `3bcc5cf`
- Ratings 0.4 source `b284e822fa2f23c820987c795a2d780f16334fc3`
- [Reproduction](rb328/README.md)

| Task | Status |
|---|---|
| 1. Fatigue | DESIGN COMPLETE, IMPLEMENTED |
| 2. Rotation | DESIGN COMPLETE, IMPLEMENTED |
| 3. Calibration and soak | DESIGN COMPLETE, IMPLEMENTED |

## Standing gates

 a) pytest -q b1 native, full suite, after the last change.

 b) Legacy hash guards unchanged (six rows, native/evidence/rb3-reach/legacy-hashes.txt).

 c) Determinism: same code + roster + seed gives identical trace and state hashes.

 d) Compatibility (individuation off, fatigue off): real seed 1 = 57-76, trace 44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072, state 046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d.

 e) CORE identity (fatigue off, learned values off): neutral-real seed 1 = 61-80, trace c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256, state c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745.

 f) Speed: fatigue and rotation ON may add at most 5% per step on top of CORE.

## Workload and rotation

The default-off switch is `fatigue_rotation`. Off retains the original CORE kernel. On replaces the old kernel writes to its reserve with a live-work and recovery model. Fresh athletes start at 1.0. The live workload uses the greater of achieved speed and the braking-envelope speed for the current movement command, relative to the athlete’s effective maximum speed. A concave workload curve accounts for repeated short movement demands. Stamina adjusts intensity in the middle of the range and preserves the standing and full-sprint endpoints. Its rate modifier speeds recovery and slows drain. Dead time recovers at the standing rate for the field lineup. The bench recovers at the same independent rate for every athlete.

Effective speed and acceleration retain the kernel coefficients `0.70 + 0.30 × reserve` and `0.55 + 0.45 × reserve`. Braking, turning, strength, agility, jumping and maximum throwing speed use `1 − 0.40 × (1 − reserve)`. Technical execution uses `rating × (1 − 0.30 × (1 − reserve) × (1 − rating))`. This reduces poor form by a greater fraction. Under fatigue, release motion still follows the existing admission and timing path. The motor caps release speed at current throwing capacity and updates execution accuracy. The own-body view reflects available movement output. Strategy, perception and decision ratings retain their roster values.

A field athlete crossing 0.60 is marked to leave at the next dead ball. If an eligible reserve is unavailable, the athlete remains eligible for removal at the next dead ball. Rested starters reclaim their original slots first at 0.75. Elective replacements use exact legacy position, position group, then Overall rank, in that order. Overall and legacy position stay in roster selection metadata. A Keeper can rotate from fatigue once his regulation participation reaches 36 minutes. Archers receive no elective fatigue substitutions. Existing disciplinary and injury-cover rules remain in force. Playing time is measured on the regulation clock, and required and elective substitutions have separate event records.
