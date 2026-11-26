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
    if view.registry_ratings and view.prism_agent not in ('defending', 'zone_coverage'):
        return intent, record
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


# ------------------------------------- RB-3.12 / RB-3.13 B-5 carrier valuation (carry vs pass)
# BEHAVIORAL defaults, PROVISIONAL, unsearched. Replaces the M1 values (b1/core.py) for native-rb/3. Only the
# carrier's own belief tracks, own body and own feedback are read.
#
#  constant               value  meaning
#  CARRY_BASE              2.0   carry value with no free run and nobody close
#  CARRY_FREE_W            0.6   value per metre of free run
#  CARRY_FREE_MAX_M        15    free run cap (also the value when no opponent can reach the path)
#  CARRY_PATH_STEP_M       0.5   RB-3.13: path sampling step for the closing-time free run
#  CARRY_CLOSE_M / PENALTY 3.0 / 4.0   an opponent anywhere this close costs this much
#  CARRY_GOAL_NEAR_M / FREE_M / BONUS  25 / 5 / 2.0   near the goal with this free run adds this
#  PASS_BASE               0.5   constant term
#  PASS_GAIN_W             0.35  per metre of forward gain (negative backward), gain clamped to [-15, 25]
#  PASS_CLEAR_W / BASE     0.4 / 3.0   lane margin (capped 10) minus 3  (RB-3.13: margin beyond opponents' reach)
#  PASS_SPACE_W / BASE     0.25 / 3.0  receiver's distance to his nearest opponent (capped 10) minus 3
#  PASS_DIST_W             0.03  per metre of pass length (3-30 m as in M1)
#  PRESSURE_T_S            0.8   RB-3.13: pressured = least time-to-contact of any believed opponent < this
#  CLOSING_MIN_MS          1.0   RB-3.13: floor on the closing speed used in time-to-contact
#  ACQ_RADIUS_M / EXTRA_M  0.45 / 0.2  engine radius and acquisition slack (same source as formation.acquisition_radius);
#                                the opponent's reach is ESTIMATED by the carrier's own reach (opponent bodies are not in his view)
#  LANE_MARGIN_M           0.5   RB-3.13: a lane is unsafe if any opponent, advanced by his velocity to the ball's arrival time,
#                                comes within (acquisition reach + this) of the pass path
#  LANE_SAMPLES            10    RB-3.13: path samples (0..1 of the pass)
#  PRESSURED_SPACE_M / BONUS  6.0 / 3.0  a pressured carrier gets the bonus for a SAFE pass to a receiver this free
#  BACKWARD_W              0.4   unpressured backward pass pays this per metre of loss
#  COMMIT_MS               600   after gaining control an UNPRESSURED carrier does not pass...
#  COMMIT_GAIN_M / CLEAR_M 10 / 4.0  ...unless the pass gains at least this and has at least this margin
#  TYPICAL_ACCEL / TOP      8.75 / 0.88*31.2928  RB-3.14: opponent kinematics for the free run (from his believed velocity)
#  CARRY_CONTACT_BUFFER_M  1.0   RB-3.14: free run = distance before the first opponent can reach the path, minus this
#  ESCAPE_ANGLES_DEG       +-45, +-90  RB-3.13: carry directions tried beside the straight carry ONLY when pressured with no safe pass
#  RECEIVER_CLOCK_LIMIT_S  2.0   RB-3.13: receiver in the zone he attacks with t_left under this:
#  RECEIVER_CLOCK_PENALTY  6.0   ...penalty = 6.0 * (1 - t_left / 2.0); read only for a teammate in FRESH tracks (Q-RB312-2 canon)
CARRY_BASE, CARRY_FREE_W, CARRY_FREE_MAX_M, CARRY_PATH_STEP_M = 2.0, 0.6, 15., .5
CARRY_CLOSE_M, CARRY_CLOSE_PENALTY = 3.0, 4.0
CARRY_GOAL_NEAR_M, CARRY_GOAL_FREE_M, CARRY_GOAL_BONUS = 25., 5., 2.0
PASS_BASE, PASS_GAIN_W, GAIN_MIN_M, GAIN_MAX_M = 0.5, 0.35, -15., 25.
PASS_CLEAR_W, PASS_CLEAR_BASE, PASS_SPACE_W, PASS_SPACE_BASE, PASS_DIST_W = 0.4, 3.0, 0.25, 3.0, 0.03
PASS_MIN_M, PASS_MAX_M = 3., 30.
PRESSURE_T_S, CLOSING_MIN_MS = .8, 1.0
ACQ_RADIUS_M, ACQ_EXTRA_M, ACQ_DEFAULT_REACH_M = .45, .2, 1.26431   # RB-3.16: default = RB/3 control ARM reach (R-1: arm span / 2)
LANE_MARGIN_M, LANE_SAMPLES = .5, 10
PRESSURED_SPACE_M, PRESSURED_BONUS, BACKWARD_W = 6.0, 3.0, 0.4
COMMIT_MS, COMMIT_GAIN_M, COMMIT_CLEAR_M = 600, 10., 4.0
RECEIVER_CLOCK_LIMIT_S, RECEIVER_CLOCK_PENALTY = 2.0, 6.0
TYPICAL_ACCEL, TYPICAL_TOP, CARRY_CONTACT_BUFFER_M = 8.75, .88 * 31.2928, 1.0   # RB-3.14: typical athlete (the 0.70 control) for opponent kinematics; contact buffer (m)
ESCAPE_ANGLES_DEG, ESCAPE_LEN_M = (45., -45., 90., -90.), 15.   # RB-3.13: lateral carry directions tried beside the straight one (ties keep the straight one)


def acquisition_reach(view):
    """Fallback estimate of an opponent's acquisition reach (the carrier's own reach + radius + slack)."""
    reach = view.body.reach if view.body is not None else ACQ_DEFAULT_REACH_M
    return reach + ACQ_RADIUS_M + ACQ_EXTRA_M


def opp_reach(view, o):
    """RB-3.14: the perceived opponent's own acquisition reach (public body size, read only for tracks in `fresh`);
    falls back to the estimate when the view carries no body size for him."""
    r = dict(getattr(view, 'body_reach', ()) or ()).get(o.entity)
    return acquisition_reach(view) if r is None else r + ACQ_RADIUS_M + ACQ_EXTRA_M


