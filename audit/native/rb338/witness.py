"""Read-only traces of Archer spending and the two seconds before carrier outs."""
from collections import defaultdict, deque
from math import atan2, degrees, hypot
from typing import NamedTuple

from native import cognition, cognition_rb3, paired_policy

WINDOW_MS = 2000
FIELD_LENGTH = 100.


class Moment(NamedTuple):
    id: str
    team: str
    x: float
    y: float
    z: float
    vx: float
    vy: float
    facing: tuple
    posture: str
    frozen: bool
    immune: bool
    target: tuple | None
    context: dict
    contact: str
    collision: tuple | None
    maneuver: str


def line_distance(x, y):
    return min(x,y,FIELD_LENGTH-x,FIELD_LENGTH-y)


def defender_read(p, defenders):
    def identity(player):
        return getattr(player,'id',None) or player.entity

    nearest = min(defenders,key=lambda q:(hypot(q.x-p.x,q.y-p.y),identity(q)),default=None)
    if nearest is None:
        return None
    dx,dy = nearest.x-p.x,nearest.y-p.y
    distance = hypot(dx,dy)
    closing = ((p.vx-nearest.vx)*dx+(p.vy-nearest.vy)*dy)/max(.001,distance)
    return dict(id=identity(nearest),distance=round(distance,3),closing_mps=round(closing,3))


