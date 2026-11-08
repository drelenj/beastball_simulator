# HP-002 Reconciliation

## 1. Source and provenance labels

Reconciliation input is Claude's `HP-002_reconciliation_spec_DRAFT_r3.md`, dated
2026-11-07, branch `claude/hp002-audit`. This document distinguishes:

- **Independent HP-001 evidence:** verified in the accepted T2–T5 artifacts and
  source snapshot by Codex.
- **Claude finding:** supplied by HP-002 r3 but not independently rerun during
  T6.
- **Joint design agreement:** compatible architectural conclusion, not a claim
  that both auditors reproduced the same measurement.

## 2. Agreements

| Topic | Reconciled position | Provenance |
|---|---|---|
| IA-001 | cognition receives observations, beliefs, knowledge and communication; PHY retains truth | joint design agreement; HP-001 independently found true-state leaks |
| Layering | generation, evaluation, selection, MC, and PHY are distinct ownership stages | joint design agreement; HP-001 found current ownership distributed |
| Qualified determinism | PHY deterministic given state, commands, environment and named modeled draws | joint design agreement; T3 independently supports repeatability |
| MC scope | MC uses the executing athlete's own state/capability and chooses no target | joint design agreement |
| Formation-free | legacy positional assignment is not a future emergent formation | joint design agreement; T2 independently maps anchors |
| C-7 | full PRISM Archer cognition is mandatory for B1 | approved HP-002 decision accepted as T6 input |
| B0/B1 separation | preservation and future cognition are different gates | joint design agreement |
| No rating progression | out of scope | joint design agreement |
| Preservation is not canon validation | accepted traces preserve behavior, not magnitude correctness | joint design agreement; explicit T3 acceptance condition |
| Provenance tags | athlete, rule, team planner, legacy table | adopted from HP-002 DO-3 and extended for MC/PHY telemetry |
| Dependency order | preserve first; document MC; then information boundary and domain migrations | joint design agreement |

## 3. Disagreements and required changes

### R-01 — Catch ownership

HP-002 r3's ownership table places catch generation/evaluation/selection as
automatic. T6's explicit requirement calls for cognitive preparation, motor
execution, and physical grasp/contact resolution. The reconciled proposal is:

- preserve automatic catching in the historical B0 adapter;
- define `CatchPrepareIntent` for B1;
- MC owns readiness, hand placement, reach, and takeoff execution;
- PHY owns swept contact, arrest, security, contention, and possession.

This is a real architecture change to HP-002's table and requires approval. It
does not authorize implementation.

### R-02 — Focus semantics

HP-001 source/audit evidence supports Focus as perception/attention/belief
behavior in the present stack. T6 does not assign it a motor-error role. If
HP-002's future MC design intends Focus to affect aim, release, catching, or
locomotion, that is a new rating mapping requiring canon approval and validation.

### R-03 — MC “physical constraints”

T6 narrows the phrase: MC may access own true body/capability and a restricted,
command-local constraint projection. It may not query live true ball or opponent
state under the label of constraint. Target geometry is captured from the
selected belief/intention.

### R-04 — Command acceptance and legality

MC acceptance is schedulability, not true legality. Apparent legality belongs to
cognition/view; true legality belongs to rules/PHY. This avoids leaking hidden
state and permits an attempted action to fail or consume resources according to
the approved rule.

### R-05 — AthleteView status

T6 defines a typed `AthleteView` because the authorized specification requires an
enforceable boundary. HP-002 O8 still governs implementation approval. The paper
type does not itself authorize building or installing the view.

## 4. Claude claims not independently replicated in T6

The following remain labeled Claude findings even where the interface responds
to them:

- quantitative percentages or cadence measurements in HP-002 r3;
- exact Archer shadow/drive-mode residual true-state accesses;
- measured receiver reroute timing/cadence details beyond the HP-001 T2 source
  ownership finding;
- HP-002-specific policy value distributions.

They are legitimate design inputs from the parallel audit but not rebranded as
independently verified conclusions.

## 5. Open HP-002 decisions retained

| ID | Decision remains open | T6 handling |
|---|---|---|
| O1 | What opponent morphology is legitimately visible? | `ObservedEntity` is configurable and uncertainty-bearing |
| O2 | How does a receiver learn the target? | requires observation/communication/belief provenance |
| O3 | Belief update timing within a decision interval | capture/delivery/effective times explicit; policy unselected |
| O4 | In-flight tracking cadence | cadence is versioned config; no default chosen |
| O5 | Gate C acceptance tolerances/envelopes | matrix requires later approval |
| O6 | Archer target policy, structure targets, constants, public eligibility | required versioned inputs; unapproved values fail validation |
| O7 | Authorize T3A and cross-replication | remains blocked |
| O8 | Approve AthleteView implementation | paper contract only |
| O9 | Rules audit/dead-ball exception | rule-required placements isolated from formations |
| O10 | Carrier archetype biases | option-policy parameter, not interface default |

## 6. Additional decisions exposed by T6

| ID | Approval needed |
|---|---|
| T6-O1 | Approve B1 prepared-catching ownership and revise HP-002 table |
| T6-O2 | Confirm Focus has no MC effect, or authorize a new rating mapping study |
| T6-O3 | Define Keeper intent modes and arbitration policy without selecting tactical behavior prematurely |
| T6-O4 | Approve interruption/supersession priority rules for simultaneous commands |
| T6-O5 | Approve causal ID encoding and future telemetry schema version |
| T6-O6 | Ratify platform/numeric policy and physical-parity tolerances after cross-platform evidence |

## 7. Reconciled status

The specifications are compatible once R-01 through R-05 are acknowledged.
Only R-01 changes a substantive HP-002 ownership assignment. All other items
clarify interfaces or preserve an approval boundary. No unresolved item is
silently assigned a default in this packet.
