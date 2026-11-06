# HP-002 Stage A — decision-ownership audit, cognition side (full PRISM stack)
Claude, 2026-11-06. Source: commit 2abe497 + evidence branch tools; branch `claude/hp002-audit`. **Read-only: no simulation behaviour, physics, ratings or cognition changed; nothing from T2 pre-empted.** Scope: the full PRISM stack (`PRISM_I OFFBALL TEAMVIEW FREEVIEW JSPLIT OFFACT CATCH_V2 KEEPER HAND_FIGHT`), short games, seeds 1–4. Labels: **[measured]** by instrument, **[read]** from source, **[pending]** not yet audited.

## 1. Method and instruments
- `tools/audit_trace.py` — `sys.setprofile` tracer; counts each decision/execution function as running *inside* a live `prism_field_v0.with_view` frame (decision on the player's beliefs) or *outside* (decision on true engine state). Output `audit/trace_full_s1.json`.
- `tools/audit_canary.py` — counterfactual and hidden-state perturbation probe at every carrier decision (`Match.c4c2_decide` = Pocket's `pocket_decide`). It recomputes shoot/carry/continue/best-pass values (A) on true state as the engine does now, (B) inside the carrier's own belief view, and (C) with only the opponents the carrier cannot perceive (no belief or confidence below `CONF_MIN`) moved 100 km away. Probe is behaviour-neutral: **event-log hash, score and event count identical with probe on and off for all 4 seeds [measured]** (`audit/CANARY_SUMMARY.json`).
- Caveat: `with_view` swaps player x/y/vx/vy in place, so only those fields (plus ball position/velocity) are belief-substituted; any other field a decision reads is not covered by this probe.

## 2. Headline findings
**F1. Only the policy's target and pass-ranking functions run on beliefs.** In one full-PRISM game, `Policy.targets` ran 4,336 times inside a view and `pass_ranked` 101 times inside. **Every other decision function ran outside any view, on true state [measured]:** `pocket_decide` (109), `pocket_eval` (1,534), `pocket_cont` (493), `pocket_pass_option` (389), `pocket_plan_pass` (402), `c4c2_confront` (1,481), `carrier_decision` (225), `c3_contain` (247), `c3_region` (8), `c4c2_targets` (225), `route_receiver` (225), `catch_contacts` (81), `arrow_decisions` (422), `auto_substitutions` (322).
**F2. The carrier's shoot/carry/continue/pass decision reads true opponent and receiver positions [read + measured].** `pocket_pass_option` takes the lane from `active_field()` true positions; `c4c2_eval`/`c4c2_cont` take pressure margins from true opponents. PRISM touches this decision only through pass-menu ranking noise (Playmaking) and `judge_opts` value noise (Finishing/Playmaking). Over 2,209 carrier decisions:
  - at least one opponent was hidden from the carrier in **47.5%** (1.33 of 8.7 opponents on average);
  - recomputing the options inside his own belief view changes the chosen action in **5.2%** and the best pass target in **42.8%** (median relative value change: shoot 0.6–5.6%, continue 0–3.8%, pass 5.2–6.4% by seed, carry 0);
  - moving **only the hidden opponents** far away changes some option value in **19.1%** of decisions, the best pass target in **4.3%**, and the chosen action in **0.6%** (6 of 1,049).
  Interpretation: the information leak is real and frequent in values, rare in final action choice. Not an artefact of one seed (flips 0–6 per seed).
**F3. A central, authored receiver-routing routine overrides off-ball players [read].** `c4c2_targets` (legacy, outside any view) assigns up to `ctrl_receivers` teammates to the best of 20 fixed spots on arcs of 8/12/16/19 m in front of the goal (angles −45…45°), ranking spots by pass-completion × shot/carry value computed from **true** opponents, and sends the nearest free teammate to each. A carrier with a carry intent is sent at the goal centre. PRISM off-ball overrides re-apply after it, but where they do not act this team-level routine decides. It is both a tactical prescription (receiving spots and geometry) and a true-state read. It conflicts with section 8 of the Initiative (no prescribed tactics) and must be treated as legacy tactical logic.
**F4. Defender contain/drive and region logic are legacy [measured/read].** `c3_contain`, `c3_region` run on true state; PRISM contributes only `duel_flip` (probability of flipping the decision, scaled by Defender Duel). Marking acts through `judge_target` (beliefs, pursuit only); Zone Reads through held position noise on non-pursuit defenders.
**F5. `route_receiver` gives the intended receiver a perfect interception point [read].** It uses `predict_path` on the true ball, not the receiver's belief (FREEVIEW does not reach it).
**F6. Archers are not under PRISM in play [read].** `arrow_decisions` ran 422 times outside any view; `prism_archer_v0` is shadow-only per its notes.
**F7. Kicking is still reachable [measured in T1].** Not repeated here; ownership belongs to the rules audit.

## 3. Ownership table (per action)
Columns: 1 generates options · 2 evaluates · 3 selects · 4 ratings acting · 5 resolves physics · 6 can legacy bypass/override PRISM · 7 unauthorized information.
| Action | 1 Generate | 2 Evaluate | 3 Select | 4 Ratings | 5 Resolve | 6 Legacy override | 7 Info |
|---|---|---|---|---|---|---|---|
| Locomotion target (all field players) | `Policy.targets` core + tendencies anchors + block/bounce wrappers [read] | core zone/lane scoring; PRISM judge/zone noise | engine adopts at `next_decision` cadence | PRISM eight (via perception), Marking, Zone Reads, decision_speed | `c3_desired`/`c3_move` | **yes**: `c4c2_targets`, `route_receiver` overwrite after policy; OFFACT re-applies after them | targets in-view [measured]; overwrites on true state; `c3_desired` avoidance not yet checked [pending] |
| Carry/shoot/continue/pass choice | fixed 4 options in `pocket_decide` | `pocket_eval/cont/pass_option` with drill tables (`C4C2_EST`) on **true** state | argmax + style band; `judge_opts` noise | Playmaking, Finishing (noise only) | `make_pass`/`make_shot`/carry | tendencies wrappers on `c4c2_eval/cont`; `carrier_decision` bounce wrapper | **true opponents/receivers** [measured F2] |
| Pass target menu | `pass_ranked` (in view) | `pocket_pass_option` (true) | max value | Playmaking | `plan_pass`/`make_pass`/throwing_v1 | none in menu; evaluation on true | unseen mates filtered [in view]; receiver lane on true |
| Shot | `pocket_decide` | `c4c2_eval` on true | argmax | Finishing (noise) | `make_shot`, throwing | none | as above |
| Receive pass / catch | intended-receiver routing | `route_receiver` true path | automatic | catch_v2 physics ratings | `catch_contacts`/CATCH_V2 | n/a (automatic) | perfect ball path [F5]; catch/jump decision [pending] |
| Defend carrier (contain/drive) | `c3_contain`/`c3_region` | legacy | legacy + `duel_flip` | Defender Duel (flip prob.) | engine contact | n/a | true state |
| Pursue/mark | `Policy.targets` | `judge_target` on beliefs | argmax of noisy score | Marking | `c3_move` | after-policy overwrites | beliefs [measured] |
| Zone defence | core zone anchors | held noise | engine | Zone Reads | `c3_move` | anchors = authored zones | positions by formation |
| Off-ball action (open/engage/call/wait/free ball) | `offball_actions_v0` five actions | scoring constants (placeholder) on beliefs (`believed`) | argmax + noise | eight PRISM + Live/Air Pursuit | `c3_move` | overwritten by `c4c2_targets` unless re-applied | beliefs [read] |
| Off-ball hand fight | automatic engagement in range | four-pillar contest | automatic | Blocking technique, strength, balance, perception | `hand_fight_v0` + `c3_push` | n/a | physical; band/foul detect uses true (referee) |
| Tackle | contact on engagement | physics | automatic; Carrier/Defender maneuver choice via `pose_engine` | Carrier Duel | `Engine.tackle`/`c3_*` | n/a | physical |
| Keeper save | `prism_keeper` | keeper-own beliefs | PRISM keeper | Goalkeeping | physics | [pending] verify no true reads | [pending] |
| Archer shot | `arrow_decisions` | legacy | legacy | none | `shoot_arrow` | n/a | **not PRISM** [F6] |
| Substitution | `auto_substitutions` rules | legacy rotation | automatic | none | engine | n/a | coach-level (PRISM III) |
| Restarts/inbound | `restarts_v1`, `c4c2_inbound` | legacy formation | legacy | none | engine | n/a | legacy placement |

## 4. What this means for B1 and the Initiative (for DreLen's decisions)
1. A PRISM I result that depends on carrier decisions is **not information-clean** today. F2 is quantified, not catastrophic for action choice (0.6% flips from hiding alone), but pass-target and value effects are material.
2. Removing the F2 leak means evaluating `pocket_decide` inside the carrier's own belief view (`with_view`), and rebuilding receiver/opponent inputs from his beliefs. That changes behaviour and ratings sensitivity; it needs your approval and a recalibration plan.
3. F3 (`c4c2_targets`) is legacy tactics that prescribe receiving geometry. The formation-free control mode must neutralise it as well as the positional anchors; otherwise "no hardcoded positions" is false.
4. Nothing here requires architectural change now. All proposals are held until T2 reconciliation, per your instruction.

## 5. Not yet audited (Stage B plan, read-only)
Keeper save decision and `prism_keeper` true-state reads; PRISM jump decision; catch decision; hand-fight engagement trigger; `c3_desired` obstacle avoidance; throwing execution error source; `block_option`/`bounce_option` internals; non-position fields read by decisions (heading, posture, hold state: needs field-level poison probe); Archer shadow; restart placement; per-wrapper pass-through when gated off (T2). Also a regulation-length canary run and the same probe under B0 for comparison.

## 6. Reproduce
`python3 tools/audit_trace.py 1 out.json full`; `python3 tools/audit_canary.py <seed> out.json probe|noprobe` (compare `log_sha256`). Python 3.13, NumPy 2.5.3 (Claude environment).
