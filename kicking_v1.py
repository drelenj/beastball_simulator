"""Kick and dribble v1: the other two ways a player can move the ball, built on throwing_v1 (same chain readiness, same shapes, same Pocket air).  ALL DIALS PROVISIONAL.

RULE being served (DreLen, Oct 29): in possession a player may carry without limit, dribble once and kick once; both reset when the ball hits the goal or possession changes.

KICK (ratings: Kick Power, Kick Accuracy;  readiness from the same Condition layer)
  foot speed  = FOOT_V * (0.5 + 0.5*power) * kick_chain,   kick_chain = 0.55*legs + 0.25*torso + 0.20*balance          (balance falls with restraint)
  ball speed  = 1.32 * foot speed * efficiency  (+ 0.3 of the kicker's own forward speed), capped at Pocket's 40 m/s ball_limit.   (1.32 = (1+e) m_foot/(m_foot+m_ball), e 0.5, foot 3 kg)
  contact     : lateral offset d (in units of the ball's short radius) ~ N(0, 0.05 + 0.30*(1-accuracy));  efficiency = 1 - 0.4 d^2;  direction error = 0.35*asin(d) plus Pocket's base error (3 deg*(1-accuracy), 1 deg floor)
  prolate balls: the long axis is at a random angle phi to the foot path (punt: sd 15 deg*(1-0.7*acc); kick off the ground: sd 25 deg*(1-0.6*acc)); the contact normal tilts and sends the ball off line by 0.5*(1 - 1/aspect^2)*phi.
  delay       : punt = time to loaded + drop 0.32 s + strike 0.10 s;  ground kick = 0.25 s swing (ball already at the feet)

DRIBBLE (rating: ball handling)
  The carrier bounces the ball off the ground and regathers it.  Cycle time T = (v_down + v_hit)/g-ish from the bounce (restitution 0.775, Pocket).  The ball loses 22 % of its horizontal speed relative to the carrier per bounce
  (the carrier pushes ahead to compensate, leaving the hand's push noise sd = 0.04 + 0.35*(1 - ball_handling) m).  A prolate ball turns its heading randomly at the bounce, sd = BOUNCE_K*(1 - 1/aspect^2) degrees, so the
  carrier's own speed u turns that heading error into u*sin(sd)*T metres of lateral miss.  Regather succeeds if the ball ends within the hand's catch envelope (0.6 m, Pocket catch_hand_travel_m).
"""
import math, random
import throwing_v1 as T
import ball_handling_v1 as BH

FOOT_V = 30.
FOOT_TO_BALL = 1.32
KICK_DROP_S, KICK_STRIKE_S, GROUND_SWING_S = .32, .10, .25
CATCH_ENVELOPE = .6
RESTITUTION = .7746
H_SPEED_LOSS = .22
def kick_chain(t):
    """kicking leg .40, support leg .15, torso .25, balance .20.  With part holds: the kicking leg is hurt by its own hold (x(1-.9h)), the support leg by (1-.6h), the torso (1-.4h), balance by held arms."""
    rl, rt, ra = T.readiness(t)
    if not t.part_hold:
        balance = 1. - .6 * t.hold_rho
        return .55 * rl + .25 * rt + .20 * balance
    h = T.holds(t); sup = 'left' if t.kick_leg == 'right' else 'right'
    rl0, rt0, _ = T.readiness(T.Thrower(**{**t.__dict__, 'part_hold': {}}))      # readiness without holds, then apply the kick-specific ones
    balance = 1. - .3 * h['arm'] - .3 * h['off'] - .3 * h['torso'] - .4 * h['head']
    return .40 * rl0 * (1. - .9 * h[t.kick_leg + '_leg']) + .15 * rl0 * (1. - .6 * h[sup + '_leg']) + .25 * rt0 * (1. - .4 * h['torso']) + .20 * max(0., balance)
def kick_speed_max(t):
    return FOOT_V * (T.POWER_FLOOR + (1 - T.POWER_FLOOR) * t.power) * kick_chain(t) * FOOT_TO_BALL
