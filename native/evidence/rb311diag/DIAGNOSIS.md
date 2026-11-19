# RB-3.11 Part B: possession diagnosis on RB-3.10 (diagnosis only)

Claude (lead/reviewer), 19 Nov 2026. Branch `claude/rb-3-11-diagnosis` from `claude/rb-3-10-formation-hold` @ 45a298c. No engine, rule, cognition or constant was changed. Measurements are TESTED (reproducible from logs); recommendations are DESIGN COMPLETE only. Nothing is ACCEPTED.

## OWNER BRIEFING
1. **Accomplished.** Possession-end diagnosis of RB-3.10 on real seeds 1, 3, 5 and control seed 1. A read-only observer re-ran all four matches; every re-run reproduced the RB-3.10 trace and state hashes exactly.
2. **What it shows.** Possessions are short (median 4.5 s of live time; ~214 per team) because the offense gives the ball away, not because the defense or the rules force it:
   - **Catch-and-pass offense.** A carrier holds the ball a median 0.8 s, moves at a mean 2.5 m/s, gains a median 0.6 m, and passes. About 900 passes per match; 43% backward, 20% forward. Open-play passes fail 24-34%. Passes that go astray end about 40% of possessions.
   - **Scrimmage leak, then second tackle.** 47% of scrimmage snaps are caught by a teammate standing at the edge of the 2 m snap corridor, after 0.5 m of travel, not by the designated receiver. After a first tackle, 52% of scrimmages end in a second tackle (turnover) a median 2.5 s after the snap, for a median gain of 2 m. Second tackles end 20% of possessions (28% in control).
   - **Weak finish.** 29% of possessions reach the Keeper Zone edge. 378 of 501 entries stop short after 0.8 s with nobody within 5 m. Shots: all from inside 20 m, 21% scored; no long throws for the 4-point band.
3. **Unproven.** Fix effects are estimates. Four matches only. One unverified side observation: player speeds in general look modest against canon top speed (rating x 44.7 m/s); needs its own engine check.
4. **Blocking.** Nothing. No canon question blocks these fixes.
5. **Recommended action.** Build E-3 (wide snap corridor) and B-5 (carry/pass valuation) first, measure, then B-6 and B-7.

## Top causes (real rosters, 1,281 possessions in 3 matches; control in brackets)

### 1. Passes thrown away (about 40% of possessions) - BEHAVIORAL
- Possession ends: pass intercepted or loose 28.5% [30.4%], pass out of bounds off own team 11.2% [12.1%].
- 4,063 ball holds: median hold 0.8 s, median forward gain 0.58 m; 67% end in a pass with median gain 0.02 m. Observer: carrier mean speed 2.2-2.8 m/s, peak 4.0-4.9 m/s.
- 2,732 passes (2.1 per possession, ~910 per match). Direction in open play: backward 585, lateral 448, forward 380. Fail rate (intercepted or out): backward 24%, lateral 27%, forward 34%; post-snap 10-19%. 1,032 passes (38%) are caught by a teammate other than the target.
- Decision values in the carrier log: pass options ~6.4-6.9, carry ~2.0. Pass wins as soon as a pass decision is available.
- Carrying is legal canon ("the ball is thrown or carried"); dribble rule unrelated. So this is decision valuation.

### 2. Scrimmage snap leak and the second tackle (20% of possessions [28%]) - ENGINEERING + BEHAVIORAL
- 924 scrimmage snaps (non-snap40): designated receiver first touch 477 (median 3.6 m of travel); a teammate first touch 435 (median 0.5 m of travel, lateral offset exactly 2.0 m); opponent 12. Control: 179 / 166 / 11.
- Cause: `native/rulebook/formation.py` places any offense player inside the snap corridor exactly on y = 50 +/- LANE_HALF_WIDTH_M (2 m), and places offense 1 m behind the line, so teammates stand within catching reach of the snap. The owner ruled the lane clear; the implementation does not achieve it.
- After a first-tackle scrimmage (467): second tackle 243 (52%), possession lost otherwise 143, other award 70, goal 11. Passes after the snap: 564 backward or level, 149 forward. Second-tackle victim: snapper 83, receiver 42, other 118. Median gain from the line 2.0 m (quartiles 0, 2, 5.6), median 2.5 s after the snap.