def time_to_contact(view, o, reach=None):
    """Seconds until believed opponent `o` can reach the carrier: (distance - his reach) over his closing speed (>= 1 m/s)."""
    reach = opp_reach(view, o) if reach is None else reach
    dx, dy = view.x - o.x, view.y - o.y
    d = hypot(dx, dy)
    if d < 1e-9:
        return 0.
    closing = max(CLOSING_MIN_MS, (o.vx * dx + o.vy * dy) / d)
    return max(0., d - reach) / closing


def release_time_s(view):
    """Seconds from this decision to the release: the athlete's OWN release delay (RB-3.15; the engine's
    pass_release_ms x (1.35 - .5 x ball_handling)), else the flat pass_release_ms, plus any time left on a pending command."""
    pending = 0
    if getattr(view, 'pending_command_id', None) is not None and view.pending_release_ms is not None:
        pending = max(0, view.pending_release_ms - view.delivered_ms)
    own = getattr(view, 'own_release_ms', None)
    return ((own if own is not None else getattr(view, 'pass_release_ms', 250)) + pending) / 1000.


def release_blocked(view, opps):
    """RB-3.14: some opponent, advanced to the release time, is within his reach of the release point (the carrier)."""
    t = release_time_s(view)
    if 'projected_beliefs' in view.paired_fixes:
        from .turnovers import projected
        return any(hypot(x-view.x,y-view.y) <= opp_reach(view,o)
                   for o in opps for x,y in (projected(o,view,t),))
    return any(hypot(o.x + o.vx * t - view.x, o.y + o.vy * t - view.y) <= opp_reach(view, o) for o in opps)


def is_pressured(view, opps):
    return any(time_to_contact(view, o) < PRESSURE_T_S for o in opps) or release_blocked(view, opps)


def typical_time_to(o, px, py, reach, view=None):
    """RB-3.14: seconds for a TYPICAL athlete (TYPICAL_ACCEL, TYPICAL_TOP) starting from believed opponent `o`'s position
    and velocity to come within `reach` of (px, py). Signed velocity along the line first has to be braked if it points away."""
    dx, dy = px - o.x, py - o.y
    d = hypot(dx, dy)
    D = max(0., d - reach)
    if D <= 0.:
        return 0.
    a, vmax = TYPICAL_ACCEL, (31.2928 if "planning_speed" in getattr(view,"paired_fixes",()) else TYPICAL_TOP)
    v0 = (o.vx * dx + o.vy * dy) / d
    t0 = 0.
    if v0 < 0.:
        t0, D, v0 = -v0 / a, D + v0 * v0 / (2. * a), 0.
    v0 = min(v0, vmax)
    d1 = (vmax * vmax - v0 * v0) / (2. * a)
    if D <= d1:
        return t0 + (-v0 + (v0 * v0 + 2. * a * D) ** .5) / a
    return t0 + (vmax - v0) / a + (D - d1) / vmax


def free_run_m(view, opps, aim):
    """RB-3.14: distance the carrier covers along (x,y)->aim before the first believed opponent can reach his path, minus
    CARRY_CONTACT_BUFFER_M, clamped [0, CARRY_FREE_MAX_M]. The carrier's time uses his own body; an opponent's time is
    typical-athlete kinematics from his believed velocity, to within his own acquisition reach."""
    dx, dy = aim[0] - view.x, aim[1] - view.y
    L = hypot(dx, dy)
    if L < 1e-9:
        return CARRY_FREE_MAX_M
    ux, uy = dx / L, dy / L
    top = min(L, CARRY_FREE_MAX_M)
    denials = tuple((o, opp_reach(view, o)) for o in opps)
    k = 0
    while True:
        sdist = k * CARRY_PATH_STEP_M
        if sdist > top + 1e-9:
            return round(top, 6)
        px, py = view.x + ux * sdist, view.y + uy * sdist
        t_me = time_to_cover(view, sdist, (ux, uy))
        for o, radius in denials:
            if typical_time_to(o, px, py, radius, view) <= t_me:
                return round(max(0., min(CARRY_FREE_MAX_M, sdist - CARRY_CONTACT_BUFFER_M)), 6)
        k += 1


def carry_value(view, opps, aim):
    fr = free_run_m(view, opps, aim)
    near = min((hypot(o.x - view.x, o.y - view.y) for o in opps), default=99.)
    gx = view.own_goal_x + view.attack_sign * 100.
    v = CARRY_BASE + CARRY_FREE_W * fr - (CARRY_CLOSE_PENALTY if near < CARRY_CLOSE_M else 0.)
    if hypot(gx - view.x, 50. - view.y) < CARRY_GOAL_NEAR_M and fr >= CARRY_GOAL_FREE_M:
        v += CARRY_GOAL_BONUS
    return round(v, 6), fr


def lane_margin(view, c, opps, speed, t_release=None):
    """Margin (m) by which the pass path stays beyond every opponent's own acquisition reach + LANE_MARGIN_M.
    RB-3.14: each opponent is advanced by his believed velocity over the release time and then over the ball's travel to
    each sample; samples run from the release point (f=0) to the receiver. Negative = unsafe."""
    t_release = release_time_s(view) if t_release is None else t_release
    dx, dy = c.x - view.x, c.y - view.y
    dist = hypot(dx, dy)
    margin = 99.
    denials = tuple((o, opp_reach(view, o) + LANE_MARGIN_M) for o in opps)
    if 'projected_beliefs' in view.paired_fixes:
        from .turnovers import projected
        for k in range(LANE_SAMPLES+1):
            f = k/LANE_SAMPLES
            px,py,tb = view.x+dx*f,view.y+dy*f,t_release+dist*f/speed
            for other,radius in denials:
                x,y = projected(other,view,tb)
                margin = min(margin,hypot(x-px,y-py)-radius)
        return margin
    for k in range(LANE_SAMPLES + 1):
        f = k / LANE_SAMPLES
        px, py, tb = view.x + dx * f, view.y + dy * f, t_release + dist * f / speed
        for o, radius in denials:
            margin = min(margin, hypot(o.x + o.vx * tb - px, o.y + o.vy * tb - py) - radius)
    return margin


