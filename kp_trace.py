def install(CO):
    M=CO.match.Match; cp=M.c4c_plan
    def cp2(self,p,path,cross,seen,force=False):
        r=cp(self,p,path,cross,seen,force); b=self.s.ball
        if p.id=='B10': print('PLAN now',self.s.now,'seen',seen[:3],'cross',cross and [round(c,2) for c in cross[1:]],'ball',[round(v,2) for v in (b.x,b.y,b.z,b.vx,b.vy,b.vz)],{k:(round(v,2) if isinstance(v,float) else v) for k,v in (r or {}).items() if not isinstance(v,(list,dict))}, 'target',(r or {}).get('target'))
        return r
    M.c4c_plan=cp2
