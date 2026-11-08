# HP-001 T2 — Runtime Patch-Chain and Decision-Ownership Audit

**Status:** T2 complete; awaiting approval. T3 has not started.  
**Accepted baseline preserved:** B0-P4-DEFAULT, commit `2abe497ca82588cb2d8c871a7aab61daaae95c12`.  
**Audit date:** 2026-11-06.  
**Method:** source inspection plus read-only runtime instrumentation. No simulator source or behavior was changed.

## 1. Executive finding

Pocket 4 is not a single controller with a clean cognition → motor → physics boundary. It is an ordered patch stack over the embedded Pocket 2 core. Decision ownership is shared as follows:

1. PRISM owns belief construction and, when enabled, temporarily substitutes belief-state positions into selected legacy policy calls.
2. Legacy `Policy.targets`, positional tendencies, C4c2 valuation, and pass policy still generate most candidate targets and action values.
3. PRISM split-judgment and off-ball layers perturb or replace parts of those outputs; they do not replace the carrier controller.
4. The legacy C4c2 controller remains the final carrier action selector.
5. “Motor Control” is not a discrete component. Release timing, pose, throw/kick sampling, individual decision cadence, locomotion limits, and contact response are distributed across Pocket 4 wrappers and the C3 kernel.
6. C3 and `Engine` own physical integration and ordered event commitment.

This architecture can support B1 only if validation explicitly tests precedence, state visibility, and wrapper cardinality. It is not safe to infer decision ownership from filenames or feature flags alone.

## 2. Scope and preservation

The audit operated on the exact T1 source reconstruction and used only:

- `sys.settrace` to observe `patch_source`'s unmodified replacement list;
- code-object and closure inspection to compare pristine and installed runtimes;
- `sys.setprofile` to observe one deterministic decision and its delayed physical execution;
- static source review.

No source under `repo2abe497/` was edited. No physics, ratings, rules, kicking, formation mode, cognition migration, or native implementation was changed.

## 3. `patch_source` replacement map

### 3.1 Installation semantics

`load_pocket()` calls `patch_source()` before importing the embedded core (`pocket4_proto.py:75-121`). The function:

1. reads the monolithic source;
2. builds an ordered list of `(anchor, replacement)` pairs;
3. checks only `if anchor not in text`;
4. applies `text.replace(anchor, replacement)`, replacing **every** occurrence;
5. imports the resulting temporary source.

It never asserts an expected match count.

### 3.2 B0 map

B0 activates the patcher because `KEEPER_STEP_FRAC` defaults to `.5`, while the early-return condition treats `.95` as the unpatched value. Seven replacements are installed:

| # | Dependency | Source line(s) in monolith | Exact matches | Effective B0 result |
|---:|---|---|---:|---|
| 1 | `ARCH_RMIN`, `ARCH_RMAX` | 1770, 1792, 3794 | **3** | Identity text at defaults (`10<=d<=70`), but all three sites are owned by one broad anchor. |
| 2 | `ARCH_RMIN`, `ARCH_RMAX` | 3774 | 1 | Identity text at defaults. |
| 3 | `ARCH_NEAR` | 3774 | 1 | Identity text at default 9 m. |
| 4 | `RULESET` | 5829 | 1 | Identity text at default `1.0.1`. |
| 5 | `KEEPER_STEP_FRAC` | 3219 | 1 | Changes `.95*R` to `.5*R`; this is part of accepted B0. |
| 6 | `PLAT` | 1780 | 1 | Adds a platform-aware branch; with `PLAT=0`, runtime behavior falls through to the historical service-zone test. |
| 7 | `PLAT` | 2400 | 1 | Adds a platform-aware branch; with `PLAT=0`, runtime behavior falls through to the historical archer-zone test. |

The first anchor proves that “anchor present” is not equivalent to “one intended site.” `all_anchors_exactly_once` is false in B0.

### 3.3 Maximal map and flag dependencies

The maximal audit configuration produced 28 ordered replacement specifications:

