"""Off-ball scenarios: each isolates one decision and one rating.  usage: N=20 python3 offball_scenarios.py [scenario ...]    (writes offball_scenarios.json)
 free_ball   Live Ball Pursuit : a loose ground ball rolls between A1 and B0 (equal distances); who gets it first, rating .98 vs .40 (and .70 v .70 control)
 air_ball    In-Air Ball Pursuit: a pass in the air comes down between A1 and B0; who gets it
 open_space  RUN_OPEN          : attacker A1 starts covered by B0; openness (distance to nearest defender) after 4 s, OFFACT off (engine target only) vs on
 call        CALL              : the carrier is pressed and cannot see A1 (behind him, outside his cone); how often the first pass goes to A1, OFFACT calls on vs off
 engage      ENGAGE / WAIT     : action mix chosen by an off-ball attacker near a defender who threatens the carrier; hand-fight pairs formed
Everything else is parked.  Deterministic per seed."""
import sys, os, math, json, copy, importlib, collections, multiprocessing as mp
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
for k, v in (('PRISM_OFFACT', '1'), ('PRISM_I', '1'), ('PRISM_OFFBALL', '1'), ('PRISM_TEAMVIEW', '1'), ('PRISM_FREEVIEW', '1'), ('PRISM_JSPLIT', '1'), ('CATCH_V2', '1'), ('PRISM_KEEPER', '1'), ('KP_MINOBS', '3'), ('HAND_FIGHT', '1')): os.environ.setdefault(k, v)
BASE = dict(height=2.55, reach=1.173, mass=197.)   # plus A1's own roster row for BOTH players (see world): everything equal, only the rating under test differs
PARKED = set()
def _pin(CO):
    Policy = CO.policies.Policy
    if getattr(Policy, '_pinned', False): return
    o = Policy.targets
    def targets(self, st):
        out = o(self, st)
        for pid in PARKED:
            q = st.players.get(pid)
            if q is not None and pid in out: out[pid] = (q.x, q.y)
        return out
    Policy.targets = targets; Policy._pinned = True
def world(a1=None, b0=None, ra1=None, rb0=None, seed=1, extra=None):
    import scenario_1v2_v0 as SC, prism_ratings_v0 as PR
    p = SC.proc(); CO, P, S = p['CO'], p['P'], p['S']; Ty = CO.types; _pin(CO); PARKED.clear()
    S.fstats.clear(); S.fprism.clear(); getattr(S, 'kprism', {}).clear(); getattr(S, 'oa', {}).clear(); getattr(S, 'calls', {}).clear()
    ov = copy.deepcopy(P.ROSTER_OVERRIDES)
    row = dict(ov.get('A1', {}))
    for pid, d in (('A1', a1), ('B0', b0)): ov[pid] = dict(row); ov[pid].update(BASE); ov[pid].update(d or {})
    P.ROSTER_OVERRIDES = ov
    S.prism_r = {pid: dict(PR.NEUTRAL, **(r or {})) for pid, r in (('A1', ra1), ('B0', rb0))}
    S.seed = seed; m = CO.match.Match(P.configuration(p['st'], seed, dict(P.CALIBRATION))); s = m.s
    s.phase = Ty.Phase.LIVE; s.now = 1000; s.opening_team = 'A'; s.alternate = 'B'; s.opening_deadline = None; s.opening_touched = True
    return p, CO, S, Ty, m, s
def park(p, s, keep):
    out = []
    for q in s.players.values():
        if q.active and q.role == 'field' and q.id not in keep:
            i = int(q.id[1:]); q.x, q.y = (5. if q.team == 'A' else 95.), (3. + 3. * i) if q.team == 'A' else (97. - 3. * i); q.vx = q.vy = 0.; q.target = (q.x, q.y); out.append(q.id); PARKED.add(q.id)
    return out
def place(q, x, y, face=None):
    q.x, q.y, q.vx, q.vy = x, y, 0., 0.; q.target = (x, y); q.posture = 'upright'
    if face: q.facing = face
def hold(p, s, carrier='A0', at=(30., 20.)):
    sh = s.players[carrier]; place(sh, *at); sh.next_decision = s.now + 10 ** 7; PARKED.add(carrier)
