# Defender PRISM in the engine (v0.4, flags PRISM_FIELD=1 PRISM_DEF=1)

## What is wired [P]
- The DEF_K (3) defenders nearest the carrier re-choose their pursuit target through their OWN view of the attackers (the same `with_view` swap the carrier uses): unseen attackers are hidden, seen ones sit at belief position/velocity. Ratings: PRISM_FIELD_RATINGS (same for both teams).
- With PRISM_MANEUVERS=1 a defender who actually sees the carrier reads an executing maneuver's tell: confidence (Clarity, Focus, cone) x Instinct halves the carrier's evade chance at most (TELL_READ .5).
- Metrics: `def_unseen` (carrier not in his belief), `def_err` (distance between his belief-based target and the omniscient one), tell-read mean, carrier-clear rate.

## Sweep (sweep_defender_engine.py, 8 short games per row, both teams same ratings)
| config | goals | tackles | unseen | target error | tell read |
|---|---|---|---|---|---|
| legacy | 72 | 242 | 0% | 0 | - |
| carrier on PRISM only (neutral) | 74 | 295 | 0% | 0 | - |
| carrier + defenders, neutral | 131 | 198 | 2% | 3.47 m | .45 |
| all .1 / all .95 | 122 / 106 | 215 / 202 | 9% / 1% | 3.40 / 2.48 m | .08 / .90 |
| reaction .1 / .95 | 115 / 105 | 194 / 203 | 2% | 3.67 / 2.64 m | .45 / .47 |
| focus .1 / .95 | 82 / 87 | 214 / 184 | 5% / 1% | 3.41 / 3.54 m | .40 / .46 |
| vision, awareness, clarity .1 / .95 | 95-113 (no pattern) | 183-220 | 1-3% | 3.4-3.6 m | .45 |
| instinct .1 / .95 | 131 / 131 | 198 | 2% | 3.47 m | .09 / .86 |

## Reading
- Putting defenders on a neutral (.5) PRISM makes defence much worse than omniscient (goals 74 -> 131 over 8 games, tackles 295 -> 198); a neutral perceiver is a mediocre one, so the layer shifts the baseline, as in the lab. Needs calibration (higher default ratings or smaller noise) before it becomes default.
- Goals and tackles over 8 games are noise-dominated (single-rating cells span 77-131 with no monotone pattern). The mechanistic metric responds: target error falls with Reaction (3.67 -> 2.64 m) and with all ratings high (2.48 m); unseen-carrier rate falls with Focus (5% -> 1%) and overall ratings (9% -> 1%); tell-read follows Instinct.
- Vision, Awareness and Clarity alone do not move target error: the nearest defenders are close to the carrier and he is inside their cone most of the time; staleness (Reaction) dominates. Same lesson as the Archer and the lab.
- Instinct changes nothing in outcomes: maneuvers meet tackles only a handful of times per 8 games, so a tell-read effect cannot show up; use the lab (maneuver_lab.html) for tell/Instinct effects.
- Next: more seeds for outcome effects (about 40 games per cell for +-5%), or add a decision-regret metric on the defender's lane/angle choice instead of goals; then Judgment (which side to take away) and teammates (PRISM II warnings).

Files: prism_field_v0.py (PRISM_DEF hooks), pose_engine_v0.py (tell read), sweep_defender_engine.py, plat_def_sweep.json.

## Decision-regret measure (added; 5 short games per row, PRISM_MANEUVERS off)
`def_regret` in prism_field_v0.py. At each decision of the 3 defenders nearest the carrier (carrier 10-30 m away) it scores his belief-based target and the omniscient target, on TRUE state, by miss = |target - where the carrier is when the defender arrives|; regret = miss(belief) - miss(omniscient). Only pursuit decisions are scored (his omniscient target within PRISM_PURSUIT_R = 6 m of the carrier); zone-position decisions are skipped (first version scored them and was meaningless: miss was ~19 m even for the omniscient target).
Absolute miss is ~8.8 m because the engine's pursuit aims at the carrier's current position, not ahead of him; the regret is relative to that same rule, so it isolates what imperfect perception costs.