def zone_clock_penalty(view, c, max_age_ms):
    """RB-3.13: 6.0 * (1 - t_left/2) for a receiver in the zone he attacks with t_left < 2 s. Canon (Q-RB312-2): the exact
    clock is read only for a teammate who is in the carrier's fresh tracks (age <= max_age_ms)."""
    if not 0 <= view.delivered_ms - c.captured_ms <= max_age_ms:
        return 0.
    clock = dict(getattr(view, 'mate_zone_ms', ()) or ()).get(c.entity)
    if clock is None:
        return 0.
    left = max(0., (5000 - clock) / 1000.)
    return RECEIVER_CLOCK_PENALTY * (1. - left / RECEIVER_CLOCK_LIMIT_S) if left < RECEIVER_CLOCK_LIMIT_S else 0.


def pass_value(view, c, opps, pressured, max_age_ms=2000, *, handoff=False):
    """(value, gain, margin) for a pass to believed teammate track `c`; None outside the range or on an unsafe lane."""
    from .throw_speed import release_speed
    sg = view.attack_sign
    dx, dy = c.x - view.x, c.y - view.y
    dist = hypot(dx, dy)
    if not handoff and not PASS_MIN_M <= dist <= PASS_MAX_M:
        return None
    from . import paired_policy as paired
    from .ladder import pass_target
    speed = pass_target(view,c.entity,dist) if paired.enabled(view,'pass_speed') else release_speed(dist, view.max_throw_speed if paired.enabled(view,'arrival_lane') else 120.)
    margin = 10. if handoff else (paired.arrival_clearance(view,(c.x,c.y),speed,1.6,opps)
              if paired.enabled(view,'arrival_lane') else lane_margin(view,c,opps,speed))
    if margin < 0:
        return None                                              # unsafe lane: excluded
    if not handoff and rb319_has(view, 'A4') and pass_exit_s(view, c, speed) < PASS_EXIT_MIN_S:
        return None                                              # RB-3.19 A4: a missed ball would leave the field within 1 s of the receiver
    gain = max(GAIN_MIN_M, min(GAIN_MAX_M, sg * dx))
    space = min([hypot(o.x - c.x, o.y - c.y) for o in opps] + [10.])
    v = (PASS_BASE + PASS_GAIN_W * gain + PASS_CLEAR_W * (min(margin, 10.) - PASS_CLEAR_BASE)
         + (PASS_SPACE_W + C.owned_effect(view, 'playmaking', .10, agent='playmaking')) * (space - PASS_SPACE_BASE) - PASS_DIST_W * dist
         + (PRESSURED_BONUS if pressured and space >= PRESSURED_SPACE_M else 0.)
         - (BACKWARD_W * abs(gain) if gain < 0 and not pressured else 0.)
         - zone_clock_penalty(view, c, max_age_ms))
    return round(v, 6), gain, margin


def carrier_options(view, fresh, carry_aim, sg=None, max_age_ms=2000):
    """RB/3 carry and pass options for the ball carrier: [(kind, target, aim, value)], in the M1 tuple form.
    carry_aim None (a Keeper) means no carry option. Pure: own belief tracks (`fresh`), own body, own feedback."""
    opps = [t for t in fresh if t.team not in (view.team, 'ball') and t.role != 'archer']
    mates = sorted((t for t in fresh if t.team == view.team and t.role != 'archer' and t.entity != view.athlete), key=lambda t: t.entity)
    pressured = is_pressured(view, opps)
    held = getattr(view, 'own_control_ms', None)
    committed = (not pressured) and held is not None and held < COMMIT_MS
    out = []
    passes = []
    if carry_aim is not None and rb319_has(view, 'A2'):
        carry_aim = keep_in(view, carry_aim)          # RB-3.19 A2
    for c in mates:
        r = pass_value(view, c, opps, pressured, max_age_ms)
        if r is None:
            continue
        v, gain, margin = r
        if committed and not (gain >= COMMIT_GAIN_M and margin >= COMMIT_CLEAR_M):
            continue
        passes.append(('pass', c.entity, (c.x, c.y), v))
    if carry_aim is not None:
        best_aim, best_v = carry_aim, carry_value(view, opps, carry_aim)[0]
        dx, dy = carry_aim[0] - view.x, carry_aim[1] - view.y
        L = hypot(dx, dy)
        if pressured and not passes and L > 1e-9:       # pressured with no safe pass: look for a lateral way out
            from math import cos, sin, radians
            near = min(opps, key=lambda o: (hypot(o.x - view.x, o.y - view.y), o.entity), default=None)
            nx, ny = ((near.x - view.x), (near.y - view.y)) if near is not None else (0., 0.)
            nl = hypot(nx, ny) or 1.
            toward = lambda ax, ay: ((ax - view.x) * nx + (ay - view.y) * ny) / (nl * (hypot(ax - view.x, ay - view.y) or 1.))
            best_key = (best_v, -toward(*best_aim))     # equal values (e.g. all blocked): prefer the direction away from the nearest opponent
            for ang in ESCAPE_ANGLES_DEG:
                c_, s_ = cos(radians(ang)), sin(radians(ang))
                aim = (round(_clamp(view.x + (dx * c_ - dy * s_) / L * ESCAPE_LEN_M), 3), round(_clamp(view.y + (dx * s_ + dy * c_) / L * ESCAPE_LEN_M), 3))
                if rb319_has(view, 'A2'):
                    aim = keep_in(view, aim)
                v_ = carry_value(view, opps, aim)[0]
                key = (v_, -toward(*aim))
                if key[0] > best_key[0] + 1e-9 or (abs(key[0] - best_key[0]) <= 1e-9 and key[1] > best_key[1] + 1e-9):
                    best_aim, best_v, best_key = aim, v_, key
        out.append(('carry', None, best_aim, best_v))
    out.extend(passes)
    if (view.cognition == 'native-rb/3' and getattr(view, 'rb3_handoff_block_enabled', False)
            and not getattr(view, 'snap_hold', False) and view.body):
        arm_reach = dict(getattr(view, 'body_reach', ()))
        frozen = {pid for pid, light in getattr(view, 'status_indicators', ()) if light == 'red'}
        for mate in mates:
            if mate.entity in frozen:
                continue
            if hypot(mate.x - view.x, mate.y - view.y) > view.body.reach + arm_reach.get(mate.entity, view.body.reach):
                continue                                                  # B1: the receiver is within reach
            if not C.in_own_zone(view.team, view.x, view.y, view) and C.in_own_zone(view.team, mate.x, mate.y, view):
                continue
            faster = view.attack_sign * (mate.vx - view.body.vx) >= HANDOFF_FASTER_MS
            backward = view.attack_sign * (mate.x - view.x) < 0
            if not (pressured or faster) or (backward and not pressured):
                continue                                                  # B1 (RB-3.19, restored in RB-3.21): pressured, or the receiver is clearly faster; never back unless pressured
            hb = getattr(view, 'handed_by', None)
            if hb is not None and hb[0] == mate.entity and hb[1] < HANDBACK_MS:
                continue                                                  # RB-3.20b: no immediate hand-back
            value, _, _ = pass_value(view, mate, opps, pressured, max_age_ms, handoff=True)
            out.append(('handoff', mate.entity, (mate.x, mate.y), value))
    return out


