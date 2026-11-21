# HP-002 Codex checkpoint — 21 November 2026

## OWNER BRIEFING

1. **Accomplished.** Reconciled the Codex line to the exact RB-3.22 source tree, checked keeper geometry and running speed, and staged the draft ratings.
2. **What it can do now.** Native runs the RB-3.21 defaults and can store draft technical and mental ratings separately from the ratings used in matches.
3. **Unproven.** The neutral-rating soak is in progress. The post-preparation full-suite and replay checks passed. Carrier moves phase 2 is deferred within this run budget.
4. **Blocking.** GitHub did not return the named talent-soak branch. The missing matches are running from the reconciled source.
5. **Recommended action.** Use the reconciled code as the review point and use the paired neutral-rating runs to assess the talent-gap breakdown.

## 1. Reconciliation

**IMPLEMENTED and TESTED** on `codex/rb-3-22-reconciled` at `eb30f605f24b906777b88d6cb3a552b3584639ef`. Parents are `ac520686ea9` and `e6ca6a4e3bc7e76493d6aa2999acb48f4bf9dcc5`. The complete tracked tree matches the latter, `9ef4eff55dd3d91a7f3f11bb65d992545cd0bfa0`. Where older Codex-only restart behavior differed, exact RB-3.22 parity took precedence.

The reconciled tree already uses the shared per-athlete release clock, `round(250 * (1.35 - 0.5 * ball_handling))`, for the view and the executing port. The workbook converts arm span to arm reach by halving it (median 1.23425 m across 712 players at workbook ref `81f92e3`) and keeps standing reach separate. The control arm reach is 1.26431 m. The keeper's standing hand point and hand radius are 0.62 times height and 0.9 times arm reach, respectively. The keeper forecast fallback uses the control reach, and the rulebook port populates `body_height`.

### Standing gates

a) Full suite AFTER your last change: pytest -q b1 native (not a subset).

b) Legacy hash guards unchanged (native-v0/2, v0/3, rb/2; seeds 1 and 3 over 3000 steps; reference native/evidence/rb3-reach/legacy-hashes.txt).

c) Determinism: same code + roster + seed gives identical trace and state hashes.

d) Identity: unless a task says it changes behavior, real seed 1 and control seed 1 reproduce the RB-3.21 soak gate hashes 44399b08... / 046ea55b... (full values in claude/soak-rb-3-21 @ 9e66749).

| Gate | Reconciled source | Draft-rating preparation |
|---|---|---|
| a | **TESTED** — 662 passed, 23 subtests passed | **TESTED** — 665 passed, 23 subtests passed |
| b | **TESTED** — six trace/state/config rows matched | **TESTED** — the same six rows matched |
| c | **TESTED** — real seed 1 matched across the instrumented run, the local suite and the upstream run. | **TESTED** — paired 300-step runs with and without supplied draft values match each other. The real seed-1 full run also matched in the suite. |
| d | **TESTED** — both full matches matched all three hashes | **TESTED** — real seed 1 matched in the full suite, and the full control replay matched trace, state and config |

Full hashes from the `eb30f60` runs, compared with `9e66749`:

| Seed-1 block | Score (A–B) | Trace | State | Config |
|---|---:|---|---|---|
| Real | 57–76 | `44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072` | `046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d` | `3d66214c927b42abf493bfe93c9d7ef85675364f54b5e6a9f245daadc4799550` |
| Control | 55–79 | `b4f5ed690665f894ad06560b1108a83f9b556b9cfe50e56463fdc39adb9f523b` | `b28b5ba40f82c6d0d601af8dc6a8a86e0b3dcad763df14b6c75da83cd6645676` | `a7801233eda227769c11718f57f11db6b7e27b6c2cd72170899e1c01844ff89c` |

