# OWNER BRIEFING

1. **IMPLEMENTED**. RB-3.27 extends offline grading through the end of each possession, adds an opt-in expected-points policy and reads the ratings 0.4 workbook using its named ratings.
2. PRISM can load a versioned table before kickoff. Athletes still pick from their existing options using their observations, beliefs and decision error. The hand-set policy remains the default.
3. The complete rollout fit, held-out Gauge, learned anchor and paired roster soak are being measured. This checkpoint will be updated from the raw results.
4. The learned regulation runs depend on the fit finishing. No canon question is pending.
5. Use the completed fit and paired match evidence to judge the opt-in policy when those results are available.

## Revisions and status

- Branch `codex/rb-3-27-drill-values`
- Lead-verified parent `14b393da76bd24b3655dc539fe7ab4ce2ab73972`
- Scoring, fitting, runtime opt-in and tests `2264f1f`
- Regulation evidence runners `d5400ae`
- Roster source and reproduction instructions `1b7b206`

| Task | Status | Evidence |
|---|---|---|
| 1. Possession scoring | DESIGN COMPLETE, IMPLEMENTED | Focused scenario checks passed. Original-sample regrade in progress. |
| 2. More moments and refit | DESIGN COMPLETE, IMPLEMENTED | Ten seed sources, stratified carrier sampling, two held-out matches. Fit in progress. |
| 3. Learned PRISM values | DESIGN COMPLETE, IMPLEMENTED | Opt-in integration and focused firewall tests passed. Regulation anchor and performance checks pending. |
| 4. Gauge | DESIGN COMPLETE, IMPLEMENTED | Paired-seed script ready. Held-out result depends on the fit. |
| 5. Real ratings | DESIGN COMPLETE, IMPLEMENTED | Pinned workbook and selection readback in evidence. Soak in progress. |

## Standing gates

 a) pytest -q b1 native, full suite, after the last change.

 b) Legacy hash guards unchanged (six rows, native/evidence/rb3-reach/legacy-hashes.txt).

 c) Determinism: same code + roster + seed gives identical trace and state hashes.

 d) Compatibility (individuation off): real seed 1 = 57-76, trace 44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072, state 046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d.

 e) CORE identity (learned values OFF): neutral-real seed 1 = 61-80, trace c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256, state c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745.

 f) Speed: individuation-on at most 15% slower per step than RB-3.22; learned values must not add more than 5% on top.

 g) Firewall: live true state never reaches cognition; learned artifacts enter only as versioned files loaded before a match; the purity test covers the new loader.

The full suite reported `767 passed, 1 warning, 23 subtests passed in 652.72s (0:10:52)`. The warning was the pytest dependency's `CallSpec2` deprecation.

The focused tests cover a defensive intervention during the opponent's possession, separate reporting of the action outcome, rejection of a changed table, decisions after removal of the loaded file, an information-boundary poison test, and independent 0.422 roster selection.

## Implemented measurement

Each branch starts from a captured decision and changes one selected option. The return is the choosing team's net points through a turnover, goal, period end or a 120 simulated-second safety cap. If a team started on defence, the rollout tracks the other team's possession. Passing, Finishing and Takedown retain the first action outcome and elapsed time as a diagnostic. The branch seed derivation and 20 replicates per option remain fixed for comparison with RB-3.26.

The neutral sample retains the original 150 selections from seeds 1–3 and adds preregistered draws from seeds 4–10. Training uses 1–8. Seeds 9 and 10 remain out of fitting, through the Gauge. Live expected-point cells use a training-only hierarchy of action, game situation and detail. A cell starts with 40 trials' worth of the parent estimate, a shrinkage choice for this experiment. The four diagnostic tables and the two live tables compare held-out mean squared error against the relevant pooled training mean.

The live configuration stores the artifact SHA-256. Startup validates the schema, feature version and checksum and builds immutable table cells. Normal decisions do no file I/O. Carrier options and committed Finishing aims use the same available information and seeded error as CORE. Their learned values displace the hand-set values, including the carrier's flat shot offset. No value artifact is required when the switch is off.

The ratings 0.4 workbook is pinned in the reproduction note. The named ratings supply the simulator's inputs. The calculated Overall for this experiment supplies the selection order. The readback independently checks top IDs by position group, the 22 entry shape, the underlying rating columns and role-specific attributes for the 12 franchises in the match sample.

Reproduction commands and evidence locations are in [rb327/README.md](rb327/README.md).
