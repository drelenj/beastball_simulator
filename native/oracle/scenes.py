"""Author a true-state starting position with per-athlete observation overrides."""
from dataclasses import replace
import json
from pathlib import Path

from native.roster import load_rows
from native.rulebook.config import RulebookConfigV3

from .matches import match_build
from .snapshot import Build

SCHEMA = 'oracle-scene/1'
PLAYER_FIELDS = frozenset(('x', 'y', 'z', 'vx', 'vy', 'vz', 'facing', 'target',
                           'posture', 'active', 'fatigue', 'freeze_until', 'immune_until',
                           'minor_count', 'major_count', 'exclusion_ms'))
STATE_FIELDS = frozenset(('now', 'period', 'live_ms', 'dead_ms', 'game_ms', 'possession_ms',
                          'score', 'ends', 'owner', 'tackle_count', 'opening_deadline',
                          'opening_contestants', 'opening_touched', 'opening_team'))
POSSESSION_FIELDS = frozenset(('pp', 'tc', 'dp_team', 'dp_holder', 'unc_team', 'unc_start',
                               'ball_status', 'last_toucher', 'passing', 'zone_start',
                               'zone_violated', 'carry_inside', 'contested'))


def assign(obj, updates, allowed):
    for key, value in updates.items():
        if key not in allowed or not hasattr(obj, key):
            raise ValueError(f'unsupported scene attribute {key!r}')
        if isinstance(getattr(obj, key), tuple):
            value = tuple(value)
        setattr(obj, key, value)


def scene(source):
    spec = json.loads(Path(source).read_text()) if isinstance(source, (str, Path)) else source
    if spec.get('schema') != SCHEMA:
        raise ValueError('unsupported scene format')
    seed = spec.get('seed', 1)
    if 'rosters' in spec:
        roster = {team: load_rows(spec['rosters'][team], team) for team in ('A', 'B')}
        build = Build(seed, RulebookConfigV3(
            roster_digests=tuple(roster[team].digest for team in ('A', 'B')),
            individuation='individuation/2'), roster)
    else:
        build = match_build(seed, roster=spec.get('roster', 'control'))
    driver = build.create()
    port = driver.port
    match, state, engine = port.m, port.m.s, port.m.e
    state.now = port.config.latency_ms
    assign(state, spec.get('state', {}), STATE_FIELDS)
    state.phase = port.types.Phase(spec.get('phase', 'live'))
    match.s.opening_deadline = state.opening_deadline if state.phase == port.types.Phase.OPENING else None
    engine.hunt_cleared = state.phase != port.types.Phase.OPENING
    for pid, data in spec.get('players', {}).items():
        assign(state.players[pid], data, PLAYER_FIELDS)
    if spec.get('restart'):
        data = spec['restart']
        if state.phase != port.types.Phase.DEAD:
            raise ValueError('an authored restart requires dead play')
        engine.award(data['team'], data['x'], data['y'], data.get('reason', 'oracle_scene'), normalize=False)
        if data.get('kind'):
            state.restart.kind = data['kind']
        assign(state.restart, {k: v for k, v in data.items() if k not in ('team', 'x', 'y', 'kind', 'reason', 'rules')},
               state.restart.__dataclass_fields__)
        state.restart.rs.update(data.get('rules', {}))
    else:
        state.restart = None
    if 'ball' in spec:
        ball = dict(spec['ball'])
        if 'mode' in ball:
            ball['mode'] = port.types.BallMode(ball['mode'])
        state.ball = port.types.Ball(**ball)
    if state.ball.carrier is not None:
        holder = state.players[state.ball.carrier]
        state.owner = state.owner or holder.team
        engine.follow_carrier()
        for coordinate in ('x','y','z'):
            if coordinate in spec.get('ball', {}):
                setattr(state.ball, coordinate, spec['ball'][coordinate])
    tracker = engine.possession
    engine.native_seen = len(engine.log)
    tracker.live = state.phase in (port.types.Phase.LIVE, port.types.Phase.OPENING, port.types.Phase.FLIGHT)
    tracker.now = state.now
    tracker.goal = dict(state.ends)
    tracker.ball_xy = (state.ball.x, state.ball.y)
    tracker.pp = state.owner
    engine.rb.possession = state.owner
    engine.rb.period = state.period
    if state.ball.carrier:
        tracker.tc = state.owner
        tracker.dp_team, tracker.dp_holder = state.owner, state.ball.carrier
        tracker.unc_team, tracker.unc_start = state.owner, state.now - tracker.cfg.direct_possession_threshold_ms
        tracker.ball_status = 'direct'
    assign(tracker, spec.get('possession', {}), POSSESSION_FIELDS)
    port.platform_motor(0)
    port.assert_invariants()

    beliefs = spec.get('beliefs', {'mode': 'perceived'})
    mode = beliefs.get('mode', 'perceived')
    if mode not in ('perceived', 'authored') or mode == 'perceived' and beliefs.get('athletes'):
        raise ValueError('belief overrides require authored mode')
    # The example clock starts at delivery. Sensor readings model the scene one
    # configured latency before that boundary and are available on its first turn.
    port.capture(state.now - port.config.latency_ms)
    driver.next_sense = state.now + port.config.sense_ms
    driver.last_live_at, driver.last_live_ms = state.now, state.live_ms
    if mode == 'authored':
        for pid, override in beliefs.get('athletes', {}).items():
            frame = port.frames[pid][-1]
            changes = override.get('tracks', {})
            known = {track.entity for track in frame.tracks}
            if changes.keys() - known:
                raise ValueError(f'{pid}: track override requires a perceived entity')
            tracks = tuple(replace(track, **changes.get(track.entity, {})) for track in frame.tracks)
            ball_course = frame.ball_course
            if 'ball_course' in override:
                ball_course = replace(ball_course, **override['ball_course']) if ball_course else None
            port.frames[pid][-1] = replace(frame, tracks=tracks, ball_course=ball_course)
    return build, driver
