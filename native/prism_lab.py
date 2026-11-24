"""Reproducible paired PRISM scenarios and neutral-roster match checks."""
import argparse
from collections import Counter
from dataclasses import replace
import json
from math import degrees, hypot
from pathlib import Path
from random import Random
from statistics import mean
from time import process_time

from b1.emergence_intents import AthleteBody, BallCourseBelief
from . import cognition as C
from . import cognition_rb3 as RB
from . import cognition_v3 as V3
from . import individuation as IND
from . import prism_registry as P
from . import roster as R
from .nbl_roster import load_canon_nbl
from .rulebook.config import RulebookConfigV3
from .rulebook.port import RulebookPort
from .rulebook.rb31_soak import measure
from .run import run_match

LEVELS = (.4, .5, .6, .7, .8, .9, 1.)
SEEDS = range(1, 21)
TEAMS = ('Garvian Guardians', 'Ala Apex')


def neutral_rosters(real):
    rosters = load_canon_nbl(TEAMS) if real else R.rb3_control_rosters()
    keys = set(R.RATINGS) | set(R.OPTIONAL_RATINGS)
    return {team: R.load_rows(
        [dict(a.values) | dict.fromkeys(keys, .7) | {'id': a.source_id, 'role': a.role}
         for a in roster.athletes], team) for team, roster in rosters.items()}


def match_case(seed, mode, roster, max_steps=None):
    r = load_canon_nbl(TEAMS) if roster == 'real' else neutral_rosters(roster == 'neutral-real')
    cfg = RulebookConfigV3(roster_digests=tuple(r[t].digest for t in ('A', 'B')),
                           individuation=IND.VERSION if mode == 'on' else 'off')
    start = process_time()
    result, port = run_match(seed, cfg, rosters=r, max_steps=max_steps, port_factory=RulebookPort)
    result['cpu_ms_per_step'] = (process_time() - start) * 1000 / result['steps']
    result['possessions'] = measure(port, ())['possessions']
    result['prism_commits'] = dict(Counter(row['subagent'] for row in result.get('prism_commits', ())))
    return result


def scene(seed, name, value):
    rng = Random(seed)
    jitter = rng.uniform(-.3, .3)
    t = 1000
    view = C.AthleteView('obs', 'A0', 'A', 'field', 0, t, 81., 49., True, 1, 0., (),
                         C.Signals('live', 1, 50000, 1250, 0, 0, None, None, False, passive_team='A'),
                         body=AthleteBody('A0', 'A', 81., 49., 0., 6., 0., 0.,
                                          2.39, 1.26, 8.75, 11.81, 31.29, .91),
                         cognition='native-rb/3', max_throw_speed=95., registry_ratings=((name, value),))
    mate = C.Track('A1', 'A', 'field', 94., 55. + jitter, 3., 1., t)
    keeper = C.Track('BK', 'B', 'keeper', 98., 49.5 + jitter, 0., 0., t)
    ball = C.Track(C.BALL, 'ball', 'ball', 70. + jitter, 48., 9., 1., t)
    contact = C.Track('B1', 'B', 'field', 82. + jitter, 50., -3., 0., t)
    course = BallCourseBelief('course', t - 150, t, ball.x, ball.y, .8, 9., 1., .5)
    belief = C.BeliefState('belief', 'obs', (mate, keeper, ball), ball_course=course)
    return view, belief, contact, rng


def signature(intent):
    return (intent.kind, intent.target, intent.aim, intent.contact,
            round(intent.speed, 5), round(intent.height, 5))


