# OWNER BRIEFING

1. RB-3.26 fixes Reaction timing and adds a separate ORACLE package for replay, physical rollouts and grading. The drill completed 11,880 rollouts across 150 captured decisions.
2. ORACLE can resume a saved match in a fresh process or start from an authored field state. It can grade each option on one athlete's menu while the rest of the match uses the normal decision logic.
3. Higher Playmaking followed the hand-set values more closely and incurred more rollout regret in this pilot. Two of the four fitted tables improved over the pooled baseline on held-out seed 3. Transfer to other teams remains unproven.
4. All standing gates passed. The Gauge missed its true-regret criterion. No canon question is pending.
5. Review the largest disagreements and the many points-only ties in the commitment stages before using any learned value in PRISM.

## Revisions and status

- Owner's RB-3.25 baseline `2612256e1beab3477c58866d8878882c60abf70f`
- Task 0 clock correction `d7ab3eb`
- Snapshot, scene and force harness `1c5f563`
- Rollout, mining, fitting and gauge code `c0f8970`
- Captured-match preparation `ee6104c`
- Final implementation and tests `0879f85`

| Task | Status | Evidence |
|---|---|---|
| 0. Reaction | DESIGN COMPLETE, IMPLEMENTED, TESTED | 10,000-decision sweep at each level, compatibility and new seed-1 fingerprints |
| 1. Harness | DESIGN COMPLETE, IMPLEMENTED, TESTED | Full and prepared snapshots, true-state scenes, firewall test |
| 2. Rollouts | DESIGN COMPLETE, IMPLEMENTED, TESTED | One forced option, independent branch seeds, stage horizons and 11,880 branch outcomes |
| 3. Drill | DESIGN COMPLETE, IMPLEMENTED, TESTED | 150 sampled decisions, four fitted tables with held-out scores |
| 4. Gauge | DESIGN COMPLETE, IMPLEMENTED, TESTED | Belief regret decreased. Rollout regret increased across the tested levels |

## Standing gates

 a) pytest -q b1 native, full suite, after the last change.

 b) Legacy hash guards unchanged (native-v0/2, v0/3, rb/2; seeds 1 and 3, 3000 steps; native/evidence/rb3-reach/legacy-hashes.txt).

 c) Determinism: same code + roster + seed gives identical trace and state hashes.

 d) Compatibility (individuation off): real seed 1 = 57-76, trace 44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072, state 046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d.

 e) CORE identity: individuation on, all ratings 0.70, real bodies (neutral-real), seed 1 = 87-79, trace 317d40ba3cbfd5409bec2f39075ced1122e73c7e1fd1ce4ff0dd7a65c2af7b01, state 26d9d339aa4c80c2956731948d25c7dbe93e9bb8ed152af124d706bd75ee85ef - EXCEPT after Task 0, which changes CORE on purpose: report the new CORE hashes from then on.

 f) Speed: individuation-on at most 15% slower per step than RB-3.22; ORACLE code must add nothing to a normal match run.

The final full suite reported `762 passed, 1 warning, 23 subtests passed in 648.21s (0:10:48)`. The warning was the pytest dependency's `CallSpec2` deprecation. The focused suite reported 18 passing tests. All six legacy trace, state and config rows matched. The full regulation continuation results confirm the post-Task-0 CORE fingerprints below.

The paired 1,500-step real-roster timing used RB-3.22 `eb30f605f24b906777b88d6cb3a552b3584639ef`. CPU times per step were 3.702 and 3.585 ms on the reference and 3.985 and 4.069 ms on CORE. The median was **3.643 vs. 4.027 ms**, an increase of **10.53%**. Two full-code seed-1 windows had matching trace and state.

- Timed CORE trace `94a78267864f0a08dbf9feeaa368f21cd089174ba00ce9b72f869bf78760afc4`
- Timed CORE state `20c56e1cfc539a4ddb7c11c8e0ce4e18cd941f672eaf4fcbdc5254309713fe`

## Task 0 Reaction timing

| Reaction | Requested ms | Old mean ms | New mean ms |
|---:|---:|---:|---:|
| .40 | 560 | 600 | 560 |
| .50 | 540 | 600 | 540 |
| .60 | 520 | 600 | 520 |
| .70 | 500 | 500 | 500 |
| .80 | 480 | 500 | 480 |
| .90 | 460 | 500 | 460 |
| 1.00 | 440 | 500 | 440 |
| .783 | 483.4 | 500 | 483.4 |

