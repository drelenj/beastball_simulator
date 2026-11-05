"""Reproducible runner for Beastball v3.3 (fatigue + injury layer).  Usage: python run_beastball_v33.py [output_dir]  (default ./results_v33)
Deterministic.  Writes CSV/JSON plus summary_v33.json (quoted by the report).  Run time about 1-2 minutes.
"""
import csv, json, sys, hashlib, platform, math
from dataclasses import asdict, replace
from pathlib import Path
import beastball_locomotion_v32 as m
import beastball_locomotion_v33 as F
from beastball_locomotion_v32 import Settings, rated, assess

ROOT = Path(__file__).resolve().parent
_ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = Path(_ARGS[0]) if _ARGS else ROOT / 'results_v33'
OUT.mkdir(parents=True, exist_ok=True)
SUMMARY = {}
MPH = .44704
FP = F.FatigueParams()


def write_csv(name, rows):
    rows = list(rows); keys = []
    for r in rows:
        for k in r:
            if k not in keys: keys.append(k)
    with (OUT / name).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys); w.writeheader(); w.writerows(rows)
    return rows


def top_mph(p, T=14.):
    return assess(p, 0., Settings(duration_s=T))['sustained_speed_m_s'] / MPH


def manifest():
    files = sorted(ROOT.glob('beastball_*.py')) + [ROOT / 'run_beastball_v33.py']
    (OUT / 'v33_parameter_manifest.json').write_text(json.dumps(dict(
        module='beastball_locomotion_v33', fatigue=asdict(FP), injury_regions=F.INJURY_REGIONS, v32_params=asdict(m.Params()),
        python=platform.python_version(), source_sha256={f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in files}), indent=1, default=str))


def fixed_condition_table():
    """Top speed with a FIXED reserve level (steady-state effect of fatigue on speed) for several base ratings, field and Keeper."""
    rows = []
    for role in ('field', 'keeper'):
        for base in (.6, .7, .8, .9, 1.0):
            p = rated(base, role)
            for R in (1., .75, .5, .25, 0.):
                cond = F.Condition(reserve=R)
                pe = F.effective_profile(p, cond, FP)
                eff = cond.effective_ratings(p.athlete, FP)
                rows.append(dict(role=role, base_rating=base, reserve=R, eff_strength=round(eff['strength'], 3), eff_explosive=round(eff['explosive_power'], 3),
                                 top_mph=round(top_mph(pe), 1), top_m_s=round(top_mph(pe) * MPH, 2)))
    write_csv('fatigue_fixed_reserve_speed.csv', rows)
    base = {(r['role'], r['base_rating']): r['top_mph'] for r in rows if r['reserve'] == 1.}
    SUMMARY['fixed_reserve'] = {f"{r['role']}_{r['base_rating']}_R{r['reserve']}": r['top_mph'] for r in rows if r['role'] == 'field'}
    SUMMARY['fixed_reserve_empty_vs_fresh_pct'] = {str(b): round(100 * next(r['top_mph'] for r in rows if r['role'] == 'field' and r['base_rating'] == b and r['reserve'] == 0.) /
                                                                       base[('field', b)] - 100, 1) for b in (.6, .7, .8, .9, 1.0)}


def fade_curves():
    rows = []
    for rt in (.6, .75, .9, 1.0):
        p = rated(rt)
        summ, tr = F.run(p, 0., Settings(duration_s=20.))
        pk = max(a['speed'] for a in tr)
        for t in (2, 4, 6, 8, 10, 12, 14, 17, 20):
            a = [x for x in tr if x['t'] >= t][0]
            rows.append(dict(rating=rt, t_s=t, speed_mph=round(a['speed'] / MPH, 1), pct_of_peak=round(100 * a['speed'] / pk, 1), reserve=a['reserve'],
                             eff_strength=a['eff_strength'], distance_m=a['x']))
        SUMMARY.setdefault('fade', {})[str(rt)] = dict(upright=summ['upright'], peak_mph=round(pk / MPH, 1),
                                                        pct_of_peak_at_10s=[r['pct_of_peak'] for r in rows if r['rating'] == rt and r['t_s'] == 10][0],
                                                        pct_of_peak_at_20s=[r['pct_of_peak'] for r in rows if r['rating'] == rt and r['t_s'] == 20][0],
                                                        reserve_at_20s=summ['reserve_end'])
    write_csv('fade_maximal_effort.csv', rows)


