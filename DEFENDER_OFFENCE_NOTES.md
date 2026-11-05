# Defenders in the offence (tendencies v1.1)

Implements the "Rotational Attack Architecture" idea from the design discussion as a **proposed** simulator behaviour, not a rule. Defenders = Guards and Trappers. Switch: `--off tend_nodefadv` is not a normal system name; use `S.on` flag `tend_nodefadv` (run with `off=('tend_nodefadv',)`). Coach dial: env `DEF_FREEDOM` (0 = never join, 1 = default, >1 = predatory swarm).

## Decision (per live step, own team in possession)
For each Guard/Trapper: `V_advance = F * (0.30 + 0.60*terr + 0.35*[just won ball]) * (0.75 + 0.25*near) - 0.45*counter_risk - 0.40*[cover short]`
- `F` attacking freedom = position base (Guard .85, Trapper .95) + archetype shift (Hybrid Guard/Trapper +.25, Sweeping Guard +.15, Press/Crusher +.10, Anchor -.20, Recovery Trapper -.10, Archer Trapper -.15) times `DEF_FREEDOM`.
- `terr` = how far upfield the ball is (0 at u=30, 1 at u=65); `near` = how close he is to the ball (45 m).
- `counter_risk` = opponents already in our half / 4. `cover short` = fewer than 2 other Defenders/Sentinels left back.
- Joins at V >= .22, leaves at V < .08 (min hold 4 s), at most 3 Defenders forward at once.

## While advanced
- Guard: central penetration, 10 m ahead of the ball. Trapper: weak-side wide channel, 7 m ahead.
- Decision values: shoot x1.12, carry x1.12 (x1.20 right after winning the ball), pass value to him x1.10.
- **Cover handoff**: one Sentinel (else Hunter, else Tracker, else Pathfinder) per advanced Defender drops to hold the vacated space until the Defender is back.
- **Recovery**: when possession is lost, advanced Defenders revert to the defensive rules; cover holders keep their space until the Defender is back inside our 40 m line (or 6 s pass).

## Measured (6 short games, Ala vs Xenar, tendencies on)
| | without | with |
|---|---|---|
| Defender share of points | 12.9% | 20.4% |
| Defender share of shots | 14.6% | 27.5% |
| Defender share of touches | 22.9% | 26.8% |
| Total goals per game | 14.2 | 15.5 |
Time spent advanced: Trappers ~35%, Guards ~28% of live steps.

## Not modelled yet
Attackers dropping into Ranger cover, rotation philosophies (shape-first / handoff / funnel / pursuit), per-team coaching settings (only the one `DEF_FREEDOM` dial), funnel-to-Archer traps, "membrane integrity" as an emergent measure.

## Also fixed
Rotation could sub out the player due to take a dead-ball restart (engine `KeyError: None`); the restart taker now stays on.

## Regulation check (2 games with defender advance vs 1 baseline game)
Defenders: 17.5% of points (53 of 303), 18.8% of shots, 24.7% of touches vs 9.0%, 10.0%, 22.4% without. Final scores 64-99 and 52-88 (163 and 140 total goals vs ~145 baseline). Only 2+1 games: indicative, not calibrated.
Observed twice in long games: a team forfeits (`minimum_lineup`) after many minor penalties - an existing rules interaction, not specific to this feature.
