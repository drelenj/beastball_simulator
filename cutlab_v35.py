"""Cut metrics: heading change at a given speed - time to within 5 degrees, speed at that moment, lowest speed, footprint, upright, lean."""
import math
import beastball_locomotion_v35 as w, beastball_locomotion_v33 as c
from beastball_locomotion_v32 import rated, Settings
NOFAT = c.FatigueParams(max_loss=1e-9, tech_max_loss=1e-10, exhaust_time_s=1e9)
M = .44704
def cut(r, v0, ang, params=None, arc=None, T=5., role='field', cond=None, fp=None, tdeg=5.):
    s = Settings(mode='speed', target_speed=v0, duration_s=T, turn_degrees=ang, turn_time_s=1.)
    sim = w.Sim(rated(r, role), s, params, cond, fp or NOFAT, 1e9, None, arc); sim.reset(v0)
    vmin = 1e9; th = None; t0 = x0 = y0 = None; v_at = dist = None
    for _ in range(int(T / s.dt)):
        if sim.fallen: break
        sim.advance(s.dt)
        if sim.t >= 1.:
            if t0 is None: t0, x0, y0 = sim.t, sim.x, sim.y
            vmin = min(vmin, sim._speed())
            err = abs((math.degrees(math.atan2(sim.vy, sim.vx)) - ang + 180) % 360 - 180)
            if th is None and err <= tdeg and sim._speed() > .5:
                th = sim.t - t0; v_at = sim._speed(); dist = math.hypot(sim.x - x0, sim.y - y0)
    res = dict(ok=not sim.fallen, reason=sim.reason, t_head=None if th is None else round(th, 2), vmin_pct=None if vmin > 1e8 else round(100 * vmin / v0),
               v_at_heading_pct=None if v_at is None else round(100 * v_at / v0), footprint_m=None if dist is None else round(dist, 1),
               peak_lean_deg=round(math.degrees(math.atan(sim.peak_lat_tilt)), 1))
    return res
if __name__ == '__main__':
    for arc in (w.ArcParams(enabled=False), w.ArcParams()):
        print('ARC', arc.enabled)
        for v0 in (10., 25., 40.):
            for ang in (45., 90.):
                print(' v0', v0, 'ang', ang, cut(1.0, v0, ang, arc=arc))
