"""Working-canon provisional banded scoring. Shot bands exclude passes."""
import math
from collections import Counter

def install(co,cfg):
 E,T=co.engine.Engine,co.types;P=T.Phase
 old_init,old_release,old_acquire,old_award=E.__init__,E.release,E.acquire,E.award
 def init(self,*a,**kw):
  old_init(self,*a,**kw);self.rb_bands={t:Counter() for t in ('A','B')};self.rb_attempts=[]
 E.__init__=init
 def band(distance):
  return 'under10' if distance<cfg.release_bands[0][0] else '10_to20' if distance<cfg.release_bands[1][0] else '20plus'
 def release(self,pid,velocity,kind='pass',*args,**kw):
  ok=old_release(self,pid,velocity,kind,*args,**kw)
  if ok and kind not in ('loose','kick'):
   s=self.s;p=s.players[pid];d=math.hypot(s.ball.x-s.attack_goal(p.team),s.ball.y-50);key=band(d)
   if kind=='shot':
    s.ball.rb_release_band=key
    self.rb_bands[p.team][key+'_attempts']+=1
   self.rb_attempts.append(dict(player=pid,team=p.team,distance=d,band=key,t_ms=s.now,kind=kind,shot_attempt=kind=='shot'))
  return ok
 E.release=release
 def acquire(self,pid,*args,**kw):
  result=old_acquire(self,pid,*args,**kw)
  if result:
   self.s.ball.rb_release_band=None
   self.s.ball.rb_deliberate_team=None
  return result
 E.acquire=acquire
 def award(self,*args,**kw):
  result=old_award(self,*args,**kw)
  if self.s.ball:
   self.s.ball.rb_release_band=None
   self.s.ball.rb_deliberate_team=None
  return result
 E.award=award
 def goal(self,defending,y=None,z=None):
  s,b=self.s,self.s.ball;y=b.y if y is None else y;z=b.z if z is None else z
  plane=s.ends[defending];cross=(b.x-plane)*(1 if plane==100 else -1)-b.radius
  margin=min(cross,cfg.goal_radius-math.hypot(y-50,z)-b.radius)
  scoring=s.other(defending);holder=s.players.get(b.carrier);releaser=s.players.get(b.last_releaser)
  own=bool(holder and holder.team==defending or releaser and releaser.team==defending)
  keeper_invalid=not own and (holder and holder.role=='keeper' or releaser and releaser.role=='keeper' or getattr(b,'native_keeper_touch',None)==scoring)
  valid=not keeper_invalid and margin>=-1e-7 and s.phase in (P.LIVE,P.OPENING,P.FLIGHT) and b.scoring
  if not valid:
   if keeper_invalid and margin>=0:self.boundary(b.x,y)
   return False
  scoring=s.other(defending);holder=s.players.get(b.carrier);releaser=s.players.get(b.last_releaser)
  own=bool(holder and holder.team==defending or releaser and releaser.team==defending)
  if not own and (holder and holder.role=='keeper' or releaser and releaser.role=='keeper' or getattr(b,'native_keeper_touch',None)==scoring):
   self.boundary(b.x,y);return False
  carry=bool(holder and holder.team==scoring)
  origin=getattr(b,'native_release_point',(b.x,b.y));distance=math.hypot(origin[0]-s.attack_goal(scoring),origin[1]-50)
  key='own' if own else 'carry' if carry else getattr(b,'rb_release_band',band(distance))
  if carry:self.rb_bands[scoring]['carry_attempts']+=1
  if own or carry or getattr(b,'rb_release_band',None) is not None:
   self.rb_bands[scoring][key+'_goals']+=1
  if carry:self.native_stats[scoring]['carries']+=1
  elif not own:self.release_successes[scoring][int(distance)]+=1
  self.add_score(scoring,self.rb.points(carry,distance,own),'own' if own else 'carry' if carry else 'release',release_distance=None if carry else distance,band=key)
  if s.phase==P.FINAL:return True
  if s.game_ms<=0:self.end_period()
  else:self.award(defending,s.ends[defending]+s.attack_sign(defending)*40,50,'goal',fresh=True,normalize=False)
  return True
 E.goal=goal

 old_restart=E.restart_release
 def restart_release(self,pid,velocity,*args,**kw):
  ok=old_restart(self,pid,velocity,*args,**kw)
  if ok:
   s=self.s;p=s.players[pid];d=math.hypot(s.ball.x-s.attack_goal(p.team),s.ball.y-50);key=band(d)
   self.rb_attempts.append(dict(player=pid,team=p.team,distance=d,band=key,t_ms=s.now,kind='restart_pass',shot_attempt=False))
  return ok
 E.restart_release=restart_release
