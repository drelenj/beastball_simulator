# OWNER BRIEFING

1. The experimental branch now has a live rating registry, workbook aliases, an agent selector and a commit log. The enabled simulator routes the revised perception, decision and execution hooks through the existing Native pipeline.
2. It can read separately authored ratings and preserve compatibility mode. The lab ran the owner scale from 0.40 through 1.00, with 20 paired scenarios per level.
3. Several hooks remain partial. Passing selects release speed and arc for the already chosen receiver. It has no alternate pass type or independent release timer. Takedown chooses drive versus containment after an observed wrap. Grip selection and a separate finishing sequence are unproven. Evasion and Reflex cover existing decisions and preparation windows. There is no mid-motion dodge retargeting. Defending has no distinct defensive block selection. The optional maneuver ratings were deferred.
4. The original workbook has no independently authored values for the new ratings. The release timing boundary and Stretch approval are recorded in QUESTIONS.md.
5. Recommended action is to review the partial hooks and replay evidence before using the branch for rating calibration.

## Phase status

| Phase | Status | Source |
|---|---|---|
| 1. Schema and plumbing | DESIGN COMPLETE, IMPLEMENTED, TESTED for schema and compatibility suite | `96d6e04531dc67a1573d03049602eee2578e3a7e` |
| 2. Enabled hooks | DESIGN COMPLETE, IMPLEMENTED and TESTED in part | `add8572cc8080665cb99008233d8ae1c9ce0e754`, `dd8e2a1baa424544ee9903d984bbe750ed1cfa8e`, `aa7fbcb742d9036977c357c922a11e28e92dadf0`, `b6418aa9aeb15c19d1c00b4bd7cbdd723d3926fa` |
| 3. Measurement | DESIGN COMPLETE, IMPLEMENTED and TESTED for the paired scenarios. Full match and benchmark evidence below. | `698a929c7d2f717336f63a6f81e0e4be5b226c7e`, `c39a60d76ef7fa614a6c5ae3bbaa12bccde6dfed` |

Branch `codex/rb-3-24-prism-registry` starts at `d1845d022625ddaf6d0f9d5ddc5e60179c63be34`. The RB-3.22 benchmark uses `eb30f605f24b906777b88d6cb3a552b3584639ef`.

## Standing gates

 a) pytest -q b1 native, full suite, after your last change.

 b) Legacy hash guards unchanged (native-v0/2, v0/3, rb/2; seeds 1 and 3, 3000 steps; native/evidence/rb3-reach/legacy-hashes.txt).

 c) Determinism: same code + roster + seed gives identical trace and state hashes.

 d) Compatibility (individuation off): real seed 1 reproduces 57-76, trace 44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072, state 046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d.

 e) Speed: paired 1,500-step benchmark against RB-3.22; individuation-on may be at most 15% slower per step, or explain why.

## Registry and ownership

- `rb323/rating-consumers.json` records the layer, owner, runtime consumers and status. Generate it with `PYTHONPATH=. python audit/native/rb324/build_registry.py`. The historical registry can be retrieved from the parent commit. Compatibility `passing` in the substrate still mirrors Throw Accuracy. The authored Passing rating owns a separate decision after the receiver is selected.
- An explicit new value takes precedence over a legacy alias. Where two retired names feed the same owner, the loader gives Marking precedence over Judgment for Defending and Carrier Duel precedence over Contact Resistance for Evasion. Existing workbook fallbacks retain their compatibility meaning. The enabled adapter defaults radar Awareness to 0.70 when the only workbook value is an OVR proxy. It likewise avoids treating the workbook Balance proxy as authored Evasion.
- Radar extends detection outside the cone within 6–14 m while preserving the body occlusion mask. Clarity sets observation noise and recognition error. Velocity estimates come from successive noisy positions and Instinct filters them. Focus stores a bounded number of tracks, expires them and adds a bounded drift to remembered positions. Instinct estimates remembered positions from those tracks. Anticipation uses conservative velocity estimates to forecast from delivered cues. The experiment does not estimate forecast error against a distribution of actual future trajectories.
- Agent selection uses a delivered belief, role and possession signal. The main decision stores one selected agent. An admitted pass or shot records the child at wind-up start. For contact, the record marks admitted contact commands and is distinct from the kernel's actual collision or grip time. Contact refinement uses own touch and balance. Phase 1 recorded agents and admitted boundaries without switching decision paths. Phase 2 consumes the selected agent in the opt-in path.
- Ball Handling keeps the release clock. Reflex uses the delivered course in the catch and save motors and runs committed contact decisions on its own cadence. Reaction changes deliberate decisions only. The goalie and catcher still need a feasible interception under the existing physics. The engine records legality, quotas, physical outcomes and score.
- Own rating data stays in the athlete view. Opponent dimensions use the captured frame. Memory estimates cannot look up unobserved player state. A poison test changes opponent location, dimensions and ratings plus true ball coordinates after capture. The delivered views and decisions retain the same inputs. IA-001 coverage is scenario based, with the existing purity suite and separate new hook probes.

