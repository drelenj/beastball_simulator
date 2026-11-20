from dataclasses import dataclass
from native.config import NativeConfig,POCKET

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
    rb3_handoff_block_enabled: bool = False

    def record(self):
        record = super().record()
        if not self.rb3_handoff_block_enabled:
            # OFF is the exact RB-3.16 effective configuration.
            record.pop('rb3_handoff_block_enabled')
        return record

    def __post_init__(self):
        if self.thaw_contact_buffer_ms<0:raise ValueError('thaw_contact_buffer_ms must be >= 0')
        if self.defender_mark_distance_m<=0 or self.defender_ball_leash_m<=0:raise ValueError('defender baseline distances must be positive')
        if self.zone_residence_ms<=0 or self.zone_marked_distance_m<0:raise ValueError('zone residence parameters out of range')
        if self.version!='native-rb/3' or self.profile!='native-rb' or self.scoring!='banded':raise ValueError('RB/3 profile mixing')
        if len(self.roster_digests)!=2 or any(not isinstance(x,str) or len(x)!=64 for x in self.roster_digests):raise ValueError('RB/3 requires A and B roster digests')
        if self.mapping_version!='attr-map/2' or self.body_standards!=() or self.pocket_settings!=_RB3_POCKET:raise ValueError('RB/3 mapping/mechanics mismatch')
        if self.m2!='null' or self.legacy_layers or (self.periods,self.period_seconds,self.overtime_seconds)!=(4,600,300):raise ValueError('RB/3 canon profile mismatch')
