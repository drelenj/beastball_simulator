"""Beastball v3.2 acceptance gates - one definition shared by the runner and the tests.

Gates are fixed BEFORE looking at v3.2 results (Phase B of the handoff) and are applied identically to the shipped v3.0
solver and to v3.2.  Three tiers, as the handoff requires:

  integrity   every scenario: finite state, zero contact force in flight, friction cone respected, energy audit (v3.2).
  gait        only at physically attainable start speeds (start <= ATTAINABLE_FRACTION * declared top speed of the profile,
              taken from the v1.1 Dynamics model that v3.0 itself uses), 6 s straight running:
                G1 upright for the full 6 s            G2 step frequency inside a human-plausible band
                G3 foot ground speed <= FOOT_RATIO x body speed (no teleporting foot)
                G4 peak normal force <= MAX_NORMAL_BW  G5 speed kept: from rest >= REST_FRACTION x declared top within
                   6 s; from a running start the speed is not lost by more than SPEED_KEEP
  stress      starts above attainable speed, 90 degree cuts etc.: reported, never required to pass.

All thresholds are provisional engineering criteria, not canon.
"""
from math import hypot, isfinite
from beastball_physical_standard_v11 import profile, Dynamics
import beastball_unified_locomotion_v30 as v30
import beastball_locomotion_v32 as v31

ATTAINABLE_FRACTION = .9
MIN_STEP_HZ, MAX_STEP_HZ = 1.5, 6.0
FOOT_RATIO = 2.0
MAX_NORMAL_BW = 12.0
REST_FRACTION = .4
SPEED_KEEP = .15
DURATION_S = 6.0
TIERS = ('developing', 'average', 'exceptional')
ROLES = ('field', 'keeper')
STARTS = (0., 20., 44.704)
DYN = Dynamics()


def declared_top(p):
    return DYN.top_speed(p)


def scenario_tier(p, start):
    return 'gait' if start <= ATTAINABLE_FRACTION * declared_top(p) + 1e-9 else 'stress'


def run_v30(p, start, dt=.005, duration=DURATION_S, turn=0.):
    r, tr = v30.assess(p, start, v30.Settings(dt=dt, duration_s=duration, turn_degrees=turn), trace=True)
    bw = p.athlete.mass_kg * v30.G
    foot = 0.
    for a, b in zip(tr, tr[1:]):
        h = b['t'] - a['t']
        if h <= 0: continue
        for k in ('left', 'right'):
            foot = max(foot, hypot(b[k + '_x'] - a[k + '_x'], b[k + '_y'] - a[k + '_y']) / h)
    peak_body = max([hypot(t['vx'], t['vy']) for t in tr] + [start])
    # The take-off tick of v3.0 is labelled 'flight' but still carries the push-off force that was applied during that tick
    # (end-of-step bookkeeping).  That is a labelling boundary, not a physics violation, so only samples whose predecessor
    # was also 'flight' are checked.
    flight_force = max([b['normal_N'] for a, b in zip(tr, tr[1:]) if a['phase'] == 'flight' and b['phase'] == 'flight'] + [0.])
    elapsed = r['elapsed_s']
    return dict(engine='v3.0', profile=p.label, start_speed_m_s=start, dt_s=dt, duration_s=duration, turn_degrees=turn,
                upright=not r['grounded'], reason=r['reason'] if r['grounded'] else '', elapsed_s=elapsed,
                touchdowns=r['landings'], step_frequency_hz=round(r['landings'] / elapsed, 4) if elapsed > 0 else None,
                speed_end_m_s=round(hypot(r['vx_m_s'], r['vy_m_s']), 4), speed_peak_m_s=round(peak_body, 4),
                exceeds_benchmark=peak_body > v31.BENCHMARK_M_S + 1e-9,
                peak_normal_bw=round(r['peak_normal_N'] / bw, 4), peak_shear_bw=round(r['peak_shear_N'] / bw, 4),
                foot_peak_ground_speed_m_s=round(foot, 3), foot_over_body=round(foot / max(peak_body, 1e-9), 3),
                friction_violation_N=r['friction_violation_N'], flight_force_N=round(flight_force, 6),
                energy_audit_rel=None, positive_ground_work_J=None)


