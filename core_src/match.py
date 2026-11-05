"""Spatial autonomous play with explicit trajectories and calibrated-assumption hooks."""
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