Decisions still happen at a Native boundary. Each consecutive deliberate decision advances the previous deadline by its requested interval. The scheduler resets after a missed whole interval or a Reflex-controlled commitment. The millisecond means above use a 100 ms grid with 10,000 consecutive decisions. The clock does not change the fixed observation schedule or Ball Handling's release clock.

Task 0 alone reported `753 passed, 1 warning, 23 subtests passed in 646.56s (0:10:46)`. All six legacy rows matched. The compatibility run reproduced gate d. CORE seed 1 finished **61–80** in **32,509 steps**.

- CORE trace `c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256`
- CORE state `c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745`
- CORE config `e3eb027d0506db1297def02bb74924cb9c3878fa17226ffb6a47e56722976835`

## Replay and firewall

The snapshot extends the rulebook review boundary to the full running graph, including clocks, field bodies, possession, rules and counters, active motor commitments, observation delivery and MESH queues. A captured decision stores the delivered view and the turn's position in the tick. The state aliases and private physics namespace are rebound in a newly booted driver. RNGs are restored with their stream states. The trace prefix is captured as the original hashed bytes.

The static firewall test checks live Native, frozen substrate and B1 source for ORACLE imports. The regular runner has no ORACLE import or snapshot work. A fresh-process restore runs the normal continuation path. The saved fit stays in `native/oracle/artifacts/`.

Every continuation reproduced the uninterrupted final score, steps, config, trace and state. Compatibility also reproduced the owner hashes in gate d. The uninterrupted CORE fingerprint matched Task 0.

| Capture step | CORE continuation CPU s | Compatibility continuation CPU s |
|---:|---:|---:|
| 4,000 | 129.9 | 122.2 |
| 14,000 | 87.9 | 83.0 |
| 25,000 | 35.9 | 34.2 |

The authored carrier scene resolved its forced first choice in 13 steps through a score. The receiver scene supplies its first observation with 300 ms of nominal horizontal travel to the receiver's initial x-coordinate. The engine registered the catch 279 ms after delivery. Both event traces are saved in the evidence directory.

## Drill sample

The three neutral-real CORE matches recorded every delivered decision. Each journal includes the observed tracks and ball course, the owning ratings, the menu values, and the selected action. Procedural turns may have a procedural menu in place of a rated Strategy menu.

| Match seed | Score A–B | Decisions logged | Mining CPU s |
|---:|---:|---:|---:|
| 1 | 61–80 | 160,374 | 258.6 |
| 2 | 79–71 | 158,414 | 260.9 |
| 3 | 78–84 | 162,154 | 265.3 |
| Total | | 480,942 | 784.8 |

The carrier sample assigned ten decisions to each distance and pressure stratum. Pressure uses the Playmaking predicate on the athlete's delivered beliefs. The three sub-agent samples each contain 30 commitments selected by the same stable decision-identity ranking.

| Stage or stratum | Eligible | Sampled |
|---|---:|---:|
| Carrier, under 20 m, open | 596 | 10 |
| Carrier, under 20 m, pressured | 330 | 10 |
| Carrier, 20–40 m, open | 1,204 | 10 |
| Carrier, 20–40 m, pressured | 1,143 | 10 |
| Carrier, over 40 m, open | 3,540 | 10 |
| Carrier, over 40 m, pressured | 3,133 | 10 |
| Passing | 925 | 30 |
| Finishing | 262 | 30 |
| Takedown | 1,752 | 30 |

The complete compressed journals and captured source moments live in `/workspace/rb326-evidence/mined/`. The committed journal manifest lists the byte counts and SHA-256 fingerprints. The selected beliefs and individual rollout and Gauge rows are the review dataset.

## Rollout scoring and timing

Each feasible option received 20 branch seeds derived from the captured moment, option index and replicate. At a sub-agent decision the branch replays the commitments that already led to that menu. The intervention changes only the designated choice. The return is the scoreboard change for the choosing athlete's team minus its opponent's change, measured at the stopping tick.

| Stage | Branches | CPU s | CPU s per branch | Time caps |
|---|---:|---:|---:|---:|
| Playmaking carrier | 4,540 | 1,465.1 | 0.323 | 1 |
| Passing | 2,640 | 292.2 | 0.111 | 3 |
| Finishing | 2,300 | 182.4 | 0.079 | 15 |
| Takedown | 2,400 | 192.0 | 0.080 | 77 |
| Total | 11,880 | 2,131.6 | 0.179 | 96 |

