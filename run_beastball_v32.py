"""Reproducible runner for Beastball v3.2.   Usage:  python run_beastball_v32.py [output_dir] [--no-plots]   (default ./results_v32)

Deterministic (no random numbers anywhere).  Writes CSV/JSON/plots plus a parameter manifest and a headline summary
(summary_v32.json) that the technical report quotes.  v3.1 is imported unchanged and used as the baseline.
"""
import csv, json, sys, hashlib, platform, collections, math, time
from dataclasses import asdict
from pathlib import Path
import beastball_locomotion_v31 as m31
import beastball_locomotion_v32 as m32
import beastball_gates_v31 as gt31
import beastball_gates_v32 as gt
from beastball_locomotion_v32 import Params, Settings, assess, derive, rated, BENCHMARK_M_S
from beastball_physical_standard_v11 import profile, Dynamics, PerformanceProfile
from beastball_physical_standard_v1 import Athlete

ROOT = Path(__file__).resolve().parent
_ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
NO_PLOTS = '--no-plots' in sys.argv[1:]
OUT = Path(_ARGS[0]) if _ARGS else ROOT / 'results_v32'
OUT.mkdir(parents=True, exist_ok=True)
SUMMARY = {}
DYN = Dynamics()
MPH = 0.44704
RATINGS = (.05, .1, .2, .3, .45, .6, .7, .8, .92, 1.0)


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


def custom(height, mass, rating=.7, label=None):
    a = Athlete(height, mass, strength=rating, explosive_power=rating, traction=rating, technique=rating)
    return PerformanceProfile(label or f'h{height:g}_m{mass:g}_r{rating:g}', a, min(1., rating), rating, rating, rating)


def pct(a, b):
    return round(100 * (a - b) / b, 3) if b else None


def sprint(p, T=16., engine=m32, **kw):
    return engine.assess(p, 0., engine.Settings(duration_s=T, **kw))


def timed(name, fn):
    t = time.time(); fn(); print(f'  {name}: {time.time() - t:.1f} s', flush=True)


# ------------------------------------------------------------------------------------------------ 1. manifest
def manifest():
    files = sorted(ROOT.glob('beastball_*.py')) + [ROOT / 'run_beastball_v32.py']
    man = dict(module='beastball_locomotion_v32', benchmark_m_s=BENCHMARK_M_S, params=asdict(Params()), settings_defaults=asdict(Settings()),
               python=platform.python_version(), platform=platform.platform(),
               source_sha256={f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files},
               gate_thresholds=dict(ATTAINABLE_FRACTION=gt.ATTAINABLE_FRACTION, MIN_STEP_HZ=gt.MIN_STEP_HZ, MAX_STEP_HZ=gt.MAX_STEP_HZ,
                                    FOOT_RATIO=gt.FOOT_RATIO, MAX_NORMAL_BW=gt.MAX_NORMAL_BW, REST_FRACTION=gt.REST_FRACTION,
                                    SPEED_KEEP=gt.SPEED_KEEP, DURATION_S=gt.DURATION_S),
               calibration=dict(note='drive_N_per_kg is the ONLY constant fitted to the 100 mph canon: rating-1.0 field athlete, 16 s maximal sprint '
                                     'from rest, mean ground speed over the last 8 strides = 44.704 m/s (compliant-leg contact, posture limit on).'),
               derived_capacities={})
    for tier in gt.TIERS:
        for role in gt.ROLES:
            p = profile(tier, role); man['derived_capacities'][p.label] = derive(p)
    for rt in (.2, .45, .7, 1.0):
        for role in gt.ROLES:
            p = rated(rt, role); man['derived_capacities'][p.label] = derive(p)
    write_json('v32_parameter_manifest.json', man)