Run `python -m native.rulebook.scoring_audit --legacy` for the six 3,000-step cases. For the full gates run `python -m native.rulebook.reach_run --block real --seed 1 --outdir /tmp/rb322-real` and the same command with `--block control` and a separate output directory. The result files, gzipped logs and observed legacy hashes are in `native/evidence/rb322-codex/reconcile/`.

## 2. Talent-gap soak

**TESTED** for the default block, using the 10 original per-match results at `9e66749:native/evidence/rb321-soak/real/`. The three neutral blocks are in progress at the time of this checkpoint. The 16 completed matches in this snapshot, their paired seeds, their per-match results and their event streams are recorded under `native/evidence/rb322-codex/talent/`. Technical-neutral and physical-neutral seed 1 reuse the per-match files on `e6ca6a4` in `native/evidence/rb322/runs/`. Missing matches run from a clean Python-source export of `eb30f60`, with roster workbook ref `81f92e3` and a maximum of two matches at a time.

The estimator weights each team-match equally for median, possessions and pooled standard deviation. The margin is Ala (B) minus Garvian (A). SDs are sample SDs. The median describes the 20 team scores from this fixture. Raw score events and changes in passive possession were also checked against the per-match records.

| Mode | Seeds | Median team points | Possessions/team | Ala mean margin | Ala wins | SD Garvian / Ala / pooled |
|---|---|---:|---:|---:|---:|---|
| Default | 1–10 | 84.5 | 151.95 | +32.1 | 9/10 | 12.85 / 16.68 / 21.93 |

`python -m audit.native.rb322_talent_probe RESULTS_ROOT --verify-raw` recomputes from per-match files and verifies seed, terminal status, score and possession count. Use `--allow-partial` while the soak is running. The optional runner fills missing result files using `reach_run`. The physical-neutral block equalizes the nine ratings while retaining body differences and the OVR-selected players. Technical neutral equalizes current technical proxies. Both-neutral retains those bodies, roster selection, side assignment and seeded match effects.

## 3. Keeper save physics

**TESTED**, read-only, against `eb30f60`. `python -m audit.native.rb322_physics_probe` reproduces the isolated lab evidence in `native/evidence/rb322-codex/physics-probe.json`. At each distance and aim the drill exercised awareness .5/.7/.9 with and without a perfect release-time save intent. The latter still went through the normal motor reaction gate. The 2.39 m control keeper had a 1.482 m hand centre, 1.138 m hand radius, and nominal depth one quarter of shot distance. RB-3.21 ball launch and flight ran at 58 m/s initial speed.

| Release distance | Time to keeper depth, centre / wide | Ball centre to goal plane, centre / wide | Central shot event | Wide and low | Wide and high |
|---:|---|---|---|---|---|
| 10 m | 130 / 134 ms | 173 / 178 ms | Catch at 119 ms | Goal at 180 ms | Frame at 180 ms |
| 12 m | 156 / 159 ms | 208 / 212 ms | Catch at 145 ms | Goal at 214 ms | Frame at 213 ms |
| 15 m | 195 / 197 ms | 260 / 263 ms | Catch at 184 ms | Goal at 265 ms | Frame at 265 ms |

Central aim was 1.50 m high. Wide aim was 2.40 m off centre at 0.40 and 2.00 m high. At 12 m, the wide low shot was 1.80 m lateral and 0.77 m vertical from the standing hand point at depth, 1.96 m away. The wide high shot was 1.80 m lateral and 0.43 m vertical at depth. Its plane aim is outside the semicircle. Step travel, lift and dives were zero in all 54 trials. The keeper motor reaction was 200/176/152 ms across the awareness values, with another 100 ms for an unset keeper and a 100 ms dive lead requirement. The normal sensor delay is 200 ms. The 36 real-body trials produced the same outcomes without motion or dives. Garvian starter NBL24-07-11 had 1.128 m coverage and 165.2 ms deliberate reaction. Ala starter NBL24-01-11 had 1.331 m coverage and 158.0 ms reaction. Both bodies were loaded unchanged from workbook ref `81f92e3`.

