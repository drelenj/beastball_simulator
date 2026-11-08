# Requirements Traceability

| T6 requirement | Primary evidence | Status / boundary |
|---:|---|---|
| 1. Typed core contracts | `TYPED_CONTRACTS.md` §§1–9 | Complete paper contracts for all seven named types plus config/RNG support |
| 2. Decision ownership | main spec §§2, 5; HP-002 reconciliation §§2–3 | Five-stage cognition/MC/PHY ownership specified |
| 3. IA-001 information boundary | main spec §3; typed view/belief contracts; tests C-01–C-03 | True-state handle prohibited; authoritative PHY state retained |
| 4. Intent, command, timing, outcome | main spec §4; typed contracts §§5–8; decision-tick example | Separate IDs/times; no silent replacement; delays preserved |
| 5. Full Archer cognition C-7 | main spec §7; validation C-10–C-13 | Complete interface; undecided rule/policy values remain approval-gated |
| 6. Catch, Keeper, jump | main spec §6; contracts; validation C-07–C-09 | Prepared B1 catch proposed; automatic B0 catch preserved |
| 7. Existing mechanism mapping | `LEGACY_MECHANISM_MAP.md` | Throw, catch, hand, pose, locomotion, fatigue, ball, Arrow, Keeper, rules mapped |
| 8. Config/RNG/repro/telemetry | main spec §§8–9; contracts §§9–10 | T5-compatible, deterministic IDs, explicit unavailable semantics |
| 9. Validation requirements | `VALIDATION_MATRIX.md` | Gates A/B/C, T3 tolerances and gaps, T3A approval boundary |
| 10. Performance/portability | main spec §10; validation P-01–P-03 | External supervisor replaces future SIGALRM dependency; pathology retained |
| 11. HP-002 reconciliation | `HP002_RECONCILIATION.md` | Agreements, five clarifications/conflicts, open decisions, provenance labels |
| 12. Packet, diagrams, matrix, risk, sequence | README, diagrams in main/example/sequence, matrix, risk register, sequence | Complete design packet; no implementation |

## Constraint compliance

| Constraint | Evidence |
|---|---|
| Paper/design only | Documentation files are the only T6 deliverables |
| No physics/rating/cognition/rule/default changes | Scope boundaries in README, main §12, provenance §5 |
| No B1 behavioral implementation | All future phases are explicitly unauthorized |
| No artificial velocity clamps | Main §10.3 and risk MR-08 |
| Preserve B0 and T1–T5 | Gate A and exact provenance hashes |
| Stop before native implementation | Implementation sequence ends T6 at its review gate |
