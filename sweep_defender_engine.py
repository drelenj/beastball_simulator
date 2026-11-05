"""Defender PRISM sweep in the engine.  python3 sweep_defender_engine.py [seeds] [workers]   -> plat_def_*.json + table
Each config: env for one subprocess per seed.  Both teams get the same ratings (PRISM_FIELD_RATINGS)."""
import sys, os, json, subprocess, collections
from concurrent.futures import ThreadPoolExecutor
HERE = os.path.dirname(os.path.abspath(__file__))
SEEDS = [int(x) for x in (sys.argv[1] if len(sys.argv) > 1 else '1,2,3,4,5,6,7,8').split(',')]; W = int(sys.argv[2]) if len(sys.argv) > 2 else 4
RUN = r'''
import sys, os, json, collections
seed = int(sys.argv[1]); os.chdir(%r); sys.path.insert(0, %r)
import tend_check as T, pocket4_proto as X
P = X.install(X.load_pocket())
over, ex, names = X.make_rosters(T.G.read_csv('Ala_Lady_Reds_input.csv'), T.G.read_csv('Xenar_Dzaku_input.csv'), seed)
r, log, el = X.run(P, over, ex, names, off=(), seed=seed, short=True)
ev = collections.Counter(e['event'] for e in log); pm = getattr(X.S, 'pm', None); fs = getattr(X.S, 'fstats', {})
print('RESULT' + json.dumps(dict(goals=r['score']['A'] + r['score']['B'], ev={k: ev[k] for k in ('tackle_count', 'strip', 'possession_change')}, pm=dict(pm.stats) if pm else {}, f=dict(fs))))
''' % (HERE, HERE)
BASE = dict(vision=.5, awareness=.5, clarity=.5, reaction=.5, focus=.5, instinct=.5, anticipation=.5, judgment=.5)
D = dict(PRISM_FIELD='1', PRISM_DEF='1')
CFG = [('PRISM carrier+def, neutral', D, BASE),
       ('all .1', D, {k: .1 for k in BASE}), ('all .95', D, {k: .95 for k in BASE})]
for k in ('vision', 'awareness', 'clarity', 'reaction', 'focus'):
    for v in (.1, .95): CFG.append((f'{k}={v}', D, dict(BASE, **{k: v})))
if os.environ.get('SWEEP_SET') == 'focus':
    CFG = [('neutral', D, BASE)]
    for prm in ('slew', 'memory', 'pulse', 'tracked', 'identify'):
        for v in (.1, .95): CFG.append((f'focus={v} via {prm} only', dict(D, PRISM_FOCUS_ONLY=prm), dict(BASE, focus=v)))
    for v in (.1, .95): CFG.append((f'focus={v} (all five)', D, dict(BASE, focus=v)))
if os.environ.get('SWEEP_SET') == 'bounded':
    DB = dict(D, PRISM_BOUNDED='1', PRISM_BALLVIEW='1'); CFG = [('bounded+ball: neutral', DB, BASE)]
    for k in ('focus', 'reaction', 'clarity'):
        for v in (.1, .95): CFG.append((f'bounded+ball: {k}={v}', DB, dict(BASE, **{k: v})))
    for v in (.1, .95): CFG.append((f'bounded+ball: all={v}', DB, {k: v for k in BASE}))
if os.environ.get('SWEEP_SET') == 'ballonly':
    CFG = []
    for tag, extra in (('player+ball', {}), ('ball-only', dict(PRISM_HIDE_CARRIER='1'))):
        DB = dict(D, PRISM_BOUNDED='1', PRISM_BALLVIEW='1', **extra)
        CFG.append((f'{tag}: neutral', DB, BASE))
        for k in ('focus', 'reaction'):
            for v in (.1, .95): CFG.append((f'{tag}: {k}={v}', DB, dict(BASE, **{k: v})))
if os.environ.get('SWEEP_SET') == 'carrierbelief':
    DB = dict(D, PRISM_BOUNDED='1', PRISM_BALLVIEW='1', PRISM_CARRIER_BELIEF='1'); CFG = [('cbelief: neutral', DB, BASE)]
    for k in ('focus', 'reaction', 'vision', 'awareness', 'clarity'):
        for v in (.1, .95): CFG.append((f'cbelief: {k}={v}', DB, dict(BASE, **{k: v})))
    for v in (.1, .95): CFG.append((f'cbelief: all={v}', DB, {k: v for k in BASE}))
if os.environ.get('SWEEP_SET') == 'judge3':
    DB = dict(D, PRISM_BOUNDED='1'); DJ = dict(DB, PRISM_JUDGE_DEF='1')
    CFG = [('no judgment (aim at carrier)', DB, BASE)]
    for v in (0, .1, .3, .5, .7, .95): CFG.append((f'judgment={v}', DJ, dict(BASE, judgment=v)))
    for v in (.1, .95): CFG.append((f'judgment={v}, reaction=.95', DJ, dict(BASE, judgment=v, reaction=.95)))
    for v in (.1, .95): CFG.append((f'judgment={v}, reaction=.1', DJ, dict(BASE, judgment=v, reaction=.1)))
if os.environ.get('SWEEP_SET') == 'install':
    CFG = [('layer off', {}, None), ('PRISM_I (per-athlete ratings)', dict(PRISM_I='1'), None)]
