"""1v2 scenario harness (real Match, real contact/pass/tackle kernel).  A0 carries toward goal, A1 is an off-ball threat running alongside,
B0 is the tested defender (optionally B1 a teammate defender).  Everyone else is parked.  The carrier uses the real policy; A1 runs a fixed route.
B0 holds still for PRELUDE_S so perception warms up, then plays a fixed OPTION for RUN_S:
  lane fraction f: 0 = go at the carrier, .35 = shade toward the threat, .7 = sit in the passing lane, 1 = mark the threat.
Deterministic given (seed, scenario, option).  Outcome = attack value over the run (see value()).
"""
import sys, os, json, math, random, collections
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
OPTIONS = (0., .35, .7, 1.)
PRELUDE_S, RUN_S = 0.4, 3.8
W_GOAL, W_TURN = 20., 15.            # [P] attack value = ball advance (m) + 20 per goal - 15 per turnover

_P = {}
def proc():
    if _P: return _P
    import tend_check as T, pocket4_proto as X
    P = X.install(X.load_pocket()); CO = P.CORE; S = X.S
    over, ex, names = X.make_rosters(T.G.read_csv('Ala_Lady_Reds_input.csv'), T.G.read_csv('Xenar_Dzaku_input.csv'), 1)
    S.tend = {pid: X.PT.Tend(n['position'] if n['position'] in X.PT.POSITIONS else 'TRK', n.get('report_arch', '')) for pid, n in names.items()}
    S.on = set(X.SYSTEMS); S.shape = 'sphere'; S.extras = ex; S.names = names; S.seed = 1
    P.ROSTER_OVERRIDES = P.validate_roster(over) and over
    st = dict(P.SETTINGS); st['save_events'] = False; st['archery'] = False
    Policy = CO.policies.Policy; o_targets = Policy.targets
    def targets(self, s):
        out = o_targets(self, s); c = _P.get('ctrl')
        if not c: return out
        for pid in c['parked']:
            q = s.players[pid]; out[pid] = (q.x, q.y)
        if self.team == 'A':
            a1 = s.players[c['a1']]; out[c['a1']] = (a1.x + 12., a1.y)
        else:
            d = s.players[c['b0id']]; out[c['b0id']] = c['b0'](s, d)
            b1id = c.get('b1id')
            if b1id and b1id in s.players and b1id not in c['parked']: q = s.players[b1id]; out[b1id] = c['b1'](s, q) if c.get('b1') else (q.x, q.y)
        return out
    Policy.targets = targets
    o_rank, o_choice = Policy.pass_ranked, Policy.pass_choice
    def pass_ranked(self, s, q):
        r = o_rank(self, s, q); c = _P.get('ctrl')
        return [x for x in r if x.id == c['a1']] if c and q.team == 'A' else r
    def pass_choice(self, s, q):
        c = _P.get('ctrl')
        if c and q.team == 'A':
            r = o_rank(self, s, q); return next((x for x in r if x.id == c['a1']), None)
        return o_choice(self, s, q)
    Policy.pass_ranked = pass_ranked; Policy.pass_choice = pass_choice
    _P.update(X=X, P=P, CO=CO, S=S, st=st, names=names)
    return _P

def lane_point(c, t, f): return (c[0] + (t[0] - c[0]) * f, c[1] + (t[1] - c[1]) * f)

