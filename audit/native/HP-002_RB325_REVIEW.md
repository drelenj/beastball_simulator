# Review: RB-3.25 PRISM CORE (codex/rb-3-25-prism-core @ 2612256), 24 Nov 2026

Claude (lead reviewer). Status: verification TESTED; nothing ACCEPTED.

## Reproduced independently (fresh worktree at 2612256)
- Compatibility real seed 1: 57-76, 32,528 steps, trace 44399b08...c072, state 046ea55b...865d (gate d).
- CORE, all ratings 0.70, real bodies (Garvian A vs Ala B), seed 1: 87-79, 32,483 steps, trace 317d40ba...7b01, state 26d9d339...85ef (= Codex evidence).
- Evidence files agree with the report: real seeds 1-5 scores 87-79, 99-63, 68-116, 71-123, 70-88 (pooled median 83); control seed 1 72-78 (repeat identical); possessions 137-147 per team; share of possessions ending in an attempt 29-45%.

## Findings
1. PRISM I is structurally complete per the RB-3.25 stop line: option menus with symmetric decision error (half-width 0.75 x (1 - r)), every rating hooked, 0.70 game inside the owner's ranges, gates a-e pass (speed +8.6%).
2. Large spread with identical ratings: Ala minus Garvian margins -8, -36, +48, +52, +18 (bodies and chance only). Consistent with RB-3.22 (both-neutral Ala +29 over 10 seeds). Five seeds cannot size it.
3. Shot option offset -1.40 is a flat hand-set penalty used to bring scores into range. Provisional; DRILL must replace it.
4. Reaction moves in steps because decision times snap to the 100 ms tick. Engineering fix: carry the fractional remainder between decisions.
5. Instinct (and Stamina in its scenario) under 2% effect.
6. 0.70 anchoring re-centred Reaction, Focus, Reflex and Anticipation so 0.70 equals the old behaviour; Awareness and Contact Resistance are fixed at 0.70 inside the physical kernels.

## Recommended
Owner: accept RB-3.25 as the PRISM CORE baseline with individuation opt-in (provisional values). Next: lead regenerates ratings in the registry's names; ORACLE scenario harness, then DRILL on the checkpoint's "Needs ORACLE DRILL" list; small fix for Reaction tick snapping.
