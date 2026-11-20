"""RB-3.3 PROVISIONAL owner rulings (17 Nov 2026): Archer may target any offensive player
outside the Keeper Zones; period starts by seeded coin flip; report fields."""
import random
import pytest
from collections import Counter
from .port import RulebookPort
from .period_start import COIN_STREAM, coin, offence_for
from .test_clocks import release_period_start
from native.run import run_match


from native.roster import rb3_control_rosters as control_rosters


def test_flip_is_seeded_from_its_own_stream_and_deterministic():
    for seed in range(1,9):
        a,b=RulebookPort(seed),RulebookPort(seed)
        expect=coin(random.Random(COIN_STREAM.format(seed=seed)))
        assert a.m.e.rb_flip['first']==b.m.e.rb_flip['first']==expect
    assert len({RulebookPort(seed).m.e.rb_flip['first'] for seed in range(1,9)})==2      # both outcomes occur
    flips=[r for r in RulebookPort(1).m.e.log if r['event']=='coin_flip']
    assert len(flips)==1 and flips[0]['data']['purpose']=='first_offence'


def test_start_pattern_winner_loser_loser_winner_and_overtime():
    assert [offence_for(n,'A',None) for n in (1,2,3,4)]==['A','B','B','A']
    assert [offence_for(n,'B',None) for n in (1,2,3,4)]==['B','A','A','B']
    assert [offence_for(n,'A','B') for n in (5,6,7,8)]==['B','A','B','A']   # OT alternation: PLACEHOLDER
    with pytest.raises(ValueError):offence_for(5,'A',None)


@pytest.mark.parametrize('seed',[1,2])
def test_engine_period_starts_follow_the_flip_are_snap40_at_y50_with_no_hunt(seed):
    p=RulebookPort(seed);s,e=p.m.s,p.m.e;w=e.rb_flip['first'];l='B' if w=='A' else 'A';seen=[]
    for period in (1,2,3,4,5,6):
        r=s.restart
        assert s.period==period and s.phase==p.types.Phase.DEAD and r.reason=='period_start'
        assert r.kind=='snap40' and r.y==50 and r.x==s.ends[r.team]+s.attack_sign(r.team)*40
        assert s.owner==r.team and s.tackle_count==0 and s.possession_ms==p.config.play_clock_ms and not e.hunt_cleared
        seen.append(r.team)
        release_period_start(p);s.owner=None
        s.score={'A':0,'B':0};s.game_ms=0;e.end_period();p.advance_intermission()
    ot=e.rb_flip['overtime']
    assert seen[:4]==[w,l,l,w] and ot in ('A','B') and seen[4]==ot and seen[5]!=ot
    assert [r['data']['purpose'] for r in e.log if r['event']=='coin_flip']==['first_offence','first_overtime']
    assert not any(r['event']=='hunt_start' for r in e.log)
    assert sum(r['event']=='period_start' for r in e.log)==7


def test_hunt_code_kept_but_not_used_at_period_starts():
    p=RulebookPort(1);e=p.m.e
    assert callable(e.rb_open_hunt) and e.begin_hunt.__name__=='period_start'


def test_archer_can_target_any_offensive_player_outside_keeper_zones():
    p=RulebookPort(1);s,e=p.m.s,p.m.e;P=p.types.Phase
    s.phase=P.LIVE;e.hunt_cleared=True;s.owner='B';e.possession.pp=e.possession.tc='B';e.rb.possession='B'
    for q in s.players.values():
        if q.role!='archer':q.x,q.y=50.,90.
    for x in (25.,50.,75.):       # A's own end is 0: 25, 50 and 75 m from it, all outside both zones
        t=s.players['B0'];t.x,t.y=x,50.;t.immune_until=-1
        assert e.shoot_arrow('A11','B0',(1,0,0)),x
    assert not any(r['event']=='foul' for r in e.log)


def test_control_seed_now_affects_the_outcome():
    rosters=control_rosters();hashes={};flips={}
    for seed in (1,2,3,4):
        p=RulebookPort(seed,rosters=rosters);flips[seed]=p.m.e.rb_flip['first']
        r,_=run_match(seed,p.config,max_steps=400,rosters=rosters,port_factory=lambda *a,**k:p)
        hashes[seed]=r['trace_hash']
    assert len(set(flips.values()))==2 and len(set(hashes.values()))==4


@pytest.fixture(scope='module')
def window():
    r,p=run_match(1,max_steps=3000,port_factory=lambda *a,**k:RulebookPort(1))
    return r,p


def test_report_fields_foul_origin_discipline_offence_arrow_and_carry_outcomes(window):
    r,p=window;log=p.m.e.log
    awards=[x for x in log if x['event']=='foul_award']
    assert awards and all(x['data']['origin_foul']['reason'] for x in awards)
    disc=[x['data']['ruling'] for x in log if x['event']=='rb_discipline']
    assert disc and all(d['offence'] and d['offence']['reason'] for d in disc)
    released={x['data']['arrow'] for x in log if x['event']=='arrow_release'}
    outcomes=Counter();ended=set()
    for x in log:
        if x['event']=='arrow_outcome':outcomes[x['data']['outcome']]+=1;ended.add(x['data']['arrow'])
    assert outcomes and set(outcomes)<={'hit','hit_other','inert','ball','miss'}
    assert ended<=released and len(released-ended)==sum(a.live for a in p.m.s.arrows)
    carries=[x['data'] for x in log if x['event']=='carry_outcome']
    assert all(c['outcome'] in ('goal','tackled','grounded','turnover','stopped_short') for c in carries)
