"""RB/3 decision adjustments (RB-3.4, owner rulings 17 Nov 2026). PROVISIONAL, pure.

Applied only when view.cognition is 'native-rb/3'. Inputs: the athlete's
view and own belief. A frozen player is known only from the public status light the
athlete can see (view.status_indicators 'red') and his believed position.
- No press or tackle on a believed-frozen player: the intent becomes a 'position'.
- Path planning: if the straight path to a locomotion aim passes a believed-frozen
  player, the athlete aims for a waypoint beside him (steer around).
The Archer's re-check at release is the existing decide path (abort_draw when the
target is no longer believed legal), with 'loose' accepted under RB/3.
Constants are PRIMITIVE and unsearched.
"""
from dataclasses import replace
from math import hypot
from . import cognition as C

CLEARANCE_M = 1.6      # path passing closer than this to a frozen body is re-routed
SIDESTEP_M = 2.2       # waypoint offset beside the frozen body
MOVES = ('position', 'carry', 'pursue', 'press', 'mark', 'support', 'receive', 'search', 'keeper_set', 'restart_position')


def frozen_tracks(view, belief):
    red = {pid for pid, light in getattr(view, 'status_indicators', ()) if light == 'red'}   # RulebookView only
    return [t for t in belief.tracks if t.entity in red and view.delivered_ms - t.captured_ms <= 2000]


def detour(x, y, aim, obstacles):
    ax, ay = aim[0] - x, aim[1] - y
    d2 = ax * ax + ay * ay
    if d2 < 1e-6:
        return aim, None
    best = None
    for o in obstacles:
        f = ((o.x - x) * ax + (o.y - y) * ay) / d2
        if not 0. < f < 1.:
            continue
        gap = hypot(o.x - x - f * ax, o.y - y - f * ay)
        if gap < CLEARANCE_M and (best is None or f < best[0]):
            best = (f, o)
    if best is None:
        return aim, None
    f, o = best
    n = d2 ** .5
    px, py = -ay / n, ax / n                      # unit normal to the path
    side = 1. if (o.x - x) * px + (o.y - y) * py < 0 else -1.   # pass on the side away from him
    wx = min(99.4, max(.6, o.x + side * px * SIDESTEP_M))
    wy = min(99.4, max(.6, o.y + side * py * SIDESTEP_M))
    return (round(wx, 3), round(wy, 3)), o.entity


# ---------------------------------------------------------------- RB-3.6 defender baseline
# BEHAVIORAL baseline (owner, 18 Nov 2026), PROVISIONAL. The two distances arrive in the view as a
# public team instruction (view.defender_baseline = (enabled, mark_distance_m, ball_leash_m)), from
# RulebookConfigV3, so a later tactics layer can override them. Everything else is belief-based.
MARK_STANDOFF = .7           # PRIMITIVE: aim at this fraction of the marking distance, goal side
LEASH_STANDOFF = .9          # PRIMITIVE: aim at this fraction of the leash, on my side of the ball
REENTRY_BLOCK_MS = 3000      # does not re-enter his own zone within 3 s unless a condition holds there
LOCOMOTION = ('position', 'mark', 'support', 'scan', 'search', 'pursue')


def _clamp(v, lo=.6, hi=99.4):
    return lo if v < lo else hi if v > hi else v


def _fresh(view, belief, age=2000):
    return [t for t in belief.tracks if 0 <= view.delivered_ms - t.captured_ms <= age]


def _ball(view, belief):
    b = next((t for t in _fresh(view, belief) if t.entity == C.BALL), None)
    if b is not None:
        return (b.x, b.y)
    if view.holds_ball:
        return (view.x, view.y)
    return belief.last_ball[:2] if belief.last_ball else None


def _satisfies(xy, opps, ball, mark, leash):
    return (any(hypot(o.x - xy[0], o.y - xy[1]) <= mark for o in opps)
            or (ball is not None and hypot(ball[0] - xy[0], ball[1] - xy[1]) <= leash))


def _toward(ax, ay, bx, by, r):
    """Point at distance r from (ax, ay) in the direction of (bx, by)."""
    dx, dy = bx - ax, by - ay
    d = hypot(dx, dy) or 1.
    return (round(_clamp(ax + dx / d * r), 3), round(_clamp(ay + dy / d * r), 3))


