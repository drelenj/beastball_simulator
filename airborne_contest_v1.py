"""Airborne contest v1: one model for every contest over a ball in flight (pass, shot, kick, juggle, loose ball).  ALL DIALS PROVISIONAL.

WHY ONE MODEL: a catch, a defender's swat, a header, a foot on a juggled ball and a jump ball are the same question: can a limb of player A be where the ball is, at a moment when A is ready, before player B can?  Only the limb, the intent and the result of the touch differ.

PIECES
  flight(...)      ball path with Pocket's drag, gravity, restitution; records every field contact (feeds the foot rule).
  plan(...)        what a player can reach: for each moment the ball passes, a constant-acceleration run to a body spot, a jump if the ball is above his standing reach, ending with the limb on the ball.
                   Feasibility = needed acceleration <= his acceleration (fatigue-scaled), speed <= top, lift needed <= his jump rise, takeoff early enough (crouch).
  Traj             the plan as a function of time.  A jump cannot be steered: once off the ground the horizontal velocity is frozen and the lift is ballistic (Pocket's launched Keeper).
  resolve(...)     the contest.  Everyone plans from the same observation instant; each sweeps the ball path with his limb; HANDS must be 'set' (Pocket: P = 1 - exp(-(t - t_obs)/tau), tau = 0.12*(1.3-0.6*awareness)),
                   the contact is at the closest approach (or when set, if later), the EARLIEST contact in the contest is the one acted on; a catch is secure with Pocket's energy test; an unsecured touch,
                   a swat, a header or a foot deflects the ball, the flight restarts from the contact, and everyone who is not already in the air re-plans.

LIMBS   catch/swat: hand sphere centre 0.80 h, radius reach + 0.2 (reach = 0.46 h, the 0.2 is Pocket's slack);  foot: centre 0.25 h, radius 0.28 h;  head: centre 0.95 h, radius 0.40 m.
JUMP    COM lift = JUMP_RISE_MAX * jump_rating * fatigue (absolute: the same rating gives the same lift whatever the height, a taller player's hands are simply higher: canon).  Ballistic.
READING a player starts to move move_delay = 0.35 - 0.20*awareness after the ball last changed course (the intended receiver sees the passer prepare: pre_s earlier); he aims where he reads the ball, with aim noise 0.05 + 0.30*(1-awareness) m;
        takeoff timing noise 0.02 + 0.08*(1-timing) s, timing = mean(catching, awareness).
SECURE  capacity = 1100 N * 0.6 m * (0.4 + 0.9 catching) * (1 - miss^2) / catch_multiplier(shape);  E = 0.5 m v_rel^2;  P(secure) = 1/(1 + (E/capacity)^2)       (Pocket's, with the shape factor from ball_handling_v1)
        an unsecured catch keeps 0.2 of the relative speed, turned by U(-1.05, 1.05) rad (Pocket's).
"""
import math, random
from dataclasses import dataclass, field
import throwing_v1 as T, ball_handling_v1 as BH, kicking_v1 as K

G = T.G; BALL_R = T.BALL_D / 2; BALL_M = T.BALL_MASS
C_DRAG = T.AIR_POCKET * T._c_real              # quadratic drag coefficient (1/m) that reproduces Pocket's linear 0.015/s at 30 m/s
RESTITUTION = .7746; BOUNCE_FRIC = .10; ROLL_DECEL = 1.5
PATH_DT = .004; PLAN_STEP = .02
JUMP_RISE_MAX = 1.3             # m of centre-of-mass lift at jump rating 1.0 (Pocket's jump_height default)
CROUCH_RUN, CROUCH_STAND = .08, .20     # s of plant before takeoff, running / standing
LAND_S = .20                    # s after touchdown before he can act
CATCH_ARREST_N, CATCH_TRAVEL_M, DEFLECT_KEEP, TURN_MAX = 1100., .6, .2, 1.05
ARM_V = 10.                      # m/s, how fast a limb gets from its neutral place (within 0.3 of its envelope) to the ball
JUMP_MARGIN = .90                # he plans a jump only for a lift up to this fraction of his rise: timing error needs slack
JUMP_PENALTY_S = .10             # a jump commits him (no steering, a landing lock): he leaves the ground only if it gets him to the ball this much sooner than staying down
COOLDOWN_S = .20                # Pocket: a player who touched cannot touch again for 200 ms
SWAT_SWING, SWAT_KEEP = 8., .35
SCOOP_S = .15                   # extra time to get the hands down to a low ball
BODY_R = .35

