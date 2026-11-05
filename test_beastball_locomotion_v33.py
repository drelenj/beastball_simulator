"""Tests for Beastball v3.3 (fatigue + injury layer).  Run: python -m unittest -q test_beastball_locomotion_v33  (about 1-2 minutes)
v3.2 is the untouched base (SHA pinned).  Expected failures record open problems."""
import hashlib, unittest
from pathlib import Path
import beastball_locomotion_v32 as m
import beastball_locomotion_v33 as F
from beastball_locomotion_v32 import Settings, rated, assess

ROOT = Path(__file__).resolve().parent
V32_SHA256 = 'a8785d1d2edae8cf3a212d582dee7c8d082d37141269efc679755403309583a6'
MPH = .44704
FP = F.FatigueParams()


def top_mph(p):
    return assess(p, 0., Settings(duration_s=14.))['sustained_speed_m_s'] / MPH


class Unit(unittest.TestCase):
    def test_validation(self):
        for bad in (dict(u_cp=1.2), dict(max_loss=1.0), dict(exhaust_time_s=0), dict(recovery_tau_s=float('nan'))):
            with self.assertRaises(ValueError): F.FatigueParams(**bad)
        for bad in (dict(reserve=1.5), dict(region='spleen', severity=.5), dict(severity=2.)):
            with self.assertRaises(ValueError): F.Condition(**bad)

    def test_effective_rating_arithmetic(self):
        a = rated(.8).athlete
        c = F.Condition(reserve=.5, region='hamstring', severity=.5)
        e = c.effective_ratings(a, FP)
        loss = 1 - FP.max_loss * .5 ** FP.loss_exponent
        self.assertAlmostEqual(e['strength'], .8 * (1 - .5 * .5) * loss, places=12)
        self.assertAlmostEqual(e['explosive_power'], .8 * (1 - .5 * .9) * loss, places=12)
        self.assertAlmostEqual(e['traction'], .8, places=12)           # hamstring weight 0, fatigue does not touch traction
        self.assertAlmostEqual(e['technique'], .8 * (1 - 0.) * (1 - FP.tech_max_loss * .5 ** FP.loss_exponent * (1 - .8)), places=12)

    def test_fatigue_hits_physical_ratings_hard_technique_softly_and_not_traction(self):
        e = F.Condition(reserve=0.).effective_ratings(rated(.8).athlete, FP)
        self.assertEqual(e['traction'], .8)
        self.assertLess(e['strength'], .8); self.assertLess(e['explosive_power'], .8); self.assertLess(e['technique'], .8)
        self.assertGreater(e['technique'], e['strength'])               # technique degrades less than the physical ratings

    def test_good_form_survives_fatigue_poor_form_gets_lazy(self):
        loss = {T: 1 - F.Condition(reserve=0.).effective_ratings(rated(T).athlete, FP)['technique'] / T for T in (.4, .7, .95, 1.)}
        self.assertGreater(loss[.4], loss[.7]); self.assertGreater(loss[.7], loss[.95])
        self.assertEqual(loss[1.], 0.)
        self.assertLess(loss[.95], .02)
        self.assertLess(max(loss.values()), FP.max_loss)

    def test_effective_ratings_floored(self):
        e = F.Condition(region='general', severity=1., reserve=0.).effective_ratings(rated(.3).athlete, FP)
        for v in e.values(): self.assertGreaterEqual(v, FP.floor_rating)

    def test_rest_recovers_toward_full(self):
        c = F.Condition(reserve=.2); c.rest(60., FP)
        self.assertAlmostEqual(c.reserve, 1 - .8 * 2.718281828459045 ** -1, places=9)
        c.rest(1e5, FP); self.assertAlmostEqual(c.reserve, 1., places=9)


class Base(unittest.TestCase):
    def test_v32_is_untouched_and_curve_unchanged(self):
        self.assertEqual(hashlib.sha256((ROOT / 'beastball_locomotion_v32.py').read_bytes()).hexdigest(), V32_SHA256)
        for r, mph in ((.4, 47.1), (.7, 75.7), (1.0, 99.9)):
            self.assertAlmostEqual(top_mph(rated(r)), mph, delta=.3, msg=r)

    def test_neutral_condition_is_identical_to_v32(self):
        for rt in (.3, 1.):
            for role in ('field', 'keeper'):
                a = assess(rated(rt, role), 0., Settings(duration_s=12.))
                b, _ = F.run(rated(rt, role), 0., Settings(duration_s=12.), fatigue=F.FatigueParams(max_loss=1e-9, tech_max_loss=1e-10, exhaust_time_s=1e9))
                self.assertEqual(a['speed_end_m_s'], b['speed_end_m_s'])
                self.assertEqual(a['touchdowns'], b['touchdowns'])

    def test_determinism(self):
        a, _ = F.run(rated(.9), 0., Settings(duration_s=10.)); b, _ = F.run(rated(.9), 0., Settings(duration_s=10.))
        self.assertEqual(a, b)


