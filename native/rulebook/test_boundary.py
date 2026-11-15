import json
from native import cognition as C
from .port import RulebookPort
from .run import run_match

def test_extended_view_replay_and_poison():
 p=RulebookPort(1);s=p.m.s;p.capture(s.now);s.now+=300
 v,b=p.view('A0',s.now);before=C.decide(v,b)
 payload=json.loads(json.dumps(C.view_to_json(v,b)));v2,b2=p.view_from_json(payload)
 assert C.decide(v2,b2)==before
 s.players['B0'].x=-9999;s.ball.z=99999;p.m.e.rb.timeouts['A']=0
 assert C.decide(v,b)==before

def test_premarking_minor_and_zone_line():
 p=RulebookPort(1);s,e=p.m.s,p.m.e;e.award('A',50,50,'fixture');s.restart.taker='A0'
 for q in s.players.values():
  if q.role!='archer':q.x=45 if q.team=='A' else 55;q.y=80
 s.players['A0'].x=50;s.players['A0'].y=50;s.players['B0'].x=51;s.players['B0'].y=50
 assert not e.restart_release('A0',(20,0,1),'A1')
 assert s.players['B0'].minor_count==1 and s.tackle_count==1
 e.award('B',95,50,'zone_residence',fresh=True,normalize=False)
 assert s.restart.x==80

def test_short_integrated_replay():
 a,_=run_match(1,max_steps=100)
 b,_=run_match(1,max_steps=100)
 assert (a['trace_hash'],a['state_hash'])==(b['trace_hash'],b['state_hash'])

def test_restart_intent_inside_placeholder_ball_clearance():
 p=RulebookPort(1);s,e=p.m.s,p.m.e;e.award('A',50,50,'fixture');s.restart.taker='A0'
 for q in s.players.values():
  if q.role!='archer':q.x=45 if q.team=='A' else 55;q.y=80
 s.players['A0'].x=50;s.players['A0'].y=50;s.players['B0'].x=51;s.players['B0'].y=50
 p.capture(s.now);s.now+=300
 v,b=p.view('B0',s.now);intent,_=C.decide(v,b)
 assert intent.kind=='restart_position'
 assert ((intent.aim[0]-50)**2+(intent.aim[1]-50)**2)**.5<5
 # This pins the unresolved incompatibility, not a passing full-match gate.
 assert p.submit(intent)['status']=='accepted'
 assert e.restart_release('A0',(20,0,1),'A1') is False
 assert s.players['B0'].minor_count==1

def test_final_rb_score_and_injury_hooks_cannot_mutate_completed_match():
 p=RulebookPort(1);s,e=p.m.s,p.m.e;s.period=6
 e.add_score('A',1,'half_goal');assert s.phase==p.types.Phase.FINAL
 history=list(e.rb.scores);calls=list(e.rb.calls);now=s.now
 e.add_score('B',9,'release');e.rb_force_injury('A0');e.rb_begin_pause('timeout',45000);e.elapse(1)
 assert s.score=={'A':1,'B':0} and e.rb.scores==history and e.rb.calls==calls
 assert e.rb_pause is None and s.now==now

def test_not_ready_restart_does_not_sanction_marking():
 p=RulebookPort(1);s,e=p.m.s,p.m.e;e.award('A',50,50,'fixture');s.restart.taker='A0'
 s.players['A0'].x=40;s.players['A0'].y=50;s.players['B0'].x=41;s.players['B0'].y=50
 assert not e.ready('A0')
 assert not e.restart_release('A0',(20,0,1),'A1')
 assert s.players['B0'].minor_count==0