# ------------------------------------------------ RB-3.19 keep the ball in play (A2, A3, A4)
# BEHAVIORAL defaults, PROVISIONAL (lead decisions, 20 Nov 2026). Only when the team instruction view.rb319 lists the step.
#  constant              value  meaning
#  BOUNDARY_MARGIN_M     2.0    A2: carry/escape/truck aims stay at least this far inside every boundary line (convex clamp of the aim);
#                               the end line inside the goal mouth (|y-50| <= goal_radius) is the goal and is exempt
#  PURSUERS              2      A3: the nearest two teammates (by time to the ball's path before it reaches a line) pursue a loose ball
#  PURSUIT_STEP_S        .1     A3: sampling step of the ball's path
#  PASS_EXIT_MIN_S       1.0    A4 (RB-3.21: RB-3.20b's 0.5 s reverted): no pass whose path, if not caught, reaches a boundary line less than this many seconds beyond the receiver
BOUNDARY_MARGIN_M, PURSUERS, PURSUIT_STEP_S, PASS_EXIT_MIN_S = 2.0, 2, .1, 1.0     # RB-3.21: A4 horizon back to 1.0 s (lead; RB-3.20b 0.5 s reverted)

# ------------------------------------------------ RB-3.19 Part B tactics (B1 handoff, B2 blocks, B3 carrier moves)
# BEHAVIORAL defaults, PROVISIONAL (lead decisions, 21 Nov 2026); only when rb3_handoff_block_enabled / rb3_carrier_moves_enabled.
#  HANDOFF_FASTER_MS      2.0   B1: receiver this much faster toward the attacked goal (m/s), or the carrier is pressured
#  HANDBACK_MS            2000  B1 (RB-3.20b, kept in RB-3.21): never back to the teammate who handed me the ball within this
#  BLOCKERS               2     B2: at most this many off-ball attackers block (within BLOCK_NEAR_M of the carrier and AHEAD of him)
#  BLOCK_NEAR_M / BLOCK_FAR_M  8 / 10  B2: blocker distance to the carrier; never block a defender farther than BLOCK_FAR_M from the carrier
#  BLOCK_THREAT_S         1.5   B2: block defenders whose time-to-contact with the carrier is under this
#  MOVE_REACT_S           0.5   B3: truck / stiff-arm only when a tackler reaches the carrier within this
#  FACING_GOAL_COS        .5    B3: the carrier is "facing the goal" if his heading is within 60 degrees of it
HANDOFF_FASTER_MS = 2.0
HANDBACK_MS = 2000      # RB-3.20b (kept in RB-3.21): no hand-back to the giver within this
BLOCKERS, BLOCK_NEAR_M, BLOCK_FAR_M, BLOCK_THREAT_S = 2, 8., 10., 1.5
MOVE_REACT_S, FACING_GOAL_COS = .5, .5


def rb319_has(view, part):
    return view.cognition == 'native-rb/3' and part in (getattr(view, 'rb319', '') or '')


def keep_in(view, aim):
    """A2: clamp an aim into the field minus BOUNDARY_MARGIN_M (the box is convex, so the path from any inside point stays inside);
    the end line within the goal mouth is exempt."""
    m = BOUNDARY_MARGIN_M
    x, y = aim
    y = max(m, min(100. - m, y))
    if "mouth_boundary" in getattr(view,"paired_fixes",()):
        from .geometry import goal_section
        outside = not goal_section(y,.62*(view.body.height if view.body else 2.39),.1075,view.goal_radius)
    else:
        outside = abs(y - 50.) > view.goal_radius
    if outside:
        x = max(m, min(100. - m, x))
    return (round(x, 3), round(y, 3))


def pass_exit_s(view, c, speed):
    """A4: seconds, beyond the receiver, until the line of the pass reaches a boundary (end line in the goal mouth exempt); inf if none."""
    dx, dy = c.x - view.x, c.y - view.y
    L = hypot(dx, dy)
    if L < 1e-9:
        return float('inf')
    ux, uy = dx / L, dy / L
    best = float('inf')
    if abs(ux) > 1e-9:
        d = ((100. if ux > 0 else 0.) - c.x) / ux
        if d >= 0 and abs(c.y + uy * d - 50.) > view.goal_radius:
            best = min(best, d)
    if abs(uy) > 1e-9:
        d = ((100. if uy > 0 else 0.) - c.y) / uy
        if d >= 0:
            best = min(best, d)
    return best / max(speed, 1e-6)


