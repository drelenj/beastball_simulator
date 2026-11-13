"""SPRINT-30 pure per-athlete cognition. No simulation imports.

PRIMITIVE: every scoring constant below is a provisional rule-based policy
parameter (see b1/registry.py and SPRINT30_LIMITATIONS.md). Inputs are only an
immutable AthleteView and the athlete's own BeliefState.
"""
from dataclasses import dataclass, asdict, replace
from math import hypot

from . import core as M1          # Base A (governed M1) pure decision code

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
    judgment: float = 0.7                # SELF-1: own abilities known exactly
    zone_radius: float = 20.0            # G: inside = distance < R


@dataclass(frozen=True)
class BeliefState:
    revision: str
    observation_id: str
    tracks: tuple
    own_feedback: tuple = ()
    max_track_age_ms: int = 2000
    last_ball: tuple | None = None      # (x, y, captured_ms) own memory


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


def home_position(view, ref_x, defending):
    """PRIMITIVE: slot-grid shape (spec deviation BA-7: externally assigned)."""
    sg, k = view.attack_sign, view.slot
    row = (0, -1, -1, -1, 0, 0, 0, 1, 1, 1)[k % 10]
    lane = (50, 22, 50, 78, 14, 40, 86, 28, 60, 72)[k % 10]
    if k % 10 == 0:
        row = 1
    depth = (-16, 2, 14)[row + 1] - (12 if defending else 0)
    if defending:
        lane = 50 + (lane - 50) * .6
    return (_clamp(ref_x + sg * depth, 6, 94), float(lane))


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
    """Ruleset 1.0.2 (R-17) legality judged from the Archer's own belief and public signals.
    PRIMITIVE: belief margins (12-62 m, track age <= 700 ms) are hand-set."""
    d = hypot(t.x - view.x, t.y - view.y)
    return (t.role != 'archer' and t.entity not in view.signals.immune
            and not (t.role == 'keeper' and in_own_zone(t.team, t.x, t.y, view))
            and 12. <= d <= 62. and now - t.captured_ms <= 700)


