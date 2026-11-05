"""Tests for Beastball v3.1.  Run:  python -m unittest -q test_beastball_locomotion_v31   (about 1-2 minutes)

Layers:  Unit / Invariant / Regression / Convergence / Sensitivity / Acceptance (the gates in beastball_gates_v31) /
         BaselineV30 (documents what the shipped v3.0 does NOT meet) / DocumentedUnmet (expected failures = open problems).
A test marked expectedFailure is an INTENTIONALLY FAILING gate: it records a known unresolved problem or a baseline
deficiency and will start 'unexpectedly succeeding' (loudly) when the problem is fixed.
"""
import ast, csv, unittest
from dataclasses import replace
from math import hypot, atan2, degrees
from pathlib import Path
import beastball_locomotion_v31 as m
import beastball_unified_locomotion_v30 as m30
import beastball_gates_v31 as gt
from beastball_locomotion_v31 import Params, Settings, assess, derive, rated, BENCHMARK_M_S
from beastball_physical_standard_v11 import profile
from beastball_physical_standard_v1 import Athlete
from beastball_physical_standard_v11 import PerformanceProfile

ROOT = Path(__file__).resolve().parent


def custom(h, mass, s=.7, e=.7, t=.7):
    return PerformanceProfile('c', Athlete(h, mass, strength=s, explosive_power=e, traction=t, technique=.7), .7, .7, .7, .7)


def sprint(p, T=30., params=None, **kw):
    return assess(p, 0., Settings(duration_s=T, **kw), params=params)


class Unit(unittest.TestCase):
    def test_params_and_settings_validate(self):
        for bad in (dict(kappa0=0), dict(drive_N_per_kg=float('nan')), dict(sweep_max_leg=1.2), dict(sweep_min_leg=.7)):
            with self.assertRaises(ValueError): Params(**bad)
        for bad in (dict(dt=0), dict(dt=.05), dict(duration_s=0), dict(mode='teleport'), dict(turn_degrees=181), dict(turn_time_s=-1)):
            with self.assertRaises(ValueError): Settings(**bad)

    def test_negative_or_nan_start_speed_rejected(self):
        for v in (-1., float('nan'), float('inf')):
            with self.assertRaises(ValueError): assess(rated(.7), v, Settings(duration_s=1.))

    def test_derive_scales_with_mass_and_ratings(self):
        a = derive(custom(2.54, 180.)); b = derive(custom(2.54, 360.))
        self.assertAlmostEqual(b['peak_vertical_force_N'] / a['peak_vertical_force_N'], 2., places=9)
        self.assertAlmostEqual(b['thrust_peak_N'] / a['thrust_peak_N'], 2., places=9)
        self.assertAlmostEqual(b['kappa_peak_vertical_bw'], a['kappa_peak_vertical_bw'], places=9)      # in bodyweights: mass-free
        self.assertEqual(b['swing_time_full_sweep_s'], a['swing_time_full_sweep_s'])
        s1, s2 = derive(custom(2.54, 180., s=.4)), derive(custom(2.54, 180., s=.9))
        self.assertGreater(s2['kappa_peak_vertical_bw'], s1['kappa_peak_vertical_bw'])
        self.assertEqual(s2['swing_rel_speed_m_s'], s1['swing_rel_speed_m_s'])                           # strength does not buy leg speed
        e1, e2 = derive(custom(2.54, 180., e=.4)), derive(custom(2.54, 180., e=.9))
        self.assertGreater(e2['swing_rel_speed_m_s'], e1['swing_rel_speed_m_s'])
        self.assertLess(e2['rfd_time_to_peak_s'], e1['rfd_time_to_peak_s'])
        self.assertEqual(e2['kappa_peak_vertical_bw'], e1['kappa_peak_vertical_bw'])                     # explosive power does not buy peak force

    def test_no_hidden_keeper_bonus(self):
        f, k = derive(rated(.7, 'field')), derive(rated(.7, 'keeper'))
        for key in ('kappa_peak_vertical_bw', 'ability_strength', 'ability_explosive', 'mu'):
            self.assertAlmostEqual(f[key], k[key], places=12, msg=key)
        self.assertAlmostEqual(k['leg_length_m'] / f['leg_length_m'], 3.2004 / 2.54, places=9)
        self.assertAlmostEqual(k['thrust_peak_N'] / k['mass_kg'], f['thrust_peak_N'] / f['mass_kg'], places=9)

    def test_leg_geometry_from_height(self):
        self.assertAlmostEqual(derive(rated(.7))['leg_length_m'], .53 * 2.54, places=9)

    def test_no_speed_clamp_in_source(self):
        src = (ROOT / 'beastball_locomotion_v31.py').read_text()
        names = {n.id for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Attribute)}
        for token in ('MAX_SPEED', 'speed_fraction', 'swing_speed_m_s', 'clamp', 'vmax'):
            self.assertNotIn(token, names, token)
        self.assertNotIn('min(speed', src)
        # BENCHMARK_M_S may only be used for reporting
        lines = src.splitlines()
        used = sorted({n.lineno for n in ast.walk(ast.parse(src)) if isinstance(n, ast.Name) and n.id == 'BENCHMARK_M_S'})
        self.assertTrue(used)
        for ln in used:
            self.assertTrue(any(k in lines[ln - 1] for k in ('exceeds_benchmark', 'benchmark_exceedance', 'self_propelled_exceedance', 'imparted_start', 'BENCHMARK_M_S = ')), lines[ln - 1])