if os.environ.get('SWEEP_SET') == 'install2':
    CFG = [('PRISM_I no maneuvers', dict(PRISM_I='1', PRISM_MANEUVERS='0'), None), ('PRISM_I no defender layer', dict(PRISM_I='1', PRISM_DEF='0'), None), ('maneuvers only', dict(PRISM_MANEUVERS='1'), None)]
if os.environ.get('SWEEP_SET') == 'center':
    CFG = [('center .5 (default)', dict(PRISM_I='1'), None), ('center .6', dict(PRISM_I='1', PRISM_RATING_CENTER='.6'), None), ('center .7', dict(PRISM_I='1', PRISM_RATING_CENTER='.7'), None)]
if os.environ.get('SWEEP_SET') == 'probe':
    DB = dict(D, PRISM_BOUNDED='1', PRISM_JUDGE_DEF='1', PRISM_JD_PROBE='1')
    CFG = [('probe reaction=.5', DB, BASE), ('probe reaction=.95', DB, dict(BASE, reaction=.95))]
if os.environ.get('SWEEP_SET') == 'judge':
    DB = dict(D, PRISM_BOUNDED='1'); DJ = dict(DB, PRISM_JUDGE_DEF='1')
    CFG = [('no judgment (aim at carrier)', DB, BASE)]
    for v in (.1, .5, .95): CFG.append((f'judgment={v}', DJ, dict(BASE, judgment=v)))
    for v in (.1, .95): CFG.append((f'judgment={v}, reaction=.95', DJ, dict(BASE, judgment=v, reaction=.95)))
    for v in (.1, .95): CFG.append((f'judgment={v}, reaction=.1', DJ, dict(BASE, judgment=v, reaction=.1)))
def one(a):
    name, env, rt, sd = a; e = dict(os.environ, **env)
    if rt is not None: e['PRISM_FIELD_RATINGS'] = json.dumps(rt)
    o = subprocess.run([sys.executable, '-c', RUN, str(sd)], env=e, capture_output=True, text=True, timeout=1800)
    l = [x for x in o.stdout.splitlines() if x.startswith('RESULT')]
    return name, (json.loads(l[0][6:]) if l else {'err': o.stderr[-300:]})
jobs = [(n, e, r, sd) for n, e, r in CFG for sd in SEEDS]
agg = collections.defaultdict(collections.Counter)
with ThreadPoolExecutor(W) as ex:
    for name, d in ex.map(one, jobs):
        if 'err' in d: print('ERR', name, d['err']); continue
        c = agg[name]; c['games'] += 1; c['goals'] += d['goals']
        for k, v in d['ev'].items(): c[k] += v
        for k, v in d['f'].items(): c['f_' + k] += v
        for k, v in d['pm'].items():
            if k.startswith(('start_', 'out_', 'tackle_vs_', 'evaded_', 'tell_read', 'strip_')): c['pm_' + k] += v
json.dump({k: dict(v) for k, v in agg.items()}, open(os.path.join(HERE, os.environ.get('SWEEP_OUT', 'plat_def_regret.json')), 'w'))
print('%-38s %5s %5s %5s %5s | %6s %7s %7s | %6s | %7s %6s %6s %7s %7s' % ('config', 'goals', 'tkl', 'strip', 'poss', 'unseen', 'tgt_err', 'tellrd', 'clear%', 'reg_n', 'reg_m', 'reg>.25', 'reg>2m', 'miss_v'))
for name, _, _ in CFG:
    c = agg.get(name)
    if not c: continue
    n = max(1, c['f_def_views']); clr = sum(v for k, v in c.items() if k.startswith('pm_out_clear_')); tk = sum(v for k, v in c.items() if k.startswith('pm_out_tackled_'))
    rn = max(1, c['f_dreg_n'])
    print('%-38s %5d %5d %5d %5d | %5.0f%% %6.2fm %6.2f | %5.0f%% | %7d %5.2fm %5.0f%% %5.0f%% %6.2fm' % (name, c['goals'], c['tackle_count'], c['strip'], c['possession_change'],
          100 * c['f_def_unseen'] / n, c['f_def_err_x100'] / 100 / n, c['pm_tell_read_x100'] / 100 / max(1, c['pm_tell_read_n']), 100 * clr / max(1, clr + tk),
          c['f_dreg_n'], c['f_dreg_sum_x100'] / 100 / rn, 100 * c['f_dreg_pos'] / rn, 100 * c['f_dreg_big'] / rn, c['f_dreg_miss_view_x100'] / 100 / rn))

if os.environ.get('SWEEP_SET') == 'probe':
    for name, _, _ in CFG:
        c = agg.get(name); n = max(1, c['f_pj_n']); print(name, 'decisions', c['f_pj_n'], '| aim-at-carrier miss %.2f m | best option in menu (oracle) %.2f m' % (c['f_pj_base_x100'] / 100 / n, c['f_pj_menu_oracle_x100'] / 100 / n))
        for J in (0, 10, 30, 50, 70, 95, 100): print('   J=%.2f  miss %.2f m  far-ahead pick %2.0f%%' % (J / 100, c['f_pj_J%d_x100' % J] / 100 / n, 100 * c['f_pj_Jfar%d' % J] / n))
