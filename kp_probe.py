import os,sys;sys.path.insert(0,'.')
import keeper_drill_v0 as K, multiprocessing as mp
jobs=[(D,v,phi,sd) for D,v in ((30,67.1),(40,67.1),(60,101.)) for phi in range(0,181,30) for sd in (1,2)]
with mp.Pool(2,maxtasksperchild=20) as pool: res=pool.map(K.one,jobs,chunksize=4)
import collections; agg=collections.defaultdict(list)
for a,r in res:
    if r: agg[(a[0],a[1])].append((1 if r['goal'] else 0, 1 if r['touch'] else 0))
for k,x in sorted(agg.items()): print(k,'goal %.2f touch %.2f n %d'%(sum(g for g,_ in x)/len(x),sum(t for _,t in x)/len(x),len(x)))
