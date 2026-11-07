"""HP-002 r3: instrumentation neutrality test (req 4).  Shows that decision-ID recording, tracing (sys.setprofile) and ownership sentinels
(outermost pass-through wrappers) do NOT change: score, event/log hash, random-stream consumption (end state of every match RNG stream, module RNGs, global random),
match stats, or the historical wrapper chains once removed; and that while installed they sit OUTSIDE the unmodified historical function (identity check).
usage: python3 tools/audit_neutrality.py <seed> <out.json> <b0|full> <plain|instr>"""
import sys, os, json, hashlib, gc, random
seed = int(sys.argv[1]); out = sys.argv[2]; fs = sys.argv[3]; mode = sys.argv[4]
if fs == 'full':
    os.environ.update(PRISM_I='1', PRISM_OFFBALL='1', PRISM_TEAMVIEW='1', PRISM_FREEVIEW='1', PRISM_JSPLIT='1', PRISM_OFFACT='1', CATCH_V2='1', PRISM_KEEPER='1', HAND_FIGHT='1')
sys.argv = ['x']; sys.path.insert(0, os.getcwd())
import pocket4_proto as X
P = X.install(X.load_pocket()); CO = P.CORE; Match = CO.match.Match; Policy = CO.policies.Policy
H = lambda o: hashlib.sha256(repr(o).encode()).hexdigest()[:16]
TARGETS = [(Match, n) for n in ('step', 'carrier_decision', 'route_receiver', 'c4c2_targets', 'move_players', 'arrow_decisions')] + [(Policy, 'targets')]
def chain(fn, seen=None, depth=0):
    seen = seen if seen is not None else set(); res = []
    if fn is None or id(fn) in seen or depth > 40: return res
    seen.add(id(fn)); code = getattr(fn, '__code__', None)
    res.append((getattr(fn, '__qualname__', '?'), code.co_filename.split('/')[-1] if code else '?', code.co_firstlineno if code else 0))
    for c in (getattr(fn, '__closure__', None) or ()):
        try: v = c.cell_contents
        except ValueError: continue
        if callable(v): res += chain(v, seen, depth + 1)
    return res
def chain_digest(): return H([(cls.__name__, n, chain(getattr(cls, n, None))) for cls, n in TARGETS])
before = chain_digest(); orig = {(cls, n): getattr(cls, n) for cls, n in TARGETS if hasattr(cls, n)}
ids = [0]; marks = []; calls = [0]
installed_outer_is_wrapper = {}
if mode == 'instr':
    for (cls, n), f in orig.items():
        def mk(f, n):
            def w(*a, **k):
                ids[0] += 1; marks.append((n, ids[0]))            # decision ID / ownership sentinel: counter only, no RNG, no scheduling, no state write
                return f(*a, **k)
            w.__wrapped__ = f; w.__name__ = n; return w
        setattr(cls, n, mk(f, n)); installed_outer_is_wrapper[f'{cls.__name__}.{n}'] = getattr(cls, n).__wrapped__ is f
    def prof(frame, ev, arg):
        if ev == 'call': calls[0] += 1
    sys.setprofile(prof)
g0 = H(random.getstate())
over, ex, names = X.make_rosters(seed=seed)
try: res, log, el = X.run(P, over, ex, names, seed=seed, short=True)
finally: sys.setprofile(None)
ms = [o for o in gc.get_objects() if type(o) is Match]; m = ms[-1] if ms else None
streams = {k: H(v.getstate()) for k, v in sorted((m.rng if m is not None and hasattr(m, 'rng') else {}).items(), key=lambda kv: str(kv[0]))}
extra = {}
for nm in ('arng',):
    v = getattr(X.S, nm, None)
    if v is not None and hasattr(v, 'getstate'): extra['S.' + nm] = H(v.getstate())
extra['global_random_consumed'] = (H(random.getstate()) != g0)
if mode == 'instr':
    for (cls, n), f in orig.items(): setattr(cls, n, f)
after = chain_digest()
rep = dict(seed=seed, flagset=fs, mode=mode, score=res['score'], n_log=len(log), log_hash=H([str(e) for e in log]), rng_streams=streams, rng_extra=extra,
           stats_hash=H(sorted((str(k), str(v)) for k, v in (m.stats.items() if m is not None else []))), chain_before=before, chain_after_removal=after,
           chain_restored=(before == after), wrappers_outside_unmodified=installed_outer_is_wrapper, sentinel_marks=len(marks), profile_calls=calls[0])
json.dump(rep, open(out, 'w'), indent=1); print(json.dumps({k: v for k, v in rep.items() if k not in ('rng_streams',)}))
