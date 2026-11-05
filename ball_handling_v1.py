"""Ball handling v1: what a ball's SHAPE does to carrying, stripping, catching and loose-ball play.  PROVISIONAL dials (flagged).  Same mass (0.40 kg) and volume as the rulebook sphere.
Derived from geometry (aspect = long/short axis, grip fit from throwing_v1):
  exposed / extended carry : retention x grip_quality / (1 + LEVER*(aspect-1))    a long axis hands the defender a lever; extended arm gets 1.5x the lever
  tucked carry             : retention x (1 + TUCK_GAIN*(a-1) - TUCK_PEN*(a-1)^2)  a line of contact along forearm and ribs; too long to cover and the gain turns over (best near aspect 1.55)
  catch                    : multiplier on catch difficulty = (1/grip_quality) * (1 + CATCH_K*(aspect-1)*(1 - spiral_quality));  spiral_quality = stability * spin quality (thrower accuracy)
  loose ball               : each bounce turns the heading by N(0, BOUNCE_K*(1 - 1/aspect^2)) degrees;  the sphere bounces true
Retention values feed Codex's v0.4 force-grip world through BallParameters.pose_factor (no edit to his files).
"""
import math, random
import throwing_v1 as T
import beastball_anatomy_v03 as v3
LEVER, TUCK_GAIN, TUCK_PEN, CATCH_K, BOUNCE_K = .5, .55, .5, .6, 10.
BASE_POSE = {'exposed': 1.0, 'tucked': 1.55, 'extended': .80, 'loaded': .70, 'braced': 2.17}      # exposed/tucked/extended: Codex's v0.3 values (sphere);  loaded and braced added here (braced = 1.4 x tucked)
def rel_factors(shape, height=2.54):
    a = shape.aspect; x = a - 1.
    q = T.grip_quality(T.Thrower(height=height), shape)
    e = q / (1. + 1.5 * LEVER * x); tk = 1. + TUCK_GAIN * x - TUCK_PEN * x * x
    return dict(exposed=q / (1. + LEVER * x), extended=e, loaded=e, tucked=tk, braced=tk)
def ball_parameters(shape, height=2.54):
    rf = rel_factors(shape, height)
    return v3.BallParameters(mass=shape.mass, radius=T.BALL_D / 2, pose_factor={k: BASE_POSE[k] * rf[k] for k in BASE_POSE})
def catch_multiplier(shape, accuracy, air=T.AIR_POCKET, height=2.54, speed=30.):
    t = T.Thrower(height=height, accuracy=accuracy); q = T.grip_quality(t, shape)
    if shape.aspect <= 1.0: return 1. / q
    om = T.spin_rate(t, shape); sg = T.stability(shape, om, speed, air)
    spiral = min(1., sg / 1.3) * (.3 + .7 * accuracy) * 1.0
    return (1. / q) * (1. + CATCH_K * (shape.aspect - 1.) * (1. - spiral))
def loose_ball(shape, n=400, seed=5, v_h=22., v_z=-6., h0=1.0, e=.7746, mu=.22):
    """Ball knocked loose at height h0 with horizontal speed v_h: bounce until the bounce height is under 3 cm.  Returns rest-position scatter (lateral sd, along sd, mean distance) and number of bounces."""
    rng = random.Random(seed); sig = math.radians(BOUNCE_K * (1. - 1. / shape.aspect ** 2)); out = []
    for _ in range(n):
        x = y = 0.; hd = 0.; z = h0; vz = v_z; vh = v_h; nb = 0
        while True:
            tf = max(0., (vz + math.sqrt(vz * vz + 2 * 9.81 * (z - .1075))) / 9.81)
            x += vh * math.cos(hd) * tf; y += vh * math.sin(hd) * tf
            vzi = -(vz - 9.81 * tf); vz = e * vzi; vh *= (1. - mu); hd += rng.gauss(0, sig); z = .1075; nb += 1
            if nb == 2: p2 = (x, y)
            if vz * vz / (2 * 9.81) < .03 or nb > 12: break
        # roll out
        roll = vh * vh / (2 * 3.0); x += roll * math.cos(hd); y += roll * math.sin(hd); out.append((x, y, nb, p2))
    xs = [o[0] for o in out]; ys = [o[1] for o in out]
    mean = lambda v: sum(v) / len(v); sd = lambda v: math.sqrt(sum((a - mean(v)) ** 2 for a in v) / len(v))
    return dict(after2_lateral_sd_m=round(sd([o[3][1] for o in out]), 2), after2_mean_m=round(mean([o[3][0] for o in out]), 1), rest_lateral_sd_m=round(sd(ys), 2), rest_mean_dist_m=round(mean([math.hypot(a, b) for a, b, _, _ in out]), 1), bounces=round(mean([o[2] for o in out]), 1))
