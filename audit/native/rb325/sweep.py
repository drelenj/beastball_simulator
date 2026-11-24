"""Paired rating scenarios for PRISM CORE. Outcome differences are descriptive."""
import argparse
from collections import Counter
from dataclasses import replace
import csv
import json
from math import atan2, degrees, hypot, log2
from pathlib import Path
from statistics import mean

from native import cognition as C, prism_core as CORE, prism_lab as L, prism_registry as R
from native.prism_motion import maneuver, reflex_gain, STIFF_ARM_IMPULSE_RANGE, TRUCK_DRIVE_RANGE

DECISIONS = frozenset(('playmaking', 'defending', 'zone_coverage', 'in_air_ball_pursuit',
                       'live_ball_pursuit', 'disruption', 'goalkeeping', 'passing',
                       'finishing', 'evasion', 'takedown'))


def base_view(seed, name, value):
    v, b, contact, rng = L.scene(seed, name, value)
    return replace(v, core_entropy=f'paired/{seed}'), b, contact, rng


def decision_probe(name, value, seed):
    view, belief, contact, rng = base_view(seed,name,value)
    # Controlled near-tie menu estimates, using identical physical commands and
    # exact production valuation/noise. This isolates option selection only.
    first = C.ActionIntent('i','d',view.athlete,'carry',None,(91.,51.),None,None,view.delivered_ms)
    labels = {
        'playmaking': ('carry','shoot'), 'defending': ('mark','chase'),
        'zone_coverage': ('near_post','far_post'), 'in_air_ball_pursuit': ('pursue_now','landing'),
        'live_ball_pursuit': ('approach','intercept'), 'disruption': ('hold','draw'),
        'goalkeeping': ('set','save'), 'passing': ('direct','loft'), 'finishing': ('high','near_post'),
        'evasion': ('dodge','run_through'), 'takedown': ('drive','contain'),
    }[name]
    candidates = [CORE.Option(first, 1. + rng.uniform(-.12,.12), name, label) for label in labels]
    menu = CORE.Menu(view)
    selected = menu.choose(name,candidates)
    records = menu.records[0]['options']
    magnitude = mean(abs(row[3]-row[2]) for row in records)
    return magnitude, selected.label, 'near-tie selector using production menu'


def reset_motor_fixture():
    port, player = L.physical_lab()
    player.z = player.vz = 0.
    player.posture = 'upright'
    player.fatigue = 1.
    player.bal_src = {}
    player.a.balance = player.a.endurance = .7
    player.a.jump_height = .91
    player.a.maximum_speed = L.R.speed_mps(.7)
    player.a.acceleration = L.R.acceleration(.7)
    for technique in R.MANEUVERS:
        player.native_registry[technique] = .7
    return port,player


def throw_probe(name, value, seed, rng):
    port, player = reset_motor_fixture()
    state = port.m.s
    state.now += 1_000
    state.owner = player.team
    state.restart = None
    player.x, player.y = 50., 50.
    state.ball = port.types.Ball(mode=port.types.BallMode.CONTROLLED,
                                 x=player.x, y=player.y, z=player.hand_height,
                                 last_touch=player.team, carrier=player.id)
    port.pending.clear()
    port.m.rng['ball'].seed(seed)
    player.a.ball_handling = value if name == 'ball_handling' else .7
    player.native_max_throw_speed = L.R.max_throw_speed(value if name == 'throw_power' else .7)
    player.native_throw_error_base_deg = L.R.throw_error_base_deg(value if name == 'throw_accuracy' else .7)
    speed = player.native_max_throw_speed if name == 'throw_power' else 50.
    attempt = C.ActionIntent('i','d',player.id,'pass',None,(75.,50.),None,None,state.now,
                             speed=speed,height=1.6,period=state.period)
    command = port.submit(attempt)['command']
    state.now = command.release_ms
    port.ball_motor()
    assert port.outcomes[-1].status == 'released'
    if name == 'throw_power':
        speed = hypot(state.ball.vx,state.ball.vy,state.ball.vz)
        return speed, speed >= rng.uniform(77.,130.), 'actual ball release speed'
    if name == 'throw_accuracy':
        yaw = abs(degrees(atan2(state.ball.vy,state.ball.vx)))
        return yaw, yaw <= rng.uniform(.2,2.0), 'actual ball release heading'
    elapsed = command.release_ms - command.start_ms
    return elapsed, elapsed <= rng.uniform(215.,293.), 'actual pass wind-up'