# ------------------------------------------------------------------------------------------------ 2. gates v3.1 vs v3.2
def baseline_gates():
    rows = []
    for engine, run, gmod in (('v3.1', gt31.run_v31, gt31), ('v3.2', gt.run_v31, gt)):
        for p, s in gmod.scenario_grid():
            row = run(p, s); g = gmod.gates(row, p)
            row = dict(row); row['engine'] = engine
            row.update(tier=g['tier'], declared_top_m_s=g['declared_top_m_s'], passed_required=g['passed_required'], failed_gates=';'.join(g['failed']))
            for k, v in g['results'].items(): row[k] = 'PASS' if v['passed'] else 'FAIL'
            rows.append(row)
    write_csv('gates_v31_vs_v32_straight_6s.csv', rows)
    summ = {}
    for eng in ('v3.1', 'v3.2'):
        rr = [r for r in rows if r['engine'] == eng]
        gait = [r for r in rr if r['tier'] == 'gait']; stress = [r for r in rr if r['tier'] == 'stress']
        summ[eng] = dict(scenarios=len(rr), gait_scenarios=len(gait), gait_passed=sum(r['passed_required'] for r in gait),
                         integrity_failures=sum(1 for r in rr if any(k.startswith('I') for k in r['failed_gates'].split(';'))),
                         stress_scenarios=len(stress), stress_upright=sum(1 for r in stress if r['upright']),
                         gait_gate_failures=dict(collections.Counter(k for r in gait for k in r['failed_gates'].split(';') if k)))
    SUMMARY['gates_6s_straight'] = summ


# ------------------------------------------------------------------------------------------------ 3. rating -> top speed (ABSOLUTE)
def rating_sweep():
    rows = []
    for role in gt.ROLES:
        for rt in RATINGS:
            p = rated(rt, role)
            for contact in ('spring', 'halfsine'):
                r = sprint(p, contact=contact)
                rows.append(dict(engine='v3.2', contact=contact, role=role, rating=rt, upright=r['upright'], reason=r['reason'],
                                 sustained_m_s=r['sustained_speed_m_s'], sustained_mph=round(r['sustained_speed_m_s'] / MPH, 2),
                                 peak_m_s=r['speed_peak_m_s'], declared_v11_m_s=round(DYN.top_speed(p), 3),
                                 step_hz=r['step_frequency_hz'], contact_s=r['contact_time_s'], flight_s=r['flight_time_s'],
                                 step_length_m=r['step_length_m'], peak_N_bw=r['peak_normal_bw'], max_leg_extension=r['max_leg_extension'],
                                 mean_touchdown_reach=r['touchdown_reach_mean_leg'], leg_stiffness_N_m=r.get('leg_stiffness_N_m'),
                                 leg_natural_freq_hz=r.get('leg_natural_freq_hz'), peak_leg_compression_m=r.get('peak_leg_compression_m'),
                                 energy_audit_rel=r['energy_audit_rel']))
            r1 = sprint(p, T=40., engine=m31)
            rows.append(dict(engine='v3.1', contact='halfsine', role=role, rating=rt, upright=r1['upright'], reason=r1['reason'],
                             sustained_m_s=r1['sustained_speed_m_s'], sustained_mph=round(r1['sustained_speed_m_s'] / MPH, 2), peak_m_s=r1['speed_peak_m_s'],
                             declared_v11_m_s=round(DYN.top_speed(p), 3), step_hz=r1['step_frequency_hz'], contact_s=r1['contact_time_s'],
                             flight_s=r1['flight_time_s'], step_length_m=r1['step_length_m'], peak_N_bw=r1['peak_normal_bw'],
                             max_leg_extension=r1['max_leg_extension'], mean_touchdown_reach=r1['touchdown_reach_mean_leg'], energy_audit_rel=r1['energy_audit_rel']))
    write_csv('rating_sweep.csv', rows)
    ok = [r for r in rows if r['engine'] == 'v3.2' and r['contact'] == 'spring']
    field = {r['rating']: r for r in ok if r['role'] == 'field'}
    keeper = {r['rating']: r for r in ok if r['role'] == 'keeper'}
    kf = {rt: pct(keeper[rt]['sustained_m_s'], field[rt]['sustained_m_s']) for rt in RATINGS if keeper[rt]['upright'] and field[rt]['upright']}
    k31 = {}
    for rt in RATINGS:
        a = [r for r in rows if r['engine'] == 'v3.1' and r['rating'] == rt]
        if len(a) == 2 and all(x['upright'] for x in a):
            k31[rt] = pct([x for x in a if x['role'] == 'keeper'][0]['sustained_m_s'], [x for x in a if x['role'] == 'field'][0]['sustained_m_s'])
    SUMMARY['rating_sweep'] = dict(
        spring_field_mph={rt: field[rt]['sustained_mph'] for rt in RATINGS}, spring_field_upright={rt: field[rt]['upright'] for rt in RATINGS},
        spring_keeper_upright={rt: keeper[rt]['upright'] for rt in RATINGS},
        keeper_minus_field_pct_v32=kf, keeper_minus_field_pct_v31=k31,
        rating_1_field_m_s=field[1.0]['sustained_m_s'], rating_1_keeper_m_s=keeper[1.0]['sustained_m_s'],
        spring_vs_halfsine_pct={rt: pct(field[rt]['sustained_m_s'], [r for r in rows if r['engine'] == 'v3.2' and r['contact'] == 'halfsine' and r['role'] == 'field' and r['rating'] == rt][0]['sustained_m_s'])
                                for rt in RATINGS if field[rt]['upright']},
        max_leg_extension_all_spring=max(r['max_leg_extension'] for r in ok if r['upright']),
        max_peak_N_bw=max(r['peak_N_bw'] for r in ok if r['upright']))


