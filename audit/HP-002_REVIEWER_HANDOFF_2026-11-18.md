# HP-002 reviewer checkpoint (18 Nov 2026, ~21:45 CT)

Written by Claude (cognition lead / independent reviewer) as a checkpoint for itself or a successor model in this chat. Source of truth for rulings: audit/HP-002_OWNER_RULINGS_2026-11-16.md. Review records: audit/native/HP-002_RB3_1_CHECKPOINT_REVIEW.md, HP-002_SOAK_RB32_REVIEW.md, HP-002_RB33_REVIEW.md, HP-002_RB35_REVIEW.md (no files yet for RB-3.6 through RB-3.10; findings were given in chat only).

## Roles and working rules
- Owner: DreLen, final authority on CANON; relays by copy-paste, so anything for another agent is a self-contained paste block.
- Claude: lead/reviewer; pushes only to claude/ branches in drelenj/beastball_simulator. Codex: engine lead (codex/ branches). Opus: provisional builder (claude/ branches). Haiku: soak runner. Possible change: Opus becomes lead/reviewer and Sonnet builds (pilot proposed on RB-3.11 Part A).
- Reports start with a plain-English OWNER BRIEFING (1 accomplished, 2 what it can do now, 3 unimplemented or unproven, 4 blocking, 5 recommended action). Use DESIGN COMPLETE / IMPLEMENTED / TESTED / ACCEPTED strictly; only the owner ACCEPTS.
- Decision classes: CANON to owner; ENGINEERING by evidence; BEHAVIORAL tested defaults. Owner often answers "recommended".
- Review habit: recompute headline numbers from raw logs or engine metrics, never only the builder's summary. Harness: native/run.py::run_match (not native/rulebook/run.py); determinism = same code+roster+seed gives identical trace/state hashes; machine has 2 cores, 3-5 min per match.

## Baselines and branches
- ACCEPTED baseline: claude/rb-3-8-drop-freeze-recovery @ 185b557 (freeze recovery retreat condition dropped; thaw buffer 1000 ms kept). Acceptance does NOT cover overall game behavior. Soak on it: claude/soak-rb-3-8 @ 3364aa0 (13 matches, all finished).
- Diagnosis: claude/rb-3-7-offense-diagnosis @ e975901.
- PROVISIONAL, not accepted: claude/rb-3-9-offense-fixes @ 6a328bf (formation, distance-based pass speed, carrier B-2); claude/rb-3-10-formation-hold @ 45a298c (no nose tackle, hold rule, receiver override, clear lane, auto-unfreeze). Linear stack on 185b557.
- Codex: codex/native-rb-3-2 @ ac52068 "RB-3.8 reconciled" (kept R31-1; RB-3.8 reference hashes superseded by R31-1 integration, decided by Claude as engineering). Codex next: cherry-pick 185b557..6a328bf, review formation.py, then 6a328bf..45a298c; do NOT build its own formation.
- Roster ref 81f92e3 (Dante Sinella top Archer 99; Kamasi Sinella locked).

## Where the game stands (RB-3.10, real seeds 1/3/5 + control 1)
Snap interception 0.6-2.3% (was ~50%); possessions 208-221 per team (target ~100); 13-22% possessions end in an attempt (target ~50%); carry goals 0/4/4/3; total points 55/60/73/46 (target 80-85); zone_residence calls 15/6/15/5 unchanged; foul-award points 7-22.

## Open items
- Owner to answer Q-RB310-1..5 (my recommendations: yes to 1, 3, 4; yes to first two parts of 2 but bar arrows during the hold (CANON, owner's call); Q5 no rule change, fix behavior via Z-2/Z-3). Also still unconfirmed interpretations: tackler stands at the neutral zone edge across the snapper; "nobody moves" pins everyone except the throw and the catch reaction.
- Defaults standing unless owner objects: formation for every scrimmage; majors inside 10 m move to the 10 m clamp; tosses unchanged (3 m, old speed); field length 100 m hard-coded (Codex to expose it).
- In flight: Haiku soak on 45a298c (claude/soak-rb-3-10, 13 matches); Opus RB-3.11 (Part A zone exit/marking behavior Z-2/Z-3; Part B fresh possession-end diagnosis) on claude/rb-3-11-zone-behavior; Codex reconcile of the RB-3.9 range.
- Next review steps: recompute each report from raw logs; then a merged SHA, a full Haiku soak, owner acceptance request.
- Older unresolved: canon average height 8'4" conflict; Archer legal-target/carries earlier note; HIVE-LAB-0 design draft; tech rating spec; RB-3.6 to RB-3.10 review record files not yet written.
- Mistakes to avoid: I once drew a defender frozen inside a Keeper Zone (illegal; only offensive players outside both zones can be frozen). Builders have missed purity tests when running only part of the suite; require full b1 + native.
