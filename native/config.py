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
    version: str = 'native-v0/2'
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
    dead_stall_limit_ms: int = 120000
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


# ---------------------------------------------------------------------------
# native-v0/3 (FAB-1). NativeConfig above is native-v0/2 and is not altered:
# its record, digest and behaviour stay byte-identical (Native PRISM 0).
# ---------------------------------------------------------------------------
CANON_ARROW_SPEED = 250.          # m/s, owner-confirmed (FAB-1a)

def _standards_v3(arrow_speed):
    return tuple((k,arrow_speed if k=='archery_release_speed' else v) for k,v in NativeConfig.body_standards)

def _pocket_v3(arrow_speed):
    # No arrow_limit key: canon has no arrow speed cap.
    return tuple(sorted((k,arrow_speed if k=='arrow_speed' else v) for k,v in POCKET if k!='arrow_limit'))

@dataclass(frozen=True)
class NativeConfigV3(NativeConfig):
    version: str = 'native-v0/3'
    # FAB-1a. Arrow release speed = arrow_speed_ratio x fastest-player maximum_speed.
    # Default reproduces the canon 250 m/s at the engine's present 27 m/s top speed.
    # Change this one number (or pass --arrow-speed-ratio) to change arrow speed.
    arrow_speed_ratio: float = CANON_ARROW_SPEED/27.
    arrow_speed_cap: float | None = None      # canon: no cap
    # FAB-1b. Wrap, takedown, run-through, brace and dodge are athlete intents;
    # the engine's hold-mode and escape-effort placeholder controllers are not used.
    athlete_contact: str = 'intent-owned-v1'
    # FAB-1c. Belief-based restart claim / target / position decisions.
    restart_cognition: str = 'belief-v1'
    body_standards: tuple = ()                # derived in __post_init__
    pocket_settings: tuple = ()               # derived in __post_init__

    def __post_init__(self):
        if not self.arrow_speed_ratio>0:raise ValueError('arrow_speed_ratio must be positive')
        if self.arrow_speed_cap is not None:raise ValueError('canon has no arrow speed cap')
        speed=self.arrow_speed
        for name,want in (('body_standards',_standards_v3(speed)),('pocket_settings',_pocket_v3(speed))):
            if getattr(self,name) not in ((),want):raise ValueError('native-v0/3 derives '+name+' from arrow_speed_ratio')
            object.__setattr__(self,name,want)
        if self.physical_assumptions!=physical_defaults():
            raise ValueError('native-v0 mechanics are versioned together; profile mixing rejected')
        if self.version!='native-v0/3' or self.profile!='native-v0' or self.m2!='null' or self.legacy_layers:
            raise ValueError('Native does not mix profiles or enable legacy deciders')
        if self.periods!=4 or self.period_seconds!=600 or self.overtime_seconds!=300:
            raise ValueError('full canon duration required; scenarios set state clocks explicitly')
        if self.athlete_contact!='intent-owned-v1' or self.restart_cognition!='belief-v1':
            raise ValueError('native-v0/3 mechanics are versioned together')

    @property
    def fastest_player_speed(self):
        return dict(NativeConfig.body_standards)['maximum_speed']

    @property
    def arrow_speed(self):
        return round(self.arrow_speed_ratio*self.fastest_player_speed,6)


def _attr_pocket():
    values=dict(POCKET)
    values.update(player_speed=44.704,arrow_speed=250.,ball_limit=134.1)
    values.pop('arrow_limit',None)
    values.pop('pass_speed',None)
    return tuple(sorted(values.items()))


@dataclass(frozen=True)
class AttrConfig(NativeConfigV3):
    """ATTR-1 mechanics. Roster content is supplied to NativePort separately."""
    version: str = 'attr-map/1'
    profile: str = 'native-attr'
    mapping_version: str = 'attr-map/1'
    roster_digests: tuple = ()
    arrow_speed_ratio: float | None = None
    body_standards: tuple = ()
    pocket_settings: tuple = field(default_factory=_attr_pocket)

    def __post_init__(self):
        if self.version!='attr-map/1' or self.profile!='native-attr' or self.mapping_version!='attr-map/1':
            raise ValueError('ATTR-1 profile mixing rejected')
        if len(self.roster_digests)!=2 or any(not isinstance(x,str) or len(x)!=64 for x in self.roster_digests):
            raise ValueError('ATTR-1 requires two canonical roster digests')
        if self.body_standards!=() or self.pocket_settings!=_attr_pocket():
            raise ValueError('ATTR-1 derives body standards from rosters and mechanics from attr-map/1')
        if self.physical_assumptions!=physical_defaults() or self.m2!='null' or self.legacy_layers:
            raise ValueError('ATTR-1 does not mix physical assumptions or legacy layers')
        if (self.periods,self.period_seconds,self.overtime_seconds)!=(4,600,300):
            raise ValueError('full canon duration required')

    @property
    def fastest_player_speed(self):return 44.704

    @property
    def arrow_speed(self):return 250.


VERSIONS = {'native-v0/2':NativeConfig,'native-v0/3':NativeConfigV3,'attr-map/1':AttrConfig}

def config_for(version='native-v0/2',**overrides):
    return VERSIONS[version](**overrides)

def is_v3(config):
    return isinstance(config,NativeConfigV3)

def is_attr(config):
    return isinstance(config,AttrConfig)
