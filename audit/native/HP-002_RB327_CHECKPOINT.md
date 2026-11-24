# OWNER BRIEFING

1. **IMPLEMENTED and TESTED**. RB-3.27 regraded the original sample, completed 29,780 possession rollouts, fitted DRILL v1 and measured both policies in 40 real-roster games.
2. PRISM can load a versioned expected-points table before kickoff and use it for carrier choices and shot aim. The ratings 0.4 workbook supplies each athlete’s explicit ratings. The hand-set policy remains the default.
3. Neither Gauge met its regret criterion. The neutral anchor scored a median of 66 points per team and averaged 153.2 possessions per team. Both missed the owner ranges.
4. The evidence does not support promoting learned values to the default. The held-out shot-conversion fit also scored worse than the pooled prediction. No canon question is pending.
5. Keep hand-set values as the default. Use the committed rollout and match records to review the carrier choice and shot-aim estimates before another promotion decision.

## Revisions and status

- Branch `codex/rb-3-27-drill-values`
- Lead-verified parent `14b393da76bd24b3655dc539fe7ab4ce2ab73972`
- Scoring, fitting, runtime opt-in and tests `2264f1f`
- Regulation evidence runners `d5400ae`
- Roster source and reproduction instructions `1b7b206`
- Deterministic artifact provenance `e67bb3d`
- Original sample scoreboard regrade `460b982`
- DRILL v1 and Gauge raw data `5bde37a`
- Paired CPU benchmark `7fa1c9b`
- Neutral anchor and full replay `698e723`

| Task | Status | Evidence |
|---|---|---|
| 1. Possession scoring | DESIGN COMPLETE, IMPLEMENTED, TESTED | All 150 original decisions regraded. 11,880 rollouts. |
| 2. More moments and refit | DESIGN COMPLETE, IMPLEMENTED, TESTED | Ten neutral seeds, 384 decisions, 29,780 rollouts and six held-out comparisons. |
| 3. Learned PRISM values | DESIGN COMPLETE, IMPLEMENTED, TESTED | Gate f and reproducibility passed. The six-game anchor missed both owner ranges. |
| 4. Gauge | DESIGN COMPLETE, IMPLEMENTED, TESTED | Neither held-out test met the 2-standard-error criterion. |
| 5. Real ratings | DESIGN COMPLETE, IMPLEMENTED, TESTED | Twenty games per mode across six franchise pairs. All finished. |

## Standing gates

 a) pytest -q b1 native, full suite, after the last change.

 b) Legacy hash guards unchanged (six rows, native/evidence/rb3-reach/legacy-hashes.txt).

 c) Determinism: same code + roster + seed gives identical trace and state hashes.

 d) Compatibility (individuation off): real seed 1 = 57-76, trace 44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072, state 046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d.

 e) CORE identity (learned values OFF): neutral-real seed 1 = 61-80, trace c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256, state c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745.

 f) Speed: individuation-on at most 15% slower per step than RB-3.22; learned values must not add more than 5% on top.

 g) Firewall: live true state never reaches cognition; learned artifacts enter only as versioned files loaded before a match; the purity test covers the new loader.

The full suite, rerun with the final artifact checked in, reported `767 passed, 1 warning, 23 subtests passed in 627.29s (0:10:27)`. An earlier repeat ran out of scratch space while unpacking legacy engines. The final run used an isolated temporary directory in memory. The warning was the pytest dependency's `CallSpec2` deprecation.

The six legacy trace, state and config rows matched exactly. The full compatibility and CORE learned-off runs reproduced gates d and e. Their raw results are in `rb327/evidence/compatibility.json` and `rb327/evidence/core.json`.

The focused tests cover a defensive intervention during the opponent's possession, separate reporting of the action outcome, rejection of a changed table, decisions after removal of the loaded file, an information-boundary poison test, and independent 0.422 roster selection.

## Timing and fixed-window replay

Two paired 1,500-step windows on the archived real roster, seeds 1 and 3, measured process CPU. RB-3.22 was `eb30f605f24b906777b88d6cb3a552b3584639ef`.

| Mode | Seed 1 ms/step | Seed 3 ms/step | Median ms/step |
|---|---:|---:|---:|
| RB-3.22 | 3.686 | 4.123 | 3.904 |
| CORE, learned off | 4.038 | 4.751 | 4.394 |
| CORE, learned on | 3.921 | 3.970 | 3.946 |

CORE off was +12.55% versus RB-3.22, and CORE on was +1.05%. Learned on was -10.22% versus CORE off. These net comparisons include the work resulting from different decisions and do not isolate lookup CPU. Both thresholds in gate f passed. The independent learned-on seed-1 window matched score, steps, config and both hashes.

