"""Pure value contracts and athlete cognition. No simulation imports."""
from dataclasses import dataclass
from math import hypot


@dataclass(frozen=True)
class Contact:
    entity: str
    team: str
    x: float
    y: float
    captured_ms: int
    vx: float = 0.0
    vy: float = 0.0
    has_ball: bool = False


@dataclass(frozen=True)
class DecisionConfig:
    role: str = 'carrier'
    carry_target: tuple[float, float] | None = None
    pursuit_lookahead_s: float = 1.2


@dataclass(frozen=True)
class AthleteView:
    observation_id: str
    athlete: str
    team: str
    delivered_ms: int
    x: float
    y: float
    holds_ball: bool
    contacts: tuple[Contact, ...]
    pending_command_id: str | None = None
    pending_release_ms: int | None = None


@dataclass(frozen=True)
class BeliefState:
    revision: str
    observation_id: str
    contacts: tuple[Contact, ...]
    own_feedback: tuple[tuple[str, str, int], ...] = ()
    max_contact_age_ms: int = 2000


@dataclass(frozen=True)
class ActionIntent:
    intent_id: str
    decision_id: str
    athlete: str
    kind: str
    target: str | None
    aim: tuple[float, float] | None
    decided_ms: int
    related_command_id: str | None = None


@dataclass(frozen=True)
class MotorCommand:
    command_id: str
    intent: ActionIntent
    start_ms: int
    release_ms: int
    desired_velocity: tuple[float, float, float] | None


@dataclass(frozen=True)
class PhysicalOutcome:
    outcome_id: str
    command_id: str | None
    status: str
    resolved_ms: int
    entity_id: str | None = None


def receive_outcome(outcome: PhysicalOutcome):
    """Restricted own-action feedback; no opponent/body state escapes PHY."""
    return (outcome.outcome_id, outcome.status, outcome.resolved_ms)


def decide(view: AthleteView, belief: BeliefState,
           config: DecisionConfig = DecisionConfig()):
    """B1 PRISM option layer: individual belief-only lane evaluation.

    Values are provisional policy parameters, not physical/rating changes.
    This replaces the legacy tactical evaluator; sensing/beliefs use PRISM.
    """
    if belief.observation_id != view.observation_id:
        raise ValueError('belief/view provenance mismatch')
    contacts = tuple(c for c in belief.contacts
                     if 0 <= view.delivered_ms-c.captured_ms <= belief.max_contact_age_ms)
    failed_feedback = next((f for f in belief.own_feedback
                            if f[1] == 'interrupted' or f[1].startswith('rejected_')),
                           None)
    latest_feedback = belief.own_feedback[-1] if belief.own_feedback else None
    if config.role == 'defender':
        ball = next((c for c in contacts if c.entity == 'BALL'), None)
        opponents = [c for c in contacts if c.team not in (view.team, 'neutral')]
        carriers = [c for c in opponents if c.has_ball]
        if ball is not None and opponents:
            nearest = min(opponents, key=lambda c: hypot(c.x-ball.x, c.y-ball.y))
            # The association is made from the athlete's two beliefs, never
            # from authoritative ownership.  Once separated, pursue the ball.
            target = [nearest] if hypot(nearest.x-ball.x, nearest.y-ball.y) <= 2.5 else [ball]
        else:
            target = carriers or ([ball] if ball is not None else [])
        options=[('no_action',None,None,0.0)]
        for c in target:
            speed=hypot(c.vx,c.vy)
            if c.entity == 'BALL':
                lead_t=.25
                aim=(c.x+lead_t*c.vx,c.y+lead_t*c.vy)
            elif speed >= .1:
                # Lead the observed heading by a bounded distance.  This is
                # an interception from belief, not access to true state.
                lead=5.
                aim=(c.x+lead*c.vx/speed,c.y+lead*c.vy/speed)
            else:
                aim=(c.x,c.y)
            options.append(('move',c.entity,aim,
                            10.0-hypot(aim[0]-view.x,aim[1]-view.y)*.01))
        chosen=max(options,key=lambda o:(o[3],o[0],o[1] or ''))
        did=f'{view.observation_id}/decision'
        intent=ActionIntent(did+'/intent',did,view.athlete,*chosen[:3],view.delivered_ms)
        return intent,{'decision_id':did,'owner':view.athlete,
                       'observation_id':view.observation_id,'belief_revision':belief.revision,
                       'fresh_contact_ids':[c.entity for c in contacts],
                       'stale_contact_ids':[c.entity for c in belief.contacts if c not in contacts],
                       'considered_feedback':list(belief.own_feedback),
                       'pending_command_id':view.pending_command_id,
                       'options':options,'selected':chosen}
    if view.pending_command_id is not None:
        options = [('continue_current', None, None, 0.0)]
    elif failed_feedback:
        # A failed action produces one explicit reassessment cycle. The caller
        # supplies only feedback not yet considered by a prior decision.
        options = [('no_action', None, None, 0.0)]
    else:
        base=('carry',None,config.carry_target,2.0) if (
            view.holds_ball and config.carry_target is not None) else (
            'retain' if view.holds_ball else 'no_action',None,None,0.0)
        options = [base]
    if view.holds_ball and view.pending_command_id is None and not failed_feedback:
        opponents = [c for c in contacts if c.team not in (view.team, 'neutral')]
        for c in sorted(contacts, key=lambda c: c.entity):
            if c.team != view.team:
                continue
            dx, dy = c.x-view.x, c.y-view.y
            distance = hypot(dx, dy)
            if not 3 <= distance <= 30:
                continue
            clearance = 10.0
            for d in opponents:
                f = max(0., min(1., ((d.x-view.x)*dx+(d.y-view.y)*dy)/(distance**2)))
                clearance = min(clearance, hypot(d.x-view.x-f*dx, d.y-view.y-f*dy))
            value = clearance - 3.0 - .03*distance
            options.append(('pass', c.entity, (c.x, c.y), value))
    chosen = max(options, key=lambda o: (o[3], o[0], o[1] or ''))
    did = f'{view.observation_id}/decision'
    intent = ActionIntent(did+'/intent', did, view.athlete, *chosen[:3],
                          view.delivered_ms,
                          view.pending_command_id if chosen[0] == 'continue_current' else None)
    return intent, {'decision_id': did, 'owner': view.athlete,
                    'observation_id': view.observation_id, 'belief_revision': belief.revision,
                    'fresh_contact_ids':[c.entity for c in contacts],
                    'stale_contact_ids':[c.entity for c in belief.contacts if c not in contacts],
                    'considered_feedback': list(belief.own_feedback),
                    'pending_command_id': view.pending_command_id,
                    'options': options, 'selected': chosen}
