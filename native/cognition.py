"""Native v0 pure primitive cognition.
Provenance: B1 cognition at 7741539/5c23fe8, Emergence-1 761dca5.
Default parameters are unsearched; procedural choices are PLACEHOLDERs.
Cognition receives only an immutable view and own belief. No quality claim.
"""
from dataclasses import dataclass, asdict, replace
from math import hypot
from .emergence.params import PolicyParams
from .emergence.positioning import choose_position
from .individuation import effect as rating_effect
from . import prism_registry as PRISM


def registry_rating(view, name):
    return next((r for key, r in view.registry_ratings if key == name), PRISM.AVERAGE)


def owned_effect(view, name, scale, legacy=None, agent=None):
    if not view.registry_ratings:
        return rating_effect(view, legacy or name, scale)
    if agent and view.prism_agent != agent:
        return 0.
    return (registry_rating(view, name) - PRISM.AVERAGE) * scale

from b1 import communication as COM
from b1 import emergence_intents as E
from b1 import core as M1          # Base A (governed M1) pure decision code

BALL = 'BALL'
BALL_KINDS = ('pass', 'shoot', 'draw_release', 'restart_pass')
FAILED = ('interrupted', 'release_failed')


@dataclass(frozen=True)
class Track:
    entity: str
    team: str          # 'A' / 'B' / 'ball'
    role: str          # public (uniform): field / keeper / archer / ball
    x: float
    y: float
    vx: float
    vy: float
    captured_ms: int


@dataclass(frozen=True)
class Signals:
    """Public officiating / scoreboard signals (not hidden state)."""
    phase: str
    period: int
    game_ms: int
    possession_ms: int
    score_own: int
    score_opp: int
    restart_team: str | None
    restart_xy: tuple | None
    i_am_taker: bool
    # rules signals from the authoritative possession layer (D1 record section 3)
    passive_team: str | None = None      # PP; None until the first direct possession (R-01)
    direct_team: str | None = None
    direct_holder: str | None = None
    contested: bool = False
    ball_status: str | None = None
    immune: tuple = ()                   # players visibly frozen / immune (public)
    pass_call: tuple | None = None       # teammate's shouted pass: (passer, target, aim_x, aim_y)
    tackle_count: int = 0                # public scoreboard fact


@dataclass(frozen=True)
class AthleteView:
    observation_id: str
    athlete: str
    team: str
    role: str
    slot: int
    delivered_ms: int
    x: float
    y: float
    holds_ball: bool
    attack_sign: int
    own_goal_x: float
    tracks: tuple
    signals: Signals
    pending_command_id: str | None = None
    pending_kind: str | None = None
    pending_target: str | None = None
    pending_release_ms: int | None = None
    arrows_loaded: int | None = None
    last_release_ms: int | None = None
    posture: str = 'upright'
    policy: PolicyParams = PolicyParams()
    body: E.AthleteBody | None = None
    restart: tuple | None = None
    contestant: str | None = None
    hunt: bool = False
    bench_role: str | None = None
    dribble_used: bool = False
    zone_elapsed_ms: int = 0
    max_throw_speed: float = 40.
    goal_radius: float = 3.
    hunt_cleared: bool = False
    messages: tuple[COM.Delivery, ...] = ()
    ownership_enabled: bool = False
    ball_course: E.BallCourseBelief | None = None
    own_restraint: float = 0.
    tuck_fraction: float = 0.
    zone_radius: float = 20.0            # G: inside = distance < R
    # native-v0/3 (FAB-1); defaults leave native-v0/2 decisions unchanged
    cognition: str = 'native-v0/2'
    own_held: int = 0                    # SELF-1 touch: opponents' holds on my own body
    own_balance_load: float = 0.         # SELF-1: own balance, 0 settled .. 1 grounded
    own_hold_target: str | None = None   # own action: whom my own hands hold
    own_mass_kg: float | None = None     # ATTR-1: exact own-body knowledge only
    individual_ratings: tuple[tuple[str, float], ...] = ()
    registry_ratings: tuple[tuple[str, float], ...] = ()
    recognized_ball: str | None = None
    prism_agent: str | None = None
    core_entropy: str | None = None
    core_decision_ms: int = 500
    core_motion: tuple | None = None
    own_skills: tuple = ()               # ATTR-1: self only; never teammate/opponent ratings


@dataclass(frozen=True)
class BeliefState:
    revision: str
    observation_id: str
    tracks: tuple
    own_feedback: tuple = ()
    max_track_age_ms: int = 2000
    last_ball: tuple | None = None      # (x, y, captured_ms) own memory
    ball_course: E.BallCourseBelief | None = None
    messages: tuple[COM.Delivery, ...] = ()


@dataclass(frozen=True)
class ActionIntent:
    intent_id: str
    decision_id: str
    athlete: str
    kind: str
    target: str | None
    aim: tuple | None
    aim_vel: tuple | None
    gaze: tuple | None
    decided_ms: int
    related_command_id: str | None = None
    speed: float = 27.
    height: float = 1.6
    auxiliary: E.KeeperIntent | None = None
    contact: str | None = None
    record_id: str | None = None
    period: int | None = None
    wait_ms: int = 0
    technique: str | None = None


