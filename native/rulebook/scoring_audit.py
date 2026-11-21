"""Forced scoring-physics cases: python -m native.rulebook.scoring_audit."""
import argparse
import gzip
import json
import math
import random
from collections import Counter
from pathlib import Path

from .config import RulebookConfigV3
from .port import RulebookPort
from native.roster import rb3_control_rosters
from b1.emergence_intents import BallCourseBelief, KeeperIntent, forecast_course
from types import SimpleNamespace


def lab(role, rosters=None):
    rosters = rosters or rb3_control_rosters()
    cfg = RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A', 'B')))
    port = RulebookPort(1, cfg, rosters=rosters)
    state = port.m.s
    state.now = 60000
    state.phase = port.types.Phase.LIVE
    state.restart = None
    player = next(p for p in state.players.values()
                  if p.active and p.role == role and state.ends[p.team] == 0)
    for p in state.players.values():
        p.active = p is player
    player.x, player.y, player.z = 3., 50., 0.
    player.vx = player.vy = player.vz = 0.
    player.target = (player.x, player.y)
    player.next_action = player.next_decision = 0
    return port, player


def new_flight(port, origin, velocity):
    state = port.m.s
    state.ball = port.types.Ball(
        mode=port.types.BallMode.SHOT, x=origin[0], y=origin[1], z=origin[2],
        vx=velocity[0], vy=velocity[1], vz=velocity[2],
        release_time=state.now, version=1, scoring=True)
    port.m.rng['ball'] = random.Random(1)
    return state.ball


def keeper_case(awareness, offset, height, *, force_intent=False, rosters=None):
    port, keeper = lab('keeper', rosters)
    match = port.m
    state = match.s
    keeper.a.awareness = awareness
    origin = (12., 50., keeper.hand_height)
    velocity, *_ = port.geom.launch_for(origin, (0., 50. + offset, height), 58., 9.81, .015)
    ball = new_flight(port, origin, velocity)
    tick = state.now
    course = forecast_course(BallCourseBelief('forced', tick, tick, *origin, *velocity),
                             9.81, .015, horizon_s=.24, step_s=.001)
    cross = match.c4c_threat(keeper, course)
    course = tuple(point for point in course if point[0] <= cross[1])
    intent = KeeperIntent('forced/keeper', keeper.id, 'save', tick, 'forced', course=course)
    if force_intent:
        port.keeper_intents[keeper.id] = SimpleNamespace(auxiliary=intent)
        keeper.native_keeper_course_ms = tick
    # Normal live decisions receive flight information after sensor latency.
    # The forced intent is an explicit zero-latency motor stress test.
    maximum_lateral, maximum_vertical, launched = 0., 0., False
    event = None
    while state.now - tick < 260:
        targets = {}
        port.keeper_motor(targets)
        old = {keeper.id: (keeper.x, keeper.y, keeper.z)}
        match.c3_move(1, targets)
        maximum_lateral = max(maximum_lateral, abs(keeper.y - 50.))
        maximum_vertical = max(maximum_vertical, keeper.z)
        launched |= bool(getattr(keeper, 'c4c_launch', None))
        events = match.advance_ball(1, old)
        if events:
            event = min(events, key=lambda ev: (ev.at, ev.kind != 'goal'))
            break
        state.now += 1
    at_depth = min(course, key=lambda point: abs(point[1] - 3.))
    return dict(awareness=awareness, aim=[offset, height], forced_intent=force_intent,
                keeper_id=keeper.id, body_height_m=keeper.a.height, arm_reach_m=keeper.a.reach,
                standing_reach_m=keeper.a.standing_reach_m,
                latency_ms=port.config.latency_ms, depth_ms=1000 * at_depth[0],
                plane_ms=None if cross is None else 1000 * cross[1],
                reaction_ms=200 * (1.3 - .6 * awareness),
                lateral_demand_m=abs(at_depth[2] - 50.),
                vertical_demand_m=abs(at_depth[3] - .62 * keeper.a.height),
                hand_radius_m=.9 * keeper.a.reach, hand_height_m=.62 * keeper.a.height,
                displaced_y_m=maximum_lateral, lifted_m=maximum_vertical, launched=launched,
                outcome=event.kind if event else None,
                contact_kind=event.data.get('c4c_kind') if event else None,
                at_ms=state.now - tick + event.at if event else None,
                flight_speed=math.hypot(*velocity), radius=ball.radius)


