"""RB engine driver; reuses Native's unchanged athlete decision implementation."""
from native.port import NativePort,body
from dataclasses import dataclass,fields
from native import cognition as C
from .authorities import CREW

@dataclass(frozen=True)
class RulebookView(C.AthleteView):
    rb3_handoff_block_enabled: bool = False
    rb3_carrier_moves_enabled: bool = False
    ball_material: tuple | None = None        # RB-3.21 public: the ball material (k, h, e, a_roll) when the material model is on
    handed_by: tuple | None = None            # RB-3.20b own memory: (teammate who handed me the ball I hold, ms ago)
    rb319: str = ''                           # RB-3.19 public team instruction: enabled ball-in-play steps ('' = off)
    status_indicators: tuple = ()
    freezes_left: int | None = None
    officials: tuple = CREW
    # RB-3.6 (native-rb/3 only; None elsewhere): public team instruction and own-body memory
    defender_baseline: tuple | None = None   # (enabled, mark_distance_m, ball_leash_m)
    own_zone_exit_ms_ago: int | None = None  # live ms since I last left my own Keeper Zone
    own_control_ms: int | None = None         # RB-3.12 own body: ms since I gained control of the ball (None if I do not hold it)
    mate_zone_ms: tuple = ()                  # RB-3.12 public: (teammate id, live ms in the zone he attacks) for teammates inside it
    pass_release_ms: int = 250                # RB-3.14 compatibility spelling for own_release_ms
    own_release_ms: int | None = None          # RB/3 own unrestrained pass/shot delay (one source: port own_release_ms)
    body_reach: tuple = ()                    # Public arm reach (half span), keyed by player id; read only for perceived players
    body_height: tuple = ()                   # RB-3.15 public body size: (player id, height m); read only for perceived players
    snap_hold: bool = False                   # RB-3.13 public: the snap hold is in force (no arrow may be released)
    formation: tuple | None = None            # RB-3.9a public: (snapper, receiver, receiver_x, receiver_y, my_spot_x, my_spot_y)

from .config import RulebookConfig