| Indices | Flag dependency | Sites | Match-count result | Behavioral target |
|---|---|---|---|---|
| 1–2 | `ARCH_RMIN`, `ARCH_RMAX` | 1770, 1792, 3774, 3794 | #1 = **3**; #2 = 1 | Release legality, impact-range eligibility, structural target filtering, and final range check. |
| 3 | `ARCH_NEAR` | 3774 | 1 | Structural archer target proximity to carrier. |
| 4 | `RULESET` | 5829 | 1 | Runtime ruleset configuration literal. |
| 5 | `KEEPER_STEP_FRAC` | 3219 | 1 | Keeper step-versus-dive reach fraction. |
| 6–7 | `PLAT` | 1780, 2400 | 1 each | Service and archer-zone eligibility. |
| 8–9 | `NET_R != 6` | 401, 4906 | 1 each | Goal aperture and frame-contact radius. |
| 10–11 | `PRISM_JSPLIT=1` | 3449, 5599 | 1 each | Inserts `judge_opts` into both carrier decision implementations. |
| 12–13 | `KEEPER_FT != 0` | 193, 9706 | 1 each | Configuration and serialized default keeper height. |
| 14–21 | `CATCH_V2=1` | 5029, 5064–5082, 4934, 5004, 5301, 3203 | #19 = **2**; all others = 1 | Catch reaction/capacity/security/acquisition hooks and removal of keeper-specific reach multipliers. |
| 22–28 | `PRISM_KEEPER=1` | 3150, 3145, 3147, 3149, 3154, 3177, 3155 | 1 each | Keeper awareness, notice, observation time, readiness, wake time, belief-ball path, and crossing judgment. |

The complete exact old/new strings, ordered indices, hashes, match counts, and source line lists are in `t2_audit/patch_map_b0.json` and `t2_audit/patch_map_maximal.json`.

### 3.4 Failure modes

| Risk | Result |
|---|---|
| Missing anchor | Loud: raises `RuntimeError`. |
| Duplicate anchor | **Silent:** every occurrence is replaced. This is demonstrated by indices 1 and 19. |
| Identity replacement | Can conceal duplicate ownership; B0 index 1 matches three sites but leaves identical text. |
| Semantically unrelated duplicate | No site validation exists; a future matching literal would be patched automatically. |
| Ordered overlap | Later anchors operate on already modified text and can fail or change cardinality. |
| Flag timing | `PLAT`, range values, `CATCH_V2`, `PRISM_JSPLIT`, and `PRISM_KEEPER` are captured at module import. Changing them after import does not rebuild the core. |
| Temporary-source identity | Runtime code locations may be embedded or temporary rather than the checked-in monolith, complicating traceback/source attribution. |

## 4. Runtime override and wrapper inventory

### 4.1 Counts

| Configuration | Pristine attrs | Installed attrs | Changed | Added | False positives | Effective differences |
|---|---:|---:|---:|---:|---:|---:|
| B0-P4-DEFAULT | 334 | 334 | 32 | 0 | 2 dataclass methods | **30** |
| Full cognition audit | 334 | 348 | 50 | 14 | 2 dataclass methods | **62** |

The two excluded entries are `Tactics.__setattr__` and `Tactics.__delattr__`, regenerated by the dataclass machinery in separate processes. The full 96-row comparison, including original function, effective function, and recursively captured closure chain, is in:

- `t2_audit/RUNTIME_OVERRIDE_INVENTORY.md`
- `t2_audit/runtime_override_inventory.csv`
- raw snapshots and diffs under `t2_audit/runtime_*.json`

The B0 effective set is 16 `Engine` methods, 13 `Match` methods, and `Policy.targets`. The earlier T1 phrase “15 Engine / 14 Match” was a classification error; the total of 30 was correct. Independent symbol enumeration gives 16/13/1.

### 4.2 Installation order

Installation order is behaviorally significant because each wrapper captures the method that exists at that moment:

