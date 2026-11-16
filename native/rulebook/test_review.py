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

@pytest.mark.parametrize('period',[1,2,4,6])
def test_review_reverses_wrong_goal_during_break_or_after_final(period):
 p=RulebookPort(1);s,e=p.m.s,p.m.e;s.period=e.rb.period=period
 s.phase=p.types.Phase.LIVE;s.owner='A';s.game_ms=0 if period<6 else 1000
 s.ball=p.types.Ball(mode=p.types.BallMode.SHOT,x=100+s.ball.radius-.1,y=50,z=1.5,scoring=True,last_releaser='A0')
 call=e.rb_force_goal_call('B',True)
 assert s.phase in (p.types.Phase.DEAD,p.types.Phase.FINAL)
 if period<4:assert e.rb_pause and e.rb_pause['kind']=='break'
 else:assert s.phase==p.types.Phase.FINAL
 assert e.rb_review('B',call)
 assert s.score['A']==0 and s.phase==p.types.Phase.DEAD and s.period==period
 assert e.rb_pause is None and s.result is None
 # Correction resumes through normal period/OT machinery, not a forced result.
 e.resolve_timers()
 assert s.phase!=p.types.Phase.FINAL
 assert not e.rb_review('B',call)

def test_lost_review_in_halftime_costs_old_half_resources_only():
 p=RulebookPort(1);s,e=p.m.s,p.m.e;s.period=e.rb.period=2
 s.phase=p.types.Phase.LIVE;s.owner='A';s.game_ms=0
 s.ball=p.types.Ball(mode=p.types.BallMode.SHOT,x=101,y=50,z=1.5,scoring=True,last_releaser='A0')
 assert e.goal('B');call=max(e.rb_evidence)
 assert s.period==3 and e.rb_pause
 assert not e.rb_review('B',call)
 assert e.rb.timeouts['B']==2 and e.rb.challenges['B']==1

def test_final_correct_goal_can_be_reviewed_and_stands():
 p=RulebookPort(1);s,e=p.m.s,p.m.e;s.period=e.rb.period=6;s.phase=p.types.Phase.LIVE
 s.ball=p.types.Ball(mode=p.types.BallMode.SHOT,x=101,y=50,z=1.5,scoring=True,last_releaser='A0')
 assert e.goal('B');assert s.phase==p.types.Phase.FINAL
 assert not e.rb_review('B',max(e.rb_evidence))
 assert s.result['winner']=='A' and e.rb.challenges['B']==0

def test_natural_review_evidence_always_calls_actual_state():
 p=RulebookPort(1);s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE;s.owner='A'
 s.ball=p.types.Ball(mode=p.types.BallMode.SHOT,x=101,y=50,z=1.5,scoring=True,last_releaser='A0')
 assert e.goal('B')
 evidence=e.rb_evidence[max(e.rb_evidence)]
 assert evidence.called==evidence.actual==True
