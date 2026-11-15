"""Rule admission through real contact, movement, projectile and restart paths."""
import pytest
from .port import RulebookPort

@pytest.mark.parametrize('protection',['frozen','keeper','dead'])
def test_contact_admission_routes_breach_to_major(protection):
 p=RulebookPort(1);s,e=p.m.s,p.m.e;s.now=1000;s.phase=p.types.Phase.LIVE
 target='A10' if protection=='keeper' else 'A0';q=s.players[target];a=s.players['B0']
 q.x,q.y=3,50;a.x,a.y=4,50
 e.possession.pp='A';s.owner='A'
 if protection=='frozen':q.freeze_until=6000
 if protection=='dead':e.award('A',50,50,'fixture')
 assert not e.engage(a.id,q.id,'tackle')
 assert a.major_count==1 and a.exclusion_ms==120000 and s.restart.team=='A'
 assert not a.active

def test_recovery_execution_blocks_queued_release_and_forward_zone_entry():
 p=RulebookPort(1);s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE;s.now=10000
 q=s.players['A0'];q.x,q.y=79,50;q.rb_recover=(79,50,9000)
 q.target=(95,50);q.vx=10
 p.m.move_players(100,{'A0':(95,50)})
 assert q.x==79 and q.vx==0
 q.x=82;s.ball=p.types.Ball(mode=p.types.BallMode.CONTROLLED,carrier=q.id,x=82,y=50,z=1.5,scoring=True)
 assert not e.release(q.id,(20,0,1),'shot')
 assert s.ball.carrier==q.id
 q.x=76;s.now=11000;assert e.rb_recovery_ready(q)
 q.x=82; q.rb_recover=(85,50,9000)
 assert e.rb_recovery_ready(q) and e.release(q.id,(20,0,1),'shot')

def test_major_goal_line_scrimmage_can_release():
 p=RulebookPort(1);s,e=p.m.s,p.m.e;s.now=1000;s.phase=p.types.Phase.LIVE
 s.owner='A';e.possession.pp='A';s.players['A0'].x=3;s.players['A0'].y=50
 from native import cognition as C
 s.players['B0'].native_intent=C.ActionIntent('head','d','B0','press','A0',None,None,None,s.now,contact='head')
 assert not e.engage('B0','A0','block',surface='head')
 assert s.restart.x==0
 for q in s.players.values():
  if q.active and q.role!='archer':q.x=0 if q.team=='A' else 10;q.y=80
 r=s.restart;r.taker='A0';s.players['A0'].x,s.players['A0'].y=r.taker_spot
 assert e.restart_release('A0',(20,0,1),'A1')
 assert s.phase==p.types.Phase.LIVE