class Invariants(unittest.TestCase):
    CASES = [(rated(.2), 0.), (rated(.7), 15.), (rated(1.0), 0.), (rated(.7, 'keeper'), 10.), (profile('average', 'field'), 20.)]

    def test_zero_normal_force_in_flight_and_nonnegative_force(self):
        for p, v in self.CASES:
            r, tr = assess(p, v, Settings(duration_s=5.), trace=True, sample_dt=.0025)
            self.assertTrue(r['upright'], p.label)
            fl = [t['N'] for t in tr if t['phase'] == 'flight']
            self.assertGreater(len(fl), 100)
            self.assertEqual(max(fl), 0.)
            self.assertGreaterEqual(min(t['N'] for t in tr), 0.)

    def test_normal_force_zero_at_contact_edges(self):
        r, tr = assess(rated(.7), 10., Settings(dt=.0005, duration_s=2.), trace=True)
        bw = 180 * m.G
        first = [b['N'] / bw for a, b in zip(tr, tr[1:]) if a['phase'] == 'flight' and b['phase'] == 'stance']
        self.assertTrue(first)
        self.assertLess(max(first), .15)         # no onset spike (v3.0: 10.3 BW on the first landing tick)

    def test_energy_audit_and_impulse_balance(self):
        for p, v in self.CASES:
            r = assess(p, v, Settings(duration_s=20.))
            self.assertLess(r['energy_audit_rel'], 1e-4, p.label)
            self.assertAlmostEqual(r['vertical_impulse_ratio'], 1., delta=.01, msg=p.label)    # mean vertical impulse = body weight x period

    def test_leg_never_below_compression_limit_and_reach_bounded(self):
        for p, v in self.CASES:
            r = assess(p, v, Settings(duration_s=20.))
            self.assertGreater(r['min_leg_ratio'], 1 - Params().compression_limit)
            self.assertLessEqual(r['max_leg_extension'], Params().reach_max_leg + 1e-9)
            self.assertLess(r['touchdown_reach_mean_leg'], 1.10)

    def test_friction_cone_respected_and_traction_matters(self):
        r = sprint(rated(1.0), 20.)
        self.assertEqual(r['slip_impulse_Ns'], 0.)
        lo = sprint(rated(1.0), 20., traction=.2)
        self.assertGreater(lo['slip_impulse_Ns'], 0.)
        self.assertLess(lo['sustained_speed_m_s'], r['sustained_speed_m_s'])
        _, tr = assess(rated(1.0), 0., Settings(duration_s=3., traction=.5), trace=True)
        self.assertTrue(tr)

    def test_swing_foot_speed_within_derived_cap_no_teleport(self):
        for p, v in self.CASES:
            r = assess(p, v, Settings(duration_s=10.))
            self.assertLessEqual(r['foot_peak_relative_speed_m_s'], r['swing_rel_speed_cap_m_s'] * 1.01, p.label)
            self.assertLess(r['foot_peak_ground_speed_m_s'], 2.0 * max(r['speed_peak_m_s'], 5.), p.label)

    def test_determinism(self):
        a = assess(rated(.7), 5., Settings(duration_s=6.)); b = assess(rated(.7), 5., Settings(duration_s=6.))
        self.assertEqual(a, b)

    def test_rotational_invariance_of_heading(self):
        base = sprint(rated(.7), 10.)
        for ang in (30, 90, -90, 180):
            r = sprint(rated(.7), 10., turn_degrees=ang)
            self.assertAlmostEqual(r['sustained_speed_m_s'], base['sustained_speed_m_s'], places=3)
            self.assertAlmostEqual(r['touchdowns'], base['touchdowns'], delta=0)
            self.assertAlmostEqual(abs((r['heading_end_deg'] - ang + 180) % 360 - 180), 0., delta=.5)

    def test_start_from_rest_with_any_heading_is_upright(self):          # regression: zero-time touchdown loop found in the first full run
        for ang in (0, 45, 90, 180):
            for t in gt.TIERS:
                r = assess(profile(t, 'field'), 0., Settings(duration_s=3., turn_degrees=ang))
                self.assertTrue(r['upright'], (ang, t, r['reason']))

    def test_benchmark_is_reporting_only(self):
        # a rating-1.0 athlete with 1.3x muscle capacity must exceed 100 mph (nothing clamps) and say so
        r = sprint(rated(1.0), 30., muscle=1.3)
        self.assertTrue(r['upright'])
        self.assertGreater(r['sustained_speed_m_s'], BENCHMARK_M_S + 1.)
        self.assertTrue(r['exceeds_benchmark']); self.assertGreater(r['self_propelled_exceedance_m_s'], 1.)

    def test_imparted_speed_is_distinct_from_self_propelled(self):
        r = assess(rated(.45), 50., Settings(duration_s=.5))
        self.assertTrue(r['imparted_start_exceeds_benchmark'])
        self.assertIsNone(r['self_propelled_exceedance_m_s'])             # undefined: the speed was handed to the athlete
        s = sprint(rated(.45), 30.)
        self.assertFalse(s['imparted_start_exceeds_benchmark'])

    def test_speed_not_runaway_without_resistance_limit(self):
        p = rated(1.0)
        r = assess(p, 0., Settings(duration_s=40., muscle=2.0))
        self.assertTrue(r['upright'] or r['reason'])
        self.assertLess(r['speed_peak_m_s'], derive(p, muscle=2.)['fv_zero_force_speed_m_s'])    # bounded by the force-velocity zero-force speed

    def test_fall_reports_reason_never_raises(self):
        r = assess(rated(.3), 40., Settings(duration_s=3.))
        self.assertFalse(r['upright']); self.assertIn(r['reason'], ('missed_touchdown', 'landing_travel_exceeded', 'degenerate_gait', 'stuck_in_flight', 'overreach'))


