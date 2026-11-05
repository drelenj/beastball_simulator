"""Census part 2: throw speed/range/aim error per athlete (C), tackle variants head-on / side / from behind (D), air reach (E).  python3 census2_v0.py [seeds]"""
import sys, os, json, math, statistics as st
os.environ.setdefault('RULES_V03', '1'); os.environ['PRISM_I'] = '1'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenario_1v2_v0 as SC
N = int(sys.argv[1]) if len(sys.argv) > 1 else 6
p = SC.proc(); names = p['names']; P = p['P']; CO = p['CO']; over = P.ROSTER_OVERRIDES
field = ['A%d' % i for i in range(10)]; lab = {k: '%s/%s' % (names[k]['position'], names[k].get('report_arch', '')) for k in names}
out = dict(throw={}, air={}, tackle={})
# C/E: throw
m = CO.match.Match(P.configuration(p['st'], 1, P.CALIBRATION)); import importlib; core = importlib.import_module(CO.match.Match.__module__)
for k in field + ['A10', 'A11']:
    q = m.s.players[k]; rho, factor, extra = m.c3_release_state(q, 'pass'); sp = m.cfg['pocket']['pass_speed'] * factor
    lo, hi = 0., 150.
    for _ in range(25):
        mid = (lo + hi) / 2
        if core.launch_for((50., 50., q.hand_height), (50. + mid, 50., q.hand_height), sp, m.assume['gravity'], m.assume['ball_drag']) is not None: lo = mid
        else: hi = mid
    sh = m.c3_release_state(q, 'shot')
    out['throw'][k] = dict(lab=lab[k], pass_speed=round(sp, 1), pass_range_m=round(lo), aim_err_deg=round(extra, 2), shot_factor=round(sh[1], 2), hand_h=round(q.hand_height, 2),
                           air_reach=round(over[k]['height'] * 0 + q.hand_height + over[k]['jump_height'], 2), jump=round(over[k]['jump_height'], 2))
    print(k, out['throw'][k])
# D: tackle variants.  carrier runs; defender: head-on (dd=15,sD=0), side (dd=10,sD=8), behind (dd=-6, defender faster?)
VAR = dict(head_on=dict(dd=15., sD=0.), side=dict(dd=10., sD=8.), behind=dict(dd=-7., sD=0.))
for vn, geo in VAR.items():
    for i in field:
        for j in field:
            j_ = 'B' + j[1:]; rows = []
            for sd in range(N):
                a1 = next(k for k in field if k != i); sc = dict(vc=6., tx=8., ty=6., ids=(i, a1, j_, None), dec_ms=99999, **geo)
                rows.append(SC.run(sd + 1, sc, 0.))
            out['tackle']['%s|%s|%s' % (vn, i, j_)] = dict(tackle=sum(1 for r in rows if r['ev']['tackle_count'] or r['ev']['strip']) / N, adv=st.mean(r['adv'] for r in rows))
    print('variant', vn, 'done', flush=True)
json.dump(out, open('census2_v0.json', 'w'))