| config | mean regret | decisions regretting > .25 m | > 2 m |
|---|---|---|---|
| neutral | 2.21 m | 59% | 33% |
| all .1 / all .95 | 1.87 / 1.80 | 55 / 54% | 30 / 23% |
| reaction .1 / .95 | 2.59 / 1.74 | 61 / 54% | 35 / 22% |
| clarity .1 / .95 | 2.68 / 2.31 | 60 / 59% | 34 / 32% |
| vision .1 / .95 | 2.08 / 2.31 | 62 / 60% | 34 / 34% |
| awareness .1 / .95 | 2.32 / 2.29 | 59 / 60% | 32 / 34% |
| focus .1 / .95 | 1.55 / 2.59 | 55 / 62% | 30 / 37% |

Reading: Reaction separates cleanly (35% -> 22% large-regret decisions, regret 2.59 -> 1.74 m); Clarity weakly; Vision and Awareness not at all (carrier is in the cone). Focus is REVERSED and unexplained (low Focus has lower regret); suspects: a frozen picture extrapolated at the last velocity is a better aim than a fresh noisy one for a carrier running straight, so lapses cost little while noise costs more. That is a modelling question about the lapse/noise balance, not evidence that Focus is bad. 'All .1' also beating neutral on mean regret shows the measure is still confounded (~2 m is within what correlated decisions could produce); treat only the Reaction effect as established.

## The Focus puzzle (resolved in two parts)
Focus decomposition (sweep, 5 games per row): in the engine Focus acts through gaze slew, belief memory and radar pulse period; tracked count and identify delay are not read anywhere (rows identical to neutral). Slew and pulse do nothing; the reversal came entirely from belief memory (focus .1: regret 1.69 m / 30% large; focus .95: 2.57 m / 36%).
Two causes, both modelling defects, not Focus effects:
1. Unbounded extrapolation. `Belief.at()` extrapolates a stale belief forever; a long memory keeps stale attackers alive as straight-line phantoms. Fix `ArcherPrism.at_bounded()` (velocity decays with extrap_tau_s = 1.2 s, acceleration term capped at .6 s), flag PRISM_BOUNDED=1 (default OFF, so earlier carrier/Archer results reproduce). Neutral regret 2.21 -> 1.61 m.
2. Free ball position (the main leak). When a defender lost the carrier, the policy fell back on the TRUE ball position, and the ball is in the carrier's hands, so a defender who had lost the carrier was better informed than one who saw him. Fix: for an opposing carrier the defender's ball is his belief about the carrier (bounded, last-known fallback, 0.5% leak when nothing was ever seen), flag PRISM_BALLVIEW (default ON; it only touches defenders). This enforces the PRISM governing rule: no free information.

Result with both fixes (bounded+ball, 5 games per row):
| config | mean regret | large (>2 m) |
|---|---|---|
| neutral | 1.86 m | 31% |
| reaction .1 / .95 | 2.15 / 1.52 | 30 / 23% |
| focus .1 / .95 | 1.63 / 1.97 | 29 / 32% |
| clarity .1 / .95 | 1.98 / 2.04 | 34 / 33% |
| all .1 / all .95 | 1.93 / 1.52 | 30 / 22% |
Reaction and 'all ratings' are now monotone and clean (all: 1.93 -> 1.52 m, 30 -> 22%). The Focus reversal shrank from 0.75 m (1.58 vs 2.33) to 0.34 m (1.63 vs 1.97) but is not gone: a residual of about a third of the Reaction effect, direction unchanged. Open: whether low Focus still gains from a hidden carrier simply dropping out of the policy's player logic, leaving a ball-only rule; test by hiding the carrier from the policy always (ball-only) and comparing.
Files: prism_archer_v0.py (at_bounded), prism_field_v0.py (BOUNDED, BALLVIEW, FOCUS_ONLY diagnostic), sweep_defender_engine.py (SWEEP_SET = focus | bounded), plat_def_focus.json, plat_def_bounded.json, plat_def_ballview.json.