class RulebookPort(NativePort):
    def __init__(self,seed=1,config=None,policies=None,plumbing=True,rosters=None):
        self.learned_values = None
        path = getattr(config,'drill_values_path',None)
        if path is not None:
            from native.learned_values import read_model

            self.learned_values = read_model(path,config.drill_values_sha256)
        super().__init__(seed,config or RulebookConfig(),policies,plumbing,rosters=rosters)
        self.setup={p.id:(abs(p.x-self.m.s.ends[p.team]),p.y) for p in self.m.s.players.values()}
        self.last_reset_period=1
        self.m.e.rb_port=self
        if self.attr:
            self.m.e.rb_designated={team:{role:tuple(q.id for q in self.m.s.players.values() if q.team==team and q.role==role)
                                         for role in ('keeper','archer')} for team in ('A','B')}
        for team in ("A","B"):
            bench=next(p for p in self.m.s.players.values() if p.team==team and not p.active and p.role=='field')
            assert self.m.e.rb_substitute(None,bench.id,setup=True)
            if self.attr:
                reserve=next(p for p in self.m.s.players.values() if p.team==team and not p.active and p.role=='keeper')
                self.m.e.rb_reserves[team]=reserve.id
        self.platform_motor(0)
        if self.config.version == 'native-rb/3' and self.config.rb3_handoff_block_enabled:
            from .handoff_block import HandoffBlock
            self.rb317 = HandoffBlock(self)
        if self.config.version == 'native-rb/3' and self.config.rb3_carrier_moves_enabled:
            from .carrier_moves import CarrierMoves
            self.rb318 = CarrierMoves(self)
        if getattr(self.config, 'fatigue_rotation', False):
            from .fatigue_rotation import FatigueRotation
            if self.config.rotation_rhythm == 'PLANNED':
                from .planned_rotation import PlannedRotation

                self.rotation = PlannedRotation(self, rosters)
            else:
                self.rotation = FatigueRotation(self, rosters)

    @property
    def intermission_pending(self):return self.m.e.rb_pause is not None

    def advance_intermission(self):
        e=self.m.e
        rotation = getattr(self, 'rotation', None)
        if rotation:
            s = e.s
            now, live, active = s.now, s.live_ms, {p.id for p in s.players.values() if p.active}
        e.elapse(e.rb_pause['until']-self.m.s.now)
        if rotation:
            rotation.advance(now, live, active)
        if self.last_reset_period!=self.m.s.period:
            # PLACEHOLDER procedural reset: reuse legal initial scatter, no formation.
            for p in self.m.s.players.values():
                if p.role=='archer':continue
                depth,y=self.setup[p.id];p.x=self.m.s.ends[p.team]+self.m.s.attack_sign(p.team)*depth;p.y=y
                p.z=p.vx=p.vy=p.vz=0.;p.target=(p.x,p.y)
            self.move.clear();self.pending.clear();self.keeper_intents.clear()
            self.platform_motor(0);self.last_reset_period=self.m.s.period

    def step(self):
        actions = getattr(self, 'rb317', None)
        moves = getattr(self, 'rb318', None)
        if self.intermission_pending:
            if actions:
                actions.update_blocks()
            self.advance_intermission()
            return
        e=self.m.e;s=self.m.s
        rotation = getattr(self, 'rotation', None)
        if rotation:
            rotation.rotate()
            now, live, active = s.now, s.live_ms, {p.id for p in s.players.values() if p.active}
        if s.phase==self.types.Phase.DEAD:
            for team in ('A','B'):
                if e.rb_timeout(team):
                    # Yield a positive dead-time step; the driver then consumes
                    # the remaining official pause and resets only its watchdog.
                    e.elapse(1)
                    if rotation:
                        rotation.advance(now, live, active)
                    return
        if s.phase==self.types.Phase.OPENING:e.rb_hunt_release()
        self.m.rb_previous_positions={p.id:(p.x,p.y,p.z) for p in s.players.values()}
        if self.config.version=='native-rb/3':e.rb_hold_step(self) # RB-3.10 snap hold
        if moves:
            moves.update()
        if actions:
            actions.update_blocks()
        super().step()
        if actions:
            actions.update_blocks(steer=False)
        if moves:
            moves.update(execute=False)
        if rotation:
            rotation.advance(now, live, active)
            rotation.rotate()
        if self.config.version=='native-rb/3':e.rb_form_restart() # RB-3.9a scrimmage formation

    def fill_cover(self):
        self.m.e.rb_fill_slots()

    def assert_invariants(self):
        self.m.e.assert_invariants()
        assert all(sum(p.team==team for p in self.m.s.players.values())==22 for team in ('A','B'))
        assert 0<=self.m.s.tackle_count<=1

    def capture(self,now):
        super().capture(now)
        if self.prism_core:
            self.capture_core_metadata(now)
            return
        if not hasattr(self,'indicator_frames'):self.indicator_frames={}
        if self.individuation and not hasattr(self, 'visible_bodies'):
            self.visible_bodies = {}
        for pid,frames in self.frames.items():
            f=frames[-1]
            if f.captured_ms!=now:continue
            visible={t.entity for t in f.tracks}|{pid}
            self.indicator_frames[f.frame_id]=tuple((q.id,'red' if q.frozen(now) else 'amber' if now<=q.immune_until else 'off') for q in self.m.s.players.values() if q.id in visible)

            if self.individuation:
                self.visible_bodies[f.frame_id] = tuple(
                    (q.id, round(q.a.reach, 4), round(q.a.height, 4))
                    for q in self.m.s.players.values() if q.id in visible)
        keep={f.frame_id for frames in self.frames.values() for f in frames}
        self.indicator_frames={i:v for i,v in self.indicator_frames.items() if i in keep}
        if self.individuation:
            self.visible_bodies = {i:v for i,v in self.visible_bodies.items() if i in keep}

    def capture_core_metadata(self, now):
        """Read each public size and status once per sensing tick."""
        if not hasattr(self, 'indicator_frames'):
            self.indicator_frames = {}
            self.visible_bodies = {}
        metadata = {
            q.id: ('red' if q.frozen(now) else 'amber' if now <= q.immune_until else 'off',
                   round(q.a.reach, 4), round(q.a.height, 4))
            for q in self.m.s.players.values() if q.active
        }
        for pid, frames in self.frames.items():
            f = frames[-1]
            if f.captured_ms != now:
                continue
            ids = sorted({t.entity for t in f.tracks if t.entity in metadata} | {pid})
            self.indicator_frames[f.frame_id] = tuple((who,metadata[who][0]) for who in ids)
            self.visible_bodies[f.frame_id] = tuple((who,*metadata[who][1:]) for who in ids)
        cutoff = now - 21*self.config.sense_ms
        for store in (self.indicator_frames, self.visible_bodies):
            if len(store) > 500:
                for frame_id in tuple(store):
                    if int(frame_id.split('/',2)[1]) < cutoff:
                        del store[frame_id]

    def view(self,pid,now,bench_role=None):
        v,b=super().view(pid,now,bench_role)
        if v is None:return v,b
        f=next((f for f in reversed(self.frames.get(pid,())) if f.captured_ms<=now-self.config.latency_ms),None)
        states=self.indicator_frames.get(f.frame_id,()) if f and hasattr(self,'indicator_frames') else ()
        extra={}
        if self.config.version=='native-rb/3':
            c=self.config;exits=getattr(self.m.e,'rb35',{}).get('own_exit',{})
            extra=dict(defender_baseline=(c.defender_baseline,c.defender_mark_distance_m,c.defender_ball_leash_m),
                       own_zone_exit_ms_ago=self.m.s.live_ms-exits[pid] if pid in exits else None,
                       rb3_handoff_block_enabled=c.rb3_handoff_block_enabled)
            extra['rb3_carrier_moves_enabled'] = c.rb3_carrier_moves_enabled
            extra['rb319'] = c.rb319_parts if c.rb319_ball_in_play_enabled else ''
            extra['ball_material'] = (c.rb321_ball_drag_k, c.rb321_ball_bounce_h, c.rb321_ball_restitution, c.rb321_ball_roll_decel) if c.rb321_ball_material_enabled else None
            hb_ = getattr(self, 'rb317', None); got_ = hb_.last_handoff.get(pid) if hb_ is not None else None
            extra['handed_by'] = (got_[0], self.m.s.now - got_[1]) if got_ and self.m.s.ball.carrier == pid else None
            r=self.m.s.restart;fm=r.rs.get('formation') if r is not None and hasattr(r,'rs') else None
            extra['formation']=(fm['snapper'],fm['receiver'],fm['receiver_xy'][0],fm['receiver_xy'][1],*fm['spots'].get(pid,(None,None))) if fm else None
            sb=self.m.s.ball
            extra['own_control_ms']=self.m.s.now-sb.control_time if sb.carrier==pid else None
            me_=self.m.s.players[pid];e_=self.m.e;res=getattr(e_,'residence',{});covered=self.m.s.own_zone(self.m.s.other(me_.team)) if e_.possession.pp==me_.team else None
            extra['mate_zone_ms']=tuple(sorted((q.id,self.m.s.live_ms-res[q.id]) for q in self.m.s.players.values()
                                               if covered is not None and q.active and q.team==me_.team and q.id!=pid and q.role=='field'
                                               and q.id in res and e_.zone(q.x,q.y)==covered)) if not self.individuation and covered is not None else ()
            hold=getattr(self.m.e,'rb310_hold',None);extra['snap_hold']=bool(hold)
            extra['own_release_ms'] = extra['pass_release_ms'] = self.own_release_ms(me_)
            if self.individuation:
                sizes = getattr(self, 'visible_bodies', {}).get(f.frame_id, ()) if f else ()
                kept = {t.entity for t in v.tracks} | {pid}
                extra['body_reach'] = tuple(sorted((who, reach) for who, reach, _ in sizes if who in kept))
                extra['body_height'] = tuple(sorted((who, height) for who, _, height in sizes if who in kept))
                states = tuple(row for row in states if row[0] in kept)
                if v.role == 'archer':
                    extra['freezes_left'] = max(0, 5 - self.m.e.rb.quotas[v.team]['freezes'])
            else:
                extra['body_reach']=tuple(sorted((q.id,round(q.a.reach,4)) for q in self.m.s.players.values() if q.active))
                extra['body_height']=tuple(sorted((q.id,round(q.a.height,4)) for q in self.m.s.players.values() if q.active))
            if fm is None and hold:   # RB-3.11: the designated receiver stays public during the snap hold (until the catch)
                extra['formation']=(hold['snapper'],hold['receiver'],hold['receiver_xy'][0],hold['receiver_xy'][1],None,None)
        return RulebookView(**{f.name:getattr(v,f.name) for f in fields(C.AthleteView)},status_indicators=states,**extra),b

    def _submit_intent(self,intent):
        p=self.m.s.players.get(intent.athlete)
        if self.intermission_pending:return {'status':'rejected','reason':'official_pause'}
        if p and not self.m.e.rb_can_enter(p):return {'status':'rejected','reason':'ineligible'}
        recovery_move=bool(p and intent.kind in ('position','restart_position','pursue','search') and intent.aim and self.m.s.attack_sign(p.team)*(p.x-intent.aim[0])>0)
        if p and self.m.e.rb_recovery_blocked(p) and not recovery_move:
            return {'status':'rejected','reason':'freeze_recovery'}
        return super()._submit_intent(intent)

    def archer_motor(self):
        m,s=self.m,self.m.s
        for pid,pend in list(self.pending.items()):
            if pend['cmd'].intent.kind!='draw_release' or s.now<pend['due']:continue
            p=s.players[pid]
            if pend['period']!=s.period or not p.eligible(s.now):self.resolve(pid,'interrupted');continue
            if 'release_intent' not in pend:continue
            i=pend['release_intent'];age=(s.now-i.decided_ms)/1000;vx,vy=i.aim_vel or (0,0)
            target=(i.aim[0]+vx*age,i.aim[1]+vy*age,1.6)
            ans=self.geom.ballistic((p.x,p.y,p.z+.72*p.a.height),target,self.config.arrow_speed,9.81)
            if ans is None:self.resolve(pid,'rejected_geometry');continue
            velocity = ans[0]
            if self.individuation:
                from native.individuation import yaw_velocity
                velocity = yaw_velocity(velocity, m.rng['arrow'].uniform(-1., 1.) * (1 - p.a.archery_accuracy))
            ok=m.e.shoot_arrow(pid,i.target,velocity);self.resolve(pid,'arrow_released' if ok else 'rejected_by_engine')

    @staticmethod
    def view_from_json(payload):
        from copy import deepcopy
        data=deepcopy(payload);status=data['view'].pop('status_indicators',());officials=data['view'].pop('officials',CREW)
        baseline=data['view'].pop('defender_baseline',None);exit_ago=data['view'].pop('own_zone_exit_ms_ago',None);form=data['view'].pop('formation',None);ctl=data['view'].pop('own_control_ms',None);mz=data['view'].pop('mate_zone_ms',());sh=data['view'].pop('snap_hold',False);prm=data['view'].pop('pass_release_ms',250);br=data['view'].pop('body_reach',())
        own_release = data['view'].pop('own_release_ms', None);bh=data['view'].pop('body_height',())
        actions = data['view'].pop('rb3_handoff_block_enabled', False)
        moves = data['view'].pop('rb3_carrier_moves_enabled', False)
        r319 = data['view'].pop('rb319', '')
        hby = data['view'].pop('handed_by', None)
        bmat = data['view'].pop('ball_material', None)
        freezes_left = data['view'].pop('freezes_left', None)
        v,b=C.view_from_json(data)
        return RulebookView(**{f.name:getattr(v,f.name) for f in fields(C.AthleteView)},status_indicators=tuple(tuple(x) for x in status),freezes_left=freezes_left,officials=tuple(officials),
                            defender_baseline=tuple(baseline) if baseline is not None else None,own_zone_exit_ms_ago=exit_ago,formation=tuple(form) if form is not None else None,own_control_ms=ctl,snap_hold=sh,pass_release_ms=prm,own_release_ms=own_release,body_height=tuple(tuple(x) for x in bh),body_reach=tuple(tuple(x) for x in br),mate_zone_ms=tuple(tuple(x) for x in mz),rb3_handoff_block_enabled=actions,
                            rb3_carrier_moves_enabled=moves,rb319=r319,handed_by=tuple(hby) if hby is not None else None,ball_material=tuple(bmat) if bmat is not None else None),b