def absolute_rating():
    """Same ratings, different bodies: top speed must not depend on height, mass, or role (ruling).  v3.1 shown for contrast."""
    rows = []
    for rt in (.45, .7, 1.0):
        for engine, eng in (('v3.2', m32), ('v3.1', m31)):
            for h in (2.0, 2.4, 2.54, 2.9, 3.2004, 3.6):
                for mass in (120., 180., 300., 420.):
                    p = custom(h, mass, rt)
                    try:
                        r = eng.assess(p, 0., eng.Settings(duration_s=16 if engine == 'v3.2' else 40))
                    except Exception as e:
                        rows.append(dict(engine=engine, rating=rt, height_m=h, mass_kg=mass, upright=False, reason=type(e).__name__)); continue
                    rows.append(dict(engine=engine, rating=rt, height_m=h, mass_kg=mass, upright=r['upright'], reason=r['reason'],
                                     sustained_m_s=r['sustained_speed_m_s'], peak_N_bw=r['peak_normal_bw'], max_leg_extension=r['max_leg_extension']))
    write_csv('absolute_rating_height_mass.csv', rows)
    out = {}
    for engine in ('v3.2', 'v3.1'):
        for rt in (.45, .7, 1.0):
            v = [r['sustained_m_s'] for r in rows if r['engine'] == engine and r['rating'] == rt and r.get('upright')]
            n = sum(1 for r in rows if r['engine'] == engine and r['rating'] == rt)
            out[f'{engine}_r{rt:g}'] = dict(runs=n, upright=len(v), min=round(min(v), 3) if v else None, max=round(max(v), 3) if v else None,
                                            spread_pct=round(100 * (max(v) - min(v)) / min(v), 3) if v else None)
    SUMMARY['absolute_rating'] = out


