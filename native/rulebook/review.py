"""Recorded-state review. Force-call hooks inject officiating errors, not injuries/RNG."""
import copy,math
from dataclasses import dataclass

@dataclass(frozen=True)
class Evidence:
    kind: str
    called: bool
    actual: bool
    margin: float
    before: object
    engine: object
    data: tuple


def install(co,cfg):
 E,T=co.engine.Engine,co.types;P=T.Phase
 old_init,old_goal,old_boundary,old_foul=E.__init__,E.goal,E.boundary,E.foul
 def init(self,*args,**kw):
  old_init(self,*args,**kw);self.rb_evidence={}
 E.__init__=init
 def snapshot(self):
  keys=('possession','restart_results','restart_serial','native_stats','rb_bands','rb_attempts','release_attempts','release_successes','freezes','rb_slots','period_history','score_history')
  return copy.deepcopy(self.s),{k:copy.deepcopy(getattr(self,k)) for k in keys}|{'scores':list(self.rb.scores),'quotas':copy.deepcopy(self.rb.quotas),**{'authority_'+k:copy.deepcopy(getattr(self.rb,k)) for k in ('exclusions','injuries','evaluated','warnings','period','timeouts','challenges','timeout_triggers')}}
 def save(self,kind,called,actual,margin,before,engine,**data):
  self.rb_evidence={i:e for i,e in self.rb_evidence.items() if e.before.live_ms==self.s.live_ms}
  row=self.rb.ruling(kind,called=called,**data)
  self.emit('rb_'+kind,'RB-1',ruling=dict(row))
  self.rb_evidence[row['id']]=Evidence(kind,called,actual,margin,before,engine,tuple(data.items()))
  return row['id']
 E.rb_save_call=save
 def goal_call(self,defending,called=None):
  s=self.s;b=s.ball;before,engine=snapshot(self);plane=s.ends[defending]
  margin=min((b.x-plane)*(1 if plane==100 else -1)-b.radius,cfg.goal_radius-math.hypot(b.y-50,b.z)-b.radius)
  actual=margin>=0 and b.scoring;called=actual if called is None else called
  if called:
   if not actual:
    b.x=plane+(1 if plane==100 else -1)*(b.radius+.2);b.y=50;b.z=1.5
   old_goal(self,defending)
  else:self.award(s.owner or s.other(defending),b.x,b.y,'reviewable_no_goal',normalize=False)
  return save(self,'goal' if called else 'no_goal',called,actual,margin,before,engine,defending=defending)
 E.rb_force_goal_call=goal_call
 def goal(self,defending,y=None,z=None):
  before,engine=snapshot(self);b=self.s.ball;plane=self.s.ends[defending]
  yy=b.y if y is None else y;zz=b.z if z is None else z
  margin=min((b.x-plane)*(1 if plane==100 else -1)-b.radius,cfg.goal_radius-math.hypot(yy-50,zz)-b.radius)
  result=old_goal(self,defending,y,z)
  save(self,'goal' if result else 'no_goal',bool(result),bool(result),margin,before,engine,defending=defending)
  return result
 E.goal=goal
 def boundary_call(self,called=None,scoring_play=True,major_foul=False,carrier=None):
  s=self.s;before,engine=snapshot(self)
  q=s.players.get(carrier);x,y=(q.x,q.y) if q else(s.ball.x,s.ball.y)
  margin=max(-x,x-100,-y,y-100)+(q.radius if q else -s.ball.radius)
  actual=margin>=0;called=actual if called is None else called
  if called:old_boundary(self,x,y,carrier)
  else:self.award(s.owner or 'A',x,y,'reviewable_in_bounds',normalize=False)
  return save(self,'boundary',called,actual,margin,before,engine,scoring_play=scoring_play,major_foul=major_foul,x=x,y=y,carrier=carrier)
 E.rb_force_boundary_call=boundary_call
 def boundary(self,x=None,y=None,carrier=None):
  s=self.s;before,engine=snapshot(self);b=s.ball;xx=b.x if x is None else x;yy=b.y if y is None else y
  scoring=b.mode==T.BallMode.SHOT or b.carrier is not None and min(abs(b.x),abs(100-b.x))<cfg.zone_radius
  result=old_boundary(self,x,y,carrier)
  if s.phase!=P.FINAL:
   margin=max(-xx,xx-100,-yy,yy-100)+(s.players[carrier].radius if carrier else -b.radius)
   save(self,'boundary',True,True,margin,before,engine,scoring_play=scoring,major_foul=False,x=xx,y=yy,carrier=carrier)
  return result
 E.boundary=boundary
 def contact_call(self,actor,victim,called=None):
  s=self.s;p=s.players[victim];before,engine=snapshot(self)
  actual=p.role=='keeper' and self.possession.keeper_protected(p.team,(p.x,p.y))
  called=actual if called is None else called
  if called:old_foul(self,actor,victim,'protected_keeper')
  else:self.award(s.owner or p.team,p.x,p.y,'contact_stands',normalize=False)
  return save(self,'keeper_immunity',called,actual,0.,before,engine,actor=actor,victim=victim)
 E.rb_force_keeper_call=contact_call
 def foul(self,actor,victim=None,reason='hold',**kw):
  if victim and self.s.players[victim].role=='keeper':
   before,engine=snapshot(self);p=self.s.players[victim]
   actual=self.possession.keeper_protected(p.team,(p.x,p.y));result=old_foul(self,actor,victim,reason,**kw)
   if self.s.phase!=P.FINAL:save(self,'keeper_immunity',actual,actual,0.,before,engine,actor=actor,victim=victim)
   return result
  return old_foul(self,actor,victim,reason,**kw)
 E.foul=foul
 def review(self,team,call_id):
  s=self.s;ev=self.rb_evidence.get(call_id)
  if s.phase not in (P.DEAD,P.FINAL) or not ev or ev.before.live_ms!=s.live_ms:return False
  across_period=ev.before.period!=s.period
  resources=ev.engine['authority_challenges'] if across_period else self.rb.challenges
  timeouts=ev.engine['authority_timeouts'] if across_period else self.rb.timeouts
  if resources[team]<=0:return False
  data=dict(ev.data)
  if ev.kind=='boundary' and not(data['scoring_play'] or data['major_foul']):return False
  wrong=ev.called!=ev.actual and (ev.kind=='keeper_immunity' or abs(ev.margin)>cfg.review_tolerance_m+1e-12)
  if not wrong:
   resources[team]-=1
   if timeouts[team]>0:timeouts[team]-=1
  else:
   self.close_restart('review_reversal');now=s.now;dead=s.dead_ms;history=list(self.rb.calls)
   self.rb_pause=None
   restored=copy.deepcopy(ev.before);s.__dict__.clear();s.__dict__.update(restored.__dict__);s.now=now;s.dead_ms=dead
   for k,v in ev.engine.items():
    if k.startswith('authority_'):setattr(self.rb,k[10:],copy.deepcopy(v))
    elif k=='scores':self.rb.scores=list(v)
    elif k=='quotas':self.rb.quotas=copy.deepcopy(v)
    else:setattr(self,k,copy.deepcopy(v))
   self.native_seen=len(self.log)
   if ev.kind in ('goal','no_goal'):
    if ev.actual:old_goal(self,data['defending'])
    elif s.ball.x < -s.ball.radius or s.ball.x > 100+s.ball.radius or s.ball.y < -s.ball.radius or s.ball.y > 100+s.ball.radius:old_boundary(self,s.ball.x,s.ball.y)
    else:self.award(s.owner or s.other(data['defending']),s.ball.x,s.ball.y,'review_corrected_no_goal',normalize=False)
   elif ev.kind=='boundary':
    if ev.actual:old_boundary(self,data['x'],data['y'],data.get('carrier'))
    else:self.award(s.owner or 'A',s.ball.x,s.ball.y,'review_corrected_in_bounds',normalize=False)
   elif ev.actual:old_foul(self,data['actor'],data['victim'],'protected_keeper')
   else:self.award(s.owner or s.players[data['victim']].team,s.ball.x,s.ball.y,'review_corrected_contact',normalize=False)
   port=getattr(self,'rb_port',None)
   if port:port.pending.clear();port.move.clear();port.keeper_intents.clear()
  self.rb_evidence.pop(call_id,None)
  row=self.rb.ruling('review',team=team,call_id=call_id,reversed=wrong,margin_m=ev.margin)
  self.emit('rb_review','RB-1',ruling=dict(row))
  return wrong
 E.rb_review=review

