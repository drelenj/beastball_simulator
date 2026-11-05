"""Lead pass with no speed cap.  Receiver starts 60 m downfield and 80 m across (100 m from the passer), 100-speed (38 m/s effective), running in stride.
For each ball speed: the intercept point (receiver position at the ball's arrival), flight time, in bounds?  Ratio = ball speed / 38."""
import sys,os,math,importlib; os.environ['PRISM_I']='1'; sys.path.insert(0,'.')
import scenario_1v2_v0 as SC
p=SC.proc(); P=p['P']; CO=p['CO']
m=CO.match.Match(P.configuration(p['st'],1,P.CALIBRATION)); core=importlib.import_module(CO.match.Match.__module__)
g,k=m.assume['gravity'],m.assume['ball_drag']; o=(0.,0.,1.6); R0=(60.,80.); VR=38.
def at_speed(sp,vx,vy):
    """intercept by scanning arrival time T: ball released at speed sp reaches the receiver's position at T"""
    best=None
    for i in range(1,400):
        T=i*.02; tgt=(R0[0]+vx*T,R0[1]+vy*T,1.8); s=core.launch_for(o,tgt,sp,g,k)
        if s is None: continue
        d=s[1]-T
        if best is None or abs(d)<abs(best[0]): best=(d,T,tgt)
    return best if best and abs(best[0])<.03 else None
dirs={'downfield (+x)':(1,0),'across (+y)':(0,1),'across back (-y)':(0,-1),'away along the throw line':(60/100,80/100)}
print('ball m/s  ratio | '+' | '.join(dirs))
for sp in (40.,60.,80.,114.,150.):
    row=[]
    for d in dirs.values():
        r=at_speed(sp,VR*d[0],VR*d[1])
        row.append('no lead found' if r is None else '%.2fs (%.0f,%.0f)%s'%(r[1],r[2][0],r[2][1],'' if 0<r[2][0]<=100 and 0<r[2][1]<=100 else ' OUT'))
    print('%7.0f  %5.1fx | '%(sp,sp/VR)+' | '.join(row))
print('\nminimum ball speed that catches him IN BOUNDS (field 100 x 100):')
for n,d in dirs.items():
    f=None
    for sp in range(40,401,2):
        r=at_speed(float(sp),VR*d[0],VR*d[1])
        if r and 0<r[2][0]<=100 and 0<r[2][1]<=100: f=(sp,r); break
    print('  %-28s'%n, 'none up to 400 m/s' if not f else '%d m/s = %.1fx, flight %.2fs, catch (%.0f,%.0f)'%(f[0],f[0]/VR,f[1][1],f[1][2][0],f[1][2][1]))
