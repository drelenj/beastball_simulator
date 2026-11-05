#!/usr/bin/env python3
"""Beastball Pocket 2.0: finished experimental parameter lab.
Tap Run in Pythonista 3; on a computer run this script with Python 3.10+.
No dependencies, network, downloads or companion files required.
Parameter controls are defined in the final app section; phone edits persist.
Scoring presets and physical assumptions are experiments, not final canon.
See the included guide and change logs for decisions and validation.
"""
# ================= EDIT YOUR PARAMETERS HERE =================
SETTINGS = {'label': 'Beastball Pocket parameter lab',
 'seed': 20260921,
 'matches': 1,
 'period_seconds': 120,
 'periods': 2,
 'overtime_seconds': 30,
 'play_clock': 45,
 'player_speed': 27.0,
 'acceleration': 10.0,
 'braking': 13.5,
 'turning': 13.0,
 'ball_speed': 40.0,
 'pass_speed': 27.0,
 'arrow_speed': 29.0,
 'keeper_zone_radius': 20.0,
 'inner_zone_radius': 15.0,
 'inner_points': 3,
 'release_points': 2,
 'allow_outside_releases': True,
 'outside_points': 1,
 'carry_value': 4,
 'archery': True,
 'adapt_scoring': True,
 'save_events': False,
 'dt_ms': 100,
 'tackles_per_possession': 2,
 'zone_inbound': True,
 'inbound_mark_offset': 8.0,
 'zone_marking': True,
 'marking_distance': 3.0,
 'rating_A': 70,
 'rating_B': 70,
 'rating_spread': 15,
 'field_height': 2.55,
 'field_mass': 230.0,
 'field_reach': 1.173,
 'keeper_height_A': 3.2004,
 'keeper_height_B': 3.2004,
 'keeper_mass_A': 230.0,
 'keeper_mass_B': 230.0,
 'keeper_reach_fraction': 0.46,
 'keeper_speed': 27.0,
 'keeper_acceleration': 10.0,
 'keeper_braking': 13.5,
 'keeper_turning': 13.0,
 'keeper_jump': 1.6,
 'defense_A': 0,
 'defense_B': 0}
# ---- CALIBRATION: physical assumptions of the model ----------------------
# These are NOT sport design choices. They describe how the simulated world
# behaves. Changing one is an experiment and is recorded in every export.
CALIBRATION = {
    # -- carried over from Pocket 1.1 --
    "gravity": 9.81,             # m/s^2
    "ball_drag": 0.015,          # 1/s, exponential speed loss of the ball in flight
    "arrow_drag": 0.06,          # 1/s, exponential speed loss of an arrow in flight
    "catch_noise": 0.15,         # m, aim scatter for shots (passes now use pass_aim_error_deg)
    "tackle_rate": 1.25,         # unitless multiplier on how fast a wrap grounds a carrier
    "block_force": 1.0,          # unitless multiplier on off-ball pushing
    "arrow_error_scale": 1.0,    # unitless multiplier on archer aim error
    "fatigue_rate": 1.0,         # unitless multiplier on tiring
    "body_radius_scale": 1.0,    # unitless multiplier on body size for contact
    "pass_release_ms": 250,      # ms, base time to prepare a pass (shots take longer)
    "grip_delay_ms": 300,        # ms added to pass preparation at full grip
    "bow_draw_ms": 600,          # ms, base time to draw a bow
    "ball_restitution": 0.7745966692,  # bounce: fraction of vertical speed kept
    "frame_thickness": 0.2,      # m, thickness of the goal frame
    # -- C1: passing and catching --
    "ball_mass_kg": 0.4,         # kg, from the rulebook ball specification
    "pass_aim_error_deg": 3.0,   # degrees, one-sigma launch-direction error of a passer with skill 0; scales with (1 - skill)
    "catch_arrest_force_N": 1100.0,  # N, force an average catcher's hands sustain while keeping grip
    "catch_hand_travel_m": 0.6,  # m, distance the hands can give while stopping the ball
    "catch_reaction_s": 0.12,    # s, time constant for seeing a flight and setting the hands
    "deflection_speed_kept": 0.2,   # fraction of relative ball speed kept after an unsecured catch
    # -- C1 mechanism switches: 1 = on, 0 = Pocket 1.1 behaviour (for one-at-a-time comparisons) --
    "c1_pass_planning": 1,       # passes aimed with the real speed, flight time, gravity and drag
    "c1_receiver_routing": 1,    # the intended receiver moves to meet the ball's actual path
    "c1_chasers_read_flight": 1, # loose-ball chasers of both teams read the actual flight
    "c1_catch_model": 1,         # reach / alignment / energy catch model with deflections
    # -- C3a: contact kernel. Every value below is a declared physical hypothesis or a placeholder controller setting.
    #    None is fitted to match totals. See C3a_Coefficients.md for the reasoning and the drill that exercises each. --
    "c3_contact": 1,             # 1 = contact kernel; 0 = the C2m3 contact model, speed offences and speed ceilings included (replay path)
    "c3_substep_ms": 10,         # ms, contact integration step inside each match step (not a tie window)
    "contact_restitution": 0.1,  # unitless, fraction of closing speed returned in a body collision
    "contact_time_s": 0.15,      # s, duration of a body collision, for the ground impulse a braced athlete can take
    "traction_coefficient": 0.8, # unitless, ground friction available for bracing
    "brace_speed_mps": 2.0,      # m/s, an athlete moving slower than this and facing the contact is set to brace
    "shock_speed_mps": 6.0,      # m/s, own velocity change that fully unbalances an athlete of balance 0.5; scales with (0.5 + balance)
    "rearm_gap_m": 0.3,          # m, bodies must separate this far before a new collision shock can occur between them
    "grip_gain_per_s": 4.0,      # 1/s, grip build-up while the hands can reach; scales with (0.5 + tackling), fatigue and alignment
    "grip_resist_per_s": 1.0,    # 1/s, grip loss to the carrier working free; scales with (0.5 + contact resistance)
    "grip_slip_per_s": 2.0,      # 1/s, grip loss when slip equals the reference slip speed
    "grip_slip_ref_mps": 4.0,    # m/s, reference slip (tangential or separating relative speed)
    "grip_overload_per_s": 4.0,  # 1/s, grip loss when the load excess is 1
    "grip_overload_time_s": 0.15,    # s, time over which a hold would have to stop residual slip; defines the load excess
    "grip_force_N": 2500.0,      # N, force a full grip transmits for strength 0.5; scales with (0.5 + strength)
    "topple_time_s": 1.0,        # s, time for a sustained moment equal to the static tipping moment to ground an athlete who does not recover
    "balance_recovery_per_s": 1.5,   # 1/s, recovery rate of balance load for balance 0.5; scales with (0.5 + balance)
    "base_half_width_frac": 0.2, # fraction of height: half-width of the base of support, recovery step included
    "hold_height_upper_frac": 0.7,   # fraction of height at which an upper-torso hold acts
    "hold_height_lower_frac": 0.45,  # fraction of height at which a hip / upper-thigh hold acts
    "lower_hold_leg_factor": 0.6,    # fraction of propulsion and of balance recovery removed by a full lower hold
    "holder_load_factor": 0.35,  # fraction of the reaction that loads the holder's own balance (he chose the hold and is set for it)
    "tackle_grip_threshold": 0.3,    # candidate: grip at or above this, with current lawful engagement, is a materially maintained hold
    "tackle_source_majority": 0.5,   # share of balance load from lawful defensive sources that, with current lawful contact, makes a tackle
    "restraint_weight_matched": 1.0, # restraint weight of a hold on the action it bears on (upper on hand releases, lower on kicks)
    "restraint_weight_other": 0.3,   # restraint weight of a hold on the other kind of action
    "restraint_speed_loss": 0.5, # fraction of launch speed lost at full restraint
    "restraint_error_deg": 8.0,  # degrees, one-sigma launch error added sideways at full restraint (half of it in elevation)
    "collision_risk_tolerance": 0.5, # CONTROLLER, not physics: balance load from a foreseen collision an athlete accepts before he slows
    "contact_foul_min_shock": 0.05,  # LEGAL materiality (C3a2; applied in C3a3 to the athlete's own part): an unlawful body contact he initiated is adjudicated only if the part of the balance load on the other athlete that his own approach supplied is at least this (0 = every touch)
    "c3_prep_round_ms": 0,       # COMPARISON ONLY: 0 = a pass or shot takes its actual preparation time; 100 = round it up to a whole 100 ms as C3a1 and earlier did
    "c3_follow_distance": 1,     # CONTROLLER switch: 1 = an athlete keeps a stopping distance behind an opponent he would otherwise hit from behind; 0 = he does not (comparison only)
    # -- C3b: around the tackle. Declared hypotheses and placeholder controller settings, as above. See C3b_Coefficients.md. --
    "c3b": 1,                    # 1 = C3b behaviour; 0 = the build behaves as accepted C3a3 (comparison and replay)
    "slide_friction": 0.8,       # unitless: a grounded athlete slides and is slowed at this x g. Same value as traction_coefficient by assumption
    "get_up_time_s": 0.8,        # s, time to rise from the ground for an athlete of balance 0.5 once he has stopped sliding; x (1.5 - balance)
    "get_up_max_slide_mps": 1.0, # m/s, he can begin to rise once he is sliding no faster than this
    "descent_time_s": 0.5,       # s, time for a carrier to lower himself to the ground deliberately when nothing holds him up
    "containment_window_s": 2.0, # CONTROLLER, not physics: a holder contains instead of tackling when the carrier's zone time has this long or less to run (0 = never)
    "descent_window_s": 2.0,     # CONTROLLER, not physics: a held carrier tries to go to ground when his zone time has this long or less to run (0 = never)
    "recovery_react": 1,         # CONTROLLER switch: 1 = opponents respond to a first-tackle recovery award after their own reaction time; 0 = at their next decision, as C2
    "exit_protection": 1,        # switch: 1 = an off-ball attacker denied every practicable way out of the zone by opponents' contact does not give up an expiry; 0 = C2 behaviour
    # -- C3c: DreLen's four contact rulings. Every number is a declared hypothesis or a placeholder, not his. See C3c_Coefficients.md. --
    "c3c": 1,                    # 1 = C3c behaviour; 0 = the build behaves as corrected C3b, C3b3 (comparison and replay)
    "arm_pin_grip": 0.5,         # grip of an upper hold at which the arms are fully pinned: restraint on a hand release = min(1, grip / this). 1.0 = the C3a rule
    "tuck_after_delay_frac": 1.0,# HANDLING assumption: a hand wind-up is given up, and the ball tucked, once holds have cost it this fraction of its own unrestrained length. 0 = never
    "strip_in_motion_factor": 4.0, # the retained strip rate is multiplied by 1 + (this - 1) x pin while an upper hold pins the arms during a hand wind-up. 1.0 = no change
    "c3_region_policy": 1,       # CONTROLLER policy: 1 = a defender also takes the upper region against a carrier with a pass open; 0 = only once a wind-up is visible, as C3a; 2 (C4a) = also when the carrier is inside the zone he defends
    "blindside_rear_half_angle_deg": 15.0, # degrees either side of straight behind inside which a hit is from behind. EXPERIMENTAL reading of DreLen's ruling; the canon angle is his. 75.52 = the retained Pocket 1.1 line
    "escape_force_N": 2500.0,    # N, force a carrier of strength 0.5 and balance 0.5 can pry at a hold with, at full effort and no balance load. Same value as grip_force_N by assumption. 0 = no escape work
    # -- C4.0: Keeper Zone violations as ruled by DreLen on 7 October. Terminal processing is corrected unconditionally and has no switch. --
    "c4_zone": 1,                # 1 = the ruling: no personal sanction for a zone expiry; defensive first violation of a possession resets the tackle count, second is a penalty run. 0 = the C3c2 consequences (comparison and replay)
    "zone_direct_penalty": 0,    # EXPERIMENTAL PROPOSAL, NOT CANON, off: 1 = a defender over his allowance and unmarked who controls or plays the ball, or blocks a shot, gives away a penalty run at once
    # -- C4a: contact carry-forwards. Controller and experimental-design settings, not fitted to anything. See C4a_Mechanism_Submission.md. --
    "escape_allocation": 1,      # how a held carrier's ONE prying effort is shared among the holds on him: 1 = equally (default); 2 = all on the weakest as he feels it (lowest grip); 3 = all on the weakest by the holder's real strength (perfect information, drills only); 0 = full effort on every hold (C4.0r2)
    "contact_roster": 0,         # 0 = every athlete 0.68 (uniform control, default); 1 = mixed and mirrored, starters balanced, rotated by seed (C4b); 2 = team A 0.90 against team B 0.30; 3 = the reverse; 4 = the C4a mixed design as delivered (reproduction only)
    # -- C4b: support-foot scoring origin (DreLen's ruling) and the gait model that places the feet. Declared hypotheses, not fitted. --
    "c4b": 1,                    # 1 = scoring origin from the support foot, and the Carry rules; 0 = pelvis origin as C4a (comparison and replay)
    "gait_step_base_frac": 0.25, # step length at walking pace, as a fraction of height
    "gait_step_per_mps_frac": 0.035, # added to the step length per m/s of speed, as a fraction of height
    "gait_step_max_frac": 1.1,   # longest step, as a fraction of height
    "gait_duty_rest": 0.62,      # share of a stride each foot is down, at rest (above 0.5: double support)
    "gait_duty_per_mps": 0.03,   # taken off that share per m/s of speed
    "gait_duty_min": 0.22,       # least share at speed (below 0.5: a flight phase)
    "gait_half_width_frac": 0.09,# each foot's distance to the side of the line of travel, as a fraction of height
    "gait_still_mps": 0.5,       # m/s, slower than this both feet are down beside the pelvis
    "gait_reset_frac": 0.75,     # a planted foot further than this x height from the pelvis is put back under him (a placement, not a step)
    # -- C4c: Keeper mechanics (build specification 7). Declared hypotheses, not fitted. --
    "c4c": 1,                    # 1 = the C4c Keeper (reaction limit, planned step, jump or dive, body, parry, landing and get-up, positioning); 0 = the C4b Keeper
    "keeper_depth_frac": 0.25,   # positioning: off his line by this fraction of the ball's distance from the centre of his goal
    "keeper_depth_min_m": 1.0,   # ... but at least this far
    "keeper_depth_max_m": 4.0,   # ... and at most this far
    "keeper_reaction_s": 0.2,    # s from a ball's change of course until he can act on it, x (1.3 - 0.6 x awareness)
    "keeper_unset_s": 0.1,       # s added if he was moving faster than keeper_set_mps at that instant
    "keeper_set_mps": 1.5,       # m/s, at or below this he is set
    "keeper_pushoff_frac": 0.4,  # horizontal launch: up to sqrt(2 x acceleration x this x height)
    "keeper_extension_frac": 0.3,# hands go out along a full dive by this x height
    "keeper_dive_hand_frac": 0.3,# hand height at full lean, x height (0.62 upright)
    "keeper_dive_lean": 0.35,    # a launch with at least this lean is a dive (he lands on the ground)
    "keeper_launch_min_s": 0.1,  # s, a launch cannot meet the ball sooner than this after he decides (time to leave the ground)
    "keeper_parry_restitution": 0.35, # an unsecured hand contact: rebound of the normal component of the ball's relative velocity
    "keeper_body_restitution": 0.3,   # the same off his body
    "keeper_attempt_margin_m": 1.5,   # with nothing reachable he still launches at the nearest point if it is within his reach plus this
    "keeper_dive_time_s": 0.25,  # he stays on his feet, running towards the meeting point, until this long before it, then launches
    "keeper_aim_frac": 0.5,      # a launch aims to bring his hands within this fraction of their reach of the ball (0.9 at worst)
    "keeper_parry_swing_mps": 5.0,    # m/s, in a deliberate parry the hand is driven into the ball along the contact normal
    "keeper_windup_set": 1,      # 1 = he stops and sets when a carrier within 35 m begins a wind-up
    "keeper_confront": 1,        # 1 = he goes to meet an opposing carrier at his goal mouth
    "keeper_confront_m": 7.0,    # ... within this distance of the centre of his goal
    "keeper_gather_m": 6.0,      # a slow loose ball within this distance of him, in his own Keeper Zone: he goes to gather it
    # -- C4c2: the C4c1 audit corrections and DreLen's scoring rulings of 9 October --
    "c4c2": 1,                   # 1 = body contacts keep recovery, body proposals revalidated, the offensive origin kept through defensive touches, arcs in the farther territory; 0 = C4c1
    "reversal_rule": 0,          # OPEN: a team's own flight redirected into its own goal by an opponent. 0 = own-goal value; 1 = valued from the redirecting opponent's foot
    # -- C4c2: the common controller (build specification 7). Its success estimates are the drill tables embedded in the program, not these. --
    "controller": 1,             # 1 = the common controller (shot, carry, pass or carry on, by expected points from drill estimates); 0 = the inherited controllers
    "ctrl_lookahead_s": 0.6,     # s, how far ahead "carry on" looks (one step: the same choices from where he would be)
    "ctrl_style_A": 0,           # team A approach: 0 = balanced (the best estimate), 1 = carry-heavy, 2 = pass-heavy
    "ctrl_style_B": 0,           # team B approach, the same
    "ctrl_style_band": 0.1,      # a styled team takes its preferred choice when it is within this fraction of the best
    "ctrl_receivers": 2,         # attacking players sent to the open spots that are worth most to a receiver
    "ctrl_short_inbound": 1,     # 1 = an inbound has a short option and an entry option, coordinated with the taker
    "ctrl_keeper": 1,            # 1 = the Keeper confronts a carrier when the estimates say that concedes less than staying
    "keeper_height_m": 0.0,      # 0 = the inherited 2.55 m Keeper; else 2.7432 to 3.6576 m (DreLen's 9 to 12 ft), family H (reach 0.46 x height)
}
# Declared range for every C3 coefficient: (low, high, basis). These are the ranges within which each hypothesis is thought
# plausible and should be varied when its sensitivity is examined. They are declarations, not results, and nothing enforces them.
C3_RANGES = {
    "c3_substep_ms": (5, 20, "numerical setting; 5, 10 and 20 are compared in the drills"),
    "contact_restitution": (0.0, 0.3, "soft-body impact: mostly inelastic"),
    "contact_time_s": (0.05, 0.3, "duration of a body impact"),
    "traction_coefficient": (0.5, 1.2, "studded footwear on turf"),
    "brace_speed_mps": (1.0, 4.0, "from set to jogging"),
    "shock_speed_mps": (4.0, 10.0, "velocity change that fully unbalances an average athlete"),
    "rearm_gap_m": (0.1, 0.6, "separation that ends one contact episode"),
    "grip_gain_per_s": (2.0, 8.0, "a secure hold in roughly 0.2 to 0.8 s unopposed"),
    "grip_resist_per_s": (0.5, 2.0, "carrier working free, relative to gain"),
    "grip_slip_per_s": (1.0, 4.0, "loss at the reference slip speed"),
    "grip_slip_ref_mps": (2.0, 8.0, "relative speed at which a hold is hard to keep"),
    "grip_overload_per_s": (2.0, 8.0, "loss when the hold is asked for more than it can transmit"),
    "grip_overload_time_s": (0.05, 0.3, "time scale over which a hold must stop residual slip"),
    "grip_force_N": (1500.0, 4000.0, "force a full two-arm hold transmits; 6 to 16 times body weight is not claimed, only bracketed"),
    "topple_time_s": (0.5, 2.0, "time to go down under a sustained tipping moment without recovering"),
    "balance_recovery_per_s": (0.75, 3.0, "one recovery step every 0.3 to 1.3 s"),
    "base_half_width_frac": (0.15, 0.3, "half stance width with a recovery step, as a fraction of height"),
    "hold_height_upper_frac": (0.6, 0.8, "chest to shoulder"),
    "hold_height_lower_frac": (0.35, 0.55, "upper thigh to hip"),
    "lower_hold_leg_factor": (0.3, 0.9, "how far a full leg hold removes drive and stepping"),
    "holder_load_factor": (0.2, 0.6, "share of the reaction that unbalances a holder who is set for it"),
    "tackle_grip_threshold": (0.2, 0.5, "candidate: what counts as a materially maintained hold"),
    "tackle_source_majority": (0.5, 0.75, "majority of the load from lawful defensive causes"),
    "restraint_weight_matched": (0.7, 1.0, "a hold on the limbs the action uses"),
    "restraint_weight_other": (0.1, 0.5, "a hold elsewhere on the body"),
    "restraint_speed_loss": (0.25, 0.75, "launch speed lost under full restraint"),
    "restraint_error_deg": (4.0, 16.0, "launch error under full restraint"),
    "collision_risk_tolerance": (0.25, 1.0, "controller: balance load an athlete accepts from a foreseen incidental collision"),
    "contact_foul_min_shock": (0.0, 0.2, "legal materiality: balance load below which a touch is not a hit"),
    "c3_prep_round_ms": (0, 100, "comparison setting: 0 or 100 only"),
    "c3_follow_distance": (0, 1, "controller switch: 0 or 1"),
    "c3b": (0, 1, "switch: 0 or 1"),
    "slide_friction": (0.4, 1.2, "body sliding and tumbling on turf"),
    "get_up_time_s": (0.4, 1.5, "rising from the ground; 0.8 s was the fixed inherited value"),
    "get_up_max_slide_mps": (0.0, 3.0, "speed at which an athlete can get his feet under him"),
    "descent_time_s": (0.3, 1.0, "going to ground deliberately"),
    "containment_window_s": (0.0, 5.0, "controller: 0 = never contain, 5 = always in the zone"),
    "descent_window_s": (0.0, 5.0, "controller: 0 = never go to ground, 5 = always in the zone when held"),
    "recovery_react": (0, 1, "controller switch: 0 or 1"),
    "exit_protection": (0, 1, "switch: 0 or 1"),
    "c3c": (0, 1, "switch: 0 or 1"),
    "arm_pin_grip": (0.3, 1.0, "grip of a high wrap that pins the arms completely; 0.3 is the material-hold threshold, 1.0 the C3a rule"),
    "tuck_after_delay_frac": (0.5, 2.0, "handling: how long a carrier persists with a stalled wind-up, in wind-up lengths"),
    "strip_in_motion_factor": (1.0, 8.0, "how much less secure the ball is in a pinned throwing motion; no evidence"),
    "c3_region_policy": (0, 2, "controller policy: 0 wind-up seen only, 1 also a pass open (C3c), 2 also inside the defended zone (C4a)"),
    "blindside_rear_half_angle_deg": (10.0, 45.0, "geometric reading of 'directly behind'; DreLen owns the canon value"),
    "escape_force_N": (1500.0, 4000.0, "prying force; bracketed like grip_force_N, which it is set equal to"),
    "c4_zone": (0, 1, "switch: 0 or 1"),
    "zone_direct_penalty": (0, 1, "experimental switch: 0 or 1; a proposal awaiting DreLen's ruling"),
    "escape_allocation": (0, 3, "named policy: 0 full on every hold (C4.0r2), 1 equal shares, 2 weakest as felt, 3 weakest in truth (drills only)"),
    "contact_roster": (0, 4, "named design: 0 uniform, 1 mixed mirrored balanced and rotated, 2 A strong B weak, 3 A weak B strong, 4 the C4a mixed design"),
    "c4b": (0, 1, "switch: 0 or 1"),
    "gait_step_base_frac": (0.15, 0.35, "walking step: 0.4 to 0.9 m for a 2.55 m athlete"),
    "gait_step_per_mps_frac": (0.02, 0.05, "step lengthening with speed"),
    "gait_step_max_frac": (0.8, 1.4, "longest sprinting step"),
    "gait_duty_rest": (0.55, 0.7, "walking duty factor"),
    "gait_duty_per_mps": (0.015, 0.05, "fall of the duty factor with speed"),
    "gait_duty_min": (0.15, 0.35, "sprinting duty factor"),
    "gait_half_width_frac": (0.05, 0.15, "stance half-width"),
    "gait_still_mps": (0.2, 1.0, "speed below which he stands"),
    "gait_reset_frac": (0.5, 1.2, "placement threshold"),
    "c4c": (0, 1, "switch: 0 or 1"),
    "keeper_depth_frac": (0.0, 0.5, "how far off his line"),
    "keeper_depth_min_m": (0.5, 3.0, "least depth"),
    "keeper_depth_max_m": (1.0, 8.0, "greatest depth"),
    "keeper_reaction_s": (0.1, 0.35, "response time to a ball's change of course"),
    "keeper_unset_s": (0.0, 0.25, "penalty for moving at the instant"),
    "keeper_set_mps": (0.5, 3.0, "set threshold"),
    "keeper_pushoff_frac": (0.2, 0.6, "dive push-off length"),
    "keeper_extension_frac": (0.15, 0.45, "arm extension in a dive"),
    "keeper_dive_hand_frac": (0.15, 0.45, "hand height at full lean"),
    "keeper_dive_lean": (0.2, 0.6, "dive threshold"),
    "keeper_launch_min_s": (0.05, 0.2, "time to leave the ground"),
    "keeper_parry_restitution": (0.1, 0.6, "hand rebound"),
    "keeper_body_restitution": (0.1, 0.6, "body rebound"),
    "keeper_attempt_margin_m": (0.0, 3.0, "desperation margin"),
    "keeper_dive_time_s": (0.15, 0.5, "time in the air before the meeting"),
    "keeper_aim_frac": (0.2, 0.9, "how squarely he aims his hands"),
    "keeper_parry_swing_mps": (0.0, 10.0, "hand speed into a parry"),
    "keeper_windup_set": (0, 1, "switch: 0 or 1"),
    "keeper_confront": (0, 1, "switch: 0 or 1"),
    "keeper_confront_m": (3.0, 20.0, "confrontation distance"),
    "keeper_gather_m": (0.0, 15.0, "loose-ball gathering distance"),
    "c4c2": (0, 1, "switch: 0 or 1"),
    "reversal_rule": (0, 1, "open rule: 0 or 1"),
    "controller": (0, 1, "switch: 0 or 1"),
    "ctrl_lookahead_s": (0.2, 1.5, "carry-on look-ahead"),
    "ctrl_style_A": (0, 2, "approach: 0, 1 or 2"),
    "ctrl_style_B": (0, 2, "approach: 0, 1 or 2"),
    "ctrl_style_band": (0.0, 0.3, "style tolerance"),
    "ctrl_receivers": (0, 4, "receivers sent to open spots"),
    "ctrl_short_inbound": (0, 1, "switch: 0 or 1"),
    "ctrl_keeper": (0, 1, "switch: 0 or 1"),
    "keeper_height_m": (0.0, 3.6576, "0 = inherited, else 2.7432 to 3.6576 m"),
}
# ============================================================
import sys, types, json, math, hashlib, time, copy, gzip, statistics
from pathlib import Path
VERSION = "Beastball-Pocket-Next-C4c2"
CHECKPOINT = "C4c2 submission (not yet accepted, no campaign run): accepted-in-development C4c1 plus the body-contact recovery correction, body revalidation at commitment, the scoring rulings of 9 October (offensive origin kept through defensive touches; arcs in the farther territory) and the common controller. M1.6.1"
SOURCE_HASHES = {'geometry': '0524ba4d29c739aefaf8ea63559297121046331e50b451b54b7d5a831de41bc8', 'types': 'cde795cbf4b4fdf5721bed23edcd3491ccba23e04bb329e5291db47828a739cd', 'engine': 'db3e423abad30b671f2baa38e131288e0f68d14ecc9e908ad52505b25d3475e9', 'policies': 'd66263707da8abbc7029a56ad2856850124ef0aa8c2a54e9c08c8c503121bbbe', 'match': 'b0a6681246d55607e0a603372fe794ce7a23660adc3d8c44b17ff9434f15db97'}
NOTES = [
 "Experimental parameter lab; not canon, not competitive-balance proof.",
 "Embedded spatial/rules core from Working Rules 1.0.1; full main build unchanged.",
 "Two identical average rosters: 22 each; 10 field players, Keeper, Archer active; 10 reserves.",
 "Pocket-S4: three release territories replace attacking carry goals. Keeper and inner radii are configurable; boundary lines belong to the deeper territory.",
 "Pocket-S1 origin: last deliberate release/strike/touch; incidental deflections retain origin. Own goals use release_points. Penalty releases use release_points regardless of origin.",
 "Pocket-S2: selected ball/arrow speeds also change their experimental legal caps; higher arrow energy is a model experiment, NOT equipment certification.",
 "Pocket-S3: fresh possession and foul clock floors respect selected play_clock; short fixed special timers remain source rules.",
 "Pocket-P2: radial shooting-distance threshold and close carrier targets respond to territory values when adapt_scoring=True; tactics are heuristic, not optimized.",
 "Keeper Zone radius also changes occupancy, keeper protection, and restart placement. Inner zone changes scoring only. Controlled attacking crossings do not score; own goals and penalties use release_points.",
 "Omitted from phone workflow: full campaigns, charts, replay UI, source rulebook; spatial/contact/archery engine is retained.",
 "Tested on desktop Python; no physical iPhone or Pythonista runtime available for certification.",
 "C1 change 1: restart passes and strikes get the same 1e-6 ball-speed tolerance open-play releases already had.",
 "C1 change 2: passes, kicks to a receiver and restart passes are aimed with the real release speed, flight time, gravity and drag. An unreachable receiver is replaced by the next option; if none is reachable the pass is not thrown.",
 "C1 change 3: pass aim error is an angle (pass_aim_error_deg x (1 - skill)), replacing a fixed small scatter at the target. Shot aim is unchanged.",
 "C1 change 4: the intended receiver moves to meet the ball's actual path. He picks the reachable point needing the least change of course, judged from his present motion, and runs through it on time. Loose-ball chasers of both teams read the actual flight instead of a fixed 0.4 s extrapolation.",
 "C1 change 5 (revision 2): a ball within reach is not thereby touched. The ball and the player's hands are swept together through each step. A player gets his hands to a reachable ball only once he has read its course (elapsed time since the release, last deflection or bounce); otherwise it passes untouched. A set player meets the ball at its closest approach, at that time and point. Whether he secures it depends on the ball's energy relative to his hands against their capacity. An established contact that is not secured deflects the ball; a Keeper's is a parry. This also governs the Keeper's catches.",
 "C1 revision 2: only the earliest contact in a step is acted on. Two secure contacts count as simultaneous (joint control between opponents) only if they fall in the same millisecond of the match clock. Cooldowns and block counts are applied when a contact event is committed, never when it is proposed.",
 "C1 has no body-contact model: a ball that no hand plays passes a player's body, as in Pocket 1.1.",
 "C1 revision 3: a proposed contact is checked again when it is committed. If the player can no longer make it (frozen, grounded, excluded, off the field, play stopped), nothing happens and the log records contact_rejected. After a deflection or a frame rebound inside a step, the rest of that step is resolved at once, including goals and boundaries. A player's reading of a flight counts all the time since it began, even if the ball starts within his reach.",
 "C1 change 6: under the new catch model a player is judged where he is at the moment of contact; a player outside the field at that instant does not play the ball.",
 "C2: a first counted tackle keeps possession (count one); a second gives the ball to the opponents. Outside the attacked Keeper Zone the first tackle is followed by a live recovery: the ball stays where it was, opponents' bodies must leave a one-metre disc, and the team has three live seconds to pick it up, with no protection after pickup.",
 "C2: a first tackle inside the attacked Keeper Zone gives a goal-line inbound from a mark 8 m from the goal centre, with three-metre clearance. No goal counts in that aperture until an attacker standing in the field outside the zone controls or deliberately plays the ball.",
 "C2: Keeper Zone occupancy. The team in possession has five seconds; leaving across the arc inside the field resets the count; leaving over the end line pauses it and re-entry does not reset it. Defenders may stay while within marking distance of an eligible attacker; otherwise five seconds, then a technical foul. A change of possession clears every count.",
 "C2 limits: off-ball exit-route protection is NOT modelled (possible cases are only logged, and attacking-expiry totals carry that limitation); get-up time is the Pocket 1.1 fixed 0.8 s; ball placement after a tackle is immediate; who recovers the ball, who takes the inbound, where it is thrown and how players use the zone are placeholder controllers; players do not block each other during a recovery (the old contact model only runs with a ball carrier). With the old contact model few tackles complete at the delivered tackle rate, so continuation is rarely exercised in matches until C3.",
 "C2 caution: under the new occupancy rule the placeholder controllers let attackers go deeper into the zone and score more than in C1. That is a rule and a controller acting together and has not been separated or validated; no campaign has been run on this build.",
 "C4c2 (decided by DreLen, 9 October): a shot or pass that goes into the opponents goal stays an offensive goal through defensive touches, a failed save included, and its value comes from the last attacking player to touch it. A foot on the Keeper Zone arc is an outside release; a foot on the inner arc is a zone release. A flight turned into its own goal by an opponent is still an open question (reversal_rule).",
 "C4c (ours, experimental): the Keeper reacts to a ball's change of course after a declared response time, reads its flight from what he sees, and meets it on his feet or with a jump or dive within his push-off and jump limits. His body blocks, his hands catch or parry, and after a dive he is down for a moment. These are hypotheses for drills, not calibrated values.",
 "C4b (decided by DreLen): the scoring origin of a release is the support foot. Both feet down: the one nearer the goal he attacks; one down: that one; in the air: the last foot that was down. Each foot stays where it was planted until it is lifted.",
 "C4b (ours, experimental): the feet come from a simple declared gait model (step length and the share of each stride a foot is down both change with speed). It is a hypothesis, compared against the pelvis in every match record.",
 "C4b: a Carry, secure control before the whole ball crosses, can score in configurations B and C (carry_value above 0). The six configurations of the build specification are in SCORING_CONFIGURATIONS. The controllers do not yet choose between carrying and releasing: that is C4c.",
 "C4a (ours, experimental): a held carrier has one prying effort, shared among the holds on him; equal shares by default, or all of it on the hold he feels weakest. With one holder nothing changes.",
 "C4a: rosters can vary strength, balance and tackling (a mixed, mirrored design, or a strong team against a weak one), so that a strong carrier can meet a weak holder. The default is still every athlete at 0.68.",
 "C4a: where a defender takes hold is a named controller policy: high only once he sees a wind-up, also when a pass is open (default), or also when the carrier is inside the zone he defends.",
 "C4.0 (decided by DreLen, 7 October): a team does not forfeit off Keeper Zone violations. An attacking expiry is a turnover. A defensive violation, the first of a possession, returns the tackle count to zero; the second is a penalty run. Defenders caught at the same moment are one violation. No warning or exclusion is given for either kind of expiry: that last part is our reading, not yet confirmed by him.",
 "C4.0 (ours, experimental): 'the same moment' is the same millisecond; expiries a millisecond apart are two violations. A called defender gets one period to leave or regain marking, worked out from his position and speed; still there unmarked after it is a new violation. The first violation also raises the possession clock to at least 20 s, and the usual three-second advantage is played.",
 "C4.0 proposal, off: a direct penalty run when a defender over his allowance and unmarked controls or plays the ball or blocks a shot (zone_direct_penalty). It is DreLen's to rule on.",
 "C4.0: a finished match is committed once. Exactly one match_complete, at most one forfeit, and nothing changes the result, score, clocks, statistics or record afterwards. Sanctions queued for one stoppage are all administered before any ground to end the match is judged; both teams below the minimum together is an abandonment, not a forfeit. A horn that decides the match gives no exemption.",
 "C4.0 r2: a defender marked, or out of the zone, at the instant he plays the ball is judged as he is then. The compliance time is worked out on the motion the kernel allows him, tired or fresh. An attacking expiry and a defensive violation at the same millisecond are judged together (rulebook 15.5): a first defensive violation offsets, a second is a penalty run.",
 "C4.0 limits: defenders' controllers are unchanged, so they do not yet play to the higher price of a second violation; an attack can still strand defenders by leaving together. Neither has been measured. No campaign has been run on this build.",
 "C3a: contact is physical. Bodies collide with one equal and opposite impulse; a fast collision loads balance instead of being a foul. Grip starts at zero, builds only while the hands can reach a carrier in control, and is lost to slip and overload. A hold transmits force up to its grip capacity; that force, through its height on the body, loads the carrier's balance, and he is grounded when the load reaches 1. Any athlete can be grounded, the tackler included.",
 "C3a: a grounding is a counted tackle only if the carrier was in control and a lawful defensive engagement was present at that instant: a hold at or above the grip threshold, or lawful defensive causes making up the majority of the load together with current lawful contact. Otherwise it is the existing forced release.",
 "C3a: a hold slows a pass or shot in preparation, lowers the launch speed available and adds launch error, by region and action. Wrap entitlement, grip, coupling and drive end the instant the carrier loses control.",
 "C3a2: order of events. Motion and contact run to the first event the rules must act on (a grounding, a strip, a foul, a completed pass or shot, a catch, an arrow hit, a goal) and stop there; that event is committed and play continues from the committed state. A collision is resolved at the instant the bodies touch, reach at the instants it begins and ends, both solved on the path actually travelled. The clock is in whole milliseconds, so 'at' means within one millisecond.",
 "C3a2: a pass or shot now takes its actual preparation time. It was rounded up to a whole 100 ms before; set c3_prep_round_ms to 100 to compare.",
 "C3a2: legality on real collisions. At each body collision the script records who ran into whom. An athlete who ran into an opponent from behind (blindside), or into a protected carrier, is penalised under the existing rule, unless the contact was unavoidable (see C3a3). Both athletes take the physical consequences whoever is at fault. There is no speed offence.",
 "C3a3: responsibility for a collision. An athlete initiated a contact if his own motion carried him into the other at all; supplying the smaller part of the closing speed does not excuse him. Separately, the part of the hit his own motion supplied must put at least contact_foul_min_shock of balance load on the other athlete to be adjudicated. Carried by another contact: only the velocity that other athletes' forces actually put on him, towards the man he hit, and that he had not had his reaction time and braking to take off, is not his; holding or being held, or having been hit, is not an excuse by itself. No time to avoid: only where his contact had been lawful and that changed (the man turned his back, lost the ball, became protected) when the gap was already shorter than his reaction and braking distance; being out of reach is not a lawful approach.",
 "C3a2 not simulated, so never penalised by the kernel: contact to the head, neck, spine, groin or joints, and with claws, horns or weapons (bodies are discs, there is no anatomy); contact with a frozen, grounded, airborne, excluded or off-field athlete (they are not solid bodies yet); contact between team-mates; holding a player without the ball (a hold cannot form on one, and ends the instant control is lost).",
 "C3b: going down. A grounded athlete keeps the velocity he had and slides, slowed by ground friction; he can begin to rise once he is sliding slower than 1 m/s, and rising takes 0.8 s x (1.5 - balance). The instant he is upright is known when he goes down and an interval ends exactly then. The tackle no longer stops the carrier dead.",
 "C3b: containment and descent. A holder may hold the carrier up without driving him down (a controller choice, made when a tackle would only be the attack's first and the carrier's zone time is about to run out). A held carrier may try to go to ground; containing holders carry as much of his weight as their grip can, and he goes down only as fast as what is left allows. Going down under a material hold is a counted tackle, logged as his descent.",
 "C3b: first-tackle recovery. Every defender with a material hold at the grounding has time to disengage, not only the credited tackler. Opponents respond to the award after their own reaction time. Bodies are solid during the recovery: blocking away from the disc is legal, running into a man in the disc is not. What was necessary, what each took and what was his own delay are logged.",
 "C3b: off-ball exit. An attacker without the ball who had time to leave the zone, was run into by an opponent while he still had it, and had no practicable route at any check afterwards does not give up an expiry; the opponent has obstructed him. No way out counts as practicable if it needs more than the zone time he has left. The zone time that ran while he was denied is given back, and the opponent to whom most of it is put down is penalised. A standing screen is legal. Every attacking expiry is logged with its class.",
 "C3b: the record kept for a pending advantage follows a slot through exclusion or injury and its refilling. A substitute's walk to the gate covers distance by elapsed time. A record of velocity imposed on an athlete is never larger than the velocity he still has.",
 "C3b limits: ground friction, get-up time and descent time are hypotheses with no evidence behind them; the containment and descent choices are placeholder controllers; a grounded athlete is still not a solid body and cannot be held or blocked; a holder who supports a descending carrier pays no balance cost for it; exit routes are straight lines tested against where opponents stand, once per interval; there is still no body contact during a second-tackle (turnover) award.",
 "C3c (decided by DreLen, numbers ours): a high wrap pins the arms. An upper hold restrains a pass or shot by grip / 0.5, complete at grip 0.5; a lower hold does not pin whatever its grip. A carrier whose wind-up has been held up for as long as the wind-up itself takes gives it up and tucks the ball, and with his arms pinned he does not begin one. While his arms are pinned in a wind-up the retained strip chance is higher, by up to 4 times at full pin; there is no new fumble.",
 "C3c (decided by DreLen, numbers ours): only a hit from directly behind is from behind. The experimental reading is 15 degrees either side of straight behind; the canon angle is his to set (blindside_rear_half_angle_deg). The same line is used for legality and for the controller that keeps a stopping distance. Collisions are unchanged: mass and velocity decide who goes down. Centre of gravity and stance are NOT modelled.",
 "C3c (decided by DreLen, numbers ours): a held carrier who is not winding up works to free himself. His prying force grows with his strength and balance, falls as his balance is loaded, and is set against the holder's grip force; it loosens the grip continuously. Prying beyond the holder's full grip force tears the grip away as well; if that outruns the rate at which the holder can re-close his hands, the grip runs down to zero and the hold is off. He may reach again after his reaction time, for a new hold from nothing. There is no escape by timer. Whether he gets free before he is brought down is the contest.",
 "C3c limits: the pin threshold, the tuck time, the strip factor, the rear angle and the prying force have no evidence behind them; working free costs the carrier nothing but the use of his arms; the defender's choice of a high or low hold and the carrier's choice to work free are placeholder controllers.",
 "C3a limits: every contact coefficient is a hypothesis that evidence does not yet support; the drills report predictions, not validation; get-up is still the fixed 0.8 s; there is no contact during a recovery, no containment choice and no controlled descent (C3b); frozen, grounded and airborne athletes are still not solid bodies; team-mates do not collide; reach is one planar distance for both hold regions, not a model of the arms. The tackle_rate setting now does nothing unless c3_contact is 0.",
 "C3a: the Pocket 1.1 strip chance is kept unchanged as an inherited hypothesis, converted to a rate so that it does not depend on the contact substep.",
 "C1: the four mechanisms can be switched off one at a time in CALIBRATION. With all four off, play equals C0-speedfix.",
 "The measurement layer (M1.3) only reads the finished event log. Measures the legacy log cannot support are reported as unavailable, not zero.",
 "Results are reproducible on one runtime. One phone run and one desktop run of the same seed were observed to diverge after 38 events, so a phone result and a desktop result may be compared statistically, not event by event.",
]
CORE_SOURCES = {
    'geometry': r'''"""Metres; exact geometry is separate from motion assumptions."""
import math

def clamp(v,a,b):return max(a,min(b,v))
def norm(x,y):return math.hypot(x,y)
def unit(x,y):
 d=norm(x,y);return (x/d,y/d)if d>1e-9 else(0.,0.)
def distance(a,b):return norm(a.x-b.x,a.y-b.y)
def goal_x(team):return 100. if team=='A'else 0.
def own_goal_x(team):return 0. if team=='A'else 100.
def attack_sign(team):return 1 if team=='A'else-1

def restart_point(x,y,radius=20):
 x,y=clamp(x,5,95),clamp(y,5,95)
 for gx in (0.,100.):
  d=norm(x-gx,y-50)
  if d<=radius:x,y=gx+(x-gx)*(radius+.5)/d,50+(y-50)*(radius+.5)/d
 return x,y

def zone(x,y,radius=20):
 if 0<=x<=100 and 0<=y<=100:
  if norm(x,y-50)<=radius:return 0
  if norm(x-100,y-50)<=radius:return 1
 return None

def segment_distance(px,py,ax,ay,bx,by):
 dx,dy=bx-ax,by-ay;l=dx*dx+dy*dy
 t=clamp(((px-ax)*dx+(py-ay)*dy)/l,0,1)if l else 0
 return norm(px-ax-t*dx,py-ay-t*dy),t

def segment3_distance(point,a,b):
 d=tuple(b[i]-a[i]for i in range(3));l=sum(x*x for x in d)
 t=clamp(sum((point[i]-a[i])*d[i]for i in range(3))/l,0,1)if l else 0
 return math.sqrt(sum((point[i]-a[i]-t*d[i])**2 for i in range(3))),t

def legal_goal(y,z,r=.1075):
 #The ball's entire circular section must fit the semicircle above the surface.
 return z>=r-1e-7 and norm(y-50,z)+r<=6+1e-7

def ballistic(origin,target,speed,g=9.81,high=False):
 dx,dy=target[0]-origin[0],target[1]-origin[1];d=norm(dx,dy);dz=target[2]-origin[2]
 if d<.01:return(0.,0.,speed),max(.01,abs(dz)/speed)
 disc=speed**4-g*(g*d*d+2*dz*speed*speed)
 if disc<0:return None
 theta=math.atan((speed*speed+(1 if high else-1)*math.sqrt(disc))/(g*d))
 h=speed*math.cos(theta);ux,uy=unit(dx,dy)
 return(h*ux,h*uy,speed*math.sin(theta)),d/h

def ball_at(b,t,g=9.81,k=.015):
 """Where a free ball will be t seconds ahead: gravity plus linear drag, before any bounce."""
 if k<1e-9:return(b.x+b.vx*t,b.y+b.vy*t,b.z+b.vz*t-.5*g*t*t)
 e=1-math.exp(-k*t)
 return(b.x+b.vx*e/k,b.y+b.vy*e/k,b.z+(b.vz+g/k)*e/k-g*t/k)

def launch_for(origin,target,speed,g=9.81,k=.015):
 """Launch velocity of exactly the given speed whose flatter arc passes through target, with drag.
 Returns (velocity, flight_time), or None when the target is out of range at that speed."""
 dx,dy=target[0]-origin[0],target[1]-origin[1];d=norm(dx,dy);dz=target[2]-origin[2]
 if d<.05 or speed<=0:return None
 ux,uy=unit(dx,dy)
 def miss(theta):
  vh=speed*math.cos(theta);vz=speed*math.sin(theta)
  if k<1e-9:t=d/vh;return vz*t-.5*g*t*t-dz,t
  q=1-k*d/vh
  if q<=0:return None,None
  t=-math.log(q)/k;e=1-math.exp(-k*t)
  return(vz+g/k)*e/k-g*t/k-dz,t
 lo,hi=-1.2,math.pi/4
 elo,_=miss(lo);ehi,_=miss(hi)
 if ehi is None or ehi<0 or elo is None or elo>0:return None
 for _ in range(48):
  mid=(lo+hi)/2;em,_=miss(mid)
  if em is None or em<0:lo=mid
  else:hi=mid
 theta=(lo+hi)/2;_,t=miss(theta)
 vh=speed*math.cos(theta)
 return(vh*ux,vh*uy,speed*math.sin(theta)),t

def predict_path(b,g=9.81,k=.015,restitution=.7745966692,horizon=3.0,step=.05):
 """Sampled future path of a free ball, using the same flight, bounce and roll rules as the match itself.
 Returns [(t,x,y,z)], ending where the ball leaves the field. Cached on the ball for the current state."""
 key=(b.x,b.y,b.z,b.vx,b.vy,b.vz)
 cache=getattr(b,'_path_cache',None)
 if cache and cache[0]==key:return cache[1]
 x,y,z,vx,vy,vz=key;t=0.;drag=math.exp(-k*step);path=[(0.,x,y,z)]
 while t<horizon:
  x+=vx*step;y+=vy*step;z+=vz*step-.5*g*step*step;vx*=drag;vy*=drag;vz=(vz-g*step)*drag
  if z<=b.radius:
   z=b.radius
   if abs(vz)>2:vz=-vz*restitution;vx*=.76;vy*=.76
   else:vz=0;vx*=max(0,1-step*3);vy*=max(0,1-step*3)
  t+=step;path.append((t,x,y,z))
  if not(-1<=x<=101 and -1<=y<=101):break
 b._path_cache=(key,path);return path

def intercept_xy(p,path,reach=1.0,earliest=True):
 """Where player p should run to meet a ball, read from its predicted path.
 A point is playable when the ball is within reach of the hands, or low enough to scoop.
 Reachability starts from the player's present motion: by time t he can be anywhere within
 1/2 x acceleration x t^2 of where his current velocity would carry him, and no further than top speed allows.
 earliest=True: the first playable point he can reach (cutting the ball off).
 earliest=False: within the first stretch of the path he can reach, the point needing the least change of course (receiving it).
 Falls back to the playable point he misses by least, then to the end of the path.
 For the receiver (earliest=False) the returned target is placed along the line to the meeting point at the braking distance of the
 speed needed to cover the distance in the time left, allowing for the time it takes to build that
 speed. The mover's own speed law then holds that speed, so the player
 arrives when the ball does and runs through it, instead of sprinting early or slowing to a stop."""
 hand=p.z+.62*p.a.height;vmax=p.a.maximum_speed*.88;a=p.a.acceleration;pick=None;least=1e9;best=None;slackbest=1e9;at=None;bi=None
 for i,(t,x,y,z) in enumerate(path):
  if not(0<=x<=100 and 0<=y<=100):break
  ok=False
  if abs(z-hand)<=reach or z<.4:
   d=norm(x-p.x,y-p.y);dev=norm(x-p.x-p.vx*t,y-p.y-p.vy*t);room=.5*a*t*t+.2*reach
   if dev<=room and d-.2*reach<=vmax*t:
    ok=True
    if earliest:pick=(t,x,y);break
    if dev<least:least=dev;pick=(t,x,y);at=i
   elif max(dev-room,d-.2*reach-vmax*t)<slackbest:slackbest=max(dev-room,d-.2*reach-vmax*t);best=(t,x,y);bi=i
  if pick and not ok:break #only the first stretch of the path he can reach is considered; he does not wait for a later one
 if not earliest and at is None and pick is None and bi is not None:
  #No point is comfortably reachable: he goes for the one he misses by least, refined the same way.
  at=bi;pick=best;least=norm(best[1]-p.x-p.vx*best[0],best[2]-p.y-p.vy*best[0])
 if not earliest and at is not None:
  #The path is sampled; between the samples next to the chosen one, take the instant at which continuing on course comes closest.
  for j in(at-1,at):
   if j<0 or j+1>=len(path):continue
   (t0,x0,y0,_),(t1,x1,y1,_)=path[j],path[j+1]
   if not(0<=x0<=100 and 0<=y0<=100 and 0<=x1<=100 and 0<=y1<=100):continue
   ax,ay=x0-p.x-p.vx*t0,y0-p.y-p.vy*t0;bx,by=x1-p.x-p.vx*t1-ax,y1-p.y-p.vy*t1-ay;l=bx*bx+by*by
   u=clamp(-(ax*bx+ay*by)/l,0,1)if l>1e-12 else 0.;dev=norm(ax+u*bx,ay+u*by)
   if dev<least:least=dev;pick=(t0+u*(t1-t0),x0+u*(x1-x0),y0+u*(y1-y0))
 t,x,y=pick or best or path[-1][:3]
 d=norm(x-p.x,y-p.y)
 if not earliest and d>1e-6 and t>1e-6: #the receiver is re-routed every step, so he can be paced; a chaser simply goes to the point
  ux,uy=(x-p.x)/d,(y-p.y)/d;v0=p.vx*ux+p.vy*uy;short=d-v0*t
  if short<=0:v=d/t #already quick enough: ease to the speed that arrives on time
  else:
   disc=a*a*t*t-2*a*short #speed to build, at acceleration a, so that the distance is covered in time t
   v=v0+a*t-math.sqrt(disc)if disc>=0 else vmax
  v=clamp(v,0.,vmax);lead=max(v*v/(2*p.a.braking),min(d,.3));x=p.x+ux*lead;y=p.y+uy*lead
 return(clamp(x,.5,99.5),clamp(y,.5,99.5))

def travel_time(d,a,v):
 #One-dimensional reach estimate, explicitly a policy approximation.
 threshold=v*v/(2*a)
 return math.sqrt(2*d/a)if d<=threshold else v/a+(d-threshold)/v

def disk_path_blocked(a,b,players,extra=.2,exclude=()):
 return any(p.id not in exclude and segment_distance(p.x,p.y,*a,*b)[0]<p.radius+extra for p in players)
''',
    'types': r'''from dataclasses import dataclass,field,asdict
from enum import Enum
from .geometry import clamp

class Phase(str,Enum):
 OPENING='opening';LIVE='live';DEAD='dead';AWARD='award';FLIGHT='finishing_flight';PENALTY='penalty';BREAK='break';REVIEW='review';SHOOTOUT='shootout';SUSPENDED='suspended';FINAL='final'
class BallMode(str,Enum):
 CONTROLLED='carried';LOOSE='loose';PASS='passed';KICK='kicked';SHOT='shot';DEAD='dead';OUT='out';CONTESTED='contested'

@dataclass
class Attributes:
 height:float=2.45
 mass:float=220
 reach:float=1.18
 strength:float=.65
 acceleration:float=9
 maximum_speed:float=25
 braking:float=12
 turning:float=12
 agility:float=.65
 endurance:float=.7
 balance:float=.65
 contact_resistance:float=.65
 tackling:float=.65
 blocking:float=.65
 ball_handling:float=.65
 passing:float=.65
 kicking:float=.6
 catching:float=.65
 awareness:float=.65
 decision_speed:float=.3
 archery_accuracy:float=.7
 archery_release_speed:float=28
 keeper_skill:float=.7
 jump_height:float=1.3
 def validate(self):
  assert 1.4<=self.height<=3.6576
  assert 0<self.maximum_speed<=44.704
  assert self.mass>0 and self.acceleration>0 and self.braking>0
  for k in ['strength','agility','endurance','balance','contact_resistance','tackling','blocking','ball_handling','passing','kicking','catching','awareness','archery_accuracy','keeper_skill']:
   assert 0<=getattr(self,k)<=1,(k,getattr(self,k))

@dataclass
class Player:
 id:str
 team:str
 role:str='field'
 active:bool=True
 a:Attributes=field(default_factory=Attributes)
 x:float=50
 y:float=50
 z:float=0
 vx:float=0
 vy:float=0
 vz:float=0
 facing:tuple=(1.,0.)
 posture:str='upright'
 available:bool=True
 injured:bool=False
 disqualified:bool=False
 freeze_until:int=-1
 immune_until:int=-1
 exclusion_ms:int=0
 minor_count:int=0
 major_count:int=0
 zone_ms:list=field(default_factory=lambda:[0,0])
 outside_ms:list=field(default_factory=lambda:[3000,3000])
 keeper_hold_ms:int=0
 keeper_outside_ms:int=3000
 unmarked_ms:list=field(default_factory=lambda:[0,0])   #C2: defender's unmarked allowance used, per zone
 zone_loc:list=field(default_factory=lambda:[None,None]) #C2: last observed 'in' / 'out' (in field, outside zone) / 'off' (outside field), per zone
 zone_fouled:list=field(default_factory=lambda:[0,0])   #C2: live time after which an unmarked expiry may be called again; 0 = none pending
 tackled_until:int=-1                                    #C2: recognised tackle-ground recovery; occupancy pauses until then
 fatigue:float=1
 next_decision:int=0
 next_action:int=0
 target:tuple=(50.,50.)
 slot:int=0
 @property
 def radius(self):return clamp(.30+self.a.mass*.00065,.38,.82)
 @property
 def speed(self):return (self.vx*self.vx+self.vy*self.vy)**.5
 @property
 def hand_height(self):return self.z+.62*self.a.height
 def eligible(self,t):return self.active and self.available and not self.injured and not self.disqualified and self.exclusion_ms<=0 and t>=self.freeze_until
 def frozen(self,t):return t<self.freeze_until

@dataclass
class Ball:
 version:int=0
 mode:BallMode=BallMode.DEAD
 x:float=50
 y:float=50
 z:float=.1075
 vx:float=0
 vy:float=0
 vz:float=0
 carrier:str|None=None
 control_time:int=-1
 last_touch:str|None=None
 last_releaser:str|None=None
 scoring:bool=False
 release_time:int=-1
 intended:str|None=None
 contested:tuple=()
 radius:float=.1075

@dataclass
class Arrow:
 id:int
 team:str
 shooter:str
 target:str|None
 x:float
 y:float
 z:float
 vx:float
 vy:float
 vz:float
 origin:tuple
 release_time:int
 live:bool=True
 first_impact:bool=True
 spent:bool=True

@dataclass
class Quiver:
 allocation:int=20
 spent:int=0
 loaded:int=5
 reload_until:int=-1
 last_release:int=-999999

@dataclass
class Restart:
 team:str
 x:float
 y:float
 reason:str
 ready_at:int|None=None
 taker:str|None=None
 created_at:int=0
 kind:str='free_pass'      #C2: 'inbound' (goal-line inbound) or 'recovery' (restored first-tackle recovery)
 clearance:float=5.        #m, opponents' distance from the restart spot
 remaining:int=3000        #ms of recovery granted when a restored recovery resumes
 taker_spot:tuple|None=None
 note:str=''

@dataclass
class Engagement:
 actor:str
 target:str
 kind:str
 started:int
 progress:float=0

@dataclass
class Event:
 kind:str
 actor:str|None=None
 target:str|None=None
 data:dict=field(default_factory=dict)
 at:int|None=None

@dataclass
class MatchState:
 now:int=0
 period:int=1
 game_ms:int=600000
 possession_ms:int=45000
 owner:str|None=None
 phase:Phase=Phase.DEAD
 score:dict=field(default_factory=lambda:{'A':0,'B':0})
 ball:Ball=field(default_factory=Ball)
 players:dict=field(default_factory=dict)
 quivers:dict=field(default_factory=lambda:{'A':Quiver(),'B':Quiver()})
 arrows:list=field(default_factory=list)
 restart:Restart|None=None
 engagements:dict=field(default_factory=dict)
 alternate:str='A'
 opening_team:str|None=None
 opening_failures:int=0
 opening_deadline:int|None=None
 opening_touched:bool=False
 opening_contestants:tuple=('A0','B0')
 hunt_choice_team:str='B'
 ends:dict=field(default_factory=lambda:{'A':0,'B':100})
 award_spot:tuple|None=None
 award_available:int|None=None
 award_deadline:int|None=None
 tail_until:int|None=None
 tail_owner:str|None=None
 contested_until:int|None=None
 advantage:dict|None=None
 penalty:dict|None=None
 extension:bool=False
 extension_team:str|None=None
 suspended_at:int|None=None
 result:dict|None=None
 warning:dict=field(default_factory=lambda:{'A':set(),'B':set()})
 timeouts:dict=field(default_factory=lambda:{'A':2,'B':2})
 review:dict|None=None
 challenges:dict=field(default_factory=lambda:{'A':1,'B':1})
 shootout:dict|None=None
 stoppages:int=0
 tackle_count:int=0             #C2: counted tackles in the current possession (C4.0: in the current set; a zone violation can return it to zero)
 zone_violations:int=0          #C4.0: defensive Keeper Zone violations called against the team defending this possession, both zones together
 tackle_ordinal:int=0           #C4.0: counted tackles in this possession whatever the count has been reset to
 reconstruction:dict|None=None  #C2: {'team','zone','live_since'} while the attacked zone must be cleared
 recovery:dict|None=None        #C2: first-tackle live recovery in progress
 live_ms:int=0
 dead_ms:int=0
 last_score_cause:int|None=None
 period_seconds:int=600
 keeper_zone_radius:float=20
 regulation_periods:int=4
 overtime_seconds:int=300
 def other(self,t):return 'B'if t=='A'else'A'
 def attack_sign(self,t):return 1 if self.ends[t]==0 else-1
 def attack_goal(self,t):return 100-self.ends[t]
 def own_zone(self,t):return 0 if self.ends[t]==0 else 1
 def active(self,team=None):return[p for p in self.players.values()if p.active and(team is None or p.team==team)]
''',
    'engine': r'''"""Deterministic legal state transitions. Stochastic execution belongs in match.py.
All official time is integer milliseconds. Events at an identical time are grouped.
"""
import math,hashlib,json
from dataclasses import asdict
from .types import *
from .geometry import norm,zone,restart_point,legal_goal,clamp

RULES={'acquire':'1.5–1.9;5.2','pass':'4.4–4.5','tackle':'6.4–6.7','freeze':'7.1–7.4','boundary':'9.1;10.1–10.6','goal':'9.1–9.3;16.2','foul':'11;12;15','restart':'10.2–10.5','clock':'5;16.6','sub':'14.1–14.3','opening':'4.1–4.3','period':'18.1–18.4'}
class RulesError(Exception):pass
class MatchFinal(BaseException):
 """C4.0: raised by Engine.complete once the result is committed. It unwinds every engine call in progress, so that no line
 after the commitment runs. It is caught at the outermost engine call (see the guard at the end of this file) and never
 reaches the caller. It is not an error and is not an Exception, so no handler meant for errors can swallow it part-way."""

class Engine:
 def __init__(self,state=None,config=None):
  self.s=state or MatchState();self.config=config or {};self.log=[];self.event_seq=0
  if self.config.get('ruleset','1.0.1')not in('1.0.1','1.0.2'):raise RulesError('Unknown ruleset; source behavior must not be silently selected')
  self.pending_discipline=[];self.debts=[];self.cause=None;self.last_progress=None
  self.review_snapshot=None;self.score_history=[];self.next_arrow=1
  self.pocket=self.config.get("pocket",{});self.play_ms=int(self.pocket.get("play_clock",45)*1000)
  self.s.keeper_zone_radius=self.pocket.get("keeper_zone_radius",20)
  self.period_history=[];self.opening_ref_ms=0;self.metrics={}
  self.c3=bool(self.config.get('assumptions',{}).get('c3_contact',0)) #C3a: contact kernel. Off = the C2m3 engine, speed offences included.
  self.c3b=False;self.assume={};self.grace=[] #C3b: the Match sets c3b and the merged assumptions straight after construction
  self.c3c=False;self.blind_cos=.25 #C3c: the Match sets these. blind_cos is the cosine of the half-angle of the rear cone; 0.25 is the retained Pocket 1.1 line
  #C2 rule options. With all three off the engine behaves as C1 revision 3.
  self.c2_tackles=int(self.pocket.get('tackles_per_possession',1))>=2;self.c2_inbound=bool(self.pocket.get('zone_inbound',False))
  self.vacated={'A':[],'B':[]};self.vacated_keep={'A':[],'B':[]};self.c2_occ=bool(self.pocket.get('zone_marking',False));self.c2_any=self.c2_tackles or self.c2_inbound or self.c2_occ;self.mark_d=float(self.pocket.get('marking_distance',3.));self.mark_off=float(self.pocket.get('inbound_mark_offset',8.))
  #C4.0 terminal processing. final_seq is the id of the record that committed the result; final_refused counts what was asked
  #of the engine afterwards and refused. terminal_grounds holds grounds for ending the match raised while several sanctions of
  #one stoppage are being administered (terminal_hold), so that they are judged together and not in the order of a loop.
  self.final_seq=None;self.final_refused={};self.depth=0;self.terminal_hold=0;self.terminal_grounds=[]
  #C4.0 Keeper Zone ruling. The Match sets these from CALIBRATION. c4_zone: no personal sanction for a zone expiry.
  #c4_occ: the defensive consequences (needs zone marking). zone_direct: the proposed direct penalty, experimental, off.
  self.c4_zone=False;self.c4_occ=False;self.zone_direct=False
  self.c4b=False #C4b: the Match sets it
  self.c4c=False #C4c: the Match sets it
  self.c4c2=False;self.reversal_rule=0 #C4c2: the Match sets them
 def count(self,key,n=1):
  cs=getattr(self,'contact_stats',None)
  if cs is not None:cs[key]+=n
 def zone(self,x,y):
  return zone(x,y,self.s.keeper_zone_radius)
 def territory(self,team,x,y):
  if not(0<=x<=100 and 0<=y<=100):return 'outside_release'
  d=norm(x-self.s.attack_goal(team),y-50)
  if self.c4c2:
   #C4c2, decided by DreLen on 9 October: a line belongs to the farther scoring territory. On the inner arc: a zone release; on the
   #Keeper Zone arc: an outside release. (This supersedes the specification's deeper-territory convention.) The end line is not
   #settled by this ruling: the field test above and the eligibility rule are kept as they were.
   if d<self.pocket.get('inner_zone_radius',5):return 'inner_release'
   if d<self.s.keeper_zone_radius:return 'inside_release'
   return 'outside_release'
  if d<=self.pocket.get('inner_zone_radius',5):return 'inner_release'
  if d<=self.s.keeper_zone_radius:return 'inside_release'
  return 'outside_release'
 def territory_points(self,method):
  return self.pocket.get({'inner_release':'inner_points','inside_release':'release_points','outside_release':'outside_points'}[method],3)
 def emit(self,event,rule,**data):
  if self.final_seq is not None:
   #C4.0: the log of a completed match is closed. This is a backstop; the engine's own paths do not reach it.
   self.final_refused['emit:'+event]=self.final_refused.get('emit:'+event,0)+1;return self.event_seq
  s=self.s;self.event_seq+=1
  rec={'id':self.event_seq,'live_ms':s.live_ms,'t_ms':s.now,'period':s.period,'g_ms':s.game_ms,'p_ms':s.possession_ms,'phase':s.phase.value,'owner':s.owner,'carrier':s.ball.carrier,'ball_mode':s.ball.mode.value,'ball':[round(s.ball.x,3),round(s.ball.y,3),round(s.ball.z,3)],'score':dict(s.score),'event':event,'rule':rule,'cause':self.cause,'data':data}
  self.log.append(rec);return self.event_seq
 def eligible(self,p,ball_action=True):
  if not p.eligible(self.s.now):return False
  if p.role=='archer':return not ball_action
  if p.posture!='airborne'and not(0<=p.x<=100 and 0<=p.y<=100):return False
  if self.s.penalty is not None and p.id not in (self.s.penalty['runner'],self.s.penalty['keeper']):return False
  if self.s.phase==Phase.FLIGHT and p.team==self.s.tail_owner:return False
  return True
 def live(self):return self.s.phase in (Phase.LIVE,Phase.AWARD,Phase.OPENING)
 def new_owner(self,team,reason):
  s=self.s
  changed=s.owner!=team
  if changed:
   s.award_spot=None;s.award_available=None;s.award_deadline=None
   previous=s.owner;s.owner=team;s.possession_ms=self.play_ms
   self.emit('possession_change','1.6;5.2',previous=previous,team=team,reason=reason)
   self.c2_new_possession(previous,team,reason)
  if s.opening_team is None:
   s.opening_team=team;s.alternate=s.other(team)
  return changed
 def c2_new_possession(self,previous,team,reason):
  """C2: a new team possession. Tackle count returns to zero, reconstruction and any first-tackle recovery end,
  and every stored zone count and unmarked allowance is cleared for both teams."""
  s=self.s;s.tackle_count=0;s.zone_violations=0;s.tackle_ordinal=0 #C4.0: the defensive zone-violation counter and the tackle ordinal belong to the possession
  if s.recovery:self.emit('recovery_failed','C2-3.1',reason=reason);s.recovery=None
  if s.reconstruction:self.end_reconstruction('goal'if reason=='goal'else'opposing_possession')
  if self.c2_occ:
   stored=0;adv=s.advantage
   if adv and'c2'in adv and adv['team']==previous and'keep'not in adv['c2']:
    #The advantaged team has lost the ball inside its advantage. Keep what is about to be cleared, in case the advantage is recalled.
    adv['c2']['keep']={p.id:(list(p.zone_ms),list(p.unmarked_ms),list(p.zone_fouled))for p in s.players.values()}
    if self.c3b:
     #C3b: a slot left empty by an exclusion or injury has state waiting for whoever fills it. That is part of what is about to be cleared.
     for tm in('A','B'):
      for i,st in enumerate(self.vacated[tm]):
       if self.vacated_keep[tm][i]is None:self.vacated_keep[tm][i]=(adv['c2']['keep'],tuple(list(x)for x in st))
   if self.c3b:self.vacated={tm:[([0,0],[0,0],[0,0])for _ in self.vacated[tm]]for tm in('A','B')} #the waiting slots stay (their kept record needs them); their counts are cleared
   else:self.vacated={'A':[],'B':[]}
   for p in s.players.values():
    if p.zone_ms[0]or p.zone_ms[1]or p.unmarked_ms[0]or p.unmarked_ms[1]:stored+=1
    if self.c4_occ:
     for j in(0,1):
      if p.zone_fouled[j]:self.emit('zone_compliance','C4.0-zone',player=p.id,zone=j,how='possession_ended',ms_before_deadline=p.zone_fouled[j]-s.live_ms)
    p.zone_ms=[0,0];p.unmarked_ms=[0,0];p.zone_fouled=[0,0]
   self.emit('occupancy_cleared','C2-5',team=team,previous=previous,reason=reason,players_with_stored_time=stored)
 def end_reconstruction(self,reason):
  s=self.s;r=s.reconstruction;s.reconstruction=None
  self.emit('reconstruction_ended','C2-4.2',team=r['team'],zone=r['zone'],reason=reason,live_ms_uncleared=s.live_ms-r['live_since'])
 def slot_inherit(self,o,n):
  """C2: n takes over o's slot: stored zone counts, unmarked allowance, pending violation and any record kept for a pending
  advantage. No arc exit is invented: the newcomer's location is observed afresh."""
  n.zone_ms=list(o.zone_ms);n.unmarked_ms=list(o.unmarked_ms);n.zone_fouled=list(o.zone_fouled);n.zone_loc=[None,None]
  keep=self.s.advantage['c2'].get('keep')if self.s.advantage and'c2'in self.s.advantage else None
  if keep and o.id in keep:keep[n.id]=keep.pop(o.id)
 def slot_vacate(self,p):
  #A field slot emptied by exclusion or injury: its state waits for whoever fills the slot.
  if self.c2_occ:
   self.vacated[p.team].append((list(p.zone_ms),list(p.unmarked_ms),list(p.zone_fouled)))
   #C3b: any record kept for a pending advantage leaves with the slot, not with the excluded or injured athlete
   keep=self.s.advantage['c2'].get('keep')if self.c3b and self.s.advantage and'c2'in self.s.advantage else None
   self.vacated_keep[p.team].append((keep,keep.pop(p.id))if keep and p.id in keep else None)
   if self.c3b:p.zone_ms=[0,0];p.unmarked_ms=[0,0];p.zone_fouled=[0,0] #the state belongs to the slot now; the athlete who has left it carries none
 def slot_fill(self,n):
  if not self.c2_occ:return
  v=self.vacated[n.team];st=v.pop(0)if v else([0,0],[0,0],[0,0])
  n.zone_ms,n.unmarked_ms,n.zone_fouled=[list(x)for x in st];n.zone_loc=[None,None]
  vk=self.vacated_keep[n.team];kept=vk.pop(0)if vk else None
  keep=self.s.advantage['c2'].get('keep')if self.s.advantage and'c2'in self.s.advantage else None
  if kept is not None and keep is not None and kept[0]is keep:keep[n.id]=tuple(list(x)for x in kept[1]) #C3b: the newcomer holds the slot's kept record while that advantage is pending
 def c2_snapshot(self):
  #C2: the continuation state at a foul instant, kept with an advantage so that a failed advantage restores it.
  s=self.s
  return{'count':s.tackle_count,'recon':dict(s.reconstruction)if s.reconstruction else None,'zone_violations':s.zone_violations,'ordinal':s.tackle_ordinal} #C4.0: the violation counter and tackle ordinal are part of the foul instant
 def c2_restore(self,adv,changed,cause):
  """C2: a failed advantage returns play to the foul instant: tackle count and reconstruction. Zone counts follow what the
  players actually did. If possession did not change hands they were never cleared and are left alone. If it did, the counts
  held when the advantaged team lost the ball are returned (adv['c2']['keep']), less any lawful in-field arc exit made since,
  which occupancy() removes from that record as it happens. An end-line exit removes nothing. The record follows the slot
  through substitution and specialist replacement."""
  snap=adv.get('c2');s=self.s
  if not snap:return
  was=s.tackle_count;s.tackle_count=snap['count']
  if was!=snap['count']:self.emit('tackle_count_restored','C2-5',count_from=was,count_to=snap['count'],cause=cause)
  s.zone_violations=snap.get('zone_violations',0);s.tackle_ordinal=snap.get('ordinal',0) #C4.0: a violation called at or before the foul instant is still on the count after a recall; its remedy is not given twice
  if s.reconstruction and not snap['recon']:self.end_reconstruction('advantage_restored')
  elif snap['recon']and not s.reconstruction:s.reconstruction=dict(snap['recon']);self.emit('reconstruction_restored','C2-4.2',team=snap['recon']['team'],zone=snap['recon']['zone'],cause=cause)
  keep=snap.get('keep')
  if self.c2_occ and keep is not None:
   #A kept record exists only because a turnover inside the advantage cleared the counts. It is given back whoever holds the ball
   #at the recall, including when the advantaged team has won it back (A to B to A): that second change cleared the counts again.
   for p in s.players.values():
    if p.id in keep:p.zone_ms,p.unmarked_ms,p.zone_fouled=[list(v)for v in keep[p.id]]
   for tm in('A','B'):
    for i,kept in enumerate(self.vacated_keep[tm]):
     #C3b: a slot still empty at the recall gets its kept state back, to be handed to whoever fills it
     if kept is not None and kept[0]is keep:self.vacated[tm][i]=tuple(list(x)for x in kept[1]);self.vacated_keep[tm][i]=None;self.emit('vacant_slot_state_returned','C3b-9',team=tm,zone_ms=list(kept[1][0]),unmarked_ms=list(kept[1][1]))
  if changed:
   if not s.extension:s.possession_ms=min(self.play_ms,max(20000,adv['p'])) #the restored clock with the defensive-foul floor, not a fresh clock
  self.emit('advantage_state_restored','C2-5',cause=cause,tackle_count=s.tackle_count,possession_changed_during_advantage=changed,zone_counts_returned=keep is not None,p_ms=s.possession_ms,**({'zone_violations':s.zone_violations}if self.c4_occ else{}))
 def reconstruction_check(self,p,witness):
  """C2: reconstruction clears on live eligible attacking play by a player whose pelvis is inside the field and
  strictly outside the attacked zone. The ball need not have left the zone."""
  s=self.s;r=s.reconstruction
  if not r or p.team!=r['team']or not self.eligible(p)or p.posture=='grounded':return False
  if not(0<=p.x<=100 and 0<=p.y<=100)or self.zone(p.x,p.y)==r['zone']:return False
  s.reconstruction=None;self.count('reconstructions_cleared')
  self.emit('reconstruction_cleared','C2-4.2',player=p.id,witness=witness,pelvis=[round(p.x,3),round(p.y,3)],live_ms_uncleared=s.live_ms-r['live_since']);return True
 def begin_hunt(self):
  s=self.s;s.phase=Phase.OPENING;s.owner=None;s.possession_ms=self.play_ms;s.ball=Ball(mode=BallMode.LOOSE,x=50,y=50,z=.1075,scoring=False)
  s.opening_touched=False;s.opening_deadline=s.now+10000
  for team,pid in zip(('A','B'),s.opening_contestants):
   p=s.players[pid];p.x=42 if team=='A'else 58;p.y=50;p.vx=p.vy=0
  self.emit('opening_ground_touch','4.2',contestants=s.opening_contestants)
 def failed_hunt(self,reason):
  s=self.s;s.opening_failures+=1
  if s.opening_failures>=2:
   team=s.other(s.hunt_choice_team);self.award(team,50,50,'opening_fallback');s.opening_deadline=None
  else:self.begin_hunt()
  self.emit('opening_failed','4.3',reason=reason,count=s.opening_failures)
 def acquire(self,pid,forced_joint=False):
  s=self.s;p=s.players[pid];b=s.ball
  if s.phase==Phase.FLIGHT:
   if p.team!=s.tail_owner and self.eligible(p):self.end_flight('defensive_control',p.x,p.y)
   else:self.end_flight('offensive_touch',p.x,p.y)
   return True
  if not self.live()and s.phase!=Phase.PENALTY:return False
  if not self.eligible(p):self.illegal(pid,'ineligible_ball_action');return False
  if p.role=='archer':self.illegal(pid,'archer_body_ball');return False
  if b.carrier is not None:return b.carrier==pid
  if b.last_releaser==pid:self.illegal(pid,'self_recontact');return False
  if s.phase==Phase.AWARD and p.team!=s.owner:self.illegal(pid,'exclusive_recovery');return False
  if s.phase==Phase.PENALTY and pid==s.penalty['keeper']:
   self.emit('penalty_save','12.4',player=pid);self.finish_penalty(0);return True
  if s.extension and s.owner is not None and p.team!=s.extension_team:
   self.emit('extension_turnover','16.6',player=pid);self.end_period();return True
  if s.phase==Phase.OPENING and not s.opening_touched and pid not in s.opening_contestants:
   self.illegal(pid,'premature_opening');return False
  ox,oy=(p.c4c_launch['off'][0],p.c4c_launch['off'][1])if self.c4c and getattr(p,'c4c_launch',None)else(0.,0.) #C4c: at full stretch in a dive his hands are out along it
  if math.hypot(b.x-p.x-ox,b.y-p.y-oy)>p.a.reach+p.radius+.2 or not(p.z-.2<=b.z<=p.z+p.a.height+p.a.reach):return False
  if s.recovery and p.posture=='grounded':return False #C2: a grounded player, the tackled carrier included, recovers the ball only after becoming upright
  if self.c4_occ and p.team!=s.owner and self.zone_intervention(p,'control'):return False
  self.new_owner(p.team,'control');s.phase=Phase.LIVE if s.phase!=Phase.PENALTY else Phase.PENALTY
  b.version+=1;b.mode=BallMode.CONTROLLED;b.carrier=pid;b.control_time=s.now;b.scoring=True;b.last_touch=p.team;b.last_releaser=None;b.contested=();s.contested_until=None
  if self.c4c2:b.pocket_release_team=p.team;b.c4c2_def=[];b.c4c2_off=pid;b.c4c2_off_i=0 #C4c2: secured control ends the old flight; his team owns whatever follows
  s.opening_deadline=None;s.opening_touched=True;s.award_deadline=None
  self.follow_carrier();self.emit('control','1.5;5.2',player=pid)
  if s.recovery:
   #C2: pickup ends first-tackle protection at once. No post-pickup immunity.
   self.emit('recovery_pickup','C2-3.1',player=pid,elapsed_ms=s.now-s.recovery['started'],replacement=bool(s.recovery.get('replacement')));s.recovery=None;s.award_spot=None;s.award_available=None
  self.reconstruction_check(p,'secure_control')
  if p.posture=='grounded':self.grounded(pid)
  return True
 def c1_reason(self,event):
  """C1: why a proposed contact cannot be accepted at this instant, or None. The same conditions the kernel
  applied when it proposed the contact, tested again against the state at the moment of commitment."""
  s=self.s;b=s.ball;p=s.players[event.actor]
  if b.carrier is not None:return'ball_controlled'
  if b.mode==BallMode.CONTESTED:return'ball_contested'
  if s.phase not in(Phase.LIVE,Phase.OPENING,Phase.AWARD,Phase.FLIGHT,Phase.PENALTY):return'play_stopped'
  if event.data.get('c4c_kind')=='body':
   if not self.c4c2:return None #C4c: the ball meeting the Keeper's body is physics, not a play: no eligibility test
   #C4c2: the body is passive (grounded, frozen, in a recovery: it still stops the ball), but it must still be on the field and
   #taking part in this phase: the same participation tests the kernel applied when it proposed the contact.
   if not p.active:return'not_available'
   if s.penalty is not None and p.id not in(s.penalty['runner'],s.penalty['keeper']):return'not_a_penalty_participant'
   if s.phase==Phase.FLIGHT and p.team==s.tail_owner:return'finishing_flight'
   if s.phase==Phase.OPENING and not s.opening_touched and p.id not in s.opening_contestants:return'premature_opening'
   if s.phase==Phase.AWARD and p.team!=s.owner:return'exclusive_recovery'
   if b.last_releaser==p.id:return'own_release'
   return None
  if not p.eligible(s.now):return'frozen'if p.active and p.frozen(s.now)else'not_available'
  if not self.eligible(p):return'not_eligible_here'
  if p.posture=='grounded':return'grounded'
  if s.now<p.next_action:return'cooldown'
  if b.last_releaser==p.id:return'own_release'
  if s.phase==Phase.AWARD and p.team!=s.owner:return'exclusive_recovery'
  if s.phase==Phase.OPENING and not s.opening_touched and p.id not in s.opening_contestants:return'premature_opening'
  return None
 def c1_reject(self,event,why):
  self.emit('contact_rejected','assumption:c1_contact',player=event.actor,kind=event.kind,reason=why)
  cs=getattr(self,'contact_stats',None)
  if cs is not None:cs['contacts_rejected']+=1
  return False
 def c1_commit(self,event):
  """C1: commit a proposed contact. Returns True only if the action was accepted. Ball position, velocity,
  observation reset, resume flag, cooldown and statistics are applied together and only then. A rejected
  proposal changes nothing and is logged as contact_rejected with its reason."""
  s=self.s;b=s.ball;d=event.data;p=s.players[event.actor];why=self.c1_reason(event)
  if why is None and event.kind=='acquire':
   keep=(b.x,b.y,b.z);b.x,b.y,b.z=d['ball_point']
   if not self.acquire(event.actor):b.x,b.y,b.z=keep;why='not_in_control_range'
  if why is not None:return self.c1_reject(event,why)
  cs=getattr(self,'contact_stats',None)
  if event.kind=='touch':
   deliberate=d.get('deliberate',True)
   if s.phase==Phase.FLIGHT:
    c2=self.c4c2_flight_touch(p,deliberate)if self.c4c2 else None #C4c2 review: recorded as a defensive touch of the flight
    self.emit('touch','1.5;4.5',player=p.id,deliberate=deliberate,tail_flight=True,**({'scoring_flight':c2}if c2 else{}))
   else:self.touch(p.id,deliberate)
   b.x,b.y,b.z=d['ball_point'];b.vx,b.vy,b.vz=d['velocity'];b.version+=1;b.course_time=s.now;b.resume=True
   if self.c4c2:p.next_action=max(p.next_action,s.now+d.get('cooldown_ms',0)) #C4c2: a contact never shortens a recovery (a grounding, a landing) already being served
   else:p.next_action=s.now+d.get('cooldown_ms',0)
   if cs is not None and d.get('keeper_block'):cs['keeper_blocks']+=1
  if self.c4c and d.get('c4c_kind'):self.emit('keeper_contact','C4c-K',player=p.id,kind=d['c4c_kind'],ball_point=[round(c,3)for c in d['ball_point']],deliberate=d.get('deliberate',True),
                                              **({'velocity_in':d.get('c4c_vin'),'velocity_out':[round(c,3)for c in d['velocity']],'normal':d.get('c4c_normal'),'hand_velocity':d.get('c4c_hand_v'),'secure_p':d.get('c4c_secure_p')}if event.kind=='touch'else{}))
  if cs is not None:cs['contacts_committed']+=1
  return True
 def follow_carrier(self):
  s=self.s;b=s.ball
  if b.carrier:
   p=s.players[b.carrier];sgn=s.attack_sign(p.team);offset=.35+.35*p.a.reach
   b.x=p.x+sgn*offset;b.y=p.y;b.z=p.hand_height;b.vx=p.vx;b.vy=p.vy;b.vz=p.vz
 def touch(self,pid,deliberate=True):
  s=self.s;p=s.players[pid];b=s.ball
  if s.phase==Phase.FLIGHT:
   if p.team==s.tail_owner:self.end_flight('offensive_touch',b.x,b.y)
   elif self.c4c2:self.c4c2_flight_touch(p,deliberate) #C4c2 review
   return
  if not self.live()and s.phase!=Phase.PENALTY:return
  if deliberate and(not self.eligible(p)or p.posture=='grounded'):
   self.illegal(pid,'ineligible_touch');return
  if b.last_releaser==pid:
   self.illegal(pid,'self_recontact');return
  if self.c4_occ and p.team!=s.owner and(deliberate or b.mode==BallMode.SHOT)and self.zone_intervention(p,'block_shot'if b.mode==BallMode.SHOT else'play_ball'):return
  b.last_touch=p.team;c2=None
  if self.c4c2:c2=self.c4c2_touch(p,deliberate)
  elif deliberate:
   b.scoring=True;b.last_releaser=None;b.pocket_origin=(p.x,p.y);b.pocket_release_team=p.team;self.reconstruction_check(p,'deliberate_play')
   if self.c4b:self.c4b_set_origin(p) #C4b: a deliberate touch (a tip) establishes the origin by the same foot rule
  s.opening_touched=True
  self.emit('touch','1.5;4.5',player=pid,deliberate=deliberate,**({'scoring_flight':c2}if c2 else{}))
 def c4c2_snap(self):
  b=self.s.ball;cp=lambda v:list(v)if isinstance(v,list)else dict(v)if isinstance(v,dict)else v
  return{k:cp(getattr(b,k,None))for k in('pocket_release_team','pocket_origin','c4b_origin','c4b_launch','c4c2_def','c4c2_off','c4c2_off_i')}
 def c4c2_unsnap(self,snap,actors):
  b=self.s.ball
  for k,v in snap.items():setattr(b,k,v)
  ft=snap['pocket_release_team']
  for pid in actors:
   q=self.s.players[pid]
   if ft is None:continue
   if q.team!=ft:
    xy=self.c4b_origin(q)[0]if self.c4b else(q.x,q.y);b.c4c2_def=list(b.c4c2_def or[])+[(q.id,round(xy[0],3),round(xy[1],3),True)]
   else:
    b.pocket_origin=(q.x,q.y)
    if self.c4b:self.c4b_set_origin(q)
    b.c4c2_off=q.id;b.c4c2_off_i=len(b.c4c2_def or[])
 def c4c2_flight_touch(self,p,deliberate):
  #a touch in the finishing flight by the team that does not own it is a defensive touch of that flight
  b=self.s.ball;ft=getattr(b,'pocket_release_team',None)
  if b.scoring and ft is not None and p.team!=ft:
   xy=self.c4b_origin(p)[0]if self.c4b else(p.x,p.y);b.c4c2_def=list(getattr(b,'c4c2_def',None)or[])+[(p.id,round(xy[0],3),round(xy[1],3),bool(deliberate))];return'defensive_touch_origin_kept'
  return None
 def c4c2_touch(self,p,deliberate):
  """C4c2, decided by DreLen on 9 October. While a scoring flight is under way (the ball is scoring and has a flight team, the team
  that released or last secured it), a touch by the other team, deliberate or not, a Keeper's parry included, is a defensive touch:
  the flight, its team and its offensive origin are kept. A touch by the flight team, deliberate or not, moves the offensive origin
  to that player's support foot (the last offensive player to touch the ball). With no scoring flight, a deliberate touch starts a
  new flight, as before. Flight team, offensive origin and last touch are kept as separate state."""
  b=self.s.ball;ft=getattr(b,'pocket_release_team',None)
  if b.scoring and ft is not None:
   if deliberate:b.last_releaser=None;self.reconstruction_check(p,'deliberate_play')
   if p.team!=ft:
    xy=self.c4b_origin(p)[0]if self.c4b else(p.x,p.y)
    b.c4c2_def=list(getattr(b,'c4c2_def',None)or[])+[(p.id,round(xy[0],3),round(xy[1],3),bool(deliberate))]
    return'defensive_touch_origin_kept'
   b.pocket_origin=(p.x,p.y)
   if self.c4b:self.c4b_set_origin(p)
   b.c4c2_off=p.id;b.c4c2_off_i=len(getattr(b,'c4c2_def',None)or[]);return'offensive_touch_origin_moved' #defensive touches before this one no longer make a reversal
  if deliberate:
   b.scoring=True;b.last_releaser=None;b.pocket_origin=(p.x,p.y);b.pocket_release_team=p.team;self.reconstruction_check(p,'deliberate_play')
   if self.c4b:self.c4b_set_origin(p)
   b.c4c2_def=[];b.c4c2_off=p.id;b.c4c2_off_i=0;return'new_flight'
  return None
 def release(self,pid,velocity,kind='pass',target=None,forced=False):
  s=self.s;b=s.ball;p=s.players[pid]
  if b.carrier!=pid:return False
  if not forced and(not self.eligible(p)or p.posture=='grounded' or s.phase not in (Phase.LIVE,Phase.PENALTY)):
   self.illegal(pid,'illegal_release');return False
  speed=math.sqrt(sum(v*v for v in velocity))
  if not forced and speed>self.pocket.get("ball_limit",40)+1e-6:self.illegal(pid,'ball_release_speed');return False
  self.follow_carrier();b.version+=1;b.carrier=None;b.vx,b.vy,b.vz=velocity;b.mode={'pass':BallMode.PASS,'kick':BallMode.KICK,'shot':BallMode.SHOT}.get(kind,BallMode.LOOSE)
  b.pocket_origin=(p.x,p.y);b.pocket_release_team=p.team
  c4o=self.c4b_set_origin(p)if self.c4b else None #C4b: the support foot at the instant of release
  b.release_time=s.now;b.last_releaser=None if forced else pid;b.last_touch=p.team;b.scoring=not forced;b.intended=target
  if self.c4c2:b.c4c2_def=[];b.c4c2_off=pid;b.c4c2_off_i=0 #C4c2: a release begins a new flight with its own identity and origin
  s.award_spot=None;s.award_available=None
  if not forced:
   p.keeper_hold_ms=0
   if kind=='shot'and s.advantage and s.advantage['team']==p.team:s.advantage=None;self.emit('advantage_realized','11.2',method='voluntary_shot')
  self.emit('release','4.4–4.5;7.3'if forced else'4.4–4.5;3.1',player=pid,kind=kind,forced=forced,velocity=list(velocity),target=target,**({'origin':c4o}if c4o else{}))
  if s.phase==Phase.PENALTY:s.penalty['released']=True
  return True
 def strike(self,pid,velocity,kind='kick'):
  s=self.s;p=s.players[pid];b=s.ball
  if not self.live()or b.carrier is not None:return False
  if not self.eligible(p)or p.posture=='grounded':self.illegal(pid,'ineligible_touch');return False
  if b.last_releaser==pid:self.illegal(pid,'self_recontact');return False
  if math.dist((b.x,b.y),(p.x,p.y))>p.a.reach+p.radius:return False
  if math.sqrt(sum(v*v for v in velocity))>self.pocket.get("ball_limit",40)+1e-6:self.illegal(pid,'ball_release_speed');return False
  ft=getattr(b,'pocket_release_team',None);defk=self.c4c2 and b.scoring and ft is not None and p.team!=ft
  b.version+=1;b.vx,b.vy,b.vz=velocity;b.mode=BallMode.KICK if kind=='kick'else BallMode.SHOT;b.scoring=True;b.last_touch=p.team;b.last_releaser=pid;b.release_time=s.now
  if defk:
   #C4c2: a kick by the other team on a scoring flight is a defensive deflection: the flight and its offensive origin are kept
   xy=self.c4b_origin(p)[0]if self.c4b else(p.x,p.y);b.c4c2_def=list(getattr(b,'c4c2_def',None)or[])+[(p.id,round(xy[0],3),round(xy[1],3),True)];c4o=None
  else:
   b.pocket_origin=(p.x,p.y);b.pocket_release_team=p.team
   c4o=self.c4b_set_origin(p)if self.c4b else None #C4b: for a kick, the support foot (the planted one)
   if self.c4c2:b.c4c2_def=[];b.c4c2_off=pid;b.c4c2_off_i=0
  c2k=('defensive_kick_origin_kept'if defk else'new_flight')if self.c4c2 else None
  self.emit('strike','4.4–4.5;5.2',player=pid,kind=kind,velocity=list(velocity),**({'origin':c4o}if c4o else{}),**({'scoring_flight':c2k}if c2k else{}));self.reconstruction_check(p,'deliberate_play');return True
 def frame_contact(self,velocity=None,point=None):
  if self.s.phase not in(Phase.LIVE,Phase.FLIGHT,Phase.PENALTY,Phase.OPENING):return
  b=self.s.ball;b.version+=1
  if velocity:b.vx,b.vy,b.vz=velocity
  if point:b.x,b.y,b.z=point
  self.emit('frame_contact','2.3;5.2;5.5')
 def retrieve_arrow(self,arrow_id):
  if self.s.phase not in(Phase.DEAD,Phase.BREAK):return False
  ar=next((a for a in self.s.arrows if a.id==arrow_id),None)
  if ar is None:return False
  ar.live=False;self.emit('arrow_retrieved','3.9',arrow=arrow_id,ammunition_added=0);return True
 def joint_control(self,pids):
  s=self.s;b=s.ball
  if len({s.players[p].team for p in pids})<2:return self.acquire(pids[0])
  if not all(self.eligible(s.players[p])for p in pids):return False
  b.carrier=None;b.mode=BallMode.CONTESTED;b.contested=tuple(sorted(pids));b.vx=b.vy=b.vz=0;s.contested_until=s.now+1000
  self.emit('joint_control','6.9',players=list(pids));return True
 def held(self):
  s=self.s
  if s.phase==Phase.OPENING and s.opening_team is None:return self.failed_hunt('joint_control')
  team=s.alternate;self.award(team,s.ball.x,s.ball.y,'held_ball');self.emit('held_ball','6.9',team=team)
 def contact_legal(self,a,t,kind='tackle',surface='torso',reach=True):
  #C3a3: reach=False leaves out the distance test, so that the answer is the legal condition alone: would this contact be lawful
  #if it happened? Being out of reach is a fact about distance; it must not stand in for, or hide, a protection that applies.
  s=self.s
  if not(self.eligible(a)and self.eligible(t)):return False,'ineligible_contact'
  if a.role=='archer'or t.role=='archer':return False,'archer_contact'
  if surface in ('head','neck','spine','groin','joint','knee','claw','horn','weapon'):return False,'dangerous_surface'
  if a.posture!='upright'or t.posture=='grounded':return False,'grounded_contact'
  av=getattr(a,'contact_velocity',(a.vx,a.vy));tv=getattr(t,'contact_velocity',(t.vx,t.vy))
  #C3a: the two contact-speed offences exist only in the legacy replay path. What a fast collision does is now physical (balance shock).
  if not self.c3 and(max(norm(*av),norm(*tv))>12+1e-7 or norm(av[0]-tv[0],av[1]-tv[1])>8+1e-7):return False,'contact_speed'
  if kind=='tackle' and s.ball.carrier!=t.id:return False,'noncarrier_wrap'
  if reach and norm(a.x-t.x,a.y-t.y)>a.radius+t.radius+.7*(a.a.reach+t.a.reach):return False,'out_of_contact_range'
  if kind!='tackle':
   dx,dy=a.x-t.x,a.y-t.y
   #C3c (decided by DreLen: only a hit from directly behind counts). From behind means strictly inside the rear cone: the hitter's
   #bearing from the other athlete is closer to the line straight out of his back than the half-angle. On the boundary it is lawful.
   if dx*t.facing[0]+dy*t.facing[1]<-self.blind_cos*max(.1,norm(dx,dy)):return False,'blindside'
  if s.phase==Phase.AWARD and a.team!=s.owner:
   rec=s.recovery
   #C2: a first-tackle recovery protects only its one-metre disc. Legal screening outside the disc remains possible.
   if not rec or min(norm(a.x-rec['spot'][0],a.y-rec['spot'][1])-a.radius,norm(t.x-rec['spot'][0],t.y-rec['spot'][1])-t.radius)<1:return False,'protected_recovery'
  if s.award_spot and s.award_available is not None and s.now<s.award_available+2000 and s.ball.carrier==t.id:
   if norm(s.ball.x-s.award_spot[0],s.ball.y-s.award_spot[1])<=1 and a.team!=t.team:return False,'protected_recovery'
  return True,'legal'
 def engage(self,actor,target,kind='block',surface='torso',sanction=True):
  a,t=self.s.players[actor],self.s.players[target]
  legal,reason=self.contact_legal(a,t,'tackle'if kind=='tackle'else'block',surface)
  if not legal:
   if sanction and reason!='out_of_contact_range':self.foul(actor,target,reason,major=reason in('contact_speed','dangerous_surface','ineligible_contact'),danger=reason in('contact_speed','dangerous_surface','ineligible_contact'))
   return False
  key=(actor,target,kind)
  if key not in self.s.engagements:
   self.s.engagements[key]=Engagement(actor,target,kind,self.s.now);self.emit('engagement','6.1–6.4',actor=actor,target=target,kind=kind)
  return True
 def tackle(self,actor,target,body='knee',witnessed=False):
  s=self.s;a,t=s.players[actor],s.players[target]
  if body in ('hand','foot'):
   self.emit('incomplete_tackle','6.5',actor=actor,target=target,body=body);return False
  #C3a: a grounding classified by the contact kernel carries its own witness of a lawful engagement, taken at the instant of
  #grounding on the kernel's substep. It is not re-tested against positions interpolated across the whole step.
  if witnessed:
   if s.ball.carrier!=target or not a.eligible(s.now)or not t.eligible(s.now):return False
  elif not self.engage(actor,target,'tackle'):return False
  if s.phase==Phase.PENALTY:
   self.emit('penalty_tackle','12.4',actor=actor,target=target);self.finish_penalty(0);return True
  if s.extension and a.team!=s.extension_team:self.emit('extension_tackle','16.6');self.end_period();return True
  bx,by=s.ball.x,s.ball.y
  if self.c3b:self.go_down(t) #C3b: he keeps the momentum he has and slides; getting up takes modelled time
  else:t.posture='grounded';t.next_action=s.now+800;t.vx=t.vy=0
  t.tackled_until=t.next_action
  if self.c2_tackles and s.owner==t.team and s.tackle_count==0:return self.first_tackle(a,t,bx,by)
  if self.c2_tackles:s.tackle_ordinal+=1;self.emit('tackle_count','C2-3',team=t.team,count_from=s.tackle_count,count_to=s.tackle_count+1,tackler=actor,carrier=target,spot=[bx,by],procedure='turnover',**({'ordinal_in_possession':s.tackle_ordinal}if self.c4_occ else{}))
  self.new_owner(a.team,'tackle');s.possession_ms=self.play_ms;s.phase=Phase.AWARD
  s.ball.version+=1;s.ball.carrier=None;s.ball.mode=BallMode.LOOSE;s.ball.scoring=False;s.ball.last_releaser=None;s.ball.x=bx;s.ball.y=by;s.ball.z=.1075;s.ball.vx=s.ball.vy=s.ball.vz=0
  s.award_spot=(bx,by);s.award_available=s.now;s.award_deadline=s.now+5000;s.engagements.clear()
  self.emit('tackle_award','6.5–6.7',actor=actor,target=target,spot=[bx,by]);return True
 def first_tackle(self,a,t,bx,by):
  """C2: first counted tackle of a possession. Possession is retained and the count becomes one.
  In the attacked Keeper Zone: goal-line inbound, and the zone must be cleared before a goal can count.
  Anywhere else, including the team's own zone: live local exclusive recovery at the ball's position."""
  s=self.s;team=t.team;bx=clamp(bx,0,100);by=clamp(by,0,100);attacked=s.own_zone(s.other(team));zj=self.zone(bx,by)
  where='attacked_zone'if zj==attacked else'own_zone'if zj==s.own_zone(team)else'outside'
  inbound=self.c2_inbound and where=='attacked_zone'
  s.tackle_count=1;s.engagements.clear();s.tackle_ordinal+=1
  self.emit('tackle_count','C2-3',team=team,count_from=0,count_to=1,tackler=a.id,carrier=t.id,spot=[bx,by],where=where,procedure='zone_inbound'if inbound else'live_recovery',**({'ordinal_in_possession':s.tackle_ordinal}if self.c4_occ else{}))
  if inbound and s.advantage:
   #A formal stoppage ends a pending advantage unrealised: play returns to the foul instant, so this tackle is not kept on the count.
   self.recall_advantage();return True
  if inbound:
   s.reconstruction={'team':team,'zone':attacked,'live_since':s.live_ms};self.count('reconstructions_set');self.emit('reconstruction_set','C2-4',team=team,zone=attacked)
   side=-1 if by<50 else 1 if by>50 else self.inbound_side(team)
   self.inbound(team,0. if attacked==0 else 100.,50+side*self.mark_off);return True
  b=s.ball;s.phase=Phase.AWARD
  b.version+=1;b.carrier=None;b.mode=BallMode.LOOSE;b.scoring=False;b.last_releaser=None;b.x=bx;b.y=by;b.z=.1075;b.vx=b.vy=b.vz=0
  s.award_spot=(bx,by);s.award_available=s.now;s.award_deadline=s.now+3000
  s.recovery={'team':team,'spot':(bx,by),'started':s.now,'must_clear':{},'committed':self.recovery_committed(team,bx,by)|{a.id}|set(self.grace)}
  self.emit('recovery_started','C2-3.1',team=team,spot=[bx,by],deadline=s.award_deadline,carrier=t.id,tackler=a.id,placed_at=s.now)
  if self.c3b:self.recovery_react(team,sorted(set(self.grace)-{a.id}))
  return True
 def recovery_react(self,team,holders=()):
  """C3b: opponents respond to a first-tackle recovery award after their own reaction time, not whenever their decision cycle
  next comes round. Until then each carries on with what he was doing. (Controller timing; recovery_react = 0 switches it off.)"""
  s=self.s;react={}
  for q in s.players.values():
   if q.active and q.role!='archer'and q.team!=team and self.assume['recovery_react']:
    q.next_decision=s.now+int(1000*q.a.decision_speed);react[q.id]=q.next_decision-s.now
  self.emit('recovery_compliance','C3b-5',holders_with_grace=list(holders),committed=sorted(s.recovery['committed']),reaction_ms=react)
 def recovery_committed(self,team,sx,sy):
  #Opponents for whom being in the disc is not avoidable: a body already inside it at the tackle, or one moving towards it whose
  #response time and braking distance carry it in. Standing or moving nearby is not enough. The tackler is added by the caller.
  out=set()
  for q in self.s.players.values():
   if not q.active or q.role=='archer'or q.team==team:continue
   dx,dy=q.x-sx,q.y-sy;d=norm(dx,dy);gap=d-(1+q.radius)
   if gap<0:out.add(q.id);continue
   vin=-(q.vx*dx+q.vy*dy)/max(d,1e-9)
   if vin>0 and gap<=vin*vin/(2*max(1,q.a.braking))+vin*q.a.decision_speed:out.add(q.id)
  return out
 def inbound_side(self,team):
  #An exact tie between the two marks: the attacking side chooses. Provisional controller: the side with more unmarked teammates.
  s=self.s;opp=[q for q in s.players.values()if q.team!=team and q.role!='archer'and self.eligible(q)];n={-1:0,1:0}
  for p in s.players.values():
   if p.team==team and p.role!='archer'and self.eligible(p)and all(norm(p.x-q.x,p.y-q.y)>self.mark_d for q in opp):n[-1 if p.y<50 else 1]+=1
  return 1 if n[1]>n[-1]else-1
 def inbound(self,team,gx,my,reason='zone_inbound',foul=False):
  """C2: goal-line inbound at the authorised mark. Possession clock and tackle count are retained; three-metre clearance;
  the taker stands just outside the field at the mark."""
  self.award(team,gx,my,reason,foul=foul,normalize=False);r=self.s.restart
  if r is not None and r.reason==reason:r.kind='inbound';r.clearance=3.;r.taker_spot=(gx+(-.4 if gx==0 else .4),my)
 def recovery_watch(self):
  """C2: the one-metre exclusion disc around a first-tackle recovery, checked against opponents' body footprints.
  An opponent inside must leave. One who cannot yet move (grounded, frozen) is an unavoidable obstruction, not an offence.
  One who could have left by now and has not is interfering."""
  s=self.s;rec=s.recovery;sx,sy=rec['spot']
  if self.c3b:
   #C3b: when an opponent who had to clear the disc has left it, record what was necessary, what he took and what was his own delay
   for pid,w in list(rec.get('inside',{}).items()):
    q=s.players[pid]
    if not q.active or norm(q.x-sx,q.y-sy)>=1+q.radius:
     self.emit('recovery_cleared','C3b-5',player=pid,found_inside_ms=w['at']-rec['started'],necessary_m=round(w['depth'],3),unable_ms=w['wait'],allowed_ms=w['clear_by']-w['at'],took_ms=s.now-w['at'],attributable_delay_ms=max(0,s.now-w['clear_by']),had_grace=pid in rec['committed'])
     del rec['inside'][pid]
  for q in s.players.values():
   if not q.active or q.role=='archer'or q.team==rec['team']:continue
   d=norm(q.x-sx,q.y-sy)
   if d>=1+q.radius:continue
   able=q.eligible(s.now)and q.posture!='grounded'
   if q.id not in rec['must_clear']:
    if able and q.id not in rec['committed']:
     #Avoidable occupation of the pickup space: he was clear, and able to stay clear, when the recovery began.
     self.count('recovery_interference_fouls');self.emit('recovery_obstruction','C2-3.1',player=q.id,unavoidable=False,entered_late=True,body_inside_disc_m=round(1+q.radius-d,3),clear_by=s.now)
     self.foul(q.id,None,'recovery_interference');return True
    wait=0 if able else max(0,max(q.next_action,q.freeze_until)-s.now)
    need=math.sqrt(2*(1+q.radius-d)/max(1,q.a.acceleration))+q.a.decision_speed+.3
    rec['must_clear'][q.id]=s.now+wait+int(1000*need)
    if self.c3b:rec.setdefault('inside',{})[q.id]={'at':s.now,'depth':1+q.radius-d,'wait':wait,'clear_by':rec['must_clear'][q.id]}
    if not able:self.count('recovery_unavoidable_obstructions')
    self.emit('recovery_obstruction','C2-3.1',player=q.id,unavoidable=not able,body_inside_disc_m=round(1+q.radius-d,3),clear_by=rec['must_clear'][q.id])
   elif able and s.now>rec['must_clear'][q.id]:
    self.count('recovery_interference_fouls');self.foul(q.id,None,'recovery_interference');return True
  return False
 def recovery_blocked(self):
  #Pickup is physically impossible when an opponent who cannot move has his body over the ball.
  s=self.s;sx,sy=s.recovery['spot']
  return any(q.active and q.role!='archer'and q.team!=s.recovery['team']and norm(q.x-sx,q.y-sy)<q.radius+s.ball.radius and not(q.eligible(s.now)and q.posture!='grounded')for q in s.players.values())
 def restore_recovery(self,cause,floor=False,remaining=3000):
  """C2: formal interruption of a first-tackle recovery. The exclusive recovery is restored at its original spot,
  the tackle count is kept, and the recovery resumes (resume_recovery) once the disc is clear."""
  s=self.s;rec=s.recovery;team=rec['team'];x,y=rec['spot'];self.count('recoveries_restored')
  self.emit('recovery_interrupted','C2-3.2',cause=cause,remaining_ms=remaining)
  s.recovery=None;self.award(team,x,y,'recovery_restored',foul=floor,normalize=False);r=s.restart
  if r is not None and r.reason=='recovery_restored':r.kind='recovery';r.remaining=remaining;r.note=cause
  return True
 def recovery_blockers(self,r):
  return[q for q in self.s.players.values()if q.active and q.role!='archer'and q.team!=r.team and norm(q.x-r.x,q.y-r.y)<1+q.radius]
 def resume_recovery(self):
  s=self.s;r=s.restart
  if s.phase!=Phase.DEAD or r is None or r.kind!='recovery':return False
  b=s.ball;b.version+=1;b.mode=BallMode.LOOSE;b.carrier=None;b.x=r.x;b.y=r.y;b.z=.1075;b.vx=b.vy=b.vz=0;b.scoring=False;b.last_releaser=None
  s.phase=Phase.AWARD;s.award_spot=(r.x,r.y);s.award_available=s.now;s.award_deadline=s.now+r.remaining
  s.recovery={'team':r.team,'spot':(r.x,r.y),'started':s.now,'must_clear':{},'replacement':True,'committed':set()};s.restart=None
  self.emit('recovery_resumed','C2-3.2',team=r.team,spot=[r.x,r.y],deadline=s.award_deadline,cause=r.note)
  if self.c3b:self.recovery_react(r.team)
  return True
 def exit_run(self,st,p,j,ax,ay,limit_ms):
  """C3b2: the time (ms) athlete p needs to get out of Keeper Zone j steering for the point (ax, ay), from the state
  st = (x, y, vx, vy, fatigue), or None if he is not out, inside the field, within limit_ms. It is his own motion law, the one
  the mover applies: top speed, his acceleration or braking along his present velocity, his turning limit across it. So a
  velocity pointing the wrong way has to be braked off and turned first, and that costs what it really costs. 20 ms steps.
  C3b3: a time later than limit_ms is never returned. The time reported is the end of the 20 ms step in which he is first out,
  so it is late by up to 20 ms: a way out he would in truth just make can be reported as not made, never the reverse."""
  s=self.s;gx=0. if j==0 else 100.;R=s.keeper_zone_radius;x,y,vx,vy,fat=st;dt=.02;t=0
  vmax=max(.1,p.a.maximum_speed*.88*(.70+.30*fat));acc=max(1.,p.a.acceleration*(.55+.45*fat));brk=p.a.braking;trn=p.a.turning*dt
  while t<limit_ms:
   dx,dy=ax-x,ay-y;d=norm(dx,dy);sp=norm(vx,vy)
   desx,desy=(dx/d*vmax,dy/d*vmax)if d>1e-9 else(0.,0.)
   dvx,dvy=desx-vx,desy-vy;a=acc if desx*desx+desy*desy>sp*sp else brk
   if sp>1:
    along=clamp((dvx*vx+dvy*vy)/sp,-brk*dt,a*dt);nx,ny=-vy/sp,vx/sp;side=clamp(dvx*nx+dvy*ny,-trn,trn)
    vx,vy=vx+along*vx/sp+side*nx,vy+along*vy/sp+side*ny
   else:
    dv=norm(dvx,dvy)
    if dv>0:
     k=min(1.,a*dt/dv);vx+=dvx*k;vy+=dvy*k
   x+=vx*dt;y+=vy*dt;t+=20
   if not(0<=x<=100 and 0<=y<=100):return None
   if norm(x-gx,y-50)>R:return t if t<=limit_ms else None #C3b3: out, but only after the limit, is not out within it
  return None
 def exit_points(self,j):
  #23 aim points just beyond the arc of zone j inside the field, 7.5 degrees apart as seen from the goal.
  s=self.s;gx=0. if j==0 else 100.;sg=1. if j==0 else-1.;R=s.keeper_zone_radius+.1;out=[]
  for i in range(-11,12):
   phi=math.radians(7.5*i);ex=gx+sg*R*math.cos(phi);ey=50+R*math.sin(phi)
   if 0<=ex<=100 and 0<=ey<=100:out.append((ex,ey))
  return out
 def exit_free(self,st,p,j,left_ms):
  """C3b2: the fastest time out with nobody in the way, from state st: the least over the aim points, searched up to left_ms; if
  none gets him out by then, the straight-out point is run on up to 6 s so that the shortfall can be reported. None: over 6 s."""
  best=None
  for ax,ay in self.exit_points(j):
   t=self.exit_run(st,p,j,ax,ay,left_ms if best is None else min(left_ms,best))
   if t is not None and(best is None or t<best):best=t
  if best is None:
   gx=0. if j==0 else 100.;ax,ay=min(self.exit_points(j),key=lambda q:norm(q[0]-st[0],q[1]-st[1]));best=self.exit_run(st,p,j,ax,ay,6000)
  return best
 def exit_routes(self,p,j,left_ms):
  """C3b: the ways out of Keeper Zone j practicable for athlete p now. For each aim point: whether an upright eligible
  opponent's body stands in the straight lane to it (within the two body radii of the line, ahead of him and short of the
  arc), and the time he needs to be out steering for it (exit_run, C3b2). A route is practicable if the lane is clear and he is
  out within the zone time he has left. Returns (fastest time with nobody in the way in ms, fastest practicable time in ms or
  None, number of practicable routes). A snapshot test: opponents are taken where they stand."""
  lanes=self.exit_lanes(p,j,left_ms);ok=[t for i,t in lanes.items()if t is not None]
  return self.exit_free((p.x,p.y,p.vx,p.vy,p.fatigue),p,j,left_ms),(min(ok)if ok else None),len(ok)
 def exit_lanes(self,p,j,left_ms,only=None,bodies=None):
  #{aim point index: time out in ms, or None if he is not out within left_ms} for every aim point whose lane is clear of opponents.
  #only: an iterable of indices to which the timing is limited (the lane test is still made for all).
  #bodies (C3b3): a set, filled with the opponents whose bodies stand in at least one lane.
  s=self.s;st=(p.x,p.y,p.vx,p.vy,p.fatigue);out={}
  opp=[q for q in s.players.values()if q.active and q.team!=p.team and q.role!='archer'and self.eligible(q)and q.posture=='upright']
  for i,(ex,ey)in enumerate(self.exit_points(j)):
   dx,dy=ex-p.x,ey-p.y;d=norm(dx,dy)
   if d>1e-9:
    ux,uy=dx/d,dy/d
    inl=[q.id for q in opp if 0<(q.x-p.x)*ux+(q.y-p.y)*uy<d+q.radius and abs((q.x-p.x)*uy-(q.y-p.y)*ux)<p.radius+q.radius]
    if inl:
     if bodies is not None:bodies.update(inl)
     continue
   out[i]=self.exit_run(st,p,j,ex,ey,left_ms)
  return out
 def exit_before(self,p,j,snap):
  #The witness at a snapshot (x, y, vx, vy, fatigue, zone time left): the fastest time out with nobody in the way against the time left.
  free=self.exit_free(snap[:5],p,j,snap[5]);return{'left_ms':snap[5],'free_ms':free,'sufficient':free is not None and free<=snap[5]}
 def exit_watch(self):
  """C3b off-ball exit protection, the witness (episodes: C3b2). An attacker without the ball who is inside the zone he attacks
  and whose own target lies outside it is trying to leave. His state is noted at every check (once per interval).
  An obstruction EPISODE begins when an opponent materially runs into him (the kernel's collision witness) and no episode is
  open. Its 'before' witness is his state at the last check before that contact: was his time still enough then? From then on,
  at every check, the lanes are examined (exit_lanes). A lane OPENS when it is clear of opponents and he could be out by it in
  the zone time left; the time it needed then is kept with it. It stays open for as long as it stays clear, and CLOSES when an
  opponent's body is in it. (Running short of time on a lane that stayed clear does not close it: that time went because he
  did not take it.) The zone time since the previous check is put down to the state found at that check: OPEN (some lane
  open) or DENIED (none).
  An opening counts against him only when it was real: a lane open for at least as long as it needed when it opened. Then he
  ignored an attainable exit; the episode is closed against him, and a later contact begins a new episode with its own 'before'
  witness. An opening shorter than that proves nothing: a further contact joins the same episode. The record ends when he is
  out, or stops trying.
  C3b3, who denied him. Zone time found DENIED at a check is put down to the opponents who have run into him in this episode
  and whose bodies stand in his lanes at that check. If none of them does (the lanes are clear but the time is gone, or the
  bodies in them have not touched him), it is put down to whoever it was put down to at the check before, and at the start of
  a denied stretch to the opponent who last ran into him before it began. A lane that was open also closes when an opponent
  runs into him, he needs longer for it than he did at the check before, and he can no longer be out by it in the time left;
  if he still can, that lane needs from then on the time it has been open plus the time he needs from there. A contact that
  does not set him back changes no lane: time he let run on an open lane is still his. So a contact made while he is already denied, by an
  opponent who is not in his way, takes on nothing. Each stretch is kept with its length, its opponents and that basis."""
  s=self.s
  for p in s.players.values():
   rec=getattr(p,'exit_try',None)
   if not p.active or p.role=='archer':
    if rec:p.exit_try=None
    continue
   j=next((k for k in(0,1)if p.zone_loc[k]=='in'),None)
   trying=j is not None and p.team==s.owner and s.ball.carrier!=p.id and p.zone_ms[j]>0 and not(p.role=='keeper'and j==s.own_zone(p.team))and self.zone(*p.target)!=j
   if not trying or(rec and rec['zone']!=j):
    if rec:p.exit_try=None
    if not trying:continue
    rec=None
   zms=p.zone_ms[j];left=5000-zms;snap=(p.x,p.y,p.vx,p.vy,p.fatigue,left)
   if rec is None:rec=p.exit_try={'zone':j,'since':s.now,'start':snap,'last':snap,'zms':zms,'seen':getattr(p,'c3_hit',(-1,None))[0],'ep':None,'episodes':0}
   ep=rec['ep'];step=zms-rec['zms']
   if ep is not None and not ep['ignored']:
    #the zone time since the previous check belongs to the state found then
    self.exit_account(ep,step);ep['since_contact_open_ms']+=step if ep['state']=='open'else 0.
   hit=getattr(p,'c3_hit',None);fresh=False
   if hit and hit[0]>rec['seen']:
    fresh=True
    rec['seen']=hit[0];before=self.exit_before(p,j,rec['last'])
    if ep is None or ep['ignored']:
     ep=rec['ep']={'before':before,'contacts':[],'by':None,'state':None,'lanes':{},'denied_ms':0.,'open_ms':0.,'need_ms':None,'longest_open_ms':0.,'since_contact_open_ms':0.,'ignored':False,'checks':0,
                   'deniers':[],'basis':None,'denied_by':{},'segments':[],'opened':False};rec['episodes']+=1
    ep['contacts'].append({'at_ms':round(hit[0],1),'by':hit[1],'left_ms':left,'before':before,'route_open_ms_since_previous_contact':ep['since_contact_open_ms']});ep['by']=hit[1];ep['since_contact_open_ms']=0.
   if ep is not None and not ep['ignored']:
    bodies=set();now=self.exit_lanes(p,j,left,bodies=bodies);ep['checks']+=1;lanes=ep['lanes'];was=ep['state']
    for i in[i for i in lanes if i not in now]:del lanes[i] #an opponent's body is in that lane now
    if fresh and lanes:
     #C3b3: an opponent has just run into him. For each lane still open and clear: does he need longer for it now than he did
     #at the check before? Then the contact has set him back on it. If he can no longer be out by it in the time left, it closes;
     #otherwise it needs, from now on, the time it has been open plus the time he needs from here.
     pts=self.exit_points(j);prev=rec['last'][:5]
     for i in list(lanes):
      a=self.exit_run(prev,p,j,pts[i][0],pts[i][1],6000);b=now[i]if now[i]is not None else self.exit_run(snap[:5],p,j,pts[i][0],pts[i][1],6000)
      if b is None or(a is not None and b>a):
       if now[i]is None:del lanes[i]
       else:lanes[i][0]=max(lanes[i][0],lanes[i][1]+now[i])
    for i,t in now.items():
     if i not in lanes and t is not None:lanes[i]=[t,0.] #it opens: [time it needs from here, how long it has been open]
    ep['state']='open'if lanes else'denied'
    if lanes:ep['need_ms']=min(v[0]for v in lanes.values());ep['deniers']=[];ep['basis']=None
    else:
     who=sorted({c['by']for c in ep['contacts']}&bodies)
     if who:ep['deniers']=who;ep['basis']='ran_into_him_and_stands_in_his_lanes'
     elif was!='denied'or not ep['deniers']:ep['deniers']=[ep['by']];ep['basis']='last_to_run_into_him_before_this_denial'
     else:ep['basis']='carried_from_the_check_before'
   rec['last']=snap;rec['zms']=zms
 def exit_account(self,ep,step):
  #Zone time that has run since the last check, put down to the state found at that check.
  if ep['state']=='open':
   ep['open_ms']+=step
   if step>0:ep['opened']=True
   for v in ep['lanes'].values():
    v[1]+=step;ep['longest_open_ms']=max(ep['longest_open_ms'],v[1])
    if v[1]>=v[0]:ep['ignored']=True;ep['need_ms']=v[0]
  elif ep['state']=='denied':
   ep['denied_ms']+=step
   if step>0:
    #C3b3: this stretch of denied time, and the opponents it is put down to (each in full when there are several)
    for q in ep['deniers']:ep['denied_by'][q]=ep['denied_by'].get(q,0.)+step
    seg=ep['segments']
    if seg and not ep['opened']and seg[-1]['by']==ep['deniers']and seg[-1]['basis']==ep['basis']:seg[-1]['ms']+=step
    else:seg.append({'by':list(ep['deniers']),'basis':ep['basis'],'ms':step})
    ep['opened']=False
 def zone_expiry_c3b(self,p,j):
  """C3b: an attacker's five seconds in the zone have run out. For the ball carrier: record who was holding him and whether he
  was being contained. For an off-ball attacker: classify his exit from the witness (exit_watch). Where his time was enough as
  he set off and still enough just before the obstruction episode now open began, and he has not ignored an attainable exit
  since, opponents' contact has denied him his way out: no expiry is given, and exactly the zone time that ran while no
  practicable route existed in that episode is given back.
  C3b3: the opponent penalised is the one to whom most of that denied time is put down (exit_watch); on equal time, the one of
  them who ran into him last. The record gives every denied stretch with its opponents, each opponent's total, and the last
  opponent to run into him, who is not thereby the one responsible."""
  s=self.s;rec=getattr(p,'exit_try',None);carrier=s.ball.carrier==p.id;extra={};ep=None
  if carrier:
   held=[{'player':k[0],'grip':round(en.progress,4),'containing':bool(getattr(en,'contain',False))}for k,en in sorted(s.engagements.items())if k[2]=='tackle'and k[1]==p.id]
   cls='carrier_contained'if any(h['containing']for h in held)else'carrier_held'if held else'carrier_free'
   extra={'holders':held}
   if cls=='carrier_contained':self.count('containment_expiries')
  elif not self.assume['exit_protection']:cls='not_assessed'
  elif rec is None or rec['zone']!=j:cls='no_exit_attempt'
  else:
   start=self.exit_before(p,j,rec['start']);ep=rec['ep']
   if ep is not None and not ep['ignored']:
    #the time from the last check to the expiry belongs to the state found at that check
    self.exit_account(ep,p.zone_ms[j]-rec['zms']);rec['zms']=p.zone_ms[j]
   if not start['sufficient']:cls='time_already_insufficient'
   elif ep is None:cls='no_opposing_contact'
   elif not ep['before']['sufficient']:cls='time_insufficient_before_contact'
   elif ep['ignored']:cls='practicable_route_remained'
   else:cls='all_routes_denied_by_contact'
   extra={'exit':{'since':rec['since'],'left_ms':start['left_ms'],'free_ms':start['free_ms'],'sufficient':start['sufficient'],'episodes':rec['episodes'],
                  **({'contacts':ep['contacts'],'before_contact':ep['before'],'denied_ms':ep['denied_ms'],'route_open_ms':ep['open_ms'],'longest_continuous_open_ms':ep['longest_open_ms'],
                      'needed_ms_by_the_lane_concerned':ep['need_ms'],'ignored_attainable_exit':ep['ignored'],'checks_after':ep['checks'],
                      'denied_segments':[dict(g)for g in ep['segments']],'denied_ms_by_opponent':dict(sorted(ep['denied_by'].items())),'last_contact_by':ep['by']}if ep is not None else{'contacts':[]})}}
  if cls=='all_routes_denied_by_contact':
   last={c['by']:i for i,c in enumerate(ep['contacts'])};share=ep['denied_by']
   by=max(share,key=lambda q:(share[q],last.get(q,-1)))if share else ep['by'];back=max(0.,p.zone_ms[j]-ep['denied_ms']);self.count('exit_obstructions')
   self.emit('exit_obstruction','C3b-8',player=p.id,zone=j,by=by,zone_ms_restored_to=back,**extra)
   p.zone_ms[j]=back;p.exit_try=None
   self.foul(by,p.id,'exit_obstruction',advantage=True);return
  self.count('attacking_zone_expiries');self.emit('attacking_zone_expiry','C2-5',player=p.id,zone=j,possible_exit_interference=self.exit_interference(p,j),exit_class=cls,**extra)
  if self.c4_occ and self.zone_offset(p,'zone_expiry',p.zone_ms[j]):return #C4.0 r2: a defensive violation of the same millisecond (15.5)
  self.illegal(p.id,'zone_expiry')
 def c4b_origin(self,p):
  """C4b, decided by DreLen: the scoring origin of a release is the support foot. Both feet planted: the foot nearer the goal
  he attacks (distance to its centre, the radial territory geometry); one planted: that foot; airborne: the last planted foot's
  position. Returns (x, y) and the record of how it was found, with the pelvis kept beside it. Without foot state (the legacy
  path) the pelvis is used and the record says so."""
  s=self.s;ft=getattr(p,'feet',None);gx=s.attack_goal(p.team);pel=(p.x,p.y)
  if not ft:return pel,{'rule':'pelvis_no_foot_state','pelvis':[round(p.x,3),round(p.y,3)]}
  down=[k for k in('L','R')if ft[k]['planted']]
  if down:
   k=min(down,key=lambda k:(norm(ft[k]['x']-gx,ft[k]['y']-50),k));xy=(ft[k]['x'],ft[k]['y']);rule='both_planted_nearer_goal'if len(down)==2 else'one_planted'
  elif getattr(p,'last_plant',None):xy=p.last_plant[:2];k=p.last_plant[3];rule='airborne_last_plant'
  else:return pel,{'rule':'pelvis_no_foot_state','pelvis':[round(p.x,3),round(p.y,3)]}
  return xy,{'rule':rule,'foot':k,'origin':[round(xy[0],3),round(xy[1],3)],'pelvis':[round(p.x,3),round(p.y,3)],
             'territory':self.territory(p.team,*xy),'pelvis_territory':self.territory(p.team,*pel),
             'feet':{q:[round(ft[q]['x'],3),round(ft[q]['y'],3),ft[q]['planted']]for q in('L','R')if'x'in ft[q]}}
 def c4b_auto_points(self,carry):
  #C4b: the value of an automatic penalty award under the active configuration (build specification 2): the carry value for a
  #denied or automatic finish when Carry is enabled, otherwise the zone-release value. Declared mapping, the Lead's position.
  cv=self.pocket.get('carry_value',0)
  return cv if(carry and cv>0)else self.pocket.get('release_points',9)
 def c4b_set_origin(self,p):
  #C4b: the origin of the last deliberate play, with its record kept on the ball for the goal record
  b=self.s.ball;xy,rec=self.c4b_origin(p);b.pocket_origin=xy;b.c4b_origin=rec;b.c4b_launch=(round(b.x,3),round(b.y,3),round(b.z,3));return rec
 def zone_due(self):
  """C4.0: the defending players who can be called for an unmarked expiry now, each with the live millisecond at which he
  became callable: the instant his allowance ran out, or, if he has been called already, the end of his compliance time.
  Not callable: a Keeper in his own zone, an Archer, a frozen player, a player off the field (his count is paused there
  and he is not in the zone), and a called player whose compliance time is still running."""
  s=self.s;out=[]
  if s.owner is None:return out #no possession, no defending team
  for p in s.players.values():
   if not p.active or p.role=='archer'or p.team==s.owner or p.frozen(s.now):continue
   j=self.zone(p.x,p.y)
   if j is None or(p.role=='keeper'and j==s.own_zone(p.team)):continue
   if p.unmarked_ms[j]<5000 or s.live_ms<p.zone_fouled[j]:continue
   out.append((max(s.live_ms-(p.unmarked_ms[j]-5000),p.zone_fouled[j]),p.id,j))
  return sorted(out)
 def zone_compliance_time(self,p,j):
  """C4.0: the one opportunity a called defender has to leave the zone or regain marking, in live milliseconds, worked out
  from where he is and how he is moving when called. Declared estimate, not fitted, built as a bound that holds whatever he
  was doing (C4.0 r2: on the motion the C3 kernel actually allows him, tired or fresh):
    reaction: his decision time, during which a moving player may still be speeding up, at his full attribute acceleration
      (no fatigue reduction, the conservative side for this part), in the worst direction (further in), to at most his
      fresh top speed;
    stop: from that speed at his braking;
    run: from rest to the arc by the shortest line, integrated on the kernel's own limits: acceleration
      x (0.55 + 0.45 x fatigue), top speed x (0.70 + 0.30 x fatigue) x 0.88 (off the ball), and the slowing the kernel
      applies as he nears a target 2 m beyond the arc (the exit target of the controllers). Fatigue is taken at its lowest
      value it could reach during the whole estimate (it falls while he runs);
    0.3 s.
  The drill (drills_c4_0.py) checks it against the kernel at three fatigue levels and with acceleration, braking, top speed,
  decision time and endurance varied one at a time. It is not a new five seconds, and nothing renews it: not a later check,
  not a substitution (the slot keeps the deadline)."""
  s=self.s;gx=0 if j==0 else 100;way=max(0,s.keeper_zone_radius-norm(p.x-gx,p.y-50))+.1;rt=p.a.decision_speed
  sp=p.speed;brk=max(1,p.a.braking);acc=max(1,p.a.acceleration);fresh_top=max(.1,p.a.maximum_speed*.88)
  v1=min(max(fresh_top,sp),sp+acc*rt)if sp>0 else 0.;drift=(sp+v1)/2*rt;stop=v1/brk;d=way+drift+v1*v1/(2*brk)
  burn=(.00015+.006)*(1.25-p.a.endurance*.6)*float(self.assume.get('fatigue_rate',1.)) #the kernel's fatigue cost per second at full intensity
  T=rt+stop+3.;run=0.
  for _ in range(3): #the run time depends on the fatigue reached, which depends on the run time: settle it (three passes are ample)
   f=max(.15,p.fatigue-burn*T);a=max(.1,p.a.acceleration*(.55+.45*f));top=max(.1,p.a.maximum_speed*(.70+.30*f)*.88)
   run=0.;x=0.;v=0.;n=400;dx=d/n
   for i in range(n): #distance-stepped: speed at each point is the least of what acceleration, top speed and the arrival braking allow
    xe=x+dx;ve=min(math.sqrt(v*v+2*a*dx),top,math.sqrt(2*brk*max(0.,d+2.-xe)))
    run+=dx/max(.05,(v+ve)/2);x,v=xe,ve
   T=rt+stop+run
  parts={'distance_out_m':round(way,3),'speed_mps':round(sp,3),'fatigue':round(p.fatigue,4),'fatigue_assumed':round(f,4),'reaction_ms':int(1000*rt),'drift_m':round(drift,3),'stop_ms':int(1000*stop),'run_ms':int(1000*run),'margin_ms':300}
  parts['allowed_ms']=1+parts['reaction_ms']+parts['stop_ms']+parts['run_ms']+parts['margin_ms'];return parts
 def zone_witness(self,p):
  #C4.0: the nearest opponent who could mark him at this instant (eligible, in the field, on his feet), and how far away he is.
  s=self.s;att=[q for q in s.players.values()if q.active and q.role!='archer'and q.team==s.owner and self.eligible(q)and q.posture!='grounded']
  if not att:return None,None
  q=min(att,key=lambda q:norm(q.x-p.x,q.y-p.y));return q.id,norm(q.x-p.x,q.y-p.y) #exact; rounded only where it is logged
 def zone_call(self,offset=False):
  """C4.0, DreLen's ruling of 7 October. A defensive Keeper Zone violation is the expiry of the unmarked allowance of one or
  more defenders at the same resolved millisecond: they are one violation with one consequence. The team defending has one
  counter for the opposing possession, across both zones.
    First violation of the possession: the tackle count returns to zero and the possession clock is raised to
      min(play clock, max(remaining, 20 s)); in an untimed extension, to its ten seconds (rulebook 16.6). The period clock
      is not touched. Advantage is played as for any defensive foul: realised, play goes on with the remedy kept; failed,
      play returns to the foul instant, which already contains the remedy, so it is given once.
    Second violation of the possession: a penalty run under the existing procedure. If an advantage is pending it ends
      unrealised and the clocks return to its foul instant first, as for any foul inside an advantage (retained).
  No personal sanction either time (see foul). Each defender called gets one compliance time (zone_compliance_time); if he
  is still in the zone, unmarked, when it ends, that is a new violation. So is a later expiry by another defender.
  Returns True if a violation was called."""
  s=self.s;due=self.zone_due()
  if not due:return False
  t0=due[0][0];group=[d for d in due if d[0]==t0];later=[d for d in due if d[0]!=t0]
  s.zone_violations+=1;n=s.zone_violations;team=s.players[group[0][1]].team;parts=[]
  for _,pid,j in group:
   p=s.players[pid];again=p.zone_fouled[j]>0;c=self.zone_compliance_time(p,j);near,dist=self.zone_witness(p)
   parts.append({'player':pid,'zone':j,'unmarked_ms':p.unmarked_ms[j],'ground':'still_unmarked_after_compliance_time'if again else'allowance_expired','nearest_opponent':near,'nearest_opponent_m':None if dist is None else round(dist,3),'compliance':c,'compliance_deadline_live_ms':s.live_ms+c['allowed_ms']})
   p.zone_fouled[j]=s.live_ms+c['allowed_ms'];self.count('defensive_unmarked_expiries');self.emit('defensive_unmarked_expiry','C2-5',player=pid,zone=j)
  first=n==1;was=(s.tackle_count,s.possession_ms);adv=s.advantage
  if offset: #C4.0 r2: the award is offset by an attacking technical of the same millisecond (zone_offset); nothing else changes here
   self.count('zone_violations');self.emit('zone_violation','C4.0-zone',team=team,against=s.owner,number_in_possession=n,remedy='offset_by_simultaneous_attacking_offence',resolved_live_ms=t0,called_live_ms=s.live_ms,
            participants=parts,due_later_in_this_instant=[d[1]for d in later],tackle_count_from=was[0],tackle_count_to=was[0],p_ms_from=was[1],p_ms_to=was[1],
            advantage_already_pending=adv is not None,recovery_in_progress=s.recovery is not None,reconstruction=s.reconstruction is not None,personal_sanction=None);return True
  if first:
   s.tackle_count=0
   s.possession_ms=10000 if s.extension else min(self.play_ms,max(20000,s.possession_ms))
   #a foul instant already on record for this team's own pending advantage must give the remedy back if that advantage is recalled
   if adv and'c2'in adv and adv['team']==s.owner:adv['c2']['count']=0;adv['c2']['zone_violations']=n
  self.count('zone_violations');self.count('zone_violation_resets'if first else'zone_violation_penalties')
  self.emit('zone_violation','C4.0-zone',team=team,against=s.owner,number_in_possession=n,remedy='tackle_count_reset'if first else'penalty_run',resolved_live_ms=t0,called_live_ms=s.live_ms,
            participants=parts,due_later_in_this_instant=[d[1]for d in later],tackle_count_from=was[0],tackle_count_to=s.tackle_count,p_ms_from=was[1],p_ms_to=s.possession_ms,
            advantage_already_pending=adv is not None,recovery_in_progress=s.recovery is not None,reconstruction=s.reconstruction is not None,personal_sanction=None)
  self.foul(group[0][1],None,'zone_unmarked',advantage=first,penalty=not first);return True
 def zone_offset(self,p,reason,over_ms):
  """C4.0 r2 (the Lead's audit, choice 4): an attacking technical expiry (zone residence, or the Keeper's ball hold) falls due
  at the same live millisecond as a defensive zone violation. Both offences are collected before possession changes, and
  rulebook 15.5 decides:
    a first defensive violation is a technical, like the attacking expiry: same severity, so the awards offset and the team
    in control keeps the ball with its pre-event clock (a restart at the ball, as for offsetting fouls). The defensive
    violation is still recorded and counted for the possession, and its defenders still get their compliance time;
    a second defensive violation is a penalty-chance offence, more serious than a technical: the attack, its victim, gets
    the penalty run, and the attacking expiry gives no turnover.
  Personal discipline is personal (15.5): none for a zone expiry; the Keeper's ball hold keeps its own. Not applied while an
  advantage is pending: an attacking offence then enforces the earlier defensive foul (11.3, retained). A defensive
  violation due earlier than the attacking expiry is called first, as the earlier event (16.1). A different precedence is
  DreLen's to set. Returns True if it dealt with the attacking expiry."""
  s=self.s
  if s.advantage is not None:return False
  t=s.live_ms-max(0,over_ms-5000);due=self.zone_due()
  if not due or due[0][0]>t:return False
  if due[0][0]<t:self.zone_call();return True #an earlier, uncalled defensive offence comes first; the attacking expiry is judged after it
  first=s.zone_violations==0
  self.count('zone_offences_simultaneous');self.emit('simultaneous_offences','15.5',attacking={'player':p.id,'reason':reason},defending=[d[1]for d in due if d[0]==t],
            resolution='offset_same_severity'if first else'penalty_chance_offence_prevails',live_ms=t)
  if reason=='keeper_hold':self.discipline(p.id,'warning')
  if not first:self.zone_call();return True
  self.zone_call(offset=True);self.award(s.owner,s.ball.x,s.ball.y,'offsetting_fouls');return True
 def zone_overdue(self,p):
  """C4.0: is this defender, at this instant, over his unmarked allowance, in a zone, with no exemption? The marking test is
  made on positions as they are now, not as they were when his count was last updated. Returns the witness, or None."""
  s=self.s
  if not self.c4_occ or s.owner is None or p.team==s.owner or not p.active or p.role=='archer'or p.frozen(s.now):return None
  j=self.zone(p.x,p.y)
  if j is None or(p.role=='keeper'and j==s.own_zone(p.team))or p.unmarked_ms[j]<5000:return None
  near,dist=self.zone_witness(p)
  if near is not None and dist<=self.mark_d:return None
  return{'player':p.id,'zone':j,'eligible':self.eligible(p),'unmarked_ms':p.unmarked_ms[j],'nearest_opponent':near,'nearest_opponent_m':None if dist is None else round(dist,3),'marking_distance_m':self.mark_d,'called_before':p.zone_fouled[j]>0,'compliance_time_left_ms':max(0,p.zone_fouled[j]-s.live_ms)}
 def zone_intervention(self,p,act):
  """C4.0: a defender who is over his allowance and unmarked is about to control or play the ball, or block a shot.
  Always recorded. A violation of his that is due at this very millisecond is called before his play counts, so it cannot be
  lost to the change of possession his own play would cause.
  PROPOSAL, NOT CANON, off unless CALIBRATION['zone_direct_penalty'] = 1: the intervention itself is a penalty run. One
  penalty: no first-violation remedy is given for the same incident. Returns True if play was stopped."""
  s=self.s;b=s.ball
  if not self.live():return False
  self.zone_reconcile() #C4.0 r2: marking and exits as they stand at this instant, before anyone is judged
  w=self.zone_overdue(p)
  if w is None:return self.zone_due_first()
  self.count('zone_overdue_interventions');self.emit('zone_overdue_intervention','C4.0-zone',act=act,ball_mode=b.mode.value,scoring_attempt=b.mode==BallMode.SHOT,direct_penalty_rule=self.zone_direct,**w)
  if self.zone_direct:
   s.zone_violations+=1;self.count('zone_violations');self.count('zone_direct_penalties')
   self.emit('zone_violation','C4.0-zone',team=p.team,against=s.owner,number_in_possession=s.zone_violations,remedy='direct_penalty_run',resolved_live_ms=s.live_ms,called_live_ms=s.live_ms,participants=[w],personal_sanction=None)
   self.foul(p.id,None,'zone_intervention',penalty=True);return True
  return self.zone_due_first()
 def zone_due_first(self):
  """C4.0: every defensive violation due at this instant is called before a defender's control or play of the ball at this
  instant counts, so that the change of possession it may cause cannot erase it. Returns True if play was stopped.
  C4.0 r2 (the Lead's audit): first the marking exemptions and the arc exits are brought up to this instant (zone_reconcile),
  so that a defender who is marked at the moment of the play is not called on a count from before it."""
  self.zone_reconcile()
  while self.live()and self.zone_due():self.zone_call()
  return not self.live()
 def exit_interference(self,p,j):
  #Telemetry only: the player was moving outward and in an opponent's engagement. This is not a finding of obstruction.
  s=self.s;gx=0 if j==0 else 100;rx,ry=p.x-gx,p.y-50;outward=(p.vx*rx+p.vy*ry)/max(.1,norm(rx,ry))>.5
  return bool(outward and any(p.id in(k[0],k[1])and s.players[k[0]].team!=s.players[k[1]].team for k in s.engagements))
 def zone_reconcile(self):
  """C4.0 r2: bring every occupancy witness up to this instant without adding any time: a marking exemption that holds now
  renews the allowance, and a lawful arc exit resets the counts, exactly as the next update would. Used where a defender's
  play on the ball must be judged at its own instant (zone_due_first, zone_intervention)."""
  self.occupancy(0,watch=False)
 def occupancy(self,dt,watch=True):
  """C2 Keeper Zone occupancy. Pelvis position decides; the arc belongs to the zone.
  Team in possession: five seconds per zone. The count resets only on an exit across the arc inside the field. Outside the
  field it is paused and kept, and re-entry does not reset it.
  Team out of possession: exempt while within marking distance of any eligible opponent in the field; otherwise a
  five-second unmarked allowance, renewed by regaining marking or by an exit across the arc.
  A Keeper is exempt in his own zone. Counts pause while frozen and during recognised tackle recovery, and do not accrue in dead time."""
  s=self.s;att=None
  for p in s.players.values():
   if not p.active or p.role=='archer':continue
   infield=0<=p.x<=100 and 0<=p.y<=100;zn=self.zone(p.x,p.y)
   for j in(0,1):
    loc='off'if not infield else'in'if zn==j else'out';prev=p.zone_loc[j]
    if prev!=loc:
     stored=p.zone_ms[j]or p.unmarked_ms[j]
     if prev=='in'and loc=='out':
      if stored or p.zone_fouled[j]:self.count('zone_exits_valid_with_stored_time');self.emit('zone_exit_valid','C2-5',player=p.id,zone=j,stored_ms=p.zone_ms[j],unmarked_ms=p.unmarked_ms[j])
      if self.c4_occ and p.zone_fouled[j]:self.emit('zone_compliance','C4.0-zone',player=p.id,zone=j,how='left_across_the_arc',ms_before_deadline=p.zone_fouled[j]-s.live_ms)
      p.zone_ms[j]=0;p.unmarked_ms[j]=0;p.zone_fouled[j]=0
      keep=s.advantage['c2'].get('keep')if s.advantage and'c2'in s.advantage else None
      if keep and p.id in keep: #a witnessed lawful exit also resets what a recalled advantage would give back
       for v in keep[p.id]:v[j]=0
     elif prev=='in'and loc=='off'and stored:self.count('zone_exits_over_end_line_with_stored_time');self.emit('zone_exit_invalid','C2-5.1',player=p.id,zone=j,stored_ms=p.zone_ms[j],unmarked_ms=p.unmarked_ms[j])
     elif prev=='off'and loc=='out'and stored:self.emit('zone_reentry_no_reset','C2-5.1',player=p.id,zone=j,stored_ms=p.zone_ms[j],unmarked_ms=p.unmarked_ms[j])
     p.zone_loc[j]=loc
    if loc!='in'or s.owner is None:continue
    if p.role=='keeper'and j==s.own_zone(p.team):continue
    paused=dt<=0 or p.frozen(s.now)or s.now<p.tackled_until
    if p.team==s.owner:
     if not paused:p.zone_ms[j]+=dt
     continue
    if att is None:att=[q for q in s.players.values()if q.active and q.role!='archer'and q.team==s.owner and self.eligible(q)and q.posture!='grounded']
    if not p.frozen(s.now)and any(norm(q.x-p.x,q.y-p.y)<=self.mark_d for q in att):
     if self.c4_occ and p.zone_fouled[j]:
      q=min(att,key=lambda q:norm(q.x-p.x,q.y-p.y));self.emit('zone_compliance','C4.0-zone',player=p.id,zone=j,how='marking_regained',ms_before_deadline=p.zone_fouled[j]-s.live_ms,marking=q.id,distance_m=round(norm(q.x-p.x,q.y-p.y),3))
     p.unmarked_ms[j]=0;p.zone_fouled[j]=0 #marking is regained whenever it is true, also in dead time
    elif not paused:p.unmarked_ms[j]+=dt
    elif self.c4_occ and dt>0 and p.zone_fouled[j]>s.live_ms:p.zone_fouled[j]+=dt #C4.0: a called defender who cannot move (frozen, or in recognised tackle recovery) is not using his compliance time
  if watch and self.c3b and self.assume['exit_protection']:self.exit_watch()
 def strip(self,actor,target,witnessed=False):
  s=self.s
  if s.ball.carrier!=target:return False
  if witnessed:
   #C3a: a strip scheduled by the kernel was lawful when scheduled. If a freeze or exclusion has intervened it simply does not happen;
   #a stale prediction must not be turned into an ineligible-contact foul.
   if not(self.eligible(s.players[actor])and self.eligible(s.players[target])):
    self.emit('superseded_observation','16.1-16.2',kind='strip',actor=actor,target=target);return False
  elif not self.engage(actor,target,'tackle'):return False
  self.release(target,(s.players[target].vx,s.players[target].vy,0),'loose',forced=True)
  s.ball.scoring=True #A legal strip is a fumble, not a mandatory ineligible release.
  self.emit('strip','6.4;5.2',actor=actor,target=target);return True
 def go_down(self,p):
  """C3b: an athlete goes to ground. He keeps his horizontal velocity and slides, slowed by ground friction
  (slide_friction x g). He can begin to rise once he is sliding no faster than get_up_max_slide_mps, and rising takes
  get_up_time_s x (1.5 - balance). Nothing else acts on a grounded athlete (he is not a solid body and cannot be held), so the
  instant he is upright is known when he goes down. An athlete already down is not put down again."""
  s=self.s;A=self.assume
  if p.posture=='grounded'and s.now<p.next_action:return
  v=norm(p.vx,p.vy);a=A['slide_friction']*A['gravity'];slide=max(0.,v-A['get_up_max_slide_mps'])/a if a>0 else 0.;rise=A['get_up_time_s']*(1.5-p.a.balance)
  p.posture='grounded';p.down_at=s.now;p.next_action=s.now+int(math.ceil(1000*(slide+rise)-1e-9))
  self.emit('c3_down','C3b-1',player=p.id,speed_mps=round(v,3),slide_ms=round(1000*slide,1),rise_ms=round(1000*rise,1),upright_at=p.next_action)
 def grounded(self,pid):
  s=self.s;p=s.players[pid]
  if self.c3b:self.go_down(p)
  else:p.posture='grounded';p.next_action=s.now+800
  if s.ball.mode==BallMode.CONTESTED:self.held();return
  if s.ball.carrier==pid:
   if s.phase==Phase.PENALTY:self.finish_penalty(0);return
   self.release(pid,(p.vx,p.vy,0),'loose',forced=True)
  self.emit('grounded','6.8',player=pid)
 def freeze(self,pid,arrow=None,panel=True,direct=True,in_range=True):
  s=self.s;p=s.players[pid]
  if s.phase==Phase.FLIGHT or not self.live():return False
  protected_keeper=p.role=='keeper'and self.zone(p.x,p.y)==s.own_zone(p.team)
  broad=self.config.get('ruleset','1.0.1')=='1.0.2'
  valid=panel and direct and in_range and self.eligible(p)and not protected_keeper and s.now>p.immune_until and (broad or s.ball.carrier==pid)
  if not valid:self.emit('inert_impact','3.6;7.1',player=pid,arrow=arrow);return False
  was_carrier=s.ball.carrier==pid
  if was_carrier:self.release(pid,(p.vx,p.vy,p.vz),'loose',forced=True)
  p.freeze_until=s.now+5000;p.immune_until=s.now+15000
  s.engagements={k:e for k,e in s.engagements.items()if pid not in(k[0],k[1])}
  self.emit('freeze','WR-02;7.1–7.4'if broad else'7.1–7.4',player=pid,arrow=arrow,until=p.freeze_until,immune_until=p.immune_until,was_carrier=was_carrier);return True
 def archer_in_lane(self,p):
  low=self.s.ends[p.team]==0
  return (0<=p.x<=50 and-10<=p.y<=-3)if low else(50<=p.x<=100 and 103<=p.y<=110)
 def shoot_arrow(self,pid,target,velocity,origin=None):
  s=self.s;p=s.players[pid];q=s.quivers[p.team]
  not_live=not self.live()or s.phase==Phase.OPENING and s.owner is None
  if q.loaded>0 and q.spent<q.allocation:
   q.loaded-=1;q.spent+=1
  else:self.illegal(pid,'ammunition');return False
  if not_live:self.illegal(pid,'early_arrow');return False
  if p.role!='archer'or not self.eligible(p,False)or not self.archer_in_lane(p):self.illegal(pid,'archer_lane');return False
  point=origin or(p.x,p.y,.72*p.a.height)
  if target=='ball':pos=(s.ball.x,s.ball.y,s.ball.z);legal=s.ball.carrier is None and not(s.recovery and s.phase==Phase.AWARD) #C2: an awarded recovery ball is not a legal intended target
  else:
   t=s.players[target];pos=(t.x,t.y,t.z+.55*t.a.height)
   legal=t.team!=p.team and self.eligible(t)and s.now>t.immune_until and not(t.role=='keeper'and self.zone(t.x,t.y)==s.own_zone(t.team))
  d=math.dist(point,pos)
  if not legal or not(10<=d<=70):self.illegal(pid,'archery_target');return False
  speed=math.sqrt(sum(v*v for v in velocity))
  if speed>self.pocket.get("arrow_limit",30)+1e-6 or .5*.042*speed*speed>max(20,.5*.042*self.pocket.get("arrow_limit",30)**2)+1e-6:self.illegal(pid,'arrow_speed');return False
  if s.now<q.reload_until or s.now-q.last_release<2000:
   self.illegal(pid,'ammunition');return False
  q.last_release=s.now
  ar=Arrow(self.next_arrow,p.team,pid,target,*point,*velocity,point,s.now);self.next_arrow+=1;s.arrows.append(ar)
  self.emit('arrow_release','3.7–3.8',arrow=ar.id,player=pid,target=target,velocity=list(velocity),range=d,remaining=q.allocation-q.spent);return ar
 def reload(self,pid):
  s=self.s;p=s.players[pid];q=s.quivers[p.team];low=s.ends[p.team]==0
  service=(-10<=p.y<=-5)if low else(105<=p.y<=110)
  if p.role!='archer'or not self.eligible(p,False)or not service or q.spent>=q.allocation:return False
  if s.now<q.reload_until:return False
  q.reload_until=s.now+5000;q.loaded=0
  self.emit('reload_start','3.8',player=pid,ready=q.reload_until);return True
 def arrow_impact(self,arrow_id,target,panel=True,kind='player'):
  s=self.s;ar=next((a for a in s.arrows if a.id==arrow_id),None)
  if ar is None or not ar.live:return False
  ar.live=False
  if kind=='player':
   p=s.players[target];d=math.dist(ar.origin,(ar.x,ar.y,ar.z))
   if p.team==ar.team:self.emit('inert_impact','3.7;7.1',player=target,arrow=ar.id,reason='teammate');return False
   return self.freeze(target,ar.id,panel,ar.first_impact,10<=d<=70)
  if kind=='ball'and s.recovery and s.phase==Phase.AWARD:
   #C2: a previously legal arrow displaces the awarded ball. Neutral interruption; original spot; at least two seconds on resumption.
   self.emit('arrow_ball','7.1',arrow=ar.id,recovery=True);self.restore_recovery('incidental_arrow',remaining=max(2000,s.award_deadline-s.now));return False
  if kind=='ball'and(self.live()or s.phase==Phase.FLIGHT):
   s.ball.version+=1;s.ball.vx+=ar.vx*.07;s.ball.vy+=ar.vy*.07;s.ball.vz+=ar.vz*.07
   s.ball.last_touch=ar.team;self.emit('arrow_ball','7.1',arrow=ar.id)
  else:self.emit('arrow_stop','3.9',arrow=ar.id,kind=kind)
  return False
 def award(self,team,x,y,reason,foul=False,fresh=False,normalize=True):
  s=self.s
  if s.extension and team!=s.extension_team:return self.end_period()
  if team is None:team=s.alternate
  old=s.owner;keep=None
  if s.recovery and s.recovery['team']==team:
   #C2: a neutral or same-team stoppage during a first-tackle recovery restores the recovery at its original spot.
   #A failed advantage is different: play returns to the foul instant, so the recovery is superseded. So is it by a fresh possession (after a penalty).
   if reason!='advantage_recalled'and not fresh:return self.restore_recovery(reason,floor=foul)
   self.emit('recovery_superseded','C2-3.2',reason=reason);s.recovery=None
  if self.c2_any and s.phase==Phase.DEAD and s.restart and s.restart.kind!='free_pass'and s.restart.team==team and not fresh and reason!='advantage_recalled':
   keep=s.restart;x,y=keep.x,keep.y;normalize=False #C2: an inbound or a restored recovery is retaken at its own mark, never relocated
  self.new_owner(team,reason)
  if fresh and old==team:self.c2_new_possession(old,team,reason) #C2: a fresh clock for the same team (after a goal against it, or a penalty) is a new possession
  if fresh:s.possession_ms=self.play_ms
  elif old==team and foul:s.possession_ms=min(self.play_ms,max(20000,s.possession_ms))
  if normalize:x,y=restart_point(x,y,self.s.keeper_zone_radius)
  s.phase=Phase.DEAD;s.ball.version+=1;s.ball.carrier=None;s.ball.mode=BallMode.DEAD;s.ball.contested=();s.contested_until=None;s.ball.x=x;s.ball.y=y;s.ball.z=.1075;s.ball.vx=s.ball.vy=s.ball.vz=0;s.ball.scoring=False;s.ball.last_releaser=None
  s.restart=Restart(team,x,y,reason,created_at=s.now);s.tail_until=None;s.award_deadline=None;s.engagements.clear();s.stoppages+=1
  if keep:r=s.restart;r.kind=keep.kind;r.clearance=keep.clearance;r.remaining=keep.remaining;r.taker_spot=keep.taker_spot;r.note=keep.note
  for ar in s.arrows:ar.live=False
  self.flush_discipline()
  if self.terminal_grounds:return #C4.0: the match is about to end at this instant; no restart is announced
  self.emit('restart_awarded','10.2–10.6',team=team,spot=[x,y],reason=reason)
 def ready(self,taker):
  s=self.s;r=s.restart
  if s.phase!=Phase.DEAD or not r:return False
  p=s.players[taker]
  if r.kind=='recovery':return False
  able=self.eligible(p)or(r.kind=='inbound'and p.eligible(s.now)and p.role!='archer'and p.posture!='grounded') #C2: the inbound taker stands just outside the field
  if p.team!=r.team or not able or norm(p.x-r.x,p.y-r.y)>.5:return False
  if any(q.team!=r.team and self.eligible(q)and q.role!='archer'and norm(q.x-r.x,q.y-r.y)<r.clearance-1e-6 for q in s.players.values()):return False
  r.ready_at=s.now;r.taker=taker;self.emit('restart_ready','10.3',taker=taker);return True
 def restart_release(self,taker,velocity,target=None,method='hand'):
  s=self.s;r=s.restart
  if not r or s.phase!=Phase.DEAD:return False
  p=s.players[taker]
  able=self.eligible(p)or(r.kind=='inbound'and p.eligible(s.now)and p.role!='archer'and p.posture!='grounded')
  if r.ready_at is None or s.now-r.ready_at>5000 or r.taker!=taker or method!='hand' or norm(p.x-r.x,p.y-r.y)>.5 or not able:
   self.award(s.other(r.team),r.x,r.y,'restart_fault',fresh=True);return False
  if math.sqrt(sum(v*v for v in velocity))>self.pocket.get("ball_limit",40)+1e-6:self.illegal(taker,'ball_release_speed');return False
  if any(q.team!=r.team and self.eligible(q)and q.role!='archer'and norm(q.x-r.x,q.y-r.y)<r.clearance-1e-6 for q in s.players.values()):
   if r.kind=='inbound':
    #C2: retake at the same mark, no relocation, with the clock floor and the ordinary technical discipline for the nearest encroacher
    q=min((q for q in s.players.values()if q.team!=r.team and self.eligible(q)and q.role!='archer'and norm(q.x-r.x,q.y-r.y)<r.clearance-1e-6),key=lambda q:(norm(q.x-r.x,q.y-r.y),q.id))
    self.emit('inbound_encroachment','C2-4.1',player=q.id,distance=round(norm(q.x-r.x,q.y-r.y),3));self.pending_discipline.append((q.id,'warning',False));self.inbound(r.team,r.x,r.y,'defensive_restart_fault',foul=True)
   else:self.award(r.team,r.x,r.y,'defensive_restart_fault',foul=True)
   return False
  if r.reason=='held_ball':s.alternate=s.other(r.team)
  b=s.ball;b.version+=1;b.mode=BallMode.PASS;b.x=r.x;b.y=r.y;b.z=p.hand_height;b.vx,b.vy,b.vz=velocity;b.release_time=s.now;b.last_touch=p.team;b.last_releaser=taker;b.scoring=False;b.intended=target
  s.phase=Phase.LIVE;s.restart=None
  self.emit('restart_release','10.4',taker=taker,target=target,velocity=list(velocity))
  if r.kind!='inbound':self.reconstruction_check(p,'restart_release') #C2: an ordinary in-field release beyond the arc clears; the inbound itself does not
  return True
 def boundary(self,x=None,y=None,carrier=None):
  s=self.s;b=s.ball
  if s.phase in(Phase.DEAD,Phase.BREAK,Phase.FINAL,Phase.SUSPENDED):return
  x=b.x if x is None else x;y=b.y if y is None else y
  if s.phase==Phase.PENALTY:self.finish_penalty(0);return
  if s.phase==Phase.FLIGHT:self.end_flight('out',x,y);return
  if s.phase==Phase.AWARD:team=s.owner
  else:team=s.other(b.last_touch)if b.last_touch else None
  if s.phase==Phase.OPENING and team is None:return self.failed_hunt('unclaimed_out')
  b.mode=BallMode.OUT;b.carrier=None
  self.emit('boundary','10.1',crossing=[x,y],last_touch=b.last_touch,carrier=carrier)
  self.award(team,x,y,'boundary')
 def goal(self,defending,y=None,z=None):
  s=self.s;b=s.ball
  if s.phase not in(Phase.LIVE,Phase.OPENING,Phase.AWARD,Phase.FLIGHT,Phase.PENALTY):return False
  y=b.y if y is None else y;z=b.z if z is None else z
  if not legal_goal(y,z,b.radius):self.boundary(b.x,y);return False
  rc=s.reconstruction
  if rc and s.penalty is None and s.own_zone(defending)==rc['zone']:
   #C2: while the attacked zone is uncleared no goal counts in that aperture, including a deflected own goal.
   self.count('uncleared_no_goals');self.emit('no_goal','C2-4.2',reason='reconstruction_uncleared');self.boundary(b.x,y);return False
  if s.phase==Phase.AWARD or not b.scoring:
   self.emit('no_goal','9.1',reason='ineligible_ball');self.boundary(b.x,y);return False
  p=s.players.get(b.carrier)
  if p and(not self.eligible(p)or p.posture=='grounded'):
   self.emit('no_goal','9.1;16.2',reason='ineligible_carrier');self.boundary(b.x,y);return False
  scoring=s.other(defending)
  carried=bool(p and p.team==scoring and b.control_time<s.now)
  origin=getattr(b,'pocket_origin',None)
  outside=bool(not carried and origin and(self.territory(scoring,*origin)=='outside_release'if self.c4c2 else self.zone(*origin)!=s.own_zone(defending))) #C4c2 review: on the arc is outside
  own_goal=bool(not carried and ((p and p.team==defending) or getattr(b,'pocket_release_team',scoring)==defending))
  if outside and not own_goal and self.pocket.get('zone_only',False) and s.penalty is None:
   self.emit('no_goal','Pocket-S1',reason='outside_release',origin=origin);self.boundary(b.x,y);return False
  method='carry' if carried else 'own_goal' if own_goal else 'outside_release' if outside else 'inside_release'
  points=self.pocket.get('carry_points',5) if carried else self.pocket.get('outside_points',3) if outside and not own_goal and s.penalty is None else self.pocket.get('release_points',3)
  carry_ok=self.c4b and self.pocket.get('carry_value',0)>0 and carried #C4b: Carry enabled (configurations B and C)
  if self.pocket.get('release_territories')and carry_ok:
   #C4b, the Lead's position accepting Claude's Carry eligibility: eligible secure control clearly before the whole ball crossed
   #(control from an earlier millisecond); the carrier need not cross. A grounding or freeze at the crossing, or a catch at it,
   #is not a Carry (the first is refused above as an ineligible carrier; the second is a released ball, handled in batch).
   method='carry';points=self.pocket['carry_value']
  elif self.pocket.get('release_territories'):
   if p and p.team==scoring:
    self.emit('no_goal','Pocket-S4',reason='release_required')
    if s.penalty is not None:self.finish_penalty(0)
    else:self.boundary(b.x,y)
    return False
   if not own_goal and origin is None:
    self.emit('no_goal','Pocket-S4',reason='missing_release_origin');self.boundary(b.x,y);return False
   method='own_goal' if own_goal else self.territory(scoring,*origin)
   points=self.pocket.get('release_points',9) if own_goal or s.penalty is not None else self.territory_points(method)
   dt_=(getattr(b,'c4c2_def',None)or[])[getattr(b,'c4c2_off_i',0):]if self.c4c2 else None
   if self.c4c2 and own_goal and p is None and dt_:
    #C4c2: the team's own flight redirected into its own goal by an opponent without secured control. OPEN (the Lead): not a true
    #own goal (an opponent intervened) and not settled by the failed-save ruling. Prototype, switch reversal_rule: 0 = the own-goal
    #value (the zone-release value) credited to the opponents, recorded as its own method; 1 = the redirecting opponent's touch is
    #valued as an offensive play from his support foot.
    method='reversal';last=dt_[-1]
    if self.reversal_rule==1 and s.penalty is None:points=self.territory_points(self.territory(scoring,last[1],last[2]))
  if s.penalty is not None:self.finish_penalty(points);return True
  if s.advantage:s.advantage=None;self.emit('advantage_realized','11.2',method='goal')
  s.score[scoring]+=points
  if self.c4c2 and method!='carry':
   dl=getattr(b,'c4c2_def',None)or[]
   c2rec={'flight_team':getattr(b,'pocket_release_team',None),'last_offensive_toucher':getattr(b,'c4c2_off',None),'defensive_touches':[list(x)for x in dl],
          'offensive_goal_through_defensive_touch':bool(dl)and method not in('own_goal','reversal')}
  else:c2rec={}
  cause=self.emit('goal','9.1–9.3',team=scoring,points=points,defending=defending,method=method,release_origin=origin,control_time=b.control_time,**c2rec,
                  **({'origin_witness':None if method=='carry'else getattr(b,'c4b_origin',None),'launch_point':None if method=='carry'else getattr(b,'c4b_launch',None),
                      'origin_to_goal_m':None if method=='carry'or origin is None else round(norm(origin[0]-s.attack_goal(scoring),origin[1]-50),3)}if self.c4b else{}))
  s.last_score_cause=cause;self.score_history.append({'cause':cause,'team':scoring,'points':points,'t_ms':s.now})
  self.minor_goal_release(defending)
  if s.extension:return self.end_period()
  if s.game_ms<=0:return self.end_period()
  offset=max(25,s.keeper_zone_radius+.5);x=s.ends[defending]+(offset if s.ends[defending]==0 else-offset)
  self.award(defending,x,50,'goal',fresh=True,normalize=False);return True
 def illegal(self,pid,reason):
  p=self.s.players[pid]
  if reason=='ineligible_ball_action'and p.active and p.frozen(self.s.now):reason='frozen_participation'
  self.foul(pid,None,reason,major=reason=='ineligible_ball_action')
 def foul(self,actor,victim=None,reason='hold',major=False,danger=False,penalty=False,certain=False,carry=False,advantage=False,disqualify=False):
  s=self.s;a=s.players[actor];victim_team=s.players[victim].team if victim else s.other(a.team)
  if s.phase==Phase.FINAL:return
  if danger:
   a.dangerous_majors=getattr(a,'dangerous_majors',0)+1
   if a.dangerous_majors>=2:disqualify=True
  self.emit('foul','11;15',actor=actor,victim=victim,reason=reason,major=major,danger=danger,penalty=penalty)
  sanction='dq'if disqualify else'major'if major or danger or reason in('hold','deliberate_delay','transition_foul')else'minor'if reason in('illegal_tackle','late_hold','archery_target','archer_lane','ammunition','arrow_speed','early_arrow')else'warning'
  #C4.0, decided by DreLen on 7 October: a team does not forfeit off Keeper Zone violations. Builder's reading, provisional until he
  #confirms it: neither kind of zone expiry enters the warning and exclusion ladder at all. The category is narrow: the attacking
  #residence expiry and the defending unmarked-allowance expiry (and the proposed intervention penalty, which is the same incident).
  #Exit obstruction, recovery interference, the Keeper's ball-hold and every contact foul keep their own discipline.
  if self.c4_zone and reason in('zone_expiry','zone_unmarked','zone_intervention'):sanction=None
  if s.phase==Phase.PENALTY:
   pen=s.penalty
   if a.team!=pen['team']and pen['keeper_fouls']>=1 and sanction not in('dq',None):sanction='major'
   self.discipline(actor,sanction,permanent=disqualify)
   if a.team==pen['team']:self.finish_penalty(0)
   else:
    pen['keeper_fouls']+=1
    if pen['keeper_fouls']>=2:self.finish_penalty(self.c4b_auto_points(True)if self.c4b else self.pocket.get("release_points",9) if self.pocket.get("release_territories") else self.pocket.get("carry_points",5))
    else:self.reset_penalty()
   return
  spot=(s.ball.x,s.ball.y)
  if victim and s.attack_sign(victim_team)*(s.players[victim].x-spot[0])>0:spot=(s.players[victim].x,s.players[victim].y)
  if advantage and not danger and s.owner==victim_team and not certain and not penalty and self.live():
   if s.advantage is None:
    s.advantage={'team':victim_team,'g':s.game_ms,'p':s.possession_ms,'spot':spot,'until':s.now+3000,'origin_x':s.ball.x}
    if self.c2_any:s.advantage['c2']=self.c2_snapshot()
   if sanction is not None:self.pending_discipline.append((actor,sanction,disqualify))
   self.emit('advantage','11.2',team=victim_team);return
  restore=None
  if s.advantage:
   #Rulebook 11.3: an offence before the advantage is realised ends play and the earlier defensive foul is enforced, also when the
   #later offender is the advantaged team (who is still sanctioned below). This is retained behaviour, not a C2 change.
   adv=s.advantage;s.game_ms=adv['g'];s.possession_ms=adv['p'];victim_team=adv['team'];spot=adv['spot'];s.advantage=None;restore=(adv,s.owner!=adv['team'])
   if s.recovery and'c2'in adv:self.emit('recovery_superseded','C2-3.2',reason='foul_during_advantage');s.recovery=None
  self.discipline(actor,sanction,permanent=disqualify)
  if s.phase==Phase.FINAL:return
  if certain:
   self.penalty_goal(victim_team,self.c4b_auto_points(carry)if self.c4b else self.pocket.get("release_points",9) if self.pocket.get("release_territories") else self.pocket.get("carry_points",5) if carry else self.pocket.get("release_points",3));return
  if penalty:self.start_penalty(victim_team);return
  if s.game_ms<=0 and not s.extension:
   s.extension=True;s.extension_team=victim_team;s.possession_ms=10000
  elif s.extension:s.possession_ms=10000
  if s.recovery and s.recovery['team']==victim_team and not s.extension:
   #C2: a defensive foul during a first-tackle recovery restores the recovery at its original spot, with the defensive-foul clock floor.
   self.restore_recovery('defensive_foul:'+reason,floor=True);return
  self.award(victim_team,*spot,'foul',foul=not s.extension)
  if restore:self.c2_restore(restore[0],restore[1],'foul_during_advantage')
  if s.extension:s.possession_ms=10000
 def flush_discipline(self,resolve=True):
  """Sanctions deferred behind an advantage are all administered at the stoppage, as one instant (rulebook 11.2: 'applied at
  the next stop'). C4.0: a ground for ending the match that arises while they are administered is held until every one of
  them is on the record, and the grounds are then judged together (terminal_resolve)."""
  pending=self.pending_discipline;self.pending_discipline=[];self.terminal_hold+=1
  try:
   for args in pending:self.discipline(args[0],args[1],args[2])
  finally:self.terminal_hold-=1
  if resolve and not self.terminal_hold:self.terminal_resolve()
 def terminal_ground(self,team,reason):
  #C4.0: a team can no longer continue (rulebook 1.4). One ground per team per instant.
  if all(t!=team for t,_ in self.terminal_grounds):self.terminal_grounds.append((team,reason))
  if not self.terminal_hold:self.terminal_resolve()
 def terminal_resolve(self):
  """C4.0: judge the grounds raised at one instant, from the rulebook:
  1. Both teams unable to continue: abandoned, referred for replay, no winner (1.4, 18.8).
  2. One team unable to continue: that team forfeits (1.4, 18.6).
  The order in which the sanctions happened to be queued decides nothing. A horn that would decide the match by score gives
  no exemption (C4.0 r2, the Lead's audit: 1.4 makes insufficient slots after exclusions a forfeit; that amendment is DreLen's)."""
  g=self.terminal_grounds;self.terminal_grounds=[]
  if not g:return False
  if len(g)>1:
   self.emit('abandoned','1.4;18.8',reason='both_teams_unable_to_continue',grounds=[list(x)for x in g]);self.complete('abandoned_replay')
  self.forfeit(*g[0])
 def discipline(self,pid,kind,permanent=False):
  s=self.s;p=s.players[pid]
  if kind is None:return #C4.0: an offence that carries no personal sanction (a Keeper Zone expiry under the ruling of 7 October)
  if kind=='warning':
   if 'technical'in s.warning[p.team]:kind='minor'
   else:s.warning[p.team].add('technical');self.emit('warning','15',player=pid);return
  if kind=='minor':p.minor_count+=1;ms=60000
  else:p.major_count+=1;ms=120000
  dq=kind=='dq'or p.major_count>=2 or p.minor_count>=3
  if dq:ms=120000
  was_active=p.active;p.disqualified=dq;was_role=p.role;p.active=False
  if was_active and was_role=='field':self.slot_vacate(p)
  previous=next((d for d in self.debts if d['player']==pid and(d['remaining']>0 or d['permanent'])),None)
  if previous:
   previous['remaining']=max(previous['remaining'],ms)if dq else previous['remaining']+ms;previous['permanent']|=permanent
   if kind!='minor':previous['kind']=kind
   ms=previous['remaining']
  else:self.debts.append({'team':p.team,'player':pid,'remaining':ms,'permanent':permanent,'kind':kind,'seq':self.event_seq})
  p.exclusion_ms=ms
  if was_role in('keeper','archer')and not previous:
   eligible=[q for q in s.players.values()if q.team==p.team and q.id!=pid and q.eligible(s.now)and q.role=='field']
   if eligible:
    q=max(eligible,key=lambda q:q.a.keeper_skill if was_role=='keeper'else q.a.archery_accuracy)
    if self.c2_occ:self.slot_vacate(q);self.slot_inherit(p,q) #C2: the promoted player takes the specialist slot's state; his own field slot is left for its replacement
    q.role=was_role;q.x=p.x;q.y=p.y;q.vx=q.vy=0
    self.emit('specialist_replacement','14.3',old=pid,new=q.id,role=was_role)
   else:self.terminal_ground(p.team,'no_specialist');return
  self.emit('discipline','15.2–15.4',player=pid,kind=kind,disqualified=dq,permanent=permanent,duration=ms)
  if sum(1 for d in self.debts if d['team']==p.team and(d['permanent']or d['remaining']>0))>3:self.terminal_ground(p.team,'minimum_lineup')
 def same_incident_discipline(self,pid,kinds,permanent=False):
  rank={'warning':0,'minor':1,'major':2,'dq':3}
  self.discipline(pid,max(kinds,key=lambda k:rank[k]),permanent)
  self.emit('multiple_sanctions_recorded','15.3',player=pid,sanctions=kinds)
 def minor_goal_release(self,team):
  choices=[d for d in self.debts if d['team']==team and d['kind']=='minor'and d['remaining']>0 and not d['permanent']]
  if choices:
   d=min(choices,key=lambda d:(d['remaining'],d['seq']));d['remaining']=0;self.s.players[d['player']].exclusion_ms=0;self.emit('minor_released','15.6',player=d['player'])
 def sub(self,out_id,in_id):
  s=self.s;o,n=s.players[out_id],s.players[in_id]
  if o.team!=n.team or not o.active or n.active or not n.available or n.injured or n.disqualified or n.exclusion_ms>0:return False
  specialist=o.role in('keeper','archer')
  if specialist and s.phase not in(Phase.DEAD,Phase.BREAK):return False
  if s.ball.carrier==out_id:return False
  low=s.ends[o.team]==0;gate=(70,80,0)if low else(20,30,100)
  if not specialist and(not gate[0]<=o.x<=gate[1]or not(o.y+o.radius<0 if low else o.y-o.radius>100) or not gate[0]<=n.x<=gate[1]or abs(n.y-gate[2])>2 or(n.y>0 if low else n.y<100)):return False
  oldrole=o.role;o.active=False;n.active=True;n.role=oldrole;n.slot=o.slot
  n.zone_ms=list(o.zone_ms);n.outside_ms=list(o.outside_ms)
  #C2: the replacement inherits the slot's stored counts, unmarked allowance and any pending violation. Entering is not an arc exit.
  self.slot_inherit(o,n)
  #Retained from Pocket 1.1: a live freeze and the Keeper hold timer pass to the replacement. An incoming later freeze deadline is not shortened.
  n.freeze_until=max(n.freeze_until,o.freeze_until)
  n.keeper_hold_ms=o.keeper_hold_ms
  n.x,n.y=(o.x,o.y)if specialist else((gate[0]+gate[1])/2,.2 if low else 99.8)
  self.emit('substitution','14.1–14.3',out=out_id,incoming=in_id,role=oldrole,freeze_until=n.freeze_until);return True
 def replace_unavailable_specialist(self,out_id,in_id):
  s=self.s;o,n=s.players[out_id],s.players[in_id]
  if s.phase not in(Phase.DEAD,Phase.BREAK)or o.active or o.role not in('keeper','archer')or o.team!=n.team or n.active or not n.available or n.injured or n.disqualified or n.exclusion_ms>0:return False
  n.role=o.role;n.active=True;n.x=o.x;n.y=o.y;n.freeze_until=o.freeze_until;n.zone_ms=list(o.zone_ms);n.vx=n.vy=0
  if self.c2_any:self.slot_inherit(o,n) #C2: the same slot inheritance as an ordinary substitution
  self.emit('specialist_replacement','14.3–14.4',old=o.id,new=n.id,role=n.role);return True
 def validate_lineup(self):
  problems=[]
  for team in('A','B'):
   roster=[p for p in self.s.players.values()if p.team==team];active=[p for p in roster if p.active]
   if len(roster)!=22:problems.append(team+': roster must contain22')
   if sum(p.role=='keeper'for p in active)!=1:problems.append(team+': exactly one active Keeper required')
   if sum(p.role=='archer'for p in active)!=1:problems.append(team+': exactly one active Archer required')
   if not 7<=sum(p.role=='field'for p in active)<=10:problems.append(team+': Field Player count outside7–10')
  self.emit('lineup_check','1.3–1.4',passed=not problems,problems=problems);return not problems
 def injury(self,pid,concussion=False):
  s=self.s;p=s.players[pid]
  if p.active and p.role=='field':self.slot_vacate(p)
  p.injured=True;p.available=False;p.active=False
  p.medical_return_live=s.live_ms+60000;p.no_day_return=concussion
  self.emit('injury','14.4',player=pid,concussion=concussion)
  self.safety_stop('injury')
 def medical_clear(self,pid):
  p=self.s.players[pid]
  if getattr(p,'no_day_return',False)or self.s.live_ms<getattr(p,'medical_return_live',0):return False
  p.injured=False;p.available=True;self.emit('medical_clear','14.4',player=pid);return True
 def safety_stop(self,reason='hazard'):
  s=self.s
  if s.phase==Phase.OPENING and s.owner is None:return self.failed_hunt(reason)
  if s.phase==Phase.FLIGHT:return self.end_flight(reason,s.ball.x,s.ball.y)
  self.award(s.owner or s.alternate,s.ball.x,s.ball.y,'safety_'+reason)
 def start_penalty(self,team,shootout=False):
  s=self.s
  runners=[p for p in s.players.values()if p.team==team and p.eligible(s.now)and p.role!='archer']
  keepers=[p for p in s.players.values()if p.team!=team and p.role=='keeper'and p.eligible(s.now)]
  if not keepers: #C4.0: rulebook 12.3, an eligible team-mate replaces a frozen or excluded Keeper for the run; only if there is none is it a forfeit
   keepers=sorted([p for p in s.players.values()if p.team!=team and p.available and not p.injured and not p.disqualified and p.exclusion_ms<=0 and not p.frozen(s.now)and p.role!='archer'],key=lambda p:(-p.a.keeper_skill,p.id))[:1]
  if not runners and not keepers: #C4.0: neither side can stage the run; that is both teams unable to continue, not a forfeit by the side tested first
   self.terminal_hold+=1;self.terminal_ground(team,'penalty_eligibility');self.terminal_ground(s.other(team),'penalty_eligibility');self.terminal_hold-=1
   if not self.terminal_hold:self.terminal_resolve()
   return
  if not runners or not keepers:self.forfeit(team if not runners else s.other(team),'penalty_eligibility');return
  if shootout:
   used=s.shootout['used'][team];all_roster=[p for p in s.players.values()if p.team==team and p.available and not p.injured and not p.disqualified and p.exclusion_ms==0]
   if len(used)>=len(all_roster):used.clear()
   runners=[p for p in all_roster if p.id not in used];runner=max(runners,key=lambda p:p.a.ball_handling+p.a.agility);used.append(runner.id)
  else:runner=max(runners,key=lambda p:p.a.ball_handling+p.a.agility)
  keeper=keepers[0]
  s.penalty={'team':team,'runner':runner.id,'keeper':keeper.id,'until':s.now+10000,'released':False,'keeper_fouls':0,'shootout':shootout,'runner_original_role':runner.role,'saved_active':{p.id:p.active for p in s.players.values()}}
  self.reset_penalty();self.emit('penalty_start','12.1–12.4',team=team,runner=runner.id,keeper=keeper.id,shootout=shootout)
 def reset_penalty(self):
  s=self.s;pen=s.penalty;team=pen['team'];r=s.players[pen['runner']];k=s.players[pen['keeper']]
  if not r.available or r.disqualified or r.exclusion_ms>0 or r.frozen(s.now):
   runners=[p for p in s.players.values()if p.team==team and p.eligible(s.now)and p.role!='archer']
   if not runners:return self.forfeit(team,'penalty_runner')
   r=max(runners,key=lambda p:p.a.ball_handling+p.a.agility);pen['runner']=r.id;pen['runner_original_role']=r.role
  if not k.available or k.disqualified or k.exclusion_ms>0 or k.frozen(s.now): #C4.0: frozen too (12.3)
   replacements=[p for p in s.players.values()if p.team==k.team and p.available and not p.disqualified and not p.injured and p.exclusion_ms==0 and not p.frozen(s.now)and p.role!='archer']
   if not replacements:return self.forfeit(k.team,'penalty_keeper')
   k=max(replacements,key=lambda p:p.a.keeper_skill);pen['keeper']=k.id
  if not r.active:
   outgoing=next((p for p in s.players.values()if p.team==r.team and p.active and p.role=='field'),None)
   if outgoing:outgoing.active=False
  r.active=k.active=True;r.role='field'if r.role=='archer'else r.role;k.role='keeper'
  r.x=s.attack_goal(team)-s.attack_sign(team)*25;r.y=50;r.vx=r.vy=0;k.x=s.attack_goal(team);k.y=50;k.vx=k.vy=0
  s.ball=Ball(mode=BallMode.CONTROLLED,x=r.x,y=50,z=r.hand_height,carrier=r.id,control_time=s.now-1,scoring=True,last_touch=team)
  s.owner=team;s.phase=Phase.PENALTY;pen['until']=s.now+10000;pen['released']=False;s.restart=None;s.engagements.clear();self.follow_carrier()
 def finish_penalty(self,points):
  s=self.s;pen=s.penalty
  if pen is None:return
  team=pen['team'];shootout=pen['shootout'];s.players[pen['runner']].role=pen.get('runner_original_role',s.players[pen['runner']].role)
  for pid,active in pen['saved_active'].items():
   p=s.players[pid];p.active=active and not p.disqualified and p.exclusion_ms<=0 and p.available
  s.penalty=None
  if shootout:
   so=s.shootout;so['attempts'][team]+=1;so['goals'][team]+=int(points>0)
   self.emit('shootout_attempt','18.2–18.4',team=team,success=points>0)
   self.next_shootout();return
  if points:
   s.score[team]+=points;cause=self.emit('penalty_goal_scored','12.4',team=team,points=points);self.score_history.append({'cause':cause,'team':team,'points':points,'t_ms':s.now})
  else:self.emit('penalty_failed','12.4',team=team)
  if s.game_ms<=0:return self.end_period()
  self.award(team,50,50,'penalty_retained',fresh=True,normalize=False)
 def penalty_goal(self,team,points):
  s=self.s;s.score[team]+=points;cause=self.emit('penalty_goal','12.2',team=team,points=points);self.score_history.append({'cause':cause,'team':team,'points':points,'t_ms':s.now})
  if s.game_ms<=0:return self.end_period()
  self.award(team,50,50,'penalty_retained',fresh=True,normalize=False)
 def timeout(self,team):
  s=self.s
  if s.phase!=Phase.DEAD or not s.restart or s.restart.ready_at is not None or s.timeouts[team]<=0:return False
  s.timeouts[team]-=1;s.restart.created_at+=60000;self.emit('timeout','5.7',team=team,until=s.now+60000);return True
 def start_flight(self,penalty=False):
  s=self.s;s.phase=Phase.FLIGHT;s.tail_until=s.now+3000;s.tail_owner=s.owner if not penalty else s.penalty['team']
  self.emit('finishing_flight','5.5',until=s.tail_until,penalty=penalty)
 def end_flight(self,reason,x,y):
  s=self.s
  self.emit('flight_ended','5.5–5.6',reason=reason)
  if s.penalty:return self.finish_penalty(0)
  if s.advantage:return self.recall_advantage()
  if s.game_ms<=0:return self.end_period()
  self.award(s.other(s.tail_owner),x,y,'possession_expiry',fresh=True)
 def recall_advantage(self):
  s=self.s;adv=s.advantage
  if not adv:return
  s.advantage=None;s.game_ms=adv['g'];s.possession_ms=adv['p'];changed=s.owner!=adv['team']
  if s.game_ms<=0:s.extension=True;s.extension_team=adv['team'];s.possession_ms=10000
  self.award(adv['team'],*adv['spot'],'advantage_recalled',foul=not s.extension)
  self.c2_restore(adv,changed,'advantage_recalled')
  if s.extension:s.possession_ms=10000
  self.emit('advantage_recalled','11.2;16.4',restored_g=s.game_ms,restored_p=s.possession_ms)
 def clock_expiry(self):
  s=self.s;b=s.ball
  if s.phase not in(Phase.LIVE,Phase.AWARD,Phase.OPENING,Phase.PENALTY):return
  if s.phase==Phase.PENALTY:
   if s.now<s.penalty['until']:return
   if b.carrier is None and b.z>b.radius and s.penalty['released']:self.start_flight(True)
   else:self.finish_penalty(0)
   return
  if s.game_ms>0 and s.possession_ms>0:return
  if s.extension and s.possession_ms>0:return
  if b.carrier is None and b.mode in(BallMode.PASS,BallMode.KICK,BallMode.SHOT,BallMode.LOOSE)and b.z>b.radius+1e-6:
   if s.reconstruction and s.game_ms<=0:self.emit('no_finishing_flight','C2-4.2',reason='reconstruction_uncleared') #C2: no score-based finishing flight for an uncleared ball at the horn
   else:self.start_flight();return
  if s.advantage:return self.recall_advantage()
  if s.game_ms<=0:return self.end_period()
  self.award(s.other(s.owner),b.x,b.y,'possession_expiry',fresh=True)
 def end_period(self):
  s=self.s
  if s.phase==Phase.FINAL:return
  s.extension=False;s.extension_team=None;s.advantage=None;s.tail_until=None;s.penalty=None;s.ball.carrier=None;s.ball.mode=BallMode.DEAD;s.restart=None;s.engagements.clear()
  s.tackle_count=0;s.recovery=None
  if s.reconstruction:self.end_reconstruction('period_end')
  self.flush_discipline();self.period_history.append({'period':s.period,'score':dict(s.score),'t_ms':s.now});self.emit('period_end','5;18',score=dict(s.score))
  if s.period<s.regulation_periods:
   s.period+=1;s.game_ms=s.period_seconds*1000
   if s.period==3:self.exchange_ends();s.timeouts={'A':2,'B':2};s.challenges={'A':1,'B':1}
   s.quivers={t:Quiver()for t in('A','B')}
   team=s.other(s.opening_team or'A')if s.period in(2,4)else(s.opening_team or'A')
   s.owner=None;self.award(team,50,50,'quarter_start',fresh=True,normalize=False);return
  if s.period==s.regulation_periods:
   if s.score['A']!=s.score['B']:return self.complete('regulation')
   s.period+=1;s.game_ms=s.overtime_seconds*1000;s.timeouts={'A':1,'B':1};s.challenges={'A':1,'B':1};s.quivers={t:Quiver(allocation=10)for t in('A','B')};s.opening_team=None;s.opening_failures=0;self.begin_hunt();self.emit('overtime_start','18.1');return
  if s.period==s.regulation_periods+1:
   s.period+=1;s.game_ms=s.overtime_seconds*1000;self.exchange_ends();s.quivers={t:Quiver(allocation=10)for t in('A','B')};s.owner=None;self.award(s.other(s.opening_team or'A'),50,50,'overtime_half',fresh=True,normalize=False);return
  if s.score['A']!=s.score['B']:return self.complete('overtime')
  s.shootout={'attempts':{'A':0,'B':0},'goals':{'A':0,'B':0},'used':{'A':[],'B':[]},'first':'A'};self.next_shootout()
 def exchange_ends(self):
  s=self.s;s.ends={t:100-x for t,x in s.ends.items()}
  for p in s.players.values():
   p.x=100-p.x;p.y=100-p.y;p.vx=-p.vx;p.vy=-p.vy
   ext=getattr(p,'c3_ext',None)
   if self.c3b and ext:p.c3_ext=(tuple((t,-x,-y,b)for t,x,y,b in ext[0]),(-ext[1][0],-ext[1][1],ext[1][2],ext[1][3])) #C3b: an imposed-velocity record turns with the velocity it describes
  self.emit('ends_exchanged','2.2;18.1')
 def next_shootout(self):
  s=self.s;so=s.shootout;aa,bb=so['attempts']['A'],so['attempts']['B'];ga,gb=so['goals']['A'],so['goals']['B']
  if aa==bb and aa>=5 and ga!=gb:return self.complete('shootout','A'if ga>gb else'B')
  if max(aa,bb)<=5 and(ga>gb+5-bb or gb>ga+5-aa):return self.complete('shootout','A'if ga>gb else'B')
  pair=min(aa,bb);first=so['first']if pair%2==0 else s.other(so['first']);team=first if aa==bb else('A'if aa<bb else'B')
  self.start_penalty(team,True)
 def complete(self,method,winner=None):
  """C4.0: the one place a result is committed. Exactly one match_complete. Sanctions still queued behind an advantage are
  written to the record without effect on the ladder. The call then unwinds (MatchFinal): nothing after it runs."""
  s=self.s
  if winner is None and method!='abandoned_replay':winner='A'if s.score['A']>s.score['B']else'B'
  if self.pending_discipline:
   self.emit('sanctions_not_administered','11.2;15',sanctions=[[a[0],a[1]]for a in self.pending_discipline if a[1]is not None],reason='match_ended_before_the_next_stop:'+method);self.pending_discipline=[]
  s.phase=Phase.FINAL;s.ball.mode=BallMode.DEAD;s.ball.carrier=None;s.restart=None
  s.result={'winner':winner,'method':method,'score':dict(s.score),'shootout':s.shootout['goals']if s.shootout else None}
  self.emit('match_complete','18.1–18.5',result=s.result);self.final_seq=self.event_seq
  raise MatchFinal()
 def forfeit(self,team,reason):
  s=self.s;win=s.other(team)
  if s.score[win]<=s.score[team]:s.score={team:0,win:5}
  self.emit('forfeit','18.6',team=team,reason=reason);self.complete('forfeit',win)
 def suspend(self,reason):
  s=self.s
  if s.phase==Phase.FINAL:return
  self.safety_stop(reason);s.suspended_at=s.now;s.phase=Phase.SUSPENDED;self.emit('suspended','7.6;18.8',reason=reason)
 def resume(self):
  s=self.s
  if s.phase!=Phase.SUSPENDED:return False
  if s.now-s.suspended_at>=86400000:
   self.emit('abandoned','18.8');self.complete('abandoned_replay') #C4.0 r2: the retained 24-hour abandonment is committed like any result: one match_complete, no winner
  pause=s.now-s.suspended_at
  for p in s.players.values():
   if p.freeze_until>s.suspended_at:p.freeze_until+=pause
   if p.immune_until>s.suspended_at:p.immune_until+=pause
  for q in s.quivers.values():
   if q.reload_until>s.suspended_at:q.reload_until+=pause
   q.last_release+=pause
  s.phase=Phase.DEAD;s.suspended_at=None;self.emit('resumed','18.8');return True
 def neutral_offset(self,actors,major=False):
  s=self.s;self.terminal_hold+=1
  try:
   for actor in actors:self.discipline(actor,'major'if major else'minor')
  finally:self.terminal_hold-=1
  if not self.terminal_hold:self.terminal_resolve() #C4.0: offsetting fouls are one instant (inside a held batch, the batch judges); if both teams fall below the minimum the match is abandoned, not forfeited by whoever was listed first
  if s.penalty:
   s.penalty['keeper_fouls']+=1
   if s.penalty['keeper_fouls']>=2:self.finish_penalty(self.c4b_auto_points(True)if self.c4b else self.pocket.get("release_points",9) if self.pocket.get("release_territories") else self.pocket.get("carry_points",5))
   else:self.reset_penalty();self.emit('penalty_retake','12.5',reason='simultaneous_independent_fouls')
  else:self.award(s.owner or s.alternate,s.ball.x,s.ball.y,'offsetting_fouls')
 def dispatch(self,event):
  self.cause={'kind':event.kind,'actor':event.actor,'target':event.target,'at':self.s.now};d=event.data;k=event.kind
  if d.get('c1_contact'):self.c1_commit(event)
  elif k=='acquire':
   if 'ball_point'in d:self.s.ball.x,self.s.ball.y,self.s.ball.z=d['ball_point']
   self.acquire(event.actor)
  elif k=='release':self.release(event.actor,tuple(d['velocity']),d.get('kind','pass'),event.target)
  elif k=='touch':
   self.touch(event.actor,d.get('deliberate',True))
   if 'velocity'in d and self.s.ball.carrier is None:
    self.s.ball.vx,self.s.ball.vy,self.s.ball.vz=d['velocity'];self.s.ball.version+=1
    if 'ball_point'in d:self.s.ball.x,self.s.ball.y,self.s.ball.z=d['ball_point']
  elif k=='tackle':
   if self.s.players[event.target].frozen(self.s.now):self.emit('tackle_cancelled','7.4;16.2',actor=event.actor,target=event.target)
   elif'c3'in d:
    #C3b: everyone who had a material lawful hold on the carrier at the grounding (grip at or above the tackle threshold), or was in
    #lawful contact with him then and had lawfully put a material load on his balance, is owed the time to disengage from a
    #first-tackle recovery, not only the one credited with the tackle. Being within reach with a token grip is not enough.
    if self.c3b:self.grace=sorted({h['player']for h in d['c3'].get('holders',[])if h['grip']>=self.assume['tackle_grip_threshold']}|{q for q,v in d['c3'].get('lawful_supplied',{}).items()if q in d['c3'].get('in_lawful_contact',[])and v>=self.assume['contact_foul_min_shock']})
    self.emit('c3_grounding','C3-6.7',counted=True,**d['c3']);self.tackle(event.actor,event.target,d.get('body','knee'),witnessed=True);self.grace=[]
   else:self.tackle(event.actor,event.target,d.get('body','knee'))
  elif k=='ground':
   p=self.s.players[event.actor]
   if'c3'in d:
    #C3a: a physical grounding that is not a counted tackle. A carrier still in control makes the existing forced release.
    if not p.active or p.posture=='grounded':self.cause=None;return
    self.emit('c3_grounding','C3-6.7',counted=False,**d['c3'])
   self.grounded(event.actor)
  elif k=='note':self.emit(d['event'],d.get('rule','C3'),**d['data']) #C3a: a kernel log record, written at its own time inside the step
  elif k=='freeze':self.freeze(event.target,**d)
  elif k=='impact':self.arrow_impact(d['arrow'],event.target,d.get('panel',True),d.get('kind','player'))
  elif k=='goal':self.goal(d['defending'],d.get('y'),d.get('z'))
  elif k=='boundary':self.boundary(d.get('x'),d.get('y'),event.actor)
  elif k=='foul':self.foul(event.actor,event.target,**d)
  elif k=='clock':self.clock_expiry()
  elif k=='strip':self.strip(event.actor,event.target,witnessed='c3'in d)
  elif k=='frame':self.frame_contact(d.get('velocity'),d.get('point'))
  elif k=='strike':self.strike(event.actor,d['velocity'],d.get('kind','kick'))
  elif k=='held':self.held()
  elif k=='block':self.engage(event.actor,event.target,'block',d.get('surface','torso'))
  elif k=='safety':self.safety_stop(d.get('reason','hazard'))
  else:raise RulesError('Unknown event '+k)
  self.cause=None
 def batch(self,events):
  #C4.0: one batch is one instant. Grounds to end the match raised by any of its events are judged together at its end.
  self.terminal_hold+=1
  try:self.batch_events(events)
  finally:self.terminal_hold-=1
  if not self.terminal_hold:self.terminal_resolve()
 def batch_events(self,events):
  #Caller advances to the shared timestamp before the batch. Known time order is never reversed.
  events=[e for e in events if 'generation'not in e.data or e.data['generation']==self.s.ball.version]
  for e in events:e.data.pop('generation',None)
  if any(e.kind=='goal'for e in events)and self.live():
   for p in self.s.players.values():
    zn=self.zone(p.x,p.y)
    if p.active and not p.frozen(self.s.now)and zn is not None and p.zone_ms[zn]>=5000 and not(p.role=='keeper'and zn==self.s.own_zone(p.team)):
     events.append(Event('foul',p.id,data={'reason':'zone_expiry'}))
  simultaneous_fouls=[e for e in events if e.kind=='foul']
  if len({self.s.players[e.actor].team for e in simultaneous_fouls})==2 and len(events)==len(simultaneous_fouls) and len({bool(e.data.get('danger'))for e in simultaneous_fouls})==1:
   self.neutral_offset([e.actor for e in simultaneous_fouls],any(e.data.get('major')or e.data.get('danger')or e.data.get('reason')=='hold'for e in simultaneous_fouls));self.assert_invariants();return
  kept=[]
  for e in events:
   why=self.c1_reason(e)if e.data.get('c1_contact')else None
   if why is None:kept.append(e)
   else:self.c1_reject(e,why)
  events=kept
  catches=[e for e in events if e.kind=='acquire']
  if len({self.s.players[e.actor].team for e in catches})>1 and self.s.ball.carrier is None:
   if all(e.data.get('c1_contact')for e in catches):
    #C1 numerical convention, not a physical claim: secure contacts by opponents in the same clock millisecond cannot be ordered.
    self.s.ball.x,self.s.ball.y,self.s.ball.z=catches[0].data['ball_point']
    self.emit('simultaneous_contact','assumption:c1_same_millisecond',players=[e.actor for e in catches],points=[[round(v,3)for v in e.data['ball_point']]for e in catches])
    cs=getattr(self,'contact_stats',None)
    if cs is not None:cs['contacts_committed']+=1
   self.joint_control([e.actor for e in catches]);events=[e for e in events if e.kind!='acquire']
  original_scoring=self.s.ball.scoring;original_carrier=self.s.ball.carrier
  c2snap=self.c4c2_snap()if self.c4c2 else None
  goals=[e for e in events if e.kind=='goal'and legal_goal(e.data.get('y',self.s.ball.y),e.data.get('z',self.s.ball.z))]
  if goals:events=[e for e in events if not(e.kind=='boundary'and not e.actor and 0<=e.data.get('y',self.s.ball.y)<=100 and(e.data.get('x',self.s.ball.x)<0 or e.data.get('x',self.s.ball.x)>100))]
  priority={'safety':0,'boundary':4,'acquire':10,'freeze':20,'impact':20,'tackle':30,'ground':31,'release':35,'goal':40,'foul':50,'clock':60,'touch':15,'held':32,'strip':29,'block':12,'frame':13,'strike':35}
  def key(e):
   if e.kind=='foul'and(e.data.get('danger')or self.s.players[e.actor].team==self.s.owner):return 1
   return priority.get(e.kind,25)
  score_before=sum(self.s.score.values())
  for e in sorted(events,key=key):
   if e.data.get('control_witness') is not None and (self.s.ball.carrier!=e.target or self.s.ball.version!=e.data['control_witness']):
    self.emit('superseded_observation','16.1–16.2',kind=e.kind,actor=e.actor,target=e.target);continue
   if e.kind=='foul'and sum(self.s.score.values())>score_before and self.s.players[e.actor].team!=self.score_history[-1]['team']and not e.data.get('danger'):
    kind='major'if e.data.get('major')else'minor'
    if self.c4_zone and e.data.get('reason')in('zone_expiry','zone_unmarked'):kind=None #C4.0: no personal sanction for a zone expiry, on this path too
    self.discipline(e.actor,kind);self.emit('post_goal_discipline','16.2–16.3',player=e.actor,**({'kind':kind}if self.c4_zone else{}));continue
   if e.kind=='goal'and catches and original_carrier is None and original_scoring and self.s.ball.scoring and self.s.phase in(Phase.LIVE,Phase.FLIGHT):
    self.s.ball.carrier=None;self.s.ball.mode=BallMode.SHOT;self.s.ball.scoring=True
    if c2snap is not None:self.c4c2_unsnap(c2snap,[c.actor for c in catches])
   self.dispatch(e)
  self.assert_invariants()
 def elapse(self,dt,resolve=True):
  s=self.s
  if dt<0:raise RulesError('Negative time')
  active=s.phase in(Phase.LIVE,Phase.AWARD,Phase.OPENING)
  if self.c2_occ:self.occupancy(dt if active else 0) #exits are tracked in dead time too; time accrues only when live
  if s.reconstruction and s.ball.carrier and self.live():self.reconstruction_check(s.players[s.ball.carrier],'carried_out')
  #The caller slices at next_deadline(); this method will not silently cross one.
  if active:
   if not s.extension:s.game_ms=max(0,s.game_ms-dt)
   if s.owner is not None:s.possession_ms=max(0,s.possession_ms-dt)
   s.live_ms+=dt
   for d in self.debts:
    if not d['permanent'] and d['remaining']>0:
     d['remaining']=max(0,d['remaining']-dt);self.s.players[d['player']].exclusion_ms=d['remaining']
   for p in s.players.values():
    if not p.active:continue
    zn=self.zone(p.x,p.y)
    if p.frozen(s.now):continue
    for j in(()if self.c2_occ else(0,1)):
     exempt=p.role=='keeper'and j==s.own_zone(p.team)
     if zn==j and not exempt:p.zone_ms[j]+=dt;p.outside_ms[j]=0
     else:
      p.outside_ms[j]+=dt
      if p.outside_ms[j]>=3000:p.zone_ms[j]=0
    if p.role=='keeper':
     if zn==s.own_zone(p.team):
      p.keeper_outside_ms=0
      if s.ball.carrier==p.id:p.keeper_hold_ms+=dt
     else:
      p.keeper_outside_ms+=dt
      if p.keeper_outside_ms>=3000:p.keeper_hold_ms=0
  elif s.phase!=Phase.FINAL:s.dead_ms+=dt
  s.now+=dt
  if s.phase!=Phase.SUSPENDED:
   for t,q in s.quivers.items():
    if q.reload_until>=0:
     archer=next((p for p in s.players.values()if p.team==t and p.active and p.role=='archer'),None)
     inside=archer is not None and self.archer_in_lane(archer)and(archer.y<=-5 if s.ends[t]==0 else archer.y>=105)
     if not inside:q.reload_until=-1;self.emit('reload_cancelled','3.8',team=t)
    if q.reload_until>=0 and s.now>=q.reload_until:q.loaded=min(5,q.allocation-q.spent);q.reload_until=-1;self.emit('reload_complete','3.8',team=t,loaded=q.loaded)
  if resolve:self.resolve_timers()
 def next_deadline(self):
  s=self.s;values=[]
  if s.phase in(Phase.LIVE,Phase.AWARD,Phase.OPENING):
   if not s.extension:values.append(s.now+s.game_ms)
   if s.owner is not None:values.append(s.now+s.possession_ms)
   if s.opening_deadline:values.append(s.opening_deadline)
   if s.award_deadline:values.append(s.award_deadline)
   if s.contested_until:values.append(s.contested_until)
   if s.advantage:values.append(s.advantage['until'])
   for p in s.players.values():
    if p.active and not p.frozen(s.now):
     j=self.zone(p.x,p.y)
     if j is not None and not(p.role=='keeper'and j==s.own_zone(p.team)):
      values.append(s.now+max(0,5000-p.zone_ms[j]))
      if self.c2_occ and p.unmarked_ms[j]<5000:values.append(s.now+5000-p.unmarked_ms[j])
      if self.c4_occ and p.zone_fouled[j]>s.live_ms:values.append(s.now+p.zone_fouled[j]-s.live_ms) #C4.0: the end of a compliance time is resolved at its own millisecond
     if p.role=='keeper'and s.ball.carrier==p.id and j==s.own_zone(p.team):values.append(s.now+max(0,5000-p.keeper_hold_ms))
  if s.phase==Phase.REVIEW:values.append(s.review['until'])
  if s.phase==Phase.FLIGHT:values.append(s.tail_until)
  if s.phase==Phase.PENALTY:values.append(s.penalty['until'])
  if s.phase==Phase.DEAD and s.restart:
   values.append(s.restart.ready_at+5000 if s.restart.ready_at is not None else s.restart.created_at+30000)
  if s.phase!=Phase.SUSPENDED:
   for p in s.players.values():
    if p.freeze_until>s.now:values.append(p.freeze_until)
   for q in s.quivers.values():
    if q.reload_until>s.now:values.append(q.reload_until)
  return min(values)if values else s.now+1000000
 def resolve_timers(self):
  s=self.s
  if s.phase in(Phase.FINAL,Phase.SUSPENDED):return
  if self.live():
   for p in list(s.players.values()):
    if not p.active or p.frozen(s.now):continue
    j=self.zone(p.x,p.y)
    if j is not None and p.zone_ms[j]>=5000 and not(p.role=='keeper'and j==s.own_zone(p.team)):
     if self.c3b and self.c2_occ:self.zone_expiry_c3b(p,j);return
     if self.c2_occ:self.count('attacking_zone_expiries');self.emit('attacking_zone_expiry','C2-5',player=p.id,zone=j,possible_exit_interference=self.exit_interference(p,j))
     if self.c4_occ and self.zone_offset(p,'zone_expiry',p.zone_ms[j]):return #C4.0 r2 (15.5)
     self.illegal(p.id,'zone_expiry');return
    if self.c2_occ and not self.c4_occ and j is not None and p.unmarked_ms[j]>=5000 and p.team!=s.owner and s.advantage is None and s.live_ms>=p.zone_fouled[j]and not(p.role=='keeper'and j==s.own_zone(p.team)):
     #C2: defensive technical foul. Advantage where available; otherwise a free pass with the defensive-foul clock floor. The allowance is not renewed by the whistle.
     #He is liable again only after the live time physically needed to leave by the shortest route; regaining marking or leaving ends the violation.
     gx=0 if j==0 else 100;way=max(0,s.keeper_zone_radius-norm(p.x-gx,p.y-50))+.1
     p.zone_fouled[j]=s.live_ms+1+int(1000*(math.sqrt(2*way/max(1,p.a.acceleration))+p.a.decision_speed+.3));self.count('defensive_unmarked_expiries');self.emit('defensive_unmarked_expiry','C2-5',player=p.id,zone=j)
     self.foul(p.id,None,'zone_unmarked',advantage=True);return
    if p.role=='keeper'and s.ball.carrier==p.id and p.keeper_hold_ms>=5000:
     if self.c4_occ and p.team==s.owner and self.zone_offset(p,'keeper_hold',p.keeper_hold_ms):return #C4.0 r2 (15.5)
     self.illegal(p.id,'keeper_hold');return
   if self.c4_occ and self.zone_call():return #C4.0: after any attacking expiry or Keeper hold of this instant (retained order, not a new ruling)
   if s.recovery and s.phase==Phase.AWARD and self.recovery_watch():return
   if s.opening_deadline and s.now>=s.opening_deadline and s.owner is None:return self.failed_hunt('timeout')
   if s.award_deadline and s.phase==Phase.AWARD and s.now>=s.award_deadline:
    if s.recovery and self.recovery_blocked():return self.restore_recovery('unavoidable_obstruction') #C2: safe restoration when pickup was physically impossible
    return self.award(s.other(s.owner),*s.award_spot,'pickup_timeout',fresh=True)
   if s.contested_until and s.now>=s.contested_until:return self.held()
   if s.advantage:
    a=s.advantage
    if s.owner==a['team'] and s.ball.carrier and s.attack_sign(a['team'])*(s.ball.x-a['origin_x'])>=5:s.advantage=None;self.emit('advantage_realized','11.2',method='progress')
    elif s.now>=a['until']:return self.recall_advantage()
   self.clock_expiry()
  elif s.phase==Phase.REVIEW and s.now>=s.review['until']:self.finish_review(False,inconclusive=True)
  elif s.phase==Phase.FLIGHT and s.now>=s.tail_until:self.end_flight('three_seconds',s.ball.x,s.ball.y)
  elif s.phase==Phase.PENALTY:self.clock_expiry()
  elif s.phase==Phase.DEAD and s.restart and s.restart.ready_at is None and s.now>=s.restart.created_at+30000:
   r=s.restart;near=[p for p in s.players.values()if p.team==r.team and self.eligible(p)and p.role!='archer'and norm(p.x-r.x,p.y-r.y)<=.5]
   blockers=[p for p in s.players.values()if p.team!=r.team and self.eligible(p)and p.role!='archer'and norm(p.x-r.x,p.y-r.y)<r.clearance]
   if r.kind=='recovery':
    blockers=[p for p in self.recovery_blockers(r)if self.eligible(p)]
    if not blockers:return self.resume_recovery()
   offender=min(blockers,key=lambda p:p.id)if blockers else next((p for p in s.players.values()if p.team==r.team and self.eligible(p)and p.role!='archer'),None)
   if offender:self.foul(offender.id,None,'deliberate_restart_delay',major=True)
   else:self.forfeit(r.team,'no_restart_taker')
  elif s.phase==Phase.DEAD and s.restart and s.restart.ready_at is not None and s.now>=s.restart.ready_at+5000:
   r=s.restart;self.award(s.other(r.team),r.x,r.y,'restart_timeout',fresh=True)
 def advance(self,dt):
  end=self.s.now+dt
  while self.s.now<end:
   self.resolve_timers()
   span=min(end-self.s.now,max(1,self.next_deadline()-self.s.now))
   self.elapse(span)
  self.assert_invariants()
 def request_review(self,team,issue,official=False):
  s=self.s;allowed={'goal','eligibility','freeze','boundary','release_time','player_identity','clock_owner','serious_misconduct'}
  if s.phase!=Phase.DEAD or not s.restart or s.restart.ready_at is not None or issue not in allowed:return False
  if not official and s.challenges[team]<=0:return False
  s.review={'team':team,'issue':issue,'official':official,'until':s.now+90000};s.phase=Phase.REVIEW
  self.emit('review_start','17.4–17.5',team=team,issue=issue,official=official,until=s.review['until']);return True
 def finish_review(self,successful,correction=None,inconclusive=False):
  s=self.s
  if s.phase!=Phase.REVIEW or s.review is None:return False
  r=s.review;s.review=None;s.phase=Phase.DEAD
  if not r['official']and not successful:s.challenges[r['team']]-=1
  if correction and successful:
   if 'game_ms'in correction:s.game_ms=correction['game_ms']
   if 'possession_ms'in correction:s.possession_ms=correction['possession_ms']
   if 'team'in correction:self.award(correction['team'],*correction.get('spot',(s.ball.x,s.ball.y)),'review_correction')
  s.restart.created_at=s.now;s.restart.ready_at=None
  self.emit('review_complete','17.5–17.6',successful=successful,inconclusive=inconclusive,correction=correction,challenge_retained=successful or r['official']);return True
 def save_review_point(self,label):
  import copy
  self.review_snapshot=(label,copy.deepcopy(self.s),len(self.log),list(self.score_history))
  self.emit('review_checkpoint','17.4–17.6',label=label)
 def review_freeze_error(self,affected_team,missed=False):
  if self.review_snapshot is None:return False
  import copy
  label,old,seq,scores=self.review_snapshot
  #Sequence finality: a later legal restart closes ordinary review.
  if any(r['event']=='restart_release'for r in self.log[seq:]):return False
  elapsed=self.s.now;restored=copy.deepcopy(old)
  self.s.__dict__.update(restored.__dict__);self.s.now=elapsed;self.score_history=scores
  self.award(affected_team,old.ball.x,old.ball.y,'missed_freeze_review'if missed else'false_freeze_review')
  self.emit('review_correction','7.5;17.6',label=label,void_after_event=seq,missed=missed)
  return True
 def equipment_check(self,ball_diameter=.215,ball_mass=.4,arrow_mass=.04,arrow_speed=30,certified=True,magik=False):
  valid=.213<=ball_diameter<=.217 and .390<=ball_mass<=.410 and .038<=arrow_mass<=.042 and arrow_speed<=30 and .5*arrow_mass*arrow_speed**2<=20 and certified and not magik
  self.emit('equipment_check','1.1;3.1–3.6',passed=valid)
  return valid
 def terminal_record(self):
  """C4.0: everything that must not change once a match is complete, as plain data. Tests compare it before and after."""
  s=self.s;r=s.restart
  return json.loads(json.dumps({'phase':s.phase.value,'result':s.result,'score':dict(s.score),'now':s.now,'period':s.period,'g_ms':s.game_ms,'p_ms':s.possession_ms,'live_ms':s.live_ms,'dead_ms':s.dead_ms,
   'owner':s.owner,'restart':None if r is None else[r.team,r.x,r.y,r.reason,r.kind],'ball':[s.ball.mode.value,s.ball.carrier],'advantage':s.advantage is not None,'penalty':s.penalty is not None,'extension':s.extension,
   'tackle_count':s.tackle_count,'zone_violations':s.zone_violations,'warning':{t:sorted(v)for t,v in s.warning.items()},'debts':[dict(d)for d in self.debts],'queued_sanctions':[list(a)for a in self.pending_discipline],
   'players':{p.id:[p.active,p.role,p.disqualified,p.exclusion_ms,p.minor_count,p.major_count]for p in s.players.values()},'records':len(self.log),'last_id':self.event_seq,'final_id':self.final_seq,
   'periods':self.period_history,'scores':self.score_history,'stoppages':s.stoppages,
   'positions':{p.id:[p.x,p.y,p.z,p.vx,p.vy,p.posture]for p in s.players.values()},'stats':dict(getattr(self,'contact_stats',None)or{}),'engagements':sorted(map(str,s.engagements))},default=str))
 def assert_invariants(self):
  s=self.s;b=s.ball
  assert s.game_ms>=0 and s.possession_ms>=0,('negative_clock',s.now)
  assert b.carrier is None or b.mode==BallMode.CONTROLLED,('carrier_mode',b.mode)
  assert not(b.carrier and b.contested),'double_control'
  if b.carrier:
   p=s.players[b.carrier];assert p.team==s.owner or s.phase==Phase.PENALTY,('control_owner',p.id,s.owner)
   assert p.eligible(s.now),('ineligible_carrier',p.id,s.now,p.freeze_until)
  if s.phase==Phase.DEAD:assert s.restart is not None and b.carrier is None,'undefined_stoppage'
  if s.phase==Phase.AWARD:assert s.owner and s.award_spot and s.award_deadline,'undefined_award'
  if s.phase==Phase.FLIGHT:assert s.tail_until is not None and b.carrier is None,'invalid_tail'
  if s.phase==Phase.FINAL:assert s.result is not None,'missing_result'
  for q in s.quivers.values():assert 0<=q.loaded<=5 and 0<=q.spent<=q.allocation,'ammunition'
  for t in('A','B'):
   assert sum(p.active for p in s.players.values()if p.team==t)<=12,'extra_player'
  return True

#C4.0 terminal processing. Every Engine method that can change the match is guarded:
#  - called on a completed match, it does nothing, returns None and is counted in final_refused;
#  - if the match is completed inside it, the completion unwinds to the outermost guarded call, which returns None.
#The methods below only read, or only compute, and are left as they are. A self-check asserts that every method of the class is
#either guarded or on this list, so a method added later cannot escape by omission.
FINAL_READ_ONLY=('zone','territory','territory_points','emit','eligible','live','c2_snapshot','c1_reason','contact_legal','recovery_committed','inbound_side',
 'recovery_blocked','recovery_blockers','exit_run','exit_points','exit_free','exit_routes','exit_lanes','exit_before','exit_interference','archer_in_lane','next_deadline',
 'assert_invariants','validate_lineup','zone_due','zone_compliance_time','zone_witness','zone_overdue','terminal_record')
def _final_guard(name,f):
 def guarded(self,*a,**k):
  if self.s.phase==Phase.FINAL:
   self.final_refused[name]=self.final_refused.get(name,0)+1;return None
  self.depth+=1
  try:return f(self,*a,**k)
  except MatchFinal:
   if self.depth>1:raise
   return None
  finally:self.depth-=1
 guarded.__name__=name;guarded.__doc__=f.__doc__;guarded.guarded=True;return guarded
FINAL_GUARDED=tuple(n for n,f in vars(Engine).items()if callable(f)and not n.startswith('__')and n not in FINAL_READ_ONLY)
for _n in FINAL_GUARDED:setattr(Engine,_n,_final_guard(_n,vars(Engine)[_n]))
''',
    'policies': r'''"""Policies choose observable actions; no policy chooses whether an action scores."""
from dataclasses import dataclass,replace
import math,random
from .types import Player,Attributes,MatchState
from .geometry import norm,clamp,unit,zone,segment_distance,predict_path,intercept_xy

@dataclass(frozen=True)
class Tactics:
 width:float=25
 support:float=9
 pace:float=.75
 pass_pressure:float=5
 shoot_distance:float=23
 escort:int=1
 escort_spacing:float=2.5
 escort_shape:str='arc'
 arrow_interval:float=18
 reserve:int=2
 possession_patience:float=.5
 hunt_count:int=3
 defense:str='adaptive'
 risk:float=.5

TACTICS={
 'balanced':Tactics(),
 'speed':Tactics(width=31,support=16,pace=1,pass_pressure=4,shoot_distance=28,escort=0,arrow_interval=22,possession_patience=.1,hunt_count=4,defense='hunt',risk=.8),
 'contact':Tactics(width=17,support=5,pace=.5,pass_pressure=2.7,shoot_distance=12,escort=2,arrow_interval=24,possession_patience=.8,hunt_count=3,defense='man',risk=.35),
 'escort':Tactics(width=15,support=4,pace=.5,pass_pressure=2,shoot_distance=12,escort=4,escort_spacing=2.4,arrow_interval=20,possession_patience=.75,hunt_count=3,defense='zone',risk=.35),
 'wide':Tactics(width=42,support=12,pace=.72,pass_pressure=8,shoot_distance=30,escort=0,arrow_interval=22,possession_patience=.55,hunt_count=2,defense='zone',risk=.65),
 'archery':Tactics(width=28,support=7,pace=.67,pass_pressure=5,shoot_distance=22,escort=1,arrow_interval=4,reserve=0,possession_patience=.5,hunt_count=4,defense='hunt',risk=.6),
 'zone_pressure':Tactics(width=23,support=6,pace=.7,pass_pressure=4,shoot_distance=13,escort=2,arrow_interval=16,possession_patience=.7,hunt_count=3,defense='man',risk=.65),
 'conservative':Tactics(width=30,support=9,pace=.5,pass_pressure=7,shoot_distance=25,escort=1,arrow_interval=25,reserve=4,possession_patience=.95,hunt_count=2,defense='zone',risk=.2),
 'hunt':Tactics(width=26,support=8,pace=.8,hunt_count=6,defense='hunt',arrow_interval=14,risk=.7),
 'zone':Tactics(width=30,support=11,pace=.65,hunt_count=1,defense='zone',possession_patience=.6),
 'man':Tactics(width=24,support=8,pace=.75,hunt_count=3,defense='man',risk=.6)
}

def mix_tactics(primary,secondary=None,weight=.5,overrides=None):
 a=TACTICS[primary]
 if secondary:
  b=TACTICS[secondary];kw={}
  for name in a.__dataclass_fields__:
   x,y=getattr(a,name),getattr(b,name)
   if isinstance(x,(float,int)):kw[name]=x*(1-weight)+y*weight
   else:kw[name]=y if weight>=.5 else x
  kw['escort']=round(kw['escort']);kw['hunt_count']=round(kw['hunt_count']);kw['reserve']=round(kw['reserve']);a=Tactics(**kw)
 return replace(a,**(overrides or{}))

def make_roster(team,archetype,rng):
 players={}
 for i in range(22):
  a=Attributes();a.height=clamp(rng.gauss(2.55,.27),1.8,3.6576);a.mass=clamp(rng.gauss(230,40),110,420);a.reach=.46*a.height
  for k in('strength','agility','endurance','balance','contact_resistance','tackling','blocking','ball_handling','passing','kicking','catching','awareness'):
   setattr(a,k,clamp(rng.gauss(.68,.065),.4,.95))
  a.maximum_speed=clamp(rng.gauss(27,3),18,38);a.acceleration=rng.uniform(8,12);a.braking=rng.uniform(11,16);a.turning=rng.uniform(10,16);a.decision_speed=rng.uniform(.18,.38)
  if archetype=='speed':a.maximum_speed=42;a.acceleration=14;a.mass=155;a.strength=.52;a.agility=.88;a.turning=17;a.contact_resistance=.53;a.braking=17
  elif archetype=='power':a.mass=390;a.height=3.1;a.reach=1.5;a.strength=.9;a.balance=.83;a.maximum_speed=21;a.acceleration=7;a.turning=8;a.blocking=.84;a.contact_resistance=.9
  elif archetype=='reach':a.height=3.6576;a.mass=330;a.reach=1.8;a.maximum_speed=25;a.acceleration=8;a.catching=.86;a.blocking=.8
  elif archetype=='technical':a.mass=190;a.maximum_speed=27;a.passing=.9;a.catching=.88;a.ball_handling=.9;a.awareness=.9;a.decision_speed=.16;a.strength=.57
  elif archetype=='endurance':a.endurance=.96;a.mass=235;a.maximum_speed=25;a.strength=.7
  elif archetype=='mixed':
   if i%3==0:a.mass=350;a.strength=.87;a.maximum_speed=22
   elif i%3==1:a.maximum_speed=40;a.acceleration=13;a.mass=165
   else:a.passing=.9;a.catching=.87;a.awareness=.88
  elif archetype=='precision':a.archery_accuracy=.96;a.keeper_skill=.87
  elif archetype!='balanced':raise ValueError('Unknown roster '+archetype)
  role='field'if i!=10 and i!=11 else'keeper'if i==10 else'archer'
  if role=='keeper':a.keeper_skill=max(a.keeper_skill,.82);a.catching=max(a.catching,.82);a.jump_height=1.6
  if role=='archer':a.archery_accuracy=max(a.archery_accuracy,.86);a.archery_release_speed=29
  a.validate();p=Player(f'{team}{i}',team,role,i<12,a,slot=i)
  if i<10:p.x=18+(i//5)*14;p.y=10+(i%5)*18
  elif i==10:p.x=3;p.y=50
  elif i==11:p.x=25;p.y=-5
  else:p.x=75;p.y=-43
  if team=='B':p.x=100-p.x;p.y=100-p.y
  p.target=(p.x,p.y);players[p.id]=p
 return players

class Policy:
 def __init__(self,team,tactics,defense=None):
  self.assume={};self.pocket={};self.team=team;self.t=tactics;self.defense=defense or tactics.defense;self.recent=[];self.last_score=(0,0)
 def eligible(self,s):return[p for p in s.players.values()if p.team==self.team and p.eligible(s.now)and p.role!='archer']
 def targets(self,s):
  t=self.t;sgn=s.attack_sign(self.team);own=s.ends[self.team];goal=s.attack_goal(self.team);b=s.ball;ours=self.eligible(s)
  opp=[p for p in s.players.values()if p.team!=self.team and p.eligible(s.now)and p.role!='archer'];fields=[p for p in ours if p.role=='field']
  carrier=s.players.get(b.carrier);attacking=s.owner==self.team
  targets={};clock=s.possession_ms/1000;losing=s.score[self.team]<s.score[s.other(self.team)];late=s.period>=4 and s.game_ms<120000
  live_carrier=carrier if carrier and carrier.team==self.team else None
  escorts=[]
  if live_carrier:
   escorts=sorted((p for p in fields if p.id!=carrier.id),key=lambda p:norm(p.x-carrier.x,p.y-carrier.y))[:t.escort]
  for p in ours:
   if p.role=='keeper':
    if b.carrier==p.id:targets[p.id]=(own+sgn*(s.keeper_zone_radius+2),50)
    else:
     gy=clamp(50+(b.y-50)*.35,45,55);gx=own+sgn*(2 if not attacking else 7)
     if b.carrier is None and b.vx*sgn<0 and abs(b.vx)>.1:
      tt=(own-b.x)/b.vx
      if 0<tt<2:gy=clamp(b.y+b.vy*tt,44,56)
     targets[p.id]=(gx,gy)
    continue
   zn=zone(p.x,p.y,s.keeper_zone_radius)
   distance_out=max(0,(s.keeper_zone_radius+1.5)-norm(p.x-(0 if zn==0 else 100),p.y-50))if zn is not None else 0
   exit_ms=1000*(math.sqrt(2*distance_out/max(1,p.a.acceleration))+p.speed/max(1,p.a.braking)+p.a.decision_speed+.3)
   if self.pocket.get('zone_marking'):exit_ms+=1200 #C2 provisional controller: leave earlier. The free-run exit estimate is too short in traffic, and under C2 an exit costs nothing.
   if zn is not None and p.zone_ms[zn]>=max(400,5000-exit_ms):
    gx=0 if zn==0 else 100;ux,uy=unit(p.x-gx,p.y-50);targets[p.id]=(clamp(gx+ux*(s.keeper_zone_radius+2),1,99),clamp(50+uy*(s.keeper_zone_radius+2),1,99));continue
   if zn is not None and self.pocket.get('zone_marking')and not attacking and p.unmarked_ms[zn]>=max(400,5000-exit_ms-600):
    #C2 provisional controller: an unmarked defender running out of allowance closes on the nearest opponent if that is quicker than leaving, else leaves.
    md=self.pocket.get('marking_distance',3.);near=min(opp,key=lambda q:norm(q.x-p.x,q.y-p.y))if opp else None
    if near is not None and norm(near.x-p.x,near.y-p.y)-md<distance_out:targets[p.id]=(clamp(near.x,1,99),clamp(near.y,1,99));continue
    gx=0 if zn==0 else 100;ux,uy=unit(p.x-gx,p.y-50);targets[p.id]=(clamp(gx+ux*(s.keeper_zone_radius+2),1,99),clamp(50+uy*(s.keeper_zone_radius+2),1,99));continue
   rc=getattr(s,'reconstruction',None)
   if rc and rc['team']==self.team and b.carrier==p.id and zn==rc['zone']:
    #C2 provisional controller: the carrier takes the ball out across the arc to clear the zone.
    gx=0 if zn==0 else 100;ux,uy=unit(p.x-gx,p.y-50);targets[p.id]=(clamp(gx+ux*(s.keeper_zone_radius+3),1,99),clamp(50+uy*(s.keeper_zone_radius+3),1,99));continue
   if not self.pocket.get('zone_marking')and any(p.zone_ms[j]>400 and p.outside_ms[j]<3000 for j in(0,1)): #Pocket 1.1 controller for the old three-second outside wait; it has no meaning under C2 occupancy
    targets[p.id]=(clamp(p.x-sgn*4,s.keeper_zone_radius+2,98-s.keeper_zone_radius),clamp(p.y,4,96));continue
   if s.phase.value=='award':
    if attacking:
     nearest=min(fields,key=lambda q:norm(q.x-b.x,q.y-b.y))if fields else p
     targets[p.id]=(b.x,b.y)if p.id==nearest.id else(clamp(b.x+sgn*8,2,98),clamp(b.y+(p.slot%2*2-1)*7,2,98))
    else:
     ux,uy=unit(p.x-b.x,p.y-b.y);targets[p.id]=(clamp(b.x+ux*5,2,98),clamp(b.y+uy*5,2,98))
    continue
   if b.carrier is None:
    tt=.4;chase=(clamp(b.x+b.vx*tt,1,99),clamp(b.y+b.vy*tt,1,99))
    read=self.assume.get('c1_chasers_read_flight')
    if read:
     #C1: read the ball's real path (flight, bounces and roll), not a fixed 0.4 s extrapolation.
     #Each field player finds where it could meet the ball; the closest few to their own meeting point go.
     key=(s.now,b.version,b.x,b.y)
     if getattr(self,'_chase_key',None)!=key:
      path=predict_path(b,self.assume.get('gravity',9.81),self.assume.get('ball_drag',.015),self.assume.get('ball_restitution',.7745966692))
      pts={q.id:intercept_xy(q,path,q.a.reach*.9,True)for q in fields}
      order=sorted(fields,key=lambda q:(norm(q.x-pts[q.id][0],q.y-pts[q.id][1]),q.id))
      self._chase_key=key;self._chase=(pts,[q.id for q in order])
     pts,order=self._chase;rank=order.index(p.id)
     if rank<(4 if t.defense=='hunt'else 3):targets[p.id]=pts[p.id];continue
    else:
     rank=sorted(fields,key=lambda q:norm(q.x-chase[0],q.y-chase[1])).index(p)
     if rank<(4 if t.defense=='hunt'else 3):targets[p.id]=chase;continue
    if False:pass
    else:targets[p.id]=(clamp(b.x-sgn*(6+rank),3,97),clamp(50+(p.slot%5-2)*t.width/2,3,97))
    continue
   if live_carrier:
    if p.id==carrier.id:
     nearest=sorted(opp,key=lambda q:norm(q.x-p.x,q.y-p.y))[:4]
     options=[clamp(p.y+dy,4,96)for dy in(-14,-7,0,7,14)]
     def lane(y):
      endpoint=(clamp(p.x+sgn*12,0,100),y)
      room=min((segment_distance(q.x,q.y,p.x,p.y,*endpoint)[0]for q in nearest),default=20)
      return room-.025*abs(y-50)-.08*abs(y-p.y)
     dest=max(options,key=lane)
     if t.possession_patience>.9 and not losing and late and clock>15:dest=clamp(p.y+(8 if p.y<50 else-8),5,95);gx=p.x-sgn*3
     else:
      lookahead=max(15,p.a.maximum_speed**2/(2*p.a.braking)+8)
      gx=clamp(p.x+sgn*lookahead,.25,99.75)
     if abs(goal-p.x)<14:dest=clamp(50+(3.8 if p.y>50 else-3.8),45,55);gx=goal-sgn*.2
     if self.pocket.get('release_territories') and abs(goal-p.x)<max(14,s.keeper_zone_radius+2):
      pc=self.pocket
      seek_inner=pc.get('adapt_scoring') and pc['inner_points']>max(pc['release_points'],pc['outside_points'] if not pc['zone_only'] else 0)
      radius=pc['inner_zone_radius'] if seek_inner else s.keeper_zone_radius
      gx=goal-sgn*max(.5,radius*.6);dest=50+(1 if p.y>50 else -1)*min(3.8,radius*.3)
     targets[p.id]=(gx,dest)
    elif p in escorts:
     i=escorts.index(p);n=len(escorts)
     if t.escort_shape=='ring':angle=2*math.pi*i/max(1,n)
     elif t.escort_shape=='wedge':angle=(-1 if i%2 else 1)*(.5+.35*(i//2))
     else:angle=(-1.15+2.3*i/max(1,n-1))if n>1 else 0
     targets[p.id]=(clamp(carrier.x+sgn*(t.escort_spacing*math.cos(angle)+.2*carrier.speed),1,99),clamp(carrier.y+t.escort_spacing*math.sin(angle),1,99))
    else:
     row=p.slot%5;dy=(row-2)*t.width/2
     lead=t.support*(1 if p.slot%3 else-.65)
     if t==TACTICS['zone_pressure'] and abs(goal-b.x)<40:lead=abs(goal-b.x)-8
     targets[p.id]=(clamp(b.x+sgn*lead,3,97),clamp(50+dy,3,97))
   else:
    target_carrier=carrier
    ranked=sorted(fields,key=lambda q:norm(q.x-carrier.x,q.y-carrier.y))
    if self.defense=='man':
     candidates=sorted((q for q in opp if q.role=='field'),key=lambda q:q.slot)
     mark=candidates[p.slot%len(candidates)]if candidates else carrier
     targets[p.id]=(clamp(mark.x+sgn*1.2,1,99),clamp(mark.y,1,99))
    elif self.defense=='hunt'or p in ranked[:t.hunt_count]:
     rank=ranked.index(p);lead=.25+rank*.06
     tx=carrier.x+carrier.vx*lead;ty=carrier.y+carrier.vy*lead
     angle=0 if rank==0 else(-1 if rank%2 else 1)*(.7+rank*.5)
     targets[p.id]=(clamp(tx,1,99),clamp(ty+angle,1,99))
    else:
     line=clamp(b.x+sgn*12,own+sgn*(s.keeper_zone_radius+2) if sgn>0 else 8,92 if sgn>0 else own+sgn*(s.keeper_zone_radius+2))
     if sgn<0:line=clamp(b.x-12,8,78)
     observed_y=sum(v[1]for v in self.recent)/len(self.recent)if self.recent else 50
     targets[p.id]=(line,clamp(50+(p.slot%5-2)*15+.15*(observed_y-50),5,95))
  return targets
 def pass_ranked(self,s,p):
  """C1: every pass option, best first, so an unreachable first choice can be replaced."""
  sgn=s.attack_sign(p.team)
  mates=[q for q in self.eligible(s)if q.id!=p.id and q.posture=='upright'and norm(q.x-p.x,q.y-p.y)<45]
  opponents=[q for q in s.players.values()if q.team!=p.team and q.eligible(s.now)and q.role!='archer']
  def utility(q):
   d=norm(q.x-p.x,q.y-p.y)
   lane=min((segment_distance(o.x,o.y,p.x,p.y,q.x,q.y)[0]for o in opponents),default=15)
   pressure=min((norm(o.x-q.x,o.y-q.y)for o in opponents),default=15)
   return .45*sgn*(q.x-p.x)+1.3*min(lane,8)+.8*min(pressure,12)-.10*d+2*q.a.catching
  return sorted(mates,key=utility,reverse=True)
 def pass_choice(self,s,p):
  b=s.ball;sgn=s.attack_sign(p.team)
  mates=[q for q in self.eligible(s)if q.id!=p.id and q.posture=='upright'and norm(q.x-p.x,q.y-p.y)<45]
  opponents=[q for q in s.players.values()if q.team!=p.team and q.eligible(s.now)and q.role!='archer']
  def utility(q):
   d=norm(q.x-p.x,q.y-p.y)
   lane=min((segment_distance(o.x,o.y,p.x,p.y,q.x,q.y)[0]for o in opponents),default=15)
   pressure=min((norm(o.x-q.x,o.y-q.y)for o in opponents),default=15)
   advancement=sgn*(q.x-p.x)
   return .45*advancement+1.3*min(lane,8)+.8*min(pressure,12)-.10*d+2*q.a.catching
  return max(mates,key=utility)if mates else None
''',
    'match': r'''"""Spatial autonomous play with explicit trajectories and calibrated-assumption hooks."""
import math,random,json,copy,hashlib
from collections import Counter,defaultdict
from pathlib import Path
from .types import *
from .engine import Engine
from .policies import Policy,TACTICS,mix_tactics,make_roster
from .geometry import *

C4C_KEYS=('keeper_depth_frac','keeper_depth_min_m','keeper_depth_max_m','keeper_reaction_s','keeper_unset_s','keeper_set_mps','keeper_pushoff_frac',
 'keeper_extension_frac','keeper_dive_hand_frac','keeper_dive_lean','keeper_launch_min_s','keeper_parry_restitution','keeper_body_restitution','keeper_attempt_margin_m','keeper_dive_time_s','keeper_aim_frac','keeper_parry_swing_mps',
 'keeper_windup_set','keeper_confront','keeper_confront_m','keeper_gather_m')
C4C2_EST={'conv': {'dist': [3, 6, 9, 12, 15, 20, 25, 30, 40], 'ang': [0, 30, 60], 'height': [2.55, 2.7432, 3.2004, 3.6576], 'speed': [40.0, 50.0], 'p': [[[[0.9375, 0.875, 0.8125], [1.0, 1.0, 0.0], [1.0, 1.0, 0.6875], [1.0, 1.0, 0.3125], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [0.0, 0.125, 0.0]], [[0.875, 0.625, 0.875], [1.0, 1.0, 0.0], [1.0, 1.0, 0.375], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 0.875, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0]], [[0.9375, 0.875, 0.5625], [1.0, 0.75, 0.0], [1.0, 1.0, 0.25], [1.0, 1.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.875, 0.0, 0.0], [0.125, 0.0, 0.0], [0.5, 0.0625, 0.9375]], [[0.8125, 0.8125, 0.5625], [1.0, 0.5625, 0.0], [1.0, 0.9375, 0.3125], [1.0, 0.5, 0.0], [0.25, 0.0, 0.0], [0.0, 0.0, 0.0], [0.25, 0.0, 0.0], [0.0, 0.0, 0.0], [0.4375, 0.0, 0.0]]], [[[1.0, 0.8125, 0.8125], [1.0, 1.0, 0.0], [1.0, 1.0, 0.9375], [1.0, 1.0, 0.875], [1.0, 1.0, 0.5], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0]], [[1.0, 0.9375, 0.9375], [1.0, 1.0, 0.0], [1.0, 1.0, 0.5625], [1.0, 1.0, 0.6875], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 0.8125, 0.0]], [[0.9375, 0.8125, 0.75], [1.0, 0.875, 0.0], [1.0, 1.0, 0.625], [1.0, 1.0, 0.5], [1.0, 1.0, 0.0], [1.0, 0.3125, 0.0], [1.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.6875]], [[0.9375, 0.75, 0.75], [1.0, 0.75, 0.0], [1.0, 0.9375, 0.4375], [1.0, 1.0, 0.625], [1.0, 1.0, 0.0], [0.375, 0.0, 0.0], [0.0625, 0.0, 0.0], [0.5, 0.0, 0.0], [0.0, 0.0, 0.0]]]]}, 'conv_out': {'dist': [3, 6, 9, 12, 15, 20, 25, 30, 40], 'ang': [0, 30, 60], 'height': [2.55, 2.7432, 3.2004, 3.6576], 'speed': [40.0, 50.0], 'p': [[[[0.375, 0.875, 0.625], [0.0, 0.0, 1.0], [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.625, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.875], [1.0, 1.0, 1.0], [1.0, 1.0, 0.0]], [[0.625, 0.375, 0.75], [0.0, 0.0, 0.75], [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.25, 0.0], [1.0, 0.875, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.375], [1.0, 1.0, 0.0]], [[0.625, 0.625, 1.0], [0.0, 0.0, 1.0], [0.125, 0.0, 0.0], [0.875, 0.0, 0.0], [0.75, 0.625, 0.0], [1.0, 0.25, 0.0], [1.0, 0.375, 0.0], [0.75, 0.0, 0.0], [0.0, 0.0, 0.0]], [[0.25, 0.75, 0.75], [0.0, 0.0, 0.875], [0.0, 0.0, 0.0], [0.75, 0.0, 0.0], [0.75, 0.5, 0.0], [0.875, 0.625, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]], [[[0.75, 0.875, 1.0], [0.0, 0.0, 1.0], [0.125, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.875, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0]], [[0.875, 0.625, 0.875], [0.0, 0.0, 1.0], [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.75, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [1.0, 1.0, 0.0]], [[0.5, 0.875, 1.0], [0.0, 0.0, 0.625], [0.375, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.625, 0.0], [1.0, 0.875, 0.0], [1.0, 0.875, 0.0], [1.0, 0.5, 0.0], [0.125, 0.0, 0.0]], [[0.0, 0.75, 0.625], [0.0, 0.0, 1.0], [0.625, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 0.875, 0.0], [1.0, 0.75, 0.0], [1.0, 0.5, 0.0], [1.0, 0.0, 0.0], [0.0, 0.0, 0.0]]]]}, 'windup': {'margin': [-0.5, -0.4, -0.3, -0.2, -0.1, 0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7], 'goal_factor': [0.825, 0.825, 0.825, 0.875, 0.875, 0.875, 0.9375, 0.9375, 1.0, 1.0, 1.0, 1.0, 1.0], 'p_tackled': [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 'runs_per_bin': [0, 0, 80, 32, 16, 24, 16, 24, 24, 8, 16, 8, 16], 'unpressured_goal_rate': 1.0, 'note': 'shooter 15 m out on the axis, one defender running in; goal_factor = chance of a goal at that margin / chance unpressured (applied to the conversion table everywhere); p_tackled = chance he is grounded or tackled within the wind-up and 0.6 s after'}, 'carry': {'dist': [4, 6, 9, 12, 16, 20], 'ang': [0, 30], 'p': [[[[0.8, 1.0], [1.0, 1.0], [1.0, 1.0], [1.0, 1.0], [1.0, 1.0], [1.0, 1.0]], [[0.8, 1.0], [1.0, 1.0], [0.6, 0.6], [0.2, 0.3333], [0.2, 0.7333], [0.6667, 0.6]]], [[[0.8, 1.0], [0.6667, 1.0], [0.1333, 0.2], [0.2667, 0.6667], [0.2667, 0.2667], [0.0, 0.0]], [[0.7333, 1.0], [0.2667, 0.5333], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]]]}, 'pass': {'dist': [5, 10, 15, 20, 30, 40], 'lane': [1.0, 2.0, 4.0, 8.0, 99.0], 'p': [[0.6786, 0.6786, 0.8214, 0.8214, 0.8214], [0.7857, 0.7857, 0.7857, 0.8214, 0.8571], [0.6786, 0.7143, 0.75, 0.75, 0.75], [0.5357, 0.6429, 0.7143, 0.7143, 0.7143], [0.5, 0.75, 0.75, 0.75, 0.75], [0.4643, 0.6429, 0.6429, 0.6429, 0.6429]], 'raw': [[0.6786, 0.5714, 0.8214, 0.7143, 0.6786], [0.7857, 0.6429, 0.5714, 0.8214, 0.8571], [0.6786, 0.7143, 0.75, 0.7143, 0.7143], [0.5357, 0.6429, 0.7143, 0.5714, 0.6429], [0.5, 0.75, 0.6071, 0.3929, 0.6429], [0.4643, 0.6429, 0.5357, 0.5714, 0.5]]}, 'v_ret': {'zone_value_units': 0.3394, 'first_tackles': 383, 'source': ['smoke_c4c1_reference/A-low_mixed_seed2_experiment.jsonl.gz', 'smoke_c4c1_reference/A-low_seed1_experiment.jsonl.gz', 'smoke_c4c1_reference/B-high_seed1_control.jsonl.gz', 'smoke_c4c1_reference/C-low_seed1_experiment.jsonl.gz']}} #C4c2: the drill tables of c4c2_estimates.json (drills_c4c2_estimates.py), embedded at build time; None = not yet measured
C4C2_POS={'dist_edges': [0, 10, 15, 20, 30, 45, 70, 200], 'clock_edges_s': [0, 1000], 'zone_value_units': [[1.0467], [0.8443], [0.7612], [0.7612], [0.7612], [0.7612], [0.7612]], 'raw_zone_value_units': [[1.0467], [0.8443], [0.6729], [0.5145], [0.6479], [0.9049], [0.8142]], 'samples': [[750], [655], [431], [1103], [970], [1934], [2685]], 'source': ['smoke_c4c1_reference/A-low_mixed_seed2_experiment.jsonl.gz', 'smoke_c4c1_reference/A-low_seed1_experiment.jsonl.gz', 'smoke_c4c1_reference/B-high_seed1_control.jsonl.gz', 'smoke_c4c1_reference/C-low_seed1_experiment.jsonl.gz'], 'note': 'zone_value_units is the monotone (non-increasing in distance) fit used by the controller; raw_zone_value_units are the cell means'} #C4c2: the value of a possession carrying on, by the carrier's distance (c4c2_possession.json, from the stored C4c1 smoke matches)
DEFAULT_ASSUMPTIONS={'gravity':9.81,'ball_drag':.015,'arrow_drag':.06,'catch_noise':.15,'tackle_rate':1.25,'block_force':1.,'arrow_error_scale':1.,'fatigue_rate':1.,'body_radius_scale':1.,'pass_release_ms':250,'grip_delay_ms':300,'bow_draw_ms':600,'ball_restitution':.7745966692,'frame_thickness':.2,'ball_mass_kg':.4,'pass_aim_error_deg':3.,'catch_arrest_force_N':1100.,'catch_hand_travel_m':.6,'catch_reaction_s':.12,'deflection_speed_kept':.2,'c1_pass_planning':1,'c1_receiver_routing':1,'c1_chasers_read_flight':1,'c1_catch_model':1,
 'c3_contact':1,'c3_substep_ms':10,'contact_restitution':.1,'contact_time_s':.15,'traction_coefficient':.8,'brace_speed_mps':2.,'shock_speed_mps':6.,'rearm_gap_m':.3,
 'grip_gain_per_s':4.,'grip_resist_per_s':1.,'grip_slip_per_s':2.,'grip_slip_ref_mps':4.,'grip_overload_per_s':4.,'grip_overload_time_s':.15,'grip_force_N':2500.,
 'topple_time_s':1.,'balance_recovery_per_s':1.5,'base_half_width_frac':.2,'hold_height_upper_frac':.7,'hold_height_lower_frac':.45,'lower_hold_leg_factor':.6,'holder_load_factor':.35,
 'tackle_grip_threshold':.3,'tackle_source_majority':.5,'restraint_weight_matched':1.,'restraint_weight_other':.3,'restraint_speed_loss':.5,'restraint_error_deg':8.,'collision_risk_tolerance':.5,'contact_foul_min_shock':.05,'c3_prep_round_ms':0,'c3_follow_distance':1,
 'c3b':1,'slide_friction':.8,'get_up_time_s':.8,'get_up_max_slide_mps':1.,'descent_time_s':.5,'containment_window_s':2.,'descent_window_s':2.,'recovery_react':1,'exit_protection':1,
 'c3c':1,'arm_pin_grip':.5,'tuck_after_delay_frac':1.,'strip_in_motion_factor':4.,'c3_region_policy':1,'blindside_rear_half_angle_deg':15.,'escape_force_N':2500.,
 #C4.0
 'c4_zone':1,'zone_direct_penalty':0,
 #C4a
 'escape_allocation':1,'contact_roster':0,
 #C4b
 'c4b':1,'gait_step_base_frac':.25,'gait_step_per_mps_frac':.035,'gait_step_max_frac':1.1,'gait_duty_rest':.62,'gait_duty_per_mps':.03,'gait_duty_min':.22,
 'gait_half_width_frac':.09,'gait_still_mps':.5,'gait_reset_frac':.75,
 #C4c Keeper
 'c4c':1,'keeper_depth_frac':.25,'keeper_depth_min_m':1.,'keeper_depth_max_m':4.,'keeper_reaction_s':.2,'keeper_unset_s':.1,'keeper_set_mps':1.5,
 'keeper_pushoff_frac':.4,'keeper_extension_frac':.3,'keeper_dive_hand_frac':.3,'keeper_dive_lean':.35,'keeper_launch_min_s':.1,'keeper_parry_restitution':.35,
 'keeper_body_restitution':.3,'keeper_attempt_margin_m':1.5,'keeper_dive_time_s':.25,'keeper_aim_frac':.5,'keeper_parry_swing_mps':5.,'keeper_windup_set':1,'keeper_confront':1,'keeper_confront_m':7.,'keeper_gather_m':6.,
 #C4c2: the C4c1 audit corrections and DreLen's scoring rulings (9 October). 0 = the C4c1 build.
 'c4c2':1,'reversal_rule':0,
 #C4c2 common controller (declared hypotheses; the success estimates are drill tables, not these numbers)
 'controller':1,'ctrl_lookahead_s':.6,'ctrl_style_A':0,'ctrl_style_B':0,'ctrl_style_band':.1,'ctrl_receivers':2,'ctrl_short_inbound':1,'ctrl_keeper':1,
 'keeper_height_m':0.}

class Match:
 def __init__(self,config=None):
  self.cfg=copy.deepcopy(config or{});self.seed=self.cfg.get('seed',20260916);self.requested_dt=self.cfg.get('dt_ms',100)
  if not isinstance(self.requested_dt,int)or self.requested_dt<1:raise ValueError('dt_ms must be a positive integer')
  self.dt=min(self.requested_dt,100)
  self.assume={**DEFAULT_ASSUMPTIONS,**self.cfg.get('assumptions',{})}
  self.rng={k:random.Random(self.seed+v)for k,v in {'roster':1,'ball':101,'contact':211,'arrow':307,'policy':409}.items()}
  self.s=MatchState(period_seconds=self.cfg.get('period_seconds',600),regulation_periods=self.cfg.get('regulation_periods',4),overtime_seconds=self.cfg.get('overtime_seconds',300))
  self.s.game_ms=self.s.period_seconds*1000;self.pol={}
  for team in('A','B'):
   tc=self.cfg.get('teams',{}).get(team,{});self.s.players.update(make_roster(team,tc.get('roster','balanced'),self.rng['roster']))
   for athlete in self.s.players.values():
    if athlete.team==team:
     for key,value in tc.get('attributes',{}).items():
      if key not in Attributes.__dataclass_fields__:raise ValueError('Unknown athlete attribute '+key)
      setattr(athlete.a,key,value)
     athlete.a.validate()
   tac=mix_tactics(tc.get('attack','balanced'),tc.get('secondary'),tc.get('mix_weight',.5),tc.get('overrides'))
   self.pol[team]=Policy(team,tac,tc.get('defense'))
  if self.cfg.get('pocket'):
   for p in self.s.players.values():
    p.a=Attributes(height=2.55,mass=230,reach=1.173,maximum_speed=self.cfg['pocket']['player_speed'],acceleration=self.cfg['pocket']['acceleration'],braking=self.cfg['pocket']['braking'],turning=self.cfg['pocket']['turning'],archery_release_speed=self.cfg['pocket']['arrow_speed'])
    for k in ('strength','agility','endurance','balance','contact_resistance','tackling','blocking','ball_handling','passing','kicking','catching','awareness'):setattr(p.a,k,.68)
    if p.role=='keeper':p.a.keeper_skill=.82;p.a.catching=.82;p.a.jump_height=1.6
    if p.role=='keeper'and self.assume.get('c4c2')and self.assume.get('keeper_height_m',0)>0:
     #C4c2: a Keeper at one of DreLen's intended heights (2.7432 to 3.6576 m). Family H of drills_c4c2_heights.py: arm reach 0.46 x
     #height; mass, acceleration, speed, jump and ratings unchanged (declared independent until the attribute step).
     p.a.height=self.assume['keeper_height_m'];p.a.reach=.46*p.a.height
    if p.role=='archer':p.a.archery_accuracy=.86
    p.a.validate()
  for policy in self.pol.values():policy.pocket=self.cfg.get("pocket",{});policy.assume=self.assume
  self.c4a_roster(int(self.assume.get('contact_roster',0)))
  self.pass_signal=(None,0);self.seen_version=-1;self.seen_from=0;self.hands_set={};self.bounce_mark=None;self.step_ms=0
  self.e=Engine(self.s,self.cfg)
  if not self.e.validate_lineup():raise ValueError('Invalid initial lineup')
  self.e.begin_hunt();self.step_count=0;self.trace=[];self.next_trace=0
  self.stats=Counter();self.e.contact_stats=self.stats;self.contact_cooldown={};self.pending_sub={};self.last_arrow_decision={'A':-99999,'B':-99999};self.no_archery=self.cfg.get('disable_archery',False)
  self.c3=bool(self.assume.get('c3_contact'));self.c3b=self.c3 and bool(self.assume.get('c3b'));self.e.c3b=self.c3b;self.e.assume=self.assume
  self.c3c=self.c3b and bool(self.assume.get('c3c'));self.e.c3c=self.c3c #C3c stands on C3b
  if self.c3c:self.e.blind_cos=math.cos(math.radians(self.assume['blindside_rear_half_angle_deg']))
  self.c3_init()
  if self.c3b:self.e.emit('c3b_rules','C3b',**{k:self.assume[k]for k in('slide_friction','get_up_time_s','get_up_max_slide_mps','descent_time_s','containment_window_s','descent_window_s','recovery_react','exit_protection')}) #marks the log: the C3b witnesses below can be expected in it
  if self.c3c:self.e.emit('c3c_rules','C3c',**{k:self.assume[k]for k in('arm_pin_grip','tuck_after_delay_frac','strip_in_motion_factor','c3_region_policy','blindside_rear_half_angle_deg','escape_force_N')})
  #C4.0: the Keeper Zone ruling. Its marker record is written only when it is on, so that with it off the log is the C3c2 log.
  self.e.c4_zone=bool(self.assume.get('c4_zone'));self.e.c4_occ=self.e.c4_zone and self.e.c2_occ;self.e.zone_direct=self.e.c4_occ and bool(self.assume.get('zone_direct_penalty'))
  if self.e.c4_zone:self.e.emit('c4_rules','C4.0',zone_ruling=1,defensive_consequences=self.e.c4_occ,zone_direct_penalty=int(self.e.zone_direct))
  #C4b: support-foot origin and the Carry rules. With c4b = 0 and carry_value = 0 the build is C4a.
  self.c4b=self.c3 and bool(self.assume.get('c4b'));self.e.c4b=self.c4b
  #C4c: Keeper mechanics. With c4c = 0 the Keeper is the C4b Keeper and the log is unchanged.
  self.c4c=self.c3 and bool(self.assume.get('c4c'));self.e.c4c=self.c4c
  #C4c2: body contacts keep recovery, body proposals revalidated at commitment, DreLen's scoring rulings. 0 = C4c1, log for log.
  self.c4c2=self.c3 and bool(self.assume.get('c4c2'));self.e.c4c2=self.c4c2;self.e.reversal_rule=int(self.assume.get('reversal_rule',0))
  #C4c2: the common controller needs the Keeper (c4c), the support foot (c4b) and the drill estimates
  self.ctrl=bool(self.c4c2 and self.c4c and self.c4b and self.assume.get('controller')and C4C2_EST is not None and C4C2_POS is not None);self.c4c2_last={}
  if self.c4b:self.e.emit('c4b_rules','C4b',**{k:self.assume[k]for k in('gait_step_base_frac','gait_step_per_mps_frac','gait_step_max_frac','gait_duty_rest','gait_duty_per_mps','gait_duty_min','gait_half_width_frac','gait_still_mps','gait_reset_frac')},
                       scoring={k:self.cfg['pocket'].get(k)for k in('outside_points','release_points','inner_points','carry_value')}if self.cfg.get('pocket')else None)
  if self.c4c:self.e.emit('c4c_rules','C4c',**{k:self.assume[k]for k in C4C_KEYS})
  if self.c4c2:self.e.emit('c4c2_rules','C4c2',scoring_origin='last offensive touch, kept through defensive touches (DreLen, 9 October)',arcs='a foot on an arc is in the farther territory (DreLen, 9 October)',
                           reversal_rule=self.e.reversal_rule,body_contact='keeps recovery; revalidated at commitment')
  #C4a: the marker is written only when a C4a setting differs from C4.0r2, so that with all three at those values the log is the C4.0r2 log
  if self.c3c and(self.assume['escape_allocation']or self.assume['contact_roster']or self.assume['c3_region_policy']==2):
   self.e.emit('c4a_rules','C4a',escape_allocation=int(self.assume['escape_allocation']),contact_roster=int(self.assume['contact_roster']),region_policy=int(self.assume['c3_region_policy']),
               strength_balance_tackling=getattr(self,'c4a_table',{}))
  self.pending_ball_actions={};self.pending_draw={};self.progress_samples=[];self.zone_exits=0;self.last_frame_events=[];self.capture_metrics={};self.freeze_records={};self.last_log_seen=0
 def active_field(self):return[p for p in self.s.players.values()if p.active and p.role!='archer']
 def targets_dead(self):
  s=self.s;r=s.restart
  if not r:return{}
  eligible=[p for p in s.players.values()if p.team==r.team and p.eligible(s.now)and p.role!='archer'and p.posture=='upright']
  if not eligible:return{}
  taker=s.players.get(r.taker)if r.taker else min(eligible,key=lambda p:norm(p.x-r.x,p.y-r.y))
  if not taker.eligible(s.now):r.taker=None;taker=min(eligible,key=lambda p:norm(p.x-r.x,p.y-r.y))
  self.restart_taker=None if r.kind=='recovery'else taker.id;targets={}
  spot=r.taker_spot or(r.x,r.y) #C2: the inbound taker stands just outside the field at the mark
  for p in self.active_field():
   keep=1+p.radius if r.kind=='recovery'else r.clearance #C2: a restored recovery clears body footprints from the one-metre disc
   if p.id==taker.id and r.kind!='recovery':
    targets[p.id]=spot
    if r.ready_at is not None:p.vx=p.vy=0;p.x,p.y=spot
   elif norm(p.x-r.x,p.y-r.y)<keep+.5 and p.team!=r.team:
    ux,uy=unit(p.x-r.x,p.y-r.y)
    if ux==uy==0:ux=s.attack_sign(p.team)
    choices=[(r.x+(keep+2)*math.cos(a*math.pi/12),r.y+(keep+2)*math.sin(a*math.pi/12))for a in range(24)]
    choices=[xy for xy in choices if 1<=xy[0]<=99 and 1<=xy[1]<=99]
    targets[p.id]=min(choices,key=lambda xy:norm(xy[0]-p.x,xy[1]-p.y))
   else:targets[p.id]=(clamp(p.x,1,99),clamp(p.y,1,99))
   zn=self.e.zone(p.x,p.y)
   if zn is not None and(p.zone_ms[zn]>3000 or p.unmarked_ms[zn]>3000)and p.id!=self.restart_taker and not(p.role=='keeper'and zn==s.own_zone(p.team)):
    gx=0 if zn==0 else 100;ux,uy=unit(p.x-gx,p.y-50);targets[p.id]=(clamp(gx+ux*(s.keeper_zone_radius+2),1,99),clamp(50+uy*(s.keeper_zone_radius+2),1,99))
  if self.ctrl and self.assume['ctrl_short_inbound']and r.kind=='inbound':self.c4c2_inbound(r,taker,eligible,targets)
  return targets
 def c4c2_inbound(self,r,taker,eligible,targets):
  """C4c2 (build specification 7: coordinated short-inbound and entry options). The two nearest team-mates of the taker go to a short
  option 6 m from the mark into the field and an entry option 12 m on, towards the goal they attack; at a mark inside or by the
  attacked Keeper Zone, both go just outside its arc (an inbound receiver there clears the zone). A spot within 2 m of an opponent is
  turned up to 30 degrees to the side with more room. The taker passes to the short option if its lane is clear by 2 m, else to the
  entry option, else as before."""
  s=self.s;sgn=s.attack_sign(r.team);ag=s.attack_goal(r.team);R=s.keeper_zone_radius
  opp=[q for q in s.players.values()if q.team!=r.team and q.eligible(s.now)and q.role!='archer']
  mates=sorted((q for q in eligible if q.id!=taker.id and q.role=='field'),key=lambda q:(math.hypot(q.x-r.x,q.y-r.y),q.id))[:2]
  if len(mates)<2:return
  ix,iy=unit(50-r.x+.5*sgn*25,50-r.y)
  if math.hypot(r.x-ag,r.y-50)<R+2:
   ux,uy=unit(r.x-ag,r.y-50);base=math.atan2(uy,ux);spots=[(ag+(R+1.5)*math.cos(base+da),50+(R+1.5)*math.sin(base+da))for da in(0.,-sgn*.45 if r.y>50 else sgn*.45)]
  else:spots=[(r.x+ix*6,r.y+iy*6),(r.x+ix*12+sgn*2,r.y+iy*12)]
  out=[]
  for sx,sy in spots:
   best=(sx,sy);room=min((math.hypot(o.x-sx,o.y-sy)for o in opp),default=99.)
   if room<2:
    for da in(-.52,-.26,.26,.52):
     dx,dy=sx-r.x,sy-r.y;cx=r.x+dx*math.cos(da)-dy*math.sin(da);cy=r.y+dx*math.sin(da)+dy*math.cos(da);rm=min((math.hypot(o.x-cx,o.y-cy)for o in opp),default=99.)
     if rm>room:room=rm;best=(cx,cy)
   out.append((clamp(best[0],1,99),clamp(best[1],1,99)))
  for q,xy in zip(mates,out):targets[q.id]=xy
  key=(r.created_at,r.x,r.y)
  if getattr(self,'c4c2_inb',(None,))[0]!=key:
   self.c4c2_inb=(key,mates[0].id,mates[1].id);self.e.emit('inbound_options','C4c2-7',taker=taker.id,short=mates[0].id,entry=mates[1].id,spots=[[round(c,2)for c in xy]for xy in out])
 def c4c2_inbound_order(self,r,p,order):
  inb=getattr(self,'c4c2_inb',None)
  if not(self.assume['ctrl_short_inbound']and r.kind=='inbound'and inb and inb[0]==(r.created_at,r.x,r.y)):return order
  s=self.s;opp=[q for q in s.players.values()if q.team!=p.team and q.eligible(s.now)and q.role!='archer']
  pref=[]
  for pid in inb[1:]:
   q=s.players[pid]
   if q in order and min((segment_distance(o.x,o.y,r.x,r.y,q.x,q.y)[0]for o in opp),default=99.)>=2.:pref.append(q)
  return pref+[q for q in order if q not in pref]
 def c4a_roster(self,mode):
  """C4a (the Lead's C4 contract): field players whose contact attributes differ, so that strength, balance and technique
  contests can occur in play. Only strength, balance and tackling are changed; every other attribute keeps its Pocket value.
  Keepers and Archers keep 0.68. Declared designs, not fitted:
    1 mixed, mirrored: four levels, L = 0.46, 0.60, 0.76, 0.90 (mean 0.68, the uniform control's value). Field players of a team,
      in slot order, take k = 0, 1, 2, ...: strength L[k mod 4], balance L[(k div 4) mod 4], tackling L[(k mod 4 + k div 4) mod 4].
      Over any 16 consecutive slots every strength-balance pair occurs once and tackling forms a Latin square, so the three vary
      independently. Both teams get the same slots: equal teams, unequal encounters.
    2 / 3 contrast: one team 0.90 in all three, the other 0.30 (2: A strong; 3: B strong)."""
  if not mode or not self.cfg.get('pocket'):return
  L=(.46,.60,.76,.90);self.c4a_table={}
  if mode==1:return self.c4b_roster(L)
  for team in('A','B'):
   field=sorted([p for p in self.s.players.values()if p.team==team and p.role=='field'],key=lambda p:p.slot)
   for k,p in enumerate(field):
    if mode==4:i,j=k%4,(k//4)%4;v=(L[i],L[j],L[(i+j)%4]) #the C4a design as delivered (its starters are not balanced): reproduction only
    else:x=.90 if(team=='A')==(mode==2)else .30;v=(x,x,x)
    p.a.strength,p.a.balance,p.a.tackling=v;p.a.validate();self.c4a_table[p.id]=list(v)
 def c4b_gait(self,old,ms):
  """C4b support-foot state (build specification 8; DreLen's ruling on the scoring origin). Declared gait model, not fitted:
  every athlete on the field has a left and a right foot, each planted at a fixed world position or in the air. A planted foot
  stays where it was put until it is lifted; it never slides with the pelvis.
  Over each interval the pelvis is taken along the straight line from where it was to where it is (the interval is cut at every
  event the engine commits, so a release is always at an interval's end). Steps are counted in distance: step length
  L = height x min(gait_step_max_frac, gait_step_base_frac + gait_step_per_mps_frac x speed). The left foot strikes at even step
  counts, the right at odd; each stays planted for 2 x D steps, D = clamp(gait_duty_rest - gait_duty_per_mps x speed,
  gait_duty_min, gait_duty_rest), so a walker has double support and a runner a flight phase. A striking foot lands D x L ahead of
  the pelvis along the line of travel and gait_half_width_frac x height to its own side. Slower than gait_still_mps both feet are
  down beside the pelvis. Airborne (a jump): both feet leave the ground; the last planted foot is remembered. On landing both
  feet are put down at the landing instant and point, solved from the flight (C4b r1). An athlete's feet are first placed where
  he stood at the start of his first interval. A foot further than gait_reset_frac x height from the pelvis (a placement, a restart walk) is put back
  under him: that is a teleport, not a step, and is counted."""
  s=self.s;A=self.assume;t0=s.now
  for p in s.players.values():
   if not p.active or p.role=='archer':continue
   o=old.get(p.id)
   if o is None:o=(p.x,p.y,p.z)
   self.c4b_step(p,o,t0,ms,A)
 def c4b_land_tau(self,zv,o,ms):
  """Seconds after the interval's start at which the flight it began with reaches the ground (z0 + vz0 t - g t^2 / 2 = 0), or None
  when the start state is not known (no record, or a record that does not match the height he began the interval at)."""
  if zv is None or abs(zv[0]-o[2])>1e-9 or ms<=0:return None
  g=self.assume['gravity'];z0,vz0=max(0.,zv[0]),zv[1];return max(0.,(vz0+math.sqrt(vz0*vz0+2*g*z0))/g)
 def c4b_lateral(self,p,hx,hy,side):
  w=self.assume['gait_half_width_frac']*p.a.height;return(-hy*w*side,hx*w*side)
 def c4b_plant(self,p,k,x,y,t,n=None):
  f=p.feet[k];f.update(x=x,y=y,planted=True,t=t);f['n']=n if n is not None else f.get('n',0)
 def c4b_lift(self,p,k,t):
  f=p.feet[k]
  if f['planted']:f['planted']=False;p.last_plant=(f['x'],f['y'],t,k)
 def c4b_down(self,p,t,heading=None,at=None):
  hx,hy=heading or(p.facing if math.hypot(*p.facing)>0 else(1.,0.));cx,cy=at if at is not None else(p.x,p.y)
  for k,side in(('L',1),('R',-1)):
   lx,ly=self.c4b_lateral(p,hx,hy,side);self.c4b_plant(p,k,cx+lx,cy+ly,t)
  p.feet['L']['n']=0;p.feet['R']['n']=-1;p.gait_u=0.
 def c4b_step(self,p,o,t0,ms,A):
  zv=getattr(p,'c4b_zv',None);p.c4b_zv=(p.z,p.vz) #C4b r1: his height and vertical speed at the end of this interval, which is where the next one starts
  if getattr(p,'feet',None)is None:
   #C4b r1: the feet are first put down where he stood when the interval began (its start position and time), and the gait is
   #then advanced through the interval. (C4b put them at the interval's end, timed at its start.)
   p.feet={'L':{'planted':False},'R':{'planted':False}};p.last_plant=None;p.c4b_air=False;self.c4b_down(p,t0,at=(o[0],o[1]));self.stats['c4b_feet_initialised']+=1
  ft=p.feet;h=p.a.height
  air=p.posture=='airborne'or p.z>.02
  if air and getattr(p,'c4b_air',False)and p.posture=='airborne'and p.z<=.02:
   tau=self.c4b_land_tau(zv,o,ms)
   if tau is not None and tau<=ms/1000.+1e-9:air=False;self.stats['c4b_landings_at_interval_end']+=1 #C4c: the exact landing/release tie
  if air:
   #in the air: both feet leave the ground together; the one nearer the goal he attacks is remembered last (the planted-feet rule)
   up=[k for k in('L','R')if ft[k]['planted']]
   if up:
    gx=self.s.attack_goal(p.team);up.sort(key=lambda k:-norm(ft[k]['x']-gx,ft[k]['y']-50))
    for k in up:self.c4b_lift(p,k,t0)
   p.c4b_air=True;return
  if p.posture=='grounded':return
  if p.c4b_air:
   #C4b r1: landed in this interval. The flight is ballistic from the height and vertical speed he began the interval with, so the
   #landing instant is the root of z0 + vz0 t - g t^2 / 2 = 0, kept inside the interval (the motion kernel, which says whether he is
   #down at its end, decides which interval he lands in). The pelvis is placed on the interval's straight path at that instant;
   #both feet go down there, then, and the gait is advanced only through the part of the interval after the landing.
   p.c4b_air=False;T=ms/1000.;tau=self.c4b_land_tau(zv,o,ms)
   if tau is not None:tau=min(T,tau)
   else:tau=0.;self.stats['c4b_landings_unsolved']+=1 #no record of how the flight began: down at the interval's start, as in C4b
   fr=tau/T if T>0 else 0.;lx,ly=o[0]+fr*(p.x-o[0]),o[1]+fr*(p.y-o[1]);tl=t0+tau*1000
   self.c4b_down(p,tl,at=(lx,ly));self.stats['c4b_landings']+=1
   o=(lx,ly,0.);ms=ms-tau*1000;t0=tl
  if ms<=1e-9:return #nothing left of the interval (he landed at its end, or a zero-length call): the feet stay as they are
  far=A['gait_reset_frac']*h
  if any(ft[k]['planted']and norm(ft[k]['x']-o[0],ft[k]['y']-o[1])>far for k in('L','R')):
   self.stats['c4b_feet_reset']+=1;self.c4b_down(p,t0+ms);return
  dx,dy=p.x-o[0],p.y-o[1];d=math.hypot(dx,dy);v=d/(ms/1000.)if ms>0 else 0.
  if v<A['gait_still_mps']:
   if not(ft['L']['planted']and ft['R']['planted']):self.c4b_down(p,t0+ms) #standing: both feet down beside him
   return
  L_=h*min(A['gait_step_max_frac'],A['gait_step_base_frac']+A['gait_step_per_mps_frac']*v)
  D=max(A['gait_duty_min'],min(A['gait_duty_rest'],A['gait_duty_rest']-A['gait_duty_per_mps']*v))
  hx,hy=dx/d,dy/d;u0=p.gait_u;u1=u0+d/L_;evs=[]
  for k in('L','R'):
   n=ft[k].get('n',0)
   if ft[k]['planted']and n+2*D<=u1:evs.append((max(u0,n+2*D),1,k,None)) #a lift (one already due is done at the start of the interval)
  n=math.floor(u0)+1
  while n<=u1:
   k='L'if n%2==0 else'R';evs.append((n,0,k,n))
   if n+2*D<=u1:evs.append((n+2*D,1,k,None))
   n+=1
  for u,kind,k,n in sorted(evs,key=lambda e:(e[0],-e[1])):
   fr=(u-u0)/(u1-u0)if u1>u0 else 0.;t=t0+fr*ms;px,py=o[0]+fr*dx,o[1]+fr*dy
   if kind==0:
    if ft[k]['planted']:self.c4b_lift(p,k,t) #a foot cannot strike while it is still down: it is lifted first (only at speed changes)
    lx,ly=self.c4b_lateral(p,hx,hy,1 if k=='L'else-1);self.c4b_plant(p,k,px+hx*D*L_+lx,py+hy*D*L_+ly,t,n)
   else:self.c4b_lift(p,k,t)
  p.gait_u=u1
 def c4c_body(self,old,db,ms,old_positions):
  """C4c: the Keeper's body as a capsule of his radius, from his feet to his height: upright, along his dive while launched, lying
  along it while down after one. The ball's swept path is tested against it as both move through the interval (sampled every
  0.15 m of ball travel, then bisected); the first approach to within the two radii is a block. Only the Keeper's body is
  modelled; field players' bodies are not (declared)."""
  s=self.s;b=s.ball;dt=ms/1000.;out=[]
  if dt<=0 or b.carrier is not None:return out
  span=math.sqrt(sum(c*c for c in db));n=max(4,int(span/.15)+2)
  for p in s.players.values():
   if not p.active or p.role!='keeper'or b.last_releaser==p.id:continue
   #the same participation rules as a play with the hands (penalty participants, the tail owner in a finishing flight, opening
   #contestants, exclusive recovery): where his hands may not play the ball, his body does not block it either
   if s.penalty is not None and p.id not in(s.penalty['runner'],s.penalty['keeper']):continue
   if s.phase==Phase.FLIGHT and p.team==s.tail_owner:continue
   if s.phase==Phase.OPENING and not s.opening_touched and p.id not in s.opening_contestants:continue
   if s.phase==Phase.AWARD and p.team!=s.owner:continue
   o=old_positions.get(p.id)if old_positions else None
   if o is None:o=(p.x,p.y,p.z)
   h=p.a.height;r=p.radius;R=r+b.radius;L=getattr(p,'c4c_launch',None);lift=0.
   if L is not None:k=math.sqrt(sum(c*c for c in L['off']));ax=tuple(c/k for c in L['off'])
   elif p.posture=='grounded':
    dd=getattr(p,'c4c_down',None);dv=dd[0]if dd is not None and s.now<=dd[1]else p.facing
    k=math.hypot(*dv)or 1.;ax=(dv[0]/k,dv[1]/k,0.);lift=r #lying along his dive (or, down any other way, along the way he faced)
   else:ax=(0.,0.,1.)
   def at(f):
    B=[old[j]+db[j]*f for j in range(3)];P=[o[j]+((p.x,p.y,p.z)[j]-o[j])*f for j in range(3)];P[2]+=lift
    a0=[P[j]+ax[j]*r for j in range(3)];seg=h-2*r;w=[B[j]-a0[j]for j in range(3)]
    u=clamp(sum(w[j]*ax[j]for j in range(3)),0.,seg);c=[a0[j]+ax[j]*u for j in range(3)]
    return math.sqrt(sum((B[j]-c[j])**2 for j in range(3))),[(B[j]-c[j])for j in range(3)]
   prev=0.;d0,v0=at(0.);pv=((p.x-o[0])/dt,(p.y-o[1])/dt,(p.z-o[2])/dt)
   if d0<R:
    #inside his body as the interval begins: if it is going further in (a shot from a carrier he is confronting) it is blocked at
    #once; if it is coming out (the block that put it there has been applied) it is not touched again
    k=math.sqrt(sum(c*c for c in v0))
    nrm=[c/k for c in v0]if k>1e-9 else None
    if nrm is not None and sum(((b.vx,b.vy,b.vz)[j]-pv[j])*nrm[j]for j in range(3))<-2.: #going in at more than 2 m/s (a loose ball lying against him is not a block)
     self.c4c_cinfo[(p.id,'body')]=(nrm,pv,None);out.append((0.,d0,p.id,p,None,pv))
    continue
   for i in range(1,n+1):
    f=i/n;d,_=at(f)
    if d<R:
     lo_,hi_=prev,f
     for _ in range(8):
      mid=(lo_+hi_)/2
      if at(mid)[0]<R:hi_=mid
      else:lo_=mid
     d,v=at(hi_);k=math.sqrt(sum(c*c for c in v))or 1.;nrm=[c/k for c in v]
     if sum(((b.vx,b.vy,b.vz)[j]-pv[j])*nrm[j]for j in range(3))<-.3: #meeting him at more than 0.3 m/s
      self.c4c_cinfo[(p.id,'body')]=(nrm,pv,None);out.append((hi_,d,p.id,p,None,pv))
     break
    prev=f
  return out
 def c4c_keepers(self,targets):
  """C4c Keeper (build specification 7). Called at the start of every C3 interval, from the committed state.
  1. Perception. A Keeper sees a free ball's course from the instant it last changed (a release, a committed deflection: the same
     instant the catch model uses). He can act on it keeper_reaction_s x (1.3 - 0.6 x awareness) later, plus keeper_unset_s if he
     was moving faster than keeper_set_mps at that instant. Before then his hands are not set for it and he keeps his last plan.
  2. Read. At that instant he forecasts the ball's flight from its observed position and velocity with the match's own flight
     rules (c4c_path). Nothing unobserved is used: no aim error, no later decision. A flight is a threat if it crosses his goal line
     within the aperture plus one metre.
  3. Plan (c4c_plan): the earliest point of that flight his hands can meet, either by moving on his feet (the ordinary motion
     limits) or by a launch: a dive or jump that leaves the ground at once with a push of up to sqrt(2 x acceleration x
     keeper_pushoff_frac x height) horizontally and up to sqrt(2 g jump_height) vertically, within one elliptical budget.
     If no point is reachable he launches at the one he misses by least, if that is within keeper_attempt_margin_m of his reach;
     otherwise he makes no attempt. The plan, and whether it was feasible, is recorded.
  4. A launched Keeper flies without steering and lands when his flight reaches the ground (in dead time too). After a dive (lean
     of at least keeper_dive_lean) he goes to ground by the engine's own grounding (C3b: slide, then get-up); holding the ball he
     lands upright but cannot act for the time a get-up takes. That is the price of committing. A launch cannot meet the ball
     sooner than keeper_launch_min_s after he decides.
  5. Positioning when there is no ball to save: on the line from the centre of his goal to the ball, off his line by
     keeper_depth_frac of the ball's distance (between keeper_depth_min_m and keeper_depth_max_m). When an opposing carrier
     within 35 m begins a wind-up (visible preparation) he stops and sets (keeper_windup_set). An opposing carrier within
     keeper_confront_m of the centre of his goal is confronted: he goes to meet him, and the ordinary contact rules apply (keeper_confront).
     A slow loose ball (under 6 m/s) within keeper_gather_m of him in his own Keeper Zone: he goes to gather it."""
  s=self.s;A=self.assume;b=s.ball
  for p in s.players.values():
   if not p.active or p.role!='keeper':continue
   L=getattr(p,'c4c_launch',None)
   if L is not None:
    if p.posture=='airborne'and s.now<L['t_land']-.5:continue
    self.c4c_land(p,L)
   if p.posture!='grounded':p.c4c_down=None
   if not p.eligible(s.now)or p.posture=='grounded'or b.carrier==p.id:continue
   if b.carrier is None and b.mode!=BallMode.CONTESTED:
    seen=getattr(p,'c4c_seen',None)
    if seen is None or seen[0]!=b.version:
     prev=seen[1]if seen is not None else-1e18 #as the catch model: a release or committed deflection newer than the last one seen, else now
     t_obs=max([t for t in(b.release_time,getattr(b,'course_time',-1))if t is not None and prev<t<=s.now]or[s.now])
     sp=math.hypot(p.vx,p.vy);react=1000*(A['keeper_reaction_s']*(1.3-.6*p.a.awareness)+(A['keeper_unset_s']if sp>A['keeper_set_mps']else 0.))
     p.c4c_seen=seen=(b.version,t_obs,t_obs+react,sp>A['keeper_set_mps']);p.c4c_plan=None
    pl=getattr(p,'c4c_plan',None);force=False
    if pl is not None and pl['kind']=='approach'and s.now>=pl['launch_at']:p.c4c_plan=pl=None;force=True #his launch instant: read again, and go
    if s.phase in(Phase.LIVE,Phase.FLIGHT,Phase.PENALTY)and s.now>=seen[2]-1e-9 and pl is None:
     path=self.c4c_path(b);cross=self.c4c_threat(p,path)
     if cross is not None:p.c4c_plan=self.c4c_plan(p,path,cross,seen,force)
     else:p.c4c_plan={'kind':'no_threat'}
    pl=getattr(p,'c4c_plan',None)
    if pl is not None and pl['kind']=='approach':
     p.target=pl['target'];p.next_decision=pl['launch_at'];targets.pop(p.id,None);continue
    if pl is not None and pl['kind']=='step'and s.now<pl['until']:
     p.target=pl['target'];p.next_decision=pl['until'];targets.pop(p.id,None);continue
    if s.now<seen[2]-1e-9:targets.pop(p.id,None);continue #not yet reacted to this flight: he carries on as he was
    if pl is not None and pl['kind']!='no_threat':targets[p.id]=(p.x,p.y);p.next_decision=s.now;continue #a flight he has played or let go: he holds
   if s.phase!=Phase.LIVE:continue
   t=self.c4c_position(p)
   if t is not None:targets[p.id]=t;p.next_decision=s.now
 def c4c_due(self,landings_only=False):
  s=self.s;b=s.ball;out=[]
  for p in s.players.values():
   if not p.active or p.role!='keeper':continue
   L=getattr(p,'c4c_launch',None)
   if L is not None:out.append(L['t_land']);continue
   if landings_only:continue
   seen=getattr(p,'c4c_seen',None)
   pl=getattr(p,'c4c_plan',None)
   if b.carrier is None and seen is not None and seen[0]==b.version and pl is None:out.append(seen[2])
   if pl is not None and pl['kind']=='approach':out.append(pl['launch_at'])
  return out
 def c4c_path(self,b,horizon=3.,step=.005):
  """The ball's flight forecast from its observed state, with the match's flight, drag, bounce and roll rules, in 5 ms steps."""
  A=self.assume;g=A['gravity'];drag=math.exp(-A['ball_drag']*step);e=A['ball_restitution']
  x,y,z,vx,vy,vz=b.x,b.y,b.z,b.vx,b.vy,b.vz;t=0.;out=[(0.,x,y,z)]
  while t<horizon:
   x+=vx*step;y+=vy*step;z+=vz*step-.5*g*step*step;vx*=drag;vy*=drag;vz=(vz-g*step)*drag
   if z<=b.radius:
    z=b.radius
    if abs(vz)>2:vz=-vz*e;vx*=.76;vy*=.76
    else:vz=0.;vx*=max(0.,1-step*3);vy*=max(0.,1-step*3)
   t+=step;out.append((t,x,y,z))
   if not(-2<=x<=102 and-2<=y<=102):break
  return out
 def c4c_threat(self,p,path):
  """Index and point at which the forecast flight crosses this Keeper's goal line inside the aperture (plus 1 m), or None."""
  gx=self.s.ends[p.team]
  for i in range(1,len(path)):
   t0,x0,y0,z0=path[i-1];t1,x1,y1,z1=path[i]
   if(x0-gx)*(50-gx)>=0 and(x1-gx)*(50-gx)<=0 and x1!=x0: #from the field side onto or over the line
    f=(gx-x0)/(x1-x0);y=y0+f*(y1-y0);z=z0+f*(z1-z0)
    return(i,t0+f*(t1-t0),y,z)if math.hypot(y-50,z)<=7. else None
  return None
 def c4c_reach(self,p):
  return p.a.reach*1.1 #the same hand reach the catch model gives a Keeper
 def c4c_off(self,p,lean,ux,uy):
  """Hand point relative to his base (feet) point. Upright: 0.62 x height straight up (the catch model's hand height). Leaning into
  a dive the hands go out along it: keeper_extension_frac x height out, down to keeper_dive_hand_frac x height up at full lean."""
  A=self.assume;h=p.a.height;e=A['keeper_extension_frac']*h*lean
  return(ux*e,uy*e,(.62-(.62-A['keeper_dive_hand_frac'])*lean)*h)
 def c4c_plan(self,p,path,cross,seen,force=False):
  s=self.s;A=self.assume;g=A['gravity'];R=self.c4c_reach(p);h=p.a.height;now_t=s.now
  umax=math.sqrt(2*p.a.acceleration*A['keeper_pushoff_frac']*h);vj=math.sqrt(2*g*p.a.jump_height);acc=p.a.acceleration
  i_cross,t_cross,cy,cz=cross;dt_seen=(s.now-seen[1])/1000.;best=None;pick=None
  for i in range(1,i_cross+1):
   #on his feet, if he can anywhere on the flight (no commitment): the hands stay at 0.62 x height; the pelvis can move by at most
   #a.t^2/2 from where his velocity carries him
   t,x,y,z=path[i];hx,hy=p.x+p.vx*t,p.y+p.vy*t;dz=z-(p.z+.62*h)
   if abs(dz)<R:
    room=.5*acc*t*t;need=max(0.,math.hypot(x-hx,y-hy)-room)
    if need*need+dz*dz<=(.95*R)**2:pick=('step',t,x,y,z,None);break
  for i in range(1,i_cross+1):
   if pick is not None:break
   t,x,y,z=path[i]
   if t<A['keeper_launch_min_s']:continue #a launch takes time to leave the ground: it cannot meet the ball sooner
   #else a launch at the earliest point he can meet. He stays on his feet, accelerating towards the meeting point, until the last
   #keeper_dive_time_s before it (or launches now if it is sooner), and carries that run into the launch.
   tl=0. if force else max(0.,t-A['keeper_dive_time_s']);tau=t-tl
   dx0,dy0=x-p.x-p.vx*t,y-p.y-p.vy*t;D0=math.hypot(dx0,dy0);ux,uy=(dx0/D0,dy0/D0)if D0>1e-9 else(0.,0.)
   run=.5*acc*tl*tl+acc*tl*tau;f_=min(1.,D0/run)if run>1e-9 else 0.;D=D0-f_*run #he runs no further than he needs to
   #the least lean (push / greatest push, in twentieths) that brings the hands within keeper_aim_frac of their reach of the ball (or
   #failing that the lean that gets them closest, if that is within 0.9 of their reach) at that
   #moment: the push carries him along the line to the ball and the hands go out with the lean; the vertical launch puts the
   #hands at the ball's height if it can, at least 5 cm off the ground (he is still in the air when they meet), within the
   #elliptical budget (push/greatest push)^2 + (vertical/greatest vertical)^2 <= 1. Lean 0 with no rise is standing still.
   lp=None;got=None
   for j in range(21):
    lean=j/20.;u=lean*umax;off=self.c4c_off(p,lean,ux,uy);vmax=vj*math.sqrt(max(0.,1-lean*lean));zbmax=vmax*tau-.5*g*tau*tau
    sh=abs(D-(u*tau+math.hypot(off[0],off[1])))
    if j==0:zb=clamp(z-off[2],0.,max(0.,zbmax))
    elif zbmax<.05:break #he cannot stay up until then with this much lean, nor with more
    else:zb=clamp(z-off[2],.05,zbmax)
    vz=(zb+.5*g*tau*tau)/tau if(j>0 or zb>0)else 0.;res=math.hypot(sh,z-off[2]-zb)
    L_=(u*ux,u*uy,vz,lean,ux,uy,res,tl,f_*acc)
    if lp is None or res<lp[0]-1e-9:lp=(res,L_)
    if res<=A['keeper_aim_frac']*R:got=(res,L_);break #the least lean that puts his hands on the ball
   if got is None and lp is not None and lp[0]<=.9*R:got=lp #else the closest he can get, if his hands still reach it squarely enough
   if got is not None:pick=('launch',t,x,y,z,got[1]);break
   if lp is not None and(best is None or lp[0]<best[0]):best=(lp[0],('launch',t,x,y,z,lp[1]))
  feasible=pick is not None
  if pick is None:
   if best is not None and best[0]<=R+A['keeper_attempt_margin_m']:pick=best[1]
  rec={'player':p.id,'reaction_ms':round(s.now-seen[1],1),'unset':seen[3],'crossing':[round(t_cross*1000,1),round(cy,2),round(cz,2)],'feasible':feasible}
  if pick is None:
   self.stats['c4c_no_attempt']+=1;self.e.emit('keeper_read','C4c-K',kind='none',**rec,least_miss_m=round(best[0]-R,3)if best else None)
   return{'kind':'none'}
  kind,t,x,y,z,L=pick;rec.update(kind=kind,meet_ms=round(t*1000,1),meet=[round(x,2),round(y,2),round(z,2)])
  if kind=='step':
   self.stats['c4c_steps']+=1;self.e.emit('keeper_read','C4c-K',**rec)
   return{'kind':'step','target':(clamp(x,-1,101),clamp(y,-1,101)),'until':s.now+int(math.ceil(t*1000))}
  vx,vy,vz,lean,ux,uy,res,tl,arun=L
  if tl>.005: #he runs first and launches later (c4c_keepers re-plans at that instant, from what he then sees and where he then is)
   self.stats['c4c_approaches']+=1;rec.update(kind='approach',launch_in_ms=round(tl*1000,1),lean=round(lean,3),miss_m=round(max(0.,res-R),3));self.e.emit('keeper_read','C4c-K',**rec)
   return{'kind':'approach','target':(clamp(p.x+ux*20,-1,101),clamp(p.y+uy*20,-1,101)),'launch_at':s.now+int(math.ceil(tl*1000))}
  if vz<=0 and lean<=0: #nothing to launch: he stays where he is and lets it come to his hands
   self.stats['c4c_steps']+=1;rec.update(kind='step');self.e.emit('keeper_read','C4c-K',**rec)
   return{'kind':'step','target':(p.x,p.y),'until':s.now+int(math.ceil(t*1000))}
  p.vx+=vx;p.vy+=vy;p.vz=vz;p.posture='airborne'
  t_land=s.now+1000*2*vz/g;dive=lean>=A['keeper_dive_lean']
  p.c4c_launch={'t0':s.now,'t_land':t_land,'off':self.c4c_off(p,lean,ux,uy),'lean':lean,'dir':(ux,uy),'dive':dive}
  self.stats['c4c_dives'if dive else'c4c_jumps']+=1
  rec.update(push=[round(vx,3),round(vy,3)],vz=round(vz,3),lean=round(lean,3),dive=dive,miss_m=round(max(0.,res-R),3),land_ms=round(t_land-s.now,1))
  self.e.emit('keeper_read','C4c-K',**rec);return{'kind':'launch'}
 def c4c_land_due(self):
  s=self.s
  for p in s.players.values():
   L=getattr(p,'c4c_launch',None)
   if L is not None and p.role=='keeper'and s.now>=L['t_land']-.5:self.c4c_land(p,L)
 def c4c_land(self,p,L):
  s=self.s;A=self.assume;p.c4c_launch=None;p.z=0.;p.vz=0.
  if L['dive']:
   #after a dive he is on the ground: the engine's own grounding (C3b: he slides on with his speed, slowed by ground friction, then
   #rises in get_up_time_s x (1.5 - balance)); holding the ball he lands on his feet but cannot act for the time a get-up would take
   if s.ball.carrier==p.id:
    rise=int(math.ceil(1000*A['get_up_time_s']*(1.5-p.a.balance)))if self.c3b else 800;p.posture='upright';p.next_action=max(p.next_action,s.now+rise)
   else:
    p.posture='upright'
    if self.c3b:self.e.go_down(p)
    else:p.posture='grounded';p.down_at=s.now;p.next_action=s.now+800
    p.c4c_down=(L['dir'],p.next_action)
   rec=p.next_action-s.now
   self.stats['c4c_recoveries']+=1;self.e.emit('keeper_landed','C4c-K',player=p.id,dive=True,recover_ms=rec,holding=s.ball.carrier==p.id)
  else:
   if p.posture=='airborne':p.posture='upright'
   self.e.emit('keeper_landed','C4c-K',player=p.id,dive=False,recover_ms=0,holding=s.ball.carrier==p.id)
 def c4c_position(self,p):
  s=self.s;A=self.assume;b=s.ball;gx=s.ends[p.team];inward=1. if gx==0 else-1.
  c=s.players.get(b.carrier)
  if self.ctrl and(c is None or c.team==p.team):p.c4c2_confronting=False #C4c2 review
  if c is None and math.hypot(b.vx,b.vy)<6. and math.hypot(b.x-p.x,b.y-p.y)<=A['keeper_gather_m']and self.e.zone(b.x,b.y)==s.own_zone(p.team):
   return(clamp(b.x,0,100),clamp(b.y,0,100)) #a slow loose ball near him in his zone: he gathers it
  if c is not None and c.team!=p.team:
   if self.ctrl and A['ctrl_keeper']:
    if self.c4c2_confront(p,c):
     if not getattr(p,'c4c2_confronting',False):p.c4c2_confronting=True;self.e.emit('keeper_confront','C4c2-7',player=p.id,carrier=c.id,d=round(math.hypot(c.x-gx,c.y-50),2))
     return(clamp(c.x+c.vx*.3,0,100),clamp(c.y+c.vy*.3,0,100))
    p.c4c2_confronting=False
   elif A['keeper_confront']and math.hypot(c.x-gx,c.y-50)<=A['keeper_confront_m']:
    return(clamp(c.x+c.vx*.3,0,100),clamp(c.y+c.vy*.3,0,100)) #confront a carrier at his goal mouth
   if A['keeper_windup_set']and c.id in self.pending_ball_actions and math.hypot(c.x-gx,c.y-50)<35:return(p.x,p.y) #set
  bx,by=(c.x,c.y)if c is not None else(b.x,b.y)
  vx,vy=bx-gx,by-50;d=math.hypot(vx,vy)
  if d<1e-6:vx,vy,d=inward,0.,1.
  depth=min(clamp(A['keeper_depth_frac']*d,A['keeper_depth_min_m'],A['keeper_depth_max_m']),max(A['keeper_depth_min_m'],.5*d))
  tx=gx+vx/d*depth;ty=50+vy/d*depth
  if (tx-gx)*inward<.5:tx=gx+inward*.5
  return(tx,clamp(ty,44,56))
 # ---------------- C4c2: the controller's estimators (read-only; used by the drills that measure them, and by the controller) ----------------
 def c4c2_windup_s(self,p,kind='shot'):
  return self.assume['pass_release_ms']*((1.6-.5*p.a.kicking)if kind=='shot'else(1.35-.5*p.a.ball_handling))/1000.
 def c4c2_engage_s(self,q,p,x,y):
  """Time for opponent q to come within holding reach of an athlete p standing at (x, y): his body radius plus p's, plus 0.7 x their
  reaches (the kernel's holding range). Kinematics only, from what is observable now: q's velocity towards the point (braking first
  if he is moving away), then his acceleration (x (0.55 + 0.45 x fatigue)) up to his running speed (x (0.70 + 0.30 x fatigue) x 0.88).
  No reaction delay (conservative). The drills measure what a margin computed this way means (c4c2_estimates.json, windup)."""
  if not q.active:return 9.
  wait=0.
  if q.posture=='grounded':wait=max(0.,q.next_action-self.s.now)/1000.
  if q.frozen(self.s.now):wait=max(wait,(getattr(q,'freeze_until',self.s.now)-self.s.now)/1000.)
  if wait>0:
   gap=math.hypot(x-q.x,y-q.y)-(q.radius+p.radius+.7*(q.a.reach+p.a.reach))
   if gap<=0:return wait
   V=max(.5,q.a.maximum_speed*(.70+.30*q.fatigue)*.88);a=max(.5,q.a.acceleration*(.55+.45*q.fatigue));t1=V/a;d1=V/2*t1
   return wait+(math.sqrt(2*gap/a)if d1>=gap else t1+(gap-d1)/V) #from rest once he is up (or unfrozen)
  gap=math.hypot(x-q.x,y-q.y)-(q.radius+p.radius+.7*(q.a.reach+p.a.reach))
  if gap<=0:return 0.
  ux,uy=(x-q.x)/math.hypot(x-q.x,y-q.y),(y-q.y)/math.hypot(x-q.x,y-q.y);u=q.vx*ux+q.vy*uy;t=0.
  if u<0:t=-u/q.a.braking;gap+=u*u/(2*q.a.braking);u=0.
  V=max(.5,q.a.maximum_speed*(.70+.30*q.fatigue)*.88);a=max(.5,q.a.acceleration*(.55+.45*q.fatigue));u=min(u,V)
  t1=(V-u)/a;d1=(u+V)/2*t1
  return t+((-u+math.sqrt(u*u+2*a*gap))/a if d1>=gap else t1+(gap-d1)/V)
 def c4c2_margin(self,p,x,y,extra_s):
  opp=[q for q in self.s.players.values()if q.team!=p.team and q.active and q.role!='archer']
  return min((self.c4c2_engage_s(q,p,x,y)for q in opp),default=9.)-extra_s
 @staticmethod
 def c4c2_interp(xs,ys,x):
  if x<=xs[0]:return ys[0]
  if x>=xs[-1]:return ys[-1]
  for i in range(len(xs)-1):
   if xs[i]<=x<=xs[i+1]:f=(x-xs[i])/(xs[i+1]-xs[i]);return ys[i]+f*(ys[i+1]-ys[i])
 def c4c2_conv(self,d,ang,team,out=False):
  """Drill estimate of a shot's chance of scoring from distance d (m to the centre of the goal) at angle ang (degrees off the axis),
  by the match's own shot routine against the opposing Keeper (his height; set on his line, or confronting when out), at this
  match's ball speed. Linear in distance, angle, height and ball speed between the drill cells."""
  E=C4C2_EST['conv_out'if out else'conv'];k=next((q for q in self.s.players.values()if q.team!=team and q.active and q.role=='keeper'),None)
  h=k.a.height if k else 2.55;sp=self.cfg['pocket']['ball_speed'];D=E['dist'];Aa=E['ang'];H=E['height'];S=E['speed']
  def at(si,hi):
   T=E['p'][si][hi];row=[self.c4c2_interp(Aa,[T[i][j]for j in range(len(Aa))],ang)for i in range(len(D))];return self.c4c2_interp(D,row,d)
  def h_(si):return self.c4c2_interp(H,[at(si,hi)for hi in range(len(H))],h)
  return self.c4c2_interp(S,[h_(si)for si in range(len(S))],sp)
 def c4c2_goal_factor(self,margin):
  E=C4C2_EST['windup'];return self.c4c2_interp(E['margin'],E['goal_factor'],margin)
 def c4c2_tackled_p(self,margin):
  E=C4C2_EST['windup'];return self.c4c2_interp(E['margin'],E['p_tackled'],margin)
 def c4c2_carry_p(self,d,ang,confront,chaser):
  E=C4C2_EST['carry'];T=E['p'][1 if confront else 0][1 if chaser else 0]
  row=[self.c4c2_interp(E['ang'],[T[i][j]for j in range(len(E['ang']))],ang)for i in range(len(E['dist']))];return self.c4c2_interp(E['dist'],row,d)
 def c4c2_pass_p(self,L,lane):
  E=C4C2_EST['pass'];T=E['p'];row=[self.c4c2_interp(E['lane'],T[i],lane)for i in range(len(E['dist']))];return self.c4c2_interp(E['dist'],row,L)
 # ---------------- C4c2: the common controller ----------------
 def c4c2_vposs(self,d):
  E=C4C2_POS;e_=E['dist_edges'];i=next((j for j in range(len(e_)-1)if e_[j]<=d<e_[j+1]),len(e_)-2)
  return E['zone_value_units'][i][0]*self.cfg['pocket'].get('release_points',2)
 def c4c2_keeper_out(self,k):
  return k is not None and math.hypot(k.x-self.s.ends[k.team],k.y-50)>self.assume['keeper_depth_max_m']+1.
 def c4c2_confront(self,k,c,at=None):
  """The Keeper's choice (ctrl_keeper): come out at a carrier when, by the same drill tables, that concedes less than staying. What he
  concedes is the attacker's better option: a carry-in (carry tables, Keeper staying or confronting) or a shot (conversion against a set
  or a confronting Keeper). With no Carry value there is nothing to stop by coming out, and he stays. Within 20 m only."""
  s=self.s;gx=s.ends[k.team];cx,cy=at if at is not None else(c.x,c.y);d=math.hypot(cx-gx,cy-50) #at: the same choice for a carrier imagined at another spot
  cv=self.cfg['pocket'].get('carry_value',0)if self.cfg['pocket'].get('release_territories')else 0
  if cv<=0 or d>20:return False
  ang=math.degrees(math.atan2(abs(cy-50),abs(gx-cx)+1e-9));v=self.e.territory_points(self.e.territory(c.team,cx,cy))
  chaser=any(self.c4c2_engage_s(q,c,gx,50)<d/max(c.speed,4.)for q in s.players.values()if q.team==k.team and q.role=='field'and q.active)
  stay=max(self.c4c2_carry_p(d,ang,False,chaser)*cv,self.c4c2_conv(d,ang,c.team,False)*v)
  out=max(self.c4c2_carry_p(d,ang,True,chaser)*cv,self.c4c2_conv(d,ang,c.team,True)*v)
  return out<stay
 def c4c2_eval(self,p,x,y,clock,arrow_t=None,origin=False):
  """Expected points of a shot and of a carry-in for p from (x, y), from the drill tables, and the value of what is kept if the attempt
  is stopped first (a first tackle keeps the ball: the retained value; after it, nothing)."""
  s=self.s;e=self.e;pc=self.cfg['pocket'];gx=s.attack_goal(p.team);d=math.hypot(x-gx,y-50);ang=math.degrees(math.atan2(abs(y-50),abs(gx-x)+1e-9))
  terr=e.territory(p.team,*e.c4b_origin(p)[0])if origin else e.territory(p.team,x,y)
  v=0 if(pc.get('zone_only')and terr=='outside_release')else e.territory_points(terr)
  k=next((q for q in s.players.values()if q.team!=p.team and q.active and q.role=='keeper'),None)
  w=self.c4c2_windup_s(p);m=self.c4c2_margin(p,x,y,w)
  if arrow_t is not None:m=min(m,arrow_t-w)
  vf=C4C2_EST['v_ret']['zone_value_units']*pc.get('release_points',2)if s.tackle_count==0 else 0.
  kout=self.c4c2_keeper_out(k)or(not origin and k is not None and self.assume['ctrl_keeper']and self.c4c2_confront(k,p,(x,y))) #at a spot ahead: the Keeper as his declared rule will have him
  gf=self.c4c2_goal_factor(m);pt=self.c4c2_tackled_p(m);cs=self.c4c2_conv(d,ang,p.team,kout)
  shoot=cs*gf*v+pt*vf if(clock>w+.05 and v>0)else 0. #a shot that does not score ends the possession unless he was tackled first (a first tackle keeps it)
  cv=pc.get('carry_value',0)if pc.get('release_territories')else 0;carry=0.;pcy=None
  if cv>0 and d<=20 and clock>d/max(p.speed,4.):
   conf=kout or(k is not None and self.assume['ctrl_keeper']and self.c4c2_confront(k,p,(x,y)))
   chaser=any(self.c4c2_engage_s(q,p,gx,50)<d/max(p.speed,4.)for q in s.players.values()if q.team!=p.team and q.role=='field'and q.active)
   pcy=self.c4c2_carry_p(d,ang,conf,chaser);carry=pcy*cv+(1-pcy)*vf
  return {'shoot':shoot,'carry':carry,'v':v,'d':d,'margin':m,'goal_factor':gf,'p_tackled':pt,'p_conv':cs,'p_carry':pcy,'vf':vf}
 def c4c2_carry_chance(self,p,x,y):
  #the carry table's chance for p running in from (x, y): the Keeper confronting if he is out or his rule would bring him out there
  s=self.s;gx=s.attack_goal(p.team);d=math.hypot(x-gx,y-50);ang=math.degrees(math.atan2(abs(y-50),abs(gx-x)+1e-9))
  k=next((q for q in s.players.values()if q.team!=p.team and q.active and q.role=='keeper'),None)
  conf=self.c4c2_keeper_out(k)or(k is not None and self.assume['ctrl_keeper']and self.c4c2_confront(k,p,(x,y)))
  chaser=any(self.c4c2_engage_s(q,p,gx,50)<d/max(p.speed,4.)for q in s.players.values()if q.team!=p.team and q.role=='field'and q.active)
  return self.c4c2_carry_p(d,ang,conf,chaser)
 def c4c2_cont(self,p,x,y,clock,arrow_t=None):
  """Carrying on: the better of the stored matches' value of the possession from here and one step ahead (the same choices from
  ctrl_lookahead_s further on), times the chance he gets there with the ball: the pressure drill's tackle chance at the travel margin,
  and, within 20 m, the carry table's ratio of success from here to success from there."""
  s=self.s;A=self.assume;gx=s.attack_goal(p.team);tau=A['ctrl_lookahead_s'];d=math.hypot(x-gx,y-50)
  if clock<tau+self.c4c2_windup_s(p)+.2:return 0.
  ux,uy=(gx-x)/max(d,1e-6),(50-y)/max(d,1e-6);step=min(max(0.,d-1.5),max(p.speed,.6*p.a.maximum_speed*.9)*tau);sx,sy=x+ux*step,y+uy*step
  mt=self.c4c2_margin(p,sx,sy,tau)
  if arrow_t is not None:mt=min(mt,arrow_t-tau)
  sr=1-self.c4c2_tackled_p(mt);E2=self.c4c2_eval(p,sx,sy,clock-tau)
  if d<=20.:
   #within carry range the carry table also says how likely he is to get from here to the spot with the ball: success from here =
   #reaching the spot x success from the spot, so reaching it = the ratio (at most 1), with the Keeper and chaser as at each point
   pn=self.c4c2_carry_chance(p,x,y);ps=self.c4c2_carry_chance(p,sx,sy);sr=min(sr,(min(1.,pn/ps)if ps>0 else 0.))
  vf=C4C2_EST['v_ret']['zone_value_units']*self.cfg['pocket'].get('release_points',2)if s.tackle_count==0 else 0.
  return sr*max(E2['shoot'],E2['carry'],self.c4c2_vposs(d))+(1-sr)*vf
 def c4c2_decide(self,p,clock,danger_arrow):
  """The common controller (build specification 7). The same for every scoring configuration; it reads the values in play. Choices:
  shoot now, carry in (Carry enabled), pass (the three best-ranked team-mates), or carry on. Each is valued in expected points from the
  drill tables (shot conversion, the effect of pressure on a shot, carry-in success, pass completion) and the stored matches' possession values; a
  stopped attempt keeps the retained value while the tackle count allows it; the possession clock bounds what can still be done. The
  best is taken; a team's approach (ctrl_style) prefers carrying or passing when that is within ctrl_style_band of the best."""
  s=self.s;A=self.assume;arrow_t=None
  if getattr(p,'c4c2_intent',None)and p.c4c2_intent_t<s.ball.control_time:p.c4c2_intent=None #an intent from before he (re)gained the ball is void
  if danger_arrow:
   arrow_t=min((math.hypot(ar.x-p.x,ar.y-p.y)/max(1.,math.hypot(ar.vx,ar.vy))for ar in s.arrows if ar.live and ar.team!=p.team),default=None)
  E=self.c4c2_eval(p,p.x,p.y,clock,arrow_t,origin=True);cont=self.c4c2_cont(p,p.x,p.y,clock,arrow_t)
  opts={'shoot':E['shoot'],'carry':E['carry'],'continue':cont};best_q=None;bq=-1.
  opp=[q for q in s.players.values()if q.team!=p.team and q.eligible(s.now)and q.role!='archer']
  if s.now-s.ball.control_time>180:
   for q in self.pol[p.team].pass_ranked(s,p)[:3]:
    L=math.hypot(q.x-p.x,q.y-p.y)
    if L<2.5:continue
    lane=min((segment_distance(o.x,o.y,p.x,p.y,q.x,q.y)[0]for o in opp),default=99.)
    Eq=self.c4c2_eval(q,q.x,q.y,clock-L/max(1.,self.cfg['pocket'].get('pass_speed',40.)));val=self.c4c2_pass_p(L,lane)*max(Eq['shoot'],Eq['carry'],self.c4c2_cont(q,q.x,q.y,clock))
    if val>bq:bq=val;best_q=q
   if best_q is not None:opts['pass']=bq
  best=max(opts,key=lambda k:(opts[k],k=='continue'))
  style=int(A.get('ctrl_style_'+p.team,0));band=A['ctrl_style_band']
  if style==1 and opts['carry']>0 and opts['carry']>=(1-band)*opts[best]:best='carry'
  if style==2 and 'pass'in opts and opts['pass']>=(1-band)*opts[best]:best='pass'
  prev=getattr(p,'c4c2_intent',None)
  rec=dict(player=p.id,choice=best,ev={k:round(v_,3)for k,v_ in opts.items()},d=round(E['d'],2),value=E['v'],margin=round(E['margin'],3),goal_factor=round(E['goal_factor'],3),p_tackled=round(E['p_tackled'],3),p_conv=round(E['p_conv'],3),
           p_carry=None if E['p_carry']is None else round(E['p_carry'],3),style=style)
  if best=='carry':
   if prev!='carry':p.c4c2_intent='carry';p.c4c2_intent_t=s.now;self.e.emit('controller_decision','C4c2-7',**rec);self.stats['c4c2_carry_intents']+=1
   return
  if prev=='carry':p.c4c2_intent=None;self.e.emit('carry_intent_end','C4c2-7',player=p.id,reason=best,held_ms=s.now-p.c4c2_intent_t)
  #a shot or pass is recorded when its preparation actually begins (a carrier who is held may withhold it: C3c)
  if best=='shoot':
   self.make_shot(p)
   if p.id in self.pending_ball_actions:self.e.emit('controller_decision','C4c2-7',**rec);self.stats['c4c2_shots']+=1
   return
  if best=='pass':
   rec['target']=best_q.id;self.make_pass(p,best_q,'kick'if self.pol[p.team].t.risk>.7 and math.hypot(best_q.x-p.x,best_q.y-p.y)>25 else'pass')
   if p.id in self.pending_ball_actions:
    self.e.emit('controller_decision','C4c2-7',**rec);self.stats['c4c2_passes']+=1
    if danger_arrow:p.arrow_reaction_pending=True;self.stats['arrow_evoked_pass_preparations']+=1
 def c4c2_targets(self,targets):
  """A carrier with a carry intent drives at the centre of the goal. Up to ctrl_receivers attacking team-mates go to the open spots
  that are worth most to a receiver (pass completion from the carrier x the better of a shot or a carry-in from the spot); a player
  whose time in that Keeper Zone is past 2.5 s is left to the inherited exit rule."""
  s=self.s;b=s.ball;c=s.players.get(b.carrier)
  if c is None or s.phase!=Phase.LIVE:return
  gx=s.attack_goal(c.team);sgn=s.attack_sign(c.team)
  if getattr(c,'c4c2_intent',None)=='carry':
   if s.now-getattr(c,'c4c2_intent_t',s.now)>6000 or c.c4c2_intent_t<b.control_time:c.c4c2_intent=None
   else:targets[c.id]=(gx+sgn*.6,clamp(c.y,47.,53.))
  n=int(self.assume['ctrl_receivers'])
  if n<=0 or c.role=='keeper'or math.hypot(c.x-gx,c.y-50)>40:return
  clock=s.possession_ms/1000.;opp=[q for q in s.players.values()if q.team!=c.team and q.eligible(s.now)and q.role!='archer']
  zn=s.own_zone(s.other(c.team))
  mates=[q for q in s.players.values()if q.team==c.team and q.role=='field'and q.active and q.id!=c.id and q.eligible(s.now)and q.posture=='upright'and q.zone_ms[zn]<2500]
  if not mates:return
  key=(s.now//500,c.id)
  if getattr(self,'_c4c2_spots_key',None)!=key:
   spots=[]
   for r_ in(8.,12.,16.,19.):
    for a_ in(-45,-20,0,20,45):
     x=gx-sgn*r_*math.cos(math.radians(a_));y=50+r_*math.sin(math.radians(a_));L=math.hypot(x-c.x,y-c.y)
     if L<4:continue
     lane=min((segment_distance(o.x,o.y,c.x,c.y,x,y)[0]for o in opp),default=99.);q0=mates[0]
     Eq=self.c4c2_eval(q0,x,y,clock);spots.append((self.c4c2_pass_p(L,lane)*max(Eq['shoot'],Eq['carry']),x,y))
   spots.sort(reverse=True);chosen=[]
   for val,x,y in spots:
    if all(math.hypot(x-cx,y-cy)>=5 for _,cx,cy in chosen):chosen.append((val,x,y))
    if len(chosen)>=n:break
   self._c4c2_spots_key=key;self._c4c2_spots=chosen
  free=list(mates)
  for val,x,y in self._c4c2_spots:
   if not free:break
   q=min(free,key=lambda q:math.hypot(q.x-x,q.y-y));free.remove(q);targets[q.id]=(x,y)
 def c4b_roster(self,L):
  """C4b (the Lead's C4a audit: balance and rotate the mixed roster before campaign comparisons). Mixed, mirrored design 1:
  ten starter profiles and ten reserve profiles of (strength, balance, tackling) level indices into L = 0.46, 0.60, 0.76, 0.90.
  Starters take each level of each attribute 3, 2, 2, 3 times, reserves 2, 3, 3, 2 times: every attribute averages exactly 0.68
  among the starters, among the reserves and over all twenty, and the full squad has five of each level. The profiles were chosen
  by a declared search (seed 20261008) for the smallest largest pairwise correlation between the three attributes: 0.022 among
  the starters, 0.029 among the reserves. Both teams get the same profiles in the same slots. The profiles are rotated through
  the slots by the match seed (slot j takes profile (j + seed) mod 10, separately for starters and reserves), so that no profile
  is tied to one formation position across a campaign."""
  S_=((0,2,0),(0,2,1),(0,0,2),(1,3,3),(1,0,2),(2,3,0),(2,1,3),(3,3,3),(3,1,0),(3,0,1))
  R_=((0,3,2),(0,1,2),(1,0,1),(1,1,0),(1,2,2),(2,1,1),(2,2,3),(2,2,0),(3,0,3),(3,3,1))
  for team in('A','B'):
   field=sorted([p for p in self.s.players.values()if p.team==team and p.role=='field'],key=lambda p:p.slot)
   starters=[p for p in field if p.active];reserves=[p for p in field if not p.active]
   for group,prof in((starters,S_),(reserves,R_)):
    for j,p in enumerate(group):
     v=tuple(L[i]for i in prof[(j+self.seed)%len(prof)]);p.a.strength,p.a.balance,p.a.tackling=v;p.a.validate();self.c4a_table[p.id]=list(v)
 def move_players(self,ms,targets):
  if self.c3:return self.c3_move(ms,targets) #C3a: motion and contact are integrated together; the fixed 5 and 9 m/s approach ceilings below are legacy only
  s=self.s;dt=ms/1000;active=self.active_field();old={p.id:(p.x,p.y,p.z)for p in active}
  for p in s.players.values():
   if not p.active:
    p.fatigue=min(1,p.fatigue+dt*.006*p.a.endurance);continue
   if p.role=='archer':continue
   if p.posture=='grounded'and s.now>=p.next_action and not p.frozen(s.now):p.posture='upright'
   if not p.eligible(s.now)or p.posture=='grounded':
    speed=p.speed
    if speed>0:
     new=max(0,speed-p.a.braking*dt);p.vx*=new/speed;p.vy*=new/speed
    p.x+=p.vx*dt;p.y+=p.vy*dt
    if p.posture=='airborne':
     p.z+=p.vz*dt-.5*self.assume['gravity']*dt*dt;p.vz-=self.assume['gravity']*dt
     if p.z<=0:p.z=0;p.vz=0;p.posture='upright'
    if p.frozen(s.now):self.stats['frozen_player_ms']+=ms
    continue
   if s.phase==Phase.PENALTY and p.id not in(s.penalty['runner'],s.penalty['keeper']):continue
   if s.phase==Phase.FLIGHT and not self.e.eligible(p):continue
   if s.phase==Phase.OPENING and not s.opening_touched and p.id not in s.opening_contestants:continue
   if p.id in targets and s.now>=p.next_decision:
    p.target=targets[p.id];p.next_decision=s.now+int(1000*p.a.decision_speed*(1.3-.4*p.a.awareness))
   dx,dy=p.target[0]-p.x,p.target[1]-p.y;d=norm(dx,dy);ux,uy=unit(dx,dy)
   policy=self.pol[p.team].t
   carrier=s.ball.carrier==p.id
   maxspeed=p.a.maximum_speed*(.70+.30*p.fatigue)*(policy.pace if carrier else.88)
   if carrier:maxspeed*=.90
   speed=min(maxspeed,math.sqrt(max(0,2*p.a.braking*d)))
   if d<.08:speed=0
   desiredx,desiredy=ux*speed,uy*speed
   if self.e.live()or s.phase==Phase.PENALTY:
    for q in active:
     if q.team==p.team or not q.eligible(s.now):continue
     qdx,qdy=q.x-p.x,q.y-p.y;dist=norm(qdx,qdy)
     if dist>.8+max(8,p.speed*p.speed/(2*p.a.braking)+4):continue
     ex,ey=unit(qdx,qdy);closing=(desiredx-q.vx)*ex+(desiredy-q.vy)*ey
     #Safe approach planning has finite braking; it is not an immunity granted by the engine.
     if closing>5 and dist<max(7,p.speed*p.speed/(2*p.a.braking)+4):
      desiredx-=ex*(closing-5);desiredy-=ey*(closing-5)
     contact_brake_distance=max(4,(p.speed*p.speed-81)/(2*p.a.braking)+p.speed*.25+2)
     if dist<contact_brake_distance:
      mag=norm(desiredx,desiredy)
      if mag>9:desiredx*=9/mag;desiredy*=9/mag
   #Finite longitudinal and lateral acceleration.
   dvx,dvy=desiredx-p.vx,desiredy-p.vy;dv=norm(dvx,dvy)
   accelerating=norm(desiredx,desiredy)>p.speed
   accel=(p.a.acceleration*(.55+.45*p.fatigue))if accelerating else p.a.braking
   if p.speed>1:
    along=(dvx*p.vx+dvy*p.vy)/p.speed;nx,ny=-p.vy/p.speed,p.vx/p.speed
    side=clamp(dvx*nx+dvy*ny,-p.a.turning*dt,p.a.turning*dt)
    along=clamp(along,-p.a.braking*dt,accel*dt)
    oldvx,oldvy,oldspeed=p.vx,p.vy,p.speed
    p.vx=oldvx+along*oldvx/oldspeed+side*nx;p.vy=oldvy+along*oldvy/oldspeed+side*ny
   elif dv>0:
    scale=min(1,accel*dt/dv);p.vx+=dvx*scale;p.vy+=dvy*scale
   p.velocity_samples=getattr(p,'velocity_samples',[])+[(s.now,p.vx,p.vy)]
   p.velocity_samples=[v for v in p.velocity_samples if v[0]>=s.now-100]
   p.contact_velocity=(sum(v[1]for v in p.velocity_samples)/len(p.velocity_samples),sum(v[2]for v in p.velocity_samples)/len(p.velocity_samples))
   p.x+=p.vx*dt;p.y+=p.vy*dt
   #Nonparticipating retreat remains possible; gross runaway paths produce a safety stop.
   p.x=clamp(p.x,-28,128);p.y=clamp(p.y,-38,138)
   if p.speed>.3:p.facing=unit(p.vx,p.vy)
   if p.posture=='airborne':
    p.z+=p.vz*dt-.5*self.assume['gravity']*dt*dt;p.vz-=self.assume['gravity']*dt
    if p.z<=0:p.z=0;p.vz=0;p.posture='upright'
   intensity=(p.speed/max(1,p.a.maximum_speed))**2
   if self.e.live()or s.phase==Phase.PENALTY:
    cost=(.00015+.006*intensity)*(1.25-p.a.endurance*.6)*self.assume['fatigue_rate']
    p.fatigue=clamp(p.fatigue-dt*cost,.15,1)
   elif p.speed<2:p.fatigue=min(1,p.fatigue+dt*.002*p.a.endurance)
   self.stats['player_distance_mm']+=int(norm(p.x-old[p.id][0],p.y-old[p.id][1])*1000)
  return old
 def update_archers(self,ms):
  s=self.s;dt=ms/1000
  for p in s.players.values():
   if not p.active or p.role!='archer' or not p.eligible(s.now):continue
   low=s.ends[p.team]==0;minx,maxx=(.7,49.3)if low else(50.7,99.3)
   tx=clamp(s.ball.x,minx,maxx);ty=-5.1 if low else 105.1
   dx,dy=tx-p.x,ty-p.y;d=norm(dx,dy);ux,uy=unit(dx,dy);desired=min(8,p.a.maximum_speed*.4,math.sqrt(2*p.a.braking*d))
   ax,ay=ux*desired-p.vx,uy*desired-p.vy;change=norm(ax,ay);limit=(p.a.acceleration if desired>p.speed else p.a.braking)*dt
   if change:p.vx+=ax*min(1,limit/change);p.vy+=ay*min(1,limit/change)
   p.x=clamp(p.x+p.vx*dt,minx,maxx);p.y=clamp(p.y+p.vy*dt,-9.3,-3.1)if low else clamp(p.y+p.vy*dt,103.1,109.3)
   q=s.quivers[p.team]
   if q.loaded==0 and q.spent<q.allocation and q.reload_until<0:self.e.reload(p.id)
 def ball_velocity(self,origin,target,skill,kind,factor=1.):
  speed=self.cfg['pocket']['pass_speed' if kind=='pass' else 'ball_speed'] if self.cfg.get('pocket') else (30+8*skill)if kind=='shot'else(19+12*skill)if kind=='pass'else(29+10*skill)
  speed*=factor #C3a: launch speed available under restraint (1 when unrestrained)
  noise=(1-skill)*self.assume['catch_noise']*(1.5 if kind=='shot'else 2)
  target=(target[0]+self.rng['ball'].gauss(0,noise),target[1]+self.rng['ball'].gauss(0,noise),max(.2,target[2]+self.rng['ball'].gauss(0,noise*.5)))
  ans=ballistic(origin,target,speed if self.cfg.get("pocket") else min(39.5,speed),self.assume['gravity'])
  if ans is None:
   ux,uy=unit(target[0]-origin[0],target[1]-origin[1]);return (ux*speed/math.sqrt(2),uy*speed/math.sqrt(2),speed/math.sqrt(2)) if self.cfg.get("pocket") else (ux*25,uy*25,12)
  return ans[0]
 def plan_pass(self,origin,passer,q,kind,lag=0.,speed=None):
  """C1: aim point and launch that meet receiver q, using the real release speed, flight time, gravity and drag.
  Returns (velocity, aim_xy, flight_s) or None when q cannot be reached at that speed.
  lag: in open play the players have already been moved to the end of the current step when the ball is released
  at its start, so the receiver has (flight time - lag) left to run, not the whole flight time."""
  if speed is None:speed=self.cfg['pocket']['pass_speed' if kind=='pass' else 'ball_speed']
  g=self.assume['gravity'];k=self.assume['ball_drag'];T=norm(q.x-origin[0],q.y-origin[1])/max(1e-6,speed);sol=None
  for _ in range(5):
   run=max(0.,T-lag);aim=(clamp(q.x+q.vx*run,1,99),clamp(q.y+q.vy*run,1,99),q.hand_height)
   sol=launch_for(origin,aim,speed,g,k)
   if sol is None:return None
   T=sol[1]
  return sol[0],(aim[0],aim[1]),T
 def c3_perturb(self,vel,extra_deg):
  """C3a: launch error added by restraint, sampled at release. Anisotropic: the full angle sideways, half of it in elevation."""
  if extra_deg<=0:return vel
  e=math.radians(extra_deg);speed=math.sqrt(sum(v*v for v in vel));az=math.atan2(vel[1],vel[0])+self.rng['ball'].gauss(0,e)
  el=math.asin(clamp(vel[2]/speed,-1,1))+self.rng['ball'].gauss(0,e/2)
  return(speed*math.cos(el)*math.cos(az),speed*math.cos(el)*math.sin(az),speed*math.sin(el))
 def c3_release_state(self,p,kind):
  #Restraint as it is at the instant of release: a hold that has already been escaped restrains nothing.
  rho=self.c3_rho(p,kind)if self.c3 else 0.
  if rho<=0:return 0.,1.,0.
  return rho,1-self.assume['restraint_speed_loss']*rho,self.assume['restraint_error_deg']*rho
 def aim_error(self,vel,skill):
  """C1: launch-direction error. One-sigma angle = pass_aim_error_deg x (1 - skill); speed is unchanged."""
  sigma=math.radians(self.assume['pass_aim_error_deg'])*(1-skill)
  speed=math.sqrt(sum(v*v for v in vel));az=math.atan2(vel[1],vel[0])+self.rng['ball'].gauss(0,sigma)
  el=math.asin(clamp(vel[2]/speed,-1,1))+self.rng['ball'].gauss(0,sigma)
  return(speed*math.cos(el)*math.cos(az),speed*math.cos(el)*math.sin(az),speed*math.sin(el))
 def make_pass(self,p,recipient,kind='pass',execute=False):
  if not execute:
   if self.c3c and self.c3_withhold(p,kind):return #C3c controller: with his arms pinned he does not begin a wind-up he could not finish
   self.pass_signal=(recipient.id,self.s.now)
   grip=max((e.progress for e in self.s.engagements.values()if e.kind=='tackle'and e.target==p.id),default=0)
   delay=self.assume['pass_release_ms']*(1.35-.5*p.a.ball_handling)+(0 if self.c3 else self.assume['grip_delay_ms']*grip) #C3a: a hold slows preparation while it lasts, instead of a fixed delay set at the start
   self.c3_prep[p.id]=self.s.now
   if self.c3:
    #C3a2: the preparation takes its actual time. It is no longer rounded up to a whole 100 ms step; the kernel integrates what is left of it.
    rnd=self.assume['c3_prep_round_ms']
    if rnd:delay=math.ceil(delay/rnd)*rnd #comparison setting only: the inherited rounding of the preparation up to a whole step
    self.c3_due[p.id]=self.s.now+delay;self.pending_ball_actions[p.id]=(self.s.now+int(math.ceil(delay)),kind,recipient.id);self.c3_dur[p.id]=delay;self.c3_stall[p.id]=0.
    self.e.emit('ball_action_prepared','assumption:release_execution',player=p.id,kind=kind,ready=self.s.now+int(math.ceil(delay)));return
   self.pending_ball_actions[p.id]=(self.s.now+int(math.ceil(delay/self.dt)*self.dt),kind,recipient.id)
   self.e.emit('ball_action_prepared','assumption:release_execution',player=p.id,kind=kind,ready=self.s.now+int(delay));return
  s=self.s;b=s.ball
  if self.assume['c1_pass_planning']:
   #Re-plan at release with the receiver's actual state. An unreachable receiver is replaced by the next option.
   skill=p.a.passing if kind=='pass'else p.a.kicking;plan=None;self.e.follow_carrier() #plan from the point the ball will actually leave from
   rho,factor,extra=self.c3_release_state(p,kind);base=self.cfg['pocket']['pass_speed' if kind=='pass' else 'ball_speed']
   for q in [recipient]+[m for m in self.pol[p.team].pass_ranked(s,p)if m.id!=recipient.id]:
    if not self.e.eligible(q):continue
    plan=self.plan_pass((b.x,b.y,b.z),p,q,kind,0. if self.c3 else self.step_ms/1000,base*factor if rho>0 else None)
    if plan:recipient=q;break
   if plan is None:
    self.e.emit('pass_plan_failed','assumption:pass_planning',player=p.id,kind=kind);p.next_action=s.now+100;return
   vel=self.c3_perturb(self.aim_error(plan[0],skill),extra)
   if rho>0:self.stats['c3_restrained_releases']+=1;self.e.emit('c3_restraint','C3-6.8',player=p.id,kind=kind,restraint=round(rho,4),speed_available_mps=round(base*factor,3),speed_unrestrained_mps=base,added_error_deg=round(extra,3))
   self.e.emit('pass_plan','assumption:pass_planning',player=p.id,target=recipient.id,kind=kind,aim=[round(plan[1][0],3),round(plan[1][1],3)],flight_s=round(plan[2],4),distance_m=round(norm(plan[1][0]-b.x,plan[1][1]-b.y),3))
  else:
   d=norm(recipient.x-p.x,recipient.y-p.y);tt=d/27
   target=(clamp(recipient.x+recipient.vx*tt*.75,1,99),clamp(recipient.y+recipient.vy*tt*.75,1,99),recipient.hand_height)
   vel=self.ball_velocity((b.x,b.y,b.z),target,p.a.passing if kind=='pass'else p.a.kicking,kind)
  if self.e.release(p.id,vel,kind,recipient.id):
   self.stats[kind+'_attempts']+=1;p.next_action=s.now+400
   if getattr(p,'arrow_reaction_pending',False):
    self.stats['arrow_evoked_pass']+=1;self.e.emit('arrow_response','assumption:observed_arrow_policy',player=p.id,response='completed_pass')
   p.arrow_reaction_pending=False
 def make_shot(self,p,execute=False):
  pc=self.cfg.get('pocket',{})
  if pc.get('zone_only') and self.s.phase!=Phase.PENALTY and self.e.zone(p.x,p.y)!=self.s.own_zone(self.s.other(p.team)):return
  if not execute:
   if self.c3c and self.c3_withhold(p,'shot'):return #C3c: as for a pass
   delay=int(math.ceil(self.assume['pass_release_ms']*(1.6-.5*p.a.kicking)/self.dt)*self.dt)
   if self.c3:
    exact=self.assume['pass_release_ms']*(1.6-.5*p.a.kicking);rnd=self.assume['c3_prep_round_ms'] #C3a2: actual time, not rounded up to a whole step (unless the comparison setting asks for it)
    if rnd:exact=math.ceil(exact/rnd)*rnd
    delay=int(math.ceil(exact));self.c3_due[p.id]=self.s.now+exact;self.c3_dur[p.id]=exact;self.c3_stall[p.id]=0.
   self.pending_ball_actions[p.id]=(self.s.now+delay,'shot',None);self.c3_prep[p.id]=self.s.now
   self.e.emit('ball_action_prepared','assumption:release_execution',player=p.id,kind='shot',ready=self.s.now+delay);return
  s=self.s;b=s.ball;gx=s.attack_goal(p.team);skill=(p.a.kicking+p.a.ball_handling)/2
  keeper=next((q for q in s.players.values()if q.team!=p.team and q.active and q.role=='keeper'),None)
  side=-1 if keeper and keeper.y>50 else 1
  target=(gx+s.attack_sign(p.team)*.3,50+side*(3.5+.6*skill),2.8+.3*skill)
  rho,factor,extra=self.c3_release_state(p,'shot') #C3a: the same restraint rule as any hand release; no separate shot penalty
  vel=self.c3_perturb(self.ball_velocity((b.x,b.y,b.z),target,skill,'shot',factor),extra)
  if rho>0:self.stats['c3_restrained_releases']+=1;self.e.emit('c3_restraint','C3-6.8',player=p.id,kind='shot',restraint=round(rho,4),speed_available_mps=round(self.cfg['pocket']['ball_speed']*factor,3),speed_unrestrained_mps=self.cfg['pocket']['ball_speed'],added_error_deg=round(extra,3))
  if self.e.release(p.id,vel,'shot'):self.stats['shot_attempts']+=1;p.next_action=s.now+500
 def carrier_decision(self):
  s=self.s;b=s.ball
  for pid in list(self.pending_ball_actions):
   if pid!=b.carrier:s.players[pid].arrow_reaction_pending=False
  self.pending_ball_actions={pid:a for pid,a in self.pending_ball_actions.items()if pid==b.carrier}
  if self.c3 and b.carrier in self.pending_ball_actions and self.c3_prep.get(b.carrier,-1)<b.control_time:
   self.pending_ball_actions.pop(b.carrier) #C3a: preparation begun before a loss of control is not completed after a fresh pickup
  if not b.carrier:return
  p=s.players[b.carrier]
  if not self.e.eligible(p)or s.now<p.next_action:return
  if p.id in self.pending_ball_actions:
   due,kind,target=self.pending_ball_actions[p.id]
   if s.now>=due:
    self.pending_ball_actions.pop(p.id)
    if kind=='shot':self.make_shot(p,True)
    elif target in s.players and self.e.eligible(s.players[target]):self.make_pass(p,s.players[target],kind,True)
   return
  if s.phase==Phase.PENALTY:
   keeper=s.players[s.penalty['keeper']];distance_goal=abs(s.attack_goal(p.team)-p.x)
   if distance_goal<13 and(norm(keeper.x-p.x,keeper.y-p.y)<5 or s.now>s.penalty['until']-2200):self.make_shot(p)
   return
  if s.phase!=Phase.LIVE:return
  t=self.pol[p.team].t;opp=[q for q in s.players.values()if q.team!=p.team and q.eligible(s.now)and q.role!='archer']
  pressure=min((norm(q.x-p.x,q.y-p.y)for q in opp),default=30);dg=abs(s.attack_goal(p.team)-p.x);clock=s.possession_ms/1000
  danger_arrow=False
  for ar in s.arrows:
   if ar.live and ar.team!=p.team and s.now-ar.release_time>int(p.a.decision_speed*1000):
    d,at=segment_distance(p.x,p.y,ar.x,ar.y,ar.x+ar.vx,ar.y+ar.vy)
    if d<2 and norm(ar.x-p.x,ar.y-p.y)<24:danger_arrow=True
  if self.ctrl and p.role!='keeper'and not(s.reconstruction and s.reconstruction['team']==p.team):return self.c4c2_decide(p,clock,danger_arrow)
  if p.role=='keeper'and(self.e.zone(p.x,p.y)==s.own_zone(p.team)):
   q=self.pol[p.team].pass_choice(s,p)
   if q and p.keeper_hold_ms>400:self.make_pass(p,q,'kick'if dg>70 else'pass')
   return
  pc=self.cfg.get('pocket',{})
  shot_distance=t.shoot_distance
  if pc.get('release_territories'):
   dg=norm(s.attack_goal(p.team)-p.x,50-p.y)
  if pc.get('adapt_scoring'):
   method=self.e.territory(p.team,p.x,p.y)
   value=self.e.territory_points(method)
   best=max(pc['inner_points'],pc['release_points'],pc['outside_points'] if not pc['zone_only'] else 0)
   shot_distance=clamp(t.shoot_distance*math.sqrt(value/best),4,60)
  uncleared=bool(s.reconstruction and s.reconstruction['team']==p.team) #C2: no goal can count until the zone is cleared, so the carrier does not shoot
  if (dg<shot_distance and(pressure<t.pass_pressure or clock<12))or clock<3:
   if dg<65 and not uncleared:self.make_shot(p);return
  patience=t.possession_patience
  grabbed=any(en.target==p.id and en.kind=='tackle'and en.progress>.65 for en in s.engagements.values())
  trigger=grabbed or pressure<(t.pass_pressure if t.escort<2 else .65) or danger_arrow or (t.width>35 and s.now-b.control_time>int(1400+2500*patience)) or clock<8
  if trigger and s.now-b.control_time>180:
   q=self.pol[p.team].pass_choice(s,p)
   if q and norm(q.x-p.x,q.y-p.y)>2.5:
    self.make_pass(p,q,'kick'if t.risk>.7 and norm(q.x-p.x,q.y-p.y)>25 else'pass')
    if danger_arrow:p.arrow_reaction_pending=True;self.stats['arrow_evoked_pass_preparations']+=1
 def arrow_decisions(self):
  if self.no_archery:return
  s=self.s
  if not self.e.live()or s.owner is None:self.pending_draw.clear();return
  for team in('A','B'):
   p=next((p for p in s.players.values()if p.team==team and p.active and p.role=='archer'),None)
   if not p or not p.eligible(s.now):continue
   q=s.quivers[team];t=self.pol[team].t
   interval=t.arrow_interval
   if s.period>=4 and s.score[team]<s.score[s.other(team)] and s.game_ms<120000:interval=max(2,interval*.5)
   if s.now-self.last_arrow_decision[team]<interval*1000 or q.loaded==0 or q.spent>=q.allocation:return
   if q.allocation-q.spent<=t.reserve and s.game_ms>120000:return
   carrier=s.players.get(s.ball.carrier)
   if not carrier or carrier.team==team or not self.e.eligible(carrier)or s.now<=carrier.immune_until:return
   if carrier.role=='keeper'and self.e.zone(carrier.x,carrier.y)==s.own_zone(carrier.team):return
   if self.cfg.get('ruleset','1.0.1')=='1.0.2' and self.cfg.get('archer_target_policy','structure')=='structure':
    origin=(p.x,p.y,.72*p.a.height)
    options=[c for c in self.active_field()if c.team!=team and self.e.eligible(c) and s.now>c.immune_until and norm(c.x-carrier.x,c.y-carrier.y)<=9 and not(c.role=='keeper'and self.e.zone(c.x,c.y)==s.own_zone(c.team)) and 10<=math.dist(origin,(c.x,c.y,.55*c.a.height))<=70]
    defenders=[d for d in self.active_field()if d.team==team and self.e.eligible(d)]
    def target_value(c):
     near=min((norm(d.x-c.x,d.y-c.y)for d in defenders),default=30)
     engaged=any(c.id in(k[0],k[1])for k in s.engagements)
     importance=2.2 if c.id==s.ball.carrier else 1.1+1.2*engaged+.8*max(0,1-near/8)
     return importance/(1+.11*c.speed+.006*math.dist(origin,(c.x,c.y,.55*c.a.height)))
    if options:carrier=max(options,key=target_value)
    if team in self.pending_draw:
     pending=s.players[self.pending_draw[team][1]]
     if self.e.eligible(pending) and s.now>pending.immune_until:carrier=pending
   if team not in self.pending_draw:
    self.pending_draw[team]=(s.now+int(math.ceil(self.assume['bow_draw_ms']*(1.4-.5*p.a.archery_accuracy)/self.dt)*self.dt),carrier.id)
    self.e.emit('arrow_draw','assumption:draw_time',player=p.id,target=carrier.id,ready=self.pending_draw[team][0]);continue
   due,target_id=self.pending_draw[team]
   if target_id!=carrier.id:self.pending_draw.pop(team);continue
   if s.now<due:continue
   self.pending_draw.pop(team)
   origin=(p.x,p.y,.72*p.a.height);base=(carrier.x,carrier.y,carrier.z+.55*carrier.a.height)
   d=math.dist(origin,base)
   if not 10<=d<=70:return
   speed=min(self.cfg.get("pocket",{}).get("arrow_limit",30),p.a.archery_release_speed);target=base;ans=None
   #Two lead iterations, never knowledge of future policy turns.
   for _ in range(3):
    ans=ballistic(origin,target,speed,self.assume['gravity'],False)
    if ans is None:break
    tt=ans[1];drag=self.assume['arrow_drag'];loss=.5*drag*tt
    target=(carrier.x+carrier.vx*tt+(carrier.x-origin[0])*loss,carrier.y+carrier.vy*tt+(carrier.y-origin[1])*loss,carrier.z+.55*carrier.a.height+drag*tt*tt*.6)
   if ans is None:return
   alternatives=[]
   for high in(False,True):
    sol=ballistic(origin,target,speed,self.assume['gravity'],high)
    if not sol:continue
    vel,flight=sol
    obstacles=0;unsafe=False
    for block in self.active_field():
     if block.id==carrier.id:continue
     dist,tseg=segment_distance(block.x,block.y,origin[0],origin[1],target[0],target[1])
     z=origin[2]+vel[2]*flight*tseg-.5*self.assume['gravity']*(flight*tseg)**2
     if dist<block.radius+.12 and block.z<=z<=block.z+block.a.height:
      obstacles+=1
      if block.team==team or block.frozen(s.now)or s.now<=block.immune_until or(block.role=='keeper'and self.e.zone(block.x,block.y)==s.own_zone(block.team)):unsafe=True
    if unsafe:continue
    alternatives.append((obstacles+flight*.02,vel,flight,obstacles,high))
   if not alternatives:continue
   _,vel,flight,obstacles,high=min(alternatives,key=lambda a:a[0])
   if obstacles>1 and t.risk<.7:continue
   sigma=(.0008+.009*(1-p.a.archery_accuracy))*self.assume['arrow_error_scale']
   yaw=self.rng['arrow'].gauss(0,sigma);pitch=self.rng['arrow'].gauss(0,sigma)
   vx,vy,vz=vel;vxy=norm(vx,vy);az=math.atan2(vy,vx)+yaw;el=math.atan2(vz,vxy)+pitch
   noisy=(speed*math.cos(el)*math.cos(az),speed*math.cos(el)*math.sin(az),speed*math.sin(el))
   ar=self.e.shoot_arrow(p.id,carrier.id,noisy,origin)
   self.last_arrow_decision[team]=s.now
   if ar:self.e.emit('arrow_plan','assumption:ballistic_policy',arrow=ar.id,flight_estimate=flight,obstacles=obstacles,high_arc=high,accuracy=p.a.archery_accuracy)
 # ======================= C3 contact kernel: C3a revision 3, with the C3b additions (each marked C3b and behind self.c3b) =======================
 # Three processes: body collision, grip with momentum coupling, and balance. Units: m, s, kg, N.
 # Balance load B is dimensionless: 0 settled, grounded at 1. Grip g is the fraction of grip capacity in use.
 # Every coefficient is a declared hypothesis in CALIBRATION; none is fitted to match totals.
 #
 # Order of events (revision 2). Inside an interval the athletes near an opponent are advanced in contact substeps. Each
 # substep is a DRIFT (straight-line motion at the current velocities) followed by a KICK (the forces that acted during that
 # drift). A drift never runs past the first instant at which something changes: two bodies meet, a defender's reach of the
 # carrier begins or ends, or a pass or shot in preparation completes. Those instants are solved on the relative trajectory,
 # not sampled at the ends of the substep. So during any one drift every pair is either wholly within reach or wholly out,
 # and a collision is resolved at the instant of contact. The first event that the rules engine must commit (a grounding,
 # a strip, a foul, a completed preparation) ends the interval at the next whole millisecond: nothing is integrated beyond it.
 # c3_step then commits it, reconciles holds and actions, and the following interval is computed from the committed state.
 def c3_init(self):
  self.c3_armed={};self.c3_holds={};self.c3_events=[];self.c3_down=set();self.c3_prep={};self.c3_due={};self.c3_blocks=[];self.c3_lost=False
  self.c3_integrating=False;self.c3_adv=0;self.c3_t=0.;self.c3_cache={};self.c3_pre={};self.c3_ok={};self.c3_ok_t=None;self.c3_ch={}
  self.c3_fix_drive=None;self.c3_fix_region=None;self.c3_no_strip=False;self.c3_reckless=set();self.c3_descent={};self.c3_fix_contain=None;self.c3_fix_descent=None;self.c3_stall={};self.c3_dur={};self.c3_told={};self.c3_fix_escape=None;self.c3_fix_withhold=None;self.c3_off={} #c3_off (C3c2): (holder, carrier) -> the time his hold was pried off or fended off. Then: drill and test hooks: fixed holder braking (negative = passive), fixed hold region, strip chance off, athletes whose controller does not avoid collisions
 def c3_at(self,t):
  #Kernel time t (seconds into the interval) as an offset on the match clock: the whole millisecond at or after it.
  return max(0,int(math.ceil(t*1000-1e-6)))
 def c3_note(self,t,event,rule='C3',**data):
  #A log record with its own time. During integration it is queued and written when the clock reaches that time; otherwise it is written now.
  if self.c3_integrating:self.c3_events.append(Event('note',None,None,{'event':event,'rule':rule,'data':data},at=self.c3_at(t)))
  else:self.e.emit(event,rule,**data)
 def c3_bal(self,p):
  src=getattr(p,'bal_src',None)
  if src is None:p.bal_src={};p.bal_t0=None;return 0.
  return sum(src.values())
 def c3_add(self,p,key,amount,lawful,now_ms):
  """Balance load is kept as separate contributions: (kind, other athlete, lawful or not) -> amount. A new contribution is added
  to its own entry; it never changes the lawfulness of load that is already there, and each entry decays on its own."""
  self.c3_bal(p)
  if amount<=0:return
  if not p.bal_src:p.bal_t0=now_ms
  k=(key[0],key[1],bool(lawful));p.bal_src[k]=p.bal_src.get(k,0.)+amount
 def c3_rho(self,p,kind):
  """Restraint on an action in preparation, 0..1: grip weighted by hold region and action. An upper hold bears on hand
  releases (pass, shot); a lower hold bears on kicks."""
  A=self.assume;rho=0.
  for h in self.c3_holds.values():
   if h['target']==p.id and h['g']>0:
    w=(A['restraint_weight_matched']if(h['region']=='lower')==(kind=='kick')else A['restraint_weight_other'])
    #C3c (decided by DreLen: a high wrap pins the arms to varying degrees): an upper hold restrains a hand release by
    #grip / arm_pin_grip, complete at arm_pin_grip. A lower hold, and a kick, keep the C3a weights whatever the grip.
    rho=max(rho,min(1.,h['g']/A['arm_pin_grip'])if self.c3c and h['region']=='upper'and kind!='kick'else w*h['g'])
  return min(1.,rho)
 def c3_region(self,d,c,now_ms):
  #Chosen before contact from what this defender can observe: a hand release in preparation for at least his own reaction time.
  #The region sets the height at which the hold acts, its weight on each kind of release and its effect on the legs. It does NOT
  #change who is within reach: reach is the engine's planar engagement distance for both regions (a declared limit, not anatomy).
  prep=self.c3_prep.get(c.id);pending=self.pending_ball_actions.get(c.id)
  seen=bool(pending and prep is not None and pending[1]!='kick'and now_ms-prep>=1000*d.a.decision_speed)
  pol=self.assume['c3_region_policy']
  if self.c3c and pol==2 and not seen and self.e.zone(c.x,c.y)==self.s.own_zone(d.team):
   #C4a policy 2 (controller, named and declared): he also goes high when the carrier's pelvis is inside the Keeper Zone this
   #defender defends, where a release can score. Anywhere else he goes low unless a wind-up is seen.
   return(self.c3_fix_region or'upper'),'in_defended_zone'
  if self.c3c and pol==1 and not seen and self.c3_pass_open(c):
   #C3c placeholder controller: he also goes high against a carrier who has a pass open, judged from where the players stand
   #(nothing about what the carrier intends). The price of going high is that the carrier keeps his legs.
   return(self.c3_fix_region or'upper'),'pass_open'
  return(self.c3_fix_region or('upper'if seen else'lower')),seen
 def c3_end_hold(self,key,cause,end_ms,t=0.):
  #end_ms is the witnessed end of the hold on the match clock: the instant control, reach, lawfulness or eligibility actually ended.
  h=self.c3_holds.pop(key,None)
  if h is None:return
  self.stats['c3_holds_ended']+=1
  self.c3_note(t,'c3_hold_end',actor=h['actor'],target=h['target'],region=h['region'],cause=cause,start_ms=round(h['start'],3),end_ms=round(end_ms,3),
               duration_ms=round(end_ms-h['start'],3),reach_ms=round(h['reach_ms'],3),peak_grip=round(h['peak'],4),grip_at_end=round(h['g'],4),impulse_Ns=round(h['impulse'],1),
               **({'contained_ms':round(h.get('contain_ms',0.),1)}if self.c3b else{}),**({'escape_effort_ms':round(h.get('escape_ms',0.),3),'grip_broken':h.get('broken',0),
                  'wind_up_under_this_upper_hold_ms':round(h.get('pin_ms',0.),3),'peak_pin_in_wind_up':round(h.get('pin_peak',0.),4),'peak_strip_modifier':round(h.get('smod_peak',1.),4)}if self.c3c else{}),
               **({'escape_share_ms':round(h.get('share_ms',0.),3)}if self.c3c and self.assume['escape_allocation']else{})) #C4a: effort-weighted time he worked on this hold
 def c3_reconcile(self,*unused):
  """Wrap entitlement ends with control. Called whenever the committed state may have changed: after every committed event batch,
  after a decision, and at the start of an interval. A hold whose target no longer controls the ball, whose play has stopped, or
  either of whose athletes is no longer eligible and upright ends here, at the current time. Grip, coupling and drive stop.
  Momentum already acquired is untouched."""
  for pid in list(self.c3_descent):
   #C3b: a descent attempt ends with control of the ball, at the committed event that took it
   if self.s.ball.carrier!=pid:self.c3_descent_end(pid,'control_lost',self.s.now+(self.c3_t*1000 if self.c3_integrating else 0),self.c3_t)
  if self.c3_off:self.c3_off={k:v for k,v in self.c3_off.items()if self.s.ball.carrier==k[1]} #C3c2: the record of a hold thrown off ends with that carrier's control of the ball
  if not self.c3_holds:return
  s=self.s;contact=s.phase in(Phase.LIVE,Phase.PENALTY);now=s.now+(self.c3_t*1000 if self.c3_integrating else 0)
  for key in list(self.c3_holds):
   h=self.c3_holds[key];d=s.players[h['actor']];c=s.players[h['target']];cause=None
   if s.ball.carrier!=h['target']:cause='control_lost'
   elif not contact:cause='stoppage'
   elif not(self.e.eligible(d)and self.e.eligible(c))or d.posture!='upright'or c.posture=='grounded':cause='ineligible' #frozen, excluded, off the field, or down
   if cause:self.c3_end_hold(key,cause,now,self.c3_t)
 def c3_sync(self):
  """The engine's engagement table mirrors the kernel after an interval is final: one tackle engagement per hold, carrying its grip,
  and one block engagement per lawful initiated body contact while the two stay close. The kernel itself never reads this table."""
  s=self.s
  for k in [k for k in s.engagements if k[2]=='tackle'and(k[0],k[1])not in self.c3_holds]:del s.engagements[k]
  for(d,c),h in self.c3_holds.items():
   en=s.engagements.get((d,c,'tackle'))
   if en is None:en=s.engagements[(d,c,'tackle')]=Engagement(d,c,'tackle',int(h['start']))
   en.progress=h['g'];en.contain=h.get('mode')=='contain'
  for a,b,at in self.c3_blocks:
   if(a,b,'block')not in s.engagements:s.engagements[(a,b,'block')]=Engagement(a,b,'block',at)
  self.c3_blocks=[]
  s.engagements={k:en for k,en in s.engagements.items()if s.players[k[0]].eligible(s.now)and s.players[k[1]].eligible(s.now)and norm(s.players[k[0]].x-s.players[k[1]].x,s.players[k[0]].y-s.players[k[1]].y)<4}
 def c3_save(self):
  #Everything an interval can change before its events are committed, so that the interval can be recomputed up to an earlier event.
  s=self.s
  return{'players':[(p,{**p.__dict__,'bal_src':dict(p.__dict__.get('bal_src')or{})})for p in s.players.values()],'ball':dict(s.ball.__dict__),'arrows':(list(s.arrows),[dict(a.__dict__)for a in s.arrows]),
         'rng':{k:self.rng[k].getstate()for k in('contact','ball')},'log':(len(self.e.log),self.e.event_seq),'stats':dict(self.stats),
         'holds':{k:dict(v)for k,v in self.c3_holds.items()},'descent':{k:dict(v)for k,v in self.c3_descent.items()},
         'm':{k:copy.copy(getattr(self,k))for k in('c3_armed','c3_events','c3_down','c3_lost','c3_prep','c3_due','c3_blocks','c3_ok','c3_ok_t','c3_ch','c3_stall','c3_dur','c3_told','c3_off','pending_ball_actions','hands_set','seen_version','seen_from','bounce_mark')}}
 def c3_restore(self,z):
  s=self.s
  for p,d in z['players']:
   p.__dict__.clear();p.__dict__.update(d);p.bal_src=dict(d['bal_src'])
  s.ball.__dict__.clear();s.ball.__dict__.update(z['ball']);s.arrows[:]=z['arrows'][0]
  for a,d in zip(*z['arrows']):a.__dict__.clear();a.__dict__.update(d)
  for k,v in z['rng'].items():self.rng[k].setstate(v)
  del self.e.log[z['log'][0]:];self.e.event_seq=z['log'][1];self.stats.clear();self.stats.update(z['stats'])
  self.c3_holds={k:dict(v)for k,v in z['holds'].items()}
  for k,v in z['m'].items():setattr(self,k,copy.copy(v))
  self.c3_descent={k:dict(v)for k,v in z['descent'].items()}
 def c3_step(self,ms,targets,scripted=False):
  """One interval of the normal C3 match path; returns the milliseconds actually advanced (at least 1, at most ms).
  1. Decisions at the start, from the committed state (scripted: only an action already in preparation is completed).
  2. Motion and contact (c3_move) run until the first kernel event that the engine must commit, or to ms.
  3. The ball and the arrows are advanced over the same time. If any of their events (a catch, a deflection, an arrow impact,
     a boundary, a goal) falls earlier than the end of the interval, everything is put back and the interval is recomputed
     to end at that event. No force is therefore integrated past an event that has not yet been committed.
  4. The events are committed in time order; holds and engagements are reconciled with the committed state.
  The match clock is in whole milliseconds, so 'at an event' means within one millisecond of it."""
  s=self.s;start=s.now
  if not scripted:self.carrier_decision();self.arrow_decisions()
  elif s.ball.carrier in self.pending_ball_actions:self.carrier_decision()
  if self.c4c:
   self.c4c_keepers(targets)
   for due in self.c4c_due():
    if s.now<due<s.now+ms:ms=max(1,int(math.ceil(due-s.now-1e-9))) #C4c: a Keeper reacts, and lands, in the millisecond it falls due
  for due in self.pending_ball_actions.values():
   if s.now<due[0]<s.now+ms:ms=due[0]-s.now #an action in preparation completes on time whether or not the kernel is watching its carrier
  if self.c3b:
   for p in s.players.values():
    if p.active and p.posture=='grounded'and s.now<p.next_action<s.now+ms:ms=p.next_action-s.now #C3b: an athlete is upright in the millisecond his get-up ends
  self.c3_reconcile();save=self.c3_save();chunk=ms;redo=0
  while True:
   self.step_ms=chunk;old=self.move_players(chunk,targets);adv=self.c3_adv
   if not self.c4c:self.update_keepers_jump() #C4c: the Keeper's jumps and dives are planned (c4c_plan), not triggered by height
   bz,bvz=s.ball.z,s.ball.vz;events=self.advance_ball(adv,old)+self.advance_arrows(adv)
   for e in events:
    if e.kind=='ground'and e.data.get('ball_ground')and e.at is None:
     #the inherited flight code reports that the ball reached the ground in this interval but not when. Its height follows
     #z + vz t - g t^2 / 2 exactly, so the instant is solved here and the interval ends there like any other event.
     g=self.assume['gravity'];disc=bvz*bvz+2*g*(bz-s.ball.radius)
     if disc>=0:e.at=min(adv,max(0,int(1000*(bvz+math.sqrt(disc))/g)))
   first=min([adv]+[int(e.at)for e in events if e.at is not None])
   if first>=adv-1 or redo>=24:break
   self.c3_restore(save);chunk=first+1;redo+=1
  if redo:self.stats['c3_intervals_recomputed']+=1;self.stats['c3_recomputations']+=redo
  if first<adv-1:self.stats['c3_recompute_unconverged']+=1
  self.step_ms=adv;events+=self.player_contacts(adv,old);self.c3_sync();self.update_archers(adv);self.auto_substitutions()
  if self.c4b:self.c4b_gait(old,adv) #C4b: the feet follow the interval actually advanced, before its events (a release) are committed
  self.process_events(events,start,adv,old)
  if s.phase!=Phase.FINAL:self.c3_reconcile();self.c3_sync() #C4.0: nothing is reconciled after the result
  return adv
 def c3_desired(self,p,dt,live,carrier):
  """One athlete's own propulsion for a substep: velocity change only, with the ordinary acceleration, braking and turning limits.
  No speed ceiling near opponents. A defender with an established hold brakes; one still gaining it matches the carrier.
  An athlete may slow so that an incidental collision he can foresee would not put more than his tolerated load on his own
  balance. A defender does not avoid the ball carrier: stopping him is the job, and the collision is his choice."""
  s=self.s;A=self.assume;dx,dy=p.target[0]-p.x,p.target[1]-p.y;d=math.hypot(dx,dy)
  maxspeed,tol,near=self.c3_cache[p.id];brk=p.a.braking;vx,vy=p.vx,p.vy;sp=math.hypot(vx,vy)
  speed=min(maxspeed,math.sqrt(2*brk*d))if d>=.08 else 0.
  if d>0:desx,desy=dx/d*speed,dy/d*speed
  else:desx=desy=0.
  prop=1.;hold=None
  if self.c3_holds:
   is_carrier=carrier is not None and carrier.id==p.id
   for h in self.c3_holds.values():
    if h['actor']==p.id:hold=h
    elif is_carrier and h['target']==p.id and h['region']=='lower':prop=min(prop,1-A['lower_hold_leg_factor']*h['g'])
   if hold is not None and carrier is not None and hold['target']==carrier.id:
    if hold.get('mode')=='contain':
     #C3b containment: he stays with the carrier and holds him without driving him down. No braking force of his own.
     cs=math.hypot(carrier.vx,carrier.vy);f=min(1.,maxspeed/cs)if cs>0 else 0.;desx,desy=carrier.vx*f,carrier.vy*f
    elif hold['g']>=A['tackle_grip_threshold']and not(self.c3_fix_drive is not None and self.c3_fix_drive<0):
     #placeholder tackle drive: an established holder brakes, as hard as his grip will bear. 'drive' is the fraction of his full
     #braking he is using; he eases off (25 per second) while the hold is overloaded and builds up (10 per second) while it is not.
     hold['drive']=clamp(hold.get('drive',0.)+(10. if hold['excess']<.05 else-25.)*dt,0.,1.)if self.c3_fix_drive is None else max(0.,self.c3_fix_drive)
     f=max(0.,sp-hold['drive']*brk*dt)/sp if sp>0 else 0.;desx,desy=vx*f,vy*f
    elif self.c3_fix_drive is not None and self.c3_fix_drive<0:desx,desy=vx,vy #drill hook: a passive holder, no force of his own
    else:
     cs=math.hypot(carrier.vx,carrier.vy);f=min(1.,maxspeed/cs)if cs>0 else 0.;desx,desy=carrier.vx*f,carrier.vy*f #still gaining grip: stay with the carrier, so slip stays low
  if near and hold is None and p.id not in self.c3_reckless:
   dec=p.a.decision_speed;worst=0.;behind=A['c3_follow_distance']
   for sweep in range(3):
    #taking the approach off towards one opponent can turn the desired velocity towards another, so the list is gone through
    #again until nothing more is taken off (three times at most)
    again=False
    for q,own,rsum in near:
     qdx,qdy=q.x-p.x,q.y-p.y;dist=math.hypot(qdx,qdy)
     if dist<=0:continue
     ex,ey=qdx/dist,qdy/dist
     if behind and qdx*q.facing[0]+qdy*q.facing[1]>self.e.blind_cos*dist:
      #CONTROLLER: he does not run into an opponent from behind at any speed, because he can foresee that it would be a blindside
      #foul. He may close on the man ahead only as fast as still lets him stop half a metre short, even if that man brakes as hard
      #as he can: v x dt + v^2/(2 x braking) = gap - 0.5 + (man ahead's speed away)^2/(2 x his braking), where dt is the time until
      #this controller next acts (the distance covered before he can adjust again). No reaction allowance is added on top,
      #because the controller acts on the present state without delay; adding one would count the reaction twice.
      away=max(0.,q.vx*ex+q.vy*ey);bd=brk*dt;allow=math.sqrt(bd*bd+2*brk*max(0.,dist-rsum-.5+away*away/(2*q.a.braking)))-bd;cut=desx*ex+desy*ey-allow
      if sweep==0:
       over=vx*ex+vy*ey-allow
       if over>worst:worst=over;wx,wy=ex,ey
     else:
      closing=(desx-q.vx)*ex+(desy-q.vy)*ey;vmax=tol/own;cut=0.
      if closing>vmax and dist-rsum<(closing*closing-vmax*vmax)/(2*brk)+closing*dec+.5:
       cut=min(closing-vmax,desx*ex+desy*ey) #he takes off his own approach speed only; he is not driven backwards by an opponent's rush
     if cut>1e-9:desx-=ex*cut;desy-=ey*cut;again=True
    if not again:break
   if worst>0:
    #his present velocity already closes faster than that: he gives everything to taking the excess off
    desx,desy=vx-wx*worst,vy-wy*worst
  dvx,dvy=desx-vx,desy-vy
  if sp>1:
   accel=(p.a.acceleration*(.55+.45*p.fatigue)*prop)if desx*desx+desy*desy>sp*sp else brk
   along=(dvx*vx+dvy*vy)/sp;nx,ny=-vy/sp,vx/sp;turn=p.a.turning*dt
   side=dvx*nx+dvy*ny;side=turn if side>turn else-turn if side<-turn else side
   lo=-brk*dt;hi=accel*dt;along=hi if along>hi else lo if along<lo else along
   p.vx=vx+along*vx/sp+side*nx;p.vy=vy+along*vy/sp+side*ny
  else:
   dv=math.hypot(dvx,dvy)
   if dv>0:
    accel=(p.a.acceleration*(.55+.45*p.fatigue)*prop)if desx*desx+desy*desy>sp*sp else brk
    scale=min(1,accel*dt/dv);p.vx=vx+dvx*scale;p.vy=vy+dvy*scale
 def c3_move(self,ms,targets):
  """C3 replacement for move_players. Athletes near an opponent are integrated in contact substeps together with the kernel
  (c3_run); everyone else takes the interval at once. The interval may end early, at the first kernel event the engine must
  commit; the time actually advanced is left in self.c3_adv and everyone is advanced by exactly that time."""
  s=self.s;A=self.assume;dtw=ms/1000;active=self.active_field();old={p.id:(p.x,p.y,p.z)for p in active}
  live=self.e.live()or s.phase==Phase.PENALTY;contact=s.phase in(Phase.LIVE,Phase.PENALTY)
  #C3b: during a live first-tackle recovery bodies are solid too, so blocking and obstruction near it are physical and adjudicated
  award=self.c3b and s.phase==Phase.AWARD and s.recovery is not None;contact=contact or award
  if self.c3b:
   for p in s.players.values():
    if getattr(p,'c3_ext',None):self.c3_settle(p,s.now)
   for pid in list(self.c3_descent):
    if s.ball.carrier!=pid:self.c3_descent_end(pid,'control_lost',s.now,0.)
  self.c3_down=set();self.c3_lost=False;self.c3_events=[];self.c3_t=0.;self.c3_integrating=False;movers=[];idle=[]
  self.c3_reconcile()
  for p in s.players.values():
   if not p.active:
    idle.append(p);continue
   if p.role=='archer':continue
   if p.posture=='grounded'and s.now>=p.next_action and not p.frozen(s.now):
    p.posture='upright';p.bal_src={};p.bal_t0=None
    if self.c3b:self.e.emit('c3_upright','C3b-1',player=p.id,down_ms=s.now-getattr(p,'down_at',s.now),speed_mps=round(p.speed,3))
   if self.c4c and getattr(p,'c4c_launch',None)and p.posture=='airborne':mode='fly' #C4c: a launched Keeper cannot steer in the air
   elif not p.eligible(s.now)or p.posture=='grounded':mode='slide'
   elif(s.phase==Phase.PENALTY and p.id not in(s.penalty['runner'],s.penalty['keeper']))or(s.phase==Phase.FLIGHT and not self.e.eligible(p))or(s.phase==Phase.OPENING and not s.opening_touched and p.id not in s.opening_contestants):mode='skip'
   else:
    mode='drive'
    if p.id in targets and s.now>=p.next_decision:
     p.target=targets[p.id];p.next_decision=s.now+int(1000*p.a.decision_speed*(1.3-.4*p.a.awareness))
   movers.append((p,mode))
  #which opposing pairs can interact inside this interval
  carrier=s.players.get(s.ball.carrier)if contact else None;cid=carrier.id if carrier is not None else None
  seen=self.c3_ok_t;self.c3_ok_t=s.now;okd=self.c3_ok;chd=self.c3_ch;legal_=self.e.contact_legal;bscale=A['body_radius_scale']
  body=[p for p,mode in movers if mode=='drive'and self.e.eligible(p)and p.posture=='upright']if contact else[]
  pairs=[];near={};eps1=1+A['contact_restitution'];self.c3_cache=cache={}
  for p,mode in movers:
   if mode!='drive':continue
   policy=self.pol[p.team].t;top=p.a.maximum_speed*(.70+.30*p.fatigue)*((policy.pace*.90)if s.ball.carrier==p.id else.88)
   cache[p.id]=(top,A['collision_risk_tolerance']*A['shock_speed_mps']*(.5+p.a.balance),near.setdefault(p.id,[]))
  info=[(p,p.team,p.x,p.y,p.vx,p.vy,p.radius,p.a.reach,p.a.acceleration,p.a.braking,p.speed,p.a.mass)for p in body];hyp=math.hypot;owner=s.owner
  for i,(a,ta,ax,ay,avx,avy,ra,rea,aca,bra,spa,ma)in enumerate(info):
   for b,tb,bx,by,bvx,bvy,rb,reb,acb,brb,spb,mb in info[i+1:]:
    if ta==tb:continue
    dx,dy=bx-ax,by-ay;dist=hyp(dx,dy)
    if dist>60:continue
    closing=((avx-bvx)*dx+(avy-bvy)*dy)/dist if dist>0 else 0.
    if dist<ra+rb+.7*(rea+reb)+.4+(max(0.,closing)+(aca+acb)*dtw)*dtw:pairs.append((a,b))
    if live and dist<8+(spa+spb)**2/(2*min(bra,brb)):
     #incidental collisions are avoided on foreseen own balance load; a defender does not avoid the carrier
     if not(cid==b.id and ta!=owner):near[a.id].append((b,eps1*mb/(ma+mb),ra+rb))
     if not(cid==a.id and tb!=owner):near[b.id].append((a,eps1*ma/(ma+mb),ra+rb))
     #legal-change witness (revision 3). For each athlete, whether his contact on the other would be lawful NOW if they touched:
     #the retained classification with its distance test left out, because being out of reach is not a legal condition. While it
     #would be lawful, the time and the state of the approach are noted (the gap between the two bodies, the athlete's own speed
     #towards the other, the other's speed away from him). The first interval at which it no longer would be, having been lawful
     #at the interval before, is a witnessed change of legal circumstances (the man ahead turned his back, lost the ball, became
     #protected): its time, the new classification and the state of the approach then are kept until the contact would be lawful
     #again. An athlete who comes near an opponent already unlawful to hit has no such record. Used by c3_no_time.
     if dist>0:
      for p_,q_,sx,sy,ap,aw in((a,b,dx,dy,(avx*dx+avy*dy)/dist,(bvx*dx+bvy*dy)/dist),(b,a,-dx,-dy,-(bvx*dx+bvy*dy)/dist,-(avx*dx+avy*dy)/dist)):
       key=(p_.id,q_.id)
       #a non-carrier among the athletes paired here (eligible, upright, in live play) can only be unlawful to hit from behind
       if cid==q_.id:ok,why=legal_(p_,q_,'tackle',reach=False)
       elif award:ok,why=legal_(p_,q_,'block',reach=False) #C3b: in a recovery the protected disc is a legal condition too
       else:ok=sx*q_.facing[0]+sy*q_.facing[1]<=self.e.blind_cos*max(.1,dist);why='legal'if ok else'blindside'
       if ok:
        okd[key]=(s.now,max(0.,ap),dist-(ra+rb)*bscale,aw)
        if key in chd:del chd[key]
       elif key not in chd and seen is not None and key in okd and okd[key][0]==seen:
        #C3b: also how fast his approach was growing over the interval before the change (from the two samples), within his own
        #acceleration. He is taken to carry on like that for his reaction time.
        grow=clamp((max(0.,ap)-okd[key][1])*1000./(s.now-seen),0.,p_.a.acceleration)if self.c3b and s.now>seen else 0.
        chd[key]=(s.now,max(0.,ap),why,seen,dist-(ra+rb)*bscale,aw,grow)
  fine={p.id for ab in pairs for p in ab};adv=ms;paired={(a.id,b.id)for a,b in pairs}|{(b.id,a.id)for a,b in pairs}
  for key in list(self.c3_holds):
   if key not in paired:self.c3_end_hold(key,'out_of_reach',s.now,0.)
  if fine:
   scale=A['body_radius_scale'];pairs=[(a,b,(a.radius+b.radius)*scale)for a,b in pairs]
   self.c3_integrating=True;adv=self.c3_run(ms,pairs,[p for p,mode in movers if p.id in fine],carrier,live);self.c3_integrating=False;self.c3_t=0.
  dta=adv/1000
  #athletes away from every opponent: one update for the time actually advanced
  for p,mode in movers:
   if p.id in fine or mode=='skip':continue
   self.c3_free(p,mode,dta,live,carrier)
   if mode=='drive':self.c3_recover(p,dta)
  for p in idle:p.fatigue=min(1,p.fatigue+dta*.006*p.a.endurance)
  for p,mode in movers:
   if mode=='slide'and p.frozen(s.now):self.stats['frozen_player_ms']+=adv
   if mode!='drive':continue
   p.velocity_samples=getattr(p,'velocity_samples',[])+[(s.now,p.vx,p.vy)]
   p.velocity_samples=[v for v in p.velocity_samples if v[0]>=s.now-100]
   p.contact_velocity=(sum(v[1]for v in p.velocity_samples)/len(p.velocity_samples),sum(v[2]for v in p.velocity_samples)/len(p.velocity_samples))
   if p.speed>.3:p.facing=unit(p.vx,p.vy)
   intensity=(p.speed/max(1,p.a.maximum_speed))**2
   if live:
    cost=(.00015+.006*intensity)*(1.25-p.a.endurance*.6)*A['fatigue_rate']
    p.fatigue=clamp(p.fatigue-dta*cost,.15,1)
   elif p.speed<2:p.fatigue=min(1,p.fatigue+dta*.002*p.a.endurance)
   self.stats['player_distance_mm']+=int(norm(p.x-old[p.id][0],p.y-old[p.id][1])*1000)
  self.c3_adv=adv
  return old
 def c3_free(self,p,mode,dt,live,carrier):
  s=self.s
  if mode=='fly':
   p.x=clamp(p.x+p.vx*dt,-28,128);p.y=clamp(p.y+p.vy*dt,-38,138);self.c3_fly(p,dt);return
  if mode=='slide':
   sp=p.speed
   if self.c3b and p.posture=='grounded':
    #C3b: an athlete on the ground slides against ground friction (slide_friction x g). Constant deceleration, so the distance is
    #exact: the mean of the speeds over the time he is still moving.
    if sp>0:
     a=self.assume['slide_friction']*self.assume['gravity'];new=max(0.,sp-a*dt);d=(sp+new)/2*(dt if new>0 else sp/a);p.x+=p.vx/sp*d;p.y+=p.vy/sp*d;p.vx*=new/sp;p.vy*=new/sp
   else:
    if sp>0:
     new=max(0,sp-p.a.braking*dt);p.vx*=new/sp;p.vy*=new/sp
    p.x+=p.vx*dt;p.y+=p.vy*dt
  else:
   self.c3_desired(p,dt,live,carrier)
   p.x=clamp(p.x+p.vx*dt,-28,128);p.y=clamp(p.y+p.vy*dt,-38,138)
  if p.posture=='airborne':
   p.z+=p.vz*dt-.5*self.assume['gravity']*dt*dt;p.vz-=self.assume['gravity']*dt
   if p.z<=0:p.z=0;p.vz=0;p.posture='upright'
 def c3_cross(self,rx,ry,wx,wy,R,limit,entry):
  """First time in (0, limit) at which two points with relative position (rx,ry) and relative velocity (wx,wy) are exactly R apart.
  entry=True: only the instant they come within R (body contact). entry=False: either crossing (reach begins or ends)."""
  a=wx*wx+wy*wy
  if a<1e-18:return None
  b=rx*wx+ry*wy;disc=b*b-a*(rx*rx+ry*ry-R*R)
  if disc<=0:return None
  q=math.sqrt(disc);t1=(-b-q)/a
  if 1e-9<t1<limit:return t1
  if entry:return None
  t2=(-b+q)/a
  return t2 if 1e-9<t2<limit else None
 def c3_fly(self,p,dt):
  if p.posture=='airborne':
   g=self.assume['gravity'];p.z+=p.vz*dt-.5*g*dt*dt;p.vz-=g*dt
   if p.z<=0:p.z=0;p.vz=0;p.posture='upright'
 def c3_run(self,ms,pairs,group,carrier,live):
  """Drift-and-kick integration of the athletes in opposing pairs for up to ms milliseconds. Returns the milliseconds advanced."""
  s=self.s;A=self.assume;T=ms/1000.;h=A['c3_substep_ms']/1000.;scale=A['body_radius_scale'];TOL=1e-6;now0=s.now;down=self.c3_down
  eps=A['contact_restitution'];t=0.;event=None;budget=8*int(ms/A['c3_substep_ms'])+64;pre=self.c3_pre={};dt=0.
  cpairs=[]
  if carrier is not None:
   for a,b,R in pairs:
    if carrier.id in(a.id,b.id):
     d_=b if carrier.id==a.id else a;cpairs.append((d_,d_.radius+carrier.radius+.7*(d_.a.reach+carrier.a.reach)))
   cpairs.sort(key=lambda x:x[0].id)
  # bodies that are already touching and closing as the interval begins (they met in the last fraction of a millisecond of the
  # one before, or an event cut that one short at the instant of contact) exchange their impulse now, not a substep later
  event=self.c3_contact_kick(pairs,group,None if self.c3_lost else carrier,0.,now0,TOL,eps,scale)
  while t<T-1e-9 and event is None:
   car=None if self.c3_lost else carrier;cut=min(h,T-t);budget-=1
   # ---- where this drift must stop: first body contact, first change of reach, completion of an action in preparation ----
   if budget>0:
    for a,b,R in pairs:
     if a.id in down or b.id in down:continue
     rx,ry=b.x-a.x,b.y-a.y
     if rx*rx+ry*ry>(R+TOL)*(R+TOL):
      tau=self.c3_cross(rx,ry,b.vx-a.vx,b.vy-a.vy,R,cut,True)
      if tau is not None:cut=tau
    if car is not None and car.id not in down:
     for d_,Rr in cpairs:
      if d_.id in down:continue
      tau=self.c3_cross(d_.x-car.x,d_.y-car.y,d_.vx-car.vx,d_.vy-car.vy,Rr,cut,False)
      if tau is not None:cut=tau
      off=self.c3_off.get((d_.id,car.id))if self.c3_off else None
      if off is not None:
       #C3c2: the instant a holder who was thrown off may reach for him again (his own reaction time later)
       tau=(off+1000*d_.a.decision_speed-(now0+t*1000))/1000.
       if 1e-9<tau<cut:cut=tau
   else:self.stats['c3_cut_budget_exhausted']+=1
   prep=False;rho=0.;pend=self.pending_ball_actions.get(car.id)if car is not None and car.id not in down else None
   if pend is not None:
    due=self.c3_due.get(car.id)
    if due is None or int(math.ceil(due-1e-6))!=pend[0]:due=float(pend[0])
    rho=self.c3_rho(car,pend[1]);rem=(due-(now0+t*1000))/1000.
    if rho<1 and 0<rem<=(1-rho)*cut:cut=rem/(1-rho);prep=True
    if self.c3c and rho>0 and pend[1]!='kick'and A['tuck_after_delay_frac']>0 and self.c3_dur.get(car.id):
     #C3c: the drift also stops at the instant the hold has cost this wind-up tuck_after_delay_frac of its own length
     room=(A['tuck_after_delay_frac']*self.c3_dur[car.id]-self.c3_stall.get(car.id,0.))/(rho*1000.)
     if 0<room<cut:cut=room;prep=False
   inreach={}
   if car is not None:
    for d_,Rr in cpairs:
     mx=(d_.x-car.x)+(d_.vx-car.vx)*cut*.5;my=(d_.y-car.y)+(d_.vy-car.vy)*cut*.5;inreach[d_.id]=mx*mx+my*my<=Rr*Rr
   # ---- drift ----
   dt=cut;t0=t
   for p in group:
    pre[p.id]=(p.x,p.y,p.z,p.vx,p.vy,p.vz,p.posture)
    x=p.x+p.vx*dt;y=p.y+p.vy*dt;p.x=-28 if x<-28 else 128 if x>128 else x;p.y=-38 if y<-38 else 138 if y>138 else y
    if p.posture=='airborne':self.c3_fly(p,dt)
   t+=dt;self.c3_t=t;f=1.
   if dt>0:
    # ---- kick 1: each athlete's own propulsion over the drift just made ----
    for p in group:
     if p.id in down:
      sp=p.speed
      if sp>0:
       new=max(0,sp-(A['slide_friction']*A['gravity']if self.c3b else p.a.braking)*dt);p.vx*=new/sp;p.vy*=new/sp
     else:self.c3_desired(p,dt,live,car)
    # ---- kick 2: grip, coupling through the holds and balance over the same drift ----
    f,event=self.c3_holds_kick(group,car,cpairs,inreach,dt,t0,now0)
   # ---- kick 3: bodies in contact at this instant exchange one equal and opposite impulse ----
   if event is None:event=self.c3_contact_kick(pairs,group,car,t,now0,TOL,eps,scale)
   # ---- an action in preparation: restraint has delayed it by rho x the time elapsed ----
   if pend is not None and car.id in self.pending_ball_actions and not self.c3_lost and car.id not in down:
    gone=f*dt*1000
    if prep and f>=1 and event is None:due=now0+t*1000;event=('preparation_complete',t)
    else:due+=rho*gone
    self.stats['c3_preparation_delay_ms']+=rho*gone;self.c3_due[car.id]=due;self.pending_ball_actions[car.id]=(int(math.ceil(due-1e-6)),pend[1],pend[2])
    if self.c3c and pend[1]!='kick'and event is None:
     #C3c: the time a hold has cost this wind-up so far. When it has cost as much as the whole wind-up takes unrestrained
     #(tuck_after_delay_frac x that), he gives it up and tucks the ball. The pending release is cancelled; nothing else is reset.
     st=self.c3_stall.get(car.id,0.)+rho*gone;self.c3_stall[car.id]=st;full=self.c3_dur.get(car.id)
     if A['tuck_after_delay_frac']>0 and full and st>=A['tuck_after_delay_frac']*full-1e-9:
      left=due-(now0+t*1000);del self.pending_ball_actions[car.id];self.c3_due.pop(car.id,None);self.stats['c3_tucks']+=1
      self.c3_note(t,'c3_tuck',rule='C3c-1',player=car.id,action=pend[1],stalled_ms=round(st,1),wind_up_ms=round(full,1),wind_up_left_ms=round(left,1),restraint=round(rho,4),since_start_ms=round(now0+t*1000-self.c3_prep.get(car.id,now0),1))
      event=('tuck',t)
  if event is None:return ms
  # the interval ends at the whole millisecond at or after the event; positions are moved to that instant along the last drift
  stop=min(ms,max(1,self.c3_at(event[1])));delta=stop/1000.-t
  for p in group:
   if delta<0:
    x,y,z,vx,vy,vz,posture=pre[p.id];tau=max(0.,dt+delta);p.z,p.vz,p.posture=z,vz,posture;self.c3_fly(p,tau)
    p.x=clamp(x+vx*tau,-28,128);p.y=clamp(y+vy*tau,-38,138)
   elif delta>0:
    p.x=clamp(p.x+p.vx*delta,-28,128);p.y=clamp(p.y+p.vy*delta,-38,138);self.c3_fly(p,delta)
  self.c3_t=stop/1000.
  return stop
 def c3_holds_kick(self,group,car,cpairs,inreach,dt,t0,now0):
  """Grip, coupling and balance for one drift of length dt that began at kernel time t0. Returns (f, event): f is the fraction of
  the drift after which the first athlete's balance load reached 1 (1 if nobody's did). When f < 1 the changes this kick made to
  velocities and balance are scaled back to that instant, so that nothing is applied after the first grounding."""
  s=self.s;A=self.assume;down=self.c3_down;t=t0+dt;start_ms=now0+t0*1000;end_ms=now0+t*1000
  ups=[p for p in group if p.id not in down];B0={};snap={};prior=[];strip_by=None;strip_w=None;broken=[];thrown=[]
  windup=self.pending_ball_actions.get(car.id)if self.c3c and car is not None else None
  if windup is not None and windup[1]=='kick':windup=None
  effort=self.c3_escape_effort(car,windup)if self.c3c and car is not None and car.id not in down else 0.
  share=self.c4a_shares(car,cpairs,inreach,start_ms,down)if effort>0 else{} #C4a: how that effort is divided among the holds on him
  # balance is integrated exactly over the drift: existing load decays first, then this drift's load is added with the
  # matching factor, so that dB/dt = rate - recovery x B is followed whatever the substep length
  for p in ups:
   B0[p.id]=self.c3_bal(p)
   if p.bal_src:snap[p.id]=dict(p.bal_src);self.c3_recover(p,dt)
  active=[]
  if car is not None and car.id not in down:
   for d_,Rr in cpairs:
    if d_.id in down:continue
    key=(d_.id,car.id);hd=self.c3_holds.get(key);ok=inreach[d_.id];cause='out_of_reach'
    if ok:
     #within reach for the whole of this drift (the drift was cut where reach began or ended). The contact must also be lawful.
     #Reach is the kernel's own solved test just made; the engine's distance test is left out so that it cannot hide a protected carrier.
     ok,why=self.e.contact_legal(d_,car,'tackle',reach=False);cause='not_lawful'
    if not ok:
     if hd is not None:self.c3_end_hold(key,cause,start_ms,t0)
     continue
    if hd is None:
     off=self.c3_off.get(key)if self.c3_off else None
     if off is not None:
      #C3c2: his hold on this carrier was pried off (or his grab fended off). His hands are off him. He can reach again once his
      #own reaction time has passed, and what he takes then is a new hold: its own record, grip from zero, earned by the same law.
      if start_ms<off+1000*d_.a.decision_speed-1e-6:continue
      del self.c3_off[key]
     region,seen=self.c3_region(d_,car,start_ms)
     hd=self.c3_holds[key]={'actor':d_.id,'target':car.id,'g':0.,'region':region,'start':start_ms,'reach_ms':0.,'peak':0.,'impulse':0.,'excess':0.,'force':0.,'slip':0.}
     self.stats['c3_holds_started']+=1
     self.c3_note(t0,'engagement','6.1–6.4',actor=d_.id,target=car.id,kind='tackle')
     self.c3_note(t0,'c3_hold_start',actor=d_.id,target=car.id,region=region,release_preparation_observed=seen is True,start_ms=round(start_ms,3),**({'pass_open_observed':seen=='pass_open'}if self.c3c else{}),**({'in_defended_zone_observed':seen=='in_defended_zone'}if self.assume['c3_region_policy']==2 else{}),**({'ms_since_his_last_hold_was_thrown_off':round(start_ms-off,3)}if off is not None else{}))
    # slip: relative speed that is not closing (tangential or separating), m/s
    ex,ey=unit(car.x-d_.x,car.y-d_.y);rvx,rvy=car.vx-d_.vx,car.vy-d_.vy;sep=rvx*ex+rvy*ey;tan=abs(-rvx*ey+rvy*ex)
    slip=norm(max(0.,sep),tan)
    align=.5+.5*max(0.,d_.facing[0]*ex+d_.facing[1]*ey)
    gain=A['grip_gain_per_s']*(.5+d_.a.tackling)*(.6+.4*d_.fatigue)*align
    loss=A['grip_resist_per_s']*(.5+car.a.contact_resistance)+A['grip_slip_per_s']*slip/A['grip_slip_ref_mps']+A['grip_overload_per_s']*hd['excess']
    if self.c3c and effort>0:
     #C3c (decided by DreLen: with enough strength and balance a carrier can loosen a grip and escape). A carrier working to
     #free himself pries at the hold. The force he can pry with is
     #  effort x escape_force_N x (0.5 + his strength) x (0.6 + 0.4 x his fatigue factor)
     #  x (0.5 + his balance) x (1 - his balance load now)     the balance he has to work with: less as he is being toppled
     #  x his legs                                              a lower hold takes them, by lower_hold_leg_factor x grip
     #and it is set against the holder's full grip force, grip_force_N x (0.5 + the holder's strength). That ratio is added to
     #the load excess of the hold, so it loosens the grip at the retained rate grip_overload_per_s, exactly as a load the hold
     #cannot carry already does. The holder's technique is in the gain he sets against it. Every term is continuous: there is
     #no threshold below which strength counts for nothing, and no timer. (1 - load) cannot be negative for a man on his feet.
     legs=1-A['lower_hold_leg_factor']*hd['g']if hd['region']=='lower'else 1.
     sh=share.get(d_.id,1.)if share else 1.;hd['share']=sh;hd['share_ms']=hd.get('share_ms',0.)+sh*dt*1000 #C4a: his share of the one effort
     pry=sh*effort*A['escape_force_N']*(.5+car.a.strength)*(.6+.4*car.fatigue)*(.5+car.a.balance)*max(0.,1-B0[car.id])*legs
     work=A['grip_overload_per_s']*pry/(A['grip_force_N']*(.5+d_.a.strength))
     loss+=work;hd['break_rate']=work;hd['escape_ms']=hd.get('escape_ms',0.)+dt*1000;hd['pry_N']=pry;hd['pry_t0']=t0 #C4b: which drift was pried in
     #C3c2, actual detachment (the Lead's C3c1 audit). Up to the holder's full grip force, prying is a load his grip can oppose: it
     #loosens the grip in proportion, as above, and the grip settles lower. Prying force BEYOND his full grip force is force that no
     #grip of his can oppose: it opens his hands outright, at the same retained rate,
     #  tear (1/s) = grip_overload_per_s x max(0, prying force / holder's full grip force - 1)
     #taken off the grip whatever its level. So dg/dt = (gain - tear) - (gain + loss) g. While gain > tear the grip still settles above
     #zero (lower). Once tear exceeds gain, the rate at which his technique re-closes his hands, the grip runs down to zero in a
     #finite time, and at zero the hold is off. No new coefficient and no threshold on the grip: zero grip is no hold.
     #Strength still counts at every level through the proportional term; the tear only adds to it.
     tear=A['grip_overload_per_s']*max(0.,pry/(A['grip_force_N']*(.5+d_.a.strength))-1.);hd['tear_rate']=tear
    else:hd['break_rate']=0.;tear=0.
    #dg/dt = gain*(1-g) - loss*g, integrated exactly over the time in reach, so the result does not depend on the substep length
    prior.append((hd['g'],hd['peak']));k=gain+loss
    if tear>0:
     a_=gain-tear;g0=hd['g'];geq=a_/k;tz=None
     if a_<0:tz=0. if g0<=0 else math.log(1.-g0*k/a_)/k #the instant at which the grip reaches zero, solved on the same law
     if tz is not None and tz<=dt:
      #the hold is off at start + tz. It couples and restrains nothing in this drift. It is committed below, unless a grounding in
      #this same drift came first, in which case it is put back as it was at the grounding.
      hd['g']=0.;hd['reach_ms']+=tz*1000;self.stats['c3_hold_ms']+=tz*1000;hd['escape_ms']-=(dt-tz)*1000;prior.pop()
      if'share_ms'in hd:hd['share_ms']-=hd['share']*(dt-tz)*1000 #C4b: the effort-weighted time is taken back with the prying time
      thrown.append((key,hd,d_,tz,g0,geq,k,gain));continue
     hd['g']=max(0.,geq+(g0-geq)*math.exp(-k*dt))
    else:geq=gain/k if k>0 else 0.;hd['g']=geq+(hd['g']-geq)*math.exp(-k*dt)
    if self.c3c and hd['break_rate']>0 and prior[-1][0]>=A['tackle_grip_threshold']>hd['g']:broken.append((hd,d_))
    hd['peak']=max(hd['peak'],hd['g']);hd['reach_ms']+=dt*1000;hd['slip']=slip
    self.stats['c3_hold_ms']+=dt*1000
    if self.c3b:
     #C3b containment (controller choice, observable state only): hold him up and stay with him instead of driving him down
     hd['mode']='contain'if self.c3_contain(d_,car)else'drive'
     if hd['mode']=='contain'and hd['g']>=A['tackle_grip_threshold']:
      #it is a containment once he materially has hold of him; before that he is only staying with him to get a grip
      if not hd.get('contain_ms'):self.stats['c3_containments']+=1;self.c3_note(t0,'c3_containment',rule='C3b-2',actor=d_.id,target=car.id,grip=round(hd['g'],4),zone_remaining_ms=self.c3_zone_left(car))
      hd['contain_ms']=hd.get('contain_ms',0.)+dt*1000
    active.append((hd,d_))
    # inherited strip mechanism: the Pocket 1.1 chance per second of lawful reach, converted so that halving the substep does not double it
    rate=.12*d_.a.tackling*(1-car.a.ball_handling*.6);lam=-math.log(max(1e-12,1-.1*rate))/.1;smod=None
    if self.c3c and windup and hd['region']=='upper':
     #C3c (decided by DreLen: wrapped in the throwing motion he may cough it up). No new hazard and no extra draw: the retained
     #strip rate is multiplied while his arms are pinned by an upper hold during a hand wind-up, in proportion to the pin.
     pin=min(1.,hd['g']/A['arm_pin_grip']);smod={'modifier':round(1+(A['strip_in_motion_factor']-1)*pin,4),'pin':round(pin,4),'holder':d_.id,'action':windup[1],'stalled_ms':round(self.c3_stall.get(car.id,0.),1)};lam*=smod['modifier']
     hd['pin_ms']=hd.get('pin_ms',0.)+dt*1000;hd['pin_peak']=max(hd.get('pin_peak',0.),pin);hd['smod_peak']=max(hd.get('smod_peak',1.),smod['modifier']);hd['pin_now']=dt*1000
    else:hd['pin_now']=0.
    #the strip, if drawn, takes effect at the end of this drift, after the forces that acted during it (one strip at most)
    if strip_by is None and not self.c3_no_strip and self.rng['contact'].random()<1-math.exp(-lam*dt):strip_by=d_;strip_w=smod
  if active:
   # momentum coupling through the holds, capped by grip capacity; all holds on the carrier solved together
   n=len(active);mc=car.a.mass;P=[[0.,0.]for _ in active];caps=[hd['g']*A['grip_force_N']*(.5+d_.a.strength)*dt for hd,d_ in active]
   for _ in range(4):
    imp=[]
    for i,(hd,d_)in enumerate(active):
     mu=mc*d_.a.mass/(mc+d_.a.mass);px=-mu*(car.vx-d_.vx)/n;py=-mu*(car.vy-d_.vy)/n
     tx,ty=P[i][0]+px,P[i][1]+py;mag=norm(tx,ty)
     if mag>caps[i]:
      c=caps[i]/mag if mag>0 else 0.;tx,ty=tx*c,ty*c
     imp.append((tx-P[i][0],ty-P[i][1]));P[i]=[tx,ty]
    for(hd,d_),(px,py)in zip(active,imp):
     car.vx+=px/mc;car.vy+=py/mc;d_.vx-=px/d_.a.mass;d_.vy-=py/d_.a.mass
   H=car.a.height;w=A['base_half_width_frac']*H
   for i,(hd,d_)in enumerate(active):
    mag=norm(*P[i]);F=mag/dt;hd['force']=F;hd['last_impulse']=mag;hd['last_P']=(P[i][0],P[i][1])
    mu=mc*d_.a.mass/(mc+d_.a.mass);want=mu*norm(car.vx-d_.vx,car.vy-d_.vy)
    #load excess (dimensionless): the force that would stop the slip the hold could not prevent, over the overload time, relative to
    #the holder's full grip force. Zero while the hold keeps the two bodies together. It does not depend on the substep.
    hd['excess']=want/(A['grip_overload_time_s']*A['grip_force_N']*(.5+d_.a.strength))
    lever=(A['hold_height_upper_frac']if hd['region']=='upper'else A['hold_height_lower_frac'])*H
    #toppling moment over restoring moment (dimensionless) sets a RATE of balance load, 1/s, through topple_time_s
    M=F*lever/(mc*A['gravity']*w)
    self.c3_add(car,('hold',d_.id),M/A['topple_time_s']*self.c3_span(car,dt),True,start_ms)
    Md=F*A['hold_height_upper_frac']*d_.a.height/(d_.a.mass*A['gravity']*A['base_half_width_frac']*d_.a.height)
    self.c3_add(d_,('holding',car.id),A['holder_load_factor']*Md/A['topple_time_s']*self.c3_span(d_,dt),True,start_ms)
  if self.c3b and car is not None and car.id not in down:
   # C3b controlled descent. A carrier under a material hold may choose to go to ground. He stops recovering his balance and
   # lowers himself at 1 / descent_time_s. Holders who are containing him hold him up with what their grip can carry: the part of
   # his weight they can support is taken off that rate. It is never guaranteed, and the load is his own, not the defence's.
   thr=A['tackle_grip_threshold'];held=[(hd,d_)for hd,d_ in active if hd['g']>=thr];des=self.c3_descent.get(car.id)
   want=bool(held)and self.c3_descend(car)
   if des is None and want:
    des=self.c3_descent[car.id]={'since':start_ms,'support':0.};self.stats['c3_descents_attempted']+=1
    self.c3_note(t0,'c3_descent_start',rule='C3b-3',player=car.id,zone_remaining_ms=self.c3_zone_left(car),holders=[{'player':d_.id,'grip':round(hd['g'],4),'mode':hd.get('mode')}for hd,d_ in held])
   elif des is not None and not want:
    self.c3_descent_end(car.id,'hold_lost'if not held else'no_longer_wanted',start_ms,t0);des=None
   if des is not None:
    sup=min(1.,sum(hd['g']*A['grip_force_N']*(.5+d_.a.strength)for hd,d_ in active if hd.get('mode')=='contain')/(car.a.mass*A['gravity']))
    des['support']=sup;self.c3_add(car,('descent',car.id),(1-sup)/A['descent_time_s']*dt,True,start_ms)
  # ---- grounding by accumulated load, at the interpolated instant the load reaches 1 ----
  f=1.;first=[]
  for p in ups:
   B=self.c3_bal(p)
   if B>=1:
    b0=B0[p.id];fp=clamp((1-b0)/(B-b0),0.,1.)if b0<1 and B>b0 else 0.
    if fp<f-1e-12:f=fp;first=[p]
    elif fp<=f+1e-12:first.append(p)
  if not first:
   for hd,d_ in active:
    hd['impulse']+=hd['last_impulse'];px,py=hd['last_P']
    self.c3_push(car,px/car.a.mass,py/car.a.mass,d_.id,end_ms);self.c3_push(d_,-px/d_.a.mass,-py/d_.a.mass,car.id,end_ms)
   for z in thrown:self.c3_throw_off(z,car,B0[car.id],t0,start_ms)
   for hd,d_ in broken:
    self.stats['c3_grips_broken']+=1;self.c3_note(t,'c3_grip_broken',rule='C3c-4',actor=d_.id,target=car.id,region=hd['region'],peak_grip=round(hd['peak'],4),grip=round(hd['g'],4),hold_ms=round(end_ms-hd['start'],1),
                                                  escape_ms=round(hd.get('escape_ms',0.),1),break_rate_per_s=round(hd.get('break_rate',0.),3),prying_force_N=round(hd.get('pry_N',0.),1),carrier_balance_load=round(B0[car.id],4),holder_mode=hd.get('mode'));hd['broken']=hd.get('broken',0)+1
   if strip_by is not None:
    if strip_w is not None:self.stats['c3_strips_in_wind_up']+=1;self.c3_note(t,'c3_strip_in_wind_up',rule='C3c-1',actor=strip_by.id,target=car.id,**{k:v for k,v in strip_w.items()if k!='holder'})
    self.c3_events.append(Event('strip',strip_by.id,car.id,{'control_witness':s.ball.version,'c3':True},at=self.c3_at(t)));self.c3_lost='strip';self.stats['c3_strips_scheduled']+=1
    for k2 in list(self.c3_holds):
     if k2[1]==car.id:self.c3_end_hold(k2,'strip',end_ms,t)
    return 1.,('strip',t)
   return 1.,None
  if strip_by is not None:self.stats['c3_strips_overtaken_by_grounding']+=1 #the grounding came first: the strip drawn for the end of this drift does not happen
  first.sort(key=lambda p:not(car is not None and p.id==car.id)) #the carrier is classified first (see c3_contact_kick)
  if f<1:
   #everything this kick did is taken back to the grounding instant: every athlete's velocity change (his own propulsion and
   #the coupling), the grip gained, the time in reach and the balance contributions
   pre=self.c3_pre
   for p in group:
    vx0,vy0=pre[p.id][3],pre[p.id][4];p.vx=vx0+f*(p.vx-vx0);p.vy=vy0+f*(p.vy-vy0)
   for(hd,d_),(g_was,peak_was)in zip(active,prior):
    hd['g']=g_was+f*(hd['g']-g_was);hd['peak']=max(peak_was,hd['g']);hd['reach_ms']-=(1-f)*dt*1000;self.stats['c3_hold_ms']-=(1-f)*dt*1000
    if(hd.get('pry_t0')==t0 if self.assume['escape_allocation']else hd.get('break_rate')):
     hd['escape_ms']-=(1-f)*dt*1000 #C4b: with allocation on, a hold given no share was still pried in this drift (escape time), so the test is the drift itself
     if'share_ms'in hd:hd['share_ms']-=hd['share']*(1-f)*dt*1000
    if hd.get('pin_now'):hd['pin_ms']-=(1-f)*dt*1000
   for p in ups:
    end=p.bal_src;was=snap.get(p.id,{});mix={}
    for k in list(end)+[k for k in was if k not in end]: #a fixed order: the sum of the contributions must not depend on how a set happens to be ordered
     v=was.get(k,0.)+f*(end.get(k,0.)-was.get(k,0.))
     if v>0:mix[k]=v
    p.bal_src=mix
  te=t0+f*dt;back=t-te
  for z in thrown:
   key,hd,d_,tz,g0,geq,k,gain=z
   if tz<=f*dt:self.c3_throw_off(z,car,B0[car.id],t0,start_ms)
   else:hd['g']=max(0.,geq+(g0-geq)*math.exp(-k*f*dt));hd['reach_ms']+=(f*dt-tz)*1000;self.stats['c3_hold_ms']+=(f*dt-tz)*1000;hd['escape_ms']+=(f*dt-tz)*1000 #the grounding came first: he is still held
   if'share_ms'in hd and tz>f*dt:hd['share_ms']+=hd['share']*(f*dt-tz)*1000 #C4b: and the share time with it
  for hd,d_ in active:
   hd['impulse']+=f*hd['last_impulse'];px,py=f*hd['last_P'][0],f*hd['last_P'][1]
   self.c3_push(car,px/car.a.mass,py/car.a.mass,d_.id,now0+te*1000);self.c3_push(d_,-px/d_.a.mass,-py/d_.a.mass,car.id,now0+te*1000)
  for p in first:self.c3_ground(p,car,self.c3_bal(p),te,now0+te*1000,back)
  return f,('grounding',te)
 def c3_throw_off(self,z,car,load,t0,start_ms):
  """C3c2: a hold whose grip the carrier's prying has run down to zero is off. Its restraint and coupling end at that instant
  (c3_hold_end, cause pried_off; fended_off if the grab never had any grip). The holder can reach for him again only after
  his own reaction time, and that is a new hold from zero grip. A grip that was material when the prying began to tear it is
  also recorded as broken, at the same instant, so that record keeps its meaning: worked below the tackle threshold."""
  key,hd,d_,tz,g0,geq,k,gain=z;A=self.assume;t=t0+tz;at=start_ms+tz*1000;had=hd['peak']>0;cause='pried_off'if had else'fended_off'
  if g0>=A['tackle_grip_threshold']:
   self.stats['c3_grips_broken']+=1;hd['broken']=hd.get('broken',0)+1
   self.c3_note(t,'c3_grip_broken',rule='C3c-4',actor=d_.id,target=car.id,region=hd['region'],peak_grip=round(hd['peak'],4),grip=0.,hold_ms=round(at-hd['start'],1),escape_ms=round(hd.get('escape_ms',0.),1),
                break_rate_per_s=round(hd.get('break_rate',0.),3),prying_force_N=round(hd.get('pry_N',0.),1),carrier_balance_load=round(load,4),holder_mode=hd.get('mode'))
  full=A['grip_force_N']*(.5+d_.a.strength);self.stats['c3_holds_pried_off'if had else'c3_grabs_fended_off']+=1
  self.c3_note(t,'c3_hold_detached',rule='C3c-4',actor=d_.id,target=car.id,region=hd['region'],cause=cause,grip_before_this_step=round(g0,4),peak_grip=round(hd['peak'],4),hold_ms=round(at-hd['start'],3),
               escape_ms=round(hd.get('escape_ms',0.),3),prying_force_N=round(hd.get('pry_N',0.),1),holder_full_grip_force_N=round(full,1),force_ratio=round(hd.get('pry_N',0.)/full,4),
               tear_rate_per_s=round(hd.get('tear_rate',0.),3),holder_gain_per_s=round(gain,3),carrier_balance_load=round(load,4),holder_mode=hd.get('mode'),
               holder_may_reach_again_at_ms=round(at+1000*d_.a.decision_speed,3))
  self.c3_off[key]=at;self.c3_end_hold(key,cause,at,t)
 def c3_withhold(self,p,kind):
  """C3c controller: a carrier does not begin a hand release that the hold on him would make him abandon. A wind-up is given
  up when a hold has cost it tuck_after_delay_frac of its own length; at steady restraint r it finishes first if
  r < frac / (1 + frac) (0.5 at the default). At exactly that restraint the release and the tuck fall at the same instant and the
  release has precedence, so a wind-up begun there would still be released: not beginning one at the limit itself is this
  controller's cautious choice, not something the timing forbids. He starts one only below it. Kicks are not affected."""
  f=self.assume['tuck_after_delay_frac']
  if self.c3_fix_withhold is not None:return bool(self.c3_fix_withhold)and kind!='kick'
  if kind=='kick'or f<=0:return False
  r=self.c3_rho(p,kind)
  if r<f/(1+f):return False
  if self.c3_told.get(p.id)!=self.s.ball.control_time: #logged once per spell of control
   self.c3_told[p.id]=self.s.ball.control_time;self.stats['c3_releases_withheld']+=1;self.e.emit('c3_release_withheld','C3c-1',player=p.id,action=kind,restraint=round(r,4),limit=round(f/(1+f),4))
  return True
 def c3_pass_open(self,c):
  #A pass is open to the carrier, as an opponent can see it: an eligible upright team-mate between 3 and 30 m from him with no opponent within marking distance.
  s=self.s;md=self.e.mark_d
  for q in s.players.values():
   if q.team!=c.team or q.id==c.id or q.role=='archer'or not self.e.eligible(q)or q.posture!='upright':continue
   if not 3<=norm(q.x-c.x,q.y-c.y)<=30:continue
   if all(norm(o.x-q.x,o.y-q.y)>md for o in s.players.values()if o.team!=c.team and o.active and o.role!='archer'and self.e.eligible(o)):return True
  return False
 def c4a_shares(self,car,cpairs,inreach,start_ms,down):
  """C4a (the Lead's C4 contract): a carrier has one prying effort, not one for each hold. Returns {holder: share}, shares summing
  to 1 over the holds he can work on in this drift (the holders in reach, lawful and not still recovering from being thrown off:
  the same tests the hold loop applies). Empty = the C3c2 rule, every hold at full effort.
    1 equal: 1/n each.
    2 weakest as he feels it: all on the hold with the lowest grip at the start of the drift (a grab just begun has grip 0).
      Ties: the earlier holder id. Observable: the grip is what he feels.
    3 weakest in truth: all on the hold whose holder's full grip force, grip_force_N x (0.5 + strength), times its grip, is the
      least. That uses the holder's strength, which the carrier cannot see: PERFECT INFORMATION, for drills only."""
  mode=int(self.assume.get('escape_allocation',0))
  if not mode:return{}
  cands=[]
  for d_,Rr in cpairs:
   if d_.id in down or not inreach[d_.id]:continue
   if not self.e.contact_legal(d_,car,'tackle',reach=False)[0]:continue
   key=(d_.id,car.id);hd=self.c3_holds.get(key)
   if hd is None:
    off=self.c3_off.get(key)if self.c3_off else None
    if off is not None and start_ms<off+1000*d_.a.decision_speed-1e-6:continue
   cands.append((d_,hd))
  if not cands:return{}
  if mode==1:return{d_.id:1./len(cands)for d_,_ in cands}
  g=lambda hd:hd['g']if hd else 0.
  if mode==2:w=min(cands,key=lambda c:(g(c[1]),c[0].id))[0].id
  else:w=min(cands,key=lambda c:(self.assume['grip_force_N']*(.5+c[0].a.strength)*g(c[1]),c[0].id))[0].id
  return{d_.id:(1. if d_.id==w else 0.)for d_,_ in cands}
 def c3_escape_effort(self,car,windup):
  """C3c placeholder controller: how hard a held carrier is working to break the grip, 0 to 1. Full effort, unless his arms are
  busy with a hand wind-up or he is letting himself down (C3b descent). It is logged on each hold as time spent at it."""
  if self.c3_fix_escape is not None:return float(self.c3_fix_escape)
  return 0. if windup is not None or car.id in self.c3_descent else 1.
 def c3_zone_left(self,car):
  #Milliseconds of zone time the carrier has left in the Keeper Zone his team attacks, or None if he is not in it (or occupancy is off).
  s=self.s
  if not self.e.c2_occ or s.owner!=car.team:return None
  j=self.e.zone(car.x,car.y)
  return 5000-car.zone_ms[j]if j is not None and j==s.own_zone(s.other(car.team))else None
 def c3_contain(self,d,car):
  """C3b placeholder controller: does this holder contain instead of driving the carrier down? He does when a tackle would only
  be the attack's first (it keeps the ball) and the carrier's zone time will run out within containment_window_s, so that
  holding him up wins the ball. Read from the public state: tackle count, zone and zone count."""
  if self.c3_fix_contain is not None:return bool(self.c3_fix_contain)
  s=self.s;w=self.assume['containment_window_s']
  if w<=0 or not self.e.c2_tackles or s.tackle_count!=0:return False
  left=self.c3_zone_left(car)
  return left is not None and left<=1000*w
 def c3_descend(self,car):
  """C3b placeholder controller: does the carrier, materially held, try to go to ground? He does when going down would be his
  team's first tackle (it keeps the ball) and his zone time will run out within descent_window_s."""
  if self.c3_fix_descent is not None:return bool(self.c3_fix_descent)
  s=self.s;w=self.assume['descent_window_s']
  if w<=0 or not self.e.c2_tackles or s.tackle_count!=0:return False
  left=self.c3_zone_left(car)
  return left is not None and left<=1000*w
 def c3_descent_end(self,pid,cause,end_ms,t=0.):
  des=self.c3_descent.pop(pid,None)
  if des is None:return
  p=self.s.players[pid];own=(getattr(p,'bal_src',None)or{}).get(('descent',pid,True),0.)
  if cause!='grounded':self.stats['c3_descents_failed']+=1
  self.c3_note(t,'c3_descent_end',rule='C3b-3',player=pid,cause=cause,duration_ms=round(end_ms-des['since'],1),own_load=round(own,4),support_at_end=round(des['support'],4))
 def c3_settle(self,p,now_ms):
  """C3b: an imposed-velocity record can never be larger than the velocity the athlete actually still has in its direction.
  Whatever took that velocity away (his own braking, a later collision, sliding on the ground, a restart placement that stood
  him still) took the record with it, for good: a later run of his own in the same direction is his own. A record that still
  describes real motion, such as a slide he has not stopped, is left as it is."""
  if not getattr(p,'c3_ext',None):return
  fresh,(ox,oy,t0,src)=self.c3_driven(p,now_ms) #what is left of the record now, after the braking he is credited with
  ex=ox+sum(e[1]for e in fresh);ey=oy+sum(e[2]for e in fresh);mag=math.hypot(ex,ey)
  if mag<1e-12:p.c3_ext=None;return
  cap=max(0.,(p.vx*ex+p.vy*ey)/mag)
  if cap>=mag:return
  if cap<=1e-9:p.c3_ext=None;return
  f=cap/mag;p.c3_ext=(tuple((tm,dx*f,dy*f,by)for tm,dx,dy,by in fresh),(ox*f,oy*f,t0,src))
 def c3_push(self,p,dvx,dvy,by,now_ms):
  """Record a velocity change that another athlete's contact force put on p (a collision impulse, or the coupling through a hold).
  Kept as (fresh, held): fresh is the changes of the last reaction time, each with its time and source; held is what is left of
  the older ones. See c3_driven."""
  if dvx*dvx+dvy*dvy<1e-18:return
  fresh,held=self.c3_driven(p,now_ms);p.c3_ext=(fresh+((now_ms,dvx,dvy,by),),held)
 def c3_driven(self,p,now_ms):
  """The velocity p has now that other athletes' forces put on him and that he has not had the means to take off (m/s), as
  (fresh, (x, y, time, sources)). A change is carried in full for his own reaction time. After that it joins the held part,
  which shrinks at his own braking limit: he is taken to have been able to brake it off. A force stronger than his braking
  therefore keeps driving him for as long as it lasts; a weaker or a past one stops counting. This is the causal witness for
  'carried by another contact': an amount of velocity in a direction, not the fact of having been touched or held."""
  ext=getattr(p,'c3_ext',None)
  if ext is None:return(),(0.,0.,now_ms,())
  fresh,(ox,oy,t0,src)=ext;react=1000*p.a.decision_speed;brk=p.a.braking;k=0
  for tm,dvx,dvy,by in fresh:
   g=tm+react
   if g>now_ms:break
   k+=1;mag=math.hypot(ox,oy)
   if mag>0:
    left=max(0.,mag-brk*max(0.,g-t0)/1000);ox*=left/mag;oy*=left/mag
    if left<=0:src=()
   ox+=dvx;oy+=dvy;t0=max(t0,g)
   if by not in src:src=src+(by,)
  mag=math.hypot(ox,oy)
  if mag>0:
   left=max(0.,mag-brk*max(0.,now_ms-t0)/1000);ox*=left/mag;oy*=left/mag
   if left<=0:src=()
  return fresh[k:],(ox,oy,now_ms,src)
 def c3_no_time(self,p,q,why,now_ms):
  """Unavoidable momentum, second kind: p's contact on q had been lawful, and when that changed he was already too close to stop.
  The witness is a recorded change of legal circumstances and the state of the approach at the start of the interval in which
  the contact was first found unlawful, never the distance between them now. Two ways the change is found:
    - at the start of an interval (c3_move): the man ahead has turned his back, lost the ball or become protected;
    - at the contact itself, having been lawful when this interval began: the two have moved round each other within it.
  From that state: he carries on for his own reaction time, then brakes at his own limit until he is no longer closing on q
  (q is taken to keep the speed along the line that he had). If the gap between the bodies was more than the two would close
  in that time, he could have avoided the contact and is responsible. The excuse also lasts only for that reaction and braking
  time: a contact later than that is a different approach. Steering away is not considered. Returns (excused, witness)."""
  rec=self.c3_ch.get((p.id,q.id));first=None
  if rec is None:
   ok=self.c3_ok.get((p.id,q.id))
   if ok is None or ok[0]!=self.c3_ok_t:return False,{'last_lawful_ms':None} #his contact on q was unlawful for as long as q was near him: he had all the time there was
   rec=(ok[0],ok[1],why,ok[0],ok[2],ok[3],0.);first=round(now_ms,3)
  at,u,was,seen,gap,away,grow=rec;tr=p.a.decision_speed;brk=p.a.braking
  #During his reaction time he carries on as he was. C3b: that includes the rate at which his approach was growing (grow, m/s2,
  #zero in C3a3 and whenever it was not growing), up to his top speed. Then he brakes at his own limit until he is no longer closing.
  ur=min(u+grow*tr,max(u,p.a.maximum_speed));tb=max(0.,(ur-max(0.,away))/brk)
  used=(u-away)*tr+.5*(ur-u)*tr+(ur-away)*tb-.5*brk*tb*tb;window=1000*(tr+tb);gone=now_ms-at
  #C3b2: reaction time delays a response; it is not leave to begin one. There is no blanket excuse for a contact inside the
  #reaction time: an approach he only started after the change has no speed and no growth on record here, so its stopping gap
  #is zero and it is his. What he was already doing when the change came, growing speed included, is in the gap above.
  return gap<used and gone<=window+1,{**({'approach_growing_mps2':round(grow,3)}if self.c3b else{}),'last_lawful_ms':seen,'change_seen_ms':at if first is None else first,'changed_to':was,'state_at_ms':at,'gap_then_m':round(gap,3),'approach_then_mps':round(u,3),
                                    'target_receding_then_mps':round(away,3),'stopping_gap_m':round(used,3),'elapsed_ms':round(gone,1),'stopping_time_ms':round(window,1)}
 def c3_contact_kick(self,pairs,group,car,t,now0,TOL,eps,scale):
  """Body contact at kernel time t. Physics first and for everyone: one equal and opposite normal impulse, an explicit ground
  impulse for a braced athlete, and a balance shock from each athlete's own velocity change. Legal responsibility is a separate
  question, answered at this instant from an approach witness: who was moving into whom, and which retained classification
  applies to an athlete who initiated the contact. Returns an event if the engine must commit something (a grounding, a foul)."""
  s=self.s;A=self.assume;down=self.c3_down;now_ms=now0+t*1000;event=None;hit=[]
  for a,b,R in pairs:
   if a.id in down or b.id in down:continue
   dx,dy=b.x-a.x,b.y-a.y;dist=norm(dx,dy);gap=dist-R;key=(a.id,b.id)
   if gap>A['rearm_gap_m']:self.c3_armed[key]=True
   if gap>TOL:continue
   if not(self.e.eligible(a)and self.e.eligible(b)):continue #an athlete who has stepped off the field is not a solid body, as before
   ex,ey=unit(dx,dy)
   if ex==ey==0:ex=1.
   ua=a.vx*ex+a.vy*ey;ub=-(b.vx*ex+b.vy*ey);vn=ua+ub
   if vn<=0:continue
   if self.c3b:self.c3_settle(a,now_ms);self.c3_settle(b,now_ms) #against the velocities they arrive with, before this impulse changes them
   ma,mb=a.a.mass,b.a.mass;armed=self.c3_armed.get(key,True)
   J=(1+(eps if armed else 0.))*vn/(1/ma+1/mb)
   dva=(-J/ma*ex,-J/ma*ey);dvb=(J/mb*ex,J/mb*ey)
   a.vx+=dva[0];a.vy+=dva[1];b.vx+=dvb[0];b.vy+=dvb[1]
   if not armed:continue #resting or pushing contact: momentum is exchanged, no fresh shock until the bodies have really separated
   self.c3_armed[key]=False;self.stats['c3_collisions']+=1;hit+=[a.id,b.id]
   # explicit bracing: a ground impulse, bounded by traction, taken by an athlete who is set and facing the contact
   ground=[0.,0.]
   for i,(p,q,dv,sgn)in enumerate(((a,b,dva,1),(b,a,dvb,-1))):
    facing=(p.facing[0]*ex+p.facing[1]*ey)*sgn
    if norm(p.vx-dv[0],p.vy-dv[1])<A['brace_speed_mps']and facing>0:
     cap=A['traction_coefficient']*p.a.mass*A['gravity']*A['contact_time_s'];need=p.a.mass*norm(*dv);take=min(cap,need)
     if need>0:
      c=take/need;p.vx-=dv[0]*c;p.vy-=dv[1]*c;ground[i]=take
      if i==0:dva=(dva[0]*(1-c),dva[1]*(1-c))
      else:dvb=(dvb[0]*(1-c),dvb[1]*(1-c))
   sa=norm(*dva)/(A['shock_speed_mps']*(.5+a.a.balance));sb=norm(*dvb)/(A['shock_speed_mps']*(.5+b.a.balance))
   # Legal responsibility, from the approach witness at the instant of contact (revision 3). Three separate questions:
   #  kinematic - did his own motion carry him into the other? His approach speed along the line of centres, less whatever part
   #              of it other athletes' forces had put on him and he could not yet have taken off (c3_driven). Any such speed
   #              above zero is initiation: supplying the smaller part of the closing speed does not excuse him.
   #  material  - was the part of the hit that his own motion supplied worth adjudicating? The impulse is proportional to the
   #              closing speed, so his part of the other's balance shock is the shock times his share of the closing speed.
   #              It must reach contact_foul_min_shock. What the other athlete or a third one supplied is not his.
   #  legal     - the retained classification of his contact on the other.
   # He is penalised if all three go against him, unless the legal circumstances changed too late for him to stop (c3_no_time).
   cid=car.id if car is not None and car.id in(a.id,b.id)else None;lawful={};witness=[];floor=A['contact_foul_min_shock'];imposed=[]
   for p,q,u,felt,dv,sx,sy in((a,b,ua,sb,dva,ex,ey),(b,a,ub,sa,dvb,-ex,-ey)):
    kind='tackle'if cid==q.id else'block';legal,why=self.e.contact_legal(p,q,kind)
    fresh,(ox,oy,_,src)=self.c3_driven(p,now_ms);by=[]
    for e in fresh:
     ox+=e[1];oy+=e[2]
     if e[3]not in by:by.append(e[3])
    w=min(max(0.,u),max(0.,ox*sx+oy*sy));own=max(0.,u)-w;init=own>1e-9;share=min(1.,own/vn);material=felt*share>=floor
    lawful[p.id]=legal
    rec={'player':p.id,'on':q.id,'kind':kind,'own_approach_mps':round(u,3),'share_of_closing':round(u/vn,3),'driven_approach_mps':round(w,3),'voluntary_approach_mps':round(own,3),
         'own_part_of_shock':round(felt*share,4),'initiated':init,'material':material,'classification':why}
    if self.c3c:rec['bearing_from_facing_deg']=round(math.degrees(math.acos(clamp(-(sx*q.facing[0]+sy*q.facing[1])/max(1e-9,math.hypot(*q.facing)),-1.,1.))),2) #C3c: where he came from, 0 = head-on, 180 = directly behind; logged apart from initiation, materiality and avoidability
    if not legal and init and material:
     excused,seen=self.c3_no_time(p,q,why,now_ms);rec['avoidability']=seen
     if excused:rec['not_sanctioned']='no_time_to_avoid';self.stats['c3_unavoidable_contacts']+=1
     else:
      rec['foul']=why;self.stats['c3_contact_fouls']+=1;event=('foul',t)
      self.c3_events.append(Event('foul',p.id,q.id,{'reason':why,'major':why in('contact_speed','dangerous_surface','ineligible_contact'),'danger':why in('contact_speed','dangerous_surface','ineligible_contact')},at=self.c3_at(t)))
    elif not legal and w>0 and felt*min(1.,max(0.,u)/vn)>=floor:
     #his whole approach would have been a material unlawful hit; the part he did not choose is what takes it below that
     rec['not_sanctioned']='carried_by_another_contact';rec['driven_by']=sorted(set(by)|set(src));self.stats['c3_unavoidable_contacts']+=1
    elif legal and init and material and kind=='block':
     self.c3_blocks.append((p.id,q.id,int(now_ms)));self.c3_note(t,'engagement','6.1–6.4',actor=p.id,target=q.id,kind='block')
    if self.c3b and init and material:q.c3_hit=(now_ms,p.id) #the other athlete was materially run into by him at this time
    witness.append(rec);imposed.append((p,dv,1-share,q.id))
   #what this collision did to each athlete's velocity, less the share his own voluntary approach caused, is velocity imposed on him
   for p,dv,part,by in imposed:self.c3_push(p,dv[0]*part,dv[1]*part,by,now_ms)
   self.c3_add(a,('shock',b.id),sa,lawful[b.id],now_ms);self.c3_add(b,('shock',a.id),sb,lawful[a.id],now_ms)
   self.c3_note(t,'c3_collision',a=a.id,b=b.id,t_ms=round(now_ms,3),closing_mps=round(vn,3),impulse_Ns=round(J,1),dv_a=round(norm(*dva),3),dv_b=round(norm(*dvb),3),
                shock_a=round(sa,4),shock_b=round(sb,4),ground_impulse_a=round(ground[0],1),ground_impulse_b=round(ground[1],1),carrier=cid,responsibility=witness)
  #bodies do not overlap: any residual overlap is removed along the line of centres, lighter body moves more
  for a,b,R in pairs:
   if a.id in down or b.id in down:continue
   dx,dy=b.x-a.x,b.y-a.y;dist=norm(dx,dy)
   if dist<R-TOL:
    ex,ey=unit(dx,dy)
    if ex==ey==0:ex=1.
    over=R-dist;wa=b.a.mass/(a.a.mass+b.a.mass)
    a.x-=ex*over*wa;a.y-=ey*over*wa;b.x+=ex*over*(1-wa);b.y+=ey*over*(1-wa)
  # a shock is instantaneous: an athlete it unbalances goes down at this instant, not before. If several go down together the
  # carrier is classified first, while every hold that existed at that instant is still there: the result must not depend on
  # which team's athlete happens to be listed first
  fall=[p for p in group if p.id in hit and p.id not in down and self.c3_bal(p)>=1]
  fall.sort(key=lambda p:not(car is not None and p.id==car.id))
  for p in fall:
   self.c3_ground(p,car,self.c3_bal(p),t,now_ms,0.);event=('grounding',t)
  return event
 def c3_rate(self,p):
  #balance recovery rate, 1/s. A lower hold slows it: the legs cannot step freely.
  A=self.assume;leg=1.
  if p.id in self.c3_descent:return 0. #C3b: an athlete lowering himself to the ground is not recovering his balance
  for h in self.c3_holds.values():
   if h['target']==p.id and h['region']=='lower':leg=min(leg,1-A['lower_hold_leg_factor']*h['g'])
  return A['balance_recovery_per_s']*(.5+p.a.balance)*leg
 def c3_span(self,p,dt):
  #effective time over which a constant load rate accumulates in a substep, allowing for recovery during it
  r=self.c3_rate(p);return(1-math.exp(-r*dt))/r if r>0 else dt
 def c3_recover(self,p,dt):
  #Every contribution to balance load decays on its own at the athlete's recovery rate.
  if not getattr(p,'bal_src',None):return
  decay=math.exp(-self.c3_rate(p)*dt)
  for key in list(p.bal_src):
   p.bal_src[key]*=decay
   if p.bal_src[key]<1e-4:del p.bal_src[key]
  if not p.bal_src:p.bal_t0=None
 def c3_ground(self,p,car,B,te,now_ms,back):
  """A physical grounding at kernel time te. Whether it is a counted tackle is a separate question: the carrier must be in
  control, and there must be a lawful defensive engagement or cause present at this instant - a hold at or above the grip
  threshold, or opponents in lawful contact with him now having supplied the stated majority of the balance load. Everything a
  defender in current lawful contact lawfully supplied counts together: his shocks and his hold. A brush, a stale grip, load
  from someone no longer in contact, or unlawful load cannot make a tackle. A hold exists only while it is within reach and
  lawful, so a hold listed here is in contact at this instant by construction."""
  s=self.s;A=self.assume;self.c3_down.add(p.id);at=self.c3_at(te);scale=A['body_radius_scale']
  src={'%s:%s:%s'%(k[0],k[1],'lawful'if k[2]else'unlawful'):round(v,4)for k,v in sorted(p.bal_src.items(),key=str)}
  info={'player':p.id,'t_ms':round(now_ms,3),'balance_load':round(B,4),'sources':src,'episode_ms':round(now_ms-(p.bal_t0 if p.bal_t0 is not None else now_ms),1)}
  if car is not None and p.id==car.id and not self.c3_lost:
   holds=sorted(((h,s.players[h['actor']])for h in self.c3_holds.values()if h['target']==p.id),key=lambda hd:hd[1].id)
   strong=[(h,d_)for h,d_ in holds if h['g']>=A['tackle_grip_threshold']];supplied={}
   for(kind,q,ok),v in p.bal_src.items():
    if ok and kind in('hold','shock')and q in s.players and s.players[q].team!=p.team:supplied[q]=supplied.get(q,0.)+v
   touching={d_.id for h,d_ in holds}
   for q in supplied:
    if q in touching:continue
    #body contact at this instant (positions taken back to it along the last drift), and lawful
    o=s.players[q];pre=self.c3_pre;ox,oy,px_,py_=o.x,o.y,p.x,p.y
    if back>0 and q in pre and p.id in pre:
     ox,oy=o.x-pre[q][3]*back,o.y-pre[q][4]*back;px_,py_=p.x-pre[p.id][3]*back,p.y-pre[p.id][4]*back
    if norm(ox-px_,oy-py_)-(o.radius+p.radius)*scale<=1e-3 and self.e.contact_legal(o,p,'tackle')[0]:touching.add(q)
   #only load supplied by opponents who are in lawful contact with him NOW counts towards the majority; load left by someone who has gone does not
   share=sum(v for q,v in supplied.items()if q in touching)/B if B>0 else 0.
   cls=None
   if strong:cls='tackle_under_hold';credit=max(strong,key=lambda hd:(supplied.get(hd[1].id,0.),hd[0]['g'],hd[1].id))[1].id
   elif share>=A['tackle_source_majority']and any(q in touching for q in supplied):
    cand=[q for q in supplied if q in touching];cls='tackle_by_lawful_contact';credit=max(cand,key=lambda q:(supplied[q],q))
   info.update(holders=[{'player':d_.id,'grip':round(h['g'],4),'region':h['region']}for h,d_ in holds],in_lawful_contact=sorted(touching),
               lawful_supplied={q:round(v,4)for q,v in sorted(supplied.items())},lawful_defensive_share=round(share,4))
   if self.c3b:
    des=self.c3_descent.get(p.id);own=p.bal_src.get(('descent',p.id,True),0.)
    manner=('carrier_descent_under_hold'if des is not None else'defence_driven')if cls else'unassisted_grounding' #a descent attempt exists only under a material hold, so a grounding that is not a counted tackle is unassisted, whatever part of the load was his own
    info.update(manner=manner,descent_attempted=des is not None,own_descent_load=round(own,4),containing=[d_.id for h,d_ in holds if h.get('mode')=='contain'])
    self.stats['c3_'+manner]+=1
    if des is not None:self.c3_descent_end(p.id,'grounded',now_ms,te)
   if cls:
    info.update(cls=cls,credited=credit);self.stats['c3_'+cls]+=1
    self.c3_events.append(Event('tackle',credit,p.id,{'control_witness':s.ball.version,'c3':info},at=at))
   else:
    info.update(cls='carrier_grounded_not_a_tackle');self.stats['c3_carrier_grounded_not_a_tackle']+=1
    self.c3_events.append(Event('ground',p.id,None,{'c3':info},at=at))
   self.c3_lost='carrier_grounded'
   for key in list(self.c3_holds):
    if key[1]==p.id:self.c3_end_hold(key,'carrier_grounded',now_ms,te)
  else:
   info.update(cls='non_carrier_grounded');self.stats['c3_non_carrier_grounded']+=1
   self.c3_events.append(Event('ground',p.id,None,{'c3':info},at=at))
   for key in list(self.c3_holds):
    if key[0]==p.id:self.c3_end_hold(key,'holder_grounded',now_ms,te)
  p.bal_src={};p.bal_t0=None
 def player_contacts(self,ms,old_positions=None):
  s=self.s
  if self.c3:
   #C3a: contact was resolved with the motion (c3_move). Hand over its timed events; nothing is decided here.
   ev=self.c3_events;self.c3_events=[];return ev
  if s.phase not in(Phase.LIVE,Phase.PENALTY):return[]
  events=[];dt=ms/1000;players=[p for p in self.active_field()if self.e.eligible(p)and p.posture=='upright']
  carrier=s.players.get(s.ball.carrier)
  for i,original_a in enumerate(players):
   for original_b in players[i+1:]:
    a,b=original_a,original_b
    if a.team==b.team:continue
    dist=norm(a.x-b.x,a.y-b.y);bodydist=(a.radius+b.radius)*self.assume['body_radius_scale'];close=bodydist+.65
    if dist>close:
     if old_positions and a.id in old_positions and b.id in old_positions:
      ao,bo=old_positions[a.id],old_positions[b.id];sx,sy=ao[0]-bo[0],ao[1]-bo[1]
      swept,frac=segment_distance(0,0,sx,sy,a.x-b.x,a.y-b.y)
      if swept<bodydist and(max(a.speed,b.speed)>12 or norm(a.vx-b.vx,a.vy-b.vy)>8):
       actor,victim=(a,b)if a.speed>=b.speed else(b,a)
       events.append(Event('foul',actor.id,victim.id,{'reason':'contact_speed','major':True,'danger':True},at=int(ms*frac)))
     continue
    key=tuple(sorted((a.id,b.id)))
    if s.now<self.contact_cooldown.get(key,-1):continue
    target=carrier if carrier and carrier.id in(a.id,b.id)else None;actor=(b if a==target else a)if target else a
    if target:
     legal,reason=self.e.contact_legal(actor,target,'tackle')
     if not legal:
      if reason=='contact_speed'and dist<bodydist:
       culprit=actor if actor.speed>=target.speed else target
       events.append(Event('foul',culprit.id, target.id if culprit.id==actor.id else actor.id,{'reason':'contact_speed','major':True,'danger':True}))
       self.contact_cooldown[key]=s.now+1500
      continue
     if not self.e.engage(actor.id,target.id,'tackle',sanction=False):continue
     en=s.engagements[(actor.id,target.id,'tackle')]
     ratio=(actor.a.strength*math.sqrt(actor.a.mass/220)+actor.a.tackling)/(target.a.strength*.5+target.a.balance+target.a.contact_resistance+.1)
     angle=(actor.x-target.x)*s.attack_sign(target.team)
     leverage=1.1 if angle>0 else.8
     actor.target=(target.x,target.y);actor.next_decision=s.now+250
     en.progress+=dt*self.assume['tackle_rate']*ratio*leverage*(.6+.4*actor.fatigue)
     target.vx*=max(.2,1-dt*2.5*ratio);target.vy*=max(.2,1-dt*2.5*ratio)
     actor.vx=target.vx;actor.vy=target.vy
     # A legal retained wrap closes distance; modeled grip is breakable by leverage and release.
     ux,uy=unit(target.x-actor.x,target.y-actor.y)
     actor.x=target.x-ux*(bodydist+.2);actor.y=target.y-uy*(bodydist+.2)
     self.stats['carrier_engagement_ms']+=ms
     if self.rng['contact'].random()<dt*.12*actor.a.tackling*(1-target.a.ball_handling*.6):events.append(Event('strip',actor.id,target.id,{'control_witness':s.ball.version}));self.contact_cooldown[key]=s.now+800
     elif en.progress>=1:events.append(Event('tackle',actor.id,target.id,{'control_witness':s.ball.version}));self.contact_cooldown[key]=s.now+1200
    else:
     legal,reason=self.e.contact_legal(a,b,'block')
     if not legal:
      legal2,_=self.e.contact_legal(b,a,'block')
      if legal2:a,b=b,a;legal=True
     if not legal:continue
     self.e.engage(a.id,b.id,'block',sanction=False)
     force_a=a.a.strength*a.a.blocking*math.sqrt(a.a.mass/220)*(.5+.5*a.fatigue)
     force_b=b.a.strength*b.a.blocking*math.sqrt(b.a.mass/220)*(.5+.5*b.fatigue)
     ex,ey=unit(b.x-a.x,b.y-a.y);push=clamp((force_a-force_b)*self.assume['block_force']*dt,-.35,.35)
     b.x+=ex*push;b.y+=ey*push;a.x+=ex*push;a.y+=ey*push
     overlap=max(0,bodydist-dist)
     a.x-=ex*overlap*.5;a.y-=ey*overlap*.5;b.x+=ex*overlap*.5;b.y+=ey*overlap*.5
     a.vx*=.72;a.vy*=.72;b.vx*=.72;b.vy*=.72
     self.stats['blocking_ms']+=ms
  #An engagement loses its hold when participants actually separate or eligibility changes.
  s.engagements={k:en for k,en in s.engagements.items()if s.players[k[0]].eligible(s.now)and s.players[k[1]].eligible(s.now)and norm(s.players[k[0]].x-s.players[k[1]].x,s.players[k[0]].y-s.players[k[1]].y)<4}
  return events
 def advance_ball(self,ms,old_positions):
  s=self.s;b=s.ball;dt=ms/1000;events=[]
  if s.phase not in(Phase.LIVE,Phase.OPENING,Phase.AWARD,Phase.FLIGHT,Phase.PENALTY):return events
  old=(b.x,b.y,b.z);generation=b.version
  if b.carrier:
   self.e.follow_carrier();p=s.players[b.carrier]
   if p.posture!='airborne'and not(0<=p.x<=100 and 0<=p.y<=100):events.append(Event('boundary',p.id,data={'x':p.x,'y':p.y},at=ms))
  elif b.mode!=BallMode.CONTESTED and s.phase!=Phase.AWARD:
   drag=math.exp(-self.assume['ball_drag']*dt);b.x+=b.vx*dt;b.y+=b.vy*dt;b.z+=b.vz*dt-.5*self.assume['gravity']*dt*dt;b.vx*=drag;b.vy*=drag;b.vz=(b.vz-self.assume['gravity']*dt)*drag
   if b.z<=b.radius:
    if s.phase==Phase.FLIGHT or s.phase==Phase.PENALTY and s.penalty.get('released'):
     events.append(Event('ground',None,data={'ball_ground':True}));b.z=b.radius
    else:
     b.z=b.radius
     if abs(b.vz)>2:b.vz=-b.vz*self.assume['ball_restitution'];b.vx*=.76;b.vy*=.76
     else:b.vz=0;b.vx*=max(0,1-dt*3);b.vy*=max(0,1-dt*3)
     b.mode=BallMode.LOOSE
  #Interpolate complete-ball boundary crossings before later catches.
  cuts=[]
  for axis,limit in((0,-b.radius),(0,100+b.radius),(1,-b.radius),(1,100+b.radius)):
   now=(b.x,b.y,b.z)
   if (old[axis]-limit)*(now[axis]-limit)<=0 and abs(now[axis]-old[axis])>1e-9:
    frac=(limit-old[axis])/(now[axis]-old[axis])
    outward=(limit<0 and now[axis]<old[axis])or(limit>100 and now[axis]>old[axis])
    if outward:cuts.append((frac,axis,limit))
  if cuts:
   frac,axis,limit=min(cuts);yy=old[1]+(b.y-old[1])*frac;zz=old[2]+(b.z-old[2])*frac
   if axis==0 and legal_goal(yy,zz):
    defending=next(t for t in('A','B')if s.ends[t]==(0 if limit<0 else 100));events.append(Event('goal',data={'defending':defending,'y':yy,'z':zz},at=int(frac*ms)))
   elif axis==0 and b.carrier is None and zz>=0 and 6-b.radius<=norm(yy-50,zz)<=6+self.assume['frame_thickness']+b.radius:
    gx=0 if limit<0 else 100;point=(gx+(.25 if gx==0 else-.25),yy,max(b.radius,zz))
    events.append(Event('frame',data={'velocity':(-b.vx*.6,b.vy*.8,b.vz*.8),'point':point},at=int(frac*ms)))
   else:events.append(Event('boundary',data={'x':old[0]+(b.x-old[0])*frac,'y':yy},at=int(frac*ms)))
  elif b.x<-b.radius or b.x>100+b.radius or b.y<-b.radius or b.y>100+b.radius:
   events.append(Event('boundary',data={'x':b.x,'y':b.y},at=0))
  if b.carrier is not None or b.mode==BallMode.CONTESTED:
   for ev in events:ev.data['generation']=generation
   return events
  if self.assume['c1_catch_model']:
   #Observation of a flight starts when its course last changed: at the release, at a committed deflection, or at a bounce.
   if b.version!=self.seen_version:
    marks=[t for t in(b.release_time,getattr(b,'course_time',-1))if self.seen_from<t<=s.now]
    self.seen_version=b.version;self.seen_from=max(marks)if marks else s.now;self.hands_set={};self.bounce_mark=None
   if self.bounce_mark is not None and s.now>=self.bounce_mark:self.seen_from=max(self.seen_from,self.bounce_mark);self.hands_set={};self.bounce_mark=None
   if b.carrier is None and b.mode==BallMode.LOOSE and b.z<=b.radius+1e-9 and b.vz>0 and old[2]>b.radius+1e-9:self.bounce_mark=s.now+ms
  elif b.version!=self.seen_version:self.seen_version=b.version;self.seen_from=s.now
  if self.assume['c1_catch_model']:
   for ev in self.catch_contacts(old,ms,old_positions):events.append(ev)
   for ev in events:ev.data['generation']=generation
   return events
  candidates=[]
  for p in self.active_field():
   if not self.e.eligible(p)or p.posture=='grounded' or s.now<p.next_action:continue
   if s.phase==Phase.OPENING and not s.opening_touched and p.id not in s.opening_contestants:continue
   if s.phase==Phase.AWARD and p.team!=s.owner:continue
   if b.last_releaser==p.id:continue
   hand=(p.x,p.y,p.hand_height);dd,frac=segment3_distance(hand,old,(b.x,b.y,b.z));horizontal,_=segment_distance(p.x,p.y,*old[:2],b.x,b.y)
   reach=p.a.reach*(1.1 if p.role=='keeper'else.9)
   #A standing scoop is permitted near the surface; a catch requires an actual reachable swept path.
   reachable=dd<reach or(b.z<.4 and horizontal<p.radius+.65)
   if not reachable:continue
   rel=math.sqrt((b.vx-p.vx)**2+(b.vy-p.vy)**2+b.vz*b.vz)
   quality=p.a.keeper_skill if p.role=='keeper'else p.a.catching
   probability=clamp(.30+.65*quality-.007*max(0,rel-15)+.08*(p.a.awareness-.5),.12,.98)
   if b.z<.4 and norm(b.vx,b.vy)<3:probability=clamp(.8+.18*p.a.ball_handling,.8,.98)
   if self.rng['ball'].random()<probability:candidates.append((frac,p))
   elif p.role=='keeper':
    #A failed secure catch can still be a physical block. It cannot reset ownership.
    velocity=(-b.vx*.45,b.vy+self.rng['ball'].uniform(-5,5),max(2,abs(b.vz)*.3))
    point=[old[j]+((b.x,b.y,b.z)[j]-old[j])*frac for j in range(3)]
    events.append(Event('touch',p.id,data={'deliberate':True,'velocity':velocity,'ball_point':point},at=int(frac*ms)));self.stats['keeper_blocks']+=1;p.next_action=s.now+200
  if candidates:
   candidates.sort(key=lambda x:(x[0],x[1].id));first=candidates[0][0]
   for frac,p in candidates:
    if abs(frac-first)*ms<=10:
     point=[old[j]+((b.x,b.y,b.z)[j]-old[j])*frac for j in range(3)]
     events.append(Event('acquire',p.id,data={'ball_point':point},at=int(first*ms)))
  for ev in events:ev.data['generation']=generation
  return events
 def catch_contacts(self,old,ms,old_positions=None):
  """C1 catch model, revision 2. Four separate questions:
   1. Reach. The ball and the player's hands are swept together through the step. The ball is reachable
      while their separation is under the reach (or, for a low ball, while it is within scooping distance).
      Being reachable does nothing by itself.
   2. Hands set. A player gets his hands to a reachable ball only once he has read its course:
        P(set by time t) = 1 - exp(-(t - t_obs) / tau),  tau = catch_reaction_s x (1.3 - 0.6 x awareness)
      t_obs is when the ball last changed course (release, committed deflection, bounce); the intended
      receiver's clock starts when the passer began preparing (at most 0.5 s earlier). Only elapsed time
      counts, and it counts whether or not the ball is yet reachable. A player with no record for this
      flight is sampled from t_obs; a player whose earlier sample failed is sampled only from that instant on.
      If the hands are never set while the ball is reachable, the ball passes untouched.
   3. Contact. A set player meets the ball at its closest approach to his hands, or as soon as he is set
      if that moment has already passed. This is the event time and the event point.
   4. Secure control. E = 1/2 x ball_mass x relative_speed^2 against
        capacity = catch_arrest_force_N x catch_hand_travel_m x (0.4 + 0.9 x skill) x (1 - (miss/reach)^2)
        P(secure) = 1 / (1 + (E/capacity)^2)
      An established contact that is not secured deflects the ball (a Keeper's is a parry).
  Only the earliest contact in the step is proposed, at its own time and point. Two secure contacts at
  different instants are treated as simultaneous only if they fall in the same millisecond of the match clock.
  When contacts coincide exactly because they share a threshold instant, the nearest hand is first;
  equally near hands are a genuine tie.
  This function proposes events. It changes no cooldown and counts no block: those belong to the
  handler of a committed event. The one thing it records is which players have set their hands."""
  s=self.s;b=s.ball;A=self.assume;now=(b.x,b.y,b.z);dt=ms/1000;cands=[]
  db=tuple(now[j]-old[j]for j in range(3))
  def window(r0,dr,R,dims):
   #Interval of the step, as fractions, in which |r0+f*dr|<R; and the fraction of closest approach (may exceed 1).
   a=sum(dr[j]*dr[j]for j in range(dims));c=sum(r0[j]*r0[j]for j in range(dims))-R*R
   if a<1e-12:return(0.,1.,0.)if c<0 else None
   h=sum(r0[j]*dr[j]for j in range(dims));disc=h*h-a*c
   if disc<=0:return None
   q=math.sqrt(disc);f1,f2=(-h-q)/a,(-h+q)/a
   if f2<=0 or f1>=1:return None
   return(f1,f2,-h/a)
  self.c4c_cinfo={};bodies=self.c4c_body(old,db,ms,old_positions)if self.c4c else[];fbm={c[2]:c[0]for c in bodies} #C4c: where the ball would meet a Keeper's body
  for p in self.active_field():
   if not p.eligible(s.now)or p.posture=='grounded':continue
   if s.penalty is not None and p.id not in(s.penalty['runner'],s.penalty['keeper']):continue
   if s.phase==Phase.FLIGHT and p.team==s.tail_owner:continue
   if s.phase==Phase.OPENING and not s.opening_touched and p.id not in s.opening_contestants:continue
   if s.phase==Phase.AWARD and p.team!=s.owner:continue
   if b.last_releaser==p.id:continue
   o=old_positions.get(p.id)if old_positions else None
   if o is None:o=(p.x,p.y,p.z)
   lift=p.hand_height-p.z;h0=(o[0],o[1],o[2]+lift);h1=(p.x,p.y,p.hand_height)
   if self.c4c and getattr(p,'c4c_launch',None):off=p.c4c_launch['off'];h0=(o[0]+off[0],o[1]+off[1],o[2]+off[2]);h1=(p.x+off[0],p.y+off[1],p.z+off[2]) #C4c: hands out along the dive
   r0=tuple(old[j]-h0[j]for j in range(3));dr=tuple(db[j]-(h1[j]-h0[j])for j in range(3))
   reach=p.a.reach*(1.1 if p.role=='keeper'else.9);R=reach;dims=3
   w=window(r0,dr,reach,3)
   if w is None:
    #A low ball can be scooped: horizontal distance only, and only while the ball is below 0.4 m.
    R=p.radius+.65;dims=2;w=window(r0,dr,R,2)
    if w is None:continue
    f1,f2,fc=w
    if abs(db[2])>1e-12:
     fz=(.4-old[2])/db[2]
     if db[2]<0:f1=max(f1,fz)
     else:f2=min(f2,fz)
    elif old[2]>=.4:continue
    if f2<=f1:continue
    w=(f1,f2,fc)
   f1,f2,fc=w;entered=f1>0;lo=max(0.,f1);hi=min(1.,f2)
   busy=(p.next_action-s.now)/ms
   if busy>lo:lo=busy;entered=False
   if lo>=hi:continue
   kr=None
   if self.c4c and p.role=='keeper':
    #C4c: a Keeper's hands are set by the catch model's sampled readiness (the reflex every player has) or at his reaction instant
    #(c4c_keepers: he has read the flight and is playing it), whichever is earlier
    seen=getattr(p,'c4c_seen',None)
    if seen is not None and seen[0]==b.version:kr=(seen[2]-s.now)/ms
    if kr is not None and kr<=lo:self.hands_set[p.id]=True
   tau=A['catch_reaction_s']*(1.3-.6*p.a.awareness);fset=lo;state=self.hands_set.get(p.id)
   if state is not True and tau>1e-9:
    #Readiness follows elapsed observation, whether or not the ball is reachable, and is sampled only when needed:
    #from the start of this player's observation the first time (state None), and from the last sampled instant
    #after a failed sample (state is that instant). A failed sample is never drawn again.
    upto=s.now+hi*ms
    if state is None:
     state=self.seen_from
     if b.intended==p.id and self.pass_signal[0]==p.id and b.release_time>=self.pass_signal[1]:state-=min(500,b.release_time-self.pass_signal[1])
    span=(upto-state)/1000
    if span<=0:
     self.hands_set[p.id]=state
     if kr is None or kr>=hi:continue
     fset=max(lo,kr)
    else:
     u=self.rng['ball'].random()
     if u>=1-math.exp(-span/tau):
      self.hands_set[p.id]=upto
      if kr is None or kr>=hi:continue
      fset=max(lo,kr)
     else:
      fset=max(lo,(state-1000*tau*math.log(1-u)-s.now)/ms)
      if kr is not None:fset=min(fset,max(lo,kr))
   self.hands_set[p.id]=True
   fcon=max(fset,min(fc,hi))
   if fc>1 and hi>=1 and fset<1 and p.id not in fbm:continue #set, and the ball is still closing at the end of the step: he waits for it
   if p.id in fbm:fcon=max(lo,fset,min(fcon,fbm[p.id]-1e-9)) #C4c: his hands meet the ball no later than it would reach his body (just before)
   if self.c4c and p.role=='keeper'and fcon>fc+1e-9 and dt>0 and math.sqrt(sum(c*c for c in dr))/dt>5.:continue #C4c: a fast ball (above 5 m/s relative to his hands) that has passed its nearest point to them before they are set: it is gone
   if fcon>1:continue
   if p.posture!='airborne':
    cx,cy=o[0]+(p.x-o[0])*fcon,o[1]+(p.y-o[1])*fcon
    if not(0<=cx<=100 and 0<=cy<=100):continue #outside the field at the moment of contact: he does not play the ball
   gap=math.sqrt(sum((r0[j]+fcon*dr[j])**2 for j in range(dims)));miss=min(1.,gap/R)
   pv=((p.x-o[0])/dt,(p.y-o[1])/dt,(p.z-o[2])/dt)if dt>0 else(p.vx,p.vy,0.)
   rel=math.sqrt(sum((dr[j]/dt)**2 for j in range(3)))if dt>0 else 0.
   skill=p.a.keeper_skill if p.role=='keeper'else p.a.catching
   capacity=A['catch_arrest_force_N']*A['catch_hand_travel_m']*(.4+.9*skill)*max(0.,1-miss*miss)
   energy=.5*A['ball_mass_kg']*rel*rel
   secure=1/(1+(energy/capacity)**2)if capacity>1e-9 else 0.
   if self.c4c and p.role=='keeper':
    r=[r0[j]+fcon*dr[j]for j in range(3)];k=math.sqrt(sum(c*c for c in r))
    self.c4c_cinfo[(p.id,'hands')]=([c/k for c in r]if k>1e-9 else None,pv,round(secure,4))
   cands.append((fcon,gap,p.id,p,self.rng['ball'].random()<secure,pv))
  cands+=bodies #C4c: the Keeper's body stops a ball that meets it (ok is None: a block)
  if not cands:return[]
  cands.sort(key=lambda c:c[:3]);self.stats['contacts_proposed']+=1
  point=lambda f:[old[j]+db[j]*f for j in range(3)]
  f,near,_,p,ok,pv=cands[0];at=int(f*ms)
  if ok:
   #Earliest secure contact takes the ball. Another secure contact at a different instant in the same clock millisecond
   #cannot be ordered: both are reported. Contacts at exactly the same instant share a threshold (the ball dropping to
   #scooping height, players becoming eligible together): there the nearest hand is first and the others are not reported,
   #unless they are equally near, which is a genuine tie.
   return[Event('acquire',q.id,data={'ball_point':point(g),'c1_contact':True,**({'c4c_kind':'catch'}if self.c4c and q.role=='keeper'else{})},at=at)for g,w,_,q,good,_ in cands if good and int(g*ms)==at and(q is p or g!=f or abs(w-near)<1e-9)]
  if self.c4c and p.role=='keeper':
   #C4c: a Keeper's unsecured contact is a physical rebound off the hands (a parry) or off his body (a block): the ball's velocity
   #relative to them loses (1 + e) of its component along the contact normal; nothing else is changed and nothing is random. In a
   #deliberate parry the hand also moves into the ball along the normal at keeper_parry_swing_mps.
   body=ok is None;n,hv,sec=self.c4c_cinfo[(p.id,'body'if body else'hands')];e=A['keeper_body_restitution'if body else'keeper_parry_restitution']
   #a parry is a deliberate play once he has read the flight (his reaction instant); a reflex touch before then is incidental, like
   #any other player's unsecured touch, and the shot keeps its origin. A body block is always incidental.
   seen=getattr(p,'c4c_seen',None);read=seen is not None and seen[0]==b.version and seen[2]<=s.now+f*ms+1e-9
   rv0=[(b.vx,b.vy,b.vz)[j]-hv[j]for j in range(3)]
   if n is None:k=math.sqrt(sum(c*c for c in rv0))or 1.;n=[-c/k for c in rv0]
   if read and not body:hv=[hv[j]+A['keeper_parry_swing_mps']*n[j]for j in range(3)] #a deliberate parry: the hand is driven into the ball
   rv=[(b.vx,b.vy,b.vz)[j]-hv[j]for j in range(3)];vn=sum(rv[j]*n[j]for j in range(3))
   if vn<0:rv=[rv[j]-(1+e)*vn*n[j]for j in range(3)]
   velocity=tuple(hv[j]+rv[j]for j in range(3))
   return[Event('touch',p.id,data={'deliberate':(not body)and read,'c4c_read':read,'c4c_vin':[round(c,4)for c in(b.vx,b.vy,b.vz)],'c4c_hand_v':[round(c,4)for c in hv],'velocity':velocity,'ball_point':point(f),'c1_contact':True,'cooldown_ms':0 if body else 200,'keeper_block':not body,'c4c_kind':'body'if body else'parry','c4c_normal':[round(c,4)for c in n],'c4c_secure_p':sec},at=at)]
  if p.role=='keeper':
   velocity=(-b.vx*.45,b.vy+self.rng['ball'].uniform(-5,5),max(2,abs(b.vz)*.3));deliberate=True
  else:
   #An unsecured contact: the ball keeps a fraction of its speed relative to the hands and is knocked off line.
   keep=A['deflection_speed_kept'];turn=self.rng['ball'].uniform(-1.05,1.05);rx,ry=b.vx-pv[0],b.vy-pv[1]
   c,sn=math.cos(turn),math.sin(turn)
   velocity=(pv[0]+keep*(rx*c-ry*sn),pv[1]+keep*(rx*sn+ry*c),abs(b.vz)*.3+self.rng['ball'].uniform(0,2));deliberate=False
  return[Event('touch',p.id,data={'deliberate':deliberate,'velocity':velocity,'ball_point':point(f),'c1_contact':True,'cooldown_ms':200,'keeper_block':p.role=='keeper'},at=at)]
 def fly_on(self,ms,end_positions):
  """C1: the rest of a step after the ball's course changed inside it. This is advance_ball over the remaining
  interval: the same flight rules, the same boundary, goal, frame and ground events, and the same contact kernel,
  in every phase in which advance_ball moves the ball. Events carry their own times and the new ball generation."""
  s=self.s;b=s.ball
  if ms<=0 or b.carrier is not None:return[]
  here={p.id:(p.x,p.y,p.z)for p in self.active_field()}
  for pid,new in end_positions.items():
   p=s.players[pid]
   if p.posture!='grounded':p.x,p.y,p.z=new
  events=self.advance_ball(ms,here)
  for pid,pos in here.items():s.players[pid].x,s.players[pid].y,s.players[pid].z=pos
  return events
 def advance_arrows(self,ms):
  s=self.s;events=[];dt=ms/1000;g=self.assume['gravity']
  for ar in s.arrows:
   if not ar.live:continue
   old=(ar.x,ar.y,ar.z);drag=math.exp(-self.assume['arrow_drag']*dt)
   ar.x+=ar.vx*dt;ar.y+=ar.vy*dt;ar.z+=ar.vz*dt-.5*g*dt*dt;ar.vx*=drag;ar.vy*=drag;ar.vz=(ar.vz-g*dt)*drag
   contacts=[]
   for p in self.active_field():
    if not p.active:continue
    distance2,f=segment_distance(p.x,p.y,*old[:2],ar.x,ar.y)
    z=old[2]+(ar.z-old[2])*f
    if distance2<p.radius+.045 and p.z+.12*p.a.height<=z<=p.z+p.a.height:
     panel=p.z+.2*p.a.height<=z<=p.z+.8*p.a.height
     contacts.append((f,p.id,panel))
   b=s.ball
   if b.carrier is None:
    dd,ff=segment3_distance((b.x,b.y,b.z),old,(ar.x,ar.y,ar.z))
    if dd<b.radius+.045:contacts.append((ff,'ball',False))
   if contacts:
    frac,target,panel=min(contacts,key=lambda t:t[0]);ar.x=old[0]+(ar.x-old[0])*frac;ar.y=old[1]+(ar.y-old[1])*frac;ar.z=old[2]+(ar.z-old[2])*frac
    # Ball velocity changes only when the chronologically ordered impact is applied.
    events.append(Event('impact',target=target,data={'arrow':ar.id,'panel':panel,'kind':'ball'if target=='ball'else'player'},at=int(frac*ms)))
    self.e.emit('arrow_geometry_impact','assumption:swept_body_collision',arrow=ar.id,target=target,panel=panel,blocked=target!=ar.target)
   elif ar.z<=0 or not(-30<=ar.x<=130 and-40<=ar.y<=140):
    ar.live=False;self.e.emit('arrow_miss','3.9;assumption:trajectory',arrow=ar.id,position=[ar.x,ar.y,max(0,ar.z)])
  return events
 def penalty_targets(self):
  s=self.s;pen=s.penalty;r=s.players[pen['runner']];k=s.players[pen['keeper']];sgn=s.attack_sign(r.team)
  targety=50+(3.8 if k.y<=50 else-3.8)
  return{r.id:(s.attack_goal(r.team)-sgn*.2,targety),k.id:(clamp(r.x+sgn*2,0,100),r.y)}
 def update_keepers_jump(self):
  s=self.s;b=s.ball
  if b.carrier is not None:return
  for p in self.active_field():
   if p.role!='keeper'or not self.e.eligible(p)or p.posture!='upright':continue
   if norm(b.x-p.x,b.y-p.y)<14 and b.z>p.hand_height+p.a.reach*.65:
    p.vz=math.sqrt(2*self.assume['gravity']*p.a.jump_height);p.posture='airborne';self.stats['keeper_jumps']+=1
 def auto_substitutions(self):
  s=self.s
  if s.phase not in(Phase.LIVE,Phase.DEAD,Phase.AWARD):return
  for team in('A','B'):
   low=s.ends[team]==0;gatex,gatey=(75,0)if low else(25,100)
   bench=[p for p in s.players.values()if p.team==team and not p.active and p.available and not p.injured and not p.disqualified and p.exclusion_ms<=0]
   debt=sum(d['permanent']or d['remaining']>0 for d in self.e.debts if d['team']==team)
   activefield=[p for p in s.players.values()if p.team==team and p.active and p.role=='field']
   if len(activefield)<10-debt and bench:
    p=max(bench,key=lambda p:p.fatigue);p.role='field';p.x=gatex;p.y=.1 if low else 99.9;p.active=True;self.e.slot_fill(p);self.e.emit('slot_return','14.3;15.4',player=p.id)
   if team not in self.pending_sub:
    choices=[p for p in activefield if s.ball.carrier!=p.id and p.fatigue<.55 and not p.frozen(s.now)]
    if choices and bench:
     o=min(choices,key=lambda p:p.fatigue);n=max(bench,key=lambda p:p.fatigue)
     if n.fatigue>o.fatigue+.18:self.pending_sub[team]=(o.id,n.id);self.e.emit('substitution_requested','assumption:rotation_policy',out=o.id,incoming=n.id)
   if team in self.pending_sub:
    oi,ni=self.pending_sub[team];o,n=s.players[oi],s.players[ni]
    if not o.active or not n.available or(n.active and self.e.c2_any):self.pending_sub.pop(team);continue #C2: legacy defect. A pending substitute who has meanwhile been activated was still walked to the gate every step
    o.target=(gatex,-o.radius-.2 if low else 100+o.radius+.2);o.next_decision=s.now+1000
    #Bench transit in the controlled corridor, with finite travel speed.
    ux,uy=unit(gatex-n.x,gatey-n.y);step=min(norm(gatex-n.x,gatey-n.y),(self.step_ms if self.c3b else self.dt)/1000*8);n.x+=ux*step;n.y+=uy*step #C3b: bench transit covers 8 m/s x the time actually elapsed, so short event intervals do not speed it up
    if self.e.sub(oi,ni):self.pending_sub.pop(team)
 def process_events(self,events,start,ms,old_positions=None):
  s=self.s
  #Geometry supplies substep fractions. No event is silently moved before another known timestamp.
  timed=defaultdict(list)
  for ev in events:
   offset=ms if ev.at is None else clamp(ev.at,0,ms)
   timed[start+int(offset)].append(ev)
  end=start+ms
  end_positions={p.id:(p.x,p.y,p.z)for p in self.active_field()}
  order=sorted(timed)
  while order:
   at=order.pop(0)
   if at<s.now:continue
   if old_positions:
    f=(at-start)/max(1,ms)
    for pid,old in old_positions.items():
     p=s.players[pid];new=end_positions.get(pid,old);p.x,p.y,p.z=tuple(old[j]+(new[j]-old[j])*f for j in range(3))
   self.e.elapse(at-s.now,resolve=False)
   group=timed.pop(at);mark=len(self.e.log)
   #Ball-ground is a physical terminal event, not grounding a nonexistent player.
   ground=[e for e in group if e.kind=='ground'and e.data.get('ball_ground')]
   group=[e for e in group if e not in ground]
   if self.assume['c1_catch_model']:ground=[e for e in ground if e.data.get('generation',s.ball.version)==s.ball.version] #a ground contact predicted for a flight that has since been deflected did not happen
   if group:self.e.batch(group)
   if ground:
    if s.phase==Phase.FLIGHT:self.e.end_flight('ground',s.ball.x,s.ball.y)
    elif s.phase==Phase.PENALTY and s.penalty.get('released'):self.e.finish_penalty(0)
   self.e.resolve_timers()
   if s.phase==Phase.FINAL:return #C4.0: the result is committed; the rest of the step is not played out
   if self.c3:self.c3_reconcile() #C3a: a hold ends at the committed event that ends its entitlement, at that event's time
   if self.assume['c1_catch_model']and(getattr(s.ball,'resume',False)or any(r['event']=='frame_contact'for r in self.e.log[mark:])):
    #C1: the ball's course changed inside the step (a committed deflection or a frame rebound). The rest of the
    #step is resolved now: flight, boundary, goal and frame crossings, ground contact and further catches, each at its own time.
    s.ball.resume=False
    if old_positions and at<end:
     for ev in self.fly_on(end-at,end_positions):
      k=at+(end-at if ev.at is None else int(ev.at));timed[k].append(ev)
      if k not in order:order.append(k);order.sort()
  if old_positions:
   for pid,new in end_positions.items():
    p=s.players[pid]
    if p.posture!='grounded':p.x,p.y,p.z=new
  if s.now<end:self.e.elapse(end-s.now)
  self.e.assert_invariants()
 def step(self):
  s=self.s
  if s.phase==Phase.FINAL:return
  self.e.resolve_timers()
  if s.phase==Phase.FINAL:return
  start=s.now;deadline=self.e.next_deadline()
  action_deadlines=[x[0]for x in self.pending_ball_actions.values()]+[x[0]for x in self.pending_draw.values()]
  if action_deadlines:deadline=min(deadline,min(x for x in action_deadlines if x>s.now)if any(x>s.now for x in action_deadlines)else s.now+self.dt)
  ms=min(self.dt,max(1,deadline-start));self.step_ms=ms
  new_period=getattr(self,'pending_break',[])
  self.pending_break=[]
  if new_period and s.phase!=Phase.FINAL:
   previous=new_period[-1]['data'].get('period',new_period[-1]['period']);pause=900000 if previous==2 and previous<s.regulation_periods else 300000 if previous==s.regulation_periods else 120000
   savedphase=s.phase;s.phase=Phase.BREAK;self.e.emit('intermission','5.1',duration_ms=pause)
   self.e.advance(pause)
   for p in s.players.values():p.fatigue=min(1,p.fatigue+pause/1000*.002*p.a.endurance);p.vx=p.vy=0
   s.phase=savedphase
   if s.opening_deadline:s.opening_deadline=s.now+10000
   if s.restart:s.restart.created_at=s.now
   self.record();return
  if s.phase==Phase.DEAD:
   if self.c4c:
    for due in self.c4c_due(landings_only=True):
     if s.now<due<s.now+ms:ms=max(1,int(math.ceil(due-s.now-1e-9))) #C4c: a Keeper still in the air lands on time in dead time too
   targets=self.targets_dead();old=self.move_players(ms,targets);self.update_archers(ms);self.auto_substitutions()
   if self.c4b:self.c4b_gait(old,ms) #C4b: and in dead time
   self.e.elapse(ms)
   if self.c4c:self.c4c_land_due()
   r=s.restart
   if r and r.kind=='recovery':
    #C2: a restored first-tackle recovery resumes as soon as the disc is clear of opponents' bodies (30 s is only the outer bound).
    if not self.e.recovery_blockers(r):self.e.resume_recovery() #no fixed wait: readiness is the disc being clear
    self.record();return
   if r and(r.kind=='inbound'or s.now>=r.created_at+1500): #C2: an inbound is ready as soon as taker, ball and clearance are; other restarts keep the Pocket 1.1 minimum
    taker=getattr(self,'restart_taker',None)
    if taker and r.ready_at is None and s.players[taker].speed<1.5:self.e.ready(taker)
    if r.ready_at is not None and s.now-r.ready_at>=250:
     p=s.players[r.taker];recipient=self.pol[p.team].pass_choice(s,p)
     plan=None
     if recipient and self.assume['c1_pass_planning']:
      order=[recipient]+[m for m in self.pol[p.team].pass_ranked(s,p)if m.id!=recipient.id]
      if r.kind=='inbound':order.sort(key=lambda m:self.e.zone(m.x,m.y)==self.e.zone(r.x,r.y)) #C2 provisional controller: first choice a receiver outside the arc, which clears the zone
      if self.ctrl:order=self.c4c2_inbound_order(r,p,order) #C4c2: the short option, then the entry option, when their lanes are open
      for q in order:
       plan=self.plan_pass((r.x,r.y,p.hand_height),p,q,'pass')
       if plan:recipient=q;break
      if plan is None:recipient=None
     if recipient and plan:
      self.pass_signal=(recipient.id,r.ready_at);self.e.restart_release(p.id,self.aim_error(plan[0],p.a.passing),recipient.id)
     elif recipient:
      target=(recipient.x+recipient.vx*.2,recipient.y+recipient.vy*.2,recipient.hand_height)
      vel=self.ball_velocity((r.x,r.y,p.hand_height),target,p.a.passing,'pass');self.e.restart_release(p.id,vel,recipient.id)
     else:
      # A pass into legal space requires no designated receiver.
      target=(clamp(r.x+s.attack_sign(p.team)*12,8,92),clamp(r.y+(8 if r.y<50 else-8),8,92),1.2)
      self.e.restart_release(p.id,self.ball_velocity((r.x,r.y,p.hand_height),target,p.a.passing,'pass'))
   self.record();return
  if s.phase==Phase.PENALTY:targets=self.penalty_targets()
  else:
   targets={}
   for policy in self.pol.values():targets.update(policy.targets(s))
   if self.ctrl:self.c4c2_targets(targets) #C4c2: a carry-in drives at the goal; receivers go to the open spots worth most
  if self.assume['c1_receiver_routing']:self.route_receiver(targets)
  if self.c3:
   #C3a: decisions, motion with contact, ball and arrows, and the commit of events run as one interval that ends at the first
   #event (c3_step). It may be shorter than ms; the next step starts from the committed state.
   self.c3_step(ms,targets);self.step_count+=1;self.record();return
  old=self.move_players(ms,targets);self.update_archers(ms);self.auto_substitutions();self.update_keepers_jump()
  #Decisions occur at the start of the physics interval using the current observed state.
  self.carrier_decision();self.arrow_decisions()
  events=self.advance_ball(ms,old)+self.advance_arrows(ms)+self.player_contacts(ms,old)
  self.process_events(events,start,ms,old);self.step_count+=1;self.record()
 def route_receiver(self,targets):
  """C1: while a pass is in flight, its intended receiver moves to meet the ball's actual path.
  The receiver uses only what is observable: the ball's current position and velocity."""
  s=self.s;b=s.ball
  if b.carrier is not None or not b.intended or b.mode not in(BallMode.PASS,BallMode.KICK)or s.phase!=Phase.LIVE:return
  q=s.players.get(b.intended)
  if q is None or not self.e.eligible(q)or q.posture!='upright'or q.role=='archer':return
  reach=q.a.reach*(1.1 if q.role=='keeper'else.9)
  path=predict_path(b,self.assume['gravity'],self.assume['ball_drag'],self.assume['ball_restitution'])
  targets[q.id]=intercept_xy(q,path,reach,False);q.next_decision=s.now
 def record(self):
  s=self.s
  if s.now>=self.next_trace:
   self.trace.append({'t_ms':s.now,'period':s.period,'g_ms':s.game_ms,'p_ms':s.possession_ms,'owner':s.owner,'phase':s.phase.value,'ball':[round(s.ball.x,2),round(s.ball.y,2),round(s.ball.z,2)],'players':{p.id:[round(p.x,2),round(p.y,2),round(p.fatigue,3),p.frozen(s.now)]for p in s.players.values()if p.active}})
   self.next_trace=s.now+self.cfg.get('record_positions_every_ms',1000)
  for rec in self.e.log[self.last_log_seen:]:
   if rec['event']=='period_end'and s.phase!=Phase.FINAL:self.pending_break=[rec]
   if rec['event']=='freeze':
    self.freeze_records[rec['id']]={'t':rec['t_ms'],'team':s.players[rec['data']['player']].team,'x':rec['ball'][0],'resolved':False}
   if rec['event']=='possession_change':
    for f in self.freeze_records.values():
     if not f['resolved']and rec['t_ms']-f['t']<=5000 and rec['owner']!=f['team']:self.stats['freeze_turnover_within5s']+=1;f['resolved']=True
  for rec in self.e.log[self.last_log_seen:]:
   if rec['event']=='release':
    for policy in self.pol.values():
     if self.s.players[rec['data']['player']].team!=policy.team:policy.recent.append((rec['data']['kind'],rec['ball'][1]));policy.recent=policy.recent[-12:]
  self.last_log_seen=len(self.e.log)
 def run(self,max_wall_ms=16000000):
  while self.s.phase!=Phase.FINAL and self.s.now<max_wall_ms:self.step()
  if self.s.phase!=Phase.FINAL:
   self.e.suspend('model_progress_watchdog');self.e.elapse(86400000);self.e.resume()
  return self.summary()
 def run_for(self,seconds):
  until=self.s.now+int(seconds*1000)
  while self.s.now<until and self.s.phase!=Phase.FINAL:self.step()
  return self.summary()
 def summary(self):
  s=self.s;events=Counter(r['event']for r in self.e.log);turnovers=Counter(r['data'].get('reason')for r in self.e.log if r['event']=='possession_change')
  spans=[];last=None
  for r in self.e.log:
   if r['event']=='possession_change':
    if last:spans.append((r['t_ms']-last['t_ms'])/1000)
    last=r
  total=s.live_ms+s.dead_ms
  digest=hashlib.sha256(json.dumps(self.e.log,sort_keys=True,separators=(',',':')).encode()).hexdigest()
  return{'seed':self.seed,'rules_version':self.cfg.get('ruleset','1.0.1')+' Working Rules','regulation_format':s.period_seconds==600 and s.regulation_periods==4,'result':s.result,'score':s.score,'period':s.period,'elapsed_s':s.now/1000,'live_s':s.live_ms/1000,'dead_s':s.dead_ms/1000,'active_fraction':s.live_ms/max(1,total),'events':dict(events),'turnover_causes':dict(turnovers),'stats':dict(self.stats),'mean_possession_elapsed_s':sum(spans)/len(spans)if spans else 0,'mean_final_fatigue':sum(p.fatigue for p in s.players.values())/len(s.players),'event_log_sha256':digest,'steps':self.step_count,'assumptions':self.assume}
 def save(self,path):
  path=Path(path);path.mkdir(parents=True,exist_ok=True)
  (path/'summary.json').write_text(json.dumps(self.summary(),indent=2));(path/'config.json').write_text(json.dumps(self.cfg,indent=2))
  with(path/'events.jsonl').open('w')as f:
   for r in self.e.log:f.write(json.dumps(r,separators=(',',':'))+'\n')
  with(path/'positions.jsonl').open('w')as f:
   for r in self.trace:f.write(json.dumps(r,separators=(',',':'))+'\n')


"""Final Pocket controllers and configurable rosters.

These functions extend the retained C4c2 core at packaging time. All new policy
forecasts use present state; they do not query future random draws. Forecasts
are coaching approximations, not alterations to physics or sport rules.
"""

RATED_ATTRIBUTES = ('strength', 'agility', 'endurance', 'balance',
                    'contact_resistance', 'tackling', 'blocking', 'ball_handling',
                    'passing', 'kicking', 'catching', 'awareness',
                    'archery_accuracy', 'keeper_skill')

_pocket_previous_init = Match.__init__
_pocket_previous_plan = Match.plan_pass
_pocket_previous_eval = Match.c4c2_eval
_pocket_previous_cont = Match.c4c2_cont
_pocket_previous_decide = Match.c4c2_decide


def pocket_init(self, config=None):
    _pocket_previous_init(self, config)
    self.pocket_final = bool(self.cfg.get('pocket_final'))
    self.pocket_decisions = {}
    self.pocket_carry_observations = Counter()
    self.pocket_intents = {}
    self.pocket_carry_rows = []
    self.pocket_last_occupancy = -1000
    if not self.pocket_final:
        return
    pc = self.cfg['pocket']
    overrides = self.cfg.get('roster_overrides', {})
    for team in ('A', 'B'):
        rng = random.Random(self.seed + 17041)
        players = sorted((p for p in self.s.players.values() if p.team == team), key=lambda p: p.slot)
        # Mirrored, independently permuted attribute profiles; no rating is a
        # success percentage. Physical dimensions and capacities stay separate.
        for attr in RATED_ATTRIBUTES:
            levels = [-1., -.5, 0., .5, 1.] * 4 + [0., 0.]
            rng.shuffle(levels)
            for p, level in zip(players, levels):
                value = pc['rating_' + team] + pc['rating_spread'] * level
                setattr(p.a, attr, clamp(value, 40., 100.) / 100.)
        for p in players:
            if p.role == 'keeper':
                p.a.height = self.assume.get('keeper_height_m') or pc['keeper_height_' + team]
                p.a.mass = pc['keeper_mass_' + team]
                p.a.reach = pc['keeper_reach_fraction'] * p.a.height
                p.a.maximum_speed = pc['keeper_speed']
                p.a.acceleration = pc['keeper_acceleration']
                p.a.braking = pc['keeper_braking']
                p.a.turning = pc['keeper_turning']
                p.a.jump_height = pc['keeper_jump']
            else:
                p.a.height = pc['field_height']
                p.a.mass = pc['field_mass']
                p.a.reach = pc['field_reach']
            for attr, value in overrides.get(team, {}).items():
                setattr(p.a, attr, value / 100. if attr in RATED_ATTRIBUTES else value)
            for attr, value in overrides.get(p.id, {}).items():
                setattr(p.a, attr, value / 100. if attr in RATED_ATTRIBUTES else value)
            p.a.validate()
    self.pocket_roster = {p.id: {k: getattr(p.a, k) for k in Attributes.__dataclass_fields__}
                          for p in self.s.players.values()}
    self.e.emit('pocket_final_rules', 'Pocket-2.0', controller_active=self.ctrl,
                roster=self.pocket_roster, ratings_input='40..100, divided by 100',
                forecasts='C4c2 reference drills plus present-state travel and moving-lane estimates',
                carry_failure_credit='observed first tackles only; zero before observations')


def pocket_budget(self, clock):
    if not self.pocket_final:
        return clock
    return max(0., min(clock, self.s.game_ms / 1000.))


def pocket_travel(self, p, distance):
    """Minimum straight-line time under this athlete's current capacities.

    This is an optimistic policy bound: collisions, turns and fatigue can take
    longer. It never claims a stationary athlete moves instantly at top speed.
    """
    cap = max(.1, p.a.maximum_speed * self.pol[p.team].t.pace * .9 * (.7 + .3 * p.fatigue))
    v = min(p.speed, cap)
    a = max(.1, p.a.acceleration * (.55 + .45 * p.fatigue))
    ramp = (cap - v) / a
    first = v * ramp + .5 * a * ramp * ramp
    if distance <= first:
        return (-v + math.sqrt(v*v + 2*a*max(0., distance))) / a
    return ramp + (distance - first) / cap


def pocket_receiver_position(self, q, seconds):
    """Bounded acceleration and stopping forecast toward the visible target."""
    x, y, vx, vy = q.x, q.y, q.vx, q.vy
    remain = max(0., seconds)
    while remain > 1e-8:
        dt = min(.1, remain)
        tx, ty = q.target
        dx, dy = tx-x, ty-y
        d = math.hypot(dx, dy)
        ux, uy = unit(dx, dy)
        speed = math.hypot(vx, vy)
        cap = q.a.maximum_speed * .88 * (.7 + .3*q.fatigue)
        desired = min(cap, math.sqrt(2*q.a.braking*d))
        ax, ay = ux*desired-vx, uy*desired-vy
        change = math.hypot(ax, ay)
        limit = (q.a.acceleration if desired > speed else q.a.braking) * dt
        if change:
            f = min(1., limit/change)
            vx += ax*f
            vy += ay*f
        x += vx*dt
        y += vy*dt
        remain -= dt
    return x, y


def pocket_plan_pass(self, origin, passer, q, kind, lag=0., speed=None):
    if not self.pocket_final:
        return _pocket_previous_plan(self, origin, passer, q, kind, lag, speed)
    if speed is None:
        speed = self.cfg['pocket']['pass_speed' if kind == 'pass' else 'ball_speed']
    T = norm(q.x-origin[0], q.y-origin[1]) / max(1e-6, speed)
    sol = None
    # A receiver can decelerate instead of being led at unchanged velocity to
    # an end line. The receiving route still reads the actual flight after release.
    for _ in range(6):
        x, y = self.pocket_receiver_position(q, max(0., T-lag))
        margin = max(1.25, q.radius + .5)
        aim = (clamp(x, margin, 100-margin), clamp(y, margin, 100-margin), q.hand_height)
        sol = launch_for(origin, aim, speed, self.assume['gravity'], self.assume['ball_drag'])
        if sol is None:
            return None
        T = sol[1]
    return sol[0], aim[:2], T


def pocket_eval(self, p, x, y, clock, arrow_t=None, origin=False):
    if not self.pocket_final:
        return _pocket_previous_eval(self, p, x, y, clock, arrow_t, origin)
    clock = self.pocket_budget(clock)
    result = _pocket_previous_eval(self, p, x, y, clock, arrow_t, origin)
    # Failed carries include strips and loose balls. Only empirically observed
    # first tackles receive retained-possession value. No synthetic free reset.
    n = self.pocket_carry_observations['attempts']
    retained = self.pocket_carry_observations['first_tackle'] / n if n else 0.
    pc = self.cfg['pocket']
    result['carry'] = 0.
    if pc.get('carry_value', 0) > 0 and result['d'] <= 20.:
        duration = self.pocket_travel(p, result['d'] + self.s.ball.radius)
        if duration < clock:
            prob = self.c4c2_carry_chance(p, x, y)
            result['p_carry'] = prob
            result['carry'] = prob*pc['carry_value'] + min(1.-prob, retained)*result['vf']
    result['p_retained_carry'] = retained
    result['clock_budget_s'] = clock
    return result


def pocket_cont(self, p, x, y, clock, arrow_t=None):
    if not self.pocket_final:
        return _pocket_previous_cont(self, p, x, y, clock, arrow_t)
    clock = self.pocket_budget(clock)
    tau = min(self.assume['ctrl_lookahead_s'], max(0., clock-self.c4c2_windup_s(p)-.02))
    if tau <= .02:
        return 0.
    gx = self.s.attack_goal(p.team)
    d = math.hypot(gx-x, 50-y)
    ux, uy = unit(gx-x, 50-y)
    a = p.a.acceleration * (.55 + .45*p.fatigue)
    cap = p.a.maximum_speed * self.pol[p.team].t.pace * .9 * (.7+.3*p.fatigue)
    step = min(max(0., d-1.5), cap*tau, p.speed*tau+.5*a*tau*tau)
    xx, yy = x+ux*step, y+uy*step
    margin = self.c4c2_margin(p, xx, yy, tau)
    if arrow_t is not None:
        margin = min(margin, arrow_t-tau)
    E = self.c4c2_eval(p, xx, yy, clock-tau)
    # The pressure drill factor is a disclosed policy proxy for safe progress.
    # Unconditional carry-success ratios are NOT conditional survival chances.
    survival_proxy = self.c4c2_goal_factor(margin)
    # Retain the reference value of rebuilding an attacking possession when
    # there is time to reach the zone and prepare a finish. Without this term,
    # a one-step horizon shoots from midfield instead of valuing an entry.
    entry_distance = max(0., d-self.s.keeper_zone_radius)
    can_rebuild = clock-tau > self.pocket_travel(p, entry_distance)+self.c4c2_windup_s(p)
    rebuild = self.c4c2_vposs(d) if can_rebuild else 0.
    return survival_proxy * max(E['shoot'], E['carry'], rebuild)


def pocket_pass_option(self, p, q, clock):
    if not self.e.eligible(q) or q.posture != 'upright':
        return None
    prep = self.assume['pass_release_ms']*(1.35-.5*p.a.ball_handling)/1000.
    if clock <= prep:
        return None
    rho, factor, extra = self.c3_release_state(p, 'pass')
    speed = self.cfg['pocket']['pass_speed']*factor
    # Project the receiver through preparation before forecasting the flight.
    receiver = copy.copy(q)
    receiver.x, receiver.y = self.pocket_receiver_position(q, prep)
    plan = self.plan_pass((p.x, p.y, p.hand_height), p, receiver, 'pass', speed=speed)
    if plan is None:
        return None
    velocity, (x, y), flight = plan
    remaining = clock-prep-flight
    if remaining <= self.c4c2_windup_s(q)+.02:
        return None
    L = math.hypot(x-p.x, y-p.y)
    if L < 2.5:
        return None
    # Moving opponents are measured where they will cross the visible pass
    # line, rather than where they happen to stand when preparation begins.
    lane = 99.
    for o in self.active_field():
        if o.team == p.team or not self.e.eligible(o):
            continue
        _, fraction = segment_distance(o.x, o.y, p.x, p.y, x, y)
        t = prep + clamp(fraction, 0., 1.)*flight
        distance, _ = segment_distance(o.x+o.vx*t, o.y+o.vy*t, p.x, p.y, x, y)
        lane = min(lane, distance)
    probability = self.c4c2_pass_p(L, lane)
    E = self.c4c2_eval(q, x, y, remaining)
    value = probability * max(E['shoot'], E['carry'], self.c4c2_cont(q, x, y, remaining))
    return {'q': q, 'value': value, 'p_complete': probability, 'aim': [x, y],
            'prep_s': prep, 'flight_s': flight, 'remaining_s': remaining, 'lane_m': lane}


def pocket_decide(self, p, clock, danger_arrow):
    if not self.pocket_final:
        return _pocket_previous_decide(self, p, clock, danger_arrow)
    s = self.s
    clock = self.pocket_budget(clock)
    if getattr(p, 'c4c2_intent_t', -1) < s.ball.control_time:
        p.c4c2_intent = None
    arrow_t = None
    if danger_arrow:
        arrow_t = min((math.hypot(a.x-p.x, a.y-p.y)/max(1., math.hypot(a.vx, a.vy))
                       for a in s.arrows if a.live and a.team != p.team), default=None)
    E = self.c4c2_eval(p, p.x, p.y, clock, arrow_t, True)
    options = {'shoot': E['shoot'], 'carry': E['carry'],
               'continue': self.c4c2_cont(p, p.x, p.y, clock, arrow_t)}
    passes = []
    if s.now-s.ball.control_time > 180:
        for q in self.pol[p.team].pass_ranked(s, p)[:6]:
            candidate = self.pocket_pass_option(p, q, clock)
            if candidate is not None:
                passes.append(candidate)
    option = max(passes, key=lambda v: v['value']) if passes else None
    if option:
        options['pass'] = option['value']
    best = max(options, key=lambda key: (options[key], key == 'shoot'))
    style = int(self.assume.get('ctrl_style_'+p.team, 0))
    preferred = 'carry' if style == 1 else 'pass' if style == 2 else None
    if preferred in options and options[preferred] > 0 and options[preferred] >= (1-self.assume['ctrl_style_band'])*options[best]:
        best = preferred
    previous = getattr(p, 'c4c2_intent', None)
    if previous == 'carry' and best != 'carry':
        p.c4c2_intent = None
        self.e.emit('carry_intent_end', 'Pocket-2.0', player=p.id, reason=best,
                    held_ms=s.now-getattr(p, 'c4c2_intent_t', s.now))
    if best == 'carry':
        if previous != 'carry':
            p.c4c2_intent = 'carry'
            p.c4c2_intent_t = s.now
    elif best == 'shoot' and E['shoot'] > 0:
        self.make_shot(p)
    elif best == 'pass':
        self.make_pass(p, option['q'], 'pass')
        if danger_arrow:
            p.arrow_reaction_pending = True
            self.stats['arrow_evoked_pass_preparations'] += 1
    # Record every transition and one-second heartbeat, including continue.
    # This caps log size while preserving activation and decision provenance.
    key = (best, s.ball.control_time)
    last = self.pocket_decisions.get(p.id)
    if last is None or last[0] != key or s.now-last[1] >= 1000:
        data = dict(player=p.id, choice=best, ev={k: round(v, 5) for k, v in options.items()},
                    clock_budget_s=clock, period_s=s.game_ms/1000.,
                    possession_s=s.possession_ms/1000., d=E['d'], value=E['v'],
                    p_conv=E['p_conv'], goal_factor=E['goal_factor'],
                    p_carry=E['p_carry'], p_retained_carry=E['p_retained_carry'], style=style,
                    preparation_started=p.id in self.pending_ball_actions)
        if option and best == 'pass':
            data['pass_forecast'] = {k: v for k, v in option.items() if k != 'q'}
            data['target'] = option['q'].id
        self.e.emit('controller_decision', 'Pocket-2.0', **data)
        self.pocket_decisions[p.id] = (key, s.now)


_pocket_previous_record = Match.record


def pocket_record(self):
    if self.pocket_final:
        # Each carry intent ends once. Refine failure classes without turning
        # a strip, freeze or an unfinished attempt into a first tackle.
        for event in self.e.log[self.last_log_seen:]:
            name, data = event['event'], event['data']
            if name == 'controller_decision' and data.get('choice') == 'carry':
                pid = data['player']
                if pid not in self.pocket_intents:
                    self.pocket_intents[pid] = event
                    self.pocket_carry_observations['attempts'] += 1
            elif name in ('tackle_count', 'strip', 'freeze', 'goal', 'control', 'release', 'possession_change', 'carry_intent_end', 'period_end'):
                for pid, start in list(self.pocket_intents.items()):
                    outcome = None
                    if name == 'tackle_count' and data.get('carrier') == pid:
                        outcome = 'first_tackle' if data.get('count_to') == 1 else 'second_tackle'
                    elif name == 'strip' and data.get('target') == pid:
                        outcome = 'strip_or_loose'
                    elif name == 'freeze' and data.get('player') == pid:
                        outcome = 'freeze'
                    elif name == 'control' and data.get('player') != pid:
                        actor = data.get('player', '')
                        outcome = 'teammate_control' if actor.startswith(pid[0]) else 'opponent_control'
                    elif name == 'goal':
                        outcome = 'carry_goal' if data.get('method') == 'carry' and data.get('team') == pid[0] else 'other_goal'
                    elif name in ('release', 'carry_intent_end') and data.get('player') == pid:
                        outcome = 'changed_plan'
                    elif name == 'possession_change' and event['owner'] != pid[0]:
                        outcome = 'turnover'
                    elif name == 'period_end':
                        outcome = 'period_end'
                    if outcome:
                        self.pocket_carry_observations[outcome] += 1
                        self.pocket_carry_rows.append({'start_id': start['id'], 'end_id': event['id'],
                            'player': pid, 'outcome': outcome,
                            'live_s': (event['live_ms']-start['live_ms'])/1000.})
                        del self.pocket_intents[pid]
        if self.s.phase == Phase.LIVE and self.s.owner and self.s.live_ms-self.pocket_last_occupancy >= 1000:
            self.pocket_last_occupancy = self.s.live_ms
            team = self.s.owner
            zone = self.s.own_zone(self.s.other(team))
            attackers = [p for p in self.active_field() if p.team == team and self.e.zone(p.x,p.y) == zone]
            defenders = [p for p in self.active_field() if p.team != team and self.e.zone(p.x,p.y) == zone]
            gx = self.s.attack_goal(team)
            self.e.emit('pocket_occupancy_sample', 'Pocket-2.0', attackers=len(attackers),
                defenders=len(defenders), field_defenders=sum(p.role != 'keeper' for p in defenders),
                goal_mouth_defenders=sum(math.hypot(p.x-gx,p.y-50) <= 8 for p in defenders),
                defenders_per_attacker=len(defenders)/len(attackers) if attackers else None)
    _pocket_previous_record(self)


Match.__init__ = pocket_init
Match.pocket_budget = pocket_budget
Match.pocket_travel = pocket_travel
Match.pocket_receiver_position = pocket_receiver_position
Match.plan_pass = pocket_plan_pass
Match.c4c2_eval = pocket_eval
Match.c4c2_cont = pocket_cont
Match.pocket_pass_option = pocket_pass_option
Match.c4c2_decide = pocket_decide
Match.record = pocket_record
'''
}

def load_core():
    """Load bundled local source in memory; no installation or extracted files."""
    name = '_beastball_pocket'
    pkg = types.ModuleType(name)
    pkg.__path__ = []
    sys.modules[name] = pkg
    for key, source in CORE_SOURCES.items():
        mod = types.ModuleType(name + '.' + key)
        mod.__package__ = name
        mod.__file__ = '<embedded ' + key + '.py>'
        sys.modules[mod.__name__] = mod
        setattr(pkg, key, mod)
        exec(compile(source, mod.__file__, 'exec'), mod.__dict__)
    return pkg

CORE = load_core()

def validate_calibration(cal):
    if set(cal) != set(CALIBRATION):
        raise ValueError('Calibration keys must match this script version.')
    for key, v in cal.items():
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
            raise ValueError(key + ' must be a finite number')
    positive = ('gravity', 'tackle_rate', 'pass_release_ms', 'bow_draw_ms', 'body_radius_scale', 'ball_mass_kg',
                'catch_arrest_force_N', 'catch_hand_travel_m', 'c3_substep_ms', 'contact_time_s', 'shock_speed_mps', 'grip_slip_ref_mps',
                'grip_force_N', 'grip_overload_time_s', 'topple_time_s', 'base_half_width_frac', 'hold_height_upper_frac', 'hold_height_lower_frac',
                'slide_friction', 'get_up_time_s', 'descent_time_s')
    for key in positive:
        if cal[key] <= 0: raise ValueError(key + ' must be greater than zero')
    for key in ('ball_drag', 'arrow_drag', 'catch_noise', 'block_force', 'arrow_error_scale', 'fatigue_rate',
                'grip_delay_ms', 'frame_thickness', 'pass_aim_error_deg', 'catch_reaction_s', 'deflection_speed_kept'):
        if cal[key] < 0: raise ValueError(key + ' cannot be negative')
    if not 0 <= cal['ball_restitution'] <= 1: raise ValueError('ball_restitution must be between 0 and 1')
    if cal['deflection_speed_kept'] > 1: raise ValueError('deflection_speed_kept cannot exceed 1')
    for key in ('c1_pass_planning', 'c1_receiver_routing', 'c1_chasers_read_flight', 'c1_catch_model', 'c3_contact', 'c3_follow_distance', 'c3b', 'recovery_react', 'exit_protection', 'c3c', 'c4_zone', 'zone_direct_penalty'):
        if cal[key] not in (0, 1): raise ValueError(key + ' must be 0 or 1')
    for key in ('traction_coefficient', 'brace_speed_mps', 'rearm_gap_m', 'grip_gain_per_s', 'grip_resist_per_s', 'grip_slip_per_s',
                'grip_overload_per_s', 'balance_recovery_per_s', 'restraint_error_deg', 'collision_risk_tolerance', 'c3_prep_round_ms', 'contact_foul_min_shock',
                'get_up_max_slide_mps', 'containment_window_s', 'descent_window_s', 'tuck_after_delay_frac', 'escape_force_N'):
        if cal[key] < 0: raise ValueError(key + ' cannot be negative')
    if not 0 < cal['arm_pin_grip'] <= 1: raise ValueError('arm_pin_grip must be above 0 and at most 1')
    for key in ('gait_step_base_frac', 'gait_step_per_mps_frac', 'gait_step_max_frac', 'gait_half_width_frac', 'gait_still_mps', 'gait_reset_frac'):
        if cal[key] <= 0: raise ValueError(key + ' must be greater than zero')
    if not 0 < cal['gait_duty_min'] <= cal['gait_duty_rest'] < 1 or cal['gait_duty_per_mps'] < 0: raise ValueError('gait duty factors must satisfy 0 < min <= rest < 1, and the slope cannot be negative')
    if cal['strip_in_motion_factor'] < 1: raise ValueError('strip_in_motion_factor cannot be below 1')
    for key, top in (('c3_region_policy', 2), ('escape_allocation', 3), ('contact_roster', 4), ('c4b', 1), ('c4c', 1), ('keeper_windup_set', 1), ('keeper_confront', 1), ('c4c2', 1), ('reversal_rule', 1), ('controller', 1), ('ctrl_style_A', 2), ('ctrl_style_B', 2), ('ctrl_receivers', 4), ('ctrl_short_inbound', 1), ('ctrl_keeper', 1)):   # C4a, C4b, C4c, C4c2: named policies, designs and switches
        if cal[key] not in range(top + 1): raise ValueError('%s must be a whole number from 0 to %d' % (key, top))
    if cal['keeper_height_m'] != 0 and not 2.7432 <= cal['keeper_height_m'] <= 3.6576: raise ValueError('keeper_height_m must be 0 (the inherited Keeper) or from 2.7432 to 3.6576 m (9 to 12 ft)')   # C4c2
    if not 0 < cal['blindside_rear_half_angle_deg'] <= 90: raise ValueError('blindside_rear_half_angle_deg must be above 0 and at most 90')
    for key in ('contact_restitution', 'lower_hold_leg_factor', 'holder_load_factor', 'tackle_grip_threshold', 'tackle_source_majority',
                'restraint_weight_matched', 'restraint_weight_other', 'restraint_speed_loss'):
        if not 0 <= cal[key] <= 1: raise ValueError(key + ' must be between 0 and 1')
    if cal['c3_substep_ms'] != int(cal['c3_substep_ms']) or not 1 <= cal['c3_substep_ms'] <= 100: raise ValueError('c3_substep_ms must be a whole number from 1 to 100')
    return cal

def validate(settings):
    if set(settings) != set(SETTINGS):
        raise ValueError('Settings keys must match this script version.')
    for key, default in SETTINGS.items():
        v = settings[key]
        if isinstance(default, bool):
            if not isinstance(v, bool): raise ValueError(key + ' must be True or False')
        elif isinstance(default, (int, float)):
            if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
                raise ValueError(key + ' must be a finite number')
            if isinstance(default, int) and int(v) != v: raise ValueError(key + ' must be a whole number')
    bounds = {'matches':(1,50), 'seed':(0,2147483647), 'period_seconds':(10,1200),
              'periods':(1,4), 'overtime_seconds':(10,600), 'play_clock':(5,180),
              'player_speed':(1,44.704), 'acceleration':(.5,30), 'braking':(.5,40),
              'turning':(.5,40), 'ball_speed':(5,1000), 'pass_speed':(5,1000),
              'arrow_speed':(5,1000), 'keeper_zone_radius':(1,45), 'inner_zone_radius':(.25,44.99), 'inner_points':(1,100), 'release_points':(1,100),
              'outside_points':(1,100), 'carry_value':(0,100), 'dt_ms':(20,100), 'tackles_per_possession':(1,2),
              'inbound_mark_offset':(6.5,45), 'marking_distance':(.5,15)}
    for key, (lo,hi) in bounds.items():
        if not lo <= settings[key] <= hi: raise ValueError('%s must be between %s and %s' % (key,lo,hi))
    if settings['inner_zone_radius'] >= settings['keeper_zone_radius']:
        raise ValueError('Inner zone radius must be smaller than Keeper Zone radius.')
    if not isinstance(settings['label'], str): raise ValueError('label must be text')
    return settings

def import_settings(obj):
    """Import current settings or explicitly migrate a legacy carry experiment."""
    values=copy.deepcopy(obj.get('settings',obj))
    if not isinstance(values,dict):raise ValueError('Expected a settings object.')
    legacy='carry_points' in values
    if legacy:
        carry=values.pop('carry_points')
        values.setdefault('inner_points',carry)
        values.setdefault('keeper_zone_radius',20.0)
        values.setdefault('inner_zone_radius',5.0)
    unknown=set(values)-set(SETTINGS)
    if unknown:raise ValueError('Unknown settings: '+', '.join(sorted(unknown)))
    candidate={**SETTINGS,**values}
    validate(candidate)
    cal=obj.get('calibration') if isinstance(obj,dict) else None
    if cal is not None:
        extra=set(cal)-set(CALIBRATION)
        if extra:raise ValueError('Unknown calibration values: '+', '.join(sorted(extra)))
        import_settings.calibration=validate_calibration({**CALIBRATION,**cal})
    else:
        import_settings.calibration=None
    message=('Legacy settings migrated: carry_points becomes inner_points; missing radii default to 20m / 5m. This is a NEW release-territory experiment, not a reproduction of the old run.' if legacy else '')
    return candidate,message

SCORING_CONFIGURATIONS = {   # build specification v0.2, section 2. Starting points, not balance conclusions. B: the inner arc has no distinct value.
    'A-low':  {'outside_points': 1, 'release_points': 2, 'inner_points': 3, 'carry_value': 0},
    'B-low':  {'outside_points': 1, 'release_points': 2, 'inner_points': 2, 'carry_value': 3},
    'C-low':  {'outside_points': 1, 'release_points': 2, 'inner_points': 3, 'carry_value': 4},
    'A-high': {'outside_points': 2, 'release_points': 4, 'inner_points': 6, 'carry_value': 0},
    'B-high': {'outside_points': 2, 'release_points': 4, 'inner_points': 4, 'carry_value': 6},
    'C-high': {'outside_points': 2, 'release_points': 4, 'inner_points': 6, 'carry_value': 8},
}
def scoring_configuration(name):
    """The settings for one of the six configurations (outside releases allowed). Own goals and ordinary released penalties take
    the zone-release value; a Carry-enabled penalty finish the carry value; automatic awards the carry value if Carry is enabled,
    else the zone-release value."""
    return {**SCORING_CONFIGURATIONS[name], 'allow_outside_releases': True}

def configuration(settings, seed=None, calibration=None):
    p = validate(copy.deepcopy(settings))
    cal = validate_calibration(copy.deepcopy(CALIBRATION if calibration is None else calibration))
    p.update(release_territories=True, zone_only=not p['allow_outside_releases'],
             ball_limit=max(40,p['ball_speed'],p['pass_speed']),
             arrow_limit=max(30,p['arrow_speed']))
    return {'seed':settings['seed'] if seed is None else seed, 'ruleset':'1.0.1',
            'period_seconds':settings['period_seconds'], 'regulation_periods':settings['periods'],
            'overtime_seconds':settings['overtime_seconds'], 'dt_ms':settings['dt_ms'],
            'record_positions_every_ms':1000000000,
            'disable_archery':not settings['archery'], 'pocket':p, 'assumptions':cal,
            'teams':{t:{'roster':'balanced','attack':'balanced','defense':'zone'} for t in ('A','B')}}

def fingerprint(settings):
    return hashlib.sha256(json.dumps(settings,sort_keys=True).encode()).hexdigest()[:12]

def run_match(settings, seed=None, progress=True, calibration=None):
    cal = copy.deepcopy(CALIBRATION if calibration is None else calibration)
    m = CORE.match.Match(configuration(settings,seed,cal))
    next_report = 0
    # Explicit safety bound for experimental setups; never turn an unfinished run into a win.
    watchdog = max(600000, int((settings['period_seconds']*settings['periods']+
                              settings['overtime_seconds']*2)*1000*12))
    wall_started = time.monotonic(); cpu = time.process_time()
    while m.s.phase != CORE.types.Phase.FINAL and m.s.now < watchdog:
        m.step()
        if progress and m.s.live_ms >= next_report:
            print('  P%s  clock %.1fs  A %s : %s B  live %.0fs' %
                  (m.s.period,m.s.game_ms/1000,m.s.score['A'],m.s.score['B'],m.s.live_ms/1000),flush=True)
            next_report = m.s.live_ms + 60000
    m.e.assert_invariants()
    summary = m.summary()
    summary['rules_version'] = VERSION + ' experimental configuration'
    summary['complete'] = m.s.phase == CORE.types.Phase.FINAL
    summary['ordinary_completion'] = bool(summary['complete'] and m.s.result and
                   m.s.result['method'] in ('regulation','overtime','shootout'))
    summary['cpu_seconds'] = round(time.process_time()-cpu,3)
    summary['wall_seconds'] = round(time.monotonic()-wall_started,3)
    summary['effective_roster'] = getattr(m, 'pocket_roster', {})
    summary['carry_outcome_ledger'] = dict(getattr(m, 'pocket_carry_observations', {}))
    summary['carry_outcome_rows'] = getattr(m, 'pocket_carry_rows', [])
    summary['carry_outcome_ledger']['unresolved'] = len(getattr(m, 'pocket_intents', {}))
    from collections import Counter
    goals = Counter()
    for ev in m.e.log:
        if ev['event']=='goal': goals[ev['data']['method']] += 1
        elif ev['event'] in ('penalty_goal','penalty_goal_scored'): goals['penalty'] += 1
    summary['goal_counts'] = dict(goals)
    summary['settings_fingerprint'] = fingerprint(settings)
    summary['score_events'] = [e for e in m.e.log if e['event'] in ('goal','penalty_goal','penalty_goal_scored','shootout_attempt')]
    # Measure completed ownership intervals on live time; distinguish from source wall-time metric.
    changes=[e for e in m.e.log if e['event']=='possession_change']
    intervals=[(b['live_ms']-a['live_ms'])/1000 for a,b in zip(changes,changes[1:])]
    summary['mean_completed_possession_live_s'] = statistics.mean(intervals) if intervals else None
    summary['checkpoint'] = CHECKPOINT
    summary['calibration'] = cal
    summary['measures'] = measure(m.e.log, settings)
    summary['measures_c3'] = measure_c3(m.e.log)
    summary['measures_c4'] = measure_c4(m.e.log)
    summary['report_qualifications'] = report_qualifications(summary['measures_c3'])
    return summary, m.e.log

def completed_tackles(events):
    return events['tackle_count'] if 'tackle_count' in events else events.get('tackle_award',0)

def compact(summary):
    e=summary['events'];g=summary['goal_counts']
    return ('A %s : %s B | %s\nGoals %s\nTackles %s; strips %s; arrows %s; freezes %s\n'
            'Active %.1f%%; completed-possession live mean %s s\nFinished normally: %s; event hash %s' %
            (summary['score']['A'],summary['score']['B'],str(summary.get('result') or {'method':'watchdog'}),
             g,completed_tackles(e),e.get('strip',0),e.get('arrow_release',0),e.get('freeze',0),
             100*summary['active_fraction'],summary['mean_completed_possession_live_s'],
             summary['ordinary_completion'],summary['event_log_sha256']))

def aggregate(results):
    if not results: return {}
    scores=[sum(r['score'].values()) for r in results]
    from collections import Counter
    goals=Counter()
    for r in results: goals.update(r['goal_counts'])
    return {'matches':len(results),'ordinary_completions':sum(r['ordinary_completion'] for r in results),
            'mean_combined_points':statistics.mean(scores),
            'points_per_live_minute':60*sum(scores)/max(1,sum(r['live_s'] for r in results)),
            'stdev_combined_points':statistics.stdev(scores) if len(scores)>1 else None,
            'min_combined_points':min(scores),'max_combined_points':max(scores),
            'goals':dict(goals),'mean_active_fraction':statistics.mean(r['active_fraction'] for r in results),
            'total_arrow_releases':sum(r['events'].get('arrow_release',0) for r in results),
            'total_freezes':sum(r['events'].get('freeze',0) for r in results),
            'total_tackles':sum(completed_tackles(r['events']) for r in results),
            'total_strips':sum(r['events'].get('strip',0) for r in results)}



# ============================================================
# COMMON MEASUREMENT LAYER  (version M1.3)
# Reads a finished match's event log and reports the same measures at
# every checkpoint. It never changes play: it runs after the match and
# only reads events. A measure the log cannot support is reported as
# None ("unavailable"), never as zero.
#
# M1.1 corrects M1 after the Lead's C0 audit:
#  1. every goal ends a possession, including an own goal that leaves the
#     same team in possession;
#  2. a completed tackle is attributed to the possession it ended;
#  3. a foul notice does not end a ball flight; only an actual catch,
#     boundary, goal, formal stop or period end does;
#  4. shot territory is measured from the goal the shooter is attacking,
#     and Keeper touches are counted by tracked role;
#  5. boundary awards and restart timing are matched instance by instance.
#
# M1.2 adds, for checkpoints that log them: unsecured-catch deflections (touch events
# marked not deliberate) and failed pass plans. Deliberate touches are counted as before.
# On logs without those events M1.2 gives exactly the M1.1 results.
#
# M1.3 adds, for checkpoints that log them: tackle-count transitions, first-tackle recoveries, goal-line
# inbounds, reconstruction (clear-the-zone) and Keeper Zone occupancy and marking. No M1.2 definition is changed.
# A first counted tackle does not end a possession (the log has no possession change there). Where a log
# carries tackle_count events they are the record of completed tackles; otherwise tackle_award is, as before.
# On a log without any of the new events every M1.2 measure is reproduced exactly.
# ============================================================
from collections import Counter
MEASUREMENT_VERSION = 'M1.3'

def _stats(values):
    v = sorted(values)
    if not v: return {'n': 0, 'min': None, 'max': None, 'mean': None, 'median': None}
    return {'n': len(v), 'min': round(v[0], 3), 'max': round(v[-1], 3),
            'mean': round(statistics.mean(v), 3), 'median': round(statistics.median(v), 3)}

def _team(pid):
    return pid[0] if pid else None

def measure(log, settings):
    """Common measures from one match's event log (JSON-normalised)."""
    E = json.loads(json.dumps(log))
    n = len(E)
    kz = settings.get('keeper_zone_radius', 20.0); inner = settings.get('inner_zone_radius', 5.0)

    # ---- state that must be tracked along the log --------------------
    # which goal each team attacks (ends change at half-time), who the Keepers are,
    # and the last deliberate release before each event
    attack_x = [None] * n; keeper = [None] * n; last_release = [None] * n
    ax = {'A': 100.0, 'B': 0.0}; kp = {'A': 'A10', 'B': 'B10'}; cur = None; orientation_checked = True
    for i, e in enumerate(E):
        ev = e['event']; d = e['data']
        if ev == 'ends_exchanged': ax = {'A': ax['B'], 'B': ax['A']}
        elif ev == 'specialist_replacement' and d.get('role') == 'keeper' and d.get('new'): kp = {**kp, _team(d['new']): d['new']}
        elif ev == 'substitution' and d.get('role') == 'keeper' and d.get('incoming'): kp = {**kp, _team(d['incoming']): d['incoming']}
        elif ev == 'goal' and d.get('method') != 'own_goal' and d.get('team') in ax:
            if abs(ax[d['team']] - (0.0 if e['ball'][0] < 50 else 100.0)) > 1e-9: orientation_checked = False
        attack_x[i] = dict(ax); keeper[i] = dict(kp); last_release[i] = cur
        if ev in ('release', 'restart_release'): cur = i
        elif ev in ('restart_awarded', 'period_end'): cur = None

    def release_kind(i):
        j = last_release[i]
        if j is None: return None
        return 'restart_pass' if E[j]['event'] == 'restart_release' else E[j]['data']['kind']

    def flight_outcome(i, releaser, target):
        """What actually ended the flight that began at event i. A foul notice alone ends nothing."""
        for k in range(i + 1, n):
            f = E[k]; fe = f['event']
            if fe == 'control':
                c = f['data']['player']
                if target is not None and c == target: return 'intended_receiver', k, None
                return ('other_teammate' if _team(c) == _team(releaser) else 'opponent'), k, None
            if fe == 'boundary': return 'boundary', k, None
            if fe == 'goal': return 'goal', k, None
            if fe == 'no_goal': return 'other', k, 'no_goal'
            if fe == 'held_ball': return 'other', k, 'held_ball'
            if fe in ('period_end', 'match_complete'): return 'other', k, 'period_end'
            if fe == 'penalty_start': return 'other', k, 'stopped_for_penalty'
            if fe == 'restart_awarded': return 'other', k, 'stopped_' + str(f['data'].get('reason'))
            if fe in ('release', 'restart_release'): return 'other', k, 'next_release_without_recorded_control'
        return 'other', None, 'unresolved_at_export'

    def boundary_award(i):
        """The restart award that belongs to boundary event i, and whether it changed the team."""
        before = E[i].get('owner')
        for k in range(i + 1, n):
            fe = E[k]['event']
            if fe == 'restart_awarded':
                return ('turnover' if E[k]['data'].get('team') != before else 'same_team'), k
            if fe in ('boundary', 'period_end', 'match_complete'): break
        return 'no_award', None

    # ---- possessions -------------------------------------------------
    # A possession ends on a change of team control, on ANY goal, at a penalty
    # award, and at the end of a period. Penalty attempts are not possessions.
    possessions = []; current = None; last_closed = None
    def close(i, cause):
        nonlocal current, last_closed
        if current is not None:
            current['end_live_ms'] = E[i]['live_ms']; current['end_cause'] = cause
            current['live_s'] = (current['end_live_ms'] - current['start_live_ms']) / 1000
            possessions.append(current); last_closed = current; current = None
    def open_(i, team, cause):
        nonlocal current
        current = {'team': team, 'start_live_ms': E[i]['live_ms'], 'start_cause': cause, 'shots': 0, 'goals': 0,
                   'points': 0, 'passes': 0, 'tackles_against': 0, 'own_goals_conceded': 0, 'period': E[i]['period'], 'tackle_times': [], 'goal_times': []}
    penalty_points = Counter(); in_penalty = False
    counted = any(e['event'] == 'tackle_count' for e in E)   # M1.3: this log records every completed tackle as a count transition
    for i, e in enumerate(E):
        ev = e['event']; d = e['data']
        # counters first, so an event is credited to the possession it happened in
        if ev == 'tackle_count':
            if current is not None and current['team'] == d.get('team'):
                current['tackles_against'] += 1; current['tackle_times'].append(e['live_ms'])
        elif ev == 'tackle_award' and not counted:
            tt = _team(d.get('target'))
            if current is not None and current['team'] == tt: current['tackles_against'] += 1
            elif last_closed is not None and last_closed['team'] == tt and last_closed['end_cause'] == 'tackle':
                last_closed['tackles_against'] += 1
        elif ev in ('penalty_goal', 'penalty_goal_scored'):
            penalty_points[d.get('team')] += d.get('points', 0)
        elif current is not None and not in_penalty:
            if ev == 'release' and _team(d.get('player')) == current['team']:
                if d['kind'] == 'shot': current['shots'] += 1
                elif d['kind'] == 'pass': current['passes'] += 1
            elif ev == 'goal':
                if d.get('team') == current['team']: current['goals'] += 1; current['points'] += d.get('points', 0); current['goal_times'].append(e['live_ms'])
                else: current['own_goals_conceded'] += 1
        # transitions
        if ev == 'goal' and not in_penalty:
            close(i, 'goal' if (current and d.get('team') == current['team']) else 'own_goal_conceded')
        elif ev == 'possession_change':
            reason = d.get('reason')
            if reason == 'control': reason = 'control_after_' + (release_kind(i) or 'other')
            elif reason == 'boundary':
                prior = next((E[k] for k in range(i - 1, max(-1, i - 6), -1) if E[k]['event'] == 'boundary'), None)
                reason = 'boundary_carrier_out' if (prior is not None and prior['data'].get('carrier')) else 'boundary_after_' + (release_kind(i) or 'other')
            close(i, reason)
            if not in_penalty: open_(i, d['team'], d.get('reason'))
        elif ev == 'penalty_start':
            close(i, 'penalty_awarded'); in_penalty = True
        elif ev in ('penalty_goal_scored', 'penalty_failed', 'penalty_goal', 'penalty_save', 'penalty_tackle'):
            in_penalty = False
        elif ev == 'period_end': close(i, 'period_end'); in_penalty = False
        elif ev == 'match_complete': close(i, 'match_end')
        elif current is None and not in_penalty:
            if ev == 'restart_awarded': open_(i, d.get('team'), 'restart_' + str(d.get('reason')))
            elif ev == 'control' and e.get('owner'): open_(i, e['owner'], 'control_with_no_open_possession')
    if current is not None: close(n - 1, 'log_end')

    final = next((e for e in reversed(E) if e['event'] == 'match_complete'), None)
    score = final['data']['result']['score'] if final and final['data'].get('result') else E[-1]['score']

    # ---- goals -------------------------------------------------------
    goals = []
    for i, e in enumerate(E):
        if e['event'] != 'goal': continue
        d = e['data']; origin = d.get('release_origin'); gx = 0.0 if e['ball'][0] < 50 else 100.0
        goals.append({'team': d.get('team'), 'points': d.get('points', 0), 'method': d.get('method'), 'source': release_kind(i),
                      'origin_distance_m': math.hypot(origin[0] - gx, origin[1] - 50) if origin else None})
    goal_distance = {'definition': 'recorded scoring origin to the centre of the goal entered',
                     'all': _stats([g['origin_distance_m'] for g in goals if g['origin_distance_m'] is not None])}
    for method in sorted({g['method'] for g in goals}):
        goal_distance[method] = _stats([g['origin_distance_m'] for g in goals if g['method'] == method and g['origin_distance_m'] is not None])

    # ---- shots: one terminal outcome each ----------------------------
    shot_out = Counter(); shot_other = Counter(); band = {'inner': [0, 0], 'zone': [0, 0], 'outside': [0, 0]}
    launch_dist = []; shot_goals = Counter(); shot_points = Counter(); shots_by_team = Counter()
    for i, e in enumerate(E):
        if e['event'] != 'release' or e['data']['kind'] != 'shot': continue
        who = e['data']['player']; t = _team(who); shots_by_team[t] += 1
        b = e['ball']; gx = attack_x[i][t]; dist = math.hypot(b[0] - gx, b[1] - 50); launch_dist.append(dist)
        key = 'inner' if dist <= inner else 'zone' if dist <= kz else 'outside'
        res, k, why = flight_outcome(i, who, None)
        label = res
        if res == 'goal':
            g = E[k]['data']
            if g.get('team') == t and g.get('method') != 'own_goal': shot_goals[t] += 1; shot_points[t] += g.get('points', 0)
            else: label = 'goal_for_opponent'
        elif res == 'opponent': label = 'controlled_by_opponent'
        elif res in ('other_teammate', 'intended_receiver'): label = 'controlled_by_teammate'
        elif res == 'other': label = 'other'; shot_other[why] += 1
        shot_out[label] += 1; band[key][0] += 1; band[key][1] += label == 'goal'
    shots_block = {'attempts': sum(shot_out.values()), 'outcomes': dict(shot_out), 'other_reasons': dict(shot_other),
                   'launch_distance_to_attacked_goal_m': _stats(launch_dist),
                   'by_launch_territory_of_attacked_goal': {k: {'attempts': v[0], 'goals': v[1],
                        'conversion': round(v[1] / v[0], 4) if v[0] else None} for k, v in band.items()},
                   'keeper_deliberate_touches': sum(e['event'] == 'touch' and e['data'].get('deliberate', True) and e['data'].get('player') == keeper[i].get(_team(e['data'].get('player')))
                                                    for i, e in enumerate(E)),
                   'deliberate_touches_by_others': sum(e['event'] == 'touch' and e['data'].get('deliberate', True) and e['data'].get('player') != keeper[i].get(_team(e['data'].get('player')))
                                                       for i, e in enumerate(E)),
                   'unsecured_catch_deflections': sum(e['event'] == 'touch' and not e['data'].get('deliberate', True) for e in E),
                   'attack_orientation_consistent_with_goals': orientation_checked}

    # ---- per-team possession and scoring summary ----------------------
    per_team = {}
    for t in ('A', 'B'):
        ps = [p for p in possessions if p['team'] == t]; att = [p for p in ps if p['shots'] > 0]
        shots = shots_by_team[t]
        per_team[t] = {'possessions': len(ps), 'possessions_with_attempt': len(att),
                       'attempt_possession_fraction': round(len(att) / len(ps), 4) if ps else None,
                       'shot_attempts': shots,
                       'attempts_per_attempt_possession': round(sum(p['shots'] for p in att) / len(att), 4) if att else None,
                       'mean_possession_live_s': round(statistics.mean(p['live_s'] for p in ps), 3) if ps else None,
                       'points': score.get(t), 'points_per_possession': round(score.get(t, 0) / len(ps), 4) if ps else None,
                       'goals_from_shots': shot_goals[t], 'shot_conversion': round(shot_goals[t] / shots, 4) if shots else None,
                       'mean_value_of_converted_shots': round(shot_points[t] / shot_goals[t], 4) if shot_goals[t] else None,
                       'points_from_shots': shot_points[t], 'points_from_penalties': penalty_points[t],
                       'points_other': score.get(t, 0) - shot_points[t] - penalty_points[t],
                       'own_goals_conceded': sum(p['own_goals_conceded'] for p in ps)}
    total_poss = len(possessions)

    # ---- pass, kick and restart-pass ledgers --------------------------
    def ledger(kind):
        out = Counter(); other = Counter(); award = Counter(); released = 0
        for i, e in enumerate(E):
            if kind == 'restart_pass':
                if e['event'] != 'restart_release': continue
            elif e['event'] != 'release' or e['data']['kind'] != kind: continue
            released += 1
            rel = e['data'].get('player') or e['data'].get('taker'); tgt = e['data'].get('target')
            res, k, why = flight_outcome(i, rel, tgt)
            if res == 'goal': res, why = 'other', 'goal'
            if res == 'other': other[why] += 1
            if res == 'boundary': award[boundary_award(k)[0]] += 1
            out[res] += 1
        total = sum(out.values())
        return {'attempts': total, 'reconciled_with_release_count': total == released,
                'intended_receiver': out['intended_receiver'], 'other_teammate': out['other_teammate'],
                'opponent': out['opponent'], 'boundary': out['boundary'], 'other': out['other'], 'other_reasons': dict(other),
                'boundary_turnover': award['turnover'], 'boundary_same_team': award['same_team'], 'boundary_no_award': award['no_award'],
                'reached_intended_fraction': round(out['intended_receiver'] / total, 4) if total else None,
                'reached_any_teammate_fraction': round((out['intended_receiver'] + out['other_teammate']) / total, 4) if total else None,
                'boundary_fraction': round(out['boundary'] / total, 4) if total else None}

    # ---- boundaries: cause, and the award that belongs to each --------
    bcause = Counter(); baward = Counter()
    for i, e in enumerate(E):
        if e['event'] != 'boundary': continue
        cause = 'carrier_out' if e['data'].get('carrier') else 'after_' + (release_kind(i) or 'other')
        res, _k = boundary_award(i); bcause[cause] += 1; baward[cause + '|' + res] += 1
    b_turn = sum(v for k, v in baward.items() if k.endswith('|turnover')); b_same = sum(v for k, v in baward.items() if k.endswith('|same_team'))
    boundaries = {'total': sum(bcause.values()), 'by_cause': dict(bcause), 'by_cause_and_award': dict(baward),
                  'turnovers': b_turn, 'same_team_restarts': b_same, 'no_award': sum(bcause.values()) - b_turn - b_same,
                  'turnovers_per_100_possessions': round(100 * b_turn / total_poss, 2) if total_poss else None,
                  'missed_shot_turnovers': baward.get('after_shot|turnover', 0)}

    # ---- contact ------------------------------------------------------
    wraps = [i for i, e in enumerate(E) if e['event'] == 'engagement' and e['data'].get('kind') == 'tackle']
    wrap_end = Counter(); wrap_ms = []
    for i in wraps:
        tgt = E[i]['data']['target']; t0 = E[i]['t_ms']; res = 'unresolved'; f = None
        for f in E[i + 1:]:
            fe = f['event']
            if fe == 'release' and f['data'].get('player') == tgt: res = 'carrier_released'; break
            if fe == 'tackle_award' and f['data'].get('target') == tgt: res = 'tackle_completed'; break
            if fe == 'tackle_count' and f['data'].get('carrier') == tgt: res = 'tackle_completed'; break
            if fe == 'strip' and f['data'].get('target') == tgt: res = 'strip'; break
            if fe == 'freeze' and f['data'].get('player') == tgt: res = 'freeze'; break
            if fe in ('boundary', 'goal', 'period_end', 'held_ball', 'restart_awarded'): res = fe; break
        wrap_end[res] += 1
        if res != 'unresolved': wrap_ms.append(f['t_ms'] - t0)
    tackles_by = (Counter(_team(e['data'].get('tackler')) for e in E if e['event'] == 'tackle_count') if counted
                  else Counter(_team(e['data'].get('actor')) for e in E if e['event'] == 'tackle_award'))
    contact = {'completed_tackles': sum(tackles_by.values()), 'completed_tackles_by_team': dict(tackles_by),
               'strips': sum(e['event'] == 'strip' for e in E), 'tackle_engagements': len(wraps),
               'block_engagements': sum(e['event'] == 'engagement' and e['data'].get('kind') == 'block' for e in E),
               'wrap_next_endpoint': dict(wrap_end),
               'wrap_time_to_next_endpoint_s': {**_stats([m / 1000 for m in wrap_ms]),
                    'note': 'PROXY: time from a wrap starting to the next release, tackle, strip, freeze or stoppage. It does not observe the grip breaking.'},
               'possessions_ended_by_tackle': sum(p['end_cause'] == 'tackle' for p in possessions),
               'possessions_with_tackle_and_attempt': sum(p['tackles_against'] > 0 and p['shots'] > 0 for p in possessions)}

    # ---- stoppages and flow: each award matched to its own release ----
    aw_idx = [i for i, e in enumerate(E) if e['event'] == 'restart_awarded']
    dead_ordinary = []; superseded = 0; by_reason = Counter()
    for a in aw_idx:
        reason = E[a]['data'].get('reason'); by_reason[reason] += 1; rel = None
        for k in range(a + 1, n):
            fe = E[k]['event']
            if fe == 'restart_release': rel = k; break
            if fe in ('restart_awarded', 'period_end', 'match_complete', 'penalty_start'): break
        if rel is None: superseded += 1
        elif reason not in ('quarter_start', 'overtime_half'): dead_ordinary.append((E[rel]['t_ms'] - E[a]['t_ms']) / 1000)
    stretches = []; start = None
    for e in E:
        if e['event'] in ('restart_release', 'opening_ground_touch'): start = e['live_ms']
        elif e['event'] == 'restart_awarded' and start is not None: stretches.append((e['live_ms'] - start) / 1000); start = None
    inter = sum(e['data'].get('duration_ms', 0) for e in E if e['event'] == 'intermission') / 1000
    live = E[-1]['live_ms'] / 1000; elapsed = E[-1]['t_ms'] / 1000
    flow = {'live_s': live, 'elapsed_s': elapsed, 'intermission_s': inter,
            'active_share_including_intermissions': round(live / elapsed, 4) if elapsed else None,
            'active_share_excluding_intermissions': round(live / (elapsed - inter), 4) if elapsed > inter else None,
            'restarts': len(aw_idx), 'restarts_by_reason': dict(by_reason), 'restart_setups_superseded_or_unreleased': superseded,
            'restarts_per_live_minute': round(60 * len(aw_idx) / live, 3) if live else None,
            'ordinary_restart_dead_s': _stats(dead_ordinary), 'live_stretch_between_stoppages_s': _stats(stretches),
            'possession_live_s': _stats([p['live_s'] for p in possessions])}

    # ---- archery and discipline --------------------------------------
    after_freeze = Counter()
    for i, e in enumerate(E):
        if e['event'] != 'freeze': continue
        who = e['data']['player']; res = 'unresolved'
        for f in E[i + 1:]:
            if f['event'] == 'control': res = 'same_team' if _team(f['data']['player']) == _team(who) else 'opponent'; break
            if f['event'] in ('boundary', 'goal', 'period_end'): res = f['event']; break
        after_freeze[res] += 1
    archery = {'arrows': sum(e['event'] == 'arrow_release' for e in E), 'freezes': sum(e['event'] == 'freeze' for e in E),
               'next_control_after_freeze': dict(after_freeze)}
    fouls = dict(Counter(e['data'].get('reason') for e in E if e['event'] == 'foul'))

    c2_log = any(e['event'] in _C2_EVENTS for e in E)
    return {'measurement_version': MEASUREMENT_VERSION,
            'score': score, 'total_possessions': total_poss, 'per_team': per_team,
            'possession_end_causes': dict(Counter(p['end_cause'] for p in possessions)),
            'possession_start_causes': dict(Counter(p['start_cause'] for p in possessions)),
            'goals_by_method': dict(Counter(g['method'] for g in goals)),
            'goals_by_source_release': dict(Counter(str(g['source']) for g in goals)),
            'goal_origin_distance_m': goal_distance, 'shots': shots_block,
            'pass_ledger': ledger('pass'), 'kick_ledger': ledger('kick'), 'restart_pass_ledger': ledger('restart_pass'),
            'pass_plans_failed': sum(e['event'] == 'pass_plan_failed' for e in E),
            'boundaries': boundaries, 'contact': contact, 'flow': flow, 'archery': archery, 'fouls_by_reason': fouls,
            **({'continuation': _c2_measures(E, possessions, n)} if c2_log else {}),
            'unavailable_in_this_checkpoint': ['support-foot scoring origin'] + ([] if c2_log else ['occupancy and marking states']) +
                ['get-up durations'] + ([] if c2_log else ['tackle count transitions', 'reconstruction and clearance']) + [
                'containment and controlled descent', 'grip, impulse and posture witnesses', 'separate Keeper save/parry classes',
                'true wrap duration (only a proxy is available)']}

_C2_EVENTS = {'tackle_count', 'recovery_started', 'reconstruction_set', 'occupancy_cleared', 'attacking_zone_expiry',
              'defensive_unmarked_expiry', 'zone_exit_invalid', 'zone_exit_valid'}

def _c2_measures(E, possessions, n):
    """M1.3 additions. Everything here is read from the event log alone."""
    def count(name, **match):
        return sum(e['event'] == name and all(e['data'].get(k) == v for k, v in match.items()) for e in E)
    tc = [e for e in E if e['event'] == 'tackle_count']
    transitions = Counter('%s->%s' % (e['data'].get('count_from'), e['data'].get('count_to')) for e in tc)
    first = [e for e in tc if e['data'].get('count_from') == 0 and e['data'].get('procedure') != 'turnover']
    tackles = {'count_transitions': dict(transitions),
               'completed_tackles': len(tc),
               'first_tackles': len(first), 'second_tackles': sum(e['data'].get('count_to') == 2 for e in tc),
               'turnover_on_only_tackle': sum(e['data'].get('procedure') == 'turnover' and e['data'].get('count_from') == 0 for e in tc),
               'first_tackle_by_place': dict(Counter(e['data'].get('where') for e in first)),
               'first_tackle_by_procedure': dict(Counter(e['data'].get('procedure') for e in first)),
               'counts_restored_by_failed_advantage': count('tackle_count_restored'),
               'possessions_by_tackles_against': dict(Counter(str(p['tackles_against']) for p in possessions)),
               'possessions_with_tackle_then_goal': sum(bool(p['tackle_times']) and any(g > p['tackle_times'][0] for g in p['goal_times']) for p in possessions),
               'points_after_a_tackle_in_same_possession': None}
    # ---- live recoveries: one outcome each -----------------------------
    rec_out = Counter(); pickup_ms = []; by_carrier = 0; first_action = Counter(); to_engage = []; to_action = []
    for i, e in enumerate(E):
        if e['event'] not in ('recovery_started', 'recovery_resumed'): continue
        carrier = e['data'].get('carrier'); res = 'unresolved_at_export'
        for k in range(i + 1, n):
            f = E[k]; fe = f['event']
            if fe == 'recovery_pickup':
                res = 'picked_up'; pickup_ms.append(f['data'].get('elapsed_ms')); who = f['data'].get('player'); by_carrier += who == carrier
                t0 = f['t_ms']; nxt = None
                for g in E[k + 1:]:
                    ge = g['event']
                    if ge == 'engagement' and g['data'].get('target') == who: nxt = 'engaged_before_first_action'; to_engage.append(g['t_ms'] - t0); break
                    if ge == 'release' and g['data'].get('player') == who: nxt = 'acted_before_engagement'; to_action.append(g['t_ms'] - t0); break
                    if ge in ('possession_change', 'restart_awarded', 'period_end', 'goal', 'boundary', 'freeze'): nxt = 'ended_otherwise:' + ge; break
                first_action[nxt or 'unresolved'] += 1; break
            if fe == 'recovery_failed': res = 'failed:' + str(f['data'].get('reason')); break
            if fe == 'recovery_interrupted': res = 'interrupted:' + str(f['data'].get('cause')).split(':')[0]; break
            if fe == 'recovery_superseded': res = 'superseded:' + str(f['data'].get('reason')); break
            if fe in ('period_end', 'match_complete'): res = 'period_end'; break
        rec_out[('replacement_' if e['event'] == 'recovery_resumed' else '') + res] += 1
    obstruction = [e for e in E if e['event'] == 'recovery_obstruction']
    recovery = {'started': count('recovery_started'), 'replacement_recoveries': count('recovery_resumed'),
                'outcomes': dict(rec_out), 'pickup_elapsed_s': _stats([m / 1000 for m in pickup_ms if m is not None]),
                'picked_up_by_tackled_carrier': by_carrier,
                'after_pickup': dict(first_action),
                'pickup_to_new_engagement_s': _stats([m / 1000 for m in to_engage]),
                'pickup_to_first_release_s': _stats([m / 1000 for m in to_action]),
                'opponent_bodies_in_disc': len(obstruction), 'of_which_unavoidable': sum(bool(e['data'].get('unavoidable')) for e in obstruction),
                'body_inside_disc_m': _stats([e['data'].get('body_inside_disc_m') for e in obstruction if e['data'].get('body_inside_disc_m') is not None]),
                'interference_fouls': sum(e['event'] == 'foul' and e['data'].get('reason') in ('recovery_interference', 'exclusive_recovery', 'protected_recovery') for e in E),
                'note': 'Get-up time is the fixed Pocket 1.1 value in this checkpoint, so recovery timings are provisional.'}
    # ---- inbounds --------------------------------------------------------
    inb_out = Counter(); setup = []; retakes = []
    for i, e in enumerate(E):
        if e['event'] != 'restart_awarded' or e['data'].get('reason') != 'zone_inbound': continue
        res = 'unresolved_at_export'; team = e['data'].get('team'); again = 0
        for k in range(i + 1, n):
            f = E[k]; fe = f['event']
            if fe == 'restart_release':
                setup.append((f['t_ms'] - e['t_ms']) / 1000); res = 'released_unresolved'
                for g in E[k + 1:]:
                    ge = g['event']
                    if ge == 'control': res = 'released_to_teammate' if _team(g['data']['player']) == team else 'released_to_opponent'; break
                    if ge in ('boundary', 'restart_awarded', 'period_end', 'goal', 'no_goal'): res = 'released_then_' + ge; break
                break
            if fe == 'restart_awarded':
                r = f['data'].get('reason'); same = f['data'].get('team') == team
                if same and r in ('defensive_restart_fault', 'foul'): again += 1; continue      # retake at the same mark, inside this inbound
                res = ('retained_then_' if same else 'lost_before_release:') + str(r); break
            if fe in ('period_end', 'match_complete'): res = 'period_end'; break
        inb_out[res] += 1; retakes.append(again)
    cleared = [e for e in E if e['event'] == 'reconstruction_cleared']
    inbound = {'awarded': count('restart_awarded', reason='zone_inbound'), 'outcomes': dict(inb_out),
               'retakes_after_defensive_fault': sum(retakes), 'inbounds_retaken': sum(r > 0 for r in retakes), 'inbounds_retaken_more_than_once': sum(r > 1 for r in retakes),
               'retake_note': 'Only retakes inside an inbound sequence (zone_inbound award up to its release or loss). Faults at ordinary free passes are not counted here.',
               'award_to_release_dead_s': _stats(setup)}
    reconstruction = {'set': count('reconstruction_set'), 'cleared': len(cleared),
                      'clearance_witness': dict(Counter(e['data'].get('witness') for e in cleared)),
                      'live_s_to_clearance': _stats([e['data'].get('live_ms_uncleared', 0) / 1000 for e in cleared]),
                      'ended_uncleared': dict(Counter(e['data'].get('reason') for e in E if e['event'] == 'reconstruction_ended')),
                      'goals_disallowed_uncleared': sum(e['event'] == 'no_goal' and e['data'].get('reason') == 'reconstruction_uncleared' for e in E),
                      'no_finishing_flight_at_horn': count('no_finishing_flight'), 'restored_by_failed_advantage': count('reconstruction_restored')}
    att = [e for e in E if e['event'] == 'attacking_zone_expiry']
    occupancy = {'attacking_expiries': len(att),
                 'attacking_expiries_with_possible_exit_interference': sum(bool(e['data'].get('possible_exit_interference')) for e in att),
                 'exit_interference_note': 'POSSIBLE exit interference only: the player was moving outward while in an opponent engagement. '
                                           'Exit routes are not modelled in this checkpoint, so this is not a finding of obstruction.',
                 'defensive_unmarked_expiries': count('defensive_unmarked_expiry'),
                 'valid_arc_exits_with_stored_time': count('zone_exit_valid'),
                 'invalid_end_line_exits_with_stored_time': count('zone_exit_invalid'),
                 'reentries_without_reset': count('zone_reentry_no_reset'),
                 'clearings_on_possession_change': count('occupancy_cleared')}
    recalled = [i for i, e in enumerate(E) if e['event'] == 'advantage_recalled']
    advantage = {'given': count('advantage'), 'realized': count('advantage_realized'), 'recalled': len(recalled),
                 'state_restored_to_foul_instant': count('advantage_state_restored')}
    tackles['points_after_a_tackle_in_same_possession'] = sum(p['points'] for p in possessions if p['tackle_times'] and any(g > p['tackle_times'][0] for g in p['goal_times']))
    return {'tackles': tackles, 'recovery': recovery, 'inbound': inbound, 'reconstruction': reconstruction,
            'occupancy': occupancy, 'advantage': advantage}

def measure_c3(log):
    """M1.4: contact and around-the-tackle measures. Reads the event log only. M1.3 (measure) is untouched and every M1.3
    definition keeps its meaning, including the wrap proxy. A measure whose witness is not in the log is reported as
    'unavailable', never as zero: a C2 log has no kernel witness at all, and a C3a log has none of the C3b ones."""
    import collections
    U = 'unavailable'
    names = collections.Counter(e['event'] for e in log)
    kernel = any(n.startswith('c3_') for n in names)
    c3b = names.get('c3b_rules', 0) > 0
    out = {'measurement': 'M1.4', 'kernel_witness_in_log': kernel, 'c3b_witness_in_log': c3b}
    D = lambda name: [e['data'] for e in log if e['event'] == name]
    # ---- body collisions ----
    if not kernel:
        out['collisions'] = U; out['holds'] = U; out['groundings'] = U
    else:
        col = D('c3_collision'); wit = [w for c in col for w in c['responsibility']]
        out['collisions'] = {
            'count': len(col), 'pair_impulse_Ns': _stats([c['impulse_Ns'] for c in col]), 'closing_mps': _stats([c['closing_mps'] for c in col]),
            'with_a_carrier': sum(c.get('carrier') is not None for c in col),
            'shock_on_either_athlete': _stats([x for c in col for x in (c['shock_a'], c['shock_b'])]),
            'athletes_who_initiated': sum(bool(w.get('initiated')) for w in wit),
            'initiated_and_material': (sum(bool(w.get('initiated')) and bool(w.get('material')) for w in wit) if any('material' in w for w in wit) else U) if wit else 0,
            'unlawful_by_classification': dict(collections.Counter(w['classification'] for w in wit if w['classification'] != 'legal' and w.get('initiated'))),
            'fouls': dict(collections.Counter(w['foul'] for w in wit if w.get('foul'))),
            'not_sanctioned': dict(collections.Counter(w['not_sanctioned'] for w in wit if w.get('not_sanctioned'))),
        }
        # ---- holds: the true duration, from the witnessed start and end of each hold. The M1.3 wrap proxy is not replaced. ----
        ends = D('c3_hold_end'); starts = D('c3_hold_start'); reach_s = sum(h['reach_ms'] for h in ends) / 1000
        strips = sum(1 for e in log if e['event'] == 'strip')
        out['holds'] = {
            'started': len(starts), 'ended': len(ends), 'region_at_start': dict(collections.Counter(h['region'] for h in starts)),
            'true_duration_ms': _stats([h['duration_ms'] for h in ends]), 'time_within_reach_ms': _stats([h['reach_ms'] for h in ends]),
            'peak_grip': _stats([h['peak_grip'] for h in ends]), 'reached_tackle_grip_0_3': sum(h['peak_grip'] >= .3 for h in ends),
            'ended_by': dict(collections.Counter(h['cause'] for h in ends)),
            'true_duration_ms_by_end': {c: _stats([h['duration_ms'] for h in ends if h['cause'] == c]) for c in sorted({h['cause'] for h in ends})},
            'longest_ms': max([h['duration_ms'] for h in ends], default=None),
            'transmitted_impulse_Ns': _stats([h['impulse_Ns'] for h in ends]),
            'lawful_hold_seconds': round(reach_s, 3), 'strips': strips, 'strips_per_lawful_hold_second': round(strips / reach_s, 5) if reach_s > 0 else None,
            'contained_ms': (_stats([h['contained_ms'] for h in ends if h.get('contained_ms', 0) > 0]) if c3b else U),
        }
        gr = D('c3_grounding')
        out['groundings'] = {
            'count': len(gr), 'counted_tackles': sum(bool(g.get('counted')) for g in gr), 'by_class': dict(collections.Counter(g['cls'] for g in gr)),
            'by_manner': dict(collections.Counter(g['manner'] for g in gr if 'manner' in g)) if c3b else U,
            'balance_episode_ms': _stats([g['episode_ms'] for g in gr]),
            'lawful_defensive_share_carrier': _stats([g['lawful_defensive_share'] for g in gr if 'lawful_defensive_share' in g]),
        }
    if not c3b:
        for k in ('get_up', 'descent', 'containment', 'zone_expiries_by_exit_class', 'exit_obstructions', 'recovery_compliance'): out[k] = U
    else:
        # ---- get-up: predicted when he goes down (c3_down), observed when he is upright (c3_upright) ----
        downs = [e for e in log if e['event'] == 'c3_down']; ups = D('c3_upright')
        tackled = {(e['t_ms'], e['data']['player']) for e in log if e['event'] == 'c3_grounding' and e['data'].get('counted')}
        car = [e['data'] for e in downs if (e['t_ms'], e['data']['player']) in tackled]; oth = [e['data'] for e in downs if (e['t_ms'], e['data']['player']) not in tackled]
        g = lambda rows: {'n': len(rows), 'speed_going_down_mps': _stats([r['speed_mps'] for r in rows]), 'slide_ms': _stats([r['slide_ms'] for r in rows]), 'rise_ms': _stats([r['rise_ms'] for r in rows]),
                          'predicted_down_ms': _stats([r['slide_ms'] + r['rise_ms'] for r in rows])}
        out['get_up'] = {'tackled_carriers': g(car), 'others_grounded': g(oth), 'observed_down_ms': _stats([u['down_ms'] for u in ups]), 'went_down': len(downs), 'got_up': len(ups)}
        de = D('c3_descent_end')
        out['descent'] = {'attempts': names.get('c3_descent_start', 0), 'ended_by': dict(collections.Counter(d['cause'] for d in de)), 'duration_ms': _stats([d['duration_ms'] for d in de]),
                          'own_load_at_end': _stats([d['own_load'] for d in de])}
        ex = D('attacking_zone_expiry')
        out['containment'] = {'episodes': names.get('c3_containment', 0), 'expiries_while_contained': sum(e.get('exit_class') == 'carrier_contained' for e in ex)}
        out['zone_expiries_by_exit_class'] = dict(collections.Counter(e.get('exit_class', 'unclassified') for e in ex))
        out['exit_obstructions'] = names.get('exit_obstruction', 0)
        ob = [d for d in D('exit_obstruction') if 'denied_ms_by_opponent' in d.get('exit', {})]   # C3b3 records only
        out['exit_obstruction_detail'] = {'zone_ms_given_back': sum(d['exit']['denied_ms'] for d in ob), 'with_more_than_one_opponent_denying': sum(len(d['exit']['denied_ms_by_opponent']) > 1 for d in ob),
                                          'penalised_opponent_was_not_the_last_to_run_into_him': sum(d['by'] != d['exit']['last_contact_by'] for d in ob)}
        rc = D('recovery_compliance'); cl = D('recovery_cleared'); ob = D('recovery_obstruction')
        out['recovery_compliance'] = {
            'recoveries': len(rc), 'holders_given_grace_besides_the_tackler': sum(len(r['holders_with_grace']) for r in rc),
            'reaction_ms': _stats([v for r in rc for v in r['reaction_ms'].values()]),
            'found_inside_the_disc': len(ob), 'of_which_unable_to_move': sum(bool(o['unavoidable']) for o in ob), 'of_which_entered_late': sum(bool(o.get('entered_late')) for o in ob),
            'cleared': len(cl), 'necessary_movement_m': _stats([c['necessary_m'] for c in cl]), 'took_ms': _stats([c['took_ms'] for c in cl]), 'allowed_ms': _stats([c['allowed_ms'] for c in cl]),
            'attributable_delay_ms': _stats([c['attributable_delay_ms'] for c in cl]), 'cleared_late': sum(c['attributable_delay_ms'] > 0 for c in cl),
        }
    # ---- C3c: pinning, tucks, strips in a pinned wind-up, grips worked loose, where contacts came from ----
    c3c = names.get('c3c_rules', 0) > 0; out['c3c_witness_in_log'] = c3c
    if not c3c: out['pinning_and_escape'] = U; out['approach_bearing'] = U
    else:
        tk = D('c3_tuck'); wh = D('c3_release_withheld'); sw = D('c3_strip_in_wind_up'); gb = D('c3_grip_broken'); rs = D('c3_restraint')
        why = lambda h: 'wind_up_seen' if h.get('release_preparation_observed') else 'pass_open' if h.get('pass_open_observed') else 'neither'
        out['pinning_and_escape'] = {
            'hold_region_by_what_the_defender_saw': {k: dict(collections.Counter(why(h) for h in starts if h['region'] == k)) for k in ('upper', 'lower')},
            'releases_withheld_spells': len(wh), 'tucks': len(tk), 'tuck_stalled_ms': _stats([x['stalled_ms'] for x in tk]),
            'releases_made_under_restraint': len(rs), 'restraint_at_release': _stats([x['restraint'] for x in rs]),
            'strips_in_a_pinned_wind_up': len(sw), 'strip_modifier': _stats([x['modifier'] for x in sw]),
            'grips_worked_below_the_tackle_threshold': len(gb), 'holds_with_a_grip_broken': sum(bool(h.get('grip_broken')) for h in ends),
            'of_which_ended_out_of_reach': sum(bool(h.get('grip_broken')) and h['cause'] == 'out_of_reach' for h in ends),
            'of_which_ended_with_the_carrier_grounded': sum(bool(h.get('grip_broken')) and h['cause'] == 'carrier_grounded' for h in ends),
            'escape_effort_ms_per_hold': _stats([h.get('escape_effort_ms', 0) for h in ends]),
            # C3c2: actual detachment, kept apart from a grip merely worked below the tackle threshold
            'holds_pried_off': sum(x['cause'] == 'pried_off' for x in D('c3_hold_detached')), 'of_which_had_been_material': sum(x['cause'] == 'pried_off' and x['peak_grip'] >= .3 for x in D('c3_hold_detached')),
            'grabs_fended_off_with_no_grip': sum(x['cause'] == 'fended_off' for x in D('c3_hold_detached')),
            'ms_held_before_pried_off': _stats([x['hold_ms'] for x in D('c3_hold_detached') if x['cause'] == 'pried_off']),
            'new_holds_taken_after_being_thrown_off': sum('ms_since_his_last_hold_was_thrown_off' in h for h in starts),
        }
        bins = (('ahead_0_to_90', 0, 90), ('side_rear_90_to_135', 90, 135), ('rear_quarter_135_to_165', 135, 165), ('rear_165_to_180', 165, 180.01))
        mat = [w for w in wit if w.get('initiated') and w.get('material') and 'bearing_from_facing_deg' in w]
        out['approach_bearing'] = {'of_material_initiated_contacts': {n_: sum(lo <= w['bearing_from_facing_deg'] < hi for w in mat) for n_, lo, hi in bins},
                                   'classed_blindside': sum(w['classification'] == 'blindside' for w in mat), 'note': 'degrees round from the facing of the athlete hit: 0 head-on, 180 straight behind'}
    # ---- fouls by reason; classifiers that active C3 no longer has are shown apart ----
    fr = collections.Counter(e['data']['reason'] for e in log if e['event'] == 'foul'); removed = ('contact_speed',)
    out['fouls'] = {'by_reason': {k: v for k, v in sorted(fr.items()) if k not in removed},
                    'removed_classifiers': {k: (fr.get(k, 0) if not kernel else 'classifier removed in active C3; none can occur') for k in removed}}
    return out

def report_qualifications(m4):
    """Where a note printed or saved with the M1.3 measures is no longer true of this build, say so beside it. M1.3 is not edited."""
    q = []
    if isinstance(m4, dict) and m4.get('c3b_witness_in_log'):
        q.append("C3b QUALIFICATION OF AN M1.3 NOTE: measures['continuation']['recovery']['note'] says get-up is the fixed Pocket 1.1 value. "
                 "That is NOT true of this match. Under C3b a grounded athlete slides and then rises for a modelled time; the tackle no longer "
                 "stops him. Get-up and recovery-compliance figures are in measures_c3['get_up'] and measures_c3['recovery_compliance']. "
                 "The M1.3 numbers themselves are computed exactly as before.")
    return q

def qualification_text(summary):
    q = summary.get('report_qualifications') or []
    return ''.join('\n*** ' + x for x in q)

def measure_c4(log):
    """M1.5: additions beside M1.3 (measure) and M1.4 (measure_c3), which are not touched and keep every definition. Reads the
    event log only. A measure whose witness is not in the log is 'unavailable', never zero.
    1. Terminal integrity: completion, forfeit and abandonment records, and anything written after the result.
    2. Keeper Zone violations under the ruling of 7 October (witness: the c4_rules marker).
    3. Time on the ground, split: wall clock, live time and time not live between going down and getting up, against the
       predicted time; intervals that cross a period end are counted and reported apart (a break is wall time, not play).
    4. Arrows followed by their own id from release to what became of them. M1.4 and the C3 campaign decomposition looked a
       few records ahead for a freeze; this joins on the arrow id and nothing else."""
    import collections
    U = 'unavailable'
    names = collections.Counter(e['event'] for e in log)
    out = {'measurement': 'M1.6', 'c4_zone_witness_in_log': names.get('c4_rules', 0) > 0}
    D = lambda name: [e['data'] for e in log if e['event'] == name]
    # ---- 1. terminal integrity ----
    done = [i for i, e in enumerate(log) if e['event'] == 'match_complete']
    out['terminal'] = {'match_complete_records': len(done), 'forfeit_records': names.get('forfeit', 0), 'abandoned_records': names.get('abandoned', 0),
                       'records_after_the_first_match_complete': (len(log) - done[0] - 1) if done else U,
                       'sanctions_not_administered': sum(len(d['sanctions']) for d in D('sanctions_not_administered')),
                       'grounds_not_applied_at_a_deciding_horn': len(D('terminal_ground_not_applied'))}
    # ---- 2. zone violations ----
    if not out['c4_zone_witness_in_log']:
        out['zone_violations'] = U
    else:
        zv = [e for e in log if e['event'] == 'zone_violation']; comp = D('zone_compliance'); iv = D('zone_overdue_intervention')
        # C4a correction (the Lead's C4.0r2 acceptance): only the penalty remedies are penalty runs. Each is linked to the penalty_start
        # that its own call opened (the first one after it at the same match time), and that run to its own outcome, once each. An offset
        # violation is not a run. C4.0 M1.5 counted every remedy other than a reset as a run and took the next outcome in the log.
        PEN = ('penalty_run', 'direct_penalty_run'); used = set(); pen = []; no_run = 0
        for i, e in enumerate(log):
            if e['event'] != 'zone_violation' or e['data']['remedy'] not in PEN: continue
            j = next((k for k in range(i + 1, len(log)) if log[k]['event'] == 'penalty_start' and log[k]['t_ms'] == e['t_ms'] and k not in used), None)
            if j is None: no_run += 1; continue
            used.add(j)
            pen.append(next((g for g in log[j + 1:] if g['event'] in ('penalty_goal_scored', 'penalty_failed', 'penalty_start', 'match_complete')), None))
        pen = [g if g is not None and g['event'] in ('penalty_goal_scored', 'penalty_failed') else None for g in pen]
        tc = D('tackle_count')
        out['zone_violations'] = {
            'violations': len(zv), 'by_remedy': dict(collections.Counter(e['data']['remedy'] for e in zv)),
            'by_team_defending': dict(collections.Counter(e['data']['team'] for e in zv)),
            'defenders_per_violation': dict(sorted(collections.Counter(len(e['data']['participants']) for e in zv).items())),
            'by_ground': dict(collections.Counter(p['ground'] for e in zv for p in e['data']['participants'] if 'ground' in p)),
            'possessions_with_a_violation': sum(1 for e in zv if e['data']['number_in_possession'] == 1),
            'first_violations_with_advantage_already_pending': sum(bool(e['data'].get('advantage_already_pending')) for e in zv if e['data']['remedy'] == 'tackle_count_reset'),
            'first_violations_in_a_recovery': sum(bool(e['data'].get('recovery_in_progress')) for e in zv if e['data']['remedy'] == 'tackle_count_reset'),
            'tackle_count_reset_from': dict(collections.Counter(e['data']['tackle_count_from'] for e in zv if e['data']['remedy'] == 'tackle_count_reset')),
            'possession_clock_added_ms': _stats([e['data']['p_ms_to'] - e['data']['p_ms_from'] for e in zv if e['data']['remedy'] == 'tackle_count_reset']),
            'compliance_time_allowed_ms': _stats([p['compliance']['allowed_ms'] for e in zv for p in e['data']['participants'] if 'compliance' in p]),
            'compliance_outcomes': dict(collections.Counter(c['how'] for c in comp)),
            'compliance_ms_to_spare': _stats([c['ms_before_deadline'] for c in comp if c['how'] != 'possession_ended']),
            'offset_violations': sum(1 for e in zv if e['data']['remedy'] == 'offset_by_simultaneous_attacking_offence'),
            'penalty_runs_from_violations': len(pen), 'penalty_violations_without_a_run': no_run, 'penalty_runs_without_an_outcome_recorded': sum(1 for g in pen if g is None),
            'penalty_runs_scored': sum(1 for g in pen if g and g['event'] == 'penalty_goal_scored'),
            'penalty_points': sum(g['data']['points'] for g in pen if g and g['event'] == 'penalty_goal_scored'),
            'overdue_interventions': dict(collections.Counter(d['act'] for d in iv)),
            'tackles_after_a_reset_in_the_same_possession': sum(1 for d in tc if 'ordinal_in_possession' in d and d['ordinal_in_possession'] > d['count_to']),
        }
    # ---- 3. time on the ground ----
    if names.get('c3_down', 0) == 0:
        out['grounded_exposure'] = U
    else:
        open_ = {}; rows = []; ends = [e['t_ms'] for e in log if e['event'] == 'period_end']
        for e in log:
            if e['event'] == 'c3_down':
                open_[e['data']['player']] = (e, e['data']['slide_ms'] + e['data']['rise_ms'])
            elif e['event'] == 'c3_upright' and e['data']['player'] in open_:
                d, pred = open_.pop(e['data']['player']); wall = e['t_ms'] - d['t_ms']; live = e['live_ms'] - d['live_ms']
                rows.append({'wall': wall, 'live': live, 'not_live': wall - live, 'predicted': pred, 'crosses_period_end': any(d['t_ms'] < t <= e['t_ms'] for t in ends), 'wall_minus_predicted': wall - pred})
        inside = [r for r in rows if not r['crosses_period_end']]; across = [r for r in rows if r['crosses_period_end']]
        S = lambda rs, k: _stats([r[k] for r in rs])
        out['grounded_exposure'] = {'intervals': len(rows), 'still_down_at_end_of_log': len(open_), 'crossing_a_period_end': len(across),
                                    'within_a_period': {k + '_ms': S(inside, k) for k in ('wall', 'live', 'not_live', 'predicted', 'wall_minus_predicted')},
                                    'crossing_a_period_end_wall_ms': S(across, 'wall'), 'crossing_a_period_end_live_ms': S(across, 'live'),
                                    'note': 'wall = elapsed match time from going down to upright; live = the part of it in live play; not_live = dead ball, finishing flight, penalty, review and breaks. M1.4 observed_down_ms is the wall figure over all intervals.'}
    # ---- 4. arrows, joined by arrow id ----
    rel = {e['data']['arrow']: e for e in log if e['event'] == 'arrow_release'}
    if not rel:
        out['arrows_by_id'] = U
    else:
        fate = {a: [] for a in rel}
        for e in log:
            a = e['data'].get('arrow') if isinstance(e.get('data'), dict) else None
            if a in fate and e['event'] != 'arrow_release': fate[a].append(e)
        def outcome(evs):
            for e in evs:
                if e['event'] == 'freeze': return 'freeze_of_carrier' if e['data'].get('was_carrier') else 'freeze_other'
                if e['event'] == 'inert_impact': return 'inert:' + str(e['data'].get('reason', 'not_valid'))
                if e['event'] in ('arrow_miss', 'arrow_ball', 'arrow_stop', 'arrow_retrieved'): return e['event']
            return 'no_outcome_recorded'
        res = {a: outcome(v) for a, v in fate.items()}
        panel = collections.Counter()
        for a, v in fate.items():
            g = next((e for e in v if e['event'] == 'arrow_geometry_impact' and e['data'].get('panel')), None)
            if g is not None: panel[('blocked by another body first' if g['data'].get('blocked') else 'not blocked') + ': ' + res[a]] += 1
        out['arrows_by_id'] = {'released': len(rel), 'outcome': dict(sorted(collections.Counter(res.values()).items())), 'panel_impacts_by_outcome': dict(sorted(panel.items())),
                               'note': 'no_outcome_recorded: the log has no record of what became of the arrow. Some were made dead by a stoppage (every arrow in flight is, silently); the rest ended without any record. Not a freeze in either case.',
                               'released_at_the_carrier_and_froze_him': sum(1 for a, e in rel.items() if res[a] == 'freeze_of_carrier' and e['data'].get('target') == next((g['data']['player'] for g in fate[a] if g['event'] == 'freeze'), None))}
    # ---- 5. contact by roster (C4a) ----
    mk = D('c4a_rules'); tab = mk[0]['strength_balance_tackling'] if mk else {}
    if not tab:
        out['contact_by_roster'] = U + (': uniform roster' if mk else '')
    else:
        lv = lambda pid, i: ('%.2f' % tab[pid][i]) if pid in tab else 'keeper_or_archer'
        ends = D('c3_hold_end'); pair = lambda h: 'holder strength %s | carrier strength %s' % (lv(h['actor'], 0), lv(h['target'], 0))
        tk = [g for g in D('c3_grounding') if g.get('counted')]
        out['contact_by_roster'] = {
            'design': mk[0]['contact_roster'], 'escape_allocation': mk[0]['escape_allocation'], 'region_policy': mk[0]['region_policy'],
            'holds_by_strength_pair': dict(sorted(collections.Counter(pair(h) for h in ends).items())),
            'pried_off_by_strength_pair': dict(sorted(collections.Counter(pair(h) for h in ends if h['cause'] == 'pried_off').items())),
            'fended_off_by_strength_pair': dict(sorted(collections.Counter(pair(h) for h in ends if h['cause'] == 'fended_off').items())),
            'unequal_encounters': sum(1 for h in ends if h['actor'] in tab and h['target'] in tab and tab[h['actor']][0] != tab[h['target']][0]),
            'counted_tackles_by_carrier_strength': dict(sorted(collections.Counter(lv(g['player'], 0) for g in tk).items())),
            'effort_weighted_prying_s': round(sum(h.get('escape_share_ms', 0) for h in ends) / 1000, 3),
        }
    # ---- 6. scoring origin (C4b): support foot against pelvis ----
    if names.get('c4b_rules', 0) == 0:
        out['scoring_origin'] = U
    else:
        rel = [e['data'] for e in log if e['event'] in ('release', 'strike') and isinstance(e['data'].get('origin'), dict) and not e['data'].get('forced')]
        shots = [d for d in rel if d.get('kind') == 'shot']
        ok_ = [d for d in shots if 'territory' in d['origin']]
        pair = collections.Counter('pelvis %s -> foot %s' % (d['origin']['pelvis_territory'], d['origin']['territory']) for d in ok_)
        gl = [e['data'] for e in log if e['event'] == 'goal']
        out['scoring_origin'] = {
            'releases_with_an_origin': len(rel), 'shots': len(shots), 'origin_rule': dict(collections.Counter(d['origin']['rule'] for d in rel)),
            'shots_by_pelvis_and_foot_territory': dict(sorted(pair.items())),
            'shots_whose_territory_the_foot_changes': sum(1 for d in ok_ if d['origin']['pelvis_territory'] != d['origin']['territory']),
            'foot_to_pelvis_distance_m': _stats([((d['origin']['origin'][0] - d['origin']['pelvis'][0]) ** 2 + (d['origin']['origin'][1] - d['origin']['pelvis'][1]) ** 2) ** .5 for d in ok_]),
            'goals_by_method': dict(collections.Counter(g['method'] for g in gl)), 'carry_goals': sum(1 for g in gl if g['method'] == 'carry'),
            'goal_points_by_method': {m_: sum(g['points'] for g in gl if g['method'] == m_) for m_ in sorted({g['method'] for g in gl})},
            'origin_to_goal_m': _stats([g['origin_to_goal_m'] for g in gl if g.get('origin_to_goal_m') is not None]),
            'note': 'territory changes are the support-foot classification against the pelvis classification of the same release, both on the radial geometry; origin_to_goal is from the support foot to the centre of the goal attacked.'}
    # ---- 7. the Keeper (C4c): every shot followed to its first decisive record ----
    if names.get('c4c_rules', 0) == 0:
        out['keeper'] = U
    else:
        END = ('goal', 'control', 'boundary', 'release', 'frame_contact', 'possession_change', 'no_goal')
        res = []; n = len(log)
        for i, e in enumerate(log):
            if e['event'] != 'release' or e['data'].get('kind') != 'shot' or e['data'].get('forced'): continue
            o = e['data'].get('origin') or {}; pel = o.get('pelvis')
            dist = min(((pel[0] - gx) ** 2 + (pel[1] - 50) ** 2) ** .5 for gx in (0, 100)) if pel else None
            read = None; kind = None; touched = None; j = i + 1
            while j < n:
                r = log[j]; ev = r['event']; d = r['data']
                if ev == 'keeper_read' and str(d.get('player', ''))[:1] != str(e['data'].get('player', ''))[:1] and (read is None or read.get('kind') == 'approach'): read = d #the defending Keeper's read (after an approach, the launch that follows)
                if ev == 'keeper_contact':
                    if d['kind'] == 'catch': kind = 'save'; break
                    if touched is None: touched = (d['kind'], d.get('deliberate'))
                elif ev == 'touch' and touched is None and not any(x['event'] == 'keeper_contact' and x['t_ms'] == r['t_ms'] for x in log[j + 1:j + 3]):
                    kind = 'field_deflection'; break
                elif ev in END:
                    same_t = [x['data'] for x in log[j + 1:j + 6] if x['event'] == 'keeper_contact' and x['t_ms'] == r['t_ms']]
                    if same_t and same_t[0]['kind'] == 'catch': kind = 'save'; break
                    if ev == 'possession_change':
                        ctl = [x['data'] for x in log[j + 1:j + 4] if x['event'] == 'control' and x['t_ms'] == r['t_ms']]
                        if ctl and touched is None: kind = 'caught_by_a_defender'; break
                    if touched is not None: kind = touched[0] + ('_then_goal' if ev == 'goal' else '_no_goal')
                    elif ev == 'goal': kind = 'goal_before_reaction' if read is None else 'goal_no_attempt' if read.get('kind') == 'none' else 'goal_missed_attempt'
                    elif ev == 'control': kind = 'caught_by_a_team_mate' if str(d.get('player', ''))[:1] == str(e['data'].get('player', ''))[:1] else 'caught_by_a_defender'
                    elif ev == 'frame_contact': kind = 'frame'
                    elif ev == 'boundary': kind = 'wide'
                    else: kind = 'other'
                    break
                j += 1
            res.append({'kind': kind or 'unresolved', 'dist': dist, 'read': read, 'touched': touched})
        band = lambda x: 'unknown' if x is None else 'under 10 m' if x < 10 else '10 to 15 m' if x < 15 else '15 to 20 m' if x < 20 else '20 m and over'
        isgoal = lambda r: r['kind'] in ('goal_before_reaction', 'goal_no_attempt', 'goal_missed_attempt', 'parry_then_goal', 'body_then_goal')
        bands = {}
        for r in res:
            b_ = bands.setdefault(band(r['dist']), {'shots': 0, 'goals': 0}); b_['shots'] += 1; b_['goals'] += isgoal(r)
        for b_ in bands.values(): b_['goal_fraction'] = round(b_['goals'] / b_['shots'], 4) if b_['shots'] else None
        reads = [r['read'] for r in res if r['read']]
        lands = D('keeper_landed'); gl = [e['data'] for e in log if e['event'] == 'goal']
        out['keeper'] = {
            'shots': len(res), 'outcomes': dict(sorted(collections.Counter(r['kind'] for r in res).items())),
            'by_launch_distance': dict(sorted(bands.items())),
            'reads': dict(collections.Counter(d.get('kind') for d in reads)), 'reads_feasible': sum(1 for d in reads if d.get('feasible')),
            'reads_unset_at_the_change_of_course': sum(1 for d in reads if d.get('unset')),
            'reaction_ms': _stats([d['reaction_ms'] for d in reads]),
            'dives': sum(1 for d in lands if d.get('dive')), 'jumps': sum(1 for d in lands if not d.get('dive')),
            'recovery_ms': _stats([d['recover_ms'] for d in lands if d.get('dive')]),
            'contacts': dict(collections.Counter(d['kind'] for d in D('keeper_contact'))),
            'deliberate_parries': sum(1 for d in D('keeper_contact') if d['kind'] == 'parry' and d.get('deliberate')),
            'own_goals': sum(1 for g in gl if g['method'] == 'own_goal'),
            'stopped_carries': U + ': needs carry attempts (C4c2)', 'induced_aborted_finishes': U + ': needs the C4c2 controllers',
            'note': 'each shot release is followed to its first decisive record. goal_before_reaction: in before the Keeper could act; goal_no_attempt: he read it and could not get near; goal_missed_attempt: he moved or launched and did not touch it. field_deflection: another player touched it first; caught_by_a_defender / caught_by_a_team_mate: a field player took it. A parry is deliberate only once he has read the flight.'}
    # ---- 7. C4c2 (M1.6.1): the scoring rulings of 9 October and the common controller (witness: the c4c2_rules marker) ----
    if names.get('c4c2_rules', 0) == 0:
        out['scoring_rulings'] = U; out['controller'] = U
        return out
    out['measurement'] = 'M1.6.1'
    gl = [e['data'] for e in log if e['event'] == 'goal']
    out['scoring_rulings'] = {'goals': len(gl), 'offensive_goals_through_defensive_touch': sum(1 for g in gl if g.get('offensive_goal_through_defensive_touch')),
                              'their_points': sum(g['points'] for g in gl if g.get('offensive_goal_through_defensive_touch')),
                              'true_own_goals': sum(1 for g in gl if g['method'] == 'own_goal'), 'reversals': sum(1 for g in gl if g['method'] == 'reversal'),
                              'defensive_touches_kept_origin': sum(1 for d in D('touch') + D('strike') if d.get('scoring_flight') in ('defensive_touch_origin_kept', 'defensive_kick_origin_kept')),
                              'offensive_touches_moved_origin': sum(1 for d in D('touch') if d.get('scoring_flight') == 'offensive_touch_origin_moved')}
    if not any(e['event'] == 'controller_decision' for e in log):
        out['controller'] = 'off: no controller_decision records (controller = 0)'; return out
    dec = [e for e in log if e['event'] == 'controller_decision']; n = len(log)
    ch = collections.Counter(e['data']['choice'] for e in dec)
    # each shot decision followed to its outcome; calibration of the predicted chance (conversion x pressure factor) against what happened
    cal = collections.defaultdict(lambda: [0, 0]); aborted = 0
    for i, e in enumerate(log):
        if e['event'] != 'controller_decision' or e['data']['choice'] != 'shoot': continue
        pid = e['data']['player']; pred = e['data']['p_conv'] * e['data']['goal_factor']; res = None
        for r in log[i + 1:i + 400]:
            if r['event'] == 'release' and r['data'].get('player') == pid and res is None:
                if r['data'].get('kind') != 'shot': res = 'not_released'; break
                res = 'released'; continue
            if r['event'] == 'goal': res = (r['data']['team'] == pid[0]) if res == 'released' else 'not_released'; break
            if r['event'] in ('possession_change', 'boundary', 'control') and res == 'released': res = False; break
            if r['event'] in ('c3_tuck', 'possession_change') and res is None: res = 'not_released'; break
        aborted += res == 'not_released'; b_ = min(9, int(pred * 10)); cal[b_][0] += 1; cal[b_][1] += (res is True)
    # carry intents followed to their end
    co = collections.Counter(); keepers = {d.get('player') for d in D('keeper_read') + D('keeper_contact') + D('keeper_landed')}
    for i, e in enumerate(log):
        if e['event'] != 'controller_decision' or e['data']['choice'] != 'carry': continue
        pid = e['data']['player']; res = 'open_at_end'
        for r in log[i + 1:]:
            if r['event'] == 'goal' and r['data']['team'] == pid[0]: res = 'carry_goal' if r['data']['method'] == 'carry' else 'goal_by_other_means'; break
            if r['event'] == 'carry_intent_end' and r['data']['player'] == pid: res = 'changed_to_' + r['data']['reason']; break
            if r['event'] == 'tackle_count' and r['data'].get('carrier') == pid: res = 'tackled'; break
            if r['event'] == 'control' and r['data'].get('player') != pid: res = 'stopped_by_keeper' if r['data'].get('player') in keepers else 'lost'; break
            if r['event'] == 'possession_change': res = 'lost'; break
        co[res] += 1
    kc = D('keeper_confront'); ib = D('inbound_options'); use = collections.Counter(); last = None
    for e in log:   # each inbound release, against the options recorded for that restart (the last record before it)
        if e['event'] == 'inbound_options': last = e['data']
        elif e['event'] == 'restart_release' and last is not None and e['data'].get('taker') == last['taker']:
            tg = e['data'].get('target'); use['to_short' if tg == last['short'] else 'to_entry' if tg == last['entry'] else 'to_another']+= 1; last = None
    out['controller'] = {'decisions': dict(sorted(ch.items())), 'by_style': dict(collections.Counter(e['data'].get('style') for e in dec)),
                         'shot_calibration': {'%.1f-%.1f' % (k / 10, (k + 1) / 10): {'decisions': v[0], 'goals': v[1], 'goal_fraction': round(v[1] / v[0], 3) if v[0] else None} for k, v in sorted(cal.items())},
                         'carry_attempts': sum(co.values()), 'carry_outcomes': dict(sorted(co.items())), 'keeper_confronts': len(kc),
                         'inbound_option_records': len(ib), 'inbound_releases': dict(sorted(use.items())), 'note': 'carry attempts are the declared finishing intent (a controller_decision choosing carry). shot_calibration: predicted chance of a goal (drill conversion x pressure factor) against the outcome of that shot.'}
    if isinstance(out.get('keeper'), dict):
        out['keeper']['stopped_carries'] = co.get('stopped_by_keeper', 0)
        out['keeper']['aborted_finishes'] = aborted   # shot decisions whose wind-up never became a release (tucked, or the ball lost first); not split by cause
        out['keeper'].pop('induced_aborted_finishes', None)
    return out
def measure_brief(m):
    """Short console version of the common measures."""
    a, b = m['per_team']['A'], m['per_team']['B']; p = m['pass_ledger']; r = m['restart_pass_ledger']
    f = m['flow']; c = m['contact']; bd = m['boundaries']
    def pct(x): return 'n/a' if x is None else '%.1f%%' % (100 * x)
    extra = ''
    c2 = m.get('continuation')
    if c2:
        tk = c2['tackles']; rv = c2['recovery']; oc = c2['occupancy']
        extra = ('\nFirst tackles %s (recovered %s, inbounds %s); second tackles %s; zone expiries attack %s / defence %s' %
                 (tk['first_tackles'], rv['outcomes'].get('picked_up', 0) + rv['outcomes'].get('replacement_picked_up', 0), c2['inbound']['awarded'],
                  tk['second_tackles'], oc['attacking_expiries'], oc['defensive_unmarked_expiries']))
    return ('Possessions A %s / B %s; mean live %.2f s\n'
            'Points per possession A %s / B %s\n'
            'Possessions with an attempt A %s / B %s; shot conversion A %s / B %s\n'
            'Passes %s: intended %s, any teammate %s, out of bounds %s; restart passes out %s\n'
            'Boundary turnovers %s (%s per 100 possessions); same-team boundary restarts %s\n'
            'Tackles %s; strips %s; wraps %s\n'
            'Restarts per live minute %s; active share excl. intermissions %s' %
            (a['possessions'], b['possessions'], f['possession_live_s']['mean'] or 0,
             a['points_per_possession'], b['points_per_possession'],
             pct(a['attempt_possession_fraction']), pct(b['attempt_possession_fraction']),
             pct(a['shot_conversion']), pct(b['shot_conversion']),
             p['attempts'], pct(p['reached_intended_fraction']), pct(p['reached_any_teammate_fraction']), pct(p['boundary_fraction']),
             pct(r['boundary_fraction']),
             bd['turnovers'], bd['turnovers_per_100_possessions'], bd['same_team_restarts'],
             c['completed_tackles'], c['strips'], c['tackle_engagements'],
             f['restarts_per_live_minute'], pct(f['active_share_excluding_intermissions']))) + extra


def output_dir():
    # External/iCloud scripts do not imply permission to create sibling folders.
    # Always write into the app-owned home directory, independent of __file__.
    path = Path.home() / 'Documents' / 'Beastball_Pocket_Results'
    path.mkdir(parents=True, exist_ok=True)
    return path


def run_experiment(settings, baseline=None, out=None, progress=True, calibration=None):
    validate(settings)
    calibration = validate_calibration(copy.deepcopy(CALIBRATION if calibration is None else calibration))
    if baseline is not None: validate(baseline)
    folder=Path(out) if out is not None else output_dir()
    folder.mkdir(parents=True,exist_ok=True)
    stamp=time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns()%1000000000)
    path=folder/('Beastball_'+stamp+'.json')
    payload={'format':VERSION,'checkpoint':CHECKPOINT,'measurement_version':MEASUREMENT_VERSION,
             'settings':copy.deepcopy(settings),'settings_fingerprint':fingerprint(settings),
             'calibration':copy.deepcopy(calibration),'calibration_fingerprint':fingerprint(calibration),
             'calibration_is_default':calibration==CALIBRATION,
             'pocket_1_1_source_sha256':SOURCE_HASHES,'embedded_sha256':{k:hashlib.sha256(v.encode()).hexdigest() for k,v in CORE_SOURCES.items()},
             'runtime':sys.version,'notes':NOTES,'seeds':[], 'runs':[],
             'baseline_settings':copy.deepcopy(baseline),'baseline_runs':[], 'status':'running'}
    def save():
        temporary=path.with_suffix('.tmp')
        temporary.write_text(json.dumps(payload,indent=2),encoding='utf-8')
        temporary.replace(path)
    save()
    try:
        for i in range(settings['matches']):
            seed=settings['seed']+i
            for name, cfg, key in [('CURRENT',settings,'runs')]+([('BASELINE',baseline,'baseline_runs')] if baseline else []):
                if progress: print('\n%s match %s/%s; seed %s' % (name,i+1,settings['matches'],seed),flush=True)
                summary,events=run_match(cfg,seed,progress,calibration)
                payload[key].append(summary)
                if settings['save_events']:
                    log_path=folder/(path.stem+'_'+name+'_'+str(seed)+'.jsonl.gz')
                    with gzip.open(log_path,'wt',encoding='utf-8') as f:
                        for event in events: f.write(json.dumps(event)+'\n')
                    summary['event_file']=log_path.name
                if progress: print(compact(summary)+'\n'+measure_brief(summary['measures'])+qualification_text(summary),flush=True)
                save()
            payload['seeds'].append(seed)
            save()
        payload['aggregate']=aggregate(payload['runs'])
        if baseline:
            payload['baseline_aggregate']=aggregate(payload['baseline_runs'])
            deltas=[sum(a['score'].values())-sum(b['score'].values()) for a,b in zip(payload['runs'],payload['baseline_runs'])]
            payload['paired_combined_score_deltas']=deltas
            payload['mean_paired_combined_score_delta']=statistics.mean(deltas)
            payload['comparison_note']='Same seed schedule, not identical random outcomes after policies diverge; point deltas alone do not measure play quality.'
        payload['status']='finished' if all(r['ordinary_completion'] for r in payload['runs']+payload['baseline_runs']) else 'finished_with_abnormal_matches'
    except (Exception,KeyboardInterrupt) as exc:
        payload['status']='interrupted' if isinstance(exc,KeyboardInterrupt) else 'error'
        payload['error']=repr(exc)
        save()
        print('Partial results saved:',path)
        raise
    save()
    report=VERSION+'\n'+json.dumps(payload['aggregate'],indent=2)+'\n\n'
    report+='\n\n'.join(compact(r)+'\n'+measure_brief(r['measures'])+qualification_text(r) for r in payload['runs'])
    report+='\n\nSettings:\n'+json.dumps(settings,indent=2)+'\n\nCalibration:\n'+json.dumps(calibration,indent=2)+'\n\nLimits:\n'+'\n'.join(NOTES)
    if baseline: report+='\n\nBaseline aggregate:\n'+json.dumps(payload['baseline_aggregate'],indent=2)+'\nMean paired points change: '+str(payload['mean_paired_combined_score_delta'])
    path.with_suffix('.txt').write_text(report,encoding='utf-8')
    print('\nSaved:',path,flush=True)
    return path,payload

LABELS = {'period_seconds':'Period length (live s)','periods':'Regulation periods',
 'play_clock':'Possession clock (s)','player_speed':'Max player speed (m/s)',
 'ball_speed':'Shot / kick speed (m/s)','pass_speed':'Pass speed (m/s)',
 'arrow_speed':'Arrow speed (m/s)','keeper_zone_radius':'Keeper Zone radius (m)',
 'inner_zone_radius':'Inner zone radius (m)','inner_points':'Inner release points','release_points':'Middle-zone release points',
 'allow_outside_releases':'Allow outside releases','outside_points':'Outside release points','carry_value':'Carry points (0 = off)',
 'adapt_scoring':'Value-aware shooting','dt_ms':'Physics step (ms)','save_events':'Save full event logs'}

def phone_main():
    import dialogs,clipboard
    current=copy.deepcopy(SETTINGS);baseline=copy.deepcopy(SETTINGS);last=None;cal=copy.deepcopy(CALIBRATION)
    print(VERSION+'\nOne file. Fully offline. Experimental results, not canon.\nTwo equal 22-player rosters; 12 active each.\n')
    while True:
        action=dialogs.list_dialog('Beastball Pocket',items=['Run current settings','Edit settings','Edit calibration','Reset calibration to defaults',
          'Pin current as baseline','Compare current vs baseline','Copy last results for ChatGPT',
          'Import settings from clipboard','Quick match length','Full match length','Run self-check','Show limitations','Exit'])
        if not action or action=='Exit': return
        try:
            if action=='Edit settings':
                fields=[]
                for key,val in current.items():
                    fields.append({'key':key,'title':LABELS.get(key,key.replace('_',' ').capitalize()),
                     'type':'switch' if isinstance(val,bool) else 'text' if isinstance(val,str) else 'number',
                     'value':val if isinstance(val,bool) else str(val)})
                edited=dialogs.form_dialog('Parameters (meters, seconds)',fields=fields)
                if edited is not None:
                    candidate={k:(bool(edited[k]) if isinstance(v,bool) else str(edited[k]) if isinstance(v,str)
                                  else int(edited[k]) if isinstance(v,int) else float(edited[k])) for k,v in current.items()}
                    validate(candidate);current=candidate
                    print('Settings changed:',fingerprint(current))
            elif action=='Edit calibration':
                fields=[{'key':k,'title':k.replace('_',' '),'type':'number','value':str(v)} for k,v in cal.items()]
                edited=dialogs.form_dialog('Calibration (model assumptions)',fields=fields)
                if edited is not None:
                    candidate={k:(int(float(edited[k])) if isinstance(v,int) and float(edited[k])==int(float(edited[k])) else float(edited[k])) for k,v in cal.items()}
                    validate_calibration(candidate);cal=candidate
                    print('Calibration changed:',fingerprint(cal),'(default)' if cal==CALIBRATION else '(NOT default)')
            elif action=='Reset calibration to defaults':
                cal=copy.deepcopy(CALIBRATION);print('Calibration reset to defaults.')
            elif action=='Quick match length':
                current.update(period_seconds=120,periods=2,overtime_seconds=30);print('Two 120-second periods selected.')
            elif action=='Full match length':
                current.update(period_seconds=600,periods=4,overtime_seconds=300);print('Full 4 x 600-second match selected; this takes longer.')
            elif action=='Run self-check':
                print('Self-check:',self_check(),'checks passed.')
            elif action=='Pin current as baseline':
                baseline=copy.deepcopy(current);print('Baseline pinned:',fingerprint(baseline))
            elif action in ('Run current settings','Compare current vs baseline'):
                last,payload=run_experiment(current,baseline if action.startswith('Compare') else None,calibration=cal)
                print('Use Copy last results for ChatGPT to send settings + evidence together.')
            elif action=='Copy last results for ChatGPT':
                if last is None: print('Run a match first.')
                else: clipboard.set(last.read_text(encoding='utf-8'));print('Copied complete JSON results. Paste into ChatGPT.')
            elif action=='Import settings from clipboard':
                obj=json.loads(clipboard.get());candidate=obj.get('settings',obj)
                candidate, migration=import_settings(obj)
                current=copy.deepcopy(candidate);print(migration or 'Settings imported.')
                if import_settings.calibration is not None:
                    cal=copy.deepcopy(import_settings.calibration);print('Calibration imported:',fingerprint(cal))
            elif action=='Show limitations': dialogs.text_dialog('Model limits',text='\n\n'.join(NOTES))
        except KeyboardInterrupt:
            print('Stopped. Completed matches have been saved.')
            return
        except Exception as exc:
            print('Problem:',exc)
            dialogs.alert('Beastball Pocket',str(exc),'OK',hide_cancel_button=True)

def self_check():
    """Small self-contained installation and parameter checks; no extra test files."""
    checks=0
    def expect(condition):
        nonlocal checks
        if not condition: raise AssertionError('Pocket self-check failed at check '+str(checks+1))
        checks+=1
    C1_RULES={'tackles_per_possession':1,'zone_inbound':False,'zone_marking':False}
    C3CAL={**copy.deepcopy(CALIBRATION),'c3c':0,'c4_zone':0,'escape_allocation':0,'c4b':0,'c4c':0,'c4c2':0};LEGACY={**C3CAL,'c3_contact':0};C4CAL={**copy.deepcopy(CALIBRATION),'escape_allocation':0,'c4b':0,'c4c':0,'c4c2':0};C4ACAL={**copy.deepcopy(CALIBRATION),'c4b':0,'c4c':0,'c4c2':0};C4BCAL={**copy.deepcopy(CALIBRATION),'c4c':0,'c4c2':0};C4CCAL={**copy.deepcopy(CALIBRATION),'c4c2':0};C4C2CAL=copy.deepcopy(CALIBRATION) #the C3a and C3b scenarios run with C3c off (they describe C3b2); the C3c scenarios switch it on
    def controlled(**over):
        m=CORE.match.Match(configuration({**SETTINGS,**C1_RULES,'keeper_zone_radius':20.0,'inner_zone_radius':5.0,'inner_points':25,'release_points':9,'outside_points':4,**over},None,LEGACY))
        s=m.s;s.phase=CORE.types.Phase.LIVE;s.now=1000;s.owner='A'
        s.ball=CORE.types.Ball(mode=CORE.types.BallMode.CONTROLLED,carrier='A0',control_time=0,last_touch='A',scoring=True)
        return m
    m=controlled()
    expect(len(m.s.players)==44)
    expect(all(m.s.players['A'+str(i)].a==m.s.players['B'+str(i)].a for i in range(22)))
    for t in ('A','B'):expect(sum(q.active for q in m.s.players.values() if q.team==t)==12)
    m=controlled();expect(not m.e.goal('B',50,1));expect(m.s.score['A']==0)
    for x,allow,expected in [(95,True,25),(90,True,9),(80,True,9),(79.99,True,4),(60,False,0)]:
        m=controlled(allow_outside_releases=allow)
        m.s.players['A0'].x=x;m.s.players['A0'].y=50
        expect(m.e.release('A0',(20,0,0),'shot'))
        m.s.ball.x=100;m.e.goal('B',50,1)
        expect(m.s.score['A']==expected)
    m=controlled(keeper_zone_radius=30,inner_zone_radius=10)
    expect(m.e.zone(75,50)==1)
    expect(m.e.territory('A',90,50)=='inner_release')
    other=controlled(keeper_zone_radius=15)
    expect(other.e.zone(75,50) is None and m.e.zone(75,50)==1)
    m=controlled(play_clock=17);m.e.new_owner('B','test');expect(m.s.possession_ms==17000)
    # C0 additions: the calibration block must equal the core's own defaults, and reach the match.
    expect(CALIBRATION==CORE.match.DEFAULT_ASSUMPTIONS)
    expect(controlled().assume=={**CORE.match.DEFAULT_ASSUMPTIONS,'c3_contact':0,'c3c':0,'c4_zone':0,'escape_allocation':0,'c4b':0,'c4c':0,'c4c2':0})
    # C1: the ball-speed cap. Equal to the cap and a rounding hair above are legal; a real excess is not.
    for label,factor,legal in (('equal',1.0,True),('rounding',1.0+1e-9,True),('excess',1.01,False)):
        m=controlled(ball_speed=40.0,pass_speed=40.0);v=(40.0*factor,0.0,0.0)
        expect(m.e.release('A0',v,'pass')==legal)
        m=controlled(ball_speed=40.0,pass_speed=40.0);s=m.s;p=s.players['A0'];p.x,p.y=50.0,50.0
        s.ball=CORE.types.Ball(mode=CORE.types.BallMode.LOOSE,x=50.0,y=50.0,z=1.0,last_touch='B',scoring=True)
        before=len(m.e.log);m.e.strike('A0',v)
        expect(any(r['event']=='foul' and r['data'].get('reason')=='ball_release_speed' for r in m.e.log[before:])!=legal)
        m=controlled(ball_speed=40.0,pass_speed=40.0);s=m.s
        m.e.award('A',50,50,'test');r=s.restart;tk=s.players['A0'];tk.x,tk.y=r.x,r.y
        for q in s.players.values():
            if q.team=='B' and q.role!='archer':q.x,q.y=5.0,5.0
        m.e.ready('A0');expect(m.e.restart_release('A0',v,'A1')==legal)
    # C1: the launch solver reaches its target at exactly the requested speed, with drag
    g=CORE.geometry
    for d,speed in ((5,45.0),(20,45.0),(40,45.0),(20,27.0),(40,40.0)):
        sol=g.launch_for((10.0,50.0,1.6),(10.0+d,50.0,1.6),speed,9.81,.015);expect(sol is not None)
        vel,T=sol;expect(abs(math.sqrt(sum(c*c for c in vel))-speed)<1e-6)
        ball=CORE.types.Ball(x=10.0,y=50.0,z=1.6,vx=vel[0],vy=vel[1],vz=vel[2]);x,y,z=g.ball_at(ball,T,9.81,.015)
        expect(abs(x-(10.0+d))<1e-3 and abs(z-1.6)<1e-3)
    expect(g.launch_for((10.0,50.0,1.6),(95.0,50.0,1.6),20.0,9.81,.015) is None)
    # C1 revision 2: the contact kernel.
    Ty=CORE.types;SURE=dict(catch_reaction_s=1e-12);NEVER=dict(catch_reaction_s=1e9);GRIP=dict(catch_arrest_force_N=1e12);SLIP=dict(catch_arrest_force_N=1e-6)
    def bench(**cal):
        m=CORE.match.Match(configuration({**SETTINGS,**C1_RULES,'archery':False},1,{**LEGACY,**cal}));s=m.s
        s.phase=Ty.Phase.LIVE;s.now=1000;s.owner='A'
        for q in s.players.values():
            if q.active and q.role!='archer':q.x,q.y,q.vx,q.vy=2.0,2.0,0.0,0.0
        s.ball=Ty.Ball(mode=Ty.BallMode.PASS,last_touch='A',scoring=True);m.seen_version=s.ball.version;m.seen_from=0
        return m
    def sweep(m,b0,b1,movers,ms=100):
        s=m.s;b=s.ball;b.x,b.y,b.z=b1;b.vx,b.vy,b.vz=[(b1[j]-b0[j])/(ms/1000) for j in range(3)]
        oldp={q.id:(q.x,q.y,q.z) for q in m.active_field()}
        for pid,(p0,p1) in movers.items():
            q=s.players[pid];oldp[pid]=(p0[0],p0[1],0.0);q.x,q.y=p1
        return m.catch_contacts(b0,ms,oldp),oldp
    def commit(m,evs,oldp,ms=100):
        for e in evs:e.data['generation']=m.s.ball.version
        m.process_events(evs,m.s.now,ms,oldp)
    m=bench();h=m.s.players['B1'].hand_height;R=m.s.players['B1'].a.reach*.9
    # 1. Reachable is not touched: hands never set, ball passes at 95% of reach, nothing happens.
    m=bench(**NEVER);evs,_=sweep(m,(47.0,50.0+.95*R,h),(53.0,50.0+.95*R,h),{'B1':((50.0,50.0),(50.0,50.0))})
    expect(evs==[] and m.s.players['B1'].next_action<=m.s.now and m.stats['contacts_proposed']==0)
    # 2. Ball and player are swept together: the Lead's witness never comes within reach, so no contact.
    m=bench(**SURE,**GRIP);evs,_=sweep(m,(47.0,50.0,h),(53.0,50.0,h),{'B1':((50.0,52.5),(50.0,50.0))});expect(evs==[])
    m=bench(**SURE,**GRIP);evs,_=sweep(m,(47.0,50.0,h),(53.0,50.0,h),{'B1':((50.0,50.5),(50.0,50.5))})
    expect(len(evs)==1 and evs[0].kind=='acquire' and evs[0].at==50 and abs(evs[0].data['ball_point'][0]-50.0)<1e-6)
    # 3. No manufactured simultaneity: closest approaches at 50 and 55 ms give one catch, by the first, at its own point.
    m=bench(**SURE,**GRIP);evs,oldp=sweep(m,(48.0,50.0,h),(52.0,50.0,h),{'A1':((50.0,50.0),(50.0,50.0)),'B1':((50.2,50.0),(50.2,50.0))})
    expect(len(evs)==1 and evs[0].actor=='A1' and evs[0].at==50 and abs(evs[0].data['ball_point'][0]-50.0)<1e-6)
    commit(m,evs,oldp);expect(m.s.ball.carrier=='A1' and not any(r['event']=='joint_control' for r in m.e.log))
    #    Genuine simultaneity: opponents level with each other, same millisecond, gives joint control.
    m=bench(**SURE,**GRIP);evs,oldp=sweep(m,(48.0,50.0,h),(52.0,50.0,h),{'A1':((50.0,50.4),(50.0,50.4)),'B1':((50.0,49.6),(50.0,49.6))})
    expect(sorted(e.actor for e in evs)==['A1','B1'] and all(e.at==50 for e in evs))
    commit(m,evs,oldp);expect(any(r['event']=='joint_control' for r in m.e.log))
    # 4. Proposals have no side effects; a committed contact does; an invalidated one leaves nothing behind.
    for pid in ('B1','B10'):
        m=bench(**SURE,**SLIP);q=m.s.players[pid];evs,oldp=sweep(m,(47.0,50.0,q.hand_height),(53.0,50.0,q.hand_height),{pid:((50.0,50.5),(50.0,50.5))})
        expect(len(evs)==1 and evs[0].kind=='touch' and q.next_action<=m.s.now and m.stats['keeper_blocks']==0 and m.stats['contacts_committed']==0)
        v0=(m.s.ball.vx,m.s.ball.vy);commit(m,evs,oldp)
        expect(q.next_action==1000+evs[0].at+200 and m.stats['contacts_committed']==1 and m.stats['keeper_blocks']==(1 if pid=='B10' else 0))
        expect((m.s.ball.vx,m.s.ball.vy)!=v0 and m.s.ball.carrier is None)
        touch=[r for r in m.e.log if r['event']=='touch'];expect(len(touch)==1 and touch[0]['data']['deliberate']==(pid=='B10'))
        m=bench(**SURE,**SLIP);q=m.s.players[pid];evs,oldp=sweep(m,(47.0,50.0,q.hand_height),(53.0,50.0,q.hand_height),{pid:((50.0,50.5),(50.0,50.5))})
        for e in evs:e.data['generation']=m.s.ball.version
        m.s.ball.version+=1;v0=(m.s.ball.vx,m.s.ball.vy);m.process_events(evs,m.s.now,100,oldp)   # an earlier event has already changed the ball
        expect(q.next_action<=1000 and m.stats['keeper_blocks']==0 and m.stats['contacts_committed']==0 and (m.s.ball.vx,m.s.ball.vy)==v0)
    # 5. A clean catch is committed at its own time and point.
    m=bench(**SURE,**GRIP);evs,oldp=sweep(m,(47.0,50.0,h),(53.0,50.0,h),{'B1':((50.0,50.5),(50.0,50.5))});commit(m,evs,oldp)
    expect(m.s.ball.carrier=='B1' and m.stats['contacts_committed']==1)
    # 6. Only elapsed time counts: a ball that changed course as it entered reach is met at the rate of the hazard law, no more.
    m=bench();q=m.s.players['B1'];tau=CALIBRATION['catch_reaction_s']*(1.3-.6*q.a.awareness);hits=0;N=800
    for i in range(N):
        m.hands_set={};m.seen_from=m.s.now;q.next_action=0
        evs,_=sweep(m,(50.0-R,50.0,h),(50.0-R+4.0,50.0,h),{'B1':((50.0,50.0),(50.0,50.0))});hits+=bool(evs)
    expect(abs(hits/N-(1-math.exp(-(2*R/40.0)/tau)))<.06)
    # 7. A player outside the field at the moment of contact does not play the ball.
    m=bench(**SURE,**GRIP);evs,_=sweep(m,(-.5,47.0,h),(-.5,53.0,h),{'B1':((-.6,50.0),(.4,50.0))});expect(evs==[])
    # C1 revision 3, correction 1: after a deflection inside a step, the rest of the step is resolved at once and once only.
    KEEP=('touch','goal','no_goal','boundary','frame_contact','control','finishing_flight','flight_ended','period_end')
    def deflect(point,vel,at_xy,ms=100,period_ms=None,others=None,cal=None):
        m=bench(**(cal or {}));s=m.s;b=s.ball;s.players['B1'].x,s.players['B1'].y=at_xy
        for pid,xy in (others or {}).items():s.players[pid].x,s.players[pid].y=xy
        if period_ms is not None:s.game_ms=period_ms
        b.x,b.y,b.z=point;b.pocket_origin=(85.0,50.0);b.pocket_release_team='A'
        oldp={q.id:(q.x,q.y,q.z) for q in m.active_field()}
        ev=Ty.Event('touch','B1',data={'deliberate':False,'velocity':vel,'ball_point':list(point),'c1_contact':True,'cooldown_ms':200,'keeper_block':False,'generation':b.version},at=50)
        m.process_events([ev],s.now,ms,oldp)
        for _ in range(3):m.step()
        return m,[(r['t_ms'],r['event']) for r in m.e.log if r['event'] in KEEP]
    GOAL=((99.9,50.0,1.0),(20.0,0.0,0.0),(99.3,50.0));SIDE=((50.0,99.9,1.0),(0.0,20.0,0.0),(50.0,99.3));FRAME=((99.9,56.1,.3),(20.0,0.0,0.0),(99.3,56.1))
    #   The period clock expires after the event: the crossing is resolved 10 ms after the deflection, inside the same step.
    m,q=deflect(*GOAL);expect(q==[(1050,'touch'),(1060,'goal')] and m.s.score['A']>0)
    m,q=deflect(*SIDE);expect(q==[(1050,'touch'),(1060,'boundary')])
    m,q=deflect(*FRAME);expect(q==[(1050,'touch'),(1060,'frame_contact')] and m.s.ball.x<99.7)
    m,q=deflect((50.0,50.0,h),(20.0,0.0,0.0),(49.5,50.0),others={'A1':(50.8,50.0)},cal={**SURE,**GRIP})
    expect(len(q)==2 and q[1][1]=='control' and 1085<=q[1][0]<=1092 and m.s.ball.carrier=='A1')
    #   The period clock expires 5 ms after the deflection, before the event: the clock is resolved first, then the crossing, once.
    m,q=deflect(*GOAL,ms=55,period_ms=55);expect(q==[(1050,'touch'),(1055,'finishing_flight'),(1060,'goal'),(1060,'period_end')])
    m,q=deflect(*SIDE,ms=55,period_ms=55);expect(q==[(1050,'touch'),(1055,'finishing_flight'),(1060,'flight_ended'),(1060,'period_end')])
    m,q=deflect(*FRAME,ms=55,period_ms=55);expect(q[:3]==[(1050,'touch'),(1055,'finishing_flight'),(1060,'frame_contact')] and [e for _,e in q].count('frame_contact')==1)
    m,q=deflect((50.0,50.0,h),(20.0,0.0,0.0),(49.5,50.0),ms=55,period_ms=55,others={'A1':(50.8,50.0)},cal={**SURE,**GRIP})
    expect(q[:2]==[(1050,'touch'),(1055,'finishing_flight')] and 'control' not in [e for _,e in q])
    #   The Lead's witness: the residual call itself reports the crossing at its own time.
    m=bench();b=m.s.ball;b.x,b.y,b.z,b.vx,b.vy,b.vz=99.9,50.0,1.0,20.0,0.0,0.0;evs=m.fly_on(100,{})
    expect([e.kind for e in evs]==['goal'] and evs[0].at==10 and evs[0].data['generation']==b.version)
    # C1 revision 3, correction 2: readiness counts all elapsed observation; a failed sample is not drawn again.
    def freq(m,pid,trials,prepare,b0,b1,ms=1):
        n=0
        for _ in range(trials):
            prepare();evs,_=sweep(m,b0,b1,{pid:((50.0,50.0),(50.0,50.0))},ms);n+=bool(evs)
        return n/trials
    m=bench(**GRIP);q=m.s.players['B1'];tau=CALIBRATION['catch_reaction_s']*(1.3-.6*q.a.awareness);still=((50.5,50.0,h),(50.5,50.0,h))
    #   a flight observed for a second that starts within reach (the Lead's witness: 1 ms interval)
    def fresh():m.hands_set={};m.seen_from=0;q.next_action=0
    expect(freq(m,'B1',400,fresh,*still)>.99)
    #   a ball entering reach from outside after a second of observation
    expect(freq(m,'B1',400,fresh,(47.0,50.0,h),(53.0,50.0,h),100)>.99)
    #   a signalled receiver, flight released this instant inside his reach, signal 300 ms earlier
    def signalled():m.hands_set={};m.seen_from=m.s.now;q.next_action=0;m.s.ball.intended='B1';m.s.ball.release_time=m.s.now;m.pass_signal=('B1',m.s.now-300)
    expect(abs(freq(m,'B1',1500,signalled,*still)-(1-math.exp(-.301/tau)))<.05)
    m.s.ball.intended=None
    #   a failed sample is carried forward: the next millisecond adds only that millisecond's chance
    def failed():m.hands_set={'B1':m.s.now};m.seen_from=0;q.next_action=0
    expect(freq(m,'B1',1500,failed,*still)<.04)
    #   readiness continues across step boundaries: two 20 ms steps equal one 40 ms step
    def one40():
        m.hands_set={'B1':m.s.now};q.next_action=0
        return bool(sweep(m,*still,{'B1':((50.0,50.0),(50.0,50.0))},40)[0])
    def two20():
        m.hands_set={'B1':m.s.now};q.next_action=0;first=bool(sweep(m,*still,{'B1':((50.0,50.0),(50.0,50.0))},20)[0])
        if first:return True
        m.s.now+=20;second=bool(sweep(m,*still,{'B1':((50.0,50.0),(50.0,50.0))},20)[0]);m.s.now-=20;return second
    pa=sum(one40() for _ in range(1500))/1500;pb=sum(two20() for _ in range(1500))/1500;target=1-math.exp(-.040/tau)
    expect(abs(pa-target)<.05 and abs(pb-target)<.05)
    #   cooldown: a ready player cannot make contact before his cooldown ends
    m=bench(**SURE,**GRIP);m.s.players['B1'].next_action=m.s.now+60;evs,_=sweep(m,*still,{'B1':((50.0,50.0),(50.0,50.0))},100);expect(len(evs)==1 and evs[0].at==60)
    #   a course change clears every record for the flight
    m=bench(**NEVER);b=m.s.ball;b.x,b.y,b.z=50.5,50.0,h;m.hands_set={'B1':True,'A1':1234};b.version+=1
    m.advance_ball(1,{q2.id:(q2.x,q2.y,q2.z) for q2 in m.active_field()});expect(True not in m.hands_set.values() and 1234 not in m.hands_set.values())
    # C1 revision 3, correction 3: a proposal that is no longer possible when it is committed leaves nothing behind.
    def rejected(pid,spoil,cal,move=None):
        m=bench(**SURE,**cal);q=m.s.players[pid];evs,oldp=sweep(m,(47.0,50.0,q.hand_height),(53.0,50.0,q.hand_height),{pid:((50.0,50.5),(50.0,50.5))})
        expect(len(evs)==1)
        for e in evs:e.data['generation']=m.s.ball.version
        b=m.s.ball;before=(b.x,b.y,b.z,b.vx,b.vy,b.vz,b.version,getattr(b,'resume',False),getattr(b,'course_time',None),q.next_action)
        spoil(m,q,oldp);fouls=len([r for r in m.e.log if r['event']=='foul']);m.process_events(evs,m.s.now,100,oldp);b=m.s.ball
        log=[r['event'] for r in m.e.log]
        expect(before==(b.x,b.y,b.z,b.vx,b.vy,b.vz,b.version,getattr(b,'resume',False),getattr(b,'course_time',None),q.next_action))
        expect(m.stats['contacts_committed']==0 and m.stats['keeper_blocks']==0 and m.stats['contacts_rejected']==1 and b.carrier is None)
        expect('touch' not in log and 'control' not in log and 'contact_rejected' in log and len([r for r in m.e.log if r['event']=='foul'])==fouls)
    def freeze(m,q,oldp):q.freeze_until=m.s.now+5000
    def ground(m,q,oldp):q.posture='grounded'
    def exclude(m,q,oldp):q.exclusion_ms=60000
    def offfield(m,q,oldp):oldp[q.id]=(-1.0,50.5,0.0);q.x=-1.0
    for spoil in (freeze,ground,exclude,offfield):
        rejected('B10',spoil,SLIP)   # an unsecured Keeper contact (the Lead's witness when frozen)
        rejected('B1',spoil,SLIP)    # an unsecured field-player contact
        rejected('B1',spoil,GRIP)    # a catch: the ball is not moved to the catch point either
    #   a stoppage before the proposed contact (an award changes the ball's generation): nothing is committed
    for pid,cal in (('B10',SLIP),('B1',SLIP),('B1',GRIP)):
        m=bench(**SURE,**cal);q=m.s.players[pid];evs,oldp=sweep(m,(47.0,50.0,q.hand_height),(53.0,50.0,q.hand_height),{pid:((50.0,50.5),(50.0,50.5))})
        for e in evs:e.data['generation']=m.s.ball.version
        m.e.award('A',30,30,'test');spot=(m.s.ball.x,m.s.ball.y);m.process_events(evs,m.s.now,100,oldp);log=[r['event'] for r in m.e.log]
        expect('touch' not in log and 'control' not in log and m.stats['contacts_committed']==0 and m.stats['keeper_blocks']==0 and q.next_action<=1000 and (m.s.ball.x,m.s.ball.y)==spot)
    #   an accepted contact still applies everything together
    m=bench(**SURE,**SLIP);q=m.s.players['B10'];evs,oldp=sweep(m,(47.0,50.0,q.hand_height),(53.0,50.0,q.hand_height),{'B10':((50.0,50.5),(50.0,50.5))});commit(m,evs,oldp)
    expect(m.stats['contacts_committed']==1 and m.stats['keeper_blocks']==1 and m.stats['contacts_rejected']==0 and q.next_action==1250 and m.s.ball.course_time==1050)
    #   same-millisecond convention: logged with each candidate's own point
    m=bench(**SURE,**GRIP);evs,oldp=sweep(m,(48.0,50.0,h),(52.0,50.0,h),{'A1':((50.0,50.4),(50.0,50.4)),'B1':((50.0,49.6),(50.0,49.6))});commit(m,evs,oldp)
    sim=[r for r in m.e.log if r['event']=='simultaneous_contact'];expect(len(sim)==1 and len(sim[0]['data']['points'])==2 and any(r['event']=='joint_control' for r in m.e.log))
    #   a shared threshold is not a tie: a ball dropping to scooping height between two opponents goes to the nearer hand
    m=bench(**SURE,**GRIP);evs,oldp=sweep(m,(50.0,50.0,.5),(50.0,50.0,.3),{'A1':((50.3,50.0),(50.3,50.0)),'B1':((49.4,50.0),(49.4,50.0))})
    expect(len(evs)==1 and evs[0].actor=='A1' and evs[0].at in (49,50));commit(m,evs,oldp);expect(m.s.ball.carrier=='A1' and not any(r['event']=='joint_control' for r in m.e.log))
    # ================= C2: continuation, recovery, inbound, reconstruction, occupancy =================
    # Deterministic scripted scenarios. Team A attacks x=100 (zone 1); zone 0 is A's own. Players stand still
    # unless a scenario moves them, so every outcome below is a consequence of the rules engine alone.
    LIVE,AWARD,DEAD=Ty.Phase.LIVE,Ty.Phase.AWARD,Ty.Phase.DEAD
    C2R={'tackles_per_possession':2,'zone_inbound':True,'zone_marking':True,'marking_distance':3.0,'inbound_mark_offset':8.0}
    def ok(condition,label):
        if not condition: raise AssertionError('C2 self-check failed: '+label)
        expect(True)
    def put(m,pid,xy,upright=True):
        q=m.s.players[pid];q.x,q.y=float(xy[0]),float(xy[1]);q.vx=q.vy=0.0;q.target=(q.x,q.y)
        if upright:q.posture='upright'
        return q
    def give(m,pid):
        s=m.s;s.ball=Ty.Ball(mode=Ty.BallMode.CONTROLLED,carrier=pid,control_time=s.now-500,last_touch=pid[0],scoring=True);s.phase=LIVE;m.e.follow_carrier()
    def c2m(at=(50.0,50.0),tackler='B0',carrier='A0',**over):
        m=CORE.match.Match(configuration({**SETTINGS,**C2R,'archery':False,**over},1,LEGACY));s=m.s
        s.phase=LIVE;s.now=1000;s.owner='A';s.opening_team='A';s.alternate='B';s.opening_deadline=None;s.opening_touched=True
        for q in s.players.values():
            if q.active and q.role=='field':put(m,q.id,(30.0 if q.team=='A' else 70.0,5.0+10.0*int(q.id[1:])))
        put(m,carrier,at);give(m,carrier)
        if tackler:put(m,tackler,(at[0]+1.3,at[1]))
        return m
    def tk(m,actor='B0',target=None):
        s=m.s;m.e.batch([Ty.Event('tackle',actor,target or s.ball.carrier,{'control_witness':s.ball.version})])
    def ev(m,k=0):return[r['event'] for r in m.e.log[k:]]
    def last(m,name):return next(r['data'] for r in reversed(m.e.log) if r['event']==name)
    def fouls(m,k=0):return[r['data']['reason'] for r in m.e.log[k:] if r['event']=='foul']
    def pick(m,pid):
        s=m.s;put(m,pid,(s.ball.x-.5,s.ball.y));return m.e.acquire(pid)
    def one(m,ms=900):
        """First counted tackle outside the attacked zone, opponents clear, the carrier gets up and picks the ball up."""
        tk(m);put(m,'B0',(m.s.ball.x+6,m.s.ball.y));m.e.advance(ms);return pick(m,'A0')
    def catch(m,pid,xy=None):
        s=m.s
        if xy:put(m,pid,xy)
        b=s.ball;b.x,b.y,b.z=s.players[pid].x+.3,s.players[pid].y,1.2;return m.e.acquire(pid)

    # ---- 1. continuation: first tackle keeps possession, second turns it over ----
    m=c2m();s=m.s;s.possession_ms=30000;spot=(s.ball.x,s.ball.y);k=len(m.e.log);tk(m)
    ok(s.owner=='A' and s.tackle_count==1 and s.phase==AWARD,'first tackle keeps possession, count one')
    d=last(m,'tackle_count');ok((d['count_from'],d['count_to'],d['where'],d['procedure'])==(0,1,'outside','live_recovery'),'first tackle is logged as 0->1 live recovery')
    ok('possession_change' not in ev(m,k) and 'tackle_award' not in ev(m,k),'first tackle is not a possession change')
    ok(s.possession_ms==30000 and s.award_deadline==s.now+3000,'first tackle keeps the possession clock; three seconds to recover')
    ok(s.recovery['spot']==spot and (s.ball.x,s.ball.y)==spot and last(m,'recovery_started')['placed_at']==s.now,'recovery spot is the ball at completion, placed at once')
    ok(not s.engagements,'old wraps end at the tackle')
    ok(not m.e.acquire('A0') and s.recovery is not None,'the grounded carrier cannot recover before he is upright')
    g0=s.game_ms;put(m,'B0',(spot[0]+6,spot[1]));m.e.advance(900)
    ok(s.possession_ms==29100 and s.game_ms==g0-900,'game and possession clocks run during recovery')
    ok(pick(m,'A0') and s.phase==LIVE and s.recovery is None and s.award_spot is None,'pickup ends the recovery and its protection at once')
    d=last(m,'recovery_pickup');ok(d['elapsed_ms']==900 and d['player']=='A0' and not d['replacement'],'pickup is logged with its elapsed time')
    put(m,'B1',(s.players['A0'].x+1.3,50));k=len(m.e.log);tk(m,'B1')
    ok('foul' not in ev(m,k),'a new engagement straight after pickup is legal: no post-pickup immunity')
    d=last(m,'tackle_count');ok((d['count_from'],d['count_to'],d['procedure'])==(1,2,'turnover') and 'tackle_award' in ev(m,k),'second tackle is the ordinary turnover award')
    ok(s.owner=='B' and s.tackle_count==0 and s.possession_ms==45000 and s.award_deadline==s.now+5000 and s.recovery is None,'second tackle: opponents, fresh clock, count zero, five-second pickup')
    ok(sum(e=='tackle_count' for e in ev(m))==2,'two tackles, two count events')

    # ---- 2. what keeps the count and what clears it ----
    m=c2m();s=m.s;one(m)
    ok(m.e.release('A0',(10.0,0.0,2.0),'pass','A1') and catch(m,'A1',(60,50)) and s.tackle_count==1,'count kept through a pass')
    m.e.release('A1',(10.0,0.0,2.0),'shot');m.e.touch('B10',False);ok(catch(m,'A2',(85,30)) and s.tackle_count==1,'count kept through an offensive rebound')
    m.e.release('A2',(0.0,10.0,2.0),'pass');s.ball.last_touch='B';m.e.boundary(85.0,100.5)
    ok(s.owner=='A' and s.restart.reason=='boundary' and s.tackle_count==1,'count kept through a same-team boundary')
    put(m,'A3',(s.restart.x,s.restart.y));ok(m.e.ready('A3') and m.e.restart_release('A3',(-5.0,0.0,2.0),'A4') and catch(m,'A4',(60,80)),'restart after the boundary')
    s.possession_ms=8000;m.e.foul('B3','A4','late_hold')
    ok(s.owner=='A' and s.tackle_count==1 and s.possession_ms==20000,'count kept through an ordinary defensive foul, with the clock floor')
    for label,act in (('opposing control',lambda m:(m.e.release('A0',(10.0,0.0,2.0),'pass','A1'),catch(m,'B4',(60,50)))),
                      ('a boundary award to the opponents',lambda m:(m.e.release('A0',(0.0,10.0,2.0),'pass'),m.e.boundary(50.0,100.5))),
                      ('possession-clock expiry',lambda m:(setattr(m.s,'possession_ms',400),m.e.advance(400))),
                      ('a goal',lambda m:(m.e.release('A0',(20.0,0.0,0.0),'shot'),m.e.goal('B',50,1)))):
        m=c2m();s=m.s;one(m);ok(s.tackle_count==1,'count one before '+label);act(m)
        ok(s.owner=='B' and s.tackle_count==0,'count cleared by '+label)
    m=c2m();s=m.s;one(m);m.e.release('A0',(-20.0,0.0,0.0),'pass');k=len(m.e.log);m.e.goal('A',50,1)
    ok(s.owner=='A' and s.score['B']>0 and s.tackle_count==0 and ev(m,k).count('occupancy_cleared')==1,'an own goal ends the possession even though the same team restarts')

    # ---- 3. one count per grounding; freeze and release priority ----
    m=c2m();s=m.s;put(m,'B1',(50,51.3));w=s.ball.version;k=len(m.e.log)
    m.e.batch([Ty.Event('tackle','B0','A0',{'control_witness':w}),Ty.Event('tackle','B1','A0',{'control_witness':w})])
    ok(ev(m,k).count('tackle_count')==1 and s.tackle_count==1 and 'superseded_observation' in ev(m,k),'two tacklers, one grounding, one count')
    m=c2m();s=m.s;w=s.ball.version;k=len(m.e.log)
    m.e.batch([Ty.Event('tackle','B0','A0',{'control_witness':w}),Ty.Event('freeze',None,'A0',{})])
    ok('freeze' in ev(m,k) and 'tackle_count' not in ev(m,k) and s.tackle_count==0 and s.owner=='A','freeze and tackle at one instant: the freeze governs, no tackle is counted')
    m=c2m();s=m.s;w=s.ball.version;m.e.release('A0',(10.0,0.0,2.0),'pass','A1');k=len(m.e.log);m.e.batch([Ty.Event('tackle','B0','A0',{'control_witness':w})])
    ok('tackle_count' not in ev(m,k) and s.tackle_count==0 and s.ball.mode==Ty.BallMode.PASS,'a release before completion stands; the late tackle does not happen')

    # ---- 4. where the first tackle happened is read from the ball at completion ----
    m=c2m((79.5,50.0));s=m.s;tk(m);ok(last(m,'tackle_count')['where']=='attacked_zone' and s.restart.kind=='inbound','ball inside the arc, pelvis outside: attacked zone')
    m=c2m((79.0,50.0));s=m.s;tk(m);ok(last(m,'tackle_count')['where']=='outside' and s.recovery is not None,'ball short of the arc: live recovery')
    m=c2m((10.0,50.0));s=m.s;tk(m);ok(last(m,'tackle_count')['where']=='own_zone' and s.recovery is not None and s.reconstruction is None,'first tackle in the team own zone: live recovery')
    m=c2m((5.0,50.0),carrier='A10');s=m.s;tk(m);ok(last(m,'tackle_count')['procedure']=='live_recovery' and s.owner=='A' and s.tackle_count==1,'own-zone first tackle on the Keeper: live recovery')

    # ---- 5. recovery deadlines ----
    m=c2m();s=m.s;tk(m);put(m,'B0',(60,50));k=len(m.e.log);m.e.advance(3000)
    ok(s.owner=='B' and s.restart.reason=='pickup_timeout' and s.tackle_count==0 and s.possession_ms==45000,'no pickup in three live seconds: ordinary opposing free pass')
    ok(last(m,'recovery_failed')['reason']=='pickup_timeout','the failed recovery is logged')
    m=c2m();s=m.s;s.possession_ms=1000;tk(m);put(m,'B0',(60,50));m.e.advance(1000)
    ok(s.owner=='B' and s.restart.reason=='possession_expiry','the possession clock still expires during a first-tackle recovery')
    m=c2m();s=m.s;tk(m);ok(not m.e.goal('B',50,1) and s.score=={'A':0,'B':0},'an unpicked award ball cannot score')

    # ---- 6. the one-metre disc ----
    m=c2m();s=m.s;tk(m);B0=s.players['B0'];B0.posture='grounded';B0.next_action=s.now+800;k=len(m.e.log);m.e.advance(100)
    d=last(m,'recovery_obstruction');ok(d['player']=='B0' and d['unavoidable'] and d['clear_by']>=s.now+700 and d['body_inside_disc_m']>0,'a grounded tackler inside the disc is an unavoidable obstruction, measured against his body')
    B0.next_action=d['clear_by']+500;m.e.advance(d['clear_by']-s.now+200);ok(not fouls(m,k) and s.recovery is not None,'a tackler who cannot move is not penalised, even past his clearing time')
    B0.posture='upright';s.possession_ms=9000;m.e.advance(100)
    ok(fouls(m,k)==['recovery_interference'] and last(m,'foul')['actor']=='B0','once able to leave, staying in the disc is interference')
    r=s.restart;ok(s.phase==DEAD and r.kind=='recovery' and r.reason=='recovery_restored' and s.owner=='A' and s.tackle_count==1 and s.recovery is None,'interference: play stops, recovery to be restored, count kept')
    ok(s.possession_ms==20000 and 'warning' in ev(m,k),'interference: defensive-foul clock floor and discipline')
    ok(last(m,'recovery_interrupted')['cause']=='defensive_foul:recovery_interference','the interruption is logged with its cause')
    m2=c2m();s2=m2.s;tk(m2);sp=s2.recovery['spot'];B=s2.players['B0'];m2.e.advance(100);clear_by=last(m2,'recovery_obstruction')['clear_by'];m2.e.advance(clear_by-s2.now+100)
    r=s2.restart;ok(s2.phase==DEAD and (r.x,r.y)==sp and r.kind=='recovery','the restored recovery is at the original spot, not relocated')
    ok(m2.e.recovery_blockers(r)==[B],'the restored recovery waits for the disc to clear')
    put(m2,'B0',(sp[0]+5,sp[1]));ok(m2.e.resume_recovery() and s2.phase==AWARD and s2.award_deadline==s2.now+3000 and s2.recovery['replacement'],'replacement recovery: three seconds from readiness')
    ok(pick(m2,'A1') and last(m2,'recovery_pickup')['replacement'] and s2.tackle_count==1,'the replacement recovery is picked up with the count kept')
    m=c2m();s=m.s;tk(m);m.e.advance(100);put(m,'B0',(56,50));k=len(m.e.log);m.e.advance(2000);ok(not fouls(m,k),'a tackler who leaves in time commits no offence')
    m=c2m();s=m.s;tk(m);put(m,'B0',(56,50));m.e.advance(500);put(m,'B5',(s.ball.x+.5,s.ball.y+.5));k=len(m.e.log);m.e.advance(1)
    ok(fouls(m,k)==['recovery_interference'] and last(m,'recovery_obstruction').get('entered_late'),'entering the disc when clear and able is avoidable occupation: interference')
    m=c2m();s=m.s;tk(m);put(m,'B0',(56,50));put(m,'B5',(s.ball.x+3.0,50));put(m,'A5',(s.ball.x+2.2,50));k=len(m.e.log)
    ok(m.e.engage('B5','A5','block') and not fouls(m,k) and s.recovery is not None,'legal screening outside the disc remains possible')
    put(m,'B5',(s.ball.x+1.2,50));put(m,'A5',(s.ball.x+.4,50));ok(not m.e.engage('B5','A5','block') and fouls(m,k)==['protected_recovery'] and s.restart.kind=='recovery','contact inside the disc is interference')
    m=c2m();s=m.s;tk(m);k=len(m.e.log);ok(not m.e.acquire('B0') and fouls(m,k)==['exclusive_recovery'] and s.restart.kind=='recovery' and s.tackle_count==1,'an opponent playing the awarded ball is interference')
    m=c2m();s=m.s;tk(m);sp=s.recovery['spot'];B0=put(m,'B0',(sp[0]+.2,sp[1]),False);B0.posture='grounded';B0.next_action=s.now+10**7;p0=s.possession_ms;k=len(m.e.log);m.e.advance(3000)
    ok(s.owner=='A' and s.restart.kind=='recovery' and last(m,'recovery_interrupted')['cause']=='unavoidable_obstruction' and not fouls(m,k),'pickup physically impossible: safe restoration, not a timeout')
    ok(s.tackle_count==1 and s.possession_ms==p0-3000 and (s.restart.x,s.restart.y)==sp,'safe restoration keeps count, clock and spot')
    B0.posture='upright';B0.next_action=0;k=len(m.e.log);m.e.advance(30000)
    ok(fouls(m,k)==['deliberate_restart_delay'] and s.restart.kind=='recovery' and (s.restart.x,s.restart.y)==sp and s.owner=='A','restored recovery: an able opponent still in the disc at the 30-second bound is penalised, and the recovery stays at its spot')
    m=c2m();s=m.s;tk(m);sp=s.recovery['spot'];B0=put(m,'B0',(sp[0]+.2,sp[1]),False);B0.posture='grounded';B0.next_action=s.now+10**7;m.e.advance(3000);B0.freeze_until=s.now+10**7;k=len(m.e.log);m.e.advance(30000)
    ok(not fouls(m,k) and s.phase==AWARD and s.recovery['replacement'],'restored recovery: an opponent who cannot move does not block the 30-second bound')

    # ---- 7. arrows and the awarded ball ----
    def archery(at=(50.0,50.0)):
        m=c2m(at);s=m.s;put(m,'A11',(25,-5));put(m,'B11',(75,105));return m
    m=archery();s=m.s;tk(m);k=len(m.e.log);v=(0.0,-20.0,5.0)
    ok(not m.e.shoot_arrow('B11','ball',v) and fouls(m,k)==['archery_target'] and s.owner=='A' and s.restart.kind=='recovery' and s.tackle_count==1,'a defending arrow aimed at the awarded ball: sanctioned, recovery restored')
    m=archery((30.0,30.0));s=m.s;tk(m);k=len(m.e.log)
    ok(not m.e.shoot_arrow('A11','ball',(0.0,20.0,5.0)) and fouls(m,k)==['archery_target'] and s.owner=='B' and s.tackle_count==0 and last(m,'recovery_failed')['reason']=='foul','an attacking arrow aimed at the awarded ball forfeits the recovery')
    m=archery();s=m.s;s.ball.carrier=None;s.ball.mode=Ty.BallMode.LOOSE;s.ball.z=.1075
    ar=m.e.shoot_arrow('B11','ball',v);ok(bool(ar),'an arrow at a loose ball is a legal shot')
    give(m,'A0');tk(m);put(m,'B0',(60,50));m.e.advance(1500);p0=s.possession_ms;k=len(m.e.log);m.e.arrow_impact(ar.id,None,kind='ball')
    d=last(m,'recovery_interrupted');ok(d['cause']=='incidental_arrow' and d['remaining_ms']==2000 and not fouls(m,k),'a previously legal arrow is not an offence: neutral interruption with at least two seconds')
    ok(s.owner=='A' and s.tackle_count==1 and s.possession_ms==p0 and s.restart.kind=='recovery','incidental arrow: count and clock kept, original spot')
    ok(m.e.resume_recovery() and s.award_deadline==s.now+2000,'the restored recovery resumes with the remaining time, minimum two seconds')

    # ---- 8. goal-line inbound ----
    def zone_tackle(at=(90.0,44.0),**over):
        m=c2m(at,**over);m.s.possession_ms=30000;tk(m);return m
    m=zone_tackle();s=m.s;r=s.restart
    d=last(m,'tackle_count');ok((d['where'],d['procedure'],d['count_to'])==('attacked_zone','zone_inbound',1),'first tackle in the attacked zone: inbound')
    ok(s.phase==DEAD and r.kind=='inbound' and (r.x,r.y)==(100.0,42.0) and r.clearance==3.0 and r.taker_spot==(100.4,42.0),'inbound mark on the end line, 8 m from the goal centre, nearer side')
    ok(s.owner=='A' and s.tackle_count==1 and s.possession_ms==30000 and s.reconstruction=={'team':'A','zone':1,'live_since':s.live_ms},'inbound keeps clock and count; reconstruction is set')
    ok(zone_tackle((90.0,56.0)).s.restart.y==58.0,'the other side of the goal uses the other mark')
    m=c2m((90.0,50.0));put(m,'A1',(85,70));put(m,'A2',(88,75));tk(m);ok(m.s.restart.y==58.0,'exact tie: the attacking side chooses (placeholder: the side with more unmarked team-mates)')
    m=zone_tackle();s=m.s;r=s.restart;g0=s.game_ms;m.e.advance(2000);ok(s.game_ms==g0 and s.possession_ms==30000,'inbound setup is dead time')
    A1=put(m,'A1',(100.4,42.0));ok(not m.e.eligible(A1),'a player outside the field is not eligible for ordinary play')
    put(m,'B0',(97.5,42.0));ok(not m.e.ready('A1'),'an opponent inside three metres: not ready')
    put(m,'B0',(96.5,42.0));ok(m.e.ready('A1'),'three-metre clearance, not the usual five; the taker stands outside the field')
    put(m,'A2',(70,42));ok(m.e.restart_release('A1',(-15.0,0.0,3.0),'A2') and s.phase==LIVE and s.reconstruction is not None and not s.ball.scoring,'a valid inbound release does not clear the zone and cannot score directly')
    m.e.advance(500);ok(s.possession_ms==29500,'clocks resume on the release')
    k=len(m.e.log);ok(not m.e.goal('B',50,1) and last(m,'no_goal')['reason']=='reconstruction_uncleared' and s.score['A']==0,'no direct goal from the inbound')
    m=zone_tackle();s=m.s;put(m,'A1',(100.4,42.0));m.e.ready('A1');m.e.restart_release('A1',(-15.0,0.0,3.0),'A2');put(m,'A1',(99.0,42.0));s.ball.x,s.ball.y,s.ball.z=98.5,42.0,1.2;k=len(m.e.log)
    ok(m.e.eligible(s.players['A1']) and not m.e.acquire('A1') and fouls(m,k)==['self_recontact'] and s.owner=='B','the taker may not play the ball again before another player does; lawful re-entry restores eligibility')
    ok(s.tackle_count==0 and s.reconstruction is None and last(m,'reconstruction_ended')['reason']=='opposing_possession','an attacking fault: opposing award, count zero, restriction ended')
    m=zone_tackle();s=m.s;put(m,'A1',(100.4,42.0));m.e.ready('A1');put(m,'B0',(98.0,42.0));s.possession_ms=5000;k=len(m.e.log)
    ok(not m.e.restart_release('A1',(-15.0,0.0,3.0),'A2'),'a defender inside three metres at the release: no release')
    r=s.restart;ok(r.kind=='inbound' and (r.x,r.y)==(100.0,42.0) and r.reason=='defensive_restart_fault' and r.ready_at is None,'defensive fault: retake at the same mark, no relocation')
    ok(s.possession_ms==20000 and s.tackle_count==1 and s.reconstruction is not None and 'inbound_encroachment' in ev(m,k) and 'warning' in ev(m,k),'defensive fault: clock floor, discipline, count and restriction kept')
    m=zone_tackle();s=m.s;put(m,'A1',(100.4,42.0));m.e.restart_release('A1',(-15.0,0.0,3.0),'A2')
    ok(s.owner=='B' and s.restart.reason=='restart_fault' and s.possession_ms==45000 and s.tackle_count==0 and s.reconstruction is None,'attacking fault at the inbound: ordinary opposing award')
    m=zone_tackle();s=m.s;put(m,'A1',(100.4,42.0));m.e.ready('A1');ok(not m.e.restart_release('A1',(-15.0,0.0,3.0),'A2',method='kick') and s.owner=='B' and s.restart.reason=='restart_fault','the inbound may not be kicked')
    m=zone_tackle();s=m.s;put(m,'A1',(100.4,42.0));m.e.ready('A1');put(m,'A1',(99.0,43.5));ok(not m.e.restart_release('A1',(-15.0,0.0,3.0),'A2') and s.owner=='B','the taker may not run up from the mark')
    m=zone_tackle();s=m.s;put(m,'A1',(100.4,42.0));m.e.ready('A1');ok(not m.e.restart_release('A3',(-15.0,0.0,3.0),'A2') and s.owner=='B','only the named taker releases: no hand-off')
    m=zone_tackle();s=m.s;put(m,'A1',(100.4,42.0));m.e.ready('A1');m.e.advance(5000);ok(s.owner=='B' and s.restart.reason=='restart_timeout' and s.reconstruction is None,'five seconds to execute after ready')
    m=zone_tackle();s=m.s;put(m,'B0',(98.5,42.0));k=len(m.e.log);m.e.advance(30000);r=s.restart
    ok(fouls(m,k)==['deliberate_restart_delay'] and s.owner=='A' and r.kind=='inbound' and (r.x,r.y)==(100.0,42.0) and s.tackle_count==1,'30-second bound: a defender blocking the mark is penalised and the inbound stays at its mark')
    m=zone_tackle();s=m.s;put(m,'B0',(90.0,60.0));m.e.advance(30000);ok(s.owner=='B' and s.reconstruction is None,'30-second bound with the mark clear: the attacking side is at fault')
    m=zone_tackle();s=m.s;put(m,'B0',(90.0,60.0))
    for q in s.players.values():
        if q.team=='A' and q.role!='archer':q.available=False
    m.e.advance(30000);ok(s.phase==Ty.Phase.FINAL and last(m,'forfeit')['reason']=='no_restart_taker','setup incapacity goes to the existing lineup administration, not indefinite waiting')
    m=zone_tackle();s=m.s;m.e.foul('B3','A2','late_hold');r=s.restart
    ok(r.kind=='inbound' and (r.x,r.y)==(100.0,42.0) and r.reason=='foul' and s.reconstruction is not None and s.tackle_count==1,'a defensive foul during inbound setup: retake at the same mark')
    m=zone_tackle();s=m.s;A1=put(m,'A1',(95.0,42.0));m.e.advance(100);A1.zone_ms[1]=3000;put(m,'A1',(100.4,42.0));k=len(m.e.log);m.e.advance(100)
    ok(A1.zone_ms[1]==3000 and 'zone_exit_invalid' in ev(m,k),'the taker stored count is kept, not reset, outside the field')
    m.e.ready('A1');m.e.restart_release('A1',(-15.0,0.0,3.0),'A2');put(m,'A1',(99.0,42.0));m.e.advance(100);ok(A1.zone_ms[1]==3100,'and it continues on re-entry')
    m=zone_tackle();s=m.s;A3=put(m,'A3',(85.0,50.0));m.e.advance(100);A3.zone_ms[1]=3000;put(m,'A3',(78.0,50.0));m.e.advance(100);ok(A3.zone_ms[1]==0,'a player may reset by crossing the arc during setup')

    # ---- 9. reconstruction: what clears it and what does not ----
    def uncleared(to=None):
        """An inbound has been released; the ball is live and the zone is uncleared."""
        m=zone_tackle();put(m,'B0',(90.0,60.0));put(m,'A1',(100.4,42.0));m.e.ready('A1');m.e.restart_release('A1',(-15.0,0.0,3.0),'A2')
        if to:catch(m,*to)
        return m
    m=uncleared(('A2',(90.0,45.0)));s=m.s;ok(s.reconstruction is not None,'secure control inside the zone does not clear it')
    m.e.release('A2',(20.0,0.0,0.0),'shot');k=len(m.e.log);ok(not m.e.goal('B',50,1) and s.score['A']==0,'no goal counts while uncleared')
    ok(ev(m,k).count('boundary')==1 and ev(m,k).count('no_goal')==1 and s.restart.reason=='boundary','uncleared goal: disabled-ball end-boundary handling, exactly one boundary')
    m=uncleared(('A2',(90.0,45.0)));s=m.s;m.e.release('A2',(20.0,0.0,0.0),'pass');m.e.touch('B10',False)
    ok(not m.e.goal('B',50,1) and s.score=={'A':0,'B':0},'an apparent own goal off a deflection does not count while uncleared')
    m=uncleared();s=m.s;put(m,'A3',(79.5,50.0));s.ball.x,s.ball.y,s.ball.z=80.5,50.0,1.2
    ok(m.e.zone(s.ball.x,s.ball.y)==1 and m.e.acquire('A3') and s.reconstruction is None,'a player outside the arc reaches in and secures a ball that never left the zone: cleared')
    d=last(m,'reconstruction_cleared');ok(d['witness']=='secure_control' and d['player']=='A3' and d['pelvis']==[79.5,50.0],'the clearance witness is logged')
    m.e.release('A3',(20.0,0.0,0.0),'shot');ok(m.e.goal('B',50,1) and s.score['A']>0,'after clearance a goal counts')
    m=uncleared();s=m.s;put(m,'A3',(80.0,50.0));s.ball.x,s.ball.y,s.ball.z=80.5,50.0,1.2;ok(m.e.acquire('A3') and s.reconstruction is not None,'pelvis exactly on the arc is inside the zone: not cleared')
    m=uncleared();s=m.s;put(m,'A3',(75.0,50.0));m.e.touch('A3',False);ok(s.reconstruction is not None,'an accidental touch does not clear')
    m.e.touch('A3',True);ok(s.reconstruction is None and last(m,'reconstruction_cleared')['witness']=='deliberate_play','a deliberate play outside the arc clears')
    m=uncleared();s=m.s;put(m,'A3',(75.0,50.0));s.ball.x,s.ball.y,s.ball.z=75.5,50.0,.5;ok(m.e.strike('A3',(-5.0,0.0,1.0)) and s.reconstruction is None,'a deliberate strike outside the arc clears')
    m=uncleared();s=m.s;s.ball.x,s.ball.y=60.0,42.0;m.e.advance(200);m.e.frame_contact();ok(s.reconstruction is not None,'ball flight out of the zone and a frame contact do not clear')
    ok(not m.e.reconstruction_check(put(m,'A3',(101.0,30.0)),'test') and not m.e.reconstruction_check(put(m,'B3',(60.0,30.0)),'test'),'a player outside the field, or an opponent, cannot clear')
    A3=put(m,'A3',(60.0,30.0));A3.posture='grounded';ok(not m.e.reconstruction_check(A3,'test'),'a grounded player cannot clear');A3.freeze_until=s.now+5000;A3.posture='upright';ok(not m.e.reconstruction_check(A3,'test'),'a frozen player cannot clear')
    m=uncleared(('A2',(90.0,45.0)));s=m.s;m.e.advance(100);ok(s.reconstruction is not None,'carrying inside the zone does not clear');put(m,'A2',(78.0,45.0));m.e.advance(100)
    ok(s.reconstruction is None and last(m,'reconstruction_cleared')['witness']=='carried_out','carrying the ball out across the arc clears')
    m=uncleared(('A2',(90.0,45.0)));s=m.s;m.e.release('A2',(0.0,10.0,2.0),'pass');s.ball.last_touch='B';m.e.boundary(90.0,100.5);ok(s.owner=='A' and s.reconstruction is not None,'kept through a same-team boundary')
    m=uncleared(('A2',(90.0,45.0)));s=m.s;put(m,'A5',(75.0,-1.0));n=put(m,'A12',(75.0,-.5));ok(m.e.sub('A5','A12') and s.reconstruction is not None,'kept through a substitution')
    m.e.foul('B3','A2','late_hold');r=s.restart;ok(s.owner=='A' and s.reconstruction is not None and r.kind=='free_pass' and m.e.zone(r.x,r.y) is None,'kept through a foul award; the ordinary restart is normalised outside the arc')
    put(m,'A3',(r.x,r.y));ok(m.e.ready('A3'),'the free pass is ready');m.e.advance(1000);ok(s.reconstruction is not None,'dead-ball possession at the mark and normalisation do not clear')
    ok(m.e.restart_release('A3',(10.0,0.0,3.0),'A2') and s.reconstruction is None and last(m,'reconstruction_cleared')['witness']=='restart_release','a valid ordinary restart release beyond the arc clears')
    k=len(m.e.log);ok(not s.ball.scoring and not m.e.goal('B',50,1) and last(m,'no_goal')['reason']=='ineligible_ball','clearing does not lift the separate free-pass direct-score prohibition')
    m=uncleared(('A3',(75.0,50.0)));s=m.s;ok(s.reconstruction is None,'cleared by control outside the arc');m.e.freeze('A3');ok(not s.ball.scoring and not m.e.goal('B',50,1),'clearing does not lift the separate mandatory-release restriction after a freeze')
    m=uncleared(('A2',(90.0,45.0)));s=m.s;put(m,'B1',(91.3,45.0));tk(m,'B1')
    ok(s.owner=='B' and s.tackle_count==0 and s.reconstruction is None and last(m,'reconstruction_ended')['reason']=='opposing_possession','a second tackle gives the defence ordinary possession and ends the restriction')
    m=uncleared();s=m.s;s.ball.z=2.0;s.ball.mode=Ty.BallMode.SHOT;s.game_ms=300;k=len(m.e.log);m.e.advance(300)
    ok('no_finishing_flight' in ev(m,k) and 'finishing_flight' not in ev(m,k) and 'period_end' in ev(m,k),'no score-based finishing flight for an uncleared ball at the horn')
    m=uncleared(('A3',(75.0,50.0)));s=m.s;m.e.release('A3',(20.0,0.0,5.0),'shot');s.game_ms=300;k=len(m.e.log);m.e.advance(300);ok('finishing_flight' in ev(m,k),'a cleared ball keeps its finishing flight at the horn')
    m=uncleared(('A2',(90.0,45.0)));s=m.s;k=len(m.e.log);m.e.foul('B3','A2','serious_foul',major=True,danger=True,penalty=True)
    ok(s.phase==Ty.Phase.PENALTY and 'penalty_start' in ev(m,k),'independent serious-foul penalty grounds still apply while uncleared')
    rn=s.penalty['runner'];s.players[rn].posture='upright';m.e.release(rn,(20.0,0.0,0.0),'shot');m.e.goal('B',50,1)
    ok('penalty_goal_scored' in ev(m,k) and s.score['A']>0 and s.reconstruction is None and s.tackle_count==0 and s.restart.reason=='penalty_retained','a penalty is scored under its own procedure, and the possession after it is new')
    m=c2m();s=m.s;tk(m);k=len(m.e.log);m.e.foul('B0','A0','serious_foul',major=True,danger=True,penalty=True);rn=s.penalty['runner'];s.players[rn].posture='upright';m.e.release(rn,(20.0,0.0,0.0),'shot');m.e.goal('B',50,1)
    ok(s.recovery is None and s.restart.reason=='penalty_retained' and s.restart.kind=='free_pass' and s.tackle_count==0 and last(m,'recovery_superseded')['reason']=='penalty_retained','a penalty during a recovery supersedes it: the possession after the penalty is new')
    m=uncleared(('A2',(90.0,45.0)));s=m.s;s.game_ms=0;m.e.foul('B3','A2','late_hold')
    ok(s.extension and s.extension_team=='A' and s.possession_ms==10000 and s.reconstruction is not None,'a zero-time foul keeps its existing administration while uncleared')
    m=uncleared();s=m.s;put(m,'A3',(75.0,50.0));k=len(m.e.log);m.e.batch([Ty.Event('foul','B3','A3',{'reason':'late_hold'}),Ty.Event('touch','A3',None,{'deliberate':True})])
    order=ev(m,k);ok(order.index('reconstruction_cleared')<order.index('foul'),'clearance and a foul at one instant: the play is resolved first, then the foul')

    # ---- 10. second tackle, possession clock and the horn ----
    def second(p_ms=None,g_ms=None):
        m=c2m();s=m.s;one(m);put(m,'B1',(s.players['A0'].x+1.3,50.0))
        if p_ms is not None:s.possession_ms=p_ms
        if g_ms is not None:s.game_ms=g_ms
        return m
    m=second(p_ms=300);s=m.s;w=s.ball.version;m.e.elapse(300,resolve=False);k=len(m.e.log);m.e.batch([Ty.Event('tackle','B1','A0',{'control_witness':w})]);m.e.resolve_timers()
    ok(s.owner=='B' and s.phase==AWARD and s.possession_ms==45000 and 'tackle_award' in ev(m,k) and not any(r['event']=='restart_awarded' for r in m.e.log[k:]),'second tackle and clock expiry at one instant: the tackle award stands with its fresh clock')
    m=second(p_ms=300);s=m.s;w=s.ball.version;m.e.advance(300);k=len(m.e.log);m.e.batch([Ty.Event('tackle','B1','A0',{'control_witness':w})])
    ok(s.restart.reason=='possession_expiry' and 'tackle_count' not in ev(m,k) and s.tackle_count==0,'a tackle completed after expiry cannot revive the possession or be counted')
    m=second(g_ms=300);s=m.s;w=s.ball.version;per=s.period;m.e.elapse(300,resolve=False);k=len(m.e.log);m.e.batch([Ty.Event('tackle','B1','A0',{'control_witness':w})]);m.e.resolve_timers()
    ok('period_end' in ev(m,k) and s.period==per+1 and s.restart.reason=='quarter_start' and s.tackle_count==0 and s.recovery is None,'second tackle at the horn: the period ends; no fresh ordinary possession extends play')
    m=c2m();s=m.s;s.possession_ms=300;w=s.ball.version;m.e.elapse(300,resolve=False);k=len(m.e.log);m.e.batch([Ty.Event('tackle','B0','A0',{'control_witness':w})]);m.e.resolve_timers()
    ok(ev(m,k).count('tackle_count')==1 and s.owner=='B' and s.restart.reason=='possession_expiry' and s.possession_ms==45000,'first tackle and clock expiry at one instant: the first tackle does not defeat the expiry')
    m=c2m();s=m.s;s.game_ms=300;m.e.elapse(300,resolve=False);tk(m);k=len(m.e.log);m.e.resolve_timers();ok('period_end' in ev(m,k) and s.recovery is None and s.tackle_count==0,'first tackle at the horn: the period ends and the recovery with it')
    m=c2m();s=m.s;m.e.release('A0',(20.0,0.0,0.0),'shot');k=len(m.e.log)
    m.e.batch([Ty.Event('goal',None,None,{'defending':'B','y':50.0,'z':1.0}),Ty.Event('boundary',None,None,{'x':100.5,'y':50.0})])
    ok(ev(m,k).count('goal')==1 and 'boundary' not in ev(m,k),'a valid aperture crossing is a goal and not also an ordinary boundary')

    # ---- 11. occupancy: the team in possession ----
    def occ(**pos):
        m=c2m(tackler=None)
        for pid,xy in pos.items():put(m,pid,xy)
        return m
    m=occ(A1=(90,50));s=m.s;A1=s.players['A1'];k=len(m.e.log);m.e.advance(4900);ok(A1.zone_ms[1]==4900 and not fouls(m,k),'an attacker in the zone accrues time')
    m.e.advance(100);d=last(m,'attacking_zone_expiry');ok(fouls(m,k)==['zone_expiry'] and s.owner=='B' and d['player']=='A1' and d['possible_exit_interference'] is False,'five seconds: attacking expiry, logged apart from the turnover')
    m=occ(A1=(90,50));s=m.s;A1=s.players['A1'];m.e.advance(4000);put(m,'A1',(79,50));k=len(m.e.log);m.e.advance(100)
    ok(A1.zone_ms[1]==0 and last(m,'zone_exit_valid')['stored_ms']==4000,'an exit across the arc inside the field resets the count at once')
    put(m,'A1',(90,50));m.e.advance(4000);ok(A1.zone_ms[1]==4000 and not fouls(m,k),'re-entry starts from zero: no outside wait')
    m=occ(A1=(80,50));s=m.s;A1=s.players['A1'];m.e.advance(1000);ok(A1.zone_ms[1]==1000,'pelvis exactly on the arc is in the zone')
    put(m,'A1',(79.999,50));m.e.advance(100);ok(A1.zone_ms[1]==0,'a hair outside the arc is out')
    m=occ(A1=(95,50));s=m.s;A1=s.players['A1'];m.e.advance(4000);put(m,'A1',(100.5,50));k=len(m.e.log);m.e.advance(3000)
    ok(A1.zone_ms[1]==4000 and 'zone_exit_invalid' in ev(m,k) and not fouls(m,k),'an exit over the end line pauses and keeps the count')
    put(m,'A1',(100.5,20));m.e.advance(100);put(m,'A1',(99,20));m.e.advance(100)
    ok(A1.zone_ms[1]==4000 and m.e.zone(99,20) is None and 'zone_reentry_no_reset' in ev(m,k),'re-entry beyond the zone footprint does not reset it')
    put(m,'A1',(90,50));m.e.advance(900);ok(not fouls(m,k),'no expiry before five seconds in total');m.e.advance(100);ok(fouls(m,k)==['zone_expiry'],'the kept count runs on when he returns to the zone')
    m=occ(A1=(95,50));s=m.s;A1=s.players['A1'];m.e.advance(4000);put(m,'A1',(100.5,50));m.e.advance(100);put(m,'A1',(95,50));m.e.advance(100);put(m,'A1',(79,50));m.e.advance(100)
    ok(A1.zone_ms[1]==0,'only a later in-field arc crossing renews it')
    for label,act,pause in (('frozen',lambda m,q:setattr(q,'freeze_until',m.s.now+2000),True),('recognised tackle recovery',lambda m,q:setattr(q,'tackled_until',m.s.now+2000),True),
                            ('voluntary grounding',lambda m,q:m.e.grounded(q.id),False),('an upright grip',lambda m,q:m.e.engage('B5','A1','block'),False)):
        m=occ(A1=(90,50),B5=(91.2,50));s=m.s;A1=s.players['A1'];act(m,A1);z=A1.zone_ms[1];m.e.advance(2000)
        ok(A1.zone_ms[1]==z+(0 if pause else 2000),'occupancy '+('pauses while ' if pause else 'does not pause for ')+label)
    m=occ(A1=(90,50));s=m.s;A1=s.players['A1'];m.e.advance(1000);z=A1.zone_ms[1];m.e.award('A',50,50,'test');m.e.advance(5000);ok(A1.zone_ms[1]==z,'dead time does not accrue occupancy')
    m=occ(A1=(90,50),B3=(90,60));s=m.s;m.e.advance(3000);A1,B3=s.players['A1'],s.players['B3'];z,u=A1.zone_ms[1],B3.unmarked_ms[1]
    m.e.release('A0',(10.0,0.0,2.0),'pass');m.e.touch('B4',False);m.e.advance(100);ok(A1.zone_ms[1]==z+100 and B3.unmarked_ms[1]==u+100,'a deflection or a loose ball with possession unchanged clears nothing')
    s.ball.last_touch='B';m.e.boundary(50.0,100.5);ok(s.owner=='A' and A1.zone_ms[1]==z+100,'a same-team award clears nothing')
    k=len(m.e.log);m.e.new_owner('B','control');d=last(m,'occupancy_cleared')
    ok(A1.zone_ms==[0,0] and B3.unmarked_ms==[0,0] and d['players_with_stored_time']==2 and d['team']=='B','a true possession change clears every stored count for both teams, and is logged')

    # ---- 12. occupancy: defenders and marking ----
    m=occ(B3=(90,50),A1=(88,50));s=m.s;B3=s.players['B3'];m.e.advance(6000);ok(B3.unmarked_ms[1]==0 and B3.zone_ms[1]==0,'a defender marking an attacker may stay')
    m=occ(B3=(81,50),A1=(78.5,50));s=m.s;m.e.advance(6000);ok(s.players['B3'].unmarked_ms[1]==0 and m.e.zone(78.5,50) is None,'an attacker outside the zone but in the field can be the marked player')
    m=occ(B3=(90,50),A1=(87,50));s=m.s;m.e.advance(6000);ok(s.players['B3'].unmarked_ms[1]==0,'exactly at marking distance counts as marking')
    m=occ(B3=(90,50),A1=(86.9,50));s=m.s;m.e.advance(2000);ok(s.players['B3'].unmarked_ms[1]==2000,'just beyond marking distance: the unmarked allowance runs')
    put(m,'A1',(88,50));m.e.advance(100);ok(s.players['B3'].unmarked_ms[1]==0,'regaining proximity ends and renews the allowance')
    put(m,'A1',(70,50));m.e.advance(4000);ok(s.players['B3'].unmarked_ms[1]==4000,'losing proximity starts a fresh allowance')
    m=occ(B3=(90,50),B4=(90,52),A1=(88,51));s=m.s;m.e.advance(6000);ok(s.players['B3'].unmarked_ms[1]==0 and s.players['B4'].unmarked_ms[1]==0,'several defenders may mark the same attacker')
    m=occ(B3=(90,50),A1=(88,50));s=m.s;s.players['A1'].freeze_until=s.now+4000;m.e.advance(3000);ok(s.players['B3'].unmarked_ms[1]==3000,'a frozen attacker gives no marking exemption')
    m=occ(B3=(99,50),A1=(100.5,50));s=m.s;m.e.advance(3000);ok(s.players['B3'].unmarked_ms[1]==3000,'an attacker outside the field gives no marking exemption')
    m=occ(B3=(90,50),B10=(97,50));s=m.s;m.e.advance(4000);ok(s.players['B10'].unmarked_ms[1]==0 and s.players['B10'].zone_ms[1]==0,'the Keeper is exempt in his own zone')
    m.s.players['B3'].freeze_until=m.s.now+500;m.e.advance(500);ok(m.s.players['B3'].unmarked_ms[1]==4000,'a frozen defender allowance pauses')
    m=c2m((95.0,50.0),tackler=None,carrier='A0');s=m.s;m.e.new_owner('B','control');put(m,'B10',(97,50));give(m,'B10');k=len(m.e.log);m.e.advance(4900);ok(not fouls(m,k) and s.players['B10'].keeper_hold_ms==4900 and s.players['B10'].zone_ms[1]==0,'the Keeper ball-hold timer is separate from occupancy')
    put(m,'A0',(60,50));m.e.advance(100);ok(fouls(m,k)==['keeper_hold'],'and still expires at five seconds')
    def camp(p_ms=12000):
        m=occ(B3=(90,50));s=m.s;s.possession_ms=p_ms+5000;m.e.advance(4999);return m
    m=camp();s=m.s;g0,k=s.game_ms,len(m.e.log);m.e.advance(1)
    ok(ev(m,k).count('defensive_unmarked_expiry')==1 and fouls(m,k)==['zone_unmarked'] and 'advantage' in ev(m,k) and s.phase==LIVE and s.owner=='A','unmarked expiry: defensive technical foul, advantage played')
    ok('attacking_zone_expiry' not in ev(m,k) and last(m,'defensive_unmarked_expiry')['player']=='B3','logged apart from attacking expiries')
    put(m,'A0',(57,50));m.e.follow_carrier();m.e.advance(100)
    ok(last(m,'advantage_realized')['method']=='progress' and s.advantage is None and s.owner=='A' and s.phase==LIVE and ev(m,k).count('defensive_unmarked_expiry')==1,'successful advantage: play goes on')
    B3=s.players['B3'];grace=B3.zone_fouled[1]-s.live_ms;ok(0<grace<3000 and B3.unmarked_ms[1]>=5000,'the offender gets only the time physically needed to leave, not a new allowance')
    m.e.advance(grace-1);ok(ev(m,k).count('defensive_unmarked_expiry')==1,'not called again before he could have left');m.e.advance(1)
    ok(ev(m,k).count('defensive_unmarked_expiry')==2 and fouls(m,k)==['zone_unmarked','zone_unmarked'],'still unmarked in the zone after that: called again')
    m=camp();s=m.s;m.e.advance(1);g_foul,k=s.game_ms,len(m.e.log);m.e.advance(3000);r=s.restart
    ok('advantage_recalled' in ev(m,k) and s.phase==DEAD and r.team=='A' and r.reason=='advantage_recalled' and r.kind=='free_pass','failed advantage: free pass to the attack')
    ok(s.game_ms==g_foul and s.possession_ms==20000 and s.tackle_count==0 and 'warning' in ev(m,k),'failed advantage: clocks return to the foul instant with the clock floor; discipline applied')
    B3=s.players['B3'];m.e.advance(4000);ok(B3.unmarked_ms[1]>=5000 and ev(m,k).count('defensive_unmarked_expiry')==0,'the whistle does not renew the allowance, and dead time does not add to it')
    put(m,'A1',(r.x,r.y));m.e.ready('A1');m.e.restart_release('A1',(-5.0,0.0,3.0),'A2');m.e.advance(1)
    ok(ev(m,k).count('defensive_unmarked_expiry')==1,'an offender still unmarked in the zone when play resumes is called again')
    m=camp();s=m.s;m.e.advance(1);m.e.advance(3000);k=len(m.e.log);put(m,'B3',(78,50));m.e.advance(1000);r=s.restart;put(m,'A1',(r.x,r.y));m.e.ready('A1');m.e.restart_release('A1',(-5.0,0.0,3.0),'A2');m.e.advance(100)
    ok(s.players['B3'].unmarked_ms[1]==0 and 'defensive_unmarked_expiry' not in ev(m,k),'leaving across the arc during the stoppage ends the violation')
    m=camp();s=m.s;m.e.advance(1);m.e.advance(3000);k=len(m.e.log);put(m,'A4',(88,50));m.e.advance(1000);ok(s.players['B3'].unmarked_ms[1]==0,'regaining a legitimate marking exemption during the stoppage ends it too')
    m=camp(p_ms=40000);s=m.s;m.e.advance(1);ok(s.advantage['p']==40000,'the advantage remembers the foul instant');m.e.advance(3000);ok(s.possession_ms==40000,'the clock floor does not shorten a longer remaining time')

    # ---- 13. failed advantage with tackles in between: nothing is duplicated ----
    m=camp();s=m.s;put(m,'B0',(51.3,50));m.e.advance(1);t0=s.now;m.e.advance(500);tk(m);put(m,'B0',(58,50));ok(s.tackle_count==1 and s.recovery is not None,'first tackle during an advantage: recovery as usual')
    m.e.advance(900);pick(m,'A0');k=len(m.e.log);m.e.advance(t0+3000-s.now)
    ok('advantage_recalled' in ev(m,k) and s.tackle_count==0 and last(m,'tackle_count_restored')['count_from']==1 and s.owner=='A','failed advantage returns the tackle count to the foul instant')
    M=measure(m.e.log,SETTINGS);c=M['continuation']
    ok(M['per_team']['A']['possessions']==1 and M['per_team']['B']['possessions']==0 and c['tackles']['completed_tackles']==1 and c['tackles']['counts_restored_by_failed_advantage']==1,'measured as one possession and one tackle: no duplicates')
    ok(all(r['live_ms']>=q['live_ms'] and r['t_ms']>=q['t_ms'] for q,r in zip(m.e.log,m.e.log[1:])),'event times never run backwards across the recall')
    m=occ(B3=(90,50),B0=(51.3,50));s=m.s;s.possession_ms=40000;one(m);put(m,'B1',(s.players['A0'].x+1.3,50));put(m,'A3',(92,60));m.e.advance(4100);ok('advantage' in ev(m) and s.tackle_count==1,'advantage with the count at one')
    p_foul=s.advantage['p'];m.e.advance(500);z=s.players['A3'].zone_ms[1];tk(m,'B1');ok(s.owner=='B' and s.tackle_count==0 and s.players['A3'].zone_ms[1]==0,'second tackle during the advantage: turnover')
    k=len(m.e.log);m.e.advance(3000)
    ok(s.owner=='A' and s.tackle_count==1 and last(m,'tackle_count_restored')['count_to']==1 and s.possession_ms==max(20000,p_foul),'failed advantage after a turnover: possession, count and clock return to the foul instant')
    ok(s.players['A3'].zone_ms[1]>0 and last(m,'advantage_state_restored')['possession_changed_during_advantage'],'and so do the stored zone counts')
    M=measure(m.e.log,SETTINGS);ok(M['total_possessions']==3 and all(v is None or v>=0 for v in (M['flow']['possession_live_s']['min'],)) and M['continuation']['tackles']['completed_tackles']==2,'measured without duplicate possessions, negative durations or duplicate tackles')
    m=camp();s=m.s;put(m,'A0',(90,44));give(m,'A0');put(m,'B0',(91.3,44));m.e.advance(1);ok(s.advantage is not None,'advantage pending');k=len(m.e.log);tk(m)
    ok(s.restart.reason=='advantage_recalled' and s.restart.kind=='free_pass' and s.reconstruction is None and s.tackle_count==0 and ev(m,k).count('tackle_count')==1,'first tackle in the attacked zone during an advantage: the stoppage recalls the advantage instead of an inbound')

    # ---- 14. substitution ----
    m=occ();s=m.s;A5=put(m,'A5',(75.0,-1.0));A5.zone_ms=[0,3500];A5.unmarked_ms=[700,0];A5.zone_fouled=[0,9];n=put(m,'A12',(75.0,-.5));k=len(m.e.log)
    ok(m.e.sub('A5','A12') and n.zone_ms==[0,3500] and n.unmarked_ms==[700,0] and n.zone_fouled==[0,9],'a replacement inherits the slot counts, allowance and pending violation')
    m.e.advance(1000);ok(n.zone_ms==[0,3500] and m.e.zone(n.x,n.y) is None and 'zone_exit_valid' not in ev(m,k),'entering from outside is not an arc exit: nothing is refreshed')
    put(m,'A12',(90,60));m.e.advance(1400);ok(not fouls(m,k),'no expiry before five seconds in total');m.e.advance(100);ok(fouls(m,k)==['zone_expiry'],'the inherited count runs on in the zone')

    # ---- 15. predictions made before a change of state are rejected when they arrive ----
    def proposal(pid,kind='acquire',**data):
        return Ty.Event(kind,pid,None,{'c1_contact':True,**data})
    m=c2m();s=m.s;tk(m);put(m,'B0',(58,50));put(m,'A1',(s.ball.x-.5,50));bp=(s.ball.x,s.ball.y,s.ball.z);s.players['A1'].freeze_until=s.now+3000;k=len(m.e.log)
    m.e.batch([proposal('A1',ball_point=bp)]);ok(last(m,'contact_rejected')['reason']=='frozen' and s.recovery is not None and not fouls(m,k),'a recovery pickup predicted before a freeze is rejected and leaves nothing')
    m=c2m();s=m.s;tk(m);put(m,'B0',(58,50));put(m,'A1',(s.ball.x-.5,50));bp=(s.ball.x,s.ball.y,s.ball.z);k=len(m.e.log)
    m.e.batch([proposal('A1',ball_point=bp),Ty.Event('foul','A2','B3',{'reason':'late_hold'})])
    ok(s.owner=='B' and last(m,'contact_rejected')['reason']=='play_stopped' and 'recovery_pickup' not in ev(m,k),'a recovery pickup at the instant of an attacking foul is rejected')
    m=c2m();s=m.s;tk(m);put(m,'B0',(58,50));put(m,'A1',(s.ball.x-.5,50));bp=(s.ball.x,s.ball.y,s.ball.z);m.e.advance(3000);k=len(m.e.log)
    m.e.batch([proposal('A1',ball_point=bp)]);ok(s.owner=='B' and last(m,'contact_rejected')['reason']=='play_stopped' and s.ball.carrier is None,'a recovery pickup predicted before the possession changed is rejected')
    m=c2m();s=m.s;s.game_ms=500;tk(m);put(m,'B0',(58,50));put(m,'A1',(s.ball.x-.5,50));bp=(s.ball.x,s.ball.y,s.ball.z);m.e.advance(500);k=len(m.e.log)
    m.e.batch([proposal('A1',ball_point=bp)]);ok('period_end' in ev(m) and last(m,'contact_rejected')['reason']=='play_stopped' and 'recovery_pickup' not in ev(m),'a recovery pickup predicted before the horn is rejected')
    m=uncleared();s=m.s;A3=put(m,'A3',(75.0,50.0));A3.freeze_until=s.now+3000;k=len(m.e.log)
    m.e.batch([proposal('A3','touch',deliberate=True,ball_point=(75.5,50.0,1.2),velocity=(0.0,0.0,0.0))]);ok(s.reconstruction is not None and 'reconstruction_cleared' not in ev(m,k) and last(m,'contact_rejected')['reason']=='frozen','a clearance predicted before a freeze does not clear')
    m=uncleared();s=m.s;put(m,'A3',(75.0,50.0));k=len(m.e.log);m.e.batch([proposal('A3','touch',deliberate=True,ball_point=(75.5,50.0,1.2),velocity=(0.0,0.0,0.0)),Ty.Event('foul','A2','B3',{'reason':'late_hold'})])
    ok(s.owner=='B' and 'reconstruction_cleared' not in ev(m,k) and last(m,'reconstruction_ended')['reason']=='opposing_possession','a clearance at the instant of an attacking foul: the foul comes first and the restriction ends with the possession')
    m=c2m();s=m.s;w=s.ball.version;k=len(m.e.log);m.e.batch([Ty.Event('tackle','B0','A0',{'control_witness':w}),Ty.Event('foul','B3','A2',{'reason':'contact_speed','major':True,'danger':True})])
    ok('tackle_count' not in ev(m,k) and s.tackle_count==0 and s.restart.reason=='foul' and s.owner=='A','a tackle predicted before a dangerous foul stopped play is not counted')

    # ---- 16. measurement: a first tackle stays inside the possession ----
    m=c2m();s=m.s;m.e.emit('possession_change','test',previous=None,team='A',reason='control');one(m);m.e.release('A0',(20.0,0.0,0.0),'shot');m.e.goal('B',50,1);M=measure(m.e.log,SETTINGS);c=M['continuation']
    ok(M['measurement_version']=='M1.3' and M['per_team']['A']['possessions']==1 and M['possession_end_causes'].get('goal')==1 and 'tackle' not in M['possession_end_causes'],'a first tackle does not end the possession in the measurement layer')
    ok(M['contact']['completed_tackles']==1 and M['contact']['possessions_ended_by_tackle']==0 and c['tackles']['count_transitions']=={'0->1':1},'the tackle is counted once, as a count transition')
    ok(c['recovery']['outcomes']=={'picked_up':1} and c['recovery']['picked_up_by_tackled_carrier']==1 and c['recovery']['pickup_elapsed_s']['mean']==.9,'the recovery outcome and timing are measured')
    ok(c['tackles']['possessions_with_tackle_then_goal']==1 and 'tackle count transitions' not in M['unavailable_in_this_checkpoint'],'post-tackle scoring is measured')
    m=uncleared(('A3',(75.0,50.0)));c=measure(m.e.log,SETTINGS)['continuation']
    ok(c['inbound']['awarded']==1 and c['inbound']['outcomes']=={'released_to_teammate':1} and c['reconstruction']['clearance_witness']=={'secure_control':1},'inbound outcome and clearance witness are measured')
    off=CORE.match.Match(configuration({**SETTINGS,**C1_RULES,'archery':False},1,CALIBRATION));ok(not off.e.c2_any,'with the three C2 options off the engine runs the C1 rules')

    # ================= C2m2: correction batch after the Lead audit =================
    # ---- 17. a failed advantage gives back what the players actually had: exits are history, not current location ----
    def adv_case():
        """Advantage pending for A (count one). A3 has 4.1 s stored in the attacked zone. B1 stands ready to make the second tackle."""
        m=occ(B3=(90,50),B0=(51.3,50));s=m.s;s.possession_ms=40000;one(m);put(m,'B1',(s.players['A0'].x+1.3,50));put(m,'A3',(95,58));m.e.advance(4100)
        ok(s.advantage is not None and s.players['A3'].zone_ms[1]==4100 and s.tackle_count==1,'fixture: advantage pending, A3 has 4.1 s stored');return m
    def recall(m):
        s=m.s;k=len(m.e.log);m.e.advance(s.advantage['until']-s.now);ok('advantage_recalled' in ev(m,k) and s.owner=='A' and s.tackle_count==1,'fixture: the advantage is recalled')
    m=adv_case();s=m.s;A3=s.players['A3'];put(m,'A3',(100.5,58));m.e.advance(200);tk(m,'B1');ok(s.owner=='B' and A3.zone_ms[1]==0,'turnover inside the advantage clears the counts')
    put(m,'A3',(99,20));m.e.advance(200);ok(m.e.zone(99,20) is None and A3.zone_loc[1]=='out','he is back in the field, outside the arc');recall(m)
    ok(A3.zone_ms[1]==4100,'recall after an end-line exit: the stored time comes back; the invalid exit renewed nothing')
    m=adv_case();s=m.s;A3=s.players['A3'];tk(m,'B1');put(m,'A3',(100.5,58));m.e.advance(200);put(m,'A3',(99,20));m.e.advance(200);recall(m)
    ok(A3.zone_ms[1]==4100,'the same when the end-line exit comes after the turnover')
    m=adv_case();s=m.s;A3=s.players['A3'];put(m,'A3',(78,58));m.e.advance(200);ok(A3.zone_ms[1]==0,'a lawful arc exit before the turnover');put(m,'A3',(95,58));m.e.advance(300);tk(m,'B1');m.e.advance(200);recall(m)
    ok(A3.zone_ms[1]==300 and A3.unmarked_ms[1]==0,'recall: the witnessed lawful exit stands; only the time since his return comes back, not the 4.1 s')
    m=adv_case();s=m.s;A3=s.players['A3'];tk(m,'B1');put(m,'A3',(78,58));m.e.advance(200);put(m,'A3',(95,58));m.e.advance(200);recall(m)
    ok(A3.zone_ms[1]==0,'a lawful arc exit after the turnover also stands through the recall')
    m=adv_case();s=m.s;A3=s.players['A3'];tk(m,'B1');put(m,'A3',(100.5,58));m.e.advance(100);put(m,'A3',(95,58));m.e.advance(100);put(m,'A3',(78,58));m.e.advance(100);recall(m)
    ok(A3.zone_ms[1]==0,'end line out, back in, then out across the arc: the later lawful exit resets it')
    m=adv_case();s=m.s;A5=put(m,'A5',(75.0,-1.0));A5.zone_ms=[0,3500];A5.unmarked_ms=[600,0];n=put(m,'A12',(75.0,-.5));tk(m,'B1');ok(A5.zone_ms==[0,0],'cleared by the turnover')
    ok(m.e.sub('A5','A12') and n.zone_ms==[0,0],'substitution during the advantage, after the turnover');recall(m)
    ok(n.zone_ms==[0,3500] and n.unmarked_ms==[600,0] and s.players['A3'].zone_ms[1]==4100,'recall restores the slot inherited time to the replacement, not to the player who left')
    m=adv_case();s=m.s;A5=put(m,'A5',(75.0,-1.0));A5.zone_ms=[0,3500];n=put(m,'A12',(75.0,-.5));ok(m.e.sub('A5','A12'),'substitution during the advantage, before the turnover');tk(m,'B1');recall(m)
    ok(n.zone_ms==[0,3500],'and the same when the substitution came first')
    ok(s.possession_ms==max(20000,40000-900-4100) and s.game_ms>0 and last(m,'advantage_state_restored')['possession_changed_during_advantage'],'the foul-time clock and continuation state are restored as before')

    # C2m3: the advantaged team loses the ball and wins it back inside the advantage (A to B to A), then the advantage is recalled
    def lose_and_regain(m,exit_between=False):
        s=m.s;m.e.release('A0',(10.0,0.0,2.0),'pass','A1');ok(catch(m,'B4',(60,50)) and s.owner=='B' and s.players['A3'].zone_ms[1]==0 and s.advantage['c2']['keep']['A3'][0][1]==4100,'B secures the ball: counts cleared, 4.1 s kept with the advantage')
        if exit_between:put(m,'A3',(78,58));m.e.advance(100);put(m,'A3',(95,58))
        m.e.advance(100);m.e.release('B4',(-10.0,0.0,2.0),'pass');ok(catch(m,'A1',(48,50)) and s.owner=='A' and s.advantage is not None,'A secures it again without progress: the advantage is still pending');m.e.advance(300)
    m=adv_case();s=m.s;lose_and_regain(m);k=len(m.e.log);m.e.advance(s.advantage['until']-s.now)
    ok('advantage_recalled' in ev(m,k) and s.owner=='A' and s.players['A3'].zone_ms[1]==4100,'recall with the advantaged team back in possession: the stored 4.1 s is returned, not erased')
    d=last(m,'advantage_state_restored');ok(d['zone_counts_returned'] and not d['possession_changed_during_advantage'] and s.tackle_count==1,'returned because a clearing turnover happened, independent of who owns the ball at the recall')
    ok(s.possession_ms==max(20000,40000-900-4100),'the clock is the foul-time clock with its floor')
    m=adv_case();s=m.s;lose_and_regain(m,exit_between=True);m.e.advance(s.advantage['until']-s.now)
    ok(s.owner=='A' and s.players['A3'].zone_ms[1]==0,'the same sequence with a witnessed lawful arc exit after the first turnover: the reset stands')
    m=adv_case();s=m.s;lose_and_regain(m);put(m,'A3',(78,58));m.e.advance(100);put(m,'A3',(95,58));m.e.advance(s.advantage['until']-s.now)
    ok(s.players['A3'].zone_ms[1]==0,'and with the lawful exit after regaining the ball')
    m=adv_case();s=m.s;m.e.advance(500);z=s.players['A3'].zone_ms[1];m.e.recall_advantage();ok(z==4600 and s.players['A3'].zone_ms[1]==z and not last(m,'advantage_state_restored')['zone_counts_returned'],'no turnover inside the advantage: nothing was cleared, so nothing is returned or rewound')

    # C2m3: a substitution passes on a live freeze and the Keeper hold timer, with the C2 options on and off
    for label,rules in (('C2 on',{}),('C2 off',C1_RULES)):
        m=c2m(tackler=None,**rules);s=m.s;A5=put(m,'A5',(75.0,-1.0));A5.freeze_until=6000;n=put(m,'A12',(75.0,-.5))
        ok(s.now==1000 and m.e.sub('A5','A12') and n.freeze_until==6000 and n.frozen(s.now) and not m.e.eligible(n),label+': the replacement inherits the live freeze')
        m.e.advance(4999);ok(n.frozen(s.now),label+': still frozen just before the inherited deadline');m.e.advance(1);ok(not n.frozen(s.now) and s.now==6000,label+': free exactly at the inherited deadline')
        m=c2m(tackler=None,**rules);s=m.s;A5=put(m,'A5',(75.0,-1.0));A5.freeze_until=6000;n=put(m,'A12',(75.0,-.5));n.freeze_until=9000
        ok(m.e.sub('A5','A12') and n.freeze_until==9000,label+': a later deadline the incoming player already carries is not shortened')
        m=c2m(tackler=None,**rules);s=m.s;s.players['A10'].keeper_hold_ms=3200;m.e.award('A',50,50,'test');n=s.players['A12']
        ok(m.e.sub('A10','A12') and n.role=='keeper' and n.keeper_hold_ms==3200,label+': the Keeper hold timer passes to the replacement Keeper')

    # ---- 18. recovery grace follows unavoidable movement, not proximity ----
    def near_disc(gap,v=(0.0,0.0)):
        m=c2m();s=m.s;q=put(m,'B1',(s.ball.x,s.ball.y+1+s.players['B1'].radius+gap));q.vx,q.vy=v;tk(m);put(m,'B0',(58,50));return m
    m=near_disc(.5);s=m.s;ok('B1' not in s.recovery['committed'] and 'B0' in s.recovery['committed'],'a stationary defender half a metre clear of the disc gets no grace; the tackler does')
    put(m,'B1',(s.ball.x,s.ball.y+1.0));k=len(m.e.log);m.e.advance(1)
    ok(fouls(m,k)==['recovery_interference'] and last(m,'recovery_obstruction').get('entered_late') and last(m,'foul')['actor']=='B1','he then steps into the disc: avoidable entry, interference at once')
    m=near_disc(.2,(0.0,6.0));s=m.s;ok('B1' not in s.recovery['committed'],'a defender moving away from the disc gets no grace')
    put(m,'B1',(s.ball.x,s.ball.y+1.0));k=len(m.e.log);m.e.advance(1);ok(fouls(m,k)==['recovery_interference'],'and is interfering if he turns back into it')
    m=near_disc(.5,(0.0,-8.0));s=m.s;ok('B1' in s.recovery['committed'],'a defender whose response time and braking carry him in is committed')
    put(m,'B1',(s.ball.x,s.ball.y+1.0));k=len(m.e.log);m.e.advance(1);d=last(m,'recovery_obstruction')
    ok(not fouls(m,k) and d['player']=='B1' and not d.get('entered_late') and d['clear_by']>s.now,'his entry is not an offence; he gets the time physically needed to leave')
    m.e.advance(d['clear_by']-s.now+100);ok(fouls(m,k)==['recovery_interference'],'but staying beyond that time is')
    m=near_disc(3.0,(0.0,-1.0));ok('B1' not in m.s.recovery['committed'],'a slow approach from three metres can stop: no grace')
    m=near_disc(.5,(8.0,0.0));ok('B1' not in m.s.recovery['committed'],'fast movement past the disc, not towards it, earns no grace')
    m=c2m();s=m.s;put(m,'B1',(s.ball.x,s.ball.y+1.0));tk(m);put(m,'B0',(58,50));k=len(m.e.log);m.e.advance(1);ok('B1' in s.recovery['committed'] and not fouls(m,k),'a body already inside the disc at the tackle is unavoidable occupation')

    # ---- 19. every replacement path carries the slot state ----
    def state(q,z,u,f):q.zone_ms,q.unmarked_ms,q.zone_fouled=list(z),list(u),list(f)
    m=occ(A10=(90,60));s=m.s;A10=s.players['A10'];m.e.advance(1000);ok(A10.zone_ms[1]==1000,'a Keeper in the opposing zone has no exemption there')
    state(A10,[0,4200],[0,100],[0,7]);A10.active=False;m.e.award('A',50,50,'test');n=s.players['A12']
    ok(m.e.replace_unavailable_specialist('A10','A12') and (n.zone_ms,n.unmarked_ms,n.zone_fouled)==([0,4200],[0,100],[0,7]) and n.zone_loc==[None,None],'specialist replacement inherits count, unmarked allowance and pending violation')
    m.e.advance(1000);ok(n.zone_ms==[0,4200] and n.role=='keeper','and nothing is refreshed by the replacement')
    m=occ(A10=(90,60));s=m.s
    for q in s.players.values():
        if q.team=='A' and q.role=='field' and q.active:state(q,[0,1500],[0,0],[0,0])
    state(s.players['A10'],[0,4200],[0,100],[0,7]);m.e.discipline('A10','minor');q=next(q for q in s.players.values() if q.team=='A' and q.active and q.role=='keeper')
    ok(q.id!='A10' and (q.zone_ms,q.unmarked_ms,q.zone_fouled)==([0,4200],[0,100],[0,7]),'automatic promotion: the new Keeper takes the Keeper slot state')
    ok(m.e.vacated['A']==[([0,1500],[0,0],[0,0])],'and his own field slot state waits for its replacement')
    n=s.players['A13'];state(n,[9,9],[9,9],[9,9]);m.e.slot_fill(n);ok(n.zone_ms==[0,1500] and n.unmarked_ms==[0,0] and m.e.vacated['A']==[],'the player who fills that slot inherits it, not his own stale values')
    m=occ();s=m.s;state(s.players['B4'],[2000,0],[0,3000],[0,5]);m.e.discipline('B4','minor');ok(m.e.vacated['B']==[([2000,0],[0,3000],[0,5])],'an excluded field player leaves his slot state behind')
    n=s.players['B13'];m.e.slot_fill(n);ok((n.zone_ms,n.unmarked_ms,n.zone_fouled)==([2000,0],[0,3000],[0,5]),'and the player returning into that slot inherits it')
    state(s.players['B5'],[0,0],[0,2500],[0,0]);m.e.discipline('B5','minor');m.e.new_owner('B','control');ok(m.e.vacated=={'A':[],'B':[]},'a possession change clears waiting slot states with everything else')

    # ---- 20. readiness: no fixed wait in the C2 procedures (driven through the real match step) ----
    m=zone_tackle();s=m.s;put(m,'B0',(90,60));put(m,'A1',(100.4,42.0));t0=s.now;m.step()
    ok(s.restart.ready_at is not None and s.restart.ready_at-t0<=100 and s.restart.taker=='A1','inbound: taker, ball and clearance all available, so ready at the first step')
    m=zone_tackle();s=m.s;put(m,'B0',(90,60));put(m,'A1',(92.0,42.0));t0=s.now;m.step();ok(s.restart.ready_at is None,'inbound: the taker is not at the mark yet, so not ready')
    able=[]
    for i in range(60):
        if s.restart.ready_at is not None:break
        m.step();q=s.players[m.restart_taker];able.append(math.hypot(q.x-100.0,q.y-42.0)<=.5 and q.speed<1.5)
    ok(s.restart.ready_at==s.now and able[-1] and not any(able[:-1]) and s.now-t0>500,'ready in the very step he has arrived and stopped: real movement time, no added wait')
    m=zone_tackle();s=m.s;put(m,'A1',(100.4,42.0));put(m,'B0',(98.0,42.0));t0=s.now;m.step();ok(s.restart.ready_at is None,'inbound: a defender inside three metres, so not ready')
    for i in range(60):
        if s.restart.ready_at is not None:break
        m.step()
    ok(s.restart.ready_at is not None and math.hypot(s.players["B0"].x-100.0,s.players["B0"].y-42.0)>=3.0-1e-6,'ready once he has actually cleared the three metres')
    m=c2m();s=m.s;tk(m);put(m,'B0',(58,50));m.e.restore_recovery('test');ok(s.phase==DEAD and s.restart.kind=='recovery','fixture: restored recovery, disc clear');t0=s.now;m.step()
    ok(s.phase==AWARD and s.recovery['replacement'] and s.recovery['started']-t0<=100,'restored recovery resumes at the first step when the disc is clear')
    m=c2m();s=m.s;tk(m);m.e.restore_recovery('test');B0=s.players['B0'];B0.freeze_until=s.now+2000;m.step();ok(s.phase==DEAD,'restored recovery does not resume while an opponent is still in the disc')
    for i in range(60):
        if s.phase!=DEAD:break
        m.step()
    ok(s.phase==AWARD and not any(math.hypot(q.x-s.recovery["spot"][0],q.y-s.recovery["spot"][1])<1+q.radius for q in s.players.values() if q.team=='B' and q.active and q.role!='archer'),'and resumes once he has left it')
    m=c2m();s=m.s;m.e.award('A',50,50,'test');put(m,'A1',(50,50));t0=s.now
    for i in range(14):m.step()
    ok(s.restart is not None and s.restart.ready_at is None,'an ordinary free pass keeps the Pocket 1.1 minimum before ready');m.step();m.step();ok(s.restart is None or s.restart.ready_at is not None,'and is ready after it')

    # ---- 21. reporting ----
    R=lambda events:{'score':{'A':1,'B':2},'goal_counts':{},'ordinary_completion':True,'live_s':10.0,'active_fraction':.5,'events':events}
    ok(aggregate([R({'tackle_count':5,'tackle_award':2}),R({'tackle_count':1})])['total_tackles']==6,'match totals count completed tackles once, from the count transitions')
    ok(aggregate([R({'tackle_award':3}),R({})])['total_tackles']==3,'and fall back to the old event on a log without them')
    def faulted_release(m,pid,defender,d):
        s=m.s;r=s.restart;put(m,defender,(r.x-d if r.x>50 else r.x+d,r.y));return m.e.restart_release(pid,(-15.0 if r.x>50 else 15.0,0.0,3.0),'A2')
    m=zone_tackle();s=m.s;put(m,'B0',(90,60));put(m,'A1',(100.4,42.0))
    for i in range(2):m.e.ready('A1');ok(not faulted_release(m,'A1','B5',2.0) and s.restart.kind=='inbound','inbound defensive fault %d: retake'%(i+1));put(m,'B5',(70,55))
    m.e.ready('A1');ok(m.e.restart_release('A1',(-15.0,0.0,3.0),'A2') and catch(m,'A3',(75.0,50.0)),'the inbound is finally released and caught')
    m.e.foul('B3','A3','late_hold');r=s.restart;put(m,'A4',(r.x,r.y));m.e.ready('A4');ok(not faulted_release(m,'A4','B6',4.0) and s.restart.reason=='defensive_restart_fault' and s.restart.kind=='free_pass','an ordinary free-pass defensive fault')
    c=measure(m.e.log,SETTINGS)['continuation']['inbound']
    ok((c['awarded'],c['retakes_after_defensive_fault'],c['inbounds_retaken'],c['inbounds_retaken_more_than_once'])==(1,2,1,1),'inbound retakes are counted inside their inbound; the ordinary free-pass fault is not')
    ok(c['outcomes']=={'released_to_teammate':1},'and the retaken inbound still has one outcome')

    # ================= C3a: contact kernel =================
    # The real Match motion, kernel and event processing, with scripted targets and everyone else parked. No policy decisions.
    Ev=Ty.Event
    def kb(cal=None,strips=False,**over):
        m=CORE.match.Match(configuration({**SETTINGS,'archery':False,'zone_marking':False,'zone_inbound':False,**over},1,{**C3CAL,**(cal or {})}));s=m.s
        s.phase=LIVE;s.now=1000;s.owner='A';s.opening_team='A';s.alternate='B';s.opening_deadline=None;s.opening_touched=True
        for q in s.players.values():
            if q.active and q.role=='field':kput(m,q.id,(26.0 if q.team=='A' else 74.0,1.0+2.0*int(q.id[1:])))   # parked well clear of the lane at y = 50
        m.c3_no_strip=not strips;return m
    def kput(m,pid,xy,v=(0.0,0.0)):
        q=m.s.players[pid];q.x,q.y=float(xy[0]),float(xy[1]);q.vx,q.vy=float(v[0]),float(v[1]);q.target=(q.x,q.y);q.posture='upright'
        if q.speed>.3:q.facing=CORE.geometry.unit(q.vx,q.vy)
        return q
    def ktop(m,pid,v,carrier=False):
        q=m.s.players[pid];q.fatigue=1.0;q.a.maximum_speed=v/(m.pol[q.team].t.pace*.9) if carrier else v/.88
    def kgive(m,pid):
        s=m.s;s.ball=Ty.Ball(mode=Ty.BallMode.CONTROLLED,carrier=pid,control_time=s.now-500,last_touch=pid[0],scoring=True);m.e.follow_carrier()
    def ktick(m,targets,ms=100):
        """ms of the NORMAL C3 path (Match.c3_step) with scripted targets. An interval ends at its first event, so this may be several."""
        s=m.s;end=s.now+ms;guard=0
        while s.now<end and guard<400:
            guard+=1
            for pid in targets:s.players[pid].next_decision=0
            full={q.id:(q.x,q.y) for q in m.active_field()};full.update(targets);m.c3_step(end-s.now,full,scripted=True)
            if s.ball.carrier:m.e.follow_carrier()
    def krun(m,ids,ms=10,carrier=None):
        """The kernel's own integrator (c3_run) on the named athletes, coasting: no step wrapper, no ball. Returns the kernel's queued events."""
        ps=[m.s.players[i] for i in ids];sc=m.assume['body_radius_scale']
        pairs=[(a,b,(a.radius+b.radius)*sc) for i,a in enumerate(ps) for b in ps[i+1:] if a.team!=b.team]
        m.c3_cache={q.id:(max(q.speed,.1),99.0,[]) for q in ps};m.c3_events=[];m.c3_down=set();m.c3_lost=False
        for q in ps:q.target=(q.x+q.vx*100,q.y+q.vy*100)
        m.c3_integrating=True;m.c3_run(ms,pairs,ps,m.s.players[carrier] if carrier else None,True);m.c3_integrating=False;m.c3_t=0.
        return m.c3_events
    def knotes(evs,name):return [e.data['data'] for e in evs if e.kind=='note' and e.data['event']==name]
    def load(q,sources,now):
        """Set an athlete's balance contributions: {(kind, other): (amount, lawful)}."""
        q.bal_src={(k[0],k[1],bool(v[1])):float(v[0]) for k,v in sources.items()};q.bal_t0=now
    def karrow(m,team,target,hit_in_ms,speed=60.0):
        """A real arrow in flight that reaches the target athlete's body hit_in_ms from now."""
        s=m.s;q=s.players[target];T=hit_in_ms/1000;hx,hy=q.x+q.vx*T,q.y+q.vy*T;z=q.z+.5*q.a.height
        s.arrows.append(Ty.Arrow(id=900+len(s.arrows),team=team,shooter=team+'11',target=target,x=hx-speed*T,y=hy,z=z+.5*9.81*T*T,vx=speed,vy=0.0,vz=0.0,origin=(hx-30.0,hy,z),release_time=s.now-400))
    def pursuit(v=8.0,n=1,g=None,cal=None,region=None,carrier='A0',at=(30,50)):
        """Carrier runs at v with n defenders alongside, matched in speed and within reach. g: set an established grip."""
        m=kb(cal);A=kput(m,carrier,at,(v,0));ktop(m,carrier,max(v,.1),True);kgive(m,carrier);m.c3_fix_region=region
        for i,d in enumerate(['B0','B1'][:n]):kput(m,d,(at[0]-1.1,at[1]+(1.0 if i==0 else -1.0)),(v,0));ktop(m,d,max(v,.1))
        if g is not None:
            ktick(m,{carrier:(99,at[1])},10)
            for d in ['B0','B1'][:n]:m.c3_holds[(d,carrier)]['g']=g
        return m
    def chase(m,carrier='A0',n=1):
        c=m.s.players[carrier];return {carrier:(99,c.y),**{d:(c.x,c.y) for d in ['B0','B1'][:n]}}
    def run(m,ticks,carrier='A0',n=1,stop=True):
        for i in range(ticks):
            ktick(m,chase(m,carrier,n))
            if stop and m.s.ball.carrier!=carrier:break
    def kin(m,ids):return sum(.5*m.s.players[i].a.mass*m.s.players[i].speed**2 for i in ids)
    def px(m,ids):return sum(m.s.players[i].a.mass*m.s.players[i].vx for i in ids)
    def near(a,b,tol=1e-6):return abs(a-b)<=tol*max(1.0,abs(a),abs(b))
    def count(m,name,k=0,**match):return sum(r['event']==name and all(r['data'].get(a)==b for a,b in match.items()) for r in m.e.log[k:])

    # ---- 1. collision: one equal and opposite impulse; bracing is an external ground impulse, accounted separately ----
    def crash(va,vb,ma=230,mb=230,cal=None):
        m=kb({'collision_risk_tolerance':99.0,**(cal or {})});m.c3_reckless={'A0','B0'};A=kput(m,'A0',(48,50),(va,0));B=kput(m,'B0',(52,50),(vb,0));A.a.mass=ma;B.a.mass=mb
        ktop(m,'A0',max(abs(va),.1));ktop(m,'B0',max(abs(vb),.1));m.s.ball=Ty.Ball(mode=Ty.BallMode.LOOSE,x=5.0,y=5.0,z=.1075,last_touch='A')
        return m
    for ma,mb in ((230,230),(165,350)):
        m=crash(6.0,-6.0,ma,mb);A,B=m.s.players['A0'],m.s.players['B0'];hit=None;gap=4.0-(A.radius+B.radius)
        for i in range(60):
            p0=px(m,('A0','B0'));va,vb=A.vx,B.vx;hit=(knotes(krun(m,('A0','B0'),5),'c3_collision') or [None])[0]
            if hit:break
        t_hit=1000*gap/12.0;ok(hit is not None and abs(hit['t_ms']-m.s.now-(t_hit-5*i))<2e-3 and 0<t_hit-5*i<5,'collision: it happens at the solved instant of body contact, inside the substep, not at a substep boundary')
        J=hit['impulse_Ns'];ok(near(ma*hit['dv_a'],J,1e-3) and near(mb*hit['dv_b'],J,1e-3) and near(J,1.1*12/(1/ma+1/mb),1e-3),'collision: the pair impulse is equal and opposite, J = (1+e) x closing speed / (1/mA + 1/mB) (masses %d and %d)'%(ma,mb))
        ok(hit['ground_impulse_a']==0 and hit['ground_impulse_b']==0 and near(hit['shock_a'],hit['dv_a']/(6.0*(.5+A.a.balance)),1e-3),'no bracing at speed; shock is the own velocity change over the shock speed')
    m=crash(6.0,0.0);A,B=m.s.players['A0'],m.s.players['B0'];B.facing=(-1.0,0.0);k=len(m.e.log)
    for i in range(12):
        ktick(m,{'A0':(99,50)})
        if count(m,'c3_collision',k):break
    d=last(m,'c3_collision');cap=.8*230*9.81*.15
    ok(near(d['ground_impulse_b'],cap,1e-3) and d['ground_impulse_a']==0 and d['dv_b']<d['dv_a'],'a set athlete facing the contact braces: a ground impulse bounded by traction, logged apart from the pair impulse')
    ok(near(230*d['dv_a'],d['impulse_Ns'],2e-3) and near(230*d['dv_b'],d['impulse_Ns']-d['ground_impulse_b'],2e-3),'full momentum budget: pair impulse on each body, less the external ground impulse on the braced one')
    for eps,expect_dv in ((0.0,6.0),(0.1,6.6),(0.3,7.8)):
        m=crash(6.0,-6.0,cal={'contact_restitution':eps});k=len(m.e.log)
        for i in range(10):ktick(m,{'A0':(99,50),'B0':(1,50)})
        ok(near(last(m,'c3_collision')['dv_a'],expect_dv,2e-2),'restitution %.1f: own velocity change is (1+e) x half the closing speed for equal masses'%eps)

    # ---- 2. zero shock at zero velocity change; passive contact grounds nobody; a deliberate drive can ----
    m=crash(0.0,0.0);kput(m,'A0',(50,50));kput(m,'B0',(50.85,50));k=len(m.e.log)
    for i in range(20):ktick(m,{})
    ok(count(m,'c3_collision',k)==0 and m.c3_bal(m.s.players['A0'])==0 and m.c3_bal(m.s.players['B0'])==0 and not count(m,'c3_grounding',k),'stationary contact: no shock, no balance load, nobody grounded')
    m=pursuit(0.0,g=.8);m.c3_fix_drive=-1.0;k=len(m.e.log)
    for i in range(20):ktick(m,{})
    ok(m.c3_bal(m.s.players['A0'])<.02 and not count(m,'c3_grounding',k) and ('B0','A0') in m.c3_holds,'a passive established hold on a stationary carrier transmits no force and grounds nobody')
    m=pursuit(0.0,g=.8,region='upper');m.c3_fix_drive=-1.0;k=len(m.e.log);A,B=m.s.players['A0'],m.s.players['B0']
    for i in range(40):
        ux,uy=CORE.geometry.unit(A.x-B.x,A.y-B.y);B.vx,B.vy=4.0*ux,4.0*uy;ktick(m,{})   # the holder keeps driving into him
        if m.s.ball.carrier!='A0':break
    ok(count(m,'c3_grounding',k,cls='tackle_under_hold')==1 and count(m,'tackle_count',k)==1,'a deliberate lawful drive against a stationary carrier does ground him, and it is a counted tackle')

    # ---- 3. shock re-arms only after real separation ----
    m=crash(5.0,-5.0);k=len(m.e.log)
    for i in range(25):ktick(m,{'A0':(99,50),'B0':(1,50)})
    ok(count(m,'c3_collision',k)==1 and abs(m.s.players['A0'].x-m.s.players['B0'].x)>=.899,'two bodies pushing on each other: one shock, then momentum exchange without fresh shock, and no overlap')
    A,B=m.s.players['A0'],m.s.players['B0'];kput(m,'A0',(A.x-3,50),(5,0));kput(m,'B0',(B.x+3,50),(-5,0))
    for i in range(12):ktick(m,{'A0':(99,50),'B0':(1,50)})
    ok(count(m,'c3_collision',k)==2,'after separating beyond the re-arm gap a new collision gives a new shock')

    # ---- 4. grip: zero before reach, none out of reach, lost to slip and to overload ----
    m=pursuit(8.0);kput(m,'B0',(25.0,50.0),(8,0));ktick(m,{'A0':(99,50),'B0':(26,50)})
    ok(not m.c3_holds and not any(k[2]=='tackle' for k in m.s.engagements),'out of reach: no hold and no grip')
    m=pursuit(8.0);ktick(m,chase(m),10);h=m.c3_holds[('B0','A0')];g1=h['g'];ok(0<g1<.06,'grip starts at zero and builds only with time in reach');run(m,3);g4=h['g'];ok(g4>.5,'matched in reach: grip builds')
    m.c3_fix_drive=-1.0;B=m.s.players['B0'];B.vy=12.0;ktick(m,{'A0':(99,50)},10);ok(h['g']<g4 and h['slip']>10,'tangential slip takes grip away')
    def one_substep(excess):
        m=pursuit(8.0,g=.6);m.c3_fix_drive=-1.0;h=m.c3_holds[('B0','A0')];h['excess']=excess;A,B=m.s.players['A0'],m.s.players['B0'];B.vx,B.vy=A.vx,A.vy
        krun(m,('A0','B0'),10,'A0');return h['g']
    ok(one_substep(2.0)<one_substep(0.0)<.61,'load excess takes grip away')
    m=pursuit(8.0,g=.6);m.s.players['B0'].freeze_until=m.s.now+3000;k=len(m.e.log);ktick(m,{'A0':(99,50)});ktick(m,{'A0':(99,50)})
    ok(not m.c3_holds and last(m,'c3_hold_end')['cause']=='ineligible' and not fouls(m,k),'a frozen holder has no hold: grip needs lawful contact throughout')

    # ---- 5. several holds on one carrier are solved together: the order they are listed in does not matter ----
    def two(order):
        m=pursuit(8.0,n=2,g=.5);A,B0,B1=(m.s.players[i] for i in ('A0','B0','B1'));B0.vx=6.0;B1.vx=7.0;B1.a.strength=.9
        items=list(m.c3_holds.items());m.c3_holds=dict(items if order else items[::-1]);m.c3_fix_drive=-1.0
        for i in range(30):krun(m,('A0','B0','B1') if order else ('B1','B0','A0'),10,'A0')
        return [round(v,12) for q in (A,B0,B1) for v in (q.vx,q.vy,m.c3_bal(q))]+[round(m.c3_holds[(d,'A0')]['g'],12) for d in ('B0','B1') if (d,'A0') in m.c3_holds]
    ok(two(True)==two(False),'two holds on one carrier give the same velocities, balance loads and grips whichever is processed first')
    m=pursuit(8.0,n=2,g=.5);m.c3_fix_drive=-1.0;A,B0,B1=(m.s.players[i] for i in ('A0','B0','B1'));B0.vx=5.0;B1.vx=6.0;e0=kin(m,('A0','B0','B1'));p0=px(m,('A0','B0','B1'))
    krun(m,('A0','B0','B1'),10,'A0')
    ok(kin(m,('A0','B0','B1'))<=e0+1e-9 and near(px(m,('A0','B0','B1')),p0,1e-9),'coupling through holds conserves momentum and never adds kinetic energy')

    # ---- 6. physical grounding and counted tackle are separate questions ----
    def grounded_with(g,sources,reach=True,n=1,idle=()):
        """Carrier loaded to the point of falling by the given sources, with a defender holding at grip g (or just out of reach).
        Grip gain and loss are switched off in this fixture so that the grip stays at the stated value."""
        m=pursuit(8.0,n=n,g=g if g else .01);m.c3_fix_drive=-1.0;m.assume['grip_gain_per_s']=0.0;m.assume['grip_resist_per_s']=0.0;A=m.s.players['A0'];load(A,sources,m.s.now)
        if not g:m.c3_holds[('B0','A0')]['g']=0.0
        if not reach:kput(m,'B0',(A.x-4.0,50.0),(8,0))
        for d in idle:m.c3_holds[(d,'A0')]['g']=0.0
        k=len(m.e.log);ktick(m,{'A0':(99,50)});return m,k
    OLD={('shock','B5'):[1.05,True]}
    m,k=grounded_with(.31,OLD);d=last(m,'c3_grounding')
    ok(d['cls']=='tackle_under_hold' and d['credited']=='B0' and count(m,'tackle_count',k)==1 and m.s.tackle_count==1,'grounded under a current lawful hold above the threshold: a counted tackle, whoever loaded his balance')
    m,k=grounded_with(.29,OLD);d=last(m,'c3_grounding')
    ok(d['cls']=='carrier_grounded_not_a_tackle' and not count(m,'tackle_count',k) and m.s.ball.carrier is None and last(m,'release')['forced'],'the same just below the threshold, loaded by an old shock from someone no longer in contact: not a tackle, the existing forced release')
    m,k=grounded_with(.29,{('shock','B5'):[.4,True],('hold','B0'):[.65,True]});d=last(m,'c3_grounding')
    ok(d['cls']=='tackle_by_lawful_contact' and d['credited']=='B0' and d['lawful_defensive_share']>=.5,'below the threshold, but the holder in current lawful contact supplied the majority of the load: a counted tackle')
    m,k=grounded_with(.29,{('self',None):[.7,False],('hold','B0'):[.35,True]});ok(last(m,'c3_grounding')['cls']=='carrier_grounded_not_a_tackle','a brush that supplied a minority of the load does not make a tackle')
    m,k=grounded_with(.6,OLD,reach=False,n=2,idle=('B1',));d=last(m,'c3_grounding')
    ok(d['cls']=='carrier_grounded_not_a_tackle' and [h['player'] for h in d['holders']]==['B1'] and d['holders'][0]['grip']<.01 and not count(m,'tackle_count',k),'a stale grip is not an engagement: the holder who has fallen out of reach cannot make a tackle, and the one alongside without a grip does not either')
    m,k=grounded_with(.29,{('shock','A5'):[1.05,True]});ok(last(m,'c3_grounding')['cls']=='carrier_grounded_not_a_tackle','load from a team-mate is not a defensive cause')
    m,k=grounded_with(.29,{('shock','B5'):[1.05,False]});ok(last(m,'c3_grounding')['cls']=='carrier_grounded_not_a_tackle','load from unlawful contact is not a lawful defensive cause')
    m=pursuit(8.0);A=m.s.players['A0'];kput(m,'B0',(10,10));load(A,{('shock','B5'):[.9,True]},m.s.now)
    for i in range(20):ktick(m,{'A0':(99,50)})
    ok(m.c3_bal(A)<.05 and m.s.ball.carrier=='A0','unrelated shock decays away with recovery; it cannot be banked for a later tackle')
    m=pursuit(8.0,g=.2);k=len(m.e.log);m.e.grounded('A0');ok(not count(m,'tackle_count',k) and last(m,'release')['forced'] and m.s.tackle_count==0,'voluntary grounding next to a weak hold is the existing forced release, never a tackle')
    m,k=grounded_with(.6,OLD,n=2);m2=m
    ok(count(m,'tackle_count',k)==1 and count(m,'c3_grounding',k)==1 and len(last(m,'c3_grounding')['holders'])==2,'two holders, one physical grounding, one count')
    m=pursuit(4.0,n=2,g=.6,carrier='A10',at=(8,50));A=m.s.players['A10'];load(A,{('shock','B5'):[1.05,True]},m.s.now);k=len(m.e.log);ktick(m,{'A10':(30,50)})
    ok(count(m,'tackle_count',k)==1 and last(m,'tackle_count')['where']=='own_zone' and last(m,'tackle_count')['carrier']=='A10','a Keeper carrying in his own zone, two holders: one count')
    m=crash(13.0,-13.0);k=len(m.e.log)
    for i in range(8):ktick(m,{'A0':(99,50),'B0':(1,50)})
    ok(count(m,'c3_grounding',k,cls='non_carrier_grounded')==2 and not count(m,'tackle_count',k) and m.s.players['B0'].posture=='grounded','any athlete can be grounded; without a carrier in control nobody is credited with a tackle')
    m=kb({'collision_risk_tolerance':99.0});m.c3_reckless={'A0','B0'};A=kput(m,'A0',(48,50),(13,0));B=kput(m,'B0',(52,50),(-13,0));ktop(m,'A0',13,True);ktop(m,'B0',13);kgive(m,'A0');k=len(m.e.log)
    for i in range(8):ktick(m,{'A0':(99,50),'B0':(1,50)})
    ok(last(m,'tackle_count')['tackler']=='B0' and count(m,'c3_grounding',k,cls='tackle_by_lawful_contact')==1 and B.posture=='grounded' and count(m,'tackle_count',k)==1,'a lawful hit that grounds the carrier is a tackle; the tackler who goes down with him is not credited twice and gets nothing for falling')

    # ---- 7. timing: release and grounding in actual order; no tie window ----
    m=pursuit(8.0,g=.6);m.c3_fix_drive=-1.0;s=m.s;A=s.players['A0'];kput(m,'A1',(34,56),(8,0));ktop(m,'A1',8)
    m.pending_ball_actions['A0']=(s.now,'pass','A1');m.c3_prep['A0']=s.now-300;load(A,{('shock','B5'):[1.05,True]},s.now);k=len(m.e.log);ktick(m,{'A0':(99,50),'A1':(99,56)})
    ok(count(m,'release',k)==1 and not last(m,'release')['forced'] and not count(m,'tackle_count',k) and s.tackle_count==0,'a release that completes at this instant stands, although the carrier would have been grounded a few milliseconds later')
    ok(last(m,'c3_grounding')['cls']=='non_carrier_grounded' and not m.c3_holds and last(m,'c3_hold_end')['cause']=='control_lost','and the hold ended with control: his fall is physical, not a tackle')
    m=pursuit(8.0,g=.6);m.c3_fix_drive=-1.0;s=m.s;A=s.players['A0'];kput(m,'A1',(34,56),(8,0));ktop(m,'A1',8)
    m.pending_ball_actions['A0']=(s.now+100,'pass','A1');m.c3_prep['A0']=s.now-200;load(A,{('shock','B5'):[1.05,True]},s.now);k=len(m.e.log);t_s=s.now;ktick(m,{'A0':(99,50),'A1':(99,56)});ktick(m,{'A1':(99,56)});m.carrier_decision()
    ok(count(m,'tackle_count',k)==1 and not any(r['event']=='release' and not r['data']['forced'] for r in m.e.log[k:]) and 'A0' not in m.pending_ball_actions,'a release that would complete after the grounding does not happen; its preparation is cancelled')
    t_g=next(r['t_ms'] for r in m.e.log[k:] if r['event']=='c3_grounding');ok(t_g<=t_s+1,'the grounding is committed at its own time (within the one-millisecond clock), and the interval ended there')
    m=pursuit(8.0,g=.6);s=m.s;w=s.ball.version;m.e.elapse(50,resolve=False);m.s.players['A0'].posture='upright';k=len(m.e.log)
    m.e.batch([Ev('tackle','B0','A0',{'control_witness':w,'c3':{'player':'A0','cls':'tackle_under_hold'}}),Ev('freeze',None,'A0',{})])
    ok('freeze' in ev(m,k) and not count(m,'tackle_count',k) and not count(m,'c3_grounding',k),'freeze and grounding at one millisecond: the freeze governs and no tackle is counted')
    m=pursuit(8.0,g=.6);s=m.s;w=s.ball.version;k=len(m.e.log);m.process_events([Ev('freeze',None,'A0',{},at=30),Ev('tackle','B0','A0',{'control_witness':w,'c3':{'player':'A0','cls':'tackle_under_hold'}},at=31)],s.now,100)
    ok('freeze' in ev(m,k) and not count(m,'tackle_count',k),'a freeze one millisecond before the grounding wins on time alone')
    m=pursuit(8.0,g=.6);s=m.s;w=s.ball.version;k=len(m.e.log);m.process_events([Ev('tackle','B0','A0',{'control_witness':w,'c3':{'player':'A0','cls':'tackle_under_hold'}},at=30),Ev('freeze',None,'A0',{},at=31)],s.now,100)
    ok(count(m,'tackle_count',k)==1 and 'freeze' not in ev(m,k),'a grounding one millisecond before the freeze is a tackle; the later arrow finds no carrier')
    def kernel_tackle(m,at):return Ev('tackle','B0',m.s.ball.carrier,{'control_witness':m.s.ball.version,'c3':{'player':m.s.ball.carrier,'cls':'tackle_under_hold'}},at=at)
    m=pursuit(8.0,g=.6);s=m.s;s.possession_ms=100;k=len(m.e.log);m.process_events([kernel_tackle(m,100)],s.now,100)
    ok(count(m,'tackle_count',k)==1 and s.owner=='B' and s.restart.reason=='possession_expiry','first kernel tackle and clock expiry at one instant: counted, and the expiry still stands')
    m=pursuit(8.0,g=.6);s=m.s;s.tackle_count=1;s.possession_ms=100;k=len(m.e.log);m.process_events([kernel_tackle(m,100)],s.now,100)
    ok(last(m,'tackle_count')['procedure']=='turnover' and s.owner=='B' and s.phase==AWARD and s.possession_ms==45000,'second kernel tackle and clock expiry at one instant: the tackle award stands with its fresh clock')
    m=pursuit(8.0,g=.6);s=m.s;s.tackle_count=1;s.possession_ms=60;k=len(m.e.log);tkl=kernel_tackle(m,0);m.e.advance(60)
    m.e.batch([Ev('tackle','B0','A0',dict(tkl.data))])
    ok(s.restart.reason=='possession_expiry' and not count(m,'tackle_count',k),'a kernel tackle that arrives after the expiry cannot revive the possession')
    m=pursuit(8.0,g=.6);s=m.s;s.tackle_count=1;s.game_ms=100;per=s.period;k=len(m.e.log);m.process_events([kernel_tackle(m,100)],s.now,100)
    ok(count(m,'tackle_count',k)==1 and 'period_end' in ev(m,k) and s.period==per+1,'second kernel tackle at the horn: the period ends')
    m=pursuit(8.0,g=.6);s=m.s;A=s.players['A0'];w=s.ball.version;m.e.release('A0',(30.0,0.0,2.0),'shot');k=len(m.e.log)
    m.process_events([Ev('tackle','B0','A0',{'control_witness':w,'c3':{'player':'A0','cls':'tackle_under_hold'}},at=20),Ev('goal',None,None,{'defending':'B','y':50.0,'z':1.0},at=40)],s.now,100)
    ok(count(m,'goal',k)==1 and not count(m,'tackle_count',k) and s.score['A']>0,'a grounding after the release is not a tackle and does not touch the goal that follows')

    # ---- 8. restraint on an action in preparation ----
    def passing(region=None,g=None,kind='pass',cal=None,calm=False):
        m=pursuit(8.0,g=g,region=region,cal=cal) if not calm else pursuit(8.0,cal=cal);s=m.s;A=s.players['A0'];R=kput(m,'A1',(34,56),(8,0));ktop(m,'A1',8);m.c3_fix_drive=-1.0
        if calm:kput(m,'B0',(10,10))
        m.make_pass(A,R,kind);return m
    def play(m,ticks=40):
        k=len(m.e.log)
        for i in range(ticks):
            ktick(m,{'A0':(99,50),'A1':(99,56),**({'B0':(m.s.players['A0'].x,50)} if ('B0','A0') in m.c3_holds else {})})
            if m.s.ball.carrier!='A0':break
        return k
    base=passing(calm=True);t0=base.s.now;due0=base.pending_ball_actions['A0'][0];k=play(base);rel0=next(r for r in base.e.log[k:] if r['event']=='release')
    ok(rel0['t_ms']==due0 and not count(base,'c3_restraint',k),'unrestrained: released when the preparation falls due, nothing added')
    off=CORE.match.Match(configuration({**SETTINGS,'archery':False,'zone_marking':False,'zone_inbound':False},1,LEGACY));ok(not off.c3 and off.e.c3 is False,'replay path: kernel off')
    up_=passing('upper',.5);k=play(up_);r1=next(r for r in up_.e.log[k:] if r['event']=='release');rs=last(up_,'c3_restraint')
    ok(r1['t_ms']>due0 and up_.stats['c3_preparation_delay_ms']>0,'an upper hold slows a pass in preparation: it is released later than it would have been')
    v=math.sqrt(sum(c*c for c in r1['data']['velocity']));ok(near(v,rs['speed_available_mps'],1e-4) and rs['speed_available_mps']<rs['speed_unrestrained_mps'] and near(rs['speed_available_mps'],rs['speed_unrestrained_mps']*(1-.5*rs['restraint']),1e-3),'launch speed is what the restraint leaves, and the pass is planned and thrown at that speed')
    ok(near(rs['added_error_deg'],8.0*rs['restraint'],1e-3) and rs['restraint']>.3,'launch error is added in proportion to the restraint, sampled at release')
    lo=passing('lower',.5);k=play(lo);rl=last(lo,'c3_restraint');ok(0<rl['restraint']<rs['restraint']/2 and next(r for r in lo.e.log[k:] if r['event']=='release')['t_ms']<r1['t_ms'],'a lower hold bears much less on a hand release')
    kk=passing('lower',.5,kind='kick');k=play(kk);ok(last(kk,'c3_restraint')['restraint']>rl['restraint']*2,'and bears fully on a kick')
    part=passing(calm=True);s=part.s;ktick(part,{'A0':(99,50),'A1':(99,56)});ktick(part,{'A0':(99,50),'A1':(99,56)});ok('A0' in part.pending_ball_actions,'preparation is under way before any contact')
    A=s.players['A0'];part.c3_fix_region='upper';kput(part,'B0',(A.x-1.1,51.0),(8,0));ktop(part,'B0',8);k=play(part)
    ok(next(r for r in part.e.log[k:] if r['event']=='release')['t_ms']>=due0+0 and count(part,'c3_restraint',k)==1,'contact arriving part-way through the preparation restrains only what is left')
    esc=passing('upper',.5);s=esc.s;ktick(esc,{'A0':(99,50),'A1':(99,56),'B0':(s.players['A0'].x,50)});delayed=esc.pending_ball_actions['A0'][0];kput(esc,'B0',(10,10));k=play(esc)
    re_=next(r for r in esc.e.log[k:] if r['event']=='release');ve=math.sqrt(sum(c*c for c in re_['data']['velocity']))
    ok(delayed>due0 and delayed<=re_['t_ms']<delayed+100 and not count(esc,'c3_restraint',k) and near(ve,rs['speed_unrestrained_mps'],1e-6),'escape before completion: the time already lost stays lost, but the release itself is at full speed with no added error')
    fresh=passing(calm=True);s=fresh.s;A=s.players['A0'];fresh.e.release('A0',(0.0,0.0,0.0),'loose',forced=True);s.ball.x,s.ball.y,s.ball.z=A.x+.3,A.y,1.0;s.now+=10;ok(fresh.e.acquire('A0'),'he loses the ball and picks it up again');fresh.carrier_decision()
    ok('A0' not in fresh.pending_ball_actions,'preparation begun before the loss is not completed after the fresh pickup')

    # ---- 9. wrap entitlement, grip, coupling and drive end the instant control is lost ----
    m=pursuit(8.0,g=.8);s=m.s;A,B=s.players['A0'],s.players['B0'];run(m,2);ok(m.c3_holds[('B0','A0')]['force']>500 and B.speed<A.speed+.5,'fixture: an established strong hold, transmitting force')
    va,vb=(A.vx,A.vy),(B.vx,B.vy);k=len(m.e.log);m.e.release('A0',(20.0,5.0,3.0),'pass')
    t_rel=s.now;m.c3_reconcile();m.c3_sync()
    ok(not m.c3_holds and ('B0','A0','tackle') not in s.engagements and (A.vx,A.vy)==va and (B.vx,B.vy)==vb,'control lost: the hold, its grip and its coupling end at once, and the momentum each already had is untouched')
    ok(last(m,'c3_hold_end')['cause']=='control_lost' and last(m,'c3_hold_end')['grip_at_end']>.5 and last(m,'c3_hold_end')['end_ms']==t_rel,'the end of the hold is logged with its cause, at the time of the release')
    for i in range(5):ktick(m,{'A0':(99,50),'B0':(A.x,A.y)})
    ok(not m.c3_holds and not fouls(m,k) and not count(m,'c3_hold_start',k),'bodies still side by side do not make a new hold on a player without the ball, and momentum alone is no late hold')
    s.ball.x,s.ball.y,s.ball.z=A.x+.3,A.y,1.0;s.ball.vx=s.ball.vy=s.ball.vz=0.0;s.ball.last_releaser=None;ok(m.e.acquire('A0'),'a fresh pickup');kput(m,'B0',(A.x-1.1,A.y+1.0),(A.vx,A.vy));ktick(m,{'A0':(99,50),'B0':(A.x,A.y)},10)
    ok(m.c3_holds[('B0','A0')]['g']<.06 and count(m,'c3_hold_start',k)==1,'a new action needs a new lawful engagement: grip starts again from zero')
    m=pursuit(8.0,g=.8);s=m.s;A,B=s.players['A0'],s.players['B0'];load(A,{('hold','B0'):[.97,True]},s.now);full={q.id:(q.x,q.y) for q in m.active_field()};full.update(chase(m))
    old=m.move_players(100,full);evs=m.player_contacts(100,old);ok(any(e.kind=='tackle' for e in evs),'fixture: the kernel has scheduled a grounding inside this step');va=(A.vx,A.vy);k=len(m.e.log)
    m.e.freeze('A0');m.process_events(evs,s.now,100,old)
    ok(not count(m,'tackle_count',k) and count(m,'superseded_observation',k)>=1 and s.tackle_count==0,'an earlier freeze invalidates the scheduled grounding as a tackle')
    ok((A.vx,A.vy)==va,'but the momentum the hold had already taken from him is not given back')
    for label,spoil in (('a foul that stops play',lambda m:m.e.foul('A2','B3','late_hold')),('a possession change',lambda m:(m.e.release('A0',(1.0,0.0,1.0),'pass'),catch(m,'B4',(60,50)))),('the horn',lambda m:m.e.end_period())):
        m=pursuit(8.0,g=.8);s=m.s;A=s.players['A0'];load(A,{('hold','B0'):[.97,True]},s.now);full={q.id:(q.x,q.y) for q in m.active_field()};full.update(chase(m))
        old=m.move_players(100,full);evs=m.player_contacts(100,old);k=len(m.e.log);spoil(m);m.process_events(evs,s.now,100,old)
        ok(any(e.kind=='tackle' for e in evs) and not count(m,'tackle_count',k) and s.tackle_count==0,'a grounding scheduled before '+label+' is not counted after it')
    m=pursuit(8.0,g=.8,cal=None);m.c3_no_strip=False;s=m.s;k=len(m.e.log);B=s.players['B0'];B.freeze_until=s.now+3000
    m.e.batch([Ev('strip','B0','A0',{'control_witness':s.ball.version,'c3':True})])
    ok(not fouls(m,k) and s.ball.carrier=='A0' and count(m,'superseded_observation',k)==1,'a strip scheduled before the stripper was frozen simply does not happen: no ineligible-contact foul from a stale prediction')

    # ---- 10. attribute endpoints, the removed speed offences, and the substep ----
    for lo_hi in (0.0,1.0):
        m=pursuit(8.0,n=2)
        for q in (m.s.players[i] for i in ('A0','B0','B1')):
            for a in ('strength','balance','contact_resistance','tackling','ball_handling','agility'):setattr(q.a,a,lo_hi)
        run(m,15,n=2);vals=[m.c3_bal(m.s.players[i]) for i in ('A0','B0','B1')]+[q.vx for q in (m.s.players[i] for i in ('A0','B0','B1'))]
        ok(all(math.isfinite(v) for v in vals),'attributes at %.0f: every quantity stays finite (weak capacity, never a division by zero)'%lo_hi)
    m=kb();A=kput(m,'A0',(50,50),(20,0));B=kput(m,'B0',(51.2,50),(-20,0));A.contact_velocity=(20,0);B.contact_velocity=(-20,0);kgive(m,'A0')
    ok(m.e.contact_legal(B,A,'tackle')==(True,'legal'),'active C3: no contact-speed offence, at any speed')
    lg=CORE.match.Match(configuration({**SETTINGS,'archery':False},1,LEGACY));A=lg.s.players['A0'];B=lg.s.players['B0'];A.x,A.y,B.x,B.y=50.0,50.0,51.2,50.0;A.contact_velocity=(20,0);B.contact_velocity=(-20,0);lg.s.phase=LIVE;lg.s.ball=Ty.Ball(mode=Ty.BallMode.CONTROLLED,carrier='A0',last_touch='A')
    ok(lg.e.contact_legal(B,A,'tackle')==(False,'contact_speed'),'replay path: the inherited speed offence is still there')
    m=kb();A=kput(m,'A0',(40,50),(0,0));B=kput(m,'B0',(60,50),(0,0));ktop(m,'A0',20);ktop(m,'B0',20);kgive(m,'A0')
    for i in range(12):ktick(m,{'A0':(99,50),'B0':(1,50)})
    ok(m.s.players['B0'].speed>9.5 or count(m,'c3_collision'),'active C3: the fixed 5 and 9 m/s approach ceilings are gone; a defender may close on the carrier at speed')
    times=[]
    for sub in (5,10,20):
        m=pursuit(8.0,cal={'c3_substep_ms':sub});k=len(m.e.log);run(m,20);times.append(next(r['t_ms'] for r in m.e.log[k:] if r['event']=='c3_grounding')-1000)
    ok(max(times)-min(times)<=.05*times[1] and times==sorted(times),'substep 5, 10, 20 ms: the same tackle completes within 5 percent of the same time; the shift is about one and a half substeps: '+str(times))
    rate=.12*.68*(1-.68*.6)
    for sub in (5,10,20):
        lam=-math.log(1-.1*rate)/.1;per=1-math.exp(-lam*sub/1000);ok(near(1-(1-per)**(100/sub),.1*rate,1e-12),'inherited strip chance: per 100 ms of lawful reach it equals the Pocket 1.1 value at a %d ms substep'%sub)
    m=pursuit(8.0,g=.6);m.c3_no_strip=False;m.c3_fix_drive=-1.0;draws=[];real=m.rng['contact'].random;m.rng['contact'].random=lambda:(draws.append(1),.999999)[1];ktick(m,chase(m))
    ok(len(draws)==10 and near(m.stats['c3_hold_ms'],110.0,1e-6),'one strip draw per substep of lawful reach, and reach time is accumulated for the per-second rate')
    m.rng['contact'].random=lambda:0.0;k=len(m.e.log);imp0=m.c3_holds[('B0','A0')]['impulse'];ktick(m,chase(m))
    ok(count(m,'strip',k)==1 and m.s.ball.carrier is None and not m.c3_holds and last(m,'c3_hold_end')['cause']=='strip','a strip ends control, and with it the hold')
    ok(last(m,'c3_hold_end')['impulse_Ns']>=imp0 and next(r['t_ms'] for r in m.e.log[k:] if r['event']=='strip')<=m.s.now,'the strip takes effect at the end of the drift in which it was drawn, after the forces that acted during it')

    # ================= C3a2: event order, swept geometry, legality on real collisions, causal balance =================
    def loose(m):m.s.ball=Ty.Ball(mode=Ty.BallMode.LOOSE,x=5.0,y=5.0,z=.1075,last_touch='A')
    def step1(m,targets,ms=100):
        """One interval of the normal path; returns its length."""
        for pid in targets:m.s.players[pid].next_decision=0
        full={q.id:(q.x,q.y) for q in m.active_field()};full.update(targets);return m.c3_step(ms,full,scripted=True)
    # ---- 11. physical state follows event order ----
    m=kb();m.c3_reckless={'A0','B0'};A=kput(m,'A0',(50,50),(12.5,0));B=kput(m,'B0',(50+A.radius+m.s.players['B0'].radius+.2,50),(-12.5,0));ktop(m,'A0',12.5);ktop(m,'B0',12.5);loose(m)
    k=len(m.e.log);t0=m.s.now;adv=step1(m,{'A0':(99,50),'B0':(1,50)});col=last(m,'c3_collision');gs=[r for r in m.e.log[k:] if r['event']=='c3_grounding']
    ok(near(col['t_ms']-t0,8.0,1e-6) and len(gs)==2 and all(g['t_ms']-t0==8 and near(g['data']['t_ms']-t0,8.0,1e-6) for g in gs),'a collision 8 ms into a substep: the shock is applied at 8 ms and both athletes go down at 8 ms, not before the collision')
    ok(adv==8 and m.s.now==t0+8,'the interval ends at the first event the engine must commit; nothing is integrated beyond it')
    def frozen(split):
        m=pursuit(8.0,g=.8);m.c3_fix_drive=-1.0;s=m.s;m.s.players['B0'].vx=7.0;k=len(m.e.log);t0=s.now;T={'A0':(99,50),'B0':(99,51)}
        if split:ktick(m,T,10);m.e.freeze('A0');m.c3_reconcile();ktick(m,T,90);first=10
        else:karrow(m,'B','A0',10);first=step1(m,T);ktick(m,T,100-first)
        return m,k,t0,first
    m,k,t0,first=frozen(False);ref,_,_,_=frozen(True);fz=next(r['t_ms'] for r in m.e.log[k:] if r['event']=='freeze')-t0;he=last(m,'c3_hold_end')
    ok(fz==10 and first<=11 and not m.c3_holds and he['cause']=='control_lost' and he['end_ms']==t0+10,'an arrow freezes the carrier 10 ms into an interval: the interval is recomputed to end there, and the hold ends at the freeze')
    ok(m.stats['c3_hold_ms']-10<=11 and abs(m.c3_bal(m.s.players['A0'])-ref.c3_bal(ref.s.players['A0']))<.005 and abs(m.s.players['A0'].vx-ref.s.players['A0'].vx)<.02,'no hold force or balance load is applied after the freeze: the state matches the same play split by hand at the freeze, to within the one-millisecond clock')
    ok(not any(r['event'].startswith('c3_') and r['t_ms']>t0+11 for r in m.e.log[k:]),'and the kernel records nothing for that pair after the freeze')
    def race(offset=None,cal=None):
        """An established strong hold with the holder driving, restraint switched off so that the preparation time is exact.
        offset None: no action in preparation, returns the grounding time. Otherwise the pass falls due that many ms from the grounding."""
        m=pursuit(8.0,g=.8,cal={'restraint_weight_matched':0.0,'restraint_weight_other':0.0,**(cal or {})});s=m.s;A=s.players['A0'];kput(m,'A1',(34,56),(8,0));ktop(m,'A1',8);k=len(m.e.log);t0=s.now
        if offset is not None:m.pending_ball_actions['A0']=(t0+offset,'pass','A1');m.c3_prep['A0']=t0-200
        for i in range(150):
            ktick(m,{'A0':(99,50),'A1':(99,56),'B0':(A.x,A.y)},10)
            if s.ball.carrier!='A0':break
        g=next((r['t_ms']-t0 for r in m.e.log[k:] if r['event']=='c3_grounding' and r['data']['player']=='A0'),None)
        rel=next((r['t_ms']-t0 for r in m.e.log[k:] if r['event']=='release' and not r['data']['forced']),None)
        return m,k,g,rel
    _,_,Tg,_=race();ok(Tg is not None and 40<Tg<1400 and Tg%10!=0,'fixture: the hold grounds the carrier %s ms in, at its own time and not on a substep or step boundary'%Tg)
    m,k,g,rel=race(Tg-3);ok(rel==Tg-3 and not count(m,'tackle_count',k) and not count(m,'c3_grounding',k,cls='tackle_under_hold'),'a pass whose preparation completes 3 ms before the grounding is released first, at its own millisecond, and there is no tackle')
    m,k,g,rel=race(Tg+3);m.carrier_decision();ok(rel is None and g==Tg and count(m,'tackle_count',k)==1 and 'A0' not in m.pending_ball_actions,'a pass that would complete 3 ms after the grounding is not released: the tackle comes first and the preparation is cancelled')
    m=passing('upper',.5);s=m.s;k=len(m.e.log);due=[]
    for i in range(900):
        due.append(m.c3_due['A0'] if 'A0' in m.pending_ball_actions else None);ktick(m,{'A0':(99,50),'A1':(99,56),'B0':(s.players['A0'].x,50)},1)
        if s.ball.carrier!='A0':break
    r1=next(r for r in m.e.log[k:] if r['event']=='release');was=[d for d in due if d is not None]
    ok(abs(r1['t_ms']-was[-1])<=1 and was[-1]>was[0]+50 and all(b>=a for a,b in zip(was,was[1:])),'under restraint the remaining preparation is integrated continuously, and the pass is released in the millisecond it completes')
    ok(passing(calm=True).pending_ball_actions['A0'][0]%100!=0,'a preparation takes its actual time; it is not rounded up to a whole 100 ms step')
    m=passing(calm=True,cal={'c3_prep_round_ms':100});ok((m.pending_ball_actions['A0'][0]-m.s.now)%100==0,'the comparison setting restores the inherited rounding')
    rm=CORE.match.Match(configuration({**SETTINGS,'period_seconds':90,'periods':1},11,C3CAL));inside=0;seen=0;short=0;ends=[]
    while rm.s.phase!=Ty.Phase.FINAL:
        a0=rm.s.now;k=len(rm.e.log);rm.step();a1=rm.s.now;short+=0<a1-a0<100
        for r in rm.e.log[k:]:
            if r['event'] in ('control','freeze','c3_grounding','tackle_count','strip','foul','goal','deflection','flight_ended'):
                seen+=1;inside+=not(r['t_ms']>=a1-1 or r['t_ms']==a0)
            if r['event']=='c3_hold_end':ends.append(r)
        if rm.s.live_ms>=90000:break
    ok(seen>=20 and inside==0 and short>0 and rm.stats['c3_recompute_unconverged']==0,'a real match: every catch, deflection, freeze, grounding, strip, foul, goal and ball landing that ends a flight is committed within one millisecond of the end of its interval; none lies inside one')
    ok(len(ends)>5 and all(r['data']['reach_ms']<=r['data']['duration_ms']+1e-6 and r['data']['end_ms']<=r['t_ms']+1e-6 for r in ends),'every hold record in that match: time in reach never exceeds the hold\'s duration, and no hold is reported to end after the time it is logged')

    # ---- 12. swept reach and body intersection (the kernel's own integrator, athletes at 25 m/s) ----
    def reach_of(m,d='B0',c='A0'):a,b=m.s.players[c],m.s.players[d];return a.radius+b.radius+.7*(a.a.reach+b.a.reach)
    def sweep(bx,by,bv,carrier=True):
        m=kb();m.c3_reckless={'A0','B0'};A=kput(m,'A0',(50,50));B=kput(m,'B0',(50+bx,50+by),bv);B.facing=(-1.0,0.0)
        if carrier:kgive(m,'A0')
        else:loose(m)
        return m,krun(m,('A0','B0'),10,'A0' if carrier else None)
    m=kb();R=reach_of(m);y=R-.0001;half=math.sqrt(R*R-y*y)
    m,evs=sweep(-.125,y,(25,0));he=knotes(evs,'c3_hold_end')
    ok(math.hypot(.125,y)>R and near(m.stats['c3_hold_ms'],2000*half/25,1e-6) and len(he)==1 and he[0]['cause']=='out_of_reach' and near(he[0]['duration_ms'],2000*half/25,1e-3),'reach crossed inside a substep with both ends outside: the %.3f ms actually spent within reach is found and integrated'%(2000*half/25))
    m,evs=sweep(R+.1,0,(-25,0));h=m.c3_holds[('B0','A0')]
    ok(near(m.stats['c3_hold_ms'],6.0,1e-6) and near(h['start']-m.s.now,4.0,1e-6) and 0<h['g']<.03,'entry only: grip is integrated over the 6 ms after reach begins, not over the whole substep')
    g_in=h['g'];m,evs=sweep(R-.1,0,(25,0));he=knotes(evs,'c3_hold_end')
    ok(near(m.stats['c3_hold_ms'],4.0,1e-6) and not m.c3_holds and near(he[0]['end_ms']-m.s.now,4.0,1e-3) and he[0]['cause']=='out_of_reach' and 0<he[0]['grip_at_end'],'exit only: the hold ends at the instant reach ends, 4 ms in, and its witnessed end time says so')
    m=kb();Rb=m.s.players['A0'].radius+m.s.players['B0'].radius
    m,evs=sweep(Rb+.004,0,(-1,25),carrier=False);ok(not knotes(evs,'c3_collision') and m.c3_bal(m.s.players['A0'])==0,'a glancing near miss (bodies come within 3 mm but never touch) is not a collision')
    yc=Rb-.004;hc=math.sqrt(Rb*Rb-yc*yc);m,evs=sweep(-.125,yc,(25,0),carrier=False);col=knotes(evs,'c3_collision')
    ok(math.hypot(.125,yc)>Rb and len(col)==1 and abs(col[0]['t_ms']-m.s.now-1000*(.125-hc)/25)<1e-3,'a grazing contact that begins and would end inside one substep is found, at the instant the bodies first touch')
    m,evs=sweep(Rb+.3,0,(-50,0),carrier=False);col=knotes(evs,'c3_collision');ok(len(col)==1 and abs(col[0]['t_ms']-m.s.now-6.0)<1e-3 and col[0]['closing_mps']==50.0,'a 50 m/s closing contact is met at the solved instant (6 ms), not tunnelled or caught late')
    def leaving(stays):
        """A0 has the ball. B0 has an established strong hold; B1 runs into A0 at 25 m/s and arrives 8 ms in. B0 either stays, or is
        already going past at 25 m/s and leaves reach 4 ms in."""
        m=kb();m.c3_reckless={'A0','B0','B1'};A=kput(m,'A0',(50,50));A.facing=(1.0,0.0);kgive(m,'A0');R=reach_of(m)
        B0=kput(m,'B0',(50,50+R-.1),(0,0) if stays else (0,25));B0.facing=(0.0,-1.0);B1=kput(m,'B1',(50+A.radius+m.s.players['B1'].radius+.2,50),(-25,0))
        m.c3_holds[('B0','A0')]={'actor':'B0','target':'A0','g':.6,'region':'lower','start':m.s.now-300.0,'reach_ms':300.,'peak':.6,'impulse':0.,'excess':0.,'force':0.,'slip':0.};m.c3_fix_drive=-1.0
        evs=krun(m,('A0','B0','B1'),20,'A0');g=next(e.data['c3'] for e in evs if e.kind in ('tackle','ground') and e.data['c3']['player']=='A0');return m,evs,g
    m,evs,g=leaving(True);ok(g['cls']=='tackle_under_hold' and g['credited']=='B0' and near(g['t_ms']-m.s.now,8.0,1e-4),'a holder still within reach when the carrier is knocked down holds the tackle')
    m,evs,g=leaving(False);he=[h for h in knotes(evs,'c3_hold_end') if h['actor']=='B0'][0]
    ok(he['cause']=='out_of_reach' and near(he['end_ms']-m.s.now,4.0,1e-3) and 'B0' not in [h['player'] for h in g['holders']] and g['cls']=='tackle_by_lawful_contact' and g['credited']=='B1','a holder who was within reach earlier in the same substep but has gone by the grounding instant has no engagement: the tackle is the lawful hit that grounded him')

    # ---- 13. retained contact legality acts on real collisions; physics and responsibility are separate ----
    def rear(v=20.0,facing=(1.0,0.0),cal=None,reckless=True,gap=.05):
        """B0 runs into the stationary non-carrier A0 from the -x side. facing (1,0): A0 has his back to him."""
        m=kb(cal);A=kput(m,'A0',(50,50));A.facing=facing;B=kput(m,'B0',(50-A.radius-m.s.players['B0'].radius-gap,50),(v,0));B.facing=(1.0,0.0);ktop(m,'B0',max(v,.1));loose(m)
        if reckless:m.c3_reckless={'B0'}
        return m,A,B
    m,A,B=rear();pre=m.e.contact_legal(B,A,'block');k=len(m.e.log);ktick(m,{'B0':(99,50)});col=last(m,'c3_collision');w={r['player']:r for r in col['responsibility']}
    ok(pre==(False,'blindside') and fouls(m,k)==['blindside'] and last(m,'foul')['actor']=='B0' and last(m,'foul')['victim']=='A0','a hit from behind on the normal path: the retained blindside classification is applied to the collision that actually happened, and the hitter is penalised')
    ok(w['B0']['initiated'] and w['B0']['foul']=='blindside' and near(w['B0']['share_of_closing'],1.0) and not w['A0']['initiated'] and w['A0']['classification']=='legal','the approach witness names who ran into whom; a contact that would have been lawful the other way round does not erase the illegal hit')
    gd={r['data']['player']:r['data'] for r in m.e.log[k:] if r['event']=='c3_grounding'}
    ok(set(gd)=={'A0','B0'} and 'shock:B0:unlawful' in gd['A0']['sources'] and 'shock:A0:lawful' in gd['B0']['sources'],'the physical consequence is the same whoever is at fault: both go down; the load the hitter put on his victim is recorded as unlawful')
    blind_shock=col['shock_a'];m,A,B=rear(facing=(-1.0,0.0));k=len(m.e.log);ktick(m,{'B0':(99,50)});col=last(m,'c3_collision')
    ok(not fouls(m,k) and near(col['closing_mps'],20.0,1e-3) and col['shock_a']>=1,'the same hit on a man who is facing it is lawful: no foul, at any speed. There is no speed offence')
    m,A,B=rear(v=20.0,facing=(-1.0,0.0),gap=2.0);k=len(m.e.log);step1(m,{'B0':(99,50)},20);A.facing=(1.0,0.0);ktick(m,{'B0':(99,50)},180);w={r['player']:r for r in last(m,'c3_collision')['responsibility']}
    ok(not fouls(m,k) and w['B0']['classification']=='blindside' and w['B0']['not_sanctioned']=='no_time_to_avoid' and w['B0']['avoidability']['changed_to']=='blindside' and w['B0']['avoidability']['gap_then_m']<w['B0']['avoidability']['stopping_gap_m'] and w['B0']['avoidability']['elapsed_ms']<w['B0']['avoidability']['stopping_time_ms'],'unavoidable momentum: the man ahead turned his back when the runner was already inside his reaction and braking distance, so the hit is recorded but not penalised')
    def shoved(v=8.0,gap=.3,side=False,run=None,ms=300):
        """A1 runs into B0, who is facing him, and knocks him back towards A0, who stands with his back to B0 (side: knocks him
        across A0's back instead). run: B0 then runs at A0 himself at that speed. Returns the match and B0's witness on A0."""
        m=kb();m.c3_reckless={'A1','B0'};loose(m);B=kput(m,'B0',(50,50));B.facing=(0.0,-1.0) if side else (-1.0,0.0);r=B.radius;A=kput(m,'A0',(50+2*r+gap,50));A.facing=(1.0,0.0)
        A1=kput(m,'A1',(50,50-2*r-.05),(0,v)) if side else kput(m,'A1',(50-2*r-.05,50),(v,0));ktop(m,'A1',v);tg={'A1':(A1.x,A1.y)};k=len(m.e.log)
        if run:tg['B0']=(99,50);ktop(m,'B0',run)
        for i in range(ms//50):ktick(m,tg,50)
        w=[x for r_ in m.e.log[k:] if r_['event']=='c3_collision' and r_['data']['a']=='A0' for x in r_['data']['responsibility'] if x['player']=='B0'];return m,k,(w[0] if w else None)
    m,k,w=shoved()
    ok(not fouls(m,k) and w['classification']=='blindside' and w['not_sanctioned']=='carried_by_another_contact' and w['driven_by']==['A1'] and w['own_approach_mps']>1 and near(w['driven_approach_mps'],w['own_approach_mps'],1e-3) and not w['initiated'],'unavoidable momentum: an athlete knocked into an opponent\'s back by a real collision a moment earlier is not penalised; the witness is the velocity that collision gave him, towards the man he hit')
    m,A,B=rear(v=.2);k=len(m.e.log);ktick(m,{'B0':(99,50)},500);col=last(m,'c3_collision')
    ok(not fouls(m,k) and col['shock_a']<.05 and col['responsibility'][1]['initiated'] and not col['responsibility'][1]['material'],'a touch from behind too light to matter (below contact_foul_min_shock) is recorded as initiated by him, not material, and not penalised: who ran into whom and whether it matters are separate answers')
    m,A,B=rear(v=.2,cal={'contact_foul_min_shock':0.0});k=len(m.e.log);ktick(m,{'B0':(99,50)},500);ok(fouls(m,k)==['blindside'],'with the materiality floor at zero the same touch is a foul: the floor is a declared setting, not a hidden rule')
    m,A,B=rear(v=20.0,reckless=False,gap=30.0);k=len(m.e.log)
    for i in range(40):ktick(m,{'B0':(99,50)})
    ok(not count(m,'c3_collision',k) and not fouls(m,k) and A.x-B.x>A.radius+B.radius+.3 and B.speed<.5,'CONTROLLER: an athlete who can see he would hit an opponent from behind stops short of him')
    m=pursuit(8.0);s=m.s;A,B=s.players['A0'],s.players['B0'];s.award_spot=(s.ball.x,s.ball.y);s.award_available=s.now;k=len(m.e.log)
    for i in range(3):s.award_spot=(s.ball.x,s.ball.y);ktick(m,{'A0':(99,50),'B0':(99,51)},10)
    ok(m.e.contact_legal(B,A,'tackle')==(False,'protected_recovery') and not m.c3_holds and not fouls(m,k) and not count(m,'c3_hold_start',k),'within reach of a protected carrier without touching him: no hold forms and nothing is penalised. An unsuccessful reach is not a foul')
    m=kb();m.c3_reckless={'B0'};A=kput(m,'A0',(50,50));A.facing=(-1.0,0.0);kgive(m,'A0');B=kput(m,'B0',(50-A.radius-m.s.players['B0'].radius-.05,50),(6,0));ktop(m,'B0',6);s=m.s;s.award_spot=(s.ball.x,s.ball.y);s.award_available=s.now;k=len(m.e.log);ktick(m,{'B0':(99,50)},20)
    ok(fouls(m,k)==['protected_recovery'] and last(m,'foul')['actor']=='B0','but running into a protected carrier is penalised under the retained protection, at the collision')

    # ---- 14. balance contributions are kept by cause and by lawfulness, and summed per defender ----
    m,k=grounded_with(.29,{('shock','B0'):[.42,True],('hold','B0'):[.21,True],('shock','B5'):[.42,True]});d=last(m,'c3_grounding')
    ok(d['cls']=='tackle_by_lawful_contact' and d['credited']=='B0' and near(d['lawful_defensive_share'],.6,2e-2) and d['in_lawful_contact']==['B0'],'a defender in current lawful contact who supplied a shock and a hold: both count, 60 percent of the load, a tackle')
    m2=pursuit(8.0,g=.29);m2.c3_fix_drive=-1.0;m2.assume['grip_gain_per_s']=0.0;m2.assume['grip_resist_per_s']=0.0;A=m2.s.players['A0']
    A.bal_src={('shock','B0',True):.30,('shock','B0',False):.45,('shock','B5',True):.30};A.bal_t0=m2.s.now;k=len(m2.e.log);ktick(m2,{'A0':(99,50)});d=last(m2,'c3_grounding')
    ok(d['cls']=='carrier_grounded_not_a_tackle' and near(d['lawful_supplied']['B0'],.30,5e-2) and d['sources']['shock:B0:unlawful']>d['sources']['shock:B0:lawful'],'the same defender, lawful and unlawful load: only the lawful part counts, and it is not enough')
    m3=pursuit(8.0,g=.29);m3.c3_fix_drive=-1.0;m3.assume['grip_gain_per_s']=0.0;m3.assume['grip_resist_per_s']=0.0;A=m3.s.players['A0']
    A.bal_src={('shock','B0',True):.60,('shock','B0',False):.15,('shock','B5',True):.30};A.bal_t0=m3.s.now;ktick(m3,{'A0':(99,50)});ok(last(m3,'c3_grounding')['cls']=='tackle_by_lawful_contact','and with the proportions reversed it is a tackle')
    m=pursuit(8.0);A=m.s.players['A0'];A.bal_src={('shock','B0',True):.8};A.bal_t0=m.s.now;m.c3_add(A,('shock','B0'),.0001,False,m.s.now)
    ok(near(A.bal_src[('shock','B0',True)],.8) and near(A.bal_src[('shock','B0',False)],.0001),'a later unlawful contribution does not relabel lawful load already there')
    m.c3_add(A,('shock','B0'),.1,True,m.s.now);m.c3_add(A,('shock','B0'),.05,True,m.s.now);ok(near(A.bal_src[('shock','B0',True)],.95) and near(A.bal_src[('shock','B0',False)],.0001),'repeated contributions from one source add to their own entry')
    before=dict(A.bal_src);m.c3_recover(A,.1);f=A.bal_src[('shock','B0',True)]/before[('shock','B0',True)];ok(0<f<1 and ('shock','B0',False) not in A.bal_src and near(m.c3_bal(A),.95*f),'each contribution decays on its own at the recovery rate, and one that has decayed away is dropped without touching the others')
    m=crash(5.0,-5.0);k=len(m.e.log);A,B=m.s.players['A0'],m.s.players['B0']
    for i in range(8):ktick(m,{'A0':(99,50),'B0':(1,50)})
    kput(m,'A0',(A.x-.4,50),(2,0));kput(m,'B0',(B.x+.4,50),(-2,0));ktop(m,'A0',2);ktop(m,'B0',2);key=('shock','B0',True)
    for i in range(8):
        before=A.bal_src.get(key,0.0);ktick(m,{'A0':(99,50),'B0':(1,50)},50)
        if count(m,'c3_collision',k)==2:break
    ok(count(m,'c3_collision',k)==2 and list(A.bal_src)==[key] and 0<before<A.bal_src[key],'two collisions with the same opponent, through the kernel: one entry, the second shock added to what is left of the first')

    # ---- 15. reporting: the witnessed end of a hold ----
    m=pursuit(8.0,g=.8);m.c3_fix_drive=-1.0;s=m.s;k=len(m.e.log);start=m.c3_holds[('B0','A0')]['start'];m.e.elapse(70,resolve=False);m.e.release('A0',(20.0,0.0,1.0),'pass');m.c3_reconcile();d=last(m,'c3_hold_end')
    ok(d['end_ms']==s.now and d['duration_ms']==s.now-start and d['cause']=='control_lost','a hold ended by a release 70 ms after the last integration reports the time of the release, not the last time it was integrated')
    m,k=grounded_with(.6,OLD);d=last(m,'c3_hold_end');g=last(m,'c3_grounding');ok(d['cause']=='carrier_grounded' and d['end_ms']==g['t_ms'],'a hold ended by the grounding reports the grounding instant')
    ks=list(CORE.match.DEFAULT_ASSUMPTIONS);new=ks[ks.index('c3_contact')+1:]
    ok(set(new)==set(C3_RANGES) and all(C3_RANGES[k][0]<=C3CAL[k]<=C3_RANGES[k][1] for k in new),'every C3 coefficient has a declared range, and its value lies inside it')

    # ---- 16. cases found by an independent check of this submission ----
    def two_pairs(alone):
        """Pair 1 (A0, B0) collides at 7.4 ms and both go down, ending the interval at 8 ms. Pair 2 (A1, B1), 20 m away, would first
        touch at 7.7 ms: in the fraction of a millisecond after the interval's last event."""
        m=kb();m.c3_reckless={'A0','B0','A1','B1'};loose(m);R=m.s.players['A0'].radius+m.s.players['B0'].radius
        if not alone:kput(m,'A0',(50,50),(12.5,0));kput(m,'B0',(50+R+.185,50),(-12.5,0));ktop(m,'A0',12.5);ktop(m,'B0',12.5)
        kput(m,'A1',(50,70),(12.5,0));kput(m,'B1',(50+R+.1925,70),(-12.5,0));ktop(m,'A1',12.5);ktop(m,'B1',12.5);k=len(m.e.log);t0=m.s.now
        ktick(m,{'A0':(99,50),'B0':(1,50),'A1':(99,70),'B1':(1,70)},60)
        c=next(r for r in m.e.log[k:] if r['event']=='c3_collision' and r['data']['a']=='A1');return c['t_ms']-t0,c['data']['t_ms']-t0,c['data']['closing_mps']
    solo=two_pairs(True);both=two_pairs(False)
    ok(near(solo[1],7.7,1e-4) and both[0]<=9 and abs(both[1]-7.7)<=1.0 and near(both[2],25.0,1e-3),'two bodies that first touch in the last fraction of a millisecond of an interval ended by another event collide at the start of the next one, within the one-millisecond clock, not a substep later: logged at %s ms, true contact 7.7 ms'%both[0])
    def together(order):
        """Carrier A0 and his holder B0 (grip 0.8) run into each other and both go down at the same instant. order: who is listed first."""
        m=kb();m.c3_reckless={'A0','B0'};A=kput(m,'A0',(50,50),(7,0));kgive(m,'A0');B=kput(m,'B0',(50+A.radius+m.s.players['B0'].radius+.1,50),(-7,0));m.c3_fix_drive=-1.0
        m.c3_holds[('B0','A0')]={'actor':'B0','target':'A0','g':.8,'region':'lower','start':m.s.now-300.0,'reach_ms':300.,'peak':.8,'impulse':0.,'excess':0.,'force':0.,'slip':0.}
        evs=krun(m,order,20,'A0');return next(e.data['c3'] for e in evs if e.kind in ('tackle','ground') and e.data['c3']['player']=='A0'),[e.data['c3']['player'] for e in evs if e.kind in ('tackle','ground')]
    g1,o1=together(('A0','B0'));g2,o2=together(('B0','A0'))
    ok(sorted(o1)==sorted(o2)==['A0','B0'] and g1['cls']==g2['cls']=='tackle_under_hold' and g1['credited']==g2['credited']=='B0' and [h['player'] for h in g2['holders']]==['B0'],'carrier and holder going down at the same instant: the same counted tackle whichever of them is listed first')
    m,A,B=rear(facing=(-1.0,0.0));ktick(m,{'B0':(99,50)},20)
    col=last(m,'c3_collision');fa,ha=m.c3_driven(A,m.s.now);fb,hb=m.c3_driven(B,m.s.now)
    ok(len(fa)==1 and fa[0][3]=='B0' and near(math.hypot(fa[0][1],fa[0][2]),col['dv_a'],1e-3) and fa[0][1]>0 and not fb and hb[0]==hb[1]==0,'only the athlete who was run into has velocity imposed on him by that collision (his whole velocity change, in its direction); the one who ran in caused his own')
    m=pursuit(8.0,g=.8);s=m.s;A=s.players['A0'];load(A,{('hold','B0'):[.995,True]},s.now);h=m.c3_holds[('B0','A0')];r0=h['reach_ms'];k=len(m.e.log);t0=s.now;ktick(m,chase(m),10);d=last(m,'c3_hold_end');g=last(m,'c3_grounding')
    ok(d['cause']=='carrier_grounded' and 0<g['t_ms']-t0<10 and near(d['reach_ms']-r0,g['t_ms']-t0,1e-3) and d['reach_ms']<=d['duration_ms']+1e-6,'a grounding part-way through a substep: grip, time in reach and velocity changes are all taken back to that instant, not only the balance load')

    # ================= C3a3: collision responsibility (the Lead's three counterexamples and what was found beside them) =================
    # ---- 17. initiation is a kinematic fact; materiality is a separate filter on the athlete's own part ----
    def meet(va,vb,cal=None):
        """Non-carriers A0 (+x at va) and B0 (-x at vb) meet. Both are made to face +x, so A0's contact is on B0's back."""
        m=kb(cal);m.c3_reckless={'A0','B0'};loose(m);A=kput(m,'A0',(50,50),(va,0));B=kput(m,'B0',(50+A.radius+m.s.players['B0'].radius+.04,50),(-vb,0));A.facing=B.facing=(1.0,0.0)
        ktop(m,'A0',max(va,.1));ktop(m,'B0',max(vb,.1));k=len(m.e.log);ktick(m,{'A0':(99,50) if va else (A.x,50),'B0':(1,50)},10);col=last(m,'c3_collision');return m,k,col,{r['player']:r for r in col['responsibility']}
    m,k,col,w=meet(10.0,12.0);m2,k2,col2,w2=meet(11.0,11.0)
    ok(fouls(m,k)==['blindside'] and last(m,'foul')['actor']=='A0' and w['A0']['initiated'] and near(w['A0']['share_of_closing'],.455,1e-2) and w['A0']['foul']=='blindside' and 'foul' not in w['B0'] and w['B0']['classification']=='legal','LEAD 1: an athlete who runs into an opponent\'s back while supplying the smaller part of the closing speed (10 of 22 m/s) still initiated the contact and is penalised')
    ok(fouls(m2,k2)==['blindside'] and near(col['impulse_Ns'],col2['impulse_Ns'],1e-9) and near(col['shock_b'],col2['shock_b'],1e-9) and col['shock_b']>1,'LEAD 1: the same closing speed split 11 and 11 gives the same impulse, the same shock and the same foul')
    m,k,col,w=meet(1.0,21.0);ok(fouls(m,k)==['blindside'] and w['A0']['own_part_of_shock']>=.05 and near(w['A0']['own_part_of_shock'],col['shock_b']/22,1e-2),'one twenty-second of the closing speed is still his: his part of the shock is the shock times his share, and here it is material')
    m,k,col,w=meet(.2,21.8);ok(not fouls(m,k) and w['A0']['initiated'] and not w['A0']['material'] and w['A0']['own_part_of_shock']<.05 and col['shock_b']>1,'materiality is judged on what his own motion supplied: creeping at 0.2 m/s towards a man who runs backwards into him at 21.8 is initiated, immaterial, and not penalised, however hard the hit was')
    m,k,col,w=meet(.2,21.8,{'contact_foul_min_shock':0.0});ok(fouls(m,k)==['blindside'],'and with the materiality floor at zero that touch is a foul: the floor filters, it does not decide who initiated')
    m,k,col,w=meet(0.0,22.0);ok(not fouls(m,k) and not w['A0']['initiated'] and w['A0']['voluntary_approach_mps']==0 and w['B0']['initiated'] and 'foul' not in w['B0'],'a stationary athlete whose opponent backs into him has initiated nothing')
    # ---- 18. carried by another contact needs velocity actually imposed, in the direction of the hit ----
    def third(strong):
        """LEAD 2: B0 runs at 20 m/s into the back of stationary A0 while holding A1, who runs beside him at the same velocity."""
        m=kb();m.c3_reckless={'A0','A1','B0'};m.c3_fix_drive=-1.0;A=kput(m,'A0',(50,50));A.facing=(1.0,0.0);B=kput(m,'B0',(50-A.radius-m.s.players['B0'].radius-.05,50),(20,0));B.facing=(1.0,0.0)
        kput(m,'A1',(B.x,52),(20,0));kgive(m,'A1');ktop(m,'B0',20);ktop(m,'A1',20,True)
        if strong:m.c3_holds[('B0','A1')]={'actor':'B0','target':'A1','g':.8,'region':'lower','start':m.s.now-300.0,'reach_ms':300.,'peak':.8,'impulse':0.,'excess':0.,'force':0.,'slip':0.}
        k=len(m.e.log);ktick(m,{'B0':(99,50),'A1':(99,52)},10);col=next(r['data'] for r in m.e.log[k:] if r['event']=='c3_collision' and r['data']['a']=='A0');return m,k,col,{r['player']:r for r in col['responsibility']}
    m,k,col,w=third(True);m2,k2,col2,w2=third(False);he=next(r['data'] for r in m.e.log[k:] if r['event']=='c3_hold_end')
    ok(fouls(m,k)==['blindside'] and last(m,'foul')['actor']=='B0' and w['B0']['foul']=='blindside' and w['B0']['driven_approach_mps']==0 and he['peak_grip']>=.3 and he['impulse_Ns']==0,'LEAD 2: holding a third athlete with a strong grip that transmits no force is no excuse for running into an opponent\'s back')
    ok(fouls(m2,k2)==['blindside'] and near(col['impulse_Ns'],col2['impulse_Ns'],1e-9) and near(col['shock_a'],col2['shock_a'],1e-9),'LEAD 2: with and without the grip it is the same collision and the same foul')
    m,k,w=shoved(side=True,run=6.0,gap=.15);rt=m.s.players['B0'].a.decision_speed
    ok(fouls(m,k)==['blindside'] and w['driven_approach_mps']==0 and w['voluntary_approach_mps']>1 and (next(r['t_ms'] for r in m.e.log[k:] if r['event']=='foul')-1000)<1000*rt,'a recent collision is not an excuse by existing: knocked sideways, he then ran into the man\'s back himself within his reaction time, and is penalised')
    m,k,w=shoved(gap=6.0,run=6.0,ms=2000);ok(fouls(m,k)==['blindside'] and w['driven_approach_mps']==0,'nor is an old one: knocked towards a man six metres away, he had the time to stop, kept running, and is penalised')
    m,A,B=rear(v=6.0);m.c3_push(B,3.0,0.0,'A5',m.s.now);k=len(m.e.log);ktick(m,{'B0':(99,50)},20);w=[r for r in last(m,'c3_collision')['responsibility'] if r['player']=='B0'][0]
    ok(fouls(m,k)==['blindside'] and near(w['driven_approach_mps'],3.0,1e-6) and near(w['voluntary_approach_mps'],w['own_approach_mps']-3.0,1e-6) and w['share_of_closing']>.99,'a push excuses only its own amount: given 3 m/s and running in at 6, the other 3 are his, material, and penalised')
    m,A,B=rear(v=6.0);m.c3_push(B,0.0,9.0,'A5',m.s.now);k=len(m.e.log);ktick(m,{'B0':(99,50)},20);ok(fouls(m,k)==['blindside'],'a push across his line of approach excuses none of it, whatever its size')
    def dragged(passive):
        """B0 stands just behind A0's back with a strong grip on the carrier A1, who runs past and pulls him forward into A0."""
        m=kb();m.c3_reckless={'A0','A1','B0'};m.c3_fix_drive=-1.0 if passive else None;A=kput(m,'A0',(50,50));A.facing=(1.0,0.0);B=kput(m,'B0',(50-2*A.radius-.05,50));B.facing=(1.0,0.0)
        kput(m,'A1',(B.x,51.6),(10,0));kgive(m,'A1');ktop(m,'A1',10,True);k=len(m.e.log)
        m.c3_holds[('B0','A1')]={'actor':'B0','target':'A1','g':.8,'region':'lower','start':m.s.now-300.0,'reach_ms':300.,'peak':.8,'impulse':0.,'excess':0.,'force':0.,'slip':0.}
        for i in range(8):ktick(m,{'A1':(99,51.6)},50)
        return m,k,[x for r_ in m.e.log[k:] if r_['event']=='c3_collision' and r_['data']['a']=='A0' for x in r_['data']['responsibility'] if x['player']=='B0'][0]
    m,k,w=dragged(True);ok(not fouls(m,k) and w['not_sanctioned']=='carried_by_another_contact' and w['driven_by']==['A1'] and w['own_approach_mps']>.5 and near(w['driven_approach_mps'],w['own_approach_mps'],1e-3),'the genuine case is kept: a holder pulled into an opponent\'s back by the force coming through his hold, within his reaction time, is not penalised. The witness is the velocity the hold gave him')
    B=kb().s.players['B0'];B.a.decision_speed=.3;B.a.braking=13.5;mm=kb();mm.c3_push(B,3.0,4.0,'A1',1000.0);f1,h1=mm.c3_driven(B,1299.0);f2,h2=mm.c3_driven(B,1400.0);f3,h3=mm.c3_driven(B,1300.0+1000*5/13.5+1)
    ok(len(f1)==1 and h1[:2]==(0.0,0.0) and not f2 and near(math.hypot(h2[0],h2[1]),5-1.35,1e-6) and near(h2[0]/h2[1],.75,1e-9) and h2[3]==('A1',) and h3[:2]==(0.0,0.0) and h3[3]==(),'imposed velocity: carried in full for the reaction time, then reduced at his own braking limit with its direction kept, then gone')
    B.c3_ext=None
    for i in range(100):mm.c3_push(B,.2,0.0,'A1',1000.0+10*i)
    held=mm.c3_driven(B,2000.0);tot=held[1][0]+sum(e[1] for e in held[0]);B.c3_ext=None
    for i in range(100):mm.c3_push(B,.1,0.0,'A1',1000.0+10*i)
    weak=mm.c3_driven(B,2000.0);ok(near(tot,20-13.5*.7,1e-6) and weak[1][0]<=.1+1e-9 and near(sum(e[1] for e in weak[0]),.1*29,1e-9),'a force stronger than his braking (20 m/s2 against 13.5) keeps driving him for as long as it lasts; a weaker one (10 m/s2) counts only for his reaction time (the last step to leave that window has not yet been braked off)')
    # ---- 19. no time to avoid needs a witnessed change of legal circumstances, and a gap too short to stop in ----
    def onto(gap,v=6.0,protect_after=None,ms=900):
        """B0 runs at v at the stationary carrier A0, who faces him, from gap metres. protect_after: A0 becomes a protected carrier
        that many ms into the run (0: he is protected from the start)."""
        m=kb();m.c3_reckless={'B0'};A=kput(m,'A0',(50,50));A.facing=(-1.0,0.0);kgive(m,'A0');B=kput(m,'B0',(50-A.radius-m.s.players['B0'].radius-gap,50),(v,0));B.facing=(1.0,0.0);ktop(m,'B0',v);s=m.s;k=len(m.e.log);t0=s.now
        while s.now<t0+ms and not count(m,'c3_collision',k):
            if protect_after is not None and s.now>=t0+protect_after and s.award_available is None:s.award_spot=(s.ball.x,s.ball.y);s.award_available=s.now
            ktick(m,{'B0':(99,50)},10)
        col=last(m,'c3_collision') if count(m,'c3_collision',k) else None;return m,k,col,([r for r in col['responsibility'] if r['player']=='B0'][0] if col else None),t0
    m=kb();A=kput(m,'A0',(50,50));kgive(m,'A0');B=kput(m,'B0',(44,50));m.s.award_spot=(m.s.ball.x,m.s.ball.y);m.s.award_available=m.s.now
    ok(m.e.contact_legal(B,A,'tackle')==(False,'out_of_contact_range') and m.e.contact_legal(B,A,'tackle',reach=False)==(False,'protected_recovery'),'the legal condition can be asked without the distance test: out of reach of a protected carrier, the contact would be unlawful')
    kput(m,'B1',(44,52));ok(m.e.contact_legal(B,m.s.players['A1'],'block',reach=False)[0] and all((m.e.contact_legal(B,q,'block',reach=False)[1]=='blindside')==((B.x-q.x)*q.facing[0]+(B.y-q.y)*q.facing[1]<-.25*max(.1,math.hypot(B.x-q.x,B.y-q.y))) for q in m.s.players.values() if q.team=='A' and q.role=='field' and q.active),'for an eligible upright non-carrier in live play that condition is the facing test alone, which is what the kernel applies to such pairs')
    m,k,col,w,t0=onto(3.0,protect_after=0)
    ok(fouls(m,k)==['protected_recovery'] and last(m,'foul')['actor']=='B0' and w['foul']=='protected_recovery' and w['avoidability']=={'last_lawful_ms':None} and col['shock_a']>.05 and 490<col['t_ms']-t0<510,'LEAD 3: running three metres into a carrier who was protected throughout is penalised. Being out of reach at the start was not a lawful approach')
    ok(not m.c3_ch and ('B0','A0') not in m.c3_ok,'LEAD 3: and no lawful time was ever recorded for him against that carrier')
    m,k,col,w,t0=onto(2.5,protect_after=20);a=w['avoidability']
    ok(not fouls(m,k) and w['not_sanctioned']=='no_time_to_avoid' and a['changed_to']=='protected_recovery' and a['gap_then_m']<a['stopping_gap_m'] and near(a['stopping_gap_m'],a['approach_then_mps']*.3+a['approach_then_mps']**2/27,2e-2) and a['change_seen_ms']-t0<=30,'the positive case is kept: the carrier became protected when the defender was already inside his own reaction and braking distance, so the hit is recorded and not penalised')
    m,k,col,w,t0=onto(4.2,protect_after=20);a=w['avoidability']
    ok(fouls(m,k)==['protected_recovery'] and a['gap_then_m']>a['stopping_gap_m'] and a['elapsed_ms']<a['stopping_time_ms'],'four metres out at 6 m/s he could have stopped (3.1 m needed) and is penalised, although less than his reaction time plus braking time had passed: the test is the distance he had, not the time alone')
    def passed(gap,v=8.0):
        """The carrier A0 has his back to the chasing B0 and passes the ball away; B0 runs into his back."""
        m=kb();m.c3_reckless={'B0'};A=kput(m,'A0',(50,50));A.facing=(1.0,0.0);kgive(m,'A0');B=kput(m,'B0',(50-A.radius-m.s.players['B0'].radius-gap-v*.02,50),(v,0));B.facing=(1.0,0.0);ktop(m,'B0',v);k=len(m.e.log)
        ktick(m,{'B0':(99,50)},20);m.e.release('A0',(0.0,30.0,3.0),'pass');m.c3_reconcile();rel=m.s.now
        for i in range(40):
            ktick(m,{'B0':(99,50)},50)
            if count(m,'c3_collision',k):break
        return m,k,[r for r in last(m,'c3_collision')['responsibility'] if r['player']=='B0'][0],rel
    m,k,w,rel=passed(.5);a=w['avoidability'];ok(not fouls(m,k) and w['kind']=='block' and w['not_sanctioned']=='no_time_to_avoid' and a['changed_to']=='blindside' and a['change_seen_ms']==rel and a['last_lawful_ms']<rel,'a carrier with his back turned who passes half a metre ahead of the tackler: the change is witnessed at the release, and the hit is not penalised')
    m,k,w,rel=passed(6.0);a=w['avoidability'];ok(fouls(m,k)==['blindside'] and a['gap_then_m']>a['stopping_gap_m'] and a['change_seen_ms']==rel,'the same pass six metres ahead of him: he had room to stop, ran on into the man\'s back, and is penalised')
    m,A,B=rear(v=20.0,facing=(-1.0,0.0),gap=2.0);k=len(m.e.log);step1(m,{'B0':(99,50)},20);A.facing=(1.0,0.0);m.c3_ch[('B0','A0')]=(m.s.now-5000,20.0,'blindside',m.s.now-5100,1.6,0.0,0.0);m.c3_ok.pop(('B0','A0'),None);ktick(m,{'B0':(99,50)},180)
    ok(fouls(m,k)==['blindside'],'the excuse lasts only for the reaction and braking time after the change: an old change does not cover a new approach')
    def round_him(radial,v=10.0):
        """B0 runs into the non-carrier A0, who stands facing +x, and meets him 110 degrees round from his front (behind the blindside
        line at 104.5). radial: he comes straight in along that bearing, behind the line all the way. Otherwise he comes across from
        a point 95 degrees round, in front of the line when the interval of the contact begins."""
        m=kb();m.c3_reckless={'B0'};loose(m);A=kput(m,'A0',(50,50));A.facing=(1.0,0.0);B=m.s.players['B0'];R=A.radius+B.radius;c=(math.cos(math.radians(110)),math.sin(math.radians(110)))
        st=(c[0]*(R+3.0),c[1]*(R+3.0)) if radial else (math.cos(math.radians(95))*(R+.5),math.sin(math.radians(95))*(R+.5));d=CORE.geometry.unit(c[0]*R-st[0],c[1]*R-st[1])
        kput(m,'B0',(50+st[0],50+st[1]),(d[0]*v,d[1]*v));ktop(m,'B0',v);k=len(m.e.log);tg=(50+st[0]+d[0]*40,50+st[1]+d[1]*40);pre=m.e.contact_legal(B,A,'block',reach=False)[1]
        for i in range(8):
            ktick(m,{'B0':tg},100)
            if count(m,'c3_collision',k):break
        return m,k,pre,[r for r in last(m,'c3_collision')['responsibility'] if r['player']=='B0'][0]
    m,k,pre,w=round_him(False);a=w['avoidability']
    ok(pre=='legal' and w['classification']=='blindside' and not fouls(m,k) and w['not_sanctioned']=='no_time_to_avoid' and a['last_lawful_ms']==a['state_at_ms']==1000 and 1000<a['change_seen_ms']<=1100 and a['gap_then_m']<a['stopping_gap_m'],'FOUND: two athletes move round each other inside one interval, so that a contact lawful when the interval began is from behind when it happens. That change is witnessed at the contact, with the state at the start of the interval, and he had no room to stop')
    m,k,pre,w=round_him(True);ok(pre=='blindside' and fouls(m,k)==['blindside'] and w['avoidability']=={'last_lawful_ms':None},'the same contact reached by coming straight in from behind the line is penalised: it was never lawful')
    # ---- 20. the distance test cannot hide a protected carrier from the hold either (found while repairing LEAD 3) ----
    def skim(protected,inside=.6):
        """B0 runs past the stationary carrier on a line that comes inside reach by `inside` metres and leaves it again, never touching him."""
        m=kb();m.c3_reckless={'B0'};A=kput(m,'A0',(50,50));A.facing=(-1.0,0.0);kgive(m,'A0');B=m.s.players['B0'];R=A.radius+B.radius+.7*(A.a.reach+B.a.reach)
        kput(m,'B0',(49,50+R-inside),(8,0));ktop(m,'B0',8.0);k=len(m.e.log)
        for i in range(40):
            if protected:m.s.award_spot=(m.s.ball.x,m.s.ball.y);m.s.award_available=m.s.now
            ktick(m,{'B0':(99,B.y)},10)
        return m,k
    m,k=skim(True);m2,k2=skim(False)
    ok(not count(m,'c3_hold_start',k) and not count(m,'engagement',k) and not fouls(m,k) and count(m2,'c3_hold_start',k2)==1,'a defender who passes within reach of a protected carrier and out again starts no hold, not even for the last instant before he leaves reach; the same run past an unprotected carrier does')

    # ================= C3b: around the tackle =================
    def lastev(m,name,k=0):return next(r for r in reversed(m.e.log[k:]) if r['event']==name)
    def evs(m,name,k=0):return [r for r in m.e.log[k:] if r['event']==name]
    def wvec(m,q,now=None):
        fresh,(x,y,_,src)=m.c3_driven(q,m.s.now if now is None else now)
        return (x+sum(e[1] for e in fresh),y+sum(e[2] for e in fresh))
    G=9.81;SL=C3CAL['slide_friction']*G
    # ---- 21. the motion witness follows the motion (the Lead's C3a3 finding) ----
    m=kb();A=kput(m,'A0',(50,50),(14,0));A.a.decision_speed=.2;A.a.braking=10.0;kput(m,'B0',(48,50));kgive(m,'A0');m.c3_push(A,14.0,0.0,'B0',m.s.now);k=len(m.e.log)
    ok(m.e.tackle('B0','A0',witnessed=True) and A.posture=='grounded' and near(A.vx,14.0) and near(wvec(m,A)[0],14.0),'LEAD: a tackled carrier is no longer stopped dead by the tackle routine: he keeps the velocity he had, and the record of what was imposed on him still describes real motion')
    worst=0.0;seen=[]
    for i in range(30):
        v0=A.vx;ktick(m,{},100);w=wvec(m,A);worst=max(worst,math.hypot(*w)-max(0.0,v0));seen.append((A.vx,w[0]))
    ok(worst<=1e-9 and seen[2][1]>1 and A.posture=='upright' and A.vx==0 and wvec(m,A)==(0.0,0.0) and getattr(A,'c3_ext',None) is None,'LEAD: while he slides the record is never larger than the velocity he had at the start of the interval, and when he has stopped it is gone')
    def after_stop(push):
        """A0 has (or has not) an old 14 m/s push on record, is at rest, and then runs at 6 m/s into the back of B0."""
        m=kb();m.c3_reckless={'A0'};loose(m);A=kput(m,'A0',(50,50));A.a.decision_speed=.2;A.a.braking=10.0
        if push:m.c3_push(A,14.0,0.0,'B5',m.s.now)
        ktick(m,{},10);kput(m,'A0',(50,50),(6,0));A.facing=(1.0,0.0);B=kput(m,'B0',(50+2*A.radius+.04,50));B.facing=(1.0,0.0);ktop(m,'A0',6.0);k=len(m.e.log);ktick(m,{'A0':(99,50)},10)
        return fouls(m,k),[r for r in last(m,'c3_collision')['responsibility'] if r['player']=='A0'][0]
    f1,w1=after_stop(True);f0,w0=after_stop(False)
    ok(f1==f0==['blindside'] and w1['driven_approach_mps']==0 and near(w1['voluntary_approach_mps'],w0['voluntary_approach_mps']) and 'not_sanctioned' not in w1,'LEAD: an impulse that was cancelled (he was brought to rest inside his reaction time) cannot excuse a fresh run of his own: the same foul as with no record at all')
    m=kb();A=kput(m,'A0',(50,50),(5,0));m.c3_push(A,4.0,0.0,'B5',m.s.now);m.c3_settle(A,m.s.now);a1=wvec(m,A);A.vx=3.0;m.c3_settle(A,m.s.now);a2=wvec(m,A);A.vx=5.0;m.c3_settle(A,m.s.now);a3=wvec(m,A)
    ok(near(a1[0],4.0) and near(a2[0],3.0) and near(a3[0],3.0),'the record is only ever reduced: velocity he lost and then made again himself is his own')
    A.vx=-2.0;A.vy=3.0;m.c3_settle(A,m.s.now);ok(getattr(A,'c3_ext',1) is None,'a record whose direction he is no longer moving in at all is dropped')
    m=kb();A=kput(m,'A0',(50,50),(10,0));A.a.decision_speed=.2;A.a.braking=10.0;m.c3_push(A,14.0,0.0,'B5',1000.0);m.c3_settle(A,1800.0);w8=wvec(m,A,1800.0);A.vx=5.0;m.c3_settle(A,1800.0);w5=wvec(m,A,1800.0)
    ok(near(w8[0],8.0) and near(w5[0],5.0) and near(wvec(m,A,1900.0)[0],4.0),'FOUND with the Lead\'s probe: the comparison is with what is left of the record now (14 less 0.6 s of braking is 8, which 10 m/s of real velocity still covers), not with the figure first stored; my first version cut it to 10 and then took the braking off again')
    m=kb();A=kput(m,'A0',(50,50),(6,8));m.c3_push(A,3.0,4.0,'B5',m.s.now);m.c3_settle(A,m.s.now);ok(near(wvec(m,A)[0],3.0) and near(wvec(m,A)[1],4.0),'a record that still describes real motion is left alone')
    m,k,w=shoved();ok(w['not_sanctioned']=='carried_by_another_contact' and near(w['driven_approach_mps'],w['own_approach_mps'],1e-3),'a real surviving push still excuses (the C3a3 case, unchanged with C3b on)')
    m=kb();A=kput(m,'A0',(30,40),(3,4));m.c3_push(A,3.0,4.0,'B5',m.s.now);m.e.exchange_ends();w=wvec(m,A)
    ok(near(A.vx,-3.0) and near(w[0],-3.0) and near(w[1],-4.0),'at a change of ends the record is turned round with the velocity it describes')
    # ---- 22. going down, sliding and getting up ----
    def tackled(v,bal=.68,cal=None,**over):
        m=kb(cal,**over);A=kput(m,'A0',(40,50),(v,0));A.a.balance=bal;kput(m,'B0',(38.5,50),(v,0));kgive(m,'A0');k=len(m.e.log);t0=m.s.now;m.e.tackle('B0','A0',witnessed=True);return m,A,k,t0
    m,A,k,t0=tackled(12.0);d=lastev(m,'c3_down',k)['data'];sl=(12.0-1.0)/SL;ri=.8*(1.5-.68)
    ok(near(d['slide_ms'],1000*sl,1e-3) and near(d['rise_ms'],1000*ri,1e-3) and d['upright_at']==t0+math.ceil(1000*(sl+ri)) and A.next_action==d['upright_at'] and A.tackled_until==d['upright_at'],'get-up is modelled: slide until he is slower than 1 m/s at friction 0.8 g, then rise for 0.8 s x (1.5 - balance); the instant is known when he goes down')
    x0=A.x;ktick(m,{},500);ok(near(A.vx,12.0-SL*.5,1e-6) and near(A.x-x0,12.0*.5-.5*SL*.25,1e-3) and A.posture=='grounded','he slides: velocity falls at 0.8 g and he travels accordingly')
    ktick(m,{},d['upright_at']-m.s.now);g1=A.posture;n1=m.s.now;ktick(m,{},1);u=lastev(m,'c3_upright',k)
    ok(g1=='grounded' and n1==d['upright_at'] and u['t_ms']==d['upright_at'] and u['data']['down_ms']==d['upright_at']-t0 and A.posture=='upright' and near(A.x-x0,12.0**2/(2*SL),1e-2),'an interval ends exactly when his get-up does, and he is upright from that millisecond, not from the next 100 ms; the actual time down is logged; he has slid v squared over 2 x 0.8 g')
    m,A,k,t0=tackled(0.0);d0=lastev(m,'c3_down',k)['data'];m,A,k,t0=tackled(0.0,bal=1.0);d1=lastev(m,'c3_down',k)['data'];m,A,k,t0=tackled(0.0,bal=0.0);d2=lastev(m,'c3_down',k)['data']
    ok(d0['slide_ms']==0 and near(d0['rise_ms'],656.0) and near(d1['rise_ms'],400.0) and near(d2['rise_ms'],1200.0),'standing still there is no slide; rising takes 0.4 s at balance 1 and 1.2 s at balance 0')
    m,A,k,t0=tackled(12.0,cal={'c3b':0});ok(A.vx==0 and A.next_action==t0+800 and not evs(m,'c3_down',k),'with c3b off the tackle is the C3a3 one: stopped dead, up after a fixed 0.8 s')
    m=kb();m.c3_reckless={'A0','B0'};loose(m);A=kput(m,'A0',(50,50),(12.5,0));B=kput(m,'B0',(50+A.radius+m.s.players['B0'].radius+.2,50),(-12.5,0));ktop(m,'A0',12.5);ktop(m,'B0',12.5);k=len(m.e.log);ktick(m,{'A0':(99,50),'B0':(1,50)},100)
    ds=evs(m,'c3_down',k);ok(len(ds)==2 and all(x['data']['rise_ms']==656.0 for x in ds) and A.posture==B.posture=='grounded' and A.next_action==ds[0]['data']['upright_at'],'anyone who goes down, a tackler or a blocker included, gets the same model')
    m,A,k,t0=tackled(12.0);m.e.grounded('A0');ok(len(evs(m,'c3_down',k))==1 and A.down_at==t0,'an athlete already on the ground is not put down a second time')
    # ---- 23. recovery: grace for every lawful holder, reaction to the award, and the compliance record ----
    def downed(extra=(),cal=None,**over):
        """Carrier A0 stands at (40,50) with B0 and B1 holding him at grip 0.8 from 1.5 m, and goes down under their hold: a first
        tackle and a live recovery. extra: other athletes to place, as (id, (x, y), grip or None)."""
        m=kb(cal,**over);m.c3_fix_drive=-1.0;m.assume['grip_gain_per_s']=0.0;m.assume['grip_resist_per_s']=0.0;A=kput(m,'A0',(40,50));kgive(m,'A0');ids=['B0','B1']
        kput(m,'B0',(38.9,51.0));kput(m,'B1',(38.9,49.0))
        for pid,xy,g in extra:
            kput(m,pid,xy)
            if g is not None:ids.append(pid)
        ktick(m,{},10)
        for pid in ids:m.c3_holds[(pid,'A0')]['g']=dict([(e[0],e[2]) for e in extra]).get(pid,.8)
        load(A,{('hold','B0'):[1.5,True]},m.s.now);m.c3_holds[('B0','A0')]['g']=.8;m.c3_fix_drive=1.0;k=len(m.e.log);ktick(m,{},10);m.c3_fix_drive=None;return m,k
    m,k=downed(extra=[('B2',(40.0,51.6),.05)]);s=m.s;rc=lastev(m,'recovery_compliance',k)['data'];g=lastev(m,'c3_grounding',k)['data']
    ok(s.recovery is not None and g['credited']=='B0' and rc['holders_with_grace']==['B1'] and {'B0','B1'}<=s.recovery['committed'] and 'B2' not in s.recovery['committed'] and [h['player'] for h in g['holders']]==['B0','B1','B2'],'every defender with a material lawful hold at the grounding is owed time to disengage, not only the one credited; a defender merely within reach (grip 0.05) is a bystander')
    ok(all(s.players[q].next_decision==s.recovery['started']+300 for q in rc['reaction_ms']) and len(rc['reaction_ms'])==11 and set(rc['reaction_ms'].values())=={300},'every opponent responds to the award after his own reaction time (0.3 s here), which is disclosed in the log')
    sx,sy=s.recovery['spot'];B1=s.players['B1'];B2=s.players['B2']
    def step_in(m,pid,k):
        """The named defender walks to 1.2 m from the award spot (his body inside the disc), then away again."""
        s=m.s;sx,sy=s.recovery['spot'];q=s.players[pid];ux,uy=CORE.geometry.unit(q.x-sx,q.y-sy);ktop(m,pid,4.0)
        for i in range(12):
            if not s.recovery:break
            ktick(m,{pid:(sx+ux*1.2,sy+uy*1.2)},50)
        for i in range(30):
            if not s.recovery:break
            ktick(m,{pid:(sx+ux*4,sy+uy*4)},50)
        return [r['data'] for r in m.e.log[k:] if r['event'] in ('recovery_obstruction','recovery_cleared') and r['data']['player']==pid]
    r1=step_in(m,'B1',k)
    ok(not fouls(m,k) and len(r1)==2 and r1[0]['unavoidable'] is False and 'entered_late' not in r1[0] and r1[1]['had_grace'] and r1[1]['attributable_delay_ms']==0 and 0<r1[1]['necessary_m']<.5 and r1[1]['took_ms']<=r1[1]['allowed_ms'],'a holder with grace whose body comes into the disc is given the time physically needed to leave, leaves inside it, and the record shows necessary movement, time taken and no delay of his own')
    m,k=downed(extra=[('B2',(40.0,51.6),.05)]);r2=step_in(m,'B2',k)
    ok(fouls(m,k)==['recovery_interference'] and r2[0]['entered_late'] and lastev(m,'foul',k)['data']['actor']=='B2','the bystander who does the same is interfering at once: being near the tackle earns nothing')
    m,k=downed();s=m.s;sx,sy=s.recovery['spot'];B1=s.players['B1'];ux,uy=CORE.geometry.unit(B1.x-sx,B1.y-sy);ktop(m,'B1',4.0);s.players['A0'].next_action=s.now+60000 #the carrier is kept down so that nobody picks the ball up
    for i in range(60):
        if not s.recovery:break
        ktick(m,{'B1':(sx+ux*1.2,sy+uy*1.2)},50)
    ob=[r['data'] for r in m.e.log[k:] if r['event']=='recovery_obstruction'][0]
    ok(fouls(m,k)==['recovery_interference'] and lastev(m,'foul',k)['t_ms']>ob['clear_by'] and lastev(m,'foul',k)['data']['actor']=='B1','grace is time to leave, not leave to stay: a holder who is still in the disc after the time he needed is interfering')
    m,k=downed(cal={'recovery_react':0});s=m.s;ok(not lastev(m,'recovery_compliance',k)['data']['reaction_ms'],'with recovery_react off nobody\'s decision time is touched (the C2 behaviour)')
    m,k=downed(cal={'c3b':0});ok(not evs(m,'recovery_compliance',k) and m.s.recovery['committed']=={'B0'},'with c3b off only the credited tackler has grace, as in C3a3')
    # ---- 24. bodies are solid during a live recovery: blocking outside the disc is legal, running into a man in the disc is not ----
    def recovery_hit(target_xy,from_dx,cal=None,attacker_hits=False):
        """After the first tackle of section 23: A1 stands at target_xy facing -x; B2 runs into him from from_dx metres on the -x side
        (or, attacker_hits, A1 runs into the standing B2)."""
        m,k=downed(cal=cal);s=m.s;sx,sy=s.recovery['spot'];m.c3_reckless={'A1','B2'};A1=kput(m,'A1',(sx+target_xy[0],sy+target_xy[1]));A1.facing=(-1.0,0.0)
        B2=kput(m,'B2',(A1.x-from_dx,A1.y),(0,0) if attacker_hits else (6,0));B2.facing=(1.0,0.0)
        if attacker_hits:kput(m,'A1',(A1.x,A1.y),(-6,0));ktop(m,'A1',6.0);tg={'A1':(B2.x-30,B2.y)}
        else:ktop(m,'B2',6.0);tg={'B2':(A1.x+30,A1.y)}
        k=len(m.e.log)
        for i in range(8):
            ktick(m,tg,50)
            if evs(m,'c3_collision',k) or not s.recovery:break
        return m,k,s.recovery is not None
    m,k,live=recovery_hit((0.0,6.0),1.5);col=evs(m,'c3_collision',k)
    ok(len(col)==1 and not fouls(m,k) and live and [r['classification'] for r in col[0]['data']['responsibility'] if r['player']=='B2']==['legal'],'six metres from the award spot a defender runs into an attacker who is facing him: a real collision, lawful, and the recovery goes on')
    m,k,live=recovery_hit((0.0,6.0),1.5,cal={'c3b':0});ok(not evs(m,'c3_collision',k) and not fouls(m,k),'with c3b off they pass through each other during a recovery, as in C3a3')
    m,k,live=recovery_hit((0.0,1.3),1.5);col=evs(m,'c3_collision',k);w=[r for r in col[0]['data']['responsibility'] if r['player']=='B2'][0]
    ok(fouls(m,k)==['protected_recovery'] and w['classification']=='protected_recovery' and w['foul']=='protected_recovery' and w['avoidability']=={'last_lawful_ms':None} and lastev(m,'foul',k)['data']['actor']=='B2','a defender who runs into an attacker whose body is in the disc has obstructed the recovery: penalised at the collision, and a run that was never lawful has no excuse')
    m,k,live=recovery_hit((0.0,1.3),1.5,attacker_hits=True);col=evs(m,'c3_collision',k)
    ok(len(col)==1 and not fouls(m,k) and live,'the recovering side may run into a defender there: the protection is theirs')
    def from_rest(gap,cal=None):
        """B0 stands `gap` metres behind the carrier A0 and has just set off at him. 10 ms later A0 becomes a protected carrier."""
        m=kb(cal);m.c3_reckless={'B0'};A=kput(m,'A0',(50,50));A.facing=(1.0,0.0);kgive(m,'A0');B=kput(m,'B0',(50-A.radius-m.s.players['B0'].radius-gap,50));B.facing=(1.0,0.0);ktop(m,'B0',8.0);s=m.s;k=len(m.e.log);t0=s.now
        ktick(m,{'B0':(99,50)},10);s.award_spot=(s.ball.x,s.ball.y);s.award_available=s.now
        while s.now<t0+900 and not count(m,'c3_collision',k):ktick(m,{'B0':(99,50)},10)
        return m,k,[r for r in last(m,'c3_collision')['responsibility'] if r['player']=='B0'][0],last(m,'c3_collision')['t_ms']-t0-10
    m,k,w,at=from_rest(.3);a=w['avoidability']
    ok(not fouls(m,k) and w['material'] and w['not_sanctioned']=='no_time_to_avoid' and 'within_reaction_time' not in a and at<300 and a['approach_growing_mps2']>5 and a['gap_then_m']<a['stopping_gap_m'] and w['own_approach_mps']>a['approach_then_mps']+1,'a defender already accelerating at the carrier when he became protected, who reaches him 0.27 s later, could not have stopped: his speed at the change was almost nothing, but it was growing, and carrying on like that for his reaction time covers the gap. He is not penalised')
    m,k,w,at=from_rest(.3,{'c3b':0});ok(fouls(m,k)==['protected_recovery'],'the C3a3 rule judged only his speed at the change and penalised him (unchanged with c3b off)')
    m,k,w,at=from_rest(.5);a=w['avoidability']
    ok(not fouls(m,k) and at>300 and 'within_reaction_time' not in a and a['approach_growing_mps2']>5 and a['gap_then_m']<a['stopping_gap_m'] and near(a['stopping_gap_m'],(a['approach_then_mps']-a['target_receding_then_mps'])*.3+.5*a['approach_growing_mps2']*.09+(a['approach_then_mps']+a['approach_growing_mps2']*.3-a['target_receding_then_mps'])**2/27,5e-2),'just after his reaction time the test is still the distance he needed, counting the speed he was gaining when the change came: carried on for 0.3 s and then braking, he could not have stopped in half a metre')
    m,k,w,at=from_rest(1.2);a=w['avoidability'];ok(fouls(m,k)==['protected_recovery'] and at>300 and a['gap_then_m']>a['stopping_gap_m'],'from 1.2 m he had room to stop on the same reckoning, ran on, and is penalised')
    def fresh(c3b=1,scheduled=True):
        """LEAD (C3b1 audit, correction 1). B0 stands still 5 cm behind the carrier A0. A0 passes the ball away at 1010 ms. B0, who had a
        decision already due at 1110 ms, then sets off at A0 and runs into his back. Decisions are not forced: his own schedule is kept."""
        m=kb({'c3b':c3b});m.c3_reckless={'B0'};A=kput(m,'A0',(50,50));A.facing=(1.0,0.0);kgive(m,'A0');B=kput(m,'B0',(50-A.radius-m.s.players['B0'].radius-.05,50));B.facing=(1.0,0.0);ktop(m,'B0',8.0);B.next_decision=1110
        def go(target):
            if not scheduled:B.next_decision=0
            full={q.id:(q.x,q.y) for q in m.active_field()};full['B0']=target;m.c3_step(10,full,scripted=True)
            if m.s.ball.carrier:m.e.follow_carrier()
        go((B.x,B.y));at=m.s.now;still=B.vx==0;m.e.release('A0',(0.0,30.0,3.0),'pass');k=len(m.e.log)
        for i in range(80):
            go((99.0,50.0))
            if count(m,'c3_collision',k):break
        return m,k,still,[r for r in last(m,'c3_collision')['responsibility'] if r['player']=='B0'][0],last(m,'c3_collision')['t_ms']-at
    m,k,still,w,dt_=fresh();a=w['avoidability']
    ok(still and fouls(m,k)==['blindside'] and last(m,'foul')['actor']=='B0' and w['foul']=='blindside' and 0<dt_<300 and a['approach_then_mps']==0 and a['approach_growing_mps2']==0 and a['stopping_gap_m']==0 and near(w['voluntary_approach_mps'],w['own_approach_mps']) and 'not_sanctioned' not in w,'LEAD: reaction time delays a response; it is not leave to begin an approach. Standing still at the change, he set off afterwards and hit the passer from behind 0.2 s later: nothing was committed before the change, the stopping gap is zero, and he is penalised')
    m,k,still,w,dt_=fresh(scheduled=False);ok(fouls(m,k)==['blindside'] and w['avoidability']['stopping_gap_m']==0 and dt_<300,'LEAD: the same when he sets off at once after the change')
    m,k,still,w,dt_=fresh(c3b=0);ok(fouls(m,k)==['blindside'],'and with c3b off, as C3a3 did')
    # ---- 25. containment: a holder may hold the carrier up without driving him down; his zone count runs ----
    def zone_hold(g=.8,n=1,count_ms=0,cal=None,contain=None,descend=None,v=6.0,strength=None,tackles=0):
        """Carrier A0 runs at v across the Keeper Zone his team attacks, 10 m from the goal, with n defenders alongside holding him
        at grip g. count_ms: zone time he has already used. contain / descend: force the choice (None: the controllers decide)."""
        m=kb(cal,zone_marking=True,zone_inbound=True);s=m.s;j=s.own_zone('B');gx=0.0 if j==0 else 100.0;x=gx+(10.0 if j==0 else -10.0)
        A=kput(m,'A0',(x,44.0),(0,v));ktop(m,'A0',max(v,.1),True);kgive(m,'A0');ds=['B0','B1'][:n]
        for i,d in enumerate(ds):
            D=kput(m,d,(x+(1.0 if i==0 else -1.0),42.9),(0,v));ktop(m,d,max(v,.1))
            if strength is not None:D.a.strength=strength
        m.c3_fix_contain=contain;m.c3_fix_descent=descend;s.tackle_count=tackles
        ktick(m,{'A0':(x,99.0),**{d:(x,99.0) for d in ds}},10)
        for d in ds:m.c3_holds[(d,'A0')]['g']=g
        A.zone_ms[j]=count_ms;return m,A,j,x,ds
    def zrun(m,x,ds,ms,stop=lambda m:False):
        k=len(m.e.log);t0=m.s.now
        while m.s.now<t0+ms and m.s.ball.carrier=='A0' and not stop(m):
            A=m.s.players['A0'];ktick(m,{'A0':(x,99.0),**{d:(A.x,A.y) for d in ds}},50)
        return k
    m,A,j,x,ds=zone_hold(contain=False,descend=False);k=zrun(m,x,ds,2000);gd=lastev(m,'c3_grounding',k)['data'];t_drive=gd['t_ms']
    ok(gd['manner']=='defence_driven' and gd['cls']=='tackle_under_hold' and gd['containing']==[] and m.s.tackle_count==1,'a holder who drives brings the carrier down: a defence-driven counted tackle')
    m,A,j,x,ds=zone_hold(contain=True,descend=False);z0=A.zone_ms[j];t0=m.s.now;k=zrun(m,x,ds,2000);h=m.c3_holds.get(('B0','A0'))
    ok(m.s.ball.carrier=='A0' and A.posture=='upright' and not evs(m,'c3_grounding',k) and h is not None and h['mode']=='contain' and h['g']>=.3 and m.s.now-t0>t_drive-1000+500 and m.c3_bal(A)<.5,'a holder who contains stays with him and does not drive: the carrier is still up, still held, long after the driven tackle would have come')
    ok(near(A.zone_ms[j]-z0,m.s.now-t0,1e-9) and near(h['contain_ms'],m.s.now-t0,2e-2) and any(r['event']=='c3_containment' for r in m.e.log),'his zone count runs all the while (an upright hold does not pause it), and the time contained is recorded on the hold')
    m,A,j,x,ds=zone_hold(count_ms=3500);B=m.s.players['B0'];c1=m.c3_contain(B,A);A.zone_ms[j]=2500;c2=m.c3_contain(B,A);A.zone_ms[j]=3500;m.s.tackle_count=1;c3=m.c3_contain(B,A);m.s.tackle_count=0
    kput(m,'A0',(50,50));c4=m.c3_contain(B,A);m.assume['containment_window_s']=0.0;kput(m,'A0',(x,44.0));c5=m.c3_contain(B,A)
    ok((c1,c2,c3,c4,c5)==(True,False,False,False,False),'CONTROLLER: he contains when a tackle would only be the attack\'s first and the carrier\'s zone time runs out within the window (1.5 s left of 2.0); not with 2.5 s left, not when the tackle would be the second, not outside the attacked zone, not with the window at zero')
    m,A,j,x,ds=zone_hold(count_ms=4000,descend=False,v=3.0);k=zrun(m,x,ds,1500);e=evs(m,'attacking_zone_expiry',k)
    ok(len(e)==1 and e[0]['data']['player']=='A0' and e[0]['data']['exit_class']=='carrier_contained' and e[0]['data']['holders'][0]['player']=='B0' and e[0]['data']['holders'][0]['containing'] and m.stats['containment_expiries']==1 and fouls(m,k)==['zone_expiry'] and m.s.owner=='B' and not evs(m,'c3_grounding',k),'containment to expiry: the controller holds him up through his last second, the zone time runs out, the defence wins the ball, and the expiry is logged as containment-induced with its holders')
    m,A,j,x,ds=zone_hold(count_ms=4000,contain=False,descend=False,g=0.0,v=3.0);m.c3_holds.clear();kput(m,'B0',(60,60));k=zrun(m,x,[],1500);e=evs(m,'attacking_zone_expiry',k)
    ok(len(e)==1 and e[0]['data']['exit_class']=='carrier_free' and e[0]['data']['holders']==[] and m.stats['containment_expiries']==0,'an unheld carrier who simply stays too long is logged apart from that')
    # ---- 26. controlled descent: attempted under a hold, resisted within the hold's capacity, never guaranteed ----
    m,A,j,x,ds=zone_hold(contain=False,descend=True);k=zrun(m,x,ds,2000);gd=lastev(m,'c3_grounding',k)['data'];de=lastev(m,'c3_descent_end',k)['data']
    ok(gd['manner']=='carrier_descent_under_hold' and gd['descent_attempted'] and gd['own_descent_load']>.1 and gd['cls']=='tackle_under_hold' and gd['t_ms']<t_drive and de['cause']=='grounded' and len(evs(m,'c3_descent_start',k))==1,'a carrier who goes to ground under a driving hold is down sooner than the hold alone would put him; it is logged as his descent, with the part of the load that was his own')
    ok(m.s.tackle_count==1 and evs(m,'tackle_count',k)[0]['data']['procedure']=='zone_inbound' and m.s.reconstruction is not None and m.s.reconstruction['zone']==j and m.s.owner=='A','it is not free: it costs the count, and in the attacked zone the goal-line inbound and a full reconstruction')
    m,A,j,x,ds=zone_hold(contain=False,descend=True,tackles=1);k=zrun(m,x,ds,2000);ok(lastev(m,'c3_grounding',k)['data']['manner']=='carrier_descent_under_hold' and m.s.owner=='B' and evs(m,'tackle_count',k)[0]['data']['procedure']=='turnover','with one tackle already counted, going to ground is the second tackle and a turnover')
    m,A,j,x,ds=zone_hold(contain=True,descend=True,n=2);t0=m.s.now;k=zrun(m,x,ds,2000);st=lastev(m,'c3_descent_start',k)['data']
    ok(m.s.ball.carrier=='A0' and A.posture=='upright' and not evs(m,'c3_grounding',k) and m.c3_descent['A0']['support']==1.0 and A.bal_src.get(('descent','A0',True),0.0)==0.0 and len(st['holders'])==2,'two containing holders can carry his whole weight: he tries to go down and is held up. Descent is not guaranteed by intent')
    m,A,j,x,ds=zone_hold(contain=True,descend=True,g=.5,strength=.2);k=zrun(m,x,ds,3000);gd=lastev(m,'c3_grounding',k)['data'];sup=.5*2500*.7/(A.a.mass*G)
    ok(gd['manner']=='carrier_descent_under_hold' and gd['containing']==['B0'] and 0<sup<1 and gd['t_ms']-lastev(m,'c3_descent_start',k)['t_ms']>500,'one weaker containing holder carries only part of his weight: he goes down, but more slowly than his own 0.5 s')
    m,A,j,x,ds=zone_hold(contain=True,descend=True,g=.5,strength=.2);k=len(m.e.log);ktick(m,{'A0':(x,99.0),'B0':(x,99.0)},100);own=A.bal_src[('descent','A0',True)]
    ok(near(own,(1-sup)/.5*.1,5e-2) and m.c3_rate(A)==0.0,'the rate is (1 - supported share of his weight) / descent_time_s, and he does not recover balance while he is letting himself down')
    m.c3_holds[('B0','A0')]['g']=.1;m.assume['grip_gain_per_s']=0.0;ktick(m,{'A0':(x,99.0),'B0':(x,99.0)},20);de=lastev(m,'c3_descent_end',k)['data']
    ok(de['cause']=='hold_lost' and 'A0' not in m.c3_descent and m.stats['c3_descents_failed']==1 and m.c3_rate(A)>0,'if the material hold is lost the attempt ends there, logged as a failed descent, and he recovers his balance again')
    m,A,j,x,ds=zone_hold(contain=False,descend=True,g=.1);m.assume['grip_gain_per_s']=0.0;k=zrun(m,x,ds,500);ok(not evs(m,'c3_descent_start',k),'under a token grip there is no hold to go down under: no attempt begins')
    m,A,j,x,ds=zone_hold(contain=False,descend=True);m.assume['grip_gain_per_s']=0.0;m.assume['grip_resist_per_s']=0.0;ktick(m,{'A0':(x,99.0),'B0':(x,99.0)},10);m.c3_holds[('B0','A0')]['g']=.29;load(A,{('descent','A0'):[1.5,True]},m.s.now);k=len(m.e.log);ktick(m,{'A0':(x,99.0),'B0':(x,99.0)},10);gd=lastev(m,'c3_grounding',k)['data']
    ok(gd['manner']=='unassisted_grounding' and gd['own_descent_load']>1 and not gd['descent_attempted'] and gd['cls']=='carrier_grounded_not_a_tackle' and not evs(m,'tackle_count',k) and m.s.tackle_count==0 and m.s.ball.carrier is None,'going to ground with no material hold on him (grip 0.29) is unassisted, however much of the load was his own: not a tackle, no count, the existing forced release')
    m,A,j,x,ds=zone_hold(count_ms=3500);c1=m.c3_descend(A);A.zone_ms[j]=2500;c2=m.c3_descend(A);A.zone_ms[j]=3500;m.s.tackle_count=1;c3=m.c3_descend(A);m.s.tackle_count=0;m.assume['descent_window_s']=0.0;c5=m.c3_descend(A)
    ok((c1,c2,c3,c5)==(True,False,False,False),'CONTROLLER: a held carrier tries to go down when it would be his team\'s first tackle and his zone time runs out within the window; not otherwise')
    m,A,j,x,ds=zone_hold(count_ms=3200,g=.5,strength=.2,v=3.0);k=zrun(m,x,ds,2500);names=[r['event'] for r in m.e.log[k:] if r['event'] in ('c3_containment','c3_descent_start','c3_grounding','attacking_zone_expiry')]
    ok(names[:2]==['c3_containment','c3_descent_start'] and names[-1]=='c3_grounding' and lastev(m,'c3_grounding',k)['data']['manner']=='carrier_descent_under_hold' and m.s.owner=='A' and m.s.tackle_count==1,'the contest with both controllers on and a weak holder: he is contained, tries to go down, and gets down before his time runs out, keeping the ball at the cost of the count')
    m,A,j,x,ds=zone_hold(count_ms=3200,v=3.0);k=zrun(m,x,ds,2500);names=[r['event'] for r in m.e.log[k:] if r['event'] in ('c3_containment','c3_descent_start','c3_grounding','attacking_zone_expiry')]
    ok(names==['c3_containment','c3_descent_start','attacking_zone_expiry'] and m.s.owner=='B' and lastev(m,'attacking_zone_expiry',k)['data']['exit_class']=='carrier_contained','and with a strong holder (his grip carries the carrier\'s whole weight) he is held up until his time runs out: the defence wins the ball')
    # ---- 27. off-ball exit routes: an expiry is not manufactured by contact that denies every practicable way out ----
    def leaving(depth,count_ms,defender,trying=True,cal=None,run=1200):
        """A1, without the ball, stands `depth` metres inside the arc of the zone his team attacks, straight in front of goal, with
        count_ms of zone time used, and heads straight out. defender: None, 'screen' (B0 stands still in his lane, just outside
        the arc), 'runs_in' (B0 runs at him along that lane and stays in it), 'side_hit' (B0 runs into him from the side and carries on)."""
        m=kb(cal,zone_marking=True,zone_inbound=True);s=m.s;j=s.own_zone('B');gx=0.0 if j==0 else 100.0;sg=1.0 if j==0 else -1.0;R=s.keeper_zone_radius
        kput(m,'A0',(50,10));kgive(m,'A0');A1=kput(m,'A1',(gx+sg*(R-depth),50.0));A1.facing=(sg,0.0);ktop(m,'A1',8.0);m.c3_reckless={'A1','B0'};tg={'A1':(gx+sg*(R+6),50.0) if trying else (A1.x,A1.y)}
        if defender=='screen':B=kput(m,'B0',(gx+sg*(R+.3),50.0));B.facing=(-sg,0.0)
        elif defender=='runs_in':B=kput(m,'B0',(A1.x+sg*1.2,50.0),(-sg*5,0));ktop(m,'B0',5.0);tg['B0']=(A1.x+sg*.2,50.0)
        elif defender=='side_hit':B=kput(m,'B0',(A1.x+sg*.3,50.0-1.3),(0,6));ktop(m,'B0',6.0);tg['B0']=(A1.x+sg*.3,80.0)
        ktick(m,{},10);A1.zone_ms[j]=count_ms;A1.exit_try=None;k=len(m.e.log);t0=s.now
        while s.now<t0+run and s.owner=='A' and not evs(m,'exit_obstruction',k) and A1.zone_loc[j]=='in':ktick(m,tg,20)
        return m,k,A1,j
    m,k,A1,j=leaving(1.0,4350,None);ok(not evs(m,'attacking_zone_expiry',k) and A1.zone_loc[j]=='out' and A1.zone_ms[j]==0 and getattr(A1,'exit_try',None) is None,'nobody in the way: he gets out in time, the count resets, and the exit record is closed')
    m,k,A1,j=leaving(1.0,4350,'runs_in');x=lastev(m,'exit_obstruction',k)['data'];ex=x['exit']
    ok(not evs(m,'attacking_zone_expiry',k) and m.s.owner=='A' and x['by']=='B0' and ex['sufficient'] and ex['free_ms']<ex['left_ms'] and len(ex['contacts'])>=1 and ex['before_contact']['sufficient'] and not ex['ignored_attainable_exit'] and ex['route_open_ms']==0 and ex['denied_ms']>0 and ex['checks_after']>=3,'his time was enough when he set off and just before a defender ran into him; the defender stayed in his only lane, and no practicable route existed at any check after that: no expiry is given')
    ok(lastev(m,'foul',k)['data']['reason']=='exit_obstruction' and lastev(m,'foul',k)['data']['actor']=='B0' and lastev(m,'foul',k)['data']['victim']=='A1' and A1.zone_ms[j]==x['zone_ms_restored_to']<5000 and x['exit']['denied_ms']>0 and 5000<=x['zone_ms_restored_to']+x['exit']['denied_ms']<5100 and m.stats['exit_obstructions']==1 and m.stats['attacking_zone_expiries']==0 and m.s.advantage is not None,'the defender who ran into him has obstructed the exit: a defensive foul with advantage, and the zone time lost under obstruction is given back')
    m,k,A1,j=leaving(1.0,4350,'screen');e=lastev(m,'attacking_zone_expiry',k)['data']
    ok(e['exit_class']=='no_opposing_contact' and e['exit']['sufficient'] and e['exit']['contacts']==[] and m.s.owner=='B' and not evs(m,'exit_obstruction',k) and evs(m,'c3_collision',k),'a defender who simply stands in the lane is a screen. The attacker runs into him; no opponent ran into the attacker; the expiry stands')
    m,k,A1,j=leaving(1.0,3000,'side_hit');e=lastev(m,'attacking_zone_expiry',k)['data'] if evs(m,'attacking_zone_expiry',k) else None
    ok(e is None and A1.zone_loc[j]=='out','LEAD: knocked by a defender but with a practicable route still open and time to use it, he simply gets out')
    def boxed(cnt=4200):
        """With 0.8 s in hand (or 5 - cnt/1000) and one metre to go, he is run into from the side and then heads for a point outside the zone by a line
        that stays inside it for six metres, instead of the way straight out, which is open."""
        m=kb(zone_marking=True,zone_inbound=True);s=m.s;j=s.own_zone('B');gx=0.0 if j==0 else 100.0;sg=1.0 if j==0 else -1.0;R=s.keeper_zone_radius
        kput(m,'A0',(50,10));kgive(m,'A0');A1=kput(m,'A1',(gx+sg*(R-1.0),50.0));A1.facing=(sg,0.0);ktop(m,'A1',8.0);m.c3_reckless={'A1','B0'};kput(m,'B0',(A1.x+sg*.3,50.0-1.3),(0,6));ktop(m,'B0',6.0)
        ktick(m,{},10);A1.zone_ms[j]=cnt;A1.exit_try=None;k=len(m.e.log)
        while s.owner=='A' and s.now<4000 and A1.zone_loc[j]=='in':ktick(m,{'A1':(A1.x,80.0),'B0':(A1.x+sg*.3,90.0)},20)
        return m,k,A1,j
    m,k,A1,j=boxed();e=lastev(m,'attacking_zone_expiry',k)['data']
    ok(e['exit_class']=='practicable_route_remained' and e['exit']['contacts'] and e['exit']['before_contact']['sufficient'] and e['exit']['ignored_attainable_exit'] and e['exit']['longest_continuous_open_ms']>=e['exit']['needed_ms_by_the_lane_concerned'] and m.s.owner=='B','contact plus outward intent is not enough. A defender ran into him, but a practicable route then stayed open for longer than he needed to use it and he did not take it: the expiry stands')
    m,k,A1,j=boxed(4520);e=lastev(m,'attacking_zone_expiry',k)['data']
    ok(e['exit_class']=='time_insufficient_before_contact' and e['exit']['sufficient'] and not e['exit']['before_contact']['sufficient'] and not e['exit']['ignored_attainable_exit'] and m.s.owner=='B' and not evs(m,'exit_obstruction',k),'FOUND: his time was enough as he set off, but he had used it up himself, heading the long way, before the defender touched him. No practicable route followed the contact, yet the contact took nothing from him: the expiry stands')
    m,k,A1,j=leaving(12.0,4700,'runs_in');e=lastev(m,'attacking_zone_expiry',k)['data']
    ok(e['exit_class']=='time_already_insufficient' and not e['exit']['sufficient'] and e['exit']['free_ms']>e['exit']['left_ms'] and m.s.owner=='B','LEAD: twelve metres inside with 0.3 s left, his time was already too short before anyone touched him: the expiry stands whatever the defender then did')
    m,k,A1,j=leaving(1.0,4350,'runs_in',trying=False);e=lastev(m,'attacking_zone_expiry',k)['data'];ok(e['exit_class']=='no_exit_attempt' and 'exit' not in e and m.s.owner=='B','an attacker who is not trying to leave has no exit to protect')
    m,k,A1,j=leaving(1.0,4350,'runs_in',cal={'exit_protection':0});e=lastev(m,'attacking_zone_expiry',k)['data'];ok(e['exit_class']=='not_assessed' and m.s.owner=='B' and not evs(m,'exit_obstruction',k),'with exit_protection off the same sequence is an expiry, as in C2')
    def zst(r=19.0,v=(0.0,0.0),count=4350.0):
        """An attacker without the ball r metres from the goal he attacks, straight in front of it, with radial speed v[0] (outward
        positive) and sideways speed v[1], and `count` ms of zone time used. Staged state for the route and witness routines."""
        m=kb(zone_marking=True,zone_inbound=True);s=m.s;j=s.own_zone('B');gx=0.0 if j==0 else 100.0;sg=1.0 if j==0 else -1.0
        kput(m,'A0',(50,10));kgive(m,'A0');A1=kput(m,'A1',(gx+sg*r,50.0),(sg*v[0],v[1]));A1.zone_ms[j]=count;A1.zone_loc[j]='in';A1.target=(gx+sg*26.0,50.0);return m,A1,j,gx,sg
    def freet(m,A1,j,left):return m.e.exit_free((A1.x,A1.y,A1.vx,A1.vy,A1.fatigue),A1,j,left)
    m,A1,j,gx,sg=zst(v=(-10.0,0.0));f_in=freet(m,A1,j,650.0);_,b_in,n_in=m.e.exit_routes(A1,j,650.0)
    m,A1,j,gx,sg=zst();f_rest=freet(m,A1,j,650.0);_,b_rest,n_rest=m.e.exit_routes(A1,j,650.0)
    m,A1,j,gx,sg=zst(v=(10.0,0.0));f_out=freet(m,A1,j,650.0)
    m,A1,j,gx,sg=zst(v=(0.0,10.0));f_side=freet(m,A1,j,650.0)
    ok(n_in==0 and b_in is None and f_in>1500 and not m.e.exit_before(*[zst(v=(-10.0,0.0))[i] for i in (1,2)],(gx+sg*19.0,50.0,-sg*10.0,0.0,1.0,650.0))['sufficient'],'LEAD (correction 2): one metre inside the arc but moving in at 10 m/s with 0.65 s left, he has no practicable way out. He must brake the inward speed off first, and the time says so (C3b1 reported 469 ms by treating him as standing still)')
    ok(n_rest>0 and 420<=f_rest<=480 and f_out<=120 and f_out<f_side<f_rest<f_in and f_side<=650,'the same place at rest: about 0.45 s, practicable. Already moving out at 10 m/s: a tenth of a second. Moving sideways at 10 m/s: 0.32 s, because he keeps his speed and turns outward at his turning limit. The time comes from his motion law, not from a formula for a standing start')
    m,A1,j,gx,sg=zst(r=10.0);r0=m.e.exit_routes(A1,j,5000);kput(m,'B0',(gx+sg*11.2,50.0));r1=m.e.exit_routes(A1,j,5000);r2=m.e.exit_routes(A1,j,100)
    ok(r0[2]>r1[2]>0 and r1[1]>r0[1] and r0[0]==r1[0]==r0[1] and r2[1:]==(None,0) and abs(r0[1]-1000*math.sqrt(2*10.0/(A1.a.acceleration*(.55+.45*A1.fatigue))))<=40,'exit routes: a body in a lane closes that lane and the fastest practicable way becomes a longer one; with too little time none is practicable; from rest the time is his own acceleration over the distance, to the 20 ms step')
    def two_contacts(gap_ms,second_blocks=True):
        """LEAD (correction 3), staged as in the Lead's probe with the real watcher and adjudicator. B0 runs into A1; a way out is open
        afterwards. gap_ms later B1 runs into him (and, second_blocks, stands across every lane he could use). His time then runs out."""
        m,A1,j,gx,sg=zst();s=m.s;m.e.exit_watch();A1.c3_hit=(1001.0,'B0');s.now=1001;A1.zone_ms[j]=4351.0;m.e.exit_watch();first=copy.deepcopy(A1.exit_try['ep'])
        t=1001+gap_ms
        for u in range(1101,t,100):s.now=u;A1.zone_ms[j]=4351.0+u-1001;m.e.exit_watch() #the ordinary checks, once per interval, in between
        if second_blocks:kput(m,'B1',(A1.x+sg*1.2,50.0))
        A1.c3_hit=(float(t),'B1');s.now=t;A1.zone_ms[j]=4351.0+gap_ms;m.e.exit_watch();second=copy.deepcopy(A1.exit_try['ep']);routes=m.e.exit_routes(A1,j,5000-A1.zone_ms[j])
        s.now=1650;A1.zone_ms[j]=5000.0;k=len(m.e.log);m.e.zone_expiry_c3b(A1,j);return m,A1,j,k,first,second,routes
    m,A1,j,k,first,second,routes=two_contacts(50);x=lastev(m,'exit_obstruction',k)['data'];ex=x['exit']
    ok(first['state']=='open' and routes[1:]==(None,0) and len(second['contacts'])==2 and not second['ignored'] and not evs(m,'attacking_zone_expiry',k) and x['by']=='B1' and m.s.owner=='A' and lastev(m,'foul',k)['data']['actor']=='B1','LEAD (correction 3): a way out that was open for 50 ms after the first contact, when he needed 0.47 s to use it, does not excuse a second defender who then runs into him and shuts every lane: no expiry, and the second defender has obstructed him')
    ok(ex['route_open_ms']==50 and ex['denied_ms']==599 and x['zone_ms_restored_to']==4401.0==A1.zone_ms[j] and ex['contacts'][1]['route_open_ms_since_previous_contact']==50 and ex['contacts'][1]['before']['sufficient'] and ex['contacts'][0]['by']=='B0' and ex['longest_continuous_open_ms']==50<ex['needed_ms_by_the_lane_concerned'],'LEAD: the log has the time enough before each contact, the 50 ms a route was open between them, and the count restored: exactly the 599 ms that ran with no practicable route, back to what it was at the second contact. The time of the first, unrelated contact is not given back')
    m,A1,j,k,first,second,routes=two_contacts(520);e=lastev(m,'attacking_zone_expiry',k)['data']
    ok(e['exit_class']=='time_insufficient_before_contact' and e['exit']['episodes']==2 and len(second['contacts'])==1 and second['contacts'][0]['by']=='B1' and not second['before']['sufficient'] and m.s.owner=='B' and not evs(m,'exit_obstruction',k),'LEAD: the evidence that he ignored an attainable exit is kept. With the way out open for 0.5 s after the first contact (he needed 0.44 s) and unused, the first episode is closed against him. The second contact begins a new episode with its own witness: by then he no longer had time enough, and the expiry stands although every lane was then shut')
    m,A1,j,gx,sg=zst();s=m.s;m.e.exit_watch();A1.c3_hit=(1001.0,'B0');s.now=1001;A1.zone_ms[j]=4351.0;m.e.exit_watch()
    for u in range(1101,1650,100):s.now=u;A1.zone_ms[j]=4351.0+u-1001;m.e.exit_watch()
    s.now=1650;A1.zone_ms[j]=5000.0;k=len(m.e.log);m.e.zone_expiry_c3b(A1,j);e=lastev(m,'attacking_zone_expiry',k)['data']
    ok(e['exit_class']=='practicable_route_remained' and e['exit']['ignored_attainable_exit'] and e['exit']['denied_ms']==0 and e['exit']['longest_continuous_open_ms']>=e['exit']['needed_ms_by_the_lane_concerned'] and e['exit']['episodes']==1,'and with one contact, a clear lane throughout and no attempt to use it, the class is that a practicable route remained')
    # ---- 27b. C3b3 (the Lead's C3b2 audit): no way out is practicable that needs more than the time left; who denied him ----
    m,A1,j,gx,sg=zst();need=freet(m,A1,j,6000.0);rows={left:(m.e.exit_routes(A1,j,float(left)),m.e.exit_before(A1,j,(A1.x,A1.y,A1.vx,A1.vy,A1.fatigue,float(left)))) for left in (need-20,need-19,need-10,need-1,need,need+1,need+7,need+20)}
    ok(need==440 and all(r[1:]==(None,0) and r[0]==need and not b['sufficient'] and b['free_ms']==need for left,(r,b) in rows.items() if left<need),'LEAD (C3b2 audit): at rest one metre inside the arc he needs 440 ms. With 420, 421, 430 or 439 ms left no route is practicable, and the witness agrees: not enough. The 440 ms is still reported, as the time he would have needed (C3b2 called the route practicable with 421 to 439 ms left)')
    ok(all(r[1]==need and r[2]>=1 and r[0]==need and b['sufficient'] for left,(r,b) in rows.items() if left>=need),'at the deadline exactly, and above it by 1, 7 or 20 ms, the same route is practicable and the witness says enough')
    bad=[];seen=0
    for r_,v_ in ((19.0,(0.0,0.0)),(17.3,(2.0,1.0)),(15.0,(0.0,6.0)),(12.0,(-3.0,0.0)),(18.4,(-1.0,-4.0)),(10.0,(5.0,5.0))):
        m,A1,j,gx,sg=zst(r=r_,v=v_);st=(A1.x,A1.y,A1.vx,A1.vy,A1.fatigue);pts=m.e.exit_points(j);full=[m.e.exit_run(st,A1,j,ax,ay,6000) for ax,ay in pts]
        for left in (97.0,333.0,440.0,611.0,1003.0,1499.0,2000.0,2777.0):
            lanes=m.e.exit_lanes(A1,j,left);free,best,n=m.e.exit_routes(A1,j,left);bef=m.e.exit_before(A1,j,st+(left,))
            for i,t in lanes.items():
                seen+=1
                if (t is not None and t>left) or t!=(full[i] if full[i] is not None and full[i]<=left else None):bad.append((r_,v_,left,i,t,full[i]))
            if (best is not None and best>left) or (n>0)!=bef['sufficient'] or bef['sufficient']!=(bef['free_ms']<=left):bad.append((r_,v_,left,'witness',best,bef))
    ok(not bad and seen>900,'six starting states by eight amounts of time left, none a multiple of 20 ms but two, every one of the 23 lanes: no lane is given a time beyond the time left; a time within it is the same time the run gives unlimited; and with nobody in the way the witness says enough exactly when some lane is practicable')
    def leaves_late(left_when_he_goes):
        """LEAD (C3b2 audit), staged with the real watcher and adjudicator. B0 runs into A1 with 649 ms left and stands in his way out.
        When A1 has left_when_he_goes ms left B0 moves off. Nobody else comes. His time runs out."""
        m,A1,j,gx,sg=zst();s=m.s;m.e.exit_watch();kput(m,'B0',(A1.x+sg*1.2,50.0));A1.c3_hit=(1001.0,'B0');s.now=1001;A1.zone_ms[j]=4351.0;m.e.exit_watch();first=A1.exit_try['ep']['state']
        gone=5000.0-left_when_he_goes;s.now=int(1001+gone-4351);A1.zone_ms[j]=gone;kput(m,'B0',(50,90));m.e.exit_watch();after=A1.exit_try['ep']['state']
        s.now=1650;A1.zone_ms[j]=5000.0;k=len(m.e.log);m.e.zone_expiry_c3b(A1,j);return m,A1,j,k,first,after
    m,A1,j,k,first,after=leaves_late(430.0);x=lastev(m,'exit_obstruction',k)['data'];ex=x['exit']
    ok(first=='denied' and after=='denied' and ex['denied_ms']==649 and ex['route_open_ms']==0 and x['zone_ms_restored_to']==4351.0==A1.zone_ms[j] and x['by']=='B0' and not evs(m,'attacking_zone_expiry',k),'LEAD (C3b2 audit): the defender stands in his way until he has 430 ms left and then moves off. He needs 440 ms, so no way out has opened: all 649 ms are denied time and all of it is given back, to 4351 (C3b2 called the late route open, gave back 219 ms and left the count at 4781)')
    ok(ex['denied_segments']==[{'by':['B0'],'basis':'ran_into_him_and_stands_in_his_lanes','ms':219.0},{'by':['B0'],'basis':'carried_from_the_check_before','ms':430.0}] and ex['denied_ms_by_opponent']=={'B0':649.0} and ex['last_contact_by']=='B0','the record keeps the two stretches apart: 219 ms with the defender who ran into him standing in his lanes, then 430 ms with the lanes clear and the time gone, carried to the same defender')
    m,A1,j,k,first,after=leaves_late(439.0);ok(after=='denied' and lastev(m,'exit_obstruction',k)['data']['exit']['denied_ms']==649,'the same with 439 ms left when he moves off: still no way out, still all of it denied')
    for left in (440.0,441.0,460.0):
        m,A1,j,k,first,after=leaves_late(left);e=lastev(m,'attacking_zone_expiry',k)['data']
        ok(after=='open' and e['exit_class']=='practicable_route_remained' and e['exit']['denied_ms']==649-left and e['exit']['route_open_ms']==left>=e['exit']['needed_ms_by_the_lane_concerned']==440 and not evs(m,'exit_obstruction',k) and m.s.owner=='B','with %d ms left when the defender moves off the way out is real: open for as long as it needs, and not taken. The expiry stands'%left)
    m,A1,j,k,first,second,routes=two_contacts(50);ex=lastev(m,'exit_obstruction',k)['data']['exit']
    ok(ex['denied_ms_by_opponent']=={'B1':599.0} and ex['denied_segments']==[{'by':['B1'],'basis':'ran_into_him_and_stands_in_his_lanes','ms':599.0}] and ex['last_contact_by']=='B1','in the two-contact case of C3b2 nothing changes: the first defender denied him nothing, so nothing is put down to him')
    def staged(steps):
        """The real watcher and adjudicator on a staged sequence. steps: (zone time used, {opponent: where he stands, as (metres outward of A1, metres across) or None to send him away}, who runs into A1 at this check or None, A1's radial speed or None)."""
        m,A1,j,gx,sg=zst();s=m.s;m.e.exit_watch()
        for zms,where,hit,vr in steps:
            s.now=int(1001+zms-4351);A1.zone_ms[j]=float(zms)
            for q,xy in where.items():kput(m,q,(50,88+2*int(q[1:])) if xy is None else (A1.x+sg*xy[0],50.0+xy[1]))
            if vr is not None:A1.vx=sg*vr
            if hit:A1.c3_hit=(float(s.now),hit)
            m.e.exit_watch()
        s.now=1650;A1.zone_ms[j]=5000.0;k=len(m.e.log);m.e.zone_expiry_c3b(A1,j);return m,A1,j,k
    m,A1,j,k=staged([(4351,{'B0':(1.2,0.0)},'B0',None),(4551,{'B0':None},None,None),(4601,{'B1':(1.2,0.0)},'B1',None)]);x=lastev(m,'exit_obstruction',k)['data'];ex=x['exit']
    ok(ex['denied_ms']==599 and ex['route_open_ms']==50 and x['zone_ms_restored_to']==4401.0 and ex['denied_ms_by_opponent']=={'B0':200.0,'B1':399.0} and [(g['by'],g['ms']) for g in ex['denied_segments']]==[(['B0'],200.0),(['B1'],399.0)] and x['by']=='B1' and lastev(m,'foul',k)['data']['actor']=='B1',"LEAD (restoration across contacts): B0 stands in his way for 200 ms, a way out opens for 50 ms (he needs 440), B1 runs into him and shuts it for the last 399 ms. Both denied stretches are given back and the 50 ms is not. B1, with most of the denied time, is penalised; B0's 200 ms is recorded as B0's, not B1's")
    m,A1,j,k=staged([(4351,{'B0':(1.2,0.0)},'B0',None),(4751,{'B0':None},None,None),(4851,{'B1':(-1.2,0.0)},'B1',None)]);x=lastev(m,'exit_obstruction',k)['data'];ex=x['exit']
    ok(ex['denied_ms']==649 and ex['denied_ms_by_opponent']=={'B0':649.0} and x['by']=='B0' and ex['last_contact_by']=='B1' and len(ex['contacts'])==2 and lastev(m,'foul',k)['data']['actor']=='B0' and ex['denied_segments'][-1]['basis']=='carried_from_the_check_before',"LEAD: a later contact that is not in his way takes on nothing. B0 blocks him for 400 ms and leaves him with too little time; B1 then bumps him from the goal side. The last contact is B1's, the denial is all B0's, and B0 is penalised")
    m,A1,j,k=staged([(4351,{'B0':(1.2,0.0)},'B0',None),(4551,{'B1':(-1.2,0.0)},'B1',None)]);x=lastev(m,'exit_obstruction',k)['data']
    ok(x['exit']['denied_ms_by_opponent']=={'B0':649.0} and x['by']=='B0' and x['exit']['last_contact_by']=='B1',"and while B0 is still standing in his lanes, B1's bump from behind changes nothing either")
    m,A1,j,k=staged([(4351,{'B0':(-1.2,0.0)},'B0',None),(4401,{'B0':None,'B1':(-1.2,0.0)},'B1',-10.0)]);x=lastev(m,'exit_obstruction',k)['data'];ex=x['exit']
    ok(ex['route_open_ms']==50 and ex['denied_ms']==599 and ex['denied_ms_by_opponent']=={'B1':599.0} and x['by']=='B1' and ex['denied_segments'][0]['basis']=='last_to_run_into_him_before_this_denial',"a denial with nobody in his lanes: B0's knock leaves his way open; 50 ms later B1 knocks him back towards the goal at 10 m/s and he can no longer be out in time. The denied stretch is put down to the opponent who last ran into him before it began, B1")
    m,A1,j,k=staged([(4351,{'B0':(1.2,0.0),'B1':(1.2,1.0)},'B0',None),(4451,{},'B1',None)]);x=lastev(m,'exit_obstruction',k)['data'];ex=x['exit']
    ok(ex['denied_ms']==649 and ex['denied_ms_by_opponent']=={'B0':649.0,'B1':549.0} and x['by']=='B0' and [(g['by'],g['ms']) for g in ex['denied_segments']]==[(['B0'],100.0),(['B0','B1'],549.0)],'two defenders in his lanes: B1 counts from when he too has run into him, a stretch they share is put down to each in full, and the one with more of it is penalised. The time given back is the 649 ms, once')
    m,A1,j,k=staged([(4351,{'B0':(-1.2,0.0)},'B0',None),(4571,{'B0':None,'B1':(-1.2,0.0)},'B1',None)]);e=lastev(m,'attacking_zone_expiry',k)['data']
    ok(e['exit_class']=='practicable_route_remained' and e['exit']['route_open_ms']==649 and e['exit']['denied_ms']==0 and not evs(m,'exit_obstruction',k) and m.s.owner=='B',"FOUND: a contact that does not set him back closes nothing. His way is open after B0's knock and he stands still for 220 ms; B1 then bumps him without moving him, with 429 ms left. He can no longer make it, but that time went because he did not use it: the lane stays open against him and the expiry stands")
    m,A1,j,k=staged([(4351,{'B0':(-1.2,0.0)},'B0',None),(4451,{'B0':None,'B1':(-1.2,0.0)},'B1',-0.5)]);e=lastev(m,'attacking_zone_expiry',k)['data']
    ok(e['exit_class']=='practicable_route_remained' and e['exit']['needed_ms_by_the_lane_concerned']==100+freet(*zst(v=(-0.5,0.0))[:3],6000.0)==600 and e['exit']['longest_continuous_open_ms']==649>=e['exit']['needed_ms_by_the_lane_concerned'],'FOUND: a contact that sets him back but leaves the way attainable sets back what the lane needs: open 100 ms, then knocked inward at 0.5 m/s, it needs the 100 ms plus the 500 ms he needs from there. It stayed open longer than that and he did not take it: the expiry stands')
    # ---- 28. the record kept for a pending advantage follows a slot through exclusion or injury and its refilling ----
    def adv_b(way):
        """The C2 advantage fixture (advantage pending for A, count one) with the C3b engine rules on. A5 has 3.5 s stored in zone 1
        and 0.6 s unmarked in zone 0. way: how A5 leaves his slot."""
        m=adv_case();m.e.c3b=True;s=m.s;A5=s.players['A5'];A5.zone_ms=[0,3500];A5.unmarked_ms=[600,0]
        def leave():
            if way=='excluded':m.e.discipline('A5','minor')
            else:m.e.injury('A5')
        return m,s,A5,leave
    for way in ('excluded',):
        m,s,A5,leave=adv_b(way);leave();ok(m.e.vacated['A']==[([0,3500],[600,0],[0,0])] and m.e.vacated_keep['A']==[None],way+' before the turnover: his slot state waits, as in C2')
        tk(m,'B1');ok(s.owner=='B' and m.e.vacated['A']==[([0,0],[0,0],[0,0])] and m.e.vacated_keep['A'][0][1]==([0,3500],[600,0],[0,0]) and m.e.vacated_keep['A'][0][0] is s.advantage['c2']['keep'],'the turnover clears the waiting slot with everything else, and what it held is kept with the advantage')
        k=len(m.e.log);recall(m);n=s.players['A12'];d=lastev(m,'vacant_slot_state_returned',k)['data']
        ok(m.e.vacated['A']==[([0,3500],[600,0],[0,0])] and m.e.vacated_keep['A']==[None] and d['zone_ms']==[0,3500] and A5.zone_ms==[0,0],'recall with the slot still empty: the kept state goes back to the slot, not to the athlete who has gone')
        m.e.slot_fill(n);ok((n.zone_ms,n.unmarked_ms)==([0,3500],[600,0]) and m.e.vacated['A']==[] and m.e.vacated_keep['A']==[],'and whoever then fills the slot inherits it')
        m,s,A5,leave=adv_b(way);tk(m,'B1');keep=s.advantage['c2']['keep'];ok(keep['A5'][0]==[0,3500],'turnover first: his counts are kept with the advantage');leave()
        ok('A5' not in keep and m.e.vacated_keep['A'][0][0] is keep and m.e.vacated_keep['A'][0][1][0]==[0,3500] and m.e.vacated['A']==[([0,0],[0,0],[0,0])],way+' after the turnover: the kept record leaves with the slot')
        n=s.players['A12'];m.e.slot_fill(n);ok(keep['A12'][0]==[0,3500] and n.zone_ms==[0,0] and m.e.vacated_keep['A']==[],'the newcomer holds the slot\'s kept record while the advantage is pending');recall(m)
        ok((n.zone_ms,n.unmarked_ms)==([0,3500],[600,0]) and A5.zone_ms==[0,0] and s.players['A3'].zone_ms[1]==4100,'and the recall returns it to him, with everyone else\'s')
    m,s,A5,leave=adv_b('injured');tk(m,'B1');keep=s.advantage['c2']['keep'];leave()
    ok('A5' not in keep and m.e.vacated_keep['A'][0][0] is keep and m.e.vacated_keep['A'][0][1][0]==[0,3500] and A5.zone_ms==[0,0],'an injury takes the kept record out with the slot in the same way')
    m,s,A5,leave=adv_b('excluded');tk(m,'B1');leave();s.advantage=None;n=s.players['A12'];m.e.slot_fill(n);ok(n.zone_ms==[0,0] and m.e.vacated_keep['A']==[],'if that advantage ends without a recall, the kept record dies with it: a later filler gets nothing from it')
    m=adv_case();s=m.s;A5=s.players['A5'];A5.zone_ms=[0,3500];tk(m,'B1');m.e.discipline('A5','minor');n=s.players['A12'];m.e.slot_fill(n);recall(m)
    ok(n.zone_ms==[0,0] and A5.zone_ms==[0,3500],'with c3b off the campaign behaviour is unchanged: the record goes back to the excluded athlete and his replacement gets nothing (the 12 occurrences flagged in the C2 campaign)')
    # ---- 29. bench transit covers distance by elapsed time ----
    def transit(step_ms,n,c3b=True):
        m=kb({'c3b':1 if c3b else 0});s=m.s;low=s.ends['A']==0;gate=(75.0,0.0) if low else (25.0,100.0);o=s.players['A3'];q=next(p_ for p_ in s.players.values() if p_.team=='A' and not p_.active and p_.available)
        q.x,q.y=gate[0]-20.0,gate[1];m.pending_sub['A']=(o.id,q.id);x0=q.x
        for i in range(n):m.step_ms=step_ms;m.auto_substitutions()
        return abs(q.x-x0)
    a=transit(100,3);b=transit(10,30);c=transit(1,300);d=transit(10,30,c3b=False)
    ok(near(a,2.4) and near(b,2.4) and near(c,2.4) and near(d,20.0),'a substitute walking to the gate covers 8 m/s x the time elapsed (2.4 m in 300 ms) however many intervals that time was cut into; with c3b off thirty 10 ms intervals carried him the whole 20 m to the gate, the C3a defect')
    # ---- 30. M1.4: new measures beside M1.3, which is untouched; a missing witness is 'unavailable', never zero ----
    m,k=downed(extra=[('B2',(40.0,51.6),.05)]);r_=step_in(m,'B1',k);M4=measure_c3(m.e.log);h=M4['holds'];ends=evs(m,'c3_hold_end')
    ok(M4['measurement']=='M1.4' and M4['kernel_witness_in_log'] and M4['c3b_witness_in_log'] and h['ended']==len(ends)==3 and h['true_duration_ms']['n']==3 and near(h['true_duration_ms']['max'],max(e['data']['duration_ms'] for e in ends),1e-3) and h['reached_tackle_grip_0_3']==2,'true hold duration comes from each hold\'s witnessed start and end')
    ok(M4['groundings']['by_manner']=={'defence_driven':1} and M4['groundings']['counted_tackles']==1 and M4['get_up']['tackled_carriers']['n']==1 and M4['get_up']['tackled_carriers']['rise_ms']['mean']==656.0 and M4['get_up']['others_grounded']['n']==0,'grounding class and manner, and the get-up of the tackled carrier apart from anyone else who went down')
    rc=M4['recovery_compliance'];ok(rc['recoveries']==1 and rc['holders_given_grace_besides_the_tackler']==1 and rc['reaction_ms']['median']==300 and rc['cleared']==1 and rc['cleared_late']==0 and rc['found_inside_the_disc']==1 and rc['of_which_entered_late']==0,'recovery compliance: grace given, reaction time, who was found in the disc, what was necessary and what was his own delay')
    ok(M4['fouls']['removed_classifiers']=={'contact_speed':'classifier removed in active C3; none can occur'} and M4['descent']['attempts']==0 and M4['containment']=={'episodes':0,'expiries_while_contained':0} and M4['exit_obstructions']==0,'with the witness in the log, nothing happening is a real zero')
    m,A,j,x,ds=zone_hold(count_ms=3200,v=3.0);zrun(m,x,ds,2500);M5=measure_c3(m.e.log)
    ok(M5['containment']=={'episodes':1,'expiries_while_contained':1} and M5['zone_expiries_by_exit_class']=={'carrier_contained':1} and M5['descent']['attempts']==1 and M5['descent']['ended_by']=={'control_lost':1} and M5['holds']['contained_ms']['n']==1,'containment episodes and expiries, descent attempts and how they ended, and zone expiries by exit class')
    m,k=downed(cal={'c3b':0});M6=measure_c3(m.e.log)
    ok(M6['kernel_witness_in_log'] and not M6['c3b_witness_in_log'] and all(M6[x]=='unavailable' for x in ('get_up','descent','containment','zone_expiries_by_exit_class','exit_obstructions','recovery_compliance')) and M6['groundings']['by_manner']=='unavailable' and M6['holds']['contained_ms']=='unavailable' and M6['holds']['ended']==2 and M6['groundings']['by_class']=={'tackle_under_hold':1},'a C3a log has the kernel measures and none of the C3b ones: those are unavailable, not zero')
    m=c2m();one(m);M7=measure_c3(m.e.log)
    ok(not M7['kernel_witness_in_log'] and M7['collisions']==M7['holds']==M7['groundings']==M7['get_up']=='unavailable' and M7['fouls']['removed_classifiers']=={'contact_speed':0} and isinstance(M7['fouls']['by_reason'],dict),'a C2 log has no kernel witness: every contact measure is unavailable, and the speed offence, which C2 still had, is counted in its own place')
    m=c2m();one(m);a1=measure(m.e.log,SETTINGS);b1=measure_c3(m.e.log);a2=measure(m.e.log,SETTINGS);ok(a1==a2 and 'continuation' in a1 and 'measurement' not in a1,'M1.3 is a separate function and is not changed by measuring M1.4 on the same log')
    q1=report_qualifications(M4);q2=report_qualifications(M6);q3=report_qualifications(M7)
    ok(len(q1)==1 and 'NOT true' in q1[0] and 'get_up' in q1[0] and q2==[] and q3==[],'C3b2: a report on a C3b match says, beside the retained M1.3 note that get-up is fixed, that it is not true of this match and where the modelled figures are; a C3a or C2 report says nothing, because there the note is true')

    # ================= C3c: contact after DreLen's four rulings =================
    # The C3a and C3b scenarios above ran with c3c = 0: they describe C3b2 and all still hold. From here C3c is on.
    def kc(cal=None,**kw):return kb({'c3c':1,**(cal or {})},**kw)
    def first(m,name,k=0):return next((r for r in m.e.log[k:] if r['event']==name),None)
    def thrown(m,k=0):return next((r for r in m.e.log[k:] if r['event']=='release' and not r['data'].get('forced') and r['data'].get('kind')!='loose'),None)
    def hp(region='upper',holder=.68,request='first_touch',withhold=None,cal=None,strips=False,v=6.0,ms=2500,drive=None,stop=None,each=None):
        """A carrier runs at v with one defender alongside, just within reach, and a team-mate open ahead. request: 'first_touch' (he
        asks for the pass as the hold begins), a share 0..1 of the wind-up already done when the hold begins, 'established' (asked once
        the grip is material), or None (no pass)."""
        m=kb({'c3c':1,**(cal or {})},strips=strips);m.c3_fix_region=region;m.c3_fix_withhold=withhold;m.c3_fix_drive=drive;s=m.s
        A=kput(m,'A0',(40,50),(v,0));ktop(m,'A0',v,True);kgive(m,'A0');R=kput(m,'A1',(46,58),(v,0));ktop(m,'A1',v);B=kput(m,'B0',(10,10));B.a.tackling=B.a.strength=holder;ktop(m,'B0',v);full=None
        if isinstance(request,float):
            m.make_pass(A,R,'pass');full=m.c3_due['A0']-s.now;ktick(m,{'A0':(99,50),'A1':(99,58)},int(round(request*full)))
        kput(m,'B0',(A.x-1.1,A.y+1.0),(A.vx,0));t0=s.now;k=len(m.e.log);asked=None
        if request=='first_touch':m.make_pass(A,R,'pass');full=m.c3_due['A0']-s.now;asked=s.now
        while s.now<t0+ms and s.ball.carrier=='A0' and not (stop and stop(m)):
            h=m.c3_holds.get(('B0','A0'))
            if request=='established' and asked is None and h and h['g']>=.3:asked=s.now;m.make_pass(A,R,'pass');full=m.c3_dur.get('A0')
            if each:each(m,h)
            ktick(m,{'A0':(99,50),'A1':(99,58),'B0':(A.x,A.y)},10)
        return m,k,t0,full
    # ---- 31. ruling 1: a high wrap pins the arms; a stalled wind-up is tucked; a pinned carrier does not begin one ----
    m=kc();A=kput(m,'A0',(40,50));kgive(m,'A0');kput(m,'B0',(39,51))
    def rho(region,g,kind,c3c=1):
        m.c3c=bool(c3c);m.c3_holds={('B0','A0'):{'actor':'B0','target':'A0','g':g,'region':region}};r=m.c3_rho(A,kind);m.c3c=True;m.c3_holds={};return r
    ok(near(rho('upper',.2,'pass'),.4) and rho('upper',.5,'pass')==1.0 and rho('upper',.8,'shot')==1.0 and near(rho('upper',.1,'shot'),.2),'RULING 1: an upper hold pins the arms to a degree: restraint on a pass or shot is grip / 0.5, complete from grip 0.5')
    ok(near(rho('lower',.9,'pass'),.27) and near(rho('lower',1.0,'shot'),.3),'LEAD: a lower hold gets no arm restraint from a strong grip: it keeps the C3a weight (0.3 x grip) however hard it grips')
    ok(near(rho('upper',.8,'kick'),.24) and near(rho('lower',.8,'kick'),.8),'a kick is not a hand release: unchanged from C3a under either hold')
    ok(near(rho('upper',.2,'pass',0),.2) and near(rho('upper',.8,'pass',0),.8),'with c3c off the restraint is the C3a one (grip)')
    m,k,t0,full=hp();tk_=first(m,'c3_tuck',k);g=first(m,'c3_grounding',k)
    ok(tk_ is not None and thrown(m,k) is None and near(tk_['data']['stalled_ms'],full,1e-6) and tk_['data']['action']=='pass' and 250<tk_['t_ms']-t0<400 and 'A0' not in m.pending_ball_actions and 'A0' not in m.c3_due,'RULING 1: wrapped high as he begins his pass by a tackler of the same ability, he cannot make it. When the hold has cost the wind-up as long as the wind-up itself takes he gives it up and tucks the ball; the pending release is cancelled and logged with the time stalled')
    ok(g is not None and g['data']['counted'] and g['t_ms']>tk_['t_ms'] and m.s.tackle_count==1 and m.stats['c3_tucks']==1,'and he goes down with the ball: a counted tackle, after the tuck')
    m0,k0,t00,_=hp(cal={'c3c':0});r0=thrown(m0,k0);ok(r0 is not None and r0['t_ms']-t00>400,'C3b2 (c3c off), the same sequence: the pass got away late, before he was down. This expectation changes under ruling 1')
    m,k,t0,full=hp('lower');r=thrown(m,k);rs=last(m,'c3_restraint');ok(r is not None and first(m,'c3_tuck',k) is None and rs['restraint']<.3 and r['t_ms']-t0<300,'LEAD: wrapped low at the same moment his arms are free: the pass is made, hardly delayed')
    res={}
    for share in (.2,.5,.8):
        m,k,t0,full=hp(request=share);res[share]=(thrown(m,k),first(m,'c3_tuck',k),last(m,'c3_restraint') if thrown(m,k) else None)
    ok(res[.2][0] is None and res[.2][1] and res[.5][0] is None and res[.5][1] and res[.8][0] is not None and res[.8][1] is None and .3<res[.8][2]['restraint']<.7 and res[.8][2]['speed_available_mps']<res[.8][2]['speed_unrestrained_mps'],'RULING 1: a pass 20 or 50 percent prepared when the high wrap arrives is tucked; one 80 percent prepared gets away, slower and less accurate for the restraint at release')
    m,k,t0,full=hp(request='established');wh=evs(m,'c3_release_withheld',k)
    ok(len(wh)==1 and wh[0]['data']['restraint']>=wh[0]['data']['limit']==.5 and thrown(m,k) is None and first(m,'c3_tuck',k) is None and not evs(m,'ball_action_prepared',k) and m.stats['c3_releases_withheld']==1 and first(m,'c3_grounding',k)['data']['counted'],'LEAD: a pass asked for after the high hold is established. The carrier does not begin a wind-up he could not finish (logged once for the spell of control), and goes down with the ball')
    m,k,t0,full=hp(request='established',withhold=False);tk_=first(m,'c3_tuck',k);pr=first(m,'ball_action_prepared',k)
    ok(pr is not None and tk_ is not None and thrown(m,k) is None and near(tk_['data']['stalled_ms'],full,1e-6) and tk_['t_ms']-pr['t_ms']<1.2*full+2 and tk_['data']['wind_up_left_ms']>.8*full,'LEAD: the same with that controller choice taken away: he begins the wind-up, it hardly advances (over four fifths of it still to do), and it is tucked after its own length')
    ts=[]
    for sub in (5,10,20):
        m,k,t0,full=hp(cal={'c3_substep_ms':sub});ts.append(first(m,'c3_tuck',k)['t_ms']-t0)
    ok(max(ts)-min(ts)<=6,'the tuck falls at the instant the stalled time reaches the limit, not at the end of a substep: within 6 ms at substeps of 5, 10 and 20 ms: '+str(ts))
    tw=[]
    for hold_ in (.3,.68,.9):
        m,k,t0,full=hp(holder=hold_);tw.append(first(m,'c3_tuck',k)['t_ms']-t0)
    ok(tw[0]>tw[1]>tw[2],'LEAD: weak, reference and strong holders: the stronger the tackler, the sooner the arms are pinned and the ball tucked: '+str(tw))
    # the retry after a tuck: nothing but the wind-up is reset
    seen={}
    def mark(m,h):
        if h is not None and 'retry' in seen:h['g']=.05   #the grip is kept slight from the retry on, so that the second wind-up is a fair test of the retry
        if h is not None and 'A0' not in m.pending_ball_actions and 'tuck' not in seen and first(m,'c3_tuck'):seen['tuck']=(h['g'],h['start'],m.c3_bal(m.s.players['A0']),m.s.possession_ms,id(h))
    def loosened(m):
        if 'tuck' in seen and 'retry' not in seen:
            h=m.c3_holds[('B0','A0')];h['g']=.05;A=m.s.players['A0'];b=m.c3_bal(A);m.make_pass(A,m.s.players['A1'],'pass')
            seen['retry']=(h['start'],b,m.s.possession_ms,id(h),m.c3_stall.get('A0'),'A0' in m.pending_ball_actions)
        return False
    m,k,t0,full=hp(holder=.3,stop=loosened,each=mark,ms=900);r=thrown(m,k)
    ok('retry' in seen and seen['retry'][5] and seen['retry'][4]==0.0 and seen['retry'][0]==seen['tuck'][1] and seen['retry'][3]==seen['tuck'][4] and seen['retry'][1]>=seen['tuck'][2]>0 and seen['tuck'][3]-50<=seen['retry'][2]<seen['tuck'][3]<45000,'LEAD: when the hold loosens he may begin again. The new wind-up starts its own stalled time at zero; the hold is the same hold (same start), his balance load is not reset and neither is the possession clock')
    ok(r is not None and r['t_ms']>first(m,'c3_tuck',k)['t_ms'] and len(evs(m,'c3_tuck',k))==1 and len(evs(m,'ball_action_prepared',k))==2,'and the second attempt, with the grip kept slight, is released')
    # ---- 32. ruling 1: the ball is less secure in a pinned throwing motion (a modifier on the retained strip, nothing else) ----
    class Fixed:
        """Stands in for the contact random stream: every draw returns u, and the draws are counted."""
        def __init__(self,u):self.u=u;self.n=0
        def random(self):self.n+=1;return self.u
        def getstate(self):return self.n
        def setstate(self,n):self.n=n
    def drawn(u,region='upper',request='first_touch',cal=None,ms=200,holder=.68,withhold=None):
        rg=Fixed(u)
        def swap(m,h):
            if m.rng['contact'] is not rg:m.rng['contact']=rg
        m,k,t0,full=hp(region,holder,request,withhold,cal,strips=True,ms=ms,each=swap);return m,k,t0,rg
    base=1-math.exp(-(-math.log(1-.1*.12*.68*(1-.68*.6))/.1)*.01)   # the retained chance in one 10 ms drift for these two athletes
    m,k,t0,rg=drawn(2.5*base);sw=first(m,'c3_strip_in_wind_up',k);st=first(m,'strip',k)
    ok(st is not None and sw is not None and sw['data']['modifier']>2.5 and near(sw['data']['modifier'],1+3*sw['data']['pin'],1e-3) and sw['data']['action']=='pass' and st['data']['actor']=='B0' and m.s.ball.carrier!='A0' and m.stats['c3_strips_in_wind_up']==1,'RULING 1: wrapped high in his throwing motion he may cough it up. A draw that the retained strip chance would have survived takes the ball once the arms are pinned: the chance is multiplied by 1 + 3 x pin, and the record gives the modifier, the pin and the action')
    m1,k1,t1,rg1=drawn(2.5*base,cal={'strip_in_motion_factor':1.0});m2,k2,t2,rg2=drawn(2.5*base,'lower');m3,k3,t3,rg3=drawn(2.5*base,request=None)
    ok(first(m1,'strip',k1) is None and first(m2,'strip',k2) is None and first(m3,'strip',k3) is None,'LEAD: no general fumble multiplier. The same draws take nothing with the factor at 1, under a lower hold, or under an upper hold with no wind-up in progress')
    m4,k4,t4,rg4=drawn(.999);m5,k5,t5,rg5=drawn(.999,cal={'strip_in_motion_factor':1.0});m6,k6,t6,rg6=drawn(.999,cal={'c3c':0})
    ok(rg4.n==rg5.n==rg6.n>10,'LEAD: no extra random draws: over the same 200 ms the contact stream is drawn from exactly as often with the modifier, without it, and with C3c off ('+str(rg4.n)+' draws)')
    m,k,t0,rg=drawn(2.5*base,request='established',withhold=None,ms=700);ok(first(m,'strip',k) is None and first(m,'c3_release_withheld',k) is not None,'LEAD: a carrier who keeps the ball tucked has no wind-up and so none of this vulnerability: the same draws take nothing')
    def tucked_then(m,h):
        if first(m,'c3_tuck') and not isinstance(m.rng['contact'],Fixed):m.rng['contact']=Fixed(2.5*base)
    m,k,t0,full=hp(strips=True,each=tucked_then,ms=700);ok(first(m,'c3_tuck',k) is not None and first(m,'strip',k) is None and isinstance(m.rng['contact'],Fixed) and m.rng['contact'].n>5,'LEAD: tucking the ball removes the vulnerability: after the tuck the same draws take nothing, under the same hold')
    he=None
    m,k,t0,full=hp(ms=200);m.c3_end_hold(('B0','A0'),'out_of_reach',m.s.now);he=last(m,'c3_hold_end')
    ok(near(he['wind_up_under_this_upper_hold_ms'],200,1e-6) and he['peak_pin_in_wind_up']>.6 and near(he['peak_strip_modifier'],1+3*he['peak_pin_in_wind_up'],1e-3) and he['escape_effort_ms']==0,'the exposure is on every hold record whether or not a strip came: time in a wind-up under the upper hold, the peak pin and the peak modifier')
    # ---- 33. the defender's choice of a high or low hold, from what he can see ----
    def choice(layout,policy=1,fix=None):
        m=kc({'c3_region_policy':policy});m.c3_fix_region=fix;A=kput(m,'A0',(40,50),(6,0));kgive(m,'A0');B=kput(m,'B0',(38.9,51.0),(6,0))
        if layout in ('open','marked','windup'):kput(m,'A1',(46,55.3),(6,0))
        if layout=='marked':kput(m,'B1',(46.5,56.5),(6,0))
        if layout=='far':kput(m,'A1',(80,50),(6,0))
        if layout=='windup':m.c3_fix_withhold=False;m.make_pass(A,m.s.players['A1'],'pass');m.c3_prep['A0']=m.s.now-400
        return m.c3_region(B,A,m.s.now)
    ok(choice('nobody')==('lower',False) and choice('open')==('upper','pass_open') and choice('marked')==('lower',False) and choice('far')==('lower',False) and choice('windup')==('upper',True),'the placeholder controller: a defender goes high against a carrier with a pass open (a team-mate 3 to 30 m away whom nobody is marking), and against a wind-up he has watched for his reaction time; otherwise low. Positions only: nothing about what the carrier intends')
    ok(choice('open',policy=0)==('lower',False) and choice('open',fix='lower')==('lower','pass_open') and choice('nobody',fix='upper')==('upper',False),'with the policy off it is the C3a choice; a fixed region for a drill overrides the choice and leaves what he saw on the record')
    m,k,t0,full=hp(region=None,request=None,ms=30);hs=last(m,'c3_hold_start');ok(hs['region']=='upper' and hs['pass_open_observed'] is True and hs['release_preparation_observed'] is False,'the hold record says which region was taken and what he had seen')
    # ---- 34. ruling 3: only a hit from directly behind is from behind (15 degrees either side, experimental; the canon angle is DreLen's) ----
    def cone(bearing,half=15.0,mirror=False,flip=False,v=6.0,hit=True):
        """B0 runs at v into the standing non-carrier A0, arriving from 'bearing' degrees round from the way A0 faces (0 head-on, 180
        straight behind). mirror: from his other side. flip: the same on the other half of the field, A0 facing the other way."""
        m=kc({'blindside_rear_half_angle_deg':half});m.c3_reckless={'B0'};loose(m);f=-1.0 if flip else 1.0;A=kput(m,'A0',(50,50));A.facing=(f,0.0)
        th=math.radians(-bearing if mirror else bearing);ux,uy=f*math.cos(th),f*math.sin(th);B=kput(m,'B0',(50+ux*(2*A.radius+1.0),50+uy*(2*A.radius+1.0)),(-ux*v,-uy*v));ktop(m,'B0',v)
        pre=m.e.contact_legal(B,A,'block',reach=False);k=len(m.e.log)
        if not hit:return pre
        for i in range(40):
            ktick(m,{'B0':(50-ux*30,50-uy*30)},10)
            if count(m,'c3_collision',k):break
        return pre,[r for r in last(m,'c3_collision')['responsibility'] if r['player']=='B0'][0],fouls(m,k)
    c135=cone(135);c150=cone(150);c180=cone(180)
    ok(c135[0]==(True,'legal') and c135[1]['classification']=='legal' and not c135[2] and c150[1]['classification']=='legal' and not c150[2],'RULING 3: coming in from the back quarter is fair: material hits at 135 and at 150 degrees round from his front are lawful and not penalised')
    ok(c180[0]==(False,'blindside') and c180[1]['classification']=='blindside' and c180[2]==['blindside'],'RULING 3: a hit from directly behind is still from behind, and still a foul')
    ok(cone(164.5,hit=False)[0] and not cone(165.5,hit=False)[0] and cone(164.5,mirror=True,hit=False)[0] and not cone(165.5,mirror=True,hit=False)[0] and cone(164.5,flip=True,hit=False)[0] and not cone(165.5,flip=True,hit=False)[0] and cone(164.5,mirror=True,flip=True,hit=False)[0] and not cone(165.5,mirror=True,flip=True,hit=False)[0],'LEAD: the boundary at 165 degrees: half a degree in front of it is lawful and half a degree behind it is not, from either side and on either half of the field')
    a=cone(164.5);b=cone(165.5);ok(a[1]['classification']=='legal' and not a[2] and b[1]['classification']=='blindside' and b[2]==['blindside'] and near(a[1]['bearing_from_facing_deg'],164.5,2e-3) and near(b[1]['bearing_from_facing_deg'],165.5,2e-3),'the collision that actually happens is classed by the same line, and the record carries the bearing he came from')
    def edge(half):return [bb for bb in (100,120,134,136,149,151,164,166,169,171,180) if not cone(bb,half,hit=False)[0]]
    ok(edge(10.0)==[171,180] and edge(15.0)==[166,169,171,180] and edge(30.0)==[151,164,166,169,171,180] and edge(45.0)==[136,149,151,164,166,169,171,180] and edge(75.52248781407008)==[120,134,136,149,151,164,166,169,171,180],'LEAD: half-angles of 10, 15, 30 and 45 degrees put the line at 170, 165, 150 and 135; 75.5 is the retained Pocket 1.1 line at 104.5. Classification only: nothing else moves with the setting')
    m=kc();A=kput(m,'A0',(50,50));A.facing=(1.0,0.0);B=kput(m,'B0',(50-2*A.radius-.9,50));B.facing=(1.0,0.0);ex=(1.0,0.0);R=B.x-A.x
    on=lambda ang:(lambda u:(kput(m,'B0',(50+u[0]*2.0,50+u[1]*2.0)),m.e.contact_legal(m.s.players['B0'],A,'block',reach=False)[0])[1])((math.cos(math.radians(ang)),math.sin(math.radians(ang))))
    ok(on(165-1e-6) and not on(165+1e-6) and m.e.blind_cos==math.cos(math.radians(15.0)),'LEAD: the boundary convention. From behind means strictly inside the cone: the test is dot < -cos(15) x distance, so a bearing a millionth of a degree short of 165 is lawful and one a millionth past it is not')
    w=c180[1];ok(set(('initiated','material','classification','bearing_from_facing_deg'))<=set(w) and w['initiated'] and w['material'] and 'avoidability' in w and w['avoidability']=={'last_lawful_ms':None},'LEAD: the approach geometry is logged apart from initiation, materiality and avoidability, which are witnessed as before: straight in from behind was never lawful')
    def follow(bearing,rule=1,half=15.0):
        """B0 runs at 8 m/s at A0, who stands still; B0's line makes 'bearing' with A0's facing. Collision avoidance on. rule: the
        stopping-distance controller on or off. His speed 0.3 s on."""
        m=kc({'c3_follow_distance':rule,'blindside_rear_half_angle_deg':half});loose(m);A=kput(m,'A0',(50,50));A.facing=(1.0,0.0);th=math.radians(bearing);ux,uy=math.cos(th),math.sin(th)
        B=kput(m,'B0',(50+ux*4.0,50+uy*4.0),(-ux*8,-uy*8));ktop(m,'B0',8.0)
        for i in range(3):ktick(m,{'B0':(50.0,50.0)},100)
        return B.speed
    fo={(b_,r_):follow(b_,r_) for b_ in (180,150) for r_ in (1,0)};old=(follow(150,1,75.52248781407008),follow(150,0,75.52248781407008))
    ok(fo[(180,1)]<fo[(180,0)]-.5 and fo[(150,1)]==fo[(150,0)] and old[0]<old[1]-.5,'LEAD: the same line in legality and in avoidance. The controller that keeps a stopping distance behind a man still slows a runner coming up straight behind him; it no longer acts on one coming from the back quarter at 150 degrees, where under the retained line it did: '+str([round(x,2) for x in (fo[(180,1)],fo[(180,0)],fo[(150,1)],fo[(150,0)],old[0],old[1])]))
    m=kc();A=kput(m,'A0',(50,50),(6,0));kgive(m,'A0');B=kput(m,'B0',(48.9,50),(6,0));ok(m.e.contact_legal(B,A,'tackle',reach=False)[0],'unchanged: tackling the ball carrier from behind was and is lawful; the line applies to contact with a player who has no ball')
    # responsibility and avoidability inside the new cone (the two C3a3 regressions whose geometry sat at the old line)
    def shoved_c(v=8.0,run=6.0,gap=.15):
        """As the C3a3 'knocked sideways' case, but A1 knocks B0 along A0's back line by only a little, so that B0's own run then meets A0 inside the 15 degree cone."""
        m=kc();m.c3_reckless={'A1','B0'};loose(m);B=kput(m,'B0',(50,50));B.facing=(0.0,-1.0);r=B.radius;A=kput(m,'A0',(50+2*r+gap,50));A.facing=(1.0,0.0)
        A1=kput(m,'A1',(50,50-2*r-.05),(0,v));ktop(m,'A1',v);tg={'A1':(A1.x,A1.y),'B0':(99,B.y)};ktop(m,'B0',run);k=len(m.e.log)
        for i in range(6):ktick(m,tg,50)
        w=[x for r_ in m.e.log[k:] if r_['event']=='c3_collision' and r_['data']['a']=='A0' for x in r_['data']['responsibility'] if x['player']=='B0'];return m,k,(w[0] if w else None)
    best=None
    for v_ in (1.0,1.5,2.0,3.0):
        m,k,w=shoved_c(v=v_)
        if w and w['bearing_from_facing_deg']>=165:best=(m,k,w)
    m,k,w=best;rt=m.s.players['B0'].a.decision_speed
    ok(fouls(m,k)==['blindside'] and w['driven_approach_mps']==0 and w['voluntary_approach_mps']>1 and w['bearing_from_facing_deg']>=165 and (next(r['t_ms'] for r in m.e.log[k:] if r['event']=='foul')-1000)<1000*rt,'C3a3 regression inside the cone: knocked sideways a moment before, he then runs into the man\'s back himself within his reaction time, and is penalised. The sideways knock is no excuse')
    def round_c(radial,v=10.0,meet=170.0,start=155.0):
        """B0 meets the standing non-carrier A0 at 'meet' degrees round (inside the 15 degree cone). radial: straight in along that bearing.
        Otherwise he comes across from a point 'start' degrees round, in front of the line when the interval of the contact begins."""
        m=kc();m.c3_reckless={'B0'};loose(m);A=kput(m,'A0',(50,50));A.facing=(1.0,0.0);B=m.s.players['B0'];R=A.radius+B.radius;c=(math.cos(math.radians(meet)),math.sin(math.radians(meet)))
        st=(c[0]*(R+3.0),c[1]*(R+3.0)) if radial else (math.cos(math.radians(start))*(R+.5),math.sin(math.radians(start))*(R+.5));d=CORE.geometry.unit(c[0]*R-st[0],c[1]*R-st[1])
        kput(m,'B0',(50+st[0],50+st[1]),(d[0]*v,d[1]*v));ktop(m,'B0',v);k=len(m.e.log);tg=(50+st[0]+d[0]*40,50+st[1]+d[1]*40);pre=m.e.contact_legal(B,A,'block',reach=False)[1]
        for i in range(8):
            ktick(m,{'B0':tg},100)
            if count(m,'c3_collision',k):break
        return m,k,pre,[r for r in last(m,'c3_collision')['responsibility'] if r['player']=='B0'][0]
    m,k,pre,w=round_c(False);a=w.get('avoidability',{})
    ok(pre=='legal' and w['classification']=='blindside' and not fouls(m,k) and w['not_sanctioned']=='no_time_to_avoid' and a['last_lawful_ms']==a['state_at_ms']==1000 and 1000<a['change_seen_ms']<=1100 and a['gap_then_m']<a['stopping_gap_m'],'C3a3 regression inside the cone: he comes across in front of the 165 degree line and meets his man behind it within one interval. The change is witnessed at the contact and he had no room to stop: no foul')
    m,k,pre,w=round_c(True);ok(pre=='blindside' and fouls(m,k)==['blindside'] and w['avoidability']=={'last_lawful_ms':None},'and the same contact reached by coming straight in from behind the line is penalised: it was never lawful')
    # ---- 35. ruling 4: a carrier can work a grip loose; a contest, not a timer ----
    def wr(carrier=.68,holder=.68,mode='drive',effort=None,region='upper',v=6.0,ms=3000,vfree=None,cal=None,load=None,each=None):
        """A carrier runs at v with one defender alongside within reach; no pass is on. mode 'hang': the holder only hangs on.
        effort: None = the carrier's controller, 0 = a passive carrier. vfree: the carrier's own top speed, if he has pace in hand."""
        m=kc(cal);m.c3_fix_region=region;m.c3_fix_escape=effort;m.c3_fix_drive=-1.0 if mode=='hang' else None;s=m.s
        A=kput(m,'A0',(30,50),(v,0));ktop(m,'A0',vfree or v,True);kgive(m,'A0');A.a.strength=A.a.balance=carrier
        B=kput(m,'B0',(A.x-1.1,A.y+1.0),(v,0));B.a.tackling=B.a.strength=holder;ktop(m,'B0',v);t0=s.now;k=len(m.e.log);peak=0.0;gs=[]
        while s.now<t0+ms and s.ball.carrier=='A0' and A.posture=='upright':
            h=m.c3_holds.get(('B0','A0'))
            if h is None and s.now>t0+50:break
            if load is not None:A.bal_src={('test','x',True):load};A.bal_t0=s.now
            if h:peak=max(peak,h['g']);gs.append(h['g'])
            if each:each(m,h)
            ktick(m,{'A0':(99,50),'B0':(A.x,A.y)},10)
        return m,k,t0,peak,gs
    m=kc();m.c3_fix_region='upper';A=kput(m,'A0',(30,50),(6,0));ktop(m,'A0',6.0,True);kgive(m,'A0');A.a.strength=.9;A.a.balance=.8;A.fatigue=1.0;B=kput(m,'B0',(28.9,51.0),(6,0));B.a.strength=.4;ktop(m,'B0',6.0)
    ktick(m,{'A0':(99,50),'B0':(A.x,A.y)},10);h=m.c3_holds[('B0','A0')]
    ok(near(h['pry_N'],2500*1.4*1.0*1.3*1.0,1e-6) and near(h['break_rate'],4.0*h['pry_N']/(2500*.9),1e-9) and near(h['tear_rate'],4.0*(h['pry_N']/(2500*.9)-1),1e-9) and h['tear_rate']>0 and h['escape_ms']==10,'RULING 4: the prying force is escape_force_N x (0.5 + strength) x fatigue factor x (0.5 + balance) x (1 - balance load) x legs, and it loosens the grip at grip_overload_per_s x that force / the holder\'s full grip force. C3c2: the part of it beyond his full grip force tears the grip at grip_overload_per_s x (that ratio - 1)')
    def eq(carrier,holder=.68,effort=None,load=None,region='upper'):
        m,k,t0,peak,gs=wr(carrier,holder,'hang',effort,region,ms=2500,load=load);return gs[-1] if ('B0','A0') in m.c3_holds else 0.0 #C3c2: a hold thrown off is no grip
    line=[eq(c_) for c_ in (.1,.2,.3,.4,.5,.6,.7,.8,.9,1.0)]
    ok(all(b<a-.005 for a,b in zip(line,line[1:])),'LEAD: continuous, no dead zone. Against the same holder who only hangs on, every tenth more strength and balance leaves the grip lower, across the whole range of the carrier: '+str([round(x,3) for x in line]))
    hl=[eq(.68,h_) for h_ in (.3,.5,.68,.9)];ok(all(b>a+.02 for a,b in zip(hl,hl[1:])),'and the stronger and better the holder, the more grip he keeps against the same carrier: '+str([round(x,3) for x in hl]))
    pa,ac,off=eq(.68,effort=0),eq(.68),wr(.68,.68,'hang',None,ms=2500,cal={'c3c':0})[4][-1]
    ok(near(pa,off,1e-9) and ac<pa-.2,'LEAD: a passive carrier and one working to get free are different. Passive, the grip is exactly the C3b2 one; working, it is much lower: '+str((round(pa,3),round(ac,3))))
    ok(eq(.68,load=.5)>eq(.68,load=0.0)+.05 and eq(.68,load=.9)>eq(.68,load=.5)+.05,'the balance he has left counts: with his balance half loaded he pries half as hard and the grip is higher; nearly toppled, higher still')
    ok(eq(.68,region='lower')>ac+.03,'region: a lower hold takes his legs (by lower_hold_leg_factor x grip), so he pries less and it grips more than an upper hold')
    m,k,t0,peak,gs=wr(.68,.68,'hang',None,ms=10000);ok(('B0','A0') in m.c3_holds and near(gs[-1],gs[300],5e-3) and gs[-1]>.3 and not evs(m,'c3_grip_broken',k),'LEAD: no escape by timer. Ten seconds on, a reference carrier working against a reference holder who only hangs on has the same grip on him as after three: loosened (0.34 against 0.78; 0.41 in C3c1, before the tearing term), not broken and not off')
    m,k,t0,peak,gs=wr(.68,.68,'hang',0,ms=1500);A=m.s.players['A0'];ok(A.speed>5.9 and m.c3_bal(A)<.05,'LEAD: a holder who only hangs on gets no driving force from holding: the carrier is not slowed and his balance is not loaded')
    m0,k0,t00,p0,g0=wr(effort=0);m1,k1,t01,p1,g1=wr();a0=first(m0,'c3_grounding',k0);a1=first(m1,'c3_grounding',k1)
    ok(a0 and a1 and a0['data']['counted'] and a1['data']['counted'] and a1['t_ms']-t01>a0['t_ms']-t00+150 and near(a0['t_ms']-t00,first(wr(cal={'c3c':0})[0],'c3_grounding')['t_ms']-1000,1e-9),'LEAD: an effective drive still grounds him before he gets free. Reference against reference: brought down either way, later when he works against the grip ('+str((a0['t_ms']-t00,a1['t_ms']-t01))+' ms); passive, at exactly the C3b2 time')
    m,k,t0,peak,gs=wr(.9,.3,vfree=9.0);he=last(m,'c3_hold_end')
    ok(peak==0 and not first(m,'c3_grounding',k) and he['cause']=='fended_off' and he['grip_at_end']==0 and he['duration_ms']==0 and first(m,'c3_hold_detached',k)['data']['cause']=='fended_off' and not evs(m,'c3_grip_broken',k) and ('B0','A0') not in m.c3_holds and m.s.ball.carrier=='A0' and m.s.tackle_count==0 and m.stats['c3_grabs_fended_off']>=1 and m.stats['c3_holds_pried_off']==0,'RULING 4 (C3c2): a strong, well-balanced carrier against a weak tackler who only reaches for him: the grab never takes. His prying exceeds the tackler\'s full grip force by more than the tackler can re-close his hands, so there is no grip at all, nothing restrains him and he keeps the ball (C3c1: a grip under 0.3 until he ran out of reach)')
    # ---- 35b. C3c2 (the Lead's C3c1 audit): actual detachment. A grip worked below the threshold is one thing; a hold that is off is another ----
    def pry(carrier=.9,holder=.3,ms=1500,est=200,cal=None,region='upper',effort=1.0,mode='hang',after=None):
        """The Lead's escape bench: the carrier at 6 m/s, one defender alongside in reach at the same top speed, no strips. The hold
        is established for est ms with the carrier passive; then he works at it with the given effort. after(m): called every 10 ms from then."""
        m=kc({'fatigue_rate':0.0,**(cal or {})});m.c3_fix_region=region;m.c3_fix_drive=-1.0 if mode=='hang' else None;m.c3_fix_escape=0.0;s=m.s
        A=kput(m,'A0',(20,50),(6,0));A.a.strength=A.a.balance=carrier;B=kput(m,'B0',(18.9,51),(6,0));B.a.strength=B.a.tackling=holder;ktop(m,'A0',6.0,True);ktop(m,'B0',6.0);kgive(m,'A0')
        ktick(m,{'A0':(99,50),'B0':(A.x,A.y)},est);h=m.c3_holds[('B0','A0')];g0=h['g'];st=h['start'];m.c3_fix_escape=effort;t0=s.now;k=len(m.e.log);tr=[]
        while s.now<t0+ms and s.ball.carrier=='A0' and A.posture=='upright':
            ktick(m,{'A0':(99,50),'B0':(A.x,A.y)},10);hh=m.c3_holds.get(('B0','A0'));tr.append((s.now-t0,hh['g'] if hh else None,m.c3_rho(A,'pass'),A.speed))
            if after:after(m)
        return m,k,t0,g0,st,tr,A,B
    m,k,t0,g0,st,tr,A,B=pry();det=first(m,'c3_hold_detached',k);end=first(m,'c3_hold_end',k);brk=first(m,'c3_grip_broken',k);dd=det['data'];react=1000*B.a.decision_speed
    ok(g0>.3 and det and dd['cause']=='pried_off' and end['data']['cause']=='pried_off' and end['data']['grip_at_end']==0 and end['data']['start_ms']==st and near(end['data']['end_ms'],t0+dd['hold_ms']-(t0-st),1e-2) and end['t_ms']==det['t_ms'] and m.stats['c3_holds_pried_off']==1,'LEAD (C3c1 audit): a strong, well-balanced carrier (0.9) held by a weak tackler (0.3) who only hangs on. The material grip is worked down and the hold itself ENDS: a detachment record and the end of that hold, cause pried_off, grip zero, %.0f ms after he began'%(det['t_ms']-t0))
    ok(brk and brk['t_ms']<=det['t_ms'] and brk['data']['peak_grip']>=.3>brk['data']['grip'] and m.stats['c3_grips_broken']==1,'the two records are kept apart: c3_grip_broken says a material grip was worked below the tackle threshold; c3_hold_detached says the hold is off. Here the first comes with or before the second')
    ok(dd['force_ratio']>1 and near(dd['tear_rate_per_s'],4.0*(dd['force_ratio']-1),2e-3) and dd['tear_rate_per_s']>dd['holder_gain_per_s'] and near(dd['holder_full_grip_force_N'],2500*.8,1e-6),'by the stated law and nothing else: his prying force is %.2f times the holder\'s full grip force; the part beyond it tears the grip at %.2f a second, faster than the holder re-closes his hands (%.2f a second), so the grip reaches zero'%(dd['force_ratio'],dd['tear_rate_per_s'],dd['holder_gain_per_s']))
    gone=[x for x in tr if x[0]>det['t_ms']-t0+10];starts=[r for r in evs(m,'c3_hold_start',k)]
    ok(gone and all(x[2]==0 for x in gone) and min(x[3] for x in gone)>5.9 and A.posture=='upright' and m.s.ball.carrier=='A0' and m.s.tackle_count==0 and m.c3_bal(A)<.05,'LEAD: with the hold off its restraint and its coupling are gone: restraint on a pass is exactly zero from then on, he runs at his own speed, on his feet, with the ball')
    ok(starts and all(r['data']['start_ms']!=st for r in starts) and all(r['data']['ms_since_his_last_hold_was_thrown_off']>=react-1e-6 for r in starts) and near(starts[0]['data']['ms_since_his_last_hold_was_thrown_off'],react,1e-3),'LEAD: the holder does not get the same hold back. He can reach again only after his own reaction time (%.0f ms), to the instant, and what he takes then is a new record that says how long it is since he was thrown off'%react)
    ok(len(evs(m,'c3_hold_detached',k))==1+m.stats['c3_grabs_fended_off']>=3 and all(r['data']['cause']=='fended_off' and r['data']['peak_grip']==0 for r in evs(m,'c3_hold_detached',k)[1:]) and ('B0','A0') not in m.c3_holds,'while he goes on prying with his balance intact, each new grab is fended off with no grip: every attempt is in the log and none of them restrains him')
    def relent(m):
        if ('B0','A0') not in m.c3_holds:m.c3_fix_escape=0.0 #once he is free he stops prying
    m,k,t0,g0,st,tr,A,B=pry(ms=1500,after=relent);det=first(m,'c3_hold_detached',k);ns=[r for r in evs(m,'c3_hold_start',k)];h=m.c3_holds.get(('B0','A0'));regr=[x for x in tr if x[1] is not None and x[0]>det['t_ms']-t0]
    ok(det and len(ns)==1 and h is not None and near(h['start'],ns[0]['data']['start_ms'],1e-3) and ns[0]['data']['start_ms']>det['t_ms']+react-2 and regr[0][1]<.05 and all(b[1]>=a[1] for a,b in zip(regr,regr[1:])) and h['g']>.6 and len(evs(m,'c3_hold_detached',k))==1,'LEAD: reacquisition is separately earned. If he stops prying once he is free, the holder takes a NEW hold after his reaction time, and its grip builds from zero by the ordinary law: '+str([round(x[1],2) for x in regr[:40:8]]))
    m,k,t0,g0,st,tr,A,B=pry(effort=0.0,ms=6000)
    ok(not evs(m,'c3_hold_detached',k) and not evs(m,'c3_grip_broken',k) and ('B0','A0') in m.c3_holds and tr[-1][1]>=g0 and near(tr[-1][1],tr[300][1],1e-3) and m.stats['c3_holds_pried_off']==0,'LEAD: a passive carrier is never freed, however strong. Six seconds on the same weak tackler still has him, by the same grip as after three: no escape by timer, no automatic escape')
    m,k,t0,g0,st,tr,A,B=pry(carrier=.5,holder=.5,ms=6000)
    ok(not evs(m,'c3_hold_detached',k) and ('B0','A0') in m.c3_holds and near(tr[-1][1],tr[300][1],1e-3) and tr[-1][1]>.3 and near(m.c3_holds[('B0','A0')]['tear_rate'],0,1e-12),'equal reference athletes: his prying does not exceed the holder\'s full grip force, nothing tears, the grip is loosened exactly as in C3c1 and the hold stays on')
    m,k,t0,g0,st,tr,A,B=pry(carrier=.68,holder=.5,ms=4000);h=m.c3_holds.get(('B0','A0'))
    ok(h is not None and not evs(m,'c3_hold_detached',k) and 0<h['g']<.3 and h['tear_rate']>0 and near(tr[-1][2],h['g']/.5,1e-9) and tr[-1][2]>.3 and near(tr[-1][1],tr[200][1],5e-3),'LEAD (below-threshold restraint): a grip worked below the tackle threshold but not to zero is still a hold. Carrier 0.68 on holder 0.5: grip %.2f, not material, and it still restrains a pass by %.2f. It is not logged as detached and it does not run out with time'%(h['g'],tr[-1][2]))
    m,k,t0,g0,st,tr,A,B=pry(carrier=.9,holder=.3,ms=4000,est=80);det=first(m,'c3_hold_detached',k)
    ok(g0<.3 and tr[0][2]>0 and det and det['data']['cause']=='pried_off' and 0<det['data']['peak_grip']<.3 and not evs(m,'c3_grip_broken',k) and all(x[2]==0 for x in tr if x[0]>det['t_ms']-t0+10),'LEAD (below-threshold restraint): a hold that never became material can be thrown off too. It restrained him while it lasted; once it is off the restraint is zero. No broken-grip record is made, because no material grip was broken: only the detachment')
    line=[]
    for c_ in (.5,.6,.7,.8,.9,1.0):
        m,k,t0,g0,st,tr,A,B=pry(carrier=c_,holder=.5,ms=3000);det=first(m,'c3_hold_detached',k);h=m.c3_holds.get(('B0','A0'));line.append((c_,round(h['g'],3) if h and not det else 0.0,det['t_ms']-t0 if det else None))
    ok(all(b[1]<=a[1] for a,b in zip(line,line[1:])) and line[0][2] is None and line[1][2] is None and line[-1][2] is not None and all(a[2] is None or (b[2] is not None and b[2]<=a[2]) for a,b in zip(line,line[1:])) and len({x[1] for x in line})>=4,'continuous, and not all-or-nothing: against one holder (0.5) each tenth of carrier strength and balance leaves less grip, and past the point where the tearing outruns his hands the hold comes off, sooner the stronger the carrier. (carrier, grip kept, ms to throw it off): '+str(line))
    hl=[]
    for h_ in (.3,.5,.68,.9):
        m,k,t0,g0,st,tr,A,B=pry(carrier=.9,holder=h_,ms=3000);det=first(m,'c3_hold_detached',k);hl.append((h_,det['t_ms']-t0 if det else None))
    ok(hl[0][1] is not None and hl[1][1] is not None and hl[0][1]<hl[1][1] and hl[2][1] is None and hl[3][1] is None,'and the holder counts: a 0.9 carrier throws off a 0.3 holder sooner than a 0.5 one, and does not throw off a 0.68 or a 0.9 holder at all (ms to throw off): '+str(hl))
    tl=[]
    for sub in (2,5,10,20):
        m,k,t0,g0,st,tr,A,B=pry(cal={'c3_substep_ms':sub},ms=400);tl.append(first(m,'c3_hold_detached',k)['data']['hold_ms'])
    ok(max(tl[:3])-min(tl[:3])<=10 and tl[3]-tl[0]<=25 and all(b>=a for a,b in zip(tl,tl[1:])),'the instant the grip reaches zero is solved on the grip law inside each substep, but the forces that feed that law are refreshed once a substep. At contact substeps of 2, 5, 10 and 20 ms the hold comes off '+str([round(x-200,1) for x in tl])+' ms after he begins: within one substep of each other up to the default 10 ms, later at the 20 ms comparison setting. A declared limit, like the one already recorded for upper-hold tackles')
    m,k,t0,g0,st,tr,A,B=pry(mode='drive',carrier=.68,holder=.68,ms=3000);gr=first(m,'c3_grounding',k)
    ok(gr and gr['data']['counted'] and not evs(m,'c3_hold_detached',k) and A.posture=='grounded','LEAD: an effective drive still grounds him first. Reference carrier, reference tackler who drives: he pries, the grip is loosened, the drive loads his balance, and he is tackled with the hold never off')
    def race(topple):
        """A grounding and a detachment in ONE contact substep. A strong tackler (B1) has an established passive hold; a weak one (B0)
        has had his hands on the carrier for 5 ms. Then the carrier pries, B1 drives, and the topple time is cut so short that the
        drive grounds him within the same 10 ms substep in which B0's grip would reach zero. Staged to exercise the ordering only."""
        m=kc({'fatigue_rate':0.0});m.c3_fix_region='upper';m.c3_fix_drive=-1.0;m.c3_fix_escape=0.0;s=m.s
        A=kput(m,'A0',(20,50),(6,0));A.a.strength=A.a.balance=.9;ktop(m,'A0',6.0,True);kgive(m,'A0');B1=kput(m,'B1',(18.9,49),(6,0));B1.a.strength=B1.a.tackling=.9;ktop(m,'B1',6.0)
        B0=kput(m,'B0',(10,80),(6,0));B0.a.strength=B0.a.tackling=.3;ktop(m,'B0',6.0);T=lambda:{'A0':(99,50),'B0':(A.x,A.y),'B1':(A.x,A.y)}
        ktick(m,{'A0':(99,50),'B1':(A.x,A.y)},195);kput(m,'B0',(A.x-1.1,A.y+1.0),(A.vx,A.vy));ktick(m,T(),5)
        m.c3_fix_escape=1.0;m.c3_fix_drive=1.0;m.assume['topple_time_s']=topple;t0=s.now;k=len(m.e.log);ktick(m,T(),10);return m,k,t0,A
    m,k,t0,A=race(.02);det=first(m,'c3_hold_detached',k);gr=first(m,'c3_grounding',k);e0=next(r for r in evs(m,'c3_hold_end',k) if r['data']['actor']=='B0')['data'];e1=next(r for r in evs(m,'c3_hold_end',k) if r['data']['actor']=='B1')['data']
    ok(det and gr and det['data']['actor']=='B0' and e0['cause']=='pried_off' and e0['grip_at_end']==0 and e1['cause']=='carrier_grounded' and t0<e0['end_ms']<e1['end_ms']<t0+10 and gr['data']['counted'] and A.posture=='grounded','ordering inside one substep, detachment first: the weak hold reaches zero grip %.1f ms in and is off; the drive grounds him %.1f ms in. Both stand, each at its own instant'%(e0['end_ms']-t0,e1['end_ms']-t0))
    m,k,t0,A=race(.01);gr=first(m,'c3_grounding',k);e0=next(r for r in evs(m,'c3_hold_end',k) if r['data']['actor']=='B0')['data'];e1=next(r for r in evs(m,'c3_hold_end',k) if r['data']['actor']=='B1')['data']
    ok(gr and gr['data']['counted'] and not evs(m,'c3_hold_detached',k) and e0['cause']=='carrier_grounded'==e1['cause'] and e0['end_ms']==e1['end_ms']<t0+10 and e0['grip_at_end']>0 and e0['reach_ms']<=e0['duration_ms']+1 and m.stats['c3_holds_pried_off']==0 and not m.c3_off,'LEAD: a drive that grounds him first is preserved. Grounding first: he is down %.1f ms in, before the weak grip would have reached zero. Nothing after the grounding is applied: that hold was still on him (grip %.3f), it ends with the tackle, and no detachment is recorded'%(e1['end_ms']-t0,e0['grip_at_end']))
    m,k,t0,g0,st,tr,A,B=pry(ms=150);ok(('B0','A0') in m.c3_off,'bookkeeping: the thrown-off record exists while he has the ball')
    z=m.c3_save();m.c3_off[('B9','A0')]=1.0;m.c3_restore(z);ok(('B9','A0') not in m.c3_off and ('B0','A0') in m.c3_off,'and is part of the state an interval can be recomputed from')
    kgive(m,'A1');m.c3_reconcile();ok(not m.c3_off,'and ends with his control of the ball: a later carrier starts clean')
    m,k,t0,g0,st,tr,A,B=pry(cal={'escape_force_N':0.0},ms=3000);ok(not evs(m,'c3_hold_detached',k) and not m.c3_off and tr[-1][1]>=g0,'with no prying force (the neutral setting) nothing is ever thrown off')
    m,k,t0,full=hp(holder=.3,ms=1200,cal={'escape_force_N':4000.0});gb=first(m,'c3_grip_broken',k);tk_=first(m,'c3_tuck',k)
    ok(tk_ and gb and gb['t_ms']>tk_['t_ms'] and gb['data']['grip']<.3<=gb['data']['peak_grip'] and gb['data']['prying_force_N']>0 and gb['data']['break_rate_per_s']>0 and gb['data']['escape_ms']>0 and m.stats['c3_grips_broken']>=1,'a material grip worked back below the tackle threshold is logged as broken, with the prying force and rate at that moment (here: wrapped in his wind-up by a weak tackler, he tucks the ball and then breaks the grip; prying force at the top of its declared range)')
    eff={}
    def watch(m,h):
        if h is not None:eff.setdefault('A0' in m.pending_ball_actions,[]).append(h.get('break_rate',0.))
    m,k,t0,full=hp(ms=600,each=watch);ok(set(eff[True])=={0.0} and max(eff[False])>1,'the placeholder controller: he does not pry while his arms are busy with a wind-up; from the tuck on he does')
    # ---- 36. transitions ----
    def gone(m):
        if m.s.now>=1150 and ('B0','A0') in m.c3_holds:kput(m,'B0',(10,10))
        return False
    m,k,t0,full=hp(stop=gone);r=thrown(m,k);he=last(m,'c3_hold_end')
    ok(r is not None and first(m,'c3_tuck',k) is None and he['cause']=='out_of_reach' and r['t_ms']>he['end_ms'] and 0<m.c3_stall['A0']<full and not count(m,'c3_restraint',k),'LEAD: the hold is lost during the wind-up. What it cost stays counted, but nothing more is added; the wind-up runs on at its ordinary rate and the pass is released, unrestrained')
    def frozen(m):
        B=m.s.players['B0']
        if m.s.now>=1150 and not B.frozen(m.s.now):B.freeze_until=m.s.now+3000;m.c3_reconcile()
        return False
    m,k,t0,full=hp(stop=frozen);r=thrown(m,k);he=last(m,'c3_hold_end')
    ok(r is not None and first(m,'c3_tuck',k) is None and he['cause']=='ineligible' and first(m,'strip',k) is None,'LEAD: the holder is frozen during the wind-up. The hold ends as it did in C3a (ineligible), the pin with it, and the pass is released')
    def tie(r_):
        m=kc();m.c3_fix_withhold=False;A=kput(m,'A0',(40,50),(6,0));ktop(m,'A0',6.0,True);kgive(m,'A0');R=kput(m,'A1',(46,58),(6,0));ktop(m,'A1',6.0);m.c3_rho=lambda p_,kind:r_
        kput(m,'B0',(38.9,51.0),(6,0));ktop(m,'B0',6.0);m.c3_fix_drive=-1.0;m.make_pass(A,R,'pass');full=m.c3_dur['A0'];k=len(m.e.log)
        for i in range(80):
            ktick(m,{'A0':(99,50),'A1':(99,58),'B0':(A.x,A.y)},10)
            if m.s.ball.carrier!='A0' or first(m,'c3_tuck',k):break
        return m,k,full
    m,k,full=tie(.49);r=thrown(m,k);ok(r is not None and first(m,'c3_tuck',k) is None and abs(r['t_ms']-1000-full/.51)<=1.5 and near(m.c3_stall['A0'],.49*full/.51,1e-3),'LEAD: abandonment against the scheduled release. At a steady restraint of 0.49 the wind-up finishes first (after its length / 0.51) and the pass is released')
    m,k,full=tie(.51);tk_=first(m,'c3_tuck',k);ok(thrown(m,k) is None and tk_ and abs(tk_['t_ms']-1000-full/.51)<=1.5 and near(tk_['data']['stalled_ms'],full,1e-6),'at 0.51 the stalled time reaches the limit first (after its length / 0.51) and the ball is tucked: whichever instant comes first is the one that happens')
    m,k,full=tie(.5);ok(thrown(m,k) is not None and first(m,'c3_tuck',k) is None,'at exactly 0.5 both fall at the same instant, and the release has precedence')
    class Late:
        """A contact stream that draws a strip (0.0) only in a drift that ends at or after the given match time."""
        def __init__(self,m,at):self.m=m;self.at=at;self.hits=0
        def random(self):
            late=self.m.s.now+self.m.c3_t*1000>=self.at-1e-6;self.hits+=late;return 0.0 if late else .999
        def getstate(self):return self.hits
        def setstate(self,n):self.hits=n
    def strip_at_grounding(c3c):
        req='first_touch' if c3c else None;m,k,t0,full=hp(cal={'c3c':c3c},request=req,ms=2000);tg=first(m,'c3_grounding',k)['data']['t_ms']
        def arm(m,h):
            if not isinstance(m.rng['contact'],Late):m.rng['contact']=Late(m,tg)
        m,k,t0,full=hp(cal={'c3c':c3c},request=req,strips=True,ms=2000,each=arm);return m,k,tg
    m,k,tg=strip_at_grounding(1);m0,k0,tg0=strip_at_grounding(0)
    ok(near(first(m,'c3_grounding',k)['data']['t_ms'],tg,1e-9) and first(m,'strip',k) is None and m.stats['c3_strips_overtaken_by_grounding']==1 and near(first(m0,'c3_grounding',k0)['data']['t_ms'],tg0,1e-9) and first(m0,'strip',k0) is None and m0.stats['c3_strips_overtaken_by_grounding']==1,'LEAD: strip against grounding. A strip drawn in the drift in which he goes down does not happen: the grounding comes first, at the same instant as with no strip drawn, with C3c as without it')
    m,k,t0,full=hp();s=m.s;tc=last(m,'tackle_count')
    ok(s.tackle_count==1 and tc['count_to']==1 and tc['count_from']==0 and tc['procedure']=='live_recovery' and s.recovery is not None and s.owner=='A' and s.phase==AWARD,'LEAD: continuation. Tucked and then tackled, it is the attack\'s first tackle: count one, the live recovery is awarded and the possession continues, exactly as for any first tackle')
    # ---- 37. the corrected-C3b counterexamples and the retained witnesses, with C3c on (the helpers above, rerun) ----
    C3B_=C3CAL;C3CAL={**C3B_,'c3c':1}
    m,k,still,w,dt_=fresh();a=w['avoidability']
    ok(still and fouls(m,k)==['blindside'] and a['stopping_gap_m']==0 and a['approach_then_mps']==0 and dt_<300 and w['bearing_from_facing_deg']==180.0,'C3b2 correction 1 with C3c on: a defender standing still at the change who then sets off into the passer\'s back inside his reaction time is penalised (straight behind, inside the cone)')
    m,k,w,at=from_rest(.3);ok(not fouls(m,k) and w['not_sanctioned']=='no_time_to_avoid' and at<300,'and the genuine case is still excused: already accelerating at the carrier when he became protected, 0.3 m away')
    m,A1,j,gx,sg=zst(v=(-10.0,0.0));ok(freet(m,A1,j,650.0)>1500 and m.e.exit_routes(A1,j,650.0)[1:]==(None,0),'C3b2 correction 2 with C3c on: running into the zone at 10 m/s he cannot be out in the time, and no route is practicable')
    m,A1,j,k,first_,second,routes=two_contacts(50);x=lastev(m,'exit_obstruction',k)['data']
    ok(x['by']=='B1' and x['exit']['denied_ms']==599 and x['exit']['route_open_ms']==50 and m.s.owner=='A','C3b2 correction 3 with C3c on: an opening of 50 ms does not excuse the second defender who shuts every lane; only the denied time is restored')
    f1,w1=after_stop(True);f0,w0=after_stop(False);ok(f1==f0==['blindside'] and w1['driven_approach_mps']==0,'the motion witness with C3c on: a cancelled push does not excuse a fresh run into a back')
    m,k,w=shoved();ok(not fouls(m,k) and w['not_sanctioned']=='carried_by_another_contact' and w['driven_by']==['A1'] and w['bearing_from_facing_deg']>165,'and a real surviving push still does: knocked straight into a back by a collision a moment earlier, no foul')
    C3CAL=C3B_
    # ---- 38. settings, marker, measurement, a real match ----
    new=('c3c','arm_pin_grip','tuck_after_delay_frac','strip_in_motion_factor','c3_region_policy','blindside_rear_half_angle_deg','escape_force_N')
    ok(all(k_ in C3_RANGES and k_ in CALIBRATION and C3_RANGES[k_][0]<=CALIBRATION[k_]<=C3_RANGES[k_][1] for k_ in new) and CALIBRATION['blindside_rear_half_angle_deg']==15.0 and CALIBRATION['escape_force_N']==CALIBRATION['grip_force_N'],'every C3c setting is in CALIBRATION with a declared range and lies inside it; the rear half-angle is 15 degrees and the prying force equals the grip force, by declared assumption')
    def bad(**c):
        try:configuration(SETTINGS,1,{**C3B_,'c3c':1,**c});return False
        except ValueError:return True
    ok(bad(arm_pin_grip=0) and bad(arm_pin_grip=1.2) and bad(strip_in_motion_factor=.5) and bad(blindside_rear_half_angle_deg=0) and bad(blindside_rear_half_angle_deg=95) and bad(escape_force_N=-1) and bad(tuck_after_delay_frac=-1) and bad(c3c=2) and not bad(),'settings outside their meaning are refused')
    m=kc();mk=evs(m,'c3c_rules');m0=kb();ok(len(mk)==1 and mk[0]['data']['blindside_rear_half_angle_deg']==15.0 and mk[0]['data']['escape_force_N']==2500.0 and not evs(m0,'c3c_rules') and m0.c3c is False and m0.e.blind_cos==.25 and m.e.blind_cos==math.cos(math.radians(15.0)),'a C3c match marks its log with the C3c settings; with c3c off there is no marker and the retained rear line is in force')
    m,k,t0,full=hp();M=measure_c3(m.e.log);pe=M['pinning_and_escape'];M0=measure_c3(kb().e.log)
    ok(M['c3c_witness_in_log'] and pe['tucks']==1 and near(pe['tuck_stalled_ms']['max'],full,1e-3) and pe['hold_region_by_what_the_defender_saw']['upper']=={'pass_open':1} and pe['releases_made_under_restraint']==0 and pe['strips_in_a_pinned_wind_up']==0 and pe['escape_effort_ms_per_hold']['max']>300 and M0['pinning_and_escape']=='unavailable' and M0['approach_bearing']=='unavailable' and M0['c3c_witness_in_log'] is False,'M1.4 carries the C3c measures (tucks, withheld releases, strips in a pinned wind-up, grips broken, what the defender saw, time spent prying); from a log without the C3c marker they are unavailable, never zero')
    c=cone(170);Mc=measure_c3(kc().e.log+[{'event':'c3_collision','data':{'responsibility':[c[1]],'impulse_Ns':1.0,'closing_mps':1.0,'shock_a':0.1,'shock_b':0.1}}])
    ok(Mc['approach_bearing']['of_material_initiated_contacts']=={'ahead_0_to_90':0,'side_rear_90_to_135':0,'rear_quarter_135_to_165':0,'rear_165_to_180':1} and Mc['approach_bearing']['classed_blindside']==1,'and where material contacts came from, by bearing')
    ts=[]
    for sub in (2,5,10):
        m,k,t0,peak,gs=wr(cal={'c3_substep_ms':sub});ts.append(first(m,'c3_grounding',k)['data']['t_ms']-t0)
    ok(max(ts)-min(ts)<=.02*ts[1],'substeps of 2, 5 and 10 ms: the same tackle against a carrier working at the grip completes within 2 percent of the same time: '+str([round(x) for x in ts]))
    rm=CORE.match.Match(configuration({**SETTINGS,'period_seconds':240,'periods':1},11,{**C3B_,'c3c':1}));ends=[]
    while rm.s.phase!=Ty.Phase.FINAL:
        k=len(rm.e.log);rm.step();ends+=[r for r in rm.e.log[k:] if r['event']=='c3_hold_end']
        if rm.s.live_ms>=240000:break
    over=[r['data']['reach_ms']-r['data']['duration_ms'] for r in ends if r['data']['reach_ms']>r['data']['duration_ms']+1e-6]
    ok(len(ends)>5 and all(r['data']['end_ms']<=r['t_ms']+1e-6 and 0<=r['data']['escape_effort_ms']<=r['data']['reach_ms']+2e-3 and 0<=r['data']['wind_up_under_this_upper_hold_ms']<=r['data']['reach_ms']+2e-3 for r in ends) and rm.stats['c3_recompute_unconverged']==0,'a real match with C3c on: on every hold record the time spent prying and the time in a pinned wind-up do not exceed the time in reach, no hold is reported to end after the time it is logged, and no interval failed to converge ('+str(len(ends))+' holds)')
    ok(len(over)>=1 and max(over)<=1+1e-6,'FOUND, inherited from C3a and NOT changed here: the C3a check above says a hold\'s time in reach never exceeds its duration. Over a longer match that is false by up to one millisecond, with C3c on or off: when a ball event (here a boundary) ends the possession, the hold is stamped as ending at the event and the interval that contains it runs up to one millisecond past it, the clock\'s declared resolution. The excess is never more than that: '+str([round(x,3) for x in over]))
    # ================= C4.0: terminal processing, and Keeper Zone violations as ruled by DreLen on 7 October =================
    # Every scenario above ran with c4_zone = 0: each describes the zone consequences of its own checkpoint, and all still hold.
    # The engine cases below run on the replay contact path (the contact model has no part in them) with the ruling on.
    Z4={**LEGACY,'c4_zone':1};FINAL=Ty.Phase.FINAL;PEN=Ty.Phase.PENALTY
    def z4(cal=None,carrier_at=(50.0,50.0),p_ms=30000,**pos):
        """Team A in possession, attacking zone 1 (x = 100). Field players parked outside both zones. Named players placed."""
        m=CORE.match.Match(configuration({**SETTINGS,**C2R,'archery':False},1,{**Z4,**(cal or {})}));s=m.s
        s.phase=LIVE;s.now=1000;s.owner='A';s.opening_team='A';s.alternate='B';s.opening_deadline=None;s.opening_touched=True
        for q in s.players.values():
            if q.active and q.role=='field':put(m,q.id,(30.0 if q.team=='A' else 70.0,5.0+10.0*int(q.id[1:])))
        put(m,'A0',carrier_at);give(m,'A0');s.possession_ms=p_ms
        for pid,xy in pos.items():put(m,pid,xy)
        return m
    def zv(m,k=0):return[r['data'] for r in m.e.log[k:] if r['event']=='zone_violation']
    def names(m,k=0):return[r['event'] for r in m.e.log[k:]]
    def recs(m,name,k=0):return[r for r in m.e.log[k:] if r['event']==name]
    def nodisc(m,k=0):return not any(r['event'] in('warning','discipline') for r in m.e.log[k:]) and not m.e.debts and not m.e.pending_discipline
    def frozen_record(m):return json.dumps(m.e.terminal_record(),sort_keys=True)

    # ---- 40. terminal processing: one result, committed once ----
    E=CORE.engine;meths=[n for n,f in vars(E.Engine).items() if callable(f) and not n.startswith('__')]
    ok(set(meths)==set(E.FINAL_GUARDED)|set(E.FINAL_READ_ONLY) and not set(E.FINAL_GUARDED)&set(E.FINAL_READ_ONLY) and all(getattr(vars(E.Engine)[n],'guarded',False) for n in E.FINAL_GUARDED) and len(E.FINAL_GUARDED)>80,'every Engine method is either guarded against a completed match or on the declared read-only list')
    ok(all(n in E.FINAL_GUARDED for n in('award','discipline','flush_discipline','forfeit','complete','foul','elapse','advance','batch','dispatch','release','restart_release','finish_penalty','start_penalty','reset_penalty','resume_recovery','recall_advantage','end_period','resolve_timers','new_owner','sub','freeze','goal','boundary')),'the callers named in the audit are all guarded')
    def poke(m):
        """Everything a caller might still ask of a finished match. None of it may change the terminal record."""
        e=m.e;s=m.s
        for f in(lambda:e.forfeit('A','later_call'),lambda:e.forfeit('B','later_call'),lambda:e.complete('regulation'),lambda:e.complete('forfeit','B'),lambda:e.award('B',50,50,'foul',foul=True),lambda:e.award('A',40,40,'boundary',fresh=True),
                 lambda:e.discipline('B2','minor'),lambda:e.discipline('A2','major'),lambda:e.flush_discipline(),lambda:e.foul('B4',None,'hold',major=True),lambda:e.foul('A4','B4','illegal_tackle',penalty=True),lambda:e.start_penalty('A'),
                 lambda:e.finish_penalty(5),lambda:e.penalty_goal('A',5),lambda:e.release('A0',(10.0,0.0,2.0),'pass'),lambda:e.restart_release('A1',(5.0,0.0,2.0)),lambda:e.ready('A1'),lambda:e.resume_recovery(),lambda:e.recall_advantage(),
                 lambda:e.end_period(),lambda:e.clock_expiry(),lambda:e.elapse(1000),lambda:e.advance(5000),lambda:e.resolve_timers(),lambda:e.new_owner('B','control'),lambda:e.acquire('B1'),lambda:e.goal('B',50,1),lambda:e.boundary(101,50),
                 lambda:e.batch([Ty.Event('foul','B5',data={'reason':'hold'})]),lambda:e.dispatch(Ty.Event('clock')),lambda:e.sub('A5','A12'),lambda:e.freeze('A3'),lambda:e.suspend('late'),lambda:e.timeout('A'),lambda:e.count('pass_attempts'),lambda:e.count('audit_after_final'),lambda:e.emit('late_record','none')):
            f()
        for _ in range(30):m.step()
        m.run_for(5);a=m.summary();b=m.summary();return a==b
    def finished(m,method,winner,forfeits=0):
        s=m.s;n=names(m);before=frozen_record(m);same=poke(m)
        return s.phase==FINAL and s.result['method']==method and s.result['winner']==winner and n.count('match_complete')==1 and n.count('forfeit')==forfeits and n[-1]=='match_complete' and m.e.final_seq==m.e.log[-1]['id'] and frozen_record(m)==before and same and s.restart is None
    m=CORE.match.Match(configuration({**SETTINGS,**C2R,'period_seconds':10,'periods':1},3,C4CAL));s=m.s
    while s.game_ms>1500:m.step()
    s.score={'A':3,'B':1};m.run()
    ok(finished(m,'regulation','A') and all(not k_.startswith('emit:') or k_=='emit:late_record' for k_ in m.e.final_refused),'ordinary completion of a real match: one match_complete, no forfeit, nothing after it, and stepping, export and thirty-five later calls leave the record as it was')
    m=z4();s=m.s;s.regulation_periods=4;s.period=4;s.game_ms=0;s.score={'A':7,'B':4};k=len(m.e.log);m.e.end_period()
    ok(finished(m,'regulation','A') and names(m,k)==['period_end','match_complete'] and m.e.final_refused.get('award',0)>=2 and m.e.final_refused.get('forfeit',0)>=2,'a decided final horn: period_end, match_complete, and every later call is refused and counted')
    # the fault found in the C2 reference match (seed 7): five minors queued behind advantages, administered at one stoppage
    def queued(order,already=3,team='B'):
        m=z4();s=m.s
        for i in range(already):m.e.discipline(team+str(5+i),'minor')
        m.e.pending_discipline=[(pid,'minor',False) for pid in order];return m
    m=queued(['B1','B2','B3','B4','B8'],already=0);s=m.s;s.score={'A':3,'B':9};k=len(m.e.log);m.e.award('B',95.0,23.4,'boundary');n=names(m,k)
    ok(n==['possession_change','occupancy_cleared']+['discipline']*5+['forfeit','match_complete'] and finished(m,'forfeit','A',1) and s.score=={'B':0,'A':5} and 'restart_awarded' not in n and s.stoppages==1,'the seed-7 tail: all five sanctions go on the record, then one forfeit and one match_complete; no restart is awarded and nothing follows (it was three forfeits, three completions and a restart)')
    ok([r['data']['player'] for r in recs(m,'discipline',k)]==['B1','B2','B3','B4','B8'] and len(m.e.debts)==5,'every queued sanction was administered before the ground to end the match was judged')
    # sanctions queued behind an advantage when the match ends another way
    m=queued(['B3'],already=0);s=m.s;k=len(m.e.log);m.e.forfeit('A','no_restart_taker');d=recs(m,'sanctions_not_administered',k)
    ok(names(m,k)==['forfeit','sanctions_not_administered','match_complete'] and d[0]['data']['sanctions']==[['B3','minor']] and s.players['B3'].minor_count==0 and finished(m,'forfeit','B',1) and not m.e.pending_discipline,'a forfeit while a sanction is queued behind an advantage: the sanction is written to the record, changes no count, and is not left waiting')
    def horn(scoreline,period=4):
        m=queued(['B1','B2']);s=m.s;s.regulation_periods=4;s.period=period;s.game_ms=0;s.score=dict(scoreline);k=len(m.e.log);m.e.end_period();return m,k
    m,k=horn({'A':6,'B':2})
    ok(names(m,k)==['discipline','discipline','forfeit','match_complete'] and finished(m,'forfeit','A',1) and m.s.score=={'A':6,'B':2} and 'period_end' not in names(m,k),'r2 (the Lead\'s audit): sanctions administered at a final horn are judged before the period is completed, as in accepted C3: below the minimum, the team forfeits even at a horn that would decide the match. No exemption; that amendment is DreLen\'s')
    m,k=horn({'A':2,'B':6});ok(finished(m,'forfeit','A',1) and m.s.score=={'B':0,'A':5},'and when the team below the minimum was ahead on the field: the 5-0 administrative result (rulebook 18.6)')
    m,k=horn({'A':4,'B':4});ok(names(m,k)==['discipline','discipline','forfeit','match_complete'] and finished(m,'forfeit','A',1) and m.s.period==4,'a level final horn: the same, and no overtime is set up')
    m,k=horn({'A':6,'B':2},period=2);ok(names(m,k)==['discipline','discipline','forfeit','match_complete'] and finished(m,'forfeit','A',1) and m.s.period==2 and m.s.restart is None,'the same at a half-time horn: no third period is opened')
    m=queued(['B1']);s=m.s;s.shootout={'attempts':{'A':5,'B':5},'goals':{'A':3,'B':2},'used':{'A':[],'B':[]},'first':'A'};k=len(m.e.log);m.e.next_shootout()
    ok(names(m,k)==['sanctions_not_administered','match_complete'] and finished(m,'shootout','A') and s.result['shootout']=={'A':3,'B':2} and s.players['B1'].minor_count==0,'a shoot-out decided with a sanction still queued')
    # competing grounds at one instant: judged together, never by position in a queue
    def both(order):
        m=z4();s=m.s
        for t in('A','B'):
            for i in range(3):m.e.discipline(t+str(5+i),'minor')
        m.e.pending_discipline=[(pid,'minor',False) for pid in order];k=len(m.e.log);m.e.award('A',50,50,'boundary');return m,k
    m,k=both(['A1','B1']);m2,k2=both(['B1','A1'])
    ok(names(m,k)==['discipline','discipline','abandoned','match_complete'] and finished(m,'abandoned_replay',None) and finished(m2,'abandoned_replay',None) and recs(m,'abandoned',k)[0]['data']['reason']=='both_teams_unable_to_continue' and m.s.score==m2.s.score=={'A':0,'B':0},'DECLARED PRECEDENCE: both teams below the minimum at one stoppage is an abandonment for replay with no winner (rulebook 1.4, 18.8), whichever sanction was queued first')
    def one_side(order):
        m=queued([],already=3);m.e.pending_discipline=[(pid,'minor',False) for pid in order];k=len(m.e.log);m.e.award('A',50,50,'boundary');return m,k
    m,k=one_side(['A1','B1']);m2,k2=one_side(['B1','A1'])
    ok(finished(m,'forfeit','A',1) and finished(m2,'forfeit','A',1) and names(m,k).count('discipline')==2==names(m2,k2).count('discipline'),'one team below the minimum: it forfeits, and the other team\'s sanction of the same stoppage is on the record first either way')
    m=z4();s=m.s
    for pid in('A5','A6','A7','B5','B6','B7'):m.e.discipline(pid,'minor')
    k=len(m.e.log);m.e.batch([Ty.Event('foul','A1',data={'reason':'late_hold'}),Ty.Event('foul','B1',data={'reason':'late_hold'})])
    ok(finished(m,'abandoned_replay',None) and names(m,k).count('discipline')==2,'offsetting fouls that take both teams below the minimum: abandoned, not forfeited by the team listed first')
    # callbacks already pending when the match ends
    m=z4();s=m.s;m.e.foul('B4','A0','illegal_tackle',penalty=True);ok(s.phase==PEN and s.penalty is not None,'fixture: a penalty run is in progress')
    m.e.forfeit('B','penalty_keeper');ok(finished(m,'forfeit','A',1) and m.e.final_refused.get('finish_penalty',0)>=1,'a forfeit during a penalty run: the run\'s own completion is refused afterwards')
    m=z4();s=m.s;put(m,'B0',(51.3,50));tk(m);ok(s.recovery is not None and s.phase==AWARD,'fixture: a first-tackle recovery is in progress')
    m.e.forfeit('A','no_restart_taker');ok(finished(m,'forfeit','B',1),'a forfeit during a recovery: the recovery callbacks change nothing afterwards')
    m=CORE.match.Match(configuration({**SETTINGS,**C2R,'period_seconds':30,'periods':1},5,C4CAL));s=m.s;guard=0
    while not m.pending_ball_actions and guard<3000:m.step();guard+=1
    ok(bool(m.pending_ball_actions) and s.phase!=FINAL,'fixture: a real match with a pass or shot in preparation');m.e.forfeit('B','test_ground');pend=dict(m.pending_ball_actions)
    ok(finished(m,'forfeit','A',1) and 'release' not in names(m)[-1:],'a forfeit with a release in preparation: the release never happens')
    m=z4();s=m.s;s.score={'A':9,'B':2};m.e.forfeit('A','test_ground');ok(finished(m,'forfeit','B',1) and s.score=={'A':0,'B':5},'a leading team that forfeits: the 5-0 administrative score (rulebook 18.6) is written once, with the result')
    m=z4();s=m.s;s.score={'A':9,'B':2};m.e.forfeit('B','test_ground');ok(finished(m,'forfeit','A',1) and s.score=={'A':9,'B':2},'a trailing team that forfeits: the score stands')
    m=z4();s=m.s;k=len(m.e.log);m.e.foul('B5',None,'hold',major=True);m.e.foul('B6',None,'hold',major=True);m.e.foul('B7',None,'hold',major=True);ok(s.phase!=FINAL,'three exclusions: the team continues');m.e.foul('B8',None,'hold',major=True)
    ok(finished(m,'forfeit','A',1) and names(m,k).count('restart_awarded')==3,'the forfeit rule itself is unchanged for every other cause: a fourth concurrent exclusion ends the match, and no free pass follows it')

    # ---- 41. zone violations: no personal sanction, no forfeit ----
    m=z4();mk=recs(m,'c4_rules');m0=z4({'c4_zone':0});ok(len(mk)==1 and mk[0]['data']=={'zone_ruling':1,'defensive_consequences':True,'zone_direct_penalty':0} and not recs(m0,'c4_rules') and m.e.c4_occ and not m.e.zone_direct and not m0.e.c4_zone,'the ruling is marked in the log when it is on; with it off there is no marker and no C4.0 zone path')
    m=z4(A1=(90,50));s=m.s;k=len(m.e.log);m.e.advance(5000);d=recs(m,'attacking_zone_expiry',k)
    ok(fouls(m,k)==['zone_expiry'] and s.owner=='B' and s.phase==DEAD and s.restart.team=='B' and len(d)==1 and nodisc(m,k) and not s.warning['A'],'decided by DreLen: an attacking expiry is a turnover. No warning is recorded and nothing enters the ladder')
    m0=z4({'c4_zone':0},A1=(90,50));m0.e.advance(5000);ok('warning' in names(m0) and m0.s.warning['A']=={'technical'},'with c4_zone = 0 the same expiry gives the C3c2 team warning')
    def camp4(p_ms=12000,count=1,cal=None,**pos):
        """B3 alone and unmarked in the attacked zone, one millisecond short of his allowance. The attack has a counted tackle."""
        pos.setdefault('B3',(90,50));m=z4(cal,p_ms=p_ms+4999,**pos);s=m.s;s.tackle_count=count;s.tackle_ordinal=count;m.e.advance(4999);return m
    m=camp4();s=m.s;g0,k=s.game_ms,len(m.e.log);m.e.advance(1);v=zv(m,k);B3=s.players['B3']
    ok(len(v)==1 and v[0]['number_in_possession']==1 and v[0]['remedy']=='tackle_count_reset' and v[0]['team']=='B' and v[0]['against']=='A' and [p_['player'] for p_ in v[0]['participants']]==['B3'] and v[0]['personal_sanction'] is None,'decided by DreLen: the first defensive violation of a possession is one violation with one remedy')
    ok(s.tackle_count==0 and (v[0]['tackle_count_from'],v[0]['tackle_count_to'])==(1,0) and s.possession_ms==20000 and (v[0]['p_ms_from'],v[0]['p_ms_to'])==(11999,20000) and s.game_ms==g0-1 and s.zone_violations==1,'the tackle count returns to zero and the possession clock is raised to 20 s; the period clock is not touched')
    ok(fouls(m,k)==['zone_unmarked'] and names(m,k).count('defensive_unmarked_expiry')==1 and 'advantage' in names(m,k) and s.advantage is not None and s.phase==LIVE and s.owner=='A' and nodisc(m,k) and not s.warning['B'],'advantage is played as for any defensive foul; no warning, nothing queued')
    c=v[0]['participants'][0]['compliance'];ok(c['distance_out_m']==10.1 and c['speed_mps']==0 and c['reaction_ms']==int(1000*B3.a.decision_speed) and c['stop_ms']==0 and c['margin_ms']==300 and c['allowed_ms']==1+c['reaction_ms']+c['run_ms']+300 and B3.zone_fouled[1]==s.live_ms+c['allowed_ms']==v[0]['participants'][0]['compliance_deadline_live_ms'] and 1500<c['allowed_ms']<3500,'the compliance time is worked out and logged from where he stands when called: reaction, run out, and 0.3 s; it is not a new five seconds')
    m=camp4(count=0);s=m.s;k=len(m.e.log);m.e.advance(1);v=zv(m,k);ok(s.tackle_count==0 and (v[0]['tackle_count_from'],v[0]['tackle_count_to'])==(0,0) and s.possession_ms==20000 and s.zone_violations==1,'with no tackle on the count the reset changes nothing; the clock floor still applies')
    m=camp4(p_ms=40000,count=0);s=m.s;k=len(m.e.log);m.e.advance(1);v=zv(m,k);ok(s.possession_ms==39999==v[0]['p_ms_to']==v[0]['p_ms_from'] and s.tackle_count==0,'NOT FREE IS NOT GUARANTEED: at count zero with more than 20 s left the first violation gives the attack nothing at once. What it costs the defence is that the next one is a penalty')
    # advantage: realised, failed, and failed after losing the ball
    m=camp4();s=m.s;m.e.advance(1);k=len(m.e.log);put(m,'A0',(57,50));m.e.follow_carrier();m.e.advance(100)
    ok(recs(m,'advantage_realized',k)[0]['data']['method']=='progress' and s.advantage is None and s.tackle_count==0 and s.zone_violations==1 and s.possession_ms==20000-100 and not zv(m,k),'advantage realised: play goes on, the remedy is kept, nothing is given twice')
    m=camp4();s=m.s;m.e.advance(1);g_foul,k=s.game_ms,len(m.e.log);put(m,'B3',(78,50));m.e.advance(3000);r=s.restart
    ok('advantage_recalled' in names(m,k) and s.phase==DEAD and r.team=='A' and r.kind=='free_pass' and s.game_ms==g_foul and s.possession_ms==20000 and s.tackle_count==0 and s.zone_violations==1 and not zv(m,k) and nodisc(m,k),'advantage failed: free pass at the spot, both clocks back to the foul instant, which already holds the remedy. One reset, one clock floor')
    d=recs(m,'advantage_state_restored',k)[0]['data'];ok(d['zone_violations']==1 and d['tackle_count']==0 and recs(m,'zone_compliance',k)[0]['data']['how']=='left_across_the_arc','the restoration record shows the counter; his leaving during the advantage is logged as compliance')
    m=camp4(p_ms=40000);s=m.s;m.e.advance(1);put(m,'B3',(78,50));m.e.advance(3000);ok(s.possession_ms==39999 and s.tackle_count==0,'and with more than 20 s left the recall returns the foul-instant clock, not 20 s')
    m=camp4();s=m.s;m.e.advance(1);k=len(m.e.log);put(m,'B3',(78,50));m.e.release('A0',(10.0,0.0,2.0),'pass','A1');ok(catch(m,'B4',(60,50)) and s.owner=='B' and s.zone_violations==0 and s.tackle_count==0,'the attack loses the ball inside the advantage: a new possession, counter renewed for it')
    m.e.advance(s.advantage['until']-s.now);ok('advantage_recalled' in names(m,k) and s.owner=='A' and s.tackle_count==0 and s.zone_violations==1 and s.possession_ms==20000 and len(zv(m,k))==0,'the recall gives the ball back with the original violation still on the count and the same clock: the offence is not erased and no second top-up is given')
    # the second violation
    m=camp4();s=m.s;m.e.advance(1);put(m,'A0',(57,50));m.e.follow_carrier();m.e.advance(100);B3=s.players['B3'];left=B3.zone_fouled[1]-s.live_ms;k=len(m.e.log);m.e.advance(left-1)
    ok(not zv(m,k) and s.phase==LIVE,'still unmarked in the zone one millisecond before his compliance time ends: not called');m.e.advance(1);v=zv(m,k)
    ok(len(v)==1 and v[0]['number_in_possession']==2 and v[0]['remedy']=='penalty_run' and v[0]['participants'][0]['ground']=='still_unmarked_after_compliance_time' and v[0]['resolved_live_ms']==s.live_ms and s.phase==PEN and s.penalty['team']=='A' and recs(m,'penalty_start',k) and nodisc(m,k),'decided by DreLen: the second violation of the possession is a penalty run. Here it is the same defender, still there when his compliance time ended, called at that millisecond')
    m.e.finish_penalty(0);r=s.restart;ok(s.phase==DEAD and r.reason=='penalty_retained' and s.owner=='A' and s.possession_ms==m.e.play_ms and s.zone_violations==0 and s.tackle_count==0 and B3.unmarked_ms==[0,0],'after the run the attack has its fresh possession (rulebook 12.6): a new possession, so the counter starts again')
    def after_first(ms_before_deadline,**kw):
        m=camp4(**kw);s=m.s;m.e.advance(1);put(m,'A0',(57,50));m.e.follow_carrier();m.e.advance(100);B3=s.players['B3'];m.e.advance(B3.zone_fouled[1]-s.live_ms-ms_before_deadline);return m,B3,len(m.e.log)
    m,B3,k=after_first(1);put(m,'B3',(78,50));m.e.advance(200);c=recs(m,'zone_compliance',k)
    ok(not zv(m,k) and m.s.phase==LIVE and c[0]['data']['how']=='left_across_the_arc' and c[0]['data']['ms_before_deadline']==1 and B3.unmarked_ms[1]==0 and B3.zone_fouled[1]==0,'out across the arc with a millisecond to spare: compliance, no second violation')
    m,B3,k=after_first(1);m.e.advance(1);v=zv(m,k);ok(len(v)==1 and v[0]['called_live_ms']==v[0]['resolved_live_ms']==m.s.live_ms and m.s.phase==PEN,'in the zone, unmarked, at the millisecond his time ends: called at that millisecond, not at the end of a step')
    m,B3,k=after_first(1);m.e.advance(1);put(m,'B3',(78,50));ok(len(zv(m,k))==1 and m.s.phase==PEN,'a millisecond late is late: he was called at the deadline, and leaving afterwards does not undo it')
    m,B3,k=after_first(500);put(m,'A4',(88,50));m.e.advance(100);c=recs(m,'zone_compliance',k)
    ok(not zv(m,k) and c[0]['data']['how']=='marking_regained' and c[0]['data']['marking']=='A4' and c[0]['data']['distance_m']==2.0 and B3.unmarked_ms[1]==0 and m.s.zone_violations==1,'regaining a real marking exemption inside the time is compliance. It does not erase the violation already called')
    put(m,'A4',(30,45));m.e.advance(4999);ok(not zv(m,k) and B3.unmarked_ms[1]==4999,'marking lost again: a new five seconds runs, as for any defender');m.e.advance(1);v=zv(m,k)
    ok(len(v)==1 and v[0]['number_in_possession']==2 and v[0]['participants'][0]['ground']=='allowance_expired' and m.s.phase==PEN,'and its expiry in the same possession is the second violation')
    # the same moment, and one millisecond apart
    m=camp4(B4=(92,58));s=m.s;k=len(m.e.log);m.e.advance(1);v=zv(m,k)
    ok(len(v)==1 and sorted(p_['player'] for p_ in v[0]['participants'])==['B3','B4'] and v[0]['remedy']=='tackle_count_reset' and v[0]['due_later_in_this_instant']==[] and names(m,k).count('defensive_unmarked_expiry')==2 and fouls(m,k)==['zone_unmarked'] and s.zone_violations==1 and s.phase==LIVE,'decided by DreLen: two defenders whose allowances run out at the same millisecond are one violation with one consequence')
    m=camp4(B4=(92,58));s=m.s;s.players['B4'].unmarked_ms[1]-=1;k=len(m.e.log);m.e.advance(1);v=zv(m,k)
    ok(len(v)==1 and [p_['player'] for p_ in v[0]['participants']]==['B3'] and s.phase==LIVE,'one millisecond apart: the first is called alone');m.e.advance(1);v=zv(m,k)
    ok(len(v)==2 and v[1]['number_in_possession']==2 and [p_['player'] for p_ in v[1]['participants']]==['B4'] and v[1]['resolved_live_ms']==v[0]['resolved_live_ms']+1 and s.phase==PEN,'THE LEAD\'S RULE, FLAGGED FOR DRELEN: the second, a millisecond later, is a separate violation and so a penalty. The step that reaches both does not merge them')
    m=camp4(B4=(92,58));s=m.s;s.players['B4'].unmarked_ms[1]-=1;k=len(m.e.log);m.e.elapse(2,resolve=False);m.e.resolve_timers();v=zv(m,k)
    ok(len(v)==1 and [p_['player'] for p_ in v[0]['participants']]==['B3'] and v[0]['due_later_in_this_instant']==['B4'] and v[0]['resolved_live_ms']==v[0]['called_live_ms']-1,'reached together by one update, they are still told apart by the millisecond each fell due: the earlier is called first, alone');m.e.resolve_timers();v=zv(m,k)
    ok(len(v)==2 and [p_['player'] for p_ in v[1]['participants']]==['B4'] and v[1]['resolved_live_ms']==v[0]['resolved_live_ms']+1 and s.phase==PEN,'and the later one is then the second violation')
    # one counter for both zones
    m=camp4(B5=(10,50));s=m.s;s.players['B5'].unmarked_ms[0]-=700;k=len(m.e.log);m.e.advance(1);put(m,'A0',(57,50));m.e.follow_carrier();put(m,'B3',(78,50));m.e.advance(699);ok(len(zv(m,k))==1 and s.phase==LIVE,'fixture: first violation in zone 1; another defender is 0.7 s short of his allowance in zone 0');m.e.advance(1);v=zv(m,k)
    ok(len(v)==2 and v[1]['number_in_possession']==2 and v[1]['participants'][0]['zone']==0 and v[1]['remedy']=='penalty_run' and s.phase==PEN,'the counter belongs to the possession, not to a zone: an expiry in the other zone is the second violation')
    # what does and does not renew the counter
    m,B3,k=after_first(500);s=m.s;put(m,'B3',(78,50));m.e.advance(100);m.e.boundary(50,-1);ok(s.owner=='B' and s.zone_violations==0,'a turnover renews it')
    m,B3,k=after_first(500);s=m.s;put(m,'B3',(78,50));m.e.advance(100);m.e.foul('B6','A0','illegal_tackle');ok(s.owner=='A' and s.phase==DEAD and s.zone_violations==1 and 'discipline' in names(m,k),'an ordinary foul and its free pass do not: same possession, the counter stays at one. The foul keeps its own discipline')
    m,B3,k=after_first(500);s=m.s;put(m,'B3',(78,50));m.e.advance(100);put(m,'B0',(s.players['A0'].x+1.3,50));tk(m);ok(s.tackle_count==1 and s.zone_violations==1 and s.owner=='A','a first tackle and its recovery do not')
    # end line, substitution, freeze
    m,B3,k=after_first(500);s=m.s;put(m,'B3',(100.5,50));m.e.advance(1500);ok(not zv(m,k) and B3.unmarked_ms[1]>=5000 and B3.zone_fouled[1]<s.live_ms and 'zone_exit_invalid' in names(m,k) and 'zone_compliance' not in names(m,k),'over the end line is not a way out: nothing is reset, it is not compliance, and he cannot be called while off the field')
    put(m,'B3',(99,50));m.e.advance(100);v=zv(m,k);ok(len(v)==1 and v[0]['number_in_possession']==2 and v[0]['participants'][0]['ground']=='still_unmarked_after_compliance_time' and s.phase==PEN,'back in the zone after his time has run: called at once, the second violation')
    m,B3,k=after_first(500);s=m.s;dl=B3.zone_fouled[1];put(m,'B3',(25.0,101.0));n=put(m,'B12',(25.0,100.5));m.e.advance(50);ok(m.e.sub('B3','B12') and n.zone_fouled[1]==dl and n.unmarked_ms[1]>=5000,'a substitution during compliance: the slot keeps the same deadline, not a new one')
    put(m,'B12',(90,50));m.e.advance(dl-s.live_ms-1);ok(not zv(m,k),'the replacement, in the zone and unmarked, is not called before that deadline');m.e.advance(1);v=zv(m,k);ok(len(v)==1 and v[0]['participants'][0]['player']=='B12' and v[0]['number_in_possession']==2,'and is called at it')
    m,B3,k=after_first(500);s=m.s;dl=B3.zone_fouled[1];B3.freeze_until=s.now+2000;m.e.advance(2000);ok(not zv(m,k) and B3.zone_fouled[1]==dl+2000 and B3.unmarked_ms[1]<5000+2700,'frozen during compliance: he cannot move, so neither his count nor his compliance time runs');m.e.advance(499);quiet=not zv(m,k);m.e.advance(1);ok(quiet and len(zv(m,k))==1,'and both resume when he thaws: called at the deadline moved on by exactly the time he was frozen')
    # interventions by an overdue defender
    def overdue(cal=None):
        m,B3,k=after_first(800,cal=cal);s=m.s;m.e.release('A0',(12.0,0.0,2.0),'pass','A1');return m,B3,len(m.e.log)
    m,B3,k=overdue();s=m.s;got=catch(m,'B3');w=recs(m,'zone_overdue_intervention',k)
    ok(got and s.owner=='B' and len(w)==1 and w[0]['data']['act']=='control' and w[0]['data']['player']=='B3' and w[0]['data']['called_before'] and w[0]['data']['compliance_time_left_ms']==800 and w[0]['data']['nearest_opponent_m']>3 and not w[0]['data']['direct_penalty_rule'] and not zv(m,k) and s.phase==LIVE,'baseline: an overdue, unmarked defender who intercepts is recorded with his timer, the marking witness and the act. No direct penalty in the baseline')
    m,B3,k=overdue();s=m.s;put(m,'A4',(88,50));got=catch(m,'B3');ok(got and s.owner=='B' and not recs(m,'zone_overdue_intervention',k),'marked at the instant he plays the ball (positions as they are then): lawful, nothing recorded')
    m,B3,k=overdue({'zone_direct_penalty':1});s=m.s;got=catch(m,'B3');v=zv(m,k)
    ok(not got and s.owner=='A' and s.phase==PEN and len(v)==1 and v[0]['remedy']=='direct_penalty_run' and len(recs(m,'penalty_start',k))==1 and recs(m,'c4_rules')[0]['data']['zone_direct_penalty']==1 and nodisc(m,k),'PROPOSAL, behind its own switch: the same interception is a penalty run at once. One penalty, no reset stacked on it, no personal sanction')
    m,B3,k=overdue({'zone_direct_penalty':1});s=m.s;put(m,'A4',(88,50));got=catch(m,'B3');ok(got and s.owner=='B' and s.phase==LIVE and not zv(m,k),'and under the proposal a marked defender still intercepts lawfully')
    m,B3,k=overdue({'zone_direct_penalty':1});s=m.s;b=s.ball;b.mode=Ty.BallMode.SHOT;m.e.touch('B3',deliberate=False);w=recs(m,'zone_overdue_intervention',k);ok(w[0]['data']['act']=='block_shot' and w[0]['data']['scoring_attempt'] and s.phase==PEN,'under the proposal, blocking a shot is the same')
    m,B3,k=overdue({'zone_direct_penalty':1});s=m.s;K=next(q for q in s.players.values() if q.team=='B' and q.role=='keeper');K.x,K.y=97.0,50.0;K.unmarked_ms=[0,9000];s.ball.mode=Ty.BallMode.SHOT;m.e.touch(K.id,deliberate=False);ok(not recs(m,'zone_overdue_intervention',k) and s.phase==LIVE,'the Keeper in his own zone is exempt, whatever number sits in his counter')
    m=camp4();s=m.s;m.e.elapse(1,resolve=False);m.e.release('A0',(12.0,0.0,2.0),'pass','A1');k=len(m.e.log);got=catch(m,'B3');v=zv(m,k)
    ok(got and len(v)==1 and v[0]['remedy']=='tackle_count_reset' and s.owner=='B' and s.advantage is not None and s.advantage['team']=='A' and names(m,k).index('zone_violation')<names(m,k).index('control'),'a violation due at the very millisecond he takes the ball is called before his control counts')
    m.e.advance(s.advantage['until']-s.now);ok(s.owner=='A' and s.tackle_count==0 and s.zone_violations==1 and s.possession_ms==20000,'so it survives the change of possession his own interception caused: recalled, remedy intact')
    # recovery, reconstruction, another foul's advantage
    m=z4(p_ms=30000,B3=(90,50),B0=(51.3,50));s=m.s;m.e.advance(4000);tk(m);k=len(m.e.log);ok(s.tackle_count==1 and s.recovery is not None and s.phase==AWARD and s.tackle_ordinal==1,'fixture: first-tackle recovery in progress, a defender 1 s short of his allowance');put(m,'B0',(58,50));m.e.advance(1000);v=zv(m,k)
    ok(len(v)==1 and v[0]['recovery_in_progress'] and s.tackle_count==0 and s.recovery is not None and s.phase==AWARD,'first violation during a recovery: the count returns to zero and the recovery goes on');put(m,'B3',(78,50));m.e.advance(900);ok(pick(m,'A0') and s.tackle_count==0 and s.phase==LIVE,'the pickup does not bring the old count back')
    m.e.advance(200);put(m,'B1',(s.players['A0'].x+1.3,s.players['A0'].y));tk(m,'B1');d=last(m,'tackle_count');ok(s.owner=='A' and s.tackle_count==1 and (d['count_from'],d['count_to'],d['procedure'],d['ordinal_in_possession'])==(0,1,'live_recovery',2),'the next tackle is again a first tackle of the set, and the record says it is the second of the possession')
    m=z4(p_ms=30000,carrier_at=(90.0,44.0),B3=(94,62),B0=(91.3,44));s=m.s;m.e.advance(4000);tk(m);r=s.restart;ok(s.phase==DEAD and r.kind=='inbound' and s.reconstruction is not None and s.tackle_count==1,'fixture: inbound after a first tackle in the attacked zone; the zone must be cleared')
    put(m,'B0',(90,60));put(m,'A1',(100.4,42.0));m.e.ready('A1');m.e.restart_release('A1',(-15.0,0.0,3.0),'A2');k=len(m.e.log);ok(catch(m,'A2',(88.0,42.0)) and s.reconstruction is not None,'fixture: the inbound is caught inside the zone');m.e.advance(1000);v=zv(m,k)
    ok(len(v)==1 and v[0]['reconstruction'] and s.tackle_count==0 and s.reconstruction is not None,'first violation with the zone uncleared: the count is reset; the restriction is untouched');m.e.release('A2',(20.0,0.0,0.0),'shot');ok(not m.e.goal('B',50,1) and s.score['A']==0,'and no goal counts until the zone is cleared')
    m=z4(p_ms=30000,B3=(90,50));s=m.s;s.tackle_count=1;m.e.advance(4000);m.e.foul('B6','A0','late_hold',advantage=True);ok(s.advantage is not None and s.advantage['c2']['count']==1 and len(m.e.pending_discipline)==1,'fixture: advantage pending for a different foul, called with the count at one');k=len(m.e.log);m.e.advance(1000);v=zv(m,k)
    ok(len(v)==1 and v[0]['advantage_already_pending'] and s.tackle_count==0 and len(m.e.pending_discipline)==1,'a first zone violation inside another foul\'s advantage: the remedy is given at once');put(m,'B3',(78,50));m.e.advance(2000)
    ok('advantage_recalled' in names(m,k) and s.tackle_count==0 and s.zone_violations==1 and names(m,k).count('discipline')==1,'and when that advantage fails, the return to its foul instant does not bring the old count back; the other foul\'s sanction is applied as before')
    # goal and horn
    m=camp4();s=m.s;m.e.elapse(1,resolve=False);m.e.release('A0',(20.0,0.0,0.0),'shot');k=len(m.e.log);m.e.batch([Ty.Event('goal',data={'defending':'B','y':50,'z':1})]);m.e.resolve_timers()
    ok(s.score['A']>0 and not zv(m,k) and s.owner=='B' and s.zone_violations==0,'a goal at the very millisecond of an expiry: the goal counts, the possession ends, and no violation is called against a possession that is over')
    m=camp4();s=m.s;m.e.advance(1);k=len(m.e.log);m.e.release('A0',(20.0,0.0,0.0),'shot');ok(recs(m,'advantage_realized',k)[0]['data']['method']=='voluntary_shot' and s.advantage is None,'a shot taken inside the advantage realises it (rulebook 11.2)')
    m=camp4();s=m.s;s.game_ms=1;k=len(m.e.log);m.e.advance(1);m.e.resolve_timers();v=zv(m,k)
    ok(len(v)==1 and v[0]['remedy']=='tackle_count_reset' and 'advantage_recalled' in names(m,k) and s.phase==DEAD and s.extension and s.extension_team=='A' and s.possession_ms==10000 and s.game_ms==0 and s.period==1 and s.tackle_count==0,'first violation exactly at the period horn: the existing zero-time procedure (rulebook 16.6), one ten-second untimed possession. No ordinary possession and no added period time')
    m,B3,k=after_first(1);s=m.s;s.game_ms=1;m.e.advance(1);ok(s.phase==PEN and s.game_ms==0,'second violation exactly at the horn: the penalty run is still taken (rulebook 16.6)');p0=s.period;m.e.finish_penalty(0);ok(s.period==p0+1 and 'period_end' in names(m,k) and s.restart.reason=='quarter_start','and after it the period ends; no further possession is created')
    m=camp4(p_ms=4000);s=m.s;s.extension=True;s.extension_team='A';s.game_ms=0;g=s.game_ms;k=len(m.e.log);m.e.advance(1);ok(len(zv(m,k))==1 and s.possession_ms==10000 and s.game_ms==0,'first violation inside an untimed extension: its ten seconds are restored (rulebook 16.6), not 20')
    # twelve expiry offences: nothing on the ladder, and other discipline untouched
    m=z4(p_ms=45000,B3=(90,50));s=m.s;n_first=n_pen=0
    for i in range(6):
        put(m,'B3',(90,50));put(m,'A0',(50,50));give(m,'A0');s.owner='A';s.phase=LIVE;s.possession_ms=45000;s.advantage=None;m.e.advance(5000);n_first+=len(zv(m))-n_first-n_pen
        s.advantage=None;B3=s.players['B3'];m.e.advance(B3.zone_fouled[1]-s.live_ms);n_pen=sum(v_['remedy']=='penalty_run' for v_ in zv(m));m.e.finish_penalty(0);put(m,'A1',(50,50));m.e.ready('A1');m.e.restart_release('A1',(5.0,0.0,2.0));catch(m,'A0',(53,50))
    ok(len(zv(m))==12 and n_pen==6 and nodisc(m) and s.warning=={'A':set(),'B':set()} and s.phase!=FINAL and all(q.minor_count==0 and q.major_count==0 and q.active for q in s.players.values() if q.id=='B3'),'twelve defensive expiry offences by one team, six of them penalties: no warning, no exclusion, no debt, no forfeit')
    k=len(m.e.log);m.e.foul('B6',None,'recovery_interference');m.e.foul('B7',None,'recovery_interference');ok(names(m,k).count('warning')==1 and names(m,k).count('discipline')==1 and s.warning['B']=={'technical'},'other technical fouls still follow the warning ladder: first a team warning, then a minor')
    m=z4(A1=(90,50));s=m.s
    for i in range(12):
        s.owner='A';s.phase=LIVE;s.restart=None;put(m,'A1',(90,50));put(m,'A0',(50,50));give(m,'A0');s.players['A1'].zone_ms=[0,4999];m.e.advance(1)
    ok(fouls(m).count('zone_expiry')==12 and nodisc(m) and s.phase!=FINAL,'twelve attacking expiries: twelve turnovers, nothing on the ladder')
    m0=z4({'c4_zone':0},B3=(90,50));s=m0.s;m0.e.advance(5000);ok(not zv(m0) and fouls(m0)==['zone_unmarked'] and len(m0.e.pending_discipline)==1 and s.tackle_count==0 and 'defensive_unmarked_expiry' in names(m0),'with c4_zone = 0 the defensive expiry is the C3c2 one: advantage, a sanction queued, no counter')
    # ---- 42. settings and measurement ----
    def bad4(**c):
        try:configuration(SETTINGS,1,{**C4CAL,**c});return False
        except ValueError:return True
    ok(bad4(c4_zone=2) and bad4(zone_direct_penalty=-1) and not bad4() and C4CAL['c4_zone']==1 and C4CAL['zone_direct_penalty']==0 and all(k_ in C3_RANGES for k_ in('c4_zone','zone_direct_penalty')),'the two C4.0 switches are validated; the ruling is on and the proposal off in the delivered settings')
    m,B3,k=after_first(500);put(m,'A4',(88,50));m.e.advance(100);put(m,'A4',(30,45));m.e.advance(5000);m.e.finish_penalty(0);M=measure_c4(m.e.log);Z=M['zone_violations']
    ok(M['c4_zone_witness_in_log'] and Z['violations']==2 and Z['by_remedy']=={'tackle_count_reset':1,'penalty_run':1} and Z['defenders_per_violation']=={1:2} and Z['compliance_outcomes']=={'marking_regained':1,'possession_ended':1} and Z['penalty_runs_from_violations']==1 and Z['penalty_runs_scored']==0 and Z['possessions_with_a_violation']==1 and Z['tackle_count_reset_from']=={1:1},'M1.5 counts violations, remedies, compliance and the penalty runs that followed, from the log alone')
    ok(measure_c4(z4({'c4_zone':0}).e.log)['zone_violations']=='unavailable','and reports them unavailable, not zero, for a log without the ruling')
    m=queued(['B1','B2','B3','B4','B8'],already=0);m.e.award('B',95.0,23.4,'boundary');T=measure_c4(m.e.log)['terminal']
    ok(T=={'match_complete_records':1,'forfeit_records':1,'abandoned_records':0,'records_after_the_first_match_complete':0,'sanctions_not_administered':0,'grounds_not_applied_at_a_deciding_horn':0},'M1.5 terminal integrity: one completion, one forfeit, nothing after it')
    # ---- 43. cases found by an independent review of this batch before delivery ----
    m,B3,k=after_first(1);s=m.s;K=next(q for q in s.players.values() if q.team=='B' and q.role=='keeper');K.freeze_until=s.now+4000;m.e.advance(1)
    ok(s.phase==PEN and 'forfeit' not in names(m,k) and s.players[s.penalty['keeper']].team=='B' and s.penalty['keeper']!=K.id and not s.players[s.penalty['keeper']].frozen(s.now),'REVIEW: a second violation with the defending Keeper frozen: a team-mate keeps goal for the run (rulebook 12.3). It was a forfeit, which would have been a forfeit off a zone violation')
    def same_instant(catcher,xy=None):
        m=camp4(B4=(92,58));s=m.s;s.players['B4'].unmarked_ms[1]-=1;m.e.advance(1);put(m,'A0',(57,50));m.e.follow_carrier();m.e.release('A0',(12.0,0.0,2.0),'pass','A1');k=len(m.e.log);m.e.elapse(1,resolve=False);got=catch(m,catcher,xy);return m,k,got
    m,k,got=same_instant('B5',(62,50));m2,k2,got2=same_instant('B4');v=zv(m,k);v2=zv(m2,k2)
    ok(len(v)==1==len(v2) and v[0]['participants'][0]['player']=='B4'==v2[0]['participants'][0]['player'] and v[0]['remedy']=='penalty_run'==v2[0]['remedy'] and not got and not got2 and m.s.phase==PEN==m2.s.phase,'REVIEW: a violation due at the millisecond another defender intercepts is called first, the same as when the overdue defender intercepts himself')
    def mixed(order):
        m=z4();s=m.s
        for t in('A','B'):
            for i in range(3):m.e.discipline(t+str(5+i),'minor')
        evs=[Ty.Event('foul','A1',data={'reason':'late_hold'}),Ty.Event('foul','B1',data={'reason':'late_hold','danger':True})];k=len(m.e.log);m.e.batch(evs if order else evs[::-1]);return m,k
    m,k=mixed(True);m2,k2=mixed(False)
    ok(finished(m,'abandoned_replay',None) and finished(m2,'abandoned_replay',None) and 'restart_awarded' not in names(m,k)+names(m2,k2),'REVIEW: two fouls of one millisecond that are not offsetting still form one instant: both teams below the minimum is an abandonment in either order, and no restart is announced on the way')
    m=CORE.match.Match(configuration({**SETTINGS,'archery':False,'zone_marking':False,'zone_inbound':False},1,Z4));s=m.s
    s.phase=LIVE;s.now=1000;s.owner='A';s.opening_team='A';s.opening_deadline=None;s.opening_touched=True;put(m,'A0',(95,50));give(m,'A0');B3=put(m,'B3',(90,40));B3.zone_ms=[0,5000];k=len(m.e.log)
    m.e.release('A0',(20.0,0.0,0.0),'shot');m.e.batch([Ty.Event('goal',data={'defending':'B','y':50,'z':1})])
    ok(s.score['A']>0 and 'post_goal_discipline' in names(m,k) and recs(m,'post_goal_discipline',k)[0]['data']['kind'] is None and nodisc(m,k),'REVIEW: with zone marking off, a defender\'s zone expiry disciplined after a goal is no personal sanction either under the ruling')
    m=CORE.match.Match(configuration({**SETTINGS,**C2R,'period_seconds':10,'periods':1},5,C4CAL));s=m.s;at=[];orig=m.e.complete
    def spy(*a_,**k_):
        try:return orig(*a_,**k_)
        finally:at.append(frozen_record(m))
    m.e.complete=spy
    while s.game_ms>1500:m.step()
    s.score={'A':1,'B':4};m.run();m.step();m.run_for(3);m.summary()
    ok(len(at)==1 and at[0]==frozen_record(m) and s.result['method']=='regulation','REVIEW: in a real match the state at the instant of the result, positions and engagements included, is the state afterwards: the Match no longer plays out the rest of the step')
    # ---- 44. r2: the Lead's audit of C4.0 ----
    def contact(dist,n_before=0,cal=None):
        """B3's stored allowance has run out; A4 is now dist m from him as he takes a loose ball. Count updates have not run since."""
        m=z4(cal);s=m.s;B=put(m,'B3',(90,50));B.unmarked_ms[1]=5000;B.zone_loc[1]='in';s.zone_violations=n_before;put(m,'A4',(90-dist,50))
        s.ball=Ty.Ball(mode=Ty.BallMode.LOOSE,x=90.3,y=50,z=1.2,last_touch='A');k=len(m.e.log);got=m.e.acquire('B3');return m,k,got
    m,k,got=contact(2.0);ok(got and not zv(m,k) and m.s.owner=='B' and m.s.players['B3'].unmarked_ms[1]==0 and m.s.phase==LIVE,'LEAD r2: marked at the instant he takes the ball (A4 2 m away), no violation is called on the count from before it; his interception stands')
    m,k,got=contact(2.0,1);ok(got and not zv(m,k) and m.s.phase==LIVE and not recs(m,'penalty_start',k),'and with one violation already against the possession, no penalty run: it was a second-violation penalty in C4.0')
    m,k,got=contact(9.0);v=zv(m,k);ok(got and len(v)==1 and v[0]['remedy']=='tackle_count_reset' and m.s.owner=='B' and m.s.advantage is not None,'control case unchanged: unmarked at the instant, the due violation is called first and his interception happens inside the advantage')
    m,k,got=contact(9.0,1);ok(not got and len(zv(m,k))==1 and m.s.phase==PEN,'and with one already against the possession it is the penalty run')
    m,k,got=contact(3.0);ok(got and not zv(m,k),'exactly at the marking distance he is marked')
    m,k,got=contact(3.0004);v=zv(m,k);ok(len(v)==1 and v[0]['participants'][0]['nearest_opponent_m']==3.0,'0.4 mm beyond it he is not, although the logged distance rounds to 3.000: the test uses the exact distance, the record a rounded one')
    m,k,got=contact(9.0,1,{'zone_direct_penalty':1});ok(not got and len(zv(m,k))==1 and zv(m,k)[0]['remedy']=='direct_penalty_run' and len(recs(m,'penalty_start',k))==1,'with the proposal on, one penalty, not two')
    m,k,got=contact(2.0,1,{'zone_direct_penalty':1});ok(got and not zv(m,k) and m.s.phase==LIVE,'and with it on, the marked defender intercepts lawfully')
    # the compliance bound on the kernel's motion, tired
    E4=CORE.engine.Engine;mm=z4();B=put(mm,'B3',(99,50));out_={}
    for f in(1.0,.5,.15):B.fatigue=f;out_[f]=mm.e.zone_compliance_time(B,1)
    ok(out_[.15]['allowed_ms']>out_[.5]['allowed_ms']>out_[1.0]['allowed_ms'] and out_[.15]['fatigue_assumed']<=.15+1e-9 and out_[1.0]['fatigue_assumed']<1.0,'LEAD r2: the compliance time grows as he tires, on the kernel\'s own fatigue scaling, and assumes the fatigue he will have reached by the end of the run')
    # 15.5: an attacking expiry and a defensive violation at the same millisecond
    def both(n_before=0,att_gap=0,attack='A'):
        m=z4();s=m.s
        if attack=='B':
            s.owner='B';put(m,'B0',(50,50));give(m,'B0');put(m,'A0',(30,5))
        d='B' if attack=='A' else 'A';gx=90 if attack=='A' else 10
        At=put(m,attack+'1',(gx,45));Df=put(m,d+'3',(gx,55));j=1 if attack=='A' else 0
        At.zone_ms[j]=5000;At.zone_loc[j]=Df.zone_loc[j]='in';Df.unmarked_ms[j]=5000+max(0,-att_gap);At.zone_ms[j]=5000+max(0,att_gap) #att_gap > 0: the attacker's time ran out that many ms earlier; < 0: the defender's
        s.live_ms=10000;s.zone_violations=n_before;s.tackle_count=1;s.possession_ms=30000;k=len(m.e.log);m.e.resolve_timers();return m,k
    for att in('A','B'):
        m,k=both(0,0,att);s=m.s;v=zv(m,k);so=recs(m,'simultaneous_offences',k)
        ok(len(so)==1 and so[0]['data']['resolution']=='offset_same_severity' and len(v)==1 and v[0]['remedy']=='offset_by_simultaneous_attacking_offence' and s.owner==att and s.phase==DEAD and s.restart.team==att and s.restart.reason=='offsetting_fouls' and s.tackle_count==1 and s.possession_ms==30000 and s.zone_violations==1 and not recs(m,'possession_change',k) and nodisc(m,k),'LEAD r2, rulebook 15.5, team %s attacking: an attacking expiry and a first defensive violation at one millisecond are both technicals: the awards offset, the attack keeps the ball with its clock and count, no turnover and no reset. The defensive violation is still counted'%att)
        m,k=both(1,0,att);s=m.s;v=zv(m,k);so=recs(m,'simultaneous_offences',k)
        ok(len(so)==1 and so[0]['data']['resolution']=='penalty_chance_offence_prevails' and len(v)==1 and v[0]['remedy']=='penalty_run' and s.phase==PEN and s.penalty['team']==att and not recs(m,'possession_change',k),'and with a second defensive violation, the penalty-chance offence is the more serious: the attack (team %s) gets its penalty run; the expiry no longer erases it'%att)
    m,k=both(1,1);s=m.s;ok(s.owner=='B' and not zv(m,k) and recs(m,'attacking_zone_expiry',k),'1 ms control: the attacking expiry a millisecond earlier is a turnover, and the defensive count goes with the possession')
    m,k=both(1,-1);s=m.s;v=zv(m,k);ok(len(v)==1 and v[0]['remedy']=='penalty_run' and s.phase==PEN and s.penalty['team']=='A' and not recs(m,'simultaneous_offences',k) and not recs(m,'possession_change',k),'1 ms control the other way: the defensive violation a millisecond earlier is called first, as the earlier event; nothing is offset')
    m,k=both(0,-1);s=m.s;m.e.resolve_timers();v=zv(m,k);ok(len(v)==1 and v[0]['remedy']=='tackle_count_reset' and recs(m,'attacking_zone_expiry',k) and s.owner=='A' and s.restart is not None and s.restart.team=='A','and a first violation a millisecond earlier: its advantage is pending when the attacker\'s time runs out, so the earlier defensive foul is enforced for the attack (rulebook 11.3, retained)')
    # small terminal corrections
    m=z4();s=m.s;m.e.pending_discipline=[('B3','minor',False)];m.e.suspend('audit_fixture');s.now=s.suspended_at+86400000;m.e.resume()
    ok(finished(m,'abandoned_replay',None) and names(m)[-3:]==['suspended','abandoned','match_complete'] and s.result['winner'] is None and s.players['B3'].minor_count==1,'LEAD r2: the 24-hour suspension abandonment is committed like any result: one match_complete, no winner invented (the queued sanction was administered at the suspension stoppage)')
    m=z4();m.e.forfeit('B','audit');st=dict(m.stats);m.e.count('pass_attempts');m.e.count('audit_after_final');ok(dict(m.stats)==st and m.e.final_refused.get('count')==2,'LEAD r2: count is guarded: after the result the exported statistics do not move')
    m=z4();e=m.e;s=m.s
    for pid in('B5','B6','B7'):e.discipline(pid,'minor')
    e.terminal_hold+=1;e.neutral_offset(['B1','A1']);mid=s.phase
    for pid in('A5','A6','A7'):e.discipline(pid,'minor')
    e.terminal_hold-=1;e.terminal_resolve();ok(mid!=FINAL and s.result['method']=='abandoned_replay' and names(m).count('forfeit')==0,'LEAD r2 (exploratory probe): offsetting fouls inside a wider held instant do not judge the grounds early; the instant is judged once, at its end')
    # ================= C4a: contact carry-forwards =================
    # Every scenario above runs with escape_allocation = 0, contact_roster = 0 and region policy 1: they describe C4.0r2 and still hold.
    def k4(alloc=1,cal=None,**kw):return kb({'c3c':1,'escape_allocation':alloc,**(cal or {})},**kw)
    def pile(alloc,holders=(('B0',.68),('B1',.68)),carrier=.68,ms=200,fix_escape=0.0):
        """Carrier A0 runs at 6 m/s with one or two passive holders alongside, high region fixed, no strips. Grips are first built
        with no prying (fix_escape 0); then the hook is cleared and his own controller (full effort) works."""
        m=k4(alloc);m.c3_fix_region='upper';m.c3_fix_drive=-1.0;A=kput(m,'A0',(20,50),(6,0));A.a.strength=A.a.balance=carrier;ktop(m,'A0',6,True);kgive(m,'A0')
        for n_,(pid,st) in enumerate(holders):
            B=kput(m,pid,(18.9,51.0 if n_==0 else 49.0),(6,0));B.a.strength=B.a.tackling=st;ktop(m,pid,6)
        tg=lambda:{**{'A0':(99,50)},**{pid:(A.x,A.y) for pid,_ in holders}}
        m.c3_fix_escape=fix_escape;ktick(m,tg(),ms);m.c3_fix_escape=None;return m,A,tg
    def holds(m):return{k[0]:h for k,h in m.c3_holds.items() if k[1]=='A0'}
    m,A,tg=pile(1);ktick(m,tg(),20);H=holds(m)
    ok(len(H)==2 and all(abs(h['share']-.5)<1e-12 for h in H.values()),'C4a: two holds, equal allocation: the carrier\'s one prying effort is split half and half')
    m0,A0_,tg0=pile(0);ktick(m0,tg0(),20);H0=holds(m0)
    ok(all(h['share']==1. for h in H0.values()) and all(abs(H0[q]['break_rate']-2*H[q]['break_rate'])<1e-9*max(1,H0[q]['break_rate']) or H0[q]['break_rate']==H[q]['break_rate']==0 for q in H) and sum(h['break_rate'] for h in H0.values())>0,'with escape_allocation = 0 (C4.0r2) each hold takes his full effort; under equal shares each takes half of it')
    m,A,tg=pile(1,holders=(('B0',.68),));ktick(m,tg(),20);H=holds(m);m0,A0_,tg0=pile(0,holders=(('B0',.68),));ktick(m0,tg0(),20);H0=holds(m0)
    ok(H['B0']['share']==1. and abs(H['B0']['break_rate']-H0['B0']['break_rate'])<1e-12 and abs(H['B0']['g']-H0['B0']['g'])<1e-12,'one holder: the whole effort is his, and the hold runs exactly as in C4.0r2')
    m,A,tg=pile(2);H=holds(m);H['B1']['g']=H['B0']['g']*.5;ktick(m,tg(),10);H=holds(m)
    ok(H['B1']['share']==1. and H['B0']['share']==0. and H['B0']['break_rate']==0,'weakest as he feels it: all of the effort on the hold with the lower grip, none on the other')
    m,A,tg=pile(3,holders=(('B0',.90),('B1',.30)));ktick(m,tg(),10);H=holds(m)
    ok(H['B1']['share']==1. and H['B0']['share']==0.,'weakest in truth (perfect information, drills only): all of it on the weaker holder\'s hold')
    sums=[]
    for alloc in(1,2,3):
        m,A,tg=pile(alloc,holders=(('B0',.90),('B1',.30)),carrier=.90)
        for _ in range(40):
            ktick(m,tg(),10);sh=[h.get('share',0.) for h in holds(m).values() if h.get('break_rate',0)>0 or 'share' in h];sums.append(sum(sh))
    ok(max(sums)<=1+1e-9,'the shares never add up to more than the one effort, under any policy, while holds are made, worked and thrown off')
    def outcome(alloc,secs=4.0):
        m,A,tg=pile(alloc,holders=(('B0',.90),('B1',.30)),carrier=.90);k=len(m.e.log);t0=m.s.now
        while m.s.now-t0<secs*1000 and m.s.ball.carrier=='A0' and A.posture=='upright':ktick(m,tg(),10)
        return [r['data']['actor'] for r in m.e.log[k:] if r['event']=='c3_hold_end' and r['data']['cause']=='pried_off'],m
    full,_=outcome(0);eq,_=outcome(1);weak,m3=outcome(3)
    ok('B1' in full and 'B1' in weak and 'B0' not in weak,'a strong carrier (0.90) against a strong and a weak holder: the weak hold comes off with full effort on each (C4.0r2) and with all effort on it; the strong one never does under the weakest-in-truth policy. Equal shares: '+str(eq))
    ends=[r['data'] for r in m3.e.log if r['event']=='c3_hold_end'];ok(all('escape_share_ms' in d for d in ends) and any(d['escape_share_ms']>0 for d in ends),'the hold record shows the effort-weighted time each hold was worked on')
    # region policies
    def region(policy,at,mate=None):
        m=k4(1,{'c3_region_policy':policy});A=kput(m,'A0',at);kgive(m,'A0');B=kput(m,'B0',(at[0]-1.1,at[1]+.5))
        if mate:kput(m,'A1',mate)
        return m.c3_region(B,A,m.s.now)
    ok(region(2,(88,50))==('upper','in_defended_zone') and region(1,(88,50))==('lower',False) and region(0,(88,50))==('lower',False),'C4a policy 2: a carrier inside the zone the defender defends, no pass open, no wind-up: high under policy 2, low under policies 0 and 1')
    ok(region(2,(60,50))==('lower',False) and region(1,(60,50),(70,60))==('upper','pass_open') and region(0,(60,50),(70,60))==('lower',False) and region(2,(60,50),(70,60))==('lower',False),'outside the zone: policy 2 goes low; a pass open sends him high under policy 1 only')
    m=k4(1,{'c3_region_policy':2});mk=[r for r in m.e.log if r['event']=='c4a_rules'];ok(len(mk)==1 and mk[0]['data']['region_policy']==2,'the policy is written in the marker record')
    # rosters
    def roster(mode,cal=None):
        return CORE.match.Match(configuration({**SETTINGS,'archery':False},1,{**C4ACAL,'contact_roster':mode,**(cal or {})}))
    m=roster(4);L4=(.46,.60,.76,.90); #C4b: the C4a mixed design is now design 4 (design 1 is the balanced, rotated one)
    T=lambda team:[ (q.a.strength,q.a.balance,q.a.tackling) for q in sorted([q for q in m.s.players.values() if q.team==team and q.role=='field'],key=lambda q:q.slot)]
    a,b=T('A'),T('B');pairs={(s_,b_) for s_,b_,t_ in a[:16]};tri=all(len({x[i] for x in a[:16] if x[j]==v})==4 for i in range(3) for j in range(3) if i!=j for v in L4)
    ok(a==b and len(a)==20 and len(pairs)==16 and tri and abs(sum(x[0] for x in a[:16])/16-.68)<1e-9,'mixed and mirrored: both teams get the same slots; over 16 slots every strength-balance pair occurs once and each attribute meets every level of each other one, mean 0.68')
    ok(all((q.a.strength,q.a.balance,q.a.tackling)==(.68,.68,.68) for q in m.s.players.values() if q.role!='field') and all(q.a.agility==.68 and q.a.contact_resistance==.68 for q in m.s.players.values()),'Keepers, Archers and every other attribute keep 0.68')
    mk=[r for r in m.e.log if r['event']=='c4a_rules'];ok(len(mk)==1 and mk[0]['data']['strength_balance_tackling']['A3']==list(a[3]) and len(mk[0]['data']['strength_balance_tackling'])==40,'the marker carries the table, so a log can be measured by roster')
    m=roster(2);ok(all(q.a.strength==.9 and q.a.tackling==.9 and q.a.balance==.9 for q in m.s.players.values() if q.team=='A' and q.role=='field') and all(q.a.strength==.3 for q in m.s.players.values() if q.team=='B' and q.role=='field'),'contrast 2: team A 0.90, team B 0.30');m=roster(3);ok(all(q.a.strength==.3 for q in m.s.players.values() if q.team=='A' and q.role=='field'),'contrast 3: the reverse')
    m=roster(0,{'escape_allocation':0});ok(not [r for r in m.e.log if r['event']=='c4a_rules'] and all(q.a.strength==.68 for q in m.s.players.values()),'with all three at their C4.0r2 values there is no marker and nothing changes')
    def bad4a(**c):
        try:configuration(SETTINGS,1,{**C4ACAL,**c});return False
        except ValueError:return True
    ok(bad4a(contact_roster=5) and bad4a(escape_allocation=1.5) and bad4a(escape_allocation=-1) and bad4a(c3_region_policy=3) and not bad4a(c3_region_policy=2) and not bad4a() and C4ACAL['escape_allocation']==1 and C4ACAL['contact_roster']==0 and C4ACAL['c3_region_policy']==1,'the C4a values are validated as named whole numbers; delivered: equal shares, uniform roster, region policy 1')
    # M1.5.1: penalty runs from zone violations (the Lead's C4.0r2 acceptance)
    def offset_fixture():
        m=CORE.match.Match(configuration({**SETTINGS,**C2R,'archery':False},1,{**LEGACY,'c4_zone':1}));s=m.s
        s.phase=LIVE;s.now=1000;s.owner='A';s.opening_team='A';s.alternate='B';s.opening_deadline=None;s.opening_touched=True
        for q in s.players.values():
            if q.active and q.role=='field':put(m,q.id,(30.0 if q.team=='A' else 70.0,5.0+10.0*int(q.id[1:])))
        put(m,'A0',(50,50));give(m,'A0');s.possession_ms=30000;s.tackle_count=1
        A=put(m,'A1',(90,45));B=put(m,'B3',(90,55));A.zone_ms[1]=B.unmarked_ms[1]=5000;A.zone_loc[1]=B.zone_loc[1]='in';s.live_ms=10000;m.e.resolve_timers();return m
    m=offset_fixture();Z=measure_c4(m.e.log)['zone_violations']
    ok(Z['offset_violations']==1 and Z['penalty_runs_from_violations']==0 and Z['penalty_runs_scored']==0 and Z['penalty_points']==0,'M1.5.1: an offset violation alone is no penalty run (M1.5 counted one)')
    m=offset_fixture();s=m.s;put(m,'A1',(75,45));m.e.occupancy(0);s.phase=LIVE;s.restart=None;give(m,'A0');B=s.players['B3'];s.live_ms=B.zone_fouled[1];m.e.resolve_timers();m.e.finish_penalty(2);Z=measure_c4(m.e.log)['zone_violations']
    ok(Z['offset_violations']==1 and Z['penalty_runs_from_violations']==1 and Z['penalty_runs_scored']==1 and Z['penalty_points']==2 and sum(r['event']=='penalty_start' for r in m.e.log)==1,'M1.5.1: an offset followed by a real penalty run: one run, one outcome, 2 points (M1.5 reported two runs and four points)')
    # ================= C4b: support-foot origin, Carry, scoring configurations; C4a carry-forwards =================
    # Every scenario above runs with c4b = 0 (pelvis origin): they describe their own checkpoints and still hold.
    def k4b(cal=None,**kw):return kb({'c3c':1,'c4b':1,'escape_allocation':1,**(cal or {})},**kw)
    def still(m,pid,ms=300):
        q=m.s.players[pid];ktick(m,{pid:(q.x,q.y)},ms);return q
    W=lambda q:C4BCAL['gait_half_width_frac']*q.a.height
    m=k4b();A=kput(m,'A0',(60,50));A.facing=(0.0,1.0);still(m,'A0');f=A.feet
    ok(f['L']['planted'] and f['R']['planted'] and abs(f['L']['x']-(60-W(A)))<1e-9 and abs(f['R']['x']-(60+W(A)))<1e-9 and f['L']['y']==f['R']['y']==50,'C4b: standing, both feet are down beside the pelvis, one to each side of the way he faces')
    xy,rec=m.e.c4b_origin(A);ok(rec['rule']=='both_planted_nearer_goal' and rec['foot']=='R' and abs(xy[0]-(60+W(A)))<1e-9,'decided by DreLen: both feet planted, the origin is the foot nearer the goal he attacks')
    # running: planted feet are anchored, strides alternate, a runner has a flight phase and a walker double support
    def run_feet(v,ms=1500):
        m=k4b();A=kput(m,'A0',(30,50),(v,0.0));ktop(m,'A0',v);seen=[];anch=True;flight=0;double=0;last={}
        for _ in range(ms//10):
            ktick(m,{'A0':(A.x+50,50)},10);f=A.feet
            for k_ in('L','R'):
                st=(f[k_]['planted'],f[k_].get('t'),f[k_].get('x'),f[k_].get('y'))
                if st[0] and k_ in last and last[k_][0] and last[k_][1]==st[1] and (last[k_][2],last[k_][3])!=(st[2],st[3]):anch=False
                last[k_]=st
            n=f['L']['planted']+f['R']['planted'];flight+=n==0;double+=n==2;seen.append(n)
        return m,A,anch,flight,double
    m,A,anch,fl,db=run_feet(8.0);ok(anch and fl>0,'running at 8 m/s: a planted foot never moves until it is lifted, and there are moments with neither foot down (a flight phase)')
    strikes=[]
    m2,A2,anch2,fl2,db2=run_feet(1.5);ok(anch2 and db2>0,'walking at 1.5 m/s: there are moments with both feet down (double support)')
    q=A;ok(q.feet['L'].get('n',0)%2==0 and q.feet['R'].get('n',1)%2==1,'the left foot strikes on even steps, the right on odd: they alternate')
    # jump and landing
    m=k4b();A=kput(m,'A0',(85,50));A.facing=(0.0,1.0);still(m,'A0');A.posture='airborne';A.z=.5;A.vz=3.0;m.c4b_gait({'A0':(A.x,A.y,A.z)},10)
    xy,rec=m.e.c4b_origin(A);ok(not A.feet['L']['planted'] and not A.feet['R']['planted'] and rec['rule']=='airborne_last_plant' and rec['foot']=='R','in the air: both feet up; the origin is the last foot down, here the one nearer the goal (they left together)')
    # C4b r1: a real landing on the normal path. Takeoff at x0 (outside the zone), running at 15 m/s, landing 49.6 ms later just
    # inside the 20 m arc; releases before, in the same millisecond as, and after the landing, each by interval sizes 1 to 100 ms.
    def land_fix(chunk,rel_ms,x0=79.4,v=15.0,L=.0496):
        m=k4b();A=kput(m,'A0',(x0,50));kgive(m,'A0');ktick(m,{'A0':(x0,50)},1)
        A.vx=v;ktop(m,'A0',v,True);A.posture='airborne';A.z=.1;g=m.assume['gravity'];A.vz=(.5*g*L*L-A.z)/L
        m.c4b_gait({'A0':(A.x,A.y,A.z)},0);t0=m.s.now;left=rel_ms
        while left>0:
            c=min(chunk,left);ktick(m,{'A0':(99.0,50)},c);left-=c
        k=len(m.e.log);m.e.release('A0',(20.0,0.0,0.5),'shot');r=[x for x in m.e.log[k:] if x['event']=='release'][0]['data']['origin']
        return m,A,r,t0
    LF={(c,t):land_fix(c,t) for t in(40,50,60) for c in(t,20,10,1)}
    same=all(LF[(c,t)][2]['rule']==LF[(t,t)][2]['rule'] and LF[(c,t)][2]['foot']==LF[(t,t)][2]['foot'] and abs(LF[(c,t)][2]['origin'][0]-LF[(t,t)][2]['origin'][0])<.005 and LF[(c,t)][2]['territory']==LF[(t,t)][2]['territory'] for t in(40,50,60) for c in(t,20,10,1))
    ok(same,'a landing inside an interval: the origin at release is the same whether the interval is 1, 10, 20 ms or the whole flight')
    m,A,r,t0=LF[(40,40)];ok(r['rule']=='airborne_last_plant' and abs(r['origin'][0]-79.4)<.005 and r['territory']=='outside_release','released 9.6 ms before landing: still in the air, the origin is the takeoff foot, outside the zone')
    m,A,r,t0=LF[(50,50)];tl=A.feet['L']['t']
    ok(r['rule']=='one_planted' and r['foot']=='L' and abs(r['origin'][0]-(79.4+15*.0496))<.01 and r['territory']=='inside_release' and abs(tl-(t0+49.6))<.05 and tl<=m.s.now,'released in the millisecond he lands (at 49.6 ms, released at 50): he lands first, where and when he lands, inside the zone; the landing foot is the origin')
    m,A,r,t0=LF[(60,60)];ok(r['rule']=='one_planted' and r['foot']=='L' and abs(r['origin'][0]-(79.4+15*.0496))<.01 and r['territory']=='inside_release' and abs(A.feet['R']['t']-(t0+49.6))<.05,'released 10 ms after landing: the same; at this speed the trailing foot comes up at the landing instant (its stance time is already spent)')
    m,A,r,t0=LF[(1,60)];ok(m.stats['c4b_landings']==1 and m.stats.get('c4b_landings_unsolved',0)==0,'the landing is solved from the flight, once')
    def init_fix(chunk,x0=78.6,v=15.0):
        m=k4b();A=kput(m,'A0',(x0,50),(v,0.0));kgive(m,'A0');ktop(m,'A0',v,True);t0=m.s.now
        for _ in range(100//chunk):ktick(m,{'A0':(99.0,50)},chunk)
        k=len(m.e.log);m.e.release('A0',(20.0,0.0,0.5),'shot');return [x for x in m.e.log[k:] if x['event']=='release'][0]['data']['origin'],t0
    IF=[init_fix(c) for c in(100,20,1)]
    ok(all(o['rule']=='airborne_last_plant' and abs(o['origin'][0]-78.6)<.005 and o['territory']=='outside_release' for o,t0 in IF),'feet first put down where he was when the interval began, then stepped through it: the same origin at 1, 20 and 100 ms')
    # a release astride the arc: pelvis outside the zone, the nearer foot inside
    def astride(team='A',cal=None,sett=None):
        m=k4b(cal,**(sett or {}));s=m.s
        if team=='B':s.owner='B'
        x=79.9 if team=='A' else 20.1;pid=team+'0';A=kput(m,pid,(x,50));A.facing=(0.0,1.0);kgive(m,pid);still(m,pid,200);A.facing=(0.0,1.0)
        return m,A
    m,A=astride();k=len(m.e.log);m.e.release('A0',(20.0,0.0,0.5),'shot');r=[x for x in m.e.log[k:] if x['event']=='release'][0]['data']['origin']
    ok(r['pelvis_territory']=='outside_release' and r['territory']=='inside_release' and r['rule']=='both_planted_nearer_goal','both feet astride the arc: the pelvis is outside the zone, the support foot nearer the goal is inside; the foot decides, and the release record keeps both')
    pts=m.e.goal('B',50,1);g=[x for x in m.e.log if x['event']=='goal'][-1]['data'];ok(g['method']=='inside_release' and g['points']==m.e.pocket['release_points'] and g['origin_witness']['territory']=='inside_release' and abs(g['origin_to_goal_m']-(20.1-W(A)))<1e-3,'and the goal scores the zone value, with the origin witness and the foot-to-goal distance in its record')
    m,B=astride('B');k=len(m.e.log);m.e.release('B0',(-20.0,0.0,0.5),'shot');r=[x for x in m.e.log[k:] if x['event']=='release'][0]['data']['origin']
    ok(r['pelvis_territory']=='outside_release' and r['territory']=='inside_release','mirror: the same stance at the other end, for the other team, classifies the same way')
    m,A=astride(cal={'c4b':0});k=len(m.e.log);m.e.release('A0',(20.0,0.0,0.5),'shot');d=[x for x in m.e.log[k:] if x['event']=='release'][0]['data']
    ok('origin' not in d and getattr(A,'feet',None) is None and m.s.ball.pocket_origin==(A.x,A.y) and not [x for x in m.e.log if x['event']=='c4b_rules'],'with c4b = 0 the origin is the pelvis, there are no feet and no marker: C4a')
    # kick support, a tip in the air, eligibility
    m,A=astride();m.s.ball.x,m.s.ball.y,m.s.ball.z=A.x+.4,A.y,.2;m.s.ball.carrier=None;m.s.ball.mode=Ty.BallMode.LOOSE;k=len(m.e.log);m.e.strike('A0',(20.0,0.0,0.5),'kick');r=[x for x in m.e.log[k:] if x['event']=='strike'][0]['data']['origin']
    ok(r['territory']=='inside_release','a kick: the support foot on the ground decides, by the same rule')
    m=k4b();A=kput(m,'A0',(85,50));A.facing=(0.0,1.0);still(m,'A0');A.posture='airborne';A.z=.6;m.c4b_gait({'A0':(A.x,A.y,A.z)},10);A.x=78.0
    s=m.s;s.ball=Ty.Ball(mode=Ty.BallMode.SHOT,x=78.3,y=50,z=2.0,last_touch='B',scoring=True);m.e.touch('A0',deliberate=True);o=s.ball.c4b_origin
    ok(o['rule']=='airborne_last_plant' and o['territory']=='inside_release' and o['pelvis_territory']=='outside_release','a deliberate tip in the air, the pelvis now outside the zone: the last foot down (inside) is the origin')
    m=k4b();A=kput(m,'A0',(99.95,50));A.facing=(0.0,1.0);kgive(m,'A0');still(m,'A0',200);xy,rec=m.e.c4b_origin(A)
    ok(rec['foot']=='R' and xy[0]>100 and rec['territory']=='outside_release' and rec['pelvis_territory']!='outside_release' and m.e.eligible(A),'OPEN for the rulebook: a support foot beyond the end line while the pelvis is in the field. He is eligible (the pelvis decides that), and the foot is outside the field, so the origin classifies as outside')
    # Carry and the six configurations
    SC=scoring_configuration
    ok(SC('A-low')=={'outside_points':1,'release_points':2,'inner_points':3,'carry_value':0,'allow_outside_releases':True} and SC('B-high')['inner_points']==SC('B-high')['release_points']==4 and SC('C-high')['carry_value']==8 and SC('C-low')['carry_value']==4,'the six configurations of the specification are available; under B the inner arc has no distinct value')
    def carrier_at_goal(name,ms_before=500):
        m=k4b(None,**SC(name));s=m.s;A=kput(m,'A0',(99.5,50));kgive(m,'A0');s.ball.control_time=s.now-ms_before;return m,A
    m,A=carrier_at_goal('C-low');k=len(m.e.log);m.e.goal('B',50,1);g=[x['data'] for x in m.e.log[k:] if x['event']=='goal']
    ok(g and g[0]['method']=='carry' and g[0]['points']==4 and m.s.score['A']==4 and g[0]['origin_witness'] is None,'configuration C: a Carry, secure control before the ball crosses, scores the carry value')
    m,A=carrier_at_goal('A-low');k=len(m.e.log);m.e.goal('B',50,1);ok(not [x for x in m.e.log[k:] if x['event']=='goal'] and [x for x in m.e.log[k:] if x['event']=='no_goal'][0]['data']['reason']=='release_required','configuration A: Carry disabled, a carried crossing does not score')
    m,A=carrier_at_goal('C-low',0);k=len(m.e.log);m.e.goal('B',50,1);ok(not [x for x in m.e.log[k:] if x['event']=='goal' and x['data']['method']=='carry'],'control gained at the very millisecond of the crossing is not a Carry')
    m,A=carrier_at_goal('C-low');A.posture='grounded';k=len(m.e.log);m.e.goal('B',50,1);ok(not [x for x in m.e.log[k:] if x['event']=='goal'] and [x for x in m.e.log[k:] if x['event']=='no_goal'][0]['data']['reason']=='ineligible_carrier','grounded at the crossing: no Carry')
    m,A=carrier_at_goal('C-low');A.freeze_until=m.s.now+5000;k=len(m.e.log);m.e.goal('B',50,1);ok(not [x for x in m.e.log[k:] if x['event']=='goal'],'frozen at the crossing: no Carry')
    def pen(name):
        m=k4b(None,**SC(name));m.e.start_penalty('A');s=m.s;return m,s
    m,s=pen('C-high');r=s.players[s.penalty['runner']];kput(m,r.id,(99.5,50));m.e.follow_carrier();s.ball.control_time=s.now-300;m.e.goal('B',50,1);ok(s.score['A']==8,'a Carry-enabled penalty finish carried in scores the carry value')
    m,s=pen('A-high');m.e.foul(s.penalty['keeper'],s.penalty['runner'],'hold');m.e.foul(s.penalty['keeper'],s.penalty['runner'],'hold');ok(s.score['A']==4,'two Keeper offences in a run, Carry disabled: the automatic award is the zone-release value')
    m,s=pen('C-low');m.e.foul(s.penalty['keeper'],s.penalty['runner'],'hold');m.e.foul(s.penalty['keeper'],s.penalty['runner'],'hold');ok(s.score['A']==4,'Carry enabled: the automatic award is the carry value')
    m,s=pen('B-low');r=s.players[s.penalty['runner']];kput(m,r.id,(70,50));kgive(m,r.id);m.e.follow_carrier();m.e.release(r.id,(20.0,0.0,.5),'shot');m.e.goal('B',50,1);ok(s.score['A']==2,'an ordinary released penalty takes the zone-release value regardless of origin')
    # M1.5.2
    m,A=astride();m.e.release('A0',(20.0,0.0,0.5),'shot');m.e.goal('B',50,1);M=measure_c4(m.e.log)['scoring_origin']
    ok(M['shots']==1 and M['shots_whose_territory_the_foot_changes']==1 and M['shots_by_pelvis_and_foot_territory']=={'pelvis outside_release -> foot inside_release':1} and M['goals_by_method']=={'inside_release':1},'M1.5.2: every shot is classified by foot and by pelvis, and the changes are counted')
    ok(measure_c4(kb().e.log)['scoring_origin']=='unavailable','and reported unavailable without the C4b marker')
    # C4a carry-forward 1: effort-weighted time never exceeds prying time
    m=k4b();m.c3_fix_region='upper';m.c3_fix_drive=-1.0;A=kput(m,'A0',(20,50),(6,0));A.a.strength=A.a.balance=.9;ktop(m,'A0',6,True);kgive(m,'A0');B=kput(m,'B0',(18.9,51),(6,0));B.a.strength=B.a.tackling=.3;ktop(m,'B0',6)
    tg=lambda:{'A0':(99,50),'B0':(A.x,A.y)};m.c3_fix_escape=0.;ktick(m,tg(),200);m.c3_fix_escape=None;t0=m.s.now
    while m.s.now-t0<1500:ktick(m,tg(),10)
    ends=[x['data'] for x in m.e.log if x['event']=='c3_hold_end'];ok(any(e['cause']=='pried_off' for e in ends) and all(e['escape_share_ms']<=e['escape_effort_ms']+1e-6 for e in ends),'C4a CORRECTION (the Lead\'s audit): a hold thrown off part-way through a drift: the effort-weighted time is taken back with the prying time, so it never exceeds it')
    # C4a carry-forward 2: the mixed roster balanced among starters and rotated by seed
    def mixed(seed):
        mm=CORE.match.Match(configuration({**SETTINGS,'archery':False},seed,{**C4BCAL,'contact_roster':1}));return mm
    m1=mixed(1);m2=mixed(2)
    def grp(mm,team,active):return sorted([q for q in mm.s.players.values() if q.team==team and q.role=='field' and q.active==active],key=lambda q:q.slot)
    mean=lambda g,a:sum(getattr(q.a,a) for q in g)/len(g)
    ok(all(abs(mean(grp(m1,t,act),a)-.68)<1e-9 for t in('A','B') for act in(True,False) for a in('strength','balance','tackling')),'C4a CORRECTION (the Lead\'s audit): design 1 now averages exactly 0.68 in each attribute among the starters and among the reserves, both teams')
    sig=lambda mm,t,act:[(q.a.strength,q.a.balance,q.a.tackling) for q in grp(mm,t,act)]
    ok(sig(m1,'A',True)==sig(m1,'B',True) and sorted(sig(m1,'A',True))==sorted(sig(m2,'A',True)) and sig(m1,'A',True)!=sig(m2,'A',True) and all(not(q.role!='field') or q.a.strength==.68 for q in m1.s.players.values()),'mirrored between the teams; the same ten profiles every match, rotated through the slots by the seed')
    m4=CORE.match.Match(configuration({**SETTINGS,'archery':False},1,{**C4BCAL,'contact_roster':4}));ok(abs(mean(grp(m4,'A',True),'balance')-.576)<1e-9,'the C4a design is kept as design 4, for reproducing the C4a smoke matches (its starters average 0.576 balance)')
    # ================= C4c: Keeper mechanics; the C4b r1 exact landing tie =================
    # Every scenario above runs with c4c = 0 (the C4b Keeper): they describe their own checkpoints and still hold.
    def k4c(cal=None,**kw):return kb({'c3c':1,'c4b':1,'c4c':1,'escape_allocation':1,**(cal or {})},**kw)
    # the exact tie (the Lead's C4b r1 geometry): a prepared shot falls due at the very instant the solved flight lands
    def tie(chunk,rel,L=.05):
        m=k4b();A=kput(m,'A0',(79.4,50));kgive(m,'A0');ktick(m,{'A0':(79.4,50)},1)
        A.vx=15.0;ktop(m,'A0',15.0,True);A.posture='airborne';A.z=.1;A.vz=(.5*m.assume['gravity']*L*L-A.z)/L
        m.c4b_gait({'A0':(A.x,A.y,A.z)},0);t0=m.s.now;m.pending_ball_actions['A0']=(t0+rel,'shot',None);m.c3_prep['A0']=t0;end=t0+rel
        while m.s.now<end:ktick(m,{'A0':(99.0,50)},min(chunk,end-m.s.now))
        ktick(m,{'A0':(99.0,50)},1);r=[x for x in m.e.log if x['event']=='release' and x['data']['player']=='A0'][0]
        return r['t_ms']-t0,r['data']['origin']['territory']
    TIE=[tie(c,t) for t in(49,50,51) for c in(100,20,1)]
    ok(all(dt==t for (dt,_),t in zip(TIE,[49]*3+[50]*3+[51]*3)) and [x[1] for x in TIE]==['outside_release']*3+['inside_release']*6,'C4b r1 carry-forward: a release due at the exact instant of a landing comes after it, at 100, 20 and 1 ms intervals alike (before it: the takeoff foot)')
    # ---- the Keeper (B10 defends the goal at x = 100); a fixed Keeper so that the numbers are exact ----
    class FixRng:
        """every random draw at the top of its range: a sampled reflex never sets the hands, a catch is never secure"""
        def random(self):return .999999
        def uniform(self,a,b):return(a+b)/2
        def gauss(self,mu,sd):return mu
        def getstate(self):return None
        def setstate(self,s):pass
    def kc(cal=None,lvl=.68,**kw):
        m=k4c(cal,**kw);K=m.s.players['B10'];K.a.height=2.55;K.a.reach=.46*2.55;K.a.acceleration=9.0;K.a.jump_height=1.6;K.a.braking=12.0;K.a.maximum_speed=25.0
        for k_ in('awareness','agility','keeper_skill','catching'):setattr(K.a,k_,lvl)
        return m,K
    def ready(m,K,sx,sy,kxy=(96.0,50.0),ms=1000):
        kput(m,'A0',(sx,sy));kgive(m,'A0');kput(m,'B10',kxy)
        for _ in range(ms//100):ktick(m,{'A0':(sx,sy)},100)
    def shoot(m,ty,tz,speed=40.0):
        b=m.s.ball;v,ft=CORE.geometry.launch_for((b.x,b.y,b.z),(100.2,50+ty,tz),speed,m.assume['gravity'],m.assume['ball_drag']);t0=m.s.now;k0=len(m.e.log);m.e.release('A0',v,'shot');return t0,k0,ft
    def recs(m,k0,name):return[x for x in m.e.log[k0:] if x['event']==name]
    CC=C4CCAL
    m,K=kc();mk=[x['data'] for x in m.e.log if x['event']=='c4c_rules'];ok(m.c4c and mk and mk[0]['keeper_reaction_s']==CC['keeper_reaction_s'],'C4c: the switch is on and the marker records the Keeper parameters')
    # positioning: on the line from the centre of his goal to the ball, off his line by keeper_depth_frac of its distance, within limits
    m,K=kc();ready(m,K,80,50);ok(abs(K.x-96.0)<.25 and abs(K.y-50)<.05,'positioning: a carrier 20 m out, central: he stands 4 m off his line (0.25 x 20, at most 4 m; within the settling of the kernel, 0.25 m)')
    m,K=kc();ready(m,K,92,50);ok(abs(K.x-98.0)<.25,'a carrier 8 m out: 2 m off his line')
    m,K=kc();kput(m,'A0',(85,62));kgive(m,'A0');t=m.c4c_position(K);d=math.hypot(15,12);ok(abs(t[0]-(100-15/d*min(4,.25*d)))<1e-9 and abs(t[1]-(50+12/d*min(4,.25*d)))<1e-9,'off-centre: on the line to the ball')
    m,K=kc();kput(m,'A0',(80,50));kgive(m,'A0');m.pending_ball_actions['A0']=(m.s.now+200,'shot',None);kput(m,'B10',(97.0,50.5));ok(m.c4c_position(K)==(97.0,50.5),'a carrier within 35 m begins a wind-up: he stops and sets where he is')
    m,K=kc();kput(m,'A0',(95,51),(6.0,0.0));kgive(m,'A0');t=m.c4c_position(K);ok(abs(t[0]-(95+6*.3))<1e-9,'a carrier within keeper_confront_m of the centre of his goal: he goes to meet him')
    # perception and reaction: nothing before his reaction instant; the interval is cut so that he acts in that millisecond
    m,K=kc();ready(m,K,75,50);m.rng['ball']=FixRng();t0,k0,ft=shoot(m,4.0,3.0)
    while m.s.now<t0+400:ktick(m,{'A0':(75,50)},100)
    rd=recs(m,k0,'keeper_read');react=1000*CC['keeper_reaction_s']*(1.3-.6*.68)
    ok(len(rd)>=1 and rd[0]['t_ms']==math.ceil(t0+react) and rd[0]['data']['reaction_ms']==math.ceil(t0+react)-t0 and not rd[0]['data']['unset'],'reaction: a set Keeper first acts on a flight keeper_reaction_s x (1.3 - 0.6 x awareness) after its release (178.4 ms at 0.68), in that millisecond')
    m,K=kc(lvl=.93);ready(m,K,75,50);m.rng['ball']=FixRng();t0,k0,ft=shoot(m,4.0,3.0)
    while m.s.now<t0+400:ktick(m,{'A0':(75,50)},100)
    rd=recs(m,k0,'keeper_read');ok(rd and rd[0]['t_ms']==math.ceil(t0+1000*CC['keeper_reaction_s']*(1.3-.6*.93)),'more awareness, a quicker reaction (148.4 ms at 0.93)')
    m,K=kc();ready(m,K,75,50);K.vx=2.0;m.rng['ball']=FixRng();t0,k0,ft=shoot(m,4.0,3.0)
    while m.s.now<t0+400:ktick(m,{'A0':(75,50)},100)
    rd=recs(m,k0,'keeper_read');ok(rd and rd[0]['data']['unset'] and rd[0]['t_ms']==math.ceil(t0+react+1000*CC['keeper_unset_s']),'moving faster than keeper_set_mps when the ball is released: keeper_unset_s later')
    # the read: on his feet when he can; else a jump or dive; else no attempt
    def kshot(sx,sy,ty,tz,speed=40.0,kxy=(96.0,50.0),lvl=.68,rng=None,cal=None,ms=1200):
        m,K=kc({'keeper_confront':0,**(cal or {})},lvl=lvl,ball_speed=speed);ready(m,K,sx,sy,kxy);m.rng['ball']=rng or FixRng();t0,k0,ft=shoot(m,ty,tz,speed) #ball_speed sets the release limit
        while m.s.now<t0+ms:ktick(m,{'A0':(sx,sy)},100)
        return m,K,t0,k0
    m,K,t0,k0=kshot(80,50,0.0,1.6);rd=recs(m,k0,'keeper_read');kcx=recs(m,k0,'keeper_contact')
    ok(rd and rd[0]['data']['kind']=='step' and not recs(m,k0,'keeper_landed') and kcx and kcx[0]['data']['kind']=='parry' and kcx[0]['t_ms']>=rd[0]['t_ms'],'a shot at his chest from 20 m: he stays on his feet (no launch) and plays it with his hands, after his reaction instant')
    ok(len(kcx)==1 and not [x for x in kcx if x['data']['kind']=='body'],'his hands meet the ball before it reaches his body')
    d=kcx[0]['data'];n_=d['normal'];hv=d['hand_velocity'];ri=[d['velocity_in'][j]-hv[j]for j in range(3)];ro=[d['velocity_out'][j]-hv[j]for j in range(3)]
    dot=lambda a,b_:sum(a[j]*b_[j]for j in range(3));tan=lambda r:[r[j]-dot(r,n_)*n_[j]for j in range(3)]
    ok(dot(ri,n_)<0 and abs(dot(ro,n_)+CC['keeper_parry_restitution']*dot(ri,n_))<.01 and max(abs(a-b_)for a,b_ in zip(tan(ri),tan(ro)))<.01 and d['deliberate'],'a parry is a rebound off the hand: relative to it, the normal component of the ball\'s velocity is reversed and scaled by keeper_parry_restitution, the rest kept; read, it is deliberate')
    ok(abs(dot(hv,n_)-CC['keeper_parry_swing_mps'])<2.0,'in a deliberate parry the hand is driven into the ball: keeper_parry_swing_mps along the normal, on top of his own movement (under 2 m/s here)')
    m,K,t0,k0=kshot(80,50,-2.5,.5);rd=recs(m,k0,'keeper_read');ln=recs(m,k0,'keeper_landed');L_=rd[0]['data'] if rd else {}
    ok(L_.get('kind')=='launch' and L_.get('dive') and L_['lean']>=CC['keeper_dive_lean'] and ln and ln[0]['data']['dive'],'a low shot 2.5 m to his side from 20 m: he dives (a launch with lean of at least keeper_dive_lean)')
    dn=[x for x in recs(m,k0,'c3_down') if x['data']['player']=='B10']
    ok(ln and ln[0]['t_ms']==math.ceil(rd[0]['t_ms']+L_['land_ms']) and dn and dn[0]['t_ms']==ln[0]['t_ms'] and ln[0]['data']['recover_ms']==dn[0]['data']['upright_at']-ln[0]['t_ms'],'he lands when his flight reaches the ground, in that millisecond; after a dive he goes to ground by the engine\'s own grounding (C3b: slide, then get-up)')
    m,K=kc({'keeper_confront':0});ready(m,K,80,50);m.rng['ball']=FixRng();t0,k0,ft=shoot(m,-2.5,.5);vs=[]
    while m.s.now<t0+800:
        ktick(m,{'A0':(80,50)},10)
        if getattr(K,'c4c_launch',None):vs.append((round(K.vx,9),round(K.vy,9)))
        if K.posture=='grounded':break
    ok(vs and len(set(vs))==1 and K.posture=='grounded' and K.next_action==recs(m,k0,'keeper_landed')[0]['t_ms']+recs(m,k0,'keeper_landed')[0]['data']['recover_ms'],'in the air he cannot steer: his horizontal velocity does not change from launch to landing; then he is on the ground until his recovery ends')
    m,K,t0,k0=kshot(88,50,4.5,3.5,speed=50.0,kxy=(97.0,50.0),ms=600);rd=recs(m,k0,'keeper_read')
    ok(rd and rd[0]['data']['kind']=='none' and(rd[0]['data']['least_miss_m'] is None or rd[0]['data']['least_miss_m']>CC['keeper_attempt_margin_m'])and rd[0]['data']['crossing'][0]<1000*CC['keeper_launch_min_s']+100 and not recs(m,k0,'keeper_contact'),'a shot into the far top corner from 12 m at 50 m/s: nothing he can reach in the time left, so no attempt; the time left and the nearest miss (if any launch could be timed) are recorded')
    # the body: physics, not a play
    m,K,t0,k0=kshot(94,50,0.0,.5,speed=50.0,kxy=(98.5,50.0),ms=600);kcx=recs(m,k0,'keeper_contact');rd=recs(m,k0,'keeper_read')
    ok(kcx and kcx[0]['data']['kind']=='body' and not kcx[0]['data']['deliberate'] and kcx[0]['t_ms']<t0+1000*CC['keeper_reaction_s']*(1.3-.6*.68) and not [g for g in recs(m,k0,'goal') if g['data']['method']=='own_goal'],'a low shot from 6 m at 50 m/s arrives before he can react: his body blocks it; a block is incidental (it is not a play and never an own goal)')
    d=kcx[0]['data'];n_=d['normal'];hv=d['hand_velocity'];ri=[d['velocity_in'][j]-hv[j]for j in range(3)];ro=[d['velocity_out'][j]-hv[j]for j in range(3)]
    ok(abs(dot(ro,n_)+CC['keeper_body_restitution']*dot(ri,n_))<.01,'off his body the ball rebounds with keeper_body_restitution')
    class SeqRng(FixRng):
        def __init__(self,seq):self.seq=list(seq)
        def random(self):return self.seq.pop(0)if self.seq else .999999
    m,K,t0,k0=kshot(91,50,0.0,1.6,speed=50.0,kxy=(97.75,50.0),rng=SeqRng([1e-9]),ms=600);kcx=recs(m,k0,'keeper_contact')
    ok(kcx and kcx[0]['data']['kind']=='parry' and kcx[0]['t_ms']<t0+1000*CC['keeper_reaction_s']*(1.3-.6*.68) and not kcx[0]['data']['deliberate'],'a reflex touch before his reaction instant (the catch model\'s sampled readiness) is incidental, like any player\'s, and the shot keeps its origin')
    # with c4c = 0: the C4b Keeper
    m=k4b();ready(m,m.s.players['B10'],80,50);t0,k0,ft=shoot(m,0.0,1.6)
    while m.s.now<t0+800:ktick(m,{'A0':(80,50)},100)
    ok(not recs(m,k0,'keeper_read') and not recs(m,k0,'keeper_contact') and not [x for x in m.e.log if x['event']=='c4c_rules'] and not m.c4c,'with c4c = 0 the Keeper is the C4b Keeper: no read, no contact record, no marker')
    def bad4c(**c):
        try:configuration(SETTINGS,1,{**C4CCAL,**c});return False
        except ValueError:return True
    ok(bad4c(c4c=2) and bad4c(keeper_confront=-1) and not bad4c() and all(k_ in C3_RANGES for k_ in('c4c','keeper_reaction_s','keeper_launch_min_s','keeper_parry_swing_mps','keeper_confront_m','keeper_gather_m')),'the C4c values are validated, each with its declared range')
    # M1.6
    m,K,t0,k0=kshot(80,50,-2.5,.5,rng=FixRng());M=measure_c4(m.e.log)['keeper']
    ok(M['shots']==1 and sum(M['outcomes'].values())==1 and M['dives']==1 and M['reads'].get('launch')==1,'M1.6: every shot is followed to its outcome, with the Keeper\'s read and his dives')
    ok(measure_c4(k4b().e.log)['keeper'].startswith('unavailable'),'and the Keeper section is reported unavailable without the C4c marker')
    # the independent review's cases
    m,K,t0,k0=kshot(80,50,-5.0,.5,ms=1500);rd=recs(m,k0,'keeper_read');ln=recs(m,k0,'keeper_landed');gl=recs(m,k0,'goal')
    ok(rd and rd[0]['data']['kind']=='launch' and gl and ln and gl[0]['t_ms']<ln[0]['t_ms'] and ln[0]['t_ms']==math.ceil(rd[0]['t_ms']+rd[0]['data']['land_ms']),'a dive still in the air when the ball goes dead (here a goal): he lands when his flight reaches the ground, in dead time, not at the restart')
    def loose(v,bx=98.4):
        m,K=kc({'keeper_confront':0});s=m.s;kput(m,'B10',(99.0,50.0));m.hands_set={}
        s.ball=Ty.Ball(mode=Ty.BallMode.LOOSE,x=bx,y=50.0,z=.1075,vx=-v,vy=0.,vz=0.,last_touch='A',release_time=s.now-300);s.ball.version+=1
        for _ in range(10):ktick(m,{},100)
        return s.ball.carrier
    ok(all(loose(v)=='B10' for v in(0.,.3,1.,2.)),'a slow loose ball in front of him, still or rolling away: he gathers it (the fast-ball rule applies only above 5 m/s)')
    m,K=kc({'keeper_confront':0});s=m.s;s.phase=Ty.Phase.AWARD;s.owner='A';s.award_spot=(96.5,50.);s.award_available=s.now;s.award_deadline=s.now+5000
    s.ball=Ty.Ball(mode=Ty.BallMode.LOOSE,x=96.5,y=50.0,z=.1075,last_touch='B',release_time=s.now-300);s.ball.version+=1;kput(m,'B10',(98.0,50.0),(-3.0,0.));k0=len(m.e.log)
    for _ in range(6):ktick(m,{'B10':(95.0,50.0)},100)
    ok(not recs(m,k0,'keeper_contact') and not recs(m,k0,'touch') and s.ball.vx==0,'his body follows the participation rules of a play with the hands: walking into the ball in the other team\'s exclusive recovery, he does not move it')
    m,K=kc({'keeper_confront':0});s=m.s;kput(m,'B10',(98.5,50.0));K.posture='airborne';K.z=.6;K.vz=2.0;off=m.c4c_off(K,1.0,0.,1.)
    K.c4c_launch={'t0':s.now,'t_land':s.now+600,'off':off,'lean':1.0,'dir':(0.,1.),'dive':True}
    s.ball=Ty.Ball(mode=Ty.BallMode.PASS,x=98.7,y=51.95,z=K.z+off[2]+.25,vx=-3.0,vy=0.,vz=0.,last_touch='B',release_time=s.now-600,last_releaser='B3');s.ball.version+=1
    K.c4c_seen=(s.ball.version,s.now-600,s.now-400,False);K.c4c_plan={'kind':'launch'};m.hands_set={'B10':True};m.rng['ball']=SeqRng([0.,0.,0.]);k0=len(m.e.log);ktick(m,{},100)
    ok(s.ball.carrier=='B10' and not recs(m,k0,'contact_rejected'),'a secure catch at full stretch in a dive (the ball almost 2 m to his side): taken where his hands are, not refused for being far from his feet')
    # ================= C4c2: corrections, scoring rulings, common controller =================
    # Every scenario above runs with c4c2 = 0 (C4c1): they describe their own checkpoints and still hold.
    def k42(cal=None,**kw):return kb({'c3c':1,'c4b':1,'c4c':1,'c4c2':1,'escape_allocation':1,**(cal or {})},**kw)
    SC2=lambda name:{**scoring_configuration(name),'inner_zone_radius':15.0,'keeper_zone_radius':20.0,'ball_speed':50.0}   # the smoke-match geometry: inner arc 15 m, Keeper Zone 20 m
    # ---- the Lead's correction: a body contact keeps a recovery already being served ----
    def lying(cal=None,freeze=False,upright_hold=None):
        m=k42({'keeper_confront':0,**(cal or {})});s=m.s;K=kput(m,'B10',(98.0,50.0));K.facing=(-1.0,0.0)
        if upright_hold is None:m.e.go_down(K);K.c4c_down=((-1.0,0.0),K.next_action)
        else:K.next_action=s.now+upright_hold   # an upright Keeper serving a restriction (as after landing with the ball)
        if freeze:K.freeze_until=s.now+5000
        deadline=K.next_action
        x0,rt=(94.5,s.now-300)if upright_hold is None else(96.0,s.now)   # upright: struck before his reaction instant, so he has not moved
        s.ball=Ty.Ball(mode=Ty.BallMode.SHOT,x=x0,y=50.0,z=.4,vx=30.0,vy=0.0,vz=0.0,last_touch='A',last_releaser='A0',release_time=rt,scoring=True);s.ball.version+=1;s.ball.pocket_release_team='A';s.ball.pocket_origin=(x0,50.0)
        for _ in range(20):
            ktick(m,{},10)
            if [x for x in m.e.log if x['event']=='keeper_contact']:break
        c=[x for x in m.e.log if x['event']=='keeper_contact'];at=K.next_action;ktick(m,{},10)
        return m,K,c,deadline,at
    m,K,c,dl,at=lying();ok(c and c[0]['data']['kind']=='body' and at==dl and K.posture=='grounded' and m.s.ball.vx<0,'C4c2 (the Lead): a ball striking a lying Keeper rebounds, and his get-up deadline is kept: still down 10 ms later')
    m,K,c,dl,at=lying(cal={'c4c2':0});ok(c and at<dl,'with c4c2 = 0 the C4c1 defect is reproduced: the contact erased the deadline')
    m,K,c,dl,at=lying(upright_hold=600);ok(c and at==dl and K.posture=='upright','an upright Keeper serving a restriction (as after landing with the ball): the body contact does not shorten it')
    m,K,c,dl,at=lying(freeze=True);ok(c and c[0]['data']['kind']=='body','a frozen Keeper is still a passive body on the field: the ball meets it')
    # ---- the Lead's hardening: a body proposal is revalidated at commitment ----
    def stale(change):
        m=k42();s=m.s;K=kput(m,'B10',(98.0,50.0))
        s.ball=Ty.Ball(mode=Ty.BallMode.SHOT,x=97.0,y=50.0,z=.4,vx=30.0,last_touch='A',last_releaser='A0',release_time=s.now-300,scoring=True)
        ev=Ty.Event('touch','B10',data={'c1_contact':True,'c4c_kind':'body','deliberate':False,'ball_point':(97.5,50.0,.4),'velocity':(-9.0,0.0,0.0),'cooldown_ms':0},at=s.now)
        if change=='excluded':K.active=False
        if change=='exclusive_recovery':s.phase=Ty.Phase.AWARD;s.owner='A'
        if change=='grounded':m.e.go_down(K)
        acc=m.e.c1_commit(ev);return acc,s.ball.vx
    ok(stale('excluded')==(False,30.0) and stale('exclusive_recovery')==(False,30.0),'a queued body contact is refused at commitment if he has left the field, or the other team now has exclusive recovery; the ball is untouched')
    ok(stale('grounded')==(True,-9.0),'a present, grounded Keeper is still a body: accepted (body eligibility is not hand-play eligibility)')
    # ---- DreLen, 9 October: arcs belong to the farther territory ----
    m=k42(None,**SC2('C-low'));e=m.e
    ok([e.territory('A',100-d,50.0) for d in(15-1e-5,15.0,15+1e-5,20-1e-5,20.0,20+1e-5)]==['inner_release','inside_release','inside_release','inside_release','outside_release','outside_release'] and [e.territory('B',d,50.0) for d in(15-1e-5,15.0,20-1e-5,20.0)]==['inner_release','inside_release','inside_release','outside_release'],'decided by DreLen: a foot on the inner arc is a zone release; on the Keeper Zone arc, an outside release; both ends')
    m0=kb({'c3c':1,'c4b':1,'c4c':1,'c4c2':0},**SC2('C-low'));ok(m0.e.territory('A',85.0,50.0)=='inner_release' and m0.e.territory('A',80.0,50.0)=='inside_release','with c4c2 = 0, the C4c1 deeper-territory convention')
    def stance(m,pid,x,y=50.0,foot=None):
        A=kput(m,pid,(x,y));A.facing=(0.0,1.0);m.s.owner=pid[0];kgive(m,pid);ktick(m,{pid:(x,y)},200);A.facing=(0.0,1.0)
        if foot is not None:A.feet['L'].update(x=foot,y=y,planted=True);A.feet['R'].update(x=foot,y=y,planted=True)
        return A
    def rel_terr(team,foot):
        m=k42(None,**SC2('C-low'));pid=team+'0';stance(m,pid,foot,foot=foot);k=len(m.e.log)
        m.e.release(pid,(20.0 if team=='A' else -20.0,0.0,.5),'shot');return [x for x in m.e.log[k:] if x['event']=='release'][0]['data']['origin']['territory']
    ok([rel_terr('A',f) for f in(85.0,85.00001,84.99999,80.0,80.00001,79.99999)]==['inside_release','inner_release','inside_release','outside_release','inside_release','outside_release'] and [rel_terr('B',f) for f in(15.0,14.99999,20.0,19.99999)]==['inside_release','inner_release','outside_release','inside_release'],'release witnesses with the support foot exactly on, and beside, each arc, both teams')
    # ---- DreLen, 9 October: an offensive goal keeps the last offensive touch's origin through defensive touches ----
    def flight(team='A',kind='shot',foot=88.0,conf='C-low',cal=None):
        m=k42(cal,**SC2(conf));s=m.s;pid=team+'0';x=foot if team=='A' else 100-foot;stance(m,pid,x,foot=x)
        m.e.release(pid,(20.0 if team=='A' else -20.0,0.0,0.0),kind);return m,s
    def score(m,defending):
        s=m.s;s.ball.x=100.2 if defending=='B' else -.2;s.ball.y=50.0;s.ball.z=1.0;k=len(m.e.log)
        m.e.batch([Ty.Event('goal',data={'defending':defending,'y':50.0,'z':1.0})]);g=[x['data'] for x in m.e.log[k:] if x['event']=='goal'];return g[0] if g else None
    for deliberate in(False,True):
        m,s=flight();kput(m,'B10',(98.0,50.0));m.e.touch('B10',deliberate);g=score(m,'B')
        ok(g and g['method']=='inner_release' and g['points']==3 and g['team']=='A' and g['flight_team']=='A' and g['defensive_touches'][0][0]=='B10' and g['offensive_goal_through_defensive_touch'],
           'decided by DreLen: an inner shot touched by the Keeper (%s) still goes in for 3: not an own goal, value from the shooter' % ('a deliberate parry' if deliberate else 'incidental'))
    m,s=flight(kind='pass');kput(m,'B3',(95.0,50.0));m.e.touch('B3',False);g=score(m,'B');ok(g and g['method']=='inner_release' and g['points']==3,'a pass flight deflected in by a defender: an offensive goal from the passer')
    m,s=flight(foot=75.0);A3=kput(m,'A3',(88.0,50.0));A3.feet={'L':{'x':88.0,'y':50.0,'planted':True,'t':m.s.now,'n':0},'R':{'x':88.0,'y':50.0,'planted':True,'t':m.s.now,'n':-1}};A3.last_plant=None
    m.e.touch('A3',False);kput(m,'B10',(98.0,50.0));m.e.touch('B10',True);g=score(m,'B')
    ok(g and g['method']=='inner_release' and g['last_offensive_toucher']=='A3' and g['points']==3,'an outside shot touched (incidentally) by a team-mate standing in the inner zone, then parried in: the last offensive touch sets the value (3), whether or not it was deliberate')
    m,s=flight(team='B');kput(m,'A10',(2.0,50.0));m.e.touch('A10',True);g=score(m,'A');ok(g and g['team']=='B' and g['method']=='inner_release' and g['points']==3,'mirror: the same at the other end, for the other team')
    m,s=flight(conf='A-low');kput(m,'B10',(98.0,50.0));m.e.touch('B10',True);g=score(m,'B');ok(g and g['points']==3,'and under configuration A')
    # own goals and the open reversal
    def own(touch_by=None,rule=0):
        m=k42({'reversal_rule':rule},**SC2('C-low'));s=m.s;A=stance(m,'A0',30.0,foot=30.0);m.e.release('A0',(-20.0,0.0,0.0),'pass')
        if touch_by:B=kput(m,touch_by,(5.0,50.0));B.feet={'L':{'x':5.0,'y':50.0,'planted':True,'t':s.now,'n':0},'R':{'x':5.0,'y':50.0,'planted':True,'t':s.now,'n':-1}};m.e.touch(touch_by,False)
        return score(m,'A')
    g=own();ok(g and g['team']=='B' and g['method']=='own_goal' and g['points']==2,'decided by DreLen: a team flight into its own goal with no opponent touch is a true own goal (zone value, 2)')
    g=own('B3');ok(g and g['method']=='reversal' and g['points']==2 and g['defensive_touches'][0][0]=='B3','OPEN (the Lead): the same flight turned in by an opponent without control is recorded as its own method, reversal; prototype rule 0 gives it the own-goal value')
    g=own('B3',1);ok(g and g['method']=='reversal' and g['points']==3,'prototype rule 1: valued from the redirecting opponent (his foot 5 m from the goal: inner, 3)')
    # new control ends the old flight
    m,s=flight();B=kput(m,'B5',(96.0,50.0));s.ball.x,s.ball.y,s.ball.z=96.3,50.0,1.2;s.ball.vx=s.ball.vy=s.ball.vz=0.0;m.e.acquire('B5')
    ok(s.ball.carrier=='B5' and s.ball.pocket_release_team=='B','secured defensive control ends the attacking flight: his team owns what follows')
    B.facing=(0.0,1.0);ktick(m,{'B5':(96.0,50.0)},200);m.e.release('B5',(-20.0,0.0,0.0),'pass');g=score(m,'A');ok(g and g['team']=='B' and g['method']=='outside_release' and g['points']==1,'a later release is a new flight: its value comes from the new releaser (here from 96 m, outside the far zone: 1)')
    m,s=flight(cal={'c4c2':0});kput(m,'B10',(98.0,50.0));m.e.touch('B10',True);g=score(m,'B');ok(g and g['method']=='own_goal' and g['points']==2,'with c4c2 = 0 the C4c1 rule is reproduced: the deliberate parry made it a 2-point own goal')
    # ---- the common controller (build specification 7) ----
    m=k42(None,**SC2('A-low'));A=kput(m,'A0',(80.0,50.0));B=kput(m,'B3',(70.0,50.0));R=A.radius+B.radius+.7*(A.a.reach+B.a.reach)
    gap=10.0-R;a_=B.a.acceleration*(.55+.45*B.fatigue);V=B.a.maximum_speed*(.70+.30*B.fatigue)*.88;t1=V/a_;d1=V/2*t1
    exp=math.sqrt(2*gap/a_)if d1>=gap else t1+(gap-d1)/V
    ok(abs(m.c4c2_engage_s(B,A,A.x,A.y)-exp)<1e-9,'the controller estimator: a standing opponent reaches holding range in the kinematic time (accelerating to his running speed)')
    B.vx=-5.0;ok(m.c4c2_engage_s(B,A,A.x,A.y)>exp,'one running away must first stop: later')
    E=CORE.match.C4C2_EST['conv'];si=E['speed'].index(m.cfg['pocket']['ball_speed']);hi=E['height'].index(2.55)
    ok(abs(m.c4c2_conv(12.0,0.0,'A')-E['p'][si][hi][E['dist'].index(12)][0])<1e-12 and abs(m.c4c2_conv(15.0,30.0,'A')-E['p'][si][hi][E['dist'].index(15)][1])<1e-12,'the conversion estimate is the drill table at its cells (c4c2_estimates.json, embedded)')
    def ctrl_state(conf,cx,cy,cal=None,mates=(),keeper_x=99.0):
        m=k42({'keeper_confront':0,**(cal or {})},**SC2(conf));s=m.s;A=stance(m,'A0',cx,y=cy);kput(m,'B10',(keeper_x,50.0))
        for pid,xy in mates:kput(m,pid,xy)
        s.ball.control_time=s.now-1000;s.possession_ms=40000;return m,A
    def decide(m,A):
        k=len(m.e.log);m.c4c2_decide(A,m.s.possession_ms/1000.,False);d=[x['data'] for x in m.e.log[k:] if x['event']=='controller_decision'];return d[0] if d else None
    m,A=ctrl_state('A-low',88.0,50.0);d=decide(m,A);ok(d and d['choice']=='shoot' and d['ev']['shoot']>d['ev']['continue'],'alone 12 m out (inner zone, 3 points) facing a set Keeper: he shoots; the record carries every option\'s expected points')
    m,A=ctrl_state('A-low',70.0,50.0,mates=(('A3',(88.0,52.0)),));d=decide(m,A);ok(d and d['choice']=='pass' and d['target']=='A3' and d['ev']['pass']>d['ev']['continue'],'30 m out with a team-mate free 12 m from the goal: he passes to him (the pass is worth more than carrying on)')
    m,A=ctrl_state('C-low',91.0,50.0,cal={'ctrl_keeper':0});d=decide(m,A);ok(d and d['choice']=='carry' and getattr(A,'c4c2_intent',None)=='carry','configuration C, 9 m out, the Keeper staying and nobody chasing: he carries it in (the carry table says it succeeds)')
    tg={};m.c4c2_targets(tg);ok(tg.get('A0',(0,0))[0]>100.0,'a carry intent drives at the goal')
    for _ in range(20):
        ktick(m,{'A0':tg['A0']},100)
        if [x for x in m.e.log if x['event']=='goal']:break
    g=[x['data'] for x in m.e.log if x['event']=='goal'];ok(g and g[0]['method']=='carry' and g[0]['points']==4,'and the carry scores 4')
    m,A=ctrl_state('C-low',91.0,50.0);d=decide(m,A);E1=m.c4c2_eval(A,A.x,A.y,40.0,origin=True);m0,A0=ctrl_state('C-low',91.0,50.0,cal={'ctrl_keeper':0});E0=m0.c4c2_eval(A0,A0.x,A0.y,40.0,origin=True)
    ok(E1['p_carry']<E0['p_carry'] and (d is None or d['choice']!='carry'),'the same with the Keeper choosing by the estimates (ctrl_keeper): he would come out, so a carry from 9 m is worth less (the confronting-Keeper table) and is not chosen')
    K=m.s.players['B10'];ok(m.c4c2_confront(K,A)is True,'the Keeper\'s choice: in configuration C he comes out at a carrier 9 m out (conceding less than staying, by the same tables)')
    m2,A2=ctrl_state('A-low',91.0,50.0);ok(m2.c4c2_confront(m2.s.players['B10'],A2)is False,'with no Carry value (configuration A) there is nothing to stop by coming out: he stays')
    def opts(conf):
        m,A=ctrl_state(conf,88.0,50.0);E=m.c4c2_eval(A,A.x,A.y,40.0,origin=True);return {'shoot':E['shoot'],'carry':E['carry'],'continue':m.c4c2_cont(A,A.x,A.y,40.0)}
    ol=opts('B-low');oh=opts('B-high')
    ok(all(abs(oh[k]-2*ol[k])<1e-9 for k in ol) and max(ol,key=ol.get)==max(oh,key=oh.get),'one controller for every configuration: doubling every value (B-low to B-high) doubles every estimate and changes no choice')
    m,A=ctrl_state('C-low',91.0,50.0,cal={'ctrl_keeper':0,'ctrl_style_A':2},mates=(('A3',(89.0,56.0)),));d=decide(m,A);ok(d and d['style']==2,'a styled team records its approach on every decision')
    m,A=ctrl_state('A-low',88.0,50.0,cal={'controller':0});ok(not m.ctrl,'controller = 0: the inherited controllers')
    m=k42({'keeper_height_m':3.2004});K=m.s.players['B10'];ok(abs(K.a.height-3.2004)<1e-12 and abs(K.a.reach-.46*3.2004)<1e-12 and m.s.players['A0'].a.height==2.55,'keeper_height_m: both Keepers at that height, reach 0.46 x height; nobody else changes')
    try:configuration(SETTINGS,1,{**C4C2CAL,'keeper_height_m':2.6});bad=False
    except ValueError:bad=True
    ok(bad,'a Keeper height below 9 ft (other than 0, the inherited Keeper) is refused')
    # coordinated short inbound and entry options
    m=k42(None,**SC2('A-low'));s=m.s;s.phase=Ty.Phase.DEAD;s.ball=Ty.Ball(mode=Ty.BallMode.DEAD,x=50.0,y=0.0,z=.1075)
    for pid,xy in (('A1',(50.0,1.0)),('A2',(52.0,8.0)),('A3',(46.0,10.0)),('B4',(60.0,30.0))):kput(m,pid,xy)
    r=Ty.Restart('A',50.0,0.0,'boundary',created_at=s.now,kind='inbound');r.clearance=3.0;r.taker_spot=(50.0,-.4);s.restart=r
    tg=m.targets_dead();io=[x['data'] for x in m.e.log if x['event']=='inbound_options']
    ok(io and io[0]['taker']=='A1' and {io[0]['short'],io[0]['entry']}=={'A2','A3'} and math.hypot(tg[io[0]['short']][0]-50.0,tg[io[0]['short']][1])<7.0 and math.hypot(tg[io[0]['entry']][0]-50.0,tg[io[0]['entry']][1])>9.0,
       'an inbound: the two nearest team-mates go to a short option about 6 m into the field and an entry option about 12 m on, and the record says who')
    order=m.c4c2_inbound_order(r,s.players['A1'],[s.players['A3'],s.players['A2']]);ok([q.id for q in order][:2]==[io[0]['short'],io[0]['entry']],'the taker looks first to the short option, then the entry option, when their lanes are open')
    # ---- cases from the independent review (each failed on the first C4c2 draft) ----
    def plant(q,x,y=50.0):q.feet={'L':{'x':x,'y':y,'planted':True,'t':0,'n':0},'R':{'x':x,'y':y,'planted':True,'t':0,'n':-1}};q.last_plant=None;return q
    def score_with(m,defending,extra=()):
        s=m.s;s.ball.x=100.2 if defending=='B' else -.2;s.ball.y=50.0;s.ball.z=1.0;k=len(m.e.log)
        m.e.batch(list(extra)+[Ty.Event('goal',data={'defending':defending,'y':50.0,'z':1.0})]);g=[x['data'] for x in m.e.log[k:] if x['event']=='goal'];return g[0] if g else None
    m,s=flight();q=plant(kput(m,'B10',(99.6,50.0)),99.6);g=score_with(m,'B',[Ty.Event('acquire','B10',data={'ball_point':(99.8,50.0,1.0)})])
    ok(g and g['method']=='inner_release' and g['points']==3 and g['flight_team']=='A','a Keeper catching in the same millisecond as the crossing: a released ball (C4b), and the shooter\'s goal keeps its value (not an own goal)')
    m,s=flight();m.e.start_flight();q=plant(kput(m,'B10',(98.0,50.0)),98.0);s.ball.x,s.ball.y,s.ball.z=98.3,50.0,.5
    m.e.batch([Ty.Event('touch','B10',data={'c1_contact':True,'deliberate':True,'ball_point':(98.3,50.0,.5),'velocity':(20.0,0.0,0.0),'cooldown_ms':0},at=s.now)]);g=score_with(m,'B')
    ok(g and g['method']=='inner_release' and g['defensive_touches'] and g['defensive_touches'][0][0]=='B10','in the finishing flight a defensive touch is recorded as one, and the goal keeps its value')
    m=k42(None,**SC2('C-low'));s=m.s;stance(m,'A0',30.0,foot=30.0);m.e.release('A0',(-20.0,0.0,0.0),'pass');m.e.start_flight();q=plant(kput(m,'B3',(5.0,50.0)),5.0);s.ball.x,s.ball.y,s.ball.z=5.3,50.0,.5
    m.e.batch([Ty.Event('touch','B3',data={'c1_contact':True,'deliberate':False,'ball_point':(5.3,50.0,.5),'velocity':(-20.0,0.0,0.0),'cooldown_ms':0},at=s.now)]);g=score_with(m,'A')
    ok(g and g['method']=='reversal','and a flight turned into its own goal by an opponent in the finishing flight is a reversal, as in live play')
    m,s=flight();B=plant(kput(m,'B10',(98.0,50.0)),98.0);m.e.touch('B10',True);A5=plant(kput(m,'A5',(3.0,50.0)),3.0);s.ball.x,s.ball.y,s.ball.z=3.3,50.0,.5;m.e.touch('A5',False);g=score_with(m,'A')
    ok(g and g['method']=='own_goal','a team-mate turns his own team\'s parried flight into his own goal, with no opponent touch after his: a true own goal, not a reversal')
    m,s=flight();B=plant(kput(m,'B3',(95.0,50.0)),95.0);s.ball.x,s.ball.y,s.ball.z=95.3,50.0,.2;s.ball.vx=s.ball.vy=s.ball.vz=0.0;k=len(m.e.log);m.e.strike('B3',(20.0,0.0,0.0),'kick')
    st=[x['data'] for x in m.e.log[k:] if x['event']=='strike'];g=score_with(m,'B');ok(st and st[0].get('scoring_flight')=='defensive_kick_origin_kept' and g and g['method']=='inner_release' and g['points']==3,'a defender who kicks the attacking flight into his own goal: a defensive deflection, the shooter\'s goal and value')
    m=k42(None,**{**SC2('A-low'),'allow_outside_releases':False});s=m.s;stance(m,'A0',80.0,foot=80.0);m.e.release('A0',(20.0,0.0,0.0),'shot');g=score_with(m,'B')
    ok(g is None and [x for x in m.e.log if x['event']=='no_goal' and x['data'].get('reason')=='outside_release'],'with outside releases not allowed, a support foot exactly on the Keeper Zone arc is outside: no goal')
    m=k42();s=m.s;K=kput(m,'B10',(98.0,50.0));s.ball=Ty.Ball(mode=Ty.BallMode.SHOT,x=97.0,y=50.0,z=.4,vx=30.0,last_touch='A',last_releaser='A0',release_time=s.now-300,scoring=True)
    ev=Ty.Event('touch','B10',data={'c1_contact':True,'c4c_kind':'body','deliberate':False,'ball_point':(97.5,50.0,.4),'velocity':(-9.0,0.0,0.0),'cooldown_ms':0},at=s.now)
    rs=[];s.phase=Ty.Phase.OPENING;s.opening_touched=False;s.opening_contestants=('A3','B3');rs.append(m.e.c1_reason(ev))
    s.phase=LIVE;s.opening_touched=True;s.ball.last_releaser='B10';rs.append(m.e.c1_reason(ev))
    ok(rs==['premature_opening','own_release'],'body revalidation also covers the opening contestants and his own release')
    m,A=ctrl_state('C-low',91.0,50.0,cal={'ctrl_keeper':0});d=decide(m,A);s=m.s;s.ball.control_time=s.now+1;s.now+=2;tg={};m.c4c2_targets(tg)
    ok(getattr(A,'c4c2_intent',None)is None and tg.get('A0')is None,'a carry intent from before he regained the ball is void: he is not driven at the goal until he decides again')
    quick,log=run_match({**SETTINGS,'period_seconds':20,'periods':1},7,progress=False)
    names=run_experiment.__code__.co_consts;expect('pocket_1_1_source_sha256' in names and 'embedded_sha256' in names and 'source_sha256' not in names) #C3a2: in the saved result the inherited Pocket 1.1 hashes are named as such; the current core is embedded_sha256
    ms=quick['measures']
    for name in ('pass_ledger','kick_ledger','restart_pass_ledger'):
        L=ms[name];expect(L['attempts']==L['intended_receiver']+L['other_teammate']+L['opponent']+L['boundary']+L['other'])
    expect(ms['total_possessions']==ms['per_team']['A']['possessions']+ms['per_team']['B']['possessions'])
    return checks

def main():
    if sys.version_info < (3,10): raise RuntimeError('Python 3.10 or later required (current Pythonista 3).')
    try: import dialogs
    except ImportError:
        settings=copy.deepcopy(SETTINGS)
        if len(sys.argv)>1:
            settings, message=import_settings(json.loads(Path(sys.argv[1]).read_text()))
            if message:print(message)
            run_experiment(settings,calibration=import_settings.calibration)
        else:
            run_experiment(settings)
    else: phone_main()



"""Final Pocket parameter lab, exports, phone menu and command line interface."""


FACTORY_SETTINGS = {'label': 'Beastball Pocket parameter lab',
 'seed': 20260921,
 'matches': 1,
 'period_seconds': 120,
 'periods': 2,
 'overtime_seconds': 30,
 'play_clock': 45,
 'player_speed': 27.0,
 'acceleration': 10.0,
 'braking': 13.5,
 'turning': 13.0,
 'ball_speed': 40.0,
 'pass_speed': 27.0,
 'arrow_speed': 29.0,
 'keeper_zone_radius': 20.0,
 'inner_zone_radius': 15.0,
 'inner_points': 3,
 'release_points': 2,
 'allow_outside_releases': True,
 'outside_points': 1,
 'carry_value': 4,
 'archery': True,
 'adapt_scoring': True,
 'save_events': False,
 'dt_ms': 100,
 'tackles_per_possession': 2,
 'zone_inbound': True,
 'inbound_mark_offset': 8.0,
 'zone_marking': True,
 'marking_distance': 3.0,
 'rating_A': 70,
 'rating_B': 70,
 'rating_spread': 15,
 'field_height': 2.55,
 'field_mass': 230.0,
 'field_reach': 1.173,
 'keeper_height_A': 3.2004,
 'keeper_height_B': 3.2004,
 'keeper_mass_A': 230.0,
 'keeper_mass_B': 230.0,
 'keeper_reach_fraction': 0.46,
 'keeper_speed': 27.0,
 'keeper_acceleration': 10.0,
 'keeper_braking': 13.5,
 'keeper_turning': 13.0,
 'keeper_jump': 1.6,
 'defense_A': 0,
 'defense_B': 0}
FACTORY_CALIBRATION = {'gravity': 9.81,
 'ball_drag': 0.015,
 'arrow_drag': 0.06,
 'catch_noise': 0.15,
 'tackle_rate': 1.25,
 'block_force': 1.0,
 'arrow_error_scale': 1.0,
 'fatigue_rate': 1.0,
 'body_radius_scale': 1.0,
 'pass_release_ms': 250,
 'grip_delay_ms': 300,
 'bow_draw_ms': 600,
 'ball_restitution': 0.7745966692,
 'frame_thickness': 0.2,
 'ball_mass_kg': 0.4,
 'pass_aim_error_deg': 3.0,
 'catch_arrest_force_N': 1100.0,
 'catch_hand_travel_m': 0.6,
 'catch_reaction_s': 0.12,
 'deflection_speed_kept': 0.2,
 'c1_pass_planning': 1,
 'c1_receiver_routing': 1,
 'c1_chasers_read_flight': 1,
 'c1_catch_model': 1,
 'c3_contact': 1,
 'c3_substep_ms': 10,
 'contact_restitution': 0.1,
 'contact_time_s': 0.15,
 'traction_coefficient': 0.8,
 'brace_speed_mps': 2.0,
 'shock_speed_mps': 6.0,
 'rearm_gap_m': 0.3,
 'grip_gain_per_s': 4.0,
 'grip_resist_per_s': 1.0,
 'grip_slip_per_s': 2.0,
 'grip_slip_ref_mps': 4.0,
 'grip_overload_per_s': 4.0,
 'grip_overload_time_s': 0.15,
 'grip_force_N': 2500.0,
 'topple_time_s': 1.0,
 'balance_recovery_per_s': 1.5,
 'base_half_width_frac': 0.2,
 'hold_height_upper_frac': 0.7,
 'hold_height_lower_frac': 0.45,
 'lower_hold_leg_factor': 0.6,
 'holder_load_factor': 0.35,
 'tackle_grip_threshold': 0.3,
 'tackle_source_majority': 0.5,
 'restraint_weight_matched': 1.0,
 'restraint_weight_other': 0.3,
 'restraint_speed_loss': 0.5,
 'restraint_error_deg': 8.0,
 'collision_risk_tolerance': 0.5,
 'contact_foul_min_shock': 0.05,
 'c3_prep_round_ms': 0,
 'c3_follow_distance': 1,
 'c3b': 1,
 'slide_friction': 0.8,
 'get_up_time_s': 0.8,
 'get_up_max_slide_mps': 1.0,
 'descent_time_s': 0.5,
 'containment_window_s': 2.0,
 'descent_window_s': 2.0,
 'recovery_react': 1,
 'exit_protection': 1,
 'c3c': 1,
 'arm_pin_grip': 0.5,
 'tuck_after_delay_frac': 1.0,
 'strip_in_motion_factor': 4.0,
 'c3_region_policy': 1,
 'blindside_rear_half_angle_deg': 15.0,
 'escape_force_N': 2500.0,
 'c4_zone': 1,
 'zone_direct_penalty': 0,
 'escape_allocation': 1,
 'contact_roster': 0,
 'c4b': 1,
 'gait_step_base_frac': 0.25,
 'gait_step_per_mps_frac': 0.035,
 'gait_step_max_frac': 1.1,
 'gait_duty_rest': 0.62,
 'gait_duty_per_mps': 0.03,
 'gait_duty_min': 0.22,
 'gait_half_width_frac': 0.09,
 'gait_still_mps': 0.5,
 'gait_reset_frac': 0.75,
 'c4c': 1,
 'keeper_depth_frac': 0.25,
 'keeper_depth_min_m': 1.0,
 'keeper_depth_max_m': 4.0,
 'keeper_reaction_s': 0.2,
 'keeper_unset_s': 0.1,
 'keeper_set_mps': 1.5,
 'keeper_pushoff_frac': 0.4,
 'keeper_extension_frac': 0.3,
 'keeper_dive_hand_frac': 0.3,
 'keeper_dive_lean': 0.35,
 'keeper_launch_min_s': 0.1,
 'keeper_parry_restitution': 0.35,
 'keeper_body_restitution': 0.3,
 'keeper_attempt_margin_m': 1.5,
 'keeper_dive_time_s': 0.25,
 'keeper_aim_frac': 0.5,
 'keeper_parry_swing_mps': 5.0,
 'keeper_windup_set': 1,
 'keeper_confront': 1,
 'keeper_confront_m': 7.0,
 'keeper_gather_m': 6.0,
 'c4c2': 1,
 'reversal_rule': 0,
 'controller': 1,
 'ctrl_lookahead_s': 0.6,
 'ctrl_style_A': 0,
 'ctrl_style_B': 0,
 'ctrl_style_band': 0.1,
 'ctrl_receivers': 2,
 'ctrl_short_inbound': 1,
 'ctrl_keeper': 1,
 'keeper_height_m': 0.0}

VERSION = 'Beastball-Pocket-2.0.1'
CHECKPOINT = 'Finished parameter lab: C4c2 rules and physics plus final controllers, rosters, measurements and interface'
MEASUREMENT_VERSION = 'M2.0'

# Starting laboratory configuration, the Lead's position; none of these
# starting values selects a canon scoring candidate or final calibration.
# Effective defaults are declared in SETTINGS at the top.
ROSTER_OVERRIDES = {}
RATING_ANCHORS = {40: 'worst of all time', 70: 'average',
                  78: 'dependable, unexceptional', 93: 'All-League threshold',
                  100: 'greatest of all time'}
NOTES = [
    'Finished experimental parameter lab, not canon or proof of competitive balance. C-low is the selectable starting preset.',
    'Rules and physical contact, recovery, zone occupancy, support-foot scoring, offensive flight origin and Keeper saves are inherited from C4c2. No coefficients were adjusted to force target totals.',
    'Both teams start at rating 70 with mirrored mixed profiles of spread 15. Ratings are abilities, not success percentages. Every effective player attribute is exported.',
    'Default Keepers are 10.5 ft (3.2004 m); reach scales with height. Mass, speed, acceleration, braking, turning and jump are independent parameters.',
    'The controller is heuristic. Its reference shot/carry/pass tables came from C4c2 drills at specific ratings and settings. Moving lanes and travel times are policy forecasts. Changing parameters does not retrain those tables.',
    'The period and possession clocks bound decisions. A lawful shot already released can finish after the horn under the retained flight rule.',
    'Failed carry estimates credit only first tackles observed during this match. Other failures get no retained-possession credit. The calibration report distinguishes them.',
    'Open rules: opponent reversal of an own flight uses reversal_rule 0 or 1 as an experimental option; support feet on or beyond the end line retain current participation behavior pending DreLen\'s wording.',
    'Python 3.10 or later, no dependencies, network or companion files required. Tested on desktop; this final version still needs a device run in Pythonista.',
    'Same-runtime seeds are reproducible. Phone and desktop floating-point paths can diverge; compare them statistically.',
]

_previous_validate = validate
_previous_configuration = configuration
_previous_run_experiment = run_experiment
_previous_measure = measure
_previous_calibration = validate_calibration


def validate(settings):
    _previous_validate(settings)
    bounds = {'rating_A': (40,100), 'rating_B': (40,100), 'rating_spread': (0,30),
              'field_height': (1.4,3.6576), 'field_mass': (40,700), 'field_reach': (.2,2.5),
              'keeper_height_A': (2.7432,3.6576), 'keeper_height_B': (2.7432,3.6576),
              'keeper_mass_A': (40,700), 'keeper_mass_B': (40,700),
              'keeper_reach_fraction': (.15,.8), 'keeper_speed': (1,44.704),
              'keeper_acceleration': (.5,30), 'keeper_braking': (.5,40),
              'keeper_turning': (.5,40), 'keeper_jump': (.1,3.), 'defense_A': (0,3), 'defense_B': (0,3)}
    for key, (lo, hi) in bounds.items():
        if not lo <= settings[key] <= hi:
            raise ValueError('%s must be from %s to %s' % (key, lo, hi))
    if settings['seed'] + settings['matches'] - 1 > 2147483647:
        raise ValueError('The seed schedule exceeds 2147483647.')
    return settings


def validate_calibration(cal):
    _previous_calibration(cal)
    if any(value < 0 for value in cal.values()):
        raise ValueError('Model calibration values cannot be negative.')
    for key in ('ctrl_lookahead_s', 'keeper_launch_min_s', 'keeper_dive_time_s'):
        if cal[key] <= 0:
            raise ValueError(key + ' must be positive.')
    if not 0 <= cal['ctrl_style_band'] <= 1:
        raise ValueError('Style band must be from 0 to 1.')
    if cal['keeper_depth_min_m'] > cal['keeper_depth_max_m']:
        raise ValueError('Keeper minimum depth exceeds maximum depth.')
    if not 0 <= cal['keeper_parry_restitution'] <= 1 or not 0 <= cal['keeper_body_restitution'] <= 1:
        raise ValueError('Keeper restitution must be from 0 to 1.')
    return cal


def validate_roster(overrides):
    if not isinstance(overrides, dict):
        raise ValueError('roster_overrides must be a JSON object.')
    allowed = CORE.types.Attributes.__dataclass_fields__
    rated = CORE.match.RATED_ATTRIBUTES
    for player, values in overrides.items():
        if player not in ('A', 'B') and player not in {t+str(i) for t in ('A','B') for i in range(22)}:
            raise ValueError('Unknown roster slot: ' + str(player))
        if not isinstance(values, dict):
            raise ValueError('Each roster entry must be an attribute object.')
        attr = CORE.types.Attributes()
        for key, value in values.items():
            if key not in allowed:
                raise ValueError('Unknown attribute: ' + key)
            if isinstance(value, bool) or not isinstance(value, (float,int)) or not math.isfinite(value):
                raise ValueError(key + ' must be finite numeric data.')
            if key in rated:
                if not 40 <= value <= 100:
                    raise ValueError(key + ' ratings must be 40..100.')
                value /= 100.
            elif value <= 0:
                raise ValueError(key + ' must be positive.')
            setattr(attr, key, value)
        attr.validate()
    return overrides


def configuration(settings, seed=None, calibration=None):
    cfg = _previous_configuration(settings, seed, calibration)
    cfg['pocket_final'] = True
    cfg['roster_overrides'] = copy.deepcopy(validate_roster(ROSTER_OVERRIDES))
    for team in ('A','B'):
        cfg['teams'][team]['defense'] = ['zone','man','hunt','adaptive'][settings['defense_'+team]]
    return cfg


def measure_final(log, settings):
    from collections import Counter
    marks = [e for e in log if e['event'] == 'pocket_final_rules']
    decisions = [e for e in log if e['event'] == 'controller_decision' and e.get('rule') == 'Pocket-2.0']
    # Join predictions to an actual preparation and its first subsequent release.
    # Each release is used once; a cancelled or preempted wind-up is reported.
    pending = {}
    observations = []
    for e in log:
        d, name = e['data'], e['event']
        if name == 'controller_decision' and e.get('rule') == 'Pocket-2.0' and d.get('preparation_started'):
            pending[d['player']] = e
        elif name == 'release' and d.get('player') in pending:
            intent = pending.pop(d['player'])
            if intent['data']['choice'] == 'shoot' and d.get('kind') == 'shot':
                observations.append({'release_id': e['id'], 'kind': 'shot',
                                     'predicted_goal': intent['data']['p_conv']*intent['data']['goal_factor']})
            elif intent['data']['choice'] == 'pass' and d.get('kind') == 'pass':
                f = intent['data']['pass_forecast']
                observations.append({'release_id': e['id'], 'kind': 'pass',
                                     'predicted_completion': f['p_complete'], 'remaining_s': f['remaining_s']})
        elif name in ('possession_change','period_end','match_complete'):
            pending.clear()
    release_indices = {e['id']: i for i,e in enumerate(log)}
    shot_scores = []; pass_scores = []
    for row in observations:
        index = release_indices[row['release_id']]
        release = log[index]
        team = release['data']['player'][0]
        outcome = 'unresolved'
        for e in log[index+1:]:
            name, d = e['event'], e['data']
            if name == 'goal':
                outcome = 'goal' if d.get('team') == team else 'other_goal'
                break
            if name == 'control':
                actor = d.get('player', e.get('carrier'))
                outcome = 'teammate' if actor and actor[0] == team else 'opponent'
                break
            if name in ('boundary','period_end','release','match_complete','possession_change'):
                outcome = name
                break
        row['outcome'] = outcome
        if row['kind'] == 'shot':
            shot_scores.append((row['predicted_goal'], outcome == 'goal'))
        else:
            pass_scores.append((row['predicted_completion'], outcome == 'teammate'))
    def calibration(rows):
        return {'n': len(rows), 'mean_predicted': statistics.mean(r[0] for r in rows) if rows else None,
                'observed_fraction': statistics.mean(r[1] for r in rows) if rows else None,
                'brier': statistics.mean((r[0]-r[1])**2 for r in rows) if rows else None}
    occupancy = []
    # State snapshots are emitted at most once per second by the final record
    # hook; they are samples, not an exact continuous time integral.
    for e in log:
        if e['event'] == 'pocket_occupancy_sample':
            occupancy.append(e['data'])
    return {'measurement_version': MEASUREMENT_VERSION,
            'controller_active': marks[0]['data']['controller_active'] if marks else None,
            'decision_counts': dict(Counter(e['data']['choice'] for e in decisions)),
            'decision_logging': 'choice transitions plus one-second heartbeat',
            'release_predictions_joined_once': len(observations),
            'shot_forecast_check': calibration(shot_scores),
            'pass_forecast_check': calibration(pass_scores),
            'occupancy_samples': len(occupancy),
            'packed_goal_mouth_samples': sum(d['goal_mouth_defenders'] >= 4 for d in occupancy),
            'occupancy_sampling_note': 'At most once per second of live time; counts include the Keeper. These are samples, not a time integral.',
            'ratings_are_probabilities': False,
            'estimates_retrained_for_parameters': False}


def measure(log, settings):
    result = _previous_measure(log, settings)
    result['measurement_version'] = MEASUREMENT_VERSION
    available = set()
    names = {e['event'] for e in log}
    if 'c3b_rules' in names:
        result['continuation']['recovery']['note'] = 'Grounded athletes slide and rise under the active get-up model. Get-up durations and recovery compliance are reported in measures_c3.'
        available.update(('get-up durations','containment and controlled descent','grip, impulse and posture witnesses','true wrap duration (only a proxy is available)'))
    if 'c4b_rules' in names:
        available.add('support-foot scoring origin')
    if 'c4c_rules' in names:
        available.add('separate Keeper save/parry classes')
    result['unavailable_in_this_checkpoint'] = [x for x in result['unavailable_in_this_checkpoint'] if x not in available]
    result['additional_measurements'] = 'measures_c3 contains contact and get-up witnesses; measures_c4 contains feet and Keeper witnesses; measures_final contains controller and occupancy diagnostics.'
    return result


_previous_run_match = run_match


def finish_summary(result, log, settings):
    result['measures_final'] = measure_final(log, settings)
    # Preserve shot-only M1 comparability, and add the full finishing family
    # now that carrying can score. Abandoned declared carries count as intents.
    import bisect
    changes = [e for e in log if e['event'] == 'possession_change']
    ids = [e['id'] for e in changes]
    attempts = {'A': [], 'B': []}
    for e in log:
        if e['event'] == 'release' and e['data'].get('kind') == 'shot' and e['phase'] == 'live':
            team = e['data']['player'][0]
            attempts[team].append((e['id'], 'shot'))
    for row in result['carry_outcome_rows']:
        attempts[row['player'][0]].append((row['start_id'], 'carry_intent'))
    finish = {}
    by_id = {e['id']: e for e in log}
    for team in ('A','B'):
        old = result['measures']['per_team'][team]
        pos = set()
        for eid, kind in attempts[team]:
            index = bisect.bisect_right(ids, eid)-1
            if index >= 0 and changes[index]['owner'] == team:
                pos.add(ids[index])
        rows = [r for r in result['carry_outcome_rows'] if r['player'][0] == team]
        carry_goals = [r for r in rows if r['outcome'] == 'carry_goal']
        goals = old['goals_from_shots']+len(carry_goals)
        points = old['points_from_shots']+sum(by_id[r['end_id']]['data']['points'] for r in carry_goals)
        n = len(attempts[team])
        finish[team] = {'possessions': old['possessions'], 'possessions_with_finish_attempt': len(pos),
                       'finish_attempt_possession_fraction': len(pos)/old['possessions'] if old['possessions'] else None,
                       'shots': sum(k == 'shot' for _,k in attempts[team]), 'carry_intents': len(rows),
                       'finish_attempts': n, 'attempts_per_attempt_possession': n/len(pos) if pos else None,
                       'goals_from_finish_attempts': goals, 'conversion': goals/n if n else None,
                       'mean_converted_value': points/goals if goals else None,
                       'points_from_finish_attempts': points, 'points_other': old['points']-points,
                       'points_per_possession': old['points_per_possession']}
    result['measures_final']['finishing'] = finish
    result['measures_final']['finishing_definition'] = 'Live-play shot releases plus unique declared carry intentions, including changed plans. Penalties and incidental pass/own goals are separate; shot-only M1 measures remain available.'
    # Supersede the inherited controller report, which counted carry heartbeat
    # records as additional attempts and joined outcomes through fixed windows.
    result['measures_c4']['controller'] = {**result['measures_final'],
                                         'carry_outcomes': result['carry_outcome_ledger']}
    witnessed_keeper_stops = 0
    for row in result['carry_outcome_rows']:
        end = by_id[row['end_id']]
        d = end['data']
        actor = d.get('tackler') if end['event'] == 'tackle_count' else d.get('actor') if end['event'] == 'strip' else d.get('player') if end['event'] == 'control' else None
        if actor in ('A10','B10') and actor[0] != row['player'][0]:
            witnessed_keeper_stops += 1
    keeper = result['measures_c4'].get('keeper')
    if isinstance(keeper, dict):
        keeper['stopped_carries'] = witnessed_keeper_stops
        keeper['carry_stop_definition'] = 'Unique carry intentions ended by a Keeper-witnessed tackle, strip or control; indirect effects are not attributed.'
        keeper.pop('aborted_finishes',None)
        keeper['induced_aborted_finishes'] = 'unavailable: a cancelled wind-up does not establish causal Keeper attribution'
    result['report_qualifications'] = [x for x in result.get('report_qualifications',[]) if not x.startswith('C3b QUALIFICATION OF AN M1.3 NOTE')]
    result['roster_overrides'] = copy.deepcopy(ROSTER_OVERRIDES)
    result['model_stage'] = 'finished experimental implementation; balance calibration remains adjustable'
    return result, log


def run_match(settings, seed=None, progress=True, calibration=None):
    result, log = _previous_run_match(settings, seed, progress, calibration)
    return finish_summary(result, log, settings)


def atomic_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.tmp')
    temp.write_text(json.dumps(obj, indent=2, allow_nan=False), encoding='utf-8')
    temp.replace(path)


def session_object(settings, calibration):
    return {'format': VERSION, 'settings': copy.deepcopy(settings),
            'calibration': copy.deepcopy(calibration),
            'roster_overrides': copy.deepcopy(ROSTER_OVERRIDES)}


def phone_session_object(settings, calibration, baseline):
    return {**session_object(settings, calibration), 'baseline': baseline,
            'script_defaults': {'settings': copy.deepcopy(SETTINGS),
                                'calibration': copy.deepcopy(CALIBRATION)}}


def restore_phone_session(obj):
    """Changed source defaults win; unchanged source keys keep saved menu edits.

    Old sessions have no source snapshot, so compare against shipped 2.0
    defaults for their first migration. Explicit clipboard imports remain exact.
    """
    merged = copy.deepcopy(obj)
    prior = obj.get('script_defaults', {})
    changed = []
    for group, source, factory in (('settings', SETTINGS, FACTORY_SETTINGS),
                                   ('calibration', CALIBRATION, FACTORY_CALIBRATION)):
        previous = prior.get(group, factory)
        values = merged.setdefault(group, {})
        for key, value in source.items():
            if key not in previous or value != previous[key]:
                values[key] = copy.deepcopy(value)
                changed.append(group+'.'+key)
    settings, _ = import_settings(merged)
    cal = copy.deepcopy(import_settings.calibration or CALIBRATION)
    return settings, cal, copy.deepcopy(import_settings.roster), obj.get('baseline'), changed


def show_active_speeds(settings):
    print('Active speeds (m/s): players %g; Keepers %g; shots %g; passes %g; arrows %g. Settings %s' %
          (settings['player_speed'], settings['keeper_speed'], settings['ball_speed'],
           settings['pass_speed'], settings['arrow_speed'], fingerprint(settings)))


_previous_import = import_settings


def import_settings(obj):
    if not isinstance(obj, dict):
        raise ValueError('Expected a settings/results JSON object.')
    settings, message = _previous_import(obj)
    roster = validate_roster(copy.deepcopy(obj.get('roster_overrides', {})))
    if 'roster_overrides' not in obj and obj.get('runs'):
        roster = validate_roster(copy.deepcopy(obj['runs'][0].get('roster_overrides', {})))
    # The inherited importer writes calibration onto the active public
    # import_settings function; it has already populated our attribute.
    import_settings.roster = roster
    return settings, message


def run_experiment(settings, baseline=None, out=None, progress=True, calibration=None):
    """Current and pinned baseline include their own calibration and roster."""
    global ROSTER_OVERRIDES
    cal = copy.deepcopy(CALIBRATION if calibration is None else calibration)
    if baseline is None or 'settings' not in baseline:
        path, payload = _previous_run_experiment(settings, baseline, out, progress, cal)
        payload['roster_overrides'] = copy.deepcopy(ROSTER_OVERRIDES)
        payload['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        atomic_json(path, payload)
        return path, payload
    saved = copy.deepcopy(ROSTER_OVERRIDES)
    base_settings = copy.deepcopy(baseline['settings'])
    base_cal = validate_calibration(copy.deepcopy(baseline['calibration']))
    base_roster = validate_roster(copy.deepcopy(baseline.get('roster_overrides', {})))
    path, payload = _previous_run_experiment(settings, None, out, progress, cal)
    payload['baseline_settings'] = base_settings
    payload['baseline_calibration'] = base_cal
    payload['baseline_roster_overrides'] = base_roster
    payload['roster_overrides'] = saved
    payload['status'] = 'running_baseline'
    atomic_json(path, payload)
    try:
        ROSTER_OVERRIDES = base_roster
        for seed in payload['seeds']:
            summary, events = run_match(base_settings, seed, progress, base_cal)
            if settings['save_events']:
                log_path = path.parent/(path.stem+'_BASELINE_'+str(seed)+'.jsonl.gz')
                with gzip.open(log_path, 'wt', encoding='utf-8') as f:
                    for event in events:
                        f.write(json.dumps(event)+'\n')
                summary['event_file'] = log_path.name
            payload['baseline_runs'].append(summary)
            atomic_json(path, payload)
        payload['baseline_aggregate'] = aggregate(payload['baseline_runs'])
        payload['paired_combined_score_deltas'] = [sum(a['score'].values())-sum(b['score'].values())
                  for a,b in zip(payload['runs'], payload['baseline_runs'])]
        payload['mean_paired_combined_score_delta'] = statistics.mean(payload['paired_combined_score_deltas'])
        payload['comparison_note'] = 'Same seeds; each side uses its pinned settings, calibration and roster. Policies can diverge.'
        payload['status'] = 'finished' if all(r['ordinary_completion'] for r in payload['runs']+payload['baseline_runs']) else 'finished_with_abnormal_matches'
    except (Exception, KeyboardInterrupt) as exc:
        payload['status'] = 'interrupted' if isinstance(exc, KeyboardInterrupt) else 'error'
        payload['error'] = repr(exc)
        raise
    finally:
        ROSTER_OVERRIDES = saved
        payload['script_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        atomic_json(path, payload)
        path.with_suffix('.txt').write_text(VERSION+'\n'+json.dumps(payload.get('aggregate'),indent=2)+
            '\nBaseline\n'+json.dumps(payload.get('baseline_aggregate'),indent=2)+'\n\n'+
            '\n\n'.join(compact(r)+'\n'+measure_brief(r['measures']) for r in payload['runs']), encoding='utf-8')
    return path, payload


def quick_check():
    """Bounded installation checks; full implementation tests ship separately."""
    n = 0
    def check(ok):
        nonlocal n
        if not ok:
            raise AssertionError('Quick check failed at '+str(n+1))
        n += 1
    validate(SETTINGS); validate_calibration(CALIBRATION); check(True)
    for name in SCORING_CONFIGURATIONS:
        m = CORE.match.Match(configuration({**SETTINGS, **scoring_configuration(name)}))
        check(len(m.s.players) == 44)
        check(1.4 <= m.s.players['A10'].a.height <= 3.6576)
        check(sum(q.active and q.role == 'keeper' for q in m.s.players.values()) == 2)
        check(all(.4 <= getattr(p.a,k) <= 1. for p in m.s.players.values() for k in CORE.match.RATED_ATTRIBUTES))
        check(m.pocket_budget(45.) == min(45., m.s.game_ms/1000.))
    return n


def self_check():
    return quick_check()


def phone_main():
    import dialogs
    import clipboard
    global ROSTER_OVERRIDES
    session_path = output_dir()/'Pocket_saved_parameters.json'
    current, cal, baseline, last = copy.deepcopy(SETTINGS), copy.deepcopy(CALIBRATION), None, None
    if session_path.exists():
        try:
            obj = json.loads(session_path.read_text(encoding='utf-8'))
            current, cal, ROSTER_OVERRIDES, baseline, changed = restore_phone_session(obj)
            if changed:
                print('Applied edited code parameters:', ', '.join(changed))
        except Exception as exc:
            print('Saved settings could not be loaded:', exc)
    groups = {
        'Match and output': ['label','seed','matches','period_seconds','periods','overtime_seconds','play_clock','archery','save_events','dt_ms'],
        'Scoring and zone': ['keeper_zone_radius','inner_zone_radius','outside_points','release_points','inner_points','carry_value','allow_outside_releases','tackles_per_possession','zone_inbound','inbound_mark_offset','zone_marking','marking_distance'],
        'Ratings and players': ['rating_A','rating_B','rating_spread','field_height','field_mass','field_reach','player_speed','acceleration','braking','turning','ball_speed','pass_speed','arrow_speed'],
        'Keepers': ['keeper_height_A','keeper_height_B','keeper_mass_A','keeper_mass_B','keeper_reach_fraction','keeper_speed','keeper_acceleration','keeper_braking','keeper_turning','keeper_jump'],
    }
    def edit(obj, keys, title):
        fields = [{'key': k, 'title': LABELS.get(k,k.replace('_',' ')),
                   'type': 'switch' if isinstance(obj[k],bool) else 'text' if isinstance(obj[k],str) else 'number',
                   'value': obj[k] if isinstance(obj[k],bool) else str(obj[k])} for k in keys]
        ans = dialogs.form_dialog(title, fields=fields)
        if ans is None:
            return obj
        changed = copy.deepcopy(obj)
        for k in keys:
            changed[k] = bool(ans[k]) if isinstance(obj[k],bool) else str(ans[k]) if isinstance(obj[k],str) else int(ans[k]) if isinstance(obj[k],int) else float(ans[k])
        return changed
    print(VERSION+' — parameter lab. Ratings 40..100; Keeper heights in metres.')
    actions = ['Run match','Scoring preset']+list(groups)+['Team styles','Advanced physics','Individual roster JSON',
               'Quick length','Full length','Pin baseline','Compare with baseline','Copy results','Copy parameters',
               'Import parameters','Load code parameters','Quick self-check','Model notes','Reset parameters','Exit']
    show_active_speeds(current)
    while True:
        action = dialogs.list_dialog('Beastball Pocket 2.0', actions)
        if action is None or action == 'Exit':
            atomic_json(session_path, phone_session_object(current,cal,baseline))
            return
        try:
            if action in groups:
                current = validate(edit(current, groups[action], action))
            elif action == 'Scoring preset':
                name = dialogs.list_dialog('Experimental scoring options', list(SCORING_CONFIGURATIONS))
                if name:
                    current.update(scoring_configuration(name))
            elif action == 'Team styles':
                for team in ('A','B'):
                    answer = dialogs.list_dialog('Team '+team, ['Balanced','Carry preference','Pass preference'])
                    if answer:
                        cal['ctrl_style_'+team] = ['Balanced','Carry preference','Pass preference'].index(answer)
                    answer = dialogs.list_dialog('Team '+team+' defense', ['Zone','Man','Ball hunting','Adaptive'])
                    if answer:
                        current['defense_'+team] = ['Zone','Man','Ball hunting','Adaptive'].index(answer)
            elif action == 'Advanced physics':
                prefix = dialogs.list_dialog('Physics group', ['Contact','Catch and flight','Keeper','Controller','All'])
                if prefix:
                    keys = [k for k in cal if k != 'contact_roster'] if prefix == 'All' else [k for k in cal if k != 'contact_roster' and (
                        (prefix == 'Keeper' and k.startswith('keeper_')) or
                        (prefix == 'Controller' and (k.startswith('ctrl_') or k == 'controller')) or
                        (prefix == 'Catch and flight' and any(w in k for w in ('catch','ball','arrow','pass','gravity','frame','deflection'))) or
                        (prefix == 'Contact' and any(w in k for w in ('grip','hold','contact','restraint','escape','balance','topple','slide','get_up','descent','traction','shock'))))]
                    cal = validate_calibration(edit(cal,keys,prefix))
            elif action == 'Individual roster JSON':
                answer = dialogs.text_dialog('Team A/B or slot A0..B21; ratings 40..100', text=json.dumps(ROSTER_OVERRIDES,indent=2))
                if answer is not None:
                    ROSTER_OVERRIDES = validate_roster(json.loads(answer))
            elif action == 'Quick length':
                current.update(period_seconds=120,periods=2,overtime_seconds=30)
            elif action == 'Full length':
                current.update(period_seconds=600,periods=4,overtime_seconds=300)
            elif action == 'Pin baseline':
                baseline = session_object(current,cal)
                print('Pinned settings, physics and roster.')
            elif action in ('Run match','Compare with baseline'):
                if action == 'Compare with baseline' and baseline is None:
                    raise ValueError('Pin a baseline before comparing.')
                show_active_speeds(current)
                last, _ = run_experiment(current,baseline if action == 'Compare with baseline' else None,calibration=cal)
            elif action == 'Copy results':
                if last is None:
                    raise ValueError('Run a match first.')
                clipboard.set(last.read_text(encoding='utf-8'))
                print('Copied last completed run. It retains the parameters used for that run; later menu edits do not change it.')
            elif action == 'Copy parameters':
                clipboard.set(json.dumps(session_object(current,cal),indent=2))
                show_active_speeds(current)
            elif action == 'Import parameters':
                candidate, message = import_settings(json.loads(clipboard.get()))
                current = copy.deepcopy(candidate)
                cal = copy.deepcopy(import_settings.calibration or CALIBRATION)
                ROSTER_OVERRIDES = copy.deepcopy(import_settings.roster)
                if message:
                    print(message)
            elif action == 'Quick self-check':
                print('Passed',quick_check(),'checks.')
            elif action == 'Model notes':
                dialogs.text_dialog('Model notes',text='\n\n'.join(NOTES))
            elif action in ('Reset parameters', 'Load code parameters'):
                current, cal = validate(copy.deepcopy(SETTINGS)), validate_calibration(copy.deepcopy(CALIBRATION))
                if action == 'Reset parameters':
                    ROSTER_OVERRIDES = {}
                show_active_speeds(current)
            atomic_json(session_path,phone_session_object(current,cal,baseline))
        except KeyboardInterrupt:
            print('Stopped; completed results are saved.')
        except Exception as exc:
            print('Problem:',exc)
            dialogs.alert('Beastball Pocket',str(exc),'OK',hide_cancel_button=True)


def main():
    global ROSTER_OVERRIDES
    if sys.version_info < (3,10):
        raise RuntimeError('Python 3.10 or later required.')
    if len(sys.argv) == 1:
        try:
            import dialogs
        except ImportError:
            run_experiment(copy.deepcopy(SETTINGS))
        else:
            phone_main()
        return
    import argparse
    parser = argparse.ArgumentParser(description='Beastball Pocket 2.0 parameter lab')
    parser.add_argument('parameters',nargs='?',help='settings or exported results JSON')
    parser.add_argument('--out',help='results directory')
    parser.add_argument('--preset',choices=list(SCORING_CONFIGURATIONS))
    parser.add_argument('--full',action='store_true',help='four 600-second live periods')
    parser.add_argument('--seed',type=int)
    parser.add_argument('--matches',type=int)
    parser.add_argument('--events',action='store_true')
    parser.add_argument('--quiet',action='store_true')
    parser.add_argument('--self-check',action='store_true')
    parser.add_argument('--export-parameters',help='write parameters without running a match')
    parser.add_argument('--baseline',help='pinned parameters JSON for matched-seed comparison')
    args = parser.parse_args()
    if args.self_check:
        print('Passed',quick_check(),'checks.')
        return
    current, cal = copy.deepcopy(SETTINGS), copy.deepcopy(CALIBRATION)
    if args.parameters:
        current, message = import_settings(json.loads(Path(args.parameters).read_text(encoding='utf-8')))
        cal = copy.deepcopy(import_settings.calibration or CALIBRATION)
        ROSTER_OVERRIDES = copy.deepcopy(import_settings.roster)
        if message:
            print(message)
    if args.preset:
        current.update(scoring_configuration(args.preset))
    if args.full:
        current.update(period_seconds=600,periods=4,overtime_seconds=300)
    if args.seed is not None:
        current['seed'] = args.seed
    if args.matches is not None:
        current['matches'] = args.matches
    if args.events:
        current['save_events'] = True
    validate(current)
    if args.export_parameters:
        atomic_json(args.export_parameters,session_object(current,cal))
        print('Saved parameters:',args.export_parameters)
        return
    baseline = None
    if args.baseline:
        baseline = json.loads(Path(args.baseline).read_text(encoding='utf-8'))
        bs, _ = import_settings(baseline)
        baseline = {'settings': bs,'calibration': import_settings.calibration or CALIBRATION,
                    'roster_overrides': import_settings.roster}
    run_experiment(current,baseline,args.out,not args.quiet,cal)

if __name__ == '__main__': main()
