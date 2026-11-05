import sys,os,math,importlib; os.environ['PRISM_I']='1'; sys.path.insert(0,'.')
import scenario_1v2_v0 as SC
p=SC.proc(); P=p['P']; CO=p['CO']
m=CO.match.Match(P.configuration(p['st'],1,P.CALIBRATION)); core=importlib.import_module(CO.match.Match.__module__)
g,k=m.assume['gravity'],m.assume['ball_drag']
o=(0.,0.,1.6); R0=(60.,80.)
def solve(sp,vx,vy):
    T=2.
    for _ in range(60):
        tgt=(R0[0]+vx*T,R0[1]+vy*T,1.8); s=core.launch_for(o,tgt,sp,g,k)
        if s is None: return None
        if abs(s[1]-T)<1e-3: return T,tgt
        T=.5*T+.5*s[1]
    return None
dirs={'running straight away from the passer (worst case)':(60,80),'running downfield (+x, toward the goal line)':(1,0),'running across the field (+y)':(0,1),'running across, back toward the near side (-y)':(0,-1)}
for vr in (38.,30.):
    print('receiver speed',vr,'m/s (fresh top = 0.88 x rating; 38 = the fastest athlete on the roster)')
    for name,d in dirs.items():
        n=math.hypot(*d); vx,vy=vr*d[0]/n,vr*d[1]/n; res=None
        for sp10 in range(150,401):
            sp=sp10/10.; r=solve(sp,vx,vy)
            if r: res=(sp,r); break
        if res: print('  %-52s min release speed %.1f m/s, flight %.1f s, catch point (%.0f, %.0f)%s'%(name,res[0],res[1][0],res[1][1][0],res[1][1][1],'  OUT OF BOUNDS' if not(0<res[1][1][0]<=100 and 0<res[1][1][1]<=100) else ''))
        else: print('  %-52s no release speed up to 40 m/s works'%name)
sp=40.; s=core.launch_for(o,(60.,80.,1.8),sp,g,k); print('standing receiver 100 m away at 40 m/s: flight %.2f s'%s[1]); 
for sp in (27.,30.,33.3): 
    s=core.launch_for(o,(60.,80.,1.8),sp,g,k); print('standing receiver at %.1f m/s:'%sp, 'flight %.2f s'%s[1] if s else 'out of range')
