import os,sys;sys.path.insert(0,'.')
import prism_keeper_v0 as PK
orig=PK.install
def inst(CO,S,sf):
    orig(CO,S,sf); M=CO.match.Match
    for nm in ('kp_noticed','kp_tobs','kp_ready','kp_react'):
        f=getattr(M,nm)
        def w(self,*a,_f=f,_n=nm,**k):
            r=_f(self,*a,**k)
            if a and getattr(a[0],'id','')=='B10' or _n=='kp_tobs': print(_n,self.s.now,r if not isinstance(r,float) else round(r,1), (a[2][:3] if _n in('kp_ready','kp_noticed') and a[2] else ''))
            return r
        setattr(M,nm,w)
PK.install=inst
import keeper_drill_v0 as K
for phi in (0,30):
    print('--- phi',phi); a,r=K.one((40,67.1,phi,1)); print(r and (r['goal'],r['touch']))