The observed saves did not require superhuman movement or reach. The catch kernel separately samples when a player can set their hands, using a 120 ms base time constant scaled by awareness. The 120 ms is a stochastic mean at .5 awareness and permits earlier reactions. At .7 awareness, the mean is 105.6 ms. A 0.4 kg ball at 58 m/s carries about 673 J. Native uses Catching for all roles and gives the .70 control keeper 1,109 J centred arrest capacity. The actual central contacts had 86.6% modelled security conditional on timely hands. The capacity and readiness curves are calibration assumptions. It uses the live flight clock, so the keeper may secure a ball on his standing hands before a deliberate movement command can arrive. Central placement and that reflex assumption can contribute to the reported save rate. This forced lab does not estimate the match save rate or validate the stochastic readiness curve empirically. It found no engine-law contradiction that called for a fix commit. References are `native/port.py::keeper_motor`, `native/substrate.py` (0.9 reach patch), `native/rulebook/ball_material.py`, `native/rules.py` (Native arrest capacity), and `core_src/match.py` (catch readiness and energy check).

## 4. Achieved speed

**TESTED**, read-only, against `eb30f60`. This forced straight-run lab used the actual C3 motor at 100 ms intervals with a fresh athlete (fatigue multiplier 1.0), no hold or opponent, a target beyond braking distance, and virtual runway to avoid the boundary. Acceleration rating was held equal to speed rating for this table. The measured values were identical on and off the ball.

| Rating | Canon m/s | 1 s | 2 s | 3 s | 10 s |
|---:|---:|---:|---:|---:|---:|
| 0.00 | 0.0000 | 0.00 | 0.00 | 0.00 | 0.0000 |
| 0.40 | 17.8816 | 5.00 | 10.00 | 15.00 | 17.8816 |
| 0.60 | 26.8224 | 7.50 | 15.00 | 22.50 | 26.8224 |
| 0.70 | 31.2928 | 8.75 | 17.50 | 26.25 | 31.2928 |
| 0.80 | 35.7632 | 10.00 | 20.00 | 30.00 | 35.7632 |
| 1.00 | 44.7040 | 12.50 | 25.00 | 37.50 | 44.7040 |

All nonzero ratings hit their caps by the 4 s sample. Native removes the old carrier/off-ball factors from the C3 cap in `native/substrate.py`. The actual motor in `core_src/match.py::c3_move` still decelerates on approaches and in contact. The drill isolates top speed from those match effects.

## 5. Draft ratings preparation

**IMPLEMENTED** at `bb782f6061b2d305a0a9b9a44f7d91702c9556cf` and **TESTED** in three focused scenarios, the 665-test full suite, the six legacy windows and both baseline full-match replays. The post-preparation test log and control raw replay are in `native/evidence/rb322-codex/staged/`. `native/nbl_roster.py` accepts all 18 optional names on the workbook's 0–100 scale, normalizes them, and records which cells fall back to Opening-day OVR. These values live in the staged roster record. Active gameplay ratings, roster/config replay digests and athlete views keep their current inputs. Engine `finishing` and `long_shot` each initialize to the old kicking value of zero. The existing live throw-power-derived speed ceiling remains in effect. `rb3_stage_throw_power` defaults false and, when true, supplies raw normalized Throw Power as a separate engine input for a later mapping. Three focused tests cover the draft fields, a forced invalid rating, hash identity in a paired bounded run, and the switch. No ratings were generated.

## 6. Carrier moves phase 2

Deferred for the available match budget. No phase 2 code or result is claimed. Existing carrier moves and defaults come from the reconciled tree.

## Open questions

The technical specification is under owner review. The activation step needs a confirmed relationship between the existing throw-power ceiling and any new mapping, and a decision on the population and provenance of draft ratings. This checkpoint supplies inputs for that review.
