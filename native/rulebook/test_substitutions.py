import pytest
from .port import RulebookPort
@pytest.fixture
def p():return RulebookPort(1)

def test_field_limit_archer_exempt_dead_only_and_returns(p):
 s,e=p.m.s,p.m.e
 assert sum(q.active and q.role!='archer' and q.team=='A' for q in s.players.values())==12
 s.phase=p.types.Phase.LIVE
 assert not e.rb_substitute('A0','A14')
 e.award('A',50,50,'fixture');play=s.possession_ms;now=s.now
 assert e.rb_substitute('A0','A14') and e.rb_substitute('A14','A0')
 assert (s.now,s.possession_ms)==(now,play)
 assert e.rb_substitute('A11','A14',role='archer')
 p.assert_invariants()

def test_injury_stops_clocks_and_immediate_cover(p):
 s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE;s.owner='A';play=s.possession_ms
 assert e.rb_force_injury('A0');assert s.phase==p.types.Phase.DEAD
 assert not s.players['A0'].active and s.players['A0'].injured
 assert s.possession_ms==play
 assert sum(q.active and q.role!='archer' and q.team=='A' for q in s.players.values())==12
 assert any(r['kind']=='substitution' and r['injury_exempt'] for r in e.rb.calls)

def test_head_evaluation_and_named_keeper(p):
 s,e=p.m.s,p.m.e;e.rb_force_injury('A10',head=True)
 assert s.players['A13'].active and s.players['A13'].role=='keeper'
 assert not e.rb_can_enter(s.players['A10'])
 s.score={'A':0,'B':0};e.end_period();p.advance_intermission()
 assert e.rb_can_enter(s.players['A10'])

def test_keeper_fallback_without_reserve(p):
 s,e=p.m.s,p.m.e
 for q in s.players.values():
  if q.team=='A' and not q.active:q.available=False
 e.rb_force_injury('A10')
 assert any(q.active and q.team=='A' and q.role=='keeper' for q in s.players.values())
 assert any(r['kind']=='keeper_fallback' for r in e.rb.calls)

def test_exclusion_cannot_be_bypassed_with_empty_slot_or_role_change(p):
 s,e=p.m.s,p.m.e;e.discipline('A0','major');e.award('A',50,50,'fixture')
 assert not e.rb_substitute(None,'A14')
 assert not e.rb_substitute(None,'A14',setup=True)
 assert not e.rb_substitute('A0','A14')
 assert not e.rb_substitute('A1','A14',role='keeper')
 assert e.rb_substitute('A1','A14')
 assert sum(q.active and q.team=='A' and q.role!='archer' for q in s.players.values())==11