## The real leak: 'hidden' carrier was not hidden (PRISM_CARRIER_BELIEF, default ON)
Ball-only test (PRISM_HIDE_CARRIER=1, carrier removed from the defender's player list, ball at belief): regret fell to ~0.02 m and target error to exactly 0. The defender policy finds the carrier through the ball's carrier id (s.players[s.ball.carrier]), not through the active-player list, so setting active=False left his TRUE position and velocity visible. Every time a defender 'lost' the carrier (confidence below CONF_MIN) he got him back, perfectly. That is what reversed Focus (low memory -> more 'lost' -> more free truth) and why Vision/Awareness looked flat (they only controlled how often the free truth arrived).
Fix: an opposing carrier is never hidden; he is shown at the defender's belief (bounded extrapolation, last-known fallback; 0.5% of views had nothing ever seen and still leak). Same for the ball (PRISM_BALLVIEW).

Results (bounded + ballview + carrier belief; 5 games per row):
| config | mean regret | large (>2 m) |
|---|---|---|
| neutral | 3.26 m | 35% |
| focus .1 / .95 | 3.47 / 2.72 | 36 / 35% |
| reaction .1 / .95 | 3.62 / 2.37 | 36 / 25% |
| vision .1 / .95 | 4.41 / 2.70 | 36 / 35% |
| awareness .1 / .95 | 3.71 / 3.13 | 37 / 37% |
| clarity .1 / .95 | 3.38 / 2.98 | 35 / 36% |
| all .1 / all .95 | 5.76 / 2.56 | 41 / 25% |
Every rating now lowers mean regret when raised, Focus included (the reversal is gone). Mean regret overall is higher than before because the free information is gone. The >2 m tail still moves only with Reaction and with all ratings (25% vs 36-41%), so large mistakes are mostly a staleness (Reaction) story; Vision is the largest single mean effect (4.41 -> 2.70) because a narrow cone loses the carrier for longer.

Consequences: (1) the earlier v0.4 defender sweeps (goals, tackles, 'Vision/Awareness/Clarity flat') ran with this leak and are superseded; (2) any other id-based lookup (engagements, holds, pass targets) may be a similar channel; the carrier-side view hides opponents by active=False and its lane policy reads the opponent list, so it is not affected the same way, but should be audited the same way (ball-only style test) before relying on carrier-side Vision/Awareness results.
Files: prism_field_v0.py (CARRIER_BELIEF, HIDE_CARRIER diagnostic), sweep_defender_engine.py (SWEEP_SET = ballonly | carrierbelief), plat_def_ballonly.json, plat_def_cbelief.json.

## Carrier-side leak audit (PRISM_AUDIT=1) and defender Judgment (PRISM_JUDGE_DEF=1)
**Audit.** A sentinel test inside `with_view`: after the normal call (hidden bodies inactive) the call is repeated with the hidden bodies also moved to (1e6, 1e6); any difference in the policy output means the policy still reads a hidden body. 3 games, ~15,000 views with hidden bodies: 0 differences. With PRISM_CARRIER_BELIEF=0 (the old behaviour) the same test shows 84 differences in one game, so the audit does detect the defender-side leak and the carrier-side views are clean (the carrier's lane and pass policies enumerate opponents through `eligible()`, which respects `active`). Carrier-side Vision/Awareness results stand.

**Defender Judgment.** Defenders in pursuit (true target within PRISM_PURSUIT_R of the believed carrier) choose among n = 2 + round(4J) intercept points along the believed carrier track out to PRISM_JD_L = 2 s, by predicted miss at arrival; Judgment J also sets how fully he charges for prediction uncertainty, J x .5 x PRISM_JD_ALAT (3 m/s^2) x arrival_time^2.
- First attempt (J scales the lookahead: .5 + 1.5 J s, no uncertainty charge) made defenders WORSE with more Judgment (mean regret 2.88 -> 3.57 -> 3.76 m, large-regret share 36 -> 40 -> 44%): carriers turn, so a long lead on a noisy velocity overshoots. Judgment is not 'look further ahead'.
- Second attempt (uncertainty charge; 5 games per row, reaction .5 unless stated), mean regret / >2 m / absolute true miss:
| config | regret | >2 m | miss |
|---|---|---|---|
| aim at carrier (no judgment) | 3.26 | 35% | 12.76 |
| J .1 | 4.81 | 47% | 13.95 |
| J .5 | 4.18 | 42% | 13.46 |
| J .95 | 3.02 | 34% | 12.37 |
| J .1 + reaction .95 | 3.79 | 40% | 12.91 |
| J .95 + reaction .95 | 2.06 | 30% | 10.53 |
| J .1 + reaction .1 | 4.78 | 49% | 13.99 |
| J .95 + reaction .1 | 3.83 | 39% | 12.43 |
Reading: monotone in J now, and J interacts with Reaction (J .95 + R .95 is the best row). But a low-Judgment defender is clearly worse than simply aiming at the carrier (a naive long lead hurts), and a high-Judgment defender only matches simple pursuit on the tail (34% vs 35%) with a modest mean gain (3.02 vs 3.26 m). Caveats: this is the second design after the first failed, so the monotone ordering is partly built in; JD_ALAT = 3 and JD_L = 2 are untuned; 5 games per row. Treat it as 'Judgment can avoid the cost of naive prediction', not as a measured advantage over simple pursuit. Default OFF.
Files: prism_field_v0.py (AUDIT, JUDGE_DEF, JD_L, JD_ALAT), sweep_defender_engine.py (SWEEP_SET = judge), plat_def_judge.json (first attempt), plat_def_judge2.json.

## Defender Judgment v3: Judgment as quality of the choice (PRISM_JUDGE_DEF=1)
Design (DreLen's framing): everyone sees the same menu (intercept points along the believed carrier track, tau 0-2 s in .25 s steps, aim-at-carrier included), scored by predicted miss with the full uncertainty charge (Inference's job). Judgment only sets how reliably the best-scoring option is picked: score noise 3 m x (1-J), held ~.6 s, plus a pull of 3 m x (1-J) to the habitual option (tau 0). Knobs: PRISM_JD_NOISE, PRISM_JD_HABIT (untuned [P]).
**Game-level sweep (10 games per row, plat_def_judge3.json): no usable signal.** Mean regret by J = 0/.1/.3/.5/.7/.95: 3.44/2.79/3.29/3.43/3.71/3.37 m vs 3.21 m aim-at-carrier; row spread (trajectories differ) exceeds any Judgment effect. Reaction still shows (.95: 1.8-2.5 m vs .1: 3.2-3.5 m).
**Paired probe (PRISM_JD_PROBE=1, plat_def_probe.json; game unchanged, every J scored on the same ~8,900 decisions, true miss in m):**
| | aim at carrier | J 0 | J .3 | J .7 | J 1 | best option in menu (hindsight) |
|---|---|---|---|---|---|---|
| reaction .5 | 13.78 | 13.57 | 13.49 | 13.43 | 13.48 | 11.52 |
| reaction .95 | 12.83 | 12.21 | 12.11 | 12.03 | 12.05 | 10.38 |
Reading: choosing by predicted miss beats aiming at the carrier at every J (no low-J penalty any more, the v2 problem is fixed), but the Judgment range is only ~.15 m (about 1%), flat above J .7. The hindsight-best option is ~2 m better, so the missing value is knowing where the carrier will go (prediction/intent: Inference, Anticipation), not picking among options. Far-ahead picks rise with J (36% -> 45%).
Conclusion: pursuit-point choice is a poor home for Judgment; its effect here is real but tiny. Judgment needs decisions with real tradeoffs (commit vs contain, cover vs chase, pass-lane gamble, tackle-commit timing, carrier maneuver choice). This matches the earlier commitThrottle negative result in the lab.
