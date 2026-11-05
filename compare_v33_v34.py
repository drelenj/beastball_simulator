import math, json
import beastball_locomotion_v34 as v, beastball_locomotion_v33 as c, beastball_locomotion_v32 as m
from beastball_locomotion_v32 import rated, Settings
NOFAT = c.FatigueParams(max_loss=1e-9, tech_max_loss=1e-10, exhaust_time_s=1e9)
def mk(mod, p, s):
    if mod == 'v33': return c.Sim(p, s, None, None, NOFAT, 1e9)
    return v.Sim(p, s, None, None, NOFAT, 1e9)
def accel(mod, r):
    s = Settings(duration_s=9.); sim = mk(mod, rated(r), s); sim.reset(0.)
    marks = {5: None, 10: None, 20: None, 36.576: None, 60: None}; t_s = {2: None, 4: None}
    n = int(9 / s.dt)
    for _ in range(n):
        sim.advance(s.dt)
        for d in marks:
            if marks[d] is None and sim.x >= d: marks[d] = round(sim.t, 2)
        for t in t_s:
            if t_s[t] is None and sim.t >= t: t_s[t] = round(sim._speed() / m.G * 0 + sim._speed() / .44704, 1)
    return marks, t_s
def brake(mod, r, v0):
    s = Settings(mode='brake', duration_s=8.); sim = mk(mod, rated(r), s); sim.reset(v0)
    for _ in range(int(8 / s.dt)):
        if sim.fallen or sim._speed() < .3: break
        sim.advance(s.dt)
    return round(sim.x, 2), round(sim.t, 2), not sim.fallen
def cut(mod, r, v0, ang):
    s = Settings(mode='speed', target_speed=v0, duration_s=4., turn_degrees=ang, turn_time_s=1.); sim = mk(mod, rated(r), s); sim.reset(v0)
    vmin = 99; th = None; tt = None
    for _ in range(int(4 / s.dt)):
        if sim.fallen: break
        sim.advance(s.dt)
        if sim.t >= 1.:
            if tt is None: tt = sim.t
            vmin = min(vmin, sim._speed())
            err = abs((math.degrees(math.atan2(sim.vy, sim.vx)) - ang + 180) % 360 - 180)
            if th is None and err <= 5 and sim._speed() > .5: th = round(sim.t - tt, 2)
    return round(vmin, 2), th, not sim.fallen
out = {}
for r in (.6, .7, .8, 1.0):
    out[f'accel_r{r}'] = {mod: accel(mod, r) for mod in ('v33', 'v34')}
    out[f'brake20_r{r}'] = {mod: brake(mod, r, 20.) for mod in ('v33', 'v34')}
    out[f'cut90_10ms_r{r}'] = {mod: cut(mod, r, 10., 90.) for mod in ('v33', 'v34')}
    out[f'cut60_20ms_r{r}'] = {mod: cut(mod, r, 20., 60.) for mod in ('v33', 'v34')}
json.dump(out, open('compare_v33_v34.json', 'w'), indent=1)
for k, d in out.items(): print(k, '| v33', d['v33'], '| v34', d['v34'])
