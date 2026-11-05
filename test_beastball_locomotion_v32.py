"""Tests for Beastball v3.2.  Run:  python -m unittest -q test_beastball_locomotion_v32   (about 2-3 minutes)

Layers: Unit / Invariants / Calibration / AbsoluteRating / Contact (compliant leg) / Controller / Posture+Acceleration / Cuts /
        Acceptance (gates) / Baseline (v3.1 untouched) / DocumentedUnmet (expected failures = open problems, they flip loudly
        to 'unexpected success' when fixed).
"""
import ast, hashlib, unittest
from math import hypot, atan, degrees, cos, sin, radians
from pathlib import Path
import beastball_locomotion_v31 as m31
import beastball_locomotion_v32 as m
import beastball_gates_v32 as gt
from beastball_locomotion_v32 import Params, Settings, assess, derive, rated, BENCHMARK_M_S
from beastball_physical_standard_v11 import profile, PerformanceProfile
from beastball_physical_standard_v1 import Athlete

ROOT = Path(__file__).resolve().parent
V31_SHA256 = '6dd694b7b8f09f97d83d009e1ba6027dc48422904e97349f371611a9514892b9'     # as delivered; v3.1 is the untouched baseline


def custom(h, mass, rating=.7):
    return PerformanceProfile('c', Athlete(h, mass, strength=rating, explosive_power=rating, traction=rating, technique=rating), min(1., rating), rating, rating, rating)


def sprint(p, T=16., params=None, **kw):
    return assess(p, 0., Settings(duration_s=T, **kw), params=params)


class Unit(unittest.TestCase):
    def test_params_and_settings_validate(self):
        for bad in (dict(kappa0=0), dict(drive_N_per_kg=float('nan')), dict(zeta=-1), dict(sweep_min_leg=.7), dict(rebound_gain=0)):
            with self.assertRaises(ValueError): Params(**bad)
        for bad in (dict(dt=0), dict(duration_s=0), dict(mode='teleport'), dict(contact='magic'), dict(controller='psychic'), dict(turn_degrees=181)):
            with self.assertRaises(ValueError): Settings(**bad)

    def test_negative_or_nan_start_speed_rejected(self):
        for v in (-1., float('nan'), float('inf')):
            with self.assertRaises(ValueError): assess(rated(.7), v, Settings(duration_s=1.))

    def test_kinematic_scales_are_absolute_not_body_dependent(self):
        f, k = derive(rated(.7, 'field')), derive(rated(.7, 'keeper'))
        self.assertAlmostEqual(f['kin_length_m'], k['kin_length_m'], places=12)
        self.assertAlmostEqual(f['swing_rel_speed_m_s'], k['swing_rel_speed_m_s'], places=12)
        self.assertAlmostEqual(f['fv_zero_force_speed_m_s'], k['fv_zero_force_speed_m_s'], places=12)
        self.assertGreater(k['leg_length_m'], f['leg_length_m'])                                  # anatomy (reach, leg length) still scales with height
        self.assertAlmostEqual(k['leg_length_m'] / f['leg_length_m'], 3.2004 / 2.54, places=9)

    def test_no_hidden_keeper_bonus(self):
        f, k = derive(rated(.7, 'field')), derive(rated(.7, 'keeper'))
        for key in ('kappa_peak_vertical_bw', 'ability_strength', 'ability_explosive', 'mu', 'tan_psi_acc', 'tan_psi_brk', 'tan_psi_lat'):
            self.assertAlmostEqual(f[key], k[key], places=12, msg=key)
        self.assertAlmostEqual(k['thrust_peak_N'] / k['mass_kg'], f['thrust_peak_N'] / f['mass_kg'], places=9)

    def test_drag_scales_with_mass_so_size_does_not_change_top_speed(self):
        a, b = derive(custom(2.54, 180.)), derive(custom(2.54, 360.))
        self.assertAlmostEqual(b['drag_area_m2'] / a['drag_area_m2'], 2., places=9)
        c = derive(custom(3.6, 180.))
        self.assertAlmostEqual(c['drag_area_m2'], a['drag_area_m2'], places=9)

    def test_no_speed_clamp_in_source(self):
        src = (ROOT / 'beastball_locomotion_v32.py').read_text()
        tree = ast.parse(src)
        names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)}
        for token in ('MAX_SPEED', 'speed_fraction', 'swing_speed_m_s', 'clamp', 'vmax'):
            self.assertNotIn(token, names, token)
        lines = src.splitlines()
        used = sorted({n.lineno for n in ast.walk(tree) if isinstance(n, ast.Name) and n.id == 'BENCHMARK_M_S'})
        self.assertTrue(used)
        for ln in used:
            self.assertTrue(any(k in lines[ln - 1] for k in ('exceeds_benchmark', 'benchmark_exceedance', 'self_propelled_exceedance', 'imparted_start', 'BENCHMARK_M_S = ')), lines[ln - 1])


