"""Tests for Beastball v3.5 (arc cutting + fluid-cut standard).  Run: python -m unittest -q test_beastball_locomotion_v35  (about 1-2 minutes)
v3.2, v3.3.1 and v3.4 are untouched bases (SHA pinned).  Expected failures record open problems."""
import hashlib, math, unittest
from pathlib import Path
import beastball_locomotion_v32 as m
import beastball_locomotion_v33 as c
import beastball_locomotion_v34 as v34
import beastball_locomotion_v35 as w
from beastball_locomotion_v32 import Settings, rated
from cutlab_v35 import cut, NOFAT

ROOT = Path(__file__).resolve().parent
SHA = {'beastball_locomotion_v32.py': 'a8785d1d2edae8cf3a212d582dee7c8d082d37141269efc679755403309583a6',
       'beastball_locomotion_v33.py': 'd92ed6adc1e82c55e1d4c00cb6528aed6c26b73f99b8b7322351bf42f9d405d5',
       'beastball_locomotion_v34.py': 'ecd013e615f6edcc5afdca203a793ac422f8763293bb37aed278ad7f3e282ebf'}
MPH = .44704
HOLD = c.FatigueParams(exhaust_time_s=1e9, recovery_tau_s=1e9)
MS = {22: 10., 33: 15., 55: 25., 89: 40.}


class Base(unittest.TestCase):
    def test_bases_untouched(self):
        for f, h in SHA.items():
            self.assertEqual(hashlib.sha256((ROOT / f).read_bytes()).hexdigest(), h, msg=f)

    def test_standard(self):
        q = w.STANDARD35
        self.assertEqual((q.lateral_accel_m_s2, q.mu0), (41., 4.3))
        d = v34.derive34(rated(1.0), q)
        self.assertAlmostEqual(d['tan_psi_lat'] * m.G, 50., delta=.2)          # 50 m/s^2 lateral cone at rating 1.0
        self.assertGreater(d['mu'], d['tan_psi_lat'])                            # friction never limits the lean cone
        self.assertEqual(w.STANDARD35.peak_accel_m_s2, m.Params().peak_accel_m_s2)   # acceleration and braking standards untouched
        self.assertEqual(w.STANDARD35.peak_brake_m_s2, m.Params().peak_brake_m_s2)


class ArcOffReproducesV34(unittest.TestCase):
    def test_disabled_arc_with_v32_params_is_bit_identical_to_v34(self):
        for ang in (45., 90.):
            s = Settings(mode='speed', target_speed=25., duration_s=3., turn_degrees=ang, turn_time_s=1.)
            a = v34.Sim(rated(.9), s, m.Params(), None, NOFAT, 1e9); a.reset(25.)
            b = w.Sim(rated(.9), s, m.Params(), None, NOFAT, 1e9, None, w.ArcParams(enabled=False)); b.reset(25.)
            for _ in range(int(3 / s.dt)):
                a.advance(s.dt); b.advance(s.dt)
            self.assertEqual((a.x, a.y, a.vx, a.vy, a.fallen), (b.x, b.y, b.vx, b.vy, b.fallen))


class FluidCuts(unittest.TestCase):
    def test_ninety_degree_cut_times_and_speed_kept(self):
        limits = {22: 1.0, 33: 1.0, 55: 1.35, 89: 1.6}
        for mph, lim in limits.items():
            r = cut(1.0, MS[mph], 90.)
            self.assertTrue(r['ok'], msg=f'{mph} mph {r}')
            self.assertLessEqual(r['t_head'], lim, msg=f'{mph} mph {r}')
            self.assertGreaterEqual(r['v_at_heading_pct'], 80, msg=f'{mph} mph {r}')

    def test_reversals_complete_and_keep_speed(self):             # 150 and 180 degree cuts failed or kept 1-41 percent of speed through v3.4
        for ang in (150., 180.):
            for mph in (22, 55, 89):
                r = cut(1.0, MS[mph], ang, T=7.)
                self.assertTrue(r['ok'], msg=f'{ang} @ {mph} mph {r}')
                self.assertIsNotNone(r['t_head'])
                self.assertGreaterEqual(r['v_at_heading_pct'], 80, msg=f'{ang} @ {mph} mph {r}')

    def test_cut_time_grows_with_speed_and_angle(self):
        t = {mph: cut(1.0, MS[mph], 90.)['t_head'] for mph in (22, 33, 55, 89)}
        self.assertTrue(t[22] <= t[33] < t[55] < t[89], msg=str(t))
        a = {ang: cut(1.0, 25., ang, T=7.)['t_head'] for ang in (45., 90., 150., 180.)}
        self.assertTrue(a[45.] < a[90.] < a[150.] < a[180.], msg=str(a))

    def test_low_speed_cuts_stay_upright(self):
        for v0 in (3., 6.):
            r = cut(1.0, v0, 90.)
            self.assertTrue(r['ok'], msg=str(r)); self.assertLess(r['t_head'], 1.5)

    def test_much_faster_than_instant_flip_at_speed_and_keeps_more_speed(self):
        old = cut(1.0, 25., 90., params=m.Params(), arc=w.ArcParams(enabled=False))
        new = cut(1.0, 25., 90.)
        self.assertLess(new['t_head'], .7 * old['t_head'])
        self.assertGreater(new['vmin_pct'], old['vmin_pct'] + 20)


