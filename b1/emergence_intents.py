"""Pure individual-control contracts for Emergence-1 ownership seams.

Rules publish decision records and sensors publish beliefs. Only an athlete
policy creates a semantic intent; Motor Control may accept or reject it but
does not silently substitute another choice. This module imports no simulator.
"""
from dataclasses import dataclass
import math


@dataclass(frozen=True)
class BallCourseBelief:
    revision: str
    captured_ms: int
    delivered_ms: int
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    radius: float = .11
    max_age_ms: int = 600

    def fresh(self, now_ms):
        return (self.captured_ms <= self.delivered_ms <= now_ms and
                now_ms-self.captured_ms <= self.max_age_ms)


@dataclass(frozen=True)
class AthleteBody:
    athlete: str
    team: str
    x: float
    y: float
    z: float
    vx: float
    vy: float
    vz: float
    height: float
    reach: float
    acceleration: float
    braking: float
    maximum_speed: float
    jump_height: float


@dataclass(frozen=True)
class KeeperView:
    observation_id: str
    now_ms: int
    body: AthleteBody
    own_goal_x: float
    goal_y: float = 50.
    goal_radius: float = 7.
    position_belief: tuple[float, float] | None = None


@dataclass(frozen=True)
class KeeperIntent:
    intent_id: str
    athlete: str
    kind: str
    decided_ms: int
    belief_revision: str | None
    target: tuple[float, float] | None = None
    intercept_window_ms: tuple[int, int] | None = None
    course: tuple[tuple[float, float, float, float], ...] = ()
    reason: str | None = None


@dataclass(frozen=True)
class KeeperMotorCommand:
    command_id: str
    intent_id: str
    athlete: str
    kind: str
    target: tuple[float, float] | None = None
    until_ms: int | None = None
    impulse: tuple[float, float, float] | None = None
    lean: float = 0.
    direction: tuple[float, float] = (0., 0.)
    land_ms: float | None = None
    status: str = 'accepted'
    reason: str | None = None


@dataclass(frozen=True)
class RestartDecisionRecord:
    record_id: str
    kind: str
    team: str
    mark: tuple[float, float]
    taker_spot: tuple[float, float]
    clearance_m: float
    created_ms: int
    claim_open_ms: int
    fallback_ms: int
    preferred_taker: str | None = None
    mandatory_spots: tuple[tuple[str, tuple[float, float]], ...] = ()


@dataclass(frozen=True)
class RestartAthleteView:
    observation_id: str
    now_ms: int
    athlete: str
    team: str
    x: float
    y: float
    eligible: bool
    posture: str = 'upright'
    role: str = 'field'
    zone_exit: tuple[float, float] | None = None


@dataclass(frozen=True)
class RestartIntent:
    intent_id: str
    athlete: str
    kind: str
    decided_ms: int
    record_id: str
    target: tuple[float, float] | None = None
    claim_cost: float | None = None
    reason: str | None = None


@dataclass(frozen=True)
class ArcherView:
    observation_id: str
    now_ms: int
    body: AthleteBody
    lane_min_x: float
    lane_max_x: float
    lane_y: float
    loaded: int
    allocation_remaining: int
    reload_pending: bool


@dataclass(frozen=True)
class ArcherIntent:
    intent_id: str
    athlete: str
    kind: str
    decided_ms: int
    belief_revision: str | None
    target: tuple[float, float]
    reload: bool = False
    reason: str | None = None


@dataclass(frozen=True)
class ReleasePreparationView:
    observation_id: str
    now_ms: int
    athlete: str
    action_kind: str
    own_restraint: float
    tuck_after_delay_fraction: float


@dataclass(frozen=True)
class ReleasePreparationIntent:
    intent_id: str
    athlete: str
    kind: str
    action_kind: str
    decided_ms: int
    reason: str


def _clamp(value, lo, hi):
    return max(lo, min(hi, value))


