"""RB-3.21 material parameter grid search (coarse; the fine pass is the same with the finer grids in the docstring of SUMMARY). Run: PYTHONPATH=. python3 native/evidence/rb321/material_search.py"""
import math, itertools, json
from native.rulebook.ball_material import fly, launch_for
r=.1075
def rest(st, P, dt=.1, t_max=20.):
    t=0.
    while t<t_max:
        st,_,_=fly(st,dt,P,r);t+=dt
        if st[2]<=r+1e-9 and st[5]==0 and math.hypot(st[3],st[4])<1e-9: return st[0]
    return 999.
def shot_keep(P):
    st=(0.,0.,1.5,58.,0.,0.)
    s=0.
    while True:
        st2,_,g=fly(st,.005,P,r,stop_at_ground=True)
        if st2[0]>=20: return math.hypot(st2[3],st2[5])/58.
        if g: return 0.
        st=st2
def evaluate(P):
    b1=rest((0.,0.,1.5,35.,0.,0.),P); b2=rest((0.,0.,1.5,50.,0.,0.),P)
    v=launch_for((0.,0.,1.5),(8.,0.,1.6),20.,P)
    b4=rest((0.,0.,1.5,v[0][0],0.,v[0][2]),P)
    b3=shot_keep(P)
    return b1,b2,b3,b4
def ok(m): return 38<=m[0]<=45 and m[1]<=60 and m[2]>=.9 and m[3]<=25
def cost(P):
    k,h,e,a=P
    return (abs(h-.76)/.76)**2+(abs(e-.7745966692)/.7745966692)**2+(k/.00527)**2+(math.log(a/3.))**2
res=[]
for k in (0.,.001,.002,.003,.004,.005):
  for h in (.3,.4,.5,.55,.6,.65,.7,.76):
    for e in (.3,.4,.5,.55,.6,.65,.7,.7746):
      for a in (1.,2.,3.,4.,5.,6.,8.,10.,12.,15.):
        P=(k,h,e,a);m=evaluate(P)
        if ok(m): res.append((round(cost(P),4),P,[round(x,3) for x in m]))
res.sort()
print(len(res))
for x in res[:15]: print(x)