# ------------------------------------------------------------------------------------------------ 4. acceleration (separate from sustainable running)
def acceleration():
    rows = []
    for role in gt.ROLES:
        for rt in (.3, .5, .7, 1.0):
            p = rated(rt, role)
            for engine, eng, T in (('v3.2', m32, 16), ('v3.1', m31, 16)):
                r, tr = eng.assess(p, 0., eng.Settings(duration_s=T), trace=True, sample_dt=.005)
                top = r['sustained_speed_m_s']
                v = [math.hypot(a['vx'], a['vy']) for a in tr]; t = [a['t'] for a in tr]; x = [a['x'] for a in tr]
                def t_at(target):
                    for i in range(1, len(v)):
                        if v[i] >= target > v[i - 1]:
                            return round(t[i - 1] + (t[i] - t[i - 1]) * (target - v[i - 1]) / (v[i] - v[i - 1] + 1e-12), 3)
                    return None
                def t_dist(d):
                    for i in range(1, len(x)):
                        if x[i] >= d > x[i - 1]:
                            return round(t[i - 1] + (t[i] - t[i - 1]) * (d - x[i - 1]) / (x[i] - x[i - 1] + 1e-12), 3)
                    return None
                # stride-scale acceleration: 0.25 s windows
                w = 50
                amax = max(((v[i + w] - v[i]) / (t[i + w] - t[i]) for i in range(0, len(v) - w)), default=0.)
                dec = {}
                for f in (.25, .5, .75, .9):
                    dec[f't_to_{int(f * 100)}pct_top_s'] = t_at(f * top)
                rows.append(dict(engine=engine, role=role, rating=rt, top_m_s=top, peak_stride_accel_m_s2=round(amax, 2),
                                 t10m_s=t_dist(10.), t20m_s=t_dist(20.), t40yd_s=t_dist(36.576), t100m_s=t_dist(100.),
                                 t_to_10_m_s=t_at(10.), t_to_20_m_s=t_at(20.), t_to_30_m_s=t_at(30.), t_to_40_m_s=t_at(40.),
                                 v11_time_to_90pct_top_s=round(DYN.time_to_speed(p, .9 * DYN.top_speed(p)), 3),
                                 v11_drive_accel_m_s2=round(DYN.drive_accel(p), 2), **dec))
    write_csv('acceleration_benchmarks.csv', rows)
    SUMMARY['acceleration'] = dict(
        v32_field_r1=[r for r in rows if r['engine'] == 'v3.2' and r['role'] == 'field' and r['rating'] == 1.0][0],
        v31_field_r1=[r for r in rows if r['engine'] == 'v3.1' and r['role'] == 'field' and r['rating'] == 1.0][0],
        standard_peak_accel_m_s2=m32.STD.peak_acceleration_m_s2)


def sustainable_running():
    """Max-effort (sprint) vs gait-envelope (sustainable) speeds, and the 'speed' mode tracking fixed fractions of top speed."""
    rows = []
    for rt in (.3, .5, .7, 1.0):
        p = rated(rt)
        sim = m32.Sim(p, Settings())
        top = sprint(p)['sustained_speed_m_s']
        row = dict(rating=rt, sprint_top_m_s=top, envelope_cruise_m_s=round(sim.v_env_lo, 3), envelope_sprint_m_s=round(sim.v_env_hi, 3),
                   cruise_over_top=round(sim.v_env_lo / top, 4))
        for f in (.5, .7, .9):
            r = m32.assess(p, 0., Settings(duration_s=20., mode='speed', target_speed=f * top))
            row[f'speed_mode_{int(f * 100)}pct_reached_m_s'] = r['sustained_speed_m_s']
            row[f'speed_mode_{int(f * 100)}pct_upright'] = r['upright']
            row[f'speed_mode_{int(f * 100)}pct_peak_N_bw'] = r['peak_normal_bw']
        rows.append(row)
    write_csv('sustainable_vs_maximal.csv', rows)
    SUMMARY['sustainable_running'] = rows


# ------------------------------------------------------------------------------------------------ 5. controller + contact ablations
def controller_and_contact_ablation():
    rows = []
    cases = [(rt, h) for rt in (.1, .2, .3, .45, .6, .7, .9, 1.0) for h in (2.0, 2.54, 3.2004, 3.6)]
    for contact in ('spring', 'halfsine'):
        for ctrl, reg in (('envelope', True), ('heuristic', True), ('none (unregulated)', False)):
            for rt, h in cases:
                mass = 180. if h < 3 else 300.
                p = custom(h, mass, rt)
                kw = dict(contact=contact, regulate=reg, controller='heuristic' if ctrl == 'heuristic' else 'envelope')
                try:
                    r = sprint(p, **kw)
                    rows.append(dict(contact=contact, controller=ctrl, rating=rt, height_m=h, mass_kg=mass, upright=r['upright'], reason=r['reason'],
                                     sustained_m_s=r['sustained_speed_m_s'], peak_N_bw=r['peak_normal_bw'], max_leg_extension=r['max_leg_extension']))
                except Exception as e:
                    rows.append(dict(contact=contact, controller=ctrl, rating=rt, height_m=h, mass_kg=mass, upright=False, reason=type(e).__name__))
    write_csv('ablation_controller_contact.csv', rows)
    s = {}
    for contact in ('spring', 'halfsine'):
        for ctrl in ('envelope', 'heuristic', 'none (unregulated)'):
            rr = [r for r in rows if r['contact'] == contact and r['controller'] == ctrl]
            up = [r for r in rr if r['upright']]
            s[f'{contact}/{ctrl}'] = dict(trials=len(rr), upright=len(up), reasons=dict(collections.Counter(r['reason'] for r in rr if not r['upright'])))
    # rating-only check of the envelope controller: spread at each rating across heights
    sp = {}
    for rt in (.3, .7, 1.0):
        v = [r['sustained_m_s'] for r in rows if r['contact'] == 'spring' and r['controller'] == 'envelope' and r['rating'] == rt and r['upright']]
        sp[rt] = round(100 * (max(v) - min(v)) / min(v), 3) if v else None
    s['spring_envelope_speed_spread_pct_across_heights'] = sp
    SUMMARY['ablation'] = s