def _targets(view, belief, opps, mates, ball, mark, leash):
    """Cheapest way to satisfy a condition: (cost_m, kind, aim, who)."""
    out = []
    taken = {o.entity for o in opps if any(hypot(m.x - o.x, m.y - o.y) <= mark for m in mates)}
    free = [o for o in opps if o.entity not in taken] or opps          # (d) avoid doubling up
    goal = (view.own_goal_x, 50.)
    for o in free:
        d = hypot(o.x - view.x, o.y - view.y)
        out.append((round(max(0., d - mark), 6), 'mark', _toward(o.x, o.y, *goal, MARK_STANDOFF * mark), o.entity))
    if ball is not None:
        d = hypot(ball[0] - view.x, ball[1] - view.y)
        out.append((round(max(0., d - leash), 6), 'position', _toward(ball[0], ball[1], view.x, view.y, LEASH_STANDOFF * leash), C.BALL))
    return sorted(out, key=lambda o: (o[0], o[1], o[3]))


def defender_baseline(view, belief, intent, record):
    conf = getattr(view, 'defender_baseline', None)
    if not conf or not conf[0] or view.role != 'field' or view.holds_ball or view.bench_role:
        return intent, record
    if view.restart is not None or view.signals.phase != 'live' or view.pending_command_id is not None:
        return intent, record
    _, mark, leash = conf
    sig = view.signals
    if sig.passive_team is None or sig.passive_team == view.team:
        return intent, record                     # attackers: existing 3 s zone exit applies (< 4 s)
    if view.zone_elapsed_ms >= 3000 and intent.kind == 'position':
        return intent, record                     # rule-compliance exit from the zone already chosen
    if intent.kind in ('press', 'tackle', 'receive'):
        return intent, record                     # engaging the ball: already inside the leash
    fresh = _fresh(view, belief)
    opps = [t for t in fresh if t.team not in (view.team, 'ball') and t.role == 'field']
    mates = [t for t in fresh if t.team == view.team and t.role == 'field']
    ball = _ball(view, belief)
    here = (view.x, view.y)
    now_ok = _satisfies(here, opps, ball, mark, leash)
    aim_ok = intent.aim is not None and _satisfies(intent.aim, opps, ball, mark, leash)
    new = None
    if not now_ok or (intent.kind in LOCOMOTION and not aim_ok):
        options = _targets(view, belief, opps, mates, ball, mark, leash)
        if options:
            cost, kind, aim, who = options[0]
            new = replace(intent, kind=kind, aim=aim, target=None if who == C.BALL else who, contact=None)
            record = dict(record, rb36=dict(rule='satisfy_nearer_condition', cost_m=cost, kind=kind, anchor=who,
                                            marking_now=any(hypot(o.x - view.x, o.y - view.y) <= mark for o in opps),
                                            ball_leash_now=ball is not None and hypot(ball[0] - view.x, ball[1] - view.y) <= leash))
    out = new or intent
    exit_ago = getattr(view, 'own_zone_exit_ms_ago', None)
    if (out.aim is not None and exit_ago is not None and exit_ago < REENTRY_BLOCK_MS
            and not C.in_own_zone(view.team, view.x, view.y, view) and C.in_own_zone(view.team, out.aim[0], out.aim[1], view)
            and not _satisfies(out.aim, opps, ball, mark, leash)):
        gx = view.own_goal_x
        dx, dy = out.aim[0] - gx, out.aim[1] - 50.
        d = hypot(dx, dy) or 1.
        r = view.zone_radius + 1.
        out = replace(out, aim=(round(_clamp(gx + dx / d * r), 3), round(_clamp(50. + dy / d * r), 3)))
        record = dict(record, rb36_reentry_block=True)
    return out, record


def adjust(view, belief, intent, record):
    intent, record = defender_baseline(view, belief, intent, record)
    frozen = frozen_tracks(view, belief)
    if not frozen:
        return intent, record
    ids = {t.entity for t in frozen}
    record = dict(record, rb3_frozen_believed=sorted(ids))
    if intent.kind in ('press', 'tackle') and intent.target in ids:
        intent = replace(intent, kind='position', contact=None)
        record['rb3_no_contact_on_frozen'] = intent.target
    if intent.kind in MOVES and intent.aim is not None:
        aim, around = detour(view.x, view.y, intent.aim, frozen)
        if around is not None:
            intent = replace(intent, aim=aim)
            record['rb3_detour_around'] = around
    return intent, record
