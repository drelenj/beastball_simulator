"""HP-002 Stage B probes (read-only).  (a) which jump mechanism fires (legacy omniscient plan_jumps vs PRISM-belief update_jumps);
(b) route_receiver: how far the true-ball interception target the receiver is given differs from what his own ball belief would give, and how often he has no belief yet.
usage: python3 tools/audit_probes.py <seed> <out.json> <full|b0>"""
import sys, os, json, math, copy, collections, statistics
seed = int(sys.argv[1]); out = sys.argv[2]; fs = sys.argv[3]
if fs == 'full':
    os.environ.update(PRISM_I='1', PRISM_OFFBALL='1', PRISM_TEAMVIEW='1', PRISM_FREEVIEW='1', PRISM_JSPLIT='1', PRISM_OFFACT='1', CATCH_V2='1', PRISM_KEEPER='1', HAND_FIGHT='1')
sys.argv = ['x']; sys.path.insert(0, os.getcwd())
import pocket4_proto as X
P = X.install(X.load_pocket()); S = X.S; CO = P.CORE; Match = CO.match.Match
import importlib; core = importlib.import_module(Match.__module__)
cap = {}; rr = collections.Counter(); gaps = []; berr = []
ostep = Match.step
def step(self): cap['m'] = self; return ostep(self)
Match.step = step
orr = Match.route_receiver
def route(self, targets):
    r = orr(self, targets)
    b = self.s.ball; q = self.s.players.get(b.intended) if b.intended else None
    if q is not None and b.carrier is None and q.id in targets and fs == 'full' and getattr(S, 'ball_belief', None):
        rr['calls'] += 1; bel = S.ball_belief(self, q, 3)
        if bel is None: rr['no_belief_yet'] += 1; return r
        bb = copy.copy(b); bb.x, bb.y, bb.z, bb.vx, bb.vy, bb.vz = bel[:6]; bb._path_cache = None
        path = core.predict_path(bb, self.assume['gravity'], self.assume['ball_drag'], self.assume['ball_restitution'])
        reach = q.a.reach * (1.1 if q.role == 'keeper' else .9); tb = core.intercept_xy(q, path, reach, False); tt = targets[q.id]
        gaps.append(math.hypot(tb[0] - tt[0], tb[1] - tt[1])); berr.append(math.hypot(bel[0] - b.x, bel[1] - b.y))
    return r
Match.route_receiver = route
over, ex, names = X.make_rosters(seed=seed); res, log, el = X.run(P, over, ex, names, seed=seed, short=True)
m = cap['m']
st = dict(legacy_jumps_planned=m.p4.stats.get('jumps_planned', 0), legacy_jumps_fired=m.p4.stats.get('jumps', 0), prism_field_jumps=m.stats.get('field_jumps', 0))
q = lambda v, f: round(sorted(v)[int(f * (len(v) - 1))], 2) if v else None
rep = dict(seed=seed, flagset=fs, score=res['score'], jumps=st, route=dict(rr), gap_true_vs_belief_target_m=dict(n=len(gaps), median=q(gaps, .5), p90=q(gaps, .9), mean=round(statistics.mean(gaps), 2) if gaps else None), ball_belief_pos_err_m=dict(median=q(berr, .5), p90=q(berr, .9)))
json.dump(rep, open(out, 'w'), indent=1); print(json.dumps(rep))