def tracking():
    """Sub-maximal 'speed' mode over a range of absolute targets (jogging to running) for both contact models and v3.1."""
    rows = []
    for rt in (.3, 1.0):
        p = rated(rt)
        for tgt in (2., 3., 4., 6., 8., 10., 12., 15., 20.):
            for engine, eng, kw in (('v3.2 spring', m32, dict(contact='spring')), ('v3.2 halfsine', m32, dict(contact='halfsine')), ('v3.1', m31, {})):
                r = eng.assess(p, 0., eng.Settings(duration_s=20., mode='speed', target_speed=tgt, **kw))
                rows.append(dict(rating=rt, target_m_s=tgt, engine=engine, upright=r['upright'], reason=r['reason'], reached_m_s=r['sustained_speed_m_s'],
                                 reached_over_target=round(r['sustained_speed_m_s'] / tgt, 3), peak_N_bw=r['peak_normal_bw']))
    write_csv('speed_tracking.csv', rows)
    s = {}
    for engine in ('v3.2 spring', 'v3.2 halfsine', 'v3.1'):
        rr = [r for r in rows if r['engine'] == engine]
        up = [r for r in rr if r['upright']]
        s[engine] = dict(trials=len(rr), upright=len(up), failed_targets=sorted({(r['rating'], r['target_m_s']) for r in rr if not r['upright']}),
                         mean_reached_over_target=round(sum(r['reached_over_target'] for r in up) / max(1, len(up)), 3))
    SUMMARY['speed_tracking'] = s

# ------------------------------------------------------------------------------------------------ 6. convergence
def convergence():
    rows = []
    for rt in (.45, 1.0):
        for role in gt.ROLES:
            p = rated(rt, role)
            ref = None
            for dt, sub in ((.005, .001), (.0025, .001), (.001, .001), (.005, .0005), (.005, .002)):
                r = m32.assess(p, 0., Settings(duration_s=16, dt=dt), params=Params(spring_substep_s=sub))
                rows.append(dict(rating=rt, role=role, dt=dt, spring_substep_s=sub, upright=r['upright'], sustained_m_s=r['sustained_speed_m_s'],
                                 step_hz=r['step_frequency_hz'], peak_N_bw=r['peak_normal_bw'], audit=r['energy_audit_rel']))
    write_csv('convergence.csv', rows)
    ok = [r for r in rows if r['upright']]
    base = {(r['rating'], r['role']): r['sustained_m_s'] for r in rows if r['dt'] == .005 and r['spring_substep_s'] == .001}
    dev = max(abs(r['sustained_m_s'] - base[(r['rating'], r['role'])]) / base[(r['rating'], r['role'])] * 100 for r in ok)
    SUMMARY['convergence'] = dict(runs=len(rows), upright=len(ok), max_speed_deviation_pct=round(dev, 3))


