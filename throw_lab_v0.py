"""Throw lab v0 (DreLen's split, 4 Nov): THROW POWER (physical) / THROW ACCURACY (technical) / TOUCH (technical).  Ratings 40..100 in steps of 10: 40 worst ever, 70 league average, 100 best ever.
x = (R-40)/60 maps a rating to 0..1.  Each test sets the other two ratings to 100 so they are present but irrelevant.
Rules of the model used here (provisional, all dials flagged):
  POWER     release speed v_rel_max = V_CAP*(0.5+0.5x) (throwing_v1 chain at rest, rested); the ball keeps the thrower's run; the ground-frame rule cap V_CAP=40 m/s applies.
  ACCURACY  one-sigma launch-direction error = max(0.15, 3*(1-x)) deg  *  (ball speed / 30 m/s)   <- precision falls in direct proportion to velocity;  elevation sigma = half.
  TOUCH     one-sigma error of the speed actually delivered, as a fraction of the speed chosen = max(0.003, 0.10*(1-x)).
Flight = the engine's own predict_path (gravity, drag, bounce).   python3 throw_lab_v0.py"""
import sys, os, math, json, random, statistics as st, importlib
os.environ['PRISM_I'] = '1'; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenario_1v2_v0 as SC
p = SC.proc(); P = p['P']; CO = p['CO']
m = CO.match.Match(P.configuration(p['st'], 1, P.CALIBRATION)); core = importlib.import_module(CO.match.Match.__module__)
G_, K_ = m.assume['gravity'], m.assume['ball_drag']; RES = .7745966692
V_CAP, V_REF = 40., 30.
RATINGS = (40, 50, 60, 70, 80, 90, 100)
X = lambda r: (r - 40.) / 60.
def v_rel_max(rp): return V_CAP * (.5 + .5 * X(rp))
def sig_dir_deg(ra, speed): return max(.15, 3. * (1. - X(ra))) * speed / V_REF
def sig_speed(rt): return max(.003, .10 * (1. - X(rt)))
def path(o, v): 
    b = type('B', (), dict(x=o[0], y=o[1], z=o[2], vx=v[0], vy=v[1], vz=v[2], radius=.1075))()
    return core.predict_path(b, G_, K_, RES, horizon=12., step=.01)
def vec(az, el, sp): return (sp * math.cos(el) * math.cos(az), sp * math.cos(el) * math.sin(az), sp * math.sin(el))
def throw(rng, o, az, el, sp, ra, rt):
    """what the hand does: aim (az, el) at chosen speed sp, then add accuracy and touch error"""
    s = math.radians(sig_dir_deg(ra, sp)); return vec(az + rng.gauss(0, s), el + rng.gauss(0, s / 2), sp * (1. + rng.gauss(0, sig_speed(rt))))
def miss3d(pth, tgt):
    """closest approach of the ball to the receiver's catch point (3D), before it first touches the ground past 2 m of the target"""
    return min(math.sqrt((q[1]-tgt[0])**2 + (q[2]-tgt[1])**2 + (q[3]-tgt[2])**2) for q in pth if q[1] <= tgt[0] + 3. or q[3] > .3)
def land(pth, zc):
    """first descending crossing of height zc (x, y, t) or None"""
    for a, b in zip(pth, pth[1:]):
        if a[3] > zc >= b[3]: f = (a[3] - zc) / (a[3] - b[3] or 1e-9); return a[1] + f * (b[1] - a[1]), a[2] + f * (b[2] - a[2]), a[0] + f * (b[0] - a[0])
    return None
def solve_el(o, tgt, sp, zc):
    """elevation (low arc) at speed sp that brings the ball down through height zc above tgt xy"""
    D = math.hypot(tgt[0] - o[0], tgt[1] - o[1]); lo, hi = math.radians(-5), math.radians(44); best = None
    for _ in range(40):
        mid = (lo + hi) / 2; l = land(path(o, vec(0., mid, sp)), zc)
        if l is None: hi = mid; continue
        if l[0] - o[0] < D: lo = mid
        else: hi = mid
        best = mid
    return best
def solve_speed_lob(o, D, el, zc):
    lo, hi = 3., 60.
    for _ in range(40):
        mid = (lo + hi) / 2; l = land(path(o, vec(0., el, mid)), zc)
        if l is None or l[0] - o[0] < D: lo = mid
        else: hi = mid
    return (lo + hi) / 2
