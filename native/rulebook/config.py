from dataclasses import dataclass
from native.config import NativeConfig,POCKET

RB_POCKET=tuple((k,250. if k=="arrow_speed" else None if k=="arrow_limit" else 44.7 if k=="player_speed" else v) for k,v in POCKET)
RB_BODY=tuple((k,44.7 if k=="maximum_speed" else 250. if k=="archery_release_speed" else v) for k,v in NativeConfig().body_standards)

@dataclass(frozen=True)
class RulebookConfig(NativeConfig):
    version: str = 'native-rb/1'
    profile: str = 'native-rb'
    field_roster_limit: int = 12
    scoring: str = 'flat'
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
        if self.version!='native-rb/1' or self.profile!='native-rb':raise ValueError('RB profile mixing')
        if self.scoring not in ('flat','banded'):raise ValueError('scoring mode')
        if self.m2!='null' or self.legacy_layers:raise ValueError('RB retains null M2 and no legacy layers')
        if (self.periods,self.period_seconds,self.overtime_seconds)!=(4,600,300):raise ValueError('canon duration')
