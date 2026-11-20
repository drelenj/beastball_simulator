"""RB-3.10 observer: shot conversion vs lane clearance at release (positions from observer snaps).
Lane clearance = min distance of any opposing non-keeper field player to the segment shooter->goal centre."""
import gzip, json, math, collections, glob
def seg_d(px,py,ax,ay,bx,by):
    dx,dy=bx-ax,by-ay; L2=dx*dx+dy*dy; t=max(0,min(1,((px-ax)*dx+(py-ay)*dy)/L2)) if L2 else 0
    return math.hypot(px-ax-t*dx,py-ay-t*dy), t
rows=[]
for f in sorted(glob.glob('/home/claude/wt310/native/evidence/rb311diag/observe/observe-real-seed0*.json.gz')):
    o=json.load(gzip.open(f,'rt'))
    seed=int(f.split('seed')[1][:2]); log=json.load(open(f'/home/claude/wt310/native/evidence/rb310/runs/real/raw-real-seed{seed:02d}.json'))['log']
    byid={s['id']:s for s in o['snaps']}
    for i,r in enumerate(log):
        d=r.get('data') or {}
        if r['event']!='release' or d.get('kind')!='shot' or r['id'] not in byid: continue
        sn=byid[r['id']]; tm=d['player'].split(':')[0]; gx=100-sn['ends'][tm]; gy=50.
        me=next(p for p in sn['players'] if p[0]==d['player']); ax,ay=me[3],me[4]
        opp=[p for p in sn['players'] if p[1]!=tm and p[2]=='f' and not p[5]]
        clear=min((seg_d(p[3],p[4],ax,ay,gx,gy)[0] for p in opp if seg_d(p[3],p[4],ax,ay,gx,gy)[1]>0.02), default=30.)
        dist=math.hypot(gx-ax,gy-ay)
        out='other'
        for e in log[i+1:i+90]:
            if e['event']=='goal': out='scored'; break
            if e['event']=='keeper_contact': out='keeper'; break
            if e['event']=='control':
                pid=e['data']['player']; role=next((q[2] for q in sn['players'] if q[0]==pid),'?')
                out='own' if pid.split(':')[0]==tm else ('keeper' if role=='k' else 'defence'); break
            if e['event'] in ('boundary','restart_awarded'): out='out/award'; break
        rows.append((clear,dist,out))
print('shots with positions',len(rows)); print('overall',collections.Counter(r[2] for r in rows))
for lo,hi in [(0,2),(2,4),(4,6),(6,9),(9,99)]:
    sub=[r for r in rows if lo<=r[0]<hi]; n=len(sub)
    if n: c=collections.Counter(r[2] for r in sub); print(f'lane clearance {lo}-{hi} m: n={n} scored {round(c["scored"]/n*100)}% blocked-by-defence {round(c["defence"]/n*100)}% keeper {round(c["keeper"]/n*100)}%  median dist {round(sorted(r[1] for r in sub)[n//2],1)}')
