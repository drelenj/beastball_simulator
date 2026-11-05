"""Beastball locomotion v3.5 - arc cutting (fluid turns) on top of the v3.4 speed band.

Why: through v3.4 a heading command was an instant flip of the force frame.  The athlete first had to cancel its old velocity
sideways and then build the new velocity from zero along the new heading - stop-and-go on two axes.  Every cut therefore kept
about 60 percent of speed whatever the lateral standard was (sweeping the lateral limit 16 -> 48 m/s^2 and traction 2.4 -> 5.0
changed 90-degree cut times by only 25 percent).
What changes: after the command the force frame (the direction speed is tracked along and lateral force is measured across)
ROTATES toward the commanded heading at the rate the athlete's lateral capability allows, and never leads the actual velocity
heading by more than `lead_max_deg`.  A cut is then an arc whose curvature the existing lateral cone sets; a sharper request just
takes a bigger arc unless the tactical layer also lowers the target speed.  Fatigue, injury and technique scale the cone, so they
scale the turn.  `ArcParams(enabled=False)` reproduces v3.4 exactly.
Standards (DreLen, Oct 28 2026: body, cleats and field can all carry fluid-cut loads): see STANDARD35.
"""
from dataclasses import dataclass, replace
from math import atan2, cos, sin, hypot, pi, copysign, radians, sqrt
import beastball_locomotion_v32 as m
import beastball_locomotion_v33 as c
import beastball_locomotion_v34 as v34
from beastball_locomotion_v32 import Settings, rated, G
from beastball_locomotion_v33 import Condition, FatigueParams, INJURY_REGIONS
from beastball_locomotion_v34 import BAND, MPH

# Fluid-cut standard (option B): lateral acceleration at rating 1.0 = lateral_accel * ability = 41 * 1.2195 = 50 m/s^2 (5.1 g, ground force 79 deg from
# vertical); traction raised so the friction cone is not the limit (mu = mu0 * ability = 5.2 at rating 1.0).  Provisional design values.
STANDARD35 = replace(m.Params(), lateral_accel_m_s2=41., mu0=4.3)


@dataclass(frozen=True)
class ArcParams:
    enabled: bool = True
    kappa: float = 1.0           # fraction of the lateral cone used to set the turn rate
    lead_max_deg: float = 10.    # the force frame may lead the velocity heading by at most this
    pivot_rate_rad_s: float = 6. # turn rate cap at low speed (stepping round)
    max_turn_per_step_deg: float = 35.  # the next planned foot placement can follow at most this much heading change per stride
    duty_scaled_lateral: bool = True   # lateral demand is delivered in contact only: scale it by the planned stride duty (t_contact / period)
    lateral_gain: float = 10.           # stiffness of the lateral law relative to the duty-scaled time constant (>1 saturates the cone with a small lead)
    tau_floor_s: float = .01           # floor on the lateral time constant
    v_floor_m_s: float = 1.5     # below this speed the velocity heading is not used


def _wrap(a):
    return (a + pi) % (2 * pi) - pi


class Sim(v34.Sim):
    def __init__(self, p, settings=None, params=None, condition=None, fatigue=None, v_ref=None, speed_map=None, arc=None):
        self.arc = arc or ArcParams()
        params = params or STANDARD35
        self._base_lat_tau = params.lateral_tau_s
        super().__init__(p, settings, params, condition, fatigue, v_ref, speed_map)

    def reset(self, speed):
        super().reset(speed)
        if self.arc.enabled and speed > 1e-9:
            self.turned = False                # the frame rotates after the command; a moving athlete starts along its velocity

    def _plan_stance(self, first=False):
        super()._plan_stance(first)
        if self.arc.enabled and self.arc.duty_scaled_lateral:
            duty = self.t_c / max(self.t_c + self.t_f, 1e-3)
            self.q = replace(self.q, lateral_tau_s=max(self.arc.tau_floor_s, self._base_lat_tau * duty / self.arc.lateral_gain))

    def _rederive(self):
        super()._rederive()
        self.d['lateral_peak_N'] = self.d['tan_psi_lat'] * self.d['peak_vertical_force_N']

    def _rotate_frame(self, h):
        s, a = self.s, self.arc
        psi = atan2(self.ud[1], self.ud[0])
        d = _wrap(radians(s.turn_degrees) - psi)
        if abs(d) < 1e-9: return
        v = self._speed()
        w = a.pivot_rate_rad_s
        if v > a.v_floor_m_s:
            w = min(w, a.kappa * self.d['tan_psi_lat'] * G / v)
        w = min(w, radians(a.max_turn_per_step_deg) / max(self.t_c + self.t_f, .05))
        step = copysign(min(abs(d), w * h), d)
        new = psi + step
        if v > a.v_floor_m_s:
            pv = atan2(self.vy, self.vx)
            lead = _wrap(new - pv)
            if abs(lead) > radians(a.lead_max_deg) and lead * d > 0:
                new = pv + copysign(radians(a.lead_max_deg), lead)
                if (new - psi) * d < 0: new = psi
        self.ud = (cos(new), sin(new))

    def advance(self, h):
        if self.arc.enabled and not self.turned and self.t >= self.s.turn_time_s - 1e-12:
            self.turned = True                 # keep the current frame; it is rotated below instead of flipped
        if self.arc.enabled and self.turned:
            self._rotate_frame(h)
        return super().advance(h)


# ---- copy of v3.2 Sim._horizontal_force with ONE change: the lateral muscle cap (see the marked line)
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
            Ff = min(max(Ff, -d['brake_peak_N']), cap_f)
        else:                                            # brake to rest
            Ff = min(max(m * (0. - vpar) / self.q.effort_tau_s, -d['brake_peak_N']), 0.)
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


def run(p, speed=0., settings=None, params=None, condition=None, fatigue=None, v_ref=None, sample_dt=.05, speed_map=None, arc=None):
    s = settings or Settings(duration_s=12.)
    sim = Sim(p, s, params, condition, fatigue, v_ref, speed_map, arc)
    summ = v34.run_sim(sim, speed, sample_dt)
    return summ, v34.run_sim.samples
