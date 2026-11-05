"""Work backward from play-feel targets to the loads the body must carry (analytic, plus numbers measured in the v3.4 sim)."""
import json, math
import beastball_locomotion_v34 as v, beastball_locomotion_v33 as c, beastball_locomotion_v32 as m
from beastball_locomotion_v32 import rated, Settings, G
M, MASS, H = .44704, 180., 2.54
BW = MASS * G
L = .53 * H
ab_E, ab_R = m.ability(1.0), m.ability(1.0)
mu = 2.4 * ab_R
cone_lat = 16. * ab_E; cone_brk = 22. * ab_R
out = {'constants': dict(mass_kg=MASS, height_m=H, leg_length_m=round(L, 3), friction_mu_at_1_0=round(mu, 2), lateral_cone_m_s2=round(cone_lat, 1), braking_cone_m_s2=round(cone_brk, 1))}
# 1. stopping
rows = []
for vmph in (100, 78, 56):
    vv = vmph * M
    for d in (10, 20, 30, 40, 65):
        a = vv * vv / (2 * d); t = 2 * d / vv; ke = .5 * MASS * vv * vv
        rows.append(dict(speed_mph=vmph, stop_m=d, decel_m_s2=round(a, 1), decel_g=round(a / G, 2), time_s=round(t, 2), mean_mu_needed=round(a / G, 2),
                         within_friction=a <= mu * G, within_braking_cone=a <= cone_brk, absorbed_kJ=round(ke / 1e3, 0), absorb_power_kW=round(ke / t / 1e3, 0)))
out['stopping'] = rows
# 2. turning (radius needed = v^2/a); minimum radius the model allows
rows = []
for vmph in (100, 78, 56, 34, 22):
    vv = vmph * M
    rows.append(dict(speed_mph=vmph, r_min_cone_m=round(vv * vv / cone_lat, 1), r_min_friction_m=round(vv * vv / (mu * G), 1),
                     a_lat_g_for_r10=round(vv * vv / 10 / G, 1), a_lat_g_for_r20=round(vv * vv / 20 / G, 1)))
out['turning'] = rows
# 3. dynamic similarity vs a human sprinter (leg 0.93 m, 9 m/s)
out['froude'] = dict(athlete_100mph=round((100 * M) ** 2 / (G * L), 0), human_9ms=round(81 / (G * .93), 1), body_lengths_per_s_athlete=round(100 * M / H, 1), human=round(9 / 1.8, 1),
                     field_crossing_s=round(100 / (100 * M), 2))
# 4. momentum, energy, tackle impulse
vv = 100 * M
out['collision'] = dict(momentum_kN_s=round(MASS * vv / 1e3, 2), KE_kJ=round(.5 * MASS * vv * vv / 1e3, 0),
                        push_N_per_kg_std=35., push_force_kN=round(35. * MASS * m.ability(1.0) / 1e3, 2), grip_kN=round(10. * MASS * m.ability(1.0) / 1e3, 2),
                        time_to_stop_at_push_s=round(MASS * vv / (35. * MASS * m.ability(1.0)), 2))
# 5. what the same leg force implies for a standing jump (work-energy, assumptions stated)
kappa = 8. * m.ability(1.0)
rows = []
for f in (.6, .7, .8):
    for s in (.30, .35, .40):
        rows.append(dict(avg_force_frac_of_peak=f, stroke_frac_leg=s, rise_m=round((f * kappa - 1) * s * L, 2), rise_ft=round((f * kappa - 1) * s * L / .3048, 1)))
out['jump_implied'] = dict(kappa_peak_vertical_bw=round(kappa, 2), table=rows)
# 6. energy / heat of one sprint from standing (COM-level work from the sim: a lower bound)
s = Settings(duration_s=6.); sim = v.Sim(rated(1.0), s, None, None, c.FatigueParams(max_loss=1e-9, tech_max_loss=1e-10, exhaust_time_s=1e9), 1e9)
sim.reset(0.); sim.e0 = sim._energy()
for _ in range(int(6 / s.dt)):
    if sim.fallen: break
    sim.advance(s.dt)
res = m._result(sim, sim.p, 0., s, None, None)
W = res['positive_ground_work_J']; Dw = res['drag_work_J']
out['sprint_energy'] = dict(duration_s=6., end_speed_mph=round(sim._speed() / M, 1), positive_ground_work_kJ=round(W / 1e3, 0), drag_work_kJ=round(abs(Dw) / 1e3, 0),
    metabolic_kJ_at_25pct=round(W / .25 / 1e3, 0), metabolic_kcal=round(W / .25 / 4184, 0), heat_kJ=round(W * 3 / 1e3, 0),
    core_temp_rise_K=round(W * 3 / (MASS * 3500.), 2))
json.dump(out, open('derived_requirements_v34.json', 'w'), indent=1)
for k, vv_ in out.items():
    print(k)
    if isinstance(vv_, list):
        for r in vv_: print('  ', r)
    else: print('  ', vv_)
