# RB-3.17 baseline inventory

Baseline: `9c37fd4`.

- The active C3 contact kernel (`core_src/match.py::c3_contact_kick`) exchanges
  an impulse `(1+e) * closing_speed / (1/m_a + 1/m_b)` on the normal. The
  velocity change is impulse divided by mass. Traction-limited bracing may
  absorb some of it. It resolves overlap by moving the lighter body farther,
  and applies balance shock from the remaining speed change. A lawful,
  material, voluntarily initiated hit on a non-carrier produces the block
  label. The label records the collision instant; it applies no continuing
  force, displacement, speed loss, or restraint.
- The older non-C3 `player_contacts` block branch uses strength × blocking ×
  sqrt(mass / 220) × fatigue factor, a displacement capped at 0.35 m per
  update, and a 0.72 multiplier on both velocities. It has no prescribed
  fixed duration. That physical branch is outside the active Native C3 path.
- `Engine.contact_legal` classifies contact, with Native rule and RB discipline
  wrappers. Frozen athletes are passive obstacles and the 1,000 ms thaw
  buffer rejects active contact. Contact witnesses drive the existing foul
  path. C3 grips are reserved for the carrier.
- `formation.py::rb_hold_step` pins movement and zeroes launch-time velocities
  through the snap hold. It releases at 5 m travelled or a qualifying touch.
  RB-3.17 will explicitly reject its new actions while this hold is active.
