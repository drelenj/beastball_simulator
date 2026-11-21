"""Read-only native-rb/3 labs. Run from the repository root as a module."""
import json
import math
from types import SimpleNamespace

from b1.emergence_intents import KeeperIntent
from native.roster import acceleration, speed_mps
from native.rulebook.ball_material import params, path
from native.rulebook.scoring_audit import lab, new_flight


def keeper_trial(distance, lateral, height, awareness, force_intent):
    port, keeper = lab('keeper')
    match, state = port.m, port.m.s
    start = state.now
    keeper.a.awareness = awareness
    depth = max(match.assume['keeper_depth_min_m'],
                min(match.assume['keeper_depth_max_m'],
                    distance * match.assume['keeper_depth_frac']))
    keeper.x = depth
    keeper.target = depth, keeper.y
    origin = distance, 50., keeper.hand_height
    velocity, *_ = port.geom.launch_for(origin, (0., 50. + lateral, height), 58.)
    ball = new_flight(port, origin, velocity)
    course = path((*origin, *velocity), params(port.config), ball.radius, .4, .001)
    cross = match.c4c_threat(keeper, course)
    assert cross
    at_depth = min(course, key=lambda point: abs(point[1] - depth))
    if force_intent:
        # Perfect release-time perception, with the normal engine reaction gate.
        intent = KeeperIntent('forced/keeper', keeper.id, 'save', start, 'forced',
                              course=tuple(course[:cross[0] + 1]))
        port.keeper_intents[keeper.id] = SimpleNamespace(auxiliary=intent)
        keeper.native_keeper_course_ms = start
    max_travel = max_lift = 0.
    dive = False
    event = None
    while state.now - start < 350:
        targets = {}
        port.keeper_motor(targets)
        old = {keeper.id: (keeper.x, keeper.y, keeper.z)}
        match.c3_move(1, targets)
        max_travel = max(max_travel, math.hypot(keeper.x - depth, keeper.y - 50.))
        max_lift = max(max_lift, keeper.z)
        dive |= bool(getattr(keeper, 'c4c_launch', None))
        events = match.advance_ball(1, old)
        if events:
            event = min(events, key=lambda item: (item.at, item.kind != 'goal'))
            break
        state.now += 1
    demand = (abs(at_depth[2] - 50.), abs(at_depth[3] - .62 * keeper.a.height))
    return dict(distance_m=distance, launch_speed_mps=math.hypot(*velocity),
                aim_m=[lateral, height], awareness=awareness,
                release_time_intent=force_intent,
                depth_m=depth, depth_ms=1000*at_depth[0], plane_ms=1000*cross[1],
                reaction_ms=keeper.native_keeper_flight[2] - start,
                lateral_vertical_demand_m=demand, move_m=max_travel, lift_m=max_lift,
                dive=dive, hand_height_m=.62*keeper.a.height,
                hand_radius_m=match.c4c_reach(keeper), sensor_latency_ms=port.config.latency_ms,
                outcome=event.kind if event else None,
                contact=event.data.get('c4c_kind') if event else None,
                control=event.data.get('secure') if event else None,
                event_ms=state.now - start + event.at if event else None)


def speed_trial(rating, carry):
    port, runner = lab('field')
    match = port.m
    runner.a.maximum_speed = speed_mps(rating)
    runner.a.acceleration = acceleration(rating)
    match.s.ball.carrier = runner.id if carry else None
    samples = {}
    for tick in range(1, 101):
        # Keep the real motor out of its approach/braking zone over virtual runway.
        runner.x, runner.y = 5., 50.
        runner.target = 105., 50.
        match.c3_move(100, {})
        match.s.now += 100
        if tick in (10, 20, 30, 40, 100):
            samples[tick // 10] = runner.speed
    return dict(rating=rating, carry=carry, canon_mps=44.704 * rating,
                motor_cap_mps=match.c3_cache[runner.id][0], at_seconds_mps=samples)


if __name__ == '__main__':
    print(json.dumps(dict(
        keeper=[keeper_trial(d, y, z, awareness, intent)
                for d in (10., 12., 15.) for y, z in ((0., 1.5), (2.4, .4), (2.4, 2.))
                for awareness in (.5, .7, .9) for intent in (False, True)],
        speed=[speed_trial(r, carry) for r in (0., .4, .6, .7, .8, 1.)
               for carry in (False, True)],
    ), indent=2))
