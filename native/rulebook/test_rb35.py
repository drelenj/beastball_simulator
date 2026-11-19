"""RB-3.5 PROVISIONAL owner rulings (17-18 Nov 2026): zone residence by zone; arrow edge
cases (finishing-flight release, possession change in flight); no freeze range limit."""
import math
import pytest
from .test_rb34 import rb3, live, fly, fouls
from .zone_residence import residence
from .config import RulebookConfigV3


def setup(p):
    """B has passive possession and attacks x=0 (zone 0 = A's own zone)."""
    s,e,a,t=live(p)
    assert s.ends['A']==0 and e.possession.pp=='B' and s.own_zone('A')==0
    for i,q in enumerate(x for x in s.players.values() if x.role!='archer'):
        q.x,q.y=40.+(i%10)*2.,12.+(i//10)*8.              # midfield, outside both zones, far from tests
    return s,e,a


def player(s,team,x,y,skip=()):
    q=next(q for q in s.players.values() if q.team==team and q.role=='field' and q.active and q.id not in skip)
    q.x,q.y,q.vx,q.vy=x,y,0.,0.;return q


def tick(p,ms,n=1):
    s=p.m.s
    for _ in range(n):
        before=s.live_ms;s.live_ms+=ms;s.now+=ms;residence(p,before)


def zone_calls(e):
    return [r for r in e.log if r['event']=='zone_foul_diagnosis']


def test_config_parameters():
    c=RulebookConfigV3.__dataclass_fields__
    assert c['zone_residence_ms'].default==5000 and c['zone_marked_distance_m'].default==5.0
    with pytest.raises(ValueError):rb3().config.__class__(roster_digests=rb3().config.roster_digests,zone_residence_ms=0)


def test_defender_unmarked_in_own_zone_is_called_after_5s():
    p=rb3();s,e,a=setup(p);d=player(s,'A',6.,50.)
    tick(p,100,50);assert not fouls(e,'zone_unmarked')          # timer starts at the first in-zone check
    tick(p,100,1);assert len(fouls(e,'zone_unmarked'))==1
    z=zone_calls(e)[-1]['data'];assert z['kind']=='zone_unmarked' and z['fouler']['id']==d.id and z['fouler']['zone']=='own'


def test_defender_in_the_zone_his_team_attacks_is_not_covered():
    p=rb3();s,e,a=setup(p);player(s,'A',94.,50.)
    tick(p,100,80);assert not fouls(e) and not zone_calls(e)


def test_attacker_in_attacked_zone_is_zone_residence():
    p=rb3();s,e,a=setup(p);q=player(s,'B',6.,40.)
    tick(p,100,51)
    assert any(r['event']=='restart_awarded' and r['data']['reason']=='zone_residence' for r in e.log)
    z=zone_calls(e)[-1]['data'];assert z['kind']=='zone_residence' and z['fouler']['id']==q.id and z['fouler']['zone']=='attacked'


def test_attacker_in_own_zone_is_not_covered():
    p=rb3();s,e,a=setup(p);player(s,'B',94.,50.)
    tick(p,100,80);assert not zone_calls(e) and not any(r['event']=='restart_awarded' and r['data']['reason']=='zone_residence' for r in e.log)


@pytest.mark.parametrize('gap,called',[(4.9,False),(5.0,False),(5.1,True)])
def test_marked_exemption_at_5m(gap,called):
    p=rb3();s,e,a=setup(p);player(s,'A',17.,50.);player(s,'B',17.+gap,50.)      # marker outside the zone
    tick(p,100,60);assert bool(fouls(e,'zone_unmarked'))==called


def test_timer_resets_when_he_leaves_or_is_marked():
    p=rb3();s,e,a=setup(p);d=player(s,'A',6.,50.)
    tick(p,100,40);d.x=25.;tick(p,100,1);d.x=6.;tick(p,100,40);assert not fouls(e)     # left the zone
    m=player(s,'B',22.,50.);m.y=50.;m.x=10.;tick(p,100,1);m.x=40.;tick(p,100,40);assert not fouls(e)   # marked
    tick(p,100,11);assert len(fouls(e,'zone_unmarked'))==1
    z=zone_calls(e)[-1]['data']['fouler'];assert z['reentered_within_5s'] is False and z['live_ms_in_zone']>z['live_ms_unmarked']


def test_reentry_and_diagnosis_fields():
    p=rb3();s,e,a=setup(p);d=player(s,'A',6.,50.);carrier=s.ball.carrier
    tick(p,100,1);d.x=25.;tick(p,100,1);d.x=6.;tick(p,100,51)
    z=zone_calls(e)[-1]['data'];f=z['fouler']
    assert f['reentered_within_5s'] is False and f['live_ms_since_last_exit']==5100 and f['team']=='A' and f['role']=='field' and f['frozen_or_immune_prev_10s'] is False
    assert z['possession_team']=='B' and z['ball']['status'] and z['nearest_off_ball_offence']['id']!=carrier
    assert z['nearest_offence_any']['distance_to_fouler']<=z['nearest_off_ball_offence']['distance_to_fouler']
    assert z['offence_within_20m']>=z['offence_within_10m']>=0 and z['teammates_in_same_zone']==0
    assert carrier and z['ball']['carrier']['id']==carrier


def test_live_time_share_summary_is_logged_at_period_end():
    p=rb3();s,e,a=setup(p);player(s,'A',6.,50.)
    tick(p,100,21);s.game_ms=0;e.end_period()
    row=[r for r in e.log if r['event']=='zone_time_summary'][-1]['data']['teams']['A']
    assert row['defender_ms']>0 and row['in_own_zone_ms']==2100 and row['in_own_zone_unmarked_ms']==2100


# ---- arrow edge cases
def test_release_during_finishing_flight_is_inert_and_refunded():
    p=rb3();s,e,a,t=live(p);s.phase=p.types.Phase.FLIGHT
    assert e.shoot_arrow(a,t.id,(1,0,0)) is False and not fouls(e) and e.rb.quotas['A']['arrows']==0
    assert [r['data']['reason'] for r in e.log if r['event']=='arrow_inert']==['finishing_flight_release']


def test_arrow_in_flight_when_possession_changes_is_inert_and_stays_spent():
    p=rb3();s,e,a,t=live(p)
    assert e.shoot_arrow(a,t.id,(1,0,0)) and e.rb.quotas['A']['arrows']==1
    e.possession.pp='A';e.possession.tc='A'             # A wins the ball while the arrow is in the air
    e.native_sync();assert e.rb.possession=='A'
    assert not any(x.live for x in s.arrows) and not fouls(e)
    d=[r['data'] for r in e.log if r['event']=='arrow_inert'][-1]
    assert d['reason']=='possession_change' and d['refunded'] is False and e.rb.quotas['A']['arrows']==1
    fly(p);assert not t.frozen(s.now)


def test_no_freeze_range_limit_beyond_70m():
    p=rb3();s,e,a,t=live(p);arch=s.players[a];t.x,t.y=75.,30.
    origin=(arch.x,arch.y,arch.z+.72*arch.a.height);assert math.dist(origin[:2],(t.x,t.y))>70
    v=p.geom.ballistic(origin,(t.x,t.y,1.6),p.config.arrow_speed,9.81)[0]
    assert e.shoot_arrow(a,t.id,v);fly(p,20)
    f=[r for r in e.log if r['event']=='freeze' and r['data']['player']==t.id]
    assert t.frozen(s.now) and f and not fouls(e)
