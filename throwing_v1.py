"""Throwing v1: a reduced-order whole-body-chain throw model plus ball-shape aerodynamics.   ALL CONSTANTS PROVISIONAL (design dials, flagged).
Built as a lab: it does not edit Pocket.  Its outputs map onto what Pocket's pass/shot code already consumes
  (release speed, launch-direction error sigma, release delay, restraint) so it can be wired in later.

RATINGS (the only knobs)
  Throw Power    0..1   strength side: sets how much speed the body chain can put into the ball.   v_rel_max = V_CAP * (0.5 + 0.5*power) * chain readiness
  Throw Accuracy 0..1   technique + precision: sets the one-sigma release-direction error and the spin quality.

CHAIN  (legs/hips -> torso -> arm/hand), each stage has a readiness 0..1 from the Condition layer (fatigue, damage, wear lowers it through damage):
  v_rel_max = V_CAP * (0.5 + 0.5*power) * (W_LEG*leg_term + W_TORSO*r_torso + W_ARM*r_arm),   leg_term = r_legs * (1 - LEG_RUN_LOSS*u)   (u = speed / top: a runner has less planted leg drive)
  The ball leaves with the thrower's own velocity PLUS the relative release velocity (a throw on the run carries the run).  Pocket's rulebook caps the ground-frame release at 40 m/s
  (ball_limit; faster is the foul 'ball_release_speed'), so a fast runner throwing forward must throw softer: the model solves for the legal relative speed.

ERROR  one-sigma azimuth (deg) = max(0.15, 3 * (1 - accuracy))   [Pocket's pass_aim_error_deg convention] * m_run * m_bal * m_chain * m_fat * m_effort / grip_quality ;  elevation sigma = half of it (Pocket's convention);  speed sigma/v = SIGV * the same multiplier.

BALL SHAPE  same mass (0.40 kg) and same volume as the rulebook sphere (d = 0.215 m); prolate spheroids stretched along the spin axis.
  hand interface : grip_fit = short diameter / hand span (0.13*height);  ideal about 0.62.  Long axis longer than 0.9 of the span costs release quality.
  flight         : sphere = quadratic drag + Magnus lift from spin;  spheroid = spiral thrown about its long axis, nose-on drag, gyroscopic stability Sg = (I_a w)^2 / (4 I_t M),
                   M = overturning moment ~ air * 0.5 rho v^2 V Cm;  Sg < ~1.3 wobbles: drag rises toward broadside and a random side force appears.
  AIR            : Pocket's drag is linear 0.015/s, about 50x thinner than real air for this ball.  `AIR_POCKET` scales all aerodynamic forces so the sphere at 30 m/s matches Pocket;
                   `AIR_REAL = 1` shows what the shapes would do in real air.  With Pocket's thin air, shape barely matters in flight - it matters at the hand.
"""
import math, random
from dataclasses import dataclass, field

