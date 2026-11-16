# RB-2 read-only roster handoff

Source reviewed without copying or modifying it:

- Branch/commit: `claude/hp002-audit` at `d85e790`
- Path: `audit/arcade/morphology/NBL_2026-27_Opening_Night_Rosters_CANON_OVR_morphology_physical.xlsx`
- Workbook: 31 sheets; the `All 712 Players` sheet contains 712 unique player IDs and 47 columns.

Observed physical ranges:

| Field | Minimum | Maximum |
|---|---:|---:|
| Height | 72.07 in / 1.831 m | 135.70 in / 3.447 m |
| Mass | 202.2 lb / 91.7 kg | 1,660.8 lb / 753.3 kg |
| Arm span | 70.54 in / 1.792 m | 141.12 in / 3.584 m |
| Standing reach | 89.95 in / 2.285 m | 170.02 in / 4.319 m |

The nine integer ratings are Speed, Strength, Jumping, Acceleration, Agility, Balance, Throw Power, Stamina and Durability. Every observed value is in 65–100; individual column maxima vary between 98 and 100.

Next attribute-step constraints from the owner ruling:

- The old 2.40–2.95 m / 155–285 kg Native design envelope must widen. It may not reject or merely warn on canon bodies solely because they exceed that old envelope.
- Speed remains the PLACEHOLDER proportional mapping `rating / 100 * 44.704 m/s`.
- Height and physique already influenced the supplied ratings. A future loader must consume the recorded dimensions and ratings directly and must not add a second size adjustment to those ratings.
- Position and other labels remain non-canonical decision inputs unless separately ruled.

RB-2 does not load this workbook and makes no athlete-decision or attribute-mapping change. This document is inventory for the next attribute step only.
