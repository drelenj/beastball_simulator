"""Hand-contest lab: two opposing athletes stand with overlapping hand spheres; a pass (45 m/s) arrives between them.  Who ends up with the ball?
usage: python3 hand_contest_lab.py   (writes hand_contest_lab.json).  Each row changes ONE pillar of A1 against an otherwise identical B0."""
import sys, os, math, json, copy, importlib, collections, multiprocessing as mp
os.environ['PRISM_I'] = '1'; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
BASE = dict(catching=80., awareness=70., height=2.55, reach=1.173, mass=230., strength=70., contact_resistance=70., balance=70.)
def one(a):
    name, da, db, v, seed = a; pa = da.pop('prism', None); pb = db.pop('prism', None)
    import scenario_1v2_v0 as SC
    p = SC.proc(); CO, P, S = p['CO'], p['P'], p['S']; Ty = CO.types; core = importlib.import_module(CO.match.Match.__module__)
    ov = copy.deepcopy(P.ROSTER_OVERRIDES); ov.setdefault('A1', {}).update(BASE); ov['A1'].update(da); ov.setdefault('B0', {}).update(BASE); ov['B0'].update(db); P.ROSTER_OVERRIDES = ov
    import prism_ratings_v0 as PR; S.prism_r = {'A1': dict(PR.NEUTRAL, **(pa or {})), 'B0': dict(PR.NEUTRAL, **(pb or {}))}
    S.seed = seed; m = CO.match.Match(P.configuration(p['st'], seed, dict(P.CALIBRATION))); s = m.s
    s.phase = Ty.Phase.LIVE; s.now = 1000; s.owner = 'A'; s.opening_team = 'A'; s.alternate = 'B'; s.opening_deadline = None; s.opening_touched = True
    park = []
    for q in s.players.values():
        if q.active and q.role == 'field' and q.id not in ('A0', 'A1', 'B0'):
            i = int(q.id[1:]); q.x, q.y = (5. if q.team == 'A' else 95.), (3. + 3. * i) if q.team == 'A' else (97. - 3. * i); q.vx = q.vy = 0.; q.target = (q.x, q.y); park.append(q.id)
    sh = s.players['A0']; sh.x, sh.y, sh.vx, sh.vy = 30., 50., 0., 0.; sh.target = (sh.x, sh.y); sh.posture = 'upright'; sh.next_decision = s.now + 10 ** 7
    A1, B0 = s.players['A1'], s.players['B0']
    for q, y in ((A1, 49.75), (B0, 50.25)): q.x, q.y, q.vx, q.vy = 50., y, 0., 0.; q.target = (q.x, q.y); q.posture = 'upright'; q.next_decision = s.now + 10 ** 7
    s.ball = Ty.Ball(mode=Ty.BallMode.CONTROLLED, carrier='A0', control_time=s.now - 500, last_touch='A'); m.e.follow_carrier()
    import prism_field_v0 as _PF; _PF.SKIP.clear(); _PF.SKIP.update(park + ['A0', 'A1', 'B0'])
    p['ctrl'] = dict(parked=set(park), b0=lambda s_, d: (d.x, d.y), b1=None, a0='A0', a1='A1', b0id='B0', b1id=None)
    b = s.ball; hh = .5 * (A1.hand_height + B0.hand_height); sol = core.launch_for((b.x, b.y, b.z), (50., 50., hh), v, m.assume['gravity'], m.assume['ball_drag'])
    if sol is None: return a, None
    m.e.release('A0', sol[0], 'pass', None, True); t0 = s.now; g = 0
    while s.now < t0 + int((sol[1] + 1.) * 1000) and g < 2000 and s.ball.carrier in (None, 'A0'): g += 1; m.step()
    return a, dict(who=s.ball.carrier, hc=m.stats.get('hand_contests', 0), ties=m.stats.get('hand_ties', 0))
ROWS = {
 'even': ({}, {}),
 'reach 1.40 v 1.00': (dict(reach=1.40), dict(reach=1.00)),
 'mass 330 v 150': (dict(mass=330.), dict(mass=150.)),
 'strength 100 v 40': (dict(strength=100.), dict(strength=40.)),
 'catching 100 v 40': (dict(catching=100.), dict(catching=40.)),
 'resistance 100 v 40': (dict(contact_resistance=100., balance=100.), dict(contact_resistance=40., balance=40.)),
 'PRISM Reaction .98 v .40': (dict(prism=dict(reaction=.98)), dict(prism=dict(reaction=.40))),
}
if __name__ == '__main__':
    N = int(os.environ.get('N', '40')); out = {}
    jobs = [(nm, dict(da), dict(db), 25., sd) for nm, (da, db) in ROWS.items() for sd in range(1, N + 1)]
    with mp.Pool(2, maxtasksperchild=40) as pool: res = pool.map(one, jobs, chunksize=8)
    agg = collections.defaultdict(lambda: collections.Counter())
    for a, r in res:
        if r: agg[a[0]][r['who']] += 1; agg[a[0]]['hc'] += r['hc']; agg[a[0]]['ties'] += r['ties']
    for nm in ROWS:
        c = agg[nm]; n = c['A1'] + c['B0']; print(f"{nm:34s} A1 {c['A1']:3d}  B0 {c['B0']:3d}  other {sum(v for k,v in c.items() if k not in ('A1','B0','hc','ties')):3d}  contests {c['hc']:3d} ties {c['ties']:3d}  P(A1)={c['A1']/max(1,n):.2f}")
        out[nm] = dict(c)
    json.dump(out, open('hand_contest_lab.json', 'w'))
