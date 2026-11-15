# RB-1 ADDENDUM (CANON, ratified by DreLen 14 Nov 2026). Paste after the RB-1 block; it supersedes the placeholders there.

1. Timeout policy (replaces the PLACEHOLDER in R-T). Default team policy, deterministic, no PRISM cognition: a team with a timeout left calls one at the first dead ball where (a) the opponent has scored twice in a row without a reply, or (b) it is the last 60 s of period 4 or of overtime and the team is trailing or level. One timeout per trigger; never in sudden death.

2. Review standard (replaces the placeholder in R-O). A call stands unless the recorded engine state shows it wrong by MORE than 5 cm. Goal/no goal: distance the whole ball was inside or outside the goal plane and semicircle. Boundary: distance the ball or foot was beyond the line. Keeper immunity: whether the recorded contact was on an immune Keeper at all. Wrong by more than 5 cm: reverse and restart from the corrected result. Within 5 cm: the call stands and the team loses its challenge.

3. NEW R-I, injuries and substitutions.
- Substitutions only in a dead ball, within roster limits; unlimited; a substituted player may return; no clock stop, no timeout charged. Substitute is on the field before the next restart.
- Injury stoppage: referee stops play when a player cannot continue; dead ball, clocks stop, no timeout charged; the team may replace him at once, even during an exclusion window.
- Head/neck contact flagged by the referee: the player leaves for evaluation and cannot return that period; may return from the next period.
- Each team names one reserve Keeper. Keeper injured or disqualified: the reserve takes over; if none, a field player takes the Keeper position at the next dead ball.
- An excluded (foul) player cannot be replaced until the exclusion ends; an injury replacement is exempt from that.
- Archers are substituted at any dead ball and are outside the field roster limit.
- Engine source of injuries: PLACEHOLDER. Native has no injury model; implement the stoppage and substitution mechanics and a test hook that forces an injury or head-contact flag; do NOT invent a random injury model. Add to the V3 conformance tests and the V5 events table.
