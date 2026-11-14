"""EMERGENCE-1 belief-driven positioning (replaces the `home` slot grid).

PRIMITIVE: an athlete with no ball action scores 9 candidate points (stay, or 6 m in
8 directions) from its OWN belief only. Every term is weighted by the team's
PolicyParams; no slot, formation or assigned position is used. Pure module.
"""
from math import hypot

STEP = 6.0
DIRS = ((0., 0.), (1., 0.), (.7071, .7071), (0., 1.), (-.7071, .7071),
        (-1., 0.), (-.7071, -.7071), (0., -1.), (.7071, -.7071))


def _nearest(px, py, pts):
    best = 30.
    for x, y in pts:
        d = hypot(px - x, py - y)
        if d < best:
            best = d
    return best


def _lane(ox, oy, tx, ty, opps):
    dx, dy = tx - ox, ty - oy
    d2 = dx * dx + dy * dy
    if d2 < 1e-9:
        return 0.
    best = 10.
    for x, y in opps:
        f = ((x - ox) * dx + (y - oy) * dy) / d2
        f = 0. if f < 0. else 1. if f > 1. else f
        c = hypot(x - ox - f * dx, y - oy - f * dy)
        if c < best:
            best = c
    return best


def choose_position(x, y, own_goal_x, attack_sign, zone_radius, ball_xy, carrier_xy, mode,
                    mates, opps, p):
    """mode: 'att' (own team has passive possession), 'def' (other team), 'none'.
    mates/opps: tuples of believed (x, y). Returns (aim, best_score, considered)."""
    att_goal_x = own_goal_x + attack_sign * 100.
    best, best_xy, n = None, (x, y), 0
    for ux, uy in DIRS:
        px = min(97., max(3., x + ux * STEP))
        py = min(97., max(3., y + uy * STEP))
        s = 0.
        if ball_xy is not None:
            w = p.pos_ball_att if mode == 'att' else p.pos_ball_def if mode == 'def' else .5 * (p.pos_ball_att + p.pos_ball_def)
            s -= w * hypot(px - ball_xy[0], py - ball_xy[1]) * .1
        if mode == 'att':
            s -= p.pos_goal_att * hypot(px - att_goal_x, py - 50.) * .1
            s += p.pos_opp_att * min(_nearest(px, py, opps), 10.) * .1
            if carrier_xy is not None:
                s += p.pos_lane * _lane(carrier_xy[0], carrier_xy[1], px, py, opps) * .1
        elif mode == 'def':
            s -= p.pos_goal_def * hypot(px - own_goal_x, py - 50.) * .1
            s -= p.pos_opp_def * min(_nearest(px, py, opps), 10.) * .1
        s += p.pos_spread * min(_nearest(px, py, mates), 12.) * .1
        edge = min(px, 100. - px, py, 100. - py)
        pen = max(0., 6. - edge) / 6.
        if hypot(px - own_goal_x, py - 50.) < zone_radius or hypot(px - att_goal_x, py - 50.) < zone_radius:
            pen += 1.
        s -= p.pos_edge_zone * pen
        n += 1
        if best is None or s > best + 1e-12:
            best, best_xy = s, (px, py)
    return (round(best_xy[0], 3), round(best_xy[1], 3)), round(best, 6), n
