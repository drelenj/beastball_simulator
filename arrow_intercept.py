import sys, math, random
sys.path.insert(0,'.')
exec(open('core_src/geometry.py').read().split('def ballistic')[0].split('\n',1)[0]) if False else None
import importlib.util
def load(name):
    src=open(f'core_src/{name}.py').read()
    return src
# pull ballistic/norm/unit/segment_distance from the real geometry source
ns={}
g=open('core_src/geometry.py').read()
try: exec(compile(g,'geometry','exec'),ns)
except Exception as e:
    import re; print('geometry exec issue',e); raise
ballistic=ns['ballistic']; segment_distance=ns['segment_distance']
G=9.81; DRAG=.06; H=2.54; RAD=.30+197*.00065; BODY=RAD+.045
def real_flight(o,launch,speed,dist_h,dt=.004):
    # time and height when the (dragged) arrow has covered horizontal distance dist_h
    vx,vy,vz=launch; x=y=0.;z=o[2];t=0.;ux=vx/math.hypot(vx,vy)
    while t<6:
        d=math.exp(-DRAG*dt);x+=vx*dt;y+=vy*dt;z+=vz*dt-.5*G*dt*dt;vx*=d;vy*=d;vz=(vz-G*dt)*d;t+=dt
        if math.hypot(x,y)>=dist_h: return t,z
    return t,z
def shoot(speed,rng_m,v=45.,mode='cross',sigma=.00206,ideal=False,dt=.002,rng=random,aware=False):
    o=(0.,0.,.72*H)
    if mode=='cross': pos=(rng_m,0.); vel=(0.,v)
    elif mode=='away': pos=(rng_m,0.); vel=(v,0.)
    else: pos=(rng_m,0.); vel=(-v,0.)
    cx,cy=pos; cvx,cvy=vel; cz=0.; ch=H
    target=(cx,cy,cz+.55*ch)
    ans=None
    for _ in range(3):
        ans=ballistic(o,target,speed,G,False)
        if ans is None: return None
        tt=ans[1]; loss=.5*DRAG*tt
        if ideal: loss=0
        target=(cx+cvx*tt+(cx-o[0])*loss,cy+cvy*tt+(cy-o[1])*loss,cz+.55*ch+DRAG*tt*tt*.6)
    if aware:
        # drag-aware lead: iterate on the real (dragged) flight time and re-aim so the dragged arrow arrives at the point
        T=ans[1]
        for _ in range(8):
            tx,ty=cx+cvx*T,cy+cvy*T; tz=cz+.55*ch
            dh=math.hypot(tx-o[0],ty-o[1])
            zaim=tz
            for _ in range(6):
                sol=ballistic(o,(tx,ty,zaim),speed,G,False)
                if not sol: return None
                Tn,zarr=real_flight(o,sol[0],speed,dh)
                zaim+= (tz-zarr)
            T=Tn
        target=(tx,ty,zaim)
    sol=ballistic(o,target,speed,G,False)
    if not sol: return None
    (vx,vy,vz),flight=sol
    vxy=math.hypot(vx,vy); az=math.atan2(vy,vx)+rng.gauss(0,sigma); el=math.atan2(vz,vxy)+rng.gauss(0,sigma)
    vx,vy,vz=speed*math.cos(el)*math.cos(az),speed*math.cos(el)*math.sin(az),speed*math.sin(el)
    x,y,z=o; t=0.
    while t<6:
        ox,oy,oz=x,y,z; d=math.exp(-DRAG*dt)
        x+=vx*dt;y+=vy*dt;z+=vz*dt-.5*G*dt*dt;vx*=d;vy*=d;vz=(vz-G*dt)*d;t+=dt
        px,py=cx+cvx*t,cy+cvy*t
        # sweep vs target (target position at this t; small dt so point test on segment mid)
        d2,f=segment_distance(px,py,ox,oy,x,y)
        zz=oz+(z-oz)*f
        if d2<BODY and .12*H<=zz<=H: return ('hit',t,math.hypot(vx,vy,vz))
        if z<=0: return ('miss',t,0)
    return ('miss',t,0)
def run(speed,rng_m,n=1500,**k):
    r=random.Random(7); hits=0; fl=[];vi=[];tried=0
    for _ in range(n):
        out=shoot(speed,rng_m,rng=r,**k)
        if out is None: continue
        tried+=1
        if out[0]=='hit': hits+=1; fl.append(out[1]); vi.append(out[2])
    return tried,hits,(sum(fl)/len(fl) if fl else float('nan')),(sum(vi)/len(vi) if vi else float('nan'))
if __name__=='__main__':
    aware=len(sys.argv)>1 and sys.argv[1]=='aware'
    for mode in ('cross','away','toward'):
        for sig,lab in ((.00206,'archer acc .86'),):
            print(f'--- sprinter 45 m/s, {mode}, range 95 m, {lab}, lead={"drag-aware" if aware else "engine (Pocket 2.0)"}')
            for sp in (100,125,150,175):
                t,h,fl,vi=run(sp,95.,n=600 if aware else 1500,mode=mode,sigma=sig,aware=aware)
                print(f'  {sp:>3} m/s: hit {h}/{t} = {100*h/max(t,1):5.1f}%   mean flight {fl:.2f}s  impact speed {vi:.0f} m/s')
