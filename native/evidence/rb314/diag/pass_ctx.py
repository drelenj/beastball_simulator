"""RB-3.11 Part B: open-play pass outcomes by context and direction (log-only)."""
import os, json, math, collections
from offense_diagnosis import Match
soak=os.environ['SOAK']; blocks=[tuple((x.split(':')[0],int(x.split(':')[1]))) for x in os.environ['M'].split(',')]
res=collections.defaultdict(collections.Counter); spd=collections.defaultdict(list)
for b,s in blocks:
    m=Match(soak,'/nonexistent',b,s); log=m.log; last_snap=-1e9
    for i,r in enumerate(log):
        if r['event']=='snap_hold_released': last_snap=r['live_ms']
        d=r.get('data') or {}
        if r['event']!='release' or d.get('kind')!='pass': continue
        tm=d['player'].split(':')[0]; sign=1 if m.goal(i,tm)>50 else -1
        fwd='forward' if d['velocity'][0]*sign>0.5*math.hypot(d['velocity'][0],d['velocity'][1]) else ('lateral' if d['velocity'][0]*sign>-0.5*math.hypot(*d['velocity'][:2]) else 'backward')
        ctx=('post-snap<3s' if r['live_ms']-last_snap<3000 else 'open')+'/'+fwd
        out='other'
        for q in range(i+1,min(len(log),i+80)):
            e=log[q]
            if e['event']=='control':
                p=e['data']['player']; out='to target' if p==d.get('target') else ('own other' if p.split(':')[0]==tm else 'intercepted'); break
            if e['event']=='boundary': out='out'; break
            if e['event']=='restart_awarded': out='award'; break
        res[ctx][out]+=1
for c in sorted(res):
    n=sum(res[c].values()); bad=res[c]['intercepted']+res[c]['out']
    print(f'{c:28s} n={n:4d} fail={round(bad/n*100,1)}%', dict(res[c]))
tot=collections.Counter()
for c in res: tot.update(res[c])
n=sum(tot.values()); print('ALL n',n,'fail',round((tot['intercepted']+tot['out'])/n*100,1),'%',dict(tot))
