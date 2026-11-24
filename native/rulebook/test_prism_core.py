"""Boundary cases for PRISM CORE and its paired decision noise."""
from collections import Counter
from dataclasses import replace
import json
from math import hypot
from statistics import mean

import pytest

from native import cognition as C
from native import prism_core as CORE
from native import prism_lab
from native.prism_motion import maneuver, stretch_maximum
from native.roster import load_rows, rb3_control_rosters
from .config import RulebookConfigV3
from .port import RulebookPort


@pytest.fixture
def core_port():
    rs = rb3_control_rosters()
    cfg = RulebookConfigV3(roster_digests=tuple(rs[t].digest for t in ('A','B')),
                           individuation=CORE.VERSION)
    p = RulebookPort(1, cfg, rosters=rs)
    s = p.m.s
    actor = next(q for q in s.players.values() if q.active and q.team == 'A' and q.role == 'field')
    s.now = 60_000
    s.phase = p.types.Phase.LIVE
    s.owner = 'A'
    s.restart = None
    actor.x, actor.y = 50., 50.
    actor.vx, actor.vy = 5., 0.
    s.ball = p.types.Ball(mode=p.types.BallMode.CONTROLLED,
                          x=actor.x, y=actor.y, z=actor.hand_height,
                          last_touch='A', carrier=actor.id)
    return p, actor


def intent(p, actor, kind='pass', **kwargs):
    return C.ActionIntent('intent','decision',actor.id,kind,None,(65.,50.),None,None,
                          p.m.s.now,period=p.m.s.period,**kwargs)


def test_error_shrinks_without_changing_hand_set_values():
    for owner in ('playmaking', 'defending', 'zone_coverage', 'goalkeeping', 'disruption', 'passing',
                  'finishing', 'takedown', 'evasion', 'in_air_ball_pursuit', 'live_ball_pursuit'):
        low = []
        high = []
        for seed in range(1,201):
            view, b, _, _ = prism_lab.scene(seed, owner, .4)
            view = replace(view, core_entropy=str(seed))
            base = C.ActionIntent('i','d','A0','scan',None,None,None,None,view.delivered_ms)
            options = (CORE.Option(base, 1., owner, 'a'), CORE.Option(base, 1., owner, 'b'))
            for rating, accumulator in ((.4,low),(1.,high)):
                menu = CORE.Menu(replace(view, registry_ratings=((owner,rating),)))
                menu.choose(owner, options)
                assert tuple(row[2] for row in menu.records[0]['options']) == (1.,1.)
                accumulator.extend(row[3]-row[2] for row in menu.records[0]['options'])
        assert max(map(abs,high)) == 0.
        assert abs(mean(low)) < .05
        assert max(map(abs,low)) <= CORE.ERROR_WIDTH*.6


def test_core_view_round_trips_and_contains_menu_record():
    v, b, _, _ = prism_lab.scene(1, 'playmaking', .7)
    v = replace(v, core_entropy='1/A0/1000')
    round_trip = C.view_from_json(json.loads(json.dumps(C.view_to_json(v,b))))
    assert C.decide(v,b) == C.decide(*round_trip)
    _, record = C.decide(v,b)
    assert record['core_menus'][0]['stage'] == 'carrier'
    assert len({row[0] for row in record['core_menus'][0]['options']}) >= 3


def test_evasion_and_radar_do_not_change_physical_resistance_or_preparation():
    control = rb3_control_rosters()
    for value in (.4,1.):
        rosters = {team: load_rows([
            dict(athlete.values) | {'id':athlete.source_id,'role':athlete.role,
                                    'evasion':value,'awareness':value}
            for athlete in roster.athletes],team) for team,roster in control.items()}
        config = RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A','B')),
                                  individuation=CORE.VERSION)
        port = RulebookPort(1,config,rosters=rosters)
        actor = next(iter(port.m.s.players.values()))
        assert actor.native_registry['evasion'] == actor.native_registry['awareness'] == value
        assert actor.a.contact_resistance == actor.a.awareness == .7


def test_passing_wait_keeps_windup_duration_and_releases_at_due(core_port):
    p, actor = core_port
    kick = intent(p,actor,wait_ms=100,technique='loft',speed=30.,height=2.4)
    cmd = p.submit(kick)['command']
    assert cmd.start_ms == p.m.s.now + 100
    assert cmd.release_ms - cmd.start_ms == p.own_release_ms(actor)
    assert 'A' not in p.calls
    p.m.s.now = cmd.start_ms
    p.ball_motor()
    assert p.calls['A'][0] == actor.id
    assert p.m.s.ball.carrier == actor.id
    p.m.s.now = cmd.release_ms
    p.ball_motor()
    assert p.m.s.ball.carrier is None


