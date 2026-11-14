"""Versioned explicit mechanics; constructed before loading the physical substrate."""
from dataclasses import dataclass, asdict, field
import ast
from functools import lru_cache
from pathlib import Path
import hashlib
import json

@lru_cache(maxsize=1)
def physical_defaults():
    # Read a literal data record BEFORE importing/building the physical engine.
    tree=ast.parse((Path(__file__).resolve().parents[1]/'core_src/match.py').read_text())
    node=next(n for n in tree.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DEFAULT_ASSUMPTIONS' for t in n.targets))
    values=ast.literal_eval(node.value)
    values.update(controller=0,c3_region_policy=0,fatigue_rate=0.,c1_receiver_routing=0,c1_chasers_read_flight=0)
    return tuple(sorted(values.items()))

POCKET = tuple(sorted(dict(player_speed=27.,acceleration=10.,braking=13.5,turning=13.,arrow_speed=29.,
                          ball_limit=40.,arrow_limit=30.,pass_speed=27.,keeper_zone_radius=20.,
                          inner_zone_radius=15.,inner_points=2,release_points=2,outside_points=2,carry_value=2,
                          release_territories=True,zone_only=False,tackles_per_possession=2,
                          zone_inbound=False,zone_marking=False,marking_distance=5.).items()))

@dataclass(frozen=True)
class NativeConfig:
    version: str = 'native-v0/1'
    profile: str = 'native-v0'
    periods: int = 4
    period_seconds: int = 600
    overtime_seconds: int = 300
    play_clock_ms: int = 30000
    goal_radius: float = 3.
    goal_depth: float = 3.
    zone_radius: float = 20.
    platform_height: float = 5.
    platform_setback: float = 5.
    marking_distance: float = 5.
    arrows: int = 25
    freezes: int = 5
    freeze_ms: int = 5000
    immunity_ms: int = 10000
    direct_ms: int = 500
    dt_ms: int = 100
    sense_ms: int = 200
    decision_ms: int = 500
    latency_ms: int = 200
    ratings: float = .70
    catch_model: str = 'CATCH_V2-energy-placeholder'
    hand_fight: str = 'intent-gated-placeholder'
    throw_model: str = 'THROW_SPLIT-primitive'
    m2: str = 'null'
    body_standards: tuple = (('height',2.55),('mass',230.),('reach',1.173),('maximum_speed',27.),('acceleration',10.),('braking',13.5),('turning',13.),('decision_speed',.3),('archery_release_speed',29.),('jump_height',1.3))
    physical_assumptions: tuple = field(default_factory=physical_defaults)
    pocket_settings: tuple = POCKET
    automatic_containment: bool = False
    automatic_descent: bool = False
    fatigue: bool = False
    injury: bool = False
    legacy_layers: tuple = ()

    def __post_init__(self):
        if self.physical_assumptions!=physical_defaults() or self.pocket_settings!=POCKET:
            raise ValueError('native-v0 mechanics are versioned together; profile mixing rejected')
        if self.profile != 'native-v0' or self.m2 != 'null' or self.legacy_layers:
            raise ValueError('Native does not mix profiles or enable legacy deciders')
        if self.periods != 4 or self.period_seconds != 600 or self.overtime_seconds != 300:
            raise ValueError('full canon duration required; scenarios set state clocks explicitly')

    def record(self):
        return asdict(self)

    @property
    def digest(self):
        return hashlib.sha256(json.dumps(self.record(),sort_keys=True).encode()).hexdigest()