class Regression(unittest.TestCase):
    """Pinned reference values (rtol 1%) - they move only when the model constants are deliberately changed."""
    def test_pinned_values(self):
        pins = {('field_average', 0.): 33.41, ('field_exceptional', 0.): 40.77, ('keeper_exceptional', 0.): 44.25, ('field_developing', 20.): 22.93}
        for (label, v), expect in pins.items():
            tier, role = label.split('_')[1], label.split('_')[0]
            r = assess(profile(tier, role), v, Settings(duration_s=6.))
            self.assertAlmostEqual(r['speed_end_m_s'], expect, delta=.01 * expect, msg=label)

    def test_v30_unchanged_vs_shipped_results(self):
        rows = list(csv.DictReader((ROOT / 'baseline_v30_shipped' / 'beastball_v30_results.csv').open()))
        pick = [r for r in rows if r['dt_s'] == '0.005'][::9]
        self.assertGreater(len(pick), 4)
        for row in pick:
            p = profile(row['profile'].split('_')[1], row['profile'].split('_')[0])
            r = m30.assess(p, float(row['initial_speed_m_s']), m30.Settings(turn_degrees=float(row['turn_degrees'])))
            self.assertEqual(str(r['landings']), row['landings']); self.assertEqual(f"{r['peak_normal_N']}", f"{float(row['peak_normal_N'])}")
            self.assertEqual(str(r['grounded']), row['grounded'])


