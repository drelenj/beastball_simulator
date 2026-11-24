"""RB/3.18 physical carrier commands, with the existing C3 rules as authority."""
import math

from native.cognition import MotorCommand
from .handoff_block import unit


STRETCH_MS = 200
REACH_FRACTION = .9  # Native hand sphere.
LEAD_MARGIN_M = 1.   # Near-plane intent window.


def push_power(player, skill):
    a = player.a
    return a.strength * skill * math.sqrt(a.mass / 220.) * (.5 + .5 * player.fatigue)


def truck_advantage(carrier, tackler, closing_carrier, closing_tackler, grip, assumptions):
    """Compare strength-weighted normal momentum and current grip impulse."""
    drive = max(0., closing_carrier) * carrier.a.mass * carrier.a.strength
    defence = max(0., closing_tackler) * tackler.a.mass * tackler.a.strength
    defence += grip * assumptions['grip_force_N'] * (.5 + tackler.a.strength) * assumptions['contact_time_s']
    forward_momentum = closing_carrier * carrier.a.mass - closing_tackler * tackler.a.mass
    return drive, defence, forward_momentum


class CarrierMoves:
    def __init__(self, port):
        self.port = port
        self.match = port.m
        self.engine = port.m.e
        self.state = port.m.s
        self.requests = {}
        self.engine.rb318_stretch = self.extension
        self.match.rb318_strip_multiplier = self.strip_multiplier
        self.match.rb318_truck = self.truck
        self.follow = self.engine.follow_carrier
        self.engine.follow_carrier = self.follow_stretched
        self.advance = self.match.advance_ball
        self.match.advance_ball = self.advance_stretched
        self.complete = self.engine.complete
        self.engine.complete = self.finish
        self.follow_ms = None

    def ready(self, carrier):
        s = self.state
        return (s.phase == self.port.types.Phase.LIVE and s.ball.carrier == carrier.id
                and not getattr(self.engine, 'rb310_hold', None)
                and carrier.role == 'field' and carrier.posture == 'upright'
                and self.engine.eligible(carrier))

    def opponent(self, carrier, target):
        if not target or target.team == carrier.team or target.role != 'field' or target.posture != 'upright':
            return False
        if target.frozen(self.state.now) or self.engine.rb_thaw_buffer(target):
            return False
        dx, dy = target.x - carrier.x, target.y - carrier.y
        fx, fy = carrier.facing
        return dx * fx + dy * fy >= 0 and self.engine.contact_legal(carrier, target, 'block', reach=False)[0]

    def submit(self, carrier, intent):
        s, e, p = self.state, self.engine, self.port
        if getattr(e, 'rb310_hold', None):
            return {'status': 'rejected', 'reason': 'snap_hold'}
        if not self.ready(carrier) or carrier.id in p.pending:
            return {'status': 'rejected', 'reason': 'carrier_unavailable'}
        target = s.players.get(intent.target)
        if intent.kind == 'stretch':
            if (abs(s.attack_goal(carrier.team) - carrier.x) > carrier.a.reach + LEAD_MARGIN_M
                    or abs(carrier.y - 50.) >= p.config.goal_radius):
                return {'status': 'rejected', 'reason': 'outside_stretch_window'}
        elif not self.opponent(carrier, target):
            return {'status': 'rejected', 'reason': 'contact_illegal'}
        if intent.kind == 'stiff_arm' and not self.arm_reaches(carrier, target):
            return {'status': 'rejected', 'reason': 'out_of_arm_reach'}
        self.end(carrier.id, 'replaced')
        cmd = MotorCommand(intent.intent_id + '/command', intent, s.now, None, 'carrier_move')
        p.command_log.append(cmd)
        self.requests[carrier.id] = (intent, s.ball.version)
        if intent.kind == 'stretch':
            e.emit('stretch_start', 'RB-3.18', carrier=carrier.id, team=carrier.team, intent_id=intent.intent_id)
        elif intent.kind == 'truck':
            e.emit('truck', 'RB-3.18', carrier=carrier.id, target=target.id, intent_id=intent.intent_id)
        else:
            e.emit('stiff_arm', 'RB-3.18', carrier=carrier.id, target=target.id, intent_id=intent.intent_id)
        if intent.kind in ('stretch', 'truck'):
            # Continue moving toward the intended goal or contact, without
            # teleporting the body or moving the hand independently in x/y.
            p.move[carrier.id] = intent.aim or (s.attack_goal(carrier.team), carrier.y)
        return {'status': 'accepted', 'command': cmd}

    def current(self, carrier, now, kind):
        request = self.requests.get(carrier.id)
        if not request:
            return None
        intent, version = request
        if (intent.kind == kind and self.ready(carrier) and version == self.state.ball.version
                and now - intent.decided_ms <= self.port.config.decision_ms
                and getattr(carrier, 'native_intent', None) is intent):
            return intent
        return None

    def end(self, carrier_id, reason):
        request = self.requests.pop(carrier_id, None)
        if request and request[0].kind == 'stretch':
            self.engine.emit('stretch_end', 'RB-3.18', carrier=carrier_id, reason=reason)

    def finish(self, *args, **kwargs):
        for actor_id in sorted(self.requests):
            self.end(actor_id, 'match_end')
        return self.complete(*args, **kwargs)

    def extension(self, carrier, now):
        intent = self.current(carrier, now, 'stretch')
        if intent is None:
            return 0.
        duration = round(STRETCH_MS * (1.35 - .5 * carrier.a.ball_handling))
        fraction = min(1., max(0., (now - intent.decided_ms) / duration))
        normal_offset = .35 + .35 * carrier.a.reach
        maximum = REACH_FRACTION * carrier.a.reach
        if self.port.prism_core:
            from native.prism_motion import stretch_maximum
            maximum = stretch_maximum(carrier, REACH_FRACTION)
        return max(0., maximum - normal_offset) * fraction

    def strip_multiplier(self, carrier, now):
        maximum = max(0., REACH_FRACTION * carrier.a.reach - (.35 + .35 * carrier.a.reach))
        fraction = self.extension(carrier, now) / maximum if maximum else 0.
        multiplier = self.match.assume['strip_in_motion_factor']
        if self.port.prism_core:
            multiplier = 1. + (multiplier - 1.) * (1 - carrier.a.ball_handling)
        return 1. + (multiplier - 1.) * fraction

    def follow_stretched(self):
        result = self.follow()
        ball = self.state.ball
        if ball.carrier:
            carrier = self.state.players[ball.carrier]
            now = self.state.now if self.follow_ms is None else self.follow_ms
            extra = self.extension(carrier, now)
            intent = self.current(carrier, now, 'stretch') if extra and self.port.prism_core else None
            if intent and intent.aim:
                attack = self.state.attack_sign(carrier.team)
                ux, uy = unit(intent.aim[0] - carrier.x, (intent.aim[1] - carrier.y) * carrier.a.ball_handling)
                ball.x += ux * extra if ux * attack > 0 else attack * extra
                ball.y += uy * extra if ux * attack > 0 else 0.
            else:
                ball.x += self.state.attack_sign(carrier.team) * extra
        return result

    def advance_stretched(self, ms, old_positions):
        self.follow_ms = self.state.now + ms
        try:
            return self.advance(ms, old_positions)
        finally:
            self.follow_ms = None

    @staticmethod
    def arm_reaches(carrier, target):
        return math.hypot(target.x - carrier.x, target.y - carrier.y) <= carrier.a.reach + target.radius

    def update(self, execute=True):
        s = self.state
        if self.engine.final_seq is not None:
            return
        for actor_id, (intent, _) in sorted(self.requests.items()):
            actor = s.players[actor_id]
            if self.current(actor, s.now, intent.kind) is None:
                self.end(actor_id, 'lost_control_or_expired')
            elif execute and intent.kind == 'stiff_arm':
                target = s.players[intent.target]
                if self.opponent(actor, target) and self.arm_reaches(actor, target):
                    self.stiff_arm(actor, target)
                self.end(actor_id, 'executed')

    def stiff_arm(self, actor, target):
        m, s = self.match, self.state
        p = push_power(actor, actor.a.ball_handling)
        q = push_power(target, target.a.blocking)
        a = m.assume
        impulse = a['traction_coefficient'] * actor.a.mass * a['gravity'] * a['contact_time_s']
        impulse *= p / (p + q) if p + q else 0.
        if self.port.prism_core:
            from native.prism_motion import STIFF_ARM_IMPULSE_RANGE
            impulse *= 1. + STIFF_ARM_IMPULSE_RANGE * (actor.native_registry['stiff_arm'] - .7)
        if impulse <= 0:
            return
        nx, ny = unit(target.x - actor.x, target.y - actor.y)
        if nx == ny == 0.:
            return
        for new, sign in ((actor, -1), (target, 1)):
            new.vx += sign * impulse * nx / new.a.mass
            new.vy += sign * impulse * ny / new.a.mass
        key = target.id, actor.id
        hold = m.c3_holds.get(key)
        before = hold['g'] if hold else 0.
        after = max(0., before - impulse / (a['grip_force_N'] * (.5 + target.a.strength) * a['contact_time_s']))
        if hold and after > 0:
            hold['g'] = after
        else:
            if hold:
                m.c3_end_hold(key, 'stiff_arm', s.now)
            m.c3_off[key] = s.now
        self.engine.emit('stiff_arm_effect', 'RB-3.18', carrier=actor.id, target=target.id,
                         impulse_Ns=impulse, grip_before=before, grip_after=after,
                         reacquire_ms=1000 * target.a.decision_speed if not after else 0.)

    def truck(self, carrier, a, b, ua, ub, tick, at):
        if carrier is None or carrier.id not in (a.id, b.id):
            return False
        intent = self.current(carrier, at, 'truck')
        target = b if carrier is a else a
        if (intent is None or intent.target != target.id or not self.opponent(carrier, target)
                or getattr(carrier, 'rb318_truck_used', None) == intent.intent_id):
            return False
        m = self.match
        carrier.rb318_truck_used = intent.intent_id  # C3 snapshots player state during replay.
        key = target.id, carrier.id
        grip = m.c3_holds.get(key, {}).get('g', 0.)
        drive, defence, forward = truck_advantage(carrier, target, ua if carrier is a else ub,
                                                   ub if carrier is a else ua, grip, m.assume)
        if self.port.prism_core:
            from native.prism_motion import TRUCK_DRIVE_RANGE
            drive *= 1. + TRUCK_DRIVE_RANGE * (carrier.native_registry['truck'] - .7)
        won = drive > defence and forward > 0.
        if won:
            m.c3_end_hold(key, 'truck', at, tick)
            m.c3_off[key] = at
        m.c3_note(tick, 'truck_broken' if won else 'truck_stopped', rule='RB-3.18',
                  carrier=carrier.id, target=target.id, drive=drive, defence=defence, grip=grip)
        return won
