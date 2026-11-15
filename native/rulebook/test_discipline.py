import pytest
from .port import RulebookPort
@pytest.fixture
def p():return RulebookPort(1)

def test_real_exclusion_shorthanded_until_dead_after_window(p):
 s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE
 e.discipline('A0','major');assert not s.players['A0'].active
 p.fill_cover();assert not s.players['A0'].active
 e.add_score('B',2,'release');assert s.players['A0'].exclusion_ms==120000
 e.elapse(120000,False);assert s.players['A0'].exclusion_ms==0
 assert not s.players['A0'].active
 e.award('A',50,50,'fixture');p.fill_cover();assert s.players['A0'].active
 e.discipline('A0','major');assert s.players['A0'].disqualified
 p.fill_cover();assert not s.players['A14'].active
 s.phase=p.types.Phase.LIVE;e.elapse(120000,False);e.award('A',50,50,'fixture');p.fill_cover()
 assert any(r['kind']=='substitution' and r['outgoing']=='A0' and r['incoming']!='A0' for r in e.rb.calls)

def test_minor_ladder_and_injury_exclusion_exemption(p):
 s,e=p.m.s,p.m.e
 for _ in range(4):e.discipline('A1','minor')
 assert s.players['A1'].exclusion_ms==60000
 e.rb_force_injury('A1');assert 'A1' not in e.rb_slots
 assert s.players['A1'].exclusion_ms==60000
 e.discipline('A1','minor');assert s.players['A1'].disqualified

def test_delay_warning_kick_and_major_goal_line(p):
 s,e=p.m.s,p.m.e;s.owner='A';e.possession.pp='A';s.phase=p.types.Phase.LIVE
 e.foul('A0',reason='delay_of_game');assert s.players['A0'].minor_count==0
 e.foul('A0',reason='delay_of_game');assert s.players['A0'].minor_count==1
 e.release('A2',(1,0,0),'kick');assert s.players['A2'].minor_count==1
 s.players['A3'].x=3;s.players['A3'].y=50
 e.foul('B0','A3','after_whistle');assert s.players['B0'].major_count==1 and s.restart.x==0

def test_defensive_hold_count_plus_and_offside_no_award(p):
 s,e=p.m.s,p.m.e;s.owner='A';e.possession.pp='A';s.tackle_count=0
 e.foul('B0','A4','holding');assert s.tackle_count==1 and s.score=={'A':0,'B':0}
 e.offside('defence');assert s.tackle_count==0 and s.score=={'A':0,'B':0}

@pytest.mark.parametrize('kind',['head','neck','trip','tackle','striking','after_whistle','frozen','immune_keeper'])
def test_rule_layer_major_classification(kind,p):
 from native import cognition as C
 s,e=p.m.s,p.m.e;s.now=1000;s.phase=p.types.Phase.LIVE;s.owner='A';e.possession.pp='A'
 victim='A10' if kind=='immune_keeper' else 'A0'
 if victim=='A10':s.players[victim].x=3;s.players[victim].y=50
 s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier='A1',x=50,y=50,z=1.5,scoring=True)
 reason=kind
 if kind in ('head','neck','trip','tackle'):
  s.players['B0'].native_intent=C.ActionIntent('i','d','B0','press',victim,None,None,None,s.now,contact=kind)
 if kind=='frozen':s.players[victim].freeze_until=s.now+5000;reason='contact'
 if kind=='immune_keeper':reason='contact'
 e.foul('B0',victim,reason)
 assert s.players['B0'].major_count==1 and s.players['B0'].exclusion_ms==120000
 assert s.restart.team=='A'

def test_unintentional_head_is_minor_and_requires_evaluation(p):
 s,e=p.m.s,p.m.e;s.now=1000;s.phase=p.types.Phase.LIVE;s.owner='A';e.possession.pp='A'
 e.foul('B0','A0','head')
 assert s.players['B0'].major_count==0 and s.players['B0'].minor_count==1
 assert not s.players['A0'].active and e.rb.evaluated['A0']==s.period
