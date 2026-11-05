import os,sys;sys.path.insert(0,'.')
import prism_keeper_v0 as PK
orig=PK.install
def inst(CO,S,sf):
    orig(CO,S,sf); M=CO.match.Match
    kb=M.kp_ball; cp=M.c4c_plan; ct=M.c4c_threat
    def kb2(self,p,b,seen):
        r=kb(self,p,b,seen)
        if p.id=='B10': print('BELIEF now',self.s.now,'est',[round(getattr(r,a),2) for a in 'x y z vx vy vz'.split()],'TRUE',[round(getattr(b,a),2) for a in 'x y z vx vy vz'.split()])
        return r
    def cp2(self,p,path,cross,seen,force=False):
        r=cp(self,p,path,cross,seen,force)
        if p.id=='B10': print('PLAN',self.s.now,cross and [round(c,2) for c in cross[1:]], r and {k:(round(v,2) if isinstance(v,float) else v) for k,v in r.items() if not isinstance(v,(list,dict,tuple)) or k=='target'})
        return r
    M.kp_ball=kb2; M.c4c_plan=cp2
PK.install=inst
import keeper_drill_v0 as K
for job in ((30,67.1,0,1),):
    a,r=K.one(job); print(job, r and (r['goal'],r['touch'],r['flight']))