@dataclass(frozen=True)
class MotorCommand:
    command_id: str
    intent: ActionIntent
    start_ms: int
    release_ms: int | None
    resource: str       # 'ball' | 'bow' | 'locomotion'
    desired_velocity: tuple | None = None   # pass-release-v1: admitted at ingress


@dataclass(frozen=True)
class PhysicalOutcome:
    outcome_id: str
    command_id: str | None
    status: str
    resolved_ms: int
    entity_id: str | None = None


def receive_outcome(outcome):
    """Restricted own-action feedback: id, status, time only."""
    return (outcome.outcome_id, outcome.status, outcome.resolved_ms)


def _clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


def position_from_belief(view, ref_x, defending):
    # Provenance 761dca5; Native has no role/slot anchors.
    fresh = tuple(t for t in view.tracks if view.delivered_ms-t.captured_ms<=2000)
    ball = next((t for t in fresh if t.entity==BALL),None)
    mode = 'none' if view.signals.passive_team is None else 'att' if view.signals.passive_team==view.team else 'def'
    return choose_position(view.x,view.y,view.own_goal_x,view.attack_sign,view.zone_radius,
                           (ball.x,ball.y) if ball else None,None,mode,
                           tuple((t.x,t.y) for t in fresh if t.team==view.team),
                           tuple((t.x,t.y) for t in fresh if t.team not in (view.team,'ball')),view.policy)[0]


def _lane_clearance(ox, oy, tx, ty, opponents):
    dx, dy = tx - ox, ty - oy
    d2 = dx * dx + dy * dy
    clearance = 10.0
    for o in opponents:
        f = _clamp(((o.x - ox) * dx + (o.y - oy) * dy) / d2, 0., 1.) if d2 > 0 else 0.
        clearance = min(clearance, hypot(o.x - ox - f * dx, o.y - oy - f * dy))
    return clearance


def _pass_options(view, mates, opps, restart=False):
    out = []
    sg = view.attack_sign
    near = min((hypot(o.x - view.x, o.y - view.y) for o in opps), default=30.)
    for c in sorted(mates, key=lambda c: c.entity):
        if c.role == 'archer':
            continue
        dx, dy = c.x - view.x, c.y - view.y
        d = hypot(dx, dy)
        if not 4 <= d <= 34:
            continue
        clearance = _lane_clearance(view.x, view.y, c.x, c.y, opps)
        value = (min(clearance, 6.) - 3. + .08 * sg * dx - .03 * d
                 + (2. if near < 3. else 0.) + (3. if restart else 0.))
        out.append(('restart_pass' if restart else 'pass', c.entity,
                    (round(c.x, 3), round(c.y, 3)), round(value, 6)))
    return out


def rb3_lead(x, y, aim, vel, max_throw_speed, iterations=6):
    """RB-3.9b E-1/B-1 (native-rb/3): lead a moving receiver by the real flight time at the speed
    chosen for the led distance. Fixed point: the speed depends on the led aim, the aim on the speed.
    Returns (aim, flight_time_s, speed)."""
    from .throw_speed import release_speed, flight_time
    tf = 0.
    for _ in range(iterations):
        led = (_clamp(aim[0] + vel[0] * tf, 2, 98), _clamp(aim[1] + vel[1] * tf, 2, 98))
        d = hypot(led[0] - x, led[1] - y); speed = release_speed(d, max_throw_speed); tf = flight_time(d, speed)
    led = (_clamp(aim[0] + vel[0] * tf, 2, 98), _clamp(aim[1] + vel[1] * tf, 2, 98))
    return led, tf, speed


def _m1_options(view, fresh, carrier, role, **cfg):
    """Delegate a sub-decision to the Base A (M1) pure decide(); one pipeline."""
    contacts = tuple(M1.Contact(t.entity, 'neutral' if t.team == 'ball' else t.team, t.x, t.y,
                                t.captured_ms, t.vx, t.vy, bool(carrier and carrier[0] == t.entity))
                     for t in fresh if t.role != 'archer')
    v = M1.AthleteView(view.observation_id, view.athlete, view.team, view.delivered_ms,
                       view.x, view.y, view.holds_ball, contacts)
    b = M1.BeliefState(view.observation_id + '/m1', view.observation_id, contacts, (), 10 ** 9)
    return M1.decide(v, b, M1.DecisionConfig(role=role, **cfg))[1]['options']


def in_own_zone(track_team, x, y, view):
    """G: body centre strictly inside R of that team's own goal centre."""
    gx = view.own_goal_x if track_team == view.team else view.own_goal_x + view.attack_sign * 100.
    return hypot(x - gx, y - 50.) < view.zone_radius


def keeper_protected(track, view):
    """KP / R-15 from the view only: Keeper inside own zone while his team has PP."""
    return (track.role == 'keeper' and view.signals.passive_team == track.team
            and in_own_zone(track.team, track.x, track.y, view))


