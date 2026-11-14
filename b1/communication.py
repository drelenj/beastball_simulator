"""M2 transport only. Opaque bytes have no gameplay interpretation.

Each batch is one closed send-time boundary. Producers may prepare envelopes in
parallel, but the simulation commits exactly one canonically ordered batch per
send time. Per-envelope/per-recipient RNG streams make worker order irrelevant.
"""
from dataclasses import dataclass, replace
from enum import Enum
import hashlib
import json
import random


class ContentSlot(Enum):
    OPAQUE = 'opaque'


@dataclass(frozen=True)
class MessageEnvelope:
    sender: str
    recipients: tuple[str, ...]
    kind: str
    payload: bytes
    causal_id: str
    send_ms: int
    content_slot: ContentSlot = ContentSlot.OPAQUE

    def __post_init__(self):
        if (any(not isinstance(v, str) or not v for v in (self.sender, self.causal_id, self.kind)) or
                not isinstance(self.send_ms, int) or
                not isinstance(self.recipients, tuple) or
                any(not isinstance(r, str) or not r for r in self.recipients) or
                self.send_ms < 0 or not isinstance(self.payload, bytes) or
                not self.recipients or
                len(set(self.recipients)) != len(self.recipients) or
                self.content_slot is not ContentSlot.OPAQUE):
            raise ValueError('invalid immutable envelope')

    @property
    def wire_bytes(self):
        return len(json.dumps([self.sender, sorted(self.recipients), self.kind,
                              self.payload.hex(), self.causal_id, self.send_ms,
                              self.content_slot.value], separators=(',', ':')).encode())


@dataclass(frozen=True)
class Delivery:
    envelope: MessageEnvelope
    recipient: str
    due_ms: int
    delivered_ms: int | None = None


@dataclass(frozen=True)
class DeliveryModel:
    enabled: bool = False
    delay_min_ms: int = 100
    delay_max_ms: int = 300
    loss: float = 0.
    noise: float = 0.    # independent per-byte probability; one random bit flips
    window_ms: int = 1000
    bandwidth_bytes: int = 4096  # per sender/window; multicast charged per recipient
    messages_per_window: int = 16
    queue_capacity: int = 32     # per recipient
    intake_capacity: int = 8    # per view; overflow drops newest due deliveries

    def __post_init__(self):
        if (not 0 <= self.loss <= 1 or not 0 <= self.noise <= 1 or
                not 0 <= self.delay_min_ms <= self.delay_max_ms or
                min(self.window_ms, self.bandwidth_bytes, self.messages_per_window,
                    self.queue_capacity, self.intake_capacity) <= 0):
            raise ValueError('invalid delivery model')


class TeamTransport:
    def __init__(self, seed, teams, model=DeliveryModel()):
        self.model, self.seed, self.teams = model, str(seed), dict(teams)
        self._pending, self._seen, self._usage = [], set(), {}
        self._last_send, self._intake_times = -1, {}
        self.audit = []

    def send_batch(self, envelopes, now_ms):
        """No receiver callback. Null mode does not iterate inputs or draw RNG."""
        if not self.model.enabled:
            return ()
        if now_ms <= self._last_send:
            raise ValueError('send boundaries must increase; batch simultaneous sends')
        batch = sorted(envelopes, key=lambda e:(e.send_ms,e.sender,e.causal_id))
        ids = [e.causal_id for e in batch]
        if (len(set(ids)) != len(ids) or any(i in self._seen for i in ids) or
                any(e.send_ms != now_ms or e.sender not in self.teams or
                    any(r not in self.teams or self.teams[r] != self.teams[e.sender]
                        for r in e.recipients) for e in batch)):
            raise ValueError('invalid time, team routing or duplicate causal ID')
        self._last_send = now_ms
        self._seen.update(ids)
        self._usage = {k:v for k,v in self._usage.items() if k[1] == now_ms//self.model.window_ms}
        records = []
        for e in batch:
            key = (e.sender, now_ms//self.model.window_ms)
            count, size = self._usage.get(key, (0,0))
            charge = e.wire_bytes*len(e.recipients)
            if count >= self.model.messages_per_window or size+charge > self.model.bandwidth_bytes:
                records.append((e.causal_id,None,'bandwidth'))
                continue
            self._usage[key] = (count+1,size+charge)
            for recipient in sorted(e.recipients):
                material = json.dumps([self.seed,e.sender,e.causal_id,recipient]).encode()
                rng = random.Random(int.from_bytes(hashlib.sha256(material).digest(),'big'))
                delay = rng.randint(self.model.delay_min_ms,self.model.delay_max_ms)
                lost = rng.random() < self.model.loss
                payload = bytes(b ^ ((1 << rng.randrange(8)) if rng.random() < self.model.noise else 0)
                                for b in e.payload)
                if lost:
                    status = 'lost'
                elif sum(d.recipient == recipient for d in self._pending) >= self.model.queue_capacity:
                    status = 'queue_capacity'
                else:
                    self._pending.append(Delivery(replace(e,payload=payload),recipient,now_ms+delay))
                    status = 'queued'
                records.append((e.causal_id,recipient,status))
        self._pending.sort(key=lambda d:(d.due_ms,d.envelope.send_ms,d.envelope.sender,
                                         d.envelope.causal_id,d.recipient))
        self.audit.extend(records)
        return tuple(records)

    def intake(self, recipient, now_ms):
        """Called only while constructing a new immutable receiver view."""
        if not self.model.enabled:
            return ()
        if recipient not in self.teams or now_ms <= self._intake_times.get(recipient,-1):
            raise ValueError('unknown recipient or repeated/backward intake')
        self._intake_times[recipient] = now_ms
        due = [d for d in self._pending if d.recipient == recipient and d.due_ms <= now_ms]
        self._pending = [d for d in self._pending if not (d.recipient == recipient and d.due_ms <= now_ms)]
        self.audit.extend((d.envelope.causal_id,recipient,'intake_capacity')
                          for d in due[self.model.intake_capacity:])
        return tuple(replace(d,delivered_ms=now_ms) for d in due[:self.model.intake_capacity])


@dataclass(frozen=True)
class PlanStageActivation:
    observation_id: str
    athlete: str
    stage_id: str | None = None
    causal_ids: tuple[str, ...] = ()
    active: bool = False


@dataclass(frozen=True)
class ReactionGate:
    observation_id: str
    athlete: str
    activation: PlanStageActivation
    bypass: bool = True


def plan_hooks(view, belief):
    """Empty stage registry. Hooks have no access to a transport or world."""
    if view.observation_id != belief.observation_id:
        raise ValueError('belief/view provenance mismatch')
    activation = PlanStageActivation(view.observation_id,view.athlete)
    return activation, ReactionGate(view.observation_id,view.athlete,activation)


def receive_messages(view):
    """Only the view supplies intake; neither transport nor world is accepted."""
    if any(d.recipient != view.athlete or d.delivered_ms != view.delivered_ms or
           d.envelope.send_ms > d.due_ms or d.due_ms > d.delivered_ms
           for d in view.messages):
        raise ValueError('message/view provenance mismatch')
    return tuple(view.messages)
