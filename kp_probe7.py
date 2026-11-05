import os,sys;sys.path.insert(0,'.')
import keeper_drill_v0 as K, collections
agg=collections.defaultdict(list)
for D,v in ((30,67.1),(40,67.1),(60,101.)):
    for phi in range(0,181,30):
        for sd in (1,2):
            a,r=K.one((D,v,phi,sd)); agg[(D,v)].append((int(r['goal']),int(r['touch'])))
for k,x in agg.items(): print(k,'goal %.2f touch %.2f n %d'%(sum(g for g,_ in x)/len(x),sum(t for _,t in x)/len(x),len(x)))
