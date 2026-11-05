import os,sys;sys.path.insert(0,'.')
import prism_keeper_v0 as PK
cap={}
o=PK.install
def inst(CO,S,sf): cap['S']=S; return o(CO,S,sf)
PK.install=inst
import keeper_drill_v0 as K
for phi in (0,30,60,90,120,150,180):
    a,r=K.one((40,67.1,phi,1)); S=cap['S']; k=S.kprism['B10']
    print(phi, r and (r['goal'],r['touch']), 'course_n',k['course_n'],'used',k['course_used'],'t',k['course_t'], dict(S.kstats))
