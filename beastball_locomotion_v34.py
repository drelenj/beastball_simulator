"""Beastball locomotion v3.4 - top-speed band (design target) on top of the v3.3.1 condition layer.

What changes (and what does not)
  * DESIGN TARGET (DreLen, Oct 28 2026): natural roster ratings 0.6..1.0 span a 1.25x fastest/slowest top-speed band,
    1.0 = 100 mph (NFL-combine "Table A" scaling).  Default shape: linear in rating, i.e. 0.6 -> 80, 0.7 -> 85, 0.8 -> 90,
    0.9 -> 95, 1.0 -> 100 mph.  (The v3.2 physics curve was 65.9 -> 99.9 mph over the same ratings, a 1.52x band.)
  * Only the TOP-SPEED terms use the new 'speed ability' map: vertical force capability (Strength), leg speed / swing time /
    rate of force development (Explosive), peak horizontal thrust (Strength).  The posture cones that set peak acceleration,
    braking and lateral acceleration, the braking force and traction keep the v3.2 ability map, so the accepted v3.2
    acceleration standard is unchanged.
  * The map is SOLVED, not fitted by hand: for each node rating the reference athlete (2.54 m, 180 kg, all ratings = r) is
    simulated and the speed ability found by bisection so that the sustained top speed equals the target (calibrate_v34.py).
  * Below the natural range (effective ratings under 0.6 reached through fatigue/injury) the map continues at the v3.2
    ability slope, so condition losses keep their physical steepness there (a documented kink at r_lo).
v3.2 and v3.3 files are untouched (hash-pinned in the tests).
"""
from dataclasses import dataclass
from math import sqrt
from functools import lru_cache
import beastball_locomotion_v32 as m
import beastball_locomotion_v33 as c
from beastball_locomotion_v32 import Params, Settings, G, rated, BENCHMARK_M_S
from beastball_locomotion_v33 import Condition, FatigueParams, INJURY_REGIONS, effective_profile, time_to_distance

MPH = 0.44704


@dataclass(frozen=True)
class SpeedBand:
    top_mph: float = 100.        # Table A: rating 1.0
    band: float = 1.25           # fastest / slowest natural top speed
    r_lo: float = .6             # slowest natural rating
    r_hi: float = 1.0

    def target_mph(self, r):
        lo = self.top_mph / self.band
        return lo + (self.top_mph - lo) * (r - self.r_lo) / (self.r_hi - self.r_lo)


BAND = SpeedBand()
# (rating, speed ability) nodes inside the natural range - written by calibrate_v34.py
SPEED_ABILITY_NODES = ((0.6, 1.03234), (0.65, 1.05065), (0.7, 1.06932), (0.75, 1.08763), (0.8, 1.10631), (0.85, 1.12499), (0.9, 1.14366), (0.95, 1.17443), (1, 1.21947))


def make_speed_map(nodes=None, std_ability=m.ability, r_lo=None):
    nodes = tuple(nodes or SPEED_ABILITY_NODES)
    r0, a0 = nodes[0]
    r_lo = r_lo if r_lo is not None else r0

    def speed_ability(r):
        if r >= nodes[-1][0]:
            ra, aa = nodes[-1]
            rb, ab = nodes[-2]
            return aa + (r - ra) * (aa - ab) / (ra - rb)           # linear extrapolation (ratings are <= 1 in practice)
        if r <= r_lo:
            return max(1e-3, a0 - (std_ability(r_lo) - std_ability(r)))   # v3.2 slope below the natural range
        for (ra, aa), (rb, ab) in zip(nodes, nodes[1:]):
            if ra <= r <= rb:
                return aa + (ab - aa) * (r - ra) / (rb - ra)
    return speed_ability


speed_ability = make_speed_map()


def derive34(p, q, traction=1., muscle=1., thrust_gain=1., sa=None):
    """v3.2 derive() with the top-speed capacities taken from the speed-ability map."""
    sa = sa or speed_ability
    d = m.derive(p, q, traction, muscle, thrust_gain)
    a = p.athlete
    sS, sE = sa(a.strength), sa(a.explosive_power)
    Lk = d['kin_length_m']
    t_sw = q.swing_c * sqrt(Lk / G) / sE
    d.update(speed_ability_strength=sS, speed_ability_explosive=sE,
             kappa_peak_vertical_bw=q.kappa0 * sS,
             peak_vertical_force_N=q.kappa0 * sS * a.mass_kg * G,
             rfd_time_to_peak_s=q.rfd_s / sE,
             swing_time_full_sweep_s=t_sw,
             swing_rel_speed_m_s=2 * q.sweep_max_leg * Lk / t_sw,
             fv_zero_force_speed_m_s=q.fv_froude * sqrt(G * Lk) * sE,
             thrust_peak_N=q.drive_N_per_kg * thrust_gain * muscle * a.mass_kg * sS)
    return d


