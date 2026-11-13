# EMERGENCE-1 NEXT STEPS: fastest credible path to richer emergence

Experimental. **Nothing is ACCEPTED.** M1 is accepted per its record; M2 is not started. All durations,
counts and sizes below are **ESTIMATES**. Nothing here is a rule decision; rules live only in the decision record.

## 1. Compute is the first limit

- This sprint had 4 cores and about 16 minutes of search: on the order of a couple of hundred short proxy matches (ESTIMATE; exact counts are in `EMERGENCE1_RESULTS.md`).
- That is far too few to separate parameter vectors whose true difference is small. Approximate calculation for a paired sign test, two-sided alpha 0.05, power 0.80, true split 60/40 among decided pairs:
  n = ((1.96 x 0.5 + 0.84 x sqrt(0.6 x 0.4)) / 0.1)^2 = ((0.980 + 0.412) / 0.1)^2 = about 194 decided pairs.
  With draws excluded, plan for roughly 190-200 decided pairs, so more seeds than that (ESTIMATE). A 55/45 split needs about 4 times as many (about 780, ESTIMATE).
- One comparison of two vectors therefore costs about as much as this sprint's whole search. A search that compares dozens of vectors honestly needs 10^4 to 10^5 proxy matches (ESTIMATE): 32-64 cores for a few hours, or the same machine overnight.
- Cheap wins first: profile the match loop (24 sensors ticking every 100 ms dominate), skip telemetry in search runs, and reuse the engine import across matches in a worker (ESTIMATE: 1.5-3x).
- Sequential testing (stop a pairing early once the sign test is decided either way) cuts the cost of clearly different vectors.

## 2. Make more choices searchable (largest gain in what can emerge)

1. **Merge Codex's `b1/emergence-ownership-enablers`.** Keeper save, Archer movement, restart taker and release-withholding become athlete intents, then get their own parameters. Until then no Keeper, Archer-position or set-piece style can emerge (see `b1/emergence/ENGINE_CONSTRAINTS.md`). ESTIMATE: 1-2 sessions to merge and re-run the tests.
2. **Richer option generation.** Pass speed and loft as part of the intent (the release contract already fixes "admitted speed" at decision time, so this stays inside it); shot placement as a continuous aim; carry direction candidates. Today these are fixed values, so the search can only change who and when. ESTIMATE: 2-3 sessions.
3. **Replace the hand-set Base A option values with searched ones**, without changing accepted `b1/core.py` behaviour: a parallel parametrized valuation selected by configuration, with the default reproducing Base A. ESTIMATE: 1-2 sessions.
4. **Per-role parameters, then per-athlete.** Field / Keeper / Archer first; then slots or individuals, so specialisation (a deep player, a wide player) can appear. Vector size grows from about 14 to 40-150 numbers, which needs the compute in section 1. ESTIMATE: 1 session for per-role, 2-3 for per-athlete with a search that copes.
5. **Perception-facing choices:** gaze/scanning policy and what to attend to. ESTIMATE: 2 sessions.
6. **M2 plan layer and communication** (separate milestone work): without it, combinations can only arise from independent reactions.

## 3. Better search (after the compute exists)

- **Population self-play with a league / hall of fame.** Evaluate each candidate against past champions, not only the current population, so cyclic strategies (A beats B beats C beats A) are detected instead of mistaken for progress. Report the full pay-off matrix.
- **Quality-diversity (MAP-Elites).** Define behaviour descriptors from the read-out metrics (team width and depth, pass rate, press distance, possession share, shot distance) and keep the best vector per cell. The goal is a map of distinct playstyles and how they fare against each other, not one optimum.
- **A standard optimiser (CMA-ES or similar) inside each niche** once fitness noise is under control; fitness = paired goal difference or win rate over a fixed seed block, re-sampled each generation to avoid overfitting to seeds.
- **Rating interaction:** run the same search on rosters with different rating profiles to see whether the best style depends on the athletes (it should, if ratings matter).

## 4. Exploit review loop

- Every EXPLOIT-CANDIDATE (stalling, boundary or zone-clock farming, restart abuse, Archer or Keeper loopholes, rating-independent scoring) is logged with seed, trace pointer and rule/engine row, never patched or excluded silently.
- The owner decides for each: legitimate tactic, rule change (decision record), or engine defect. The search is then re-run; a style that only exists through a defect is not a finding.
- Add automatic detectors as they are named (time in own zone, restarts per minute, shots from fixed spots).

## 5. Validation protocol (apply to every claimed result)

1. Held-out seeds never used in the search; report if the evolved vector does not beat baseline there.
2. Paired seeds with sides swapped; state seed count, gains, losses, draws and the exact sign-test p-value.
3. Confirm on full-length matches (2 x 120 s now, 4 x 600 s later) that the proxy ranking holds.
4. Show the mechanism in traces (which option, where athletes stood, what changed), not only the score.
5. Symmetry control: identical params on both sides should give about 50%; report the number.
6. Determinism: same seed and params give the same hash, serial or parallel.
7. Independent reviewer re-runs boundary and ownership checks after each change to cognition or positioning.

## 6. Suggested order (ESTIMATES)

| Step | Work | Size |
|---|---|---|
| 1 | Speed-up and a long-running search on more cores with the current parameters; honest pay-off matrix | 1-2 sessions + overnight compute |
| 2 | Merge ownership enablers; add their parameters | 1-2 sessions |
| 3 | Pass speed/loft, shot aim, searched option values | 3-5 sessions |
| 4 | League + MAP-Elites, per-role parameters | 3-4 sessions |
| 5 | Per-athlete parameters, perception choices, M2 plans | open-ended |

Blocking items: compute budget (owner), the ownership-enablers merge (Codex), and owner review of the exploit log.
