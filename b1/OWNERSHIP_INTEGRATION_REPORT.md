OWNER BRIEFING
1. Accomplished: merged the ownership enablers into Sprint-45 c64d92e and wired all four replacement hooks. IMPLEMENTED and TESTED; not ACCEPTED.
2. B1 now runs a full match with belief-derived Keeper intents, Archer movement, restart claims/positioning and athlete release withholding. Missing or stale 3-D beliefs never fall back to truth.
3. Unproven: policy quality, altitude/velocity estimation quality, emergence, full canon conformance. Home formation remains. The inherited R-15 layer still records some protected-Keeper contacts without enforcing them.
4. Blocking: no implementation blocker. Repository-wide green is unavailable: historical collection requires browser dependencies and a missing fixture; unrelated historical failures are tracked separately. Complete B1 suite passes.
5. Recommended action: independent review and later Emergence-1 integration. Proceed to null-default M2 plumbing on a child branch; no communication benefit claim.

Engineering evidence
- Branch: codex/b1-ownership-integrated, based on c64d92e, merge parent b7670b7.
- Complete B1 suite: 111 passed, 23 subtests passed (414.03 seconds).
- Full repository pytest attempted: five collection errors (CLI scripts block_test.py/rs_test.py, missing Playwright in lab, missing results_v37/capability_table_v37.json). Remaining-suite run separately, with historical failures; no B0 edits.
- Frozen B0 inventory: all 427 paths verified. core.py/runtime.py/g1.py identical to accepted 4b19719. No frozen B0 path modified.
- Full seed-1 match repeated; seed1-b.json and seed1-c.json use final implementation (seed1-a predates release telemetry). Same trace and state hashes; final B 8, A 6, two 120-second periods.
- Tests adapted to canonical inventory after merge. Policy-frequency assertions replaced by nonvacuous execution checks, a forced G1 release, and four controlled possessions per 250/500/1000 ms threshold. No game policy tuning.
- Governed G1 matrix: six conditions x 100 seeds, replay deterministic. Existing attribution/mechanism behavioural gates remain false; not reclassified as accepted.
- Full-loop G1 baseline: 16 scenarios (g1/g1_close, seeds 1-8) for M2 comparison.
- 3-D sensor: PRISM detection/occlusion/latency gate, queued noisy x/y, separate noisy altitude stream, finite-difference velocities. Provisional engineering model; no authoritative velocity fallback. Views and beliefs carry immutable BallCourseBelief; overlay callbacks return only already-delivered beliefs.
- Class traps prohibit original c4c_keepers, update_archers, targets_dead and c3_withhold; instance overlay replaces them. Existing standalone cognition fixtures retain legacy experiment Keeper options, but full-match views select keeper_control and the overlay owns that decision.

Still engine-owned
Physics, collisions, body feasibility, contact/catch adjudication, fatigue, rule clocks, substitutions, restart records/readiness/release timing and restart release geometry/fallback, penalty machinery. Rule signals are authoritative; tactics in the four replaced hooks are athlete intents. Restart claim admission uses canonical simultaneous-intent ordering. Other provisional policies (including home) remain, with no optimality claim.

Evidence hashes and decisions
{
  "trace_hash": "d2fe8000251ec3a5be254937ddc790097d3b1830acb2f27e7d2b3fe6533fa687",
  "state_hash": "79383432f0c77402fb0d0dc732624edae94d3545e68f15b53ce506cc32ae5955",
  "decisions_total": 84500,
  "decisions_by_kind": {
    "abort_draw": 23,
    "archer_hold": 6630,
    "carry": 194,
    "continue_current": 4322,
    "draw_release": 98,
    "home": 51352,
    "keeper_control": 5361,
    "mark": 1559,
    "pass": 87,
    "press": 688,
    "pursue": 2959,
    "receive": 452,
    "restart_pass": 131,
    "restart_wait": 157,
    "retain": 10,
    "scan": 219,
    "search": 8148,
    "shoot": 9,
    "support": 2101
  },
  "ownership_decisions_by_kind": {
    "archer_movement": 16654,
    "keeper": 5029,
    "release_preparation": 398,
    "restart_claim": 4756,
    "restart_position": 121084
  }
}