| Order | Installation | Principal ownership |
|---:|---|---|
| 1 | `patch_source` before embedded import | Source literals and inserted call sites. |
| 2 | Pocket 4 base assignments | `Match.__init__`, `Match.step`, `Match.auto_substitutions`. |
| 3 | `positional_tendencies_v1.install` | `Policy.targets`, C4c2 values, pass-option value. |
| 4 | `restarts_v1.install` | Restarts, dead-ball targets, Hunt, several Engine wrappers. |
| 5 | Archer loop fix | `Match.arrow_decisions`. |
| 6 | Optional platform/quiver/freeze/capability study hooks | Import-time flag dependent. |
| 7 | Arrow lead | `Engine.shoot_arrow`. |
| 8 | Throw aim and pose-delay wrappers | `aim_error`, `make_pass`, `make_shot`. |
| 9 | `THROW_SPLIT` | `plan_pass`, `make_shot`, `__init__`; active in B0. |
| 10 | `PRISM_FIELD` | `Match.step`, `Policy.targets`, pass ranking/choice. |
| 11 | `PRISM_MANEUVERS` | Carrier pose/maneuver step and Engine contact outcomes. |
| 12 | Archer PRISM shadow layer | `PRISM=1`; cognition logging, nominally no decision change. |
| 13 | `CATCH_V2` | Catch/contact/movement methods and helper additions. |
| 14 | `PRISM_JSPLIT` | Judgment helpers and defender-duel wrappers. |
| 15 | `HAND_FIGHT` | `move_players` physical hand-fight wrapper. |
| 16 | `PRISM_OFFACT` | Outer `Policy.targets`; wraps `route_receiver` and `c4c2_targets`. |
| 17 | Keeper/catcher PRISM | Keeper perception and helper additions. |
| 18 | Optional keeper trace | Diagnostics. |
| 19 | `RULES_V03.install` | Fouls, discipline, lineup, ammunition, scrimmage, step. |
| 20 | `RULES_V03.install_nokick` | `make_pass` and `make_shot`, regardless of whether the flag is on. |
| 21 | Block option | Outer `Policy.targets`. |
| 22 | Bounce option | Outermost `Policy.targets`, carrier decision, pass/shot planning, step, acquire/recontact. |

### 4.3 Important flag dependencies

- `PRISM_I=1` sets defaults for only `PRISM_FIELD`, `PRISM_DEF`, `PRISM_BOUNDED`, and `PRISM_MANEUVERS` (`pocket4_proto.py:26-28`). It does not enable off-ball cognition, teammate/free-ball views, split judgment, off-ball actions, catch v2, keeper PRISM, or hand fighting.
- `PRISM_JSPLIT`, `CATCH_V2`, and `PRISM_KEEPER` affect both pre-import source patching and later method installation. They must be set before importing `pocket4_proto`.
- `PRISM_OFFACT=1` without `PRISM_FIELD=1` installs a wrapper but normally returns unchanged because `S.m` is never established: a silent dependency.
- `HAND_FIGHT=1` without catch v2 installs the movement wrapper, but `fight()` exits when `hc_logit` is absent: another silent dependency.
- Keeper PRISM installs when `PRISM_KEEPER=1`, or when `CATCH_V2=1` and `PRISM_CATCHERS` is not explicitly disabled.
- `RULES_V03`, `RV03_SCRIM`, and `RV03_NOKICK` are checked at runtime by installed wrappers, while scoring/marking settings are transformed only when `RV03.settings()` is called during match setup. Mid-process flag changes can therefore create a mixed rules state.
- Block and bounce wrappers are always installed. Their feature switches default on, but B0 team gene rates default to zero, so their decision options are dormant while their wrappers remain in the chain.

## 5. Decision-ownership map

### 5.1 Full target chain

Under the full audit configuration, the outer-to-inner policy chain is:

`bounce_option.targets` → `block_option.targets` → `offball_actions.targets` → `prism_field.targets` → `positional_tendencies.targets` → legacy `Policy.targets`.

After both team policies return targets, `Match.step` invokes `c4c2_targets`, then `route_receiver`, then C3 (`core_src/match.py:2493-2502`). Off-ball actions wrap both post-policy overrides and restore a player's chosen off-ball action (`offball_actions_v0.py:129-141`).

### 5.2 Carrier action chain

