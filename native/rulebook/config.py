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
