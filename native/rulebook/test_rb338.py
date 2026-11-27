from dataclasses import replace

import pytest

from native import cognition as C
from native.archer_cycle import cycle_ms, opportunity_cost
from native.roster import rb3_control_rosters
from .authorities import Authorities
from .config import RulebookConfigV3
from .port import RulebookPort


def build(budget=None):
    rosters = rb3_control_rosters()
    cfg = RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in 'AB'),
                           archer_cycle=True,archer_budget=budget)
    return RulebookPort(1,cfg,rosters=rosters)


def target_intent(port, archer, target, kind='draw_release', related=None):
    s=port.m.s
    return C.ActionIntent(f'{s.now}/{target}',f'{s.now}/decision',archer,kind,target,
                          (50.,50.),None,None,s.now,related_command_id=related)


def test_default_tackles_and_archive_key():
    roster=('a'*64,'b'*64)
    live=RulebookConfigV3(roster_digests=roster)
    assert live.tackles_per_possession==3
    assert live.record()['tackles_per_possession']==3
    historical=replace(live,tackles_per_possession=2).record()
    assert not {'tackles_per_possession','archer_cycle','archer_budget'} & historical.keys()


def test_cycle_rating_and_budget_effects():
    assert cycle_ms(.70,.70)==(1000,800)
    assert cycle_ms(.90,.70)==(880,800)
    assert cycle_ms(.70,.90)==(1000,704)
    assert opportunity_cost(1,5,60000,1800,50)>opportunity_cost(5,5,60000,1800,50)
    assert opportunity_cost(1,5,60000,1800,50)>opportunity_cost(1,5,1800,1800,50)


def test_target_change_restarts_aim_and_abort_is_free():
    port=build()
    s,e=port.m.s,port.m.e
    s.phase=port.types.Phase.LIVE
    s.now=5000
    archer=next(p for p in s.players.values() if p.team=='A' and p.role=='archer' and p.active)
    target,other=[p.id for p in s.players.values() if p.team=='B' and p.role=='field' and p.active][:2]
    draw,aim=cycle_ms(archer.a.strength,archer.a.archery_accuracy)
    result=port.submit(target_intent(port,archer.id,target))
    cmd=result['command']
    assert cmd.release_ms == 5000+draw+aim
    assert not e.shoot_arrow(archer.id,target,(1,0,0))
    s.now+=draw+10
    assert port.submit(target_intent(port,archer.id,target,'release_arrow',cmd.command_id))['reason']=='archer_cycle_pending'
    other_cmd=port.submit(target_intent(port,archer.id,other,related=cmd.command_id))['command']
    assert other_cmd.release_ms==s.now+aim and other_cmd.start_ms==cmd.start_ms
    assert not e.shoot_arrow(archer.id,other,(1,0,0))
    port.submit(target_intent(port,archer.id,other,'abort_draw',other_cmd.command_id))
    assert not e.shoot_arrow(archer.id,other,(1,0,0))
    assert e.rb.remaining('A')==(15,5)


@pytest.mark.parametrize('mode,initial,period_two,period_five',
                         [('match',(25,5),(24,4),(24,4)),('period',(10,4),(10,4),(5,2))])
def test_budget_follows_team_not_possession(mode, initial, period_two, period_five):
    law=Authorities(build(mode).config)
    assert law.remaining('A')==initial
    law.arrow('A',False)
    law.quotas['A']['freezes']=1
    for team in ('A','B','A','B'):
        assert law.turnover(team) is None
    assert law.remaining('A')==(initial[0]-1,initial[1]-1)
    assert law.remaining('B')==initial
    law.enter_period(2)
    assert law.remaining('A')==period_two
    law.enter_period(5)
    assert law.remaining('A')==period_five
    for _ in range(period_five[0]):
        assert law.arrow('A',True)['kind']=='arrow_release'
    assert law.arrow('A',True)['kind']=='arrow_denied'


def test_budgeted_release_freeze_and_period_refund():
    from .test_rb34 import live

    port=build('period')
    s,e,archer,target=live(port)
    draw=port.submit(target_intent(port,archer,target.id))['command']
    s.now=draw.release_ms
    release=target_intent(port,archer,target.id,'release_arrow',draw.command_id)
    assert port.submit(release)['status']=='accepted'
    port.archer_motor()
    assert e.rb.remaining('A')==(9,4)
    assert e.assert_invariants()
    assert len(s.arrows)==1
    assert e.freeze(target.id,arrow=s.arrows[0].id)
    assert e.rb.remaining('A')==(9,3)
    e.rb.quotas['A']['freezes']=4
    other=next(p for p in s.players.values() if p.team=='B' and p.role=='field' and p.active and p.id!=target.id)
    other.x,other.y=60.,50.
    assert not e.freeze(other.id,arrow=s.arrows[0].id)
    e.end_period()
    assert s.period==2 and e.rb.remaining('A')==(10,4)
    assert not s.arrows[0].live


def test_public_budget_view_round_trip():
    port=build('match')
    pid=next(p.id for p in port.m.s.players.values() if p.team=='A' and p.role=='archer' and p.active)
    port.capture(0)
    port.m.s.now=port.config.latency_ms
    view,belief=port.view(pid,port.m.s.now)
    assert view.archer_cycle_ms==(1000,800)
    assert view.archer_budgets==('match',2400000,(('A',25,5),('B',25,5)))
    recovered,_=port.view_from_json(C.view_to_json(view,belief))
    assert recovered.archer_budgets==view.archer_budgets
    assert recovered.archer_cycle_ms==view.archer_cycle_ms


def test_match_quiver_invariant_uses_its_scoped_allocation():
    port=build('match')
    port.m.e.native_sync()
    quiver=port.m.s.quivers['A']
    assert (quiver.allocation,quiver.loaded)==(25,25)
    assert port.m.e.assert_invariants()