import os
SPLIT = os.environ.get('THROW_SPLIT', '1') == '1'   # DreLen's throw split (4 Nov): Throw Power / Throw Accuracy / Touch; no ball-speed cap; error grows with release speed.  THROW_SPLIT=0 restores the old model.
V_CAP = 40.                 # m/s, Pocket ball_limit (rulebook) - the OLD model's power scale and cap
V_POWER = 3. * 44.7 if SPLIT else V_CAP        # m/s: Throw Power 100 = 3 x the top speed of a 100-speed athlete (134.1 m/s)
RULE_CAP = 1e9 if SPLIT else V_CAP             # no cap on ball speed in the split model
V_ACC_REF = 67.             # m/s: release speed at which the rated direction error applies (the weakest thrower's maximum); error scales with hand speed / V_ACC_REF
TOUCH_SIGMA = .10           # one-sigma fractional error of the delivered speed at touch 0 (rating 40); floor TOUCH_FLOOR
TOUCH_FLOOR = .003
RATINGS = {}                # test override {player id: (throw_power, throw_accuracy, touch)} as ratings 40..100
def rating_x(r): return max(0., min(1., (r - 40.) / 60.))
W_LEG, W_TORSO, W_ARM = .30, .30, .40
LEG_RUN_LOSS = .40
POWER_FLOOR = .5            # v_rel_max at power 0 = 50 % of the cap-rated speed (Pocket's default pass_speed 27 m/s is power ~0.4 under these dials)
SIGMA0, ACC_GAIN, SIGMA_FLOOR = 3., 1., .15  # deg, Pocket pass_aim_error_deg; error = max(floor, SIGMA0 * (1 - ACC_GAIN * accuracy)) -> the same number Pocket uses at neutral conditions
SIGV = .006                 # speed one-sigma as a fraction of release speed at multiplier 1
RELEASE_S = .25             # Pocket pass_release_ms
HAND_SPAN_PER_H = .13       # m per m of height (anatomy has no finger model)
G = 9.81
RHO = 1.2
BALL_MASS = .40
BALL_D = .215
BALL_V = 4. / 3. * math.pi * (BALL_D / 2) ** 3
V_REF = 30.
# ---- ball shapes ----------------------------------------------------------------------------------------------------------------------
@dataclass
class Shape:
    name: str
    aspect: float = 1.0          # long axis / short axis (equal-volume spheroid); 1 = sphere
    mass: float = BALL_MASS
    cd_nose: float = .47         # drag coefficient on area pi*b^2 (spiral, nose-on).  sphere .47
    cd_broad: float = .47        # broadside (tumbling) coefficient, on area pi*a*b
    cm: float = 0.               # overturning-moment coefficient factor
    def axes(self):
        r = BALL_D / 2; b = r / self.aspect ** (1. / 3.); a = b * self.aspect; return a, b
    @property
    def short_d(self): return 2 * self.axes()[1]
    @property
    def long_d(self): return 2 * self.axes()[0]
    def inertia(self):
        a, b = self.axes(); Ia = .4 * self.mass * b * b; It = .2 * self.mass * (a * a + b * b); return Ia, It
SHAPES = {'sphere': Shape('sphere'),
          'prolate1.25': Shape('prolate1.25', 1.25, cd_nose=.18, cd_broad=.75, cm=.5 * .25),
          'prolate1.5': Shape('prolate1.5', 1.5, cd_nose=.15, cd_broad=.8, cm=.5 * .5),
          'prolate1.8': Shape('prolate1.8', 1.8, cd_nose=.13, cd_broad=.85, cm=.5 * .8)}
# aerodynamic scale: sphere decel at V_REF equals Pocket's linear drag (0.015/s * 30 m/s)
_c_real = .5 * RHO * .47 * math.pi * (BALL_D / 2) ** 2 / BALL_MASS
AIR_POCKET = (.015 * V_REF / V_REF ** 2) / _c_real
AIR_REAL = 1.
# ---- thrower ----------------------------------------------------------------------------------------------------------------------------
@dataclass
class Thrower:
    height: float = 2.54
    power: float = .7
    accuracy: float = .7
    touch: float = .7             # 0..1: how well the right speed is chosen and delivered (rating 40 -> 0, 100 -> 1)
    vel: tuple = (0., 0.)         # ground velocity (m/s)
    top: float = 44.7             # rested top speed, for the run fraction
    reserve: float = 1.           # fatigue reserve
    damage: dict = field(default_factory=dict)   # {part: 0..1}
    hold_rho: float = 0.          # uniform restraint (Pocket's region-level rho), 0..1
    part_hold: dict = field(default_factory=dict)   # restraint per ANATOMY PART from grips on him, {part: 0..1} (grip force / 1200 N rupture); overrides the uniform number's role when given
    hand: str = 'right'
    kick_leg: str = 'right'
    def d(self, p): return self.damage.get(p, 0.)
    @property
    def speed(self): return math.hypot(*self.vel)
    @property
    def u(self): return min(1., self.speed / self.top)
def holds(t):
    """Restraint per role from the 10-part holds: arm = throwing arm/hand, off = off arm/hand, torso, head, legs = mean of the two legs (leg or foot held), plus each leg."""
    g = lambda p: max(0., min(1., t.part_hold.get(p, 0.))); side, off = t.hand, ('left' if t.hand == 'right' else 'right')
    leg = lambda s_: max(g(s_ + '_leg'), g(s_ + '_foot'))
    return dict(arm=max(g(side + '_arm'), g(side + '_hand')), off=max(g(off + '_arm'), g(off + '_hand')), torso=g('torso'), head=g('head'), left_leg=leg('left'), right_leg=leg('right'), legs=(leg('left') + leg('right')) / 2.)
