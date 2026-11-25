# Review: RB-3.28 in-match fatigue and rotation (codex/rb-3-28-fatigue-rotation @ 49447ae), 25 Nov 2026

Claude (lead reviewer). Status: verification TESTED; nothing ACCEPTED.

## Reproduced independently (fresh worktree at 49447ae)
- Fatigue ON, ratings 0.4, Garvian vs Ala seed 1: 85-86, 32,761 steps, trace a399f74f...ac4b, state bc4898a8...61d4 (= replay-1.json).
- Soak table recomputed from evidence/matches.csv: OFF median 89.5, sd 19.9, possessions 153.2, median |margin| 29.5, 2/20 within 5, Ala-Garvian +27.0 (SE 5.8); ON median 85.5, sd 20.6, possessions 146.5, median |margin| 23.0, 2/20 within 5, Ala-Garvian +37.3 (SE 6.8), 135.5 fatigue substitutions per team per game.

## Findings
1. Minutes target met: field starters 32.35 of 40 (25.9-38.0); Keepers 40; Archers not rotated.
2. Substitution churn: about 136 fatigue substitutions per team per game, one every ~18 s of play; each field starter cycles about 7 times (stints of ~4-5 min, rests of ~1-1.5 min). Cause: held sprint reaches 0.6 in 69-89 s and bench recovery 0.60 -> 0.75 takes 94 s, so the 0.6 / 0.75 thresholds cycle quickly. The ratio sets minutes; the absolute rates set frequency.
3. Depth now matters: Ala's lead grows from +27 to +37.
4. Volatility unchanged: team score SD about 20 vs 12.7 (NBL 25-26); 10% of games within 5 vs 23%. Within the same matchup (Ala-Garvian, 10 seeds) the margin varies by about 21 points game to game, so chance alone exceeds the pro league's whole spread.

## Recommended
- Owner: choose a substitution rhythm (typical stint length). Then scale drain and bench recovery together (same ratio keeps 32 minutes).
- Next diagnosis: per-possession scoring variance (points per possession distribution, share from 5-point carries, possession count) to find what makes single games so swingy.