def run(seed, sc, option, hooks=None):
    """sc: dict(vc, dd, sD, tx, ty, ids=(a0,a1,b0,b1|None), b1pos). option: lane fraction in OPTIONS (or None: only the prelude).
    hooks.decide(m, s, sc) -> option, called once at the decision time (after the prelude); returns the chosen lane fraction."""
    p = proc(); CO, P, S = p['CO'], p['P'], p['S']; Ty = CO.types
    S.seed = seed
    for k in ('fprism', 'flast', 'fstats', 'pm'):
        v = getattr(S, k, None)
        if isinstance(v, dict) or isinstance(v, collections.Counter): v.clear()
        elif k == 'pm' and v is not None: S.pm = None
    m = CO.match.Match(P.configuration(p['st'], seed, P.CALIBRATION)); s = m.s
    s.phase = Ty.Phase.LIVE; s.now = 1000; s.owner = 'A'; s.opening_team = 'A'; s.alternate = 'B'; s.opening_deadline = None; s.opening_touched = True
    a0, a1, b0, b1 = sc['ids']
    # re-label the chosen players as A0/A1/B0/B1 positions by swapping which roster player stands where: simplest is to keep ids and move them
    park = []
    for q in s.players.values():
        if q.active and q.role == 'field' and q.id not in (a0, a1, b0, b1):
            i = int(q.id[1:]); q.x, q.y = (20. if q.team == 'A' else 80.), (3. + 3. * i) if q.team == 'A' else (97. - 3. * i)
            q.vx = q.vy = 0.; q.target = (q.x, q.y); q.posture = 'upright'; park.append(q.id)
    def put(pid, xy, v=(0., 0.)):
        q = s.players[pid]; q.x, q.y = float(xy[0]), float(xy[1]); q.vx, q.vy = float(v[0]), float(v[1]); q.target = (q.x, q.y); q.posture = 'upright'
        if q.speed > .3: q.facing = CO.geometry.unit(q.vx, q.vy)
        q.fatigue = 1.0; return q
    x0, y0 = 25., 50.
    put(a0, (x0, y0), (sc['vc'], 0.)); put(a1, (x0 + sc['tx'], y0 + sc['ty']), (sc['vc'], 0.))
    put(b0, (x0 + sc['dd'], y0 + sc['sD']), (-1., 0.))
    if b1: put(b1, sc['b1pos'])
    s.players[a0].next_decision = s.now + int(sc.get('dec_ms', 2000))
    s.ball = Ty.Ball(mode=Ty.BallMode.CONTROLLED, carrier=a0, control_time=s.now - 500, last_touch='A', scoring=True); m.e.follow_carrier()
    # the scenario ids are fixed names in the control hook: swap by aliasing through the hook
    state = dict(opt=None, chosen=None)
    def b0_target(s_, d):
        if state['opt'] is None: return (d.x, d.y)
        c, t = s_.players[a0], s_.players[a1]
        return lane_point((c.x + c.vx * .3, c.y + c.vy * .3), (t.x, t.y), state['opt'])
    def b1_target(s_, q):
        if sc.get('b1mode') == 'marks': t = s_.players[a1]; return (t.x, t.y)
        return (q.x, q.y)
    parked = set(park)
    import prism_field_v0 as _PF
    _PF.SKIP.clear()
    if os.environ.get('DRILL_SKIP','1') == '1': _PF.SKIP.update(parked)
    p['ctrl'] = dict(parked=parked, b0=b0_target, b1=b1_target, a0=a0, a1=a1, b0id=b0, b1id=b1)
    start = s.now; ev0 = len(m.e.log); bx0 = s.ball.x; feats = None
    t_dec = start + int(PRELUDE_S * 1000); t_end = t_dec + int(RUN_S * 1000)
    guard = 0
    while s.now < t_end and guard < 4000 and s.phase != Ty.Phase.FINAL:
        guard += 1
        if state['opt'] is None and s.now >= t_dec:
            if hooks and hooks.get('decide'): state['chosen'] = hooks['decide'](m, s, sc)
            state['opt'] = option if option is not None else state['chosen']
            ev_dec = len(m.e.log); bx_dec = s.ball.x
        m.step()
    p['ctrl'] = None
    log = m.e.log[ev_dec:] if state['opt'] is not None else []
    evs = collections.Counter(e['event'] for e in log)
    goal = sum(1 for e in log if e['event'] == 'goal' and e['data'].get('team', 'A') == 'A') if evs.get('goal') else 0
    turn = 1 if (s.owner != 'A' or evs.get('strip')) else 0
    adv = (s.ball.x if s.ball.carrier or True else bx_dec) - bx_dec
    rel = [e for e in log if e['event'] == 'release']
    out = dict(adv=adv, goal=goal, turn=turn, ev={k: evs.get(k, 0) for k in ('tackle_count', 'strip', 'release', 'goal', 'possession_change', 'control')},
               passed=int(any(e['data'].get('player') == a0 for e in rel)), t_end=s.now - t_dec, chosen=state['chosen'])
    # features of the first pass
    rel0 = next((e for e in log if e['event'] == 'release' and e['data'].get('player') == a0), None)
    ctl = next((e for e in log if e['event'] == 'control' and e['data'].get('player') == a1), None)
    hold = next((e for e in log if e['event'] == 'c3_hold_start' and e['data'].get('target') == a0), None)
    out['f'] = dict(t_rel=(rel0['t_ms'] if rel0 else None), completed=int(ctl is not None), held_carrier=int(hold is not None),
                    d_rec=(math.hypot(s.players[b0].x - s.players[a1].x, s.players[b0].y - s.players[a1].y) if ctl is not None else None))
    # defender-centric outcome at the end of the horizon: attack kept the ball and got past him = 1; kept but he is still ahead of the ball = .4; lost or stopped = 0
    B0 = s.players[b0]; held = (s.owner == 'A' and not evs.get('strip') and not evs.get('tackle_count') and not turn and not out['f']['held_carrier'])
    past = s.ball.x >= B0.x + 2.
    out['beat'] = 0. if not held else (1. if past else .4)
    out['value'] = out['beat']
    return out