# ------------------------------------------------------------------------------------------------ 7. strict reach / startup
def reach_and_startup():
    rows = []
    for rt in (.2, .45, .7, 1.0):
        for role in gt.ROLES:
            for head in (0., 33., 90.):
                p = rated(rt, role)
                from math import radians, cos, sin
                for start in (0., .3 * DYN.top_speed(p), .9 * DYN.top_speed(p)):
                    r = m32.assess(p, start, Settings(duration_s=6., turn_degrees=head))
                    rows.append(dict(rating=rt, role=role, heading=head, start_m_s=round(start, 2), upright=r['upright'], reason=r['reason'],
                                     max_leg_extension=r['max_leg_extension'], mean_touchdown_reach=r['touchdown_reach_mean_leg'], min_leg_ratio=r['min_leg_ratio']))
    write_csv('reach_startup.csv', rows)
    up = [r for r in rows if r['upright']]
    SUMMARY['reach_startup'] = dict(trials=len(rows), upright=len(up), max_leg_extension=max(r['max_leg_extension'] for r in up),
                                    reach_limit=Params().reach_max_leg, outcomes=dict(collections.Counter(r['reason'] or 'upright' for r in rows)))


# ------------------------------------------------------------------------------------------------ 8. cuts / lateral balance
def cuts():
    rows = []
    for rt in (.3, .5, .7, 1.0):
        p = rated(rt)
        top = sprint(p)['sustained_speed_m_s']
        for frac in (.3, .6, .9):
            for ang in (30, 60, 90, 120, 150, 180):
                for engine, eng in (('v3.2', m32), ('v3.1', m31)):
                    s0 = frac * top
                    kw = dict(duration_s=8., turn_degrees=ang, turn_time_s=1.0)
                    try:
                        r = eng.assess(p, s0, eng.Settings(**kw))
                    except Exception as e:
                        rows.append(dict(engine=engine, rating=rt, start_frac=frac, angle=ang, upright=False, reason=type(e).__name__)); continue
                    v0 = r['speed_at_turn_m_s']
                    rows.append(dict(engine=engine, rating=rt, start_frac=frac, angle=ang, upright=r['upright'], reason=r['reason'],
                                     speed_at_turn=v0, min_speed_after=r['min_speed_after_turn_m_s'],
                                     min_speed_over_entry=round(r['min_speed_after_turn_m_s'] / v0, 3) if v0 and r['min_speed_after_turn_m_s'] is not None else None,
                                     time_to_heading_5deg_s=r['time_to_heading_5deg_s'], heading_end=r['heading_end_deg'],
                                     peak_grf_angle_deg=r['peak_grf_angle_deg'], peak_lateral_tilt_deg=r.get('peak_lateral_tilt_deg'),
                                     peak_N_bw=r['peak_normal_bw'], slip_impulse=r['slip_impulse_Ns']))
    write_csv('cuts_lateral_balance.csv', rows)
    s = {}
    for engine in ('v3.2', 'v3.1'):
        rr = [r for r in rows if r['engine'] == engine]
        by_angle = {a: dict(trials=sum(1 for r in rr if r['angle'] == a), upright=sum(1 for r in rr if r['angle'] == a and r['upright'])) for a in (30, 60, 90, 120, 150, 180)}
        s[engine] = by_angle
    ok = [r for r in rows if r['engine'] == 'v3.2' and r['upright'] and r['angle'] in (60, 90)]
    s['v32_retained_speed_ratio_by_angle'] = {a: round(sum(r['min_speed_over_entry'] for r in ok if r['angle'] == a) / max(1, sum(1 for r in ok if r['angle'] == a)), 3) for a in (60, 90)}
    s['v32_max_lateral_tilt_deg'] = max((r['peak_lateral_tilt_deg'] or 0) for r in rows if r['engine'] == 'v3.2')
    s['posture_cone_deg'] = dict(accel=round(math.degrees(math.atan(m32.STD.peak_acceleration_m_s2 / 9.80665)), 2),
                                 brake=round(math.degrees(math.atan(m32.STD.peak_braking_m_s2 / 9.80665)), 2))
    SUMMARY['cuts'] = s


