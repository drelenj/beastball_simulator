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


# ---------------------------------------------------------------- RB-3.9c carrier (B-2)
CARRY_APPROACH_M = 30.     # PRIMITIVE: "in or approaching the attacked zone" (zone radius 20 + 10)
CARRY_CLEAR_M = 5.         # PRIMITIVE, tunable: no believed defender this close
KEEPER_LANE_M = 2.5        # PRIMITIVE: Keeper this close to my line to the goal is "in my lane"
ZONE_LIMIT_MS = 5000       # rule: zone_residence after 5 s in the zone he attacks (unchanged)
ZONE_MARGIN_MS = 500       # PRIMITIVE: arrive this long before the limit
CARRY_SPEED_FRAC = .8      # PRIMITIVE: expected carry speed as a fraction of own top speed
GOAL_AIM_INSET_M = 1.      # aim 1 m short of the goal plane: the carried ball crosses it ahead of the body


def _seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay; L = dx * dx + dy * dy or 1.
    f = max(0., min(1., ((px - ax) * dx + (py - ay) * dy) / L))
    return hypot(px - ax - f * dx, py - ay - f * dy)


def carrier_to_goal(view, belief, intent, record):
    """An unopposed carrier near the goal he attacks carries on to the goal when he can arrive
    before the zone_residence limit; otherwise the decision (including the 4 s exit) stands."""
    sig = view.signals
    if (not view.holds_ball or view.role != 'field' or view.restart is not None or sig.phase != 'live'
            or view.pending_command_id is not None or sig.passive_team != view.team):
        return intent, record
    sg = view.attack_sign; gx = view.own_goal_x + sg * 100.
    d = hypot(gx - view.x, 50. - view.y)
    if d > CARRY_APPROACH_M:
        return intent, record
    fresh = _fresh(view, belief)
    opps = [t for t in fresh if t.team not in (view.team, 'ball')]
    if any(t.role == 'field' and hypot(t.x - view.x, t.y - view.y) <= CARRY_CLEAR_M for t in opps):
        return intent, record
    if any(t.role == 'keeper' and _seg_dist(t.x, t.y, view.x, view.y, gx, 50.) <= KEEPER_LANE_M for t in opps):
        return intent, record
    top = view.body.maximum_speed if view.body else 27.
    eta_ms = 1000. * d / max(1., CARRY_SPEED_FRAC * top)
    inside = d < view.zone_radius
    already = view.zone_elapsed_ms if inside else 0
    entry_ms = 0. if inside else 1000. * max(0., d - view.zone_radius) / max(1., CARRY_SPEED_FRAC * top)
    if already + (eta_ms - entry_ms) > ZONE_LIMIT_MS - ZONE_MARGIN_MS:
        return intent, dict(record, rb39c='cannot_reach_goal_in_time')
    aim = (round(gx - sg * GOAL_AIM_INSET_M, 3), 50.)
    return (replace(intent, kind='carry', aim=aim, target=None, contact=None),
            dict(record, rb39c=dict(rule='unopposed_carry_to_goal', distance_m=round(d, 2), eta_ms=round(eta_ms))))


# ------------------------------------------------- RB-3.11 zone behaviour (Z-2, Z-3, Z-4)
# BEHAVIORAL defaults, PROVISIONAL, unsearched. The 5 s zone rules are unchanged; this only decides when
# an athlete starts to leave (or close on a mark) so that he is clear before his clock completes.
ZONE_LIMIT_MS_RULE = 5000     # rule: 5 s of live time (attacker in the zone he attacks; unmarked defender in his own)
EXIT_MARGIN_S = .75           # start leaving when time needed + this margin reaches the time left (owner default)
EXIT_SPEED_FRAC = .88         # off-ball speed cap used by the engine movement model (pace x .88); from rest, with own acceleration
SUPPORT_DIST_M = 8.           # an off-ball attacker within this distance of the carrier is involved in the play (owner default)
CARRIER_NEAR_BALL_M = 1.8     # the believed carrier is the player nearest the ball within this distance
SHOT_MIN_TIME_MS = 500        # a carrier's shot option is exempt while at least this much time is left to release it
ARC_INSET_M = 1.              # exit target: the zone radius + this, on the ray from the goal centre through the athlete
MARK_TRACK_AGE_MS = 600       # "marked" is judged on tracks at most this old (belief memory is 2 s; the engine's marking is instantaneous)


