"""RB-3.20a DEFECT FIX (native-rb/3, rb320_exact_bounce): exact ball-ground contact inside the engine step.

The inherited kernel (core_src/match.py advance_ball) integrates the free ball over the whole step (100 ms in Native), then,
if the ball ended the step below its radius, clamps it to the surface and reflects the END-of-step vertical velocity with
ball_restitution (stated 0.7745966692 = sqrt(0.6)). The end-of-step velocity carries up to g x dt (0.98 m/s) of fall that
happened BELOW the surface, and the clamp adds the penetration depth back as height. Measured effective restitution was
0.91-1.26 instead of 0.7746 (native/evidence/rb320/ball_scenario.out): balls kept bouncing above the 2 m/s roll threshold
for many seconds and never reached the stated rolling decay. That contradicts the code's own stated restitution: a DEFECT.

Fix: when the ball starts the step in the air and reaches the surface within it, the contact instant is solved
(z0 + vz0 t - g t^2 / 2 = radius), the stated rules are applied AT the contact with the contact velocity (|vz| > 2: reflect
with ball_restitution and keep .76 of the horizontal velocity; otherwise roll: vz = 0 and the stated rolling factor
max(0, 1 - 3 tau) over the rest of the step), and the rest of the step is flown from the surface. A ball already on the
surface at the start of the step keeps the original rules unchanged. Constants (restitution, .76, roll 3/s, 2 m/s threshold,
drag) are NOT changed: they are calibration items (see native/evidence/rb320/PHYSICS.md).
"""
import math


def contact(m, b, dt, pre):
    """Apply the ground rules for a step in which the ball ended at or below the surface. Returns True on a bounce."""
    A = m.assume; g = A['gravity']; e = A['ball_restitution']; k = A['ball_drag']; r = b.radius
    x0, y0, z0, vx0, vy0, vz0 = pre
    if z0 <= r + 1e-9:                                    # on the surface at the start: the original rules, unchanged
        b.z = r
        if abs(b.vz) > 2: b.vz = -b.vz * e; b.vx *= .76; b.vy *= .76; return True
        b.vz = 0; b.vx *= max(0, 1 - dt * 3); b.vy *= max(0, 1 - dt * 3); return False
    tc = min(dt, max(0., (vz0 + math.sqrt(max(0., vz0 * vz0 + 2 * g * (z0 - r)))) / g))
    dc = math.exp(-k * tc)
    xc, yc = x0 + vx0 * tc, y0 + vy0 * tc
    vxc, vyc, vzc = vx0 * dc, vy0 * dc, (vz0 - g * tc) * dc
    tau = dt - tc
    if abs(vzc) > 2:
        vz1 = -vzc * e; vx1, vy1 = vxc * .76, vyc * .76
        d = math.exp(-k * tau)
        b.x, b.y = xc + vx1 * tau, yc + vy1 * tau
        b.z = max(r, r + vz1 * tau - .5 * g * tau * tau)
        b.vx, b.vy, b.vz = vx1 * d, vy1 * d, (vz1 - g * tau) * d
        return True
    f = max(0., 1 - tau * 3)
    b.x, b.y, b.z = xc + vxc * tau, yc + vyc * tau, r
    b.vx, b.vy, b.vz = vxc * f, vyc * f, 0
    return False


PATCHES = [
    ("s=self.s;b=s.ball;dt=ms/1000;events=[]", "s=self.s;b=s.ball;dt=ms/1000;events=[];rb320_bounced=False"),
    ("   drag=math.exp(-self.assume['ball_drag']*dt);b.x+=b.vx*dt",
     "   rb320=(b.x,b.y,b.z,b.vx,b.vy,b.vz)\n   drag=math.exp(-self.assume['ball_drag']*dt);b.x+=b.vx*dt"),
    ("     if abs(b.vz)>2:b.vz=-b.vz*self.assume['ball_restitution'];b.vx*=.76;b.vy*=.76\n     else:b.vz=0;b.vx*=max(0,1-dt*3);b.vy*=max(0,1-dt*3)\n",
     "     rb320_bounced=self.rb320_contact(b,dt,rb320)\n"),
    ("if b.carrier is None and b.mode==BallMode.LOOSE and b.z<=b.radius+1e-9 and b.vz>0 and old[2]>b.radius+1e-9:self.bounce_mark=s.now+ms",
     "if b.carrier is None and b.mode==BallMode.LOOSE and(rb320_bounced or b.z<=b.radius+1e-9 and b.vz>0 and old[2]>b.radius+1e-9):self.bounce_mark=s.now+ms"),
]


GEOMETRY_PATCHES = [
    # predict_path (the free-ball forecast used by receiver routing and the legacy controllers, 50 ms samples): the same rule
    ("  x+=vx*step;y+=vy*step;z+=vz*step-.5*g*step*step;vx*=drag;vy*=drag;vz=(vz-g*step)*drag\n  if z<=b.radius:\n   z=b.radius\n   if abs(vz)>2:vz=-vz*restitution;vx*=.76;vy*=.76\n   else:vz=0;vx*=max(0,1-step*3);vy*=max(0,1-step*3)\n",
     "  pre=(x,y,z,vx,vy,vz)\n  x+=vx*step;y+=vy*step;z+=vz*step-.5*g*step*step;vx*=drag;vy*=drag;vz=(vz-g*step)*drag\n  if z<=b.radius:\n   x,y,z,vx,vy,vz=_rb320_path_contact(pre,x,y,z,vx,vy,vz,step,g,k,restitution,b.radius)\n"),
    ("def intercept_xy(", '''def _rb320_path_contact(pre,x,y,z,vx,vy,vz,step,g,k,restitution,r):
 class _B:pass
 b=_B();b.x,b.y,b.z,b.vx,b.vy,b.vz,b.radius=x,y,z,vx,vy,vz,r
 class _M:pass
 m=_M();m.assume={'gravity':g,'ball_restitution':restitution,'ball_drag':k}
 from native.rulebook.ball_ground import contact
 contact(m,b,step,pre)
 return b.x,b.y,b.z,b.vx,b.vy,b.vz

def intercept_xy('''),
]


def enabled(config):
    return getattr(config, 'version', None) == 'native-rb/3' and getattr(config, 'rb320_exact_bounce', False)


def install(co, cfg):
    if enabled(cfg):
        co.match.Match.rb320_contact = lambda self, b, dt, pre: contact(self, b, dt, pre)
