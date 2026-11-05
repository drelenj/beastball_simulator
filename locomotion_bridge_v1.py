"""Locomotion bridge v1: frozen locomotion 1.0 (via pocket_capability_v37) -> Pocket 2.0 mover attributes.

Pocket's mover is kinematic: top speed = maximum_speed * (.70+.30*fatigue) * (.88 non-carrier | pace*.90 carrier), constant acceleration
`acceleration*(.55+.45*fatigue)`, braking, and a lateral velocity-change limit `turning`.  The bridge does NOT edit Pocket.  Each tick it sets those
attributes from the athlete's rating and reserve so that Pocket's own mover reproduces the locomotion capabilities, and holds p.fatigue at 1 so
Pocket's built-in multipliers stay neutral (the reserve is owned by the condition layer, not by Pocket's old fatigue).
"""
import math, json, bisect
import pocket_capability_v37 as cap
MPH = .44704
TURN = {}          # filled from locomotion_bridge_v1_turning.json (calibrated against Pocket's mover, see calibrate_bridge_v1.py)
try:
    import os
    _p = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'locomotion_bridge_v1_turning.json')
    TURN = json.load(open(_p))
except Exception:
    pass


def _t_dist(a, vmax, d):
    if d <= vmax * vmax / (2 * a): return math.sqrt(2 * d / a)
    return vmax / a + (d - vmax * vmax / (2 * a)) / vmax


def fit_acceleration(top, t10, t36):
    best, besta = 1e9, 10.
    a = 4.
    while a < 60.:
        e = math.log(_t_dist(a, top, 10.) / t10) ** 2 + math.log(_t_dist(a, top, 36.576) / t36) ** 2
        if e < best: best, besta = e, a
        a += .05
    return besta


def _turn(rating, reserve, role):
    d = TURN.get(role) or TURN.get('field')
    if not d: return 20.
    rs = sorted({float(k.split('|')[0]) for k in d}); vs = sorted({float(k.split('|')[1]) for k in d})
    def br(g, x):
        x = min(max(x, g[0]), g[-1]); i = min(max(bisect.bisect_right(g, x) - 1, 0), len(g) - 2); return g[i], g[i + 1], (x - g[i]) / (g[i + 1] - g[i])
    r0, r1, tr = br(rs, rating); v0, v1, tv = br(vs, reserve)
    g = lambda r, v: d['%s|%s' % (r, v)]
    return g(r0, v0) * (1 - tr) * (1 - tv) + g(r0, v1) * (1 - tr) * tv + g(r1, v0) * tr * (1 - tv) + g(r1, v1) * tr * tv


def attributes(rating, reserve=1., role='field', region='', severity=0.):
    c = cap.capability(rating, reserve, region, severity, role)
    top = c['top_mph'] * MPH
    brake_d = c['stop25_m'] or c['stop15_m']; brake_v = 25. if c['stop25_m'] else 15.
    brake = (brake_v ** 2 - 9.) / (2 * brake_d) if brake_d else 20.
    acc = fit_acceleration(top, c['t10_s'], c['t36_6_s'])
    return dict(top=top, acceleration=acc, braking=brake, turning=_turn(rating, reserve, role), cap=c)


def apply(m, p, rating, reserve=1., role='field', region='', severity=0.):
    """Set Pocket player p's mover attributes from locomotion capability.  Call before every tick (the carrier flag changes the top-speed factor)."""
    at = attributes(rating, reserve, role, region, severity)
    carrier = m.s.ball.carrier == p.id
    factor = (m.pol[p.team].t.pace * .90) if carrier else .88
    p.a.maximum_speed = at['top'] / factor
    p.a.acceleration = at['acceleration']; p.a.braking = at['braking']; p.a.turning = at['turning']
    p.fatigue = 1.
    return at