def time_to_cover(view, distance, toward=None):
    """Time (s) to cover `distance` with the athlete's own acceleration and capped top speed.
    Starts from rest, except that an athlete moving AWAY from the target (own velocity is own-body
    knowledge) first has to brake: braking time plus the distance he travels while stopping.
    `toward` is the unit vector from the athlete to the target; None means from rest."""
    b = view.body
    v = (b.maximum_speed if b else 27.) * EXIT_SPEED_FRAC
    a = b.acceleration if b else 10.
    if distance <= 0:
        return 0.
    extra_t = extra_d = 0.
    if toward is not None and b is not None and getattr(b, 'braking', 0) > 0:
        away = -(b.vx * toward[0] + b.vy * toward[1])
        if away > 0:
            extra_t, extra_d = away / b.braking, away * away / (2. * b.braking)
    distance += extra_d
    ramp = v * v / (2. * a)
    return extra_t + ((2. * distance / a) ** .5 if distance <= ramp else v / a + (distance - ramp) / v)


def _unit(ax, ay, bx, by):
    d = hypot(bx - ax, by - ay)
    return ((bx - ax) / d, (by - ay) / d) if d > 1e-9 else None


def _arc_point(view, gx, x, y):
    dx, dy = x - gx, y - 50.
    d = hypot(dx, dy)
    ux, uy = (dx / d, dy / d) if d > 1e-6 else (-view.attack_sign if gx != view.own_goal_x else view.attack_sign, 0.)
    r = view.zone_radius + ARC_INSET_M
    return (round(_clamp(gx + ux * r), 3), round(_clamp(50. + uy * r), 3))


def _leave_distance(view, gx, aim):
    """Distance along the straight line from the athlete to `aim` until it is outside the zone (None if aim is inside)."""
    if hypot(aim[0] - gx, aim[1] - 50.) < view.zone_radius:
        return None
    ax, ay = aim[0] - view.x, aim[1] - view.y
    L = hypot(ax, ay) or 1.
    lo, hi = 0., 1.
    for _ in range(20):
        mid = (lo + hi) / 2.
        if hypot(view.x + ax * mid - gx, view.y + ay * mid - 50.) < view.zone_radius: lo = mid
        else: hi = mid
    return hi * L


def _believed_carrier_xy(view, belief):
    ball = next((t for t in _fresh(view, belief) if t.entity == C.BALL), None)
    if ball is None:
        return None
    mates = [t for t in _fresh(view, belief) if t.team == view.team and t.role == 'field' and t.entity != view.athlete]
    best = min(mates, key=lambda t: (hypot(t.x - ball.x, t.y - ball.y), t.entity), default=None)
    return (best.x, best.y) if best is not None and hypot(best.x - ball.x, best.y - ball.y) < CARRIER_NEAR_BALL_M else None


def _involved(view, belief):
    """Off-ball attacker involved in the play: designated receiver, intended pass target, or near the carrier."""
    form = getattr(view, 'formation', None)
    if form is not None and form[1] == view.athlete:
        return 'designated_receiver'
    call = view.signals.pass_call
    if call is not None and call[1] == view.athlete:
        return 'pass_target'
    cxy = _believed_carrier_xy(view, belief)
    if cxy is not None and hypot(cxy[0] - view.x, cxy[1] - view.y) <= SUPPORT_DIST_M:
        return 'support_of_carrier'
    return None


def _leave(view, gx, intent, record, rule, **info):
    aim = _arc_point(view, gx, view.x, view.y)
    return (replace(intent, kind='position', aim=aim, target=None, contact=None),
            dict(record, rb311=dict(rule=rule, **info)))


def zone_behavior(view, belief, intent, record):
    """Z-2 / Z-3 (attackers) and Z-4 (defenders). Cognition only; rule and clocks unchanged."""
    sig = view.signals
    if (view.role != 'field' or view.bench_role or view.restart is not None or sig.phase != 'live'
            or view.pending_command_id is not None or sig.passive_team is None or view.body is None):
        return intent, record
    if sig.passive_team == view.team:
        return _attacker_zone(view, belief, intent, record)
    return _defender_zone(view, belief, intent, record)


