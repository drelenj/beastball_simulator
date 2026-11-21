"""RB-3.20 Part 1B: reference model of a real ball of this sport's stated size and mass on natural grass (assumptions below),
integrated at 1 ms. Compare with ball_scenario.out. Not used by the engine.
Assumptions (stated, with sources):
- Ball: radius .1075 m, mass .4 kg (engine DEFAULT_ASSUMPTIONS ball_mass_kg, Ball radius) ~ an association-football size-5 ball
  (FIFA Laws of the Game, Law 2: circumference 68-70 cm, 410-450 g).
- Air: quadratic drag, rho 1.2 kg/m^3, Cd .25 above ~12 m/s (supercritical) and .45 below (sphere / football wind-tunnel data,
  e.g. Asai et al. 2007, Sports Engineering 10:101-110).
- Grass, vertical: coefficient of restitution .65 (FIFA Quality Programme ball-rebound test: 0.6-1.0 m rebound from a 2 m drop,
  i.e. e = sqrt(h/2) about .55-.71).
- Grass, horizontal at impact: Coulomb friction mu .5 on the contact impulse, limited by the rolling condition (horizontal speed
  not below 5/7 of the incoming one for a solid-ish ball; Cross 2002, Am. J. Phys. 70:482).
- Grass, rolling: constant rolling-resistance deceleration .8 m/s^2 (FIFA Quality Programme ball-roll test: 4-10 m from a
  ~3.1 m/s ramp exit, a = v^2 / 2d about .5-1.2 m/s^2) plus air drag."""
import math, json

R, M, RHO, A = .1075, .4, 1.2, math.pi * .1075 ** 2


def run(speed, vz0=0., z0=1.5, dt=.001, tmax=12.):
    x, z, vx, vz, t = 0., z0, speed, vz0, 0.; out = {}; first = None; bounces = 0
    while t < tmax:
        v = math.hypot(vx, vz); cd = .25 if v > 12 else .45
        k = .5 * RHO * cd * A / M
        ax, az = -k * v * vx, -9.81 - k * v * vz
        rolling = z <= R + 1e-9 and abs(vz) < 1e-9
        if rolling:
            az = 0.; ax = -k * vx * abs(vx) - .8 * (1 if vx > 0 else 0)
        x += vx * dt; z += vz * dt; vx += ax * dt; vz += az * dt; t += dt
        if z < R:
            z = R
            if first is None: first = round(t, 3)
            if abs(vz) > .3:
                J = (1 + .65) * abs(vz); vz = .65 * abs(vz); bounces += 1
                vx = max(vx * 5 / 7, vx - .5 * J)
            else:
                vz = 0.
        for T in (1., 2., 3.):
            if abs(t - T) < dt / 2: out[f's{int(T)}'] = round(x, 2)
        if rolling and vx <= 0: return dict(speed=speed, vz0=vz0, first_ground_s=first, bounces=bounces, distance_at=out, stop=dict(t_s=round(t, 2), x_m=round(x, 2)))
    return dict(speed=speed, vz0=vz0, first_ground_s=first, bounces=bounces, distance_at=out, stop=None)


if __name__ == '__main__':
    for sp in (20., 35., 50.):
        for vz in (0., 2.23):
            print(json.dumps(run(sp, vz)))
