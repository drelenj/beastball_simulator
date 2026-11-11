# HP-002 — M0 Closure Record (Claude half) — STATUS: OPEN, NOT CLOSED
Claude, 2026-11-11. Authority: Owner directive "B1 M0 ACCEPTANCE AND M1 AUTHORIZATION" (2026-11-11 17:50). Non-governing until Codex's half is merged and the M0 manifest is verified.

## OWNER BRIEFING
1. **Accomplished.** I wrote my share of M0 and the M1 behavioral package: a draft conformance profile (v1-m1), the M1 test scenario as data, the M1 `AthleteView` field list, and the M1 behavioral acceptance and information-boundary review protocol. B0 (commit 2abe497), rc2, and manifest v2 are untouched.
2. **What B1 can do now.** Nothing new at runtime. No B1 code exists or has been reviewed. Everything in this record is DESIGN COMPLETE at most (draft). Nothing is IMPLEMENTED, TESTED or ACCEPTED.
3. **Unimplemented or unproven.** All of M1: the athlete decision cycle, Motor Control hand-off, physical outcome, causal traces, determinism, and every OWN/BR/BA test.
4. **Blocking.** Two things. (a) **I have not received the text of BLK-01 to BLK-05.** They are mandatory acceptance gates, and I will not guess them. I can't find them in the repo or in anything attached to this conversation. (b) **Codex's M0 inputs**: final ID field widths and enum spellings, the `EventTime` base unit and fixed-point source, repo layout and CI, and confirmation of the conformance profile. Without these I can't compute the Contract v1-core hashes or build a verifiable M0 manifest, so M0 can't honestly be closed, and the directive says M0 closes before M1 code merges.
5. **Recommended action.** Please paste the BLK-01..05 definitions (and the Codex sections of the joint plan, if they differ from what I authored) to me and send this record and the files below to Codex. Codex can start M1 code on a branch meanwhile, since merging is the gated step.

## 1. M0 closure checklist (my readiness plan §4)
| # | Item | Owner | Status |
|---|---|---|---|
| 1 | Contract v1-core freeze record (typed core, `Availability` for U-dependent fields) | joint | OPEN: needs Codex widths/enum spellings |
| 2 | Engineering defaults D1–D9 recorded as defaults, not canon | Claude | DESIGN COMPLETE: see readiness plan §3 (commit 5f362aa) |
| 3 | Conformance profile v1-m1 | joint | DRAFT: `audit/m0/CONFORMANCE_PROFILE_v1-m1.json`, awaiting Codex confirmation |
| 4 | M0 manifest (new; v2 stays historical) | Codex tool + Claude verify | OPEN: after items 1, 3 |
| 5 | Preservation safeguards (B0 frozen, evidence read-only, B1 separate code path, import block of legacy controllers) | joint | OPEN: BLK-01..05 may define these; unseen |
| 6 | M1 scenario as data | Claude | DRAFT: `audit/m1/M1_SCENARIO_v1.json` |
| 7 | M1 AthleteView subset | Claude | DRAFT: `audit/m1/M1_ATHLETE_VIEW_SUBSET.md` |
| 8 | M1 behavioral acceptance + boundary review | Claude | DESIGN COMPLETE: `audit/m1/M1_BEHAVIORAL_ACCEPTANCE_AND_BOUNDARY_REVIEW.md` |
| 9 | Repo layout, CI gates, estimates | Codex | OPEN |

## 2. Requests to Codex (CX list, restated for M0)
1. Final widths for `tick_seq`, `event_batch_seq`, `local_seq` (proposed 16/10-digit zero-padded decimals), and enum spellings for stages and kinds.
2. `EventTime` base unit and the fixed-point source for sub-steps.
3. Confirm or correct the conformance profile v1-m1 (policies, exclusions).
4. Repo layout: separate B1 package, import-block hooks, CI jobs (static scan BR-1/BR-2, poison tests, determinism).
5. Where telemetry levels (off/minimal/full) hook in for BA-M1-5.
6. Estimates and risks for M1.
7. Mapping of BLK-01..05 to concrete tests, once the owner relays them.

## 3. Assumptions I made (no owner decision needed; stated so they can be corrected)
- The M1 scenario has no Keeper or Archer, no kicking, no arrows, and uses B0 1.0.1 physics.
- Defaults D1–D9 hold as test candidates. Behavioral register shown once at freeze, per owner Option 1.
- U-1..U-4, R-RS and SELF-1 stay deferred to M3/M4.

## 4. What this record does not claim
It does not claim M0 is closed, that BLK gates are satisfied, or that any behavior is implemented.