# ------------------------------------------------------------------------------------------------ 9. stress
def stress():
    rows = []
    for rt in (.45, 1.0):
        p = rated(rt)
        top = sprint(p)['sustained_speed_m_s']
        for tr in (1., .6, .35):
            for start in (0., top, 1.15 * top):
                r = m32.assess(p, start, Settings(duration_s=10., traction=tr))
                rows.append(dict(rating=rt, traction_scale=tr, start_m_s=round(start, 2), upright=r['upright'], reason=r['reason'], end_m_s=r['speed_end_m_s'],
                                 peak_N_bw=r['peak_normal_bw'], slip_impulse=r['slip_impulse_Ns']))
    write_csv('stress.csv', rows)
    SUMMARY['stress'] = dict(trials=len(rows), upright=sum(r['upright'] for r in rows), outcomes=dict(collections.Counter(r['reason'] or 'upright' for r in rows)))


# ------------------------------------------------------------------------------------------------ 10. traces / plots
def traces_and_plots(plots=True):
    rows = []
    for contact in ('spring', 'halfsine'):
        r, tr = m32.assess(rated(1.0), 0., Settings(duration_s=8., contact=contact), trace=True, sample_dt=.001)
        for a in tr[::5]:
            rows.append(dict(contact=contact, t=a['t'], x=round(a['x'], 4), z=round(a['z'], 4), speed=round(math.hypot(a['vx'], a['vy']), 4), vz=round(a['vz'], 4),
                             N_bw=round(a['N'] / (180 * 9.80665), 4), phase=a['phase']))
    write_csv('trace_rating1_field.csv', rows)
    if not plots: return
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rs = list(csv.DictReader((OUT / 'rating_sweep.csv').open()))
    fig, ax = plt.subplots(figsize=(6, 4))
    for role, mk in (('field', 'o-'), ('keeper', 'x--')):
        for eng, con in (('v3.2', 'spring'), ('v3.1', 'halfsine')):
            pts = [(float(r['rating']), float(r['sustained_mph'])) for r in rs if r['role'] == role and r['engine'] == eng and r['contact'] == con and r['upright'] == 'True']
            ax.plot(*zip(*pts), mk, label=f'{eng} {role}', alpha=.85)
    ax.axhline(100, color='k', lw=.6); ax.set_xlabel('rating (all four)'); ax.set_ylabel('sustained speed (mph)'); ax.legend(); ax.grid(alpha=.3)
    fig.tight_layout(); fig.savefig(OUT / 'plot_rating_speed.png', dpi=110); plt.close(fig)
    r_, trf = m32.assess(rated(1.0), 0., Settings(duration_s=7.6), trace=True, sample_dt=.0005)
    tr = [dict(t=a['t'], N_bw=a['N'] / (180 * 9.80665), z=a['z']) for a in trf if a['t'] >= 7.0]
    fig, (a1, a2) = plt.subplots(2, 1, figsize=(6, 5), sharex=True)
    a1.plot([r['t'] for r in tr], [r['N_bw'] for r in tr]); a1.set_ylabel('normal force (BW)'); a1.grid(alpha=.3)
    a2.plot([r['t'] for r in tr], [r['z'] for r in tr]); a2.set_ylabel('COM height (m)'); a2.set_xlabel('t (s)'); a2.grid(alpha=.3)
    fig.suptitle('v3.2 rating-1.0 field athlete, steady running (compliant leg)'); fig.tight_layout(); fig.savefig(OUT / 'plot_steady_strides.png', dpi=110); plt.close(fig)


def main():
    steps = [('manifest', manifest), ('gates', baseline_gates), ('rating_sweep', rating_sweep), ('absolute_rating', absolute_rating),
             ('acceleration', acceleration), ('sustainable_running', sustainable_running), ('ablation', controller_and_contact_ablation), ('tracking', tracking),
             ('convergence', convergence), ('reach_startup', reach_and_startup), ('cuts', cuts), ('stress', stress)]
    for name, fn in steps:
        timed(name, fn)
    write_json('summary_v32.json', SUMMARY)
    timed('traces', lambda: traces_and_plots(not NO_PLOTS))
    print(json.dumps(SUMMARY['gates_6s_straight'], indent=1))


if __name__ == '__main__':
    main()