class StraightLineAndBrakingUnchanged(unittest.TestCase):
    def test_top_speed_and_start_unchanged(self):
        for r in (.6, 1.0):
            s = Settings(duration_s=16.); sim = w.Sim(rated(r), s, None, None, NOFAT, 1e9)
            self.assertAlmostEqual(v34.run_sim(sim)['sustained_speed_m_s'] / MPH, v34.rested_top_speed(rated(r)) / MPH, delta=.15)
            s = Settings(duration_s=3.)
            a = v34.Sim(rated(r), s, None, None, NOFAT, 1e9); b = w.Sim(rated(r), s, None, None, NOFAT, 1e9); a.reset(0.); b.reset(0.)
            for _ in range(int(3 / s.dt)): a.advance(s.dt); b.advance(s.dt)
            self.assertAlmostEqual(a.x, b.x, delta=.02)

    def test_braking_distance_unchanged(self):
        s = Settings(mode='brake', duration_s=6.)
        a = v34.Sim(rated(1.0), s, None, None, NOFAT, 1e9); b = w.Sim(rated(1.0), s, None, None, NOFAT, 1e9); a.reset(25.); b.reset(25.)
        for _ in range(int(2 / s.dt)): a.advance(s.dt); b.advance(s.dt)
        self.assertAlmostEqual(a.x, b.x, delta=.05)


class BodiesAndConditions(unittest.TestCase):
    def test_lower_ratings_cut_slower(self):
        self.assertLess(cut(1.0, 25., 90.)['t_head'], cut(.6, 25., 90.)['t_head'])

    def test_keeper_cuts(self):
        r = cut(.8, 25., 90., role='keeper'); self.assertTrue(r['ok']); self.assertLess(r['t_head'], 1.8)

    def test_fatigue_and_injury_slow_the_cut_in_order(self):
        t0 = cut(1.0, 25., 90.)['t_head']
        tf = cut(1.0, 25., 90., cond=c.Condition(reserve=0.), fp=HOLD)['t_head']
        th5 = cut(1.0, 25., 90., cond=c.Condition(region='hamstring', severity=.5), fp=HOLD)['t_head']
        th10 = cut(1.0, 25., 90., cond=c.Condition(region='hamstring', severity=1.), fp=HOLD)['t_head']
        self.assertTrue(t0 < tf < th5 < th10, msg=(t0, tf, th5, th10))

    def test_severe_ankle_injury_cannot_complete_the_cut_in_five_seconds(self):
        r = cut(1.0, 25., 90., cond=c.Condition(region='ankle', severity=1.), fp=HOLD)
        self.assertTrue(r['ok']); self.assertIsNone(r['t_head'])


class DocumentedUnmet(unittest.TestCase):
    @unittest.expectedFailure
    def test_ninety_degree_cut_at_top_speed_in_a_second(self):
        self.assertLessEqual(cut(1.0, 40., 90.)['t_head'], 1.0)        # model gives ~1.4 s: peak ~60 kN through one foot already

    @unittest.expectedFailure
    def test_hard_stop_to_walking_speed_completes_upright(self):
        s = Settings(mode='brake', duration_s=8.); sim = w.Sim(rated(1.0), s, None, None, NOFAT, 1e9); sim.reset(20.)
        for _ in range(int(8 / s.dt)):
            if sim.fallen or sim._speed() < .3: break
            sim.advance(s.dt)
        self.assertFalse(sim.fallen)


if __name__ == '__main__':
    unittest.main()
