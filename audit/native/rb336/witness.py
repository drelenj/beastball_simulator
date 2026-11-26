"""Read-only set-speed, tackle and reaction evidence."""
from collections import Counter, defaultdict
from math import hypot

from native.reaction_clock import ReactionClock, keeper_set_speed, set_speed


class Witness:
    def __init__(self, driver):
        port = driver.port
        state, engine = port.m.s, port.m.e
        clock = port.reaction_clock
        if clock is None:
            # An observer clock has zero delay. The physical reach hook only
            # notifies it on possible contacts and never consumes randomness.
            clock = ReactionClock(port)
            port.reaction_clock = clock
            port.m.native_reaction_observe = clock.hands_delay
        self.actions = {}
        self.set_speeds = defaultdict(list)
        for p in state.players.values():
            agility = p.a.agility
            band = '<.60' if agility<.60 else '.60–.69' if agility<.70 else '.70–.79' if agility<.80 else '≥.80'
            self.set_speeds[band].append(set_speed(p))
        self.shots = []
        self.endline_continued = []
        self.tackles = []
        self.event_times = {}
        emit, step = engine.emit, port.step

        def observe(event, ident, delay):
            self.actions.setdefault(ident,dict(kind=ident[0],athlete=ident[1],ms=ident[2],
                                               delay_ms=delay,secure=False,deflected=False))
        clock.observe = observe

        def observed_emit(event, rule, **data):
            if event=='release' and data.get('kind')=='shot':
                attacker = state.players[data['player']]
                keeper = next((p for p in state.players.values() if p.active and p.role=='keeper'
                               and p.team!=attacker.team),None)
                if keeper:
                    self.shots.append(dict(speed=hypot(keeper.vx,keeper.vy),
                                           threshold=keeper_set_speed(keeper,port.m,port.config),ms=state.now))
            if event in ('control','touch'):
                info = clock.reaches.get(data.get('player'))
                if info and info[1] in self.actions:
                    self.actions[info[1]]['secure' if event=='control' else 'deflected'] = True
            elif event=='tackle_count':
                self.tackles.append((state.now,data['count_to']))
                key = clock.commands.get(data.get('actor'))
                if key and key[3] in self.actions:
                    self.actions[key[3]]['secure'] = True
            if event in ('period_end','restart_awarded','possession_change','control'):
                self.event_times[state.now] = state.live_ms
            return emit(event,rule,**data)

        def observed_step():
            ball = state.ball
            holder,x = ball.carrier,ball.x
            step()
            after = state.ball
            if holder and after.carrier==holder and 0<=x<=100 and (after.x<0 or after.x>100):
                self.endline_continued.append(dict(ms=state.now,player=holder,xy=(after.x,after.y)))
        engine.emit,port.step = observed_emit,observed_step

    def result(self):
        counts = defaultdict(Counter)
        for action in self.actions.values():
            kind = action['kind']
            group = 'paid' if action['delay_ms'] else 'set'
            counts[kind][group+'_starts'] += 1
            counts[kind][group+'_success'] += action['secure']
            if action['deflected']:
                counts['deflection'][group+'_starts'] += 1
        return dict(reactions=counts,set_speeds=self.set_speeds,shots=self.shots,
                    endline_continued=self.endline_continued,tackles=self.tackles,event_times=self.event_times)
