"""Beastball Physical Standard v3.3 - fatigue and injury layer on the (unchanged) v3.2 locomotion model.

Scope (by design decision): the rating -> speed curve of v3.2 is NOT changed.  Fatigue and injury act only by lowering an
athlete's EFFECTIVE ratings, and the v3.2 physics then produces the slower speed, longer stride cycle and weaker acceleration:

    effective rating = base rating * injury factor * fatigue factor        (floored at `floor_rating`)

  * Technique (v3.3.1) has no effect on running in v3.2 (it only fed the hand/grip models), so this layer gives it a RELATIVE role:
    when an athlete's effective technique falls below his rested technique, the lateral and braking posture cones (cutting and
    stopping control) shrink in proportion and horizontal thrust loses `tech_thrust_weight` of the proportional drop (wasted force).
    A rested athlete is unchanged, so the v3.2 rating->speed curve is untouched.  Fatigue lowers technique LESS than the physical
    ratings and scales with how poor the form is: factor = 1 - tech_max_loss*(1-R)**p*(1-technique)  (good form survives, poor form
    gets lazy).  Injury regions weight technique directly (not scaled by form).
  * Fatigue - an interpretable anaerobic-reserve (critical-speed) model.  Reserve R in [0,1].  While the athlete runs faster than
    u_cp (fraction of his rested top speed) R drains in proportion to (u-u_cp)/(1-u_cp), emptying after `exhaust_time_s` at full
    speed; below u_cp it recovers exponentially (`recovery_tau_s`).  Fatigue lowers Strength and Explosive Power (force and rate of
    force development / leg speed), not Traction or Technique:  factor = 1 - max_loss*(1-R)**loss_exponent.
  * Injury - a region (hamstring, ankle, knee, groin, general) with a severity in [0,1]; each region weights how much it removes from
    each of the four ratings:  factor = 1 - severity*weight.
  * Capacities are re-derived at every touchdown, so changes act smoothly stride to stride; with a neutral condition the result is
    identical to v3.2 (tested).

Everything here is PROVISIONAL game-design tuning, not physiology.  `exhaust_time_s` and `max_loss` are the only fatigue constants fitted to anything: with a 10 s empty-reserve time, a
rating-1.0 athlete running flat out from rest loses about 5 % of peak speed by the 10 s mark (the human elite 100 m fade, taken by TIME because Beastball athletes cover 100 m in ~4 s).  Injury weights are
design placeholders for the injury system to replace.  Known limitation: intensity is measured against the athlete's RESTED,
UNINJURED top speed, so an injured athlete running at his own (lower) maximum tires less than he physically would.
"""
from dataclasses import dataclass, field, asdict
from math import hypot, isfinite
import beastball_locomotion_v32 as m
from beastball_locomotion_v32 import Params, Settings, derive, rated, BENCHMARK_M_S
from beastball_physical_standard_v11 import PerformanceProfile
from beastball_physical_standard_v1 import Athlete

# region -> weights on (strength, explosive_power, traction, technique); provisional placeholders for the injury system
INJURY_REGIONS = {
    'hamstring': dict(strength=.50, explosive_power=.90, traction=.00, technique=.00),
    'groin':     dict(strength=.30, explosive_power=.60, traction=.10, technique=.20),
    'knee':      dict(strength=.80, explosive_power=.60, traction=.20, technique=.30),
    'ankle':     dict(strength=.20, explosive_power=.40, traction=.50, technique=.40),
    'general':   dict(strength=.50, explosive_power=.50, traction=.50, technique=.50),
}
RATING_KEYS = ('strength', 'explosive_power', 'traction', 'technique')


@dataclass(frozen=True)
class FatigueParams:
    u_cp: float = .75                  # critical speed as a fraction of rested top speed (no net drain at or below it)
    exhaust_time_s: float = 10.        # time to empty the reserve running flat out (u = 1)
    recovery_tau_s: float = 60.        # recovery time constant at rest
    tech_max_loss: float = .33         # technique factor = 1 - tech_max_loss*(1-R)^p*(1-technique): <= .33, always below the physical max_loss
    tech_effect_gain: float = 2.       # amplifies the relative technique drop before it reaches the cones/thrust (design dial)
    tech_thrust_weight: float = .5     # share of the relative technique drop that also costs horizontal thrust (cone limits take the rest)
    max_loss: float = .38              # factor on Strength/Explosive at an empty reserve = 1 - max_loss
    loss_exponent: float = 1.5
    floor_rating: float = .05          # effective ratings are never taken below this (v3.2 supports 0.05 and up)

    def __post_init__(self):
        for k, v in asdict(self).items():
            if not isfinite(v) or v <= 0: raise ValueError(f'{k} must be finite and positive')
        if not (0 < self.u_cp < 1 and 0 < self.max_loss < 1 and 0 < self.tech_max_loss < self.max_loss and self.tech_thrust_weight <= 1):
            raise ValueError('u_cp and max_loss must lie in (0,1)')


