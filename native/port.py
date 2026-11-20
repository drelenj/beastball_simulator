"""Native observation -> belief -> intent -> ingress -> motor -> physics path.
B1 moving-release ownership contracts are retained; accepted M1 files untouched.
"""
from collections import Counter, deque
from dataclasses import dataclass, asdict, replace
import hashlib
import json
import math
import random
from b1.communication import DeliveryModel, TeamTransport, receive_messages
from b1.emergence_intents import BallCourseBelief, AthleteBody, plan_keeper_motor
from . import cognition as C
from .config import NativeConfig, is_v3, is_attr
from .roster import INERT_RATINGS, engine_order, mapped_values, max_throw_speed, throw_error_base_deg, sensor_noise_scale
from .perception import visibility
from .substrate import build_core
from .restart_metric import RestartMetric


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),default=str).encode()).hexdigest()

@dataclass(frozen=True)
class ObservationFrame:
    frame_id: str
    captured_ms: int
    athlete: str
    tracks: tuple
    ball_course: BallCourseBelief | None
    signals: C.Signals
    restart: tuple | None
    contestant: str | None
    hunt: bool
    hunt_cleared: bool


def body(p):
    a=p.a
    return AthleteBody(p.id,p.team,p.x,p.y,p.z,p.vx,p.vy,p.vz,a.height,a.reach,a.acceleration,a.braking,a.maximum_speed,a.jump_height)