class Invariants(unittest.TestCase):
    def test_zero_force_in_flight_nonnegative_force_and_energy_audit(self):
        for contact in ('spring', 'halfsine'):
            for p in (rated(.45), rated(1., 'keeper')):
                r, tr = assess(p, 0., Settings(duration_s=8., contact=contact), trace=True, sample_dt=.001)
                self.assertTrue(r['upright'], (contact, p.label))
                self.assertEqual(max(t['N'] for t in tr if t['phase'] == 'flight'), 0.)
                self.assertGreaterEqual(min(t['N'] for t in tr), 0.)
                self.assertLess(r['energy_audit_rel'], 1e-6, (contact, p.label))

    def test_friction_cone_respected_and_traction_matters(self):
        p = rated(.7)
        self.assertEqual(sprint(p)['slip_impulse_Ns'], 0.)
        dry = sprint(p)['sustained_speed_m_s']
        wet = assess(p, 0., Settings(duration_s=16., traction=.5))
        self.assertLess(wet['sustained_speed_m_s'], dry)

    def test_leg_never_longer_than_anatomical_length_in_stance_and_touchdown_reach_strict(self):
        for rt in (.2, .7, 1.):
            for role in ('field', 'keeper'):
                for start in (0., 10.):
                    r = assess(rated(rt, role), start, Settings(duration_s=8.))
                    self.assertTrue(r['upright'], (rt, role, start))
                    self.assertLessEqual(r['max_leg_extension'], Params().reach_max_leg + 1e-9)
                    self.assertLessEqual(r['touchdown_reach_mean_leg'], 1.0 + 1e-9)

    def test_leg_stance_extension_capped_at_one_leg_length(self):
        for p in (rated(1.), rated(1., 'keeper'), rated(.45)):
            self.assertLessEqual(sprint(p)['max_leg_extension'], 1.0 + 1e-9)

    def test_swing_foot_speed_within_derived_cap_no_teleport(self):
        for p in (rated(.7), rated(1., 'keeper')):
            r = sprint(p)
            self.assertLessEqual(r['foot_peak_relative_speed_m_s'], r['swing_rel_speed_cap_m_s'] * (1 + 1e-6))

    def test_determinism(self):
        a, b = sprint(rated(.7)), sprint(rated(.7))
        self.assertEqual(a, b)

    def test_rotational_invariance_of_heading(self):
        for start in (0., 12.):
            base = assess(rated(.7), start, Settings(duration_s=8., turn_degrees=0.))
            for ang in (37., 90., -120.):
                r = assess(rated(.7), start, Settings(duration_s=8., turn_degrees=ang))
                self.assertTrue(r['upright'], (start, ang, r['reason']))
                self.assertAlmostEqual(r['sustained_speed_m_s'], base['sustained_speed_m_s'], delta=.05 * base['sustained_speed_m_s'] + .1, msg=(start, ang))

    def test_start_from_rest_upright_for_field_and_keeper_at_all_ratings(self):
        for role in ('field', 'keeper'):
            for rt in (.05, .1, .3, .7, 1.):
                r = sprint(rated(rt, role), 14.)
                self.assertTrue(r['upright'], (role, rt, r['reason']))

    def test_benchmark_is_reporting_only(self):
        r = assess(rated(1.), 50., Settings(duration_s=3.))
        self.assertTrue(r['imparted_start_exceeds_benchmark'])
        self.assertIsNone(r['self_propelled_exceedance_m_s'])

    def test_speed_not_runaway(self):
        self.assertLess(sprint(rated(1., 'keeper'), 40.)['speed_peak_m_s'], 1.05 * BENCHMARK_M_S)

    def test_fall_reports_reason_never_raises(self):
        r = assess(rated(.3), 60., Settings(duration_s=5.))
        self.assertIn('reason', r)


