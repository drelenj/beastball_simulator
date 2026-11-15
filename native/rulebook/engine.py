"""RB-1-only engine adapters. No cognition imports or policy replacement."""
from .authorities import Authorities


def install(co,cfg):
    E,T=co.engine.Engine,co.types;P=T.Phase
    old_init,old_elapse,old_hunt,old_release=E.__init__,E.elapse,E.begin_hunt,E.release
    old_timers,old_deadline,old_score=E.resolve_timers,E.next_deadline,E.add_score
    def init(self,*args,**kwargs):
        old_init(self,*args,**kwargs)
        self.rb=Authorities(cfg);self.rb_pause=None;self.rb_hunt_running=False
    E.__init__=init
    def publish(self,row):
        self.emit('rb_'+row['kind'],'RB-1',ruling=dict(row))
        return row
    E.rb_publish=publish
    def begin_hunt(self):
        old_hunt(self);self.rb_hunt_running=False
    E.begin_hunt=begin_hunt
    def hunt_release(self):
        if self.s.phase!=P.OPENING or self.rb_hunt_running:return False
        self.rb_hunt_running=True;self.rb_publish(self.rb.ruling('hunt_release'))
        return True
    E.rb_hunt_release=hunt_release
    def pause(self,kind,duration):
        self.rb_pause=dict(kind=kind,until=self.s.now+duration,started=self.s.now,game=self.s.game_ms,play=self.s.possession_ms)
    E.rb_begin_pause=pause
    def finish_pause(self):
        pause=self.rb_pause
        if not pause or self.s.now<pause['until']:return
        if pause['kind']=='timeout' and self.s.restart:
            r=self.s.restart;dt=self.s.now-pause['started']
            r.created_at+=dt;r.snap_deadline+=dt
            if r.ready_at is not None:r.ready_at+=dt
        self.rb_pause=None
        if pause['kind']=='break':self.begin_hunt()
        self.rb_publish(self.rb.ruling('pause_end',pause_kind=pause['kind']))
    E.rb_finish_pause=finish_pause
    def end_period(self):
        s=self.s
        self.close_restart('end_of_period');self.emit('period_end','RB-1',score=dict(s.score))
        self.period_history.append(dict(period=s.period,score=dict(s.score),t_ms=s.now))
        if s.period>=4 and s.score['A']!=s.score['B']:return self.complete('regulation' if s.period==4 else 'overtime')
        s.period+=1;s.game_ms=(600 if s.period<=4 else 300)*1000
        self.exchange_ends();row=self.rb.enter_period(s.period);self.rb_publish(row)
        self.close_restart('period_break');s.restart=None;s.phase=P.DEAD;s.ball.carrier=None;s.ball.mode=T.BallMode.DEAD
        self.rb_hunt_running=False
        self.rb_begin_pause('break',row['duration_ms'])
    E.end_period=end_period
    def elapse(self,dt,resolve=True):
        if self.rb_pause:
            assert 0<=dt<=self.rb_pause['until']-self.s.now
            self.s.dead_ms+=dt;self.s.now+=dt
            self.rb_finish_pause();return
        if self.s.phase==P.OPENING and not self.rb_hunt_running:
            self.s.dead_ms+=dt;self.s.now+=dt;return
        return old_elapse(self,dt,resolve)
    E.elapse=elapse
    def timers(self):
        if self.rb_pause:return
        return old_timers(self)
    E.resolve_timers=timers
    def deadline(self):
        return self.rb_pause['until'] if self.rb_pause else old_deadline(self)
    E.next_deadline=deadline
    def timeout(self,team):
        s=self.s
        if self.rb_pause or s.phase==P.FINAL:return False
        row=self.rb.timeout(team,s.phase==P.DEAD,self.possession.pp or s.owner,s.game_ms,s.score)
        if not row:return False
        self.rb_publish(row);self.rb_begin_pause('timeout',cfg.timeout_ms);return True
    E.rb_timeout=timeout
    def add_score(self,team,points,kind,**data):
        self.rb.score(team)
        return old_score(self,team,points,kind,**data)
    E.add_score=add_score
    old_assert=E.assert_invariants
    def invariants(self):
        if self.rb_pause:
            assert self.s.phase==P.DEAD and self.s.game_ms>=0 and self.s.possession_ms>=0
            assert self.s.ball.carrier is None
            return True
        return old_assert(self)
    E.assert_invariants=invariants
    from .substitutions import install as install_substitutions
    install_substitutions(co,cfg)
    from .discipline import install as install_discipline
    install_discipline(co,cfg)
    from .archery import install as install_archery
    install_archery(co,cfg)
    from .scoring import install as install_scoring
    install_scoring(co,cfg)