1. Legacy `carrier_decision` checks eligibility, pending actions, phase, pressure, clock, and role (`core_src/match.py:917-969`).
2. With C4c2 active, it delegates to legacy/source-patched `c4c2_decide` (`core_src/match.py:642-683`).
3. `Policy.pass_ranked` is run through the carrier's PRISM view and optional Playmaking noise (`prism_field_v0.py:260-277`).
4. Positional tendencies modify `c4c2_eval`, `c4c2_cont`, and pass-option values (`positional_tendencies_v1.py:354-381`).
5. The source-inserted `judge_opts` perturbs shoot/carry/pass valuation for split judgment (`judge_split_v0.py:17-24`).
6. **Legacy C4c2 still selects `max(opts)` and applies style-band overrides.** PRISM does not own the final selection.
7. A pass/shot enters the outer wrapper chain and becomes `pending_ball_actions`; a carry changes `c4c2_intent`; continue leaves the prior motion target in force.

### 5.3 Motor Control and physics

There is no single Motor Control API. Effective ownership is distributed:

| Function | Effective owner |
|---|---|
| Individual target acceptance cadence | C3 `c3_move`: a newly generated target is copied to `p.target` only when `now >= p.next_decision` (`core_src/match.py:1298-1302`). |
| Acceleration, braking, turning, speed intent | C3 `c3_desired` and capability-updated athlete attributes. |
| Release preparation | Legacy `make_pass`/`make_shot`, with P4 pose-delay wrapper and C3 withholding/restraint. |
| Release power/accuracy | Pocket 4 throwing or kicking model in the per-match `Engine.release` wrapper (`pocket4_proto.py:168-181`). |
| Carrier maneuvers | Optional `pose_engine_v0`; policy currently uses true nearest-threat state. |
| Contact and locomotion | C3 integration/contact kernel. |
| Ball/arrow flight | `advance_ball`/`advance_arrows`. |
| Final state changes | Ordered `process_events` → `Engine` methods. |

This distributed boundary is the main decision-ownership risk for B1: replacing cognition alone will not remove legacy target cadence, target overwrites, release heuristics, or true-state motor hooks.

## 6. Complete decision-to-outcome trace

The reproducible trace uses seed 1 with the full cognition audit flags and `RULES_V03=0`. It begins at `t=1389 ms` with B0 carrying the ball.

| Stage | Observed result |
|---|---|
| Wrapper entry | `bounce → RULES_V03 → keeper PRISM → pose → field PRISM → restarts → P4 → embedded Match.step`. |
| Target production | Legacy positional targets run inside PRISM belief substitution, then off-ball/block/bounce layers. The current policy output for B0 is `(12.0311, 36.0792)`. |
| Motor cadence | B0's held motor target remains `(14.3580, 50.0625)` because his next individual target-decision time has not arrived. |
| Carrier options | After positional values and split judgment: shoot `0.37590`, carry `0`, continue `1.34215`, pass `1.51461`. |
| Final action owner | Legacy C4c2 selects pass to B6. |
| Preparation | `pending_ball_actions['B0'] = (1945, 'pass', 'B6')`; preparation delay is 556 ms. |
| Same decision tick physical result | C3 advances 100 ms: B0 moves `(-1.41033, -0.05766) m` and velocity changes `(-1.65169, -1.10762) m/s`; ball remains controlled. |
| Delayed execution | Six later steps reach `t=1945 ms`; carrier decision executes the pending pass through bounce → RULES no-kick wrapper → P4 pose/throw wrapper → embedded `make_pass`. |
| Physical release | P4 samples the throw; embedded `Engine.release` commits ball mode `PASS`, target B6, and velocity `(36.41958, 6.68711, 4.57254) m/s`. |
| Post-execution state | At `t=2045 ms`, ball is in flight with no carrier; the pending action is cleared. |

Every profiled call/return, source file/line, actor-local identification, before/after state, option values, pending action, and release event is preserved in `t2_audit/decision_tick_trace.json`.

## 7. Legacy anchors, movement overrides, and true-state access

### 7.1 Positional anchors still active

Legacy `Policy.targets` contains all of the following:

- slot-based rows and widths (`slot % 5`, `slot % 3`);
- carrier lane menus;
- escort rings/wedges;
- man assignments by slot;
- hunt/zone lines and pursuit counts;
- fixed keeper home/ball-follow targets;
- free-ball chase counts;
- award/restart spacing.

See `core_src/policies.py:83-194`.

`positional_tendencies_v1` then applies archetype-specific `rule_lane` tables, attacking/defending leads, lanes, advancement, cover, chasers, and fixed spot menus (`positional_tendencies_v1.py:189-222, 233-351`). `DEF_FREEDOM` changes how selected defensive archetypes advance; it does not create formation-free behavior.