def missed_ball_pursuit(view, belief, intent, record):
    """A3: the passer's team's two nearest (by time to intercept the loose ball's path before it reaches a line) pursue it at once."""
    sig = view.signals
    if (not rb319_has(view, 'A3') or view.role != 'field' or view.holds_ball or view.restart is not None or sig.phase != 'live'
            or sig.ball_status != 'loose' or sig.passive_team != view.team or view.pending_command_id is not None
            or view.body is None or getattr(view, 'snap_hold', False)):
        return intent, record
    if view.registry_ratings and view.prism_agent not in ('in_air_ball_pursuit', 'live_ball_pursuit'):
        return intent, record
    fresh = _fresh(view, belief, 700)
    ball = next((t for t in fresh if t.entity == C.BALL), None)
    if ball is None:
        return intent, record
    frozen = {pid for pid, light in getattr(view, 'status_indicators', ()) if light == 'red'}
    mates = [t for t in fresh if t.team == view.team and t.role == 'field' and t.entity != view.athlete and t.entity not in frozen]
    if view.registry_ratings:
        trust = C.PRISM.forecast_factor(C.registry_rating(view, 'anticipation'))
        ball = replace(ball, vx=ball.vx * trust, vy=ball.vy * trust)
    sp = hypot(ball.vx, ball.vy)
    t_line = 6.
    if sp > 1e-6:
        for lim_t in ((100. - ball.x) / ball.vx if ball.vx > 1e-9 else (0. - ball.x) / ball.vx if ball.vx < -1e-9 else 99.,
                      (100. - ball.y) / ball.vy if ball.vy > 1e-9 else (0. - ball.y) / ball.vy if ball.vy < -1e-9 else 99.):
            t_line = min(t_line, max(0., lim_t))
    steps = [k * PURSUIT_STEP_S for k in range(int(t_line / PURSUIT_STEP_S) + 1)] or [0.]
    if 'projected_beliefs' in view.paired_fixes:
        from .turnovers import projected
        pts = [projected(ball,view,t) for t in steps]
    else:
        pts = [(ball.x + ball.vx * t, ball.y + ball.vy * t) for t in steps]

    def plan(arrive):
        """Earliest rendezvous with the ball's path before the line: argmin over the path samples of max(his arrival, the ball's time)."""
        best = min(((max(arrive(pt), t), t, pt) for t, pt in zip(steps, pts)), key=lambda r: (r[0], r[1]))
        return best[0], best[2]

    me_t, me_pt = plan(lambda pt: time_to_cover(view, hypot(pt[0] - view.x, pt[1] - view.y), _unit(view.x, view.y, *pt)))
    keys = [(me_t, view.athlete)] + [(plan(lambda pt, m=m: typical_time_to(m, pt[0], pt[1], 0., view))[0], m.entity) for m in mates]
    allowance = C.owned_effect(view, view.prism_agent, 1.5) if view.registry_ratings else 0.
    order = sorted((t - allowance if who == view.athlete else t, who) for t, who in keys)
    if view.athlete not in [who for _, who in order[:PURSUERS]]:
        return intent, record
    aim = (round(_clamp(me_pt[0]), 3), round(_clamp(me_pt[1]), 3))
    return (replace(intent, kind='pursue', aim=aim, target=C.BALL, contact=None),
            dict(record, rb319_pursuit=dict(t_s=round(me_t, 2), rank=sorted(keys).index((me_t, view.athlete)))))


# ------------------------------------------------ RB-3.15 shot quality (S-1 aim, S-2 lane)
# BEHAVIORAL defaults, PROVISIONAL, unsearched (lead decisions, 20 Nov 2026).
#  constant              value   meaning
#  SHOT_DY_M             -2.4..2.4 step .6   candidate aim offsets from the goal centre (goal plane)
#  SHOT_Z_M              .4, 1.2, 2.0        candidate aim heights
#  SHOT_BALL_R_M / EDGE  .1075 / .3          keep hypot(dy, z) <= goal_radius - ball radius - this
#  SHOT_MIN_MARGIN_M     0.3     best keeper margin below this: no shot from this decision
#  KEEPER_CENTRE_FRAC    .62     RB-3.16: believed keeper hand-point height = this x his height (engine catch kernel hand point)
#  KEEPER_HAND_FRAC      .9      RB-3.16: keeper coverage radius around that point = this x his ARM reach (engine hand sphere);
#                        R-1 maps arm reach = arm span / 2 and exposes it in body_reach (lead decision, replaces the RB-3.15 standing-reach estimate)
#  keeper position       advanced over own release delay + ball flight time (distance / shot speed) at his believed velocity
#  S-2 lane              RB-3.14 lane check from the hand to the aim point, field defenders only (keeper excluded), margin < 0 = unsafe
#  SHOT_MARGIN_W / CAP   1.5 / 2.0    value = existing shot value + SHOT_MARGIN_W x min(keeper_margin, SHOT_MARGIN_CAP)
SHOT_DY_M = (-2.4, -1.8, -1.2, -.6, 0., .6, 1.2, 1.8, 2.4)
SHOT_Z_M = (.4, 1.2, 2.0)
SHOT_BALL_R_M, SHOT_EDGE_M, SHOT_MIN_MARGIN_M = .1075, .3, .3
KEEPER_CENTRE_FRAC = .62
KEEPER_HAND_FRAC = .9
SHOT_MARGIN_W, SHOT_MARGIN_CAP = 1.5, 2.0


def shot_speed(view):
    return min(80., .5 * view.max_throw_speed)


def keeper_lateral_reach(view, k):
    """Believed keeper's reach in the goal plane (perceived body size; see the table)."""
    r = dict(getattr(view, 'body_reach', ()) or ()).get(k.entity)
    if r is None:
        r = view.body.reach if view.body is not None else ACQ_DEFAULT_REACH_M
    return KEEPER_HAND_FRAC * r