- Window trace `93451cd0c928a751d289078a4784d8827a8dcf50f14ebae6b8d534fd09f71e15`
- Window state `b67e8378233afe7fee07ffb232b8387bf2a8aa8bc374ce3c0aa4229a19843103`

## Original sample regrade

| Stage | Multi-option menus | All options tied, action horizon | All options tied, possession horizon | Best options tied, possession horizon |
|---|---:|---:|---:|---:|
| Passing | 29 | 27 | 2 | 4 |
| Takedown | 30 | 30 | 5 | 14 |

Passing also had one single-option menu. Including it in the all-equal count reproduces the lead's original 28 of 30, compared with 3 of 30 through possession end. With the longer horizon, the hand-set best fell in the best-return group in 9 of 29 Passing and 9 of 30 Takedown menus. The mean gaps to the best observed return were 0.321 and 0.260 points respectively. The 11,880 original-sample rollouts took 4,083.3 CPU seconds. Option-level evidence is summarised in `rb327/evidence/original.json`.

## Expanded fit and holdout

The ten neutral-real matches delivered 1,599,060 decisions. The sample used 204 carrier decisions, 34 per distance-by-pressure stratum, and 60 each for Passing, Finishing and Takedown. The 29,780 rollouts took 10,247.9 CPU seconds, or 0.344 seconds per rollout and 26.69 seconds per decision. The branches ended in 21,757 turnovers, 7,516 scores and 507 period ends. The safety cap was never reached. The separate action diagnostic records 282 outcomes unresolved when the possession ended.

The fitted artifact is `native/oracle/artifacts/drill-v1.json`, schema `oracle-drill-v1/1`, SHA-256 `a19e9c04431309c1ea779ab077a8dd65eefdcbb616f25481a591d5847f49753e`.

| Table | Training rollouts | Held-out rollouts | Pooled MSE | Fit MSE | Relative change |
|---|---:|---:|---:|---:|---:|
| Pass completion | 7,480 | 1,300 | 0.250367 | 0.237570 | −5.11% |
| Tackle risk | 5,040 | 1,080 | 0.178258 | 0.166536 | −6.58% |
| Shot conversion | 4,880 | 680 | 0.250019 | 0.287404 | +14.95% |
| Points by field position | 12,440 | 2,840 | 2.057356 | 2.011512 | −2.23% |
| Carrier expected points | 12,440 | 2,840 | 2.057356 | 2.019298 | −1.85% |
| Finishing expected points | 4,060 | 520 | 2.482911 | 2.465152 | −0.72% |

The binary outcome MSEs score predicted probabilities against binary results. The point tables measure squared points. Of the held-out predictions, 20 shot-conversion and 80 carrier rows reached a previously unseen most-specific bucket and used the fallback. The four outcome tables are audit diagnostics. The two expected-points tables drive the opt-in decisions.

## Held-out Gauge

The held-out sample contained 36 carrier and eight Finishing moments. Each rating level used 20 identical decision seeds per moment. True regret uses the forced possession-return estimates. Belief regret uses the athlete's expected-point estimates before applying decision error. The paired uncertainty averages the 20 within-moment differences and uses the moments as the sampling unit.

| Stage | Rating | Trials | Mean true regret | Mean belief regret |
|---|---:|---:|---:|---:|
| Playmaking | 0.40 | 720 | 0.48333 | 0.06669 |
| Playmaking | 0.70 | 720 | 0.47986 | 0.02948 |
| Playmaking | 1.00 | 720 | 0.57639 | 0.00000 |
| Finishing | 0.40 | 160 | 0.44469 | 0.06616 |
| Finishing | 0.70 | 160 | 0.36656 | 0.02590 |
| Finishing | 1.00 | 160 | 0.35000 | 0.00000 |

| Stage | True regret at 1.00 minus 0.40 | Paired SE | Verdict |
|---|---:|---:|---|
| Playmaking | +0.09306 | 0.06473 | FAIL. Regret rose at 1.00. |
| Finishing | −0.09469 | 0.05368 | FAIL. Regret fell by 1.76 standard errors. |

Both decisions followed their learned estimates more consistently as ratings rose. The holdout covers two matches, with eight Finishing moments. The raw sample, all option returns and each Gauge draw are in `rb327/evidence/{moments,grades,gauge}.jsonl.gz`.

## Neutral learned-on anchor

All athletes used 0.70 ratings. The real group used the archived roster's physical bodies.

