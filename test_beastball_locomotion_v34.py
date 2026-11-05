"""Tests for Beastball v3.4 (1.25x top-speed band).  Run: python -m unittest -q test_beastball_locomotion_v34  (about 1 minute)
v3.2 and v3.3.1 are untouched bases (SHA pinned).  Expected failures record open problems."""
import hashlib, math, unittest
from pathlib import Path
import beastball_locomotion_v32 as m
import beastball_locomotion_v33 as c
import beastball_locomotion_v34 as v
from beastball_locomotion_v32 import Settings, rated, assess

ROOT = Path(__file__).resolve().parent
V32_SHA256 = 'a8785d1d2edae8cf3a212d582dee7c8d082d37141269efc679755403309583a6'
V33_SHA256 = 'd92ed6adc1e82c55e1d4c00cb6528aed6c26b73f99b8b7322351bf42f9d405d5'
MPH = .44704
NOFAT = c.FatigueParams(max_loss=1e-9, tech_max_loss=1e-10, exhaust_time_s=1e9)


def top_mph(p):
    return v.rested_top_speed(p) / MPH


def time_to(p, dist, mod):
    s = Settings(duration_s=6.)
    sim = (c.Sim if mod == 'v33' else v.Sim)(p, s, None, None, NOFAT, 1e9); sim.reset(0.)
    for _ in range(int(6 / s.dt)):
        sim.advance(s.dt)
        if sim.x >= dist: return sim.t
    return None


class Base(unittest.TestCase):
    def test_bases_are_untouched(self):
        self.assertEqual(hashlib.sha256((ROOT / 'beastball_locomotion_v32.py').read_bytes()).hexdigest(), V32_SHA256)
        self.assertEqual(hashlib.sha256((ROOT / 'beastball_locomotion_v33.py').read_bytes()).hexdigest(), V33_SHA256)

    def test_band_target_arithmetic(self):
        b = v.BAND
        self.assertAlmostEqual(b.target_mph(1.0), 100., places=9)
        self.assertAlmostEqual(b.target_mph(.6), 80., places=9)
        self.assertAlmostEqual(b.target_mph(1.0) / b.target_mph(.6), 1.25, places=9)
        self.assertAlmostEqual(b.target_mph(.8), 90., places=9)


class Band(unittest.TestCase):
    def test_nodes_hit_target(self):
        for r in (.6, .7, .8, .9, 1.0):
            self.assertAlmostEqual(top_mph(rated(r)), v.BAND.target_mph(r), delta=.5, msg=f'rating {r}')

    def test_off_node_ratings_hit_target(self):          # interpolation of the solved map is accurate between nodes
        for r in (.62, .73, .88, .97):
            self.assertAlmostEqual(top_mph(rated(r)), v.BAND.target_mph(r), delta=.7, msg=f'rating {r}')

    def test_fastest_to_slowest_band_is_1_25(self):
        self.assertAlmostEqual(top_mph(rated(1.0)) / top_mph(rated(.6)), 1.25, delta=.012)

    def test_rating_one_is_100_mph_and_matches_v32_there(self):
        self.assertAlmostEqual(top_mph(rated(1.0)), 100., delta=.3)
        self.assertAlmostEqual(v.speed_ability(1.0), m.ability(1.0), places=3)     # the calibrated 100 mph point is preserved

    def test_monotone_in_rating_including_below_the_natural_range(self):
        prev = 0.
        for r in (.05, .1, .2, .3, .4, .5, .55, .6, .7, .8, .9, 1.0):
            s = top_mph(rated(r)); self.assertGreater(s, prev); prev = s

    def test_sub_natural_range_is_continuous_and_steeper(self):
        s55, s60, s65 = (top_mph(rated(r)) for r in (.55, .6, .65))
        self.assertLess(abs((s60 - s55) - (s65 - s60)), 3.5)       # no cliff at the join
        self.assertGreater((s60 - s55) / .05, (s65 - s60) / .05)   # condition losses keep v3.2 steepness below 0.6

    def test_keeper_follows_the_field_within_two_percent(self):
        for r in (.6, .8, 1.0):
            f, k = top_mph(rated(r)), top_mph(rated(r, 'keeper'))
            self.assertLess(abs(k / f - 1), .02, msg=f'rating {r}: field {f:.1f} keeper {k:.1f}')

    def test_mixed_profile_is_between_its_components(self):
        mixed = top_mph(rated(.8, strength=1.0, explosive_power=.6))
        self.assertGreater(mixed, top_mph(rated(.6))); self.assertLess(mixed, top_mph(rated(1.0)))


