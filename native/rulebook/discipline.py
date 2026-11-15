"""Rule-layer foul classification and shorthanded eligibility."""
import math

def install(co,cfg):
 E,T=co.engine.Engine,co.types;P=T.Phase
 old_elapse,old_deadline,old_contact=E.elapse,E.next_deadline,E.contact_legal
 def discipline(self,pid,kind,permanent=False):
  if kind is None:return
  if kind=='warning':self.rb_publish(self.rb.ruling('warning',player=pid));return
  p=self.s.players[pid]
  if kind not in ('major','minor'):kind='major';p.major_count=max(1,p.major_count)
  row=self.rb.discipline(p,kind,self.s.live_ms);p.exclusion_ms=row['duration_ms']
  self.native_stats[p.team]['major_fouls' if kind=='major' else 'minor_fouls']+=1
  if row['duration_ms']:
   self.rb_slots[pid]=dict(team=p.team,role=p.role,until=self.s.live_ms+row['duration_ms'])
   if self.s.ball.carrier==pid:self.s.ball.carrier=None;self.s.ball.mode=T.BallMode.LOOSE
  self.rb_publish(row)
 E.discipline=discipline
 def foul(self,actor,victim=None,reason='hold',major=False,danger=False,**kw):
  s=self.s
  if s.phase==P.FINAL:return
  a=s.players[actor];v=s.players.get(victim);intent=getattr(a,'native_intent',None)
  intentional=bool(intent and intent.target==victim and getattr(intent,'contact',None) in ('head','neck','trip','tackle'))
  immune=bool(v and (v.frozen(s.now) or s.now<=v.immune_until or v.role=='keeper' and self.possession.keeper_protected(v.team,(v.x,v.y))))
  ismajor=(reason in ('striking','after_whistle','protected_keeper','frozen_contact','immune_contact') or immune or intentional and (intent.contact in ('head','neck') or s.ball.carrier!=victim))
  if reason=='delay_of_game':
   warnings=self.rb.warnings.get(actor,0);self.rb.warnings[actor]=warnings+1
   if not warnings:self.discipline(actor,'warning');return
  self.emit('foul','RB-D',actor=actor,victim=victim,reason=reason,major=ismajor,intent_id=getattr(intent,'intent_id',None))
  self.discipline(actor,'major' if ismajor else 'minor')
  off=self.possession.pp or s.owner or a.team;count=s.tackle_count;x,y=(v.x,v.y) if v else (s.ball.x,s.ball.y)
  if ismajor:
   team=v.team if v else s.other(a.team)
   if self.zone(x,y) is not None:x=0. if x<50 else 100.
   r=self.award(team,x,y,'major',normalize=False)
   if x in (0.,100.):
    r.x=s.ball.x=x;r.taker_spot=(max(.6,min(99.4,x)),y);r.rs['goal_line']=True
   self.rb_publish(self.rb.ruling('major',actor=actor,victim=victim,spot=[x,y]))
  elif a.team==off or reason in ('kicking','delay_of_game','marking_pre_live') or reason in ('hold','holding','hooking','noncarrier_grip') and v and s.ball.carrier!=v.id:
   if count>=1:self.award(s.other(off),x,y,'offence_minor_turnover',fresh=True,normalize=False)
   else:self.award(off,x,y,'minor_count_plus',normalize=False);s.tackle_count=1
  else:
   if count==0:
    self.add_score(off,self.rb.points(award=True),'half_goal' if s.period<=3 else 'full_goal_award')
    if s.phase==P.FINAL:return
   self.award(off,x,y,'defence_minor',normalize=False);s.tackle_count=max(0,count-1)
   if count==0:s.possession_ms=cfg.play_clock_ms
  if v and reason in ('head','neck','head_contact','neck_contact'):
   self.rb_force_injury(v.id,head=True)
 E.foul=foul
 def contact(self,a,t,kind='tackle',surface='torso',reach=True):
  if t.frozen(self.s.now):return False,'frozen_contact'
  if self.s.now<=t.immune_until:return False,'immune_contact'
  return old_contact(self,a,t,kind,surface,reach)
 E.contact_legal=contact
 def elapse(self,dt,resolve=True):
  result=old_elapse(self,dt,resolve)
  for p in self.s.players.values():
   debt=self.rb.exclusions.get(p.id)
   if debt:p.exclusion_ms=max(0,debt['until']-self.s.live_ms)
  return result
 E.elapse=elapse
 def deadline(self):
  due=old_deadline(self)
  if self.s.phase in (P.LIVE,P.OPENING) and not self.rb_pause:
   for debt in self.rb.exclusions.values():
    if debt['until']>self.s.live_ms:due=min(due,self.s.now+debt['until']-self.s.live_ms)
  return due
 E.next_deadline=deadline
 E.strike=lambda self,pid,*a,**kw:self.foul(pid,reason='kicking')
 old_release=E.release
 def release(self,pid,velocity,kind='pass',*args,**kw):
  if kind=='kick':self.foul(pid,reason='kicking');return False
  return old_release(self,pid,velocity,kind,*args,**kw)
 E.release=release
 old_restart=E.restart_release
 def restart(self,pid,velocity,*args,**kw):
  s=self.s;r=s.restart
  if r and r.taker==pid:
   p=s.players[pid]
   for q in sorted(s.players.values(),key=lambda q:q.id):
    if q.active and q.team!=p.team and q.role!='archer' and q.id!=r.rs.get('tackler') and math.hypot(q.x-p.x,q.y-p.y)<5:
     self.foul(q.id,pid,'marking_pre_live');return False
  return old_restart(self,pid,velocity,*args,**kw)
 E.restart_release=restart
 old_award=E.award
 def award(self,team,x,y,reason,*args,**kw):
  if reason=='zone_residence':x=self.s.ends[team]+self.s.attack_sign(team)*cfg.zone_radius
  return old_award(self,team,x,y,reason,*args,**kw)
 E.award=award
