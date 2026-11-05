import os,sys;sys.path.insert(0,'.')
import prism_keeper_v0 as PK
cap={}
o=PK.install
def inst(CO,S,sf): cap['S']=S; return o(CO,S,sf)
PK.install=inst
import keeper_drill_v0 as K
a,r=K.one((40,67.1,int(os.environ.get("PHI","0")),1)); S=cap['S']; print(dict(S.kstats))
for pid,k in S.kprism.items(): print(pid,'course_n',k['course_n'],'t',k['course_t'],'nobs',len(k['obs']),[ (o[0],round(o[2],1)) for o in k['obs'][:6]])
