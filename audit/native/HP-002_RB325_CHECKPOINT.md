# OWNER BRIEFING

1. RB-3.25 adds PRISM CORE as an opt-in profile with seeded option evaluation, athlete-specific decision uncertainty, and committed action stages.
2. CORE can choose scoring, possession, defense, interception and specialist options from the athlete's observations. Passing can delay wind-up within one Reaction interval. Takedown can select a grip, and the five maneuver ratings feed their physical execution.
3. The supplied calibration meets the score and possession targets. The real-body scores span 63–123. Option values and decision accuracy still need ORACLE DRILL.
4. The single-hook diagnosis is in progress. There is no pending canon question.
5. Review the verified replay, the neutral results and the weak or abrupt lab effects before expanding the build.

## Source

- Parent RB-3.24 `3edfaad1ae5d50407c16e22dceca6ad92f9d9ae6`
- Branch `codex/rb-3-25-prism-core`
- Initial CORE implementation `89db761`
- Zone exit and first calibration adjustment `e13b96a`
- First measured candidate `20242f5cee454b1d1f7eaac83c04dcdc92035a32`
- Shared neutral shot calibration and physical independence `aab2a64da006e6c967ec4193599a7cb50b6dc70d`
- Final simulator code `742117495dfeefb4d9f5d83915001e304c8d1bdc`
- Performance comparison parent RB-3.22 `eb30f605f24b906777b88d6cb3a552b3584639ef`

Use `individuation/2` or the experimental runner's default for CORE. The explicit `--rb324` replay still selects `individuation/1`. Compatibility continues to select `off`.

## Task status

| Task | Status | Evidence |
|---|---|---|
| 1. Shooting decomposition | DESIGN COMPLETE, IMPLEMENTED | Pinned RB-3.24 layer and single-hook runs, see the table |
| 2. Decision structure | DESIGN COMPLETE, IMPLEMENTED, TESTED in scenarios | Production menu records, choice distributions and paired noise tests |
| 3. Neutral calibration | DESIGN COMPLETE, IMPLEMENTED, TESTED across six matches | All-0.70 match table |
| 4. Remaining hooks | DESIGN COMPLETE, IMPLEMENTED, TESTED in scenarios | Wind-up, legal grip, movement and reflex scenarios |
| 5. Rating sweep | DESIGN COMPLETE, IMPLEMENTED, TESTED in paired scenarios | 39 ratings, seven levels, 20 seeds per level |
| 6. Speed | DESIGN COMPLETE, IMPLEMENTED, TESTED in paired benchmark | Same-roster 1,500-step windows, seeds 1 and 3 |

## Standing gates

 a) pytest -q b1 native, full suite, after the last change.

 b) Legacy hash guards unchanged (native-v0/2, v0/3, rb/2; seeds 1 and 3, 3000 steps; native/evidence/rb3-reach/legacy-hashes.txt).

 c) Determinism: same code + roster + seed gives identical trace and state hashes.

 d) Compatibility (individuation off): real seed 1 reproduces 57-76, trace 44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072, state 046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d.

 e) Speed: individuation-on at most 15% slower per step than RB-3.22 (paired 1,500-step benchmark).

### Gate evidence

- The full suite after the final simulator change reported `744 passed, 1 warning, 23 subtests passed in 640.03s (0:10:40)`. The warning is the pytest dependency's `CallSpec2` deprecation.
- All six legacy trace, state and config rows match the recorded guard. The raw results are in `rb325/evidence/legacy.txt`.
- Two full CORE control seed-1 runs finished 72–78 in 33,041 steps. The trace was `b09944083bea5cc9ce2bb290dd4428840c7cbef93c41823d66910ceb799fd130` and the state was `ed5df2b1636522c4a10f293c8fa5250e5dd3293b4f884d68eb2a332e622f894d` in both. The real-roster 1,500-step seed-1 repeat also matched exactly.
- The compatibility fixture is 57–76 with the full trace and state listed under gate d.