LIMBS = {'catch': (.80, None, 'hand'), 'swat': (.80, None, 'hand'), 'foot': (.25, None, 'foot'), 'head': (.95, .40, 'head')}

@dataclass
class Player:
    pid: str; team: str; x: float; y: float; vx: float = 0.; vy: float = 0.
    height: float = 2.54; mass: float = 180.; jump: float = .7; catching: float = .65; awareness: float = .65
    top: float = 30.; accel: float = 9.; reserve: float = 1.
    mode: str = 'catch'              # catch | swat | foot | head
    intent: str = 'earliest'         # earliest (cut it off) | receive (least change of course)
    pre_s: float = 0.                # advance warning in seconds (intended receiver)
    kick_power: float = .7; kick_accuracy: float = .7
    aim: tuple = None                # unit 3-vector, where a foot/head/swat sends the ball
    shape: object = None
    busy_until: float = -1.          # cannot touch before this time (he has just touched the ball himself)
    jump_pen: float = JUMP_PENALTY_S   # seconds a jump must save over staying down (set negative to 'go up for it at the highest point')
    @property
    def reach(self): return .46 * self.height
    @property
    def fatigue(self): return T.fatigue_factor(self.reserve)
    @property
    def rise_max(self): return JUMP_RISE_MAX * self.jump * self.fatigue
    @property
    def timing(self): return .5 * (self.catching + self.awareness)
    @property
    def move_delay(self): return .35 - .20 * self.awareness
    @property
    def tau_set(self): return .12 * (1.3 - .6 * self.awareness)
    @property
    def a_eff(self): return self.accel * self.fatigue
    @property
    def vmax(self): return self.top * self.fatigue ** .5
    def limb(self, mode=None):
        zc, R, _ = LIMBS[mode or self.mode]
        if R is None: R = (self.reach + .2) if (mode or self.mode) in ('catch', 'swat') else .28 * self.height
        return zc * self.height, R

def flight(t0, pos, vel, tmax=6., dt=PATH_DT, air=1.):
    """Ball path under Pocket's air.  Returns (samples [(t,x,y,z,vx,vy,vz)], field_times).  A bounce above 0.5 m/s of impact is a field contact; below that the ball rolls."""
    t = t0; x, y, z = pos; vx, vy, vz = vel
    P = [(t, x, y, z, vx, vy, vz)]; fields = []
    while t - t0 < tmax:
        v = math.sqrt(vx * vx + vy * vy + vz * vz); k = C_DRAG * air * v
        vx -= k * vx * dt; vy -= k * vy * dt; vz += (-G - k * vz) * dt
        x += vx * dt; y += vy * dt; z += vz * dt; t += dt
        if z <= BALL_R and vz < 0:
            vin = -vz; z = BALL_R
            if vin > .5: vz = RESTITUTION * vin; vx *= 1 - BOUNCE_FRIC; vy *= 1 - BOUNCE_FRIC; fields.append(t)
            else: vz = 0.
        if z <= BALL_R + 1e-9 and vz == 0.:
            s = math.hypot(vx, vy); d = ROLL_DECEL * dt
            if s <= d: vx = vy = 0.
            else: vx -= vx / s * d; vy -= vy / s * d
        P.append((t, x, y, z, vx, vy, vz))
        if z <= BALL_R + 1e-9 and vz == 0. and vx == 0. and vy == 0.: break
    return P, fields

