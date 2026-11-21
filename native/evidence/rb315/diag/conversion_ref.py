"""Attempt conversion by build: shots by distance band and outcome, carries, goals by method, points per attempt."""
import sys, json, collections, math
sys.path.insert(0,'/home/claude/wt310/native/evidence/rb311diag/tools')
from offense_diagnosis import Match
S='/tmp/claude-0/-home-claude/65ce685a-b94d-53f8-bbf7-8c3464c490cd/scratchpad/ep/'
def band(d): return '<10' if d<10 else ('10-20' if d<20 else '20+')
out={}
for b in ('r310','r312','r313'):
    shots=collections.defaultdict(collections.Counter); goals=collections.Counter(); gpts=collections.Counter(); pts=0; teams=0
    keeper_ctl=0
    for blk,seed in (('real',1),('real',3),('real',5)):
        m=Match(S+b+'/soak','/nonexistent',blk,seed); log=m.log; teams+=2
        for i,r in enumerate(log):
            d=r.get('data') or {}
            if r['event']=='goal':
                goals[d['method']]+=1; gpts[d['method']]+=d['points']; pts+=d['points']
            if r['event']=='release' and d.get('kind')=='shot':
                tm=d['player'].split(':')[0]; g=m.gdist(i,tm,r['ball'][0],r['ball'][1]); o='other'
                for e in log[i+1:i+90]:
                    if e['event']=='goal': o='scored'; break
                    if e['event']=='keeper_contact': o='keeper'; break
                    if e['event']=='control':
                        p=e['data']['player']; o='own recovery' if p.split(':')[0]==tm else 'defence'; break
                    if e['event']=='boundary': o='out'; break
                    if e['event']=='restart_awarded': o='award'; break
                shots[band(g)][o]+=1
    final=[ (lambda P: (P['A']['play']+P['A']['penalty_awards'], P['B']['play']+P['B']['penalty_awards']))(None) ] if False else None
    out[b]=dict(goals_by_method=dict(goals), points_by_method=dict(gpts), goal_points_per_team=round(pts/teams,1),
               shots={k:dict(v) for k,v in shots.items()},
               shot_conv={k:round(v['scored']/max(1,sum(v.values())),3) for k,v in shots.items()},
               shots_per_team=round(sum(sum(v.values()) for v in shots.values())/teams,1))
print(json.dumps(out,indent=1))
