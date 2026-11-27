# HP-002: RB-3.36 review (Claude, 27 Nov 2026 UTC)

Reviewed `codex/rb-3-36-sets` @ 3dc4eef3aa871f72d8c13ef46a4b3b81b5c4bac3. Independent rerun: T3 seed 1 44-122,
trace 539c5548...09c9, state 0383c424...9793, digest 9342b188...e386. Matches the checkpoint.
Status: IMPLEMENTED, TESTED (5 games per arm, Garvian-Ala only).

- Boundary fix restored carries: carry points 9.1 (B4) -> 15.4 (C0).
- End-line canon: 9.0 held-ball end-line crossings per team per game now play on, yet boundary possession ends did not
  fall (32.7 -> 32.3): those carriers go out with the body a moment later.
- Universal set speed: Keeper above set speed at release 45% -> 11%, save rate unchanged within noise. The unset cost
  was not what limits saves; reach is (RB-3.32 audit: 312 of 1,218 on-target shots reachable). Remaining levers are
  the owner's goal size and Keeper height.
- Tackle trials: possessions C2 151.4 -> T3 142.2 -> T4 139.1. Only about 31% of possessions reach a first tackle and
  about 4% a third, so the tackle limit binds rarely; open-play turnovers set the pace.
- Carrier body-outs (T3 raw games): 19.2 per team per game (12.0 sideline, 7.8 end line, mostly >10 m wide of the
  goal); 184 of 238 had an admitted aim INSIDE the field (P50 2.0 m inside) yet left with an outward velocity of
  P50 3.4 m/s at total speed P50 6 m/s; 69% under believed pressure. Steering/traction cannot hold the line: turning
  16.25 x Agility (11.4 m/s^2 at .70), braking 16.875 x Agility, against 31 m/s top speed. The owner's 28 Oct ruling
  already allows traction and lateral standards to be raised for fluid cuts.
- Parity watch: Ala minus Garvian +40 to +48 in every RB-3.36 arm (strength gap about 11 by the preseason rankings;
  target slope 2.5-3 points per strength point implies about +28 to +34). Not judged on one pairing.
