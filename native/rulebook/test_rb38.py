"""RB-3.8 owner ruling (CANON, 18 Nov 2026): no freeze-recovery condition on native-rb/3.
A thawed player is never refused an action; thaw contact buffer and arrow immunity unchanged."""
import pytest
from dataclasses import replace
from .test_rb34 import live, fly, fouls
from .test_rb36 import rb3
from .port import RulebookPort
from native import cognition as C
from native.run import run_match


def frozen_near_own_end(p):
    s,e,a,t=live(p)
    q=next(x for x in s.players.values() if x.team=='A' and x.role=='field' and x.active)
    q.x,q.y=2.,10.                     # 2 m from A's own end line (freezes inside a Keeper Zone are refused)
    assert s.ends['A']==0 and e.zone(q.x,q.y) is None
    assert e.freeze(q.id,panel=True)  # a real freeze through the engine
    q.y=45.;assert e.zone(q.x,q.y)==0 # he is in his own zone when he thaws: where the old rule refused him
    return s,e,q


def test_player_frozen_2m_from_own_end_acts_immediately_after_thaw():
    p=rb3();s,e,q=frozen_near_own_end(p)
    assert q.frozen(s.now) and not hasattr(q,'rb_recover')
    s.now=q.freeze_until                                       # thawed (5 s)
    assert not q.frozen(s.now) and e.rb_recovery_ready(q) and not e.rb_recovery_blocked(q)
    for kind,aim in (('position',(30.,45.)),('mark',(10.,40.)),('pursue',(40.,50.)),('support',(25.,60.))):
        i=C.ActionIntent(f'i{kind}','d',q.id,kind,None,aim,None,None,s.now,period=s.period)
        assert p.submit(i)['status']=='accepted'
    assert e.contact_legal(q,s.players[next(x.id for x in s.players.values() if x.team=='B' and x.role=='field' and x.active)],'block')[1]!='freeze_recovery'
    # ball actions are not gated either
    s.ball.carrier=None;s.ball.mode=p.types.BallMode.LOOSE;s.ball.x,s.ball.y=q.x,q.y
    assert e.acquire(q.id)


def test_no_recovery_state_or_view_field():
    p=rb3();s,e,q=frozen_near_own_end(p);s.now=q.freeze_until+1
    p.capture(s.now);s.now+=300;v,b=p.view(q.id,s.now)
    assert not hasattr(v,'own_recovery_from_x') and not hasattr(q,'rb_recover')


def test_thaw_buffer_and_immunity_unchanged():
    p=rb3();s,e,q=frozen_near_own_end(p);d=next(x for x in s.players.values() if x.team=='B' and x.role=='field' and x.active)
    d.x,d.y=q.x+1.,q.y
    q.y=10.;d.y=10.                    # contact tests outside the zone
    assert q.freeze_until==s.now+5000 and q.immune_until==s.now+15000
    assert e.contact_legal(d,q,'block')==(True,'frozen_obstacle')
    s.now=q.freeze_until;assert e.contact_legal(d,q,'block')==(False,'immune_contact')
    s.now=q.freeze_until+999;assert e.contact_legal(d,q,'block')==(False,'immune_contact')
    s.now=q.freeze_until+1000;assert e.contact_legal(d,q,'block')[1]!='immune_contact'
    assert p.config.thaw_contact_buffer_ms==1000 and not e.freeze(q.id,panel=True)   # still arrow-immune


def test_rb2_keeps_its_recovery_rule():
    p=RulebookPort(1);s,e,a,t=live(p)
    q=next(x for x in s.players.values() if x.team=='A' and x.role=='field' and x.active);q.x,q.y=2.,10.
    assert e.freeze(q.id,panel=True) and hasattr(q,'rb_recover');q.y=45.
    s.now=q.freeze_until;assert e.rb_recovery_blocked(q)


def test_determinism_same_code_roster_seed():
    a,_=run_match(1,rb3().config,max_steps=1500,rosters=None,port_factory=lambda *x,**k:rb3())
    b,_=run_match(1,rb3().config,max_steps=1500,rosters=None,port_factory=lambda *x,**k:rb3())
    assert (a['trace_hash'],a['state_hash'])==(b['trace_hash'],b['state_hash'])