def run_v31(p, start, dt=.005, duration=DURATION_S, turn=0., params=None, **settings):
    r, tr = v31.assess(p, start, v31.Settings(dt=dt, duration_s=duration, turn_degrees=turn, **settings), params=params,
                       trace=True, sample_dt=dt)
    bw = p.athlete.mass_kg * v31.G
    flight_force = max([t['N'] for t in tr if t['phase'] == 'flight'] + [0.])
    foot = r['foot_peak_ground_speed_m_s']
    return dict(engine='v3.2', profile=p.label, start_speed_m_s=start, dt_s=dt, duration_s=duration, turn_degrees=turn,
                upright=r['upright'], reason=r['reason'], elapsed_s=r['elapsed_s'], touchdowns=r['touchdowns'],
                step_frequency_hz=r['step_frequency_hz'], speed_end_m_s=r['speed_end_m_s'], speed_peak_m_s=r['speed_peak_m_s'],
                exceeds_benchmark=r['exceeds_benchmark'], peak_normal_bw=r['peak_normal_bw'],
                peak_shear_bw=round(r['peak_horizontal_force_N'] / bw, 4), foot_peak_ground_speed_m_s=foot,
                foot_over_body=round(foot / max(r['speed_peak_m_s'], 1e-9), 3),
                friction_violation_N=r['slip_impulse_Ns'], flight_force_N=round(flight_force, 6),
                energy_audit_rel=r['energy_audit_rel'], positive_ground_work_J=r['positive_ground_work_J'],
                sustained_speed_m_s=r['sustained_speed_m_s'], benchmark_exceedance_m_s=r['benchmark_exceedance_m_s'],
                contact_time_s=r['contact_time_s'], flight_time_s=r['flight_time_s'], step_length_m=r['step_length_m'])


def gates(row, p):
    """Return {gate_name: (passed, value)} for one normalized row; tier decides which gates are required."""
    start = row['start_speed_m_s']
    top = declared_top(p)
    tier = scenario_tier(p, start)
    g = {}
    finite = all(isfinite(row[k]) for k in ('speed_end_m_s', 'peak_normal_bw', 'elapsed_s') if row.get(k) is not None)
    g['I1_finite'] = (finite, None)
    g['I2_zero_force_in_flight'] = (row['flight_force_N'] <= 1e-9, row['flight_force_N'])
    g['I3_friction_cone'] = (row['friction_violation_N'] <= 1e-6, row['friction_violation_N'])
    if row['energy_audit_rel'] is not None:
        g['I4_energy_audit'] = (row['energy_audit_rel'] < 1e-4, row['energy_audit_rel'])
    g['G1_upright_6s'] = (row['upright'], row['elapsed_s'])
    hz = row['step_frequency_hz']
    g['G2_step_frequency_band'] = (hz is not None and MIN_STEP_HZ <= hz <= MAX_STEP_HZ, hz)
    g['G3_foot_speed_ratio'] = (row['foot_over_body'] <= FOOT_RATIO, row['foot_over_body'])
    g['G4_peak_normal_force'] = (row['peak_normal_bw'] <= MAX_NORMAL_BW, row['peak_normal_bw'])
    if row['start_speed_m_s'] <= 1e-9:
        ok = row['upright'] and row['speed_end_m_s'] >= REST_FRACTION * top
        g['G5_speed_gain_from_rest'] = (ok, row['speed_end_m_s'])
    else:
        ok = row['upright'] and row['speed_end_m_s'] >= (1 - SPEED_KEEP) * start
        g['G5_speed_kept'] = (ok, row['speed_end_m_s'])
    required = [k for k in g if k.startswith('I')] + ([k for k in g if k.startswith('G')] if tier == 'gait' else [])
    return dict(tier=tier, declared_top_m_s=round(top, 3), results={k: dict(passed=bool(v[0]), value=v[1]) for k, v in g.items()},
                required=required, passed_required=all(g[k][0] for k in required),
                failed=[k for k in required if not g[k][0]])


def scenario_grid():
    for tier in TIERS:
        for role in ROLES:
            p = profile(tier, role)
            for s in STARTS:
                yield p, s