class Traj:
    """A player's motion from a state at t0: drift at the old velocity until t_s (he has not decided), accelerate at a (vector) until t_to (takeoff, or forever), then fly/run at the velocity he has."""
    def __init__(s, p, t0, pos, vel, t_s, a, t_to=math.inf, vz0=0., crouch=0., t_arr=math.inf):
        s.p = p; s.t0 = t0; s.pos = pos; s.vel = vel; s.t_s = t_s; s.a = a; s.t_to = t_to; s.vz0 = vz0; s.crouch = crouch
        s.t_acc = min(t_to, t_arr)          # he accelerates from t_s to here (the takeoff, or the moment of the planned contact), then keeps the velocity he has
        s.ps = (pos[0] + vel[0] * (t_s - t0), pos[1] + vel[1] * (t_s - t0))
    def xy(s, t):
        if t <= s.t_s: return (s.pos[0] + s.vel[0] * (t - s.t0), s.pos[1] + s.vel[1] * (t - s.t0))
        ta = min(t, s.t_acc) - s.t_s
        x = s.ps[0] + s.vel[0] * ta + .5 * s.a[0] * ta * ta; y = s.ps[1] + s.vel[1] * ta + .5 * s.a[1] * ta * ta
        if t > s.t_acc:
            tf = t - s.t_acc; x += (s.vel[0] + s.a[0] * ta) * tf; y += (s.vel[1] + s.a[1] * ta) * tf
        return (x, y)
    def v(s, t):
        if t <= s.t_s: return s.vel
        ta = min(t, s.t_acc) - s.t_s
        return (s.vel[0] + s.a[0] * ta, s.vel[1] + s.a[1] * ta)
    def lift(s, t):
        if t <= s.t_to or s.vz0 <= 0: return 0.
        tau = t - s.t_to; return max(0., s.vz0 * tau - .5 * G * tau * tau)
    def vz(s, t):
        if t <= s.t_to or s.vz0 <= 0: return 0.
        tau = t - s.t_to; return s.vz0 - G * tau if tau <= 2 * s.vz0 / G else 0.
    @property
    def t_land(s): return s.t_to + 2 * s.vz0 / G if s.vz0 > 0 and s.t_to < math.inf else None
    def airborne(s, t): return s.vz0 > 0 and s.t_to < t < s.t_to + 2 * s.vz0 / G
    def committed(s, t): return s.airborne(t)                       # cannot steer in the air
    def hand(s, t, zc):
        x, y = s.xy(t)
        if getattr(s, 'dip', None):                                   # getting the hands down to a low ball: a ramp over 0.4 s each side of the target moment
            td, zl = s.dip; f = max(0., 1. - abs(t - td) / .4); zc = zc - (zc - zl) * f
        return (x, y, zc + s.lift(t))

