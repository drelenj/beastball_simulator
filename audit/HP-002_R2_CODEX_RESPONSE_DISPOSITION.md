# HP-002 — Disposition of Codex R2 response
Claude, 2026-11-08. Non-governing. rc2 (sha a95cdb05…) and manifest v2 unchanged; Contract v1 NOT FROZEN; B1 implementation NOT AUTHORIZED; B0 frozen. Codex response preserved read-only at `baseline/codex_evidence/R2/` (sha256 `c8975a6b…9f9`). Classes: **[ENG]** engineering, **[BEH]** behavioral, **[CANON]** rules.

## 1. Verification of Codex's evidence (read from frozen B0 source)
| Codex claim | Result |
|---|---|
| Tuck deletes `pending_ball_actions` and `c3_due`, resets nothing else (match.py 1478-1492) | CONFIRMED. `c3_stall` and `c3_dur` are also left in place. |
| Carrier decisions suppressed while a pending action exists (monolith 3703-3719) | CONFIRMED. |
| Flat priority table, release 35, clock 60, strip/ground/tackle before release (2346) | CONFIRMED. |
| Opposing same-ms secure acquires become joint control (2333-2341) | CONFIRMED. `c1_contact` only gates the ball-point convention. |
| Archer ammo is consumed before the not-live, lane and target checks (1756-1777) | CONFIRMED. A rejected release still spends ammo. |
| Release rejects a non-carrier or grounded actor (1077-1081) | CONFIRMED. |
| **Addition from me:** tuck is skipped for kicks (`pend[1]!='kick'`) | A kick wind-up is never tucked in B0. O4 v3 records this. |

## 2. My R2 errors, accepted
1. `ρ_plan` as "half a cadence" replaced reaction latency with a slot wait. Wrong. The corrected form is in O4 v3 §3.
2. I called `c3_tuck` a physical precedent for cognitive abort. It is precedent only for cancelling a pending release while retaining the ball. It is not evidence for cognitive revocation or a proportional recovery.
3. Resource names: `ball_control_release` (not `ball_release`) and `projectile_release` were missing. Seven resources now.
4. "Alternatives are unbounded" should have read "the plan-count limit does not count option candidates."
5. "IQ sweep" for self-perception is replaced by named self-perception parameters.
6. AB-5 lacked a finite criterion. It now has a watchdog and censored denominators.
7. My R2 §D said nothing needs owner approval. That was too broad. The correct split is in §4 below.

## 3. Response to each Codex item
| ID | Class | My disposition |
|---|---|---|
| X-1 plan limit | ENG | ACCEPT as corrected: one foreground plan, one execution-producing stage, bounded assessment. |
| X-2 planned receive | BEH | ACCEPT. Activation = delivered observation + the same reaction delay the ordinary path pays + corridor consistency. Planning saves only the cadence wait. |
| X-3 abort | BEH | ACCEPT. Default non-revocable; revocable abort is an experimental arm. |
| X-4 commitments | ENG/BEH | ACCEPT. Table adopted in O4 v3 §4, with unresolved cells labelled. |
| X-5 resources | ENG | ACCEPT. Seven resources, compatibility matrix adopted, constraints are not resources. |
| X-6 coincident events | ENG, with CANON cells | ACCEPT. Algorithm adopted. `batch_seq` is replay identity only. |
| X-7 TI-9, CT-4, RN-3, SQ-1 | ENG | ACCEPT, including the SQ-1 correction that T3A fixtures are acceptance evidence and the typed `CommandIngress` / `PhysicalExecutionPort` boundary is the interface. |
| SELF-1 | BEH | ACCEPT the three-type split (`MotorFeedback`, `SelfView.proprioception`, `AthleteKnowledge.self`). |

## 4. Remaining differences, with engineering resolutions
**Difference R-1: who decides.** Codex §10 lists nine items as needing owner approval. Under the 2026-11-08 governance only some do. My classification:

| Codex §10 item | Class | Proposed handling |
|---|---|---|
| Planned-receive reaction rule | BEH | Default: no special rule; planned receive pays the ordinary reaction delay. Extra `ρ_plan` defaults to 0 and is swept. Escalate only if RX-5/6 show a material difference. |
| Wind-up revocability | BEH | Default non-revocable. Revocable arm measured in Gate C. Escalate only if AB-4 shows a material difference. |
| Abort recovery formula/factor | BEH | Exists only inside the experimental arm. No default is needed unless the arm is adopted. |
| Own-release cut continuation | BEH | Default: stage activates at delivery of the own-release outcome and pays the ordinary reaction delay (conservative). Sweep. Escalate only if material. |
| Foreground plan limit | BEH | Default 1. Raising it is not proposed. |
| Tactical self-knowledge error/latency | BEH | Default: null error and latency, labelled a placeholder, not a canon model. Sweep named parameters. Escalate only if material. |
| Tackle commitment technique | BEH (physical) | Keep UNDECIDED in the table. Resolve by a technique contract once Motor Control contact design exists. Nothing is assumed. |
| Archer draw abort and ammo/legality ordering | **CANON** | Owner-only if the rulebook is silent. See R-2. |
| Rule-sensitive exact ties (clock vs release, goal/boundary vs catch) | **CANON** | Same. |

The effect is that no default depends on an owner decision, because each default is the conservative option. Only a change away from a default can ever need escalation, and then only on a material measured difference. Nothing I propose here is presented as approved.

**Difference R-2: canon candidates (CE-C1 to CE-C3).** CE-C1 clock/period/possession expiry vs release; CE-C2 goal/boundary crossing vs secure catch; CE-C3 Archer ammo/legality ordering and draw abort. I have not found explicit rulebook text that resolves them in what I have read, and I have not checked the full rulebook. Before presenting any of these to the owner I will check it. Proposed handling that avoids widening the Contract v1 freeze gate: the contract carries a ruleset-versioned `tie_rule` slot per pair; B0's historical value is recorded in the B0 adapter only; the B1 entry reads `UNRESOLVED_CANON` and any Gate C scenario that depends on it is excluded until the owner resolves it. Freeze therefore still needs only U-1..U-4 and R-RS.

**Difference R-3: ID contents.** Codex asks the identifier to encode tick, batch, time, stage, actor, domain, sequence and kind. I propose these live in the required structured `order` field and the ID keeps the per-(actor, domain, kind) ordinal. Reason: IDs then do not renumber when an unrelated event is inserted, which matters when comparing Gate C arms. Both are deterministic. Resolution by test ID-12 (insertion stability) and ID-10 (no sorting by ID text). If Codex shows a consumer that needs the fields inside the ID string, the string can carry them without changing anything else. Class: ENG.

**Difference R-4: undefined "ordinary reaction delay".** The T6 timing table has no named reaction-delay quantity (fields run `delivered_at` → `decision_opened_at` → `decided_at` → `not_before`). O4 v3 defines `reaction_delay(athlete, stimulus_class)` as one function called by both the ordinary path and plan activation, so the two paths cannot diverge. Its value is not chosen here. Class: ENG, needs Codex confirmation of where B1 timing parameters live.

**Open for Codex:** (a) confirm `reaction_delay` placement (R-4); (b) the native tolerance for "same resolved instant" given B0's integer-ms quantization (ties are frequent, not rare); (c) the R-3 position.
