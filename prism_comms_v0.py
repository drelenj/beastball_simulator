"""PRISM communication interfaces (roadmap: PRISM I individual -> II distributed team cognition -> III coaching/strategic).
Phase I only ESTABLISHES the interfaces; they are inert unless COMMS_ACTIVE is set, so nothing in the individual layer changes.
Governing rule: no information moves between minds without a plausible acquisition or communication pathway.
Three information types: PRIVATE (own perception/inference), COMMUNICATED (from another mind, may be wrong or deceptive), PUBLIC (official game state only).
Pure standard library; no engine imports."""
import math
from dataclasses import dataclass, field

PRIVATE, COMMUNICATED, PUBLIC = 'private', 'communicated', 'public'
KINDS = ('observation', 'warning', 'instruction', 'intention', 'deception')     # deception is a sender-side label; receivers never see it
CHANNELS = {  # [P] range (m), base clarity at 1 m, latency (s) from speech/gesture to being understood
    'voice': dict(range=35., clarity=.9, latency=.35), 'gesture': dict(range=45., clarity=.8, latency=.25, needs_los=True), 'signal': dict(range=80., clarity=.95, latency=.2, needs_los=True)}
COMMS_ACTIVE = False


@dataclass
class Message:
    sender: str; kind: str; channel: str; t_sent: float; origin: tuple; payload: dict
    loudness: float = 1.0                      # voice only; crowd noise is applied at the receiver
    reliability: float = 1.0                   # sender-side confidence the sender attaches (receiver still applies its own trust)
    to: tuple = ()                             # intended receivers; EMPTY means any who can acquire it (overhearing by opponents is possible)
    truthful: bool = True                      # simulator-side ground truth for metrics only; never read by receivers


@dataclass
class Received:
    msg: Message; t_av: float; clarity: float; src: str = COMMUNICATED


class CommsMixin:
    """The six interface functions.  Individual PRISM keeps its own beliefs; messages land in an inbox and only enter beliefs through update_beliefs()."""
    def _comms_init(self, trust=None):
        self.inbox = []; self.comm_bel = {}; self.trust = {} if trust is None else trust; self.default_trust = .6; self.noise_db = 0.; self.comm_stats = {}

    def _cs(self, k): self.comm_stats[k] = self.comm_stats.get(k, 0) + 1

    # -- acquisition pathways ------------------------------------------------------------------
    def receive_observation(self, pid, x, y, t_obs, now_s):
        """Own perception only.  Present so the interface list is complete; Phase I's tick()/deliver() path remains the acquisition code."""
        return PRIVATE

    def can_acquire(self, msg, my_xy, my_id, crowd_noise=0., has_los=True, now_s=0.):
        """The pathway test.  Returns (ok, clarity)."""
        ch = CHANNELS[msg.channel]; d = math.dist(msg.origin, my_xy)
        if d > ch['range'] or (ch.get('needs_los') and not has_los): return False, 0.
        clarity = ch['clarity'] * max(0., 1. - d / ch['range']) ** .5
        if msg.channel == 'voice': clarity *= msg.loudness / (msg.loudness + crowd_noise + 1e-9)
        return clarity > .15, clarity

    def receive_message(self, msg, my_xy, my_id, now_s, crowd_noise=0., has_los=True):
        if not COMMS_ACTIVE: return False
        ok, cl = self.can_acquire(msg, my_xy, my_id, crowd_noise, has_los, now_s)
        if not ok: self._cs('missed'); return False
        self.inbox.append(Received(msg, msg.t_sent + CHANNELS[msg.channel]['latency'], cl)); self._cs('heard'); return True

    # -- belief integration --------------------------------------------------------------------
    def update_beliefs(self, now_s):
        """Move arrived messages into comm_bel (separate from private beliefs).  fused() decides which a decision may use."""
        if not COMMS_ACTIVE: return 0
        keep, n = [], 0
        for r in self.inbox:
            if r.t_av > now_s: keep.append(r); continue
            m = r.msg; pid = m.payload.get('about')
            if m.kind in ('observation', 'warning', 'intention', 'deception') and pid is not None and 'x' in m.payload:
                t_obs = m.payload.get('t_obs', m.t_sent); old = self.comm_bel.get(pid)
                if old is None or t_obs >= old['t']:
                    self.comm_bel[pid] = dict(x=m.payload['x'], y=m.payload['y'], vx=m.payload.get('vx', 0.), vy=m.payload.get('vy', 0.), t=t_obs,
                                              w=self.trust.get(m.sender, self.default_trust) * r.clarity * m.reliability, src=COMMUNICATED, sender=m.sender)
                    n += 1
        self.inbox = keep; return n

    def fused(self, pid, now_s, private=None):
        """Which belief a decision may use: a private one that is at least as fresh wins; else a communicated one, flagged and weighted by trust.
        private: (x, y, vx, vy, t) or None.  Returns dict(x,y,vx,vy,t,w,src) or None."""
        c = self.comm_bel.get(pid)
        if private is not None and (c is None or private[4] >= c['t']): return dict(x=private[0], y=private[1], vx=private[2], vy=private[3], t=private[4], w=1., src=PRIVATE)
        return c

    # -- sending / instructions (inert in Phase I) ---------------------------------------------
    def send_message(self, kind, channel, payload, origin, now_s, to=(), loudness=1., truthful=True, me='?'):
        if not COMMS_ACTIVE: return None
        if kind not in KINDS or channel not in CHANNELS: raise ValueError('unknown kind or channel')
        self._cs('sent'); return Message(me, kind, channel, now_s, origin, payload, loudness, 1., to, truthful)

    def receive_instruction(self, msg, my_xy, my_id, now_s, **kw):
        """An instruction arrives like any message (a coach is a sender with a voice/signal channel); it sets a goal only after update_beliefs/strategy interpret it."""
        return self.receive_message(msg, my_xy, my_id, now_s, **kw)
