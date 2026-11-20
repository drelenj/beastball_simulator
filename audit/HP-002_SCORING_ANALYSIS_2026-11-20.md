# HP-002 scoring analysis (20 Nov 2026)

Claude (lead). Status: analysis TESTED (reproducible from the scripts and logs below); recommendations DESIGN COMPLETE only. Nothing is ACCEPTED.

## OWNER BRIEFING
1. **Accomplished.** Score targets taken from your two pro season logs. The simulator's scoring gap measured on RB-3.10, RB-3.12 and RB-3.13 (real seeds 1, 3, 5).
2. **What it shows.** Pro teams score 78 a game (NBL men's) and 86 (MBL women's), matching T3 (80-85 per team). The simulator scores 26-45 per team. Attempts are not the problem: teams already make 38-82 attempts a game (target ~50). **Conversion is:** 0.55-0.82 points per attempt against the ~1.56 needed. Shots score 9-17%. The keeper takes 27-48% of shots and field defenders 24-38%. Even on a clear lane the keeper stops about two in three. The shooter aims within 1 m of the goal centre, about where the keeper stands, on a goal 6 m wide.
3. **Unproven.** Fix effects are estimates. No play-by-play exists in the pro logs, so the split of points between carries and throws is not known.
4. **Blocking.** Two canon confirmations (below). No build blocks on them.
5. **Recommended action.** Fix shot quality first (aim, lane, keeper read), then replace hand-set carrier weights with expected points calibrated from logs.

**Correction.** Earlier reviews quoted T3 as an 80-85 *combined* total. T3 is an average **team** score of 80-85 (audit/HP-002_IDEAL_BEASTBALL_TARGETS_v0.md, line 12). Earlier statements that RB-3.12 was "close to target" were wrong. Also corrected below: an earlier note that keepers touch only 2-13% of shots missed keeper catches logged as ordinary control.

## Pro season targets (owner's Drive: "NBL 25-26", "MBL 2026"; final scores only)
| | NBL men 25-26 | MBL women 2026 |
|---|---|---|
| Games | 361 | 386 |
| Team score mean (sd) | 78.1 (12.7) | 86.0 (11.9) |
| Team score p5 / median / p95 | 59 / 76 / 102 | 66 / 87 / 104 |
| Game total mean (sd) | 156.1 (17.8) | 172.0 (16.8) |
| Margin median / p90 | 13 / 28 | 9 / 27 |
| Games decided by 5 or less | 23% | 25% |
| Home win share | 53.7% | 56.2% |
| Ties | 0 | 0 |

The simulator uses the NBL 2026-27 roster, so the working target is the NBL row: about 78 per team, sd about 13.

## The gap (simulator, real seeds 1, 3, 5)
| Build | Points per team | Possessions per team | Attempts per team | Points per possession | Points per attempt |
|---|---|---|---|---|---|
| Target (T1-T3) | ~78 | ~100 | ~50 | ~0.78 | ~1.56 |
| RB-3.10 | 31.3 | 214 | 38.2 | 0.146 | 0.82 |
| RB-3.12 | 44.8 | 264 | 81.7 | 0.170 | 0.55 |
| RB-3.13 | 25.7 | 165 | 44.8 | 0.156 | 0.57 |

Expected points of the rest of a possession, by distance to goal at the moment of control (ep_curve.json): about 0.3-0.5 points inside 20 m in every build. Possessions near goal rarely pay off.

### Shots
| Build | Shots | Keeper | Field defender | Scored | Own team recovers | Out/award |
|---|---|---|---|---|---|---|
| RB-3.10 | 199 | 48% | 24% | 17% | 9% | 3% |
| RB-3.12 | 270 | 27% | 38% | 9% | 22% | 3% |
| RB-3.13 | 204 | 34% | 30% | 13% | 19% | 4% |

- Every field-defender take is in flight before the goal line, 0.03-0.3 s after release, at about chest height (1.4-1.8 m). Shots are flat drives at about 58 m/s.
- RB-3.10 with positions (observer): lanes with a field defender within 2 m of the line: 63% blocked, 9% scored. Lanes clear by 9 m or more: 1% blocked, but the keeper takes 67% and only 25% score.
- Shot aim in native/cognition.py: (goal x, 50 +/- 1 m). The goal (native/scoring, NativeConfig.goal_radius 3.0) is a 3 m-radius half-disc on the goal line: 6 m wide, 3 m tall. Shots are aimed near the keeper.
- RB-3.12+ shots: 20 m or more are 5-8% (no 4-point value realised).

## Recommendations
| ID | Class | Fix | Expected effect |
|---|---|---|---|
| S-1 | BEHAVIORAL | Shot aim: target the part of the goal mouth farthest from the believed keeper position (inside the 3 m radius with a margin), and choose height; never aim within the keeper's reach | Keeper share of clear shots falls from ~2/3 |
| S-2 | BEHAVIORAL | Shot lane: apply the RB-3.13/3.14 reach-based lane check to shots (release time, reach + margin) | Most field-defender blocks (24-38% of shots) removed |
| S-3 | ENGINEERING (Codex) | Check the keeper save model against shot physics: reaction, reach and dive vs a 58 m/s shot from 10-15 m | Rules out a superhuman keeper |
| EV-1 | BEHAVIORAL | Replace hand-set carry/pass/shot weights with expected points: V(option) = sum over outcomes of probability x value, using calibrated tables (completion by lane margin, distance and pressure; shot conversion by distance, lane and keeper offset; tackle risk by free run; EP by field position). Refit the tables from each build's logs and scenarios | Ends the carry-vs-pass weight churn; scoring becomes the objective |

Order: S-1 and S-2 (with the RB-3.14 build or right after), S-3 in parallel (Codex), then EV-1.

## Canon confirmations needed
1. Target league for the simulator: NBL men's (78 per team, sd ~13)? MBL is 86.
2. Points split: constrain only the totals and their spread now and let the split by method emerge, or do you have intended shares (carries vs throws by band, half goals, awards) or an intended open-shot save rate?

## Reproduce
Scripts and outputs in audit/analysis/scoring/: season_stats.py (pro logs; xlsx not committed), conversion.py, shot_blocks.py, shot_lane.py (RB-3.10 observer), ep_curve.py. Raw logs: claude/rb-3-10-formation-hold (native/evidence/rb310/runs), claude/rb-3-12-carrier-valuation @ 0091755, claude/rb-3-13-pass-safety @ 3fd4843; observer re-runs on claude/rb-3-11-diagnosis @ 78eb31d.
