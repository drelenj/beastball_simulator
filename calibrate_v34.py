"""Solve the speed-ability map: for each node rating find the ability a so the reference athlete's sustained top speed = target."""
import sys, time, json
import beastball_locomotion_v34 as v
from beastball_locomotion_v32 import rated, Settings, Params
MPH = v.MPH
def top_speed(r, a, T=16.):
    sm = lambda _r: a
    sim = v.Sim(rated(r), Settings(duration_s=T), Params(), v_ref=1e9, speed_map=sm)
    return v.run_sim(sim)['sustained_speed_m_s']
def solve(r, target_ms, lo=.7, hi=1.45, tol=.0004):
    flo, fhi = top_speed(r, lo) - target_ms, top_speed(r, hi) - target_ms
    assert flo < 0 < fhi, (r, flo, fhi)
    while hi - lo > tol:
        mid = .5 * (lo + hi)
        f = top_speed(r, mid) - target_ms
        if f < 0: lo = mid
        else: hi = mid
    return .5 * (lo + hi)
if __name__ == '__main__':
    nodes = [round(.6 + .05 * i, 2) for i in range(9)]
    out = []
    t0 = time.time()
    for r in nodes:
        tgt = v.BAND.target_mph(r)
        a = solve(r, tgt * MPH)
        got = top_speed(r, a) / MPH
        out.append((r, round(a, 5), round(tgt, 2), round(got, 2)))
        print(r, round(a, 5), 'target', round(tgt, 2), 'got', round(got, 2), round(time.time() - t0), 's', flush=True)
    json.dump(out, open('speed_ability_nodes.json', 'w'))
