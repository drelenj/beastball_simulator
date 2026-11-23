from dataclasses import replace
import math

import pytest

from native import cognition as C, cognition_rb3 as R3, cognition_v3 as V3
from native import individuation as I
from native.roster import load_rows, rb3_control_rosters, RosterError
from native.run import run_match
from .config import RulebookConfigV3
from .port import RulebookPort
from .test_rb312 import carrier_scene
from .test_rb311 import live, rb3, field


def rated(view, name, value):
    return replace(view, individual_ratings=((name, value),))


def pair(view, name):
    return (rated(view, name, 0.), rated(view, name, 1.))


def config(rosters, enabled=True):
    return RulebookConfigV3(roster_digests=tuple(rosters[s].digest for s in ('A', 'B')),
                            individuation=I.VERSION if enabled else 'off')


@pytest.mark.parametrize('name', I.DRAFT_RATINGS)
def test_draft_rating_validation_and_port_propagation(name):
    rosters = rb3_control_rosters()
    rows = [dict(id=a.source_id, role=a.role, **dict(a.values)) for a in rosters['A'].athletes]
    rows[0][name] = 1.1
    with pytest.raises(RosterError, match=name):
        load_rows(rows, 'A')
    rows[0][name] = .93
    rosters['A'] = load_rows(rows, 'A')
    port = RulebookPort(1, config(rosters), rosters=rosters)
    pid = 'A:' + rows[0]['id']
    port.capture(port.m.s.now)
    view, _ = port.view(pid, port.m.s.now + 200)
    assert dict(view.individual_ratings)[name] == .93
    assert sum(v != .70 for v in dict(view.individual_ratings).values()) == 1


def test_sensor_focus_and_reaction_live_port():
    rosters = rb3_control_rosters()
    p = RulebookPort(1, config(rosters), rosters=rosters)
    s = p.m.s
    me = next(q for q in s.players.values() if q.active and q.role == 'field')
    for q in s.players.values():
        q.active = q is me
    me.x, me.y, me.facing = 50., 50., (1., 0.)
    s.ball.carrier = None
    s.ball.x, s.ball.y, s.ball.z = 45., 65., 2.
    me.native_individual['vision'] = 0.
    p.capture(0)
    low = p.frames[me.id][-1]
    me.native_individual['vision'] = 1.
    p.capture(200)
    high = p.frames[me.id][-1]
    assert low.ball_course is None and high.ball_course is not None
    me.native_individual['reaction'] = 0.
    slow = p.decision_interval_ms(me.id)
    me.native_individual['reaction'] = 1.
    assert p.decision_interval_ms(me.id) < slow
    me.native_individual['focus'] = 1.
    view, _ = p.view(me.id, 1800)
    assert any(t.entity == C.BALL for t in view.tracks)
    me.native_individual['focus'] = 0.
    view, _ = p.view(me.id, 1800)
    assert not view.tracks


def test_motor_touch_and_archer_perturbations_preserve_release_magnitude():
    velocity = (22., 7., 2.)
    assert abs(I.delivery_velocity(velocity, 1., 1.)[2] - 2.) < 1e-12
    low = I.delivery_velocity(velocity, 0., 1.)
    assert low[2] > velocity[2]
    assert math.hypot(*low) == pytest.approx(math.hypot(*velocity))
    assert math.hypot(*I.yaw_velocity(velocity, 1.)) == pytest.approx(math.hypot(*velocity))
    target = (20., 10.)
    assert I.movement_aim(10., 8., target, 1.) == target
    assert I.movement_aim(10., 8., target, 0.) != target


def scene():
    v, tracks, sg = carrier_scene(me=(83., 50.), mates=((72., 63.), (86., 62.)))
    sig = replace(v.signals, phase='live', possession_ms=2000, passive_team=v.team)
    v = replace(v, attack_sign=1, own_goal_x=0., restart=None, signals=sig)
    return v, C.BeliefState('b', v.observation_id, tracks)


@pytest.mark.parametrize('name,kind', [('instinct', 'shoot'), ('finishing', 'shoot'),
                                        ('playmaking', 'pass'), ('anticipation', 'pass')])
def test_existing_carrier_options_change_with_one_rating(name, kind):
    view, belief = scene()
    belief = replace(belief, tracks=tuple(replace(t, vx=5., vy=2.) for t in belief.tracks))
    options = [[row for row in C._base_decide(v, belief)[1]['options'] if row[0] == kind]
               for v in pair(view, name)]
    assert all(options) and options[0] != options[1]


def test_keeper_position_uses_delivered_course_and_own_rating_only():
    from b1.emergence_intents import BallCourseBelief
    view, belief = scene()
    course = BallCourseBelief('ball', view.delivered_ms, view.delivered_ms, 42., 64., 1., 0., 0., 0.)
    view = replace(view, role='keeper', holds_ball=False)
    belief = replace(belief, ball_course=course)
    targets = [C.decide(v, belief)[0].auxiliary.target for v in pair(view, 'goalkeeping')]
    assert targets[0] != targets[1]
    assert all(C.decide(v, replace(belief, ball_course=None))[0].auxiliary.kind == 'hold'
               for v in pair(view, 'goalkeeping'))


