# OWNER BRIEFING

1. **IMPLEMENTED** the eight-arm ladder. **TESTED** all eight arms on Garvian Guardians vs Ala Apex seed 1. The ninth game repeated A5 for determinism.
2. Native can exercise movement admission, goal-mouth boundaries, Keeper response, targeted release interrupts, passing effort and seven-point carries as separate switches. The accompanying tables give every rung and A5 minus A0.
3. The cadence comparison uses one paired game. Score, possession, scoring mix and margins are descriptive. The catch-band rates describe these receivers and these passes.
4. All standing gates ran on CPython 3.13.5. The soak runner was delivered and the soak was left for owner review.
5. Recommend A5 (300 ms) for a future owner-authorized soak. A5 cost 1.60× A0 and the 200 ms arm cost 1.90×. Gameplay effects of the two cadences are not separable on one game.

## Standing gates

 a) full suite; b) six legacy hashes; c) determinism (repeat A5 seed 1 exactly);
 d) compat 57-76 trace 44399b08...c072 state 046ea55b...865d;
 e) CORE 61-80 trace c1a578db...a256 state c517e00f...2745;
 f) RB-3.28 85-86 trace a399f74f...ac4b state bc4898a8...61d4;
 g) RB-3.31 planned 64-96 trace ab86f8be...a08a state e8318c85...1047;
 h) RB-3.32 combined 99-74
    trace 0045e62d5de38fc85a6c38fd58298284f637bb6d1766ddb7d50cfb159ac22601
    state b2b6857584bbdc7c486b54f52bd8ebf9c2c89fde8e15893a42c70f5c3be9d9de
    (all new switches OFF);
 i) NEW: record score, trace and state hashes of A0, A5 and A5' on Garvian-Ala seed 1.

The full suite reported `817 passed, 23 subtests passed in 575.88s (0:09:35)`. All six legacy windows matched byte for byte. Historical score, trace, state and configuration digests were compared to the RB-3.32 evidence. A5 reproduced its score and all three fingerprints. [Raw evidence](rb333/evidence)

## Build and measurement

Branch `codex/rb-3-33-ladder`, parent `33c932b330417c205631b259656dd337b638f4ab`. The tested runtime commits are `6015605` and `83c2f96`. Every arm used CPython 3.13.5, Garvian as A, Ala as B, ratings 0.4 explicit, planned rotation at scale 0.58 and the hand-set decision values.

- **A0.** Disables RB-3.32 Carry Finish, keeps the other three fixes, admits holder evidence by latency plus sensor interval plus step, and checks arrival clearance at both pass-selection stages.
- **A1.** Movement targets are admitted every PRISM update. The carrier end-line test uses the half-disc at hand height. The locomotion update reserves braking distance on held-ball routes. Goal adjudication retains the whole-ball plane test.
- **A2.** The opposing Keeper gets a targeted visual sample on shot release. A second visual observation supplies a course if available. The motor uses the reaction deadline and actual motion penalty. Reachable believed saves compete with a later intercept sample. The settle option uses the observed course, an opponent possession signal and the existing 1–4 m depth. The settle range is 40 m.
- **A3.** Sensing runs at 100 ms and ordinary observation latency stays 200 ms. Reaction scales the 300 ms deliberate clock. Targeted release cues wake the receiver, defenders within 15 m of the pass segment and defenders committed against the releaser. A wrap-release cue excludes the old holder from immediate takedown choices. A5prime uses a 200 ms base.
- **A4.** Open-play passes signal wind-up immediately or after the admitted wait. Receiver forecasts and the pass menu use the requested distance rule, capped by receiver Catching. Catch capacity inverts the existing eighth-power security curve at 90% security and 0.4 miss, using a stationary receiver as the safe-speed reference. Existing Touch changes pitch at constant speed, so the new independent uniform Touch error changes realised speed. Throw Accuracy still controls angular error. Restarts retain their own release contracts.
- **A5.** The rule authority and physical configuration agree on carry 7. Release distance selects the public scoring value. Near goal, continuation and shot options map existing utility to a bounded chance and multiply by the possible scoring reward. Direct carry routes use carry points times route probability. Finishing can offer stretch whenever the existing hand envelope reaches the plane inside the mouth. Ball Handling governs extension and security.
- **Strength audit.** The observer joins the target ID to the roster Strength column. The 44 selected ratings range from 0.65 to 0.96, with 24 distinct values. Wrong-target commitments put a non-carrier’s strength in this column. This is a roster attribute measured before fatigue.

## Single-game interpretation

For the three quantities with an owner-supplied reference, the flags below use twice the quoted RB-3.32 game-to-game SD (8 interceptions, 6 boundary turnovers or 38 team points). This is a descriptive scale. All remaining contrasts are **within single-game noise** for decisions about adoption. Rates with no prior variability estimate are left descriptive.

