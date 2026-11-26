from dataclasses import dataclass, replace
import math
from native.config import NativeConfig,POCKET

from .fatigue_rotation import PLANNED_RATE_SCALE

_RB_POCKET_OVERRIDES=dict(arrow_speed=250.,arrow_limit=None,player_speed=44.7,inner_zone_radius=10.,inner_points=2,release_points=3,outside_points=4,carry_value=5)
RB_POCKET=tuple((k,_RB_POCKET_OVERRIDES.get(k,v)) for k,v in POCKET)
RB_BODY=tuple((k,44.7 if k=="maximum_speed" else 250. if k=="archery_release_speed" else v) for k,v in NativeConfig().body_standards)

@dataclass(frozen=True)
class RulebookConfig(NativeConfig):
    version: str = 'native-rb/2'
    profile: str = 'native-rb'
    field_roster_limit: int = 12
    scoring: str = 'banded'
    carry_points: int = 5
    release_bands: tuple = ((10.,2),(20.,3),(None,4))
    full_award_points: int = 3
    own_goal_points: int = 2
    arrows: int = 15
    pocket_settings: tuple = RB_POCKET
    body_standards: tuple = RB_BODY
    arrow_speed: float = 250.
    breaks_ms: tuple = (120000,600000,120000,180000)
    sudden_break_ms: int = 60000
    timeout_ms: int = 45000
    review_tolerance_m: float = .05

    def __post_init__(self):
        if self.version!='native-rb/2' or self.profile!='native-rb':raise ValueError('RB profile mixing')
        if self.scoring!='banded':raise ValueError('native-rb/2 measurements require banded scoring')
        if self.m2!='null' or self.legacy_layers:raise ValueError('RB retains null M2 and no legacy layers')
        if (self.periods,self.period_seconds,self.overtime_seconds)!=(4,600,300):raise ValueError('canon duration')


_RB3_POCKET=tuple(sorted((k,v) for k,v in dict(RB_POCKET,player_speed=44.704,ball_limit=134.1).items() if k!='pass_speed'))