def archer_target_legal(t, view, now):
    # Canon: opposing fields on offence with team control, outside either zone.
    # native-v0/3 PLACEHOLDER (Q-FAB1-2): the rules layer as built has no team control while a
    # pass is in flight, so a release then is an archery_target foul; the v0/3 Archer does not
    # choose it. RB/3 restores the original predicate because its Rulebook
    # possession layer retains qualifying team control during flight.
    # RB/3 (RB-3.4 ruling 3): passive possession only; a loose ball is still the offence's.
    statuses = (('carried',) if view.cognition=='native-v0/3' else
                ('carried','pass_in_flight','loose') if view.cognition=='native-rb/3' else
                ('carried','pass_in_flight'))
    return (view.hunt_cleared and t.role=='field' and
            t.team==view.signals.passive_team and view.signals.ball_status in statuses and
            t.entity not in view.signals.immune and
            not in_own_zone(t.team,t.x,t.y,view) and
            not in_own_zone(view.team,t.x,t.y,view) and now-t.captured_ms<=700)


def _base_decide(view: AthleteView, belief: BeliefState, *, compact=False):
    if belief.observation_id != view.observation_id:
        raise ValueError('belief/view provenance mismatch')
    COM.plan_hooks(view, belief)
    now = view.delivered_ms
    fresh = tuple(t for t in belief.tracks
                  if 0 <= now - t.captured_ms <= belief.max_track_age_ms)
    ball = next((t for t in fresh if t.entity == BALL), None)
    mates = [t for t in fresh if t.team == view.team]
    opps = [t for t in fresh if t.team not in (view.team, 'ball')]
    sg = view.attack_sign
    goal = (view.own_goal_x + sg * 100., 50.)
    sig = view.signals
    latest = belief.own_feedback[-1] if belief.own_feedback else None
    failed = bool(latest and (latest[1].split(':')[0] in FAILED or latest[1].startswith('rejected_')))
    if view.holds_ball and any(f[1] in ('released:pass', 'released:shoot') for f in belief.own_feedback):
        # own-action knowledge (rule 3) overrides the delayed ball-in-hand sense: I just released it
        view = replace(view, holds_ball=False)
    banned = latest[1].split(':')[-1] if failed and ':' in latest[1] else None
    options = []      # (kind, target, aim, value)
    gaze = (ball.x, ball.y) if ball else (belief.last_ball[:2] if belief.last_ball else None)

    # believed ball carrier, from perception only
    carrier = None
    if view.holds_ball:
        carrier = ('me', view.team)
    elif ball is not None:
        best = min((t for t in mates + opps if t.role != 'archer'),
                   key=lambda t: (hypot(t.x - ball.x, t.y - ball.y), t.entity), default=None)
        read_held = not view.registry_ratings or view.recognized_ball in (None, 'held')
        if read_held and best is not None and hypot(best.x - ball.x, best.y - ball.y) < 1.8:
            carrier = (best.entity, best.team)
    bx, by = ((view.x, view.y) if view.holds_ball else (ball.x, ball.y) if ball
              else belief.last_ball[:2] if belief.last_ball else (None, None))

    if view.pending_command_id is not None:
        options.append(('continue_current', None, None, 0.))
        if view.role == 'archer' and view.pending_kind == 'draw_release':
            # Belief-driven interlock (replaces the Round 1 true-state motor interlock): the
            # Archer itself aborts the draw when, by its own current belief, the release
            # would no longer be legal. The motor never checks true state.
            tgt = next((o for o in opps if o.entity == view.pending_target), None)
            if (tgt is None or not archer_target_legal(tgt, view, now) or sig.phase != 'live'
                    or sig.passive_team is None):
                options.append(('abort_draw', view.pending_target, None, 1.))
    elif view.ownership_enabled and view.role == 'keeper' and not view.holds_ball:
        options.append(('keeper_control', None, None, 0.))
    elif view.role == 'archer':
        options.append(('archer_hold', None, None, 0.))
        # Ruleset 1.0.2 (D1 record R-17): any eligible player may be frozen; a Keeper inside
        # his own zone is protected; R-01: no target before the first passive possession.
        ready = (view.arrows_loaded or 0) > 0 and (
            view.last_release_ms is None or now - view.last_release_ms >= 2600) and not getattr(view, 'snap_hold', False)   # RB-3.13: no arrow during the snap hold
        if (ready and sig.phase == 'live' and sig.passive_team is not None and banned != 'draw_release'
                and (not view.registry_ratings or getattr(view, 'freezes_left', None) != 0)):
            for t in sorted(opps, key=lambda t: t.entity):
                if not archer_target_legal(t, view, now):
                    continue
                d = hypot(t.x - view.x, t.y - view.y)
                is_carrier = bool(carrier and carrier[0] == t.entity)
                # PRIMITIVE: carrier preferred; otherwise the opponent nearest the ball
                near_ball = hypot(t.x - bx, t.y - by) if bx is not None else 40.
                value = (3. if is_carrier else 1.6 - .04 * near_ball) - .02 * d
                if view.registry_ratings:
                    value += owned_effect(view, 'disruption',
                                          PRISM.DISRUPTION_CARRIER_WEIGHT if is_carrier else .5,
                                          agent='disruption')
                    value += owned_effect(view, 'disruption', PRISM.DISRUPTION_HOLD_WEIGHT,
                                          agent='disruption')
                options.append(('draw_release', t.entity, (round(t.x, 3), round(t.y, 3)), round(value, 6)))
    elif sig.phase not in ('live', 'opening', 'penalty', 'award'):
        if sig.i_am_taker:
            options.append(('restart_wait', None, None, 0.))
            if banned != 'restart_pass':
                options += _pass_options(view, mates, opps, restart=True)
        else:
            ref = sig.restart_xy[0] if sig.restart_xy else (bx if bx is not None else 50.)
            if view.role == 'keeper':
                options.append(('keeper_set', None, (view.own_goal_x + sg * 2., 50.), 1.))
            else:
                options.append(('position', None, position_from_belief(
                    view, ref, sig.restart_team not in (None, view.team)), 1.))
    elif view.holds_ball:
        options.append(('retain', None, None, 0.))
        if not failed or True:
            near = min((hypot(o.x - view.x, o.y - view.y) for o in opps), default=30.)
            dg = hypot(goal[0] - view.x, goal[1] - view.y)
            if view.role != 'keeper':
                if dg <= view.policy.shot_range and banned != 'shoot':
                    keeper = next((o for o in opps if o.role == 'keeper'), None)
                    side = -1. if keeper is not None and keeper.y > 50 else 1.
                    value = 5.5 - .2 * dg + (8. if near < 5.8 else 0.) + (
                        5. if 0 < sig.possession_ms < 5000 else 0.)
                    if view.cognition == 'native-rb/3':      # RB-3.15 S-1/S-2: aim away from the keeper, safe lane, margin in the value
                        from . import cognition_rb3 as R3
                        plan = R3.shot_plan(view, fresh)
                        if plan is not None:
                            options.append(('shoot', None, plan['aim'],
                                            round(value + (R3.SHOT_MARGIN_W + owned_effect(view, 'playmaking', .8, 'finishing', 'playmaking')) * min(plan['margin'], R3.SHOT_MARGIN_CAP), 6)))
                    else:
                        options.append(('shoot', None, (goal[0], 50. + side * 1.), round(value, 6)))
                # carry toward goal, drifting away from the nearest believed opponent ahead
                ahead = [o for o in opps if sg * (o.x - view.x) > 0 and hypot(o.x - view.x, o.y - view.y) < 9]
                drift = 0.
                if ahead:
                    o = min(ahead, key=lambda o: (hypot(o.x - view.x, o.y - view.y), o.entity))
                    drift = 6. if o.y <= view.y else -6.
                aim = (_clamp(view.x + sg * 10., 1, 99),
                       _clamp(view.y + drift + (.25 * (50 - view.y) if dg < 40 else 0.), 3, 97))
                options.append(('carry', None, (round(aim[0], 3), round(aim[1], 3)),
                                round(.8 + .25 * min(near, 8.), 6)))
            # Base A (M1) carrier decision supplies the carry-vs-pass valuation.
            carry_opt = next((o for o in options if o[0] == 'carry'), None)
            options = [o for o in options if o[0] != 'carry']
            if view.cognition == 'native-rb/3':      # RB-3.12 B-5: carry and pass valued by cognition_rb3.carrier_options
                from .cognition_rb3 import carrier_options
                carrier_vals = carrier_options(view, fresh, carry_opt[2] if carry_opt else None, sg, belief.max_track_age_ms)
            else:
                carrier_vals = _m1_options(view, fresh, carrier, 'carrier', carry_target=carry_opt[2] if carry_opt else None)
            for k, t, a, v in carrier_vals:
                if k == 'pass' and banned == 'pass':
                    continue
                if k == 'pass':
                    # PRIMITIVE: belief-based lead. The semantic aim is the receiver's believed
                    # position advanced by its believed velocity over the nominal flight time
                    # (cognition's choice; Motor never leads the receiver).
                    rt = next(x for x in fresh if x.entity == t)
                    if view.cognition == 'native-rb/3':
                        a = rb3_lead(view.x, view.y, a, (rt.vx * (1 + owned_effect(view, 'playmaking', .5, 'anticipation', 'playmaking')),
                                                        rt.vy * (1 + owned_effect(view, 'playmaking', .5, 'anticipation', 'playmaking'))), view.max_throw_speed)[0]
                    else:
                        tf = min(1.2, hypot(a[0] - view.x, a[1] - view.y) / 27.)
                        a = (_clamp(a[0] + rt.vx * tf, 2, 98), _clamp(a[1] + rt.vy * tf, 2, 98))
                if k in ('carry', 'pass', 'handoff'):
                    options.append((k, t, (round(a[0], 3), round(a[1], 3)),
                                    round(v + (4. if view.role == 'keeper' and k == 'pass' else 0.), 6)))
    elif view.role == 'keeper':
        gx = view.own_goal_x
        if bx is None:
            options.append(('keeper_set', None, (gx + sg * 2., 50.), 1.))
        else:
            d = hypot(bx - gx, by - 50.)
            depth = _clamp(.15 * d, 1.5, 6.)
            ux, uy = ((bx - gx) / d, (by - 50.) / d) if d > 1e-6 else (sg, 0.)
            options.append(('keeper_set', None, (round(gx + ux * depth, 3), round(50. + uy * depth, 3)), 1.))
            if ball is not None and carrier is None:
                speed = hypot(ball.vx, ball.vy)
                toward = -sg * ball.vx
                if speed > 7. and toward > 3.:
                    t_cross = abs(ball.x - gx) / toward
                    y_cross = ball.y + ball.vy * t_cross
                    if t_cross < 3. and abs(y_cross - 50.) < 9. and banned != 'keeper_save':
                        # PROVISIONAL (U-1..U-4 Keeper-zone canon open): save intent
                        options.append(('keeper_save', BALL, (round(gx, 3), round(y_cross, 3)), 6.))
                elif speed < 6. and d < 16.:
                    options.append(('pursue', BALL, (round(ball.x, 3), round(ball.y, 3)), 3.))
    else:                               # field player without the ball, live play
        if sig.pass_call and sig.pass_call[1] == view.athlete:
            # PRIMITIVE comms: a teammate called a pass to me; go to the called aim point
            aim = (sig.pass_call[2], sig.pass_call[3])
            if ball is not None and carrier is None and hypot(ball.vx, ball.vy) > 3.:
                # ball seen in flight: go to the nearest point of its believed path
                v2 = ball.vx * ball.vx + ball.vy * ball.vy
                t = _clamp(((view.x - ball.x) * ball.vx + (view.y - ball.y) * ball.vy) / v2, 0., 1.5)
                trust = PRISM.forecast_factor(registry_rating(view, 'anticipation')) if view.registry_ratings else 1.
                aim = (round(_clamp(ball.x + ball.vx * t * trust, 1, 99), 3), round(_clamp(ball.y + ball.vy * t * trust, 1, 99), 3))
            options.append(('receive', sig.pass_call[0], aim, 5.))
        if bx is None:
            # hold position while looking for the ball (running to a slot abandoned pass targets)
            options.append(('scan', None, (view.x, view.y), 1.))
        elif ball is None:
            options.append(('search', None, (round(bx, 3), round(by, 3)), 1.))
        elif carrier is None:           # loose or in flight
            t_lead = min(1., hypot(ball.x - view.x, ball.y - view.y) / 9.)
            if view.registry_ratings:
                t_lead *= PRISM.forecast_factor(registry_rating(view, 'anticipation'))
                course = belief.ball_course
                if course and view.prism_agent == 'in_air_ball_pursuit':
                    from .cognition_rb3 import flight_horizon
                    t_lead = min(t_lead, flight_horizon(course))
            px = _clamp(ball.x + ball.vx * t_lead, 1, 99)
            py = _clamp(ball.y + ball.vy * t_lead, 1, 99)
            mine = hypot(px - view.x, py - view.y)
            closer = sum(1 for t in mates if t.role == 'field'
                         and hypot(px - t.x, py - t.y) < mine)
            options.append(('position', None, position_from_belief(view, ball.x, False), 1.))
            airborne = (view.prism_agent == 'in_air_ball_pursuit' if view.registry_ratings else
                        belief.ball_course is not None and belief.ball_course.z > .45)
            pursuit = 'in_air_ball_pursuit' if airborne else 'live_ball_pursuit'
            if closer <= 1 or mine < 7. + owned_effect(view, pursuit, 6., agent=pursuit):
                options.append(('pursue', BALL, (round(px, 3), round(py, 3)),
                                round(4. - .05 * mine + owned_effect(view, pursuit, 1., agent=pursuit), 6)))
        elif carrier[1] == view.team:
            aim = position_from_belief(view, ball.x, False)
            lead = owned_effect(view, 'playmaking', 5., agent='playmaking') if view.registry_ratings else 0.
            if lead:
                aim = (_clamp(aim[0] + lead * sg, 1., 99.), aim[1])
            options.append(('support', carrier[0], aim, 1.))
        else:
            c = next(o for o in opps if o.entity == carrier[0])
            mine = hypot(c.x - view.x, c.y - view.y)
            closer = sum(1 for t in mates if t.role == 'field'
                         and hypot(c.x - t.x, c.y - t.y) < mine)
            mark_aim = position_from_belief(view, ball.x, True)
            if view.individual_ratings:
                mix = .4 + owned_effect(view, 'defending', .5, 'marking', 'defending')
                mark_aim = tuple(round((1 - mix) * a + mix * b, 3)
                                 for a, b in zip(mark_aim, (c.x - sg * 4., c.y)))
                mark_aim = tuple(_clamp(a, 1., 99.) for a in mark_aim)
            options.append(('mark', None, mark_aim, 1.))
            # KP (R-15): no opponent-initiated contact on a protected Keeper
            if (closer <= 1 and banned != 'press' and not keeper_protected(c, view)
                    and (not view.registry_ratings or view.prism_agent == 'defending')):
                # Base A (M1) defender decision: pursuit or the continuous lane option
                for k, t, a, v in _m1_options(view, fresh, carrier, 'defender',
                                              enable_lane_option=True, defender_judgment=.7 + owned_effect(view, 'defending', .35, 'judgment', 'defending')):
                    if k == 'move':
                        options.append(('press', t, (round(_clamp(a[0], 1, 99), 3), round(_clamp(a[1], 1, 99), 3)),
                                        round(v - 7., 6)))

    release = None
    if view.ownership_enabled and view.holds_ball:
        release = E.decide_release_preparation(E.ReleasePreparationView(
            view.observation_id, now, view.athlete, 'pass',
            view.own_restraint, view.tuck_fraction))
        if release.kind == 'retain':
            options = [o for o in options if o[0] not in ('pass', 'shoot', 'restart_pass')]
            if not options:
                options = [('retain', None, None, 0.)]
    bias = {'pass':view.policy.bias_pass,'shoot':view.policy.bias_shoot,
            'press':view.policy.bias_press,'pursue':view.policy.bias_pursue,
            'draw_release':view.policy.archer_eager}
    if not view.registry_ratings and 0 < sig.possession_ms < 3000 and view.holds_ball:
        bias['shoot'] += rating_effect(view, 'instinct', 2.)
    options = [(k,t,a,round(v+bias.get(k,0.),6)) for k,t,a,v in options
               if not(k=='pass' and view.policy.pass_min_clearance>0 and
                      _lane_clearance(view.x,view.y,a[0],a[1],opps)<view.policy.pass_min_clearance)]
    chosen = max(options, key=lambda o: (o[3], o[0], o[1] or ''))
    did = f'{view.observation_id}/decision'
    aim_vel = None
    if chosen[0] == 'draw_release':
        t = next(o for o in opps if o.entity == chosen[1])
        aim_vel = (round(t.vx, 3), round(t.vy, 3))
    intent = ActionIntent(did + '/intent', did, view.athlete, chosen[0], chosen[1], chosen[2],
                          aim_vel, (round(gaze[0], 3), round(gaze[1], 3)) if gaze else None, now,
                          view.pending_command_id if chosen[0] in ('continue_current', 'abort_draw') else None)
    if compact:
        return intent, {'options': options, 'believed_carrier': carrier}
    record = {'decision_id': did, 'owner': view.athlete, 'role': view.role,
              'observation_id': view.observation_id, 'belief_revision': belief.revision,
              'fresh_track_ids': [t.entity for t in fresh],
              'stale_track_ids': [t.entity for t in belief.tracks if t not in fresh],
              'believed_carrier': list(carrier) if carrier else None,
              'considered_feedback': list(latest) if latest else None,
              'pending_command_id': view.pending_command_id,
              'options': [list(o) for o in options], 'selected': list(chosen),
              'selection_rule': 'max(value, kind, target)',
              'release_preparation': asdict(release) if release else None}
    return intent, record


