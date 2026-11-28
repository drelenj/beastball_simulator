# HP-002: Neon's Archer review, checked against 939606c (Claude, 28 Nov 2026)

| Neon claim | Verdict | Evidence |
|---|---|---|
| opportunity_cost makes scarcity about 0.99 all period | CONFIRMED | archer_cycle.py:10-14: available = horizon/cycle; port.py ~228 horizon = s.game_ms (period time left, 600,000 at the start); cycle about 1,800 ms -> 333; scarcity = 1 - 4/333 = 0.988; cost = 0.988 x (3 - 0.02 d). Carrier values end near zero, off-ball values negative, until the last seconds. |
| Archers shoot only because of "+1.5 / +2.0" tendency bonuses | WRONG SIZE | cognition.py:18-23 owned_effect = (rating - 0.70) x scale, so the bonus is 0 at 0.70 and at most about +/-0.45 (carrier) at the rating extremes. It IS a tendency (carrier weight 1.5 vs off-ball 0.5 shifts the mix with the rating) and should go, but it is not why Archers shoot. |
| Stuck drawn bow / duplicate continue_current | PLAUSIBLE | cognition.py ~681-706: when ready, hold option is continue_current at 0.0; if every release value < 0 the Archer keeps holding and archer_motor (rulebook/port.py ~262-271) waits for release_intent. Duplicate continue_current options when pending and not ready. |
| No flight-time lead | CONFIRMED | rulebook/port.py ~272: target = aim + aim_vel x (now - decided_ms); arrow flight (distance / 250 m/s) not added. |
| No freeze check at release | CONFIRMED | rulebook/archery.py ~53: only remaining[0] (arrows) is checked. |
| Unclamped decrement at period end | CONFIRMED | rulebook/archery.py ~40 `quotas[...]['arrows'] -= 1` (no max(0, ...)). |
| Arrow sweep has no team filter | CONFIRMED (intent unknown) | rulebook/archery.py arrows(): loops over active_field() for all players; whether teammates can be hit needs an owner ruling. |
| freezes_left assigned twice; single freeze scalar | CONFIRMED | rulebook/port.py ~237 and ~245. |
| Recommends point budget C (carrier 2, off-ball 1, 5 or 6 pts/period), release legality + impact cost, max draw hold | Design advice | Adopted as the trial plan pending owner approval. |
