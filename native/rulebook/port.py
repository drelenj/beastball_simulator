"""RB engine driver; reuses Native's unchanged athlete decision implementation."""
from native.port import NativePort,body
from dataclasses import dataclass,fields
from native import cognition as C
from .authorities import CREW

@dataclass(frozen=True)
class RulebookView(C.AthleteView):
    status_indicators: tuple = ()
    officials: tuple = CREW
    # RB-3.6 (native-rb/3 only; None elsewhere): public team instruction and own-body memory
    defender_baseline: tuple | None = None   # (enabled, mark_distance_m, ball_leash_m)
    own_zone_exit_ms_ago: int | None = None  # live ms since I last left my own Keeper Zone

from .config import RulebookConfig

class RulebookPort(NativePort):
    def __init__(self,seed=1,config=None,policies=None,plumbing=True,rosters=None):
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

    @property
    def intermission_pending(self):return self.m.e.rb_pause is not None

    def advance_intermission(self):
        e=self.m.e;e.elapse(e.rb_pause['until']-self.m.s.now)
        if self.last_reset_period!=self.m.s.period:
            # PLACEHOLDER procedural reset: reuse legal initial scatter, no formation.
            for p in self.m.s.players.values():
                if p.role=='archer':continue
                depth,y=self.setup[p.id];p.x=self.m.s.ends[p.team]+self.m.s.attack_sign(p.team)*depth;p.y=y
                p.z=p.vx=p.vy=p.vz=0.;p.target=(p.x,p.y)
            self.move.clear();self.pending.clear();self.keeper_intents.clear()
            self.platform_motor(0);self.last_reset_period=self.m.s.period

    def step(self):
        if self.intermission_pending:self.advance_intermission();return
        e=self.m.e;s=self.m.s
        if s.phase==self.types.Phase.DEAD:
            for team in ('A','B'):
                if e.rb_timeout(team):
                    # Yield a positive dead-time step; the driver then consumes
                    # the remaining official pause and resets only its watchdog.
                    e.elapse(1);return
        if s.phase==self.types.Phase.OPENING:e.rb_hunt_release()
        self.m.rb_previous_positions={p.id:(p.x,p.y,p.z) for p in s.players.values()}
        super().step()

    def fill_cover(self):
        self.m.e.rb_fill_slots()

    def assert_invariants(self):
        self.m.e.assert_invariants()
        assert all(sum(p.team==team for p in self.m.s.players.values())==22 for team in ('A','B'))
        assert 0<=self.m.s.tackle_count<=1

    def capture(self,now):
        super().capture(now)
        if not hasattr(self,'indicator_frames'):self.indicator_frames={}
        for pid,frames in self.frames.items():
            f=frames[-1]
            if f.captured_ms!=now:continue
            visible={t.entity for t in f.tracks}|{pid}
            self.indicator_frames[f.frame_id]=tuple((q.id,'red' if q.frozen(now) else 'amber' if now<=q.immune_until else 'off') for q in self.m.s.players.values() if q.id in visible)

        keep={f.frame_id for frames in self.frames.values() for f in frames}
        self.indicator_frames={i:v for i,v in self.indicator_frames.items() if i in keep}

    def view(self,pid,now,bench_role=None):
        v,b=super().view(pid,now,bench_role)
        if v is None:return v,b
        f=next((f for f in reversed(self.frames.get(pid,())) if f.captured_ms<=now-self.config.latency_ms),None)
        states=self.indicator_frames.get(f.frame_id,()) if f and hasattr(self,'indicator_frames') else ()
        extra={}
        if self.config.version=='native-rb/3':
            c=self.config;exits=getattr(self.m.e,'rb35',{}).get('own_exit',{})
            extra=dict(defender_baseline=(c.defender_baseline,c.defender_mark_distance_m,c.defender_ball_leash_m),
                       own_zone_exit_ms_ago=self.m.s.live_ms-exits[pid] if pid in exits else None)
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
            ok=m.e.shoot_arrow(pid,i.target,ans[0]);self.resolve(pid,'arrow_released' if ok else 'rejected_by_engine')

    @staticmethod
    def view_from_json(payload):
        from copy import deepcopy
        data=deepcopy(payload);status=data['view'].pop('status_indicators',());officials=data['view'].pop('officials',CREW)
        baseline=data['view'].pop('defender_baseline',None);exit_ago=data['view'].pop('own_zone_exit_ms_ago',None)
        v,b=C.view_from_json(data)
        return RulebookView(**{f.name:getattr(v,f.name) for f in fields(C.AthleteView)},status_indicators=tuple(tuple(x) for x in status),officials=tuple(officials),
                            defender_baseline=tuple(baseline) if baseline is not None else None,own_zone_exit_ms_ago=exit_ago),b
