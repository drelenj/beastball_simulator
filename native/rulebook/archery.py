"""RB quota, execution, swept relative collision and observable equipment status."""
import math

def install(co,cfg):
 E,M,T=co.engine.Engine,co.match.Match,co.types;P=T.Phase
 old_sync=E.native_sync;old_freeze=E.freeze
 v3=cfg.version=='native-rb/3'
 def sync(self):
  old_sync(self)
  team=self.possession.pp
  if team is not None and team!=self.rb.possession:
   self.rb_publish(self.rb.turnover(team))
   if v3:
    epoch=self.__dict__.setdefault('rb_quota_epoch',{'A':0,'B':0});epoch[self.s.other(team)]+=1
    # RB-3.5 ruling 2: an arrow in flight when possession changes is inert and stays spent.
    for ar in self.s.arrows:
     if ar.live:
      ar.live=False;self.emit('arrow_inert','RB-3.5',arrow=ar.id,player=ar.shooter,target=ar.target,reason='possession_change',refunded=False)
  if v3 and self.s.phase in (P.DEAD,P.FINAL):
   # RB-3.4 ruling 2: an arrow still in flight when the ball goes dead is inert and is not
   # charged to the Archer's quota (refunded only within the same possession quota).
   epoch=self.__dict__.setdefault('rb_quota_epoch',{'A':0,'B':0})
   for ar in self.s.arrows:
    if not ar.live:continue
    ar.live=False;refund=getattr(ar,'rb_epoch',None)==epoch[ar.team]
    if refund:self.rb.quotas[ar.team]['arrows']=max(0,self.rb.quotas[ar.team]['arrows']-1)
    self.emit('arrow_inert','RB-3.4',arrow=ar.id,player=ar.shooter,target=ar.target,reason='dead_ball_in_flight',refunded=refund)
  for t,q in self.s.quivers.items():
   q.allocation=cfg.arrows;q.spent=self.rb.quotas[t]['arrows'];q.loaded=cfg.arrows-q.spent
   self.freezes[t]=self.rb.quotas[t]['freezes']
 E.native_sync=sync
 def shoot(self,pid,target,velocity,origin=None):
  s=self.s;p=s.players[pid];t=s.players.get(target);quota=self.rb.quotas[p.team]
  if quota['arrows']>=cfg.arrows:return False
  if v3:
   self.native_sync()
   if s.phase in (P.DEAD,P.FLIGHT):
    # RB-3.4 ruling 2: released while the ball is dead: inert, no foul, not charged.
    # RB-3.5 ruling 2: the same for a release while a shot is in the air after the clock expired.
    s.quivers[p.team].last_release=s.now
    self.emit('arrow_inert','RB-3.4',player=pid,target=target,reason='dead_ball_release' if s.phase==P.DEAD else 'finishing_flight_release',refunded=True);return False
   # RB-3.4 rulings 1 and 3: judged at release; passive possession only (no team-control test).
   checks=dict(archer=p.role=='archer',archer_eligible=p.eligible(s.now),phase=s.phase==P.LIVE,hunt_not_cleared=self.hunt_cleared,
               stale_target=t is not None and t.role=='field' and t.team!=p.team,
               target_frozen=t is not None and not t.frozen(s.now),
               target_ineligible=t is not None and (t.frozen(s.now) or t.eligible(s.now)),
               target_immune=t is not None and s.now>t.immune_until,
               in_zone=t is not None and self.zone(t.x,t.y) is None,
               possession=t is not None and self.possession.pp==t.team)
   legal=all(checks.values())
   if not legal:self.emit('archery_target_diagnosis','RB-3.4-report',player=pid,target=target,failed=[k for k,v in checks.items() if not v],ball_status=self.possession.public().ball_status)
  else:
   legal=(p.role=='archer' and p.eligible(s.now) and s.phase==P.LIVE and self.hunt_cleared and t is not None and t.role=='field' and t.team!=p.team and t.eligible(s.now) and s.now>t.immune_until and self.zone(t.x,t.y) is None and self.possession.pp==t.team and self.possession.tc==t.team)
  row=self.rb.arrow(p.team,legal);self.rb_publish(row);self.native_sync()
  s.quivers[p.team].last_release=s.now
  if not legal:self.foul(pid,target if t else None,'archery_target');return False
  speed=math.sqrt(sum(v*v for v in velocity))
  if speed<=0:return False
  # Engine owns canonical projectile speed, with no obsolete30m/s cap.
  v=tuple(c*cfg.arrow_speed/speed for c in velocity);point=(p.x,p.y,cfg.platform_height+.72*p.a.height)
  ar=T.Arrow(self.next_arrow,p.team,pid,target,*point,*v,point,s.now);self.next_arrow+=1;s.arrows.append(ar)
  if v3:ar.rb_epoch=self.__dict__.setdefault('rb_quota_epoch',{'A':0,'B':0})[p.team]
  self.emit('arrow_release','RB-A',player=pid,target=target,arrow=ar.id,velocity=list(v),origin=list(point));return ar
 E.shoot_arrow=shoot
 def freeze(self,pid,arrow=None,panel=True,direct=True,in_range=True):
  p=self.s.players[pid];projectile=next((a for a in self.s.arrows if a.id==arrow),None)
  team=projectile.team if projectile else self.s.other(p.team)
  if not panel or p.frozen(self.s.now) or self.s.now<=p.immune_until or self.rb.quotas[team]['freezes']>=5:return False
  if self.zone(p.x,p.y) is not None:return False
  # Native wrapper also enforces Keeper and recovery protections.
  # Retain Native recovery/keeper admission, but its historical quota key
  # inferred the shooter from the victim. RB uses the actual projectile team.
  previous=dict(self.freezes);self.freezes[self.s.other(p.team)]=0
  try:ok=old_freeze(self,pid,arrow,panel,direct,True)
  finally:self.freezes.clear();self.freezes.update(previous)
  if ok:
   self.rb.quotas[team]['freezes']+=1
   for t in ('A','B'):self.freezes[t]=self.rb.quotas[t]['freezes']
   p.rb_recover=(p.x,p.y,p.freeze_until)
   self.rb_publish(self.rb.ruling('freeze',player=pid,until=p.freeze_until,immune_until=p.immune_until))
  return ok
 E.freeze=freeze
 def ready(self,p):
  r=getattr(p,'rb_recover',None)
  return not r or self.s.now>=r[2]+2000 and self.s.attack_sign(p.team)*(r[0]-p.x)>=3
 E.rb_recovery_ready=ready
 # The same rule applies at execution, including commands admitted before
 # a freeze. Recovery locomotion is permitted; ball/contact acts are not.
 def blocked(self,p):return self.zone(p.x,p.y) is not None and not self.rb_recovery_ready(p)
 E.rb_recovery_blocked=blocked
 from functools import wraps
 def gate(fn):
  @wraps(fn)
  def call(self,pid,*a,**kw):
   if self.rb_recovery_blocked(self.s.players[pid]):return False
   return fn(self,pid,*a,**kw)
  return call
 for name in ('acquire','touch','release','restart_release'):
  setattr(E,name,gate(getattr(E,name)))
 old_move=M.move_players
 def move(self,ms,targets):
  allowed=dict(targets)
  for p in self.s.players.values():
   if not p.active or self.e.rb_recovery_ready(p):continue
   aim=allowed.get(p.id,p.target)
   if aim is None:continue
   back=self.s.attack_sign(p.team)*(p.x-aim[0])>0
   enters=any(co.geometry.segment_distance(gx,50,p.x,p.y,*aim)[0]<cfg.zone_radius for gx in (0.,100.))
   if enters and not back:
    # Cancel prohibited propulsion; do not choose a new destination.
    allowed[p.id]=(p.x,p.y);p.target=(p.x,p.y);p.vx=p.vy=0.
  return old_move(self,ms,allowed)
 M.move_players=move
 def arrows(self,ms):
  s=self.s;events=[];dt=ms/1000;g=self.assume['gravity'];previous=getattr(self,'rb_previous_positions',{})
  for ar in s.arrows:
   if not ar.live:continue
   old=(ar.x,ar.y,ar.z);drag=math.exp(-self.assume['arrow_drag']*dt)
   ar.x+=ar.vx*dt;ar.y+=ar.vy*dt;ar.z+=ar.vz*dt-.5*g*dt*dt
   ar.vx*=drag;ar.vy*=drag;ar.vz=(ar.vz-g*dt)*drag;hits=[]
   for p in self.active_field():
    if not p.active:continue
    px,py,pz=previous.get(p.id,(p.x,p.y,p.z))
    distance,f=co.geometry.segment_distance(0,0,old[0]-px,old[1]-py,ar.x-p.x,ar.y-p.y)
    z=old[2]+(ar.z-old[2])*f-(pz+(p.z-pz)*f)
    if distance<p.radius+.045 and .12*p.a.height<=z<=p.a.height:
     # PLACEHOLDER panel witness: torso/thigh height band on body cylinder;
     # outer versus inner thigh has no retained anatomical witness.
     hits.append((f,p.id,.2*p.a.height<=z<=.8*p.a.height))
   b=s.ball
   if b.carrier is None:
    distance,f=co.geometry.segment3_distance((b.x,b.y,b.z),old,(ar.x,ar.y,ar.z))
    if distance<b.radius+.045:hits.append((f,'ball',False))
   if hits:
    f,target,panel=min(hits);ar.x,ar.y,ar.z=tuple(a+(b-a)*f for a,b in zip(old,(ar.x,ar.y,ar.z)))
    events.append(T.Event('impact',target=target,data={'arrow':ar.id,'panel':panel,'kind':'ball' if target=='ball' else 'player'},at=int(f*ms)))
    self.e.emit('arrow_geometry_impact','RB-A:swept_relative',arrow=ar.id,target=target,panel=panel)
   elif ar.z<=0 or not(-30<=ar.x<=130 and -40<=ar.y<=140):
    ar.live=False;self.e.emit('arrow_miss','RB-3.3-report',arrow=ar.id,position=[ar.x,ar.y,max(0,ar.z)]) # log only
  return events
 M.advance_arrows=arrows