class Fatigue(unittest.TestCase):
    def test_fade_calibration_rating_one_loses_about_five_percent_by_ten_seconds(self):
        s, tr = F.run(rated(1.), 0., Settings(duration_s=12.))
        pk = max(a['speed'] for a in tr); v10 = [a for a in tr if a['t'] >= 10][0]['speed']
        self.assertTrue(s['upright'])
        self.assertTrue(.92 <= v10 / pk <= .97, v10 / pk)

    def test_reserve_drains_monotonically_in_max_effort_and_speed_falls_late(self):
        s, tr = F.run(rated(.9), 0., Settings(duration_s=20.))
        res = [a['reserve'] for a in tr]
        self.assertTrue(all(b <= a + 1e-12 for a, b in zip(res, res[1:])))
        self.assertLess(res[-1], .35)
        pk = max(a['speed'] for a in tr)
        self.assertLess(tr[-1]['speed'], .85 * pk)

    def test_jogging_below_critical_speed_does_not_drain_the_reserve(self):
        top = top_mph(rated(.9)) * MPH
        s, _ = F.run(rated(.9), 0., Settings(duration_s=25., mode='speed', target_speed=.6 * top))
        self.assertTrue(s['upright']); self.assertGreater(s['reserve_end'], .97)

    def test_fixed_reserve_lowers_top_speed_monotonically(self):
        prev = 1e9
        for R in (1., .75, .5, .25, 0.):
            v = top_mph(F.effective_profile(rated(.9), F.Condition(reserve=R), FP))
            self.assertLess(v, prev); prev = v
        self.assertTrue(.60 <= prev / top_mph(rated(.9)) <= .72, prev)       # empty reserve: about -32 %

    def test_repeated_sprints_recover_with_rest(self):
        peaks = []
        for rest in (0., 30., 120., 600.):
            c = F.Condition(); F.run(rated(.9), 0., Settings(duration_s=8.), condition=c); c.rest(rest, FP)
            s, tr = F.run(rated(.9), 0., Settings(duration_s=8.), condition=c); peaks.append(max(a['speed'] for a in tr))
        self.assertTrue(all(b > a for a, b in zip(peaks, peaks[1:])), peaks)
        self.assertGreater(peaks[-1] / max(peaks), .995)

    def test_fatigue_matters_compared_with_a_zero_loss_control(self):
        a, _ = F.run(rated(.9), 0., Settings(duration_s=14.))
        b, _ = F.run(rated(.9), 0., Settings(duration_s=14.), fatigue=F.FatigueParams(max_loss=1e-9, tech_max_loss=1e-10, exhaust_time_s=1e9))
        self.assertLess(a['speed_end_m_s'], .95 * b['speed_end_m_s'])


class Injury(unittest.TestCase):
    def test_more_severe_is_slower_for_every_region(self):
        for region in F.INJURY_REGIONS:
            prev = 1e9
            for sev in (0., .25, .5, .75):
                v = top_mph(F.effective_profile(rated(.9), F.Condition(region=region, severity=sev), FP))
                self.assertLessEqual(v, prev + 1e-9, (region, sev)); prev = v

    def test_region_ordering_hamstring_and_knee_hurt_more_than_ankle(self):
        v = {r: top_mph(F.effective_profile(rated(.9), F.Condition(region=r, severity=.5), FP)) for r in ('hamstring', 'knee', 'ankle', 'groin')}
        self.assertLess(v['hamstring'], v['ankle']); self.assertLess(v['knee'], v['ankle']); self.assertLess(v['hamstring'], v['groin'])

    def test_a_moderate_hamstring_or_knee_injury_puts_a_09_athlete_in_the_sub_06_speed_zone(self):
        for r in ('hamstring', 'knee'):
            v = top_mph(F.effective_profile(rated(.9), F.Condition(region=r, severity=.5), FP))
            self.assertLess(v, top_mph(rated(.6)) + 1.0, r)

    def test_injured_athletes_remain_upright_across_the_grid(self):
        for rt in (.6, 1.):
            for role in ('field', 'keeper'):
                for reg, sev in (('hamstring', .6), ('knee', .75), ('general', .9)):
                    for r0 in (1., .2):
                        s, _ = F.run(rated(rt, role), 0., Settings(duration_s=16.), condition=F.Condition(reserve=r0, region=reg, severity=sev))
                        self.assertTrue(s['upright'], (rt, role, reg, sev, r0, s['reason']))

    def test_cuts_stay_upright_when_degraded(self):
        for cond in (F.Condition(reserve=0.), F.Condition(region='knee', severity=.5), F.Condition(region='ankle', severity=.5)):
            pe = F.effective_profile(rated(.9), cond, FP)
            top = assess(pe, 0., Settings(duration_s=14.))['sustained_speed_m_s']
            for ang in (45, 90):
                self.assertTrue(assess(pe, .6 * top, Settings(duration_s=8., turn_degrees=ang, turn_time_s=1.))['upright'], (cond, ang))