| 1,500-step window | RB-3.22 CPU ms/step | CORE CPU ms/step |
|---|---:|---:|
| Real seed 1 | 3.802 | 3.990 |
| Real seed 3 | 3.586 | 4.036 |
| Seed 1 repeat | 3.588 | 4.035 |
| Median of paired seeds | 3.694 | 4.013 |

The matched benchmark passed at **8.64%** slower. Both modes ran under the same concurrent compatibility workload. An earlier comparison used baseline and CORE windows taken under different background loads and measured 16.80%; those records are in `rb325/evidence/timing-unmatched/`. Keep the paired sample and its repeated fingerprint as the speed gate evidence.

The 1,500-step profiles show 3.82 cumulative seconds in CORE RulebookPort capture, 1.78 in CORE decisions, and 3.67 in native physical stepping. The corresponding baseline costs were 3.44, 1.53 and 3.34 seconds. CORE ran 1,279 live physical steps in that profile, compared with 1,125 for RB-3.22. Instinct projected 27,342 remembered sightings. The profiles and raw function timings are in `rb325/evidence/`.

## Decision boundaries

- Each option has a hand-set value and an owner. The selector adds a symmetric, seeded error with half-width `0.75 × (1 − rating)`. All constants and option values are **PROVISIONAL - TO BE REPLACED BY ORACLE DRILL**. The seed is scoped to the athlete, decision time and stage. At 1.00 there is zero sampling error. The published holder state, known own timing and delivered views are the inputs.
- The carrier menu reuses the existing legal carry, receiver, handoff and shot candidates, and compares them with evasive carry. Defenders compare man marking, chasing, area responsibility, blocks and feasible takedown commits. Pursuit evaluates routes using the observed ball. Keeper and Archer choices retain rulebook eligibility before their own menu evaluates alternatives.
- After pass commitment, Passing compares direct, fast, loft, bounce and delay options as feasible. It can advance the intended lane with observed receiver movement. Any delay is within one Reaction interval. Starting release motion keeps the original Ball Handling clock. Finishing selects an aim or Stretch once the carrier commits to a scoring attempt.
- Evasion chooses techniques after the carrier commits. Five separate maneuver ratings change physical execution. After wrap, Takedown compares drive and containment and can switch grip with a retention cost. Reflex gates late adjustments from delivered observations and is independent of Reaction.
- Focus snapshot and memory results are cached per athlete and decision tick. Pending actions can use the delivered frame without allocating a transformed memory. Instinct projects remembered tracks when needed. Anticipation runs only for a pursued ball or a possible Keeper intercept. Body metadata is read once per sensing tick and surfaced only for observed entities. Pass and carry search reuse opponent reach calculations within each lane evaluation.

## Calibration changes

| Mechanism | RB-3.24 or first CORE value → final CORE value | Reason |
|---|---|---|
| Decision option perturbation | Signed option bonuses → symmetric half-width `0.75 × (1 − r)` | A rating changes uncertainty while preserving the hand-set value |
| Reaction | `500 × (1.3 − .4r)` → `500 × (1 + .4 × (.70 − r))` ms | League average uses the ordinary 500 ms decision cadence |
| Focus capacity and retention | `round(4 + 8r)`, `1400 + 600r` ms → `20 + round(8 × (r − .70))`, `2000 + round(600 × (r − .70))` ms | Keep ordinary track coverage at the league average |
| Native catcher readiness | Delivered frame followed by `0.55 − 0.35r` s → existing stochastic hand preparation with Reflex multiplier `1 + .65 × (.70 − r)` after delivered evidence | Preserve viable catch preparation for ordinary passes |
| Keeper motor | Delayed gate, rating-dependent push-off → ordinary push-off and preparation clock with Reflex multiplier | Goalkeeping influences decisions through uncertainty. Reflex handles late readiness |
| Anticipation velocity adjustment | `1 − .25 × (1 − r)` → `1 − .25 × (.70 − r)` | Anchor the average forecast at the observed velocity |
| Shot option offset | `0 → −.55 → −1.40` | The first candidate averaged 105.5 points over the two control teams. A single lower baseline applies to all rosters, without a rating-dependent slope |
| Frozen kernel Awareness and Contact Resistance inputs in CORE | Athlete Awareness and Evasion → `.70` | Radar Awareness and post-commit Evasion stay separate from hand-preparation time and physical grip resistance |
| Area valuation | Distance coefficient `.07 → .045` and inside-zone bonus `1.5 → .85` | Preserve man pressure while keeping a situational area alternative |
| Zone exits | Pursuit could bypass existing zone exit policy → every relevant field route checks it | Initial CORE seed 1 gave 116 points from penalty awards. The calibration candidate gave 1 |
| Stretch reach and strip exposure | Fixed maximum `.9 × arm reach` → `(.9 − .18 × (1 − Ball Handling)) × arm reach`. Extra strip multiplier scales by `1 − Ball Handling` | Apply the owner ruling on physical execution |
| Grip change | No selection → legal upper/lower choices with `.75` grip retention when switching | Give changing technique a physical cost |
| Maneuvers | Five newly distinct execution slopes | Juke lateral gain .5, Spin speed loss .2, Hurdle jump fraction .36, Stiff-arm impulse range .5 and Truck drive range .5. All are provisional |

