"""Tests for Beastball v3.6 (fluid stops).  Run: python -m unittest -q test_beastball_locomotion_v36  (about 1 minute)
v3.2 - v3.5 are untouched bases (SHA pinned).  Expected failures record open problems."""
import hashlib, math, unittest
from pathlib import Path
import beastball_locomotion_v32 as m
import beastball_locomotion_v33 as c
import beastball_locomotion_v34 as v34
import beastball_locomotion_v35 as v35
import beastball_locomotion_v36 as z
from beastball_locomotion_v32 import Settings, rated
from stoplab_v36 import stop, NOFAT

ROOT = Path(__file__).resolve().parent
SHA = {'beastball_locomotion_v32.py': 'a8785d1d2edae8cf3a212d582dee7c8d082d37141269efc679755403309583a6',
       'beastball_locomotion_v33.py': 'd92ed6adc1e82c55e1d4c00cb6528aed6c26b73f99b8b7322351bf42f9d405d5',
       'beastball_locomotion_v34.py': 'ecd013e615f6edcc5afdca203a793ac422f8763293bb37aed278ad7f3e282ebf',
       'beastball_locomotion_v35.py': 'f9691073b92f97aad26d405c00aaf019de3402aa210238bfaafde4503b1f3d24'}
MPH = .44704
HOLD = c.FatigueParams(exhaust_time_s=1e9, recovery_tau_s=1e9)


class Base(unittest.TestCase):
    def test_bases_untouched(self):
        for f, h in SHA.items():
            self.assertEqual(hashlib.sha256((ROOT / f).read_bytes()).hexdigest(), h, msg=f)

    def test_standard(self):
        q = z.STANDARD36
        self.assertEqual((q.peak_brake_m_s2, q.brake_N_per_kg), (35., 100.))
        self.assertEqual((q.lateral_accel_m_s2, q.mu0, q.peak_accel_m_s2), (41., 4.3, m.Params().peak_accel_m_s2))   # cut and acceleration standards untouched
        d = v34.derive34(rated(1.0), q)
        self.assertAlmostEqual(d['tan_psi_brk'] * m.G, 42.7, delta=.3)
        self.assertGreater(d['mu'], d['tan_psi_brk'])


class OffReproducesV35(unittest.TestCase):
    def test_disabled_law_with_v35_params_is_bit_identical(self):
        s = Settings(mode='brake', duration_s=3.)
        a = v35.Sim(rated(.9), s, v35.STANDARD35, None, NOFAT, 1e9); a.reset(25.)
        b = z.Sim(rated(.9), s, v35.STANDARD35, None, NOFAT, 1e9, None, None, z.BrakeParams(enabled=False)); b.reset(25.)
        for _ in range(int(3 / s.dt)): a.advance(s.dt); b.advance(s.dt)
        self.assertEqual((a.x, a.vx, a.fallen), (b.x, b.vx, b.fallen))


class FluidStops(unittest.TestCase):
    def test_stops_complete_upright_at_every_speed_and_rating(self):       # failed near 2 m/s through v3.5
        for r in (.6, 1.0):
            for v0 in (5., 10., 15., 25., 35., 44.7):
                x = stop(v0, r=r); self.assertTrue(x['ok'], msg=f'r{r} {v0} {x}'); self.assertLess(x['end_speed'], .5)

    def test_stop_distance_targets_rating_one(self):
        for mph, v0, lim in ((33, 15., 2.5), (55, 25., 9.), (78, 35., 21.), (100, 44.7, 36.)):
            x = stop(v0); self.assertLessEqual(x['d3'], lim, msg=f'{mph} mph {x}')

    def test_distance_grows_with_speed_and_falls_with_rating(self):
        d = [stop(v0)['d3'] for v0 in (10., 15., 25., 35., 44.7)]
        self.assertEqual(d, sorted(d))
        self.assertLess(stop(25., r=1.0)['d3'], stop(25., r=.6)['d3'])

    def test_much_shorter_than_v35_at_top_speed(self):
        old = stop(44.7, q=v35.STANDARD35, br=z.BrakeParams(enabled=False))
        self.assertLess(stop(44.7)['d3'], .75 * old['d3'])

    def test_keeper_stops(self):
        self.assertTrue(stop(25., r=.8, role='keeper')['ok'])

    def test_fatigue_and_injury_lengthen_stops_in_order(self):
        d0 = stop(25.)['d3']
        df = stop(25., cond=c.Condition(reserve=0.), fp=HOLD)['d3']
        dh = stop(25., cond=c.Condition(region='hamstring', severity=1.), fp=HOLD)['d3']
        self.assertTrue(d0 < dh and d0 <= df, msg=(d0, df, dh))


class OthersUnchanged(unittest.TestCase):
    def test_top_speed_and_start_identical_to_v35(self):
        for r in (.6, 1.0):
            s = Settings(duration_s=3.)
            a = v35.Sim(rated(r), s, None, None, NOFAT, 1e9); b = z.Sim(rated(r), s, None, None, NOFAT, 1e9); a.reset(0.); b.reset(0.)
            for _ in range(int(3 / s.dt)): a.advance(s.dt); b.advance(s.dt)
            self.assertAlmostEqual(a.x, b.x, delta=.02)

    def test_cuts_identical_to_v35(self):
        for ang in (90., 180.):
            s = Settings(mode='speed', target_speed=25., duration_s=4., turn_degrees=ang, turn_time_s=1.)
            a = v35.Sim(rated(1.0), s, None, None, NOFAT, 1e9); b = z.Sim(rated(1.0), s, None, None, NOFAT, 1e9); a.reset(25.); b.reset(25.)
            for _ in range(int(4 / s.dt)): a.advance(s.dt); b.advance(s.dt)
            self.assertAlmostEqual(a.x, b.x, delta=.3); self.assertAlmostEqual(a.y, b.y, delta=.3)


class DocumentedUnmet(unittest.TestCase):
    @unittest.expectedFailure
    def test_severe_ankle_injury_stop_completes(self):
        self.assertTrue(stop(25., cond=c.Condition(region='ankle', severity=1.), fp=HOLD)['ok'])

    @unittest.expectedFailure
    def test_stop_from_top_speed_in_one_second(self):
        self.assertLessEqual(stop(44.7)['t3'], 1.0)          # model: 1.34 s at 3.2 g average


if __name__ == '__main__':
    unittest.main()
