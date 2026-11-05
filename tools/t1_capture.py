"""T1 capture: run ONE game in a fresh process with PRISM disabled (B0) and write a JSON record.
usage: python3 tools/t1_capture.py <seed> <short|reg> <outfile>
Records: effective env flags, python/numpy, score/result, event count, event-type counts, SHA-256 of the canonical event log and of the result dict (wall-clock fields removed)."""
import sys, os, json, hashlib, time, platform
seed = int(sys.argv[1]); mode = sys.argv[2]; out = sys.argv[3]
sys.argv = ['x']; sys.path.insert(0, os.getcwd())
import numpy
import pocket4_proto as X
FLAG_PREFIXES = ('PRISM', 'HAND_FIGHT', 'CATCH_V2', 'KP_', 'PLAT', 'RULESET', 'ARCH_', 'NET_R', 'KEEPER', 'FREEZE', 'QUIVER', 'KEEPER_STEP', 'ARROW', 'PASS_', 'SHOT_', 'FZ_', 'INJ_', 'LOAD_')
flags = {k: v for k, v in sorted(os.environ.items()) if k.startswith(FLAG_PREFIXES)}
P = X.install(X.load_pocket()); over, ex, names = X.make_rosters(seed=seed)
t = time.time(); r, log, el = X.run(P, over, ex, names, seed=seed, short=(mode == 'short')); wall = time.time() - t
def norm(o):
    if isinstance(o, dict): return {str(k): norm(v) for k, v in sorted(o.items(), key=lambda kv: str(kv[0]))}
    if isinstance(o, (list, tuple)): return [norm(v) for v in o]
    if isinstance(o, float): return repr(o)
    return o
def canon(o): return json.dumps(norm(o), default=str, separators=(',', ':'))   # float repr keeps full precision; keys of mixed type sorted as strings
def strip(d):
    return {k: v for k, v in d.items() if not any(w in k.lower() for w in ('wall', 'cpu'))} if isinstance(d, dict) else d
from collections import Counter
rec = dict(seed=seed, mode=mode, flags=flags, python=platform.python_version(), numpy=numpy.__version__, os=platform.platform(),
           score=r['score'], result=r['result'], n_events=len(log), event_types=dict(Counter(e.get('event') for e in log if isinstance(e, dict))),
           log_sha256=hashlib.sha256(canon(log).encode()).hexdigest(), result_sha256=hashlib.sha256(canon(strip(r)).encode()).hexdigest(),
           result_keys_dropped=[k for k in r if any(w in k.lower() for w in ('wall', 'cpu'))], wall_s=round(wall, 2))
json.dump(rec, open(out, 'w'), indent=1)
print(seed, mode, rec['score'], rec['n_events'], rec['log_sha256'][:12], rec['wall_s'], 's')