def _attacker_zone(view, belief, intent, record):
    sg = view.attack_sign; gx = view.own_goal_x + sg * 100.
    d = hypot(view.x - gx, view.y - 50.)
    inside = d < view.zone_radius
    if not inside:
        # Z-3: an off-ball attacker does not walk into the zone he attacks unless involved in the play
        if (not view.holds_ball and intent.aim is not None and hypot(intent.aim[0] - gx, intent.aim[1] - 50.) < view.zone_radius
                and _involved(view, belief) is None):
            return (replace(intent, aim=_arc_point(view, gx, intent.aim[0], intent.aim[1])),
                    dict(record, rb311=dict(rule='Z-3_stay_out', aim_was=list(intent.aim))))
        return intent, record
    time_left = (ZONE_LIMIT_MS_RULE - view.zone_elapsed_ms) / 1000.
    out_dir = _unit(gx, 50., view.x, view.y)                       # outward from the goal centre: toward the arc
    t_arc = time_to_cover(view, view.zone_radius + ARC_INSET_M - d, out_dir)
    if view.holds_ball:
        rule = record.get('rb39c')
        if isinstance(rule, dict) and rule.get('rule') == 'unopposed_carry_to_goal':
            return intent, record                      # carrier rule: carrying on to score with margin (exempt)
        if intent.kind == 'shoot' and time_left * 1000. >= SHOT_MIN_TIME_MS and t_arc + EXIT_MARGIN_S < time_left:
            return intent, record                      # a real shot option, while there is still time to exit
        if t_arc + EXIT_MARGIN_S < time_left:
            return intent, record
        eta = time_to_cover(view, d, _unit(view.x, view.y, gx, 50.))
        if t_arc >= time_left > eta:                   # cannot clear the arc in time, but can still score
            aim = (round(gx - sg * GOAL_AIM_INSET_M, 3), 50.)
            return (replace(intent, kind='carry', aim=aim, target=None, contact=None),
                    dict(record, rb311=dict(rule='Z-2_carrier_last_resort_to_goal', eta_s=round(eta, 2), time_left_s=round(time_left, 2))))
        return _leave(view, gx, intent, record, 'Z-2_carrier_exit', t_arc_s=round(t_arc, 2), time_left_s=round(time_left, 2))
    involved = _involved(view, belief)
    if involved is None:                               # Z-3: off-ball and not involved: head out at once
        return _leave(view, gx, intent, record, 'Z-3_off_ball_exit', t_arc_s=round(t_arc, 2), time_left_s=round(time_left, 2))
    if t_arc + EXIT_MARGIN_S >= time_left:             # Z-2: involved, but his clock is running out
        cross = _leave_distance(view, gx, intent.aim) if intent.aim is not None else None
        if cross is not None and time_to_cover(view, cross, _unit(view.x, view.y, *intent.aim)) <= t_arc * 1.15:
            return intent, record                      # his own intent already takes him out as fast
        return _leave(view, gx, intent, record, 'Z-2_exit', involved=involved, t_arc_s=round(t_arc, 2), time_left_s=round(time_left, 2))
    return intent, record


def _defender_zone(view, belief, intent, record):
    gx = view.own_goal_x
    d = hypot(view.x - gx, view.y - 50.)
    if d >= view.zone_radius or view.holds_ball:
        return intent, record
    conf = getattr(view, 'defender_baseline', None)
    mark = conf[1] if conf else 5.
    fresh = _fresh(view, belief, MARK_TRACK_AGE_MS)
    opps = [t for t in fresh if t.team not in (view.team, 'ball') and t.role == 'field']
    if any(hypot(o.x - view.x, o.y - view.y) <= mark for o in opps):
        return intent, record                          # marked: the engine clock is reset
    time_left = (ZONE_LIMIT_MS_RULE - view.zone_elapsed_ms) / 1000.
    t_arc = time_to_cover(view, view.zone_radius + ARC_INSET_M - d, _unit(gx, 50., view.x, view.y))
    mates = [t for t in fresh if t.team == view.team and t.role == 'field' and t.entity != view.athlete]
    free = [o for o in opps if not any(hypot(m.x - o.x, m.y - o.y) <= mark for m in mates)] or opps
    best = min(free, key=lambda o: (hypot(o.x - view.x, o.y - view.y), o.entity), default=None)
    t_mark = time_to_cover(view, max(0., hypot(best.x - view.x, best.y - view.y) - MARK_STANDOFF * mark), _unit(view.x, view.y, best.x, best.y)) if best else None
    t_best = min(t for t in (t_arc, t_mark) if t is not None)
    if t_best + EXIT_MARGIN_S < time_left:
        return intent, record
    if t_mark is not None and t_mark < t_arc:
        aim = _toward(best.x, best.y, gx, 50., MARK_STANDOFF * mark)
        return (replace(intent, kind='mark', aim=aim, target=best.entity, contact=None),
                dict(record, rb311=dict(rule='Z-4_close_on_mark', target=best.entity, t_mark_s=round(t_mark, 2), time_left_s=round(time_left, 2))))
    cross = _leave_distance(view, gx, intent.aim) if intent.aim is not None else None
    if cross is not None and time_to_cover(view, cross, _unit(view.x, view.y, *intent.aim)) <= t_arc * 1.15:
        return intent, record
    return _leave(view, gx, intent, record, 'Z-4_leave', t_arc_s=round(t_arc, 2), time_left_s=round(time_left, 2))


def adjust(view, belief, intent, record):
    intent, record = carrier_to_goal(view, belief, intent, record)
    intent, record = defender_baseline(view, belief, intent, record)
    intent, record = zone_behavior(view, belief, intent, record)
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
