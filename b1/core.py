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


def decide(view: AthleteView, belief: BeliefState):
    """B1 PRISM option layer: individual belief-only lane evaluation.

    Values are provisional policy parameters, not physical/rating changes.
    This replaces the legacy tactical evaluator; sensing/beliefs use PRISM.
    """
    if belief.observation_id != view.observation_id:
        raise ValueError('belief/view provenance mismatch')
    contacts = tuple(c for c in belief.contacts
                     if 0 <= view.delivered_ms-c.captured_ms <= belief.max_contact_age_ms)
    options = [('retain' if view.holds_ball else 'no_action', None, None, 0.0)]
    if view.holds_ball:
        opponents = [c for c in contacts if c.team != view.team]
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
    intent = ActionIntent(did+'/intent', did, view.athlete, *chosen[:3], view.delivered_ms)
    return intent, {'decision_id': did, 'owner': view.athlete,
                    'observation_id': view.observation_id, 'belief_revision': belief.revision,
                    'fresh_contact_ids':[c.entity for c in contacts],
                    'stale_contact_ids':[c.entity for c in belief.contacts if c not in contacts],
                    'options': options, 'selected': chosen}