def plan(p, t0, pos, vel, path, t_obs, mode=None, rng=None, tmax=8.0):
    """Choose the contact moment on `path` and build the Traj.  Returns (Traj, info).  rng adds the player's reading and timing noise (None = a perfect reader)."""
    mode = mode or p.mode; zc, R = p.limb(mode)
    t_s = t_obs + max(0., p.move_delay - p.pre_s)
    u_run = min(1., math.hypot(*vel) / max(1e-9, p.top)); crouch = CROUCH_STAND + (CROUCH_RUN - CROUCH_STAND) * u_run
    a_eff, vmax, rise_max = p.a_eff, p.vmax, p.rise_max
    cands = []
    for k in range(0, len(path), max(1, int(round(PLAN_STEP / PATH_DT)))):
        t_i, bx, by, bz = path[k][:4]
        if t_i <= t_s + .05 or t_i - t_obs > tmax: continue
        lift_req = max(0., bz - zc - R); low = bz < zc - R - 1e-9
        viol = max(0., lift_req - JUMP_MARGIN * rise_max)
        lift_plan = max(min(rise_max, lift_req + .08), min(rise_max, bz - zc - .6 * R)) if lift_req > 0 else 0.        # jump high enough to have the ball well inside the envelope if the rise allows, not at its edge
        extra = SCOOP_S if low and mode in ('catch', 'swat') else 0.
        dzp = 0. if low else (bz - zc - lift_plan)
        rho = .85 * math.sqrt(max(0., R * R - dzp * dzp))
        q = (pos[0] + vel[0] * (t_i - t0), pos[1] + vel[1] * (t_i - t0))
        dx, dy = q[0] - bx, q[1] - by; dq = math.hypot(dx, dy)
        if dq > 1e-9: ux, uy = dx / dq, dy / dq
        else:
            vv = math.hypot(path[k][4], path[k][5]) or 1.; ux, uy = -path[k][4] / vv, -path[k][5] / vv
        B = (q[0], q[1]) if dq <= rho else (bx + ux * rho, by + uy * rho)
        dev = (B[0] - q[0], B[1] - q[1]); dn = math.hypot(*dev)
        if lift_plan > 0:
            vz0 = math.sqrt(2 * G * lift_plan); t_up = vz0 / G; t_to = t_i - t_up; ta = t_to - t_s - extra
            ok_time = ta >= crouch; tf = t_up
        else:
            vz0 = 0.; t_to = math.inf; ta = t_i - t_s - extra; ok_time = ta > 0; tf = 0.
        K_ = .5 * ta * ta + ta * tf if ok_time else 0.
        if ok_time and K_ > 0: a_req = dn / K_; vend = math.hypot(vel[0] + (dev[0] / K_) * ta, vel[1] + (dev[1] / K_) * ta)
        else: a_req = 0. if dn < 1e-9 else 9e9; vend = math.hypot(*vel)
        need = max(a_req / a_eff, vend / vmax if vend > vmax else 0., 1.0 + viol / max(.1, rise_max) * 4 if viol > 0 else 0., 1e9 if not ok_time and lift_plan > 0 else 0.)
        cands.append(dict(k=k, t=t_i, ball=(bx, by, bz), B=B, dev=dev, need=need, lift=lift_plan, vz0=vz0, t_to=t_to, ta=ta, tf=tf, extra=extra, dn=dn, ok_time=ok_time, viol=viol))
    feas = [c for c in cands if c['need'] <= 1.0 and c['ok_time'] and c['viol'] == 0]
    if feas:
        first = min(feas, key=lambda c: c['t'] + (p.jump_pen if c['lift'] > 0 else 0.))
        if p.intent == 'receive':
            grounded = [c for c in feas if c['lift'] == 0.]
            if grounded: first = grounded[0]
            run = [first]
            pool = grounded if grounded else feas
            for c in pool[pool.index(first) + 1:]:
                if c['k'] == run[-1]['k'] + max(1, int(round(PLAN_STEP / PATH_DT))): run.append(c)
                else: break
            ch = min(run, key=lambda c: c['dn'])
        else: ch = first
        attempt = True
    else:
        near = [c for c in cands if (c['ok_time'] or c['lift'] == 0.) and c['viol'] == 0]     # best effort never jumps for what no jump can reach
        ch = min(near, key=lambda c: c['need']) if near else None
        attempt = ch is not None and ch['need'] <= 2.0
        if not attempt: ch = None
    info = dict(feasible=bool(feas), attempt=attempt, mode=mode)
    if ch is None:
        return Traj(p, t0, pos, vel, t_s, (0., 0.), math.inf, 0., crouch, t_arr=t_s), dict(info, target=None)
    dev = ch['dev']
    if rng is not None:                                              # he reads the ball with error: his target body spot is off by aim noise; takeoff timing is off
        sg = .05 + .30 * (1. - p.awareness); dev = (dev[0] + rng.gauss(0, sg), dev[1] + rng.gauss(0, sg))
    ta, tf = ch['ta'], ch['tf']; K_ = .5 * ta * ta + ta * tf if ch['ok_time'] else 0.
    a = (dev[0] / K_, dev[1] / K_) if K_ > 1e-9 else (0., 0.)
    an = math.hypot(*a)
    if an > a_eff: a = (a[0] / an * a_eff, a[1] / an * a_eff)
    t_to, vz0 = ch['t_to'], ch['vz0']
    if vz0 > 0:
        if rng is not None: t_to += rng.gauss(0, .02 + .08 * (1. - p.timing))
        t_to = max(t_s + crouch * .5, t_to)
    tr = Traj(p, t0, pos, vel, t_s, a, t_to if vz0 > 0 else math.inf, vz0, crouch, t_arr=ch['t'])
    if mode in ('catch', 'swat') and ch['ball'][2] < zc - R - 1e-9: tr.dip = (ch['t'], ch['ball'][2] + .3 * R)
    return tr, dict(info, target=ch['ball'], t=ch['t'], need=ch['need'], jump=vz0 > 0, lift=ch['lift'], body=ch['B'])