- A0 minus RB332 — interception -13.0 per team.
- A1 minus A0 — interception +9.0 per team.
- A2 minus A1 — out of bounds +8.0 per team.
- A3 minus A2 — out of bounds -11.5 per team.
- A4 minus A3 — out of bounds +11.5 per team, Points per team +42.5 per team.
- A5 minus A4 — out of bounds +6.0 per team, Points per team -54.0 per team.
- A5prime minus A5 — out of bounds +7.0 per team.
- A5 minus A0 — out of bounds +15.5 per team, Points per team -45.5 per team.

The A0 transition also disables Carry Finish. Its difference combines that change with the two A0 fixes. No conditions were retuned. The combined groups of changes within later rungs also limit causal attribution.

## Inspection and limits

- A5 CPU 226.78 s (1.60× A0). Top sampled frames port.py/capture (614 samples), <string>/__init__ (486 samples), port.py/<genexpr> (190 samples). Within the 2.5× budget.
- A5prime CPU 269.94 s (1.90× A0). Top sampled frames port.py/capture (610 samples), <string>/__init__ (588 samples), port.py/<genexpr> (258 samples). Within the 2.5× budget.

All restarts closed. The final-state and scoreboard checks passed. A box-score screen found the following field players with over one live minute and under 0.1 m of movement: []. This screen cannot rule out short stationary episodes.

A4 to A5 reduced near-goal carries ending in a shot from 62 to 21. Handoffs rose from 9 to 15 and near-goal passes from 3 to 15. A5 scored zero carry goals and attempted zero stretches. At 141,099 ms a held ball crossed at (−0.108, 20.264) while its carrier was still at (0.652, 20.262) aiming for (1, 50). This is outside the goal mouth. The braking rule permits a residual boundary loss.

The turnover ledger lacks an independent “drop caused turnover” or “deflection caused turnover” label. The tables report targeted drops and deflections leading out separately. Lateral pass miss is measured at the intended range from launch yaw. It does not include vertical or receiver timing errors. Each arm has a named roster box in JSON and CSV. [Definitions and commands](rb333/README.md) · [Raw results](rb333/evidence) · [Named boxes](rb333/evidence/boxes)

Before changing any parameters, measure the remaining score and possession gaps across more than one seed. Any later retune should isolate one rung. No new CANON question arose.

[All per-arm values and differences](rb333/TABLES.md)

## What changed on seed 1

A5 averaged 46 points per team, 45.5 fewer than A0. Possessions were nearly unchanged at 135 versus 136. The share of possessions ending in an attempt fell from 37.87% to 26.30%. Boundary losses rose from 24.5 to 40.0 per team, including 6.0 more body crossings and 9.5 more ball crossings. All of these boundary losses were outside the mouth. Interceptions fell by 4.0 per team, within single-game noise.

A5′ averaged 68.5 points and 158 possessions per team. Both final configurations scored below the owner's 75–90 reference. A5 fell inside the 100–150 possession reference and A5′ exceeded it by eight. On this game, A5′ produced one carry goal and neither final configuration started a stretch. The evidence supports comparing the value of continuation with shooting in a future experiment before adjusting cadence or scoring.

The A3 field interrupts generated 239 wrap aborts per team. No arm logged an immediate retarget. Despite having fresher evidence, A5 committed 28.82% of its takedowns against an athlete who was not the actual carrier at commitment. Abort counts and the non-carrier share describe separate events. A clear case for review is why committing from the last perceived carrier remains so frequent. The Keeper was moving faster than the set threshold at 40.62% of A5 shots. The match does not establish that the settle rule reliably produces a stationary Keeper.

The single-game checks exercise the combined switch sets. Two limits matter for implementation review. The open-play boundary guard for the selected carry uses the shared mouth-aware clamp. Earlier pass-lead and positional option generators still impose their own tactical field bounds, so a literal single clamp for every aim in the codebase remains incomplete. The drop and deflection totals describe witnessed events. Exact possession losses caused solely by a drop or a deflection in open play cannot be identified from the saved event labels. None of the eight games targeted a receiver with Catching below 0.60.

## Gate i

Tested runtime commit `83c2f9681cbc255a747e3154fd29f85a6664984e`.

- A0 80–103, config `7a92a06d264305cb107e8413b7da4295d5c447c8b56999f2100e43c4944eee5e`, trace `8f61716e720f8cd039eaf05d30f5fc1a84e97be1b3712977d4a24665b7892433`, state `2ca4dfd0aa8e660fefb80066ad23c80e3e74dfd9e85e7a099cb89a2807b20d75`.
- A5 45–47, config `6cc2cb426330db22707aa20877bf6d4a101a63dc815c9f0adf9fd7f4c86147e2`, trace `fd7525653598e77f1bb440847cdd46cb4364d1521dab66832c91681dde5fc194`, state `1a3a61bd1aeaeb769d7ce2ac94abac93a99be2f0f39673c5bb144079cc8ea4a8`.
- A5prime 67–70, config `b79babc7b9247ba6dc9287141ff7b9f50bfa139a7953b93c24d57409bf99ee5e`, trace `40901c2956225d04447a75abae5101e139e24f6314b3b6a62e7005702a1e2d3b`, state `28f641806971e80d2cc557ae1c84539f0e6da4d40630a2c2112f4e138b97b276`.
