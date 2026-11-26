# Review: RB-3.32 paired behavioural fixes (codex/rb-3-32-paired-fixes @ 33c932b), 26 Nov 2026

Claude (lead reviewer). Status: paired interception and boundary results re-derived from the per-game records (18 common games: Garvian-Ala 1-10, Yukima-Isu'Kari 1-5, Moonhawks-Ala 1-3); hashes not re-run. Nothing ACCEPTED. Run stopped early by the owner (lead advice): event-level measures only.

## Re-derived (ON minus OFF, per team per game, paired)
- Interceptions: Pass Clearance -11.64, Boundary Guard -4.75, Combined -13.11 (OFF mean 53.2).
- Boundary turnovers: Pass Clearance -0.64, Boundary Guard -8.08, Combined -11.64 (OFF mean 31.4).
Matches Codex.

## Findings
1. Each fix moves its own target: Pass Clearance cuts interceptions by a fifth (players decline about 25 passes a game); Boundary Guard cuts out-of-bounds by a quarter; Carry Finish adds about 2.3 carry goals per team per game and the first stretch goals; Fresh Takedown cuts non-carrier commitments by about 13 points of share.
2. Interceptions remain about 40 per team per game with all fixes: consistent with the confirmed engine causes (0.4 s pass flight, unused receiver head start, hidden movement clock).
3. Keepers unchanged (about 15%). Reach audit: only 312 of 1,218 on-target shots were inside the Keeper's reachable envelope; he saved 150 of those (48%). The latency stack, not willingness, limits saves.
4. Fresh Takedown lowers success after an actual hold slightly (-1.8 pp alone, -0.25 pp combined, within noise).
5. Combined (not judged): median team score 98, possessions 137.6 (-14).

## Decision (lead, BEHAVIORAL)
All four fixes ON together become the starting point for RB-3.33, which fixes the confirmed engine bugs, applies carry 7 and the goal-mouth canon, and is judged on 200+ games.
