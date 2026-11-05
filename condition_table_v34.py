import json
import beastball_locomotion_v34 as v, beastball_locomotion_v33 as c
from beastball_locomotion_v32 import rated, Settings
M = v.MPH
FP_HOLD = c.FatigueParams(exhaust_time_s=1e9, recovery_tau_s=1e9)      # reserve stays where it is set
def top(r, cond, fp=FP_HOLD, T=14.):
    summ, _ = v.run(rated(r), 0., Settings(duration_s=T), None, cond, fp, 1e9)
    return round(summ['sustained_speed_m_s'] / M, 1)
out = {'fixed_reserve_mph': {}, 'injury_mph': {}, 'sprint_fade_mph': {}}
for r in (1.0, .8, .6):
    out['fixed_reserve_mph'][r] = {R: top(r, c.Condition(reserve=R)) for R in (1., .75, .5, .25, 0.)}
for reg in ('hamstring', 'groin', 'knee', 'ankle', 'general'):
    out['injury_mph'][reg] = {sev: top(1.0, c.Condition(region=reg, severity=sev)) for sev in (0., .25, .5, .75, 1.)}
# full-effort fade from a standing start, default fatigue params, v_ref = rested v3.4 top speed
for r in (1.0, .8):
    summ, smp = v.run(rated(r), 0., Settings(duration_s=20.), None, None, None, None, 1.)
    out['sprint_fade_mph'][r] = {int(s['t']): round(s['speed'] / M, 1) for s in smp if abs(s['t'] - round(s['t'])) < 1e-6 and s['t'] in (2., 4., 6., 8., 10., 12., 15., 20.)}
json.dump(out, open('condition_table_v34.json', 'w'), indent=1)
for k, d in out.items(): print(k, d)