class Calibration(unittest.TestCase):
    def test_rating_one_field_reproduces_the_benchmark(self):
        v = sprint(rated(1.0), 45.)['sustained_speed_m_s']
        self.assertAlmostEqual(v, BENCHMARK_M_S, delta=.01 * BENCHMARK_M_S)

    def test_speed_is_emergent_and_ordered_by_rating(self):
        sp = [sprint(rated(rt))['sustained_speed_m_s'] for rt in (.1, .3, .45, .6, .7, .8, .92, 1.0)]
        self.assertEqual(sp, sorted(sp))
        self.assertGreater(len(set(round(x, 1) for x in sp)), 7)
        self.assertGreater(sp[-1] / sp[0], 3.)


class Convergence(unittest.TestCase):
    def test_timestep_convergence_sprint(self):
        for rt, tol in ((.45, .005), (.7, .005), (1.0, .02)):
            v = [sprint(rated(rt), 30., dt=dt)['sustained_speed_m_s'] for dt in (.0025, .005, .01, .02)]
            self.assertLess((max(v) - min(v)) / (sum(v) / 4), tol, (rt, v))

    def test_timestep_convergence_cut(self):
        v = []
        for dt in (.0025, .005, .01):
            r = assess(rated(.7), 15., Settings(dt=dt, duration_s=6., mode='speed', target_speed=15., turn_degrees=90., turn_time_s=2.))
            self.assertTrue(r['upright']); v.append(r['time_to_heading_5deg_s'])
        self.assertLess(max(v) - min(v), .06)


class AnatomyAndRatings(unittest.TestCase):
    def test_strength_changes_vertical_capacity_and_speed_at_same_mass(self):
        lo = sprint(custom(2.54, 180., s=.3)); hi = sprint(custom(2.54, 180., s=.9))
        self.assertGreater(hi['sustained_speed_m_s'], lo['sustained_speed_m_s'] + 5.)
        self.assertGreater(hi['peak_normal_bw'], lo['peak_normal_bw'] + 1.)
        self.assertGreater(hi['kappa_cap_bw'], lo['kappa_cap_bw'])

    def test_explosive_power_changes_contact_flight_and_cadence_at_same_mass(self):
        lo = sprint(custom(2.54, 180., e=.3)); hi = sprint(custom(2.54, 180., e=.9))
        self.assertGreater(hi['step_frequency_hz'], lo['step_frequency_hz'] + .5)
        self.assertLess(hi['flight_time_s'], lo['flight_time_s'])
        self.assertGreater(hi['sustained_speed_m_s'], lo['sustained_speed_m_s'] + 5.)

    def test_v30_is_blind_to_strength_explosive_and_v31_is_not(self):
        base = profile('average', 'field')
        seen = set()
        for st in (.2, .7, 1.):
            for ex in (.2, .7, 1.):
                q = replace(base, athlete=replace(base.athlete, strength=st, explosive_power=ex))
                r = m30.assess(q, 10, m30.Settings(duration_s=1.)); seen.add((r['peak_height_m'], r['peak_normal_N']))
        self.assertEqual(len(seen), 1)                                   # v3.0: one value for all nine combinations
        seen31 = {sprint(custom(2.54, 180., s=st, e=ex), 20.)['sustained_speed_m_s'] for st in (.2, .7, 1.) for ex in (.2, .7, 1.)}
        self.assertEqual(len(seen31), 9)

    def test_mass_effect_same_height_and_height_effect_same_mass_are_reported_not_hidden(self):
        light, heavy = sprint(custom(2.54, 120.))['sustained_speed_m_s'], sprint(custom(2.54, 300.))['sustained_speed_m_s']
        self.assertGreater(heavy, light)                                 # drag per kg falls with mass (force capacity scales with mass)
        self.assertLess(heavy / light, 1.15)
        short, tall = sprint(custom(2.0, 180.))['sustained_speed_m_s'], sprint(custom(3.2004, 180.))['sustained_speed_m_s']
        self.assertGreater(tall, short)

    def test_keeper_vs_field_difference_comes_only_from_geometry_and_mass(self):
        f, k = sprint(rated(.7, 'field')), sprint(rated(.7, 'keeper'))
        self.assertGreater(k['sustained_speed_m_s'], f['sustained_speed_m_s'])
        # equalize geometry and mass: identical outcome
        a = sprint(custom(2.54, 180.)); b = sprint(PerformanceProfile('x', Athlete(2.54, 180., strength=.7, explosive_power=.7, traction=.7, technique=.7), .7, .7, .7, .7))
        self.assertEqual(a['sustained_speed_m_s'], b['sustained_speed_m_s'])


