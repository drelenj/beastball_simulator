"""RB/3.17 motor execution. Installed only for the enabled RB/3 profile."""
from math import dist, hypot

from native.cognition import MotorCommand


HANDOFF_MS = 150
CONTACT_EPS_M = 1e-6  # Same geometric tolerance as C3 body contact.
APPROACH_OVERLAP_M = .08  # C3 locomotion's existing near-target deadband.


def unit(dx, dy):
    length = hypot(dx, dy)
    return (dx / length, dy / length) if length else (0., 0.)


def block_power(player):
    """Legacy block-force strength, with fatigue and sqrt mass scaling."""
    a = player.a
    return a.strength * a.blocking * (a.mass / 220.) ** .5 * (.5 + .5 * player.fatigue)


def block_impedance(blocker, target, leverage):
    """Fraction of positive normal propulsion absorbed, bounded by one."""
    power = block_power(blocker)
    total = power + block_power(target)
    return leverage * power / total if total else 0.


class HandoffBlock:
    def __init__(self, port):
        self.port = port
        self.match = port.m
        self.state = self.match.s
        self.engine = self.match.e
        self.blocks = {}
        self.engaged = {}
        self.drive = self.match.c3_desired
        self.match.c3_desired = self.drive_with_blocks
        self.complete_match = self.engine.complete
        self.engine.complete = self.finish

    def finish(self, *args, **kwargs):
        self.close_engagements({})
        return self.complete_match(*args, **kwargs)

    def actor_ready(self, player):
        return self.engine.eligible(player) and player.posture != 'grounded'

    def handoff_reason(self, giver, receiver):
        s, p, e = self.state, self.port, self.engine
        if getattr(e, 'rb310_hold', None):
            return 'snap_hold'
        if s.phase not in (p.types.Phase.LIVE, p.types.Phase.PENALTY) or s.ball.carrier != giver.id:
            return 'not_live_carrier'
        if receiver is None or receiver is giver or receiver.team != giver.team:
            return 'not_teammate'
        if not (self.actor_ready(giver) and self.actor_ready(receiver)) or not e.rb_can_enter(receiver):
            return 'ineligible_hands'
        # A conservative guard for the unsettled case of a transfer into
        # the giving team's own zone from outside (no ZR-T flight exists).
        if e.zone(giver.x, giver.y) != s.own_zone(giver.team) and e.zone(receiver.x, receiver.y) == s.own_zone(giver.team):
            return 'own_zone_entry'
        return None

    def block_reason(self, blocker, target):
        s, e = self.state, self.engine
        if getattr(e, 'rb310_hold', None):
            return 'snap_hold'
        if s.phase != self.port.types.Phase.LIVE:
            return 'not_live'
        if target is None or target.team == blocker.team or target.role != 'field':
            return 'not_opposing_field'
        if s.ball.carrier in (blocker.id, target.id):
            return 'carrier'
        if blocker.posture != 'upright' or target.posture != 'upright':
            return 'not_upright'
        if target.frozen(s.now):
            return 'frozen_obstacle'
        legal, reason = e.contact_legal(blocker, target, 'block', reach=False)
        return None if legal else reason

    def submit(self, actor, intent):
        p, s = self.port, self.state
        target = s.players.get(intent.target)
        if intent.kind == 'handoff':
            reason = self.handoff_reason(actor, target)
            if actor.id in p.pending:
                reason = reason or 'resource_busy'
            release = s.now + round(HANDOFF_MS * (1.35 - .5 * actor.a.ball_handling))
            resource = 'ball'
        else:
            reason = self.block_reason(actor, target)
            if intent.aim is None or not all(0 <= coordinate <= 100 for coordinate in intent.aim):
                reason = reason or 'missing_protected_point'
            release = None
            resource = 'locomotion'
        if reason:
            return {'status': 'rejected', 'reason': reason}
        command = MotorCommand(intent.intent_id + '/command', intent, s.now, release, resource)
        p.command_log.append(command)
        if intent.kind == 'handoff':
            p.pending[actor.id] = dict(cmd=command, due=release, period=s.period, version=s.ball.version)
            self.engine.emit('handoff_start', 'RB-3.17', giver=actor.id, receiver=target.id,
                             command_id=command.command_id, due_ms=release)
        else:
            self.blocks[actor.id] = (intent, s.period)
        return {'status': 'accepted', 'command': command}

    def execute_handoff(self, giver, pending):
        p, s, e = self.port, self.state, self.engine
        command = pending['cmd']
        receiver = s.players.get(command.intent.target)
        reason = self.handoff_reason(giver, receiver)
        if reason or s.ball.version != pending['version']:
            p.resolve(giver.id, 'rejected_' + (reason or 'control_changed'))
            return
        first = (giver.x, giver.y, giver.hand_height)
        second = (receiver.x, receiver.y, receiver.hand_height)
        reach = giver.a.reach + receiver.a.reach
        ball = s.ball
        gap = dist(first, second)
        if gap > reach + ball.radius:  # one ball radius of shared contact slack
            p.resolve(giver.id, 'rejected_out_of_reach')
            return
        fraction = giver.a.reach / reach
        point = tuple(a + fraction * (b - a) for a, b in zip(first, second))
        speed = dist((giver.vx, giver.vy, giver.vz), (receiver.vx, receiver.vy, receiver.vz))
        energy = .5 * self.match.assume['ball_mass_kg'] * speed ** 2
        miss = max(0., gap - reach) / ball.radius
        capacity = self.match.native_catch_capacity(receiver.a.catching, miss)
        secure = 1 / (1 + (energy / capacity) ** 8) if capacity > 1e-9 else 0.
        data = dict(giver=giver.id, receiver=receiver.id, command_id=command.command_id,
                    relative_hand_mps=speed, secure_probability=secure, point=point)
        if self.match.rng['ball'].random() < secure:
            # Reuse committed control, including possession, dribble and
            # Keeper bookkeeping. No release or flight event is emitted.
            saved = vars(ball).copy()
            ball.carrier = ball.last_releaser = None
            ball.x, ball.y, ball.z = point
            if not e.acquire(receiver.id):
                vars(ball).clear()
                vars(ball).update(saved)
                p.resolve(giver.id, 'rejected_acquisition')
                return
            self.match.c3_reconcile()
            e.emit('handoff_complete', 'RB-3.17', **data)
            p.resolve(giver.id, 'handoff_complete')
        else:
            ball.carrier = ball.last_releaser = ball.intended = None
            ball.mode = p.types.BallMode.LOOSE
            ball.x, ball.y, ball.z = point
            ball.vx = (giver.vx + receiver.vx) / 2
            ball.vy = (giver.vy + receiver.vy) / 2
            ball.vz = 0.
            ball.last_touch = giver.team
            ball.scoring = False
            ball.rb_release_team = ball.rb_release_band = None
            ball.version += 1
            ball.course_time = s.now
            self.match.c3_reconcile()
            e.emit('handoff_fumble', 'RB-3.17', **data)
            e.native_sync()
            p.resolve(giver.id, 'handoff_fumble')

    def relationship(self, blocker, target, point):
        """Target-to-blocker normal and its alignment with the protected side."""
        nx, ny = unit(blocker.x - target.x, blocker.y - target.y)
        px, py = unit(point[0] - target.x, point[1] - target.y)
        leverage = max(0., nx * px + ny * py)
        radius = (blocker.radius + target.radius) * self.match.assume['body_radius_scale']
        gap = hypot(blocker.x - target.x, blocker.y - target.y)
        separating = (blocker.vx - target.vx) * nx + (blocker.vy - target.vy) * ny
        between = (blocker.x - point[0]) * px + (blocker.y - point[1]) * py <= CONTACT_EPS_M
        if gap > radius + CONTACT_EPS_M or not between or separating > CONTACT_EPS_M:
            leverage = 0.
        return nx, ny, leverage

    def current(self, actor_id, request):
        intent, period = request
        s = self.state
        actor, target = s.players[actor_id], s.players[intent.target]
        if (s.period != period or s.now - intent.decided_ms >= self.port.config.decision_ms or
                getattr(actor, 'native_intent', None) is not intent or self.block_reason(actor, target)):
            return None
        return actor, target, intent

    def update_blocks(self, steer=True):
        s, e, p = self.state, self.engine, self.port
        if e.final_seq is not None:
            return
        now = {}
        for actor_id, request in sorted(self.blocks.items()):
            active = self.current(actor_id, request)
            if active is None:
                if getattr(s.players[actor_id], 'native_intent', None) is request[0]:
                    p.move[actor_id] = (s.players[actor_id].x, s.players[actor_id].y)
                if steer:
                    del self.blocks[actor_id]
                continue
            actor, target, intent = active
            if steer:
                nx, ny = unit(intent.aim[0] - target.x, intent.aim[1] - target.y)
                # Aim just inside the body envelope; C3, not this motor,
                # resolves impact and prevents physical overlap.
                radius = (actor.radius + target.radius) * self.match.assume['body_radius_scale']
                offset = max(0., radius - 2 * APPROACH_OVERLAP_M)
                p.move[actor.id] = (target.x + nx * offset, target.y + ny * offset)
            if self.relationship(actor, target, intent.aim)[2] > 0:
                key = actor.id, target.id
                now[key] = self.engaged.get(key, s.live_ms)
                if key not in self.engaged:
                    e.emit('block_engaged', 'RB-3.17', blocker=actor.id, target=target.id,
                           intent_id=intent.intent_id)
        self.close_engagements(now)

    def close_engagements(self, now):
        for blocker, target in sorted(self.engaged.keys() - now.keys()):
            self.engine.emit('block_shed', 'RB-3.17', blocker=blocker, target=target,
                             duration_ms=self.state.live_ms - self.engaged[blocker, target])
        self.engaged = now

    def drive_with_blocks(self, target, dt, live, carrier):
        before = target.vx, target.vy
        self.drive(target, dt, live, carrier)
        if not live or self.state.ball.carrier == target.id:
            return
        dvx, dvy = target.vx - before[0], target.vy - before[1]
        strongest = 0.
        correction = (0., 0.)
        for actor_id, request in sorted(self.blocks.items()):
            if request[0].target != target.id:
                continue
            active = self.current(actor_id, request)
            if active is None:
                continue
            actor, _, intent = active
            nx, ny, leverage = self.relationship(actor, target, intent.aim)
            if (target.target[0] - target.x) * nx + (target.target[1] - target.y) * ny <= 0:
                continue  # Let an athlete brake or voluntarily turn away.
            absorbed = (dvx * nx + dvy * ny) * block_impedance(actor, target, leverage)
            if absorbed > strongest:
                strongest = absorbed
                correction = absorbed * nx, absorbed * ny
        target.vx -= correction[0]
        target.vy -= correction[1]