### 3. Weak finishing near goal (attempts 13-22% of possessions; target ~50%) - BEHAVIORAL
- 702 possessions reach the opposing 40; 517 get within 32 m; 368 reach the zone edge.
- 501 zone entries by a carrier: median start 19.4 m from goal, carry 3.3 m over 0.8 s, median 0 defenders within 5 m at entry; outcomes stopped short 378, grounded 69, turnover 46, goal 8. Near-goal choices (<20 m): carry 482, shoot 226, pass 112.
- 199 shots, median 11.5 m: under 10 m 29% scored, 10-15 m 19%, 15-20 m 0%; none beyond 20 m. Defence recovers 60%.

### Not the main cause
- Arrows: 1.2 arrows and 0.37 freezes per possession; carrier freezes end 4.4% of possessions.
- Zone rules end 5.8% of possessions (being addressed by RB-3.11 Part A).
- Restart throws lost 5.1% (down from ~36% before the formation).

## Recommended fixes (DESIGN COMPLETE, not implemented)
| ID | Class | Fix | Evidence | Expected effect | Risk |
|---|---|---|---|---|---|
| E-3 | ENGINEERING | Snap corridor half-width larger than the widest catch reach on the field plus a margin; place displaced players clear of it in depth too | 435 of 924 snaps taken at the 2.0 m corridor edge | Snap reaches the designated receiver as ruled; ends the 0.5 m catches | Low |
| B-5 | BEHAVIORAL | Carry/pass valuation: value carrying by expected ground gained under current pressure; pass only when it gains ground, escapes pressure or sets up a shot; backward or lateral passes only under pressure; commit to a carry for a minimum time unless pressured | Pass ~6.5 vs carry ~2.0; 0.8 s holds, 0.02 m gain; 910 passes/match; 19.8% pass failure | Far fewer passes and pass turnovers; longer possessions; more ground gained | Over-carrying into tackles; needs measurement |
| B-6 | BEHAVIORAL | Scrimmage spacing and post-snap play: offense spread in width and depth instead of 1 m behind the line; receiver's default is to run to space or pass forward, not back to the line | 52% of first-tackle scrimmages end in a second tackle; median gain 2 m | Fewer second-tackle turnovers | Overlaps B-5 |
| B-7 | BEHAVIORAL | Finishing: check why the RB-3.9 unopposed-carrier rule rarely fires (378 stops with 0 defenders within 5 m); shot selection to use the 10-20 m (3 pt) and 20 m+ (4 pt) bands | 8 carry goals from 501 entries; no 20 m+ shots | More attempts and points per attempt | Long shots convert worse |
| E-4 | ENGINEERING (Codex) | Check achieved player speeds against canon top speed (rating x 44.704 m/s) | Unverified: carriers peak under 5 m/s | Rules out a physics cap behind cause 1 | None |

Order: E-3 and B-5 together, measure; then B-6; then B-7.

## Reproduce
- Raw logs: `native/evidence/rb310/runs/{real,control}/raw-*-seedNN.json` (gzip copies used under `soak/`, not committed).
- Observer: `tools/observe.py --block real --seed N --out observe` (BB_REPO env for the repo path); outputs `observe/observe-*.json.gz` with hashes.
- Tables: `PARTB_TABLES.txt`, `offense_diagnosis.json`; scripts in `tools/` (post_snap.py, snap_chain.py, pass_ctx.py, holds.py, shots_passes.py, carrier_motion.py, offense_diagnosis.py).
