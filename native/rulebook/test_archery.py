import pytest,math
from .port import RulebookPort
@pytest.fixture
def p():return RulebookPort(1)

def live(p):
 s,e=p.m.s,p.m.e;s.phase=p.types.Phase.LIVE;e.hunt_cleared=True;e.rb_hunt_running=True
 s.owner='B';e.possession.pp=e.possession.tc='B';e.rb.possession='B'
 for q in s.players.values():
  if q.role!='archer':q.x=80;q.y=80
 s.players['B0'].x=40;s.players['B0'].y=50
 return s,e

def test_speed_quota_any_distance_legal_and_no_tunnelling(p):
 s,e=live(p);a=e.shoot_arrow('A11','B0',(1,0,0))
 assert math.sqrt(a.vx*a.vx+a.vy*a.vy+a.vz*a.vz)==pytest.approx(250)
 a.x=30;a.y=50;a.z=1.5;a.vz=0
 events=p.m.advance_arrows(100)
 assert any(ev.target=='B0' for ev in events)
 # Owner ruling 17 Nov 2026: any offensive player outside the Keeper Zones. B0 at x=60
 # (more than 50 m from A's own end) was illegal under RB-3.1 and is now a legal target.
 s.players['B0'].x=60;minors=s.players['A11'].minor_count
 for _ in range(14):
  s.players['B0'].immune_until=-1;assert e.shoot_arrow('A11','B0',(1,0,0))
 assert s.players['A11'].minor_count==minors
 assert not any(r['event']=='foul' and r['data'].get('reason')=='archery_target' for r in e.log)
 assert e.rb.quotas['A']['arrows']==15
 assert not e.shoot_arrow('A11','B0',(1,0,0))

def test_archer_still_cannot_target_inside_a_keeper_zone_or_non_possessing_team(p):
 s,e=live(p);t=s.players['B0'];t.x,t.y=95.,50.         # inside B's attacked zone (A's own)
 assert not e.shoot_arrow('A11','B0',(1,0,0))
 t.x,t.y=8.,50.;assert not e.shoot_arrow('A11','B0',(1,0,0))   # inside the other Keeper Zone
 t.x,t.y=60.,50.;e.possession.pp=e.possession.tc='A'
 assert not e.shoot_arrow('A11','B0',(1,0,0))

def test_freeze_cap_panel_recovery_and_turnover(p):
 s,e=live(p);q=s.players['B0']
 assert not e.freeze(q.id,panel=False)
 assert e.freeze(q.id,panel=True)
 assert not e.freeze(q.id,panel=True)
 s.now=q.freeze_until+2000;q.x-=3
 assert not e.rb_recovery_ready(q)
 q.x+=6;assert e.rb_recovery_ready(q)
 e.rb.quotas['A']['arrows']=15
 e.possession.pp='A';e.possession.tc='A';e.native_sync()
 assert e.rb.quotas['A']['arrows']==15 and e.rb.quotas['B']['arrows']==0
 e.possession.pp='B';e.possession.tc='B';e.native_sync()
 assert e.rb.quotas['A']['arrows']==0

def test_status_view_is_captured_not_live_truth(p):
 s,e=live(p);q=s.players['B0'];q.freeze_until=s.now+5000;q.immune_until=s.now+15000
 p.capture(s.now);s.now+=300
 v,b=p.view('A11',s.now);assert ('B0','red') in v.status_indicators
 q.freeze_until=0;q.immune_until=0
 assert ('B0','red') in v.status_indicators

def test_five_actual_freezes_then_cap_and_captured_amber(p):
 s,e=live(p)
 for n in range(5):assert e.freeze('B'+str(n))
 assert e.rb.quotas['A']['freezes']==5
 assert not e.freeze('B5')
 q=s.players['B0'];s.now=q.freeze_until
 assert not q.frozen(s.now) and s.now<q.immune_until
 p.capture(s.now);s.now+=300
 v,b=p.view('B0',s.now);assert ('B0','amber') in v.status_indicators
 assert not e.freeze('B0')
 s.now=q.immune_until+1;e.possession.pp=e.possession.tc='A';e.native_sync()
 assert e.rb.quotas['A']['freezes']==5
 e.possession.pp=e.possession.tc='B';e.native_sync()
 assert e.freeze('B0')

@pytest.mark.parametrize('protection',['frozen','immune','keeper'])
def test_illegal_arrow_is_minor_even_if_target_has_contact_protection(p,protection):
 s,e=live(p);target='B10' if protection=='keeper' else 'B0';q=s.players[target]
 q.x,q.y=40,50
 if protection=='frozen':q.freeze_until=s.now+5000
 if protection=='immune':q.immune_until=s.now+10000
 assert not e.shoot_arrow('A11',target,(1,0,0))
 assert s.players['A11'].minor_count==1 and s.players['A11'].major_count==0
 assert e.rb.quotas['A']['arrows']==1

def test_physical_friendly_panel_hit_spends_shooting_team_freeze_quota(p):
 s,e=live(p);a=e.shoot_arrow('A11','B0',(1,0,0));q=s.players['A0'];q.x,q.y=40,50
 e.rb.quotas['B']['freezes']=e.freezes['B']=5
 assert e.freeze(q.id,arrow=a.id)
 assert e.rb.quotas['A']['freezes']==1 and e.rb.quotas['B']['freezes']==5
 assert e.freezes['A']==1 and e.freezes['B']==5