def shot_plan(view, fresh):
    """S-1 and S-2: choose the aim point on the goal plane. Returns dict(aim=(x, y), z, margin) or None (shot not offered).
    Pure: own belief tracks, own body, own release delay."""
    sg = view.attack_sign
    gx = view.own_goal_x + sg * 100.
    speed = shot_speed(view)
    t_rel = release_time_s(view)
    t_flight = abs(gx - view.x) / speed
    keeper = next((t for t in sorted(fresh, key=lambda t: t.entity)
                   if t.team not in (view.team, 'ball') and t.role == 'keeper'), None)
    fields = [t for t in fresh if t.team not in (view.team, 'ball') and t.role == 'field']
    limit = view.goal_radius - SHOT_BALL_R_M - SHOT_EDGE_M
    if keeper is not None:
        if 'projected_beliefs' in view.paired_fixes:
            from .turnovers import projected
            _,ky = projected(keeper,view,t_rel+t_flight)
        else:
            ky = keeper.y + keeper.vy * (t_rel + t_flight)
        kz = KEEPER_CENTRE_FRAC * (dict(getattr(view, 'body_height', ()) or ()).get(keeper.entity) or (view.body.height if view.body is not None else 2.39))
        klat = keeper_lateral_reach(view, keeper)
    best = None
    for dy in SHOT_DY_M:
        for z in SHOT_Z_M:
            if hypot(dy, z) > limit + 1e-9:
                continue
            margin = 99. if keeper is None else hypot(50. + dy - ky, z - kz) - klat
            key = (round(margin, 6), -abs(dy), -z, dy)
            if best is None or key > best[0]:
                best = (key, dy, z, margin)
    if best is None or best[3] < SHOT_MIN_MARGIN_M:
        return None
    _, dy, z, margin = best
    aim = (gx, round(50. + dy, 3))
    if fields:
        c = type('Aim', (), dict(x=aim[0], y=aim[1]))()
        if lane_margin(view, c, fields, speed, t_rel) < 0:
            return None                                                # S-2: a field defender can reach the shot path at release time
    return dict(aim=aim, z=z, margin=margin)


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
EXIT_MARGIN_S = 1.5           # RB-3.12: was .75. Start leaving when time needed + this margin reaches the time left (owner)
CLOSE_LEAVE_WINDOW_S = .3     # RB-3.12: |t_mark - t_arc| within this: pick the faster of closing on the mark and leaving
CLOSE_LEAVE_TIE_S = .05       # RB-3.12: ...and a difference under this is a tie: leave if the mark is moving away (owner question)
MARK_REASON_NEAR_M = 5.       # RB-3.12: an unmarked opponent in or within this of the zone is a reason to stay
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
    v = (b.maximum_speed if b else 27.) * (1. if "planning_speed" in getattr(view,"paired_fixes",()) else EXIT_SPEED_FRAC)
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


def _involved(view, belief, intent=None):
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
    if intent is not None and intent.kind == 'pursue' and cxy is None:
        return 'loose_ball_pursuit'                # RB-3.12: chasing a loose ball is involvement
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
                and _involved(view, belief, intent) is None):
            return (replace(intent, aim=_arc_point(view, gx, intent.aim[0], intent.aim[1])),
                    dict(record, rb311=dict(rule='Z-3_stay_out', aim_was=list(intent.aim))))
        return intent, record
    time_left = (ZONE_LIMIT_MS_RULE - view.zone_elapsed_ms) / 1000.
    exit_margin = EXIT_MARGIN_S + C.owned_effect(view, 'playmaking', .65, 'zone_reads', 'playmaking')
    out_dir = _unit(gx, 50., view.x, view.y)                       # outward from the goal centre: toward the arc
    t_arc = time_to_cover(view, view.zone_radius + ARC_INSET_M - d, out_dir)
    if view.holds_ball:
        finish_eta = record.get('planned_finish_eta_s')
        if finish_eta is not None and finish_eta + .15 < time_left:
            return intent, record
        rule = record.get('rb39c')
        if isinstance(rule, dict) and rule.get('rule') == 'unopposed_carry_to_goal':
            return intent, record                      # carrier rule: carrying on to score with margin (exempt)
        if intent.kind == 'shoot' and time_left * 1000. >= SHOT_MIN_TIME_MS and t_arc + exit_margin < time_left:
            return intent, record                      # a real shot option, while there is still time to exit
        if t_arc + exit_margin < time_left:
            return intent, record
        eta = time_to_cover(view, d, _unit(view.x, view.y, gx, 50.))
        if t_arc >= time_left > eta:                   # cannot clear the arc in time, but can still score
            aim = (round(gx - sg * GOAL_AIM_INSET_M, 3), 50.)
            return (replace(intent, kind='carry', aim=aim, target=None, contact=None),
                    dict(record, rb311=dict(rule='Z-2_carrier_last_resort_to_goal', eta_s=round(eta, 2), time_left_s=round(time_left, 2))))
        return _leave(view, gx, intent, record, 'Z-2_carrier_exit', t_arc_s=round(t_arc, 2), time_left_s=round(time_left, 2))
    involved = _involved(view, belief, intent)
    if involved is None:                               # Z-3: off-ball and not involved: head out at once
        return _leave(view, gx, intent, record, 'Z-3_off_ball_exit', t_arc_s=round(t_arc, 2), time_left_s=round(time_left, 2))
    if t_arc + exit_margin >= time_left:             # Z-2: involved, but his clock is running out
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
    # RB-3.12: a reason to stay is an unmarked opponent in or within MARK_REASON_NEAR_M of the zone whom he can reach in the time left
    reason = (best is not None and hypot(best.x - gx, best.y - 50.) <= view.zone_radius + MARK_REASON_NEAR_M
              and t_mark is not None and t_mark < time_left)
    if not reason:
        return _leave(view, gx, intent, record, 'Z-4_no_reason_leave', t_arc_s=round(t_arc, 2), time_left_s=round(time_left, 2))
    area_margin = EXIT_MARGIN_S + C.owned_effect(view, 'zone_coverage', .65, agent='zone_coverage')
    if min(t_arc, t_mark) + area_margin < time_left:
        return intent, record
    diff = t_mark - t_arc
    if abs(diff) <= CLOSE_LEAVE_TIE_S:                  # tie: leave if the mark is moving away from me
        ux, uy = _unit(view.x, view.y, best.x, best.y) or (0., 0.)
        close = (best.vx * ux + best.vy * uy) <= 0.
    else:
        close = t_mark < t_arc                          # within CLOSE_LEAVE_WINDOW_S or not: the faster
    if close:
        aim = _toward(best.x, best.y, gx, 50., MARK_STANDOFF * mark)
        return (replace(intent, kind='mark', aim=aim, target=best.entity, contact=None),
                dict(record, rb311=dict(rule='Z-4_close_on_mark', target=best.entity, t_mark_s=round(t_mark, 2), t_arc_s=round(t_arc, 2), time_left_s=round(time_left, 2))))
    cross = _leave_distance(view, gx, intent.aim) if intent.aim is not None else None
    if cross is not None and time_to_cover(view, cross, _unit(view.x, view.y, *intent.aim)) <= t_arc * 1.15:
        return intent, record
    return _leave(view, gx, intent, record, 'Z-4_leave', t_arc_s=round(t_arc, 2), time_left_s=round(time_left, 2))