def decide(view: AthleteView, belief: BeliefState):
    if belief.observation_id != view.observation_id:
        raise ValueError('belief/view provenance mismatch')
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
        if best is not None and hypot(best.x - ball.x, best.y - ball.y) < 1.8:
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
    elif view.role == 'archer':
        options.append(('archer_hold', None, None, 0.))
        # Ruleset 1.0.2 (D1 record R-17): any eligible player may be frozen; a Keeper inside
        # his own zone is protected; R-01: no target before the first passive possession.
        ready = (view.arrows_loaded or 0) > 0 and (
            view.last_release_ms is None or now - view.last_release_ms >= 2600)
        if ready and sig.phase == 'live' and sig.passive_team is not None and banned != 'draw_release':
            for t in sorted(opps, key=lambda t: t.entity):
                if not archer_target_legal(t, view, now):
                    continue
                d = hypot(t.x - view.x, t.y - view.y)
                is_carrier = bool(carrier and carrier[0] == t.entity)
                # PRIMITIVE: carrier preferred; otherwise the opponent nearest the ball
                near_ball = hypot(t.x - bx, t.y - by) if bx is not None else 40.
                value = (3. if is_carrier else 1.6 - .04 * near_ball) - .02 * d
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
                options.append(('home', None, home_position(
                    view, ref, sig.restart_team not in (None, view.team)), 1.))
    elif view.holds_ball:
        options.append(('retain', None, None, 0.))
        if not failed or True:
            near = min((hypot(o.x - view.x, o.y - view.y) for o in opps), default=30.)
            dg = hypot(goal[0] - view.x, goal[1] - view.y)
            if view.role != 'keeper':
                if dg <= 32 and banned != 'shoot':
                    keeper = next((o for o in opps if o.role == 'keeper'), None)
                    side = -1. if keeper is not None and keeper.y > 50 else 1.
                    value = 5.5 - .2 * dg + (8. if near < 5.8 else 0.) + (
                        5. if 0 < sig.possession_ms < 5000 else 0.)
                    options.append(('shoot', None, (goal[0], 50. + side * 3.6), round(value, 6)))
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
            for k, t, a, v in _m1_options(view, fresh, carrier, 'carrier',
                                          carry_target=carry_opt[2] if carry_opt else None):
                if k == 'pass' and banned == 'pass':
                    continue
                if k == 'pass':
                    # PRIMITIVE: belief-based lead. The semantic aim is the receiver's believed
                    # position advanced by its believed velocity over the nominal flight time
                    # (cognition's choice; Motor never leads the receiver).
                    rt = next(x for x in fresh if x.entity == t)
                    tf = min(1.2, hypot(a[0] - view.x, a[1] - view.y) / 27.)
                    a = (_clamp(a[0] + rt.vx * tf, 2, 98), _clamp(a[1] + rt.vy * tf, 2, 98))
                if k in ('carry', 'pass'):
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
                aim = (round(_clamp(ball.x + ball.vx * t, 1, 99), 3), round(_clamp(ball.y + ball.vy * t, 1, 99), 3))
            options.append(('receive', sig.pass_call[0], aim, 5.))
        if bx is None:
            # hold position while looking for the ball (running to a slot abandoned pass targets)
            options.append(('scan', None, (view.x, view.y), 1.))
        elif ball is None:
            options.append(('search', None, (round(bx, 3), round(by, 3)), 1.))
        elif carrier is None:           # loose or in flight
            t_lead = min(1., hypot(ball.x - view.x, ball.y - view.y) / 9.)
            px = _clamp(ball.x + ball.vx * t_lead, 1, 99)
            py = _clamp(ball.y + ball.vy * t_lead, 1, 99)
            mine = hypot(px - view.x, py - view.y)
            closer = sum(1 for t in mates if t.role == 'field'
                         and hypot(px - t.x, py - t.y) < mine)
            options.append(('home', None, home_position(view, ball.x, False), 1.))
            if closer <= 1 or mine < 7.:
                options.append(('pursue', BALL, (round(px, 3), round(py, 3)),
                                round(4. - .05 * mine, 6)))
        elif carrier[1] == view.team:
            options.append(('support', carrier[0], home_position(view, ball.x, False), 1.))
        else:
            c = next(o for o in opps if o.entity == carrier[0])
            mine = hypot(c.x - view.x, c.y - view.y)
            closer = sum(1 for t in mates if t.role == 'field'
                         and hypot(c.x - t.x, c.y - t.y) < mine)
            options.append(('mark', None, home_position(view, ball.x, True), 1.))
            # KP (R-15): no opponent-initiated contact on a protected Keeper
            if closer <= 1 and banned != 'press' and not keeper_protected(c, view):
                # Base A (M1) defender decision: pursuit or the continuous lane option
                for k, t, a, v in _m1_options(view, fresh, carrier, 'defender',
                                              enable_lane_option=True, defender_judgment=view.judgment):
                    if k == 'move':
                        options.append(('press', t, (round(_clamp(a[0], 1, 99), 3), round(_clamp(a[1], 1, 99), 3)),
                                        round(v - 7., 6)))

    chosen = max(options, key=lambda o: (o[3], o[0], o[1] or ''))
    did = f'{view.observation_id}/decision'
    aim_vel = None
    if chosen[0] == 'draw_release':
        t = next(o for o in opps if o.entity == chosen[1])
        aim_vel = (round(t.vx, 3), round(t.vy, 3))
    intent = ActionIntent(did + '/intent', did, view.athlete, chosen[0], chosen[1], chosen[2],
                          aim_vel, (round(gaze[0], 3), round(gaze[1], 3)) if gaze else None, now,
                          view.pending_command_id if chosen[0] in ('continue_current', 'abort_draw') else None)
    record = {'decision_id': did, 'owner': view.athlete, 'role': view.role,
              'observation_id': view.observation_id, 'belief_revision': belief.revision,
              'fresh_track_ids': [t.entity for t in fresh],
              'stale_track_ids': [t.entity for t in belief.tracks if t not in fresh],
              'believed_carrier': list(carrier) if carrier else None,
              'considered_feedback': list(latest) if latest else None,
              'pending_command_id': view.pending_command_id,
              'options': [list(o) for o in options], 'selected': list(chosen),
              'selection_rule': 'max(value, kind, target)'}
    return intent, record


def view_to_json(view, belief):
    return {'view': asdict(view), 'belief': asdict(belief)}


def view_from_json(d):
    v, b = dict(d['view']), dict(d['belief'])
    tr = lambda xs: tuple(Track(**t) for t in xs)
    v['tracks'] = tr(v['tracks'])
    s = dict(v['signals'])
    s['restart_xy'] = tuple(s['restart_xy']) if s['restart_xy'] else None
    s['immune'] = tuple(s.get('immune', ()))
    s['pass_call'] = tuple(s['pass_call']) if s.get('pass_call') else None
    v['signals'] = Signals(**s)
    b['tracks'] = tr(b['tracks'])
    b['own_feedback'] = tuple(tuple(f) for f in b['own_feedback'])
    b['last_ball'] = tuple(b['last_ball']) if b['last_ball'] else None
    return AthleteView(**v), BeliefState(**b)