def probe(name, value, seed):
    v, b, contact, rng = scene(seed, name, value)
    if name == 'vision':
        angle = rng.uniform(95., 118.)
        quantity = degrees(IND.visual_half_angle(value))
        return quantity, angle <= quantity, 'detection threshold'
    if name == 'awareness':
        distance = rng.uniform(9., 14.)
        quantity = P.radar_radius(value)
        return quantity, distance <= quantity, 'radar threshold'
    if name == 'clarity':
        read = P.recognize(b.ball_course, value, rng.random())
        return P.clarity_sd(value), read, 'recognition outcome'
    if name == 'focus':
        return P.memory_limit(value), 0 <= 1650 + rng.randrange(350) <= P.retention_ms(value), 'retained track'
    if name == 'reaction':
        ms = IND.cognitive_interval_ms(500, value)
        return ms, ms <= rng.randrange(450, 600), 'decision opportunity'
    if name == 'reflex':
        seconds = P.reflex_seconds(value)
        return seconds, seconds <= rng.uniform(.20, .42), 'preparation deadline'
    if name == 'instinct':
        stale = replace(contact, captured_ms=400)
        x,y = P.remembered_position(stale, v.delivered_ms, .70, value, 850)
        return hypot(x-stale.x, y-stale.y), (round(x, 3), round(y, 3)), 'estimated position'
    if name in ('anticipation', 'in_air_ball_pursuit', 'live_ball_pursuit'):
        read = 'loose' if name == 'live_ball_pursuit' else 'pass'
        vx = 4. if name == 'anticipation' else 0.
        v = replace(v, holds_ball=False, x=63. + rng.uniform(-1.0, 1.0), y=48., recognized_ball=read)
        mates = (C.Track('A1', 'A', 'field', 71., 48., 0., 0., 1000),
                 C.Track('A2', 'A', 'field', 70., 49., 0., 0., 1000))
        b = replace(b, tracks=(*mates, replace(b.tracks[-1], vx=vx, vy=0.)))
        intent, record = C.decide(v, b)
        pursuit = next((row[3] for row in record['options'] if row[0] == 'pursue'), 0.)
        return pursuit, signature(intent), 'selected command'
    if name in ('playmaking', 'passing', 'finishing'):
        if name == 'playmaking':
            intent, record = C.decide(v, b)
            return max(row[3] for row in record['options']), signature(intent), 'selected command'
        kind, target, aim = ('pass', 'A1', (94., 55.)) if name == 'passing' else ('shoot', None, (100., 51.))
        intent = C.ActionIntent('i', 'd', 'A0', kind, target, aim, None, None, 1000, speed=47.)
        intent = RB.committed_delivery(v, b, intent)
        return intent.speed if kind == 'pass' else intent.height, signature(intent), 'committed delivery'
    if name in ('defending', 'zone_coverage', 'takedown', 'evasion'):
        v = replace(v, holds_ball=name == 'evasion',
                    own_held=int(name == 'evasion'),
                    own_balance_load=.5 + rng.uniform(-.1, .1),
                    own_hold_target='B1' if name == 'takedown' else None,
                    prism_agent='defending')
        intent = C.ActionIntent('i', 'd', 'A0', 'carry' if v.holds_ball else 'press',
                                contact.entity, (88., 50.), None, None, 1000)
        if name == 'evasion':
            intent, record = V3.carrier_contact(v, b, intent, {})
        elif name == 'zone_coverage':
            v = replace(v, signals=replace(v.signals, passive_team='B'))
            agent = P.select_agent(v, replace(b, tracks=(contact,), ball_course=None), C.registry_rating)
            return value, agent, 'selected agent'
        else:
            contact = replace(contact, x=v.x + V3.TACKLE_COMMIT_M + rng.uniform(-.26, .26), y=v.y)
            intent, record = V3.defender_contact(v, replace(b, tracks=(contact,)), intent,
                                                  {'believed_carrier': ('B1', 'B')})
        return record['contact_options'][0 if name == 'evasion' else 1][3], signature(intent), 'selected contact'
    if name == 'goalkeeping':
        v = replace(v, role='keeper', x=2., y=50., holds_ball=False)
        b = replace(b, ball_course=replace(b.ball_course, y=64., vx=4.))
        intent, _ = C.decide(v, b)
        target = intent.auxiliary.target
        return target[1], target, 'selected positioning'
    if name == 'disruption':
        v = replace(v, role='archer', x=-5., y=50., holds_ball=False, arrows_loaded=15, hunt_cleared=True,
                    signals=replace(v.signals, passive_team='B', ball_status='carried'))
        contact = replace(contact, x=rng.uniform(54., 72.))
        b = replace(b, tracks=(contact, b.tracks[-1]))
        intent, record = C.decide(v, b)
        return max(row[3] for row in record['options']), signature(intent), 'selected action'
    if name == 'touch':
        velocity = IND.delivery_velocity((28., 0., 3.), value, rng.uniform(-1., 1.))
        return velocity[2], velocity, 'release vector'
    if name == 'agility':
        aim = IND.movement_aim(v.x, v.y, (92., 58. + rng.random()), value)
        return R.braking(value), aim, 'motor aim'
    maps = {
        'speed': R.speed_mps, 'acceleration': R.acceleration, 'jump': lambda r: 1.3*r,
        'throw_power': R.max_throw_speed, 'throw_accuracy': R.throw_error_base_deg,
        'ball_handling': lambda r: round(250 * (1.35 - .5*r)),
    }
    if name in maps:
        return maps[name](value), None, 'mapped quantity only'
    return None, None, 'scenario not measured'


def sweep():
    retired = set(P.ALIASES)
    names = sorted((set(R.RATINGS) | set(R.INERT_RATINGS) | set(P.NEW_RATINGS)
                    | {'acceleration'}) - retired)
    output = {}
    for name in names:
        reference = [probe(name, .70, seed) for seed in SEEDS]
        output[name] = []
        for level in LEVELS:
            cases = [probe(name, level, seed) for seed in SEEDS]
            values = [case[0] for case in cases if case[0] is not None]
            outcomes = [c[1] != r[1] for c, r in zip(cases, reference) if c[1] is not None]
            output[name].append(dict(level=level, seeds=len(cases), metric_mean=mean(values) if values else None,
                                     changed=sum(outcomes) if outcomes else None, compared=len(outcomes),
                                     scope=cases[0][2], trials=cases))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, required=True)
    parser.add_argument('--match', choices=('on', 'off'))
    parser.add_argument('--roster', choices=('real', 'neutral-real', 'control'), default='real')
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--max-steps', type=int)
    args = parser.parse_args()
    data = match_case(args.seed, args.match, args.roster, args.max_steps) if args.match else sweep()
    args.out.write_text(json.dumps(data, sort_keys=True, indent=None if not args.match else 2) + '\n')


if __name__ == '__main__':
    main()