def _sweep(tr, p, mode, path, t_from, t_set, cooldown_until):
    """First contact of this player's limb with the ball path: (t, k, gap) or None.
    The ball is 'in reach' while its distance to the limb centre is under R.  Within a stretch in reach, each local minimum of that distance (the ball passing nearest) is a chance:
    the limb gets there at max(t_set + arm travel, the moment of nearest approach) -- 'at the closest approach, or as soon as he is set if that has passed' (Pocket) -- and the chance is real only if the ball is still in reach then."""
    zc, R = p.limb(mode)
    k0 = 0
    while k0 < len(path) and path[k0][0] < max(t_from, cooldown_until): k0 += 1
    n = len(path)
    k = k0
    while k < n:
        hx, hy, hz = tr.hand(path[k][0], zc); d = math.sqrt((path[k][1] - hx) ** 2 + (path[k][2] - hy) ** 2 + (path[k][3] - hz) ** 2)
        if d > R: k += 1; continue
        ds = []; ks = k          # a stretch in reach
        while k < n:
            hx, hy, hz = tr.hand(path[k][0], zc); d = math.sqrt((path[k][1] - hx) ** 2 + (path[k][2] - hy) ** 2 + (path[k][3] - hz) ** 2)
            if d > R: break
            ds.append(d); k += 1
        t_out = path[k - 1][0]
        mins = [i for i in range(len(ds)) if (i == 0 or ds[i] <= ds[i - 1]) and (i == len(ds) - 1 or ds[i] < ds[i + 1])]
        for i in mins:
            kc = ks + i; t_c = path[kc][0]; t_hit = max(t_set + max(0., ds[i] - .3 * R) / ARM_V, t_c)
            if t_hit > t_out + 1e-9: continue
            kk = kc
            while kk < k - 1 and path[kk][0] < t_hit: kk += 1
            hx, hy, hz = tr.hand(path[kk][0], zc); g = math.sqrt((path[kk][1] - hx) ** 2 + (path[kk][2] - hy) ** 2 + (path[kk][3] - hz) ** 2)
            if g <= R: return (path[kk][0], kk, g)
    return None

def _secure(p, rel_speed, miss, shape):
    mult = BH.catch_multiplier(shape, p.catching) if shape is not None else 1.
    cap = CATCH_ARREST_N * CATCH_TRAVEL_M * (.4 + .9 * p.catching) * max(0., 1 - miss * miss) / mult
    E = .5 * BALL_M * rel_speed * rel_speed
    return (1. / (1. + (E / cap) ** 2)) if cap > 1e-9 else 0.

