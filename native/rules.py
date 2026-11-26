"""Native rule adapters. Provenance: B0 engine, rules_v03 and restarts_v1 at
2abe497, D1 tracker at c64d92e; authoritative amendments are the owner prompt.
PLACEHOLDER choices are supplied by cognition, never by this rules module.
"""
import math
from collections import Counter
from b1.possession import PossessionTracker, RulesConfig


def install(CO, cfg):
    E, M, T = CO.engine.Engine, CO.match.Match, CO.types
    P, B = T.Phase, T.BallMode
    original_init, original_elapse = E.__init__, E.elapse
    original_acquire, original_touch, original_release = E.acquire, E.touch, E.release
    original_contact, original_batch, original_emit = E.contact_legal, E.batch_events, E.emit
    original_freeze = E.freeze

    def init(self,s,config=None):
        original_init(self,s,config)
        self.native_config = cfg
        self.possession = PossessionTracker(RulesConfig(cfg.direct_ms,cfg.zone_radius))
        self.native_events, self.native_seen = [], 0
        self.possession_history=[]
        self.native_stats = {t:Counter() for t in ('A','B')}
        self.release_attempts={t:Counter() for t in ('A','B')}
        self.release_successes={t:Counter() for t in ('A','B')}
        self.dribbles, self.dribble_replay = {}, None
        self.freezes = Counter()
        self.restart_serial, self.restart_results = 0, {}
        self.hunt_claims = {}
        self.residence = {}
        self.vacancies = []
        self._syncing = False
        self.hunt_cleared = False
        self.play_ms = cfg.play_clock_ms
    E.__init__ = init

    if 'sideline_held_ball' in getattr(cfg,'rb333',()):
        from .geometry import held_sideline_in_play
        M.native_held_sideline_in_play = lambda self, ball: held_sideline_in_play(
            ball,self.s.players.get(ball.carrier))

    def sync(self):
        if self._syncing:return
        self._syncing = True
        try:
            s,b=self.s,self.s.ball
            self.possession.goal=dict(s.ends)
            events=[]
            for rec in self.log[self.native_seen:]:
                d,k=rec['data'],rec['event']
                if k=='release':
                    kind = 'shot_release' if d.get('kind')=='shot' else 'loose' if d.get('kind')=='loose' else 'pass_release'
                    events.append(dict(kind=kind,player=d['player'],team=s.players[d['player']].team))
                elif k=='touch':events.append(dict(kind='touch',player=d['player'],team=s.players[d['player']].team))
                elif k=='restart_awarded':events.append(dict(kind=k,team=d['team'],rst1=d.get('reason','').startswith('ZR-')))
                elif k=='restart_release':events.append(dict(kind=k,team=d['team']))
                elif k=='boundary':events.append(dict(kind='out_of_play'))
                elif k in ('goal','period_end','hunt_start'):events.append(dict(kind='dead'))
                elif k in ('strip','c3_strip_in_wind_up','handoff_fumble'):events.append(dict(kind='loose'))
            self.native_seen=len(self.log)
            events.append(dict(kind='live' if s.phase in (P.LIVE,P.OPENING,P.FLIGHT) else 'dead')) if self.possession.live != (s.phase in (P.LIVE,P.OPENING,P.FLIGHT)) else None
            touching={b.carrier:s.players[b.carrier].team} if b.carrier else {}
            if b.mode==B.CONTESTED:touching.update({pid:s.players[pid].team for pid in b.contested})
            holder=s.players.get(b.carrier)
            made=self.possession.step(s.now,touching,(b.x,b.y),events,(holder.x,holder.y) if holder else None)
            for row in made:
                if row['event']=='passive_possession':
                    self.freezes.clear()
                    for q in s.quivers.values():q.allocation=cfg.arrows;q.spent=0;q.loaded=cfg.arrows
                    if row.get('previous') is not None:
                        self.native_stats[row['previous']]['turnovers']+=1
                        s.possession_ms=cfg.play_clock_ms;s.tackle_count=0
                if row['event']=='violation' and s.phase==P.LIVE:
                    self.award(s.other(row['team']),b.x,b.y,row['violation'],fresh=True,normalize=False)
        finally:self._syncing=False
        # A rules violation may emit its restart while synchronization is held.
        # Consume that adjudication immediately, before any subsequent contact.
        if self.native_seen<len(self.log):self.native_sync()
    E.native_sync = sync

    def close_restart(self,status):
        r=self.s.restart
        if r is not None and hasattr(r,'native_id') and self.restart_results.get(r.native_id)=='pending':
            self.restart_results[r.native_id]=status
            self.emit('restart_closed','native',restart_id=r.native_id,status=status)
    E.close_restart=close_restart

    def award(self,team,x,y,reason,foul=False,fresh=False,normalize=True):
        s=self.s
        if s.phase==P.FINAL:return
        team=team or s.alternate
        self.close_restart('superseded:'+reason)
        self.dribbles.clear();self.dribble_replay=None
        if fresh or s.owner!=team:
            previous=self.possession.pp or s.owner
            s.owner=team;s.possession_ms=cfg.play_clock_ms;s.tackle_count=0
            if previous and previous!=team:self.native_stats[previous]['turnovers']+=1
            self.freezes.clear()
            for q in s.quivers.values():q.allocation=cfg.arrows;q.spent=0;q.loaded=cfg.arrows;q.reload_until=-1
        else:s.owner=team
        s.recovery=s.reconstruction=s.advantage=s.penalty=None
        s.award_deadline=s.award_available=s.award_spot=None
        s.engagements.clear()
        s.ball=T.Ball(mode=B.DEAD,x=float(x),y=float(y),z=.1075,last_touch=team)
        if reason in ('possession_expiry','second_tackle','turnover','offence_minor_turnover'):
            own=s.ends[team];sg=s.attack_sign(team);x=max(x,own+40) if sg>0 else min(x,own-40)
        kind='snap40' if reason in ('goal','period_start') else 'toss' if reason=='boundary' else 'scrim'
        if kind=='snap40':x=s.ends[team]+s.attack_sign(team)*40;y=50.
        if kind=='toss':
            x,y=max(0.,min(100.,x)),max(0.,min(100.,y))
            side=min(('x0','x1','y0','y1'),key=lambda k:{'x0':x,'x1':100-x,'y0':y,'y1':100-y}[k])
            if side=='x0':x=0.
            elif side=='x1':x=100.
            elif side=='y0':y=0.
            else:y=100.
            if x in (0.,100.) and abs(y-50)<cfg.zone_radius:
                y=50-cfg.zone_radius if y<50 else 50+cfg.zone_radius
            spot=(x+(-.6 if x==0 else .6 if x==100 else 0),y+(-.6 if y==0 else .6 if y==100 else 0))
        else:
            x,y=max(.5,min(99.5,x)),max(.5,min(99.5,y));spot=(x,y)
        self.restart_serial+=1
        r=T.Restart(team,x,y,reason,created_at=s.now,kind=kind,clearance=3. if kind=='toss' else 0.,taker_spot=spot)
        r.native_id=f'{s.period}/{self.restart_serial}'
        r.rs={'kind':kind,'snapper':None,'tackler':None}
        r.clock_runs=s.possession_ms>10000 and reason=='first_tackle'
        r.snap_deadline=s.now+(5500 if kind=='toss' else 10000)
        s.restart=r;s.phase=P.DEAD;s.ball.x,s.ball.y=x,y
        self.restart_results[r.native_id]='pending'
        self.emit('restart_awarded','native',team=team,reason=reason,spot=[x,y],restart_id=r.native_id,kind=kind)
        self.native_sync()
        return r
    E.award=award

    def new_owner(self,team,reason):
        s=self.s;changed=s.owner!=team
        if changed:
            previous=s.owner;s.owner=team
            self.emit('possession','native',team=team,previous=previous,reason=reason)
        return changed
    E.new_owner=new_owner

    def begin_hunt(self):
        s=self.s
        self.close_restart('period_end')
        s.restart=s.recovery=s.reconstruction=None
        s.owner=None;s.phase=P.OPENING;s.possession_ms=cfg.play_clock_ms;s.tackle_count=0
        s.opening_contestants=();s.opening_touched=False;s.opening_deadline=None
        s.ball=T.Ball(mode=B.LOOSE,x=50,y=50,z=.1075)
        self.hunt_claims={};self.hunt_cleared=False;self.dribbles.clear()
        self.possession_history.extend(self.possession.ledger)
        self.possession=PossessionTracker(RulesConfig(cfg.direct_ms,cfg.zone_radius,goal_x=tuple(s.ends.items())))
        self.freezes.clear()
        for q in s.quivers.values():q.allocation=cfg.arrows;q.spent=0;q.loaded=cfg.arrows
        self.emit('hunt_start','native',period=s.period)
    E.begin_hunt=begin_hunt
    def failed_hunt(self,reason):
        self.emit('hunt_retake','native',reason=reason);self.begin_hunt()
    E.failed_hunt=failed_hunt

    def acquire(self,pid,forced_joint=False):
        s,b=self.s,self.s.ball
        if s.phase==P.OPENING and pid not in s.opening_contestants:
            self.failed_hunt('false_start');return False
        if b.last_releaser==pid:
            if self.dribble_replay==pid:
                b.last_releaser=None;self.dribble_replay=None
            else:
                self.foul(pid,reason='self_recontact');return False
        recovery=s.ball.mode==B.LOOSE
        old={k:v for k,v in self.dribbles.items()} if self.dribble_replay==pid else None
        ok=original_acquire(self,pid,forced_joint)
        if ok:
            b.native_keeper_touch=s.players[pid].team if s.players[pid].role=='keeper' else None
            if recovery:s.players[pid].native_recovery=(b.x,b.y,s.now)
            if old is None:self.dribbles={pid:self.dribbles.get(pid,0)}
            else:self.dribbles=old
            if s.phase==P.LIVE and not self.hunt_cleared:
                if math.hypot(b.x-50,b.y-50)<=5:s.phase=P.OPENING
            self.native_sync()
        return ok
    E.acquire=acquire
    def touch(self,pid,deliberate=True):
        if self.dribble_replay!=pid:self.dribbles.clear()
        result=original_touch(self,pid,deliberate)
        self.s.ball.native_keeper_touch=self.s.players[pid].team if self.s.players[pid].role=='keeper' else None
        self.native_sync();return result
    E.touch=touch
    def release(self,pid,velocity,kind='pass',target=None,forced=False):
        if kind=='kick':raise AssertionError('kick prohibited by Native config')
        if kind=='dribble':
            if self.dribbles.get(pid,0)>=1:self.foul(pid,reason='second_dribble');return False
            self.dribbles[pid]=1;self.dribble_replay=pid;kind='pass'
        result=original_release(self,pid,velocity,kind,target,forced)
        if result:
            self.s.ball.native_keeper_touch=self.s.players[pid].team if self.s.players[pid].role=='keeper' else None
            self.s.ball.native_release_kind=kind
            self.s.ball.native_release_point=(self.s.ball.x,self.s.ball.y)
            self.s.ball.pocket_origin=(self.s.ball.x,self.s.ball.y)
            self.s.ball.pocket_release_team=self.s.players[pid].team
            if kind=='shot':self.native_stats[self.s.players[pid].team]['shots']+=1
            if kind!='loose':
                team=self.s.players[pid].team
                distance=math.hypot(self.s.ball.x-self.s.attack_goal(team),self.s.ball.y-50)
                self.release_attempts[team][int(distance)]+=1
        self.native_sync();return result
    E.release=release
    E.strike=lambda *a,**k: (_ for _ in ()).throw(AssertionError('kick/strike disabled'))

    def contact_legal(self,a,t,kind='tackle',surface='torso',reach=True):
        if t.role=='keeper' and a.team!=t.team and self.possession.keeper_protected(t.team,(t.x,t.y)):
            return False,'protected_keeper'
        if self.s.ball.carrier==t.id and surface in ('joint','knee'):
            surface='torso'
        if self.s.ball.carrier!=t.id and kind in ('grip','pull','hold','wrap'):return False,'noncarrier_grip'
        if kind!='tackle' and surface in ('hip','shoulder','arm'):surface='torso'
        legal,reason=original_contact(self,a,t,kind,surface,reach)
        return (True,'legal') if reason=='blindside' else (legal,reason)
    E.contact_legal=contact_legal

    def tackle(self,actor,target,body='knee',witnessed=False):
        s=self.s;a,t=s.players[actor],s.players[target]
        if s.ball.carrier!=target:return False
        if not witnessed and not self.contact_legal(a,t,'tackle')[0]:return False
        if t.role=='keeper' and self.possession.keeper_protected(t.team,(t.x,t.y)):return False
        x,y=s.ball.x,s.ball.y;count=s.tackle_count
        self.go_down(t)
        self.emit('tackle_count','native',actor=actor,target=target,count_to=count+1)
        if count==0:
            gx=s.attack_goal(t.team);sg=s.attack_sign(t.team)
            if abs(gx-x)<10:x=gx-sg*10
            s.tackle_count=1
            r=self.award(t.team,x,y,'first_tackle',normalize=False)
            s.tackle_count=1;r.rs.update(snapper=target,tackler=actor)
        else:self.award(a.team,x,y,'second_tackle',fresh=True,normalize=False)
        return True
    E.tackle=tackle

    def discipline(self,pid,kind,permanent=False):
        if kind is None:return
        p=self.s.players[pid]
        if kind in ('minor','warning'):
            p.minor_count+=1;ms=60000 if p.minor_count==4 else 0;dq=p.minor_count>=5
        elif kind=='major':
            p.major_count+=1;ms=120000;dq=p.major_count>=2
        else:ms=0;dq=True
        if permanent:dq=True
        self.native_stats[p.team]['major_fouls' if kind=='major' else 'minor_fouls']+=1
        if dq or ms:
            p.disqualified=dq;p.exclusion_ms=0 if dq else ms
            if p.active:self.vacancies.append((p.team,p.role,p.slot,p.x,p.y))
            p.active=False
            if self.s.ball.carrier==pid:self.s.ball.carrier=None;self.s.ball.mode=B.LOOSE
        self.emit('discipline','native',player=pid,kind=kind,duration=ms,disqualified=dq)
        available=sum(q.team==p.team and q.available and not q.disqualified and q.exclusion_ms<=0 for q in self.s.players.values())
        if available<12:self.forfeit(p.team,'fewer_than_12_of_22')
    E.discipline=discipline
    def foul(self,actor,victim=None,reason='hold',major=False,danger=False,**kwargs):
        s=self.s;a=s.players[actor];off=self.possession.pp or s.owner or a.team
        # Intent provenance, not an incidental collision classification, defines intentional contact.
        intent=getattr(a,'native_intent',None)
        intentional=bool(intent and getattr(intent,'contact',None) in ('head','trip') and intent.target==victim)
        ismajor=intentional and (getattr(intent,'contact',None)=='head' or (victim and s.ball.carrier!=victim))
        self.emit('foul','native',actor=actor,victim=victim,reason=reason,major=ismajor,intent_id=getattr(intent,'intent_id',None))
        self.discipline(actor,'major' if ismajor else 'minor')
        x,y=s.ball.x,s.ball.y
        if victim:
            v=s.players[victim]
            if s.attack_sign(off)*v.x>s.attack_sign(off)*x:x,y=v.x,v.y
        count=s.tackle_count
        if a.team==off:
            if count>=1:return self.award(s.other(off),x,y,'offence_minor_turnover',fresh=True,normalize=False)
            r=self.award(off,x,y,'offence_minor',normalize=False);s.tackle_count=1;return r
        if count==0:
            self.add_score(off,1 if s.period<=3 else 2,'half_goal' if s.period<=3 else 'full_goal_award')
            if s.phase==P.FINAL:return
        r=self.award(off,x,y,'defence_minor',normalize=False);s.tackle_count=max(0,count-1)
        if count==0:s.possession_ms=cfg.play_clock_ms
        return r
    E.foul=foul

    def add_score(self,team,points,kind,**data):
        s=self.s;s.score[team]+=points
        self.native_stats[team]['half_goal_awards' if kind=='half_goal' else 'goals']+=1
        self.emit('foul_award' if 'award' in kind or kind=='half_goal' else 'goal','native',team=team,points=points,method=kind,**data)
        if s.period>cfg.periods+1:self.complete('sudden_death',team)
    E.add_score=add_score
    def goal(self,defending,y=None,z=None):
        s,b=self.s,self.s.ball
        y=b.y if y is None else y;z=b.z if z is None else z
        if not CO.geometry.legal_goal(y,z,b.radius):return False
        if s.phase not in (P.LIVE,P.OPENING,P.FLIGHT) or not b.scoring:return False
        scoring=s.other(defending);p=s.players.get(b.carrier)
        release_pid=b.last_releaser
        releaser=s.players.get(release_pid)
        if getattr(b,'native_keeper_touch',None)==scoring or (p and p.role=='keeper' and p.team==scoring) or (releaser and releaser.role=='keeper' and releaser.team==scoring):
            self.boundary(b.x,y);return False
        carry=bool(p and p.team==scoring and b.control_time<s.now)
        origin=getattr(b,'native_release_point',None)
        distance=None if carry or origin is None else math.hypot(origin[0]-s.attack_goal(scoring),origin[1]-50)
        if carry:self.native_stats[scoring]['carries']+=1
        elif distance is not None:self.release_successes[scoring][int(distance)]+=1
        self.add_score(scoring,2,'carry' if carry else 'release',defending=defending,release_distance=distance)
        if s.phase==P.FINAL:return True
        if s.game_ms<=0:self.end_period()
        else:self.award(defending,s.ends[defending]+s.attack_sign(defending)*40,50,'goal',fresh=True,normalize=False)
        return True
    E.goal=goal

    def offside(self,side):
        s=self.s;r=s.restart;team=r.team;sg=s.attack_sign(team);count=s.tackle_count
        self.close_restart('procedural:'+side)
        self.emit('scrimmage_penalty','native',side=side,team=team)
        if side=='offence' and count>=1:return self.award(s.other(team),r.x-sg*5,r.y,'turnover',fresh=True,normalize=False)
        snapper,tackler=r.rs.get('snapper'),r.rs.get('tackler');clock_runs=r.clock_runs
        nr=self.award(team,r.x+sg*(5 if side=='defence' else -5),r.y,'offside',normalize=False)
        nr.rs.update(snapper=snapper,tackler=tackler);nr.clock_runs=clock_runs;s.tackle_count=max(0,count-1) if side=='defence' else count+1
        return nr
    E.offside=offside
    def ready(self,taker):
        s=self.s;r=s.restart;p=s.players[taker]
        if not r or p.team!=r.team or (p.role!='field' and not (p.role=='keeper' and r.kind!='toss' and r.rs.get('snapper')==p.id)) or not p.eligible(s.now) or p.posture!='upright':return False
        if math.dist((p.x,p.y),r.taker_spot)>.8:return False
        if r.kind=='toss' and s.now<r.created_at+1500:return False
        r.taker=taker
        if r.kind!='toss':
            sg=s.attack_sign(r.team)
            for q in s.players.values():
                if not q.active or q.role=='archer' or q.id==taker:continue
                if r.kind=='snap40':bad=abs(q.x-s.ends[q.team])>40+.05
                else:bad=sg*(q.x-r.x)>.05 if q.team==r.team else sg*(q.x-r.x)<-.05
                if bad:return False
        if r.ready_at is None:
            r.ready_at=r.created_at+1500 if r.kind=='toss' else s.now
            if r.kind=='toss':r.snap_deadline=r.ready_at+4000
            self.emit('restart_ready','native',taker=taker)
        return True
    E.ready=ready
    def restart_release(self,taker,velocity,target=None,method='hand'):
        s=self.s;r=s.restart
        if not r or s.phase!=P.DEAD or not self.ready(taker):return False
        if target==taker:return False
        if r.kind=='toss':
            if any(q.active and q.team!=r.team and q.role!='archer' and math.hypot(q.x-r.x,q.y-r.y)<3 for q in s.players.values()):return False
        else:
            for p in s.players.values():
                if not p.active or p.role=='archer' or p.id==taker:continue
                if r.kind=='snap40':
                    illegal=abs(p.x-s.ends[p.team])>40+.05
                else:
                    sign=s.attack_sign(r.team)
                    illegal=sign*(p.x-r.x)>.05 if p.team==r.team else sign*(p.x-r.x)<-.05
                if illegal:self.offside('offence' if p.team==r.team else 'defence');return False
        self.close_restart('released')
        team=r.team;s.ball=T.Ball(mode=B.PASS,x=r.x,y=r.y,z=s.players[taker].hand_height,
                                  vx=velocity[0],vy=velocity[1],vz=velocity[2],last_touch=team,
                                  last_releaser=taker,scoring=r.kind!='toss',release_time=s.now,intended=target)
        s.ball.native_release_kind='pass';s.ball.native_release_point=(r.x,r.y)
        s.restart=None;s.phase=P.LIVE;self.dribbles.clear()
        self.emit('restart_release','native',taker=taker,target=target,team=team,restart_id=r.native_id,velocity=list(velocity))
        self.native_sync();return True
    E.restart_release=restart_release

    def end_period(self):
        s=self.s
        self.close_restart('end_of_period')
        self.emit('period_end','native',score=dict(s.score))
        self.period_history.append(dict(period=s.period,score=dict(s.score),t_ms=s.now))
        if s.period>=cfg.periods and s.score['A']!=s.score['B']:
            return self.complete('regulation' if s.period==cfg.periods else 'overtime')
        s.period+=1;s.game_ms=(cfg.period_seconds if s.period<=cfg.periods else cfg.overtime_seconds)*1000
        if s.period==3:self.exchange_ends()
        self.begin_hunt()
    E.end_period=end_period
    def clock_expiry(self):
        s,b=self.s,self.s.ball
        if s.phase not in (P.LIVE,P.OPENING,P.FLIGHT):return
        if s.game_ms>0 and (s.owner is None or s.possession_ms>0):return
        if b.carrier is None and b.mode==B.SHOT and b.z>b.radius:
            if s.phase!=P.FLIGHT:s.phase=P.FLIGHT;s.tail_until=s.now+10000;s.tail_owner=s.owner;self.emit('finishing_flight','native')
            return
        if s.game_ms<=0:self.end_period()
        elif s.owner:self.award(s.other(self.possession.pp or s.owner),b.x,b.y,'possession_expiry',fresh=True,normalize=False)
    E.clock_expiry=clock_expiry
    def resolve_timers(self):
        s=self.s
        if s.phase==P.FINAL:return
        if not self.hunt_cleared and math.hypot(s.ball.x-50,s.ball.y-50)>5+s.ball.radius:
            self.hunt_cleared=True
            if s.phase==P.OPENING:s.phase=P.LIVE
            self.emit('hunt_cleared','native')
        if s.phase==P.DEAD and s.restart:
            r=s.restart
            if r.clock_runs and s.possession_ms<=0:
                self.close_restart('play_clock_expiry')
                self.award(s.other(r.team),r.x,r.y,'possession_expiry',fresh=True,normalize=False)
                self.native_sync();return
            if r.kind=='toss' and s.now>=r.created_at+5500:
                self.close_restart('toss_timeout')
                # Owner ruling 17 Nov 2026 (PROVISIONAL, supersedes RB-2 goal-line placement):
                # every toss timeout (end line and side boundary) is a turnover scrimmage at the
                # other team's own 40 or the spot, whichever is closer to the goal it attacks.
                self.award(s.other(r.team),r.x,r.y,'turnover',fresh=True,normalize=False)
            elif s.now>=r.snap_deadline:
                self.close_restart('snap_timeout');self.offside('offence')
        elif s.phase==P.FLIGHT:
            if s.ball.carrier is not None or s.ball.z<=s.ball.radius or s.now>=s.tail_until:
                if s.game_ms<=0:self.end_period()
                elif s.owner:self.award(s.other(s.owner),s.ball.x,s.ball.y,'possession_expiry',fresh=True,normalize=False)
        elif s.contested_until and s.now>=s.contested_until:
            # PLACEHOLDER B0 held-ball tie resolution; no penalty is inferred.
            s.contested_until=None;self.held()
        else:self.clock_expiry()
        self.native_sync()
    E.resolve_timers=resolve_timers
    def next_deadline(self):
        s=self.s;due=[s.now+cfg.dt_ms]
        if s.phase in (P.LIVE,P.OPENING):
            due.append(s.now+max(1,s.game_ms))
            if s.owner:due.append(s.now+max(1,s.possession_ms))
        for player in s.players.values():
            if player.freeze_until>s.now:due.append(player.freeze_until)
        if s.phase in (P.LIVE,P.OPENING):
            if self.possession.unc_start is not None and self.possession.dp_team!=self.possession.unc_team:
                due.append(max(s.now+1,self.possession.unc_start+cfg.direct_ms))
            for team,start in self.possession.zone_start.items():
                if start is not None and not self.possession.zone_violated[team]:due.append(max(s.now+1,start+5000))
        if s.restart:
            due.append(s.restart.snap_deadline)
            if s.restart.clock_runs:due.append(s.now+max(1,s.possession_ms))
        return max(s.now+1,min(due))
    E.next_deadline=next_deadline
    def elapse(self,dt,resolve=True):
        s=self.s
        if dt<0:raise ValueError('negative time')
        active=s.phase in (P.LIVE,P.OPENING)
        if active:
            s.game_ms=max(0,s.game_ms-dt)
            if s.owner:s.possession_ms=max(0,s.possession_ms-dt)
            s.live_ms+=dt
            for p in s.players.values():p.exclusion_ms=max(0,p.exclusion_ms-dt)
        elif s.phase!=P.FINAL:
            s.dead_ms+=dt
            if s.restart and s.restart.clock_runs:s.possession_ms=max(0,s.possession_ms-dt)
        s.now+=dt
        # Native owns occupancy; disable the retired B0 residency timer inputs.
        for p in s.players.values():p.zone_ms=[0,0];p.unmarked_ms=[0,0];p.keeper_hold_ms=0
        if resolve:self.resolve_timers()
    E.elapse=elapse

    def freeze(self,pid,arrow=None,panel=True,direct=True,in_range=True):
        p=self.s.players[pid];shooting=self.s.other(p.team)
        recovery=getattr(p,'native_recovery',None)
        if recovery and self.s.now-recovery[2]<2000 and math.hypot(p.x-recovery[0],p.y-recovery[1])<=3:return False
        if (p.role=='keeper' and self.zone(p.x,p.y)==self.s.own_zone(p.team)) or self.freezes[shooting]>=cfg.freezes:return False
        ok=original_freeze(self,pid,arrow,panel,direct,True)
        if ok:self.freezes[shooting]+=1
        return ok
    E.freeze=freeze
    E.archer_in_lane=lambda self,p:p.role=='archer' and abs(p.y-50)<.001 and p.x==self.s.ends[p.team]+(-cfg.platform_setback if self.s.ends[p.team]==0 else cfg.platform_setback)
    def shoot_arrow(self,pid,target,velocity,origin=None):
        s=self.s;p=s.players[pid];q=s.quivers[p.team]
        if q.spent>=cfg.arrows:return False
        q.spent+=1;q.loaded=max(0,cfg.arrows-q.spent);q.last_release=s.now
        self.native_sync();t=s.players.get(target)
        legal=(p.role=='archer' and p.eligible(s.now) and self.archer_in_lane(p) and s.phase==P.LIVE and self.hunt_cleared and t is not None and t.team!=p.team and t.role=='field' and
               self.possession.pp==t.team and self.possession.tc==t.team and self.zone(t.x,t.y) is None and t.eligible(s.now) and s.now>t.immune_until)
        if not legal:self.foul(pid,target if t else None,'archery_target');return False
        point=(p.x,p.y,cfg.platform_height+.72*p.a.height)
        speed=math.sqrt(sum(v*v for v in velocity))
        cap=getattr(cfg,'arrow_speed_cap',30.) # native-v0/2: 30; native-v0/3: None (canon, no cap)
        if cap is not None and speed>cap+1e-6:self.foul(pid,reason='arrow_speed');return False
        ar=T.Arrow(self.next_arrow,p.team,pid,target,*point,*velocity,point,s.now);self.next_arrow+=1;s.arrows.append(ar);q.last_release=s.now
        self.emit('arrow_release','native',player=pid,target=target,arrow=ar.id,velocity=list(velocity),origin=list(point));return ar
    E.shoot_arrow=shoot_arrow
    E.reload=lambda *a,**k:False

    def batch_events(self,events):
        # Normalize legacy danger/hold flags before simultaneous discipline;
        # incidental head contacts cannot become majors through neutral_offset.
        for event in events:
            if event.kind=='foul':
                actor=self.s.players[event.actor];intent=getattr(actor,'native_intent',None)
                chosen=bool(intent and getattr(intent,'contact',None) in ('head','trip') and intent.target==event.target)
                major=chosen and (intent.contact=='head' or self.s.ball.carrier!=event.target)
                event.data['major']=major;event.data['danger']=major
                if event.data.get('reason')=='hold':event.data['reason']='holding'
        # Exact coincident boundaries precede catches; goals precede catches.
        goals=[e for e in events if e.kind=='goal']
        boundaries=[e for e in events if e.kind=='boundary']
        if goals:
            for ev in goals:self.dispatch(ev)
            events=[e for e in events if e.kind not in ('goal','acquire','boundary')]
        elif boundaries:
            for ev in boundaries:self.dispatch(ev)
            events=[e for e in events if e.kind not in ('boundary','acquire')]
        if self.s.phase!=P.FINAL:original_batch(self,events)
    E.batch_events=batch_events
    from .ladder import catch_capacity
    M.native_catch_capacity=lambda self,skill,miss:catch_capacity(skill,miss,self.assume['ball_mass_kg'])

    # Finality gate for newly installed mutators; old B0 guards cannot wrap methods
    # added after import. No command can mutate a completed Native match.
    from functools import wraps
    def final_gate(name, fn):
        @wraps(fn)
        def guarded(self,*args,**kwargs):
            if self.s.phase==P.FINAL:
                self.final_refused[name]=self.final_refused.get(name,0)+1
                return None
            return fn(self,*args,**kwargs)
        return guarded
    for name in ('award','new_owner','begin_hunt','failed_hunt','acquire','touch','release','tackle',
                 'discipline','foul','add_score','goal','offside','ready','restart_release','end_period',
                 'clock_expiry','resolve_timers','elapse','freeze','shoot_arrow','batch_events'):
        setattr(E,name,final_gate(name,getattr(E,name)))
