"""Beastball Physical Standard v3.2 - validation/calibration milestone (experimental reduced-order model, SI units).

v3.1 is kept byte-identical in beastball_locomotion_v31.py and is the baseline.  What v3.2 changes (register in the report):
  1. Ratings are absolute: gait kinematics (swing speed, force-velocity scale, sweep) are built from a REFERENCE body
     (2.54 m / 180 kg) and aerodynamic drag area scales with mass, so top speed depends on the four ratings only (mass: exactly;
     height: a weak residual of ~1 % per 0.5 m is documented).  Height and mass still act through leg length/reach, momentum,
     vertical force in bodyweights and anatomy.
  2. Contact='spring' (default): compliant SLIP-type leg; the normal force EMERGES from leg compression (RK4, 1 ms substeps,
     force-unload / full-extension lift-off located by bisection).  Stiffness is sized from the planned impulse and stride
     geometry, learned stride to stride; vertical damping ratio zeta; extensor rebound servo.  contact='halfsine' (v3.1 prescribed
     force) is kept as an ablation/legacy option with its own calibration (halfsine_drive_scale).
  3. Strict anatomy: touchdown geometry z = sqrt(L^2 - s^2) so hip-to-foot reach <= 1.0 L (tolerance 0.5 %), stance leg length is
     capped at 1.0 L (lift-off when fully extended), start-up strides included (v3.1 reached 1.16 L).
  4. Interpretable controller (controller='envelope'): effort follows the gait envelope derived from the same planning equations
     (utilisation of vertical-force capacity versus speed); the v3.1 util/fill band remains as controller='heuristic'.
  5. Posture / lateral-balance limit: ground-force tilt must stay inside an ellipse with semi-axes tan(psi_acc), tan(psi_brk) along
     the heading and tan(psi_lat) across it, anchored to the v1 standard (peak accel 16 m/s^2, braking 22 m/s^2, scaled by ability).
  6. Acceleration is therefore posture-limited (not friction-limited as in v3.1) and is separate from the gait-envelope speed band;
     there is NO energetics/fatigue model, so 'sustainable' running is only a gait-envelope utilisation band.
The only constants fitted to the 100 mph canon are drive_N_per_kg (spring) and halfsine_drive_scale (legacy contact).

Inherited v3.1 docstring follows.

Beastball Physical Standard v3.1 - uncapped, rating-coupled locomotion laboratory.

Status: experimental reduced-order model (SI units).  NOT articulated biomechanics, NOT integrated with Pocket.
Every constant in `Params` is PROVISIONAL.  The only canon-derived number is BENCHMARK_M_S (100 mph), which is used
for REPORTING and for the single calibration of the horizontal force scale; it is never applied to velocity.

What changed relative to v3.0 (full register in the technical report):
  * No velocity clamp or speed governor.  v3.0 commanded vmax = profile.speed_fraction*44.704 m/s; v3.1 commands
    effort (maximal thrust) or a speed target that is only a goal for the controller, never a limit on the state.
  * Terminal / sustainable speed emerges from: Hill-type force-velocity decline of horizontal thrust, aerodynamic
    drag, ground friction (mu*N), vertical force capacity (stride geometry), finite swing-leg speed (foot cycling),
    and the rate of force development (contact-time floor).
  * Swing foot is carried with the body after liftoff (v3.0 left it anchored on the ground, which created a
    spurious 2.6-3.0x body-speed foot requirement).
  * Contact is a force-driven half-sine normal reaction N(t)=A*sin(pi*t/Tc): zero force at touchdown (no onset
    spike), vertical impulse balanced analytically, COM height integrated during stance (leg length checked).
  * Vertical capacity, swing speed, force-velocity scale, contact-time floor and leg length are derived from body
    geometry, mass and ratings (Strength -> force capability, Explosive Power -> leg speed and rate of force
    development).  Keeper vs field differences arise only from height and mass; there is no role multiplier.
  * Events (liftoff, touchdown) are located exactly inside a step, so results converge as dt shrinks.

Reduced-order assumptions that remain (see report): point-mass COM with massless legs of length L; feet on the
COM's line of travel (no lateral stance width); no trunk rotation / lean dynamics (balance is NOT modelled; the GRF
angle is reported); swing-foot clearance height not modelled; half-sine normal-force shape is assumed (v3.1 contact only; v3.2 default has an emergent force).
"""
from dataclasses import dataclass, replace, asdict
from math import sqrt, hypot, sin, cos, pi, atan2, atan, degrees, radians, isfinite
from beastball_physical_standard_v11 import profile, PerformanceProfile
from beastball_physical_standard_v1 import Standard

G = 9.80665
BENCHMARK_M_S = 44.704          # 100 mph: canonical reference for the fastest self-propelled athletes (reporting only)
STD = Standard()
ability = STD.ability           # (0.4+0.6r)/(0.4+0.6*0.7): 1.0 at rating 0.7


