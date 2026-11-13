# SPRINT45 UNLIMITED STRATEGY — fastest credible path to a validated PRISM after Round 2

Status: planning document. **Nothing is ACCEPTED.** M1 is not accepted (open item H3). All durations are **ESTIMATES** in working sessions.
Basis: `SPRINT30_UNLIMITED_STRATEGY.md`, the milestone plan, `audit/HP-002_OWNER_DECISIONS_D1_RECORD.md`, reviews R4, R5, R6 and the draft `pass-release-v1` contract (branch `claude/hp002-audit`). Specs were read selectively, not re-audited.

## 1. What changed since Round 1

- **Canon gates are settled** by the owner decision record: U-1 (Keeper protection KP-01..14 + KP-OG), U-2 (zone clock), U-3 (zone geometry G-1..G-6, R = 20), U-4 (U4-01..13), R-RS (ruleset 1.0.2 for B1 only; B0 stays 1.0.1), SELF-1 (exact), P-1 = 500 ms (tested at 250/500/1000), P-2..P-4, C-1..C-3. No owner decision blocks the next step.
- **The rules-state table R-01..R-22 is DESIGN COMPLETE only** (derived by the reviewer, never run before this sprint). The sprint's `b1/possession.py` is a first primitive implementation, not a validated one.
- **Governed M1 moved** to `4b19719` (G1 v2 after R6). H1 closed, H2 closed with one residual, H4 conditionally closed, **H3 open**.
- The `pass-release-v1` contract is a DESIGN COMPLETE draft engineering contract; its 60 degree bound is a provisional default "to be tested".

## 2. Milestone path

| M | Remaining work | Exit evidence | ESTIMATE |
|---|---|---|---|
| M1 | Close H3 (BA-M1-3): mechanism-level evidence that a sharper defender plays differently (lane-option selection rate, distance to lane at release, interception rate conditional on the option), then a paired outcome test. Relabel by-elimination causes as `unknown`. MR-1..MR-5 on at least 20 seeds; confirm or change the 60 degree bound from traces | Reviewer reproduces matrix hashes; sign test with seed count stated; owner decision on acceptance | 2–4 |
| M2 | Plan layer, `PlanStageActivation`, `ReactionGate`, communication channel, receiver cognition, give-and-go. Not started | Combination completes and fails for traced reasons; no activation before delivery | 5–8 |
| M3 | All roles under the boundary against the decided KP and G cells: Keeper belief of the flight feeding a Motor Control dive command; Archer belief model and target set under 1.0.2; closed physical execution port instead of run-time hook replacement | Per-role trace sets; one test per KP cell; zero true-state reads found by an independent reviewer | 8–12 |
| M4 | Validate the rules-state layer row by row (R-01..R-22), restarts and U4 scenarios, zone-clock violations enforced in the B1 path, rule-event ledger | One test per row that can fail; P-1 sensitivity at 250/500/1000 ms; reproducible full matches | 6–10 |
| M5 | Gates A/B/C, B0-versus-B1 distributions, performance budget, formation-free arm, acceptance bundle | Bundle with all hashes; owner decision | 5–10 |

Total: roughly 26–44 sessions (ESTIMATE). M1 and M2 can proceed in parallel. M3 and M4 no longer wait on canon.

## 3. Replacing each remaining primitive

