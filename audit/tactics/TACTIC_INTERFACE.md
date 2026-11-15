# TACTICS-0: tactic interface (how a tactic reaches athletes without breaking IA-001)
Claude (Fable), 2026-11-15. Branch `claude/tactics-0`. Written against Native v0/3 (`claude/native-v0-3-handoff-69stxd` @ 8613280).
Status: **DESIGN COMPLETE**. Not IMPLEMENTED, not TESTED, not ACCEPTED.

## OWNER BRIEFING
1. **Accomplished.** A design for how a team tactic reaches twelve athletes who share no live channel: each athlete carries his own copy of a pre-match playbook, as something he remembers, and it shapes his decisions through the normal intent pipeline. Fourteen information-boundary tests are specified.
2. **What the simulator can do now.** Native v0/3 already has a small version of this: a 16-number team vector that is fixed before the match and reaches each athlete only through his own view. It is the same for all teammates, so it cannot carry slots.
3. **Unimplemented or unproven.** The playbook, its delivery, the cognition that reads it and all fourteen tests. Whether athletes can run a timed joint play from a shared plan and their own beliefs, with no messages, is unknown.
4. **Blocking.** Nothing blocks the design. Building it needs Codex (the view field, the harness input, one public signal) and Claude (the playbook compiler and the cognition).
5. **Recommended action.** Relay sections 3 and 6 to Codex with the attribute step spec. Decide Q-TAC-6 (may a plan change at a break or timeout) when convenient; the placeholder is no.

## 1. The rule this must keep
**IA-001 (decided by DreLen).** Athletes hold individual, imperfect knowledge that improves with realistic observation and experience; the engine keeps authoritative true state for physical resolution. Cognition and Motor Control never read hidden state.

What follows from it here:
- An athlete decides from his own view and his own belief. Nothing else enters `decide(view, belief)`.
- There is no live team channel in Native. M2 message content is null and stays null.
- The engine does not prescribe: it places nobody, chooses for nobody and corrects nobody toward a plan.
- An athlete may not read another athlete's hidden attributes, including a teammate's ratings.

## 2. The design in one paragraph
A tactic is a **pre-match plan that each athlete holds as his own prior**. Before the match, outside the engine, a coach step assigns the roster to the tactic's slots by rating band and compiles one **playbook** per athlete. The playbook is delivered once, in the athlete's own view, and never changes during the match. The athlete's cognition reads it together with what he sees and believes, and the result is an ordinary `ActionIntent` that goes through the same admission and motor path as today. No message is sent, no state is hidden, and the engine reads nothing from the playbook.

This is the plan a player learns in the week before a match: he knows his job, his teammates' jobs and the set plays. On the field he still has to see where the ball is.

## 3. What a playbook contains
One immutable record per athlete. Team-level content is identical in every teammate's copy; the slice marked "mine" differs.

| Field | Content | Whose knowledge it is |
| --- | --- | --- |
| `tactic_id`, `playbook_digest` | Which tactic, and a hash of the whole team plan | Team meeting |
| `my_slot` | My slot id and instance number (for example GUN 2) | Mine |
| `my_parameters` | Every team parameter of `tactics_0.json`, with my slot's overrides applied | Mine (team values are shared) |
| `my_anchors` | My slot's five anchors: offence, defence, own restart, opponent restart, Hunt | Mine |
| `slot_chart` | For every teammate id: slot id and instance. For every slot instance: the bench order | Team meeting. Contains no ratings |
| `plays` | The named restart and Hunt plays, written by slot | Team meeting |
| `policy_params` | The 16 `PolicyParams` values (the EXPRESSIBLE NOW part), so present cognition keeps working | Team meeting |

What a playbook **never** contains: anything about the opponent; any teammate's ratings or body; any live state; any absolute match time; any instruction that names a future event as if it were known.

## 4. How it shapes a decision
`decide(view, belief)` stays the only decision function and stays pure. The playbook is a field of the view.