def free_ball(a):
    """one chaser (A1), a bouncing loose ball: how often he secures it within 8 s and how fast, by Live Ball Pursuit"""
    os.environ['PRISM_OFFACT'] = '1'; cfg, seed = a; p, CO, S, Ty, m, s = world(dict(), dict(), cfg.get('ra'), cfg.get('rb'), seed)
    s.owner = 'A'; pk = park(p, s, ('A0', 'A1')); hold(p, s); A1 = s.players['A1']; place(A1, 42. + 2. * (seed % 3), 48., (1., 0.))
    s.ball = Ty.Ball(mode=Ty.BallMode.LOOSE, x=50., y=30., z=.4, vx=1.5 * ((seed % 5) - 2), vy=15., vz=4.5, carrier=None, control_time=s.now, last_touch='A')
    import prism_field_v0 as PF; PF.SKIP.clear(); PF.SKIP.update(pk + ['A0'])
    for g in range(80):
        m.step()
        if s.ball.carrier == 'A1': return a, dict(who='A1', t=g)
    return a, dict(who='none', t=80)
def air_ball(a):
    """one receiver (A1), a pass in the air that lands off to his side: does he get under it (catch) and how fast, by In-Air Ball Pursuit"""
    os.environ['PRISM_OFFACT'] = '1'; cfg, seed = a; p, CO, S, Ty, m, s = world(dict(), dict(), cfg.get('ra'), cfg.get('rb'), seed)
    s.owner = 'A'; pk = park(p, s, ('A0', 'A1')); sh = s.players['A0']; place(sh, 30., 50.); sh.next_decision = s.now + 10 ** 7; PARKED.add('A0')
    A1 = s.players['A1']; tx, ty = 62., 50. + 3. + 1.1 * (seed % 6); place(A1, 60., 50., (1., 0.))
    s.ball = Ty.Ball(mode=Ty.BallMode.CONTROLLED, carrier='A0', control_time=s.now - 500, last_touch='A'); m.e.follow_carrier()
    import prism_field_v0 as PF; PF.SKIP.clear(); PF.SKIP.update(pk + ['A0'])
    core = importlib.import_module(CO.match.Match.__module__); b = s.ball
    sol = core.launch_for((b.x, b.y, b.z), (tx, ty, A1.hand_height), 22., m.assume['gravity'], m.assume['ball_drag'])
    for _ in range(8): m.step()
    m.e.release('A0', sol[0], 'pass', None, True)
    for g in range(60):
        m.step()
        if s.ball.carrier == 'A1': return a, dict(who='A1', t=g)
        if s.ball.carrier not in (None, 'A0'): break
    return a, dict(who='none', t=60)
def open_space(a):
    cfg, seed = a; p, CO, S, Ty, m, s = world(dict(), dict(), cfg.get('ra'), cfg.get('rb'), seed)
    os.environ['PRISM_OFFACT'] = '1' if cfg.get('act') else '0'
    s.owner = 'A'; pk = park(p, s, ('A0', 'A1', 'B0', 'B1', 'B2')); c = s.players['A0']; place(c, 40., 50., (1., 0.))
    A1, B0, B1, B2 = s.players['A1'], s.players['B0'], s.players['B1'], s.players['B2']
    place(A1, 52., 44., (1., 0.)); place(B0, 53.5, 46., (-1., 0.)); place(B1, 50., 58., (-1., 0.)); place(B2, 60., 40., (-1., 0.))
    s.ball = Ty.Ball(mode=Ty.BallMode.CONTROLLED, carrier='A0', control_time=s.now - 500, last_touch='A'); m.e.follow_carrier()
    import prism_field_v0 as PF; PF.SKIP.clear(); PF.SKIP.update(pk[:0])
    c.next_decision = s.now + 10 ** 7
    for g in range(40):
        c.target = (c.x + 1.5, c.y); m.step()
    op = min(math.hypot(A1.x - q.x, A1.y - q.y) for q in (B0, B1, B2))
    return a, dict(open=op, acts=dict(collections.Counter(v[1] for v in getattr(S, 'oa', {}).values())))
def call(a):
    cfg, seed = a; p, CO, S, Ty, m, s = world(dict(), dict(), cfg.get('ra'), cfg.get('rb'), seed)
    os.environ['PRISM_OFFACT'] = '1' if cfg.get('act') else '0'
    s.owner = 'A'; pk = park(p, s, ('A0', 'A1', 'A2', 'B0', 'B1')); c = s.players['A0']; place(c, 40., 50., (1., 0.))
    A1, A2, B0, B1 = s.players['A1'], s.players['A2'], s.players['B0'], s.players['B1']
    place(A1, 30., 58., (1., 0.)); place(A2, 56., 50., (-1., 0.)); place(B0, 44., 50., (-1., 0.)); place(B1, 54., 50., (-1., 0.))
    s.ball = Ty.Ball(mode=Ty.BallMode.CONTROLLED, carrier='A0', control_time=s.now - 500, last_touch='A'); m.e.follow_carrier()
    to = {'A1': None}
    for g in range(30):
        m.step()
        if s.ball.mode.value == 'passed' or s.ball.carrier not in ('A0',):
            tgt = getattr(s.ball, 'intended', None); return a, dict(first=tgt or s.ball.carrier or 'x', t=g, calls=S.fstats.get('oa_calls', 0), heard=S.fstats.get('call_heard', 0))
    return a, dict(first='none', t=30, calls=S.fstats.get('oa_calls', 0), heard=S.fstats.get('call_heard', 0))
