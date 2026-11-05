"""Beastball locomotion v3.6 - fluid stops on top of v3.5 (fluid cuts) and v3.4 (speed band).

Through v3.5 a braking demand was a P-law "remove the speed in effort_tau (0.35 s)" applied only while the foot is down (duty 0.2-0.9), so every
stride removed ~4.5 m/s whatever the braking cone or force cap (raising the cone 22 -> 50 m/s^2 and the cap 40 -> 100 N/kg moved a 25 m/s stop
only from 18.7 to 15.4 m).  The same flaw as the lateral law fixed in v3.5.  v3.6 scales any deceleration demand by gain * (period / contact), so the
braking cone and force cap become the real limits.  `BrakeParams(enabled=False)` reproduces v3.5 exactly.
The one change inside the force function (copied from v3.5) is marked 'v3.6'.
"""
from dataclasses import dataclass, replace
from math import sqrt, hypot
import beastball_locomotion_v32 as m
import beastball_locomotion_v33 as c
import beastball_locomotion_v34 as v34
import beastball_locomotion_v35 as v35
from beastball_locomotion_v32 import Settings, rated, G
from beastball_locomotion_v33 import Condition, FatigueParams
from beastball_locomotion_v34 import BAND, MPH
from beastball_locomotion_v35 import ArcParams, STANDARD35

STANDARD36 = replace(STANDARD35, peak_brake_m_s2=35., brake_N_per_kg=100.)   # braking cone 35*1.2195 = 43 m/s^2 (4.4 g) at rating 1.0; force cap 100 N/kg x ability (provisional)


@dataclass(frozen=True)
class BrakeParams:
    enabled: bool = True
    gain: float = 3.             # stiffness of the deceleration law relative to the duty-scaled demand
    max_boost: float = 40.


class Sim(v35.Sim):
    def __init__(self, p, settings=None, params=None, condition=None, fatigue=None, v_ref=None, speed_map=None, arc=None, brake=None):
        self.brake = brake or BrakeParams()
        self.brake_boost = 1.
        super().__init__(p, settings, params or STANDARD36, condition, fatigue, v_ref, speed_map, arc)

    def _plan_stance(self, first=False):
        super()._plan_stance(first)
        b = self.brake
        self.brake_boost = min(b.max_boost, max(1., b.gain * (self.t_c + self.t_f) / max(self.t_c, 1e-3))) if b.enabled else 1.

    def _horizontal_force(self, N, Dx, Dy, z, vx, vy):
        """Leg axial force + muscular thrust, limited by muscle (force-velocity) and the friction cone.  Returns (Fx, Fy, slip)."""
        d, m = self.d, self.m
        zz = max(z, 1e-3)
        Fax = (N * Dx / zz, N * Dy / zz)
        s = self.s
        ud = self.ud; nd = (-ud[1], ud[0])
        vpar = vx * ud[0] + vy * ud[1]; vperp = vx * nd[0] + vy * nd[1]
        cap_f = d['thrust_peak_N'] * max(0., 1 - max(vpar, 0.) / d['fv_zero_force_speed_m_s'])
        cap_f *= self.effort
        if s.mode == 'sprint':
            Ff = cap_f
        elif s.mode == 'speed':
            Ff = m * (s.target_speed - vpar) / self.q.effort_tau_s + self.f_int
            if Ff < 0: Ff *= self.brake_boost                  # v3.6: a deceleration demand is delivered in contact only
            Ff = min(max(Ff, -d['brake_peak_N']), cap_f)
        else:                                            # brake to rest
            Ff = min(max(m * (0. - vpar) / self.q.effort_tau_s * self.brake_boost, -d['brake_peak_N']), 0.)   # v3.6 duty-scaled
        Fl = -m * vperp / self.q.lateral_tau_s
        lat_cap = d.get('lateral_peak_N', d['thrust_peak_N'])   # v3.5: the lateral muscle limit is the lean cone at peak vertical force, not the forward-thrust capacity
        Fl = min(max(Fl, -lat_cap), lat_cap)
        # posture limit: total horizontal force along the heading in [-tan_brk, +tan_acc]*N, across it within +-tan_lat*N
        ax_par = Fax[0] * ud[0] + Fax[1] * ud[1]; ax_perp = Fax[0] * nd[0] + Fax[1] * nd[1]
        Ff = min(max(Ff, -d['tan_psi_brk'] * N - ax_par), d['tan_psi_acc'] * N - ax_par)
        Fl = min(max(Fl, -d['tan_psi_lat'] * N - ax_perp), d['tan_psi_lat'] * N - ax_perp)
        # combined lean limit (lateral balance): the total GRF tilt vector must stay inside the posture ellipse
        # (semi-axes tan_psi_acc|brk along the heading, tan_psi_lat across it) - a cut and a brake/push share one lean budget
        if N > 1e-9:
            tp = d['tan_psi_acc'] if Ff + ax_par >= 0 else d['tan_psi_brk']; tl = d['tan_psi_lat']
            a_, b_ = (ax_par / tp), (ax_perp / tl)
            c_, e_ = (Ff / tp), (Fl / tl)
            qa = c_ * c_ + e_ * e_
            if qa > 1e-18 and (a_ + c_) ** 2 + (b_ + e_) ** 2 > N * N:
                qb = 2 * (a_ * c_ + b_ * e_); qc = a_ * a_ + b_ * b_ - N * N
                disc = max(0., qb * qb - 4 * qa * qc)
                sc_ = min(1., max(0., (-qb + sqrt(disc)) / (2 * qa))) if qc <= 0 else 0.
                Ff, Fl = Ff * sc_, Fl * sc_
            self.peak_lat_tilt = max(self.peak_lat_tilt, abs(Fl + ax_perp) / N)
        cmd = (Ff * ud[0] + Fl * nd[0], Ff * ud[1] + Fl * nd[1])
        lim = d['mu'] * N
        slip = 0.
        ax = hypot(*Fax)
        if ax >= lim:                                    # leg force alone exceeds the friction cone: foot slips
            if ax > 1e-9:
                tot = (Fax[0] * lim / ax, Fax[1] * lim / ax)
            else:
                tot = (0., 0.)
            slip = ax - lim
            return tot[0], tot[1], slip, (0., 0.)
        # largest s in [0,1] with |Fax + s*cmd| <= lim
        a2 = cmd[0] ** 2 + cmd[1] ** 2
        if a2 < 1e-12:
            sc = 0.
        else:
            b = 2 * (Fax[0] * cmd[0] + Fax[1] * cmd[1]); c = ax ** 2 - lim ** 2
            disc = max(0., b * b - 4 * a2 * c)
            sc = (-b + sqrt(disc)) / (2 * a2)
            sc = min(1., max(0., sc))
        c2 = (cmd[0] * sc, cmd[1] * sc)
        return Fax[0] + c2[0], Fax[1] + c2[1], 0., c2


def run(p, speed=0., settings=None, params=None, condition=None, fatigue=None, v_ref=None, sample_dt=.05, speed_map=None, arc=None, brake=None):
    s = settings or Settings(duration_s=12.)
    sim = Sim(p, s, params, condition, fatigue, v_ref, speed_map, arc, brake)
    summ = v34.run_sim(sim, speed, sample_dt)
    return summ, v34.run_sim.samples
