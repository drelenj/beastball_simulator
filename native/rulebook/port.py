"""RB engine driver; reuses Native's unchanged athlete decision implementation."""
from native.port import NativePort
from .config import RulebookConfig

class RulebookPort(NativePort):
    def __init__(self,seed=1,config=None,policies=None,plumbing=True):
        super().__init__(seed,config or RulebookConfig(),policies,plumbing)
        self.setup={p.id:(abs(p.x-self.m.s.ends[p.team]),p.y) for p in self.m.s.players.values() if p.role!='archer'}
        self.last_reset_period=1

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
                if e.rb_timeout(team):self.advance_intermission();return
        if s.phase==self.types.Phase.OPENING:e.rb_hunt_release()
        super().step()