@dataclass(frozen=True)
class Params:
    # ---- geometry
    leg_length_height: float = .53     # leg length / standing height (human ~0.52)
    sweep_max_leg: float = .60         # max foot offset ahead/behind COM during stance, as fraction of leg length
    stance_time_c: float = .70         # low-speed contact time scale: tau_c = c*sqrt(L/g)
    sweep_min_leg: float = .05
    trail_tol_leg: float = .05         # swing foot may touch down this far (x L) behind the COM before it counts as a trip
    compression_limit: float = .50     # max leg shortening (fraction of L) before the athlete collapses (v3.1: .40)
    extension_tol: float = .02
    reach_max_leg: float = 1.005       # max hip-to-foot distance at touchdown / leg length (strict; was 1.20 in v3.1)
    # ---- v3.2: ratings are absolute (ruling): gait kinematics use a REFERENCE body, not the athlete's own leg length
    absolute_kinematics: bool = True   # False = v3.1 behaviour (kinematic scales from own leg length)
    drag_per_mass: bool = True         # True: drag area scales with mass (ratings-only top speed); False: CdA = c*h^2 (v3.1)
    ref_height_m: float = 2.54
    ref_mass_kg: float = 180.
    # ---- v3.2 posture/balance limit on the ground-force inclination (horizontal force <= tan(psi) * normal force)
    #      anchored to the v1 standard: peak acceleration 16 m/s^2 * ability(Explosive), peak braking 22 m/s^2 * ability(Traction)
    peak_accel_m_s2: float = STD.peak_acceleration_m_s2
    peak_brake_m_s2: float = STD.peak_braking_m_s2
    lateral_accel_m_s2: float = STD.peak_acceleration_m_s2
    posture_limit: bool = True
    # ---- v3.2 compliant leg (contact='spring'): SLIP-type leg spring along the hip-to-foot line.  Stiffness k is sized per stride from the
    #      planned vertical impulse and the stride geometry (k = k_scale*A/(compression*cos a)); k_scale is learned stride to stride from the
    #      impulse error.  The leg has linear damping on the VERTICAL speed (ratio zeta, tissue dissipation) and an extensor 'rebound servo'
    #      that adds force while the leg re-lengthens until the planned vertical take-off speed is reached (active muscle work).
    min_compression_leg: float = .08   # slow running: compression the leg takes even without geometric shortening (fraction of L)
    rebound_gain: float = 15.0         # push-off servo gain (x 1/t_contact)
    zeta: float = .25                  # leg damping ratio on vertical motion
    damp_ramp_frac: float = .15        # damping force ramps in over this fraction of the planned contact (no impact spike)
    spring_substep_s: float = .001
    k_adapt: float = 1.0               # per-stride learning exponent of the stiffness scale (1 = dead-beat on the impulse ratio)
    # ---- vertical capability  (Strength -> force, Explosive -> rate of force development)
    kappa0: float = 8.0                # peak vertical GRF at ability(strength)=1, in bodyweights
    rfd_s: float = .015                # time-to-peak-force at ability(explosive)=1 (s); contact >= 2x this
    # ---- leg speed (Explosive)
    swing_c: float = 1.0               # minimum full-sweep swing time = c*sqrt(L/g)/ability(explosive)
    fv_froude: float = 20.2            # zero-force leg speed = fv_froude*sqrt(g*L)*ability(explosive); 20.2 = 2x benchmark at rating 1.0
    # ---- horizontal force (Strength)
    drive_N_per_kg: float = 100.62       # peak horizontal thrust at zero leg speed; CALIBRATED so rating 1.0 sustains 100 mph (v17 had 35)
    halfsine_drive_scale: float = 0.6373   # contact='halfsine' (legacy/ablation) has its own calibration of the thrust scale to the 100 mph canon
    brake_N_per_kg: float = 40.        # peak horizontal braking force (v17 value)
    lateral_tau_s: float = .25
    speed_ki: float = .25              # per-stride integral gain of the speed-tracking controller (mode='speed')
    effort_tau_s: float = .35
    # ---- traction (v1 value)
    mu0: float = STD.traction_coefficient
    # ---- external resistance
    air_density: float = 1.2
    cd_area_per_h2: float = .17        # drag area CdA = c*h^2  (1.1 m^2 at 2.54 m; ~0.55 m^2 for a 1.8 m human)
    # ---- controller
    fill_lo: float = .80               # swing completion (landed/target foot offset) at which thrust effort reaches 0
    fill_hi: float = .95               # ... and at which it is back to full effort
    util_lo: float = .85               # vertical-force utilisation (wanted/available peak) below which thrust effort is full
    util_hi: float = .97              # ... and at which it reaches 0 (the athlete senses force saturation and stops accelerating)
    effort_smooth: float = .5          # per-stride low-pass on effort (0..1; 1 = no smoothing)
    flight_floor_s: float = .03
    swing_margin_s: float = .01
    max_flight_s: float = 1.5

    def __post_init__(self):
        for k, v in asdict(self).items():
            if isinstance(v, bool): continue
            if not isfinite(v) or v <= 0:
                raise ValueError(f'{k} must be finite and positive')
        if self.sweep_min_leg >= self.sweep_max_leg or self.sweep_max_leg >= 1:
            raise ValueError('invalid sweep limits')


@dataclass(frozen=True)
class Settings:
    dt: float = .005                   # maximum integration/sampling step; events are located exactly
    duration_s: float = 6.
    mode: str = 'sprint'               # 'sprint' (maximal effort), 'speed' (track target_speed), 'brake' (stop)
    target_speed: float = 0.
    turn_degrees: float = 0.           # commanded heading relative to the initial heading
    turn_time_s: float = 0.            # time at which the heading command switches (0 = from the start)
    traction: float = 1.               # multiplier on mu (surface/footwear), not an athlete rating
    muscle: float = 1.                 # multiplier on horizontal muscle capacity (diagnostic)
    thrust_gain: float = 1.            # multiplier on horizontal force scale used by calibration only
    regulate: bool = True              # gait-feasibility effort regulation (controller); False = ablation (always full effort)
    contact: str = 'spring'            # 'spring' (v3.2: compliant leg, forces emerge from compression) or 'halfsine' (v3.1 prescribed force)
    controller: str = 'envelope'       # 'envelope' (v3.2: feed-forward gait-envelope speed law) or 'heuristic' (v3.1 util/fill band)

    def __post_init__(self):
        if not (0 < self.dt <= .02 and 0 < self.duration_s <= 60 and self.turn_time_s >= 0 and self.traction > 0 and self.muscle > 0 and self.thrust_gain > 0):
            raise ValueError('invalid settings')
        if self.contact not in ('spring', 'halfsine') or self.controller not in ('envelope', 'heuristic') or self.mode not in ('sprint', 'speed', 'brake') or not -180 <= self.turn_degrees <= 180:
            raise ValueError('invalid settings')


def derive(p, params=None, traction=1., muscle=1., thrust_gain=1.):
    """Rating/geometry -> physical capacities (the documented mapping)."""
    q = params or Params()
    a = p.athlete
    L = q.leg_length_height * a.height_m
    Lk = q.leg_length_height * q.ref_height_m if q.absolute_kinematics else L      # kinematic scale length
    abS, abE, abR = ability(a.strength), ability(a.explosive_power), ability(a.traction)
    tau_c = q.stance_time_c * sqrt(Lk / G)
    t_sw = q.swing_c * sqrt(Lk / G) / abE
    d = dict(
        mass_kg=a.mass_kg, height_m=a.height_m, leg_length_m=L,
        ability_strength=abS, ability_explosive=abE, ability_traction=abR,
        kappa_peak_vertical_bw=q.kappa0 * abS,
        peak_vertical_force_N=q.kappa0 * abS * a.mass_kg * G,
        rfd_time_to_peak_s=q.rfd_s / abE,
        swing_time_full_sweep_s=t_sw,
        swing_rel_speed_m_s=2 * q.sweep_max_leg * Lk / t_sw, kin_length_m=Lk,
        fv_zero_force_speed_m_s=q.fv_froude * sqrt(G * Lk) * abE,
        thrust_peak_N=q.drive_N_per_kg * thrust_gain * muscle * a.mass_kg * abS,
        brake_peak_N=q.brake_N_per_kg * muscle * a.mass_kg * abS,
        mu=q.mu0 * abR * traction,
        tan_psi_acc=(q.peak_accel_m_s2 * abE / G) if q.posture_limit else 1e9,
        tan_psi_brk=(q.peak_brake_m_s2 * abR / G) if q.posture_limit else 1e9,
        tan_psi_lat=(q.lateral_accel_m_s2 * abE / G) if q.posture_limit else 1e9,
        drag_area_m2=(q.cd_area_per_h2 * q.ref_height_m ** 2 * a.mass_kg / q.ref_mass_kg) if q.drag_per_mass else q.cd_area_per_h2 * a.height_m ** 2,
        tau_c_s=tau_c, sweep_max_m=q.sweep_max_leg * Lk, sweep_min_m=q.sweep_min_leg * Lk,
        fv_froude=q.fv_froude)
    return d


