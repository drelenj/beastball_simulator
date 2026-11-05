import os,sys;sys.path.insert(0,'.')
import prism_keeper_v0 as PK
orig=PK.install
def inst(CO,S,sf):
    orig(CO,S,sf); M=CO.match.Match; r0=M.kp_ready
    def kr(self,p,b,seen):
        k=S.kprism.get(p.id); ok=r0(self,p,b,seen)
        if p.id=='B10': print('ready?',ok,'now',self.s.now,'seen',seen[:3],'nobs',len(k['obs']) if k else None,[ (o[0],round(o[1])) for o in (k['obs'][-6:] if k else [])])
        return ok
    M.kp_ready=kr
PK.install=inst
import keeper_drill_v0 as K
a,r=K.one((30,67.1,45,1)); print(r and (r['goal'],r['touch']))