def catch_case(role, speed, offset, *, random_seed=1, age_ms=0, hands=None, rosters=None):
    port, player = lab(role, rosters)
    match = port.m
    player.x = 20.
    origin = (20. - speed * .065, 50. + offset, player.hand_height)
    ball = new_flight(port, origin, (speed, 0., 0.))
    match.rng['ball'] = random.Random(random_seed)
    match.seen_version, match.seen_from = ball.version, match.s.now - age_ms
    if hands is not None:
        match.hands_set[player.id] = hands
    events = match.advance_ball(100, {player.id: (player.x, player.y, player.z)})
    return [(ev.kind, ev.at, ev.data) for ev in events]


def body_block():
    port, keeper = lab('keeper')
    match = port.m
    keeper.x = 20.
    ball = new_flight(port, (16.23, 50., keeper.hand_height), (58., 0., 0.))
    match.seen_version, match.seen_from = ball.version, match.s.now
    match.hands_set[keeper.id] = match.s.now + 100  # no sampled hands readiness in this interval
    event, = match.advance_ball(100, {keeper.id: (keeper.x, keeper.y, keeper.z)})
    match.s.now += event.at
    assert match.e.c1_commit(event)
    return dict(event=event.kind, at_ms=event.at, kind=event.data['c4c_kind'],
                outgoing=[ball.vx, ball.vy, ball.vz], carrier=ball.carrier, mode=ball.mode.value)


def speeds(carry):
    port, runner = lab('field')
    match = port.m
    runner.x, runner.y = 5., 50.
    match.s.ball.carrier = runner.id if carry else None
    # Virtual straight runway, with the normal C3 motor and no opponents.
    # Rebase x after each interval so the physical field clamp stays out of it.
    samples = []
    for tick in range(1, 51):
        runner.target = (105., 50.)
        match.c3_move(100, {})
        match.s.now += 100
        runner.x = 5.
        if tick in (10, 20, 30, 50):
            samples.append(runner.speed)
    return dict(carry=carry, maximum=runner.a.maximum_speed, acceleration=runner.a.acceleration,
                cap=match.c3_cache[runner.id][0], speeds=samples)