@lru_cache(maxsize=512)
def _rested_cached(key, params, T, sa_id):
    h, mass, S, E, R, Tq = key
    from beastball_physical_standard_v1 import Athlete
    from beastball_physical_standard_v11 import PerformanceProfile
    p = PerformanceProfile('x', Athlete(h, mass, strength=S, explosive_power=E, traction=R, technique=Tq), 1., 1., 1., 1.)
    sim = Sim(p, Settings(duration_s=T), params, v_ref=1e9, speed_map=_MAPS[sa_id])
    return run_sim(sim)['sustained_speed_m_s']


_MAPS = {}


def rested_top_speed(p, params=None, speed_map=None, T=16.):
    sm = speed_map or speed_ability
    _MAPS[id(sm)] = sm
    a = p.athlete
    return _rested_cached((a.height_m, a.mass_kg, a.strength, a.explosive_power, a.traction, a.technique), params or Params(), T, id(sm))


class Sim(c.Sim):
    """v3.3.1 simulation with the v3.4 speed-ability map."""

    def __init__(self, p, settings=None, params=None, condition=None, fatigue=None, v_ref=None, speed_map=None):
        self.speed_map = speed_map or speed_ability
        if v_ref is None:
            v_ref = rested_top_speed(p, params, self.speed_map)
        super().__init__(p, settings, params, condition, fatigue, v_ref)

    def _rederive(self):
        s, q = self.s, self.q
        self.p = effective_profile(self.base_profile, self.cond, self.fp)
        self.d = derive34(self.p, q, s.traction, s.muscle, s.thrust_gain * (q.halfsine_drive_scale if s.contact == 'halfsine' else 1.), self.speed_map)
        self._apply_technique()
        self.v_env_lo, self.v_env_hi = self.gait_envelope()


def run_sim(sim, speed=0., sample_dt=.05):
    s = sim.s
    sim.reset(speed)
    sim.e0 = sim._energy()
    n = int(round(s.duration_s / s.dt))
    samples, nxt = [], 0.
    for _ in range(n):
        if sim.fallen: break
        sim.advance(s.dt)
        sim.peak_speed = max(sim.peak_speed, sim._speed())
        if sim.t >= nxt - 1e-12:
            eff = sim.cond.effective_ratings(sim.base_profile.athlete, sim.fp)
            samples.append(dict(t=round(sim.t, 4), x=round(sim.x, 3), speed=round(sim._speed(), 4), reserve=round(sim.cond.reserve, 4),
                                eff_strength=round(eff['strength'], 4), eff_explosive=round(eff['explosive_power'], 4)))
            nxt += sample_dt
    steps = sim.steps[-8:] if len(sim.steps) >= 4 else sim.steps
    tt = sum(r['period_s'] for r in steps if r.get('period_s')); xx = sum(r['step_length_m'] for r in steps if r.get('period_s'))
    summ = dict(upright=not sim.fallen, reason=sim.reason, elapsed_s=round(sim.t, 4), distance_m=round(sim.x, 3),
                speed_end_m_s=round(sim._speed(), 4), speed_peak_m_s=round(sim.peak_speed, 4),
                sustained_speed_m_s=round(xx / tt, 4) if tt > 0 else None, reserve_end=round(sim.cond.reserve, 4),
                reserve_min=round(sim.reserve_min, 4), touchdowns=sim.touchdowns)
    run_sim.samples = samples
    return summ


def run(p, speed=0., settings=None, params=None, condition=None, fatigue=None, v_ref=None, sample_dt=.05, speed_map=None):
    """Same contract as v3.3 run(): returns (summary, samples)."""
    s = settings or Settings(duration_s=12.)
    sim = Sim(p, s, params, condition, fatigue, v_ref, speed_map)
    summ = run_sim(sim, speed, sample_dt)
    return summ, run_sim.samples
