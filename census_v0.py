"""Capability census (step 1).  Real roster (Ala Lady Reds), real engine.
A: attribute table per athlete.  B: 1v1 carrier-vs-defender matrix (head-on, defender goes at the carrier, carrier runs, no pass).  C: throw speed / range per athlete.
python3 census_v0.py [seeds]"""
import sys, os, json, math, collections, statistics as st
os.environ.setdefault('RULES_V03', '1'); os.environ['PRISM_I'] = '1'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scenario_1v2_v0 as SC
N = int(sys.argv[1]) if len(sys.argv) > 1 else 3
p = SC.proc(); names = p['names']; P = p['P']
field = [k for k in names if k.startswith('A') and k[1:].isdigit() and int(k[1:]) <= 9]
lab = {k: '%s/%s' % (names[k]['position'], names[k].get('report_arch', '')) for k in names}
over = P.ROSTER_OVERRIDES
A = {}
for k in field + ['A10', 'A11']:
    o = over[k]; A[k] = dict(lab=lab[k], h=round(o['height'], 2), kg=round(o['mass']), reach=round(o['reach'], 2), vmax=round(o['maximum_speed'], 1), acc=round(o['acceleration'], 1), turn=round(o['turning'], 1),
                             str=round(o['strength']), tack=round(o['tackling']), blk=round(o['blocking']), pas=round(o['passing']), catch=round(o['catching']), jump=round(o['jump_height'], 2), aware=round(o['awareness']))
print('A. attributes'); [print(k, v) for k, v in A.items()]
res = {}
others = lambda a, b: [k for k in field if k not in (a, b)]
for i in field:
    for j in field:
        j_ = 'B' + j[1:]; rows = []
        for sd in range(N):
            a1 = next(k for k in field if k != i)
            sc = dict(vc=6., dd=15., sD=0., tx=8., ty=6., ids=(i, a1, j_, None), dec_ms=99999)
            r = SC.run(sd + 1, sc, 0.); rows.append(r)
        res['%s|%s' % (i, j_)] = dict(tackle=sum(1 for r in rows if r['ev']['tackle_count'] or r['ev']['strip']) / N, turn=sum(r['turn'] for r in rows) / N, adv=st.mean(r['adv'] for r in rows), beat=st.mean(r['beat'] for r in rows))
    print('carrier', i, lab[i], 'done', flush=True)
json.dump(dict(attrs=A, matrix=res), open('census_v0.json', 'w'))