def ttc_at(view, o, cx, cy):
    """Time-to-contact of believed opponent `o` with a body at (cx, cy) (the believed carrier): RB-3.13 definition."""
    dx, dy = cx - o.x, cy - o.y
    d = hypot(dx, dy)
    if d < 1e-9:
        return 0.
    closing = max(CLOSING_MIN_MS, (o.vx * dx + o.vy * dy) / d)
    return max(0., d - opp_reach(view, o)) / closing


def choose_block(view, belief, intent, record):
    """B2: up to BLOCKERS off-ball attackers within BLOCK_NEAR_M of the carrier and ahead of him block the defenders whose
    time-to-contact with him is under BLOCK_THREAT_S; each takes the threat he can reach first; none beyond BLOCK_FAR_M."""
    if (view.registry_ratings and view.prism_agent != 'playmaking'):
        return intent, record
    if (view.cognition != 'native-rb/3' or not getattr(view, 'rb3_handoff_block_enabled', False)
            or view.role != 'field' or view.holds_ball or view.pending_command_id
            or view.signals.phase != 'live' or getattr(view, 'snap_hold', False)
            or view.signals.passive_team != view.team or view.body is None):
        return intent, record
    fresh = _fresh(view, belief, belief.max_track_age_ms)
    carrier_id = (record.get('believed_carrier') or (None,))[0]
    carrier = next((p for p in fresh if p.entity == carrier_id and p.team == view.team), None)
    if carrier is None:
        return intent, record
    frozen = {pid for pid, light in getattr(view, 'status_indicators', ()) if light == 'red'}
    sg = view.attack_sign
    threats = []
    for t in fresh:
        if t.role != 'field' or t.team in (view.team, 'ball') or t.entity in frozen:
            continue
        if hypot(t.x - carrier.x, t.y - carrier.y) <= BLOCK_FAR_M and ttc_at(view, t, carrier.x, carrier.y) < (
                    BLOCK_THREAT_S + C.owned_effect(view, 'playmaking', .35, agent='playmaking')):
            threats.append(t)
    if not threats:
        return intent, record
    me = type('Me', (), dict(entity=view.athlete, x=view.x, y=view.y, vx=view.body.vx, vy=view.body.vy))()
    pool = [me] + [t for t in fresh if t.team == view.team and t.role == 'field' and t.entity not in (view.athlete, carrier.entity) and t.entity not in frozen]
    cands = sorted((q for q in pool if sg * (q.x - carrier.x) > 0 and hypot(q.x - carrier.x, q.y - carrier.y) <= BLOCK_NEAR_M),
                   key=lambda q: (hypot(q.x - carrier.x, q.y - carrier.y), q.entity))[:BLOCKERS]
    left = list(threats)
    mine = None
    for q in cands:
        if not left:
            break
        if q.entity == view.athlete:
            reach_t = lambda o, q=q: time_to_cover(view, hypot(o.x - q.x, o.y - q.y), _unit(q.x, q.y, o.x, o.y))
        else:
            reach_t = lambda o, q=q: typical_time_to(q, o.x, o.y, 0., view)
        pick = min(left, key=lambda o: (reach_t(o), o.entity))
        left.remove(pick)
        if q.entity == view.athlete:
            mine = pick
    if mine is None:
        return intent, record
    point = (carrier.x, carrier.y)
    return (replace(intent, kind='block', target=mine.entity, aim=point, contact=None),
            dict(record, selected=['block', mine.entity, point], rb317_protected=carrier.entity))


def choose_carrier_move(view, belief, intent, record):
    if (view.cognition != 'native-rb/3' or not getattr(view, 'rb3_carrier_moves_enabled', False)
            or not view.holds_ball or not view.body or view.role != 'field'
            or view.pending_command_id or view.signals.phase != 'live' or getattr(view, 'snap_hold', False)):
        return intent, record
    goal = 100. - view.own_goal_x
    if abs(goal - view.x) <= view.body.reach + 1. and abs(view.y - 50.) < view.goal_radius:
        choice = ('stretch', None, (goal, view.y))
    else:
        frozen = {pid for pid, light in getattr(view, 'status_indicators', ()) if light == 'red'}
        front = (view.body.vx, view.body.vy) if hypot(view.body.vx, view.body.vy) > .3 else (view.attack_sign, 0.)
        candidates = []
        for opponent in _fresh(view, belief, belief.max_track_age_ms):
            if opponent.team == view.team or opponent.role != 'field' or opponent.entity in frozen:
                continue
            dx, dy = opponent.x - view.x, opponent.y - view.y
            distance = hypot(dx, dy)
            if not distance or dx * front[0] + dy * front[1] < 0:
                continue
            nx, ny = dx / distance, dy / distance
            own_speed = view.body.vx * nx + view.body.vy * ny
            opp_speed = -(opponent.vx * nx + opponent.vy * ny)
            if own_speed + opp_speed > 0.:
                candidates.append((distance, opponent.entity, opponent, own_speed, opp_speed))
        if not candidates:
            return intent, record
        candidates = [c for c in candidates if ttc_at(view, c[2], view.x, view.y) <= MOVE_REACT_S]    # B3: a tackler reaches me within 0.5 s
        if not candidates:
            return intent, record
        distance, _, opponent, own_speed, opp_speed = min(candidates)
        # Size and closing motion are public. Use the 0.70 control as an
        # opponent strength prior and scale its mass by observed height.
        height = dict(getattr(view, 'body_height', ())).get(opponent.entity, 2.39)
        mass = 226. * (height / 2.39) ** 3
        own_mass = view.own_mass_kg or 226.
        radius = lambda kg: max(.38, min(.82, .30 + .00065 * kg))
        closing_ms = 1000 * max(0., distance - radius(own_mass) - radius(mass)) / (own_speed + opp_speed)
        strength = dict(view.own_skills).get('strength', .70)
        heading = hypot(view.body.vx, view.body.vy)
        facing_goal = view.attack_sign * view.body.vx > FACING_GOAL_COS * heading if heading > .3 else True
        if closing_ms <= 300 and own_speed > 0 and facing_goal and own_mass * own_speed * strength > mass * max(0., opp_speed) * .70:
            choice = ('truck', opponent.entity, (opponent.x, opponent.y))
        elif opp_speed > 0 and distance <= view.body.reach + radius(mass) and (
                not view.registry_ratings or closing_ms / 1000 <= C.PRISM.reflex_seconds(
                    C.registry_rating(view, 'reflex'))):
            choice = ('stiff_arm', opponent.entity, None)
        else:
            return intent, record
    kind, target, aim = choice
    return (replace(intent, kind=kind, target=target, aim=aim, contact=None),
            dict(record, selected=list(choice), rb318_move=kind))