class Calibration(unittest.TestCase):
    def test_rating_one_field_reproduces_100_mph_canon(self):
        self.assertAlmostEqual(sprint(rated(1.))['sustained_speed_m_s'], BENCHMARK_M_S, delta=.05)

    def test_rating_one_keeper_within_two_percent_of_field(self):
        f, k = sprint(rated(1.))['sustained_speed_m_s'], sprint(rated(1., 'keeper'))['sustained_speed_m_s']
        self.assertLess(abs(k - f) / f, .02)

    def test_speed_is_ordered_by_rating_and_pinned(self):
        prev = 0.
        pinned = {.1: 23.52, .3: 38.69, .7: 75.80, .92: 96.51}
        for rt in (.05, .1, .2, .3, .45, .6, .7, .8, .92, 1.):
            v = sprint(rated(rt))['sustained_speed_m_s']
            self.assertGreater(v, prev); prev = v
            if rt in pinned: self.assertAlmostEqual(v / .44704, pinned[rt], delta=.5, msg=rt)


class AbsoluteRating(unittest.TestCase):
    def test_top_speed_independent_of_mass(self):
        for rt in (.45, 1.):
            v = [sprint(custom(2.54, mass, rt))['sustained_speed_m_s'] for mass in (120., 180., 300., 420.)]
            self.assertLess((max(v) - min(v)) / min(v), 1e-3, rt)

    def test_top_speed_weakly_dependent_on_height_and_keeper_matches_field(self):
        for rt in (.45, .7):
            v = [sprint(custom(h, 180., rt))['sustained_speed_m_s'] for h in (2.4, 2.54, 2.9, 3.2004, 3.6)]
            self.assertLess((max(v) - min(v)) / min(v), .015, rt)       # <=1.5 % over a 1.5 m height range
        f, k = sprint(rated(.7))['sustained_speed_m_s'], sprint(rated(.7, 'keeper'))['sustained_speed_m_s']
        self.assertLess(abs(k - f) / f, .01)

    def test_v31_depended_strongly_on_build_for_contrast(self):
        v = [m31.assess(custom(h, 180., .7), 0., m31.Settings(duration_s=30.))['sustained_speed_m_s'] for h in (2.0, 3.6)]
        self.assertGreater((max(v) - min(v)) / min(v), .08)


class Contact(unittest.TestCase):
    def test_normal_force_emerges_from_leg_compression_not_a_prescribed_half_sine(self):
        r, tr = assess(rated(.7), 0., Settings(duration_s=6., contact='spring'), trace=True, sample_dt=.0005)
        # pick the last complete stance and compare its shape with the half-sine of equal peak and duration
        idx = [i for i, t in enumerate(tr) if t['phase'] == 'stance' and t['N'] > 0]
        runs, cur = [], [idx[0]]
        for i in idx[1:]:
            if i == cur[-1] + 1: cur.append(i)
            else: runs.append(cur); cur = [i]
        runs.append(cur)
        seg = [tr[i]['N'] for i in runs[-3]]
        pk, n = max(seg), len(seg)
        err = max(abs(seg[i] - pk * sin(3.141592653589793 * (i + .5) / n)) for i in range(n)) / pk
        self.assertGreater(err, .01)
        self.assertGreater(r['leg_stiffness_N_m'], 0.)
        self.assertGreater(r['leg_natural_freq_hz'], 0.)
        self.assertLess(r['peak_leg_compression_m'], Params().compression_limit * rated(.7).athlete.height_m * .53)

    def test_spring_and_halfsine_agree_on_speed_within_ten_percent_but_are_not_identical(self):
        for rt in (.3, .7, 1.):
            a = sprint(rated(rt), contact='spring')['sustained_speed_m_s']; b = sprint(rated(rt), contact='halfsine')['sustained_speed_m_s']
            self.assertNotEqual(a, b)
            self.assertLess(abs(a - b) / b, .10, rt)

    def test_timestep_and_substep_convergence(self):
        base = sprint(rated(.7))['sustained_speed_m_s']
        for dt, sub in ((.0025, .001), (.005, .0005), (.005, .002)):
            v = assess(rated(.7), 0., Settings(duration_s=16., dt=dt), params=Params(spring_substep_s=sub))['sustained_speed_m_s']
            self.assertLess(abs(v - base) / base, .002, (dt, sub))


