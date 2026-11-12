import sys, json, math, copy
from b1.runtime import PhysicalExecutionPort, ObservationProjector, CommandIngress
from b1.core import decide
mode=sys.argv[1]; seed=int(sys.argv[2]); arg=sys.argv[3] if len(sys.argv)>3 else ''
p=PhysicalExecutionPort(seed); s=p.m.s
import prism_ratings_v0
r=prism_ratings_v0.assign(p.roster_overrides,p.roster_names)['A0']
a=s.players['A0']; A1=s.players['A1']; B0=s.players['B0']
if mode=='moved':
    a.x,a.y=70.,20.; a.facing=(-0.6,0.8); p.m.e.follow_carrier()
if mode=='defy':
    B0.y=float(arg)
if mode=='poison':
    # sentinel every hidden attribute of B0 and A1 except body dimensions the sensor legitimately uses
    for q in (A1,B0):
        for k in vars(q.a):
            if k in('height','weight','mass'): continue
            if isinstance(getattr(q.a,k),(int,float)): setattr(q.a,k,0.123456)
        for k in('stamina','fatigue','energy','intent','plan'):
            if hasattr(q,k) and isinstance(getattr(q,k),(int,float)): setattr(q,k,-9.)
if mode=='behind':   # defender moved physically to a place the athlete cannot sense (behind, far)
    B0.x,B0.y=2.,95.
sensor=ObservationProjector(seed,a,r)
out=[]
for t in range(1000,1301,100): sensor.capture(t,s)
s.now=1300
v,b=sensor.deliver(1300,s); i,d=decide(v,b)
print(json.dumps({'mode':mode,'arg':arg,'seed':seed,'self':[v.x,v.y],'true':[a.x,a.y],'contacts':[(c.entity,round(c.x,3),round(c.y,3)) for c in v.contacts],'kind':i.kind,'opts':[(o[0],round(o[3],3)) for o in d['options']]}))
if mode=='moved':
    ok=CommandIngress(p).submit_batch([i])[0][1]; print(ok['status'], ok.get('command') and ok['command'].desired_velocity)