`restarts_v1` contains explicit formation tables and snap alignments (`restarts_v1.py:23-61, 209-260`). Whether dead-ball formations should remain in a future formation-free mode is a canon decision, not an implementation detail.

### 7.2 Movement-target override order

1. Both policies generate base targets.
2. C4c2 can overwrite the carrier target for carry intent and up to `ctrl_receivers` receiver spots (`core_src/match.py:684-717`).
3. `route_receiver` overwrites the intended receiver with an intercept of the **actual** current ball path (`core_src/match.py:2508-2517`).
4. Off-ball actions, if active for that athlete, restore their PRISM-selected target after both overrides.
5. C3 may still hold the athlete's previous `p.target` until the athlete's individual decision cadence permits adoption.
6. Pose maneuvers may then directly nudge position and scale velocity after normal integration (`pose_engine_v0.py:87-127`).

Thus “the target returned by cognition” is not necessarily the target physically followed in that tick.

### 7.3 True-state access

| Component | State used | Audit conclusion |
|---|---|---|
| Legacy `Policy.targets` and pass utilities | Full player and ball state | Omniscient unless called inside `with_view`. |
| PRISM `with_view` | Temporarily mutates shared player/ball objects to beliefs | Converts many legacy reads, but is mutation-based, non-thread-safe, and incomplete for data not swapped. Restores in `finally`. |
| PRISM base `out` | Initially generated once on true state | Some athletes are later replaced with belief-view outputs; unchanged athletes retain omniscient targets. |
| Unseen teammate with no belief | Actual formation position | Explicit true prior at `prism_field_v0.py:132`; counted as `mate_prior_true`. |
| PRISM regret telemetry | True state | Diagnostic only in reviewed paths; does not change the returned choice. |
| C4c2 option values | True/current match state, except pass ranking's view | Shoot/carry/continue values and opponent lists remain substantially omniscient. |
| Off-ball action base target | Inherited engine target | PRISM scoring searches around a legacy/possibly omniscient anchor by design. |
| `route_receiver` | Actual ball position/velocity | Explicitly actual observable state; no individual observation latency. |
| Pose maneuver threat | True nearest opponent, distance, velocity | File documentation admits no PRISM belief yet. |
| Block option | True positions | File documentation marks this provisional. |
| Hand fight and C3 | True physical state | Correct for physics, but must not feed private state back into cognition without an explicit observation boundary. |

The `with_view` audit sentinel can detect hidden-body coordinate leaks inside the wrapped call, but it does not prove that all upstream anchors, cached values, globals, post-policy overrides, or auxiliary option values are belief-owned.

### 7.4 Conflict with formation-free emergence

Formation-free behavior would conflict with at least four active owners:

1. legacy slot/row/escort/man/zone targets;
2. positional-tendency lane/archetype tables;
3. C4c2 receiver spot menus and carrier goal drives;
4. restart formations and First Hunt placements.

Off-ball actions are not formation-free: their candidate set is deliberately centered on the engine's existing formation/lane target. PRISM perception changes what players think they see, not the structural target vocabulary they are allowed to choose from.

## 8. `RULES_V03` audit and B0 kicking

### 8.1 Complete behavioral effects when enabled

| Area | Effect |
|---|---|
| Match settings | Flat scoring: inner, release, outside, and carry values all 2; marking distance 5 m. |
| Discipline | Warning becomes minor; non-danger/non-serious majors are downgraded; first three minors recorded without exclusion, fourth gives 60 s exclusion, fifth disqualifies. |
| Defensive minor | Tackle count decreases by one; at zero, award 1 point in periods 1–3 or 2 points in period 4/overtime; offense keeps possession. |
| Offensive minor | Tackle count increases; a second count causes turnover through the inherited foul path. |
| Lineup | A substitute fills excluded/disqualified field slots to keep 10 field players when available; minimum-lineup terminal ground is suppressed when at least 12 eligible players remain. |
| Archery | Every new possession resets each quiver to 25 allocated, 5 loaded; freezes are capped at five per shooter team per possession. |
| Contact Scrimmage | First tackle, second-tackle turnover, fouls, Keeper Zone reset, minimum 10 m goal distance, turnover placement no worse than own 40 m, offside penalties, 10 s snap window, and conditional possession-clock running. |
| Restart integration | `restarts_v1` changes scrimmage readiness, defensive/offensive offside consequences, and disables its older first-tackle scrimmage path when V03 owns it. |
| No-kick shim | `make_pass(kind='kick')` is converted to `pass`; shots temporarily use passing in place of kicking skill. |