| Match | Score A–B | Possessions A / B | Possessions ending in an attempt A / B |
|---|---:|---:|---:|
| real-1 | 61–75 | 153 / 155 | 18.3% / 20.6% |
| real-2 | 68–49 | 156 / 156 | 18.6% / 13.5% |
| real-3 | 64–58 | 157 / 157 | 19.1% / 15.9% |
| real-4 | 70–100 | 149 / 148 | 16.8% / 19.6% |
| real-5 | 50–92 | 144 / 145 | 18.8% / 24.1% |
| control-1 | 61–76 | 159 / 159 | 17.0% / 23.3% |

The pooled median team score was **66.0** against the owner range **75–90**. Mean possessions were **153.17** and the median was **155.5** against the range **100–150 per team**. The range was 144–159 observed possessions per team. The mean share ending with an attempt was **18.80%**. Real bodies alone had a median team score of 66.0, mean possessions of 152.0 and an 18.53% attempt-ending share. Control had a median team score of 68.5, 159 possessions per team and a 20.13% attempt-ending share. No policy re-tuning followed these runs.

The full learned-on neutral-real seed 1 repeated **61–75** in **31,976** steps from a second process. Both runs matched all three digests.

- Config `5f311cb7c76fe771df547c41badf24a743994c2569f56eca7eda63b3cda20225`
- Trace `4da6c2add2e910d6c6edd1862a5c4710d3abbad42474b3da9e5a2c7ee37e642d`
- State `4f5c1f65c4977a68de1abfedea91cb09703b3d6984bde8a1d0e62ad847219b67`

## Ratings 0.4 paired soak

The primary pairing was Garvian Guardians (A) and Ala Apex (B), seeds 1–10. Each of the other five fixed pairings used seeds 1 and 2. All 40 games finished with every restart resolved and reported their invariants passed. The 20 learned-off matches took 3,216.5 CPU seconds, and the 20 learned-on matches took 3,003.7 CPU seconds. The six neutral anchor runs took 912.3 CPU seconds.

| Mode | Games | Median team score | Mean / median team possessions | Possessions ending in an attempt | Ala mean margin ± SE | Ala wins |
|---|---:|---:|---:|---:|---:|---:|
| Learned off | 20 | 89.5 | 153.15 / 152 | 35.41% | +27.0 ± 6.14 | 9/10 |
| Learned on | 20 | 81.5 | 161.60 / 163 | 19.01% | +34.9 ± 8.23 | 10/10 |

The median team score in the primary pairing alone was 90.5 off and 76.0 on. Its mean team possessions were 152.55 off and 159.05 on. The mean attempt-ending share was 35.49% off and 18.28% on.

The [per-match CSV](rb327/evidence/matches.csv) contains every score, both possession totals, terminal-attempt share, shot releases, carry attempts, score margin and fingerprints. The CSV keeps shot releases distinct from carried scoring attempts. The [raw runs](rb327/evidence) include exact per-match results and a completeness check for 49 regulation results, counting the two identity runs, six anchors, one replay and 40 paired games.

## Implemented measurement

Each branch starts from a captured decision and changes one selected option. The return is the choosing team's net points through a turnover, goal, period end or a 120 simulated-second safety cap. If a team started on defence, the rollout tracks the other team's possession. Passing, Finishing and Takedown retain the first action outcome and elapsed time as a diagnostic. The branch seed derivation and 20 replicates per option remain fixed for comparison with RB-3.26.

The neutral sample retains the original 150 selections from seeds 1–3 and adds preregistered draws from seeds 4–10. Training uses 1–8. Seeds 9 and 10 remain out of fitting, through the Gauge. Live expected-point cells use a training-only hierarchy of action, game situation and detail. A cell starts with 40 trials' worth of the parent estimate, a shrinkage choice for this experiment. The four diagnostic tables and the two live tables compare held-out mean squared error against the relevant pooled training mean.

The live configuration stores the artifact SHA-256. Startup validates the schema, feature version and checksum and builds immutable table cells. Normal decisions do no file I/O. Carrier options and committed Finishing aims use the same available information and seeded error as CORE. Their learned values displace the hand-set values, including the carrier's flat shot offset. No value artifact is required when the switch is off.

The ratings 0.4 workbook is pinned in the reproduction note. Its source commit is `b284e822fa2f23c820987c795a2d780f16334fc3` and its SHA-256 is `47b48af7a19035428d517582370fa1782b542980c783edf3dfb20619cf437fba`. The named ratings supply the simulator's inputs. The calculated Overall for this experiment supplies the selection order. The readback independently checks top IDs by position group, the 22 entry shape, the underlying rating columns and role-specific attributes for the 12 franchises in the match sample.

## Open questions

No canon decision was required. The main empirical question is whether a different set of belief-only features can rank choices well enough that reducing decision error improves possession returns. This checkpoint measures DRILL v1 as fitted and records the failed Gauge and anchor.

Reproduction commands and evidence locations are in [rb327/README.md](rb327/README.md).
