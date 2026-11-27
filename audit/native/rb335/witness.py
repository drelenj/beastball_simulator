"""Read-only RB-3.35 match observations."""
from collections import Counter
from math import hypot

from native import cognition


class Witness:
    def __init__(self, driver):
        port = driver.port
        state, engine = port.m.s, port.m.e
        self.issues, self.accepted = Counter(), Counter()
        self.blocked = Counter()
        self.plants = 0
        self.arrivals = []
        self.sidelines = 0
        self.tackles, self.scrimmages = [], []
        self.carrier_out = {}
        collisions = {}
        flight = None
        latest_issue = None
        self.keeper_plants_at_release = 0
        planted = set()
        advance, submit, emit, step = driver.advance, port.submit, engine.emit, port.step

        def observe_decision(view, belief, remaining, selector):
            nonlocal latest_issue
            intent, record = (selector(view,belief,remaining) if selector is not None
                              else cognition.decide(view,belief))
            latest_issue = record.get('contact_issue')
            if latest_issue:
                path, _, _, blocked = latest_issue
                self.issues[path] += 1
                self.blocked[path] += blocked
            if view.role == 'keeper':
                planted.discard(view.athlete)
                if any(menu['choice']=='plant' for menu in record.get('core_menus',())):
                    self.plants += 1
                    planted.add(view.athlete)
            return intent,record

        def observed_submit(intent):
            result = submit(intent)
            if latest_issue and intent.contact in ('wrap','takedown') and result['status']=='accepted':
                self.accepted[latest_issue[0]] += 1
            return result

        def observed_emit(event, rule, **data):
            nonlocal flight
            index = emit(event,rule,**data)
            if event == 'release':
                if data.get('kind')=='shot':
                    team = state.players[data['player']].team
                    self.keeper_plants_at_release += any(state.players[p].team!=team for p in planted)
                flight = None
                if data.get('kind')=='pass':
                    pending = port.pending.get(data['player'],{}).get('cmd')
                    if pending and pending.intent.aim and pending.intent.target in state.players:
                        x,y = pending.intent.aim
                        dx,dy = x-state.ball.x,y-state.ball.y
                        flight = (index,pending.intent.target,x,y,dx,dy)
            elif event in ('control','boundary','restart_awarded','goal','period_end'):
                if event=='control' and flight and data.get('player')==flight[1]:
                    self._arrival(state,flight,'target_control')
                flight = None
            if event=='c3_collision':
                for key in ('a','b'):
                    if data.get(key):
                        collisions[data[key]] = state.now
            elif event=='boundary':
                holder = data.get('carrier') or state.ball.carrier
                if holder:
                    self.carrier_out[index] = (state.now-collisions.get(holder,-1000)<=500)
            elif event=='tackle_count' and data.get('count_to')==1:
                self.tackles.append(state.now)
            elif event=='restart_awarded' and data.get('kind')=='scrimmage':
                self.scrimmages.append(state.now)
            return index

        def observed_step():
            nonlocal flight
            ball = state.ball
            holder = ball.carrier
            old_y = ball.y
            step()
            if flight:
                _,_,x,y,dx,dy = flight
                ball = state.ball
                if (ball.x-x)*dx+(ball.y-y)*dy >= 0 and ball.carrier is None:
                    self._arrival(state,flight,'aim_plane')
                    flight = None
            ball = state.ball
            if holder and holder==ball.carrier and (0 <= old_y <= 100) and (ball.y<0 or ball.y>100):
                self.sidelines += 1

        def observed_advance(*,progress=None,select=None):
            def observe(view,belief,remaining):
                return observe_decision(view,belief,remaining,select)
            return advance(observe,progress=progress)

        driver.advance = observed_advance
        port.submit, engine.emit, port.step = observed_submit, observed_emit, observed_step

    def _arrival(self,state,flight,kind):
        index,target,x,y,_,_ = flight
        receiver = state.players[target]
        self.arrivals.append(dict(id=index,kind=kind,ms=state.now,receiver=target,
                                  xy=(receiver.x,receiver.y),distance=hypot(x-receiver.x,y-receiver.y)))

    def result(self):
        return dict(path_issued=self.issues,path_accepted=self.accepted,path_gated=self.blocked,
                    plants=self.plants,plants_at_release=self.keeper_plants_at_release,
                    arrivals=self.arrivals,sidelines=self.sidelines,first_tackles=self.tackles,
                    scrimmages=self.scrimmages,carrier_after_contact=self.carrier_out)
