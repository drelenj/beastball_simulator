"""RB-3.21 Beastball ball material (owner ruling 21 Nov 2026: a fictional material; the lead sets drag, bounce, kept horizontal
speed and rolling resistance for realistic-feeling play and the owner's targets). native-rb/3 only; one model used by the
engine step AND every forecast (geometry.predict_path, geometry.launch_for, Match.c4c_path, the Native Keeper's course).

Model (per substep SUB_S, semi-implicit, with the contact instant interpolated inside the substep; RB-3.20a exact contact):
  air:      dv/dt = -k |v| v  - g z^          (quadratic drag, k = rb321_ball_drag_k, 1/m)
  contact:  |vz| > ROLL_VZ_MPS: vz -> -e vz (e = rb321_ball_restitution), horizontal x h (h = rb321_ball_bounce_h)
            otherwise the ball rolls: vz = 0, z = radius
  rolling:  d|v|/dt = -(a_roll + k |v|^2)    (a_roll = rb321_ball_roll_decel, m/s^2, constant)
The 2 m/s roll threshold is the engine's existing rule (core_src/match.py advance_ball), unchanged.
"""
import math

SUB_S = .005
ROLL_VZ_MPS = 2.
G = 9.81


def params(cfg):
    return (cfg.rb321_ball_drag_k, cfg.rb321_ball_bounce_h, cfg.rb321_ball_restitution, cfg.rb321_ball_roll_decel)


def fly(state, dt, P, r, stop_at_ground=False, g=G):
    """Advance (x, y, z, vx, vy, vz) by dt. Returns (state, bounced, reached_ground)."""
    k, h, e, a_roll = P
    x, y, z, vx, vy, vz = state
    n = max(1, int(math.ceil(dt / SUB_S - 1e-9))); hh = dt / n
    bounced = ground = False
    for _ in range(n):
        left = hh
        while left > 1e-12:
            if z <= r + 1e-9 and vz <= 0.:                                  # rolling on the surface
                z, vz = r, 0.
                s = math.hypot(vx, vy)
                if s <= 0.:
                    break
                dec = a_roll + k * s * s
                s1 = max(0., s - dec * left)
                tt = left if s1 > 0 else s / dec
                d = (s + s1) / 2 * tt
                x += vx / s * d; y += vy / s * d
                vx *= s1 / s; vy *= s1 / s
                break
            v = math.sqrt(vx * vx + vy * vy + vz * vz)
            ax, ay, az = -k * v * vx, -k * v * vy, -g - k * v * vz
            z1 = z + vz * left + .5 * az * left * left
            if z1 > r:
                x += vx * left + .5 * ax * left * left; y += vy * left + .5 * ay * left * left; z = z1
                vx += ax * left; vy += ay * left; vz += az * left
                break
            # contact inside this interval: solve z + vz t + az t^2 / 2 = r for the first t
            A2, B, Cc = .5 * az, vz, z - r
            disc = B * B - 4 * A2 * Cc
            tc = (-B - math.sqrt(max(0., disc))) / (2 * A2) if abs(A2) > 1e-12 else (-Cc / B if B < 0 else 0.)
            tc = min(left, max(0., tc))
            x += vx * tc + .5 * ax * tc * tc; y += vy * tc + .5 * ay * tc * tc; z = r
            vx += ax * tc; vy += ay * tc; vz += az * tc
            left -= tc
            ground = True
            if stop_at_ground:
                return (x, y, z, vx, vy, vz), bounced, ground
            if abs(vz) > ROLL_VZ_MPS:
                vz = -vz * e; vx *= h; vy *= h; bounced = True
            else:
                vz = 0.
            if tc <= 0. and vz > 0.:
                # bounced at the start of the interval: continue the rest of the interval in the air
                continue
    return (x, y, z, vx, vy, vz), bounced, ground


def path(state, P, r, horizon, step, lo=-1., hi=101.):
    """Forecast [(t, x, y, z)] with the same model, sampled every `step`, ending where the ball leaves [lo, hi]."""
    t = 0.; out = [(0., state[0], state[1], state[2])]
    while t < horizon - 1e-12:
        state, _, _ = fly(state, step, P, r)
        t += step; out.append((t, state[0], state[1], state[2]))
        if not (lo <= state[0] <= hi and lo <= state[1] <= hi):
            break
        if state[2] <= r + 1e-9 and state[5] == 0. and state[3] == 0. and state[4] == 0.:
            break
    return out