def fatigue_factor(reserve, max_loss=.35, expo=2.): return 1. - max_loss * (1. - reserve) ** expo     # same shape as the locomotion bridge's FatigueParams
def readiness(t):
    fat = fatigue_factor(t.reserve)
    legs = (t.d('left_leg') + t.d('right_leg') + t.d('left_foot') + t.d('right_foot')) / 4.
    r_legs = (1. - .8 * legs) * fat
    r_torso = (1. - .6 * t.d('torso')) * fat
    side = t.hand
    r_arm = (1. - .7 * t.d(side + '_arm')) * (1. - .5 * t.d(side + '_hand')) * fat
    if t.part_hold:
        h = holds(t); r_legs *= (1. - .5 * h['legs']); r_torso *= (1. - .6 * h['torso'] - .15 * h['off']); r_arm *= (1. - .85 * h['arm'])
    return r_legs, r_torso, r_arm
def chain(t):
    rl, rt, ra = readiness(t); leg_term = rl * (1. - LEG_RUN_LOSS * t.u)
    c = W_LEG * leg_term + W_TORSO * rt + W_ARM * ra
    return c, (rl, rt, ra)
def v_rel_max(t, quick=False):
    c, _ = chain(t); return V_POWER * (POWER_FLOOR + (1 - POWER_FLOOR) * t.power) * c * (QUICK_SPEED if quick else 1.)
def grip_quality(t, shape):
    span = HAND_SPAN_PER_H * t.height; fit = shape.short_d / span
    q = max(.2, 1. - ((fit - .62) / .35) ** 2)
    if shape.long_d > .9 * span: q *= max(.5, 1. - 2.5 * (shape.long_d / span - .9))
    return q
def multiplier(t, shape, effort):
    c, (rl, rt, ra) = chain(t)
    m_run = 1. + 1.2 * t.u; m_bal = 1. + 2.0 * t.hold_rho + ((lambda h: 3. * h['arm'] + 1.5 * h['torso'] + .8 * h['off'] + 1.0 * h['legs'] + .5 * h['head'])(holds(t)) if t.part_hold else 0.); m_chain = 1. + 1.5 * (1. - min(rl, rt, ra))
    m_fat = 1. + 1.0 * (1. - t.reserve); m_eff = 1. if SPLIT else 1. + .3 * effort ** 2
    return m_run * m_bal * m_chain * m_fat * m_eff / grip_quality(t, shape)
# CARRY POSES, most secure to most ready:  braced (hand+arm, pinned to torso, covered by the off arm) > tucked (hand+arm, pinned to torso) > exposed (hand+arm only)
#   > extended (ball out in front: more exposed than exposed, but a quick route to a throw) > loaded (cocked, in the throwing position).
# TRANSITION_S: time from each pose to LOADED (the full throw starts from loaded; RELEASE_S is the forward swing + release), seconds at accuracy 0.
# QUICK throw ('touch pass', basketball-style): thrown from extended/exposed/loaded WITHOUT winding up: arm only.  Faster, weaker, less accurate.
TRANSITION_S = {'loaded': 0., 'extended': .05, 'exposed': .10, 'tucked': .35, 'braced': .55}
QUICK_SPEED, QUICK_SIGMA, QUICK_DELAY = .55, 1.6, .45
TRANSITION_Q = {'loaded': 0., 'extended': .02, 'exposed': .06}
OCCUPIED_OFF_HAND = {'braced'}        # the off arm is busy covering the ball: no fending, stiff-arm, balance or grip
REGRIP_S = .30                                                   # extra seconds per unit of (aspect - 1): a long ball must be turned to the spin grip
def transition_time(t, shape, pose):
    regrip = 0. if pose == 'loaded' else REGRIP_S * (shape.aspect - 1.)      # a loaded ball is already on the spin grip
    return (TRANSITION_S[pose] + regrip) * (1.15 - .3 * t.accuracy) / grip_quality(t, shape)
def release_delay(t, shape=None, pose=None, quick=False):
    c, _ = chain(t); d = RELEASE_S * (1. + .8 * (1. - c)) * (1.15 - .3 * t.accuracy)
    if quick:
        if pose is not None and pose not in TRANSITION_Q: raise ValueError('a quick throw needs the ball at loaded, extended or exposed')
        return d * QUICK_DELAY + (0. if pose is None else TRANSITION_Q[pose] * (1.15 - .3 * t.accuracy))
    return d if shape is None or pose is None else d + transition_time(t, shape, pose)