def engage(a):
    cfg, seed = a; p, CO, S, Ty, m, s = world(dict(), dict(), cfg.get('ra'), cfg.get('rb'), seed)
    os.environ['PRISM_OFFACT'] = '1'
    s.owner = 'A'; pk = park(p, s, ('A0', 'A1', 'B0')); c = s.players['A0']; place(c, 40., 50., (1., 0.)); A1, B0 = s.players['A1'], s.players['B0']
    place(A1, 38., 56., (1., 0.)); place(B0, 47., 53., (-1., 0.))
    s.ball = Ty.Ball(mode=Ty.BallMode.CONTROLLED, carrier='A0', control_time=s.now - 500, last_touch='A'); m.e.follow_carrier(); c.next_decision = s.now + 10 ** 7
    for g in range(40): c.target = (c.x + 1.2, c.y); m.step()
    return a, dict(acts=dict(collections.Counter(v[1] for v in S.oa.values())), pairs=m.stats.get('hf_pairs', 0), steps=m.stats.get('hf_steps', 0), dB=math.hypot(B0.x - 47., B0.y - 53.))
SC_ = dict(free_ball=free_ball, air_ball=air_ball, open_space=open_space, call=call, engage=engage)
ROWS = {
 'free_ball': {'Live Ball Pursuit .40': dict(ra=dict(live_pursuit=.40)), 'Live Ball Pursuit .70': dict(ra=dict(live_pursuit=.70)), 'Live Ball Pursuit .98': dict(ra=dict(live_pursuit=.98))},
 'air_ball': {'In-Air Pursuit .40': dict(ra=dict(air_pursuit=.40)), 'In-Air Pursuit .70': dict(ra=dict(air_pursuit=.70)), 'In-Air Pursuit .98': dict(ra=dict(air_pursuit=.98))},
 'open_space': {'engine target only': dict(act=False), 'actions, judgment .98': dict(act=True, ra=dict(judgment=.98)), 'actions, judgment .40': dict(act=True, ra=dict(judgment=.40))},
 'call': {'no off-ball actions': dict(act=False), 'actions + calls': dict(act=True)},
 'engage': {'actions, judgment .70': dict()},
}
def run_cell(args):
    name, cfg, seeds = args
    with mp.get_context('fork').Pool(1, maxtasksperchild=1) as pool: return name, cfg, pool.map(SC_[name], [(cfg, sd) for sd in seeds], chunksize=1)
if __name__ == '__main__':
    N = int(os.environ.get('N', '12')); which = sys.argv[1:] or list(SC_); out = {}
    for name in which:
        for lab, cfg in ROWS[name].items():
            res = [r for _, r in (SC_[name]((cfg, sd)) if os.environ.get('INLINE') else (None, None) for sd in range(1, N + 1))] if os.environ.get('INLINE') else None
            if res is None:
                with mp.get_context('fork').Pool(2, maxtasksperchild=1) as pool: res = [r for _, r in pool.map(SC_[name], [(cfg, sd) for sd in range(1, N + 1)], chunksize=1)]
            out[f'{name}|{lab}'] = res
            if name in ('free_ball', 'air_ball'):
                c = collections.Counter(r['who'] for r in res); ok = [r['t'] for r in res if r['who'] == 'A1']; print(f"{name:11s} {lab:22s} secured {c['A1']:3d}/{len(res)}   mean time when secured {sum(ok)/max(1,len(ok))*.1:.2f}s")
            elif name == 'open_space': print(f"{name:11s} {lab:22s} openness after 4 s {sum(r['open'] for r in res)/len(res):.2f} m   actions {dict(collections.Counter(k for r in res for k, v in r['acts'].items() for _ in range(v)))}")
            elif name == 'call':
                c = collections.Counter(r['first'] for r in res); print(f"{name:11s} {lab:22s} first pass target {dict(c)}   calls {sum(r['calls'] for r in res)}  heard {sum(r['heard'] for r in res)}")
            else:
                print(f"{name:11s} {lab:22s} actions {dict(collections.Counter(k for r in res for k, v in r['acts'].items() for _ in range(v)))}   hand-fight pairs {sum(r['pairs'] for r in res)}  steps {sum(r['steps'] for r in res)}")
    json.dump(out, open('offball_scenarios.json', 'w'), default=str)