def _unit(x, y, fallback=(1., 0.)):
    n = hypot(x, y)
    return (x / n, y / n) if n > 1e-9 else fallback


class Sim:
    """Mutable single-athlete simulation.  Deterministic; no random numbers."""

    def __init__(self, p, settings=None, params=None):
        self.p = p
        self.s = settings or Settings()
        self.q = params or Params()
        self.d = derive(p, self.q, self.s.traction, self.s.muscle, self.s.thrust_gain * (self.q.halfsine_drive_scale if self.s.contact == 'halfsine' else 1.))
        self.m = p.athlete.mass_kg
        self.L = self.d['leg_length_m']
        self.v_env_lo, self.v_env_hi = self.gait_envelope()
        self.reset(0.)

    # ------------------------------------------------------------------ setup
    def reset(self, speed):
        if not isfinite(speed) or speed < 0:
            raise ValueError('invalid start speed')
        s = self.s
        self.t = 0.
        self.turned = s.turn_time_s <= 0
        a0 = radians(s.turn_degrees) if self.turned else 0.
        self.ud = (cos(a0), sin(a0))
        # an athlete at rest simply faces the commanded direction; a moving athlete keeps its velocity heading (+x)
        self.head = self.ud if speed <= 1e-9 else (1., 0.)
        self.x = self.y = 0.
        self.vx, self.vy = speed * self.head[0], speed * self.head[1]
        self.fallen = False; self.reason = ''
        self.phase = 'stance'
        self.ts = 0.
        sh = self._half_sweep(speed)
        self.uf = self.head
        self.fx, self.fy = sh * self.head[0], sh * self.head[1]   # support foot ahead of COM
        self.z = sqrt(self.L ** 2 - sh ** 2); self.vz = 0.
        self.r_after = None
        self.r_next = (-sh * self.head[0], -sh * self.head[1])     # placeholder; set from the planned flight below
        self.max_ext = 0.; self.min_leg = 1.; self.reach_sum = 0.; self.reach_n = 0
        self.vz_td = 0.; self.f_int = 0.; self.k_scale = 1.; self.L_rest = self.L; self.N_now = 0.; self.k_leg = 0.; self.c_leg = 0.; self.x_comp = 0.; self.stance_peak_comp = 0.
        # counters / metrics
        self.touchdowns = 0; self.liftoffs = 0
        self.energy_work = dict(ground=0., drag=0., ground_pos=0.)
        self.e0 = None
        self.peak_lat_tilt = 0.; self.max_comp = 0.; self.peak_N = 0.; self.peak_Fh = 0.; self.peak_grf_angle = 0.
        self.slip_impulse = 0.
        self.peak_speed = speed; self.peak_foot_ground = 0.; self.peak_foot_rel = 0.
        self.steps = []          # per-stride records
        self.cur = dict(t_td=0., x_td=0., y_td=0., v_td=speed)
        self.flight_t = 0.
        self.effort = 1.; self.fill = 1.; self.util_v = 0.
        self.z_to = self.z
        self.imp_stance = 0.
        self.t_c = 0.; self.t_force = 0.; self.A = 0.
        self._plan_stance(first=True)
        # the foot that lands next has already been swinging for one flight: start it where it would be in steady gait
        adv = min(2 * sh, self.d['swing_rel_speed_m_s'] * self.t_f)
        self.r_next = ((-sh + adv) * self.head[0], (-sh + adv) * self.head[1])
        self.e0 = self._energy()

    # ------------------------------------------------------- gait envelope (v3.2)
    def util_steady(self, v):
        """Vertical-force utilisation A/(kappa m g) the steady symmetric gait would need at speed v (same planning equations as
        the stance planner with zero acceleration)."""
        d = self.d
        sh = self._half_sweep(v)
        t_c = min(max(2 * sh / max(v, .5), .008), 1.5 * d['tau_c_s'])
        t_f = self._nominal_flight(sh, t_c)
        T_F = max(t_c, 2 * d['rfd_time_to_peak_s'])
        denom = T_F * (1 - cos(pi * t_c / T_F)) / pi
        return (t_f + t_c) / (denom * d['kappa_peak_vertical_bw'])

    def gait_envelope(self):
        """Speeds at which the steady gait needs util_lo / util_hi of the athlete's vertical force capacity (bisection)."""
        def solve(u):
            lo, hi = .5, 4 * self.d['fv_zero_force_speed_m_s']
            if self.util_steady(hi) < u: return hi
            for _ in range(60):
                mid = .5 * (lo + hi)
                if self.util_steady(mid) < u: lo = mid
                else: hi = mid
            return .5 * (lo + hi)
        return solve(self.q.util_lo), solve(self.q.util_hi)

    # ----------------------------------------------------------- small helpers
    def _speed(self): return hypot(self.vx, self.vy)
    def _energy(self): return .5 * self.m * (self.vx ** 2 + self.vy ** 2 + self.vz ** 2) + self.m * G * self.z

    def _half_sweep(self, v):
        d = self.d
        return min(d['sweep_max_m'], max(d['sweep_min_m'], v * d['tau_c_s'] / 2))

    def _drag(self):
        v = self._speed()
        k = .5 * self.q.air_density * self.d['drag_area_m2'] * v
        return (-k * self.vx, -k * self.vy)

    # --------------------------------------------------------------- planning
    def _plan_stance(self, first=False):
        """Called at touchdown: sets contact duration, normal-force amplitude and the flight the controller aims for."""
        d, q, m = self.d, self.q, self.m
        D = (self.x - self.fx, self.y - self.fy)
        dist = hypot(*D)
        self.d_front = dist
        v0 = self._speed()
        if self.s.mode == 'speed':        # integral action: removes the steady speed error left by dissipation (per stride, anti-windup)
            ud = self.ud
            vpar0 = self.vx * ud[0] + self.vy * ud[1]
            self.f_int += self.q.speed_ki * m * (self.s.target_speed - vpar0) / self.q.effort_tau_s
            self.f_int = min(max(self.f_int, -d['brake_peak_N']), d['thrust_peak_N'])
        a_exp = self._expected_accel()
        # contact lasts until the COM has travelled 2*dist (foot goes from `dist` ahead to `dist` behind):
        #   v0*t + a*t^2/2 = 2*dist
        if abs(a_exp) < 1e-6:
            t_geo = 2 * dist / max(v0, .5)
        else:
            disc = v0 * v0 + 4 * a_exp * dist
            t_geo = (-v0 + sqrt(disc)) / a_exp if disc >= 0 else 2 * dist / max(v0, .5)
        vpar = max(v0, .5)
        self.t_c = min(max(t_geo, .008), 1.5 * d['tau_c_s'])
        self.t_force = max(self.t_c, 2 * d['rfd_time_to_peak_s'])
        # Flight: the foot that lands after the next one needs a full sweep (2*s_h) over (flight + this stance + next flight),
        # so the controller schedules t_f = (t_sweep - t_c)/2 (+margin).  This is a feed-forward plan from speed, not a reaction
        # to the last foot error (a reactive plan made the gait chaotic in the first prototype).
        self.t_f = self._nominal_flight(self._half_sweep(v0), self.t_c)
        vz_td = self.vz if not first else -G * self.t_f / 2
        if first: self.vz = vz_td
        self._set_amplitude(vz_td)
        self._set_spring()

    def _set_spring(self):
        m, q = self.m, self.q
        om = pi / max(self.t_c, 1e-3)
        # SLIP geometry: the contact time is set by the horizontal travel, the leg is compressed geometrically by L(1-cos a)
        # at mid-stance (a = leg half-angle), so the stiffness that delivers the planned vertical impulse (peak A of the
        # half-sine equivalent) is k = A / (L (1-cos a) cos a); k_scale is learned per stride from the impulse error.
        sa = min(.95, max(.02, self._half_sweep(self._speed()) / self.L))
        ca = sqrt(1 - sa * sa)
        self.k_leg = self.k_scale * max(self.A, .5 * self.m * G) / (max(self.L * (1 - ca), q.min_compression_leg * self.L) * ca)
        ltd = hypot(hypot(self.x - self.fx, self.y - self.fy), self.z)
        self.L_rest = min(self.L, ltd)                      # leg lands unloaded: rest length = length at touchdown (no pre-load)
        self.c_leg = 2 * q.zeta * m * om
        self.stance_peak_comp = 0.

    def _set_amplitude(self, vz_td):
        d, m = self.d, self.m
        self.vz_td = vz_td
        vz_to = G * self.t_f / 2
        J = m * (vz_to - vz_td) + m * G * self.t_c               # required vertical impulse over the stance
        denom = self.t_force * (1 - cos(pi * self.t_c / self.t_force)) / pi
        A = J / denom
        self.A = max(0., min(A, d['peak_vertical_force_N']))
        self.A_wanted = A
        self.util_v = A / max(d['peak_vertical_force_N'], 1e-9)
        if self.s.regulate:
            q = self.q
            if self.s.controller == 'envelope':
                eu = min(1., max(0., (self.v_env_hi - self._speed()) / max(self.v_env_hi - self.v_env_lo, 1e-9)))
            else:
                eu = min(1., max(0., (q.util_hi - self.util_v) / (q.util_hi - q.util_lo)))
            ef = min(1., max(0., (self.fill - q.fill_lo) / (q.fill_hi - q.fill_lo)))
            tgt = min(eu, ef)
            self.effort += (tgt - self.effort) * q.effort_smooth
        self.ts = 0.

    def _nominal_flight(self, s_half, t_c):
        q, d = self.q, self.d
        t_sweep = 2 * s_half / d['swing_rel_speed_m_s']
        return min(max(q.flight_floor_s, (t_sweep - t_c) / 2 + q.swing_margin_s), q.max_flight_s)

    def _nominal_cycle(self, v):
        sh = self._half_sweep(v)
        t_c = min(max(2 * sh / max(v, .5), .008), 1.5 * self.d['tau_c_s'])
        return t_c, self._nominal_flight(sh, t_c)

    def _swing_target(self, v):
        sh = self._half_sweep(v)
        return (sh * self.uf[0], sh * self.uf[1])

    def _expected_accel(self):
        """Controller's forecast of horizontal acceleration during the coming stance (used only to time contact)."""
        d, m, s = self.d, self.m, self.s
        ud = self.ud
        vpar = self.vx * ud[0] + self.vy * ud[1]
        cap_f = d['thrust_peak_N'] * max(0., 1 - max(vpar, 0.) / d['fv_zero_force_speed_m_s']) * self.effort
        if s.mode == 'sprint': Ff = cap_f
        elif s.mode == 'speed': Ff = min(max(m * (s.target_speed - vpar) / self.q.effort_tau_s + self.f_int, -d['brake_peak_N']), cap_f)
        else: Ff = min(max(m * (0. - vpar) / self.q.effort_tau_s, -d['brake_peak_N']), 0.)
        if s.contact == 'spring':        # posture cone: horizontal force <= tan(psi)*N, N ~ mean of the (previous) half-sine
            Ff = min(Ff, d['tan_psi_acc'] * max(2 * self.A / pi, m * G))
        a = .85 * Ff / m          # thrust is partly limited by mu*N near touchdown/liftoff where the half-sine N is small
        dr = self._drag()
        a += (dr[0] * ud[0] + dr[1] * ud[1]) / m
        return a

    # ----------------------------------------------------------------- forces
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
        lat_cap = d['thrust_peak_N']
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

    # ------------------------------------------------------------- integration
    def _swing_update(self, tau, T_next, T_after):
        """Move both swing feet (relative to COM) toward the planned touchdown offset so they arrive on schedule, at no more
        than the finite relative swing speed.  T_* = time remaining (before this step) until each foot is due to land."""
        d = self.d
        vmax_rel = d['swing_rel_speed_m_s']
        tgt = self._swing_target(self._speed())
        for name, T in (('r_next', T_next), ('r_after', T_after)):
            r = getattr(self, name)
            if r is None: continue
            dx, dy = tgt[0] - r[0], tgt[1] - r[1]
            dist = hypot(dx, dy)
            want = dist   # greedy: arrive as early as the finite swing speed allows, then hover at the target
            step = min(want, vmax_rel * tau)
            nr = (r[0] + dx / dist * step, r[1] + dy / dist * step) if dist > 1e-12 else r
            rel = step / tau if tau > 0 else 0.
            self.peak_foot_rel = max(self.peak_foot_rel, rel)
            if tau > 0 and dist > 1e-12:
                gv = hypot(self.vx + dx / dist * step / tau, self.vy + dy / dist * step / tau)
                self.peak_foot_ground = max(self.peak_foot_ground, gv)
            setattr(self, name, nr)

    def _stance_sub(self, tau):
        d, m, q = self.d, self.m, self.q
        t0, t1 = self.ts, self.ts + tau
        T_next = (self.t_c - self.ts) + self.t_f
        tf, A, tc = self.t_force, self.A, self.t_c
        def Nof(t): return A * sin(pi * t / tf) if 0 <= t <= tc + 1e-12 else 0.
        # vertical (analytic impulse, exact for the half-sine)
        c0, c1 = cos(pi * t0 / tf), cos(pi * t1 / tf)
        vN = (A * tf / (pi * m)) * (c0 - c1)
        zN = (A * tf / (pi * m)) * (tau * c0 - (tf / pi) * (sin(pi * t1 / tf) - sin(pi * t0 / tf)))
        vz1 = self.vz + vN - G * tau
        z1 = self.z + self.vz * tau - .5 * G * tau * tau + zN
        # horizontal: explicit midpoint
        D0 = (self.x - self.fx, self.y - self.fy)
        dr0 = self._drag()
        N0 = Nof(t0)
        Fx, Fy, _, _ = self._horizontal_force(N0, D0[0], D0[1], self.z, self.vx, self.vy)
        a0 = ((Fx + dr0[0]) / m, (Fy + dr0[1]) / m)
        vxm, vym = self.vx + .5 * tau * a0[0], self.vy + .5 * tau * a0[1]
        xm, ym = self.x + .5 * tau * self.vx, self.y + .5 * tau * self.vy
        zm = .5 * (self.z + z1)
        Nm = Nof(t0 + .5 * tau)
        sp = self.vx, self.vy
        self.vx, self.vy = vxm, vym                      # drag at midpoint velocity
        drm = self._drag()
        self.vx, self.vy = sp
        Fx, Fy, slip, act = self._horizontal_force(Nm, xm - self.fx, ym - self.fy, zm, vxm, vym)
        ax, ay = (Fx + drm[0]) / m, (Fy + drm[1]) / m
        vx1, vy1 = self.vx + ax * tau, self.vy + ay * tau
        x1, y1 = self.x + .5 * (self.vx + vx1) * tau, self.y + .5 * (self.vy + vy1) * tau
        # work bookkeeping (independent Gauss-2 quadrature for the vertical term)
        wv = 0.
        for g_ in (-1 / sqrt(3), 1 / sqrt(3)):
            tt = t0 + .5 * tau * (1 + g_)
            cc = cos(pi * tt / tf)
            vzt = self.vz + (A * tf / (pi * m)) * (c0 - cc) - G * (tt - t0)
            wv += .5 * tau * Nof(tt) * vzt
        wh = (Fx * (self.vx + vx1) * .5 + Fy * (self.vy + vy1) * .5) * tau
        self.energy_work['ground'] += wv + wh
        self.energy_work['ground_pos'] += max(wv + wh, 0.)
        self.energy_work['drag'] += (drm[0] * (self.vx + vx1) * .5 + drm[1] * (self.vy + vy1) * .5) * tau
        self.imp_stance += (A * tf / pi) * (c0 - c1) if t1 <= tc + 1e-12 else 0.
        # commit
        self.x, self.y, self.vx, self.vy, self.z, self.vz = x1, y1, vx1, vy1, z1, vz1
        self.ts = t1; self.t += tau
        N1 = Nof(t1)
        self.peak_N = max(self.peak_N, N1, Nm)
        fh = hypot(Fx, Fy)
        self.peak_Fh = max(self.peak_Fh, fh)
        if Nm > 1e-6 * m * G: self.peak_grf_angle = max(self.peak_grf_angle, degrees(atan2(fh, Nm)))
        self.slip_impulse += slip * tau
        # geometry checks
        D1 = (self.x - self.fx, self.y - self.fy)
        leg = hypot(hypot(*D1), self.z)
        self.max_ext = max(self.max_ext, leg / self.L)
        self.min_leg = min(self.min_leg, leg / self.L)
        if leg / self.L < 1 - self.q.compression_limit:
            self._fall('landing_travel_exceeded')
        self._swing_update(tau, T_next, None)


    # ------------------------------------------------------------ compliant leg (v3.2)
    def _spring_forces(self, st, ts):
        """Forces for state st=(x,y,z,vx,vy,vz) at stance time ts.  Returns (ax, ay, az, N, Fh, slip, Fx, Fy, dragx, dragy)."""
        x, y, z, vx, vy, vz = st
        m, q, d = self.m, self.q, self.d
        ex, ey = x - self.fx, y - self.fy
        l = max(sqrt(ex * ex + ey * ey + z * z), 1e-6)
        ldot = (ex * vx + ey * vy + z * vz) / l
        ramp = min(1., ts / max(q.damp_ramp_frac * self.t_c, 1e-4))
        ez = max(z / l, 1e-3)
        F = self.k_leg * (self.L_rest - l) - self.c_leg * ramp * vz / ez
        F = max(F, 0.)
        # rebound servo: while the leg is lengthening, the extensor muscles add force until the vertical take-off speed
        # planned for this stride is reached (active push-off; its work is booked as ground work in the energy audit)
        rb = min(1., max(0., (vz + .1) / .3))
        if rb > 0. and F > 0.:                  # only while the leg is still compressed - a leg at rest length lifts off
            err = G * self.t_f / 2 - vz         # + : push harder; - : the extensors relax (excess take-off speed is shed)
            F = max(F + rb * m * q.rebound_gain * err / (max(self.t_c, 1e-3) * ez), 0.)
        if F * ez > d['peak_vertical_force_N']:
            F = d['peak_vertical_force_N'] / max(ez, 1e-3)          # muscle force capacity (leg yields beyond it)
        N = F * ez
        Fx, Fy, slip, _ = self._horizontal_force(N, ex, ey, z, vx, vy)
        sp = self.vx, self.vy
        self.vx, self.vy = vx, vy
        dr = self._drag()
        self.vx, self.vy = sp
        ax, ay = (Fx + dr[0]) / m, (Fy + dr[1]) / m
        az = N / m - G
        return ax, ay, az, N, hypot(Fx, Fy), slip, Fx, Fy, dr[0], dr[1], F, l

    def _rk4_stance(self, h):
        """One RK4 step of the stance dynamics from the current state; returns (new_state, work_ground, work_drag, extras)."""
        st = (self.x, self.y, self.z, self.vx, self.vy, self.vz)
        ts = self.ts
        def f(s_, t_):
            ax, ay, az, N, Fh, slip, Fx, Fy, dx, dy, F, l = self._spring_forces(s_, t_)
            return (s_[3], s_[4], s_[5], ax, ay, az), (N, Fh, slip, Fx, Fy, dx, dy, F, l)
        def add(a, b, c): return tuple(ai + c * bi for ai, bi in zip(a, b))
        k1, e1 = f(st, ts)
        k2, e2 = f(add(st, k1, h / 2), ts + h / 2)
        k3, e3 = f(add(st, k2, h / 2), ts + h / 2)
        k4, e4 = f(add(st, k3, h), ts + h)
        new = tuple(st[i] + h / 6 * (k1[i] + 2 * k2[i] + 2 * k3[i] + k4[i]) for i in range(6))
        # power of ground force and drag along the RK4 stages (consistent with the integrator order)
        wg = wd = 0.
        for wgt, k_, e_, s_ in ((1, k1, e1, st), (2, k2, e2, add(st, k1, h / 2)), (2, k3, e3, add(st, k2, h / 2)), (1, k4, e4, add(st, k3, h))):
            N, Fh, slip, Fx, Fy, dx, dy, F, l = e_
            vx_, vy_, vz_ = s_[3], s_[4], s_[5]
            wg += wgt * (Fx * vx_ + Fy * vy_ + N * vz_)
            wd += wgt * (dx * vx_ + dy * vy_)
        wg *= h / 6; wd *= h / 6
        return new, wg, wd, e1, e4

    def _commit_stance(self, new, wg, wd, e0, e1, h):
        self.x, self.y, self.z, self.vx, self.vy, self.vz = new
        self.ts += h; self.t += h
        self.energy_work['ground'] += wg
        self.energy_work['ground_pos'] += max(wg, 0.)
        self.energy_work['drag'] += wd
        N = e1[0]
        self.N_now = N
        self.imp_stance += .5 * (e0[0] + e1[0]) * h
        self.peak_N = max(self.peak_N, N, e0[0])
        self.peak_Fh = max(self.peak_Fh, e1[1])
        if N > 1e-6 * self.m * G: self.peak_grf_angle = max(self.peak_grf_angle, degrees(atan2(e1[1], N)))
        self.slip_impulse += e1[2] * h
        l = e1[8]
        self.max_ext = max(self.max_ext, l / self.L)
        self.min_leg = min(self.min_leg, l / self.L)
        self.stance_peak_comp = max(self.stance_peak_comp, self.L - l)
        self.max_comp = max(self.max_comp, self.L - l)
        if l / self.L < 1 - self.q.compression_limit:
            self._fall('landing_travel_exceeded')

    def _stance_spring(self, rem):
        """Integrate the compliant-leg stance for up to `rem` seconds; returns (time used, lifted_off)."""
        q = self.q
        used = 0.
        lifted = False
        while used < rem - 1e-12 and not self.fallen:
            h = min(q.spring_substep_s, rem - used)
            snap = self._snapshot()
            e0 = self._spring_forces((self.x, self.y, self.z, self.vx, self.vy, self.vz), self.ts)
            e0 = (e0[3], e0[4], e0[5], e0[6], e0[7], e0[8], e0[9], e0[10], e0[11])
            new, wg, wd, _, e1 = self._rk4_stance(h)
            Fend = e1[7]
            unload = ((Fend <= 1e-9 and self.ts + h > .2 * self.t_c) or e1[8] >= self.L)     # force gone, or leg fully extended
            if unload:
                # locate the instant the leg force reaches zero by bisection on the sub-step length
                lo, hi = 0., h
                for _ in range(40):
                    mid = .5 * (lo + hi)
                    sn = self._snapshot()
                    nw, _, _, _, ee = self._rk4_stance(mid)
                    self._restore(sn)
                    if ee[7] > 1e-9 and ee[8] < self.L: lo = mid
                    else: hi = mid
                h = max(lo, 1e-9)
                new, wg, wd, _, e1 = self._rk4_stance(h)
                lifted = True
            self._commit_stance(new, wg, wd, e0, e1, h)
            self._swing_update(h, (self.t_c - self.ts) + self.t_f, None)
            used += h
            if lifted or self.fallen: break
            if self.ts > 4 * max(self.t_c, .05):
                self._fall('stuck_in_stance'); break
        return used, lifted

    def _adapt_spring(self):
        """Per-stride learning at lift-off: scale the stiffness by the ratio of required to achieved vertical impulse."""
        q = self.q
        vz_t = G * self.t_f / 2
        got = self.vz - self.vz_td + G * self.ts
        need = vz_t - self.vz_td + G * self.ts
        if got > .05 and need > .02:
            r = min(2., max(.5, need / got))
            self.k_scale = min(6., max(.2, self.k_scale * r ** q.k_adapt))
        elif got <= .05:
            self.k_scale = min(6., self.k_scale * 1.3)

    def _flight_sub(self, tau):
        m = self.m
        tt = self._time_to_touchdown()
        if tt is None: tt = max(self.vz, 0.) / G
        tc_n, tf_n = self._nominal_cycle(self._speed())
        T_next, T_after = tt, tt + tc_n + tf_n
        dr = self._drag()
        sp = self._speed()
        vx1, vy1 = self.vx + dr[0] / m * tau, self.vy + dr[1] / m * tau
        # one midpoint refinement for drag
        self.vx, self.vy, vx0, vy0 = (self.vx + vx1) / 2, (self.vy + vy1) / 2, self.vx, self.vy
        drm = self._drag()
        self.vx, self.vy = vx0, vy0
        vx1, vy1 = self.vx + drm[0] / m * tau, self.vy + drm[1] / m * tau
        self.energy_work['drag'] += (drm[0] * (self.vx + vx1) * .5 + drm[1] * (self.vy + vy1) * .5) * tau
        self.x += .5 * (self.vx + vx1) * tau; self.y += .5 * (self.vy + vy1) * tau
        self.vx, self.vy = vx1, vy1
        self.z += self.vz * tau - .5 * G * tau * tau
        self.vz -= G * tau
        self.t += tau
        self._swing_update(tau, T_next, T_after)
        self.flight_t += tau

    # ------------------------------------------------------------------ events
    def _phi(self):
        """>0 once the foot is further behind the COM than it was ahead at touchdown (symmetric sweep) or the leg is over-extended."""
        dpar = (self.x - self.fx) * self.uf[0] + (self.y - self.fy) * self.uf[1]
        return max(self._leg_ratio() - 1.0, (dpar - self.d_front) / self.L)

    def _leg_ratio(self):
        return hypot(hypot(self.x - self.fx, self.y - self.fy), self.z) / self.L

    def _past_midstance(self):
        return (self.x - self.fx) * self.uf[0] + (self.y - self.fy) * self.uf[1] > 0.

    def _snapshot(self):
        sn = dict(self.__dict__)
        sn['energy_work'] = dict(self.energy_work)
        return sn

    def _restore(self, sn):
        self.__dict__.clear(); self.__dict__.update(sn)
        self.energy_work = dict(sn['energy_work'])

    def _fall(self, reason):
        self.fallen = True; self.reason = reason; self.phase = 'fall'

    def _liftoff(self):
        D = (self.x - self.fx, self.y - self.fy)
        self.liftoffs += 1
        rec = dict(t_td=self.cur['t_td'], t_lo=self.t, x_td=self.cur['x_td'], x_lo=self.x,
                   contact_s=self.t - self.cur['t_td'], impulse=self.imp_stance,
                   v_td=self.cur['v_td'], v_lo=self._speed(), A_wanted=self.A_wanted, A=self.A,
                   impulse_planned=None)
        self.cur['rec'] = rec
        self.r_after = (-D[0], -D[1])
        # strict anatomy: the next foot lands with the leg fully extended, i.e. when the COM has descended to the height at
        # which a straight leg of length L reaches the planned foot offset (v3.1 landed at the lift-off height and let the leg overreach)
        sh_n = self._half_sweep(self._speed())
        self.z_to = sqrt(max(self.L ** 2 - sh_n ** 2, (.2 * self.L) ** 2))
        rec['lift_reason'] = self.lift_reason
        if self.s.contact == 'spring': self._adapt_spring()
        self.phase = 'flight'; self.flight_t = 0.
        self.fx = self.fy = None
        self.imp_stance = 0.; self.N_now = 0.

    def _touchdown(self):
        r = self.r_next
        uf = self.uf
        if r[0] * uf[0] + r[1] * uf[1] < -self.q.trail_tol_leg * self.L:
            self._fall('missed_touchdown'); return
        reach = hypot(hypot(*r), self.z) / self.L
        self.max_ext = max(self.max_ext, reach)
        if reach > self.q.reach_max_leg:
            self._fall('overreach'); return
        self.reach_sum += reach; self.reach_n += 1
        self.touchdowns += 1
        tgt = self._half_sweep(self._speed())
        self.fill = min(1., max(0., (r[0] * uf[0] + r[1] * uf[1]) / tgt))
        self.fx, self.fy = self.x + r[0], self.y + r[1]
        self.phase = 'stance'
        v = self._speed()
        self.uf = _unit(self.vx + .5 * v * (self.ud[0] if self.turned else 0.),
                        self.vy + .5 * v * (self.ud[1] if self.turned else 0.), self.uf)
        rec = self.cur.get('rec')
        if rec is not None:
            rec['flight_s'] = self.t - rec['t_lo']
            rec['step_length_m'] = hypot(self.x - self.cur['x_td'], self.y - self.cur['y_td'])
            rec['period_s'] = self.t - self.cur['t_td']
            self.steps.append(rec)
        self.cur = dict(t_td=self.t, x_td=self.x, y_td=self.y, v_td=v)
        self.r_next, self.r_after = self.r_after, None
        if self.r_next is None:
            self.r_next = (-self._half_sweep(v) * self.uf[0], -self._half_sweep(v) * self.uf[1])
        vz_td = self.vz
        self._plan_stance(first=False)
        self._set_amplitude(vz_td)

    def _time_to_touchdown(self):
        """Exact ballistic time until the COM returns to its takeoff height (symmetric flight); None if it cannot (apex below)."""
        z, vz = self.z, self.vz
        zt = self.z_to
        disc = vz * vz + 2 * G * (z - zt)
        if disc < 0:
            return None
        return max((vz + sqrt(disc)) / G, 0.)

    def advance(self, h):
        if not self.turned and self.t >= self.s.turn_time_s - 1e-12:
            self.turned = True
            a0 = radians(self.s.turn_degrees); self.ud = (cos(a0), sin(a0))
        rem = h
        guard = 0
        td0 = self.touchdowns
        while rem > 1e-12 and not self.fallen:
            guard += 1
            if guard > 100000 or self.touchdowns - td0 > 200: self._fall('degenerate_gait'); break
            if self.phase == 'stance' and self.s.contact == 'spring':
                used, lifted = self._stance_spring(rem)
                rem -= used
                if self.fallen: break
                if lifted:
                    self.lift_reason = 'unload'; self._liftoff()
                continue
            if self.phase == 'stance':
                to_lo = self.t_c - self.ts
                tau = min(rem, to_lo)
                lift = False
                if tau > 1e-12:
                    snap = self._snapshot(); l0 = self._phi()
                    self._stance_sub(tau)
                    l1 = self._phi()
                    if l1 > 0. and self._past_midstance():
                        # symmetric sweep reached (or leg fully extended) inside this step: locate the liftoff exactly
                        self._restore(snap)
                        f = 0. if l0 >= 0. else min(1., max(0., (0. - l0) / (l1 - l0)))
                        tau *= f
                        if tau > 1e-12: self._stance_sub(tau)
                        lift = True; self.lift_reason = 'sweep'
                rem -= tau
                if self.fallen: break
                if lift or self.ts >= self.t_c - 1e-10:
                    if not lift: self.lift_reason = 'time'
                    self._liftoff()
            else:
                tt = self._time_to_touchdown()
                if tt is None:                        # apex lower than touchdown height: land at apex
                    tt = max(self.vz, 0.) / G
                tau = min(rem, tt)
                if tau > 1e-12: self._flight_sub(tau)
                rem -= tau
                if tau >= tt - 1e-12 and not self.fallen:
                    self._touchdown()
                elif self.flight_t > self.q.max_flight_s:
                    self._fall('stuck_in_flight')
        return not self.fallen