class Sensitivity(unittest.TestCase):
    def test_monotone_responses_to_physical_parameters(self):
        base = sprint(rated(.7))['sustained_speed_m_s']
        def v(**kw): return sprint(rated(.7), params=replace(Params(), **kw))['sustained_speed_m_s']
        self.assertLess(v(cd_area_per_h2=.17 * 1.5), base)               # more drag -> slower
        self.assertGreater(v(drive_N_per_kg=61.8 * 1.3), base)           # more thrust -> faster
        self.assertGreater(v(kappa0=9.5), base)                          # more vertical capacity -> faster (gait-limited at r=0.7)
        self.assertLess(v(swing_c=1.3), base)                            # slower leg swing -> slower
        self.assertGreater(v(leg_length_height=.6), base)

    def test_all_perturbations_stay_upright(self):
        for kn in ('kappa0', 'swing_c', 'fv_froude', 'drive_N_per_kg', 'cd_area_per_h2', 'sweep_max_leg', 'leg_length_height'):
            for fac in (.8, 1.25):
                if kn == 'sweep_max_leg' and fac > 1: continue           # longer sweep violates the reach limit (next test)
                q = replace(Params(), **{kn: getattr(Params(), kn) * fac})
                r = assess(rated(.7), 0., Settings(duration_s=20.), params=q)
                self.assertTrue(r['upright'], (kn, fac, r['reason']))

    def test_reach_limit_binds_when_sweep_is_stretched(self):
        r = assess(rated(.7), 0., Settings(duration_s=20.), params=replace(Params(), sweep_max_leg=.75))
        self.assertFalse(r['upright']); self.assertEqual(r['reason'], 'overreach')


class Cuts(unittest.TestCase):
    def test_progressive_cuts_reach_commanded_heading_upright(self):
        top = sprint(rated(.7))['sustained_speed_m_s']
        for ang in (30, 45, 90):
            v = .5 * top
            r = assess(rated(.7), v, Settings(duration_s=8., mode='speed', target_speed=v, turn_degrees=ang, turn_time_s=2.))
            self.assertTrue(r['upright'], ang)
            self.assertLess(abs(r['heading_end_deg'] - ang), 1.)
            self.assertIsNotNone(r['time_to_heading_5deg_s'])
        t30 = assess(rated(.7), .5 * top, Settings(duration_s=8., mode='speed', target_speed=.5 * top, turn_degrees=30, turn_time_s=2.))['time_to_heading_5deg_s']
        t90 = assess(rated(.7), .5 * top, Settings(duration_s=8., mode='speed', target_speed=.5 * top, turn_degrees=90, turn_time_s=2.))['time_to_heading_5deg_s']
        self.assertGreater(t90, t30)                                     # bigger cut takes longer

    def test_sharper_cut_loses_more_speed_and_needs_more_force(self):
        v = 15.
        r = {a: assess(rated(.7), v, Settings(duration_s=8., mode='speed', target_speed=v, turn_degrees=a, turn_time_s=2.)) for a in (30, 90)}
        self.assertLess(r[90]['min_speed_after_turn_m_s'], r[30]['min_speed_after_turn_m_s'])
        self.assertGreater(r[90]['peak_horizontal_force_N'], r[30]['peak_horizontal_force_N'])


