# HP-002: Neon's review of the RB-3.33 plan, checked against code (Claude, 25 Nov 2026)

Source checked: `codex/rb-3-32-paired-fixes` @ 33c932b. Verdicts: CONFIRMED (read in code or recomputed),
PARTLY (true mechanism, wrong size), WRONG, PLAUSIBLE (consistent with code, not traced end to end).

| # | Neon claim | Verdict | Evidence |
|---|---|---|---|
| 1 | Fresh Takedown dies if decision_ms drops: freshness window is tied to the decision clock | CONFIRMED, critical | `paired_policy.py:68-69` requires `delivered-captured <= core_decision_ms*(1+.4*(.7-reaction))`; `port.py:329` picks a frame with `captured <= now-latency_ms` (200), frames every `sense_ms` (200), so frame age is 200-400 ms. At 500 ms it always passes; at 150 ms it never passes; at 250 ms it mostly fails. |
| 2 | Catch cliff at ~58 m/s for an average catcher (680 J) | PARTLY | Neon used the core formula; Native overrides it (`rules.py:494`, cubic-plus in skill, exponent 3.6) with the 8th-power cutoff (`substrate.py:30`). Recomputed 50%-secure speed at miss 0.4: catching .45 41 m/s, .55 44, .60 49, .65 57, .70 68, .75 83, .80 100. Secure at 55 m/s: .60 → 13%, .65 → 63%, .70 → 97%. Average hands are fine; below-average hands collapse. |
| 3 | Throw error scales with speed | CONFIRMED | `port.py:604` `sd = base*release_speed/67`; lateral miss at a fixed distance is proportional to speed, so a 58 m/s pass misses about twice as wide as a 29 m/s pass. |
| 4 | Decision faster than sensing re-reads the same frame; CPU risk | CONFIRMED, plus more | `config.py:44-47`: dt_ms 100, sense 200, latency 200. Also: dt_ms 100 quantises any interval below 100 ms, so 150 ms is effectively 100 or 200. 30 games cost 5,143.5 CPU-s (~171 s/game). |
| 5 | carry_finish contaminates the baseline | CONFIRMED | Hardcoded 5 (`paired_policy.py:133` `5*probability`, `:141` band 5), 1.55 continuation cap (`:147`), shot formula (`:143`). Alone: median 90 → 105.5, team score SD 16.4 → 23.3. `rulebook/config.py:17` still has `carry_points = 5` (canon is 7). |
| 6 | Keeper 'set' vs 'save' menu noise | PARTLY | Neon omitted the time term: save = 1.15 + 0.6*min(window,.6) (`prism_core.py:32,364`). Uniform noise ±0.225 per option at .70. P(set beats save): ~2.5% at a 0.33 s window, ~14% at 0.10 s, ~22% at 0. Real, but not most of the 113 no_commit. |
| 7 | keeper_unset_s 0.10 s added when moving > 1.5 m/s | CONFIRMED | `port.py:647-648`, `match.py:30,364`; with ~0.176 s reaction that leaves ~0.06 s of a 0.34 s mean flight, below `keeper_launch_min_s` 0.10 (`match.py:437`). |
| 8 | c4c_due ignores native_keeper_flight | PLAUSIBLE | `match.py:382-393` schedules from `c4c_seen`/`c4c_plan` only; `port.py:690` sets `c4c_seen` on the Native path. Up to one 100 ms step of jitter. |
| 9 | Keeper already 1-4 m off the line on the bisector | CONFIRMED | `match.py:30` depth min 1 / max 4. Plan item "2-5 m" is mostly in place; the gap is behaviour timing, not depth. |
| 10 | Two lane-clearance models | CONFIRMED | `paired_policy.arrival_clearance` (with acceleration) and `cognition_rb3.lane_margin:297-311` (velocity only). |
| 11 | Stretch gate too tight | CONFIRMED | `paired_policy.py:95` needs contact < 0.28 s. |
| 12 | Traction gives wide turns | CONFIRMED (deferred) | `roster.py:58-63`: braking 11.8, turning 11.4 m/s² at .70. Physiology tuning: after the soak, not in RB-3.33. |

## Lead decisions (ENGINEERING / BEHAVIORAL)
- Clean baseline: carry_finish OFF; Fresh Takedown freshness made independent of the decision clock; one lane model.
- Cadence: sense_ms 100 (= dt_ms); latency_ms stays 200; decision base sweep 200 / 300 against 500. Nothing below dt_ms.
- Interrupts: targeted only (Keeper on shot release, committed tackler on target release, intended receiver plus defenders within 15 m of the pass line). Sideline handled in locomotion braking.
- Passing: release speed is capped by the intended receiver's believed safe speed (Touch is the throttle). Throw-error scaling is kept and reported.
- Ladder trials (cumulative), not each alone: cheaper and matches the coupling Neon identified.
- CPU guard before the soak.

Neon's forecast (all fixes, carry 7): possessions ~95-115, median team score ~72-88. Recorded as a reference.