def assess(p, speed, settings=None, params=None, trace=False, sample_dt=None):
    """Run one scenario.  Returns a result dict (and an optional trace)."""
    s = settings or Settings()
    sim = Sim(p, s, params)
    sim.reset(speed)
    tr = []
    n = int(round(s.duration_s / s.dt))
    sdt = sample_dt or s.dt
    t_up = 0.
    next_sample = 0.
    t_elapsed = 0.
    cut = dict(min_speed=None, t_heading=None, v_at_turn=None, t_turn=None)
    for _ in range(n):
        if sim.fallen: break
        sim.advance(s.dt)
        sim.peak_speed = max(sim.peak_speed, sim._speed())
        if sim.turned and s.turn_degrees:
            if cut['t_turn'] is None:
                cut['t_turn'] = sim.t; cut['v_at_turn'] = sim._speed(); cut['min_speed'] = sim._speed()
            cut['min_speed'] = min(cut['min_speed'], sim._speed())
            err = abs((degrees(atan2(sim.vy, sim.vx)) - s.turn_degrees + 180) % 360 - 180)
            if cut['t_heading'] is None and err <= 5. and sim._speed() > .5:
                cut['t_heading'] = sim.t - cut['t_turn']
        if trace and sim.t >= next_sample - 1e-12:
            N = (sim.N_now if s.contact == 'spring' else (sim.A * sin(pi * sim.ts / sim.t_force) if sim.phase == 'stance' and sim.ts <= sim.t_c else 0.)) if sim.phase == 'stance' else 0.
            tr.append(dict(t=round(sim.t, 6), x=sim.x, y=sim.y, z=sim.z, vx=sim.vx, vy=sim.vy, vz=sim.vz,
                           speed=sim._speed(), phase=sim.phase, N=N))
            next_sample += sdt
    return _result(sim, p, speed, s, tr if trace else None, cut)


