from dataclasses import replace
import pytest
from .port import RulebookPort
from .config import RulebookConfig

@pytest.mark.parametrize('distance,points',[(9.999,2),(10,3),(19.999,3),(20,4)])
def test_real_release_band_and_goal(distance,points):
 p=RulebookPort(1,replace(RulebookConfig(),scoring='banded'));s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE;e.rb_hunt_running=True
 s.owner='A';s.players['A0'].x=100-distance;s.players['A0'].y=50
 s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier='A0',x=100-distance,y=50,z=1.5,scoring=True)
 e.follow_carrier();s.players['A0'].x+=(100-distance)-s.ball.x
 assert e.release('A0',(25,0,1),'shot');s.ball.x=101;s.ball.y=50;s.ball.z=1.5
 assert e.goal('B');assert s.score['A']==points
 assert e.rb_attempts[-1]['distance']==pytest.approx(distance)

def test_flat_carry_banded_carry_and_keeper_own():
 for mode,points in [('flat',2),('banded',5)]:
  p=RulebookPort(1,replace(RulebookConfig(),scoring=mode));s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE;s.owner='A'
  s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier='A0',x=101,y=50,z=1.5,scoring=True)
  assert e.goal('B') and s.score['A']==points
 p=RulebookPort(1,replace(RulebookConfig(),scoring='banded'));s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE
 s.ball=p.types.Ball(mode=p.types.BallMode.SHOT,last_releaser='A10',x=-1,y=50,z=1.5,scoring=True)
 assert e.goal('A') and s.score['B']==2

def test_restart_throw_is_an_attempt_once_at_actual_release():
 p=RulebookPort(1);s,e=p.m.s,p.m.e;e.award('A',50,50,'fixture');s.restart.taker='A0'
 for q in s.players.values():
  if q.role!='archer':q.x=40 if q.team=='A' else 60
 s.players['A0'].x=50;s.players['A0'].y=50
 assert e.restart_release('A0',(24,0,1),'A1')
 assert e.rb_attempts[-1]['kind']=='restart_pass' and e.rb_attempts[-1]['distance']==50
 assert len(e.rb_attempts)==1
