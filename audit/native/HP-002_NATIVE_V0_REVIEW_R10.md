# HP-002: independent review R10 of Native v0 (codex/native-v0 @ a1b1313)
Claude, 2026-11-14. Reviewer: Claude (independent). Subject: Codex delivery a1b131379845322bbc9970ad667a6d68dec10dd7. Status words: nothing here is ACCEPTED; acceptance is DreLen's.

## OWNER BRIEFING
1. **Accomplished.** I reproduced Codex's evidence myself: tests, seed-1 hashes, config digest, the null-versus-absent replay, and a read of the cognition, port, rules and config code.
2. **What Native v0 can do now.** It plays a full legal 4 x 600 s match, deterministically, under the ruleset as built. It is a working functional baseline.
3. **Unproven or wrong.** Three real findings: the Archer is nearly inert (arrow speed is far below canon), tackles almost never happen in full matches, and a quarter of restarts end in a timeout because the placeholder restart behaviour is weak.
4. **Blocking.** Nothing blocks accepting the baseline as a functional baseline. F-1 to F-3 should be fixed in a new config version before any experiment is run on it.
5. **Recommended action.** Accept a1b1313 as NATIVE-PRISM-0 (functional only), then have Codex produce `native-v0/3` with the F-1 to F-3 fixes before the Emergence-1 rerun or the hive-mind lab.

## 1. What I verified myself
| Check | Result |
| --- | --- |
| Tests: `pytest b1 native` | 197 passed, 23 subtests passed (matches Codex) |
| Seed 1 trace hash, state hash, config digest | All three equal Codex's reported values, on Python 3.13.18 / numpy 2.5.3 (Codex used 3.12.14 / 2.5.4), so the result is portable across those stacks |
| Seed 1 with M2 plumbing absent | Trace, state, config digest and score identical to the null-mode run |
| Accepted files `b1/core.py`, `runtime.py`, `g1.py` | Byte-identical to 4b19719 |
| Environment switches | None read in `native/`; `legacy_layers=()` enforced in config; a test covers env flags |
| Kicking | Guarded at three places; no `kick` decision kind in the seed-1 run |
| Config vs canon | Periods, overtime 300 s, 30 s clock, goal 3 m, zone 20 m, platform 5 m / 5 m, marking 5 m, 25 arrows, 5 freezes, 5 s / 10 s, 500 ms: all match |
| Test edits | One line in `test_sprint.py` (allows the authorized M2 `communication` import); `preservation.py` now enumerates the canonical 427-path inventory (new Native files excluded by design) |
| Defender residence concern | I suspected cognition forced every field player out of the Keeper Zone after 3 s. Not so: the timer runs only for attackers and unmarked defenders |

Not verified by me: the other 24 soak seeds (I reran seed 1 only, to save usage). I relied on Codex's soak files for those.

## 2. Findings
| ID | Finding | Evidence | Class |
| --- | --- | --- | --- |
| F-1 | **Archer is nearly inert.** Arrows are capped at 30 (hard-coded foul `arrow_speed` above 30; release speed 29) against a fastest player of 27, so they are about as fast as a runner. Canon: no arrow speed cap, arrow speed 250 m/s (about 5.6 times the fastest player). Seed 1: 435 arrows released, 385 misses, 14 freezes. | `native/config.py` (`arrow_speed=29`, `arrow_limit=30`), `native/rules.py` shoot_arrow | CANON mismatch, config change. Origin: the B0 default, and **my prompt omitted arrow speed**, so Codex had no spec |
| F-2 | **Tackles barely occur in full matches.** Seed 1: 993 collisions but 6 groundings and 5 tackle-count events in 2400 s; no major fouls, no offside, no natural overtime. Likely cause (not verified): automatic containment and descent were disabled (Q-CONTACT-1) and no athlete-owned tackle-to-ground decision replaced them. The tackle, scrimmage, offside and second-tackle rules are therefore proven by forced tests, not by play. | seed-1 `engine_events`, Q-CONTACT-1 | ENGINEERING / BEHAVIORAL |
| F-3 | **Placeholder restarts time out too often.** Seed 1: 147 of 575 restarts (25.6%) ended in a timeout: 129 toss timeouts, 18 snap timeouts. Boundary events number 293, so tosses are about half the restarts and roughly 44% of them time out; snaps about 60% (24 goals + 5 tackles, 18 timeouts). `rejected_geometry` 108, `rejected_by_engine` 65 suggest the nearest-teammate throw is often rejected. Each timeout hands over or penalises, so turnovers are 552 per match. | seed-1 `restart_statuses`, `outcomes_by_status` | BEHAVIORAL (placeholder cognition, mine to replace) |
| F-4 | Release speed and height are constants for every pass (speed min(27, max), height 1.6). Disclosed as PH6; the report's wording "owns release parameters" overstates it. | `native/cognition.py` | Wording |
| F-5 | The "restart closure 100%" figure is true but means every restart reached a recorded outcome, including timeouts. Actual release is 72.9% in seed 1 (71.8% across the 25). | report and seed 1 | Wording |

## 3. Judgement
Native v0 meets its stated bar: it functions, it is debugged, it is deterministic, it honours the ownership and information rules, and every rule is implemented or labelled. It does not yet play a game on which tactical conclusions can be drawn, because of F-1 to F-3. Seed 1 ended 58 to 77; I make no claim about whether that is good.

## 4. Recommendation (DreLen decides)
1. Accept a1b1313 as NATIVE-PRISM-0 for functional purposes.
2. Before the Emergence-1 rerun or the hive-mind lab, Codex ships `native-v0/3`: (a) arrow speed per canon with no cap (DreLen to confirm 250 m/s and its ratio to top speed), (b) a restart-closure metric that separates release from timeout, plus the placeholder fix for toss and snap (Claude supplies the cognition, Codex the rejection causes), (c) an athlete-owned tackle-to-ground path so grounded tackles occur in play. Each change gets a new config version and a new manifest; Native PRISM 0 hashes stay reproducible.
3. F-2 to F-3 widen the plan: the forced-scenario batch should include scrimmage-heavy and tackle-heavy cases until tackles occur naturally.
