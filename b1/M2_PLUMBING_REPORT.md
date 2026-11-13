OWNER BRIEFING
1. Accomplished: M2 transport and empty plan-stage interfaces are DESIGN COMPLETE and IMPLEMENTED. Functional evidence is listed below. Nothing is ACCEPTED by this submission.
2. B1 can carry bounded, delayed, lossy, noisy opaque envelopes through receiver AthleteView into BeliefState. NULL MODE is the default; no production sender or plan content is defined. The existing pass call remains the only production message.
3. Unproven: communication usefulness, plan usefulness, emergent play quality, and inherited behavioural/canon limitations from Step 1. No claim that communication helps.
4. Blocking: no implementation blocker. Repository-wide green remains unavailable; complete B1 and targeted functional results are recorded below. Historical test failures are not reclassified as acceptance.
5. Recommended action: Claude independently reviews ownership and M2 plumbing, then owner considers acceptance. Keep message/plan content deferred until after Emergence-1.

Engineering contract
- Branch codex/b1-m2-plumbing starts at Step 1 commit 77415393c9287d6aa9b84f415d26a0b8565d003d.
- MessageEnvelope is frozen: sender, recipient tuple, kind, opaque bytes payload, unique causal ID, send time and typed OPAQUE content slot. No gameplay interpretation or message vocabulary is supplied.
- TeamTransport receives an explicit public team roster. Cross-team routing and duplicate causal IDs fail before mutation. One closed batch per strictly increasing send time; canonical order is (send time, sender, causal ID), then sorted recipients. Concurrent producers prepare envelopes; the simulation commits one closed batch. The mutable transport is not an interface for concurrent queue writes.
- Default limits (provisional engineering configuration, not sport canon): delay 100-300 ms; loss/noise zero; 4096 serialized wire bytes per sender per 1000 ms, multicast charged per recipient; 16 messages per sender/window; 32 queued deliveries per receiver; 8 intakes per view. Oversized/rate-limited sends are dropped, full queues reject new entries, intake overflow drops newest due entries. Audit statuses distinguish loss, bandwidth, queue and intake capacity.
- Wire size is the canonical JSON UTF-8 encoding with hex bytes. Kind is metadata only. Noise independently flips one random bit per affected payload byte; metadata and content type are preserved.
- RNG is seeded with SHA-256 of (match seed, sender, causal ID, recipient), independent of engine/PRISM streams and producer scheduling. Delay, loss and payload noise are sampled once per routed recipient; loss/capacity cannot alter any other envelope's random stream.
- Delivery order is (due time, send time, sender, causal ID, recipient). No receiver callback exists. Intake occurs during MatchPort.deliver; the immutable view owns the deliveries and receive_messages(view) alone transfers them into BeliefState. Future-due messages cannot appear early.
- PlanStageActivation and ReactionGate are typed hooks called by cognition. The stage registry is empty: inactive activation, no stage ID, bypass gate. Neither hook has a world/transport reference or accepts an intent to rewrite.
- Cognition never reads message payloads for action selection. Tests compare complete decisions/intents with and without messages across roles, possession and pending-command states. Targets, receivers, aims and action kinds remain identical.
- NULL MODE neither iterates a send batch nor draws transport RNG or emits message records. Empty view/belief slots and bypass hooks do not enter action/physics trace hashing. JSON round-trip supports opaque payload bytes.
- Accepted core.py, runtime.py and g1.py remain identical to 4b19719. Frozen B0 files remain unchanged.

Verification commands
- `.venv/bin/python -m pytest -q b1`
- `.venv/bin/python -m pytest -q b1/test_communication.py`
- `.venv/bin/python -m b1.match_run --seed 1 --telemetry-off --out b1/evidence_m2/null-seed1.json`
- `.venv/bin/python -m b1.g1 --matrix 100 --out b1/evidence_m2/null-g1-matrix.json`
- Full-loop three-athlete matrix: run_match(seed, scenario, 9000, False), scenarios g1/g1_close, seeds 1-8; compare every row with evidence_ownership/matchport-matrix.json.

Functional evidence
- Complete B1 suite: 117 passed, 23 subtests passed (406.27 s). This run collected the original six M2 tests; the additional pre-delivery poison case and expanded final action-isolation cases were verified in the final focused run: seven passed (7.46 s).
- M2-2: synthetic messages traverse actual enabled transport delay/noise into receiver view/belief; loss=1 test delivers nothing. JSON round-trip preserves deliveries. Poison before delivery changes live ball/player/ownership and future queued messages without changing the received view, belief or decision.
- M2-3: identical envelopes replay across serial and ProcessPoolExecutor runs and reversed producer input order, with identical delivery payloads/order/audit; causal IDs survive and duplicate IDs reject atomically.
- M2-4: tests enforce byte and message budgets, window rollover, multicast cost, canonical ordering, queue/intake capacities and team routing.
- M2-5: complete decisions/intents equal with and without synthetic messages across all three roles, possession/no possession, pending/no pending; hooks remain inactive/bypass.
- M2-1: full seed-1 null replay equals Step 1 trace/state, decision-kind counts, ownership counts, score and end time. Sixteen full-loop three-athlete null scenarios equal every baseline trace/state/terminal.
- M2-1 governed matrix: all 600 episode records equal baseline exactly; matrix hash 3f61f1e6d66a78120281755d2f9e771db0b90959a0806f3e84173d32c33edd12. Existing behavioural/attribution gates are unchanged (including false gates).
- Final preservation check: 427 frozen B0 paths verified; accepted core/runtime/g1 diff empty.

Repository-wide limitations
Full pytest collection stops on CLI entry scripts block_test.py and rs_test.py, missing Playwright in lab, and missing results_v37/capability_table_v37.json. An available-suite run excluding those paths completed: 335 passed, 19 xfailed, 23 subtests passed, seven failed. Five were the earlier B1 assertions subsequently fixed and verified by the green complete B1 reruns. Two require absent baseline_v30_shipped/beastball_v30_results.csv and LOCOMOTION_1_0_MANIFEST.json. No frozen B0 file or fixture was synthesized or modified. Raw logs are committed in evidence_m2. Repository-wide green is not claimed.