class Controller(unittest.TestCase):
    def test_envelope_controller_upright_across_ratings_and_heights(self):
        for rt in (.2, .45, .7, 1.):
            for h, mass in ((2.2, 160.), (2.54, 180.), (3.2004, 300.)):
                r = sprint(custom(h, mass, rt))
                self.assertTrue(r['upright'], (rt, h, r['reason']))

    def test_controller_has_no_hidden_state_dependence_on_rating_tables(self):
        sim = m.Sim(rated(.7), Settings())
        self.assertLess(sim.v_env_lo, sim.v_env_hi)
        self.assertGreater(sim.util_steady(sim.v_env_lo), .8)

    def test_speed_mode_tracks_fractions_of_top_speed_upright(self):
        for rt in (.3, 1.):
            top = sprint(rated(rt))['sustained_speed_m_s']
            for f in (.3, .5, .9):
                r = assess(rated(rt), 0., Settings(duration_s=20., mode='speed', target_speed=f * top))
                self.assertTrue(r['upright'], (rt, f, r['reason']))
                self.assertLess(r['sustained_speed_m_s'], f * top * 1.03)
                self.assertGreater(r['sustained_speed_m_s'], f * top * .90)       # integral action removes the dissipation-induced offset

    def test_speed_mode_tracks_low_absolute_targets_down_to_two_m_s(self):
        for rt in (.3, 1.):
            for tgt in (2., 3., 6., 10.):
                r = assess(rated(rt), 0., Settings(duration_s=20., mode='speed', target_speed=tgt))
                self.assertTrue(r['upright'], (rt, tgt, r['reason']))
                self.assertGreater(r['sustained_speed_m_s'], .85 * tgt)

    def test_unregulated_gait_is_less_robust_than_regulated(self):
        reg = unreg = 0
        for rt in (.1, .3, .6, 1.):
            for h, mass in ((2.54, 180.), (3.2004, 300.)):
                reg += sprint(custom(h, mass, rt))['upright']
                unreg += sprint(custom(h, mass, rt), regulate=False)['upright']
        self.assertGreater(reg, unreg)


class PostureAndAcceleration(unittest.TestCase):
    def test_ground_force_tilt_never_exceeds_the_posture_cone(self):
        for rt in (.3, .7, 1.):
            p = rated(rt); d = derive(p)
            r = sprint(p)
            self.assertLessEqual(r['peak_grf_angle_deg'], degrees(atan(max(d['tan_psi_acc'], d['tan_psi_brk']))) + .5, rt)

    def test_peak_acceleration_consistent_with_v1_standard(self):
        p = rated(1.)
        r, tr = assess(p, 0., Settings(duration_s=8.), trace=True, sample_dt=.005)
        v = [hypot(t['vx'], t['vy']) for t in tr]; t = [x['t'] for x in tr]
        i20 = next(i for i, s in enumerate(v) if s >= 20.)
        mean_a = 20. / t[i20]
        cap = derive(p)['tan_psi_acc'] * 9.80665
        self.assertLessEqual(mean_a, cap * 1.01)               # mean acceleration to 20 m/s cannot exceed the cone limit
        self.assertGreater(mean_a, .5 * cap)                   # ... and the athlete actually uses a large part of it

    def test_acceleration_is_slower_than_v31_early_and_reaches_same_top_speed_band(self):
        a32, a31 = sprint(rated(1.)), m31.assess(rated(1.), 0., m31.Settings(duration_s=16.))
        self.assertLess(abs(a32['sustained_speed_m_s'] - a31['sustained_speed_m_s']) / a31['sustained_speed_m_s'], .02)


