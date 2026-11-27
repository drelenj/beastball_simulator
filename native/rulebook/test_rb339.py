from dataclasses import replace

import pytest

from native.edge_control import FLAGS, clamp_aim
from native import cognition_rb3, paired_policy
from .test_prism_core import core_port
from .test_rb336 import port_with


def player_with(core_port,flags,role='field'):
    port = port_with(core_port,rb333=flags)
    match, state = port.m, port.m.s
    player = next(p for p in state.players.values() if p.team=='A' and p.role==role and p.active)
    match.c3_cache[player.id] = (30.,0.,())
    return port,player


@pytest.mark.parametrize('role',('field','keeper'))
def test_edge_braking_consumes_the_step_first(core_port,role):
    port,p=player_with(core_port,('edge_brake',),role)
    p.x,p.y,p.vx,p.vy,p.target=50.,1.25,8.,-5.,(75.,1.)
    port.m.c3_desired(p,.1,True,None)
    assert p.vx==pytest.approx(8.)
    assert p.vy==pytest.approx(-5.+p.a.braking*.1)


def test_unused_braking_budget_can_steer_after_outward_speed_is_cancelled(core_port):
    port,p=player_with(core_port,('edge_brake',))
    p.x,p.y,p.vx,p.vy,p.target=50.,p.radius+.2,4.,-.3,(58.,.1)
    port.m.c3_desired(p,.1,True,None)
    assert p.vy==pytest.approx(0.)
    assert p.vx>4.
    assert p.vx-4.<=p.a.acceleration*(.1-.3/p.a.braking)


def test_turn_switch_selects_the_long_way_only_with_a_line_on_short_side(core_port):
    port,p=player_with(core_port,('edge_turn',))
    for y, expected in ((4.,1),(20.,-1)):
        p.x,p.y,p.vx,p.vy,p.target=50.,y,7.,0.,(30.,y-2.)
        port.m.c3_desired(p,.1,True,None)
        assert p.vy*expected>0
        assert abs(p.vy)<=p.a.turning*.1+1e-9


def test_disabled_for_dead_ball_and_deliberate_substitution(core_port):
    port,p=player_with(core_port,FLAGS)
    m,s=port.m,port.m.s
    p.x,p.y,p.vx,p.vy=50.,1.,5.,-6.
    aim=(70.,-.5)
    assert m.native_edge_update(p,.1,False,8.,-8.,p.a.acceleration) is False
    s.phase=port.types.Phase.DEAD
    assert m.native_boundary_target(p,aim)==aim
    s.phase=port.types.Phase.LIVE
    m.pending_sub['A']=(p.id,'reserve')
    assert m.native_edge_update(p,.1,True,8.,-8.,p.a.acceleration) is False
    assert m.native_boundary_target(p,aim)==aim


def test_keep_in_uses_each_outward_component_and_player_braking(core_port):
    port,p=player_with(core_port,('edge_aim',))
    p.x,p.y,p.vx,p.vy=70.,20.,8.,-9.
    goal_x=port.m.s.attack_goal(p.team)
    clamp=port.m.native_boundary_target
    aim=(100.,0.)
    got=clamp(p,aim)
    assert got==pytest.approx((100-max(2,p.radius+64/(2*p.a.braking)+.5),
                               max(2,p.radius+81/(2*p.a.braking)+.5)))
    port.capture(0)
    port.m.s.now=port.config.latency_ms
    view,_=port.view(p.id,port.m.s.now)
    view=replace(view,paired_fixes=('edge_aim',),own_goal_x=100-goal_x)
    predicted=tuple(round(c,3) for c in got)
    assert cognition_rb3.keep_in(view,aim)==predicted
    assert paired_policy.boundary_aim(view,aim)==predicted


@pytest.mark.parametrize('sign',(-1,1))
def test_attacking_carrier_can_cross_only_the_goal_mouth(core_port,sign):
    port,p=player_with(core_port,FLAGS)
    s=port.m.s
    goal=100. if sign>0 else 0.
    s.ends={'A':100-goal,'B':goal}
    p.x,p.vx,p.vy=goal-sign*1.5,sign*6.,0.
    aim=(goal+sign*3.,50.)
    s.ball.carrier=p.id
    p.y=50.
    assert port.m.native_boundary_target(p,aim)==aim
    assert port.m.native_edge_update(p,.1,True,sign*9.,0.,p.a.acceleration) is False
    p.y=45.
    wide=(aim[0],45.)
    assert port.m.native_boundary_target(p,wide)[0]!=wide[0]
    assert port.m.native_edge_update(p,.1,True,sign*9.,0.,p.a.acceleration) is True
    p.y=50.
    s.ball.carrier=None
    assert port.m.native_boundary_target(p,aim)[0]!=aim[0]


def test_angled_mouth_path_and_very_long_stopping_distance():
    body=dict(x=95.,y=44.,vx=10.,vy=0.,radius=.5,braking=11.,
              goal=100.,hand_height=1.5,ball_radius=.1075,goal_radius=3.)
    assert clamp_aim((105.,56.),**body)==(105.,56.)
    assert clamp_aim((105.,65.),**body)[0]<100.
    body.update(vx=40.,braking=.01,goal=None)
    assert clamp_aim((105.,65.),**body)==(2.,65.)


def test_master_switch_registers_all_three_parts(core_port):
    config=core_port[0].config
    assert not set(FLAGS).intersection(config.rb333)
    assert replace(config,rb333=('edge_control',)).rb333==('edge_control',*FLAGS)
