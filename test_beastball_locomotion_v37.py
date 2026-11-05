"""Tests for Beastball v3.7 (float control valve).  Run: python -m unittest -q test_beastball_locomotion_v37"""
import hashlib, unittest
from pathlib import Path
import beastball_locomotion_v36 as v36
import beastball_locomotion_v37 as z
from beastball_locomotion_v32 import Settings, rated
from beastball_locomotion_v33 import Condition, FatigueParams
ROOT = Path(__file__).resolve().parent
SHA = {'beastball_locomotion_v32.py': 'a8785d1d2edae8cf3a212d582dee7c8d082d37141269efc679755403309583a6',
       'beastball_locomotion_v33.py': 'd92ed6adc1e82c55e1d4c00cb6528aed6c26b73f99b8b7322351bf42f9d405d5',
       'beastball_locomotion_v34.py': 'ecd013e615f6edcc5afdca203a793ac422f8763293bb37aed278ad7f3e282ebf',
       'beastball_locomotion_v36.py': '6184cda74c905247aaa2c253188724ea725af4331be53285d80316047fef4b11'}
fp, vp = FatigueParams(), z.ValveParams()


def sim(st=.7, mode='sprint', v0=0., T=20., target=None, cond=None, r=.7, valve=None):
    s = Settings(mode=mode, duration_s=T, **({'target_speed': target} if target else {}))
    x = z.Sim(rated(r), s, None, cond or Condition(), None, None, None, None, None, valve, st); x.reset(v0); return x, s


def run_until(x, s, T):
    for _ in range(int(T / s.dt)):
        if x.fallen: break
        x.advance(s.dt)
    return x


class Valve(unittest.TestCase):
    def test_bases_untouched(self):
        for f, h in SHA.items(): self.assertEqual(hashlib.sha256((ROOT / f).read_bytes()).hexdigest(), h, msg=f)

    def test_valve_law_endpoints(self):
        sens, drain, rec = z.stamina_terms(.7, vp, fp)
        self.assertAlmostEqual(z.valve_rate(0., drain, rec), rec)
        self.assertAlmostEqual(z.valve_rate(.5, drain, rec), 0.)
        self.assertAlmostEqual(z.valve_rate(1., drain, rec), -drain)
        self.assertGreater(z.valve_rate(.25, drain, rec), 0); self.assertLess(z.valve_rate(.75, drain, rec), 0)

    def test_stamina_orders_every_term(self):
        a, b = z.stamina_terms(.4, vp, fp), z.stamina_terms(1., vp, fp)
        self.assertGreater(a[0], b[0]); self.assertGreater(a[1], b[1]); self.assertLess(a[2], b[2])    # sensitivity, drain high at low stamina; recovery low

    def test_bench_is_flat_and_beats_the_best_valve_recovery(self):
        self.assertGreater(z.bench_rate(.4), z.stamina_terms(1., vp, fp)[2])
        a, b = Condition(reserve=0.), Condition(reserve=0.)
        z.bench_rest(a, 10., .4); z.bench_rest(b, 10., 1.)
        self.assertEqual(a.reserve, b.reserve); self.assertAlmostEqual(z.bench_rest(Condition(reserve=0.), 1e4, .5), 1.)

    def test_held_top_speed_empties_reserve_in_exhaust_time_at_reference(self):
        x, s = sim(T=14.)
        t = None
        for _ in range(int(14 / s.dt)):
            x.advance(s.dt)
            if t is None and x.cond.reserve <= .001: t = x.t
        self.assertAlmostEqual(t, 10., delta=.3)

    def test_higher_stamina_lasts_longer_in_a_sprint(self):
        r = []
        for st in (.4, .7, 1.):
            x, s = sim(st, T=12.); run_until(x, s, 12.); r.append(x.cond.reserve)
        self.assertEqual(r, sorted(r)); self.assertLess(r[1], .01); self.assertGreater(r[2], .3)

    def test_half_top_speed_hold_is_level(self):
        x, s = sim(mode='speed', v0=19., target=19., T=30., cond=Condition(reserve=.6)); run_until(x, s, 30.)
        self.assertAlmostEqual(x.cond.reserve, .6, delta=.05)

    def test_jogging_and_standing_recover_faster_than_half_speed(self):
        x, s = sim(mode='speed', v0=5., target=5., T=20., cond=Condition(reserve=.3)); run_until(x, s, 20.)
        self.assertGreater(x.cond.reserve, .55)

    def test_hard_cut_and_stop_are_intense_at_moderate_speed(self):
        s = Settings(mode='speed', target_speed=25., duration_s=3., turn_degrees=90., turn_time_s=.3)
        x = z.Sim(rated(1.), s, None, Condition(), None, 1e9, None, None, None, None, 1.); x.reset(25.)
        pk = 0.
        for _ in range(int(3 / s.dt)): x.advance(s.dt); pk = max(pk, x.intensity)
        self.assertGreater(pk, .7)
        s = Settings(mode='brake', duration_s=3.)
        x = z.Sim(rated(1.), s, None, Condition(), None, 1e9, None, None, None, None, 1.); x.reset(25.)
        pk = 0.
        for _ in range(int(2 / s.dt)): x.advance(s.dt); pk = max(pk, x.intensity)
        self.assertGreater(pk, .7)

    def test_disabled_valve_reproduces_v36_exactly(self):
        s = Settings(duration_s=6.)
        a = v36.Sim(rated(.8), s, None, Condition(), None, 1e9); a.reset(0.)
        b = z.Sim(rated(.8), s, None, Condition(), None, 1e9, None, None, None, z.ValveParams(enabled=False)); b.reset(0.)
        for _ in range(int(6 / s.dt)): a.advance(s.dt); b.advance(s.dt)
        self.assertEqual((a.x, a.vx, a.cond.reserve), (b.x, b.vx, b.cond.reserve))

    def test_rested_athlete_unchanged_for_a_short_effort(self):
        s = Settings(duration_s=2.)
        a = v36.Sim(rated(1.), s, None, Condition(), None, 1e9); a.reset(0.)
        b = z.Sim(rated(1.), s, None, Condition(), None, 1e9, None, None, None, None, 1.); b.reset(0.)
        for _ in range(int(2 / s.dt)): a.advance(s.dt); b.advance(s.dt)
        self.assertAlmostEqual(a.x, b.x, delta=.5)

    def test_reserve_stays_in_bounds_and_no_falls(self):
        for st in (.2, 1.):
            x, s = sim(st, T=30.); run_until(x, s, 30.)
            self.assertFalse(x.fallen); self.assertTrue(0. <= x.cond.reserve <= 1.)


if __name__ == '__main__':
    unittest.main()
