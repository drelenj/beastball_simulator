# HP-002 — Give-and-go: decisions reclassified under the new governance
Claude, 2026-11-08. Non-governing. rc2, manifest v2 and B0 unchanged; Contract v1 NOT FROZEN; nothing implemented. Format per the new submission rules (A to E).

## A. What was accomplished
1. J-1…J-8 reclassified (below). No owner decision is requested for any of them.
2. J-4 and J-5 compared on their physical and information consequences, with numbers from the B0 source.
3. Everything else I had open was reclassified, and my earlier "preserve B0" defaults were withdrawn where they rested only on B0's existence.

**Governance classes:** CANON (rules of Beastball; owner) · ENGINEERING (architecture, interfaces, queues, ordering, IDs; evidence, tests and Codex) · BEHAVIORAL (planning, anticipation, commitment, reaction, decision quality; recommend a default, test it, escalate only for a material gameplay difference).

| ID | Class | Disposition |
|---|---|---|
| J-1 continuation of a preselected stage | ENGINEERING | **Decided jointly** (Codex and I agree): allowed only for stages chosen in the source decision, with guard, expiry, trace record and no option evaluation. Tests GNG-NOFREE, GG-3. |
| J-2 queue semantics | ENGINEERING | **Decided jointly:** one queued conflicting bundle per exclusive resource set, atomic multi-resource admission, replacement not accumulation, no global athlete queue. Tests GNG-QUEUE, GNG-ATOMIC. |
| J-3 own-release trigger | ENGINEERING | **Decided jointly:** the preselected cut activates at the committed release event (proprioceptive; no perception delay). |
| J-4 observed-return receive stage | BEHAVIORAL | default recommended below; measured before it hardens |
| J-5 wind-up revocability | BEHAVIORAL | default recommended below; my earlier "preserve B0" is withdrawn |
| J-6 no recipient substitution at release | existing architectural requirement | not a new rule. The accepted restricted Motor Control (no target selection or substitution in MC) already requires it. B0's substitution is a Gate C change-register entry, not an approval. |
| J-7 plan limits | ENGINEERING | adopted as a default (one active plan per athlete, one active stage per plan) to keep traces and decision-budget invariants testable; GG-11 verifies; revisit only if a scenario catalogue needs more. Codex to confirm, not an owner item. |
| J-8 ordered events and batches | ENGINEERING | **Decided jointly.** `batch_seq` added to the causal-ID `order` tuple. |
Also reclassified: T6-O3, T6-O4, T6-O5, A-1 (dependency order), SQ-1, TI-9, CT-4, RN-3, T6-O6 are ENGINEERING and go through Codex and tests. SELF-1 becomes BEHAVIORAL (default below). The CANON items remain U-1…U-4 and R-RS (which ruleset's freeze rule applies is a rule question).
Withdrawn: AP-3 ("keep the non-revocable wind-up because B0 has it") and AP-7 as a B0-preservation requirement. The 400 ms post-release recovery is a calibrated parameter under the calibration freeze, not a requirement; the missing accuracy penalty for moving while winding up is a physics-fidelity gap outside HP-002, logged, not decided.

## B. What changes for B1 athlete behavior (proposed defaults)
**J-4 receive stage.** Compare three designs for A's receiving the return:
| Design | Reaction latency | Information access | Readiness advantage over ordinary |
|---|---|---|---|
| a. ordinary cognition only | delivery latency + wait for the next cadence slot | full, current | none |
| b. unrestricted plan continuation | delivery latency only | corridor and window fixed at t0, from older belief | removes the slot wait entirely, and can act on a stale corridor |
| c. restricted continuation (recommended default) | delivery latency + a reaction time the athlete has (rating-driven), no slot wait | same delivered observation as (a); activation requires the observed return to be consistent with the preselected corridor, otherwise the stage is dropped and ordinary cognition takes over | bounded: it removes the slot-phase jitter and part of the wait, not the delivery delay |
B0 numbers: decision cadence is `decision_speed × (1.3 − 0.4 × awareness)`, with `decision_speed` defaulting to 0.3 s (so about 270–330 ms; I believe it is uniform across the roster, because the roster overrides carry no such field, but I have not confirmed this). The mean wait for a slot is therefore about 0.15 s and the worst case about 0.3 s, against a return flight of roughly 0.35–0.4 s: the choice moves catch preparation by a large fraction of the flight, so it is a real gameplay lever, though not a rules question. B0 also gave the intended receiver a hidden credit of up to 500 ms of awareness; B1 replaces that with communication and observation (O2), so design (c) must not re-create it.
*Default:* (c), with the reaction time initially set to the athlete's mean ordinary slot wait, so planning mainly removes jitter and worst-case delay rather than adding a large free advantage. Tests: planned versus unplanned return catch success, GG-4, a check that no planned activation precedes its observation delivery. *Escalate only if* measurements show completed give-and-gos differing materially from the intent, which I would report with the numbers.

**J-5 wind-up revocability.** B0 wind-up is 250 × (1.35 − 0.5 × ball_handling) ms, about 212–337 ms, and B0 suppresses the carrier's decisions while it runs.
| | Non-revocable (as B0) | Revocable at decision opportunities, with cost |
|---|---|---|
| Physics | the throw happens unless physics tucks it | a cognitive abort acts like B0's existing tuck: ball retained, wind-up progress lost, recovery cost |
| Chance the athlete gets a decision slot during a wind-up (B0 numbers) | slots occur but are ignored | about 0.8 for typical ratings (wind-up about 240 ms against a cadence of about 290 ms) |
| Information use | information that arrives after the wind-up starts cannot help | an abort needs delivered information, then a slot, then acceptance; I expect few aborts, but this is a prediction |
| Failure risk | a carrier throws into a lane that has plainly closed | noise-driven flip-flops and start-abort-start loops, which the abort cost and the reaction chain should suppress |
| Fit to "decision quality" and reaction timing | weak: it ignores perception that exists | consistent: any intent can be revoked until its commitment event, and the cost is physical |
*Default:* revocable until the release commits, through ordinary decisions only (no plan guard may abort from hidden state), with the tuck-style cost. No special non-revocable carve-out. Tests: abort rate, flip-flop rate, pass completion change in the Gate C register. *Escalate only if* measured abort frequency or completion rate changes materially; I will report the numbers rather than ask in advance.

**SELF-1 (own capabilities).** Default: proprioceptive state (position, velocity, balance, fatigue felt) is exact; knowledge of one's own capability ratings is an individual estimate with a small error that shrinks with experience, as IA-001 says of athlete knowledge. The error is a schema parameter set to zero by default so exact self-knowledge can be tested as the null case (IQ tests). Not a rules change.

## C. Verified versus proposed
| Verified | Proposed |
|---|---|
| B0 mechanics of pass preparation, release, locomotion overlap, post-release recovery, receiver credit (source read by Codex and me independently) | the J-4 default (c) and its reaction-time setting |
| Cadence formula and wind-up formula from source; `decision_speed` default 0.3 s in the type definition | that `decision_speed` is uniform across the roster (unconfirmed) |
| Codex and I agree on J-1, J-2, J-3, J-8 | J-7 plan limits (Codex silent) |
| rc2 and manifest v2 still verify | the J-5 default and the expectation that aborts are rare |
Nothing here was run as a B1 experiment; no implementation exists.

## D. What genuinely requires owner approval
**Nothing from the give-and-go set.** J-4 and J-5 become owner questions only if measurement shows a material gameplay difference; I will bring numbers, not ask in advance. The canon items already open are unchanged: U-1…U-4 and R-RS.

## E. Recommended next action
1. Codex: respond on J-7, on the J-4 design (c) activation consistency check, and on the J-5 abort-cost mechanism; supply the per-action commitment events, the coincident-event table and the channel extraction.
2. Then I write T6-O4 v3 and T6-O5 v3 (ordered events and batches, per-resource atomic queues, plan layer, `batch_seq`, derived stage IDs) as an engineering proposal for acceptance by test, not by owner approval.
3. Define the measurement plan for J-4 and J-5 so Gate C can report the effect once B1 exists.