Existing core physics, scoring and regulation are preserved in compatibility. Newly hand-set menu weights are declared in `native/prism_core.py`.

The following menu parameters are new. Each is **PROVISIONAL - TO BE REPLACED BY ORACLE DRILL**.

| Choice | New values | Use |
|---|---|---|
| Carrier | Carry-to-goal increment `1.0`, evade-under-pressure increment up to `2.5` | Compare running through space with evading a nearby opponent |
| Scoring commit | Stretch option `13`, believed reach allowance `0.45 m` | Offer hand extension near the scoring plane within the actor's believed reach |
| Defending | Block range `3 m`, option `0.8`; takedown range `2.2 m`, increment `0.35` | Offer nearby defensive contact alternatives |
| Passing | Wait cost `0.22`, fast/loft cost `0.25`, bounce cost `0.65`, lane gain weight `0.12`, waiting receiver speed floor `1.6 m/s` | Compare launch adjustments with the direct release |
| Goalkeeping | Setting value `1.0`, saving base `1.15`, course window weight `0.6`, shift cost `0.3` | Evaluate a position change or commitment against staying ready |
| Disruption | Wait value `0.65` | Compare holding a prepared draw with releasing it |
| Air pursuit | Landing-option cost `0.12` | Compare chasing the currently visible route with its projected landing |
| Takedown | Upper grip value `0.3`, lower grip target-speed weight `0.06` | Compare upper and lower holds after commitment |
| Late maneuver | Closing threshold `2.5 m`, maximum age `0.6 s` | Keep late adjustments within an admitted movement and its observed contact window |

## RB-3.24 layer decomposition

These are full matches on the pinned RB-3.24 parent at 0.70 with real bodies. The two controls use the untouched compatibility and individuation profiles. An all-switches verification matched the untouched enabled trace and state over 1,500 steps. Isolated layers use controlled source switches on the pinned version. The trial outputs, script, switch list and reproduction commands are in `rb325/`.

The primary endpoint is shot count. Follow-up switches are run for layers shifting the two-seed total by at least 10%. Counts per 100 possessions help distinguish fewer possessions from changes in shot frequency. Individual full-match trajectories diverge after each intervention, so the numbers include interactions.

