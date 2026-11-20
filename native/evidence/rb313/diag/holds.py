"""RB-3.11 Part B: how long a carrier holds the ball and how far he advances it (log-only)."""
import os, collections
from offense_diagnosis import Match, med
soak=os.environ['SOAK']; blocks=[tuple((x.split(':')[0],int(x.split(':')[1]))) for x in os.environ['M'].split(',')]
hold=[]; adv=[]; ends=collections.Counter(); adv_by=collections.defaultdict(list)
for b,s in blocks:
    m=Match(soak,'/nonexistent',b,s); log=m.log; cur=None
    for i,r in enumerate(log):
        ev=r['event']; d=r.get('data') or {}
        if ev=='control':
            p=d['player']; tm=p.split(':')[0]; cur=(p,tm,r['live_ms'],r['ball'][0],1 if m.goal(i,tm)>50 else -1); continue
        if cur and ev in ('release','tackle_count','boundary','strip','freeze','goal','restart_awarded'):
            if ev=='freeze' and d.get('player')!=cur[0]: continue
            if ev=='tackle_count' and d.get('target')!=cur[0]: continue
            p,tm,t0,x0,sg=cur; h=r['live_ms']-t0; a=(r['ball'][0]-x0)*sg
            k=('release:'+d.get('kind','?')) if ev=='release' else ev
            ends[k]+=1; hold.append(h); adv.append(a); adv_by[k].append(a); cur=None
n=sum(ends.values())
print('ball holds',n,'median hold s',round(med(hold)/1000,2),'median forward advance m',med(adv))
for k,v in ends.most_common(8): print(f'  ended by {k}: {v} ({round(v/n*100,1)}%), median advance {med(adv_by[k])} m')
import statistics; print('advance quartiles',[round(x,1) for x in statistics.quantiles(adv,n=4)])