out = dict(power={}, accuracy={}, speed_precision={}, touch={})
# ---------------- POWER (accuracy = touch = 100, noise-free)
print('POWER (deterministic; accuracy and touch irrelevant)')
for r in RATINGS:
    rel = v_rel_max(r); run = 18.   # m/s: a hard-running thrower
    peak_run = min(V_CAP, run + rel)
    best_r = 0.
    for ang in [a / 2. for a in range(20, 120)]:
        el = math.radians(ang); x, z, vx, vz, t = 0., 1.6, rel * math.cos(el), rel * math.sin(el), 0.
        while t < 30.:
            vx += -K_ * vx * .002; vz += (-G_ - K_ * vz) * .002; x += vx * .002; z += vz * .002; t += .002
            if z <= 1.0 and vz < 0: break
        best_r = max(best_r, x)
    lo = best_r   # same gravity and linear drag as the engine, without the 100 m field edge
    out['power'][r] = dict(release_speed=round(rel, 1), peak_speed_on_run=round(peak_run, 1), max_distance=round(lo, 1)); print(r, out['power'][r])
# ---------------- ACCURACY (power = touch = 100)
print('ACCURACY: target 10/20/30/40 m away at 27 m/s, power and touch 100; closest approach of the ball to the receiver hands (3D); hit% within 0.6 m (gap) and 1.2 m (catch radius)')
rng = random.Random(1); NS = 600
for r in RATINGS:
    row = {}
    for d in (10, 20, 30, 40):
        o = (0., 0., 1.6); tgt = (d, 0., 1.6); el = solve_el(o, tgt, 27., 1.6); lat = []; ver = []
        for _ in range(NS):
            lat.append(miss3d(path(o, throw(rng, o, 0., el, 27., r, 100)), tgt))
        row[d] = dict(mean_miss=round(st.mean(min(x, 30) for x in lat), 2), hit_06=round(sum(x <= .6 for x in lat) / NS, 2), hit_12=round(sum(x <= 1.2 for x in lat) / NS, 2))
    out['accuracy'][r] = row; print(r, {d: (v['mean_miss'], v['hit_06'], v['hit_12']) for d, v in row.items()})
print('SPEED vs PRECISION (accuracy 70, 20 m target, power and touch 100): the same thrower at different ball speeds')
for sp in (15., 20., 27., 35., 40.):
    o = (0., 0., 1.6); tgt = (20., 0., 1.6); el = solve_el(o, tgt, sp, 1.6)
    if el is None: continue
    lat = [miss3d(path(o, throw(rng, o, 0., el, sp, 70, 100)), tgt) for _ in range(NS)]
    out['speed_precision'][sp] = dict(mean_miss=round(st.mean(lat), 2), hit_12=round(sum(x <= 1.2 for x in lat) / NS, 2)); print(sp, out['speed_precision'][sp])
# ---------------- TOUCH (power = accuracy = 100): lob over an obstruction
H_OBS = 3.0; MARGIN = .25; ZC = 1.8
print('TOUCH: a defender-height obstruction (top %.1f m) midway; lob must clear it by %.2f m and come down within 1.2 m of the receiver at hand height %.1f m' % (H_OBS, MARGIN, ZC))
for r in RATINGS:
    row = {}
    for D in (6, 9, 12):
        o = (0., 0., 1.6); chosen = None
        for ang in range(45, 86, 1):
            el = math.radians(ang); sp = solve_speed_lob(o, D, el, ZC); pth = path(o, vec(0., el, sp)); zm = next((q[3] for q in pth if q[1] >= D / 2), 0.)
            if zm >= H_OBS + MARGIN and sp <= V_CAP: chosen = (el, sp); break
        if chosen is None: row[D] = None; continue
        ok = clear = 0; errs = []
        for _ in range(NS):
            pth = path(o, throw(rng, o, 0., chosen[0], chosen[1], 100, r)); zm = next((q[3] for q in pth if q[1] >= D / 2), 0.); c = zm >= H_OBS
            e = miss3d(pth, (D, 0., ZC)); errs.append(e); clear += c; ok += (c and e <= 1.2)
        row[D] = dict(elev=round(math.degrees(chosen[0])), speed=round(chosen[1], 1), clears=round(clear / NS, 2), complete=round(ok / NS, 2), mean_miss=round(st.mean(errs), 2))
    out['touch'][r] = row; print(r, {d: (v['complete'], v['mean_miss']) if v else None for d, v in row.items()})
json.dump(out, open('throw_lab_v0.json', 'w'), default=str)
