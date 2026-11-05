import beastball_locomotion_v37 as z
from beastball_locomotion_v32 import rated, Settings
from beastball_locomotion_v33 import Condition, FatigueParams
import json
def trace(r=.7, stamina=.7, mode='sprint', v0=0., T=30., target=None, cond=None, vp=None, every=2.5, **kw):
    s = Settings(mode=mode, duration_s=T, **({'target_speed': target} if target else {}))
    sim = z.Sim(rated(r), s, None, cond or Condition(), None, None, None, None, None, vp, stamina); sim.reset(v0)
    out, nxt = [], 0.
    for _ in range(int(T / s.dt)):
        if sim.fallen: break
        sim.advance(s.dt)
        if sim.t >= nxt: out.append((round(sim.t, 1), round(sim._speed(), 1), round(sim.intensity, 2), round(sim.cond.reserve, 3))); nxt += every
    return out
if __name__ == '__main__':
    for st in (.4, .7, 1.0):
        print('sprint hold stamina', st); print(trace(stamina=st, T=40., every=5.))
    print('hold 50% of top speed'); print(trace(mode='speed', target=22., v0=22., T=30., every=5.))
    print('standing'); print(trace(mode='speed', target=0., v0=0., T=10., cond=Condition(reserve=.3), every=2.5))
