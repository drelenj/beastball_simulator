"""Reproducible runner for Beastball v3.1.   Usage:  python run_beastball_v31.py [output_dir]   (default ./results_v31)

Everything is deterministic (no random numbers anywhere).  Writes CSV/JSON/plots plus a parameter manifest and a headline
summary that the technical report quotes verbatim.  Run time: roughly 3-6 minutes on one core.
"""
import csv, json, sys, hashlib, platform, collections, math
from dataclasses import asdict, replace
from pathlib import Path
import beastball_locomotion_v31 as m31
import beastball_unified_locomotion_v30 as m30
import beastball_gates_v31 as gt
from beastball_locomotion_v31 import Params, Settings, assess, derive, rated, BENCHMARK_M_S
from beastball_physical_standard_v11 import profile
from beastball_physical_standard_v1 import Athlete
from beastball_physical_standard_v11 import PerformanceProfile

ROOT = Path(__file__).resolve().parent
_ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
NO_PLOTS = '--no-plots' in sys.argv[1:]
OUT = Path(_ARGS[0]) if _ARGS else ROOT / 'results_v31'
OUT.mkdir(parents=True, exist_ok=True)
SUMMARY = {}


def write_csv(name, rows):
    rows = list(rows)
    keys = []
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    return rows


def write_json(name, obj):
    (OUT / name).write_text(json.dumps(obj, indent=1, default=str))


def custom(height, mass, strength=.7, explosive=.7, traction=.7, technique=.7, label=None):
    a = Athlete(height, mass, strength=strength, explosive_power=explosive, traction=traction, technique=technique)
    return PerformanceProfile(label or f'h{height:g}_m{mass:g}_s{strength:g}_e{explosive:g}', a, .7, .7, .7, .7)


def sustained(p, T=40., params=None, **settings):
    """Maximal-effort sprint from rest; result['sustained_speed_m_s'] is the mean ground speed over the last 8 strides."""
    r = assess(p, 0., Settings(duration_s=T, **settings), params=params)
    return r


def pct(a, b):
    return round(100 * (a - b) / b, 2) if b else None