| Run | Score A–B | Possessions A/B | Terminal attempts A/B | Shots A/B | Open pass completion A/B |
|---|---:|---:|---:|---:|---:|
| off-1 | 96–57 | 147/145 | 22.4%/15.2% | 49/28 | 66.7%/58.6% |
| off-3 | 52–98 | 143/142 | 13.3%/16.9% | 27/36 | 58.2%/67.9% |
| on-1 | 35–29 | 105/104 | 7.6%/11.5% | 15/19 | 43.8%/41.2% |
| on-3 | 42–39 | 120/119 | 12.5%/10.1% | 17/15 | 36.4%/37.6% |
| perception-1 | 56–100 | 131/130 | 15.3%/22.3% | 26/32 | 69.6%/70.1% |
| perception-3 | 49–71 | 131/132 | 19.1%/22.0% | 32/33 | 68.3%/68.4% |
| recognition-1 | 61–52 | 133/132 | 30.1%/22.7% | 32/24 | 63.1%/57.0% |
| recognition-3 | 70–55 | 135/135 | 31.1%/25.2% | 34/24 | 68.3%/57.1% |
| inference-1 | 45–102 | 137/137 | 29.2%/35.0% | 31/36 | 60.4%/62.0% |
| inference-3 | 65–82 | 133/133 | 23.3%/32.3% | 29/36 | 62.6%/63.1% |
| strategy-1 | 61–63 | 134/135 | 28.4%/31.9% | 38/32 | 60.5%/65.1% |
| strategy-3 | 55–73 | 128/128 | 32.8%/43.0% | 37/43 | 65.6%/64.2% |
| motor-1 | 43–89 | 129/130 | 27.1%/25.4% | 24/26 | 51.6%/53.3% |
| motor-3 | 73–85 | 128/128 | 36.7%/28.1% | 32/31 | 50.5%/57.8% |
| execution-1 | 68–57 | 135/134 | 33.3%/28.4% | 29/26 | 69.9%/68.3% |
| execution-3 | 99–92 | 139/139 | 39.6%/37.4% | 44/36 | 67.3%/60.3% |

The early `off`, `on` and `perception` rows count shots as terminal attempts. The remaining rows include carries recorded by the scoring-attempt witness. The early terminal percentages are lower bounds and should be compared within that scope.

| Switch | Shots | Shots per 100 possessions | Median team score |
|---|---:|---:|---:|
| off | 140 | 24.3 | 76.5 |
| on | 66 | 14.7 | 37.0 |
| perception | 123 | 23.5 | 63.5 |
| recognition | 114 | 21.3 | 58.0 |
| inference | 132 | 24.4 | 73.5 |
| strategy | 150 | 28.6 | 62.0 |
| motor | 113 | 21.9 | 79.0 |
| execution | 135 | 24.7 | 80.0 |

The full stack fell from 140 to 66 shots and from 76.5 to 37.0 median team points in this two-seed sample. Seed 1 scored 35–29, matching the lead's witness exactly. Recognition and Motor Control each lowered both total shots and shots per possession. Perception's lower shot total tracks the reduced possession supply closely. Strategy and Execution alone retained or increased shots per possession. Inference alone changed that rate by 0.1 shots per 100 possessions. The isolated Inference run measures recent-read filtering and forecast changes. Its remembered-track projection requires the Focus path.

The old Reflex catch gate alone produced 102 shots across seeds 1 and 3. Open-play pass completion fell from 355/567 (62.6%) to 170/370 (45.9%). The old implementation added a fixed `0.55 − 0.35 × Reflex` seconds after delivered ball evidence. At 0.70 that adds 305 ms after delivery, compared with a stochastic catch-preparation scale of about 106 ms in compatibility. The added gate blocks preparation for part of the short-pass window. This observation motivates the CORE change to ordinary preparation with a graded late adjustment.

Dropping only that gate from the full stack raised completion from 139/350 (39.7%) to 212/383 (55.4%). Total shots rose from 66 to 92 and the pooled team-score median rose from 37 to 50. This confirms an effect on both sides of the intervention. The remaining gap depends on other hooks and how their match paths interact.

Focus alone reduced shots to 127; its neutral capacity was 10 and its retention was 1,820 ms. The combined Recognition layer reduced shots to 114. Reaction alone reduced deliberate decisions from 309,042 to 275,041, while producing 147 shots. Within Motor Control, Reflex save alone produced 160, Reflex cadence 155, and steering 145. The field catch gate is the isolated Motor Control change that reproduced a shooting decrease in this sample.

## Neutral calibration

Both teams use 0.70 for every rated attribute. A is Garvian Guardians and B is Ala Apex in the real-body runs. The control uses the standard uniform body for both teams. Every match reached the final and closed every recorded restart.

