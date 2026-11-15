# ATTR-1 sensitivity audit

This is a direction audit, not a quality, balance, or emergence result. Each row used 200 paired trials at rating 0.60 versus 1.00. Shared random noise cancels within each pair.

| Rating | Expected | Mean at 0.60 | Mean at 1.00 | Result |
|---|---:|---:|---:|---|
| speed | higher | 16.249778 | 21.249778 | expected |
| agility | higher | 28.000344 | 43.750344 | expected |
| strength | higher | 1100.000236 | 1500.000236 | expected |
| balance | higher | -0.909044 | -0.666620 | expected |
| stamina | inert | 0.998707 | 0.998707 | INERT |
| tackling | higher | 1.100598 | 1.500598 | expected |
| blocking | higher | 0.428215 | 0.714508 | expected |
| contact_resistance | higher | -0.750511 | -0.600511 | expected |
| ball_handling | higher | -0.640656 | -0.400656 | expected |
| catching | higher | 0.939386 | 1.299386 | expected |
| awareness | higher | -1.251820 | -0.751820 | expected |
| throw_power | higher | 89.400307 | 134.100307 | expected |
| throw_accuracy | higher | -1.999410 | -0.149410 | expected |
| jump | higher | 0.780244 | 1.300244 | expected |
| keeper_skill | inert | 0.999816 | 0.999816 | INERT |
| archery_accuracy | inert | 0.998935 | 0.998935 | INERT |

All expected directions passed. Stamina is inert because fatigue is off. Keeper skill and Archer accuracy are stored in the athlete but not consumed by the current active Native execution paths; this is explicit in `QUESTIONS_FOR_OWNER.md`.
