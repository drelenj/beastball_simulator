from dataclasses import replace
from types import SimpleNamespace

import pytest

from native import ladder
from native.geometry import body_out
from native.paired_policy import fresh_ball_holder
from native.rulebook.config import RulebookConfigV3
from native.rulebook.test_prism_core import core_port
from native.rulebook.test_rb332 import scene
from native.cognition import Track
from b1.emergence_intents import BallCourseBelief


def test_ladder_effective_configuration():
    cfg = RulebookConfigV3(roster_digests=('a'*64,'b'*64))
    assert 'rb333' not in cfg.record()
    assert cfg.carry_points == 5 and cfg.decision_ms==500
    full = replace(cfg,rb333=('cadence','carry_seven'))
    assert (full.sense_ms,full.latency_ms,full.decision_ms,full.carry_points)==(100,200,300,7)
    assert replace(full,rb333=(*full.rb333,'fast_cadence')).decision_ms==200
    with pytest.raises(ValueError):
        replace(cfg,rb333=('typo',))


def test_safe_pass_speed_and_scoring_thresholds(core_port):
    port,view,_=scene(core_port)
    data=(400,7,((10,2),(20,3),(None,4)),3,(('weak',.4),('strong',1.)),.4)
    view=replace(view,ladder_data=data,max_throw_speed=134.1)
    speed=ladder.pass_target(view,'weak',30.)
    capacity=port.m.native_catch_capacity(.4,.4)
    assert 1/(1+(.5*.4*speed**2/capacity)**8)==pytest.approx(.9)
    assert ladder.pass_target(view,'strong',30.)==pytest.approx(67.05)
    assert [ladder.release_points(view,d) for d in (2.99,3,10,20)]==[7,2,3,4]


def test_end_boundary_checks_hand_height():
    p=SimpleNamespace(posture='upright',x=100.1,y=50.,radius=.5,hand_height=1.8)
    assert body_out(p) and not body_out(p,3.)
    p.y=52.5
    assert body_out(p,3.)


def test_frame_freshness_independent_of_decision_clock(core_port):
    _,v,b=scene(core_port)
    v=replace(v,paired_fixes=('frame_freshness',),ladder_data=(400,),core_decision_ms=200)
    def holder(age):
        at=v.delivered_ms-age
        track=Track('r','B','field',51.,50.,2.,0.,at)
        course=BallCourseBelief('sample',at,v.delivered_ms,51.,50.,1.4,2.,0.,0.)
        return fresh_ball_holder(v,replace(b,ball_course=course),(track,))
    assert holder(400)=='r' and holder(401) is None


def test_reflex_recipients_exclude_distant_uncommitted_defender(core_port):
    port,giver=core_port
    port.config=replace(port.config,rb333=('keeper_interrupt','field_interrupt'))
    players=[p for p in port.m.s.players.values() if p.active]
    defenders=[p for p in players if p.team!=giver.team and p.role=='field']
    receiver=next(p for p in players if p.team==giver.team and p.role=='field' and p!=giver)
    for p in defenders:
        p.x,p.y=60.,79.
    defenders[0].y=65.
    defenders[1].native_intent=SimpleNamespace(target=giver.id,contact='wrap')
    listeners=ladder.release_listeners(port,giver,'pass',receiver.id,(80.,50.))
    assert listeners[receiver.id]=='pass'
    assert listeners[defenders[0].id]=='pass'
    assert listeners[defenders[1].id]=='release_from_wrap'
    assert defenders[2].id not in listeners
    shot=ladder.release_listeners(port,giver,'shoot',None,(100.,50.))
    assert sum(reason=='shot' for reason in shot.values())==1
    assert receiver.id not in shot


def test_carry_seven_and_release_bands_in_rule_authority():
    from native.roster import rb3_control_rosters
    from .port import RulebookPort
    rosters=rb3_control_rosters()
    cfg=RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in 'AB'),rb333=('carry_seven',))
    p=RulebookPort(1,cfg,rosters=rosters)
    e,s=p.m.e,p.m.s
    s.now,s.phase,s.restart,s.owner=60000,p.types.Phase.LIVE,None,'A'
    carrier=s.players['A:0']
    gx,sg=s.attack_goal('A'),s.attack_sign('A')
    carrier.x,carrier.y=gx-2*sg,50.
    s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier=carrier.id,scoring=True)
    e.follow_carrier()
    assert e.release(carrier.id,(sg*10.,0.,0.),'shot')
    s.ball.x=gx+sg*(s.ball.radius+.001)
    assert e.goal('B',50.,1.)
    assert s.score['A']==7 and e.rb_bands['A']['carry_goals']==1
    assert [e.rb.points(distance=d) for d in (9.,10.,20.)]==[2,3,4]
    assert e.rb.points(own=True)==2


def test_carry_value_preserves_scoring_and_separates_expected_values(core_port):
    from math import exp
    from native.paired_policy import continuation_points, shot_points

    cfg = RulebookConfigV3(roster_digests=('a'*64, 'b'*64), rb333=('carry_value', 'cadence'))
    assert (cfg.carry_points, cfg.decision_ms) == (7, 300)
    assert dict(cfg.pocket_settings)['carry_value'] == 7

    _, view, _ = scene(core_port)
    data = (400, cfg.carry_points, cfg.release_bands, cfg.carry_release_radius_m)
    view = replace(view, x=88., y=50., own_goal_x=0., ladder_data=data)
    plan = dict(aim=(100., 49.), margin=2.)
    assert shot_points(view, plan, scoring_table=True) == pytest.approx(3*(.28+.11*2)*exp(-12./45.))
    assert continuation_points(3., carry_scale=cfg.carry_points/5.) == pytest.approx(2.17/2)
    view = replace(view, x=98.)
    assert shot_points(view, plan, scoring_table=True) == pytest.approx(7*(.28+.11*2)*exp(-2./45.))