def _touch(p, mode, bvel, hvel, miss, shape, rng):
    """Result of one contact: ('caught'|'deflect', ball velocity after)."""
    rv = [bvel[j] - hvel[j] for j in range(3)]; rs = math.sqrt(sum(c * c for c in rv))
    if mode == 'catch':
        if rng.random() < _secure(p, rs, miss, shape): return 'caught', hvel
        turn = rng.uniform(-TURN_MAX, TURN_MAX); c, s = math.cos(turn), math.sin(turn)
        return 'deflect', (hvel[0] + DEFLECT_KEEP * (rv[0] * c - rv[1] * s), hvel[1] + DEFLECT_KEEP * (rv[0] * s + rv[1] * c), abs(bvel[2]) * .3 + rng.uniform(0, 2))
    if mode == 'swat':
        d = p.aim or (-rv[0] / (rs or 1.), -rv[1] / (rs or 1.), -.3)
        n = math.sqrt(sum(c * c for c in d)); d = tuple(c / n for c in d)
        sg = .15 + .5 * (1. - p.catching); az = math.atan2(d[1], d[0]) + rng.gauss(0, sg); el = math.asin(max(-1., min(1., d[2]))) + rng.gauss(0, sg / 2)
        sw = SWAT_SWING * (.5 + .5 * p.catching)
        return 'deflect', tuple(hvel[j] + SWAT_KEEP * rv[j] + sw * v for j, v in enumerate((math.cos(el) * math.cos(az), math.cos(el) * math.sin(az), math.sin(el))))
    if mode == 'foot':
        th = T.Thrower(height=p.height, power=p.kick_power, accuracy=p.kick_accuracy, reserve=p.reserve)
        d = p.aim or (1., 0., .3); n = math.sqrt(sum(c * c for c in d)); d = tuple(c / n for c in d)
        v, _ = K.kick(th, p.shape or T.SHAPES['sphere'], d, 12., rng, 'punt'); return 'deflect', tuple(hvel[j] + v[j] for j in range(3))
    if mode == 'head':
        d = p.aim or (1., 0., .5); n = math.sqrt(sum(c * c for c in d)); d = tuple(c / n for c in d)
        sg = .25 * (1.2 - p.catching); az = math.atan2(d[1], d[0]) + rng.gauss(0, sg); el = math.asin(max(-1., min(1., d[2]))) + rng.gauss(0, sg / 2)
        sp = min(12., .6 * rs + 3.)
        return 'deflect', (hvel[0] + sp * math.cos(el) * math.cos(az), hvel[1] + sp * math.cos(el) * math.sin(az), hvel[2] + sp * math.sin(el))
    raise ValueError(mode)

