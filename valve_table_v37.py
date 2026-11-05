import json
import beastball_locomotion_v37 as z
import beastball_locomotion_v36 as v36
from beastball_locomotion_v32 import rated, Settings
from beastball_locomotion_v33 import Condition, FatigueParams
from stoplab_v36 import NOFAT
fp = FatigueParams(); vp = z.ValveParams()
def sprint_empty_time(st, r=.7, T=60.):
    s = Settings(mode='sprint', duration_s=T); sim = z.Sim(rated(r), s, None, Condition(), None, None, None, None, None, None, st); sim.reset(0.)
    t50 = tz = None; out = {}
    for _ in range(int(T / s.dt)):
        sim.advance(s.dt)
        if t50 is None and sim.cond.reserve <= .5: t50 = sim.t
        if tz is None and sim.cond.reserve <= .001: tz = sim.t
        if sim.t >= 10 and 'res10' not in out: out['res10'] = round(sim.cond.reserve, 3); out['speed10'] = round(sim._speed(), 1)
    out.update(t_half=round(t50, 1) if t50 else None, t_empty=round(tz, 1) if tz else None, speed_end=round(sim._speed(), 1)); return out
tab = {}
for st in (.4, .55, .7, .85, 1.0):
    sens, drain, rec = z.stamina_terms(st, vp, fp)
    n = z.valve_rate(.5, drain, rec)
    tab[str(st)] = dict(sensitivity=round(sens, 3), drain_per_s=round(drain, 4), recover_per_s=round(rec, 4), full_drain_s=round(1 / drain, 1), full_recover_s=round(1 / rec, 1),
                        top_speed_intensity=round(min(1, sens), 3), net_rate_at_top_speed_per_s=round(z.valve_rate(min(1, sens), drain, rec), 4), neutral_rate=n,
                        bench_per_s=round(z.bench_rate(st), 4), bench_full_s=round(1 / z.bench_rate(st), 1), sprint=sprint_empty_time(st))
json.dump(tab, open('results_v37/valve_table_v37.json', 'w'), indent=1)
for k, v in tab.items(): print(k, v)
