"""What the v3.4 reference athlete (2.54 m, 180 kg) must be able to do - measured in the simulator, then simple derived consequences."""
import json, math
import beastball_locomotion_v34 as v, beastball_locomotion_v33 as c, beastball_locomotion_v32 as m
from beastball_locomotion_v32 import rated, Settings, G
NOFAT = c.FatigueParams(max_loss=1e-9, tech_max_loss=1e-10, exhaust_time_s=1e9)
BW = 180. * G
def sim_for(r, s):
    sim = v.Sim(rated(r), s, None, None, NOFAT, 1e9); return sim
def metrics(sim, speed, s):
    sim.reset(speed); sim.e0 = sim._energy()
    for _ in range(int(s.duration_s / s.dt)):
        if sim.fallen: break
        sim.advance(s.dt); sim.peak_speed = max(sim.peak_speed, sim._speed())
    return m._result(sim, sim.p, speed, s, None, None)
KEYS = ['sustained_speed_m_s', 'step_frequency_hz', 'step_length_m', 'contact_time_s', 'flight_time_s', 'duty_factor', 'peak_normal_bw',
        'peak_horizontal_force_N', 'peak_grf_angle_deg', 'peak_lateral_tilt_deg', 'peak_leg_compression_m', 'foot_peak_ground_speed_m_s']
out = {}
for r in (1.0, .6):
    s0 = Settings(duration_s=16.); vtop = metrics(sim_for(r, s0), 0., s0)['sustained_speed_m_s']
    s = Settings(mode='speed', target_speed=vtop, duration_s=5.)
    res = metrics(sim_for(r, s), vtop, s)
    out[f'topspeed_r{r}'] = {k: res.get(k) for k in KEYS}
    out[f'topspeed_r{r}']['drag_N'] = .5 * 1.2 * sim_for(r, s).d['drag_area_m2'] * res['sustained_speed_m_s'] ** 2
    out[f'topspeed_r{r}']['drag_kW'] = out[f'topspeed_r{r}']['drag_N'] * res['sustained_speed_m_s'] / 1e3
for r in (1.0, .6):
    for v0 in (15., 25., 35.):
        if r == .6 and v0 > 30: continue
        s = Settings(mode='brake', duration_s=6.); sim = sim_for(r, s); sim.reset(v0); sim.e0 = sim._energy()
        xs = ts = None
        for _ in range(int(6 / s.dt)):
            if sim.fallen: break
            sim.advance(s.dt)
            if sim._speed() < 3 and xs is None: xs, ts = sim.x, sim.t
            if sim._speed() < 3: break
        res = m._result(sim, sim.p, v0, s, None, None)
        out[f'hardstop_r{r}_from{v0:g}'] = dict(to_3ms_dist_m=round(xs, 2) if xs else None, to_3ms_time_s=round(ts, 2) if ts else None,
            avg_decel_m_s2=round((v0 - 3) / ts, 1) if ts else None, **{k: res.get(k) for k in ('peak_normal_bw', 'peak_horizontal_force_N', 'peak_grf_angle_deg', 'contact_time_s')})
for r in (1.0,):
    for v0 in (10., 20., 30.):
        s = Settings(mode='speed', target_speed=v0, duration_s=4., turn_degrees=90., turn_time_s=1.); sim = sim_for(r, s); sim.reset(v0); sim.e0 = sim._energy()
        vmin = 99.; th = None; tt = None
        for _ in range(int(4 / s.dt)):
            if sim.fallen: break
            sim.advance(s.dt)
            if sim.t >= 1.:
                tt = sim.t if tt is None else tt; vmin = min(vmin, sim._speed())
                err = abs((math.degrees(math.atan2(sim.vy, sim.vx)) - 90. + 180) % 360 - 180)
                if th is None and err <= 5 and sim._speed() > .5: th = round(sim.t - tt, 2)
        res = m._result(sim, sim.p, v0, s, None, None)
        out[f'cut90_r{r}_at{v0:g}'] = dict(min_speed_m_s=round(vmin, 2), speed_kept_pct=round(100 * vmin / v0, 0), time_to_heading_s=th, upright=not sim.fallen,
            **{k: res.get(k) for k in ('peak_normal_bw', 'peak_horizontal_force_N', 'peak_grf_angle_deg', 'peak_lateral_tilt_deg')})
# power during a sprint start
for r in (1.0, .6):
    s = Settings(duration_s=8.); sim = sim_for(r, s); sim.reset(0.)
    Pmax = 0.; Ptop = 0.; vprev = 0.; Pmax_v = 0.
    A = sim.d['drag_area_m2']; M = sim.m
    for i in range(int(8 / s.dt)):
        sim.advance(s.dt); vv = sim._speed(); a = (vv - vprev) / s.dt; vprev = vv
        if i % 4 == 3:
            pass
    # use sampled trace instead: coarse (50 ms)
    summ, smp = v.run(rated(r), 0., Settings(duration_s=8.), None, None, NOFAT, 1e9, .05)
    P = []
    for a_, b_ in zip(smp, smp[1:]):
        vm = .5 * (a_['speed'] + b_['speed']); dv = (b_['speed'] - a_['speed']) / .05
        P.append((a_['t'], (M * vm * dv + .5 * 1.2 * A * vm ** 3) / 1e3))
    # smooth with 0.25 s window
    ps = [sum(p for _, p in P[i:i + 5]) / 5 for i in range(len(P) - 4)]
    out[f'power_r{r}'] = dict(peak_mech_kW_250ms=round(max(ps), 1), peak_W_per_kg=round(max(ps) * 1e3 / M, 0), at_top_speed_kW=round(P[-1][1], 1))
json.dump(out, open('body_requirements_v34.json', 'w'), indent=1)
for k, d in out.items(): print(k, {kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in d.items()})
