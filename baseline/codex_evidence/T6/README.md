# HP-001 T6 — Native Interface Design Evidence Packet

**Status:** Design complete; implementation not authorized  
**Baseline:** `B0-P4-DEFAULT` at `2abe497ca82588cb2d8c871a7aab61daaae95c12`  
**Prepared:** 2026-11-08 UTC  
**Scope:** Paper specification only

This packet defines the interface boundary between cognition, motor control, and
physical resolution without changing the accepted historical simulator or any
T1–T5 evidence.

## Contents

| File | Purpose |
|---|---|
| `HP-001_T6_NATIVE_INTERFACE_SPEC.md` | Normative architecture, ownership, timing, data flow, configuration, randomness, telemetry, performance, and portability |
| `TYPED_CONTRACTS.md` | Language-neutral typed contracts and invariants |
| `LEGACY_MECHANISM_MAP.md` | Existing B0/Pocket 4 mechanisms mapped to future interfaces |
| `VALIDATION_MATRIX.md` | Preservation, physical-parity, cognition, information-boundary, and coverage requirements |
| `HP002_RECONCILIATION.md` | Reconciliation against Claude's HP-002 r3, with provenance labels |
| `MIGRATION_RISK_REGISTER.md` | Migration and validation risks, controls, owners, and approval gates |
| `IMPLEMENTATION_SEQUENCE.md` | Proposed future sequence; no step is authorized by T6 |
| `SOURCE_PROVENANCE.md` | Evidence inputs, source references, commands, hashes, and limitations |
| `REQUIREMENTS_TRACEABILITY.md` | Direct map from every authorized T6 deliverable to packet evidence |

## Normative language

`MUST`, `MUST NOT`, `SHOULD`, and `MAY` are used normatively. The typed
contracts are language-neutral design contracts, not source code. Where this
packet conflicts with an undecided canon question, it exposes a parameter or an
approval gate instead of selecting a rule.

## Scope boundary

No simulator source, configuration default, physics, rating mapping, cognition,
rule, random stream, trace, or accepted evidence artifact was modified while
preparing T6. This packet does not authorize B1 implementation, T3A fixture
construction, optimization, or a native rewrite.
