import math
import beastball_locomotion_v36 as z
from beastball_locomotion_v32 import rated, Settings
from cutlab_v35 import NOFAT
def stop(v0, q=None, br=None, r=1.0, role='field', cond=None, fp=None, T=8.):
    s = Settings(mode='brake', duration_s=T); sim = z.Sim(rated(r, role), s, q, cond, fp or NOFAT, 1e9, None, None, br); sim.reset(v0)
    x3 = t3 = None; xe = te = None
    for _ in range(int(T / s.dt)):
        if sim.fallen or sim._speed() < .3: break
        sim.advance(s.dt)
        if x3 is None and sim._speed() < 3: x3, t3 = sim.x, sim.t
    return dict(ok=not sim.fallen, reason=sim.reason, d3=None if x3 is None else round(x3, 1), t3=None if t3 is None else round(t3, 2),
                avg_g=None if t3 is None else round((v0 - 3) / t3 / 9.80665, 2), end_speed=round(sim._speed(), 2))