def solve_release(t, direction, want_ground_speed, shape=SHAPES['sphere'], cap=None, quick=False):
    """direction: unit 3-vector of the desired ground-frame launch; want_ground_speed: what the planner would like (<= cap).
    Returns (ground_velocity_vec, v_rel, info).  The thrower cannot exceed his chain's v_rel_max, cannot exceed the rule cap in the ground frame,
    and the ball keeps his own ground velocity.  Direction is the ground-frame direction aimed at (the planner solves for it)."""
    if cap is None: cap = RULE_CAP
    vb = (t.vel[0], t.vel[1], 0.); vmax = v_rel_max(t, quick); dx, dy, dz = direction
    want = min(want_ground_speed, cap)
    target = (dx * want, dy * want, dz * want)
    rel = (target[0] - vb[0], target[1] - vb[1], target[2])
    need = math.sqrt(sum(c * c for c in rel))
    if need <= vmax: v = target; vrel = need
    else:
        s = vmax / need; v = (vb[0] + rel[0] * s, vb[1] + rel[1] * s, rel[2] * s); vrel = vmax
    gs = math.sqrt(sum(c * c for c in v))
    if gs > cap:                                   # throwing along the run past the cap: scale the relative part down until legal
        lo, hi = 0., 1.
        for _ in range(40):
            mid = (lo + hi) / 2; w = (vb[0] + rel[0] * mid, vb[1] + rel[1] * mid, rel[2] * mid)
            if math.sqrt(sum(c * c for c in w)) > cap: hi = mid
            else: lo = mid
        v = (vb[0] + rel[0] * lo, vb[1] + rel[1] * lo, rel[2] * lo); vrel = need * lo; gs = math.sqrt(sum(c * c for c in v))
    effort = vrel / max(1e-6, V_POWER * (POWER_FLOOR + (1 - POWER_FLOOR) * t.power) * (QUICK_SPEED if quick else 1.))
    return v, vrel, dict(ground_speed=gs, v_rel=vrel, v_rel_max=vmax, shortfall=max(0., need - vrel), effort=effort, capped=gs >= cap - 1e-6 and need > 0)
def sigma_deg(t, shape, effort, back=0.):
    """back: how much slower than the thrower's own run the ball is released along the aim direction (fraction of V_CAP); a hand that has to slow the ball is a bad release."""
    return max(SIGMA_FLOOR, SIGMA0 * (1. - ACC_GAIN * t.accuracy)) * multiplier(t, shape, effort) * (1. + 2. * back)
def spin_rate(t, shape):
    """rad/s about the long axis for a spheroid (spiral); backspin for a sphere.  Quality from accuracy and grip."""
    q = grip_quality(t, shape) * (.3 + .7 * t.accuracy)
    return (60. if shape.aspect > 1.0 else 25.) * q
def sample_release(t, direction, want_speed, shape, rng, scale=1., quick=False):
    v, vrel, info = solve_release(t, direction, want_speed, shape, quick=quick)
    vb = (t.vel[0], t.vel[1], 0.); back = max(0., -sum((v[i] - vb[i]) * direction[i] for i in range(3))) / V_POWER; info['back'] = back
    sig = math.radians(sigma_deg(t, shape, info['effort'], back)) * scale * (QUICK_SIGMA if quick else 1.) * ((info['v_rel'] / V_ACC_REF) if SPLIT else 1.); gs = info['ground_speed']
    az = math.atan2(v[1], v[0]) + rng.gauss(0, sig); el = math.asin(max(-1., min(1., v[2] / gs))) + rng.gauss(0, sig / 2)
    sv = (max(TOUCH_FLOOR, TOUCH_SIGMA * (1. - t.touch)) * (1. + 2. * back) * scale) if SPLIT else SIGV * multiplier(t, shape, info['effort']) * (1. + 2. * back) * scale
    gs2 = gs * (1. + rng.gauss(0, sv))
    return (gs2 * math.cos(el) * math.cos(az), gs2 * math.cos(el) * math.sin(az), gs2 * math.sin(el)), info