def forecast_course(belief, gravity, drag, restitution=.55,
                    horizon_s=3., step_s=.01):
    """Forecast only from a delivered belief, never an authoritative Ball."""
    x, y, z = belief.x, belief.y, belief.z
    vx, vy, vz = belief.vx, belief.vy, belief.vz
    decay = math.exp(-drag*step_s)
    path = [(0., x, y, z)]
    t = 0.
    while t < horizon_s:
        x += vx*step_s
        y += vy*step_s
        z += vz*step_s-.5*gravity*step_s*step_s
        vx *= decay
        vy *= decay
        vz = (vz-gravity*step_s)*decay
        if z <= belief.radius:
            z = belief.radius
            if abs(vz) > 2.:
                vz = -vz*restitution
                vx *= .76
                vy *= .76
            else:
                vz = 0.
                vx *= max(0., 1.-3.*step_s)
                vy *= max(0., 1.-3.*step_s)
        t += step_s
        path.append((t, x, y, z))
        if not (-2. <= x <= 102. and -2. <= y <= 102.):
            break
    return tuple(path)


def _goal_crossing(view, path):
    gx = view.own_goal_x
    inward = 50.-gx
    for before, after in zip(path, path[1:]):
        t0, x0, y0, z0 = before
        t1, x1, y1, z1 = after
        if ((x0-gx)*inward >= 0. and (x1-gx)*inward <= 0. and x1 != x0):
            f = (gx-x0)/(x1-x0)
            t = t0+f*(t1-t0)
            y = y0+f*(y1-y0)
            z = z0+f*(z1-z0)
            return ((t, y, z) if math.hypot(y-view.goal_y, z) <=
                    view.goal_radius else None)
    return None


def decide_keeper(view, belief, *, gravity=9.81, drag=.035,
                  restitution=.55):
    """Choose a Keeper action from own body state and a delivered belief."""
    iid = f'{view.observation_id}/keeper-intent'
    if belief is None:
        return KeeperIntent(iid, view.body.athlete, 'hold', view.now_ms, None,
                            target=(view.body.x, view.body.y),
                            reason='no_delivered_ball_belief')
    if not belief.fresh(view.now_ms):
        return KeeperIntent(iid, view.body.athlete, 'hold', view.now_ms,
                            belief.revision, target=(view.body.x, view.body.y),
                            reason='stale_ball_belief')
    path = forecast_course(belief, gravity, drag, restitution)
    cross = _goal_crossing(view, path)
    if cross is None:
        target = view.position_belief or (view.body.x, view.body.y)
        return KeeperIntent(iid, view.body.athlete, 'position', view.now_ms,
                            belief.revision, target=target,
                            reason='no_believed_threat')
    usable = tuple(p for p in path if p[0] <= cross[0]+1e-12)
    return KeeperIntent(
        iid, view.body.athlete, 'save', view.now_ms, belief.revision,
        intercept_window_ms=(view.now_ms,
                             view.now_ms+int(math.ceil(cross[0]*1000))),
        course=usable, reason='believed_goal_crossing')