def probe(name, value, seed):
    if name in DECISIONS:
        return decision_probe(name,value,seed)
    view, belief, contact, rng = base_view(seed,name,value)
    if name == 'reaction':
        ms = round(view.core_decision_ms * (1. + .4 * (.7-value)))
        return ms, ms <= rng.randrange(440,570), 'deliberate decision deadline'
    if name == 'focus':
        cap = CORE.FOCUS_BASE_CAPACITY + round(8 * (value-.7))
        age = CORE.FOCUS_BASE_RETENTION_MS + round(600 * (value-.7))
        return age, min(cap,rng.randrange(17,25)), 'track age and capacity'
    if name == 'anticipation':
        course = CORE.future_course(belief,value).ball_course
        return course.vy, round(course.y + course.vy * .35,5), 'forecast displacement'
    if name == 'reflex':
        p = type('Own',(),{'native_registry': {'reflex':value}})()
        factor = reflex_gain(p)
        return factor, .12 * factor <= rng.uniform(.085,.16), 'hands adjustment cutoff'
    if name in ('juke','spin','hurdle'):
        port,p = reset_motor_fixture()
        p.native_registry[name]=value
        p.x,p.y,p.vx,p.vy,p.vz,p.posture=50.,50.,5.,0.,0.,'upright'
        intent=C.ActionIntent('i','d',p.id,'carry',None,(55.,54.),None,None,0,technique=name)
        aim=maneuver(p,intent,port.m.assume['gravity'])
        amount = {'juke':aim[1]-50.,'spin':p.speed,'hurdle':p.vz}[name]
        return amount, round(amount,6), 'motor execution'
    if name in ('stiff_arm','truck'):
        change = STIFF_ARM_IMPULSE_RANGE if name=='stiff_arm' else TRUCK_DRIVE_RANGE
        scale = 1. + change*(value-.7)
        return scale, scale > rng.uniform(.8,1.2), 'contact model impulse threshold'
    if name in ('ball_handling','throw_power','throw_accuracy'):
        return throw_probe(name,value,seed,rng)
    if name == 'jump':
        port,p = reset_motor_fixture()
        p.a.jump_height = 1.3 * value
        aim = C.ActionIntent('i','d',p.id,'carry',None,(25.,55.),None,None,0,technique='hurdle')
        maneuver(p,aim,port.m.assume['gravity'])
        height = p.vz**2 / (2 * port.m.assume['gravity'])
        return height, height >= rng.uniform(.13,.30), 'physical hurdle clearance'
    if name in ('speed','acceleration','stamina','balance','catching'):
        reset_motor_fixture()
    return L.probe(name,value,seed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('raw',type=Path)
    parser.add_argument('table',type=Path)
    args=parser.parse_args()
    names=sorted((set(L.R.RATINGS)|set(L.R.INERT_RATINGS)|set(R.NEW_RATINGS)|set(R.MANEUVERS)|{'acceleration'})-R.ALIASES.keys())
    result = {}
    rows=[]
    for name in names:
        levels=[[probe(name,x,seed) for seed in L.SEEDS] for x in L.LEVELS]
        reference=levels[3]
        metrics=[mean(trial[0] for trial in cases) for cases in levels]
        spread=max(metrics)-min(metrics)
        base=metrics[3]
        total_effect=100*spread/abs(base) if base else None
        jumps=[abs(a-b) for a,b in zip(metrics,metrics[1:])]
        result[name] = {}
        distributions = [Counter(trial[1] for trial in cases) for cases in levels] if name in DECISIONS else []

        def choice_distance(first, second):
            return sum(abs(first[k]-second[k]) for k in first.keys() | second.keys()) / (2 * len(L.SEEDS))

        max_choice_effect = max((choice_distance(a,b) for a in distributions for b in distributions), default=0.)
        for i,(x,cases,metric) in enumerate(zip(L.LEVELS,levels,metrics)):
            comparable=[(a,b) for a,b in zip(cases,reference) if a[1] is not None and b[1] is not None]
            flip = sum(a[1]!=b[1] for a,b in comparable)/len(comparable) if comparable else None
            counts=Counter(a[1] for a,b in comparable) if name in DECISIONS else {}
            entropy=-sum(n/20*log2(n/20) for n in counts.values()) if counts else None
            row=dict(rating=name,level=x,seeds=len(cases),mean=metric,delta_pct=100*(metric-base)/abs(base) if base else None,
                     total_effect_pct=total_effect,changed_share=flip,decision_entropy_bits=entropy,
                     decision_counts=counts, decision_total_variation=max_choice_effect if distributions else None,
                     decision_jump_over_half=bool(i and distributions and max_choice_effect and
                                                  choice_distance(distributions[i-1],distributions[i])>.5*max_choice_effect),
                     under_two_pct=total_effect is not None and total_effect<2,
                     jump_over_half=i>0 and spread>0 and jumps[i-1]>.5*spread, scope=cases[0][2])
            rows.append(row)
            result[name][str(x)] = dict(row,trials=cases)
    args.raw.write_text(json.dumps(result,sort_keys=True)+'\n')
    with args.table.open('w',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)


if __name__ == '__main__':
    main()