def resolve(players, ball_pos, ball_vel, rng, t_start=0., max_touches=4, shape=None, tmax=6., perfect=False, x_range=None):
    """The contest.  players: list of Player.  Returns dict(outcome, events, fields, final).  outcome: 'caught' | 'loose' | 'untouched'.
    events: ('touch', t, pid, mode, result, miss, airborne, rel_speed) ; ('field', t) ; ('midair', t, a, b, closing) ; ('plan', pid, info)."""
    events = []; fields_all = []
    state = {p.pid: (p.x, p.y, p.vx, p.vy, t_start) for p in players}
    trajs = {}; cool = {p.pid: p.busy_until for p in players}; planlog = {}
    t_obs = t_start; pos = ball_pos; vel = ball_vel
    for n in range(max_touches + 1):
        path, fields = flight(t_obs, pos, vel, tmax=tmax)
        if x_range is not None:                                   # the contest only counts while the ball is inside this stretch of the field (a shot block: between the shooter and the goal)
            kx = next((i for i, q in enumerate(path) if not (x_range[0] <= q[1] <= x_range[1])), None)
            if kx is not None: path = path[:max(2, kx)]; fields = [f for f in fields if f <= path[-1][0]]
        # replan everyone who is not committed
        for p in players:
            tr0 = trajs.get(p.pid)
            if tr0 is not None and tr0.committed(t_obs): continue
            if tr0 is not None:
                x, y = tr0.xy(t_obs); vx, vy = tr0.v(t_obs); st = (x, y, vx, vy, t_obs)
                if tr0.t_land is not None and t_obs < tr0.t_land + LAND_S: pass
            else: st = state[p.pid]
            tr, info = plan(p, st[4], (st[0], st[1]), (st[2], st[3]), path, t_obs, rng=None if perfect else rng)
            trajs[p.pid] = tr; planlog[(n, p.pid)] = info
            events.append(('plan', p.pid, dict(info, n=n)))
        # contact candidates
        cands = []
        for p in players:
            tr = trajs[p.pid]
            if tr.t_land is not None and tr.t_land < t_obs and t_obs < tr.t_land + LAND_S: continue
            u = rng.random(); t_start_obs = t_obs - min(.5, p.pre_s)
            t_set = t_start_obs - p.tau_set * math.log(max(1e-12, 1. - u)) if not perfect else t_obs
            r = _sweep(tr, p, p.mode, path, t_obs, t_set, cool[p.pid])
            if r: cands.append((r[0], r[2], p, r[1]))
        if not cands:
            fields_all += [(t) for t in fields]; events += [('field', t) for t in fields]
            return dict(outcome='loose' if any(e[0] == 'touch' for e in events) else 'untouched', events=events, fields=fields_all, final=path[-1], trajs=trajs, path=path)
        cands.sort(key=lambda c: (c[0], c[1])); t_c, gap, p, k = cands[0]
        ties = [c for c in cands if abs(c[0] - t_c) < .001 and c[2].team != p.team]
        fl = [t for t in fields if t < t_c]; fields_all += fl; events += [('field', t) for t in fl]
        tr = trajs[p.pid]; zc, R = p.limb(); miss = min(1., gap / R)
        hv = (tr.v(t_c)[0], tr.v(t_c)[1], tr.vz(t_c)); bv = path[k][4:7]
        # collisions in the air up to the touch
        for q in players:
            if q is p: continue
            tq = trajs[q.pid]; tt = t_obs
            while tt < t_c:
                xp, yp = tr.xy(tt); xq, yq = tq.xy(tt)
                if math.hypot(xp - xq, yp - yq) < 2 * BODY_R and (tr.lift(tt) > .05 or tq.lift(tt) > .05) and abs(tr.lift(tt) - tq.lift(tt)) < p.height * .8:
                    vp, vq = tr.v(tt), tq.v(tt); events.append(('midair', tt, p.pid, q.pid, math.hypot(vp[0] - vq[0], vp[1] - vq[1]))); break
                tt += .02
        res, nv = _touch(p, p.mode, bv, hv, miss, shape or p.shape, rng)
        events.append(('touch', t_c, p.pid, p.mode, res, round(miss, 3), tr.airborne(t_c), round(math.sqrt(sum((bv[j] - hv[j]) ** 2 for j in range(3))), 2), len(ties)))
        cool[p.pid] = t_c + COOLDOWN_S
        if res == 'caught': return dict(outcome='caught', catcher=p.pid, team=p.team, t=t_c, airborne=tr.airborne(t_c), events=events, fields=fields_all, final=path[k], trajs=trajs, path=path[:k + 1], tie=len(ties) > 1)
        t_obs = t_c; pos = path[k][1:4]; vel = nv
        for q in players:
            if trajs[q.pid].committed(t_obs): continue
            x, y = trajs[q.pid].xy(t_obs); vx, vy = trajs[q.pid].v(t_obs); state[q.pid] = (x, y, vx, vy, t_obs)
    return dict(outcome='loose', events=events, fields=fields_all, final=path[-1], trajs=trajs, path=path)

def foot_rule_events(events, holder):
    """Map contest events to FootRule events for the player whose legality is being tracked: his hand/head/body contacts are 'hand', his foot 'foot', anyone else's touch 'other', a field contact 'field'."""
    out = []
    for e in sorted((e for e in events if e[0] in ('touch', 'field')), key=lambda e: e[1]):
        if e[0] == 'field': out.append('field')
        elif e[2] == holder: out.append('foot' if e[3] == 'foot' else 'hand')
        else: out.append('other')
    return out

def mc(scene, n, seed=1):
    """Run scene(rng) -> resolve() result n times; tally outcomes by team and kind."""
    rng = random.Random(seed); tally = {}
    for i in range(n):
        r = scene(rng); key = (r['outcome'], r.get('team'), r.get('airborne'))
        tally[key] = tally.get(key, 0) + 1
    return {str(k): v / n for k, v in sorted(tally.items(), key=lambda kv: -kv[1])}
