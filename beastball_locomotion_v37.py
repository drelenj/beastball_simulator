"""Beastball locomotion v3.7 - the 'float control valve': live-intensity fatigue on top of v3.6.

Through v3.6 the reserve drained only while speed > u_cp (75 % of top speed) and recovered exponentially below it; cuts, stops and hard
accelerations at moderate speed cost nothing.  v3.7 replaces that rule (DreLen, Oct 28 2026):

  intensity I in [0,1], live:  I = min(1, max(u, load, push) * sensitivity(stamina))
      u    = speed / rested top speed                      (holding top speed = 1: the calibration activity)
      push = forward thrust demanded / rested thrust capacity (a sprint-mode athlete is at full push whatever the speed)
      load = |stride-smoothed COM acceleration| measured on the rested lean ellipse (accelerating / braking / lateral cones)
             -> hard starts, stops and cuts are intense whatever the speed
  valve:   I = 0   -> reserve recovers at its maximum rate
           I = .5  -> recovery = drain, reserve stays level
           I = 1   -> reserve drains at its maximum rate           (linear in between on each side)
  Stamina rating (0..1) sets the whole valve: recovery maximum, drain maximum, and sensitivity (the same action is less intense for a higher rating).
  Bench: a flat recovery rate above the stamina-1.0 rate, whatever the athlete's stamina.
At the reference stamina (0.7) a held top-speed sprint empties the reserve in `exhaust_time_s` (10 s) exactly as v3.3 did.
What the reserve does to Strength/Explosive/Technique (max_loss etc.) is unchanged.  `ValveParams(enabled=False)` reproduces v3.6 bit for bit.
All constants are PROVISIONAL design values.
"""
from dataclasses import dataclass, replace
from math import hypot
import beastball_locomotion_v32 as m
import beastball_locomotion_v33 as c
import beastball_locomotion_v34 as v34
import beastball_locomotion_v36 as v36
from beastball_locomotion_v32 import Settings, rated, G
from beastball_locomotion_v33 import Condition, FatigueParams
from beastball_locomotion_v36 import STANDARD36, BrakeParams
from beastball_locomotion_v35 import ArcParams

STANDARD37 = STANDARD36


@dataclass(frozen=True)
class ValveParams:
    enabled: bool = True
    ref_stamina: float = .7
    neutral: float = .5            # intensity at which recovery equals drain
    rec_full_s: float = 60.        # empty -> full at the maximum recovery rate, reference stamina
    sens_slope: float = 1. / 3.    # sensitivity = 1 - slope*(stamina - ref): 0.9 at 1.0, 1.1 at 0.4
    bench_factor: float = 1.5      # bench recovery = factor * (stamina-1.0 maximum recovery rate)
    accel_tau_s: float = .25       # smoothing of the COM acceleration used for 'load'


def stamina_terms(stamina, vp, fp):
    """(sensitivity, max drain per s, max recovery per s) for a stamina rating."""
    ab = lambda r: (.4 + .6 * r) / (.4 + .6 * vp.ref_stamina)       # the legacy ability map: 1.0 at the reference, 1.22 at 1.0
    sens = 1. - vp.sens_slope * (stamina - vp.ref_stamina)
    drain = vp.ref_stamina / max(stamina, .05) / fp.exhaust_time_s    # exhaust time scales with stamina: 10 s at 0.7, 14.3 s at 1.0
    rec = ab(stamina) / vp.rec_full_s
    return sens, drain, rec


def valve_rate(I, drain, rec, neutral=.5):
    """d(reserve)/dt from intensity: +rec at I=0, 0 at I=neutral, -drain at I=1."""
    if I <= neutral: return rec * (1. - I / neutral)
    return -drain * (I - neutral) / (1. - neutral)


def bench_rate(stamina, vp=ValveParams(), fp=FatigueParams()):
    return vp.bench_factor * stamina_terms(1., vp, fp)[2]


def bench_rest(cond, seconds, stamina=None, vp=ValveParams(), fp=FatigueParams()):
    """Rest on the bench: flat recovery, the same for every stamina rating (and stronger than the 1.0 rating's valve maximum)."""
    cond.reserve = min(1., cond.reserve + bench_rate(stamina, vp, fp) * seconds)
    return cond.reserve


class Sim(v36.Sim):
    def __init__(self, p, settings=None, params=None, condition=None, fatigue=None, v_ref=None, speed_map=None, arc=None, brake=None,
                 valve=None, stamina=None):
        self.valve = valve or ValveParams()
        self.stamina = self.valve.ref_stamina if stamina is None else stamina
        self.intensity = 0.; self._a = (0., 0.); self._ref = None
        super().__init__(p, settings, params, condition, fatigue, v_ref, speed_map, arc, brake)

    def _rested_cones(self):
        s, q = self.s, self.q
        d = v34.derive34(self.base_profile, q, s.traction, s.muscle, s.thrust_gain * (q.halfsine_drive_scale if s.contact == 'halfsine' else 1.), self.speed_map)
        self._rd = d
        return d['tan_psi_acc'] * G, d['tan_psi_brk'] * G, d['tan_psi_lat'] * G

    def _push(self):
        """Forward effort: demanded thrust as a fraction of the rested thrust capacity at this speed (sprint mode = the effort setting)."""
        s, d = self.s, self._rd
        if s.mode == 'sprint': return 1.
        if s.mode != 'speed': return 0.
        ud = self.ud
        vpar = self.vx * ud[0] + self.vy * ud[1]
        cap = d['thrust_peak_N'] * max(0., 1. - max(vpar, 0.) / d['fv_zero_force_speed_m_s'])
        dem = self.m * (s.target_speed - vpar) / self.q.effort_tau_s + self.f_int
        return min(1., max(0., dem / cap)) if cap > 1e-9 else (1. if dem > 0 else 0.)

    def advance(self, h):
        vp = self.valve
        if not vp.enabled: return super().advance(h)
        r0, v0 = self.cond.reserve, (self.vx, self.vy)
        ok = super().advance(h)
        self.cond.reserve = r0                     # the v3.3 speed-threshold law is replaced below
        if self._ref is None: self._ref = self._rested_cones()
        k = min(1., h / vp.accel_tau_s)
        self._a = (self._a[0] + k * ((self.vx - v0[0]) / h - self._a[0]), self._a[1] + k * ((self.vy - v0[1]) / h - self._a[1]))
        ud = self.ud; nd = (-ud[1], ud[0])
        ap = self._a[0] * ud[0] + self._a[1] * ud[1]; aq = self._a[0] * nd[0] + self._a[1] * nd[1]
        acc, brk, lat = self._ref
        load = hypot(ap / (acc if ap >= 0 else brk), aq / lat)
        sens, drain, rec = stamina_terms(self.stamina, vp, self.fp)
        self.intensity = min(1., max(self._speed() / self.v_ref, load, self._push()) * sens)
        self.cond.reserve = min(1., max(0., r0 + h * valve_rate(self.intensity, drain, rec, vp.neutral)))
        self.reserve_min = min(self.reserve_min, self.cond.reserve)
        return ok


def run(p, speed=0., settings=None, params=None, condition=None, fatigue=None, v_ref=None, sample_dt=.05, speed_map=None, arc=None, brake=None,
        valve=None, stamina=None):
    s = settings or Settings(duration_s=12.)
    sim = Sim(p, s, params, condition, fatigue, v_ref, speed_map, arc, brake, valve, stamina)
    summ = v34.run_sim(sim, speed, sample_dt)
    return summ, v34.run_sim.samples
