import json, math
import beastball_locomotion_v36 as z, beastball_locomotion_v35 as v35, beastball_locomotion_v34 as v34, beastball_locomotion_v33 as c, beastball_locomotion_v32 as m
from beastball_locomotion_v32 import rated, Settings, G
from stoplab_v36 import stop, NOFAT
from cutlab_v35 import cut
M = .44704; BW = 180 * G
HOLD = c.FatigueParams(exhaust_time_s=1e9, recovery_tau_s=1e9)
out = {'stops': {}, 'conditions': {}, 'loads': {}, 'regression': {}}
for r in (.6, 1.0):
    for v0 in (10., 15., 25., 35., 44.7):
        out['stops'][f'r{r}_{int(round(v0*2.237))}mph'] = stop(v0, r=r)
out['stops']['keeper_r.8_55mph'] = stop(25., r=.8, role='keeper')
for name, cond in {'reserve0': c.Condition(reserve=0.), 'hamstring.5': c.Condition(region='hamstring', severity=.5), 'hamstring1.0': c.Condition(region='hamstring', severity=1.), 'ankle1.0': c.Condition(region='ankle', severity=1.)}.items():
    out['conditions'][name] = stop(25., cond=cond, fp=HOLD)
for v0 in (15., 25., 44.7):
    s = Settings(mode='brake', duration_s=8.); sim = z.Sim(rated(1.0), s, None, None, NOFAT, 1e9); sim.reset(v0); sim.e0 = sim._energy()
    for _ in range(int(8 / s.dt)):
        if sim.fallen or sim._speed() < .3: break
        sim.advance(s.dt); sim.peak_speed = max(sim.peak_speed, sim._speed())
    r = m._result(sim, sim.p, v0, s, None, None)
    out['loads'][f'{int(round(v0*2.237))}mph'] = dict(peak_normal_BW=round(r['peak_normal_bw'], 1), peak_horizontal_kN=round(r['peak_horizontal_force_N'] / 1e3, 1), peak_horizontal_BW=round(r['peak_horizontal_force_N'] / BW, 1), grf_angle_deg=r['peak_grf_angle_deg'])
# regression vs v3.5
def top(mod, r):
    s = Settings(duration_s=16.); sim = (v35.Sim if mod == 'v35' else z.Sim)(rated(r), s, None, None, NOFAT, 1e9); return v34.run_sim(sim)['sustained_speed_m_s'] / M
def tt(mod, r, d):
    s = Settings(duration_s=6.); sim = (v35.Sim if mod == 'v35' else z.Sim)(rated(r), s, None, None, NOFAT, 1e9); sim.reset(0.)
    for _ in range(int(6 / s.dt)):
        sim.advance(s.dt)
        if sim.x >= d: return round(sim.t, 3)
for r in (.6, 1.0):
    out['regression'][f'r{r}'] = dict(top_mph={k: round(top(k, r), 2) for k in ('v35', 'v36')}, t10={k: tt(k, r, 10.) for k in ('v35', 'v36')}, t36={k: tt(k, r, 36.576) for k in ('v35', 'v36')})
def cut36(v0, ang):
    s = Settings(mode='speed', target_speed=v0, duration_s=7., turn_degrees=ang, turn_time_s=1.)
    res = {}
    for k, S in (('v35', v35.Sim), ('v36', z.Sim)):
        sim = S(rated(1.0), s, None, None, NOFAT, 1e9); sim.reset(v0); th = None; t0 = None
        for _ in range(int(7 / s.dt)):
            if sim.fallen: break
            sim.advance(s.dt)
            if sim.t >= 1.:
                t0 = sim.t if t0 is None else t0
                if th is None and abs((math.degrees(math.atan2(sim.vy, sim.vx)) - ang + 180) % 360 - 180) <= 5: th = round(sim.t - t0, 2)
        res[k] = (th, not sim.fallen)
    return res
for v0, ang in ((25., 90.), (40., 90.), (25., 180.)):
    out['regression'][f'cut{int(ang)}_{int(round(v0*2.237))}mph'] = cut36(v0, ang)
json.dump(out, open('stops_and_regression_v36.json', 'w'), indent=1)
for k, d in out.items():
    print(k)
    for kk, vv in d.items(): print('  ', kk, vv)
