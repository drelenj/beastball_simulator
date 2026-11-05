"""Catch lab: a stationary receiver, a forced pass of speed v straight at his hands (plus a lateral miss of `miss` x his reach), repeated over seeds.
Scored: did the receiver acquire the ball (secure catch).  Receiver ratings, height and reach are set per run.
usage: python3 catch_lab_v0.py   (writes catch_lab_v0.json)"""
import sys, os, math, json, copy, importlib, collections, multiprocessing as mp
os.environ['PRISM_I'] = '1'; os.environ['DRILL_SKIP'] = '1'; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
def one(a):
    v, rating, miss, reach, height, D, seed = a[:7]; dz = a[7] if len(a) > 7 else 0.; jmp = a[8] if len(a) > 8 else 100.
    import scenario_1v2_v0 as SC
    p = SC.proc(); CO, P, S = p['CO'], p['P'], p['S']; Ty = CO.types; core = importlib.import_module(CO.match.Match.__module__)
    ov = copy.deepcopy(P.ROSTER_OVERRIDES); ov.setdefault('A1', {}).update(catching=rating, awareness=70., height=height, reach=reach, jump_height=round(1.3 * jmp / 100., 3)); P.ROSTER_OVERRIDES = ov
    S.seed = seed; m = CO.match.Match(P.configuration(p['st'], seed, dict(P.CALIBRATION))); s = m.s
    s.phase = Ty.Phase.LIVE; s.now = 1000; s.owner = 'A'; s.opening_team = 'A'; s.alternate = 'B'; s.opening_deadline = None; s.opening_touched = True
    park = []
    for q in s.players.values():
        if q.active and q.role == 'field' and q.id not in ('A0', 'A1'):
            i = int(q.id[1:]); q.x, q.y = (5. if q.team == 'A' else 95.), (3. + 3. * i) if q.team == 'A' else (97. - 3. * i); q.vx = q.vy = 0.; q.target = (q.x, q.y); park.append(q.id)
    sh = s.players['A0']; sh.x, sh.y, sh.vx, sh.vy = 30., 50., 0., 0.; sh.target = (sh.x, sh.y); sh.posture = 'upright'; sh.next_decision = s.now + 10 ** 7
    rc = s.players['A1']; rc.x, rc.y, rc.vx, rc.vy = 30. + D, 50., 0., 0.; rc.target = (rc.x, rc.y); rc.posture = 'upright'; rc.next_decision = s.now + 10 ** 7
    s.ball = Ty.Ball(mode=Ty.BallMode.CONTROLLED, carrier='A0', control_time=s.now - 500, last_touch='A'); m.e.follow_carrier()
    import prism_field_v0 as _PF; _PF.SKIP.clear(); _PF.SKIP.update(park + ['A0', 'A1'])
    p['ctrl'] = dict(parked=set(park), b0=lambda s_, d: (d.x, d.y), b1=None, a0='A0', a1='A1', b0id='B0', b1id=None)
    R = rc.a.reach * .9; tgt = (rc.x, rc.y + miss * R, rc.hand_height + dz)
    b = s.ball; sol = core.launch_for((b.x, b.y, b.z), tgt, v, m.assume['gravity'], m.assume['ball_drag'])
    if sol is None: return a, None
    ev0 = len(m.e.log); m.pass_signal = m.e.pass_signal = ('A1', s.now - 500); m.e.release('A0', sol[0], 'pass', 'A1', True); t0 = s.now; g = 0
    while s.now < t0 + int((sol[1] + 1.) * 1000) and g < 2000 and s.ball.carrier is None: g += 1; m.step()
    log = m.e.log[ev0:]; caught = s.ball.carrier == 'A1'
    return a, dict(jumps=m.stats.get('field_jumps'), maxz=round(rc.z,2), pos=(round(s.ball.x,1),round(s.ball.y,1),round(s.ball.z,2)), caught=caught, flight=round(sol[1], 3), ev=sorted({e['event'] for e in log}))
if __name__ == '__main__':
    quick = os.environ.get('QUICK') == '1'; N = 3 if quick else 20; D = 20.
    VS = (20, 30, 45, 67, 100, 134); out = {}
    jobs = []
    for v in VS:
        for rating in (40, 70, 100):
            for miss in (0., .5):
                for reach in (1.0, 1.173, 1.4): jobs += [(v, rating, miss, reach, 2.55, D, sd) for sd in range(1, N + 1)]
    for v in VS:
        for rating in (50, 60, 80, 90): jobs += [(v, rating, 0., 1.173, 2.55, D, sd) for sd in range(1, N + 1)]
    with mp.Pool(2, maxtasksperchild=30) as pool: res = pool.map(one, jobs, chunksize=6)
    agg = collections.defaultdict(list)
    for a, r in res:
        if r: agg[a[:5]].append(1 if r['caught'] else 0)
    for k, x in sorted(agg.items()): out['|'.join(map(str, k))] = dict(p=sum(x) / len(x), n=len(x))
    json.dump(out, open('catch_lab_v0.json', 'w'))
    print('done', len(out))
