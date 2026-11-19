"""RB-3.11 Part B: carrier motion while holding the ball (observer carrier_track + decisions)."""
import gzip, json, math, sys, collections, statistics as st
def med(x): x=sorted(x); return round(x[len(x)//2],2) if x else None
for f in sys.argv[1:]:
    o=json.load(gzip.open(f,'rt')); tr=o['carrier_track']; dec=o['carrier_decisions']
    # segment by carrier id contiguity
    segs=[]; cur=[]
    for row in tr:
        t,c,x,y,own=row
        if cur and (c!=cur[-1][1] or t-cur[-1][0]>150): segs.append(cur); cur=[]
        cur.append(row)
    if cur: segs.append(cur)
    fwd=[]; lat=[]; dur=[]; spd=[]; vmax=[]
    for s in segs:
        if len(s)<3: continue
        t0,c,x0,y0,own=s[0]; t1,_,x1,y1,_=s[-1]; sg=1 if own<50 else -1   # attack toward 100 if own end is 0
        fwd.append((x1-x0)*sg); lat.append(abs(y1-y0)); dur.append((t1-t0)/1000)
        vs=[math.hypot(s[i+1][2]-s[i][2],s[i+1][3]-s[i][3])/max(1e-3,(s[i+1][0]-s[i][0])/1000) for i in range(len(s)-1)]
        spd.append(st.mean(vs)); vmax.append(max(vs))
    kinds=collections.Counter(d[4] for d in dec)
    aims=[]
    for d in dec:
        if d[4]=='carry' and d[5]:
            try: ax,ay=d[5][0],d[5][1]; aims.append((ax-d[2],ay-d[3]))
            except Exception: pass
    print(o['name'],'segments',len(fwd),'median s',med(dur),'median fwd m',med(fwd),'median lateral m',med(lat),'median mean speed m/s',med(spd),'median peak speed',med(vmax))
    print('  decision kinds',kinds.most_common(8))
    print('  sample carry aims (dx,dy):',[tuple(round(v,1) for v in a) for a in aims[:12]])
    print('  sample decision rows:',json.dumps(dec[:3])[:600])