def test_contact_choices_depend_on_own_duel_rating():
    view, belief = scene()
    intent = C.ActionIntent('i', 'd', view.athlete, 'carry', None, (93., 50.), None, None, view.delivered_ms)
    held = replace(view, own_held=1, own_balance_load=V3.BRACE_LOAD)
    assert [V3.carrier_contact(v, belief, intent, {})[0].contact for v in pair(held, 'carrier_duel')] == ['brace', 'run_through']
    t = C.Track('B:1', 'B', 'field', view.x + V3.TACKLE_COMMIT_M, view.y, 0., 0., view.delivered_ms)
    record = {'believed_carrier': (t.entity, t.team)}
    assert [V3.defender_contact(v, replace(belief, tracks=(t,)), intent, record)[0].contact
            for v in pair(view, 'defender_duel')] == ['wrap', 'takedown']


def test_determinism_and_self_only_view():
    rosters = rb3_control_rosters()
    cfg = config(rosters)
    hashes = []
    for _ in range(2):
        result, port = run_match(1, cfg, rosters=rosters, max_steps=500, port_factory=RulebookPort)
        hashes.append((result['trace_hash'], result['state_hash']))
    assert hashes[0] == hashes[1]
    me, other, *_ = port.active_ids()
    now = port.m.s.now
    before, _ = port.view(me, now)
    port.m.s.players[other].native_individual['finishing'] = 1.
    after, _ = port.view(me, now)
    assert before.individual_ratings == after.individual_ratings
    assert before.tracks == after.tracks
    assert before.body_height == after.body_height


def test_clarity_changes_only_vertical_sample_error():
    from random import Random
    rosters = rb3_control_rosters()
    p = RulebookPort(1, config(rosters), rosters=rosters)
    s = p.m.s
    me = next(q for q in s.players.values() if q.active and q.role == 'field')
    for q in s.players.values():
        q.active = q is me
    me.x, me.y, me.facing = 50., 50., (1., 0.)
    s.ball.carrier = None
    s.ball.x, s.ball.y, s.ball.z = 60., 50., 2.
    samples = []
    for value in (0., 1.):
        me.native_individual['clarity'] = value
        p.streams[me.id] = Random(7)
        p.capture(0)
        samples.append(p.frames[me.id][-1].ball_course)
    low, high = samples
    assert (low.x, low.y) == (high.x, high.y)
    assert abs(high.z - 2.) < abs(low.z - 2.)


@pytest.mark.parametrize('z,name', [(2., 'in_air_ball_pursuit'), (.11, 'live_ball_pursuit')])
def test_pursuit_uses_only_matching_ball_context(z, name):
    from b1.emergence_intents import BallCourseBelief
    view, belief = scene()
    view = replace(view, holds_ball=False)
    ball = C.Track(C.BALL, 'ball', 'ball', view.x - 6., view.y, 0., 0., view.delivered_ms)
    course = BallCourseBelief('course', view.delivered_ms, view.delivered_ms, ball.x, ball.y, z, 0., 0., 0.)
    belief = replace(belief, tracks=(ball,), ball_course=course)
    def value(v):
        return next(row[3] for row in C._base_decide(v, belief)[1]['options'] if row[0] == 'pursue')
    assert value(rated(view, name, 0.)) < value(rated(view, name, 1.))
    other = 'live_ball_pursuit' if name == 'in_air_ball_pursuit' else 'in_air_ball_pursuit'
    assert value(rated(view, other, 0.)) == value(rated(view, other, 1.))


def test_marking_and_judgment_influence_different_options():
    view, belief = scene()
    view = replace(view, x=55., holds_ball=False)
    ball = C.Track(C.BALL, 'ball', 'ball', 63., 52., 0., 0., view.delivered_ms)
    carrier = replace(ball, entity='B:0', role='field', team='B')
    teammate = replace(carrier, entity='B:1', x=70., y=60.)
    belief = replace(belief, tracks=(ball, carrier, teammate))
    def options(v, kind):
        return [row for row in C._base_decide(v, belief)[1]['options'] if row[0] == kind]
    assert options(rated(view, 'marking', 0.), 'mark') != options(rated(view, 'marking', 1.), 'mark')
    assert options(rated(view, 'judgment', 0.), 'press') != options(rated(view, 'judgment', 1.), 'press')
    assert options(rated(view, 'judgment', 0.), 'mark') == options(rated(view, 'judgment', 1.), 'mark')


