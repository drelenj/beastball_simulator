"""HP-002 r2 instrument: does catch_v2.update_jumps depend on TRUE ball kinematics (x,y,z,vx,vy,vz)?
Poison probe: around every update_jumps call the true ball's kinematic fields are replaced by sentinel values and restored afterwards.
If decisions depend only on the player's belief, the jump count and the event/score outcome are identical to the unpoisoned run.  Also records ball_belief None-share and which jumps fire.
Poison is applied ONLY inside update_jumps (the physics before/after sees the true ball); behaviour of the rest of the match is unchanged.
usage: python3 tools/audit_update_jumps.py <seed> <out.json> <poison|plain>"""
import sys, os, json, hashlib
seed = int(sys.argv[1]); out = sys.argv[2]; mode = sys.argv[3]
os.environ.update(PRISM_I='1', PRISM_OFFBALL='1', PRISM_TEAMVIEW='1', PRISM_FREEVIEW='1', PRISM_JSPLIT='1', PRISM_OFFACT='1', CATCH_V2='1', PRISM_KEEPER='1', HAND_FIGHT='1')
sys.argv = ['x']; sys.path.insert(0, os.getcwd())
import pocket4_proto as X
P = X.install(X.load_pocket()); S = X.S; Match = P.CORE.match.Match
cap = {}; ostep = Match.step
def step(self): cap['m'] = self; return ostep(self)
Match.step = step
def find(fn, seen=None):
    seen = seen or set()
    for c in (getattr(fn, '__closure__', None) or ()):
        try: v = c.cell_contents
        except ValueError: continue
        if getattr(v, '__name__', '') == 'update_jumps': return c
        if callable(v) and id(v) not in seen:
            seen.add(id(v)); r = find(v, seen)
            if r is not None: return r
    return None
cell = find(Match.move_players); assert cell is not None, 'update_jumps closure cell not found'
orig = cell.cell_contents; calls = [0]; fired = []; K = ('x', 'y', 'z', 'vx', 'vy', 'vz')
def wrapped(self):
    b = self.s.ball; calls[0] += 1; before = self.stats.get('field_jumps', 0)
    if mode == 'poison':
        sv = {k: getattr(b, k) for k in K}
        for k in K: setattr(b, k, 1e6)
        try: orig(self)
        finally:
            for k in K: setattr(b, k, sv[k])
    else: orig(self)
    if self.stats.get('field_jumps', 0) > before: fired.append(self.s.t if hasattr(self.s, 't') else calls[0])
cell.cell_contents = wrapped
over, ex, names = X.make_rosters(seed=seed); res, log, el = X.run(P, over, ex, names, seed=seed, short=True)
m = cap['m']
h = hashlib.sha256(json.dumps([str(e) for e in log], sort_keys=True).encode()).hexdigest()[:16] if log is not None else None
rep = dict(seed=seed, mode=mode, score=res['score'], field_jumps=m.stats.get('field_jumps', 0), calls=calls[0], fire_times=fired, log_hash=h, n_log=len(log) if log is not None else None)
json.dump(rep, open(out, 'w'), indent=1); print(json.dumps(rep))
