import pytest
from .port import RulebookPort
from .testing import rb3_port

@pytest.fixture
def p():return rb3_port(1)

def release_period_start(p):
 """Release the period-start snap through the real ready/release path."""
 s,e=p.m.s,p.m.e;r=s.restart;assert r.reason=='period_start' and r.kind=='snap40'
 for i,q in enumerate(x for x in s.players.values() if x.active and x.role!='archer'):
  q.x=s.ends[q.team]+s.attack_sign(q.team)*(10+i%20);q.y=5+4*(i%22);q.posture='upright'
 taker=next(q for q in s.players.values() if q.active and q.team==r.team and q.role=='field')
 taker.x,taker.y=r.taker_spot
 assert e.restart_release(taker.id,(-s.attack_sign(r.team)*5.,0.,1.),None)
 assert s.phase==p.types.Phase.LIVE and e.hunt_cleared
 return r.team

@pytest.mark.parametrize('period,seconds',[(1,120),(2,600),(3,120),(4,180),(5,60)])
def test_real_break_clock_ends_and_period_start_scrimmage(p,period,seconds):
 # Owner ruling 17 Nov 2026: a period begins with a snap40 scrimmage, not the Hunt.
 s,e=p.m.s,p.m.e;s.period=period;e.rb.period=period;s.score={'A':0,'B':0}
 ends=dict(s.ends);e.end_period();assert s.ends=={k:100-v for k,v in ends.items()}
 assert e.rb_pause['until']-s.now==seconds*1000
 g,play,live=s.game_ms,s.possession_ms,s.live_ms
 p.advance_intermission();assert (s.game_ms,s.possession_ms,s.live_ms)==(g,play,live)
 r=s.restart;assert s.phase==p.types.Phase.DEAD and r.reason=='period_start' and r.kind=='snap40' and r.y==50
 assert r.x==s.ends[r.team]+s.attack_sign(r.team)*40 and not e.hunt_cleared
 assert not any(x['event']=='hunt_start' for x in e.log)
 e.elapse(5);assert s.game_ms==g                       # dead ball: game clock stopped
 release_period_start(p);e.elapse(5);assert s.game_ms==g-5


def test_timeout_freezes_both_clocks_and_restart_deadline(p):
 s,e=p.m.s,p.m.e;e.award('A',50,50,'fixture');e.rb.score('B');e.rb.score('B')
 r=s.restart;deadline=r.snap_deadline;now=s.now;g,play=s.game_ms,s.possession_ms
 assert e.rb_timeout('A');p.advance_intermission()
 assert s.now==now+45000 and (s.game_ms,s.possession_ms)==(g,play)
 assert r.snap_deadline==deadline+45000
 assert not e.rb_timeout('A')


def test_release_restarts_clock_and_tackle_preserves_remaining(p):
 s,e=p.m.s,p.m.e;e.award('A',50,50,'fixture')
 for q in s.players.values():
  if q.role!='archer':q.x=45 if q.team=='A' else 55
 taker=next(q for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
 receiver=next(q for q in s.players.values() if q.team=='A' and q.role=='field' and q.active and q is not taker)
 taker.x=taker.y=50
 assert e.restart_release(taker.id,(24.,0.,1.),receiver.id)
 e.elapse(100);assert s.game_ms==599900

def test_consecutive_legal_timeouts_do_not_trigger_restart_watchdog(p):
 from native.run import run_match
 s,e=p.m.s,p.m.e;s.period=e.rb.period=4;s.game_ms=60000;s.score={'A':2,'B':2}
 e.rb.score('B');e.rb.score('B');e.award('A',50,50,'fixture')
 result,_=run_match(1,config=p.config,max_steps=4,port_factory=lambda *args:p)
 assert sum(r['kind']=='timeout' for r in e.rb.calls)==3
 assert s.now>=135000 and s.live_ms==0 and s.game_ms==60000
 assert result['status']=='partial'

def test_real_tackle_keeps_play_clock_and_snap_window_runs_only_above_ten(p):
 s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE;e.rb_hunt_running=True
 s.owner='A';e.possession.pp=e.possession.tc='A';s.possession_ms=17000
 carrier=next(q for q in s.players.values() if q.team=='A' and q.role=='field' and q.active)
 tackler=next(q for q in s.players.values() if q.team=='B' and q.role=='field' and q.active)
 carrier.x,carrier.y=50,50
 s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier=carrier.id,x=50,y=50,z=1.5,scoring=True)
 assert e.tackle(tackler.id,carrier.id,witnessed=True)
 assert s.possession_ms==17000 and s.tackle_count==1 and s.restart.rs['snapper']==carrier.id
 e.elapse(100,False);assert s.possession_ms==16900
 s.phase=p.types.Phase.LIVE;s.tackle_count=0;s.possession_ms=10000
 carrier=next(q for q in s.players.values() if q.team=='A' and q.role=='field' and q.active and q is not carrier)
 tackler=next(q for q in s.players.values() if q.team=='B' and q.role=='field' and q.active and q is not tackler)
 s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier=carrier.id,x=50,y=50,z=1.5,scoring=True)
 assert e.tackle(tackler.id,carrier.id,witnessed=True)
 e.elapse(100,False);assert s.possession_ms==10000

@pytest.mark.parametrize('points,kind',[(2,'release'),(1,'half_goal'),(3,'full_goal_award')])
def test_whole_first_overtime_then_any_score_sudden_death(p,points,kind):
 s,e=p.m.s,p.m.e;s.period=e.rb.period=4;s.game_ms=0;s.score={'A':0,'B':0}
 e.end_period();p.advance_intermission();first_ot=release_period_start(p)
 assert first_ot==e.rb_flip['overtime'] is not None
 s.owner=None # structure test: no possession, so the 30 s clock cannot interrupt the period clock
 assert s.period==5 and s.game_ms==300000
 e.add_score('A',2,'release');assert s.phase!=p.types.Phase.FINAL
 e.add_score('B',2,'release');e.elapse(299999)
 assert s.period==5 and s.phase!=p.types.Phase.FINAL
 e.elapse(1);assert s.period==6 and e.rb_pause
 p.advance_intermission();assert release_period_start(p)!=first_ot   # later OT periods alternate (PLACEHOLDER)
 e.add_score('A',points,kind)
 assert s.phase==p.types.Phase.FINAL and s.result['winner']=='A'
