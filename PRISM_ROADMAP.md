# PRISM roadmap: three layers of responsibility (not levels of authority)

| Layer | Question | Status |
|---|---|---|
| PRISM I, individual cognition | What do I perceive, believe, decide and do? Perception, Recognition, Inference, Strategy, Motor Control | In development: Archer, field carrier, lab defender |
| PRISM II, distributed cognition | What do we know, say, hear, conceal, infer from each other? | Interfaces only (this package, inert) |
| PRISM III, coaching / strategic cognition | What should the team do and how does it adapt? Instructions, never direct control | Planned |

Working names from the Codex discussion: **CORE** (I), **MESH** (II: Message Exchange & Shared Hypotheses), **ATLAS** (III: Adaptive Task Learning & Allocation). Alternatives SOMA / WEAVE / SAGE. Not decided here; names are non-genre-specific so the architecture can move to other simulators. Check existing software and trademarks before publishing any of them.

## Governing rule
No information moves between minds without a plausible acquisition or communication pathway. A coach's knowledge is not a player's knowledge; one athlete's observation is not team awareness; an overheard call can be useful and wrong.

## Three information types (tag every belief with one)
PRIVATE (own perception/inference), COMMUNICATED (from another mind; flagged, trust-weighted, may be wrong or deceptive), PUBLIC (official game state only: score, clocks; no free player positions).

## Phase I interface (established now, inert: `prism_comms_v0.py`)
receive_observation, receive_message, update_beliefs, send_message, receive_instruction (+ select_action stays in Strategy). `ArcherPrism` inherits `CommsMixin`; `COMMS_ACTIVE=False` keeps Phase I behaviour identical (existing 21 PRISM tests unchanged and passing).
- A message has sender, kind (observation, warning, instruction, intention, deception), channel (voice, gesture, signal), origin, loudness, optional addressees. Empty addressees means anyone who can acquire it, which includes opponents.
- Acquisition = range, line of sight (gesture/signal) and crowd noise (voice); arrival after channel latency; lands in a SEPARATE communicated belief store weighted by trust x clarity x sender reliability.
- fused(): a private belief at least as fresh wins; a stale private belief yields to a fresher communicated one. Receivers never see the simulator-only `truthful` flag.
- Implicit coordination (reading a teammate's rotation from movement) needs no message: it is ordinary perception plus inference, and belongs to PRISM I's Recognition/Inference.

## Order of work
1. PRISM I: defenders on PRISM in the engine (carrier + defender), Instinct/Judgment on real teams (the lab showed 1v1 cannot separate them).
2. PRISM II: first message type = warning about an unseen approaching opponent; metric = decision regret with vs without calls, and what an overhearing opponent gains.
3. PRISM III: instructions as goals interpreted through each athlete's own PRISM.