class AcceptanceGates(unittest.TestCase):
    """(i) integrity gates on every scenario, (ii) gait gates at attainable speeds, (iii) stress only reported."""
    @classmethod
    def setUpClass(cls):
        cls.rows = []
        for p, s in gt.scenario_grid():
            row = gt.run_v31(p, s); cls.rows.append((p, s, row, gt.gates(row, p)))

    def test_integrity_gates_all_scenarios(self):
        for p, s, row, g in self.rows:
            bad = [k for k, v in g['results'].items() if k.startswith('I') and not v['passed']]
            self.assertEqual(bad, [], (p.label, s))

    def test_gait_gates_at_attainable_speeds(self):
        gait = [(p, s, g) for p, s, row, g in self.rows if g['tier'] == 'gait']
        self.assertEqual(len(gait), 12)
        for p, s, g in gait:
            self.assertTrue(g['passed_required'], (p.label, s, g['failed']))

    def test_stress_tier_is_classified_and_reported_not_required(self):
        stress = [(p, s, row) for p, s, row, g in self.rows if g['tier'] == 'stress']
        self.assertEqual(len(stress), 6)
        for p, s, row in stress:
            self.assertGreaterEqual(s, .9 * gt.declared_top(p))
            self.assertIn(row['reason'], ('', 'missed_touchdown', 'degenerate_gait', 'landing_travel_exceeded', 'overreach'))

    def test_from_rest_reaches_forty_percent_of_declared_top_in_six_seconds(self):
        for p, s, row, g in self.rows:
            if s == 0.:
                self.assertGreaterEqual(row['speed_end_m_s'], .4 * gt.declared_top(p), p.label)


class BaselineV30(unittest.TestCase):
    """What the shipped v3.0 does against the SAME gates (recorded, not tuned)."""
    @classmethod
    def setUpClass(cls):
        cls.rows = []
        for p, s in gt.scenario_grid():
            row = gt.run_v30(p, s); cls.rows.append((p, s, row, gt.gates(row, p)))

    def test_v30_integrity_gates_hold(self):
        for p, s, row, g in self.rows:
            self.assertTrue(all(v['passed'] for k, v in g['results'].items() if k.startswith('I')), (p.label, s))

    def test_v30_fails_gait_gates_at_attainable_speeds(self):
        gait = [g for p, s, row, g in self.rows if g['tier'] == 'gait']
        self.assertEqual(sum(g['passed_required'] for g in gait), 0)
        self.assertEqual(sum(1 for p, s, row, g in self.rows if g['tier'] == 'gait' and not row['upright']), 10)

    def test_v30_foot_speed_artifact_in_every_gait_row_of_keepers(self):
        for p, s, row, g in self.rows:
            if g['tier'] == 'gait' and 'keeper' in p.label:
                self.assertGreater(row['foot_over_body'], 1.9)

    @unittest.expectedFailure
    def test_INTENTIONAL_FAIL_v30_meets_gait_gates(self):
        for p, s, row, g in self.rows:
            if g['tier'] == 'gait': self.assertTrue(g['passed_required'], (p.label, s))


class DocumentedUnmet(unittest.TestCase):
    """Open problems recorded as expected failures (see the report's 'unresolved' list)."""

    @unittest.expectedFailure
    def test_OPEN_keeper_top_speed_stays_within_100mph_benchmark(self):
        # Longer legs give the Keeper ~7% more top speed at equal ratings.  Canon decision required; NOT silently clamped.
        self.assertLessEqual(sprint(rated(1.0, 'keeper'), 45.)['sustained_speed_m_s'], BENCHMARK_M_S)

    @unittest.expectedFailure
    def test_OPEN_gait_is_stable_without_the_effort_regulator(self):
        for rt in (.1, .3, .6):
            self.assertTrue(assess(rated(rt), 0., Settings(duration_s=20., regulate=False))['upright'], rt)

    @unittest.expectedFailure
    def test_OPEN_strict_leg_length_is_respected_at_touchdown_during_startup(self):
        # start-up strides reach 1.16x leg length (allowance reach_max_leg=1.2); strict anatomy would require <= 1.0x
        self.assertLessEqual(sprint(rated(.7), 10.)['max_leg_extension'], 1.0 + 1e-6)

    @unittest.expectedFailure
    def test_OPEN_balance_limited_cuts(self):
        # lean/balance is not modelled, so a 90 degree cut at 90% of top speed is (implausibly) feasible:
        top = sprint(rated(1.0))['sustained_speed_m_s']; v = .9 * top
        r = assess(rated(1.0), v, Settings(duration_s=8., mode='speed', target_speed=v, turn_degrees=90., turn_time_s=3.))
        self.assertFalse(r['upright'])


if __name__ == '__main__':
    unittest.main()
