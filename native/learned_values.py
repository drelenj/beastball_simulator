"""Frozen DRILL value artifacts and belief-only lookup for PRISM."""
from bisect import bisect_left
from dataclasses import dataclass
from hashlib import sha256
import json
from math import hypot, isfinite
from pathlib import Path
from types import SimpleNamespace

SCHEMA = 'oracle-drill-v1/1'
FEATURE_VERSION = 'prism-possession-features/1'
STAGES = ('carrier','finishing')


def bucket(value, edges):
    return '?' if value is None else str(sum(value >= edge for edge in edges))


def feature_keys(stage, view, opponents, pressured, option):
    """Feature hierarchy in decreasing order of generality."""
    from . import cognition_rb3 as rb
    from .throw_speed import release_speed

    intent = option.intent
    kind = option.label.split(':',1)[0] if option.label in ('carry_goal','evade') else intent.kind
    gx, gy = 100.-view.own_goal_x, 50.
    goal_distance = hypot(gx-view.x,gy-view.y)
    context = f"{kind}/{bucket(goal_distance,(10.,20.,40.))}/{int(pressured)}"
    detail = None
    if intent.aim is not None:
        x,y = intent.aim
        if intent.kind == 'pass':
            distance = hypot(x-view.x,y-view.y)
            gain = view.attack_sign*(x-view.x)
            target = SimpleNamespace(x=x,y=y)
            speed = intent.speed if stage=='passing' else release_speed(distance,view.max_throw_speed)
            lane = rb.lane_margin(view,target,opponents,max(1.,speed))
            detail = f"{bucket(gain,(0.,7.,15.))}/{bucket(lane,(0.,2.,5.))}"
        elif intent.kind in ('shoot','stretch') and stage == 'finishing':
            keeper = next((track for track in opponents if track.role=='keeper'),None)
            if keeper is not None:
                # Extrapolate only the goalkeeper the athlete actually sees.
                speed = max(1.,intent.speed)
                t = rb.release_time_s(view) + abs(x-view.x)/speed
                height = next((h for pid,h in getattr(view,'body_height',()) if pid==keeper.entity),2.39)
                gap = hypot(y-keeper.y-keeper.vy*t,intent.height-.62*height)
                detail = f"{bucket(gap,(1.,2.,3.,4.))}/{bucket(intent.height,(.8,1.5))}"
            else:
                detail = f"?/{bucket(intent.height,(.8,1.5))}"
        elif intent.kind == 'carry':
            free = rb.free_run_m(view,opponents,intent.aim)
            detail = bucket(free,(3.,8.,12.))
    return (kind,context,context+'/'+detail) if detail is not None else (kind,context)


def option_keys(stage, view, belief, options):
    from .cognition_rb3 import is_pressured

    opponents = tuple(track for track in belief.tracks
                      if track.team not in (view.team,'ball') and track.role != 'archer'
                      and 0 <= view.delivered_ms-track.captured_ms <= belief.max_track_age_ms)
    pressure = is_pressured(view,opponents)
    return tuple(feature_keys(stage,view,opponents,pressure,option) for option in options)


@dataclass(frozen=True)
class ValueTable:
    keys: tuple[str,...]
    points: tuple[float,...]
    prior: float

    def predict(self, candidates):
        for key in reversed(candidates):
            position = bisect_left(self.keys,key)
            if position < len(self.keys) and self.keys[position] == key:
                return self.points[position]
        return self.prior


@dataclass(frozen=True)
class LearnedValues:
    digest: str
    carrier: ValueTable
    finishing: ValueTable

    def score(self, stage, view, belief, options):
        table = self.carrier if stage=='carrier' else self.finishing
        return tuple(table.predict(keys) for keys in option_keys(stage,view,belief,options))


def read_model(path, expected_digest=None):
    """Read once before constructing a match. Only numeric fit cells are exposed."""
    payload = Path(path).read_bytes()
    fingerprint = sha256(payload).hexdigest()
    if expected_digest is not None and fingerprint != expected_digest:
        raise ValueError('DRILL artifact sha256 mismatch')
    data = json.loads(payload)
    if (data.get('schema') != SCHEMA or data.get('feature_version') != FEATURE_VERSION
            or set(data.get('expected_points',{})) != set(STAGES)):
        raise ValueError('unsupported DRILL value schema')
    tables = []
    for name in STAGES:
        record = data['expected_points'][name]
        rows = sorted((key,cell['prediction']) for key,cell in record['bins'].items())
        values = [record['global_prior'],*(value for _,value in rows)]
        if any(isinstance(value,bool) or not isinstance(value,(int,float)) or
               not isfinite(value) or abs(value)>20. for value in values):
            raise ValueError(f'{name}: invalid DRILL points')
        tables.append(ValueTable(tuple(key for key,_ in rows),tuple(v for _,v in rows),values[0]))
    return LearnedValues(fingerprint,*tables)
