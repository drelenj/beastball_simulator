import os,sys;sys.path.insert(0,'.')
import prism_keeper_v0 as PK
cap={}
o=PK.install
def inst(CO,S,sf): cap['S']=S; return o(CO,S,sf)
PK.install=inst
import keeper_drill_v0 as K
a,r=K.one((40,67.1,45,1)); S=cap['S']; print(r and (r['goal'],r['touch']), dict(S.kstats))
for pid,k in S.kprism.items(): print(pid, len(k['obs']), k['obs'][:3], k['obs'][-2:], round(k['pr'].latency_s,3), k['pr'].P['fov_half_deg'], k['pr'].prof['cone_reach_m'])
for pid in ('B10',):
    k=S.kprism[pid]; print([ (o[0], round(o[2],1)) for o in k['obs'][:14]])
