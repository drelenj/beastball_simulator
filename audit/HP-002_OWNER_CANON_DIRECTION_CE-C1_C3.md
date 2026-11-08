# HP-002 — Owner canon direction on CE-C1, CE-C2, CE-C3 and how it is applied
Claude, 2026-11-08. Records DreLen's direction and my derivation. **Non-governing record**: rc2 (sha a95cdb05…) and manifest v2 are unchanged until a formally approved governing revision. Contract v1 NOT FROZEN; B1 implementation NOT AUTHORIZED; B0 frozen.

## 1. Owner direction (verbatim)
- CE-C1: "use Basketball jump shot rules as base"
- CE-C2: "use nba rules as a base"
- CE-C3: "the illegal arrows spend ammunition. It counts as soon as the arrow is released and free from the bow. So you can abort a draw"

## 2. NBA text I relied on (official.nba.com, fetched 2026-11-08)
- Rule 13 (replay): game clock review asks "whether time on the game clock expired **before** the ball left the shooter's hand" (Sec. II, item 1), and another item asks whether the ball left the hand "**prior to** the expiration of actual time" (Sec. II, item 5(2)).
- Rule 6 Sec. IV, item 1.4: the ball becomes dead when time expires for the end of a period, **except** that a field goal attempt in flight stays live until it is made, missed or touched by an offensive player.
- Rule 8 Sec. I: a player is out of bounds when touching the floor or any object on or outside a boundary; an airborne player's position is where he last touched the floor. Sec. II: the ball is out of bounds when it touches an out-of-bounds player, the floor, or any object on, above or outside a boundary; the last toucher causes it to go out.
- Not covered by the pages I read: a catch while touching a boundary, and an exact simultaneous release and expiry.

## 3. CE-C1 (clock expiry vs release): resolved at principle level
Derived rule [ruleset-versioned, `tie_rule` slot filled]:
1. A **goal attempt (shot)** counts as released if the ball left the shooter's hand before the clock expired.
2. A shot already in flight when time expires stays live until made, missed or touched by an offensive player.
3. A **release that has not left the hand** at expiry does not count; the ball is dead at expiry.
**Residual (exact tie).** The two NBA formulations differ on a release at the very same instant ("expired before it left" versus "left prior to expiry"). B0 orders release before clock, which matches the first. My recommended default is that an exact-instant release **counts**. This is a one-line tie default, not a new question; tell me if you want the other reading.
**Scope assumption.** I applied this to shots only. For a pass, kick or arrow at expiry I assume the ball is dead at expiry with no flight exception. Say so if arrows in flight should survive expiry.

## 4. CE-C2 (goal/boundary crossing vs secure catch): resolved at principle level
- **Boundary.** The NBA player-location rule replaces most "ties": an athlete's position is where they last touched the floor, and the ball is out only by touching an out-of-bounds athlete, the floor or line outside, or an object on or outside the boundary. Airspace does not put it out. A secure catch by an athlete located in bounds is valid even if the ball is in airspace over the line. An exact same-instant ball-touch of out-of-bounds floor and in-bounds secure hold: **the ball is out** (a ball touch of the boundary stands independently of possession). B0 agrees: `boundary` is priority 4, before `acquire` at 10.
- **Goal.** The NBA principle (a touch cannot prevent a scoring ball from counting) fits B0: when a goal and a secure catch coincide on a scoring ball, B0 restores the scoring-shot state, dispatches the goal and un-snaps the catches. Proposed B1 rule: **the goal stands**. A Keeper catch that starts before the ball crosses is a save; at an exact instant, the goal counts.
- **Residual.** The NBA has no hoop-free-goal analog for Keeper saves, so I used the B0-consistent rule above. NBA also resolves a simultaneous last touch out of bounds with a jump ball; Beastball's own restart (RST-1) is not changed by this direction and I did not import the jump ball.

## 5. CE-C3 (Archer ammunition): resolved
Owner direction, applied:
1. **Ammunition is spent at the instant the arrow is released and free of the bow.** That instant is the Archer's commitment event (`arrow_released_free_of_bow`).
2. **An illegal arrow still spends ammunition.** Legality is a rules judgment on a completed release; it does not refund ammo.
3. **A draw can be aborted** before release, with **no ammunition spent**. Draw is therefore revocable; only release commits.
**Effect on B0 comparison.** B0 decrements ammo at the start of `shoot_arrow` and then rejects an illegal arrow before creating it (lines 1756-1777), so ammo is spent with no Arrow object. That is consistent with items 1-2 for accounting. B0 had no draw abort (a draw could only be dropped on mismatch).
**Effect on the design.**
- The O4 v3 Archer rows are resolved: draw abortable, no ammo cost; release atomic with ammo spend.
- Legality checks (live ball, lane, target, speed, rate of fire) become **rules outcomes after release**, not Motor Control rejections. MC only refuses what is physically infeasible, such as no arrow loaded or draw not complete.
- Ammo spend and arrow-release event are one atomic transaction, so a legality classification can never refund or precede it.
**Residuals (derived mapping; correct me if wrong).**
- (a) Does an illegal arrow **fly and can it hit**, or is it nullified at release (as B0 does: no Arrow object, an illegal call, ammo spent)? Default: keep B0's nullification.
- (b) I treat the 2-second rate-of-fire limit and the reload gap as **legality** (arrow released, spent, called illegal), as in B0, not as a physical block on release.

## 6. Net effect on open items
| Item | Before | After |
|---|---|---|
| CE-C1 | UNRESOLVED_CANON | RESOLVED at principle level; one exact-tie default stated |
| CE-C2 | UNRESOLVED_CANON | RESOLVED at principle level; goal and boundary rules stated |
| CE-C3 | UNRESOLVED_CANON | RESOLVED; Archer draw abortable; ammo at release |
| Contract v1 freeze gate | U-1..U-4, R-RS | unchanged; U-1..U-4 and R-RS remain open |
| Governing documents | rc2 | not yet revised; direction recorded here and in O4 v3 rev 2 |