def test_wait_cannot_exceed_reaction_interval_and_is_interrupted_on_lost_ball(core_port):
    p, actor = core_port
    assert p.submit(intent(p,actor,wait_ms=999))['reason'] == 'outside_reaction_interval'
    assert p.submit(intent(p,actor,wait_ms=100))['status'] == 'accepted'
    p.m.s.ball.carrier = None
    p.ball_motor()
    assert actor.id not in p.pending
    assert p.outcomes[-1].status == 'interrupted'


@pytest.mark.parametrize('technique', ('juke', 'spin', 'hurdle'))
def test_maneuver_execution_depends_on_rating(core_port, technique):
    port, actor = core_port
    results = []
    for ability in (.4,1.):
        actor.native_registry[technique] = ability
        actor.posture = 'upright'
        actor.vx, actor.vy, actor.vz = 5.,0.,0.
        plan = replace(intent(port,actor,kind='carry',technique=technique),aim=(55.,54.))
        aim = maneuver(actor,plan,port.m.assume['gravity'])
        results.append((aim, hypot(actor.vx, actor.vy), actor.vz))
    assert results[0] != results[1]


def test_existing_stiff_arm_reads_technique_rating(core_port):
    p, carrier = core_port
    target = next(t for t in p.m.s.players.values() if t.active and t.team == 'B' and t.role == 'field')
    target.x, target.y = carrier.x + .8, carrier.y
    amounts = []
    for level in (.4,1.):
        target.vx = target.vy = 0.
        carrier.native_registry['stiff_arm'] = level
        p.rb318.stiff_arm(carrier,target)
        amounts.append(target.vx)
    assert 0 < amounts[0] < amounts[1]


def test_truck_rating_changes_borderline_hold(core_port):
    p, carrier = core_port
    target = next(t for t in p.m.s.players.values() if t.active and t.team == 'B' and t.role == 'field')
    target.x, target.y = carrier.x + .8, carrier.y
    carrier.facing = (1.,0.)
    p.rb318.opponent = lambda *_: True  # isolate impulse after engine legality
    outcomes = []
    for level in (.4,1.):
        carrier.native_registry['truck'] = level
        action = replace(intent(p,carrier,kind='truck',technique='truck'),
                         intent_id=f'truck-{level}',target=target.id)
        carrier.native_intent = action
        p.rb318.requests[carrier.id] = (action,p.m.s.ball.version)
        opposing = 5.1 * carrier.a.mass / target.a.mass
        outcomes.append(p.rb318.truck(carrier,carrier,target,5.5,opposing,0.,p.m.s.now))
    assert outcomes == [False,True]


def test_stretch_consumes_ball_handling_and_no_stretch_rating(core_port):
    _, actor = core_port
    actor.a.ball_handling = .4
    short = stretch_maximum(actor,.9)
    actor.a.ball_handling = 1.
    assert short < stretch_maximum(actor,.9)
    assert 'stretch' not in actor.native_registry


def test_defending_compares_man_with_area_by_observed_situation():
    v, b, t, _ = prism_lab.scene(1,'defending',.7)
    v = replace(v, holds_ball=False, core_entropy='situation', x=7.,y=50.,
                signals=replace(v.signals,passive_team='B'))
    rival = replace(t,x=27.,y=50.)
    ball = replace(b.tracks[-1],x=27.,y=50.)
    belief = replace(b, tracks=(rival,ball))
    _, record = C.decide(v,belief)
    assert {row[1] for row in record['core_menus'][0]['options']} == {'zone_coverage','defending'}
    inside = next(o[2] for o in record['core_menus'][0]['options'] if o[0]=='area')
    _, outside = C.decide(replace(v,x=47.),belief)
    outside_area = next(o[2] for o in outside['core_menus'][0]['options'] if o[0]=='area')
    assert inside - outside_area == pytest.approx(CORE.AREA_INSIDE_VALUE)


def test_reflex_can_revise_a_committed_dodge_from_newly_believed_pressure():
    view, belief, threat, _ = prism_lab.scene(1,'reflex',.4)
    view = replace(view,core_entropy='paired',core_motion=('carry','juke',(87.,51.),750))
    threat = replace(threat,x=view.x+2.3,y=view.y,vx=-3.,vy=0.)
    base = C.ActionIntent('i','d',view.athlete,'carry',None,(90.,50.),None,None,view.delivered_ms)
    labels = []
    for reflex in (.4,1.):
        menu = CORE.Menu(replace(view,registry_ratings=(('reflex',reflex),)))
        CORE.evade(menu,view,base,threat,False)
        labels.append({option[0] for option in menu.records[0]['options']})
    assert 'late_dodge_adjustment' not in labels[0]
    assert 'late_dodge_adjustment' in labels[1]