The mean cost per graded decision was 14.21 CPU seconds. Each option has its own mean, standard error and reason counts in `rb326/evidence/grades.jsonl.gz`. The 96 capped branches contributed accrued points and any events observed by the cap. The Passing branches include 1,301 completions and 1,131 misses. Takedown recorded 1,181 counted groundings and 1,142 ended holds.

## Hand-set values against rollout returns

Best-option agreement includes ties. Rank agreement is mean Kendall tau-b over menus where it is defined. Each row's regret averages across menus with at least two options.

| Stage | Multi-option menus | Defined ranks | Mean tau-b | Hand-set best in rollout-best set | Unique rollout bests | Mean points lost |
|---|---:|---:|---:|---:|---:|---:|
| Playmaking carrier | 60 | 56 | −0.00374 | 33.3% | 54 | 0.56750 |
| Passing | 29 | 2 | 0.08333 | 93.1% | 2 | 0.00862 |
| Finishing | 28 | 28 | 0.01607 | 25.0% | 15 | 0.82857 |
| Takedown | 30 | 0 | Undefined | 100% | 0 | 0 |

The hand-set best matched 15 of 54 unique carrier winners, neither of the two unique Passing winners, and one of 15 unique Finishing winners. Every Takedown option scored zero at the immediate action horizon. Passing was also usually tied on points, even when the options had different completion outcomes.

In 23 moments the hand-set best lost at least one estimated point. The largest gaps were 3.15 points for a carry compared with a shot, 2.80 for a carry compared with a pass, and 2.55 for the selected finishing lane compared with two alternative aims. The summary lists each moment and the corresponding options. The per-option standard errors describe finite rollout uncertainty.

The `−1.40` shot offset was relevant to 17 menus containing shots. Removing it in an offline re-ranking changed the hand-set winner in one menu and reduced mean regret in that subset from 1.044 to 0.903 points. The result describes the sampled menus under the existing continuation policy.

## Held-out value tables

`native/oracle/artifacts/drill-v0.json` contains the versioned fit. Seeds 1 and 2 supplied training outcomes and seed 3 supplied held-out outcomes. Populated cells shrink toward the training mean with the weight of five trials. Unseen cells predict the training mean. The pass and shot labels record success within the rollout horizon. Tackle risk records a counted grounding of the original carrier. Field-position points average the sampled intervention options equally.

| Table | Train | Held out | Held-out MSE | Pooled baseline MSE | Unseen held-out rows |
|---|---:|---:|---:|---:|---:|
| Pass completion by lane, distance and pressure | 2,620 | 1,020 | 0.25312 | 0.25114 | 40 |
| Tackle risk by free run | 1,120 | 700 | 0.13649 | 0.13748 | 0 |
| Shot conversion by distance, lane and believed Keeper offset | 1,580 | 1,060 | 0.25682 | 0.25978 | 460 |
| Points by field position | 2,600 | 1,940 | 2.40538 | 2.37846 | 0 |

The shot and tackle tables improved on the pooled prediction in this holdout. The pass and field-position tables increased error. About 43% of held-out shot rows landed in unseen cells. The fit measures new matches of the same teams under the existing CORE continuation policy.

## Gauge pilot

Each level used the same 60 carrier moments and the same 20 decision seeds per moment. Ratings other than Playmaking stayed at 0.70. The decision seed was paired across levels. Scores compare the normal selected option against the best option under the stated value source.

| Playmaking | Trials | Rollout regret, points | Belief regret, hand-set units | Regret after belief error |
|---:|---:|---:|---:|---:|
| 0.40 | 1,200 | 0.54242 | 0.01376 | 0 |
| 0.70 | 1,200 | 0.55088 | 0.00210 | 0 |
| 1.00 | 1,200 | 0.56750 | 0 | 0 |

The true-regret criterion was **unmet**. Playmaking 1.00 incurred 0.02508 more points of rollout regret than 0.40 in this pilot. Higher Playmaking followed the underlying hand-set values more closely. The chooser maximizes the perturbed believed value by construction, so regret against that value is zero at all levels. The pilot measures the recorded moments and the finite rollout estimates for each option.

See `rb326/README.md` for commands and `rb326/evidence/` for raw results.
