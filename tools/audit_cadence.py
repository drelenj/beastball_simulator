"""HP-002 r3 instrument: the `q.next_decision = s.now` write in route_receiver (match.py:2517).
For every route_receiver call that routes an intended receiver, record (before the original runs) how long the receiver's own decision timer still had to run
(natural_delay_ms = max(0, next_decision - now)) and whether the target the routine writes differs from the target he currently holds.  Read-only: logging around the original call.
Also: flights (distinct pass releases) vs calls, to show the write is repeated every tick of the flight, and the receiver's rated decision interval 1000*decision_speed*(1.3-.4*awareness).
usage: python3 tools/audit_cadence.py <seed> <out.json> <full|b0>"""
import sys, os, json, math, collections, statistics
seed = int(sys.argv[1]); out = sys.argv[2]; fs = sys.argv[3]
if fs == 'full':
    os.environ.update(PRISM_I='1', PRISM_OFFBALL='1', PRISM_TEAMVIEW='1', PRISM_FREEVIEW='1', PRISM_JSPLIT='1', PRISM_OFFACT='1', CATCH_V2='1', PRISM_KEEPER='1', HAND_FIGHT='1')
sys.argv = ['x']; sys.path.insert(0, os.getcwd())
import pocket4_proto as X
P = X.install(X.load_pocket()); Match = P.CORE.match.Match
orr = Match.route_receiver; rec = []; flights = set()
def route(self, targets):
    s = self.s; b = s.ball; q = s.players.get(b.intended) if b.intended else None
    pre = None
    if q is not None and b.carrier is None and b.mode.name in ('PASS', 'KICK') and s.phase.name == 'LIVE':
        pre = dict(now=s.now, nd=q.next_decision, held=getattr(q, 'target', None), t0=targets.get(q.id), q=q)
    r = orr(self, targets)
    if pre is not None and q.id in targets:
        q = pre['q']; new = targets[q.id]; held = pre['held']
        diff = math.hypot(new[0] - held[0], new[1] - held[1]) if held else None
        interval = 1000 * q.a.decision_speed * (1.3 - .4 * q.a.awareness)
        rec.append(dict(natural_delay=max(0, pre['nd'] - pre['now']), differs_from_held=diff, rated_interval=interval, flight=(b.last_releaser, b.release_time)))
        flights.add((b.last_releaser, b.release_time))
    return r
Match.route_receiver = route
over, ex, names = X.make_rosters(seed=seed); res, log, el = X.run(P, over, ex, names, seed=seed, short=True)
qf = lambda v, f: round(sorted(v)[int(f * (len(v) - 1))], 1) if v else None
nd = [r['natural_delay'] for r in rec]; held_diff = [r['differs_from_held'] for r in rec if r['differs_from_held'] is not None]
first = {}
for r in rec: first.setdefault(r['flight'], r)
fnd = [r['natural_delay'] for r in first.values()]
rep = dict(seed=seed, flagset=fs, score=res['score'], route_calls=len(rec), flights=len(flights),
           calls_with_pending_timer=sum(1 for d in nd if d > 0), share_pending=round(sum(1 for d in nd if d > 0) / max(1, len(nd)), 3),
           natural_delay_ms=dict(median=qf(nd, .5), p90=qf(nd, .9), max=max(nd) if nd else None),
           first_call_of_flight=dict(n=len(fnd), pending=sum(1 for d in fnd if d > 0), natural_delay_median=qf(fnd, .5), natural_delay_p90=qf(fnd, .9)),
           target_change_vs_held_m=dict(median=qf(held_diff, .5), p90=qf(held_diff, .9), share_over_1m=round(sum(1 for d in held_diff if d > 1.) / max(1, len(held_diff)), 3)),
           rated_interval_ms=dict(median=qf([r['rated_interval'] for r in rec], .5), p90=qf([r['rated_interval'] for r in rec], .9)))
json.dump(rep, open(out, 'w'), indent=1); print(json.dumps(rep))