| Primitive after Round 2 | Why it limits validity | Replacement | M |
|---|---|---|---|
| Rule-based option scoring | Hand-set constants; no plans or anticipation; outcome counts say little about intended play (R6: a step on a constant is not a rating effect) | Belief-driven option generation with continuous Judgment effects; athlete-owned plans; option trace | M2–M3 |
| Slot-grid home positions | Assigned from outside the athlete (BA-7) | Positions from each athlete's own space and marking evaluation; formation-free arm | M2–M3, shown in M5 |
| Ball as a sensor body | Ball noise, occlusion and flight read are the body tracker's, not a ball model | Ball channel in `ObservationFrame` with its own latency and flight estimate | M2 |
| Keeper save execution via the B0 C4c kernel | The dive plan reads the true flight; only the attempt is belief-owned | Keeper flight belief feeds a dive command; the kernel only executes | M3 |
| Engine-owned restart placement, substitutions, Archer platform movement | Athletes do not choose restart positions, taker or Archer position; rotation has no owner | Restart states in public match state; athlete-decided positions; a coach-level contract for substitutions; Archer locomotion intent | M3–M4 |
| Touch source for "touching the ball" derived from engine carrier / contested / touch events | B0 tracks carrying and catches, not simultaneous touches (decision record §4.2); contested (P-2, C-1..C-3) is therefore approximated | A ball-contact event source in the execution port with start and end of each touch per athlete | M4 |
| Zone-clock violations recorded but enforcement depends on B0 | R-11..R-13 are detected by the B1 layer; whether a restart follows is the B0 1.0.1 engine's rule, which may differ | B1 rules layer issues RST-1 through the execution port; conformance profile per row | M4 |
| Pass release aim | Any remaining use of receiver true kinematics breaks `pass-release-v1` item "may not lead the receiver" | Direction recomputation only, with the bound, in every pass path | M1–M3 |
| Run-time hook replacement on the B0 stepper | A missed hook is a silent leak (R4: traps cover five Match and three Policy methods; `c4c_keepers`, `targets_dead`, `make_pass`, `make_shot`, `auto_substitutions` still run) | Dedicated execution port with a closed method list | M3 |

Also still absent and to be built, not patched: the O4 action-resource model (seven resources, default-NO table, atomic bundles), O5 structured causal IDs, single-argument `decide` (BR-3).

## 4. Validation plan (obeys the sprint evidence rules)

1. **Every test can fail.** For each boundary or attribution test, record the failing counterpart: hidden state perturbed with the view fixed gives a byte-identical decision; a changed view changes the decision in the predicted direction.
2. **Effects need mechanism plus statistics.** A rating or policy change is reported as an effect only when the mechanism is seen in traces and the outcome difference passes a paired sign test, with seed count, gains, losses and p-value stated. "N paired endpoint differences" is never cited.
3. **Causes from recorded events.** Residuals are `unknown`; the unknown count is reported; a test shows `unknown` can occur.
4. **Rules-state rows.** One scenario test per R-row and per KP and G cell; P-1 at 250/500/1000 ms with escalation only for a material gameplay difference.
5. **Determinism and parity.** Same seed and configuration give identical hashes across processes; physics fixtures match frozen B0 (Gate B).
6. **Matrices.** 100+ seeds per scenario condition; full-match matrix sized from measured run time; attempted, completed and failed always reported.
7. **Independent review.** A reviewer who did not write the code reruns the tests, writes own probes and reports OWN-1..7 and BR-1..7 honestly. Only the owner accepts.

## 5. Risks

- **Touch-event fidelity.** If the engine cannot report simultaneous touches, contested states are under-counted and P-1 timing is biased. Check first in M4.
- **Rules mismatch.** B1 runs 1.0.2 while the frozen engine enforces 1.0.1; every difference must be an explicit B1 rule, not a patch to B0.
- **Engine coupling.** Hook replacement is fragile until the closed execution port exists.
- **Behaviour quality.** Whether athletes limited to their own knowledge produce the intended game remains the central unproven claim.
- **Primitive drift.** The limitations list is a gate: no milestone goes to the owner while one of its primitives remains.
- **Performance.** One sensor per athlete per tick; measure in M3.

## 6. Recommended order

1. Owner reviews the Round 2 evidence as an experiment only; no merge.
2. Close H3 through the normal review path.
3. Build the touch-event source and validate R-01..R-22 row by row (M4 groundwork can start now).
4. M2 plans and communication; then M3 role models; then M4 enforcement; then M5 gates.