## Lab findings

`rb324/rating-sweep.csv` and `rb324/lab-trials.json.gz` cover 34 active ratings, seven levels and 20 paired seeds per level. Each reported change is against the matched 0.70 case. The scope column distinguishes a changed command or physical result from an intermediate estimate, feasibility threshold or mapped quantity.

| Scenario | Observation |
|---|---|
| Defending | At 1.00, the contact command differed from the 0.70 case in 12 of 20 trials. |
| Takedown | At 0.40, the wrapped defender's contact command differed in 14 of 20 trials. |
| Playmaking | The first fixture changed option values without flipping the selected action. The separate near-tie fixture went from 0 of 20 shots at 0.40 to 14 at 0.70 and 20 at 1.00. |
| Finishing | The committed delivery vector changed in all 20 high-rated cases. Keeper position stayed fixed within each pair. |
| Throw Power | Ingress acceptance changed in 12 of 20 trials at 0.40. |
| Ball Handling | Release by the test deadline changed in 12 of 20 trials at 1.00. |
| Throw Accuracy | Actual release yaw changed in all 20 trials at 1.00. |
| Jump | The Keeper motor command changed in 1 of 20 trials at 1.00. |

The throw and Keeper motor scenarios are in `rb324/execution-trials.json`. The lab compares selected actions and direct quantities. It does not establish league effects.

## Match and gate evidence

Reproduction commands are in `rb324/README.md`. The real neutral fixture keeps the original workbook selection and body dimensions and replaces all ratings with 0.70. The control uses uniform body dimensions at the same ratings. Compatibility against the historic hash fixture uses the unmodified roster.

| Seed 1 roster | Individuation | Score | Possessions A / B | Steps | Restarts closed |
|---|---|---:|---:|---:|---:|
| Real bodies, ratings 0.70 | Off | 96–57 | 147 / 145 | 32,582 | 265 / 265 |
| Real bodies, ratings 0.70 | On | 35–29 | 105 / 104 | 30,189 | 161 / 161 |
| Control | Off | 55–79 | 144 / 144 | 33,097 | 287 / 287 |
| Control | On | 42–28 | 115 / 116 | 30,201 | 161 / 161 |

All four finished at 2,400,000 ms live time with the engine invariants passing. These single-seed comparisons show a change in score and possession frequency. The runs switch the entire experimental profile, which changes fatigue and several other mechanisms together. The data leaves the contribution of each rating and general play quality undetermined.

The serialized-view audit in `rb324/hook-replay.txt` covers 21 hook-related inputs with 20 seeds each. It replays the decision and the named probe after reconstructing the view and belief. It is an input-boundary check for those cases. The suite also checks queuing, sensor timing, replay and existing rulebook scenarios.

### Gate results

| Gate | Phase 1 schema checkout | Phase 2 hooks and Phase 3 lab checkout |
|---|---|---|
| a | 699 passed, 1 warning, 23 subtests passed in 620.05 s | 731 passed, 1 warning, 23 subtests passed in 646.80 s after the last simulator and test change |
| b | All six lines match byte for byte | All six lines match byte for byte |
| c | Enabled seed 1 repeated with exact trace, state and commit log over 1,500 steps. Seeds 1 and 3 also match the RB-3.23 enabled archive. | Enabled seed 1 repeated with exact trace, state and commit log over 1,500 steps. The enabled neutral real-roster match also repeated exactly through all four quarters. |
| d | Exact through `test_real_seed_1_with_no_overrides_reproduces_the_rb321_soak_gate` | Exact in the full suite and standalone 57–76 replay |
| e | 3.573 ms/step, +0.82% versus RB-3.22 | 4.221 ms/step, **+19.13%**, above the 15% budget |

The baseline median was 3.543 CPU ms/step. Each median uses the 1,500-step windows for real-roster seeds 1 and 3. Phase 1 records the arbiter and commit events with the RB-3.23 decision path intact. The comparison for the final hooks uses the same step count and roster. Live simulation workloads differ when decisions change.

The instrumented seed-1 profile explains the overrun. It executed 1,259 live physics calls with the switch on versus 1,125 in RB-3.22. Cumulative live physics time rose from 3.429 to 4.647 s. Cumulative rulebook capture time rose from 3.666 to 4.528 s, with 221,262 velocity filtering calls in the enabled run. Total cognition decision time fell from 1.565 to 1.238 s in the same profile. These are instrumented cumulative times. The budget comparison uses the uninstrumented CPU measurements.

The exact hashes, release and restart counts, and reproduction results are in `rb324/evidence/`. Run `python audit/native/rb324/check_evidence.py audit/native/rb324/evidence` to verify the stored files. The tested simulator and tests are at `b6418aa9aeb15c19d1c00b4bd7cbdd723d3926fa`. Later commits add evidence and review scripts.