@dataclass
class Condition:
    """Mutable athlete condition carried between runs: reserve plus an optional injury."""
    reserve: float = 1.
    region: str = ''
    severity: float = 0.

    def __post_init__(self):
        if not (0 <= self.reserve <= 1): raise ValueError('reserve must be in [0,1]')
        if self.region and self.region not in INJURY_REGIONS: raise ValueError(f'unknown injury region {self.region!r}')
        if not (0 <= self.severity <= 1): raise ValueError('severity must be in [0,1]')

    def injury_factor(self, key):
        if not self.region or self.severity <= 0: return 1.
        return 1. - self.severity * INJURY_REGIONS[self.region][key]

    def fatigue_factor(self, key, fp, base=1.):
        if key in ('strength', 'explosive_power'):
            return 1. - fp.max_loss * (1. - self.reserve) ** fp.loss_exponent
        if key == 'technique':
            return 1. - fp.tech_max_loss * (1. - self.reserve) ** fp.loss_exponent * (1. - base)
        return 1.

    def effective_ratings(self, base, fp):
        return {k: min(1., max(fp.floor_rating, getattr(base, k) * self.injury_factor(k) * self.fatigue_factor(k, fp, getattr(base, k)))) for k in RATING_KEYS}

    def rest(self, seconds, fp=FatigueParams()):
        """Recover at rest (u = 0) for `seconds`."""
        from math import exp
        self.reserve = 1. - (1. - self.reserve) * exp(-seconds / fp.recovery_tau_s)


def effective_profile(p, cond, fp):
    from dataclasses import replace
    a = p.athlete
    return replace(p, athlete=Athlete(a.height_m, a.mass_kg, **cond.effective_ratings(a, fp)))


def rested_top_speed(p, params=None, T=16.):
    """Rested, uninjured sustained top speed of this profile in the v3.2 model (reference for fatigue intensity)."""
    return m.assess(p, 0., Settings(duration_s=T), params=params)['sustained_speed_m_s']


class Sim(m.Sim):
    """v3.2 simulation whose capacities follow a time-varying Condition (fatigue reserve + injury)."""

    def __init__(self, p, settings=None, params=None, condition=None, fatigue=None, v_ref=None):
        self.base_profile = p
        self.cond = condition if condition is not None else Condition()
        self.fp = fatigue or FatigueParams()
        self.v_ref = v_ref if v_ref else rested_top_speed(p, params)
        self.reserve_min = self.cond.reserve
        super().__init__(effective_profile(p, self.cond, self.fp), settings, params)
        self._rederive()
        self.reset(0.)

    def _rederive(self):
        s, q = self.s, self.q
        self.p = effective_profile(self.base_profile, self.cond, self.fp)
        self.d = derive(self.p, q, s.traction, s.muscle, s.thrust_gain * (q.halfsine_drive_scale if s.contact == 'halfsine' else 1.))
        self._apply_technique()
        self.v_env_lo, self.v_env_hi = self.gait_envelope()

    def _apply_technique(self):
        a0, a1 = self.base_profile.athlete.technique, self.p.athlete.technique
        rel = min(1., a1 / a0) if a0 > 0 else 1.
        rel = max(.2, 1. - self.fp.tech_effect_gain * (1. - rel))
        if rel < 1.:
            d = self.d
            d['tan_psi_lat'] *= rel; d['tan_psi_brk'] *= rel
            d['thrust_peak_N'] *= 1. - self.fp.tech_thrust_weight * (1. - rel)
        self.tech_rel = rel

    def _touchdown(self):
        self._rederive()
        super()._touchdown()

    def advance(self, h):
        ok = super().advance(h)
        u = self._speed() / self.v_ref
        fp = self.fp
        if u > fp.u_cp:
            self.cond.reserve = max(0., self.cond.reserve - h / fp.exhaust_time_s * (u - fp.u_cp) / (1. - fp.u_cp))
        else:
            from math import exp
            self.cond.reserve = 1. - (1. - self.cond.reserve) * exp(-h / fp.recovery_tau_s * (fp.u_cp - u) / fp.u_cp)
        self.reserve_min = min(self.reserve_min, self.cond.reserve)
        return ok


def run(p, speed=0., settings=None, params=None, condition=None, fatigue=None, v_ref=None, sample_dt=.05):
    """Run one effort.  Returns (summary dict, samples list).  `condition` is mutated (reserve at the end of the effort)."""
    s = settings or Settings(duration_s=12.)
    sim = Sim(p, s, params, condition, fatigue, v_ref)
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
                reserve_min=round(sim.reserve_min, 4), touchdowns=sim.touchdowns,
                energy_audit_rel=None)
    return summ, samples


def time_to_distance(samples, d):
    for a, b in zip(samples, samples[1:]):
        if b['x'] >= d > a['x']:
            return round(a['t'] + (b['t'] - a['t']) * (d - a['x']) / (b['x'] - a['x'] + 1e-12), 3)
    return None
