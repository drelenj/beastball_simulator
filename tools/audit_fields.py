"""HP-002 Stage B instrument: which state FIELDS each decision function reads, and on whom (read-only; behaviour unchanged).
Wraps __getattribute__ of Player / Attributes / Ball and attributes every read to the innermost WATCHED function on the call stack (tracked with sys.setprofile).
Relation = self (the deciding actor), mate, opp, ball.  Attributes reads (p.a.X) are attributed to the owner via id(p.a).
usage: python3 tools/audit_fields.py <seed> <out.json> [full|b0]"""
import sys, os, json, time, collections
seed = int(sys.argv[1]); out = sys.argv[2]; fs = sys.argv[3] if len(sys.argv) > 3 else 'full'
if fs == 'full':
    os.environ.update(PRISM_I='1', PRISM_OFFBALL='1', PRISM_TEAMVIEW='1', PRISM_FREEVIEW='1', PRISM_JSPLIT='1', PRISM_OFFACT='1', CATCH_V2='1', PRISM_KEEPER='1', HAND_FIGHT='1')
sys.argv = ['x']; sys.path.insert(0, os.getcwd())
import pocket4_proto as X
WATCH = {'targets', 'pass_ranked', 'pass_choice', 'c4c2_decide', 'pocket_decide', 'pocket_eval', 'pocket_cont', 'pocket_pass_option', 'pocket_plan_pass', 'c4c2_eval', 'c4c2_cont', 'c4c2_targets',
         'route_receiver', 'carrier_decision', 'make_pass', 'make_shot', 'plan_pass', 'c3_contain', 'c3_region', 'c4c2_confront', 'catch_contacts', 'update_jumps', 'plan_jumps', 'fire_jumps',
         'arrow_decisions', 'c4c_position', 'c4c_plan', 'c4c2_inbound', 'c4c2_inbound_order', 'judge_target', 'fight', 'free_ball_plan', 'open_spots', 'c3_desired', 'update_keepers_jump', 'target_value'}
POS = {'x', 'y', 'vx', 'vy'}
P = X.install(X.load_pocket()); CO = P.CORE; T = CO.types
busy = [False]; stack = []; reads = collections.Counter(); owner = {}; actors = {}
def classify(obj, actor):
    c = type(obj).__name__
    if c == 'Ball': return 'ball', c
    pid = owner.get(id(obj)) if c == 'Attributes' else object.__getattribute__(obj, 'id') if c == 'Player' else None
    if pid is None: return 'other', c
    if actor is None: return 'any', c
    if pid == actor.id: return 'self', c
    pl = actors.get(pid)
    return ('mate' if pl is not None and pl.team == actor.team else 'opp'), c
def mk(cls):
    og = cls.__getattribute__
    def ga(self, name):
        v = og(self, name)
        if stack and not busy[0] and not name.startswith('__'):
            busy[0] = True
            try: fn, actor = stack[-1]; rel, c = classify(self, actor); reads[(fn, c, name, rel)] += 1
            finally: busy[0] = False
        return v
    cls.__getattribute__ = ga
def prof(frame, ev, arg):
    c = frame.f_code; n = c.co_name
    if n in WATCH:
        if ev == 'call':
            a = None
            busy[0] = True
            try:
                for k in ('p', 'd', 'q', 'c'):
                    v = frame.f_locals.get(k)
                    if v is not None and type(v).__name__ == 'Player': a = v; break
            finally: busy[0] = False
            stack.append((n + '@' + c.co_filename.split('/')[-1].replace('<embedded ', '').replace('>', ''), a))
        elif ev == 'return' and stack: stack.pop()
over, ex, names = X.make_rosters(seed=seed)
# build the owner map lazily at the first Match.step (players exist after construction)
Match = CO.match.Match; ostep = Match.step; done = [False]
def step(self):
    if not done[0]:
        for p in self.s.players.values(): owner[id(p.a)] = p.id; actors[p.id] = p
        done[0] = True; mk(T.Player); mk(T.Attributes); mk(T.Ball); sys.setprofile(prof)
    return ostep(self)
Match.step = step
t = time.time()
try: r, log, el = X.run(P, over, ex, names, seed=seed, short=True)
finally: sys.setprofile(None)
rows = [dict(func=f, cls=c, field=a, rel=rel, n=v) for (f, c, a, rel), v in sorted(reads.items())]
json.dump(dict(seed=seed, flagset=fs, score=r['score'], wall_s=round(time.time() - t, 1), rows=rows), open(out, 'w'), indent=1)
print(fs, seed, r['score'], len(rows), 'rows', round(time.time() - t, 1), 's')
