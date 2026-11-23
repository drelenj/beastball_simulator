# RB‑3.23 rating mechanisms

This opt-in experiment adds local coefficients to the existing PRISM pipeline. Disabled is the RB‑3.22 compatibility mode. Enabled is `individuation/1`. Regulation, scoring, body geometry, the set formation, action vocabulary and rules admission use the existing implementation. The experiment does not introduce a rating-based outcome draw. The motor changes a feasible command and the physics resolves the result.

The table gives the first experimental mappings. Here r is the athlete's own normalized rating and d = r − .70. Effects are bounded by the roster's [0,1] validation. Larger ratings change the indicated model input, and a favourable outcome still depends on the situation.

| Own rating | Existing path and effect | Bounds or limit |
|---|---|---|
| Vision | Visual sensor field cone | 90° + 30°r half-angle. Existing body occlusion, 2 m exception and Archer platform visibility still apply. |
| Clarity | Vertical ball sample noise and resulting observed vertical velocity | SD .04(1.4 − .6r) m. Awareness still owns XY sample noise. |
| Reaction | Runner schedules the next cognitive decision | 500(1.3 − .4r) ms at default cadence before simulation step quantization. Sensory delivery, release wind-up, save preparation and recovery retain separate clocks. |
| Anticipation | Lead a perceived moving pass receiver | Existing lead solver receives velocity scaled by 1 + .5d. The map represents trust in the short-term forecast. It has no access to future positions. |
| Focus | How long a previously observed track is kept | 1,400–2,000 ms. No new observation is created. Ball-course freshness still has its own shorter horizon. |
| Instinct | Existing shot-option value under a possession deadline | Adds 2d in the last three seconds, only when holding the ball and a shot candidate already exists. |
| Judgment | Existing M1 defender passing-lane option | Uses .70 + .35d in the existing lane interpolation. Affects lane evaluation in this version. Full risk, timing and legality reasoning remain baseline behavior. |
| Touch | Existing in-play throw motor | Pitch error ±2(1 − r)°. Release speed is conserved. Throw Accuracy still governs horizontal error. Restart snaps stay on their designated lane. |
| Motor control | Existing movement command translation | Heading grid 6(1 − r)°, so maximum rounding error decreases with rating. The motor does not change action kind, target identity, propulsion or physical collision. Restart placement and snap hold are exempt. |
| Playmaking | Existing carrier pass valuation | Receiver-space coefficient adds .10d. Ineligible or rejected lanes remain excluded. |
| Finishing | Existing shot valuation | Keeper clearance coefficient adds .8d. Goal geometry, aim feasibility and score awards stay independent of the rating. |
| Marking | Existing field defender mark option | Blends the legacy positioning point toward a perceived carrier's goal-side point with weight .4 + .5d. This is an assignment preference, with no forced defensive contact. |
| Zone reads | Existing attacking zone exit decision | Adds .65d seconds to the cognitive exit margin. The legal five-second limit stays fixed. |
| Goalkeeping | Existing Keeper's perceived-ball alignment for set position | Scales the observed lateral offset by 1 + .5d. The save planner retains a delivered course and the existing launch conditions. |
| In-air ball pursuit | Existing pursuit of a free ball with observed height above .45 m | Adds 6d metres to own nearby-pursuit threshold and d to pursuit value. Height uses delivered data. |
| Live ball pursuit | Same pursuit option for a low or unknown-height free ball | Same bounds, independent of airborne rating. |
| Carrier duel | Existing brace/run-through/dodge choice | Adds .5d to run-through option while held; adjusts minimum believed dodge lead by −.15d seconds. The grip kernel owns the actual outcome. |
| Defender duel | Existing wrap/takedown choice | Adjusts the believed commit threshold by d metres. Grip and tackle physics stay unchanged. |

## Existing capabilities

- Stamina now reaches the existing C3 energy model in the experimental profile. The fatigue rate assumption is recorded in the config and read back during match construction. The established no-burn mode still runs in compatibility.
- Keeper Skill scales the available push-off fraction of the existing save motor from .75–1 times the normal assumption. Goalkeeping sets position from belief. Catching owns contact arrest. Height and arm span still determine physical coverage.
- Archery Accuracy reduces a seeded release yaw error from ±1° to zero, preserving velocity magnitude and leaving target legality, quotas, swept contact and immunity with the existing rules and physics.
- Throw Accuracy is canonical and feeds ball release yaw. Passing is a compatibility alias. Native has no kicking action. Frozen legacy source still contains historical kick-related expressions, which remain outside the Native command path.
- The shared release clock still uses Ball Handling. Physical timing and the per-athlete acceleration/throw ceiling are independent of the scheduling change. Existing random streams own all sampling.

## Provenance and unresolved data

Use `--technical ovr` for the compatibility workbook proxies and `--technical neutral` for the published neutral diagnostic. `--technical explicit` reads the workbook headers listed in the registry, with numeric values divided by 100. The roster stores explicit-versus-fallback provenance in this mode. Missing legacy technical values fall back to Opening-day OVR, missing draft values use .70, and missing independent Contact Resistance uses .784. The old workbook adapter modes preserve their Balance fallback. The normalized CSV/row adapter already accepts independent Contact Resistance and draft ratings. The canonical workbook remains unedited and does not supply these new independently authored ratings. The experiment does not infer them from names or player archetypes.

Durability is stored as a possible susceptibility trait and Injury remains an undefined optional rating. Active injury state remains the engine's forced injury/head-evaluation and substitution state. There is no authorized injury-generation model. Neither input participates in experimental behavior fingerprints. The full roster/config digest still records supplied metadata.

These are first-pass mechanisms. A match-effect sign is not guaranteed by a monotonic input curve. An isolated option-value test shows a causal difference in evaluation and does not establish how often it changes the final command.