def match_metrics(root, cases=None):
    from native.nbl_roster import load_canon_nbl

    real_rosters = load_canon_nbl(('Garvian Guardians', 'Ala Apex'))
    rows = []
    for block, seed in cases or [('real', 1), ('real', 3), ('real', 5), ('control', 1)]:
        name = f'{block}-seed{seed:02d}'
        path = Path(root) / block / f'raw-{name}.json'
        run = json.loads(path.with_name(f'{name}.json').read_text())
        if not path.exists():
            path = path.with_suffix('.json.gz')
        row = {key: run.get(key) for key in ('status', 'score', 'trace_hash', 'state_hash', 'config_digest')}
        rows.append(dict(case=name, raw_log=str(path), **row))
        if not path.exists():
            continue
        if path.suffix == '.gz':
            with gzip.open(path, 'rt') as stream:
                log = json.load(stream)['log']
        else:
            log = json.loads(path.read_text())['log']
        shots, passes = Counter(), Counter()
        near_interceptions = 0
        keeper_ids = ({f'{team}:{slot}' for team in ('A', 'B') for slot in (18, 19)}
                      if block == 'control' else
                      {f'{team}:{player.source_id}' for team, roster in real_rosters.items()
                       for player in roster.athletes if player.role == 'keeper'})
        # A substitute's effective role may differ from his listed role
        # under the RB/3 emergency specialist cover rule.
        for event in log:
            if event['event'] == 'rb_substitution':
                ruling = event['data']['ruling']
                if ruling.get('role') == 'keeper':
                    keeper_ids.add(ruling['incoming'])
        for index, event in enumerate(log):
            data = event['data']
            if event['event'] != 'release' or data.get('kind') not in ('pass', 'shot'):
                continue
            team = data['player'].split(':')[0]
            shot = data['kind'] == 'shot'
            outcome = 'other'
            for position in range(index + 1, len(log)):
                next_event = log[position]
                kind, info = next_event['event'], next_event['data']
                if kind == 'control':
                    athlete = info['player']
                    if athlete.split(':')[0] != team:
                        outcome = 'keeper' if shot and athlete in keeper_ids else 'opponent'
                        if not shot and math.dist(event['ball'][:2], next_event['ball'][:2]) <= 3:
                            near_interceptions += 1
                    break
                if kind == 'keeper_contact' and shot:
                    if info['player'].split(':')[0] != team:
                        outcome = 'keeper'
                    break
                if kind == 'goal':
                    if shot:
                        outcome = 'scored'
                    break
                if kind in ('boundary', 'restart_awarded', 'period_end', 'final', 'release', 'restart_release'):
                    break
            (shots if shot else passes)[outcome] += 1
        rows[-1].update(shots=dict(shots), passes=dict(passes),
                        interceptions_within_3m=near_interceptions,
                        tackles=sum(event['event'] == 'tackle_count' for event in log),
                        carries=run['metrics']['carry_attempts'],
                        possessions={team: values['count'] for team, values in
                                     run['metrics']['possessions'].items()})
    return rows


def legacy_hashes():
    from native.config import NativeConfig, NativeConfigV3
    from native.run import run_match
    from .config import RulebookConfig

    profiles = [(NativeConfig(), {}), (NativeConfigV3(), {}),
                (RulebookConfig(), {'port_factory': RulebookPort})]
    for cfg, kwargs in profiles:
        for seed in (1, 3):
            result, _ = run_match(seed, cfg, max_steps=3000, **kwargs)
            print(cfg.version, seed, *(result[key] for key in (
                'trace_hash', 'state_hash', 'config_digest')), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--real', action='store_true', help='use the NBL rosters in the keeper lab')
    parser.add_argument('--matches', nargs='+', metavar='DIR', help='measure completed runs from raw logs')
    parser.add_argument('--legacy', action='store_true', help='emit six 3000-step legacy hash guards')
    args = parser.parse_args()
    if args.legacy:
        legacy_hashes()
        return
    if args.matches:
        print(json.dumps({root: match_metrics(root) for root in args.matches}, indent=2))
        return
    rosters = None
    if args.real:
        from native.nbl_roster import load_canon_nbl
        rosters = load_canon_nbl(('Garvian Guardians', 'Ala Apex'))
    cases = [keeper_case(a, y, z, force_intent=forced, rosters=rosters)
             for forced in (False, True) for a in (.5, .7, .9)
             for y, z in ((0., 1.5), (2.4, .4), (2.4, 2.))]
    catches = [dict(role=role, speed=speed, offset=offset, seed=seed,
                    events=catch_case(role, speed, offset, random_seed=seed))
               for role in ('field', 'keeper') for speed in (22., 58.)
               for offset in (0., .8) for seed in (1, 2, 3)]
    interceptions = [dict(speed=speed, offset=offset, seed=seed,
                          events=catch_case('field', speed, offset, random_seed=seed, rosters=rosters))
                     for speed in (22., 58.) for offset in (1., 2., 3.) for seed in (1, 2, 3)]
    print(json.dumps(dict(keeper=cases, catches=catches, interceptions=interceptions, body_block=body_block(),
                          running=[speeds(False), speeds(True)]), indent=2))


if __name__ == '__main__':
    main()
