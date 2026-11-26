# HP-002: RB-3.34 review (Claude, 26 Nov 2026)

Reviewed `codex/rb-3-34-carry-value` @ 9d4de6d1630ff23690fabf3e030259f996f5fa1e.

- Code: the carrier valuation matches the fix spec (route 7 x P, continuation 1.55 x 7/5 x sigmoid, shots in the
  RB-3.32 expected-value form with rulebook bands, stretch 5.25). Diff is 65 lines, switch-gated.
- Independent rerun: A6 seed 1 61-105, trace 2437b808...6aee, state e10536f2...eeaa, digest c6dfe491...bd44. Matches.
- Status: IMPLEMENTED, TESTED (5 games). Fit for a judgment soak as the corrected-build baseline (not acceptance).

## A6, 5 games (Garvian-Ala 1-5), per team per game
Points 95.2 (owner range 75-90); possessions 155.1 (range 80-110); carry goals 2.6 (18.2 points, 19% of scoring);
interceptions 33.7; out of bounds 35.9; fumbles 16.9; Keeper save rate about 13-17% by band; Ala minus Garvian
+56.8 (RB-3.32 18-game Garvian-Ala figure was about +24-26). Near-goal menu: shot 19.5%, route carry 14.5%,
continuation 65.7%, stretch 0.3%.

## Open findings (for the next build, not blocking the soak)
1. Possessions about 1.5x the owner ceiling: roughly 85 losses per team per game from interceptions, boundary and
   fumbles alone.
2. Keeper: the settle target itself moves at P50 about 2 m/s (above keeper_set_mps 1.5), so the Keeper is "unset"
   on 31-51% of shots. Options: (a) behaviour, plant on a believed shot wind-up (within canon); (b) scale the
   1.5 m/s set threshold to league speed (athletes run 44.704 x rating = 31.3 m/s at .70, about 3x human), which is
   a Keeper-only constant and needs the owner.
3. Phantom takedowns: 30.6% of commitments. 478 of 1,338 non-carrier episodes have no believed holder at all, and
   many fire about 382 ms after a release. The PRISM menu gates wrap and takedown on the believed holder, so the
   likely path is the legacy `RB.defender_baseline` after the menu (PLAUSIBLE, not traced). 535 are stale beliefs
   (frame age 200-300 ms at 31 m/s play speed).
4. Ala's margin roughly doubled versus RB-3.32. The soak's 100 random pairings will show whether skill gaps are
   amplified league-wide.