def test_zone_reads_change_exit_decision_without_changing_zone_limit():
    p = rb3()
    s, _, _, _ = live(p)
    me = field(s, 'A')[3]
    p.capture(s.now)
    v, b = p.view(me.id, s.now + 300)
    v = replace(v, restart=None, pending_command_id=None, holds_ball=False, x=92., y=50.,
                signals=replace(v.signals, passive_team='A', phase='live',
                                pass_call=('A:1', me.id, 95., 50.)))
    keep = C.ActionIntent('i', 'd', me.id, 'receive', 'A:1', (95., 50.), None, None, v.delivered_ms)
    travel = R3.time_to_cover(v, 12. + R3.ARC_INSET_M)
    v = replace(v, zone_elapsed_ms=round(5000 - (travel + 1.5) * 1000))
    assert [R3.zone_behavior(opt, b, keep, {})[0].kind
            for opt in pair(v, 'zone_reads')] == ['receive', 'position']


def test_workbook_independent_technical_columns_and_fallbacks():
    import io
    from openpyxl import load_workbook
    from native.nbl_roster import load_nbl_workbook
    from .test_rb322 import TEAMS, _workbook

    wb = load_workbook(io.BytesIO(_workbook()))
    sheet = wb['All 712 Players']
    for index, (label, value) in enumerate((('Contact Resistance (rating)', 41),
                                            ('Finishing (rating)', 83)), sheet.max_column + 1):
        sheet.cell(1, index, label)
        for row in range(2, sheet.max_row + 1):
            sheet.cell(row, index, value)
    buffer = io.BytesIO()
    wb.save(buffer)
    for roster in load_nbl_workbook(buffer, TEAMS, technical='explicit').values():
        for athlete in roster.athletes:
            assert athlete.get('contact_resistance') == .41 != athlete.get('balance')
            assert athlete.get('finishing') == .83
            assert athlete.get('vision') == .70
            assert dict(athlete.sources)['vision'] == '0.70 default'
            assert dict(athlete.sources)['tackling'] == 'Opening-day OVR fallback'


def test_archery_accuracy_changes_actual_release_vector():
    from .test_rb34 import live as archer_scene
    shots = []
    for accuracy in (0., 1.):
        rosters = rb3_control_rosters()
        port = RulebookPort(1, config(rosters), rosters=rosters)
        s, _, archer, target = archer_scene(port)
        port.m.s.players[archer].a.archery_accuracy = accuracy
        p = s.players[archer]
        draw = C.ActionIntent('draw', 'd', archer, 'draw_release', target.id,
                              (target.x, target.y), None, None, s.now)
        release = replace(draw, kind='release_arrow')
        command = C.MotorCommand('command', draw, s.now, s.now, 'bow')
        port.pending[archer] = dict(cmd=command, due=s.now, period=s.period, release_intent=release)
        port.archer_motor()
        assert s.arrows
        arrow = s.arrows[-1]
        shots.append((arrow.vx, arrow.vy, arrow.vz))
    assert shots[0] != shots[1]
    assert [math.hypot(*v) for v in shots] == pytest.approx([250., 250.])


def test_existing_physics_fatigue_reads_stamina_in_experiment_only():
    losses = []
    for enabled in (False, True):
        after = []
        for stamina in (0., 1.):
            rosters = rb3_control_rosters()
            port = RulebookPort(1, config(rosters, enabled), rosters=rosters)
            s, _, _, _ = live(port)
            runner = next(q for q in s.players.values() if q.active and q.role == 'field')
            for q in s.players.values():
                q.active = q is runner
            runner.x, runner.y, runner.vx, runner.vy = 20., 50., 15., 0.
            runner.a.endurance = stamina
            runner.target = (80., 50.)
            port.m.c3_move(100, {runner.id: (80., 50.)})
            after.append(runner.fatigue)
        losses.append(after)
    assert losses[0] == [1., 1.]
    assert losses[1][0] < losses[1][1] < 1.


def test_experimental_fingerprint_has_active_draft_and_excludes_staged_injury():
    def fingerprints(name, value):
        rosters = rb3_control_rosters()
        rows = [dict(id=a.source_id, role=a.role, **dict(a.values))
                for a in rosters['A'].athletes]
        rows[0][name] = value
        rosters['A'] = load_rows(rows, 'A')
        cfg = config(rosters)
        return cfg.digest, RulebookPort(1, cfg, rosters=rosters).behavior_digest

    assert all(a != b for a, b in zip(fingerprints('vision', 0.), fingerprints('vision', 1.)))
    a, b = fingerprints('durability', 0.), fingerprints('durability', 1.)
    assert a[0] != b[0] and a[1] == b[1]


def test_no_kicking_action_or_active_kicking_rating():
    rosters = rb3_control_rosters()
    port = RulebookPort(1, config(rosters), rosters=rosters)
    s, _, _, _ = live(port)
    p = next(q for q in s.players.values() if q.active and q.role == 'field')
    intent = C.ActionIntent('kick', 'd', p.id, 'kick', None, (50., 50.), None, None, s.now)
    assert p.a.kicking == 0.
    assert port.submit(intent)['reason'] == 'unknown_kind'
    assert p.id not in port.pending