def repeated_sprints():
    """Max effort (8 s), rest, max effort again, carrying the reserve between efforts."""
    rows = []
    for rt in (.75, .9, 1.0):
        p = rated(rt)
        for rest in (0., 10., 30., 60., 120., 300.):
            cond = F.Condition()
            s1, t1 = F.run(p, 0., Settings(duration_s=8.), condition=cond)
            r_after = cond.reserve
            cond.rest(rest, FP)
            r_start = cond.reserve
            s2, t2 = F.run(p, 0., Settings(duration_s=8.), condition=cond)
            pk1 = max(a['speed'] for a in t1); pk2 = max(a['speed'] for a in t2)
            d1 = max(a['x'] for a in t1); d2 = max(a['x'] for a in t2)
            rows.append(dict(rating=rt, rest_s=rest, reserve_after_1=round(r_after, 3), reserve_start_2=round(r_start, 3), peak1_mph=round(pk1 / MPH, 1), peak2_mph=round(pk2 / MPH, 1),
                             peak2_over_peak1=round(pk2 / pk1, 3), dist1_m=d1, dist2_m=d2, dist2_over_dist1=round(d2 / d1, 3), upright=s1['upright'] and s2['upright']))
    write_csv('repeated_sprints.csv', rows)
    SUMMARY['repeated_sprints_r0.9'] = {str(r['rest_s']): r['peak2_over_peak1'] for r in rows if r['rating'] == .9}


def injury_table():
    rows = []
    for base in (.8, .9, 1.0):
        p = rated(base)
        fresh = top_mph(p)
        for region in F.INJURY_REGIONS:
            for sev in (.1, .25, .5, .75):
                cond = F.Condition(region=region, severity=sev)
                eff = cond.effective_ratings(p.athlete, FP)
                mph = top_mph(F.effective_profile(p, cond, FP))
                rows.append(dict(base_rating=base, region=region, severity=sev, eff_strength=round(eff['strength'], 3), eff_explosive=round(eff['explosive_power'], 3),
                                 eff_traction=round(eff['traction'], 3), eff_technique=round(eff['technique'], 3), top_mph=round(mph, 1), pct_of_fresh=round(100 * mph / fresh, 1),
                                 equivalent_uniform_rating=None))
    # equivalent uniform rating: the single rating that would give the same speed in the v3.2 curve
    grid = [(round(.05 + .05 * i, 2), top_mph(rated(round(.05 + .05 * i, 2)))) for i in range(20)]
    def inv(v):
        if v >= grid[-1][1]: return 1.0
        if v <= grid[0][1]: return grid[0][0]
        for (r0, v0), (r1, v1) in zip(grid, grid[1:]):
            if v0 <= v <= v1: return round(r0 + (r1 - r0) * (v - v0) / (v1 - v0), 2)
    for r in rows: r['equivalent_uniform_rating'] = inv(r['top_mph'])
    write_csv('injury_effective_speed.csv', rows)
    SUMMARY['injury_r0.9_mph'] = {f"{r['region']}_{r['severity']}": r['top_mph'] for r in rows if r['base_rating'] == .9}
    SUMMARY['injury_min_equivalent_rating'] = min(r['equivalent_uniform_rating'] for r in rows)


def cuts_degraded():
    rows = []
    for rt in (.9,):
        p0 = rated(rt)
        cases = [('fresh', F.Condition()), ('reserve 0.5', F.Condition(reserve=.5)), ('reserve 0.0', F.Condition(reserve=0.)),
                 ('ankle .5', F.Condition(region='ankle', severity=.5)), ('knee .5', F.Condition(region='knee', severity=.5)), ('hamstring .5', F.Condition(region='hamstring', severity=.5))]
        for name, cond in cases:
            pe = F.effective_profile(p0, cond, FP)
            top = assess(pe, 0., Settings(duration_s=14.))['sustained_speed_m_s']
            for ang in (45, 90, 120):
                r = assess(pe, .6 * top, Settings(duration_s=8., turn_degrees=ang, turn_time_s=1.))
                v0 = r['speed_at_turn_m_s']
                rows.append(dict(condition=name, angle=ang, top_mph=round(top / MPH, 1), upright=r['upright'], reason=r['reason'],
                                 speed_kept=round(r['min_speed_after_turn_m_s'] / v0, 3) if v0 and r['min_speed_after_turn_m_s'] is not None else None,
                                 time_to_heading_s=r['time_to_heading_5deg_s']))
    write_csv('cuts_degraded.csv', rows)
    SUMMARY['cuts_degraded_upright'] = dict(trials=len(rows), upright=sum(r['upright'] for r in rows))


def robustness():
    rows = []
    for rt in (.6, .75, .9, 1.0):
        for role in ('field', 'keeper'):
            p = rated(rt, role)
            for reg, sev in (('', 0), ('hamstring', .25), ('hamstring', .6), ('knee', .5), ('ankle', .5), ('groin', .9), ('general', .9)):
                for r0 in (1., .4):
                    s, tr = F.run(p, 0., Settings(duration_s=20.), condition=F.Condition(reserve=r0, region=reg, severity=sev))
                    rows.append(dict(rating=rt, role=role, region=reg or 'none', severity=sev, start_reserve=r0, upright=s['upright'], reason=s['reason'],
                                     end_speed_mph=round(s['speed_end_m_s'] / MPH, 1), reserve_end=s['reserve_end']))
    write_csv('robustness_condition_grid.csv', rows)
    SUMMARY['robustness'] = dict(runs=len(rows), upright=sum(r['upright'] for r in rows))


