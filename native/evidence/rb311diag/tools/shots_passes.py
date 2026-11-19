"""RB-3.11 Part B: shot distances/outcomes and pass outcomes by context (log-only)."""
import sys, json, math, collections
sys.argv=[sys.argv[0]]+sys.argv[1:]
from offense_diagnosis import Match, med
import os
soak=os.environ['SOAK']; blocks=[tuple((x.split(':')[0],int(x.split(':')[1]))) for x in os.environ['M'].split(',')]
sd=[]; sres=collections.Counter(); band=collections.defaultdict(collections.Counter)
pres=collections.Counter(); pdist=[]
for b,s in blocks:
    m=Match(soak,'/nonexistent',b,s); log=m.log
    for i,r in enumerate(log):
        d=r.get('data') or {}
        if r['event']=='release' and d.get('kind')=='shot':
            tm=d['player'].split(':')[0]; x,y=r['ball'][0],r['ball'][1]; g=m.gdist(i,tm,x,y)
            out=None
            for q in range(i+1,min(len(log),i+80)):
                e=log[q]
                if e['event'] in ('goal','rb_goal'): out='scored'; break
                if e['event']=='control':
                    out='own recovered' if e['data']['player'].split(':')[0]==tm else ('keeper' if '-K' in e['data']['player'] or e['data']['player'].endswith(('01','02')) and False else 'defence recovered'); break
                if e['event']=='boundary': out='out'; break
                if e['event']=='restart_awarded': out='award:'+e['data']['reason']; break
            sd.append(g); sres[out]+=1
            bb='<10' if g<10 else ('10-15' if g<15 else ('15-20' if g<20 else ('20-32' if g<32 else '32+')))
            band[bb][out]+=1
print('shots',len(sd),'median dist',med(sd)); print(' outcomes',sres.most_common())
for k in ['<10','10-15','15-20','20-32','32+']:
    n=sum(band[k].values()); 
    if n: print(f'  {k}: n={n} scored={band[k]["scored"]} ({round(band[k]["scored"]/n*100)}%)', dict(band[k]))