| Body set and seed | Score A–B | Possessions A/B | Shots A/B | Open pass completion A/B | Award points A/B |
|---|---:|---:|---:|---:|---:|
| Real 1 | 87–79 | 147/147 | 48/48 | 60.7%/68.4% | 14/5 |
| Real 2 | 99–63 | 143/144 | 57/37 | 66.5%/69.1% | 8/0 |
| Real 3 | 68–116 | 144/143 | 33/59 | 65.8%/67.4% | 8/7 |
| Real 4 | 71–123 | 140/139 | 36/47 | 65.9%/64.8% | 1/5 |
| Real 5 | 70–88 | 137/138 | 42/38 | 66.2%/63.5% | 3/8 |
| Control 1 | 72–78 | 143/141 | 48/47 | 65.2%/65.2% | 2/1 |

The median of the ten real-body team scores is **83**. The control median is **75**. All 12 possession counts are inside 100–150. The real-body scores span 63–123. Seeds 3 and 4 have individual match medians of 92 and 97. The anchor is the pooled real-body median and the separate control median.

The earlier offset of `−.55` produced a real-body median of 87.5 and a control median of 105.5. The first two `−1.40` probes were followed by six fresh matches at the committed setting. Both seed-1 probes reproduced their trace and state hashes in the corresponding committed runs.

## Sweep effect sizes

The executable table is `rb325/sweep.csv`. It reports the engine quantity, effect size relative to 0.70, share changed, decision entropy, choice counts and adjacent-step flags. The raw 5,460 trials are in `rb325/sweep.json.gz`.

Instinct and Stamina measured under 2% total effect for the selected quantity. Speed had an adjacent-level jump above half its total measured effect in the acceleration-limited scenario. In the 20-seed near-tie choice samples, Defending, Disruption, Evasion, Finishing, Goalkeeping, both Pursuits, Passing, Playmaking and Takedown had at least one such distribution jump. Each decision rating enters continuously through error spread. The discrete choices can flip at close option boundaries. The event thresholds in the physical probes are lab cutoffs. The throw probes exercise actual release speed, release heading and wind-up. Selection frequency cannot establish correctness.

The additional `rb325/strategy-scenarios.json.gz` samples the role and commitment code with fixed actor observations. At `1.00` compared with the paired `0.70`, the selected Playmaking action changed in 6 of 20 trials, Passing in 3 of 20, Finishing in 13 of 20, and Takedown in 11 of 20. The raw records show all levels and counts. The running-speed jump is between `0.40` and `0.50`. Higher top speeds have little effect in this particular acceleration-limited window. The scenarios do not establish match-level effect size for a single rating.

Reaction's deadline is graded. On a steady 100 ms tick grid a 520 ms deadline at 0.60 is reached at 600 ms, while the 500 ms deadline at 0.70 is reached at 500 ms. That grid case produces an adjacent jump greater than half the realized cadence range. The sweep records the requested deadline. Regulation also contains sub-step events, so realized decision intervals depend on the event timeline.

## Needs ORACLE DRILL

- Label the true value and opportunity cost of each feasible option for a given observed situation.
- Compare immediate delivery, holding the ball and waiting to start a pass against the feasible alternatives. Estimate the value of changes in pass target, speed, lane, arc and surface contact.
- Compare carries, handoffs, throws and stretches using their true opportunities and costs. Include the cost of increased exposure to strips or tackles.
- Evaluate man versus area, mark target, pursuit, defensive block, takedown commitment and grip choice using true consequences.
- Evaluate Keeper positioning, save types and readiness, and Archer target, hold, fire and quota expenditure.
- Evaluate evasive technique, including whether to engage or avoid each confrontation and which motion to commit to.
- Replace provisional hand-set values and estimate calibrated decision uncertainty by role and situation.
- Separate decision quality from differences in sensing, motor execution and opponent behavior.

Owner questions and the resolved Stretch and Passing rulings are in `QUESTIONS.md`. Reproduction steps and scope are in `rb325/README.md`.