class Witness:
    def __init__(self, driver):
        self.port = port = driver.port
        self.match = match = port.m
        self.state = state = match.s
        self.timeline = defaultdict(deque)
        self.world_frames = deque()
        self.maneuvers = {}
        self.decisions = {}
        self.collisions = {}
        self.outs, self.releases, self.freezes = [], [], []
        self.periods = {}
        self.period_zero = {}
        self.arrows = {}
        self.clamps = None
        self.boundary_holder = None

        emit, boundary = match.e.emit, match.e.boundary
        def observed_emit(event, rule, **data):
            seq = emit(event,rule,**data)
            now = state.now
            if event == 'c3_collision':
                for actor,other,delta in (('a','b','dv_a'),('b','a','dv_b')):
                    self.collisions[data[actor]] = (now,data[other],data.get(delta))
            elif event == 'boundary':
                holder = data.get('carrier') or self.boundary_holder
                if holder:
                    self.body_out(seq,data,holder)
            elif event in ('rb_arrow_release','rb_arrow_forfeited'):
                team = data['ruling']['team']
                self.releases.append(self.timing(team) | dict(legal=event=='rb_arrow_release',
                                     remaining=match.e.rb.remaining(team)))
            elif event == 'arrow_release':
                self.releases[-1].update(shooter=data['player'],target=data['target'],arrow=data['arrow'])
                self.arrows[data['arrow']] = self.releases[-1]
            elif event == 'freeze':
                player = state.players[data['player']]
                release = self.arrows.get(data['arrow'])
                team = release['team'] if release else state.other(player.team)
                self.freezes.append(self.timing(team) | dict(arrow=data['arrow'],player=player.id,
                                                            carrier=bool(data.get('was_carrier'))))
            elif event == 'period_end':
                self.periods[state.period] = {team:match.e.rb.remaining(team) for team in ('A','B')}
            return seq

        def observed_boundary(x=None,y=None,carrier=None):
            prior = self.boundary_holder
            self.boundary_holder = carrier or state.ball.carrier
            try:
                return boundary(x,y,carrier)
            finally:
                self.boundary_holder = prior

        move, process_events, submit = match.c3_step, match.process_events, port.submit
        def observed_move(ms,targets,scripted=False):
            self.physics('physics',state.now,targets)
            return move(ms,targets,scripted)

        def observed_events(events,start,advanced,old=None):
            self.physics('physics_end',start+advanced,None)
            return process_events(events,start,advanced,old)

        def observed_submit(intent):
            result = submit(intent)
            if result['status']=='accepted':
                maneuver = (intent.technique if intent.kind=='carry' else intent.kind)
                if maneuver in ('juke','spin','stiff_arm','truck'):
                    self.maneuvers[intent.athlete] = (maneuver,state.ball.version,intent)
                else:
                    self.maneuvers.pop(intent.athlete,None)
            return result

        match.e.emit = observed_emit
        match.e.boundary = observed_boundary
        match.c3_step = observed_move
        match.process_events = observed_events
        port.submit = observed_submit

        # Capture inputs and outputs of the actual pure aim clamps. These
        # wrappers are scoped to play() and restored in its finally block.
        self.original_clamps = ((cognition_rb3,'keep_in',cognition_rb3.keep_in),
                                (paired_policy,'boundary_aim',paired_policy.boundary_aim))

    def timing(self, team, row=None):
        s = self.state
        period, live, game, now = ((row['period'],row['live_ms'],row['g_ms'],row['t_ms'])
                                  if row else (s.period,s.live_ms,s.game_ms,s.now))
        period_ms = self.port.config.period_seconds*1000 if period<=4 else 300000
        start = self.period_zero.setdefault(period,live - period_ms + game)
        minute = max(0,(live-start)//60000)+1
        if period<=5:
            minute = min(minute,10 if period<=4 else 5)
        return dict(team=team,period=period,minute=minute,now=now,live_ms=live)

    def decide(self, view, belief, remaining):
        self.clamps = [] if view.holds_ball else None
        intent, record = cognition.decide(view,belief)
        if view.role != 'archer' and not view.bench_role:
            menus = record.get('core_menus',())
            picked = next((m['choice'] for m in menus if m['stage']=='carrier'),None)
            if not picked and menus:
                picked = menus[-1]['choice']
            opponents = [t for t in belief.tracks if t.team not in (view.team,'ball') and
                         t.role in ('field','keeper') and 0<=view.delivered_ms-t.captured_ms<=belief.max_track_age_ms]
            clamps = self.clamps or ()
            self.decisions[view.athlete] = dict(label=picked or intent.kind,kind=intent.kind,
                aim=intent.aim,technique=intent.technique,believed_line_m=round(line_distance(view.x,view.y),3),
                believed_defender=defender_read(view.body,opponents) if view.body is not None else None,
                clamp_checks=clamps,selected_aim_clamped=any(c['changed'] and c['after']==intent.aim for c in clamps),
                decision_ms=view.delivered_ms,held_at_decision=view.holds_ball)
            self.sample_decision('decision',view.athlete,view.delivered_ms)
        self.clamps = None
        return intent, record

    def play(self, driver, max_steps=None):
        for module,name,function in self.original_clamps:
            def clamp(view,aim, original=function, label=name):
                result = original(view,aim)
                if self.clamps is not None:
                    self.clamps.append(dict(kind=label,before=aim,after=result,changed=aim!=result))
                return result
            setattr(module,name,clamp)
        try:
            while not driver.final and (max_steps is None or driver.steps<max_steps):
                driver.advance(select=self.decide)
        finally:
            for module,name,function in self.original_clamps:
                setattr(module,name,function)

    def moment(self, p, now, target, contact):
        collision = self.collisions.get(p.id)
        if not contact:
            contact = 'collision' if collision and 0<=now-collision[0]<=100 else 'none'
        move = self.maneuvers.get(p.id)
        if move and (self.state.ball.carrier!=p.id or self.state.ball.version!=move[1] or
                     getattr(p,'native_intent',None) is not move[2]):
            move = None
        if move and move[0] in ('stiff_arm','truck'):
            motions = getattr(self.port,'rb318',None)
            if not motions or p.id not in motions.requests:
                move = None
        return Moment(p.id,p.team,p.x,p.y,p.z,p.vx,p.vy,p.facing,p.posture,p.frozen(now),
                      now<=p.immune_until,target,self.decisions.get(p.id,{}),contact,collision,
                      move[0] if move else 'none')

    def contacts(self):
        contact = {}
        for (_,target),hold in self.match.c3_holds.items():
            if hold['g']>0:
                contact[target] = 'hold'
            else:
                contact.setdefault(target,'wrap')
        return contact

    def physics(self,kind,now,targets):
        contact = self.contacts()
        world = {
            p.id:self.moment(p,now,p.target if targets is None else targets.get(p.id,p.target),
                             contact.get(p.id))
            for p in self.state.players.values() if p.active and p.role!='archer'
        }
        self.world_frames.append((now,kind,world))
        while self.world_frames and self.world_frames[0][0]<now-WINDOW_MS-1:
            self.world_frames.popleft()

    def sample_decision(self,kind,pid,now):
        p = self.state.players[pid]
        snapshot = self.moment(p,now,self.port.move.get(pid),self.contacts().get(pid))
        defenders = (q for q in self.state.players.values() if q.active and q.team!=p.team and q.role!='archer')
        queue = self.timeline[pid]
        queue.append(self.row(kind,now,snapshot,defenders))
        while queue and queue[0]['ms']<now-WINDOW_MS:
            queue.popleft()

    @staticmethod
    def row(kind,now,body,defenders):
        return dict(body.context,kind_of_sample=kind,ms=now,locomotion_target=body.target,
                    position=(round(body.x,3),round(body.y,3),round(body.z,3)),
                    speed=round(hypot(body.vx,body.vy),3),heading_deg=round(degrees(atan2(body.vy,body.vx)),2),
                    facing=body.facing,true_line_m=round(line_distance(body.x,body.y),3),
                    defender=defender_read(body,defenders),contact=body.contact,
                    last_collision_ms=body.collision[0] if body.collision else None,collision=body.collision,
                    posture=body.posture,frozen=body.frozen,thaw_immune=body.immune,maneuver=body.maneuver)

    def body_out(self, seq, data, pid):
        now = self.state.now
        self.sample_decision('exit',pid,now)
        history = [r for r in self.timeline[pid] if now-WINDOW_MS<=r['ms']<=now]
        history.extend(self.row(kind,ms,world[pid],(q for q in world.values() if q.team!=world[pid].team))
                       for ms,kind,world in self.world_frames if now-WINDOW_MS<=ms<=now and pid in world)
        order = {'physics_end':0,'decision':1,'physics':2,'exit':3}
        history.sort(key=lambda r:(r['ms'],order[r['kind_of_sample']]))
        self.outs.append(dict(event_id=seq,team=self.state.players[pid].team,carrier=pid,
                              ms=now,crossing=data['crossing'],history=history))

    def result(self, carrier_events):
        body = {row['event_id'] for row in carrier_events if row['kind']=='carrier'}
        retired, hits = set(), []
        # The report wrapper writes some events through the original emitter.
        # Read the committed engine log after integrations and rollbacks.
        for row in self.match.e.log:
            event, data = row['event'], row['data']
            arrow = data.get('arrow')
            release = self.arrows.get(arrow)
            if release is None or event not in ('arrow_inert','arrow_outcome'):
                continue
            if event=='arrow_outcome' and arrow not in retired and data.get('struck') in self.state.players:
                hits.append(self.timing(release['team'],row) | dict(
                    arrow=arrow,struck=data['struck'],outcome=data['outcome']))
            if event=='arrow_inert' and data.get('refunded'):
                release['refunded'] = True
            retired.add(arrow)
        return dict(releases=self.releases,hits=hits,freezes=self.freezes,periods=self.periods,
                    body_outs=[row for row in self.outs if row['event_id'] in body])