def view_to_json(view, belief):
    result = {'view': asdict(view), 'belief': asdict(belief)}
    if not result['view'].get('paired_fixes'):
        result['view'].pop('paired_fixes', None)
    if view.core_entropy is None:
        result['view'].pop('core_entropy')
        result['view'].pop('core_decision_ms')
        result['view'].pop('core_motion')
    if not view.individual_ratings:
        result['view'].pop('individual_ratings')
    if not view.registry_ratings:
        for key in ('registry_ratings', 'recognized_ball', 'prism_agent'):
            result['view'].pop(key)
        result['view'].pop('freezes_left', None)
    for d in result.values():
        for message in d['messages']:
            e = message['envelope']
            e['payload'] = e['payload'].hex()
            e['content_slot'] = e['content_slot'].value
    return result


def view_from_json(d):
    v, b = dict(d['view']), dict(d['belief'])
    tr = lambda xs: tuple(Track(**t) for t in xs)
    v['tracks'] = tr(v['tracks'])
    if 'individual_ratings' in v:
        v['individual_ratings'] = tuple(tuple(row) for row in v['individual_ratings'])
    if v.get('core_motion'):
        kind, technique, aim, started = v['core_motion']
        v['core_motion'] = (kind, technique, tuple(aim) if aim else None, started)
    if 'registry_ratings' in v:
        v['registry_ratings'] = tuple(tuple(row) for row in v['registry_ratings'])
    v['policy'] = PolicyParams.from_dict(v['policy']) if isinstance(v.get('policy'),dict) else PolicyParams()
    if isinstance(v.get('body'),dict):v['body']=E.AthleteBody(**v['body'])
    if v.get('restart') is not None:v['restart']=tuple(v['restart'])
    s = dict(v['signals'])
    s['restart_xy'] = tuple(s['restart_xy']) if s['restart_xy'] else None
    s['immune'] = tuple(s.get('immune', ()))
    s['pass_call'] = tuple(s['pass_call']) if s.get('pass_call') else None
    v['signals'] = Signals(**s)
    b['tracks'] = tr(b['tracks'])
    b['own_feedback'] = tuple(tuple(f) for f in b['own_feedback'])
    b['last_ball'] = tuple(b['last_ball']) if b['last_ball'] else None
    for d in (v, b):
        messages = []
        for raw in d.get('messages', ()):
            raw = dict(raw)
            e = dict(raw.pop('envelope'))
            e['payload'] = bytes.fromhex(e['payload'])
            e['content_slot'] = COM.ContentSlot(e['content_slot'])
            e['recipients'] = tuple(e['recipients'])
            messages.append(COM.Delivery(COM.MessageEnvelope(**e), **raw))
        d['messages'] = tuple(messages)
        if d.get('ball_course') is not None:
            d['ball_course'] = E.BallCourseBelief(**d['ball_course'])
    return AthleteView(**v), BeliefState(**b)


