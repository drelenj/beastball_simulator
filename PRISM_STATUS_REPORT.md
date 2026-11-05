# PRISM I status report (for Codex test protocol) — 2026-11-05

Design rule: top-down. Physics-based athletes, ratings are the only knobs, no independent minds. Ratings 0–1 (40–100 display), 0.70 = league average.

## 1. What exists now (all env-flag gated; `PRISM_I=1` turns on the base set)
| Layer | Flag | State |
|---|---|---|
| Per-player perception tick (cone, radar, latency, beliefs) | PRISM_I | working, 8 core ratings |
| Field-player decisions on beliefs (defence pursuit, bounded error, maneuvers) | PRISM_FIELD/DEF/BOUNDED/MANEUVERS | working |
| Off-ball target decisions on beliefs | PRISM_OFFBALL | working |
| **Teammate perception** (all players inside vision/awareness; unseen mates held at stale belief; voice-call channel 35 m, .25 s lag, 1.5 s TTL) | PRISM_TEAMVIEW | NEW, working |
| **Free-ball perception** (loose + in-air ball via beliefs and engine `predict_path`) | PRISM_FREEVIEW | NEW, working |
| **Split Judgement ratings** (9, see §2) | PRISM_JSPLIT | NEW, hooks in; see caveats |
| **Off-ball actions**: RUN_OPEN, ENGAGE, CALL, WAIT, FREE_BALL | PRISM_OFFACT | NEW, working; scoring is placeholder |
| **Off-ball hand fighting** (4-pillar contest, push/jockey legal, contact band, grip fouls, blindside fouls) | HAND_FIGHT | NEW, working |
| Keeper on full PRISM; catch v2; PRISM jump decision; four-pillar ball hand contest | PRISM_KEEPER, CATCH_V2 | working |

## 2. Judgement ratings and where each acts
Playmaking → pass ranking noise + option value (pocket_decide). Finishing → shoot/carry value noise (pocket_decide). Marking → individual-defender target judgement. Zone Reads → held spatial-offset noise for zone defenders. Goalkeeping → keeper judgement (replaces `judgment` for keepers). In-Air Pursuit → pass tracking/contest (free-ball plan when ball is passed, z>.3). Live Pursuit → loose ground-ball tracking. Carrier Duel → maneuver-choice noise (pose engine). Defender Duel → contain/region flip probability. `judgment` = mean of the nine unless authored.

## 3. Evidence so far (scenario labs, N≈12–30, small)
- Live Pursuit .40/.70/.98: secured 25/29/30 of 30.
- In-Air Pursuit .40/.70/.98: secured 10/13/21 of 30; time 2.9/2.2/1.6 s.
- Goalkeeping .40/.70/.98 (45 m/s drill): goals 42/41/34 of 42.
- Playmaking .40 vs .98: best option first .45 vs .63.
- Finishing .40 vs .98: shoots 9/16 vs 2/16 (low finishers take more speculative shots; conversion effect not yet shown — goals 0/16 both).
- Calls: 493 calls, heard 4782; first-pass target shifts toward the caller.
- Open space: actions raise openness 4.0 → ~8.5–8.9 m in 4 s (no judgement separation yet).
- Hand-fight: probes run, fouls controlled after the gap/closing fix.

## 4. Known gaps / caveats (be honest in the protocol)
1. Carrier-vs-Defender duel lab is saturated (P(stopped)=1.00 everywhere) — geometry must be redone before any duel claim. Code path exists, effect unverified.
2. ENGAGE is rarely chosen (2 of ~600 actions); action scoring constants are placeholders, noise strengths are [P] (provisional).
3. Marking and Zone Reads have hooks but no dedicated effect test yet.
4. Contact band (below neck/above hip) and grip fouls are implemented but not validated at match level.
5. No match-level paired comparisons run on the full stack (≈4–5× slower per game).
6. Kick-off prior leaks true teammate positions (`mate_prior_true` counter) until first sighting.
7. `judge_opts` Finishing/Playmaking noise is only wired into Pocket 2.0 `pocket_decide` (fixed today); the legacy `c4c2_decide` rep is dead code.
8. A stale-state bug (S.fowner) that disabled perception in later matches of one process is fixed; labs run before that fix that ran several matches per process should be re-run.
9. Not built: swat/strip inside fights, ENGAGE as belief-based decision, PRISM II (MESH).

## 5. Test-ready state (target)
Ready when: duel lab redesigned and showing monotone Carrier/Defender Duel effects; Marking and Zone Reads effect tests; ≥8-game paired match comparison per arm showing no collapse (fouls, scores, pace); contact band checked in match logs; docs updated. DreLen owns calibration of noise strengths; archetype runs start after items 1–3 with PRISM I alone. PRISM II (MESH: first message = warning about unseen approaching opponent) follows once teammate perception is stable.

## 6. How to run
`INLINE=1 N=30 python3 offball_scenarios.py free_ball air_ball open_space call engage`; `N=16 INLINE=1 python3 judge_labs.py finishing playmaking duel`; `python3 gk_sweep.py`; `python3 hf_probe.py`. Flags default on in the scenario harness (PRISM_OFFACT/I/OFFBALL/TEAMVIEW/FREEVIEW/JSPLIT/CATCH_V2/KEEPER/HAND_FIGHT).
