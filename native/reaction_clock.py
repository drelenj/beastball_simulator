"""RB-3.36 readiness delays shared by reactive duties across positions."""
from math import hypot

SET_TIME_S = .40


def set_speed(player):
    return player.a.braking * SET_TIME_S


def keeper_set_speed(player, match, config):
    if 'universal_set_speed' in getattr(config,'rb333',()):
        return set_speed(player)
    return match.assume['keeper_set_mps']


class ReactionClock:
    """Latch speed at reaction onset. Renewing a command keeps its deadline."""

    def __init__(self, port):
        self.port = port
        self.match = port.m
        self.state = self.match.s
        self.unset_s = self.match.assume['keeper_unset_s']
        self.delay = round(1000*self.unset_s)
        self.unset = 'universal_unset' in port.config.rb333
        self.ball_key = None
        self.ball_start = None
        self.ball_team = None
        self.ball_speeds = {}
        self.reaches = {}
        self.commands = {}
        self.pending_moves = {}
        self.loose = {}
        self.observe = lambda *_args: None
        engine = self.match.e
        previous_emit = engine.emit

        def emit(event, rule, **data):
            if event in ('release','restart_release','frame_contact','touch'):
                ball = self.state.ball
                key = (id(ball),ball.version)
                if not ball.carrier and key != self.ball_key:
                    self.start_course(key,self.state.now)
            return previous_emit(event,rule,**data)

        engine.emit = emit

    def start_course(self, key, now):
        ball = self.state.ball
        self.ball_key, self.ball_start = key, now
        self.ball_team = ball.last_touch
        self.ball_speeds = {
            p.id: hypot(p.vx,p.vy)>set_speed(p)
            for p in self.state.players.values() if p.active and p.role!='archer'
        }
        self.reaches.clear()

    def hands_delay(self, player):
        ball, match = self.state.ball, self.match
        key = (id(ball),ball.version)
        if self.ball_key != key or match.seen_from > self.ball_start:
            self.start_course(key,match.seen_from)
        if player.id not in self.reaches:
            kind = ('interception' if self.ball_team and player.team != self.ball_team
                    else 'catch')
            delay = self.delay if self.unset and self.ball_speeds.get(player.id,False) else 0
            ident = (kind,player.id,self.ball_start,ball.version)
            self.reaches[player.id] = (delay,ident)
            self.observe('start',ident,delay)
        return self.reaches[player.id][0]

    def begin_command(self, player, kind, target):
        """Start a new reactive command episode at ingress, if applicable."""
        if kind is None:
            self.commands.pop(player.id,None)
            self.pending_moves.pop(player.id,None)
            return self.state.now
        old = self.commands.get(player.id)
        if old and old[0:2] == (kind,target):
            return old[2]
        delay = self.delay if self.unset and player.speed>set_speed(player) else 0
        ready = self.state.now + delay
        ident = (kind,player.id,self.state.now,target)
        self.commands[player.id] = (kind,target,ready,ident)
        self.pending_moves.pop(player.id,None)
        self.observe('start',ident,delay)
        return ready

    def perceive(self, view):
        self.loose[view.athlete] = view.signals.ball_status in ('loose_ground','loose_airborne')

    def admitted_move(self, player, intent, desired, old_aim):
        if intent.contact in ('wrap','takedown'):
            # Pursuit may already be under way. Only reactive contact is delayed.
            self.begin_command(player,'takedown',intent.target)
            return
        if intent.kind=='pursue' and self.loose.get(player.id,False):
            ready = self.begin_command(player,'loose_pursuit',None)
            if ready>self.state.now:
                self.pending_moves[player.id] = (ready,desired)
                self.port.move[player.id] = old_aim
        else:
            self.begin_command(player,None,None)

    def contact_ready(self, player):
        command = self.commands.get(player.id)
        return not command or command[0]!='takedown' or self.state.now>=command[2]

    def next_deadline(self, now):
        return min((c[2] for c in self.commands.values() if c[2]>now),default=float('inf'))

    def execute_moves(self):
        now = self.state.now
        for player,(deadline,aim) in tuple(self.pending_moves.items()):
            if deadline<=now:
                self.port.move[player] = aim
                del self.pending_moves[player]