def decide(view, belief, *, learned_values=None):
    """All Native semantic commands. The view names its own decision set."""
    if view.cognition == 'native-rb/3':
        if view.core_entropy is not None:
            from . import prism_core
            return prism_core.decide(view, belief, learned_values=learned_values)
        from . import cognition_v3, cognition_rb3
        if view.registry_ratings:
            view = replace(view, prism_agent=PRISM.select_agent(view, belief, registry_rating))
        intent, record = cognition_rb3.adjust(view, belief, *cognition_v3.decide(view, belief))
        if view.registry_ratings:
            intent = cognition_rb3.committed_delivery(view, belief, intent)
            record = dict(record, prism_agent=view.prism_agent,
                          final_selection=[intent.kind, intent.target, intent.aim, intent.contact])
        return intent, record
    if view.cognition == 'native-v0/3':
        from . import cognition_v3
        return cognition_v3.decide(view, belief)
    return decide_v2(view, belief)


def decide_v2(view, belief):
    """All Native semantic commands, including PLACEHOLDER procedural choices."""
    if view.observation_id != belief.observation_id:raise ValueError('provenance mismatch')
    def choice(kind,aim=None,target=None,aux=None,contact=None):
        did=view.observation_id+'/decision'
        intent=ActionIntent(did+'/intent',did,view.athlete,kind,target,aim,None,None,
                            view.delivered_ms,speed=(min(80.,.5*view.max_throw_speed) if view.cognition=='native-rb/3' else min(27.,view.max_throw_speed)),height=1.6,
                            auxiliary=aux,contact=contact,record_id=view.restart[0] if view.restart else None,period=view.signals.period)
        return intent,{'decision_id':did,'observation_id':view.observation_id,
                       'belief_revision':belief.revision,'selected':[kind,target,aim,0.],
                       'options':[[kind,target,aim,0.]],'placeholder':True}
    if view.bench_role:
        return choice('substitute_claim')
    if view.hunt and view.restart is None and not view.hunt_cleared and not view.holds_ball:
        if view.role=='field' and view.contestant is None:return choice('hunt_claim')
        if view.contestant==view.athlete:return choice('pursue',(50.,50.),BALL)
        if view.role=='field':
            dx,dy=view.x-50,view.y-50;d=hypot(dx,dy)
            return choice('position',((50+dx/max(d,.01)*7,50+dy/max(d,.01)*7) if d<6 else (view.x,view.y)))
    if view.restart is not None and view.role!='archer':
        rid,kind,team,x,y,tx,ty,taker,snapper,tackler,created,ready=view.restart
        sg=view.attack_sign if team==view.team else -view.attack_sign
        if taker is None and (view.role=='field' or snapper==view.athlete) and team==view.team and (snapper is None or snapper==view.athlete):
            return choice('restart_claim')
        if taker==view.athlete:
            if hypot(view.x-tx,view.y-ty)>.6:return choice('restart_position',(tx,ty))
            if not ready:return choice('restart_wait')
            mates=[t for t in belief.tracks if t.team==view.team and t.role=='field' and view.delivered_ms-t.captured_ms<=2000]
            mate=min(mates,key=lambda t:(hypot(t.x-view.x,t.y-view.y),t.entity),default=None)
            # PLACEHOLDER: select a believed teammate; otherwise throw to legal space.
            aim=(mate.x,mate.y) if mate else (max(1.,min(99.,x+view.attack_sign*5)),max(1.,min(99.,y+3)))
            return choice('restart_pass',aim,mate.entity if mate else None)
        px,py=view.x,view.y
        if kind=='snap40':
            px=min(px,40.) if view.own_goal_x==0 else max(px,60.)
        elif kind=='toss':
            dx,dy=px-x,py-y;d=hypot(dx,dy)
            if team!=view.team and d<3.5:px,py=x+(dx/max(d,.01) if d else 1)*4,y+(dy/max(d,.01) if d else 0)*4
        elif view.athlete==tackler:
            px,py=x+sg*5,y
        else:
            if view.team==team and sg*(px-x)>-.5:px=x-sg*.8
            if view.team!=team and sg*(px-x)<.5:px=x+sg*.8
            # Leave physical room for the claimant; this is clearance, not formation.
            if hypot(px-tx,py-ty)<2.:py=ty+(2. if view.athlete<taker else -2.) if taker else ty+2.
        return choice('restart_position',(max(.01,min(99.99,px)),max(.01,min(99.99,py))))
    # PLACEHOLDER rule compliance: leave before the 5 s residence deadline.
    # This projects a legal exit from own sensed position, not a tactical anchor.
    # RB-3.11 (native-rb/3): the fixed 3 s / 4 s timers are replaced by time-to-arc exits and defender
    # marking in cognition_rb3.zone_behavior; every other profile keeps the 3 s placeholder.
    if view.cognition!='native-rb/3' and view.role=='field' and view.zone_elapsed_ms>=3000:
        for gx in (view.own_goal_x,100-view.own_goal_x):
            dx,dy=view.x-gx,view.y-50;d=hypot(dx,dy)
            if d<view.zone_radius:
                ux,uy=((dx/d,dy/d) if d else (view.attack_sign,0.))
                return choice('position',(max(.6,min(99.4,gx+ux*(view.zone_radius+1.))),
                                          max(.6,min(99.4,50+uy*(view.zone_radius+1.)))))
    if view.role=='archer' and view.pending_command_id and view.pending_release_ms is not None and view.delivered_ms>=view.pending_release_ms:
        target=next((t for t in belief.tracks if t.entity==view.pending_target),None)
        if (target is None or view.signals.phase!='live' or getattr(view,'snap_hold',False)
                or not archer_target_legal(target,view,view.delivered_ms)
                or (view.registry_ratings and getattr(view,'freezes_left',None) == 0)):
            intent,rec=choice('abort_draw',target=view.pending_target)
        else:
            intent,rec=choice('release_arrow',(target.x,target.y),view.pending_target)
            intent=replace(intent,aim_vel=(target.vx,target.vy))
        return replace(intent,related_command_id=view.pending_command_id),rec
    if view.role=='keeper' and not view.holds_ball:
        course=belief.ball_course
        if view.registry_ratings and course:
            trust = PRISM.forecast_factor(registry_rating(view, 'anticipation'))
            course = replace(course, vy=course.vy * trust, vz=course.vz * trust)
        position=None
        if course and course.fresh(view.delivered_ms):
            d=hypot(course.x-view.own_goal_x,course.y-50);depth=max(1.,min(4.,d*.25))
            lateral = (course.y-50)*depth/max(d,.01)
            position=(view.own_goal_x+view.attack_sign*depth,50+lateral*(1+owned_effect(view, 'goalkeeping', .5, agent='goalkeeping')))
        kv=E.KeeperView(view.observation_id,view.delivered_ms,view.body,view.own_goal_x,
                        goal_radius=view.goal_radius,position_belief=position)
        if getattr(view,'ball_material',None) is not None:   # RB-3.21: the Keeper forecasts the ball the material produces
            from .cognition_rb3 import keeper_decide
            ki=keeper_decide(kv,course,view.ball_material)
        else:
            ki=E.decide_keeper(kv,course,gravity=9.81,drag=.015,restitution=.7745966692)
        return choice('keeper_control',aux=ki)
    intent,record=_base_decide(view,belief)
    # PLACEHOLDER: expose release speed and height as athlete-owned inputs.
    # The semantic pass already leads the believed receiver in the B1 policy.
    intent=replace(intent,speed=(min(80.,.5*view.max_throw_speed) if view.cognition=='native-rb/3' else min(27.,view.max_throw_speed)),height=1.6,
                   contact='wrap' if intent.kind=='press' else None,period=view.signals.period)
    if view.cognition=='native-rb/3' and intent.kind=='shoot' and intent.aim:
        from . import cognition_rb3 as R3             # RB-3.15 S-1: the chosen aim height (a pure re-derivation of the plan)
        fresh_ = tuple(t for t in belief.tracks if 0 <= view.delivered_ms - t.captured_ms <= belief.max_track_age_ms)
        plan_ = R3.shot_plan(view, fresh_)
        if plan_ is not None and plan_['aim'] == tuple(intent.aim):
            intent = replace(intent, height=plan_['z'])
    if view.cognition=='native-rb/3' and intent.kind=='pass' and intent.aim:
        # RB-3.9b B-1: release speed chosen by the (led) pass distance; same speed as used in the lead.
        from .throw_speed import release_speed
        intent=replace(intent,speed=release_speed(hypot(intent.aim[0]-view.x,intent.aim[1]-view.y),view.max_throw_speed))
    if intent.kind=='pass' and intent.aim and not in_own_zone(view.team,view.x,view.y,view) and in_own_zone(view.team,*intent.aim,view):
        return choice('retain')
    if view.holds_ball and view.role=='field' and not view.dribble_used and view.pending_command_id is None:
        mates=[t for t in belief.tracks if t.team==view.team and view.delivered_ms-t.captured_ms<2000]
        if not mates:return choice('dribble',(max(1.,min(99.,view.x+view.attack_sign*5)),view.y))
    return intent,record
