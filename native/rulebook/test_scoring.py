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
 p=RulebookPort(1);s,e=p.m.s,p.m.e;s.ball.rb_deliberate_team='B';e.award('A',50,50,'fixture')
 assert s.ball.rb_deliberate_team is None
 s.restart.taker='A0'
 for q in s.players.values():
  if q.role!='archer':q.x=40 if q.team=='A' else 60
 s.players['A0'].x=50;s.players['A0'].y=50
 assert e.restart_release('A0',(24,0,1),'A1')
 assert e.rb_attempts[-1]['kind']=='restart_pass' and e.rb_attempts[-1]['distance']==50
 assert not e.rb_attempts[-1]['shot_attempt']
 assert len(e.rb_attempts)==1
 assert sum(v for k,v in e.rb_bands['A'].items() if k.endswith('_attempts'))==0

def test_keeper_opponent_goal_is_no_goal_ruling():
 p=RulebookPort(1);s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE;s.owner='A'
 s.ball=p.types.Ball(mode=p.types.BallMode.SHOT,x=101,y=50,z=1.5,scoring=True,last_releaser='A10',last_touch='A')
 assert not e.goal('B') and s.score=={'A':0,'B':0}
 assert not any(c['kind']=='goal' for c in e.rb.calls)

def test_bounced_shot_keeps_original_release_band():
 p=RulebookPort(1,RulebookConfig(scoring='banded'));s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE
 s.owner='A';s.players['A0'].x,s.players['A0'].y=75,50
 s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier='A0',x=75,y=50,z=1.5,scoring=True)
 assert e.release('A0',(25,0,-30),'shot')
 p.m.advance_ball(100,{})
 assert s.ball.vz>0 and s.ball.rb_release_band=='20plus'
 s.ball.x,s.ball.y,s.ball.z=101,50,1.5
 assert e.goal('B') and s.score['A']==4
 assert e.rb_bands['A']['20plus_attempts']==e.rb_bands['A']['20plus_goals']==1

def test_interception_carry_is_not_stale_own_goal():
 p=RulebookPort(1,RulebookConfig(scoring='banded'));s,e=p.m.s,p.m.e
 s.phase=p.types.Phase.LIVE;s.owner='B';e.possession.pp='B'
 passer=s.players['B0'];interceptor=s.players['A0'];passer.x=passer.y=50
 s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier=passer.id,x=50,y=50,z=passer.hand_height,scoring=True)
 assert e.release(passer.id,(-5,0,1),'pass','B1')
 s.ball.rb_deliberate_team='B' # regression witness for the removed stale flag
 interceptor.x,interceptor.y=s.ball.x,s.ball.y
 assert e.acquire(interceptor.id)
 assert s.ball.rb_deliberate_team is None
 interceptor.x,interceptor.y=101,50;e.follow_carrier()
 assert e.goal('B') and s.score['A']==5
 assert e.rb_bands['A']['carry_attempts']==e.rb_bands['A']['carry_goals']==1
 assert e.rb_bands['A']['own_goals']==0

def test_defender_deflection_of_shot_is_ordinary_shooter_goal():
 p=RulebookPort(1,RulebookConfig(scoring='banded'));s,e=p.m.s,p.m.e
 s.phase=p.types.Phase.LIVE;s.owner='A';e.possession.pp='A'
 shooter=s.players['A0'];defender=s.players['B0'];shooter.x,shooter.y=75,50
 s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier=shooter.id,x=75,y=50,z=shooter.hand_height,scoring=True)
 assert e.release(shooter.id,(25,0,1),'shot')
 defender.x,defender.y=s.ball.x,s.ball.y;e.touch(defender.id,True)
 assert s.ball.last_releaser is None # a deflection is not a new release
 s.ball.x,s.ball.y,s.ball.z=101,50,1.5
 assert e.goal('B') and s.score['A']==4
 assert e.rb_bands['A']['20plus_goals']==1 and e.rb_bands['A']['own_goals']==0

def test_goal_publishes_one_official_ruling_and_shot_counter_excludes_passes():
 p=RulebookPort(1);s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE;s.owner='A'
 s.ball=p.types.Ball(mode=p.types.BallMode.SHOT,x=101,y=50,z=1.5,scoring=True,last_releaser='A0')
 before=len([r for r in e.rb.calls if r['kind'] in ('goal','no_goal')])
 assert e.goal('B')
 after=len([r for r in e.rb.calls if r['kind'] in ('goal','no_goal')])
 assert after-before==1