def plan_keeper_motor(intent, body, *, now_ms, gravity=9.81,
                      pushoff_fraction=.55, extension_fraction=.72,
                      launch_min_s=.12, dive_time_s=.32,
                      attempt_margin_m=.35, reach_factor=1.1,
                      dive_hand_fraction=.25, match_lean=False):
    """Admit a Keeper intent using only own-body capabilities."""
    cid = intent.intent_id+'/motor'
    if intent.kind in ('hold', 'position'):
        return KeeperMotorCommand(cid, intent.intent_id, body.athlete,
                                  'hold' if intent.kind == 'hold' else 'move',
                                  intent.target, now_ms+100)
    if intent.kind != 'save' or not intent.course:
        return KeeperMotorCommand(cid, intent.intent_id, body.athlete,
                                  'rejected', status='rejected',
                                  reason='unsupported_or_empty_intent')
    reach = body.reach*reach_factor
    for t, x, y, z in intent.course[1:]:
        hx, hy = body.x+body.vx*t, body.y+body.vy*t
        horizontal = math.hypot(x-hx, y-hy)
        vertical = abs(z-(body.z+.62*body.height))
        room = .5*body.acceleration*t*t
        miss = math.hypot(max(0., horizontal-room), vertical)
        if miss <= .95*reach:
            return KeeperMotorCommand(
                cid, intent.intent_id, body.athlete, 'step',
                (_clamp(x, -1., 101.), _clamp(y, -1., 101.)),
                now_ms+int(math.ceil(t*1000)))
    max_push = math.sqrt(max(0., 2.*body.acceleration*
                             pushoff_fraction*body.height))
    max_vz = math.sqrt(max(0., 2.*gravity*body.jump_height))
    best = None
    for t, x, y, z in intent.course[1:]:
        if t < launch_min_s:
            continue
        lead = max(0., t-dive_time_s)
        tau = t-lead
        px, py = body.x+body.vx*t, body.y+body.vy*t
        dx, dy = x-px, y-py
        distance = math.hypot(dx, dy)
        ux, uy = ((dx/distance, dy/distance) if distance > 1e-9
                  else (0., 0.))
        run = .5*body.acceleration*lead*lead+body.acceleration*lead*tau
        extension = extension_fraction*body.height
        if match_lean:
            # Until full lean, execution extends the hand in proportion to
            # the horizontal impulse. Solve with that same hand position.
            remaining = max(0., distance-run)
            linear_push = remaining/(tau+extension/max(max_push, 1e-9))
            push = linear_push if linear_push <= max_push else max(0., remaining-extension)/tau
            lean = min(1., push/max(max_push, 1e-9))
            hand_z = body.z+(.62-(.62-dive_hand_fraction)*lean)*body.height
        else:
            remaining = max(0., distance-run-extension)
            push = remaining/max(tau, 1e-9)
            hand_z = body.z+dive_hand_fraction*body.height
        need_vz = max(0., (z-hand_z+.5*gravity*tau*tau)/max(tau, 1e-9))
        budget = ((push/max(max_push, 1e-9))**2+
                  (need_vz/max(max_vz, 1e-9))**2)
        residual = max(0., math.sqrt(budget)-1.)*max(reach, .01)
        candidate = (residual, lead, t, ux, uy,
                     min(push, max_push), min(need_vz, max_vz))
        if best is None or candidate < best:
            best = candidate
        if budget <= 1.:
            best = candidate
            break
    if best is None or best[0] > attempt_margin_m:
        return KeeperMotorCommand(cid, intent.intent_id, body.athlete,
                                  'rejected', status='rejected_infeasible',
                                  reason='own_body_cannot_reach_believed_course')
    _, lead, meet, ux, uy, push, vz = best
    if match_lean:
        budget = math.hypot(push/max(max_push, 1e-9), vz/max(max_vz, 1e-9))
        if budget > 1.:
            push, vz = push/budget, vz/budget
    if lead > .005:
        return KeeperMotorCommand(
            cid, intent.intent_id, body.athlete, 'approach',
            (_clamp(body.x+20.*ux, -1., 101.),
             _clamp(body.y+20.*uy, -1., 101.)),
            now_ms+int(math.ceil(lead*1000)))
    lean = min(1., push/max(max_push, 1e-9))
    land = now_ms+(1000.*2.*vz/gravity if vz > 0. else meet*1000.)
    return KeeperMotorCommand(
        cid, intent.intent_id, body.athlete, 'launch',
        impulse=(push*ux, push*uy, vz), lean=lean,
        direction=(ux, uy), land_ms=land)


def decide_restart_claim(view, record):
    iid = f'{view.observation_id}/restart-claim'
    if (not view.eligible or view.team != record.team or
            view.role == 'archer' or view.posture != 'upright'):
        return RestartIntent(iid, view.athlete, 'decline', view.now_ms,
                             record.record_id, reason='not_eligible')
    if view.now_ms < record.claim_open_ms:
        return RestartIntent(iid, view.athlete, 'decline', view.now_ms,
                             record.record_id, reason='claim_window_closed')
    if (record.preferred_taker is not None and
            view.athlete != record.preferred_taker and
            view.now_ms < record.fallback_ms):
        return RestartIntent(iid, view.athlete, 'decline', view.now_ms,
                             record.record_id, reason='preferred_taker_window')
    cost = math.hypot(view.x-record.taker_spot[0],
                      view.y-record.taker_spot[1])
    if cost > .75:
        return RestartIntent(iid, view.athlete, 'approach_restart',
                             view.now_ms, record.record_id,
                             record.taker_spot, cost,
                             'move_to_claim_radius')
    if view.athlete == record.preferred_taker:
        cost -= 1000.
    return RestartIntent(iid, view.athlete, 'claim_taker', view.now_ms,
                         record.record_id, record.taker_spot, cost,
                         'preferred' if cost < 0. else 'fallback_or_open_claim')