| Playbook content | How cognition uses it | Example |
| --- | --- | --- |
| Biases and preferences | Added to option values, as `PolicyParams` biases are today | `carrier.finish_pref` raises the value of a deep throw for a GUN |
| Thresholds | Replace constants in cognition | `def.commit_gap_m` replaces `TACKLE_COMMIT_M = 6.0` |
| Filters | Remove options | `carrier.shot_range_min_m` drops a throw at goal from 12 m for Arc Siege |
| Anchors | One more candidate position, computed from my anchor and my **believed** ball, goal and teammates, and scored against the nine belief-driven candidates with weight `pos.anchor_pull` | A SCREEN's candidate is 2 m goal-side of where he believes his GUN is |
| Plays | Condition on a **public** signal and my slot | At a scrimmage (public restart record), a FEED goes 7 m behind the ball line |

The output is an `ActionIntent` of a kind that exists today. Motor admission, legality and physics are untouched. A parameter tagged NEEDS ENGINE WORK in `tactics_0.json` needs the engine work named there before its playbook value can do anything.

**The plan is a prior, not an order.** With `pos.anchor_pull` at 0 the anchor is ignored and the athlete behaves as in Native v0/3. As the weight rises the athlete holds his position more firmly against what he sees. The weight is one unsearched value (2.0) for all eight styles. How firmly athletes should hold a plan is a BEHAVIORAL question for testing, not something this design settles.

## 5. Joint play without a channel
Several styles need teammates to act together: a zone rotation, a wedge, a set restart. With no messages, three things are common knowledge and nothing else:

1. **The playbook.** Everyone holds the same chart and the same plays.
2. **Public signals** already in the view: phase, restart record (kind, spot, taker), play clock, score, period, which team has possession, who is frozen or immune.
3. **What each athlete believes he sees** of his teammates, which may be late, noisy or missing.

Each joint behaviour is therefore written as an individual rule on those three:

| Joint behaviour | Individual rule |
| --- | --- |
| Zone rotation (Zone Waves) | I enter when I believe my pair partner is outside the arc, or when his visit must have ended by the dwell limit. I leave on my own residence time, which I know exactly |
| Wedge (Carry Train) | My anchor is relative to where I believe the ball is; I hold it while I believe a teammate carries |
| Set restart | The restart record is public. My slot's play position follows from it. The taker is whoever the record names |
| Hunt | Only the holder of the contestant slot claims. The others do not |
| Who marks whom (man schemes) | I take the nearest opponent I believe is unmarked; a tie between two teammates goes to the lower slot instance, which both know from the chart |
| Who closes on the ball | I count the teammates I believe are nearer; I go if fewer than `def.pressers_max` are |

Two athletes can believe different things and both go, or neither. That is a legitimate outcome of individual knowledge. The engine must not repair it, and the test plan measures how often it happens.

## 6. Data contract and who builds what
**Before the match (harness, outside the engine).**
1. `assign(tactic, roster)` from `audit/tactics/tools/roster_tools.py`: slots by rating band. This is the coach's knowledge. Ratings do not travel past this step.
2. `compile_playbooks(tactic, assignment)` returns `{athlete_id: Playbook}` and a team digest.
3. `run_match(seed, config, playbooks={'A': ..., 'B': ...})`. Today the same call takes `policies={'A': PolicyParams, 'B': PolicyParams}`.

**During the match.**
- `AthleteView.playbook: Playbook | None`. `None` means Native v0/3 behaviour, byte for byte.
- `AthleteView.policy` is filled from `playbook.policy_params`, so present cognition is unchanged.
- The match trace hash includes each team's playbook digest, as it includes the policy vectors today.
- `view_to_json` and `view_from_json` carry the playbook, so a recorded decision can be replayed.
- Every decision record names its source: `plan` when a playbook value changed the chosen option, otherwise `belief`. This keeps the formation-free arm of the B1 specification checkable: a run with `playbook=None` must contain no `plan` record (its DO-3 provenance check).

**Arms.** The B1 specification has a formation-based arm and a formation-free arm that differ only in which providers of assignments are enabled, and it bans externally prescribed tactical assignments in the formation-free arm. A playbook is an assignment provider. A run with playbooks is therefore the formation-based arm, and it is never reported as formation-free or as emergence.

| Work | Owner |
| --- | --- |
| `playbooks` input to the harness and port; `AthleteView.playbook`; digest in the trace hash; JSON round trip | Codex |
| Public tackle count in `Signals` (needed by two parameters) | Codex |
| `Playbook` type, `compile_playbooks`, the assignment rule | Claude |
| Cognition that reads the playbook; decision-record source tag | Claude |
| Tests IB-1 to IB-14 | Claude writes the cognition-side tests; Codex the port-side ones |