class AccelerationStandardPreserved(unittest.TestCase):
    """The v3.2 acceleration standard was accepted; only top speed was re-shaped."""

    def test_cones_traction_and_braking_force_use_the_v32_ability_map(self):
        for r in (.4, .6, .8, 1.0):
            p = rated(r); d34 = v.derive34(p, m.Params()); d32 = m.derive(p, m.Params())
            for k in ('tan_psi_acc', 'tan_psi_brk', 'tan_psi_lat', 'mu', 'brake_peak_N', 'drag_area_m2', 'tau_c_s'):
                self.assertEqual(d34[k], d32[k], msg=f'{k} r={r}')

    def test_first_ten_metres_unchanged(self):
        for r in (.6, .7, .8, 1.0):
            for dist in (5., 10.):
                a, b = time_to(rated(r), dist, 'v33'), time_to(rated(r), dist, 'v34')
                self.assertLess(abs(b / a - 1), .02, msg=f'rating {r} {dist} m: v3.3 {a:.2f} v3.4 {b:.2f}')

    def test_rating_one_is_identical_to_v33(self):
        for dist in (10., 36.576, 60.):
            self.assertAlmostEqual(time_to(rated(1.0), dist, 'v33'), time_to(rated(1.0), dist, 'v34'), delta=.011)

    def test_slower_athletes_are_no_slower_than_in_v33_beyond_20_m(self):
        for r in (.6, .7):
            self.assertLessEqual(time_to(rated(r), 60., 'v34'), time_to(rated(r), 60., 'v33') + .011)


class ConditionLayer(unittest.TestCase):
    def test_neutral_condition_equals_plain_v34(self):
        p = rated(.9)
        summ, _ = v.run(p, 0., Settings(duration_s=12.), None, None, NOFAT, 1e9)
        self.assertAlmostEqual(summ['sustained_speed_m_s'] / MPH, top_mph(p), delta=.35)

    def test_exhausted_top_athlete_lands_near_a_natural_point_six(self):
        s, _ = v.run(rated(1.0), 0., Settings(duration_s=14.), None, c.Condition(reserve=0.), c.FatigueParams(exhaust_time_s=1e9, recovery_tau_s=1e9), 1e9)
        self.assertTrue(77. < s['sustained_speed_m_s'] / MPH < 85.)

    def test_injury_severity_is_monotone_and_can_go_well_below_point_six(self):
        prev = 1e9
        for sev in (0., .25, .5, .75, 1.):
            s, _ = v.run(rated(1.0), 0., Settings(duration_s=14.), None, c.Condition(region='hamstring', severity=sev), c.FatigueParams(exhaust_time_s=1e9, recovery_tau_s=1e9), 1e9)
            self.assertLess(s['sustained_speed_m_s'] / MPH, prev); prev = s['sustained_speed_m_s'] / MPH
        self.assertLess(prev, 60.)


class DocumentedUnmet(unittest.TestCase):
    @unittest.expectedFailure
    def test_hard_stop_to_walking_speed_completes_upright(self):
        # open problem inherited from v3.3: brake mode trips 'landing_travel_exceeded' near 2 m/s
        for r in (.6, .8, 1.0):
            s = Settings(mode='brake', duration_s=8.); sim = v.Sim(rated(r), s, None, None, NOFAT, 1e9); sim.reset(20.)
            for _ in range(int(8 / s.dt)):
                if sim.fallen or sim._speed() < .3: break
                sim.advance(s.dt)
            self.assertFalse(sim.fallen)

    @unittest.expectedFailure
    def test_ninety_degree_cut_at_30_ms_resolves_in_under_a_second(self):
        # lateral limit 16 m/s^2*ability gives a 2.5 s, ~45 m radius turn at 30 m/s: not yet 'fluid'
        s = Settings(mode='speed', target_speed=30., duration_s=4., turn_degrees=90., turn_time_s=1.)
        sim = v.Sim(rated(1.0), s, None, None, NOFAT, 1e9); sim.reset(30.)
        th = None
        for _ in range(int(4 / s.dt)):
            if sim.fallen: break
            sim.advance(s.dt)
            if sim.t >= 1. and th is None and abs((math.degrees(math.atan2(sim.vy, sim.vx)) - 90. + 180) % 360 - 180) <= 5: th = sim.t - 1.
        self.assertIsNotNone(th); self.assertLess(th, 1.)


if __name__ == '__main__':
    unittest.main()