@dataclass(frozen=True)
class RulebookConfigV3(RulebookConfig):
    version: str = 'native-rb/3'
    mapping_version: str = 'attr-map/2'
    roster_digests: tuple = ()
    body_standards: tuple = ()
    pocket_settings: tuple = _RB3_POCKET
    # RB-3.4 (owner ruling 17 Nov 2026, PROVISIONAL): contact with a player who has just thawed is
    # immune_contact for this long after the thaw; frozen players are obstacles (no contact foul).
    thaw_contact_buffer_ms: int = 1000
    # RB-3.5: zone residence by zone (defender: own zone; attacker: attacked zone)
    zone_residence_ms: int = 5000
    zone_marked_distance_m: float = 5.0
    # RB-3.6 BEHAVIORAL baseline (owner, 18 Nov 2026; cognition, PROVISIONAL): a defender is always
    # within defender_mark_distance_m of an opposing field player or within defender_ball_leash_m of
    # the ball. Delivered to athletes as public team instructions; a tactics layer may override them.
    defender_baseline: bool = True
    defender_mark_distance_m: float = 5.0
    defender_ball_leash_m: float = 25.0
    # RB-3.22 (owner CANON, 'everything on by default'): the ACCEPTED RB-3.21 baseline is the default; each stays switchable.
    rb3_handoff_block_enabled: bool = True
    rb3_carrier_moves_enabled: bool = True
    carry_release_radius_m: float = 3.0
    # RB-3.19 BEHAVIORAL (cognition only, PROVISIONAL): keep the ball in play. rb319_parts lists the enabled steps (A1 toss speed and lane,
    # A2 boundary awareness, A3 missed-ball pursuit, A4 pass depth safety). OFF (default) is the exact RB-3.18 effective configuration.
    rb319_ball_in_play_enabled: bool = True
    rb319_parts: str = 'A1A2A3A4'
    # RB-3.20a DEFECT FIX (engine, PROVISIONAL): exact ball-ground contact inside the step (native/rulebook/ball_ground.py).
    # False is the exact RB-3.19 effective configuration and physics.
    rb320_exact_bounce: bool = True
    # RB-3.21 BALL MATERIAL (owner ruling 21 Nov 2026: Beastball's ball is a fictional material; lead-set values, PROVISIONAL).
    # Model and use: native/rulebook/ball_material.py (engine step, predict_path, launch_for, c4c_path, the Native Keeper's course).
    # Design basis (lead targets): T-B1 level 35 m/s from 1.5 m rests after 38-45 m; T-B2 level 50 m/s rests within 60 m;
    # T-B3 a 58 m/s shot keeps >= 90% of its speed over 20 m of flight; T-B4 a 20 m/s pass at the normal launch angle rests within
    # 25 m. Values: the gentlest grid point meeting all four (least change from the previous engine: horizontal .76, restitution
    # .7746, roll ~exp(-3t) ~ 3 m/s^2 at 1 m/s, drag ~0), searched in native/evidence/rb321/material_search.py.
    rb321_ball_material_enabled: bool = True
    rb321_ball_drag_k: float = .0005        # 1/m, quadratic air drag dv/dt = -k|v|v
    rb321_ball_bounce_h: float = .44        # horizontal speed kept per bounce (was .76)
    rb321_ball_restitution: float = .6      # vertical restitution (was .7746)
    rb321_ball_roll_decel: float = 3.0      # m/s^2, constant rolling resistance (was v *= 1 - 3 dt)
    # RB-3.22 talent source (ENGINEERING, diagnosis only): how the NBL roster loader fills ratings. Applied when the roster is
    # loaded (native/nbl_roster.load_canon_nbl via native.rulebook.reach_run --override); recorded here so the run is labelled.
    rb322_technical_source: str = 'ovr'       # 'ovr' (Opening-day OVR/100) | 'neutral' (.784 for every player)
    rb322_physical_source: str = 'roster'     # 'roster' | 'neutral' (league mean of each of the nine physical ratings)

    individuation: str = 'off'
    fatigue_rotation: bool = False
    rotation_rhythm: str = "R1"
    planned_rate_scale: float = PLANNED_RATE_SCALE
    rb333: tuple[str, ...] = ()
    tackles_per_possession: int = 2
    rb332_pass_clearance: bool = False
    rb332_carry_finish: bool = False
    rb332_fresh_takedown: bool = False
    rb332_boundary_guard: bool = False
    drill_values_path: str | None = None
    drill_values_sha256: str | None = None

    def with_drill_values(self, path):
        from native.learned_values import read_model

        values = read_model(path)
        return replace(self,drill_values_path=str(path),drill_values_sha256=values.digest)

    def record(self):
        record = super().record()
        if self.tackles_per_possession == 2:
            record.pop('tackles_per_possession')
        if not self.rb333:
            record.pop('rb333')
        record.pop('drill_values_path')
        for key in ('rb332_pass_clearance','rb332_carry_finish','rb332_fresh_takedown','rb332_boundary_guard'):
            if not record[key]:
                record.pop(key)
        if self.rotation_rhythm != 'PLANNED':
            record.pop('planned_rate_scale')
        if self.rotation_rhythm == 'R1':
            record.pop('rotation_rhythm')
        if self.fatigue_rotation:
            from .fatigue_rotation import parameters

            record['fatigue_rotation_parameters'] = parameters(self.rotation_rhythm, self.planned_rate_scale)
        else:
            record.pop('fatigue_rotation')
        if self.drill_values_sha256 is None:
            record.pop('drill_values_sha256')
        if self.individuation == 'off':
            record.pop('individuation')
        if not self.rb3_handoff_block_enabled:
            # OFF is the exact RB-3.16 effective configuration.
            record.pop('rb3_handoff_block_enabled')
        if not self.rb3_carrier_moves_enabled:
            record.pop('rb3_carrier_moves_enabled')
        if self.carry_release_radius_m == 0:
            record.pop('carry_release_radius_m')
        if self.rb322_technical_source == 'ovr':
            record.pop('rb322_technical_source')
        if self.rb322_physical_source == 'roster':
            record.pop('rb322_physical_source')
        if not self.rb321_ball_material_enabled:
            for key in ('rb321_ball_material_enabled', 'rb321_ball_drag_k', 'rb321_ball_bounce_h', 'rb321_ball_restitution', 'rb321_ball_roll_decel'):
                record.pop(key)
        if not self.rb320_exact_bounce:
            record.pop('rb320_exact_bounce')
        if not self.rb319_ball_in_play_enabled:
            record.pop('rb319_ball_in_play_enabled'); record.pop('rb319_parts')
        return record

    def __post_init__(self):
        from .fatigue_rotation import RHYTHMS
        from native.ladder import SWITCHES
        if type(self.tackles_per_possession) is not int or self.tackles_per_possession not in (2,3,4):
            raise ValueError('the tackle count must be 2, 3, or 4')
        if set(self.rb333) - SWITCHES or len(set(self.rb333)) != len(self.rb333):
            raise ValueError("unknown or repeated RB-3.33 switch")
        expected_pocket=_RB3_POCKET
        if {'carry_seven', 'carry_value'}.intersection(self.rb333):
            object.__setattr__(self,'carry_points',7)
            expected_pocket=tuple((key,7 if key=='carry_value' else value) for key,value in _RB3_POCKET)
            if self.pocket_settings==_RB3_POCKET:
                object.__setattr__(self,'pocket_settings',expected_pocket)
        if 'cadence' in self.rb333:
            object.__setattr__(self,'sense_ms',self.dt_ms)
            object.__setattr__(self,'decision_ms',200 if 'fast_cadence' in self.rb333 else 300)

        if (self.rotation_rhythm not in (*RHYTHMS, 'PLANNED')
                or self.rotation_rhythm != 'R1' and not self.fatigue_rotation):
            raise ValueError('a rotation rhythm requires the fatigue switch')
        if self.rotation_rhythm == 'PLANNED' and not 0 < self.planned_rate_scale <= 1:
            raise ValueError('planned rotation rate scale must be in (0, 1]')
        if not isinstance(self.fatigue_rotation, bool):
            raise ValueError('fatigue_rotation must be a boolean')
        if (self.drill_values_path is None) != (self.drill_values_sha256 is None):
            raise ValueError('DRILL path and fingerprint must be provided together')
        if self.drill_values_path is not None and self.individuation != 'individuation/2':
            raise ValueError('DRILL values require PRISM CORE')
        if self.individuation not in ('off', 'individuation/1', 'individuation/2'):
            raise ValueError('unknown individuation mapping')
        if self.individuation in ('individuation/1', 'individuation/2'):
            object.__setattr__(self, 'physical_assumptions', tuple(
                (key, 1. if key == 'fatigue_rate' else value)
                for key, value in self.physical_assumptions))
        if self.rb322_technical_source not in ('ovr', 'neutral', 'explicit') or self.rb322_physical_source not in ('roster', 'neutral'):
            raise ValueError('rb322 talent source must be ovr|neutral|explicit and roster|neutral')
        if not math.isfinite(self.carry_release_radius_m) or self.carry_release_radius_m < 0:
            raise ValueError('carry release radius must be finite and nonnegative')
        if self.thaw_contact_buffer_ms<0:raise ValueError('thaw_contact_buffer_ms must be >= 0')
        if self.defender_mark_distance_m<=0 or self.defender_ball_leash_m<=0:raise ValueError('defender baseline distances must be positive')
        if self.zone_residence_ms<=0 or self.zone_marked_distance_m<0:raise ValueError('zone residence parameters out of range')
        if self.version!='native-rb/3' or self.profile!='native-rb' or self.scoring!='banded':raise ValueError('RB/3 profile mixing')
        if len(self.roster_digests)!=2 or any(not isinstance(x,str) or len(x)!=64 for x in self.roster_digests):raise ValueError('RB/3 requires A and B roster digests')
        if self.mapping_version!='attr-map/2' or self.body_standards!=() or self.pocket_settings!=expected_pocket:raise ValueError('RB/3 mapping/mechanics mismatch')
        if self.m2!='null' or self.legacy_layers or (self.periods,self.period_seconds,self.overtime_seconds)!=(4,600,300):raise ValueError('RB/3 canon profile mismatch')
