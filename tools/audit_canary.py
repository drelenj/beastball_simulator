"""HP-002 canary / counterfactual probe (read-only).  At every carrier decision (Match.c4c2_decide = Pocket 2.0 pocket_decide), recompute the option values
(shoot, carry, continue, best pass) twice with the SAME pure functions: (A) on true state as the engine does today, (B) inside the carrier's own PRISM belief view
(prism_field_v0.with_view).  Records value differences and argmax flips.  Also reports how many opponents were hidden from the carrier at that moment and the effect of
moving only hidden opponents far away (hidden-state perturbation).  The probe never changes game state; integrity is proven by comparing the canonical event-log hash
with probe on vs off.
usage: python3 tools/audit_canary.py <seed> <out.json> <probe|noprobe>"""
import sys, os, json, math, hashlib, collections, statistics
seed = int(sys.argv[1]); out = sys.argv[2]; mode = sys.argv[3]
os.environ.update(PRISM_I='1', PRISM_OFFBALL='1', PRISM_TEAMVIEW='1', PRISM_FREEVIEW='1', PRISM_JSPLIT='1', PRISM_OFFACT='1', CATCH_V2='1', PRISM_KEEPER='1', HAND_FIGHT='1')
sys.argv = ['x']; sys.path.insert(0, os.getcwd())
import pocket4_proto as X
sys.path.insert(0, os.path.join(os.getcwd(), 'tools')); import t1_canon_hash as H

P = X.install(X.load_pocket()); S = X.S; CO = P.CORE; Match = CO.match.Match
rec = collections.defaultdict(list); n = collections.Counter()
def options_now(self, p, clock, arrow_t):
    E = self.c4c2_eval(p, p.x, p.y, clock, arrow_t, True)
    o = {'shoot': E['shoot'], 'carry': E['carry'], 'continue': self.c4c2_cont(p, p.x, p.y, clock, arrow_t)}
    best_pass = None
    if self.s.now - self.s.ball.control_time > 180:
        for q in self.pol[p.team].pass_ranked(self.s, p)[:6]:
            c = self.pocket_pass_option(p, q, clock)
            if c is not None and (best_pass is None or c['value'] > best_pass['value']): best_pass = c
    if best_pass: o['pass'] = best_pass['value']
    return o, (best_pass['q'].id if best_pass else None)
def argmax(o): return max(o, key=lambda k: (o[k], k == 'shoot'))
orig = Match.c4c2_decide
def decide(self, p, clock, danger_arrow):
    if mode == 'probe' and S.fprism.get(p.id) is not None and self.pocket_final:
        s = self.s; clk = self.pocket_budget(clock); arrow_t = None
        if danger_arrow: arrow_t = min((math.hypot(a.x - p.x, a.y - p.y) / max(1., math.hypot(a.vx, a.vy)) for a in s.arrows if a.live and a.team != p.team), default=None)
        pr = S.fprism[p.id]; now = s.now / 1000.
        opp = [o for o in s.players.values() if o.team != p.team and o.active and o.role == 'field']
        hidden = [o for o in opp if pr.bget(o.id) is None or pr.confidence(o.id, now) < S.CONF_MIN]
        A, qa = options_now(self, p, clk, arrow_t)
        B, qb = S.with_view(s, p, lambda: options_now(self, p, clk, arrow_t))
        n['decisions'] += 1; n['hidden_ge1'] += bool(hidden); n['hidden_sum'] += len(hidden); n['opp_sum'] += len(opp)
        flip = argmax(A) != argmax(B); n['argmax_flip'] += flip; n['pass_target_change'] += (qa != qb and 'pass' in A and 'pass' in B)
        for k in ('shoot', 'carry', 'continue', 'pass'):
            if k in A and k in B: rec[k].append(abs(A[k] - B[k]) / max(1e-9, max(abs(A[k]), abs(B[k]), 1e-3)))
        if hidden:   # hidden-state perturbation: send only the hidden opponents far away, true state otherwise
            sv = [(o, o.x, o.y) for o in hidden]
            try:
                for o in hidden: o.x, o.y = 1e5, 1e5
                C, qc = options_now(self, p, clk, arrow_t)
            finally:
                for o, x, y in sv: o.x, o.y = x, y
            n['pert_n'] += 1; n['pert_flip'] += (argmax(A) != argmax(C)); n['pert_changed'] += any(abs(A[k] - C[k]) > 1e-9 for k in A if k in C)
            n['pert_pass_target_change'] += (qa != qc and 'pass' in A and 'pass' in C)
    return orig(self, p, clock, danger_arrow)
Match.c4c2_decide = decide
over, ex, names = X.make_rosters(seed=seed); r, log, el = X.run(P, over, ex, names, seed=seed, short=True)
st = {k: dict(mean=round(statistics.mean(v), 4), median=round(statistics.median(v), 4), p90=round(sorted(v)[int(.9 * (len(v) - 1))], 4), n=len(v)) for k, v in rec.items() if v}
res = dict(seed=seed, mode=mode, score=r['score'], n_events=len(log), log_sha256=H.digest(log), result_sha256=H.digest({k: v for k, v in r.items() if not any(w in k.lower() for w in ('wall', 'cpu'))}), stats_sha256=H.digest({k: (v if not isinstance(v, float) else repr(v)) for k, v in sorted(getattr(P.CORE, 'LASTSTATS', {}).items())}) if False else None, counts=dict(n), rel_value_diff_true_vs_view=st)
json.dump(res, open(out, 'w'), indent=1); print(mode, seed, r['score'], len(log), res['log_sha256'][:12], dict(n))
