"""HP-002 audit instrument (read-only; behaviour unchanged).  Runs one short full-PRISM game under sys.setprofile and records, for every decision/execution
function of interest, how often it ran INSIDE a PRISM belief view (a live prism_field_v0.with_view frame) and how often OUTSIDE.
usage: python3 tools/audit_trace.py <seed> <out.json> [flagset]     flagset: full (default) | b0"""
import sys, os, json, time, collections
seed = int(sys.argv[1]); out = sys.argv[2]; fs = sys.argv[3] if len(sys.argv) > 3 else 'full'
if fs == 'full':
    os.environ.update(PRISM_I='1', PRISM_OFFBALL='1', PRISM_TEAMVIEW='1', PRISM_FREEVIEW='1', PRISM_JSPLIT='1', PRISM_OFFACT='1', CATCH_V2='1', PRISM_KEEPER='1', HAND_FIGHT='1')
sys.argv = ['x']; sys.path.insert(0, os.getcwd())
import pocket4_proto as X
WATCH = {'targets', 'pass_ranked', 'pass_choice', 'pocket_decide', 'pocket_eval', 'pocket_cont', 'pocket_pass_option', 'pocket_plan_pass', 'c4c2_decide', 'c4c2_eval', 'c4c2_cont',
         'c4c2_targets', 'route_receiver', 'carrier_decision', 'make_pass', 'make_shot', 'plan_pass', 'c3_contain', 'c3_region', 'c3_desired', 'move_players', 'catch_contacts',
         'update_keepers_jump', 'arrow_decisions', 'auto_substitutions', 'c4c_plan', 'c4c_position', 'c4c2_confront', 'c4c2_inbound', 'c3_contact_kick', 'strike', 'tackle', 'engage',
         'judge_target', 'judge_opts', 'duel_flip', 'fight', 'band_foul', 'decide_off', 'free_ball_plan', 'open_spots', 'noisy_rank', 'keeper_decide', 'keeper_targets', 'jump_decision'}
depth = [0]; cnt = collections.Counter(); first = {}
def prof(frame, ev, arg):
    c = frame.f_code; n = c.co_name
    if n == 'with_view' and c.co_filename.endswith('prism_field_v0.py'):
        if ev == 'call': depth[0] += 1
        elif ev == 'return': depth[0] -= 1
        return
    if ev == 'call' and n in WATCH:
        f = c.co_filename.split('/')[-1]; k = (f, n, 'IN' if depth[0] > 0 else 'OUT'); cnt[k] += 1; first.setdefault(k, c.co_firstlineno)
P = X.install(X.load_pocket()); over, ex, names = X.make_rosters(seed=seed)
t = time.time(); sys.setprofile(prof)
try: r, log, el = X.run(P, over, ex, names, seed=seed, short=True)
finally: sys.setprofile(None)
rows = [dict(file=f, func=n, where=w, calls=v, line=first[(f, n, w)]) for (f, n, w), v in sorted(cnt.items())]
json.dump(dict(seed=seed, flagset=fs, score=r['score'], wall_s=round(time.time() - t, 1), rows=rows), open(out, 'w'), indent=1)
print(seed, fs, r['score'], len(rows), 'rows', round(time.time() - t, 1), 's')
