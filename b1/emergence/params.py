"""EMERGENCE-1 PolicyParams: a team's fixed, bounded preference vector.

PRIMITIVE: 16 numbers. They are searched, not truths. A vector is fixed before the
match, identical for all teammates, and reaches cognition only inside the athlete's
own AthleteView. Pure module (dataclasses, math only).
"""
from dataclasses import dataclass, fields, asdict

# name: (low, high, default, meaning)
BOUNDS = {
    'bias_pass':     (-6., 6., 0., 'added to every pass option value'),
    'bias_shoot':    (-6., 6., 0., 'added to the shoot option value'),
    'bias_press':    (-6., 6., 0., 'added to press (close on the believed carrier)'),
    'bias_pursue':   (-6., 6., 0., 'added to pursue / contest a loose ball'),
    'pass_min_clearance': (0., 6., 0., 'risk: pass options with believed lane clearance below this (m) are dropped'),
    'shot_range':    (8., 60., 32., 'risk: maximum believed distance to goal (m) at which shoot is an option'),
    'pos_ball_att':  (-3., 3., .6, 'positioning, own team has passive possession: pull toward the believed ball'),
    'pos_ball_def':  (-3., 3., 1.2, 'positioning, other team has possession: pull toward the believed ball'),
    'pos_goal_att':  (-3., 3., 1., 'positioning, in possession: pull toward the goal attacked'),
    'pos_goal_def':  (-3., 3., 1., 'positioning, out of possession: pull toward own goal'),
    'pos_spread':    (-3., 3., 1., 'positioning: prefer distance from the nearest believed teammate'),
    'pos_opp_att':   (-3., 3., .6, 'positioning, in possession: prefer distance from the nearest believed opponent'),
    'pos_opp_def':   (-3., 3., .6, 'positioning, out of possession: prefer closeness to the nearest believed opponent'),
    'pos_lane':      (-3., 3., .8, 'positioning, in possession: prefer an open believed lane from the carrier'),
    'pos_edge_zone': (0., 3., 1., 'positioning: penalty near field edges and inside either Keeper zone'),
    'archer_eager':  (-3., 3., 0., 'Archer: added to every draw-and-release option value'),
}
NAMES = tuple(BOUNDS)


@dataclass(frozen=True)
class PolicyParams:
    bias_pass: float = 0.
    bias_shoot: float = 0.
    bias_press: float = 0.
    bias_pursue: float = 0.
    pass_min_clearance: float = 0.
    shot_range: float = 32.
    pos_ball_att: float = .6
    pos_ball_def: float = 1.2
    pos_goal_att: float = 1.
    pos_goal_def: float = 1.
    pos_spread: float = 1.
    pos_opp_att: float = .6
    pos_opp_def: float = .6
    pos_lane: float = .8
    pos_edge_zone: float = 1.
    archer_eager: float = 0.

    def __post_init__(self):
        for f in fields(self):
            v = getattr(self, f.name)
            lo, hi = BOUNDS[f.name][:2]
            if isinstance(v, bool) or not isinstance(v, (int, float)) or v != v or not lo <= v <= hi:
                raise ValueError(f'PolicyParams.{f.name}={v!r} outside [{lo}, {hi}]')

    def as_dict(self):
        return {k: round(float(v), 4) for k, v in asdict(self).items()}

    @staticmethod
    def from_dict(d):
        unknown = set(d) - set(NAMES)
        if unknown:
            raise ValueError(f'unknown PolicyParams fields: {sorted(unknown)}')
        return PolicyParams(**{k: float(v) for k, v in d.items()})

    def key(self):
        return ','.join(f'{getattr(self, n):.4f}' for n in NAMES)


assert tuple(f.name for f in fields(PolicyParams)) == NAMES
DEFAULT = PolicyParams()


def clip(name, value):
    lo, hi = BOUNDS[name][:2]
    return round(min(hi, max(lo, float(value))), 4)