def admit_restart_claims(claims):
    valid = [c for c in claims if c.kind == 'claim_taker' and
             c.claim_cost is not None]
    # Motor ingress does not rank athletes by hidden/full-state suitability.
    # Every claimant is already physically inside the claim radius; a true
    # simultaneous collision is resolved by canonical command ordering.
    return min(valid, key=lambda c:(c.decided_ms, c.intent_id)) if valid else None


def decide_restart_position(view, record, admitted_taker):
    iid = f'{view.observation_id}/restart-position'
    mandatory = dict(record.mandatory_spots)
    if view.athlete == admitted_taker:
        target, reason = record.taker_spot, 'admitted_taker_spot'
    elif view.athlete in mandatory:
        target, reason = mandatory[view.athlete], 'rules_record_spot'
    elif admitted_taker is None:
        claim = decide_restart_claim(view, record)
        if claim.kind == 'approach_restart':
            target, reason = record.taker_spot, 'approach_taker_claim'
        else:
            target = (_clamp(view.x, 1., 99.), _clamp(view.y, 1., 99.))
            reason = 'hold_until_claim_window'
    elif view.zone_exit is not None:
        target, reason = view.zone_exit, 'rules_record_zone_exit'
    elif view.team != record.team:
        distance = math.hypot(view.x-record.mark[0], view.y-record.mark[1])
        keep = record.clearance_m+.5
        if distance < keep:
            ux, uy = (((view.x-record.mark[0])/distance,
                       (view.y-record.mark[1])/distance)
                      if distance > 1e-9 else (1., 0.))
            target = (_clamp(record.mark[0]+(keep+1.5)*ux, 1., 99.),
                      _clamp(record.mark[1]+(keep+1.5)*uy, 1., 99.))
            reason = 'clear_restart_mark'
        else:
            target = (_clamp(view.x, 1., 99.), _clamp(view.y, 1., 99.))
            reason = 'hold_legal_position'
    else:
        target = (_clamp(view.x, 1., 99.), _clamp(view.y, 1., 99.))
        reason = 'hold_legal_position'
    return RestartIntent(iid, view.athlete, 'move', view.now_ms,
                         record.record_id, target, reason=reason)


def decide_archer_movement(view, ball_belief):
    iid = f'{view.observation_id}/archer-intent'
    reload_now = (view.loaded == 0 and view.allocation_remaining > 0 and
                  not view.reload_pending)
    if ball_belief is None or not ball_belief.fresh(view.now_ms):
        revision = None if ball_belief is None else ball_belief.revision
        reason = ('no_delivered_ball_belief' if ball_belief is None
                  else 'stale_ball_belief')
        return ArcherIntent(iid, view.body.athlete, 'hold', view.now_ms,
                            revision, (view.body.x, view.body.y), reload_now,
                            reason)
    target = (_clamp(ball_belief.x, view.lane_min_x, view.lane_max_x),
              view.lane_y)
    return ArcherIntent(iid, view.body.athlete, 'move', view.now_ms,
                        ball_belief.revision, target, reload_now,
                        'track_believed_ball')


def decide_release_preparation(view):
    """Athlete choice replacing the legacy engine-side c3_withhold gate."""
    iid = f'{view.observation_id}/release-preparation'
    if view.action_kind == 'kick' or view.tuck_after_delay_fraction <= 0.:
        return ReleasePreparationIntent(iid, view.athlete, 'prepare_release',
                                        view.action_kind, view.now_ms,
                                        'unaffected_action')
    limit = (view.tuck_after_delay_fraction/
             (1.+view.tuck_after_delay_fraction))
    if view.own_restraint >= limit:
        return ReleasePreparationIntent(
            iid, view.athlete, 'retain', view.action_kind, view.now_ms,
            'athlete_declined_under_own_restraint')
    return ReleasePreparationIntent(iid, view.athlete, 'prepare_release',
                                    view.action_kind, view.now_ms,
                                    'athlete_accepts_release_risk')