class NativePort:
    def __init__(self,seed=1,config=None,policies=None,plumbing=True,rosters=None):
        self.config=config or NativeConfig()
        self.CO=build_core(self.config);co=self.CO;cfg=self.config
        self.types,self.geom=co.types,co.geometry
        make_roster=co.match.make_roster
        self.attr=is_attr(cfg)
        self.behavior_digest=cfg.digest
        if self.attr:
            if not rosters or set(rosters)!=set(('A','B')):raise ValueError('ATTR-1 requires A and B rosters')
            if tuple(rosters[t].digest for t in ('A','B'))!=cfg.roster_digests:raise ValueError('roster digest/config mismatch')
            if cfg.version=='native-rb/3':
                # Full config/roster digest is retained in the result. Gameplay hashes
                # use only consumed ratings, so changing stored inert fields has no effect.
                active={t:[(a.source_id,a.role,tuple((k,v) for k,v in a.values if k not in INERT_RATINGS))
                           for a in rosters[t].athletes] for t in ('A','B')}
                config_record=cfg.record();config_record['roster_digests']=('behavior-only','behavior-only')
                self.behavior_digest=digest((config_record,active))
            def attr_validate(a):
                assert 1.4<=a.height<=3.6576 and 0<=a.maximum_speed<=44.704 and a.mass>0
                assert a.acceleration>=0 and a.braking>=0
                for key in ('strength','agility','endurance','balance','contact_resistance','tackling','blocking','ball_handling','passing','kicking','catching','awareness','archery_accuracy','keeper_skill'):
                    assert 0<=getattr(a,key)<=1,(key,getattr(a,key))
            co.types.Attributes.validate=attr_validate
        def uniform(team,archetype,rng):
            players=make_roster(team,archetype,rng)
            if self.attr:
                ordered=engine_order(rosters[team]);result={}
                for slot,(old,record) in enumerate(zip(players.values(),ordered)):
                    old.id=f'{team}:{record.source_id}';old.slot=slot;old.role=record.role;old.active=slot<12
                    for key,value in mapped_values(record).items():setattr(old.a,key,value)
                    raw=dict(record.values)
                    if cfg.version == 'native-rb/3':
                        old.a.standing_reach_m = raw.get('standing_reach_m')
                    old.native_source_id=record.source_id
                    old.native_max_throw_speed=max_throw_speed(raw['throw_power'])
                    old.native_throw_error_base_deg=throw_error_base_deg(raw['throw_accuracy'])
                    old.native_sensor_noise_scale=sensor_noise_scale(raw['awareness'])
                    old.fatigue=1.;old.a.validate();result[old.id]=old
                return result
            for p in players.values():
                for key in ('strength','agility','endurance','balance','contact_resistance','tackling','blocking','ball_handling','passing','catching','awareness','archery_accuracy','keeper_skill'):
                    setattr(p.a,key,cfg.ratings)
                p.a.kicking=0. # inert legacy storage; never read by Native commands
                for key,value in cfg.body_standards:setattr(p.a,key,value)
                # PLACEHOLDER legal initial scatter, no positional slots/tactical roles.
                p.x=rng.uniform(6,44) if team=='A' else rng.uniform(56,94);p.y=rng.uniform(6,94)
                p.fatigue=1.;p.target=(p.x,p.y)
            return players
        co.match.make_roster=uniform
        pocket=dict(cfg.pocket_settings)
        # Pocket's convenience roster override resets abilities; direct core config avoids it.
        settings=dict(seed=seed,period_seconds=cfg.period_seconds,regulation_periods=cfg.periods,
                      overtime_seconds=cfg.overtime_seconds,dt_ms=cfg.dt_ms,ruleset='1.0.2',
                      assumptions=dict(cfg.physical_assumptions),
                      native=cfg.record())
        self.m=m=co.match.Match(settings)
        m.cfg['pocket']=pocket;m.e.pocket=pocket;m.e.c2_tackles=True;m.e.c2_inbound=False;m.e.c2_occ=False;m.e.mark_d=cfg.marking_distance
        m.s.keeper_zone_radius=cfg.zone_radius
        for pol in m.pol.values():pol.pocket=pocket
        self.seed=seed;self.rules=m.e.possession;self.settings=settings
        self.v3=is_v3(cfg)
        if self.attr:
            from types import MethodType
            old_release,old_restart=m.e.release,m.e.restart_release
            def within(pid,velocity):
                return math.sqrt(sum(v*v for v in velocity))<=m.s.players[pid].native_max_throw_speed+1e-7
            def attr_release(engine,pid,velocity,*args,**kwargs):
                return old_release(pid,velocity,*args,**kwargs) if within(pid,velocity) else False
            def attr_restart(engine,pid,velocity,*args,**kwargs):
                return old_restart(pid,velocity,*args,**kwargs) if within(pid,velocity) else False
            m.e.release=MethodType(attr_release,m.e);m.e.restart_release=MethodType(attr_restart,m.e)
        self.restart_metric=RestartMetric() # read-only measurement (FAB-1c)
        self.arrow_speed=cfg.arrow_speed if self.v3 else 29. # ATTR and v0/3 are fixed/derived in config; v0/2 retained
        self.pending,self.move,self.feedback={}, {}, {}
        self.outcomes=[];self.intents=[];self.decisions=Counter();self.admissions=Counter()
        self.frames={};self.memory={};self.history={};self.gaze={};self.next_frame={};self.course_beliefs={}
        self.streams={pid:random.Random(f'native/sensor/{seed}/{pid}') for pid in m.s.players}
        self.communication=TeamTransport(seed,{p.id:p.team for p in m.s.players.values()},DeliveryModel()) if plumbing else None
        from .emergence.params import DEFAULT
        self.policies={team:(policies or {}).get(team,DEFAULT) for team in ('A','B')}
        self.command_log=[];self.release_log=[];self.keeper_intents={}
        self.calls={};self.observation_count=0;self.next_sense=0
        self.trace=hashlib.sha256();self.trace.update(self.behavior_digest.encode());self.trace.update(digest({t:p.as_dict() for t,p in self.policies.items()}).encode())
        self.hook_calls=Counter()
        m.carrier_decision=self.ball_motor;m.arrow_decisions=self.archer_motor;m.c4c_keepers=self.keeper_motor
        m.update_archers=self.platform_motor;m.auto_substitutions=lambda:None
        m.c4c2_targets=m.route_receiver=lambda targets:None
        m.c4c2_inbound=lambda *a,**k:None
        m.penalty_targets=lambda:self.move.copy()
        m.c3_withhold=lambda *a:False
        m.c3_fix_contain=False;m.c3_fix_descent=False
        m.native_wrap_authorized=lambda p,q:bool(getattr(p,'native_intent',None) and p.native_intent.contact=='wrap' and p.native_intent.target==q.id)
        if self.v3:
            # FAB-1b: hold mode and escape effort are athlete intents, never engine controllers.
            def contact(p,target=None):
                i=getattr(p,'native_intent',None)
                if i is None:return None
                if cfg.version=='native-rb/3' and (m.s.now-i.decided_ms>=cfg.decision_ms or i.period!=m.s.period or
                        (i.contact in ('wrap','takedown') and (i.target!=target or m.s.ball.carrier!=target))):return None
                return i.contact
            m.native_wrap_authorized=lambda p,q:bool(contact(p,q.id) in ('wrap','takedown') and p.native_intent.target==q.id)
            m.c3_contain=lambda d,car:contact(d,car.id)!='takedown'
            m.c3_escape_effort=lambda car,windup:1. if windup is None and car.id not in m.c3_descent and contact(car)=='run_through' and car.native_intent.kind=='carry' else 0.
        for pol in m.pol.values():pol.t=replace(pol.t,pace=(1/.9 if self.attr else 1.))
        # Pure policies cannot call back into retired controllers.
        def forbidden(*a,**k):raise RuntimeError('retired tactical controller reached')
        for name in ('carrier_decision','arrow_decisions','targets_dead','update_archers','c4c2_decide','pocket_decide'):
            setattr(type(m),name,forbidden)
        for pol in m.pol.values():pol.targets=lambda state:self.move.copy();pol.pass_choice=forbidden;pol.pass_ranked=forbidden
        self.platform_motor(0)
        for q in m.s.quivers.values():q.allocation=cfg.arrows;q.loaded=cfg.arrows
        self.verify_effective()

    def verify_effective(self):
        cfg,m=self.config,self.m
        effective=dict(periods=m.s.regulation_periods,period_seconds=m.s.period_seconds,
                       overtime_seconds=m.s.overtime_seconds,play_clock_ms=m.e.play_ms,
                       marking_distance=m.e.mark_d,zone_radius=m.s.keeper_zone_radius,
                       goal_radius=cfg.goal_radius,platform_height=cfg.platform_height,
                       platform_setback=cfg.platform_setback,catch_model=cfg.catch_model,m2=cfg.m2)
        assert all(effective[k]==cfg.record()[k] for k in effective)
        assert dict(cfg.physical_assumptions)==self.m.assume
        assert dict(cfg.pocket_settings)==self.m.e.pocket
        effective['physical_assumptions']=dict(self.m.assume)
        effective['pocket_settings']=dict(self.m.e.pocket)
        assert self.geom.legal_goal(50.,2.8,.1) and not self.geom.legal_goal(50.,3.01,.1)
        for p in m.s.players.values():
            assert self.attr or all(getattr(p.a,key)==value for key,value in cfg.body_standards)
            if p.role=='archer' and p.active:
                assert p.x in (-5.,105.) and p.y==50. and p.z==5.
                assert p.facing==(float(m.s.attack_sign(p.team)),0.), (p.id,p.facing,m.s.attack_sign(p.team))
        self.effective=effective
        return effective

    def platform_motor(self,ms):
        for p in self.m.s.players.values():
            if p.role=='archer' and p.active:
                p.x=self.m.s.ends[p.team]+(-self.config.platform_setback if self.m.s.ends[p.team]==0 else self.config.platform_setback)
                p.y=50.;p.z=self.config.platform_height;p.vx=p.vy=p.vz=0.;p.facing=(float(self.m.s.attack_sign(p.team)),0.)

    def active_ids(self):
        return sorted(p.id for p in self.m.s.players.values() if p.active and p.eligible(self.m.s.now))

    def capture(self,now):
        s=self.m.s;e=self.m.e;e.native_sync();rs=e.possession.public();r=s.restart
        restart=(r.native_id,r.kind,r.team,r.x,r.y,*r.taker_spot,r.taker,r.rs.get('snapper'),r.rs.get('tackler'),r.created_at,r.ready_at is not None) if r else None
        ps=[p for p in s.players.values() if p.active]
        blockers=[(q.id,q.x,q.y,q.z,q.z+q.a.height,q.radius) for q in ps if q.role!='archer']
        ids=self.active_ids()
        raw_entities=[(q.id,q.team,q.role,q.x,q.y,q.z) for q in ps if q.role!='archer']
        b=s.ball;raw_entities.append((C.BALL,'ball','ball',b.x,b.y,b.z))
        mask=visibility([(pid,s.players[pid].x,s.players[pid].y,s.players[pid].z+.72*s.players[pid].a.height,s.players[pid].role=='archer') for pid in ids],
                        [(eid,x,y,z) for eid,team,role,x,y,z in raw_entities],blockers)
        for vi,pid in enumerate(ids):
            p=s.players[pid];rng=self.streams[pid]
            tracks=[];course=None
            entities=raw_entities
            facing=math.atan2(p.facing[1],p.facing[0])
            # PLACEHOLDER sensor: bounded field cone + body-cylinder occlusion;
            # platform vision has no occlusion; positions noisy, velocities from own reads.
            for ei,(eid,team,role,x,y,z) in enumerate(entities):
                if eid==pid:continue
                dx,dy=x-p.x,y-p.y;d=math.hypot(dx,dy)
                off=(math.atan2(dy,dx)-facing+math.pi)%(2*math.pi)-math.pi
                if p.role!='archer' and abs(off)>math.radians(120) and d>2:continue
                if not mask[vi,ei]:continue
                sigma=(.04+.002*d)*(p.native_sensor_noise_scale if self.attr else 1.)
                ox,oy,oz=x+rng.gauss(0,sigma),y+rng.gauss(0,sigma),max(.1075,z+rng.gauss(0,.04))
                old=self.history.get((pid,eid));vx=vy=vz=0.
                if old and now>old[0]:
                    dt=(now-old[0])/1000;vx,vy,vz=((ox-old[1])/dt,(oy-old[2])/dt,(oz-old[3])/dt)
                self.history[pid,eid]=(now,ox,oy,oz)
                tracks.append(C.Track(eid,team,role,round(ox,3),round(oy,3),round(vx,3),round(vy,3),now))
                if eid==C.BALL:course=BallCourseBelief(f'course/{pid}/{now}',now,now+self.config.latency_ms,ox,oy,oz,vx,vy,vz)
            call=self.calls.get(p.team)
            sig=C.Signals(s.phase.value,s.period,s.game_ms,s.possession_ms,s.score[p.team],s.score[s.other(p.team)],
                          r.team if r else None,(r.x,r.y) if r else None,bool(r and r.taker==pid),
                          rs.passive_team,rs.direct_team,rs.direct_holder,rs.contested,rs.ball_status,
                          tuple(q.id for q in ps if q.frozen(now) or now<=q.immune_until),call[:4] if call and call[4]>=now and call[0]!=pid else None,
                          tackle_count=s.tackle_count)
            frame=ObservationFrame(f'native/{now}/{pid}',now,pid,tuple(tracks),course,sig,restart,e.hunt_claims.get(p.team),s.phase==self.types.Phase.OPENING and not e.hunt_cleared,e.hunt_cleared)
            self.frames.setdefault(pid,deque()).append(frame)
            while len(self.frames[pid])>20:self.frames[pid].popleft()

    def view(self,pid,now,bench_role=None):
        p=self.m.s.players[pid]
        self.rules=self.m.e.possession
        frames=self.frames.get(pid,())
        f=next((f for f in reversed(frames) if f.captured_ms<=now-self.config.latency_ms),None)
        if f is None and bench_role is None:return None,None
        if f is None or bench_role is not None:
            # A cover claim receives current public officiating through its view.
            # A returned substitute's old on-field visual frame is not a current
            # period signal and supplies no fresh ball/athlete observations.
            rs=self.rules.public();s=self.m.s
            sig=C.Signals(s.phase.value,s.period,s.game_ms,s.possession_ms,s.score[p.team],s.score[s.other(p.team)],None,None,False)
            f=ObservationFrame(f'native/{now}/{pid}/bench',now,pid,(),None,sig,None,None,False,self.m.e.hunt_cleared)
        mem=self.memory.setdefault(pid,{})
        mem.update({t.entity:t for t in f.tracks})
        tracks=tuple(t for t in sorted(mem.values(),key=lambda t:t.entity) if now-t.captured_ms<=2000)
        course=f.ball_course
        # No sensor fallback: own old course can go stale, or be absent.
        self.course_beliefs[pid]=course
        self.observation_count+=1;oid=f'native/{now}/{pid}/obs/{self.observation_count}'
        pend=self.pending.get(pid);rs=f.signals
        holds=self.m.s.ball.carrier==pid # exact own proprioception, SELF-1
        messages=self.communication.intake(pid,now) if self.communication else ()
        view=C.AthleteView(oid,pid,p.team,p.role,p.slot,now,p.x,p.y,holds,self.m.s.attack_sign(p.team),self.m.s.ends[p.team],tracks,rs,
                           pending_command_id=pend['cmd'].command_id if pend else None,
                           pending_release_ms=pend['due'] if pend else None,
                           pending_kind=pend['cmd'].intent.kind if pend else None,pending_target=pend['cmd'].intent.target if pend else None,
                           arrows_loaded=self.m.s.quivers[p.team].allocation-self.m.s.quivers[p.team].spent if p.role=='archer' else None,
                           last_release_ms=self.m.s.quivers[p.team].last_release if p.role=='archer' else None,
                           posture=p.posture,policy=self.policies[p.team],body=body(p),restart=f.restart,
                           contestant=f.contestant,hunt=f.hunt,bench_role=bench_role,dribble_used=bool(self.m.e.dribbles.get(pid)),
                           zone_elapsed_ms=self.m.s.live_ms-self.m.e.residence.get(pid,self.m.s.live_ms),
                           max_throw_speed=p.native_max_throw_speed if self.attr else 40.,own_mass_kg=p.a.mass if self.attr else None,
                           own_skills=tuple((key,getattr(p.a,key)) for key in ('strength','agility','endurance','balance','contact_resistance','tackling','blocking','ball_handling','passing','catching','awareness','archery_accuracy','keeper_skill')) if self.attr else (),
                           hunt_cleared=f.hunt_cleared,messages=messages,ownership_enabled=True,ball_course=course,
                           own_restraint=self.m.c3_rho(p,'pass'),tuck_fraction=self.m.assume['tuck_after_delay_frac'],zone_radius=self.config.zone_radius,
                           **(self.own_contact(p) if self.v3 else {}))
        belief=C.BeliefState(oid+'/belief',oid,tracks,tuple(self.feedback.pop(pid,())),2000,None,course,receive_messages(view))
        return view,belief

    def own_contact(self,p):
        """SELF-1 own-body knowledge only: holds on me, my balance, whom I hold."""
        holds=self.m.c3_holds
        return dict(cognition=self.config.version if self.config.version=='native-rb/3' else 'native-v0/3' if self.attr else self.config.version,
                    own_held=sum(1 for (a,t),h in holds.items() if t==p.id and h['g']>0),
                    own_balance_load=round(min(1.,self.m.c3_bal(p)),4),
                    own_hold_target=next((t for (a,t),h in sorted(holds.items()) if a==p.id),None))

    def submit(self,intent):
        admission=self._submit_intent(intent)
        self.trace.update(digest([intent.intent_id,admission['status'],admission.get('reason')]).encode())
        self.admissions[admission['status']]+=1
        return admission

    def _submit_intent(self,intent):
        m,s,e=self.m,self.m.s,self.m.e;p=s.players.get(intent.athlete);kind=intent.kind
        if p is None or intent.decided_ms!=s.now:return {'status':'rejected','reason':'actor_time'}
        if intent.period is not None and intent.period!=s.period:return {'status':'rejected','reason':'stale_period'}
        p.native_intent=intent
        self.intents.append(intent);self.decisions[kind]+=1
        row=[intent.intent_id,kind,intent.target,intent.aim,intent.speed,intent.height,intent.record_id,intent.contact,
             (intent.auxiliary.intent_id,intent.auxiliary.kind,intent.auxiliary.belief_revision) if intent.auxiliary else None]
        self.trace.update(digest(row).encode())
        if kind=='substitute_claim':
            vacancy=next((v for v in e.vacancies if v[0]==p.team),None)
            if p.active or not vacancy or not p.available or p.disqualified or p.exclusion_ms>0:return {'status':'rejected','reason':'ineligible_cover'}
            if self.attr and p.role!=vacancy[1]:return {'status':'rejected','reason':'fixed_role'}
            _,role,slot,x,y=vacancy;p.active=True;p.role=role;p.slot=slot;p.x=x;p.y=y;p.z=0;p.vx=p.vy=p.vz=0
            self.command_log.append(C.MotorCommand(intent.intent_id+'/command',intent,s.now,None,'procedural'))
            e.vacancies.remove(vacancy);e.emit('substitute','native',player=p.id,role=role,intent_id=intent.intent_id);self.platform_motor(0)
            return {'status':'accepted'}
        if not p.active:return {'status':'rejected','reason':'inactive'}
        if kind in ('handoff', 'block'):
            actions = getattr(self, 'rb317', None)
            return actions.submit(p, intent) if actions else {'status': 'rejected', 'reason': 'feature_off'}
        if kind in ('restart_claim','restart_position','restart_pass','restart_wait') and (s.restart is None or intent.record_id!=s.restart.native_id):
            return {'status':'rejected','reason':'stale_restart_record'}
        if kind=='hunt_claim':
            if p.role!='field' or p.team in e.hunt_claims or e.hunt_cleared:return {'status':'rejected','reason':'hunt_closed'}
            self.command_log.append(C.MotorCommand(intent.intent_id+'/command',intent,s.now,None,'procedural'))
            e.hunt_claims[p.team]=p.id;s.opening_contestants=tuple(e.hunt_claims.values())
            e.emit('hunt_claim','native',player=p.id,intent_id=intent.intent_id);return {'status':'accepted'}
        if kind=='restart_claim':
            r=s.restart
            if not r or r.taker or (p.role!='field' and r.rs.get('snapper')!=p.id) or r.team!=p.team:return {'status':'rejected','reason':'claim_closed'}
            if r.rs.get('snapper') not in (None,p.id):return {'status':'rejected','reason':'mandatory_snapper'}
            self.command_log.append(C.MotorCommand(intent.intent_id+'/command',intent,s.now,None,'procedural'))
            r.taker=p.id;e.emit('restart_claim','native',player=p.id,intent_id=intent.intent_id,restart_id=r.native_id)
            return {'status':'accepted'}
        if kind=='keeper_control':
            self.keeper_intents[p.id]=intent
            if self.config.version == 'native-rb/3':
                observed = self.course_beliefs.get(p.id)
                aux = intent.auxiliary
                p.native_keeper_course_ms = (observed.captured_ms if observed and aux
                                             and observed.revision == aux.belief_revision else None)
            self.command_log.append(C.MotorCommand(intent.intent_id+'/command',intent,s.now,None,'keeper'))
            return {'status':'accepted'}
        if kind=='release_arrow':
            pending=self.pending.get(p.id)
            if not pending or pending['cmd'].intent.kind!='draw_release' or intent.related_command_id!=pending['cmd'].command_id or intent.target!=pending['cmd'].intent.target:
                return {'status':'rejected','reason':'stale_draw'}
            pending['release_intent']=intent
            self.command_log.append(C.MotorCommand(intent.intent_id+'/command',intent,s.now,s.now,'bow'))
            return {'status':'accepted'}
        if kind=='abort_draw':
            self.pending.pop(p.id,None);return {'status':'accepted'}
        if kind=='continue_current':return {'status':'accepted' if p.id in self.pending else 'rejected'}
        if kind in ('retain','archer_hold','restart_wait','scan','no_action'):return {'status':'accepted'}
        if kind in ('position','restart_position','carry','pursue','press','mark','support','receive','search','keeper_set','keeper_save') or (kind=='tackle' and self.v3):
            if intent.aim is None:return {'status':'rejected','reason':'missing_aim'}
            self.move[p.id]=intent.aim
            cmd=C.MotorCommand(intent.intent_id+'/command',intent,s.now,None,'locomotion')
            self.command_log.append(cmd);return {'status':'accepted','command':cmd}
        if kind in ('pass','shoot','restart_pass','draw_release','dribble','bounce'):
            if p.id in self.pending:return {'status':'rejected','reason':'resource_busy'}
            if kind not in ('restart_pass','draw_release') and s.ball.carrier!=p.id:return {'status':'rejected','reason':'not_carrier'}
            if intent.aim is None:return {'status':'rejected','reason':'missing_aim'}
            target_height=.1075 if kind in ('bounce','dribble') else intent.height
            origin=(s.ball.x,s.ball.y,s.ball.z) if kind!='draw_release' else (p.x,p.y,p.z+.72*p.a.height)
            target=(*intent.aim,target_height)
            limit=p.native_max_throw_speed if self.attr else 40.
            if kind!='draw_release' and intent.speed>limit+1e-9:return {'status':'rejected','reason':'throw_speed'}
            ans=self.geom.launch_for(origin,target,min(intent.speed,limit),9.81,.015) if kind!='draw_release' else None
            if kind!='draw_release' and ans is None:return {'status':'rejected','reason':'geometry'}
            delay = 600 if kind == 'draw_release' else 250
            if self.config.version == 'native-rb/3' and kind in ('pass', 'shoot'):
                delay = self.own_release_ms(p)
            cmd=C.MotorCommand(intent.intent_id+'/command',intent,s.now,s.now+delay,
                               'bow' if kind=='draw_release' else 'ball',ans[0] if ans else None)
            self.pending[p.id]={'cmd':cmd,'velocity':ans[0] if ans else None,'due':cmd.release_ms,'period':s.period}
            self.command_log.append(cmd)
            if kind=='pass':self.calls[p.team]=(p.id,intent.target,*intent.aim,s.now+2500)
            if kind not in ('draw_release','restart_pass'):self.move[p.id]=(p.x,p.y)
            return {'status':'accepted','command':cmd}
        return {'status':'rejected','reason':'unknown_kind'}

    def own_release_ms(self, player):
        """Unrestrained thrown-pass and shot wind-up on the integer clock."""
        return round(self.m.assume['pass_release_ms'] * (1.35 - .5 * player.a.ball_handling))

    def resolve(self,pid,status):
        p=self.pending.pop(pid,None)
        if p:
            cmd=p['cmd'];o=C.PhysicalOutcome(cmd.command_id+'/outcome',cmd.command_id,status,self.m.s.now)
            self.outcomes.append(o);self.feedback.setdefault(pid,[]).append((o.outcome_id,status+':'+cmd.intent.kind,o.resolved_ms))

    def ball_motor(self):
        m,s,e=self.m,self.m.s,self.m.e
        self.hook_calls['ball_motor']+=1
        for pid,pend in list(self.pending.items()):
            i=pend['cmd'].intent
            if pend['period']!=s.period:self.resolve(pid,'interrupted');continue
            if i.kind=='draw_release':continue
            if i.kind!='restart_pass' and s.ball.carrier!=pid:self.resolve(pid,'interrupted');continue
            if s.now<pend['due']:continue
            p=s.players[pid]
            if i.kind == 'handoff':
                self.rb317.execute_handoff(p, pend)
                continue
            if i.kind=='restart_pass':
                if s.restart is None:self.resolve(pid,'interrupted');continue
                if s.restart.taker!=pid or i.record_id!=s.restart.native_id:self.resolve(pid,'rejected_taker_or_record');continue
                # Release is solely the admitted aim; no true receiver lookup.
                origin=(s.restart.x,s.restart.y,p.hand_height)
            else:origin=(s.ball.x,s.ball.y,s.ball.z)
            ans=self.geom.launch_for(origin,(*i.aim,.1075 if i.kind in ('bounce','dribble') else i.height),i.speed,9.81,.015)
            if ans is None:self.resolve(pid,'rejected_geometry');continue
            old=pend['velocity'];new=ans[0]
            dot=sum(a*b for a,b in zip(old,new));sizes=math.sqrt(sum(x*x for x in old)*sum(x*x for x in new))
            angle=math.degrees(math.acos(max(-1,min(1,dot/max(sizes,1e-9)))))
            if angle>60:self.resolve(pid,'rejected_geometry');continue
            self.release_log.append(dict(command_id=pend['cmd'].command_id,intent_id=i.intent_id,angle=angle,speed=i.speed,height=i.height,target=i.target))
            if i.kind=='restart_pass':
                ok=e.restart_release(pid,new,i.target)
                if not ok and s.restart is not None and s.restart.taker==pid:
                    # Retain this athlete command until legal readiness; procedural deadline still applies.
                    continue
            else:
                # ATTR maps a requested angular SD onto the primitive uniform
                # direction error: half-width = sqrt(3)*SD. Legacy replay keeps
                # its historical Gaussian exactly.
                if self.attr:
                    sd=p.native_throw_error_base_deg*i.speed/67.
                    yaw=math.radians(m.rng['ball'].uniform(-math.sqrt(3)*sd,math.sqrt(3)*sd))
                else:yaw=m.rng['ball'].gauss(0,math.radians((1-.7)*3))
                vx,vy,vz=new;new=(vx*math.cos(yaw)-vy*math.sin(yaw),vx*math.sin(yaw)+vy*math.cos(yaw),vz)
                ok=e.release(pid,new,'shot' if i.kind=='shoot' else 'dribble' if i.kind=='dribble' else 'pass',i.target)
            self.resolve(pid,'released' if ok else 'rejected_by_engine')

    def archer_motor(self):
        m,s=self.m,self.m.s
        for pid,pend in list(self.pending.items()):
            if pend['period']!=s.period:self.resolve(pid,'interrupted');continue
            if pend['cmd'].intent.kind!='draw_release' or s.now<pend['due']:continue
            p=s.players[pid]
            if not p.eligible(s.now):self.resolve(pid,'interrupted');continue
            if 'release_intent' not in pend:continue
            i=pend['release_intent'];age=(s.now-i.decided_ms)/1000
            vx,vy=i.aim_vel or (0,0);target=(i.aim[0]+vx*age,i.aim[1]+vy*age,1.6)
            ans=self.geom.ballistic((p.x,p.y,p.z+.72*p.a.height),target,self.arrow_speed,9.81)
            if ans is None:self.resolve(pid,'rejected_geometry');continue
            ok=m.e.shoot_arrow(pid,i.target,ans[0]);self.resolve(pid,'arrow_released' if ok else 'rejected_by_engine')

    def keeper_motor(self,targets):
        m,s=self.m,self.m.s
        rb3 = self.config.version == 'native-rb/3'
        for p in s.players.values():
            if p.role!='keeper' or not p.active:continue
            if rb3 and s.ball.carrier is None:
                # Restart awards replace the Ball and can reuse its version.
                marks = (s.ball.release_time, getattr(s.ball, 'course_time', -1))
                flight = (s.ball.version, *marks)
                timing = getattr(p, 'native_keeper_flight', None)
                if timing is None or timing[0] != flight:
                    previous = timing[1] if timing else -math.inf
                    started = max((t for t in marks
                                   if previous < t <= s.now and t >= 0), default=s.now)
                    reaction = m.assume['keeper_reaction_s']*(1.3-.6*p.a.awareness)
                    if p.speed > m.assume['keeper_set_mps']:
                        reaction += m.assume['keeper_unset_s']
                    p.native_keeper_flight = (flight, started, started+1000*reaction)
            launch=getattr(p,'c4c_launch',None)
            if launch:
                if p.posture=='airborne' and s.now<launch['t_land']-.5:continue
                m.c4c_land(p,launch)
            plan=getattr(p,'c4c_plan',None)
            if plan and s.now<plan['until']:
                targets[p.id]=plan['target'];continue
            p.c4c_plan=None
            i=self.keeper_intents.get(p.id)
            if i is None or i.auxiliary is None:targets[p.id]=(p.x,p.y);continue
            if s.ball.carrier==p.id:continue
            if rb3 and i.auxiliary.kind == 'save':
                observed_ms = getattr(p, 'native_keeper_course_ms', None)
                if (s.ball.carrier is not None or observed_ms is None or
                        observed_ms < p.native_keeper_flight[1] or
                        s.now+1e-9 < p.native_keeper_flight[2]):
                    targets[p.id] = (p.x, p.y)
                    continue
                # The forecast starts at capture, including both delivery
                # latency and any remaining wait at the motor.
                elapsed = max(0., (s.now-observed_ms)/1000)
                course = tuple((t-elapsed, x, y, z) for t,x,y,z in i.auxiliary.course if t >= elapsed)
                intent = replace(i.auxiliary, course=course)
                cmd = plan_keeper_motor(
                    intent, body(p), now_ms=s.now, gravity=m.assume['gravity'],
                    pushoff_fraction=m.assume['keeper_pushoff_frac'],
                    extension_fraction=m.assume['keeper_extension_frac'],
                    launch_min_s=m.assume['keeper_launch_min_s'],
                    dive_time_s=m.assume['keeper_dive_time_s'],
                    dive_hand_fraction=m.assume['keeper_dive_hand_frac'],
                    reach_factor=m.c4c_reach(p)/p.a.reach, match_lean=True)
            else:
                cmd=plan_keeper_motor(i.auxiliary,body(p),now_ms=s.now,gravity=9.81)
            if cmd.kind in ('hold','move','step','approach'):
                targets[p.id]=cmd.target or (p.x,p.y)
                if cmd.kind in ('step','approach'):p.c4c_plan=dict(kind='step',until=cmd.until_ms,target=cmd.target)
            elif cmd.kind=='launch':
                vx,vy,vz=cmd.impulse;p.vx+=vx;p.vy+=vy;p.vz=vz;p.posture='airborne'
                p.c4c_seen=(s.ball.version,s.now,s.now,False)
                p.c4c_launch=dict(t0=s.now,t_land=cmd.land_ms,off=m.c4c_off(p,cmd.lean,*cmd.direction),lean=cmd.lean,dir=cmd.direction,dive=cmd.lean>=m.assume['keeper_dive_lean'])
            else:targets[p.id]=(p.x,p.y)

    def fill_cover(self):
        e,s=self.m.e,self.m.s
        if s.phase==self.types.Phase.FINAL:return
        for vacancy in list(e.vacancies):
            candidates=sorted(p.id for p in s.players.values() if p.team==vacancy[0] and not p.active and p.available and not p.disqualified and p.exclusion_ms==0 and (not self.attr or p.role==vacancy[1]))
            for pid in candidates:
                v,b=self.view(pid,s.now,bench_role=vacancy[1]);intent,rec=C.decide(v,b)
                if self.submit(intent)['status']=='accepted':break
            else:raise RuntimeError('cover unavailable: '+str([(p.id,p.active,p.disqualified,p.exclusion_ms,p.available) for p in s.players.values() if p.team==vacancy[0]]))

    def step(self):
        m,s,e=self.m,self.m.s,self.m.e;P=self.types.Phase
        before_live=s.live_ms
        previous_carrier=s.ball.carrier
        previous_xy=(s.players[previous_carrier].x,s.players[previous_carrier].y) if previous_carrier else (s.ball.x,s.ball.y)
        if s.phase==P.FINAL:return
        self.ball_motor()
        if s.phase==P.FINAL:return
        self.archer_motor()
        if s.phase==P.FINAL:return
        e.resolve_timers()
        if s.phase==P.FINAL:return
        m.c4c_land_due()
        if s.phase==P.DEAD:
            span=min(self.config.dt_ms,max(1,e.next_deadline()-s.now))
            m.move_players(span,self.move)
            self.platform_motor(0)
            if s.restart and s.restart.taker:e.ready(s.restart.taker)
            e.elapse(span)
            self.ball_motor()
        elif s.phase!=P.FINAL:
            span=min(self.config.dt_ms,max(1,e.next_deadline()-s.now))
            if self.config.version == 'native-rb/3':
                # Do not round a scheduled throw up to the next physics tick.
                throw = self.pending.get(s.ball.carrier)
                if throw and throw['cmd'].intent.kind in ('pass', 'shoot', 'handoff') and throw['due'] > s.now:
                    span = min(span, throw['due'] - s.now)
            m.c3_step(span,self.move.copy());m.step_count+=1;m.record()
        if s.phase==P.FINAL:return
        m.c4c_land_due()
        self.fill_cover();e.native_sync()
        self.rules=e.possession
        if previous_carrier and s.live_ms>before_live:
            p=s.players[previous_carrier];distance=max(0.,s.attack_sign(p.team)*(p.x-previous_xy[0]))
            e.native_stats[p.team]['distance_progressed']+=distance
        # Native residency, strict arc geometry and 5 m marked-defender exemption.
        if s.phase==P.LIVE and self.config.version=='native-rb/3':
            # RB-3.5 (PROVISIONAL): residence by zone, config timings, diagnosis logging.
            from .rulebook.zone_residence import residence
            residence(self,before_live)
        elif s.phase==P.LIVE:
            pp=e.possession.pp
            for p in s.players.values():
                zn=e.zone(p.x,p.y)
                if not p.active or p.role!='field' or zn is None:
                    self.m.e.residence.pop(p.id,None);continue
                marked=p.team!=pp and any(q.active and q.team!=p.team and q.role=='field' and math.hypot(q.x-p.x,q.y-p.y)<=5 for q in s.players.values())
                if marked:self.m.e.residence.pop(p.id,None);continue
                start=e.residence.setdefault(p.id,s.live_ms)
                if s.live_ms-start>=5000:
                    # PLACEHOLDER unmarked defenders use the same 5 s grace.
                    if p.team==pp:e.award(s.other(p.team),p.x,p.y,'zone_residence',fresh=True,normalize=False)
                    else:e.foul(p.id,reason='zone_unmarked')
                    e.residence.clear();break
        else:e.residence.clear()
        self.platform_motor(0)
        self.fill_cover()
        from .geometry import body_out
        carrier=s.players.get(s.ball.carrier)
        if carrier and body_out(carrier) and s.phase in (P.LIVE,P.OPENING):
            e.boundary(carrier.x,carrier.y,carrier.id)
        self.restart_metric.observe(self)
        self.assert_invariants()

    def assert_invariants(self):
        s=self.m.s
        self.m.e.assert_invariants()
        for team in ('A','B'):
            assert sum(p.team==team for p in s.players.values())==22
            if not(s.phase==self.types.Phase.FINAL and s.result['method']=='forfeit'):
                assert sum(p.team==team and p.active for p in s.players.values())==12
        assert 0<=s.tackle_count<=1
        assert not any(i.kind=='kick' for i in self.intents[-30:])
        assert self.config.legacy_layers==()
