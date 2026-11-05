"""Capability table for Pocket: what an athlete can do, by rating x condition, from the frozen-candidate locomotion model (v3.7 stack, valve off, condition held)."""
import json, sys, time
from multiprocessing import Pool
import beastball_locomotion_v36 as z
import beastball_locomotion_v33 as c
from beastball_locomotion_v32 import rated, Settings
from stoplab_v36 import stop
from cutlab_v35 import cut
HOLD = c.FatigueParams(exhaust_time_s=1e9, recovery_tau_s=1e9)
MPH = .44704
def cell(a):
    r, role, reserve, region, sev = a
    mk = lambda: c.Condition(reserve=reserve, region=region, severity=sev)
    s = Settings(duration_s=16.)
    summ, samp = z.run(rated(r, role), 0., s, None, mk(), HOLD, 1e9)
    out = dict(rating=r, role=role, reserve=reserve, region=region, severity=sev,
               top_mph=round(summ['sustained_speed_m_s'] / MPH, 1) if summ['sustained_speed_m_s'] else None,
               t10=c.time_to_distance(samp, 10.), t36=c.time_to_distance(samp, 36.576), upright=summ['upright'])
    top = (summ['sustained_speed_m_s'] or 0.)
    for v in (15., 25., 35.):
        if v > top: out[f'stop{int(v)}'] = dict(ok=None, d=None, t=None, reason='above_top_speed'); continue
        st = stop(v, r=r, role=role, cond=mk(), fp=HOLD)
        out[f'stop{int(v)}'] = dict(ok=st['ok'], d=st['d3'], t=st['t3'], reason=st['reason'])
    for v in (15., 25.):
        if v > top: out[f'cut90_{int(v)}'] = dict(ok=None, t=None, vmin_pct=None, reason='above_top_speed'); continue
        ct = cut(r, v, 90., role=role, cond=mk(), fp=HOLD)
        out[f'cut90_{int(v)}'] = dict(ok=ct['ok'], t=ct['t_head'], vmin_pct=ct['vmin_pct'], reason=ct['reason'])
    return out
if __name__ == '__main__':
    cells = []
    for r in (.6, .7, .8, .9, 1.0):
        for res in (1., .75, .5, .25, 0.): cells.append((r, 'field', res, '', 0.))
    for reg in c.INJURY_REGIONS:
        for r in (.6, .8, 1.0):
            for sev in (.5, 1.): cells.append((r, 'field', 1., reg, sev))
    for r in (.6, .8, 1.0):
        for res in (1., .5, 0.): cells.append((r, 'keeper', res, '', 0.))
    t0 = time.time()
    with Pool(2) as p: rows = p.map(cell, cells)
    json.dump(rows, open('results_v37/capability_table_v37.json', 'w'), indent=1)
    print(len(rows), 'cells', round(time.time() - t0), 's')
