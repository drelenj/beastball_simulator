# OWN / BR checks for belief-driven positioning and PolicyParams

Experimental. Nothing ACCEPTED. IDs from `b1/sprint30/OWN_BR_CHECKLIST.md`
(source `audit/m1/M1_BEHAVIORAL_ACCEPTANCE_AND_BOUNDARY_REVIEW.md`). Subject: `b1/emergence/positioning.py`
(scores candidate points from the athlete's own view/belief, weights from `PolicyParams` in
`b1/emergence/params.py`) and the parameter injection in `b1/matchport.py` / `b1/cognition.py`.

| ID | Check for positioning / params | Falsified if |
|---|---|---|
| OWN-1 | After sensor capture, poison every live field (all bodies, ball, carrier, phase, clocks, rules tracker, ends, roles, the OTHER team's params). The positioning decision record (candidates, per-term scores, chosen point) is byte-identical. | Any byte of the record differs. |
| OWN-2 | Hold the delivered view fixed, move true teammates/opponents/ball. Chosen point unchanged. | Chosen point moves with the view fixed. |
| OWN-3 | Hold true state fixed, alter the view (believed ball moved, a teammate track added next to the chosen point, an opponent on the lane). The chosen point and term scores move in the direction the weights predict; a weight set to 0 removes that term's influence. | Scores do not recompute, move against the sign of the weight, or a zero weight still changes the choice. |
| OWN-4 | Every positioning intent resolves observation -> decision -> intent -> command; the record lists the candidates, their scores and the selection rule, and re-applying the rule reproduces the choice. The params used are in the record or the trace header. | Dangling ID, unreproducible choice, or params absent from the trace. |
| OWN-5 | The move target admitted by ingress equals the intent aim. No `home` slot-grid, formation anchor or legacy hook supplies a target; `home` appears in the decision counts only if the fallback flag is on. | A move target differs from the intent, or a slot-grid target is used with the fallback off. |
| OWN-6 | Positioning decisions occur only at the athlete's cadence and never before the observation is delivered. | A decision precedes its delivery or is off-cadence. |
| OWN-7 | A teammate/opponent out of view stops influencing spacing terms once its track is stale; it never snaps to its true position. | A spacing term follows a body the athlete cannot see. |
| BR-1 | AST scan of `positioning.py` and `params.py`: imports only `dataclasses`, `math`, typing and pure B1 modules (`cognition`, `core`). | Any simulator import (`matchport`, `runtime`, `core_src`, `pocket4_proto`, `prism_*`, numpy/scipy). |
| BR-2 | Symbol scan: no `s.players`, `.ball.`, `with_view`, `Policy`, `pol[`, no module-level mutable state, no RNG. | Scan finds one. |
| BR-3 | Positioning is a pure function of (view, belief, params). Known deviation carried over: `decide(view, belief)` takes two arguments. Params must arrive as an immutable field of the view or immutable config, never as a global or closure. | A global/closure holds params or engine state. |
| BR-4 | Serialise view + belief + params to JSON, run positioning in a separate process with no simulator loaded; output byte-identical. | Any difference, or simulator modules present. |
| BR-5 | Motor/ingress takes only the intent; it never reads `PolicyParams` or belief. | Ingress or a motor hook reads params or belief. |
| BR-6 | Sample 50 positioning decisions from a trace; reconstruct from the trace alone and confirm the chosen point. | Any sample not reproducible. |
| BR-7 | Match runs with legacy controllers trapped and the slot-grid unreachable by default. | A trap fires or the run fails. |

## Parameter-injection checks (architecture rule 4)

| Check | Falsified if |
|---|---|
| Fixed before the match: the vector is validated against its bounds at port construction and logged in the result. | An out-of-bounds value is accepted, or the logged vector differs from the one used. |
| Identical for teammates (or per role): every view of team X carries the same params object for that role. | Two teammates of the same role see different values. |
| Own preferences only: team A's views never contain team B's params; swapping B's params with A's view fixed leaves A's decision identical. | A's decision changes at fixed view when only B's params change. |
| No global state and no change during a match: params object is frozen; identity and hash are the same at the first and last decision. | Mutation succeeds, or the hash differs within a match. |
| Determinism: same seed + same params gives the same trace hash, serial or parallel, any order. | Any hash differs. |
