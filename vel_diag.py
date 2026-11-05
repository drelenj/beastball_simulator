import sys, os, math; ARGS=list(sys.argv)
os.environ['PRISM']='0'
import tend_check as T, pocket4_proto as X
P=X.install(X.load_pocket()); M=P.CORE.match.Match; o=M.step; rec={}; last={'t':-1}
def step(self):
    r=o(self); s=self.s
    if s.now//100!=last['t']:
        last['t']=s.now//100
        for p in s.players.values():
            if p.active and p.role=='field' and s.phase.value=='live': rec.setdefault(p.id,[]).append((s.now/1000.,p.x,p.y,p.vx,p.vy))
    return r
M.step=step
over,ex,names=X.make_rosters(T.G.read_csv('Ala_Lady_Reds_input.csv'),T.G.read_csv('Xenar_Dzaku_input.csv'),1)
X.run(P,over,ex,names,off=(),seed=1,short=True)
import statistics as st
for W in (1,3,5):   # compare instantaneous truth velocity with displacement over +-W ticks (centred)
    d=[];sp=[]
    for pid,L in rec.items():
        for i in range(W,len(L)-W):
            t0,x0,y0,_,_=L[i-W]; t1,x1,y1,_,_=L[i+W]
            if t1-t0>.1*2*W*1.5 or t1-t0<=0: continue
            cx,cy=(x1-x0)/(t1-t0),(y1-y0)/(t1-t0); d.append(math.hypot(L[i][3]-cx,L[i][4]-cy)); sp.append(math.hypot(L[i][3],L[i][4]))
    print('window +-%d ticks (%.1fs): n=%d median |v_inst - v_disp| = %.2f m/s, mean %.2f, p90 %.2f, mean speed %.1f'%(W,W*.2,len(d),st.median(d),st.mean(d),sorted(d)[int(.9*len(d))],st.mean(sp)))
