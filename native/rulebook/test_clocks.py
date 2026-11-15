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
