# Review: RB-3.30 planned rotation, tackle credit, named box scores (codex/rb-3-30-planned-rotation @ f910ebe), 25 Nov 2026

Claude (lead reviewer). Status: numbers re-derived from evidence/matches.csv and the named box score; hashes not re-run by the lead (Codex reports all gates and a fresh-process replay). Nothing ACCEPTED.

## Re-derived (30 games)
Median team score 90.5; team score SD 17.2; possessions 151.0; median absolute margin 18; 10% of games within 5; Ala - Garvian +16.8 (SE 6.6), 8/10. Matches Codex.
Planned seed-1 box score: names, franchises and legacy positions present; tackles made / attempted: Garvian 50/193 (26%), Ala 31/120 (26%); top: Darius Ironstrike (GRD) 8/19.

## Findings
1. Planned rotation works: starters 31.9 min (28.1-34.5), ~39 planned and ~4.6 override substitutions per team per game (2.6 exits at the 0.52 fatigue scale).
2. Swing improving: SD 17.2 (from ~20), median margin 18 (from 23-26); still above NBL reference (12.7, 13). Close games still 10% (23% reference).
3. Canon discrepancy: the Native engine plays 11 field players plus a Keeper per side (field_roster_limit 12, Archer separate); B1 / Sprint 30 used 10 field. The owner's statement on record is a "10v10 field game". The lead's block assumed 10 starters, so one field player sits outside the plan.
4. Tackle success is about 26% of committed takedown attempts (real rugby and gridiron: roughly 80-90%). Possibly linked to scoring levels; needs a look.
5. Some box-score rows have no legacy position (filled reserves).

## Owner decisions
- Field players per side: 10 or 11?
- (Open) 4-point band test.