**Substitutions.** A substitute takes the slot of the athlete he replaces. Who left is public officiating, and the bench order is in the chart, so the substitute knows his slot without being told anything during play. If a team is short-handed during an exclusion, the others keep their own slots.

**Stages.** P0, available now: the 16-value projection, team-wide. P1: playbook delivery and each athlete's own thresholds and preferences. P2: anchors and joint plays. P3: the NEEDS ENGINE WORK parameters, after the attribute step.

## 7. What is forbidden
- No live communication. The M2 payload stays empty; the playbook is never sent over the team transport.
- No hidden state. The playbook is in the view, in the decision record and in the replay.
- No engine-side prescription. The engine, port and rules layer copy the playbook into the view and do nothing else with it. They never place, move, select or correct an athlete from it.
- No change during the match. One playbook per athlete per match. A change at a period break or timeout is not allowed in TACTICS-0 (PLACEHOLDER, Q-TAC-6).
- No reassignment from true state. Slots are assigned once, before the match, from the roster sheet.
- No opponent data. The schema has no field for it.

## 8. Information-boundary tests
None exists yet. "Poison" means replacing a value the athlete must not use with one that would change his decision if he used it.

| ID | What it shows | Method | Pass |
| --- | --- | --- | --- |
| IB-1 | Decisions depend only on view and belief | Purity scan of the cognition modules (AST: no engine, port or rules import); call `decide` twice on the same view and belief with different true state behind them | Identical intent and record |
| IB-2 | No cross-team leak | Build the first views of a match twice, changing only team B's playbook | Every team A view is byte-identical |
| IB-3 | The playbook does not change | Hash each athlete's playbook at every decision in a full match | One hash per athlete |
| IB-4 | The engine does not read the plan | Wrap the playbook so that any attribute read outside the cognition modules raises; run a 600 s window | No raise; AST scan finds no playbook read in engine, port or rules beyond the copy into the view |
| IB-5 | No playbook means Native v0/3 | Run seed 1 with `playbooks=None` | Trace hash and state hash equal the recorded native-v0/3 values |
| IB-6 | A neutral playbook changes nothing by accident | Run with a playbook that holds only the neutral values and `pos.anchor_pull = 0` | Same hashes as IB-5 apart from the digest term; decision kinds identical |
| IB-7 | An athlete holds only his own slice | Change a teammate's slot override; compare my view | My view and my decisions unchanged |
| IB-8 | No message carries the plan | Inspect every M2 envelope of a match | Payload length 0; no playbook bytes |
| IB-9 | Anchors use beliefs | Poison: give an athlete a believed ball position 15 m from the true one | His anchor candidate follows the believed position |
| IB-10 | Joint triggers use public signals and beliefs | Poison: true partner position inside the zone, believed position outside | The athlete acts on the believed position |
| IB-11 | No teammate ratings reach an athlete | Schema check of the compiled playbook; change a teammate's ratings with the assignment held fixed | Playbooks byte-identical |
| IB-12 | No opponent data | Schema check; compile team A's playbooks with two different team B rosters | Byte-identical |
| IB-13 | A substitute learns his slot only from the public substitution | Force a substitution; compare the substitute's bench view before with his field view after | Slot appears only after the public event |
| IB-14 | Determinism | Same seed and playbooks twice; serial against parallel | Identical trace and state hashes |

Two further checks belong to the formation-free arm and are not new: a run without playbooks contains no decision record with source `plan` (DO-3), and no report from a playbook run uses the word emergence.

## 9. Risks and limits
- **A plan can become an order.** A very high `pos.anchor_pull` makes an athlete hold his post whatever he sees. That still obeys IA-001, because he decides, but it is a formation grid under another name. The weight is logged and reported with every result.
- **Timing without a channel may not work.** A 3.5 s rotation leaves 1.5 s of margin; athletes sense every 200 ms with 200 ms of latency and decide every 500 ms. The margin may be too thin. That is a finding to make, not a reason to add a channel.
- **Cognition is where a leak would happen.** The tests above can show that a playbook is static and private. They cannot show that every future cognition change reads only beliefs; IB-1, IB-9 and IB-10 must run on every change.
- **The coach step sees ratings.** It runs before the match and hands each athlete only a slot. If a later design lets athletes know teammates' abilities, that is an IA-001 question for the owner, not an engineering choice.
