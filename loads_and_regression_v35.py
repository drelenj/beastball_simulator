import json, math
from dataclasses import replace
import beastball_locomotion_v35 as w, beastball_locomotion_v34 as v34, beastball_locomotion_v33 as c, beastball_locomotion_v32 as m
from beastball_locomotion_v32 import rated, Settings, G
from cutlab_v35 import NOFAT, cut
M = .44704; BW = 180 * G
OPT = {'A': replace(m.Params(), lateral_accel_m_s2=32., mu0=3.4), 'B': replace(m.Params(), lateral_accel_m_s2=41., mu0=4.3)}
out = {'loads': {}, 'regression': {}}
for k, q in OPT.items():
    for v0 in (10., 25., 40.):
        s = Settings(mode='speed', target_speed=v0, duration_s=4., turn_degrees=90., turn_time_s=1.)
        sim = w.Sim(rated(1.0), s, q, None, NOFAT, 1e9); sim.reset(v0); sim.e0 = sim._energy()
        for _ in range(int(4 / s.dt)):
            if sim.fallen: break
            sim.advance(s.dt); sim.peak_speed = max(sim.peak_speed, sim._speed())
        r = m._result(sim, sim.p, v0, s, None, None)
        out['loads'][f'{k}_{int(v0*2.237)}mph'] = dict(peak_normal_BW=round(r['peak_normal_bw'], 1), peak_horizontal_kN=round(r['peak_horizontal_force_N'] / 1e3, 1),
            peak_horizontal_BW=round(r['peak_horizontal_force_N'] / BW, 1), grf_angle_deg=r['peak_grf_angle_deg'], lean_deg=r['peak_lateral_tilt_deg'], contact_ms=round(r['contact_time_s'] * 1e3, 0),
            slip_impulse_Ns=round(r['slip_impulse_Ns'], 1), upright=r['upright'])
# regression: straight running and braking unchanged with option B vs v3.4
qB = OPT['B']
def top(mod, r):
    if mod == 'v34': return v34.rested_top_speed(rated(r)) / M
    s = Settings(duration_s=16.); sim = w.Sim(rated(r), s, qB, None, NOFAT, 1e9); return v34.run_sim(sim)['sustained_speed_m_s'] / M
def tt(mod, r, d):
    s = Settings(duration_s=6.); sim = (v34.Sim(rated(r), s, None, None, NOFAT, 1e9) if mod == 'v34' else w.Sim(rated(r), s, qB, None, NOFAT, 1e9)); sim.reset(0.)
    for _ in range(int(6 / s.dt)):
        sim.advance(s.dt)
        if sim.x >= d: return round(sim.t, 3)
def stop(mod, r, v0):
    s = Settings(mode='brake', duration_s=6.); sim = (v34.Sim(rated(r), s, None, None, NOFAT, 1e9) if mod == 'v34' else w.Sim(rated(r), s, qB, None, NOFAT, 1e9)); sim.reset(v0)
    for _ in range(int(6 / s.dt)):
        if sim.fallen or sim._speed() < 3: break
        sim.advance(s.dt)
    return round(sim.x, 2), round(sim.t, 2)
for r in (.6, .8, 1.0):
    out['regression'][f'r{r}'] = {'top_mph': {k: round(top(k, r), 2) for k in ('v34', 'v35')}, 't10': {k: tt(k, r, 10.) for k in ('v34', 'v35')}, 't36.6': {k: tt(k, r, 36.576) for k in ('v34', 'v35')},
                                  'stop_from_25': {k: stop(k, r, 25.) for k in ('v34', 'v35')}}
# other bodies and conditions (option B, 25 m/s, 90 deg)
rows = {}
rows['keeper_r.8'] = cut(.8, 25., 90., params=qB, role='keeper')
for r in (.6, .8, 1.0): rows[f'field_r{r}'] = cut(r, 25., 90., params=qB)
rows['field_r1.0_reserve0'] = cut(1.0, 25., 90., params=qB, cond=c.Condition(reserve=0.), fp=c.FatigueParams(exhaust_time_s=1e9, recovery_tau_s=1e9))
for sev in (.5, 1.0): rows[f'field_r1.0_hamstring{sev}'] = cut(1.0, 25., 90., params=qB, cond=c.Condition(region='hamstring', severity=sev), fp=c.FatigueParams(exhaust_time_s=1e9, recovery_tau_s=1e9))
rows['field_r1.0_ankle1.0'] = cut(1.0, 25., 90., params=qB, cond=c.Condition(region='ankle', severity=1.), fp=c.FatigueParams(exhaust_time_s=1e9, recovery_tau_s=1e9))
out['bodies_conditions'] = rows
json.dump(out, open('loads_and_regression_v35.json', 'w'), indent=1)
for k, d in out['loads'].items(): print('load', k, d)
for k, d in out['regression'].items(): print('reg', k, d)
for k, d in rows.items(): print('cut', k, d)