# ---- flight ----------------------------------------------------------------------------------------------------------------------------
def stability(shape, omega, v, air):
    if shape.aspect <= 1.0: return float('inf')
    Ia, It = shape.inertia(); M = max(1e-12, air * .5 * RHO * v * v * BALL_V * shape.cm)
    return (Ia * omega) ** 2 / (4. * It * M)
def fly(shape, pos, vel, omega, air, rng=None, dt=.004, tmax=6., plane_x=None):
    """Integrate one ball.  Frame: +x is the launch azimuth after rotating so that x is the horizontal launch heading (caller handles).  Returns (path list [(t,x,y,z)], info).
    sphere: quadratic drag + Magnus (backspin omega about -y gives lift); spheroid: spiral about its velocity direction with a wobble state from stability."""
    x, y, z = pos; vx, vy, vz = vel; t = 0.; path = [(0., x, y, z)]; m = shape.mass
    a_, b_ = shape.axes(); A_nose = math.pi * b_ * b_; A_broad = math.pi * a_ * b_
    wob0 = 0.; side_dir = rng.uniform(0, 2 * math.pi) if rng else 0.
    while t < tmax:
        v = math.sqrt(vx * vx + vy * vy + vz * vz)
        if shape.aspect <= 1.0:
            cd = shape.cd_nose; A = math.pi * (BALL_D / 2) ** 2
            S = (BALL_D / 2) * omega / max(v, 1.); cl = min(.35, 1.1 * S)
            qd = air * .5 * RHO * v * v / m
            drag = qd * cd * A; lift = qd * cl * A; wob = 0.
            hx, hy = vx / max(1e-9, math.hypot(vx, vy)), vy / max(1e-9, math.hypot(vx, vy))
            ax = -drag * vx / v; ay = -drag * vy / v; az = -drag * vz / v - G
            # backspin lift direction: (omega_vec x v) with omega about the horizontal axis perpendicular to heading, giving upward force for forward motion
            lz = lift * math.hypot(vx, vy) / v; lxy = -lift * vz / v
            ax += lxy * hx; ay += lxy * hy; az += lz
        else:
            Sg = stability(shape, omega, v, air); wob = max(0., min(1., (1.3 - Sg) / 1.0))
            cd = shape.cd_nose + (shape.cd_broad - shape.cd_nose) * wob
            A = A_nose + (A_broad - A_nose) * wob
            qd = air * .5 * RHO * v * v / m; drag = qd * cd * A
            ax = -drag * vx / v; ay = -drag * vy / v; az = -drag * vz / v - G
            if wob > 0 and rng:
                # side force from the yawed ball, fixed direction per throw, magnitude ~ wobble * the drag of the broadside area
                sf = wob * .5 * qd * shape.cd_broad * A_broad * .35
                hh = math.hypot(vx, vy) or 1.; px, py = -vy / hh, vx / hh
                ax += sf * math.cos(side_dir) * px; ay += sf * math.cos(side_dir) * py; az += sf * math.sin(side_dir) * .5
        vx += ax * dt; vy += ay * dt; vz += az * dt
        x += vx * dt; y += vy * dt; z += vz * dt; t += dt; path.append((t, x, y, z))
        if plane_x is not None and x >= plane_x: break
        if z < .0: break
    return path, dict(wobble=wob)
def solve_elevation(shape, speed, dist, h_release, h_target, omega, air, hi=.8):
    """Launch elevation (rad) that puts the ball at (dist, 0, h_target) when thrown along +x at `speed`, no noise.  Returns (elev, flight_time) or None."""
    def miss(el):
        p, _ = fly(shape, (0., 0., h_release), (speed * math.cos(el), 0., speed * math.sin(el)), omega, air, None, plane_x=dist)
        if p[-1][1] < dist - 1e-3: return None, p[-1][0]
        (t0, x0, _, z0), (t1, x1, _, z1) = p[-2], p[-1]; f = (dist - x0) / max(1e-9, x1 - x0)
        return z0 + f * (z1 - z0) - h_target, t0 + f * (t1 - t0)
    lo, hi_ = -.5, hi; elo, _ = miss(lo); ehi, _ = miss(hi_)
    if ehi is None or ehi < 0: return None
    if elo is not None and elo > 0: return None
    for _ in range(40):
        mid = (lo + hi_) / 2; em, _ = miss(mid)
        if em is None or em < 0: lo = mid
        else: hi_ = mid
    el = (lo + hi_) / 2; return el, miss(el)[1]