def kick_delay(t, shape, pose, mode):
    if mode == 'ground': return T.RELEASE_S * (1. + .8 * (1. - kick_chain(t))) * (1.15 - .3 * t.accuracy) * (GROUND_SWING_S / T.RELEASE_S)
    return T.transition_time(t, shape, pose) + KICK_DROP_S + KICK_STRIKE_S
def kick(t, shape, direction, want_speed, rng, mode='punt'):
    """One kick.  direction: unit 3-vector of the aim.  Returns (velocity, info).  The kick can deliver less than `want_speed` but never more than the rule cap."""
    vmax = kick_speed_max(t); u = t.speed
    # contact quality
    sd_off = .05 + .30 * (1. - t.accuracy); hp = T.holds(t) if t.part_hold else None; sup = 'left' if t.kick_leg == 'right' else 'right'
    held = (3. * hp[t.kick_leg + '_leg'] + 2. * hp[sup + '_leg'] + 1.0 * hp['torso'] + .5 * hp['arm'] + .5 * hp['off']) if hp else 2.0 * t.hold_rho
    d = rng.gauss(0, sd_off) * (1. + 1.0 * t.u + 1.5 * (1. - t.reserve) + held)
    d = max(-.95, min(.95, d)); eff = 1. - .4 * d * d
    err_az = .35 * math.asin(d); err_el = .35 * math.asin(max(-.95, min(.95, rng.gauss(0, sd_off))))
    if shape.aspect > 1.:
        phi_sd = (15. * (1. - .7 * t.accuracy)) if mode == 'punt' else (25. * (1. - .6 * t.accuracy))
        phi = rng.gauss(0, phi_sd); err_az += math.radians(.5 * (1. - 1. / shape.aspect ** 2) * phi)
        err_el += math.radians(.5 * (1. - 1. / shape.aspect ** 2) * rng.gauss(0, phi_sd))
    base = math.radians(max(1., 3. * (1. - t.accuracy)))
    err_az += rng.gauss(0, base); err_el += rng.gauss(0, base / 2)
    speed = min(T.V_CAP, min(want_speed, vmax) * eff + .3 * u * max(0., direction[0] * (t.vel[0] / u if u > 1e-6 else 0.) + direction[1] * (t.vel[1] / u if u > 1e-6 else 0.)))
    az = math.atan2(direction[1], direction[0]) + err_az; el = math.asin(max(-1., min(1., direction[2]))) + err_el
    v = (speed * math.cos(el) * math.cos(az), speed * math.cos(el) * math.sin(az), speed * math.sin(el))
    return v, dict(speed=speed, eff=eff, offset=d, v_max=vmax)
def dribble(t, shape, handling, rng, u=None, hand_h=.95):
    """One dribble (bounce and regather) at carrier speed u (default: his current speed).  Returns dict(success, miss_m, cycle_s).  Carrier keeps running; the ball is pushed with the carrier's velocity plus compensation."""
    u = t.speed if u is None else u
    v_up = math.sqrt(2 * T.G * (hand_h - .1075)); v_imp = v_up / RESTITUTION                     # the push is set so the ball rises back to hand height
    drop_v = math.sqrt(max(0., v_imp ** 2 - 2 * T.G * (hand_h - .1075))); t_down = (v_imp - drop_v) / T.G
    cycle = t_down + v_up / T.G                                                                   # down to the ground, then up to hand height
    sd_push = .04 + .35 * (1. - handling)
    miss_along = rng.gauss(0, sd_push) + (rng.gauss(0, .15 * (1. - 1. / shape.aspect ** 2)) * u * cycle * .25 if shape.aspect > 1. else 0.)   # bounce-height spread changes the return time
    sig_head = math.radians(BH.BOUNCE_K * (1. - 1. / shape.aspect ** 2))
    miss_lat = rng.gauss(0, sd_push) + u * math.sin(rng.gauss(0, sig_head)) * cycle if shape.aspect > 1. else rng.gauss(0, sd_push)
    miss = math.hypot(miss_along, miss_lat)
    return dict(success=int(miss <= CATCH_ENVELOPE), miss=miss, cycle=cycle)
