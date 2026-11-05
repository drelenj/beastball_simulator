import os,sys;sys.path.insert(0,'.')
import prism_keeper_v0 as PK
cap={}
o=PK.install
def inst(CO,S,sf): cap['S']=S; return o(CO,S,sf)
PK.install=inst
import keeper_drill_v0 as K
for job in ((30,67.1,0,1),(30,67.1,90,1),(30,67.1,45,1),(40,67.1,45,1)):
    a,r=K.one(job); S=cap['S']; print(job, r and (r['goal'],r['touch'], r['flight']), dict(S.kstats), r['dbg'][-1] if r else None)
