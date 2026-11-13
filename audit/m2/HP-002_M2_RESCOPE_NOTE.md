# HP-002 — M2 re-scope note (owner direction)
Recorded by Claude, 2026-11-13, from the owner's message (05:38 America/Chicago).

**Status: owner direction recorded. M2 is NOT authorized to start by this note; start still needs the owner's separate authorization.**

## Direction
Communication and plans have nothing to carry until playstyles exist. So M2 is re-scoped to **plumbing only**: every part and every hook built and wired, running in **bypass** (null content), and the actual messages and plan content are authored **after** Emergence-1 shows what teams do.

## M2 (re-scoped) contains
- Typed message and plan interfaces (draft already in O4/O5 v3.5): message envelope, delivery delay, loss and noise model, receiver-side belief intake through the AthleteView only, PlanStageActivation and ReactionGate hooks.
- A null mode (default): no messages, no plans. Behavior is bit-identical to the same build without M2 (same trace hash).
- Existing primitive: the pass call. It stays and is reported as the only message until content is authored.

## M2 (re-scoped) acceptance is functional only
1. Null mode reproduces the baseline trace hash exactly.
2. A synthetic test message passes through delay, loss and noise and reaches the receiver only through its view (poison test: hidden-state perturbation changes nothing).
3. Messages and plan activations carry causal IDs and replay deterministically.
4. Message bandwidth, ordering and capacity limits are enforced and tested.
5. No message can change an athlete's action type, target or receiver (Motor Control rule unchanged).

## Deferred until after Emergence-1
- What messages exist, what plans exist, and any claim that communication helps. Value is judged by paired with/without comparisons on match results, not by a hand-written definition of good communication.

## Carried from M1 acceptance
"Sharper defends better" is withdrawn as an acceptance item (see `audit/m1/HP-002_M1_ACCEPTANCE_RECORD.md`).