def neutral_equals_v32():
    out = []
    for rt in (.3, .7, 1.0):
        for role in ('field', 'keeper'):
            p = rated(rt, role)
            a = assess(p, 0., Settings(duration_s=12.))
            b, _ = F.run(p, 0., Settings(duration_s=12.), fatigue=F.FatigueParams(max_loss=1e-9, tech_max_loss=1e-10, exhaust_time_s=1e9))
            out.append(dict(rating=rt, role=role, v32_end=a['speed_end_m_s'], v33_neutral_end=b['speed_end_m_s'], identical=a['speed_end_m_s'] == b['speed_end_m_s']))
    write_csv('neutral_condition_equals_v32.csv', out)
    SUMMARY['neutral_identical'] = all(r['identical'] for r in out)


def _tech_prof(T, r=.9):
    from beastball_physical_standard_v1 import Athlete
    p = rated(r); a = p.athlete
    return replace(p, athlete=Athlete(a.height_m, a.mass_kg, strength=r, explosive_power=r, traction=r, technique=T))


def _t20_and_cut(T, R, gain, ang=90):
    fp = F.FatigueParams(exhaust_time_s=1e12, recovery_tau_s=1e12, tech_effect_gain=gain)      # reserve frozen at R
    p = _tech_prof(T)
    s, tr = F.run(p, 0., Settings(duration_s=8., ), condition=F.Condition(reserve=R), fatigue=fp, sample_dt=.005)
    t20 = [a['t'] for a in tr if a['speed'] >= 20][0]
    sim = F.Sim(p, Settings(duration_s=8., turn_degrees=ang, turn_time_s=1.), None, F.Condition(reserve=R), fp); sim.reset(20.)
    t0 = th = vt = None; vmin = 1e9
    for _ in range(int(8 / .005)):
        if sim.fallen: break
        sim.advance(.005)
        if sim.turned:
            if t0 is None: t0 = sim.t; vt = sim._speed()
            vmin = min(vmin, sim._speed())
            err = abs((math.degrees(math.atan2(sim.vy, sim.vx)) - ang + 180) % 360 - 180)
            if th is None and err <= 5 and sim._speed() > .5: th = round(sim.t - t0, 2)
    return dict(top_mph=round(s['speed_peak_m_s'] / MPH, 1), t_to_20_m_s=round(t20, 3), cut_time_to_heading_s=th, cut_speed_kept=round(vmin / vt, 3) if vt else None,
                upright=s['upright'] and not sim.fallen)


def technique_table():
    """Technique (form) under fatigue: base physical ratings 0.9, reserve frozen at R, 20 m/s entry for the 90 degree cut."""
    rows = []
    for R in (1., .5, 0.):
        for T in (.4, .7, .95):
            c = F.Condition(reserve=R); eff = c.effective_ratings(_tech_prof(T).athlete, FP)['technique']
            rows.append(dict(reserve=R, technique=T, eff_technique=round(eff, 3), technique_lost_pct=round(100 * (1 - eff / T), 1), gain=FP.tech_effect_gain,
                             **_t20_and_cut(T, R, FP.tech_effect_gain)))
    write_csv('technique_under_fatigue.csv', rows)
    SUMMARY['technique_empty_reserve'] = {str(r['technique']): dict(lost_pct=r['technique_lost_pct'], t20=r['t_to_20_m_s'], cut_s=r['cut_time_to_heading_s'], top=r['top_mph']) for r in rows if r['reserve'] == 0.}
    SUMMARY['technique_rested_identical'] = len({(r['t_to_20_m_s'], r['cut_time_to_heading_s']) for r in rows if r['reserve'] == 1.}) == 1
    sens = []
    for gain in (1., 2., 3., 6.):
        for T in (.4, .95):
            sens.append(dict(gain=gain, technique=T, **_t20_and_cut(T, 0., gain)))
    write_csv('technique_effect_gain_sensitivity.csv', sens)
    SUMMARY['technique_gain_sensitivity_empty'] = {f"gain{r['gain']}_T{r['technique']}": (r['t_to_20_m_s'], r['cut_time_to_heading_s']) for r in sens}


def main():
    for name, fn in (('manifest', manifest), ('fixed_reserve', fixed_condition_table), ('fade', fade_curves), ('repeated', repeated_sprints), ('injury', injury_table), ('technique', technique_table),
                     ('cuts', cuts_degraded), ('robustness', robustness), ('neutral', neutral_equals_v32)):
        fn(); print('  done', name, flush=True)
    (OUT / 'summary_v33.json').write_text(json.dumps(SUMMARY, indent=1, default=str))
    print(json.dumps(SUMMARY, indent=1, default=str)[:3000])


if __name__ == '__main__':
    main()
