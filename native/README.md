Native PRISM 0 functional baseline: IMPLEMENTED and TESTED; not ACCEPTED until DreLen accepts it.

The owner-amended A4 evidence uses the first25 completed results (seed set1..25). The soak was stopped; supplemental26..28 and interrupted29..30 are excluded. No new batch was started. See NATIVE_PRISM_0_MANIFEST.json for the exact simulation revision, config and evidence, and ROADMAP_NATIVE_V1.md for the DESIGN COMPLETE next-stage plan.

The captured stack uses Python 3.12.14. Create a virtual environment with
`python3 -m venv .venv`, then install `.venv/bin/python -m pip install -r native/requirements.txt`.
NumPy is the Native runtime dependency; pytest runs the B1/Native conformance suite.

Run a full canon-duration candidate: `.venv/bin/python -m native.run --seed 1 --out native/evidence/seed1.json --progress`.
Run conformance: `.venv/bin/python -m pytest -q b1 native`.
Run isolated full seed soak: `.venv/bin/python -m native.soak --workers 2 --out native/evidence/soak` (default seeds1..25 under the owner's A4 amendment; this is a reproduction command, not a further batch run).
Run legacy B1 evidence: `.venv/bin/python -m b1.match_run --profile legacy-b0 --seed 1 --telemetry-off`.

The default Native config is native-v0/2. Full 4x600 durations cannot be shortened through its profile. Scenario tests change explicit state clocks to test overtime and exact ties. NULL M2 is mandatory; --plumbing-absent is an acceptance comparison only.

Physics and rule adjudication own true state. Native observation frames contain only noisy/delayed visual observations and public officiating. Own body/equipment knowledge is exact (SELF-1). A fresh in-memory source namespace per match avoids environment/global patch contamination. The B0 C3 physical substep runs directly; the legacy tactical top-level step is not used.

All semantic choices come from native.cognition.decide. Physical motors execute admitted commands and may reject infeasible geometry without substituting a target. Keeper commitments persist until their declared deadline. Procedural claims are canonically admitted without hidden suitability rankings. The initial legal scatter is a PLACEHOLDER setup, with no positional role/formation grid.

See NATIVE_V0_INVENTORY.md, RULE_TO_TEST_MATRIX.json and QUESTIONS_FOR_OWNER.md. Native v0 includes primitive/subset implementations; it does not claim full CATCH_V2, HAND_FIGHT or THROW_SPLIT overlay equivalence. No play quality, balance, tactics or emergence result is claimed.
