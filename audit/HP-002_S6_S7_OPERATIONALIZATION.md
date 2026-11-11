# HP-002 — S6 and S7 operationalization (no new rule content)
Claude, 2026-11-11. Non-governing. This turns the owner's approved S6 and S7 into executable wording and cites the rule sources I could audit. rc2 and manifest v2 unchanged; Contract v1 NOT FROZEN.

## 1. Sources audited
| Source | What it is | Limits |
|---|---|---|
| `RULES_FLOW_v0.3.md` (sha256 `d970ea9a…`) | The working rules flow, tagged [C] canon stated by DreLen, [R] my reading, [P] provisional, [E] engine. Dated 1 Nov 2026 | Switch `RULES_V03` is off in B0-P4-DEFAULT. Which ruleset B1 runs under is still **R-RS (open)** |
| `RESTARTS_NOTES.md` (sha256 `0c9afe8b…`) | Restart and Hunt rule notes | Notes, not a rulebook |
| B0 monolith `foul()` (lines 1935-2000) | What the historical engine does | Evidence, not canon |
| The rulebook the code cites ("rulebook 11.2, 11.3, 1.4, 18.6, 18.8") | External numbered rulebook | **Not in the repository; I could not read it** |
I did not find a rulebook text in the repository. What follows rests on `RULES_FLOW_v0.3.md` [C] items and B0 behavior, and I say so wherever it matters.

## 2. S6: consequences of an illegal arrow
**Approved by the owner:** ammunition spent, illegal call, minor foul. The arrow is by the defending team's Archer, so the foul is **by the defence**.
| Ruleset | Consequence of a minor foul by the defence | Source |
|---|---|---|
| RULES_FLOW v0.3 (if adopted for B1, R-RS open) | Tackle count −1 (floor 0). If the count is already 0, the offence is awarded half a goal in Q1–Q3 and a full goal in Q4 and overtime, and keeps possession. After an award the offence restarts with a scrimmage at the ball or foul spot, whichever is closer to the goal it attacks; tackle count stays 0. Player discipline: the 4th minor is a 60 s game-time exclusion, the 5th disqualification (counts per player). | `RULES_FLOW_v0.3.md` "Minor fouls" [C] and "Major fouls and discipline" [C]; restart sentence [C], tackle-count-stays-0 [R] |
| B0 ruleset 1.0.1 (historical) | Stoppage; the other team is awarded the ball at the ball spot (or the victim's spot if closer to the goal it attacks); minor discipline. B0 `illegal()` does not request advantage. | B0 `foul()` and `illegal()` (monolith 1931-2002) |
**Result.** The restart, scoring and clock consequences of the illegal-arrow minor foul are *the ruleset's minor-foul rule*, fully specified for v0.3 by [C] text and for B0 by engine code. They are not invented here, and they depend on **R-RS**, which is already an open owner item.
**One gap I cannot close from the repository:** *advantage* for an Archer foul. v0.3 is silent, and B0 does not apply advantage to an illegal arrow. Recommended default: no advantage (B0 behavior). If the external rulebook says otherwise, it returns to the owner.

## 3. S7: normalized wording (editorial; owner intent unchanged)
The phrase "not live" is retired because it could name the same state S7 says blocks a release.
- **B1, pre-release blocker:** authoritative `play_state = stopped`, already effective in the common pre-event snapshot, blocks the release. No arrow is released and no ammunition is spent.
- **B1, post-release legality:** a distinct legality condition first effective at or after the physical release is evaluated afterward. Ammunition stays spent (the illegal-arrow rule, S5/S6).
- **B0 adapter:** preserves the legacy spend-before-`not_live`-check ordering independently (monolith 1756-1777).
**Hunt rule, an existing explicit rule that S7 must not contradict.** `RESTARTS_NOTES.md`: "Archers cannot draw or fire until the ball has left the centre circle (blocked at the decision and at the shot; nothing drawn, no ammunition spent, no foul)." B0 gates the same way at the decision (`arrow_decisions`, monolith ~3757-3760: no draw when the ball is not live or has no owner). I read this as a member of the `play_state = stopped` family for Archers: it blocks before release, spends nothing and draws no foul, which is exactly the S7 pre-release behavior. I record it under the A3 blocker list. If DreLen reads S7 differently, it returns to him.

## 4. What changes in the drafts
O4 v3.5 §4a carries this wording. A2 is now stated by reference to the ruleset's minor-foul rule, not by my summary.
