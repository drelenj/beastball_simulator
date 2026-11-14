# HP-002: owner canon rulings of 2026-11-14 (standard game)
Claude, 2026-11-14. Records DreLen's statements of 14 Nov 2026 (00:16 and 00:32 America/Chicago). Status: **CANON (owner-stated)**. Nothing here is implemented, tested or accepted. The full reference is the doc "Beastball Standard Game: Flow and Stable Rules"; this file is the repository record of what was ruled.

## OWNER BRIEFING
1. **Accomplished.** The standard-game structure and seven rules are now recorded as canon, and five open questions from the first draft are answered.
2. **What B1 can do now.** No change. The `experiment-v1` profile (branch `claude/experiment-profile-v1`) already runs flat scoring, 5 m marking, no kicking. It does not yet run the 30 s clock, the whole-period first overtime, sudden death with half goals, the 3 m semicircular goal or the 5 m platform: IMPLEMENTED = none of these.
3. **Unproven or unbuilt.** Everything below is DESIGN COMPLETE only, except the goal and platform geometry which still need the engine values checked against it.
4. **Blocking.** No canon question blocks the next step.
5. **Recommended action.** Codex implements the clock, overtime and geometry changes in the B1 path.

## 1. Rulings
| ID | Ruling | Replaces |
| --- | --- | --- |
| S-1 | Regulation is four periods of 600 s | none |
| S-2 | First hunt opens the match (and each period, per v0.3) | none |
| S-3 | Scrimmages follow tackles and scores | none |
| S-4 | First overtime is half length (300 s) and **runs the whole period**; same rules as regulation overtime | none |
| S-5 | Later overtimes are sudden death. **A half goal can win sudden death** | none |
| S-6 | Goal: semicircle of radius 3 m in front view (6 m wide, 3 m high); quadrant of radius 3 m in side view | v0.3 note that "6 m" is net width only |
| S-7 | Archer platform is 5 m high and **5 m back from the boundary / goal plane** | 15 m working default |
| S-8 | No kicking. One dribble per player's possession; it resets on a stoppage and when another player touches the ball | v0.3 [R] dribble reading |
| S-9 | 5 m marking; Keeper immunity as ruled (D1 KP-13) | none |
| S-10 | Scoring is flat (any goal 2, half goal 1) until the self-play experiment reports; the standard scoring is decided after it | none |
| S-11 | **Standard play clock is 30 s. Expiry is a turnover** | 45 s possession clock |
| S-13 | A defensive minor foul at tackle count 0 is a **full goal in the fourth period and in all overtime** (half goal in periods 1 to 3). Ruled 00:47, resolves O-1 | v0.3 wording kept, now explicit for sudden death |
| S-12 | All specific timing, distance, location and boundary rulings for violations stand as in RULES_FLOW v0.3 and the D1 record, except where S-1..S-11 change them | none |

## 2. Consequences I derived (READING, not yet confirmed)
- C-1: on expiry the other team restarts with a scrimmage at the spot or its own 40 m line, whichever is closer to the goal it attacks (same as any turnover).
- C-2: the fresh clock after a score or turnover is 30 s, and the 30 s carries through a tackle as the 45 s did.

## 3. Open (owner)
O-1 is closed by S-13. Note: with full-goal awards in all overtime, a half goal cannot arise from a foul in sudden death, so S-5's "a half goal can win sudden death" has no source unless half goals come from somewhere else. Not blocking; tell me if S-5 meant something more.
| ID | Question | Recommended default |
| --- | --- | --- |
| O-2..O-10 (nine open in the doc) | Archers per goal, overtime opening hunt, dribble stoppage and penalty, boundary rule ratification, breaks and timeouts, what counts as a goal, defensive offside at count 0, hunt violations (see the doc) | defaults in the doc |