def adjust(view, belief, intent, record):
    intent, record = carrier_to_goal(view, belief, intent, record)
    intent, record = defender_baseline(view, belief, intent, record)
    intent, record = zone_behavior(view, belief, intent, record)
    intent, record = missed_ball_pursuit(view, belief, intent, record)
    intent, record = choose_block(view, belief, intent, record)
    intent, record = choose_carrier_move(view, belief, intent, record)
    if rb319_has(view, 'A2') and intent.kind in ('carry', 'truck') and intent.aim is not None and view.holds_ball:
        intent = replace(intent, aim=keep_in(view, tuple(intent.aim)))     # RB-3.19 A2: also for the Part B moves and the zone/goal rules
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


# ------------------------------------------------ RB-3.21 the Native Keeper's course with the ball material
def keeper_decide(view, belief, material):
    """b1.emergence_intents.decide_keeper with the course forecast by the Beastball ball material (same decision rules;
    only the forecast differs). `material` is the public (k, h, e, a_roll) of the ball."""
    import math
    from b1 import emergence_intents as E
    from native.rulebook.ball_material import path
    iid = f'{view.observation_id}/keeper-intent'
    if belief is None:
        return E.KeeperIntent(iid, view.body.athlete, 'hold', view.now_ms, None, target=(view.body.x, view.body.y), reason='no_delivered_ball_belief')
    if not belief.fresh(view.now_ms):
        return E.KeeperIntent(iid, view.body.athlete, 'hold', view.now_ms, belief.revision, target=(view.body.x, view.body.y), reason='stale_ball_belief')
    course = tuple(path((belief.x, belief.y, belief.z, belief.vx, belief.vy, belief.vz), tuple(material), belief.radius, 3., .01, -2., 102.))
    cross = E._goal_crossing(view, course)
    if cross is None:
        target = view.position_belief or (view.body.x, view.body.y)
        return E.KeeperIntent(iid, view.body.athlete, 'position', view.now_ms, belief.revision, target=target, reason='no_believed_threat')
    usable = tuple(p for p in course if p[0] <= cross[0] + 1e-12)
    return E.KeeperIntent(iid, view.body.athlete, 'save', view.now_ms, belief.revision,
                          intercept_window_ms=(view.now_ms, view.now_ms + int(math.ceil(cross[0] * 1000))),
                          course=usable, reason='believed_goal_crossing')


def flight_horizon(course):
    """Time to floor on the delivered course, bounded by the caller's horizon."""
    from math import sqrt
    gravity = 9.81
    return (course.vz + sqrt(course.vz ** 2 + 2 * gravity * max(0., course.z - course.radius))) / gravity


FINISH_CLOSE_DEPTH_M = 10.
FINISH_DY_M = (-2.8, -2.65, *SHOT_DY_M, 2.65, 2.8)
FINISH_LONG_RESERVE_M = .34
FINISH_CLOSE_RESERVE_M = .18


def finishing_aim(view, fresh, intent):
    """Choose the farthest reachable mouth sample after the shot is selected."""
    gx = intent.aim[0]
    speed = intent.speed
    if speed <= 0.:
        return intent
    keeper = next((t for t in fresh if t.team not in (view.team, 'ball') and t.role == 'keeper'), None)
    if keeper is None:
        return intent
    field = [t for t in fresh if t.team not in (view.team, 'ball') and t.role == 'field']
    horizon = release_time_s(view) + abs(gx - view.x) / speed
    if 'projected_beliefs' in view.paired_fixes:
        from .turnovers import projected
        _,ky = projected(keeper,view,horizon)
    else:
        ky = keeper.y + keeper.vy * horizon
    height = dict(getattr(view, 'body_height', ())).get(keeper.entity, 2.39)
    kz = KEEPER_CENTRE_FRAC * height
    reserve = FINISH_CLOSE_RESERVE_M if abs(view.x - gx) < FINISH_CLOSE_DEPTH_M else FINISH_LONG_RESERVE_M
    rim = view.goal_radius - SHOT_BALL_R_M - reserve * (1 - C.registry_rating(view, 'finishing'))
    candidates = sorted(((hypot(50 + dy - ky, z - kz), dy, z)
                         for dy in FINISH_DY_M for z in SHOT_Z_M if hypot(dy, z) < rim),
                        reverse=True)
    for _, dy, z in candidates:
        aim = type('Aim', (), {'x': gx, 'y': 50. + dy})()
        if not field or lane_margin(view, aim, field, speed) >= 0:
            return replace(intent, aim=(aim.x, aim.y), height=z)
    return intent


def committed_delivery(view, belief, intent):
    """Pure sub-agent choice from the same frozen belief used by its parent."""
    if intent.aim is None or intent.kind not in ('pass', 'shoot'):
        return intent
    fresh = _fresh(view, belief, belief.max_track_age_ms)
    if intent.kind == 'shoot':
        return finishing_aim(view, fresh, intent)
    from .throw_speed import release_speed
    distance = hypot(intent.aim[0] - view.x, intent.aim[1] - view.y)
    speed, height = C.PRISM.pass_delivery(distance, view.max_throw_speed,
                                          release_speed(distance, view.max_throw_speed),
                                          C.registry_rating(view, 'passing'))
    opponents = tuple(t for t in fresh if t.role == 'field' and t.team != view.team)
    lane = type('Aim', (), {'x': intent.aim[0], 'y': intent.aim[1]})()
    if opponents and lane_margin(view, lane, opponents, speed) < 0:
        return intent
    return replace(intent, speed=speed, height=height)