class Technique(unittest.TestCase):
    @staticmethod
    def prof(T, r=.9):
        from dataclasses import replace
        from beastball_physical_standard_v1 import Athlete
        p = rated(r); a = p.athlete
        return replace(p, athlete=Athlete(a.height_m, a.mass_kg, strength=r, explosive_power=r, traction=r, technique=T))

    def t20_and_cut(self, T, R):
        import math
        fp = F.FatigueParams(exhaust_time_s=1e12, recovery_tau_s=1e12)         # freeze the reserve
        p = self.prof(T)
        s, tr = F.run(p, 0., Settings(duration_s=8.), condition=F.Condition(reserve=R), fatigue=fp, sample_dt=.005)
        t20 = [a['t'] for a in tr if a['speed'] >= 20][0]
        sim = F.Sim(p, Settings(duration_s=8., turn_degrees=90., turn_time_s=1.), None, F.Condition(reserve=R), fp); sim.reset(20.)
        th = None; t0 = None
        for _ in range(int(8 / .005)):
            if sim.fallen: break
            sim.advance(.005)
            if sim.turned:
                if t0 is None: t0 = sim.t
                err = abs((math.degrees(math.atan2(sim.vy, sim.vx)) - 90. + 180) % 360 - 180)
                if th is None and err <= 5 and sim._speed() > .5: th = sim.t - t0
        return t20, th, not sim.fallen, s['upright']

    def test_rested_athletes_are_unaffected_by_technique_level(self):
        a = self.t20_and_cut(.4, 1.); b = self.t20_and_cut(.95, 1.)
        self.assertEqual(a, b)

    def test_tired_poor_form_is_slower_off_the_mark_and_in_the_cut_than_tired_good_form(self):
        lazy = self.t20_and_cut(.4, 0.); good = self.t20_and_cut(.95, 0.)
        self.assertTrue(lazy[2] and lazy[3] and good[2] and good[3])
        self.assertGreater(lazy[0], good[0] * 1.05)
        self.assertGreater(lazy[1], good[1] * 1.05)

    def test_technique_costs_far_less_top_speed_than_strength_and_explosive_do(self):
        fp = F.FatigueParams(exhaust_time_s=1e12, recovery_tau_s=1e12)
        top = lambda T: F.run(self.prof(T), 0., Settings(duration_s=14.), condition=F.Condition(reserve=0.), fatigue=fp)[0]['sustained_speed_m_s']
        self.assertLess((top(.95) - top(.4)) / top(.95), .05)
        self.assertLess(top(.4), assess(self.prof(.4), 0., Settings(duration_s=14.))['sustained_speed_m_s'] * .75)    # still dominated by the physical loss

    def test_ankle_injury_degrades_technique_directly(self):
        e = F.Condition(region='ankle', severity=.5).effective_ratings(rated(.9).athlete, FP)
        self.assertAlmostEqual(e['technique'], .9 * (1 - .5 * .4), places=12)


class DocumentedUnmet(unittest.TestCase):
    @unittest.expectedFailure
    def test_OPEN_injured_athlete_tires_as_fast_as_a_healthy_one_at_equal_relative_effort(self):
        # intensity is measured against the RESTED, UNINJURED top speed, so a hurt athlete running flat out drains the reserve more slowly
        h, _ = F.run(rated(.9), 0., Settings(duration_s=14.))
        i, _ = F.run(rated(.9), 0., Settings(duration_s=14.), condition=F.Condition(region='knee', severity=.5))
        self.assertLessEqual(i['reserve_end'], h['reserve_end'] + 1e-9)

    @unittest.expectedFailure
    def test_OPEN_injury_has_healing_over_time(self):
        self.assertTrue(hasattr(F.Condition(), 'heal'))

    @unittest.expectedFailure
    def test_OPEN_fatigue_constants_are_fitted_to_more_than_one_anchor(self):
        self.assertGreater(len([k for k in vars(F.FatigueParams()) if 'anchor' in k]), 1)


if __name__ == '__main__':
    unittest.main()