def launch_for(origin, target, speed, P, g=G):
    """Launch velocity of exactly `speed` whose flatter arc passes through `target` (no bounce), with this material's drag.
    Returns (velocity, flight_time) or None when out of range."""
    k = P[0]
    dx, dy = target[0] - origin[0], target[1] - origin[1]
    d = math.hypot(dx, dy); dz = target[2] - origin[2]
    if d < .05 or speed <= 0:
        return None
    ux, uy = dx / d, dy / d

    def miss(theta):
        vh, vz = speed * math.cos(theta), speed * math.sin(theta)
        s, z, t = 0., 0., 0.
        while t < 20.:
            v = math.hypot(vh, vz)
            ah, az = -k * v * vh, -g - k * v * vz
            s1 = s + vh * SUB_S + .5 * ah * SUB_S * SUB_S
            if s1 >= d:
                f = (d - s) / max(s1 - s, 1e-12)
                return z + (vz * SUB_S + .5 * az * SUB_S * SUB_S) * f - dz, t + SUB_S * f
            z += vz * SUB_S + .5 * az * SUB_S * SUB_S; s = s1
            vh += ah * SUB_S; vz += az * SUB_S; t += SUB_S
            if vh <= 1e-3:
                return None, None
        return None, None
    lo, hi = -1.2, math.pi / 4
    elo, _ = miss(lo); ehi, _ = miss(hi)
    if ehi is None or ehi < 0 or elo is None or elo > 0:
        return None
    for _ in range(40):
        mid = (lo + hi) / 2; em, _ = miss(mid)
        if em is None or em < 0: lo = mid
        else: hi = mid
    theta = (lo + hi) / 2; _, t = miss(theta)
    vh = speed * math.cos(theta)
    return (vh * ux, vh * uy, speed * math.sin(theta)), t


# ------------------------------------------------------------------ source patches (applied by native/substrate.py)
def _between(text, start, end):
    i = text.index(start); j = text.index(end, i)
    return text[i:j]


def match_patches(root):
    src = (root / 'core_src' / 'match.py').read_text()
    step_old = _between(src, "   drag=math.exp(-self.assume['ball_drag']*dt);b.x+=b.vx*dt", "  #Interpolate complete-ball boundary crossings")
    step_new = ("   rb321_flight=s.phase==Phase.FLIGHT or s.phase==Phase.PENALTY and s.penalty.get('released')\n"
                "   rb320_bounced,rb321_ground=self.rb321_fly(b,dt,rb321_flight)\n"
                "   if rb321_flight and rb321_ground:events.append(Event('ground',None,data={'ball_ground':True}));b.z=b.radius\n"
                "   elif not rb321_flight and b.z<=b.radius+1e-9:b.z=b.radius;b.mode=BallMode.LOOSE\n")
    c4c_old = _between(src, " def c4c_path(self,b,horizon=3.,step=.005):", " def c4c_threat(self,p,path):")
    c4c_new = (" def c4c_path(self,b,horizon=3.,step=.005):\n"
               "  \"\"\"RB-3.21: the ball's flight forecast with the Beastball ball material (native/rulebook/ball_material.py), 5 ms samples.\"\"\"\n"
               "  return self.rb321_path(b,horizon,step,-2.,102.)\n")
    return [("s=self.s;b=s.ball;dt=ms/1000;events=[]", "s=self.s;b=s.ball;dt=ms/1000;events=[];rb320_bounced=False"),
            (step_old, step_new),
            ("if b.carrier is None and b.mode==BallMode.LOOSE and b.z<=b.radius+1e-9 and b.vz>0 and old[2]>b.radius+1e-9:self.bounce_mark=s.now+ms",
             "if b.carrier is None and b.mode==BallMode.LOOSE and(rb320_bounced or b.z<=b.radius+1e-9 and b.vz>0 and old[2]>b.radius+1e-9):self.bounce_mark=s.now+ms"),
            (c4c_old, c4c_new)]


def geometry_patches(root, P):
    src = (root / 'core_src' / 'geometry.py').read_text()
    pp_old = _between(src, "def predict_path(", "def intercept_xy(")
    lf_old = _between(src, "def launch_for(", "def predict_path(")
    pp_new = ("def predict_path(b,g=9.81,k=.015,restitution=.7745966692,horizon=3.0,step=.05):\n"
              " \"\"\"RB-3.21: sampled future path with the Beastball ball material (the engine's own model); g, k and restitution\n"
              " arguments are ignored in favour of the configured material.\"\"\"\n"
              " key=(b.x,b.y,b.z,b.vx,b.vy,b.vz)\n"
              " cache=getattr(b,'_path_cache',None)\n"
              " if cache and cache[0]==key:return cache[1]\n"
              " from native.rulebook.ball_material import path as _p\n"
              f" path=_p(key,{tuple(P)!r},b.radius,horizon,step,-1.,101.)\n"
              " b._path_cache=(key,path);return path\n\n")
    lf_new = ("def launch_for(origin,target,speed,g=9.81,k=.015):\n"
              " \"\"\"RB-3.21: launch velocity for the Beastball ball material (quadratic drag); g and k arguments are ignored.\"\"\"\n"
              " from native.rulebook.ball_material import launch_for as _l\n"
              f" return _l(origin,target,speed,{tuple(P)!r})\n\n")
    return [(lf_old, lf_new), (pp_old, pp_new)]


def enabled(config):
    return getattr(config, 'version', None) == 'native-rb/3' and getattr(config, 'rb321_ball_material_enabled', False)


def install(co, cfg):
    if not enabled(cfg):
        return
    P = params(cfg)
    M = co.match.Match

    def rb321_fly(self, b, dt, stop):
        st, bounced, ground = fly((b.x, b.y, b.z, b.vx, b.vy, b.vz), dt, P, b.radius, stop_at_ground=stop, g=self.assume['gravity'])
        b.x, b.y, b.z, b.vx, b.vy, b.vz = st
        return bounced, ground
    M.rb321_fly = rb321_fly
    M.rb321_path = lambda self, b, horizon, step, lo, hi: path((b.x, b.y, b.z, b.vx, b.vy, b.vz), P, b.radius, horizon, step, lo, hi)
