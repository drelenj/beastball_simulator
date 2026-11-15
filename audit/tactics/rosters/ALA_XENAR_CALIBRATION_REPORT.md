# Ala Lady Reds vs Xenar Dzaku — Pocket4 roster calibration

## Source and method
Used the supplied 2026 MBL roster entries, the actual `player_gen_v1.py` in `Beastball_Pocket4_Proto_v1.zip`, and the supplied `pocket4_proto.py` with its included Pocket 2.0 engine. Mapped MBL positions PDR/PFD to passer, SCT to receiver, STR to forward, TRK to runner, HNT to safety, SEN to backer, TRP to corner, GRD to lineman, KPR to keeper, ARC to archer. These position-to-archetype mappings are **provisional design decisions**, not canon.

The previous approximate generated files are superseded by the `*_calibrated.csv` outputs. These use the generator's CRC32 seed and weighted positional overall adjustment rather than the earlier SHA256-based ad hoc method.

## Checks
- 22 source players per team, each with 18 field, 2 keeper, 2 archer entries.
- No unknown position fallback; no generated-player warning notes.
- Maximum absolute weighted positional overall residual: Ala 0.000034, Xenar 0.000254 on 0–1 scale (0.0034 and 0.0254 points on 0–100 scale).
- Pocket4's `build_team` uses the highest-OVR 10 field players, plus highest-OVR keeper and archer. This **does not preserve all supplied starting roles**; substitutions and bench treatment require further integration.

## Four short-match smoke tests
Each is Pocket4 `--short`: two 120-second periods (240 live seconds), **not a regulation game**. A = Ala, B = Xenar.

| Seed | Ala | Xenar | Winner |
|---:|---:|---:|---|
| 1 | 2 | 11 | Xenar |
| 2 | 5 | 3 | Ala |
| 3 | 17 | 24 | Xenar |
| 4 | 14 | 12 | Ala |

Across these four short matches, average points were Ala 9.5 and Xenar 12.5. These results do not establish expected full-game scoring, team strength, or statistically robust calibration. The current Pocket4 prototype showed **zero carry intents in seed 1**, indicating game-mechanics calibration remains unfinished. No changes to canonical Beastball scoring or speed benchmark were made.

## Run
Unzip the source Pocket4 package into a folder. Put `run_mbl_match.py` in that folder and run:

```
python run_mbl_match.py --a Ala_Lady_Reds_input.csv --b Xenar_Dzaku_input.csv --seed 1 --short
```

Remove `--short` for regulation-length simulation. Run the same seed to reproduce deterministic generated players and the seeded simulation (subject to software/platform behavior).

## Open issues
1. Position mapping and individual body measurements remain provisional until actual player-specific data is supplied.
2. Pocket4 chooses top-ten field starters by overall; source roster's S/B labels are not enforced.
3. Four short smoke tests are not an acceptance matrix; test the full regulation game and multiple seeds before treating game balance as calibrated.
4. No change was made to Pocket4's underlying gameplay controller, contact physics, or scoring model.
