"""Phase A: audit of the shipped v3.0 solver. Evidence for the issue register. Writes audit_v30.json."""
import json, csv, collections, sys
from dataclasses import replace
import beastball_unified_locomotion_v30 as v30
from beastball_physical_standard_v11 import profile, Dynamics

out = {}
TIERS = ('developing', 'average', 'exceptional'); ROLES = ('field', 'keeper')

# 1. velocity clamps / speed governor ---------------------------------------------------------
dyn = Dynamics()
out['profile_top_speed_m_s'] = {f'{r}_{t}': round(dyn.top_speed(profile(t, r)), 4) for t in TIERS for r in ROLES}
# is it a clamp on velocity or a target? start above target and see what the integrator does (no thrust possible, so brake)
p = profile('average', 'field'); w = v30.World(p)
s = w.setup(44.704); st = []
for _ in range(400):
    s = w.step(s)
    if s.grounded: break
    st.append(round((s.vx ** 2 + s.vy ** 2) ** .5, 3))
out['start_44.704_average_field_speed_every_0.5s'] = st[::100]
out['speed_governor'] = ('v3.0 _desired() commands vmax=profile.speed_fraction*44.704 and _muscle() applies force proportional to '
                         '(vmax - v): top speed is prescribed by a rating-free constant, not emergent.')

# 2. rating/mass blindness of vertical system (all main-grid rows of the shipped CSV) -----------
rows = list(csv.DictReader(open('baseline_v30_shipped/beastball_v30_results.csv')))
main = [r for r in rows if r['dt_s'] == '0.005']
out['shipped_rows'] = len(rows); out['shipped_rows_dt0.005'] = len(main)
out['peak_height_unique_dt0.005'] = sorted({r['peak_height_m'] for r in main})
out['peak_normal_unique_dt0.005'] = sorted({r['peak_normal_N'] for r in main})
out['peak_height_by_dt'] = {d: sorted({r['peak_height_m'] for r in rows if r['dt_s'] == d}) for d in ('0.0025', '0.005', '0.01')}
out['peak_normal_by_dt'] = {d: sorted({r['peak_normal_N'] for r in rows if r['dt_s'] == d}) for d in ('0.0025', '0.005', '0.01')}
rr = {}
for st_ in (.2, .7, 1.):
    for ex in (.2, .7, 1.):
        q = replace(p, athlete=replace(p.athlete, strength=st_, explosive_power=ex))
        r = v30.assess(q, 10, v30.Settings(duration_s=1.))
        rr[f'strength={st_},explosive={ex}'] = (r['peak_height_m'], r['peak_normal_N'])
out['strength_x_explosive_peak_height_and_normal'] = rr
out['keeper_vs_field_peak_normal_N'] = [v30.assess(profile('average', r), 10, v30.Settings(duration_s=1.))['peak_normal_N'] for r in ROLES]
out['keeper_vs_field_mass_kg'] = [profile('average', r).athlete.mass_kg for r in ROLES]
out['keeper_vs_field_peak_normal_in_bodyweights'] = [round(x / (m * v30.G), 3) for x, m in zip(out['keeper_vs_field_peak_normal_N'], out['keeper_vs_field_mass_kg'])]

# 3. foot kinematics: anchored foot -> required ground-frame foot speed -------------------------
r_, tr = v30.assess(p, 0, v30.Settings(duration_s=2.4, swing_speed_m_s=400.), trace=True)
# foot that is NOT the support foot: how far behind COM is it at touchdown of the other one?
lag = []
prev = None
for row in tr:
    if prev and prev['phase'] != 'landing' and row['phase'] == 'landing':
        lag.append(round(row['x'] - max(row['left_x'], row['right_x']), 2))   # COM ahead of the leading foot at touchdown
    prev = row
out['v30_com_minus_leading_foot_x_at_touchdown_m'] = lag[:6]
sweep = {}
for tier in TIERS:
    for role in ROLES:
        q = profile(tier, role); vm = v30.World(q).vmax
        lo, hi = 20., 400.
        for _ in range(12):
            mid = (lo + hi) / 2
            ok = all(not v30.assess(q, f * vm, v30.Settings(swing_speed_m_s=mid, duration_s=6.))['grounded'] for f in (0, .5, 1.))
            hi, lo = (mid, lo) if ok else (hi, mid)
        sweep[f'{role}_{tier}'] = dict(top_speed=round(vm, 2), min_swing_m_s=round(hi, 1), ratio=round(hi / vm, 2))
out['min_swing_cap_for_6s_upright_starts_0_50_100pct_of_profile_top'] = sweep

# 4. contact-force onset at landing ------------------------------------------------------------
_, tr = v30.assess(p, 10, v30.Settings(duration_s=1.), trace=True)
on = []
for a, b in zip(tr, tr[1:]):
    if a['phase'] != 'landing' and b['phase'] == 'landing':
        i = tr.index(b); on.append([round(x['normal_N'], 1) for x in tr[i - 1:i + 5]])
out['normal_force_N_around_first_landings(prev tick, then landing ticks)'] = on[:3]
out['bodyweight_N_field'] = round(180 * v30.G, 1)

# 5. stance height --------------------------------------------------------------------------------
out['stance_height_fixed'] = 'step(): phase=="stance" sets z=0. every tick (COM height held constant; vz accumulates but is discarded at takeoff).'

# 6. timestep convergence of v3.0 (what it would take to call it converged) -------------------------
conv = {}
for dt in (.0025, .005, .01):
    r = v30.assess(profile('developing', 'field'), 0, v30.Settings(dt=dt, duration_s=3.))
    conv[str(dt)] = dict(x=r['x_m'], vx=r['vx_m_s'], landings=r['landings'], grounded=r['grounded'])
out['v30_timestep_developing_field_from_rest_3s'] = conv

# 7. shipped test suite vs shipped results ------------------------------------------------------------
cnt = collections.Counter('upright' if r['grounded'] == 'False' else r['reason'] for r in rows)
out['shipped_outcomes'] = dict(cnt)
json.dump(out, open('audit_v30.json', 'w'), indent=1)
for k, v in out.items(): print(k, '->', v if len(str(v)) < 400 else str(v)[:400] + '...')
