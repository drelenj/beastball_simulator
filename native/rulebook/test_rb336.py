from dataclasses import replace

import pytest

from native.geometry import body_out
from native.reaction_clock import set_speed
from native.roster import rb3_control_rosters
from native.turnovers import boundary_risk
from .port import RulebookPort
from .test_rb332 import scene
from .test_prism_core import core_port


def port_with(core_port, **changes):
    port = RulebookPort(1,replace(core_port[0].config,**changes),rosters=rb3_control_rosters())
    port.m.s.phase = port.types.Phase.LIVE
    return port


def test_angled_path_uses_the_crossing_y(core_port):
    _, view, _ = scene(core_port)
    view = replace(view,x=95.,y=45.,body=replace(view.body,vx=0.,vy=0.))
    assert boundary_risk(view,(105.,55.))
    assert not boundary_risk(replace(view,paired_fixes=('boundary_cross_y',)),(105.,55.))


@pytest.mark.parametrize('ball_mode,holder,y,depart,expected', [
    ('CONTROLLED',True,44.,0.,None),
    ('CONTROLLED',True,50.,0.,'goal'),
    ('PASS',False,44.,20.,'boundary'),
    ('LOOSE',False,44.,20.,'boundary'),
])
def test_swept_endline_preserves_goals_and_free_ball_rules(core_port,ball_mode,holder,y,depart,expected):
    port = port_with(core_port,rb333=('endline_held_ball','sideline_held_ball','mouth_boundary'))
    match,state = port.m,port.m.s
    p = state.players['A:0']
    p.x,p.y = 99.,y
    state.ball = port.types.Ball(mode=getattr(port.types.BallMode,ball_mode),
                                carrier=p.id if holder else None,x=99.8,y=y,z=1.4,vx=depart)
    if holder:
        def follow():
            state.ball.x=100.2
        match.e.follow_carrier = follow
    assert [e.kind for e in match.advance_ball(50,{}) if e.kind in ('goal','boundary')]==([expected] if expected else [])
    if holder:
        p.x=99.9
        assert body_out(p,port.config.goal_radius)==(y==44.)


@pytest.mark.parametrize('limit',[2,3,4])
def test_tackle_limit_retains_possession_until_nth_grounding(core_port,limit):
    p = port_with(core_port,tackles_per_possession=limit)
    e,s = p.m.e,p.m.s
    for count in range(1,limit+1):
        s.phase = p.types.Phase.LIVE
        s.owner = 'A'
        s.ball = p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier='A:0',x=55.,y=50.,z=1.4)
        assert e.tackle('B:0','A:0',witnessed=True)
        assert s.tackle_count==(count if count<limit else 0)
        assert s.restart.team==('A' if count<limit else 'B')
    assert s.restart.reason==('second_tackle' if limit==2 else 'nth_tackle')


def test_count_penalties_and_score_awards_use_the_trial_limit(core_port):
    p = port_with(core_port,tackles_per_possession=4)
    e,s = p.m.e,p.m.s
    s.owner=e.possession.pp='A'
    s.tackle_count=1
    e.foul('A:0',reason='hold')
    assert s.tackle_count==2 and s.restart.team=='A'
    s.phase=p.types.Phase.LIVE
    e.foul('B:0',reason='hold')
    assert s.tackle_count==1 and s.score['A']==0
    s.tackle_count=3
    e.offside('offence')
    assert s.tackle_count==0 and s.restart.team=='B'


def test_unset_latches_player_speed_and_renews_same_deadline(core_port):
    p = port_with(core_port,rb333=('universal_set_speed','universal_unset'))
    clock,s = p.reaction_clock,p.m.s
    a = s.players['A:0']
    a.vx,a.vy = set_speed(a)+1,0.
    assert clock.begin_command(a,'takedown','B:0')==s.now+100
    assert not clock.contact_ready(a)
    a.vx=0.
    s.now+=30
    assert clock.begin_command(a,'takedown','B:0')==s.now+70
    s.now+=70
    assert clock.contact_ready(a)
    a.vx=set_speed(a)+1
    clock.start_course((id(s.ball),s.ball.version),s.now)
    p.m.seen_from=s.now
    a.vx=0.
    assert clock.hands_delay(a)==100
