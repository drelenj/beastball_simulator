"""Paired real ingress and throw-motor probes for three execution ratings."""
import argparse
from dataclasses import replace
import json
from math import atan2, degrees, sqrt
from pathlib import Path
from random import Random
from statistics import mean

from b1.emergence_intents import KeeperIntent, plan_keeper_motor
from native.cognition import ActionIntent
from native.port import body
from native.prism_lab import LEVELS, SEEDS, physical_lab
from native.roster import max_throw_speed, throw_error_base_deg

parser = argparse.ArgumentParser()
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
port, athlete = physical_lab()
state = port.m.s


def trial(name, level, seed):
    draw = Random(seed)
    if name == 'jump':
        k = replace(body(athlete), x=2., y=50., vx=0., vy=0., vz=0., jump_height=1.3 * level)
        aim = (2., 50. + draw.uniform(.7, 1.4), draw.uniform(1.9, 3.1))
        intent = KeeperIntent('keeper', athlete.id, 'save', 0, 'fixture',
                              course=((0., 8., 50., aim[2]), (.29, *aim)))
        command = plan_keeper_motor(intent, k, now_ms=0, pushoff_fraction=.37,
                                    extension_fraction=.3, reach_factor=.9, match_lean=True)
        return sqrt(2 * 9.81 * k.jump_height), (command.kind, command.impulse)
    state.now += 1000
    state.phase = port.types.Phase.LIVE
    state.owner = athlete.team
    state.restart = None
    state.ball = port.types.Ball(mode=port.types.BallMode.CONTROLLED,
                                 x=50., y=50., z=athlete.hand_height, carrier=athlete.id,
                                 last_touch=athlete.team)
    athlete.x, athlete.y = 50., 50.
    athlete.a.ball_handling = level if name == 'ball_handling' else .70
    athlete.native_max_throw_speed = max_throw_speed(level if name == 'throw_power' else .70)
    athlete.native_throw_error_base_deg = throw_error_base_deg(level if name == 'throw_accuracy' else .70)
    port.m.rng['ball'] = Random(seed)
    speed = draw.uniform(66., 138.) if name == 'throw_power' else 50.
    intent = ActionIntent('intent', 'decision', athlete.id, 'pass', None, (65., 50.),
                          None, None, state.now, speed=speed, height=1.6, period=state.period)
    port.pending.clear()
    admission = port.submit(intent)
    if name == 'throw_power':
        return (athlete.native_max_throw_speed, admission['status'])
    assert admission['status'] == 'accepted', admission
    pending = port.pending[athlete.id]
    delay = pending['due'] - state.now
    if name == 'ball_handling':
        state.now += draw.randrange(215, 291)
    else:
        state.now = pending['due']
    port.ball_motor()
    if name == 'ball_handling':
        return delay, state.ball.carrier is None
    assert state.ball.carrier is None, port.outcomes[-1:]
    yaw = degrees(atan2(state.ball.vy, state.ball.vx))
    return abs(yaw), round(yaw, 6)


result = {}
for name in ('ball_handling', 'throw_power', 'throw_accuracy', 'jump'):
    reference = [trial(name, .70, seed)[1] for seed in SEEDS]
    rows = []
    for level in LEVELS:
        values = [trial(name, level, seed) for seed in SEEDS]
        rows.append(dict(level=level, mean=mean(v for v, _ in values),
                         changed=sum(o != old for (_, o), old in zip(values, reference)),
                         trials=values))
    result[name] = rows
args.out.write_text(json.dumps(result, indent=2) + '\n')
