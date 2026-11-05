"""Wiring check: the engine's own sample_release against the lab formulas, then a full-game smoke test."""
import os, sys, math, random, statistics as st; os.environ['PRISM_I'] = '1'; sys.path.insert(0, '.')
import throwing_v1 as T
rng = random.Random(5); sph = T.SHAPES['sphere']
print('SPLIT', T.SPLIT)
print('release speed by power rating (standing, rested):', {r: round(T.v_rel_max(T.Thrower(power=T.rating_x(r))), 1) for r in (40, 70, 100)})
print('direction sigma (deg) measured in sample_release  vs  lab max(.15,3(1-x))*speed/67   [power 100, touch 100, standing]')
for ra in (40, 70, 100):
    for sp in (30., 67., 134.):
        t = T.Thrower(power=1., accuracy=T.rating_x(ra), touch=1., height=2.54); az = []
        for _ in range(3000):
            v, info = T.sample_release(t, (1., 0., 0.), sp, sph, rng); az.append(math.degrees(math.atan2(v[1], v[0])))
        lab = max(.15, 3. * (1. - T.rating_x(ra))) * info['v_rel'] / 67.
        print('  accuracy %3d speed %5.1f: measured %.3f   lab %.3f' % (ra, sp, st.pstdev(az), lab))
print('speed sigma (fraction) by touch rating   [accuracy 100, power 100]')
for rt in (40, 70, 100):
    t = T.Thrower(power=1., accuracy=1., touch=T.rating_x(rt), height=2.54); sp = []
    for _ in range(3000):
        v, info = T.sample_release(t, (1., 0., 0.), 60., sph, rng); sp.append(math.sqrt(sum(c * c for c in v)) / info['ground_speed'])
    print('  touch %3d: measured %.4f   lab %.4f' % (rt, st.pstdev(sp), max(.003, .10 * (1 - T.rating_x(rt)))))
