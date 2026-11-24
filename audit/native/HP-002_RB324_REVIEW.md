# Review: RB-3.24 PRISM registry (codex/rb-3-24-prism-registry @ 3edfaad), 24 Nov 2026

Claude (lead reviewer). Status: verification TESTED; nothing ACCEPTED.

## Reproduced independently (fresh worktree at 3edfaad)
- Compatibility real seed 1: 57-76, 32,528 steps, trace 44399b08...c072, state 046ea55b...865d (gate d).
- Individuation on, all ratings 0.70, real bodies, seed 1: 35-29, 30,189 steps, trace 1678fcb5...5c51, state 46c87876...bf6e (= Codex evidence).
- Codex's evidence files agree with its report: neutral-real off 96-57 (147/145 possessions), on 35-29 (105/104); control off 55-79, on 42-28.

## Findings
1. Average players got worse. With every rating at 0.70 the hooks cut scoring from ~77 to ~32 per team. Possessions ending in an attempt fell from 15-22% to 8-12%. At d = 0 the new mechanisms (radar size, Focus capacity, Clarity noise and recognition errors, Reflex windows, Finishing aim, agent selection) are absolute changes, not individual differences.
2. Hard switches. Zone Coverage changes nothing below 0.80 and everything above, because a player compares it with his Defending (0.70). Finishing flips at 0.90. Lead's own default (player picks man vs area from his two ratings) caused the Zone switch.
3. Sweep counts any difference, not effect size: Anticipation and Instinct change their quantity by <0.1% yet flag 20/20 changes. Playmaking shows 0/120 in the sweep but works in the targeted threshold test (always carry at 0.40, always shoot at 1.00).
4. Little or no effect in scenario: Clarity (2/120), Tackling (4/120), Evasion (6/120). Mapped-only (no outcome): Ball Handling, Jump, Throw Accuracy, Throw Power.
5. Speed gate missed: 4.221 vs 3.543 ms/step (+19.1%).

## Decisions taken by lead (ENGINEERING / BEHAVIORAL)
- Calibration anchor: with all ratings at 0.70 the enabled game must stay inside the owner's ranges (75-90 per team, 100-150 possessions); ratings spread players around that game.
- Passing timing: Playmaking commits the decision to pass; Passing chooses when the release motion starts (it may wait, capped at one Reaction interval), plus lane, speed and arc. Once the motion starts, Ball Handling's clock runs and cannot be extended.
- Man vs area choice becomes a smooth, situational choice, not a hard comparison of two ratings.

## Owner question
- Stretch as its own rated maneuver (recommended: yes).
