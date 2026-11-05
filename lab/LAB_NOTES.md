# Maneuver Lab v0.1.1 - notes (31 Oct 2026)
Playable page: maneuver_lab.html (single file, runs offline). Controls: drag = steer; JUKE / SPIN / STIFF / TRUCK; CUT; BRACE (hold = set feet); TOUCH / THROW (pass to the ring marked R); pose chips Loaded..Braced; keys J K L ; = maneuvers, 1-5 poses, T touch, Y throw, Space cut, B brace, R reset, Tab slow-mo.
What is real: pose ladder + maneuver eligibility [C] (verified identical to pose_maneuvers_v0.py on 150 random command streams), locomotion and contact from the chase-lab standards, pose-dependent strip chance, wrap pins the arms. Everything else is [P] and editable in TUNE.
First numbers (score % of 300 runs, scripted carrier, best trigger timing per move; defender weak / default / elite = reaction .2/.6/.95, instinct .2/.5/1.0):
  straight 41/26/6 | cut 100/100/100 | juke 96/80/53 | spin 60/36/6 | stiff-arm 59/46/29 | truck 45/33/14
Reaction x instinct (juke, lead .7): 98 -> 50 across the grid; spin falls to 0 vs elite; truck depends on reaction only.
Start pose cost (default defender, lead .7): juke 80 tucked / 48 loaded or braced; spin 36 / 25 (loaded); stiff-arm 45 / 25 (loaded); truck 33 / 25 (loaded).
Open problems: (1) plain CUT is unbeatable at every defender rating (100%) - the defender AI or the cut standard needs work before any maneuver is tuned against it. (2) Tell windows (0.2 s) are shorter than defender reaction (0.24-0.33 s), so tells are read late. (3) Truck is weak (defender instinct does not change it).

## v0.1.2: cut fix (Oct 31)
Root cause: a wrap cannot stop a ~19 m/s carrier inside its ~1 s hold, so any wrap from behind/fringe ended in ESCAPED and a score. Cut scored 95-100% vs every defender.
Changes [P]: tackle_reach 1.3 m (fringe contact weaker: reach_impulse .7, reach_wrap .5); defender closing technique (breakdown_s, close_throttle); stale-sighting projection; NEW ankle-wrap/trip from behind (trip_p .8, trip_reach_pen .3, speed gain) per the Oct 28 ruling; stiff-arm only holds off on its covered side (stiff_cover_tol) and is a strength x technique contest (stiff_base .6, stiff_k 1); truck_dvd 1.1 / truck_brace 1.15; spin_side_mult .95 (spin is a cliff around 1.0).
Score % (300 fresh seeds, lead .55) weak/mid/elite defender: straight 15/16/14, cut 100/68/52, juke 53/53/48, spin 45/48/47, stiff-arm 58/59/59, truck 60/69/81.
Open: truck rises with defender skill (elite reads tell and tends to collide late); defender ratings barely move stiff-arm/spin/juke (only reaction/instinct feed positioning and tell reading); spin and truck have cliffs at rc~1.

## v0.1.3: defender PRISM layer (switch STD.prism_def, default 0 = v0.1.2 balance)
Defender now has vision, awareness, clarity, focus, anticipation besides reaction/instinct. When on: 10 Hz held picture (perc_dt, delay compensated by perc_comp), cone (Vision) vs radar (Awareness) with Clarity/Awareness-scaled position and velocity noise, focus lapses (freeze), tell seen only inside the cone with Clarity-scaled probability then classified by Instinct, optional turn-rate lead (Anticipation; antic_gain 0 = off).
Sweep (sweep_defender_prism.py, 200 seeds, score %, carrier wins) one rating at .1 / .95 from mid:
- Reaction: cut 99/76, straight 29/21. Clarity: straight 30/17, stiff-arm 72/62. Focus: spin 59/54, stiff 70/63. Instinct: truck 65/76, juke 69/64. All .1 vs all .95: straight 34/16, cut 98/65, truck 68/87.
- Vision, Awareness: flat. Anticipation: flat (turn-rate lead slightly hurts the cut; the cut is over before the extrapolation helps).
Why: in 1v1 the carrier is always ahead (inside the cone), so cone/radar rarely matter, and a cut is decided by timing, not by seeing. Elite defenders commit earlier and can be beaten MORE (non-monotone), so cut defence needs a commit decision (Judgment / intent), not better sight.
With the layer on, a mid defender's cut rises 61 to ~90 (held picture adds staleness variance); needs recalibration before it becomes the default.

## v0.1.4: defender Judgment (commit decision) - negative result
Added defender `judgment` rating (default 0 = unchanged behaviour). Inside breakdown range he scores up to 5 closing-throttle options (count = 1+round(4J)) by expected tackle = p_evade*(1-pMiss from lateral cut shift vs his remaining turn authority) + (1-p_evade)*pOk (closing speed enough to put a straight runner down). Knobs: judge_on, p_evade, j_cut_k, j_hit_r/j_hit_w, j_ok_lo/j_ok_span, j_blend_pow.
Result (sweep_defender_judgment.py, 200 seeds/cell, avg carrier score over 6 moves): J=0/.5/1 -> 53/53/53 with the default blend (per-seed outcomes identical: throttle above ~.45 is a plateau, below it a cliff: close_throttle .2 gives cut 97%), and 71/69/71 with a sharper blend (j_blend_pow 3), i.e. no benefit.
Reading: a 1v1 cut is not beaten by speed management. The throttle model is not what separates defenders; what would is a committed *lane* choice (which side to take away) and intent cues, which need a carrier model with context (team, lanes). So Judgment/Anticipation should be tested in the multi-player field context, as DreLen predicted, not in this 1v1 lab.