class Cuts(unittest.TestCase):
    def _cut(self, rt, frac, ang):
        top = sprint(rated(rt))['sustained_speed_m_s']
        return assess(rated(rt), frac * top, Settings(duration_s=8., turn_degrees=ang, turn_time_s=1.))

    def test_cuts_up_to_ninety_degrees_complete_upright_for_mid_and_high_ratings(self):
        for rt in (.5, .7, 1.):
            for frac in (.3, .6, .9):
                for ang in (30, 60, 90):
                    r = self._cut(rt, frac, ang)
                    self.assertTrue(r['upright'], (rt, frac, ang, r['reason']))
                    self.assertAlmostEqual(r['heading_end_deg'], ang, delta=6.)

    def test_sharper_cut_loses_more_speed_and_uses_more_lateral_lean(self):
        r30, r60, r90 = (self._cut(.7, .9, a) for a in (30, 60, 90))
        self.assertGreater(r30['min_speed_after_turn_m_s'], r60['min_speed_after_turn_m_s'])
        self.assertGreater(r60['min_speed_after_turn_m_s'], r90['min_speed_after_turn_m_s'])
        self.assertLess(r90['min_speed_after_turn_m_s'] / r90['speed_at_turn_m_s'], .75)         # hard cuts cost speed (ruling)
        self.assertGreater(r90['peak_lateral_tilt_deg'], 40.)       # the lateral lean budget is (nearly) used up in a hard cut

    def test_lateral_lean_never_exceeds_the_lateral_posture_cone(self):
        d = derive(rated(.7)); cone = degrees(atan(d['tan_psi_lat']))
        for ang in (60, 90, 120):
            self.assertLessEqual(self._cut(.7, .6, ang)['peak_lateral_tilt_deg'], cone + .5, ang)


class Acceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = [(p, s, gt.run_v31(p, s)) for p, s in gt.scenario_grid()]

    def test_integrity_gates_all_scenarios(self):
        for p, s, row in self.rows:
            g = gt.gates(row, p)
            for k, v in g['results'].items():
                if k.startswith('I'): self.assertTrue(v['passed'], (p.label, s, k, v))

    def test_gait_gates_at_attainable_speeds(self):
        n = 0
        for p, s, row in self.rows:
            g = gt.gates(row, p)
            if g['tier'] == 'gait':
                n += 1; self.assertTrue(g['passed_required'], (p.label, s, g['failed']))
        self.assertEqual(n, 12)

    def test_stress_tier_is_classified_and_reported_not_required(self):
        tiers = {gt.gates(row, p)['tier'] for p, s, row in self.rows}
        self.assertEqual(tiers, {'gait', 'stress'})


class Baseline(unittest.TestCase):
    def test_v31_source_is_byte_identical_to_the_delivered_baseline(self):
        self.assertEqual(hashlib.sha256((ROOT / 'beastball_locomotion_v31.py').read_bytes()).hexdigest(), V31_SHA256)

    def test_v31_rating_one_field_still_reproduces_its_own_calibration(self):
        r = m31.assess(m31.rated(1.), 0., m31.Settings(duration_s=45.))
        self.assertAlmostEqual(r['sustained_speed_m_s'], BENCHMARK_M_S, delta=.1)


class DocumentedUnmet(unittest.TestCase):
    """Open problems recorded as expected failures (see the report's 'unresolved' list)."""

    @unittest.expectedFailure
    def test_OPEN_rating_70_is_90_mph(self):
        # user's provisional anchor 'rating 70 = 90 mph'; the model gives ~76 mph (a canon decision on the rating->speed curve is needed)
        self.assertAlmostEqual(sprint(rated(.7))['sustained_speed_m_s'] / .44704, 90., delta=2.)

    @unittest.expectedFailure
    def test_OPEN_keeper_and_field_equal_to_one_percent_at_rating_one(self):
        f, k = sprint(rated(1.))['sustained_speed_m_s'], sprint(rated(1., 'keeper'))['sustained_speed_m_s']
        self.assertLess(abs(k - f) / f, .01)

    @unittest.expectedFailure
    def test_OPEN_sharp_cuts_beyond_ninety_degrees_are_reliable(self):
        for rt in (.5, .7, 1.):
            top = sprint(rated(rt))['sustained_speed_m_s']
            for frac in (.3, .6, .9):
                self.assertTrue(assess(rated(rt), frac * top, Settings(duration_s=8., turn_degrees=150., turn_time_s=1.))['upright'], (rt, frac))

    @unittest.expectedFailure
    def test_OPEN_fatigue_or_energetics_model_exists(self):
        # 'sustainable running' is only a gait-envelope utilisation band; there is no energetics/fatigue state
        self.assertTrue(any('fatigue' in k or 'energet' in k for k in vars(Params())))

    @unittest.expectedFailure
    def test_OPEN_athletes_below_two_metres_supported(self):
        self.assertTrue(sprint(custom(1.8, 100., .7))['upright'])


if __name__ == '__main__':
    unittest.main()
