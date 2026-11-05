import os,sys;sys.path.insert(0,'.')
import keeper_drill_v0 as K
out=[]
for phi in range(0,181,30):
    a,r=K.one((60,101.,phi,1)); out.append((phi,r and r['goal'],r and r['touch']))
print(out)
