import json, itertools
from dataclasses import replace
import beastball_locomotion_v35 as w, beastball_locomotion_v32 as m
from cutlab_v35 import cut
out = []
opts = {'A: lat 32 (cone 39 m/s2 = 4.0 g)': replace(m.Params(), lateral_accel_m_s2=32., mu0=3.4),
        'B: lat 41 (cone 50 m/s2 = 5.1 g)': replace(m.Params(), lateral_accel_m_s2=41., mu0=4.3),
        'C: lat 50 (cone 61 m/s2 = 6.2 g)': replace(m.Params(), lateral_accel_m_s2=50., mu0=5.3),
        'v3.4 ref: lat 16 (cone 19.5), instant flip': None}
for name, q in opts.items():
    arc = w.ArcParams(enabled=q is not None)
    for v0, ang in itertools.product((10., 15., 25., 40.), (45., 90., 150., 180.)):
        T = 7. if ang >= 150 else 5.
        r = cut(1.0, v0, ang, params=q or m.Params(), arc=arc, T=T)
        r.update(opt=name, v0=v0, ang=ang); out.append(r)
json.dump(out, open('cut_standard_options.json', 'w'), indent=1)
for name in opts:
    print(name)
    for ang in (45., 90., 150., 180.):
        row = [x for x in out if x['opt'] == name and x['ang'] == ang]
        print('  ', int(ang), 'deg:', ' | '.join(f"{int(x['v0']*2.237)}mph t={x['t_head']} keep={x['v_at_heading_pct']}%{'' if x['ok'] else ' FELL:'+x['reason']}" for x in row))