def _result(sim, p, speed, s, trace, cut=None):
    d = sim.d
    bw = sim.m * G
    steps = sim.steps
    last = steps[-8:] if len(steps) >= 4 else steps
    def mean(key): return sum(r[key] for r in last) / len(last) if last else float('nan')
    period = mean('period_s'); sl = mean('step_length_m')
    e_end = sim._energy()
    w = sim.energy_work
    audit = e_end - sim.e0 - w['ground'] - w['drag']
    sustained = sim._speed()
    liftoff_speed = float('nan')
    if steps:
        liftoff_speed = sum(r['v_lo'] for r in last) / len(last)
        tot_t = sum(r['period_s'] for r in last if r.get('period_s'))
        tot_x = sum(r['step_length_m'] for r in last if r.get('period_s'))
        sustained = tot_x / tot_t if tot_t > 0 else liftoff_speed      # mean ground speed over the last (<=8) strides
    imp_ratio = float('nan')
    if last:
        imp_ratio = sum(r['impulse'] / (bw * r['period_s']) for r in last if r.get('period_s')) / max(1, sum(1 for r in last if r.get('period_s')))
    peak = sim.peak_speed
    res = dict(
        profile=p.label, initial_speed_m_s=speed, mode=s.mode, target_speed_m_s=s.target_speed if s.mode == 'speed' else None,
        turn_degrees=s.turn_degrees, traction_scale=s.traction, dt_s=s.dt, duration_s=s.duration_s,
        elapsed_s=round(sim.t, 5), upright=not sim.fallen, reason=sim.reason,
        x_m=round(sim.x, 4), y_m=round(sim.y, 4), vx_m_s=round(sim.vx, 4), vy_m_s=round(sim.vy, 4),
        speed_end_m_s=round(sim._speed(), 4), speed_peak_m_s=round(peak, 4), sustained_speed_m_s=round(sustained, 4),
        liftoff_speed_m_s=round(liftoff_speed, 4) if liftoff_speed == liftoff_speed else None,
        exceeds_benchmark=peak > BENCHMARK_M_S + 1e-9, benchmark_exceedance_m_s=round(max(0., peak - BENCHMARK_M_S), 4),
        imparted_start_exceeds_benchmark=speed > BENCHMARK_M_S + 1e-9,
        self_propelled_exceedance_m_s=None if speed > BENCHMARK_M_S + 1e-9 else round(max(0., sustained - BENCHMARK_M_S), 4),
        touchdowns=sim.touchdowns, liftoffs=sim.liftoffs,
        step_frequency_hz=round(1 / period, 4) if last and period > 0 else None,
        step_length_m=round(sl, 4) if last else None,
        contact_time_s=round(mean('contact_s'), 5) if last else None,
        flight_time_s=round(mean('flight_s'), 5) if last else None,
        duty_factor=round(mean('contact_s') / period, 4) if last and period > 0 else None,
        peak_normal_N=round(sim.peak_N, 2), peak_normal_bw=round(sim.peak_N / bw, 4),
        peak_horizontal_force_N=round(sim.peak_Fh, 2), peak_grf_angle_deg=round(sim.peak_grf_angle, 2), peak_lateral_tilt_deg=round(degrees(atan(sim.peak_lat_tilt)), 2),
        leg_stiffness_N_m=round(sim.k_leg, 1) if s.contact == 'spring' else None,
        leg_natural_freq_hz=round(sqrt(sim.k_leg / sim.m) / (2 * pi), 3) if s.contact == 'spring' and sim.k_leg > 0 else None,
        peak_leg_compression_m=round(sim.max_comp, 4) if s.contact == 'spring' else None,
        slip_impulse_Ns=round(sim.slip_impulse, 4),
        foot_peak_ground_speed_m_s=round(sim.peak_foot_ground, 3), foot_peak_relative_speed_m_s=round(sim.peak_foot_rel, 3),
        positive_ground_work_J=round(w['ground_pos'], 1), net_ground_work_J=round(w['ground'], 1), drag_work_J=round(w['drag'], 1),
        energy_audit_error_J=round(audit, 4), energy_audit_rel=round(abs(audit) / max(abs(sim.e0) + abs(w['ground']) + abs(w['drag']), 1.), 8),
        vertical_impulse_ratio=round(imp_ratio, 4) if imp_ratio == imp_ratio else None,
        max_leg_extension=round(sim.max_ext, 4), min_leg_ratio=round(sim.min_leg, 4),
        touchdown_reach_mean_leg=round(sim.reach_sum / sim.reach_n, 4) if sim.reach_n else None,
        kappa_cap_bw=round(d['kappa_peak_vertical_bw'], 3), swing_rel_speed_cap_m_s=round(d['swing_rel_speed_m_s'], 3),
        fv_zero_force_speed_m_s=round(d['fv_zero_force_speed_m_s'], 3),
        heading_end_deg=round(degrees(atan2(sim.vy, sim.vx)), 3),
        turn_time_s=s.turn_time_s,
        speed_at_turn_m_s=round(cut['v_at_turn'], 4) if cut and cut['v_at_turn'] is not None else None,
        min_speed_after_turn_m_s=round(cut['min_speed'], 4) if cut and cut['min_speed'] is not None else None,
        time_to_heading_5deg_s=round(cut['t_heading'], 4) if cut and cut['t_heading'] is not None else None)
    if trace is not None:
        return res, trace
    return res


def rated(rating, role='field', **over):
    """Profile with every athlete rating set to `rating` (0..1) - used for calibration and rating sweeps."""
    from beastball_physical_standard_v1 import Athlete
    h, m = (2.54, 180.) if role == 'field' else (3.2004, 300.)
    base = dict(strength=rating, explosive_power=rating, traction=rating, technique=rating)
    base.update(over)
    return PerformanceProfile(f'{role}_r{rating:g}', Athlete(h, m, **base), min(1., max(.01, rating)), rating, rating, rating)
