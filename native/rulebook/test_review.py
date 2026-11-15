import pytest
from .port import RulebookPort

@pytest.mark.parametrize('margin,reverse',[(.049,False),(.05,False),(.051,True)])
def test_wrong_goal_threshold_and_corrected_restart(margin,reverse):
 p=RulebookPort(1);s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE;s.owner='A'
 s.ball=p.types.Ball(mode=p.types.BallMode.SHOT,x=100+s.ball.radius-margin,y=50,z=1.5,scoring=True,last_releaser='A0')
 call=e.rb_force_goal_call('B',True);assert s.score['A']==2
 # Live-state poisoning cannot alter recorded evidence.
 s.ball.x=-900
 assert e.rb_review('A',call)==reverse
 assert s.score['A']==(0 if reverse else 2)
 assert e.rb.challenges['A']==(1 if reverse else 0)
 assert s.phase==p.types.Phase.DEAD

def test_boundary_review_scope_and_keeper_binary():
 p=RulebookPort(1);s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE;s.owner='A';s.ball.x=50;s.ball.y=99
 call=e.rb_force_boundary_call(True,scoring_play=False);assert not e.rb_review('A',call)
 s.phase=p.types.Phase.LIVE;s.players['A10'].x=25;s.players['A10'].y=50
 call=e.rb_force_keeper_call('B0','A10',True)
 assert e.rb_review('A',call)
 assert s.players['B0'].major_count==0
 assert e.rb_can_enter(s.players['B0']) and 'B0' not in e.rb_slots
 assert not e.rb_review('A',99999)

def test_reversed_wrong_goal_outside_semicircle_is_toss_to_other_team():
 p=RulebookPort(1);s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE;s.owner='A'
 s.ball=p.types.Ball(mode=p.types.BallMode.SHOT,x=101,y=55,z=1.5,scoring=True,last_releaser='A0',last_touch='A')
 call=e.rb_force_goal_call('B',True);assert e.rb_review('A',call)
 assert s.score['A']==0 and s.restart.kind=='toss' and s.restart.team=='B'

def test_review_no_goal_reversed_to_keeper_own_goal():
 p=RulebookPort(1);s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE;s.owner='A'
 s.ball=p.types.Ball(mode=p.types.BallMode.SHOT,x=-1,y=50,z=1.5,scoring=True,last_releaser='A10',last_touch='A')
 call=e.rb_force_goal_call('A',False);assert e.rb_review('B',call)
 assert s.score['B']==2
