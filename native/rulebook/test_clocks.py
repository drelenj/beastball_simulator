import pytest
from .port import RulebookPort

@pytest.fixture
def p():return RulebookPort(1)

@pytest.mark.parametrize('period,seconds',[(1,120),(2,600),(3,120),(4,180),(5,60)])
def test_real_break_clock_ends_and_hunt(p,period,seconds):
 s,e=p.m.s,p.m.e;s.period=period;e.rb.period=period;s.score={'A':0,'B':0}
 ends=dict(s.ends);e.end_period();assert s.ends=={k:100-v for k,v in ends.items()}
 assert e.rb_pause['until']-s.now==seconds*1000
 g,play,live=s.game_ms,s.possession_ms,s.live_ms
 p.advance_intermission();assert (s.game_ms,s.possession_ms,s.live_ms)==(g,play,live)
 assert s.phase==p.types.Phase.OPENING and not e.rb_hunt_running
 now=s.now;e.elapse(5);assert s.game_ms==g
 e.rb_hunt_release();e.elapse(5);assert s.game_ms==g-5


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
 s.players['A0'].x=50;s.players['A0'].y=50
 assert e.restart_release('A0',(24.,0.,1.),'A1')
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
 s.players['A0'].x,s.players['A0'].y=50,50
 s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier='A0',x=50,y=50,z=1.5,scoring=True)
 assert e.tackle('B0','A0',witnessed=True)
 assert s.possession_ms==17000 and s.tackle_count==1 and s.restart.rs['snapper']=='A0'
 e.elapse(100,False);assert s.possession_ms==16900
 s.phase=p.types.Phase.LIVE;s.tackle_count=0;s.possession_ms=10000
 s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier='A1',x=50,y=50,z=1.5,scoring=True)
 assert e.tackle('B1','A1',witnessed=True)
 e.elapse(100,False);assert s.possession_ms==10000

@pytest.mark.parametrize('points,kind',[(2,'release'),(1,'half_goal'),(3,'full_goal_award')])
def test_whole_first_overtime_then_any_score_sudden_death(p,points,kind):
 s,e=p.m.s,p.m.e;s.period=e.rb.period=4;s.game_ms=0;s.score={'A':0,'B':0}
 e.end_period();p.advance_intermission();e.rb_hunt_release()
 assert s.period==5 and s.game_ms==300000
 e.add_score('A',2,'release');assert s.phase!=p.types.Phase.FINAL
 e.add_score('B',2,'release');e.elapse(299999)
 assert s.period==5 and s.phase!=p.types.Phase.FINAL
 e.elapse(1);assert s.period==6 and e.rb_pause
 p.advance_intermission();e.rb_hunt_release();e.add_score('A',points,kind)
 assert s.phase==p.types.Phase.FINAL and s.result['winner']=='A'
