# HP-002: RB-3.37 review (Claude, 27 Nov 2026 UTC)

Reviewed `codex/rb-3-37-traction` @ ad3d9aeaa14beb6cc27d0c60bc7122306683bbbc (8 games per arm: Garvian-Ala 1-5,
Yukima-Isu'Kari 1-3). Not independently rerun this time (no configuration is being adopted; L0 = T3, whose seed 1 I
reproduced in the RB-3.36 review).

- Traction is NOT the cause of carrier body-outs (lead hypothesis wrong): body-outs L0 19.2, L1 18.9, L2 21.3;
  possessions rose with traction (140.6 -> 149.2 -> 157.0). Keep traction scale 1.0.
- Archers (from the raw diagnosis, per team per game, L0): 299.7 arrows, 185.1 hits, 96.2 freezes; 0.68 freezes per
  defensive possession; 51% of possessions see at least one freeze; the 15-arrow / 5-freeze per-possession limits
  almost never bind (arrow limit 0.0, freeze limit 0.2 per team per game). Codex: 949 of 958 possession-ending
  fumbles follow a carrier freeze (about 21 per team per game, about 15% of possessions).
- In-universe write-ups treat an Archer strike that forces a release as a notable single play. Archer volume is a
  canon question for the owner.
- Carrier body-outs remain unexplained; next step is an observer that records the carrier's last 2 s (option label,
  intent, aim, locomotion target, speed/heading, nearest defender and contact state, maneuver, freeze state).
