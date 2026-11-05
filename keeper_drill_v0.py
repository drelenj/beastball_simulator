"""Keeper drill: a 12 ft Keeper with every rating 100 (and the roster's best physicals) against a shot placed anywhere on the net.  Net = semicircle radius 6 m about (goal plane, y=50, z=0) (engine legal_goal).
Shooter stands D m from the goal plane on the centre line, ball released by force (no throw model) at ball speed v toward the chosen point.  Scored = goal event.
python3 keeper_drill_v0.py"""
import sys, os, math, json, copy, importlib, multiprocessing as mp
os.environ['PRISM_I'] = '1'; os.environ['DRILL_SKIP'] = '1'; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
KEEPER = dict(height=3.6576, reach=.46 * 3.6576, mass=275., maximum_speed=44.7, acceleration=18., braking=36.2, turning=15.5, jump_height=1.6,
              strength=100, agility=100, endurance=100, balance=100, contact_resistance=100, tackling=100, blocking=100, ball_handling=100, passing=100, kicking=100, catching=100, awareness=100, archery_accuracy=100, keeper_skill=100)
def one(a):
    D, v, phi, seed = a[:4]; RA, RT = (a[4], a[5]) if len(a) > 4 else (None, None)
    import scenario_1v2_v0 as SC
    p = SC.proc(); CO, P, S = p['CO'], p['P'], p['S']; Ty = CO.types; core = importlib.import_module(CO.match.Match.__module__)
    NETR = float(os.environ.get('NETR', '6'))
    def lg(y, z, r=.1075): return z >= r - 1e-7 and math.hypot(y - 50., z) + r <= NETR + 1e-7
    pk = CO.geometry.__name__.rsplit('.', 1)[0]
    for mod in list(sys.modules.values()):
        if getattr(mod, '__name__', '').startswith(pk) and hasattr(mod, 'legal_goal'): mod.legal_goal = lg
    KH = round(float(os.environ.get('KFT', '12')) * .3048, 4); ov = copy.deepcopy(P.ROSTER_OVERRIDES); ov['B10'].update(KEEPER); ov['B10'].update(height=KH, reach=.46 * KH); P.ROSTER_OVERRIDES = ov
    cal = dict(P.CALIBRATION); cal['keeper_height_m'] = round(KH, 4)
    for kv in filter(None, os.environ.get('CAL', '').split(',')): k_, v_ = kv.split('='); cal[k_] = float(v_)
    S.seed = seed
    m = CO.match.Match(P.configuration(p['st'], seed, cal)); s = m.s
    s.phase = Ty.Phase.LIVE; s.now = 1000; s.owner = 'A'; s.opening_team = 'A'; s.alternate = 'B'; s.opening_deadline = None; s.opening_touched = True
    park = []
    for q in s.players.values():
        if q.active and q.role == 'field' and q.id != 'A0':
            i = int(q.id[1:]); q.x, q.y = (20. if q.team == 'A' else 60.), (3. + 3. * i) if q.team == 'A' else (97. - 3. * i); q.vx = q.vy = 0.; q.target = (q.x, q.y); park.append(q.id)
    sh = s.players['A0']; sh.x, sh.y, sh.vx, sh.vy = 100. - D, 50., 0., 0.; sh.target = (sh.x, sh.y); sh.posture = 'upright'; sh.next_decision = s.now + 10 ** 7
    K = s.players['B10']; K.x, K.y = 97., 50.; K.target = (K.x, K.y)
    s.ball = Ty.Ball(mode=Ty.BallMode.CONTROLLED, carrier='A0', control_time=s.now - 500, last_touch='A', scoring=True); m.e.follow_carrier()
    import prism_field_v0 as _PF; _PF.SKIP.clear(); _PF.SKIP.update(park)
    p['ctrl'] = dict(parked=set(park), b0=lambda s_, d: (d.x, d.y), b1=None, a0='A0', a1='A1', b0id='B0', b1id=None)
    r = max(.4, NETR - .6); ty = 50. + r * math.cos(math.radians(phi)); tz = max(.2, r * math.sin(math.radians(phi)))
    b = s.ball; sol = core.launch_for((b.x, b.y, b.z), (100., ty, tz), v, m.assume['gravity'], m.assume['ball_drag'])
    if sol is None: return a, None
    if RA is not None:   # full throw model: direction error grows with ball speed (accuracy), delivered speed error (touch)
        import random
        rg = random.Random('%d|%s|%s' % (seed, a, 'n')); X = lambda r: (r - 40.) / 60.
        vx_, vy_, vz_ = sol[0]; sp0 = math.sqrt(vx_ ** 2 + vy_ ** 2 + vz_ ** 2); az = math.atan2(vy_, vx_); el = math.asin(vz_ / sp0)
        sd = math.radians(max(.15, 3. * (1. - X(RA))) * sp0 / 67.); sv = max(.003, .10 * (1. - X(RT)))
        az += rg.gauss(0, sd); el += rg.gauss(0, sd / 2); sp1 = sp0 * (1. + rg.gauss(0, sv))
        sol = ((sp1 * math.cos(el) * math.cos(az), sp1 * math.cos(el) * math.sin(az), sp1 * math.sin(el)), sol[1])
    ev0 = len(m.e.log); ok = m.e.release('A0', sol[0], 'shot', None, True); s.ball.scoring = True; s.ball.last_releaser = 'A0'; t0 = s.now; g = 0
    if os.environ.get('DBG'): print('sol', [round(x, 2) for x in sol[0]], 'ball v', [round(x, 2) for x in (s.ball.vx, s.ball.vy, s.ball.vz)], 'pos', (round(s.ball.x, 2), round(s.ball.y, 2), round(s.ball.z, 2)))
    while s.now < t0 + int((sol[1] + 3.) * 1000) and g < 3000 and s.phase != Ty.Phase.FINAL:
        g += 1; m.step()
        if os.environ.get('DBG'): print(s.now - t0, (round(s.ball.x, 1), round(s.ball.y, 1), round(s.ball.z, 2)), str(s.ball.mode), 'K', (round(K.x, 1), round(K.y, 1), round(K.z, 2)), [e['event'] for e in m.e.log[ev0 + 1:] if e['t_ms'] == s.now - 1000 + 0][:0])
    p['ctrl'] = None
    log = m.e.log[ev0:]; goal = any(e['event'] == 'goal' for e in log); keeper_touch = any(e['data'].get('player') == 'B10' and e['event'] in ('control', 'touch', 'block', 'deflection', 'catch') for e in log)
    import collections
    nog = [e for e in log if e['event'] in ('no_goal', 'boundary', 'keeper_read', 'keeper_landed')]
    dbg = (nog,) +  (round(b.x,1), round(b.y,1), round(b.z,2), str(s.ball.mode), dict(collections.Counter(e['event'] for e in log)))
    return a, dict(dbg=dbg, goal=goal, flight=round(sol[1], 3), touch=keeper_touch, rel=bool(ok))
if __name__ == '__main__':
    Ds = (5, 10, 15, 20, 30, 40, 60, 80); phis = tuple(range(0, 181, 15)); jobs = [(D, v, phi, 1) for v in (67.1, 134.1) for D in Ds for phi in phis]
    with mp.Pool(2, maxtasksperchild=20) as pool: res = pool.map(one, jobs, chunksize=2)
    out = {}
    for a, r in res: out.setdefault('%.0f|%d' % (a[1], a[0]), {})[a[2]] = r
    json.dump(out, open('keeper_drill_v0.json', 'w'))
    for k, row in out.items():
        sc = [phi for phi, r in sorted(row.items()) if r and r['goal']]; print(k, 'flight %.2fs' % next((r['flight'] for r in row.values() if r), 0), 'goals', len(sc), '/', len(row), 'scoring angles', sc, flush=True)
