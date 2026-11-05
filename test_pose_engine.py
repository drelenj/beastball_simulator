"""Tests for the engine port of poses/maneuvers (pose_engine_v0.py).  Run: python3 test_pose_engine.py
Each game runs in a subprocess so the PRISM_MANEUVERS flag is read at install time, as in real use."""
import os, sys, json, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
RUN = r'''
import sys, os, json, collections
seed = int(sys.argv[1])
os.chdir(%r); sys.path.insert(0, %r)
import tend_check as T, pocket4_proto as X
P = X.install(X.load_pocket())
over, ex, names = X.make_rosters(T.G.read_csv('Ala_Lady_Reds_input.csv'), T.G.read_csv('Xenar_Dzaku_input.csv'), seed)
r, log, el = X.run(P, over, ex, names, off=(), seed=seed, short=True)
ev = collections.Counter(e['event'] for e in log); pm = getattr(X.S, 'pm', None)
print('RESULT' + json.dumps(dict(score=r['score'], ev={k: ev[k] for k in ('tackle_count', 'strip', 'possession_change', 'goal')}, pm=dict(pm.stats) if pm else None)))
''' % (HERE, HERE)

def game(seed, flag):
    env = dict(os.environ, PRISM_MANEUVERS=flag)
    out = subprocess.run([sys.executable, '-c', RUN, str(seed)], env=env, capture_output=True, text=True, timeout=600)
    line = [l for l in out.stdout.splitlines() if l.startswith('RESULT')]
    assert line, out.stderr[-800:]
    return json.loads(line[0][6:])

def ok(c, m):
    print(('PASS ' if c else 'FAIL ') + m); assert c, m

if __name__ == '__main__':
    import pose_maneuvers_v0 as PM
    # 1. flag off: pose layer absent, repeated runs identical (deterministic), no pm state
    a, b = game(1, '0'), game(1, '0')
    ok(a == b and a['pm'] is None, 'flag off: no pose state, two runs identical')
    # 2. flag on: deterministic, state present, maneuvers actually start
    c, d = game(1, '1'), game(1, '1')
    ok(c == d, 'flag on: two runs identical')
    st = c['pm']; started = sum(v for k, v in st.items() if k.startswith('start_'))
    ok(started > 0 and sum(v for k, v in st.items() if k.startswith('pose_')) > 0, 'flag on: poses tracked and maneuvers start (%d)' % started)
    # 3. only legal poses at start: FSM rules are the spec's
    ok(set(PM.ALLOWED['stiffarm']) == {'exposed', 'tucked'} and 'braced' not in PM.ALLOWED['stiffarm'], 'stiff-arm never from Braced (spec)')
    # 4. strip acceptance never raises the engine's own scheduled rate
    ok(st.get('strip_ok_tucked', 0) + st.get('strip_blocked_tucked', 0) <= st.get('strip_sched_tucked', 0) + 0, 'strip hook only filters')
    print('ALL PASS')