### 8.2 Why kicking remains enabled in B0

B0 has `RULES_V03=0`. Although the V03 and no-kick wrappers are installed, every behavior-changing branch returns to the captured original when the flag is off. The legacy controller still chooses a kick for:

- C4c2 pass choices when team risk is greater than `.7` and receiver distance exceeds 25 m (`core_src/match.py:680`);
- keeper distribution over 70 m (`core_src/match.py:949`);
- the legacy non-C4c2 trigger under the same risk/distance rule (`core_src/match.py:969`).

Those calls reach Pocket 4's per-match `Engine.release` wrapper. For `kind='kick'`, it invokes `kicking_v1.K.kick`, records the foot event, and passes `kind='kick'` into the embedded engine (`pocket4_proto.py:168-180`). The embedded engine sets `BallMode.KICK` (`core_src/engine.py:341-359`). This is the accepted historical B0 behavior and was not removed.

### 8.3 No-kick limitation

Even with `RULES_V03=1`, the shim is not a global rules gate. It wraps `Match.make_pass` and `Match.make_shot`, but not direct `Engine.release(kind='kick')`, `Engine.strike`, or a future controller that bypasses `make_pass`. Therefore “RULES_V03 eliminates all kicking” is an unverified assumption, not an invariant. B1 needs a rules-layer enforcement test at the engine boundary.

## 9. Ambiguities, conflicts, and unverified assumptions

1. **No single Motor Control owner:** the requested layer is distributed and has no stable interface.
2. **Runtime toggling can create mixed rules:** V03 wrappers read flags per call, but settings are transformed only at construction.
3. **Import-time versus runtime flags:** many PRISM and patch flags are frozen at import, while others are read at each call.
4. **Source-patch cardinality:** two maximal anchors match multiple sites; semantic intent is not machine-checked.
5. **No-kick is path-specific:** it does not enforce the rule at all physical kick entry points.
6. **Formation-free scope is undefined for dead balls:** restart alignments may be canon-preserving set pieces or prohibited positional anchors.
7. **Belief substitution is partial:** true-state option values, base anchors, caches, and post-policy routing remain.
8. **First perception tick:** field PRISM updates after the wrapped match step, so the first decision can use missing/prior beliefs and fallback paths.
9. **Shared mutable globals:** `S`, option gene tables, bounce state, and several caches persist at module scope; reset behavior is feature-specific.
10. **Wrapper reinstallability:** calling `install()` twice in one process would stack closures; no idempotence guard exists.
11. **V03 major classification:** the prose names intentional head/off-ball offenses, while code relies on `danger`, `serious_foul`, or caller-supplied metadata; the caller mapping is not proven exhaustive.
12. **Offensive-minor counter semantics:** the implementation uses the possession tackle count rather than a separate offense-minor counter.
13. **Claude coordination:** as of this audit, the repository exposes only `claude/baseline`, `claude/codex-work-package`, `claude/restore-fixtures`, and `claude/t1-b0-evidence`. No Claude T2/cognition-audit branch or artifact was available. Consequently, all T2 conclusions above are independently verified; none is adopted from an unavailable Claude claim.

The one available Claude runtime statement from T1—30 effective B0 core overrides—was independently reproduced. The total agrees; the independently corrected class split is 16 Engine, 13 Match, 1 Policy.

## 10. Recommended B1 validation tests

These are tests to authorize or reject during B1; none was implemented in T2.