# ---------------------------------------------------------------------------------------------------- 1. manifest
def manifest():
    files = sorted(ROOT.glob('beastball_*.py')) + [ROOT / 'run_beastball_v31.py']
    man = dict(
        module='beastball_locomotion_v31', benchmark_m_s=BENCHMARK_M_S,
        params=asdict(Params()), settings_defaults=asdict(Settings()),
        python=platform.python_version(), platform=platform.platform(),
        source_sha256={f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
        gate_thresholds=dict(ATTAINABLE_FRACTION=gt.ATTAINABLE_FRACTION, MIN_STEP_HZ=gt.MIN_STEP_HZ, MAX_STEP_HZ=gt.MAX_STEP_HZ,
                             FOOT_RATIO=gt.FOOT_RATIO, MAX_NORMAL_BW=gt.MAX_NORMAL_BW, REST_FRACTION=gt.REST_FRACTION,
                             SPEED_KEEP=gt.SPEED_KEEP, DURATION_S=gt.DURATION_S),
        calibration=dict(note='drive_N_per_kg (horizontal force scale) is the ONLY constant fitted to the 100 mph benchmark: '
                              'rating-1.0 field athlete, 45 s maximal sprint from rest, mean ground speed over the last 8 strides of the 45 s run = 44.70 m/s (sustained_speed_m_s).',
                         kappa0_note='kappa0=8 chosen so that the benchmark-rated athlete is thrust/drag-limited, not gait-limited '
                                     '(kappa0 8 and 9 give identical calibrated thrust).'),
        derived_capacities={})
    for tier in gt.TIERS:
        for role in gt.ROLES:
            p = profile(tier, role)
            man['derived_capacities'][p.label] = derive(p)
    for rt in (.2, .45, .7, 1.0):
        for role in gt.ROLES:
            p = rated(rt, role); man['derived_capacities'][p.label] = derive(p)
    write_json('v31_parameter_manifest.json', man)


# ---------------------------------------------------------------------------------------------------- 2. gates
def baseline_gates():
    rows = []
    for engine, run in (('v3.0', gt.run_v30), ('v3.1', gt.run_v31)):
        for p, s in gt.scenario_grid():
            row = run(p, s); g = gt.gates(row, p)
            row = dict(row)
            row.update(tier=g['tier'], declared_top_m_s=g['declared_top_m_s'], passed_required=g['passed_required'],
                       failed_gates=';'.join(g['failed']))
            for k, v in g['results'].items(): row[k] = 'PASS' if v['passed'] else 'FAIL'
            rows.append(row)
    write_csv('gates_v30_vs_v31_straight_6s.csv', rows)
    write_json('gates_v30_vs_v31_straight_6s.json', rows)
    summ = {}
    for eng in ('v3.0', 'v3.1'):
        rr = [r for r in rows if r['engine'] == eng]
        gait = [r for r in rr if r['tier'] == 'gait']; stress = [r for r in rr if r['tier'] == 'stress']
        gate_fail = collections.Counter(k for r in gait for k in r['failed_gates'].split(';') if k)
        summ[eng] = dict(scenarios=len(rr), gait_scenarios=len(gait), gait_passed=sum(r['passed_required'] for r in gait),
                         integrity_failures=sum(1 for r in rr if any(k.startswith('I') for k in r['failed_gates'].split(';'))),
                         stress_scenarios=len(stress), stress_upright=sum(1 for r in stress if r['upright']),
                         gait_gate_failures=dict(gate_fail),
                         failure_reasons=dict(collections.Counter(r['reason'] or 'upright' for r in rr)))
    SUMMARY['gates_6s_straight'] = summ


def grid_compare():
    """The shipped v3.0 81-trial grid (3 s runs, tiers x roles x speeds x {0,90 deg}, plus dt checks) on BOTH engines."""
    rows = []
    cases = [(t, r, s, a, .005) for t in gt.TIERS for r in gt.ROLES for s in (0, 10, 20, 30, 40, 44.704) for a in (0, 90)]
    cases += [('average', 'field', s, 90, dt) for dt in (.0025, .005, .01) for s in (10, 20, 40)]
    for t, r, s, a, dt in cases:
        p = profile(t, r)
        r0 = m30.assess(p, s, m30.Settings(turn_degrees=a, dt=dt))
        r1 = assess(p, s, Settings(turn_degrees=a, dt=dt, duration_s=3.))
        rows.append(dict(profile=p.label, start_speed=s, turn_degrees=a, dt=dt,
                         v30_upright=not r0['grounded'], v30_reason=r0['reason'] if r0['grounded'] else '', v30_elapsed_s=r0['elapsed_s'],
                         v30_landings=r0['landings'], v30_peak_normal_N=r0['peak_normal_N'], v30_peak_height_m=r0['peak_height_m'],
                         v31_upright=r1['upright'], v31_reason=r1['reason'], v31_elapsed_s=r1['elapsed_s'], v31_touchdowns=r1['touchdowns'],
                         v31_speed_end=r1['speed_end_m_s'], v31_peak_normal_N=r1['peak_normal_N'], v31_heading_end=r1['heading_end_deg']))
    write_csv('grid_v30_shipped_grid_vs_v31.csv', rows)
    SUMMARY['shipped_grid'] = dict(trials=len(rows),
                                   v30_upright=sum(r['v30_upright'] for r in rows),
                                   v30_outcomes=dict(collections.Counter('upright' if r['v30_upright'] else r['v30_reason'] for r in rows)),
                                   v31_upright=sum(r['v31_upright'] for r in rows),
                                   v31_outcomes=dict(collections.Counter('upright' if r['v31_upright'] else r['v31_reason'] for r in rows)))
    SUMMARY['shipped_grid']['v31_failures_by_start_speed'] = dict(collections.Counter(r['start_speed'] for r in rows if not r['v31_upright']))


# ---------------------------------------------------------------------------------------------------- 3. rating sweep
def rating_sweep():
    rows = []
    for role in gt.ROLES:
        for rt in (.05, .1, .2, .3, .45, .6, .7, .8, .92, 1.0):
            p = rated(rt, role)
            r = sustained(p, 40.)
            rows.append(dict(role=role, rating=rt, upright=r['upright'], reason=r['reason'], sustained_speed_m_s=r['sustained_speed_m_s'],
                             fraction_of_benchmark=round(r['sustained_speed_m_s'] / BENCHMARK_M_S, 4), speed_peak_m_s=r['speed_peak_m_s'],
                             exceeds_benchmark=r['exceeds_benchmark'], benchmark_exceedance_m_s=r['benchmark_exceedance_m_s'],
                             step_frequency_hz=r['step_frequency_hz'], step_length_m=r['step_length_m'], contact_time_s=r['contact_time_s'],
                             flight_time_s=r['flight_time_s'], duty_factor=r['duty_factor'], peak_normal_bw=r['peak_normal_bw'], kappa_cap_bw=r['kappa_cap_bw'],
                             peak_horizontal_force_bw=round(r['peak_horizontal_force_N'] / (p.athlete.mass_kg * m31.G), 3),
                             peak_grf_angle_deg=r['peak_grf_angle_deg'], touchdown_reach_mean_leg=r['touchdown_reach_mean_leg'], max_leg_extension=r['max_leg_extension'], min_leg_ratio=r['min_leg_ratio'], foot_peak_ground_speed_m_s=r['foot_peak_ground_speed_m_s'],
                             foot_peak_relative_speed_m_s=r['foot_peak_relative_speed_m_s'], swing_rel_speed_cap_m_s=r['swing_rel_speed_cap_m_s'],
                             positive_ground_work_J=r['positive_ground_work_J'], drag_work_J=r['drag_work_J'], energy_audit_rel=r['energy_audit_rel']))
    write_csv('v31_rating_sweep_sustained.csv', rows)
    f = {r['rating']: r for r in rows if r['role'] == 'field'}; k = {r['rating']: r for r in rows if r['role'] == 'keeper'}
    SUMMARY['rating_sweep'] = dict(field_rating_1_sustained=f[1.0]['sustained_speed_m_s'], keeper_rating_1_sustained=k[1.0]['sustained_speed_m_s'],
                                   keeper_exceeds_benchmark_by_m_s=round(k[1.0]['sustained_speed_m_s'] - BENCHMARK_M_S, 3),
                                   keeper_over_field_ratio_at_equal_rating={str(r): round(k[r]['sustained_speed_m_s'] / f[r]['sustained_speed_m_s'], 3) for r in f},
                                   all_upright=all(r['upright'] for r in rows),
                                   field_by_rating={str(r): f[r]['sustained_speed_m_s'] for r in f})


# ---------------------------------------------------------------------------------------------------- 4. sensitivity
def sensitivity():
    rows = []
    knobs = ['kappa0', 'rfd_s', 'swing_c', 'fv_froude', 'drive_N_per_kg', 'mu0', 'cd_area_per_h2', 'leg_length_height',
             'stance_time_c', 'sweep_max_leg', 'brake_N_per_kg', 'effort_smooth']
    base = Params()
    for rt in (.7, 1.0):
        p = rated(rt)
        b = sustained(p, 40.)
        rows.append(dict(rating=rt, knob='BASE', factor=1., upright=b['upright'], reason=b['reason'], sustained_speed_m_s=b['sustained_speed_m_s'], pct_vs_base=0.,
                         step_frequency_hz=b['step_frequency_hz'], peak_normal_bw=b['peak_normal_bw']))
        for kn in knobs:
            for fac in (.8, 1.25):
                v = getattr(base, kn) * fac
                if kn == 'effort_smooth': v = min(1., v)
                if kn == 'sweep_max_leg' and v >= .99: continue
                try:
                    q = replace(base, **{kn: v})
                    r = sustained(p, 40., params=q)
                except ValueError as e:
                    rows.append(dict(rating=rt, knob=kn, factor=fac, upright=False, reason=f'invalid:{e}')); continue
                rows.append(dict(rating=rt, knob=kn, factor=fac, upright=r['upright'], reason=r['reason'], sustained_speed_m_s=r['sustained_speed_m_s'],
                                 pct_vs_base=pct(r['sustained_speed_m_s'], b['sustained_speed_m_s']), step_frequency_hz=r['step_frequency_hz'],
                                 peak_normal_bw=r['peak_normal_bw']))
        for name, over, kw in (('regulator_off(ablation)', {}, dict(regulate=False)), ('util band .90/1.00', dict(util_lo=.9, util_hi=1.0), {}),
                               ('util band .80/.95', dict(util_lo=.8, util_hi=.95), {}), ('fill band .75/.90', dict(fill_lo=.75, fill_hi=.9), {})):
            r = sustained(p, 40., params=replace(base, **over), **kw)
            rows.append(dict(rating=rt, knob=name, factor=None, upright=r['upright'], reason=r['reason'], sustained_speed_m_s=r['sustained_speed_m_s'],
                             pct_vs_base=pct(r['sustained_speed_m_s'], b['sustained_speed_m_s']), step_frequency_hz=r['step_frequency_hz'],
                             peak_normal_bw=r['peak_normal_bw']))
        for tr in (.5, .75, 1.5):
            r = sustained(p, 40., traction=tr)
            rows.append(dict(rating=rt, knob='surface traction multiplier', factor=tr, upright=r['upright'], reason=r['reason'], sustained_speed_m_s=r['sustained_speed_m_s'],
                             pct_vs_base=pct(r['sustained_speed_m_s'], b['sustained_speed_m_s']), step_frequency_hz=r['step_frequency_hz'], peak_normal_bw=r['peak_normal_bw']))
    write_csv('v31_sensitivity.csv', rows)
    ok = [r for r in rows if r.get('pct_vs_base') is not None and r['knob'] != 'BASE']
    worst = sorted(ok, key=lambda r: -abs(r['pct_vs_base']))[:8]
    SUMMARY['sensitivity'] = dict(rows=len(rows), falls=sum(1 for r in rows if not r['upright']),
                                  largest_effects=[(r['rating'], r['knob'], r['factor'], r['pct_vs_base']) for r in worst])
    off = [r for r in rows if r['knob'] == 'regulator_off(ablation)']
    SUMMARY['regulator_ablation'] = [(r['rating'], r['upright'], r['reason'], r['sustained_speed_m_s']) for r in off]


def regulator_ablation_study():
    """Effort regulator is a controller ASSUMPTION; show what it does by switching it off (Settings.regulate=False)."""
    rows = []
    for rt in (.1, .2, .3, .45, .6, .7, .8, .92, 1.0):
        for role in gt.ROLES:
            p = rated(rt, role)
            on = sustained(p, 40.); off = sustained(p, 40., regulate=False)
            rows.append(dict(kind='sprint_from_rest_40s', role=role, rating=rt, on_upright=on['upright'], on_speed=on['sustained_speed_m_s'],
                             off_upright=off['upright'], off_reason=off['reason'], off_speed=off['sustained_speed_m_s'],
                             off_vs_on_pct=pct(off['sustained_speed_m_s'], on['sustained_speed_m_s']) if off['upright'] else None,
                             off_peak_normal_bw=off['peak_normal_bw'], kappa_cap_bw=off['kappa_cap_bw']))
    gate_rows = []
    for p, s in gt.scenario_grid():
        row = gt.run_v31(p, s, regulate=False); g = gt.gates(row, p)
        gate_rows.append(dict(kind='gate_6s', profile=p.label, start=s, tier=g['tier'], upright=row['upright'], reason=row['reason'],
                              passed_required=g['passed_required'], failed=';'.join(g['failed']), speed_end=row['speed_end_m_s']))
    write_csv('v31_regulator_ablation.csv', rows + gate_rows)
    gait = [r for r in gate_rows if r['tier'] == 'gait']
    SUMMARY['regulator_ablation_study'] = dict(
        sprint_falls_without_regulator=[(r['role'], r['rating'], r['off_reason']) for r in rows if not r['off_upright']],
        sprint_runs=len(rows), gait_gate_pass_without_regulator=f"{sum(r['passed_required'] for r in gait)}/{len(gait)}",
        speed_gain_pct_without_regulator={f"{r['role']}_{r['rating']}": r['off_vs_on_pct'] for r in rows if r['off_vs_on_pct'] is not None})


# ---------------------------------------------------------------------------------------------------- 5. convergence
def convergence():
    rows = []
    for rt in (.45, .7, 1.0):
        for dt in (.0025, .005, .01, .02):
            r = sustained(rated(rt), 30., dt=dt)
            rows.append(dict(scenario=f'sprint r={rt} 30 s', dt=dt, upright=r['upright'], sustained_speed_m_s=r['sustained_speed_m_s'], x_m=r['x_m'],
                             energy_audit_rel=r['energy_audit_rel'], step_frequency_hz=r['step_frequency_hz'], touchdowns=r['touchdowns']))
    p = rated(.7)
    for dt in (.0025, .005, .01, .02):
        r = assess(p, 15., Settings(dt=dt, duration_s=8., mode='speed', target_speed=15., turn_degrees=90., turn_time_s=2.))
        rows.append(dict(scenario='cut 90deg r=0.7 from 15 m/s', dt=dt, upright=r['upright'], sustained_speed_m_s=r['min_speed_after_turn_m_s'], x_m=r['x_m'],
                         energy_audit_rel=r['energy_audit_rel'], step_frequency_hz=r['step_frequency_hz'], touchdowns=r['touchdowns'],
                         time_to_heading_5deg_s=r['time_to_heading_5deg_s']))
    write_csv('v31_timestep_convergence.csv', rows)
    spread = {}
    for sc in sorted({r['scenario'] for r in rows}):
        v = [r['sustained_speed_m_s'] for r in rows if r['scenario'] == sc]
        spread[sc] = round(100 * (max(v) - min(v)) / (sum(v) / len(v)), 3)
    SUMMARY['convergence_spread_percent_dt_0.0025_to_0.02'] = spread
    SUMMARY['max_energy_audit_rel'] = max(r['energy_audit_rel'] for r in rows)


# ---------------------------------------------------------------------------------------------------- 6. strength / explosive / mass
def anatomy():
    rows = []
    for st in (.2, .7, 1.0):
        for ex in (.2, .7, 1.0):
            p = custom(2.54, 180., strength=st, explosive=ex, label=f's{st}_e{ex}')
            r = sustained(p, 40.)
            h = assess(p, 10., Settings(duration_s=6., mode='speed', target_speed=10.), trace=True, sample_dt=.005)
            res, tr = h
            late = [t['z'] for t in tr if t['t'] > 3.]
            rows.append(dict(strength=st, explosive=ex, mass_kg=180., upright=r['upright'], sustained_speed_m_s=r['sustained_speed_m_s'],
                             peak_normal_bw_at_top=r['peak_normal_bw'], kappa_cap_bw=r['kappa_cap_bw'], step_frequency_hz=r['step_frequency_hz'],
                             flight_time_s=r['flight_time_s'], contact_time_s=r['contact_time_s'], swing_rel_speed_cap_m_s=r['swing_rel_speed_cap_m_s'],
                             fv_zero_force_speed_m_s=r['fv_zero_force_speed_m_s'], peak_normal_bw_10ms=res['peak_normal_bw'],
                             com_vertical_excursion_10ms_m=round(max(late) - min(late), 4) if late else None,
                             flight_time_10ms_s=res['flight_time_s']))
    write_csv('v31_strength_x_explosive_same_mass.csv', rows)
    SUMMARY['strength_explosive_grid'] = dict(
        sustained_speed_unique=len({r['sustained_speed_m_s'] for r in rows}), peak_normal_unique=len({r['peak_normal_bw_10ms'] for r in rows}),
        excursion_unique=len({r['com_vertical_excursion_10ms_m'] for r in rows}),
        vary_strength_only={str(r['strength']): r['sustained_speed_m_s'] for r in rows if r['explosive'] == .7},
        vary_explosive_only={str(r['explosive']): r['sustained_speed_m_s'] for r in rows if r['strength'] == .7})
    mrows = []
    for h in (2.0, 2.54, 3.2004):
        for ms in (120., 180., 300.):
            p = custom(h, ms, label=f'h{h:g}_m{ms:g}')
            r = sustained(p, 40.)
            mrows.append(dict(height_m=h, mass_kg=ms, upright=r['upright'], sustained_speed_m_s=r['sustained_speed_m_s'], leg_length_m=round(.53 * h, 4),
                              peak_normal_bw=r['peak_normal_bw'], step_frequency_hz=r['step_frequency_hz'], step_length_m=r['step_length_m']))
    write_csv('v31_height_mass_sweep.csv', mrows)
    fx = {(r['height_m'], r['mass_kg']): r['sustained_speed_m_s'] for r in mrows}
    SUMMARY['height_mass'] = dict(same_height_mass_effect_percent={str(h): pct(fx[(h, 300.)], fx[(h, 120.)]) for h in (2.0, 2.54, 3.2004)},
                                  same_mass_height_effect_percent={str(ms): pct(fx[(3.2004, ms)], fx[(2.0, ms)]) for ms in (120., 180., 300.)})


# ---------------------------------------------------------------------------------------------------- 7. acceleration, stress, cuts
def acceleration():
    rows = []
    for t in gt.TIERS:
        for r in gt.ROLES:
            p = profile(t, r)
            res, tr = assess(p, 0., Settings(duration_s=15.), trace=True, sample_dt=.01)
            top = res['sustained_speed_m_s']
            def t_to(v):
                for x in tr:
                    if x['speed'] >= v: return x['t']
            rows.append(dict(profile=p.label, upright=res['upright'], t_to_10ms=t_to(10), t_to_20ms=t_to(20), t_to_50pct_of_15s_speed=t_to(.5 * top),
                             speed_at_6s=next((x['speed'] for x in tr if x['t'] >= 6.), None), speed_at_15s=res['speed_end_m_s'],
                             peak_horizontal_force_bw=round(res['peak_horizontal_force_N'] / (p.athlete.mass_kg * m31.G), 3)))
    write_csv('v31_acceleration_from_rest.csv', rows)
    SUMMARY['acceleration'] = rows


def stress():
    rows = []
    for rt in (.3, .45, .7, .92, 1.0):
        p = rated(rt)
        top = sustained(p, 40.)['sustained_speed_m_s']
        for mult in (.9, 1.0, 1.25, 1.5, 2.0):
            v = mult * top
            r = assess(p, v, Settings(duration_s=6.))
            rows.append(dict(rating=rt, own_top_speed=top, imparted_start_multiple=mult, imparted_start_m_s=round(v, 2), upright=r['upright'], reason=r['reason'],
                             elapsed_s=r['elapsed_s'], speed_end_m_s=r['speed_end_m_s'], exceeds_benchmark=r['exceeds_benchmark'],
                             benchmark_exceedance_m_s=r['benchmark_exceedance_m_s'], note='externally imparted velocity, not self-propelled'))
    # self-propelled exceedance
    p = rated(1.0, 'keeper'); r = sustained(p, 40.)
    rows.append(dict(rating=1.0, own_top_speed=r['sustained_speed_m_s'], imparted_start_multiple=0, imparted_start_m_s=0, upright=r['upright'], reason=r['reason'],
                     elapsed_s=r['elapsed_s'], speed_end_m_s=r['speed_end_m_s'], exceeds_benchmark=r['exceeds_benchmark'],
                     benchmark_exceedance_m_s=r['benchmark_exceedance_m_s'], note='KEEPER rating 1.0, self-propelled from rest (benchmark exceedance, diagnosed in report)'))
    write_csv('v31_stress_imparted_speed.csv', rows)
    SUMMARY['stress_imparted'] = dict(
        upright_by_multiple={str(mu): sum(1 for r in rows if r['imparted_start_multiple'] == mu and r['upright']) for mu in (.9, 1.0, 1.25, 1.5, 2.0)},
        total_by_multiple=5)


def cuts():
    rows = []
    for rt in (.45, .7, 1.0):
        top = sustained(rated(rt), 40.)['sustained_speed_m_s']
        for frac in (.25, .5, .75, .9):
            v = frac * top
            for ang in (30, 45, 90):
                p = rated(rt)
                r = assess(p, v, Settings(duration_s=8., mode='speed', target_speed=v, turn_degrees=ang, turn_time_s=3.))
                rows.append(dict(rating=rt, own_top_speed=round(top, 2), entry_speed_frac_of_top=frac, entry_speed_m_s=round(v, 2), cut_degrees=ang,
                                 upright=r['upright'], reason=r['reason'], speed_at_turn=r['speed_at_turn_m_s'], min_speed_after_turn=r['min_speed_after_turn_m_s'],
                                 speed_retained_pct=round(100 * r['min_speed_after_turn_m_s'] / r['speed_at_turn_m_s'], 1) if r['min_speed_after_turn_m_s'] else None,
                                 time_to_heading_5deg_s=r['time_to_heading_5deg_s'], heading_end_deg=r['heading_end_deg'],
                                 peak_horizontal_force_bw=round(r['peak_horizontal_force_N'] / (p.athlete.mass_kg * m31.G), 3), peak_normal_bw=r['peak_normal_bw'],
                                 slip_impulse_Ns=r['slip_impulse_Ns'], peak_grf_angle_deg=r['peak_grf_angle_deg']))
    write_csv('v31_cuts.csv', rows)
    SUMMARY['cuts'] = dict(trials=len(rows), upright=sum(r['upright'] for r in rows),
                           failures=[(r['rating'], r['entry_speed_frac_of_top'], r['cut_degrees'], r['reason']) for r in rows if not r['upright']],
                           note='balance/lean is not modelled: cut feasibility here is limited only by leg force capacity, friction cone and foot placement')


# ---------------------------------------------------------------------------------------------------- 8. traces + plots
def traces_and_plots(plots=True):
    for name, p, v0, T, kw in (('average_field_from_rest_6s', profile('average', 'field'), 0., 6., {}),
                               ('rating1_field_sprint_20s', rated(1.0), 0., 20., {}),
                               ('rating07_field_cut90_from_15ms', rated(.7), 15., 8., dict(mode='speed', target_speed=15., turn_degrees=90., turn_time_s=2.))):
        r, tr = assess(p, v0, Settings(duration_s=T, **kw), trace=True, sample_dt=.005)
        write_csv(f'trace_v31_{name}.csv', tr)
    r, tr = m30.assess(profile('average', 'field'), 0., m30.Settings(duration_s=6.), trace=True)
    write_csv('trace_v30_average_field_from_rest.csv', tr)
    if not plots:
        SUMMARY['plots'] = 'skipped (--no-plots)'; return
    try:
        import matplotlib; matplotlib.use('Agg')
        import matplotlib.pyplot as plt
    except Exception as e:
        SUMMARY['plots'] = f'skipped: {e}'; return
    fig, ax = plt.subplots(1, 3, figsize=(16, 4.4))
    cols = {'developing': '#2a9d8f', 'average': '#e9a23b', 'exceptional': '#c8412b'}
    for t in gt.TIERS:
        for rl, ls in (('field', '-'), ('keeper', '--')):
            p = profile(t, rl)
            r1, tr1 = assess(p, 0., Settings(duration_s=6.), trace=True, sample_dt=.02)
            ax[0].plot([x['t'] for x in tr1], [x['speed'] for x in tr1], ls, color=cols[t], label=f'v3.1 {t} {rl}')
            r0, tr0 = m30.assess(p, 0., m30.Settings(duration_s=6.), trace=True)
            ax[0].plot([x['t'] for x in tr0], [math.hypot(x['vx'], x['vy']) for x in tr0], ':', color=cols[t], alpha=.8)
    ax[0].axhline(BENCHMARK_M_S, color='k', lw=.8); ax[0].text(.1, BENCHMARK_M_S + .6, '100 mph benchmark', fontsize=8)
    ax[0].set(xlabel='time (s)', ylabel='speed (m/s)', title='From rest: v3.1 (solid/dashed) vs v3.0 (dotted, ends at fall)'); ax[0].legend(fontsize=6, ncol=2)
    rs = list(csv.DictReader((OUT / 'v31_rating_sweep_sustained.csv').open()))
    for role, c in (('field', '#2a6fdb'), ('keeper', '#c8412b')):
        xs = [float(r['rating']) for r in rs if r['role'] == role]; ys = [float(r['sustained_speed_m_s']) for r in rs if r['role'] == role]
        ax[1].plot(xs, ys, 'o-', color=c, label=role)
    ax[1].axhline(BENCHMARK_M_S, color='k', lw=.8); ax[1].set(xlabel='rating (all four set equal)', ylabel='sustained speed (m/s)', title='Emergent top speed vs rating'); ax[1].legend()
    r, tr = assess(rated(.7), 0., Settings(duration_s=12.), trace=True, sample_dt=.002)
    seg = [x for x in tr if 10. <= x['t'] <= 11.]
    ax[2].plot([x['t'] for x in seg], [x['N'] / (180 * m31.G) for x in seg], color='#2a6fdb', label='normal force (BW)')
    ax2 = ax[2].twinx(); ax2.plot([x['t'] for x in seg], [x['z'] for x in seg], color='#e9a23b', label='COM height (m)')
    ax[2].set(xlabel='time (s)', ylabel='normal force (BW)', title='Rating 0.7 field, steady stride (1 s)'); ax2.set_ylabel('COM height (m)')
    fig.tight_layout(); fig.savefig(OUT / 'plot_speed_rating_stride.png', dpi=130); plt.close(fig)
    SUMMARY['plots'] = ['plot_speed_rating_stride.png']


def main():
    """Numeric studies first; the summary is written BEFORE the (slowest, optional) trace/plot stage so a timeout there
    cannot lose the headline numbers.  `--no-plots` skips matplotlib entirely."""
    import time
    t0 = time.time()
    manifest()
    steps = (baseline_gates, grid_compare, rating_sweep, sensitivity, regulator_ablation_study, convergence, anatomy, acceleration, stress, cuts)
    for f in steps:
        print(f'running {f.__name__} (t={time.time() - t0:.1f}s)', flush=True)
        f()
    write_json('v31_summary.json', SUMMARY)
    print(f'summary written (t={time.time() - t0:.1f}s)', flush=True)
    traces_and_plots(plots=not NO_PLOTS)
    write_json('v31_summary.json', SUMMARY)
    print(f'done (t={time.time() - t0:.1f}s)')


if __name__ == '__main__':
    main()
