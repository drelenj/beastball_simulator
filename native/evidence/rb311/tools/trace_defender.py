import sys,math;sys.path.insert(0,'/home/user/beastball_simulator');sys.path.insert(0,'/home/user/beastball_simulator/native/evidence/rb311/tools')
from native.run import run_match
from native.nbl_roster import load_canon_nbl
from native.rulebook.port import RulebookPort
from native.rulebook.config import RulebookConfigV3
from native import cognition as C
rosters=load_canon_nbl(('Garvian Guardians','Ala Apex'))
cfg=RulebookConfigV3(roster_digests=tuple(rosters[t].digest for t in ('A','B')))
p=RulebookPort(1,cfg,rosters=rosters);s=p.m.s
WHO='A:NBL24-07-02';T0,T1=int(sys.argv[1])-6500,int(sys.argv[1])+200
od=C.decide;rows=[]
def dec(v,b):
    i,r=od(v,b)
    if v.athlete==WHO and T0<=s.live_ms<=T1:
        q=s.players[WHO];opp=[t for t in b.tracks if t.team=='B' and t.role=='field']
        no=min(opp,key=lambda t:math.hypot(t.x-q.x,t.y-q.y),default=None)
        rows.append((s.live_ms,v.zone_elapsed_ms,round(q.x,1),round(q.y,1),round(math.hypot(q.x,q.y-50),1),i.kind,i.aim,r.get('rb311'),r.get('rb36'),round(math.hypot(no.x-q.x,no.y-q.y),1) if no else None,v.signals.passive_team))
    return i,r
C.decide=dec
try:run_match(1,cfg,max_steps=int(sys.argv[2]),rosters=rosters,port_factory=lambda *a,**k:p)
except Exception as ex:print(ex)
for r in rows:print(r)