1. **Patch cardinality contract:** assert exact expected counts and exact source line/semantic site for every replacement. Treat multi-site anchors as explicit separate entries.
2. **Install-chain snapshot:** compare effective original/outer/inner method chains for B0, V03, PRISM-I, and full cognition matrices; fail on unexpected wrapper order or double installation.
3. **B0 non-regression gate:** rerun the accepted ten seed/mode cases and require exact score, event count, canonical event-log hash, and result hash.
4. **Global no-kick gate:** with B1 rules, force all three legacy kick-choice paths plus direct `Engine.release(kind='kick')` and `Engine.strike`; assert no legal kick reaches physics. Include `RV03_NOKICK=0` as a positive control.
5. **Rules matrix:** test `RULES_V03 × RV03_SCRIM × RV03_NOKICK × RV03_FLAT × RV03_MARK`, including callers that do and do not use `RV03.settings()`.
6. **Decision-ownership sentinel:** instrument each layer to return a unique target/action marker and assert final precedence through policy, C4c2, routing, individual decision cadence, and C3.
7. **True-state leak tests:** mutate hidden true positions while keeping beliefs fixed and require invariant choices for target generation, pass ranking, C4c2 values, off-ball actions, maneuver selection, and receiver routing where cognition is meant to be belief-owned.
8. **Formation-free anchor tripwires:** in the future mode, make calls to legacy slot rows, `rule_lane`, escort/man/zone tables, C4c2 spot menus, and any prohibited restart formation fail immediately. Decide the dead-ball exception first.
9. **Intent-to-physics trace contract:** assign a decision ID at choice time and carry it through pending action, motor preparation, release/contact, and committed outcome.
10. **Perception timing test:** explicitly verify whether cognition uses beliefs from the start or end of the current 100 ms interval.
11. **Multi-match and parallel isolation:** run multiple games per process and concurrently; assert no contamination from `S`, perception minds, bounce state, genes, or caches.
12. **Install idempotence:** either reject a second install or prove identical behavior and chain cardinality.
13. **V03 discipline/foul table:** direct tests for first through fifth minor, major/danger/serious classification, offensive and defensive count transitions, points, possession, and scrimmage placement.
14. **Property/invariant tests:** every executed action must be legal under the active rule profile; every physical outcome must originate from one recorded intent or a clearly classified emergent contact event.

## 11. Reproducible evidence index

| Artifact | Purpose |
|---|---|
| `HP-001_T2_EVIDENCE_REPORT.md` | Audit conclusions and approval stop. |
| `t2_audit/REPRODUCE.md` | Exact reproduction commands and configurations. |
| `t2_audit/patch_map.py` | Read-only capture of the unmodified replacement list. |
| `t2_audit/patch_map_b0.json` | Exact B0 replacement map and match counts. |
| `t2_audit/patch_map_maximal.json` | Exact 28-entry maximal map and match counts. |
| `t2_audit/runtime_pristine.json` | Pristine embedded-core identity inventory. |
| `t2_audit/runtime_b0.json` | Installed B0 inventory and environment reads. |
| `t2_audit/runtime_full_prism.json` | Installed full cognition inventory and environment reads. |
| `t2_audit/runtime_diff_b0.json` | Machine-readable B0 original/effective comparison. |
| `t2_audit/runtime_diff_full_prism.json` | Machine-readable full-cognition comparison. |
| `t2_audit/runtime_diff.py` | Offline inventory comparator. |
| `t2_audit/build_inventory.py` | Human-readable inventory renderer. |
| `t2_audit/RUNTIME_OVERRIDE_INVENTORY.md` | Complete original/effective/wrapper-chain table. |
| `t2_audit/runtime_override_inventory.csv` | Same inventory in tabular machine-readable form. |
| `t2_audit/decision_tick_trace.py` | Deterministic read-only decision/outcome profiler. |
| `t2_audit/decision_tick_trace.json` | Full 4,000+ call/return trace and physical release evidence. |
| `t2_audit/DECISION_OWNERSHIP_CALL_GRAPH.md` | Compact ownership/call-graph artifact. |
| `t2_audit/ENVIRONMENT.txt` | Independent runtime and accepted comparison-environment details. |
| `t2_audit/CLAUDE_COORDINATION.md` | Accessible branch inventory and independent/Claude claim separation. |
| `t2_audit/MANIFEST.sha256` | Packet hashes. |

## 12. T2 stop

T2 is complete. No T3 work has begun. Approval is required before any T3 implementation, rule repair, cognition migration, formation-free mode, recalibration, or native rewrite.
