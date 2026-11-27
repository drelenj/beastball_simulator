"""Roster admission and forced injury hook. No stochastic injury model."""
def install(co,cfg):
 E,T=co.engine.Engine,co.types;P=T.Phase
 old_init=E.__init__
 def init(self,*args,**kw):
  old_init(self,*args,**kw);self.rb_slots={};self.rb_reserves={t:t+'13' for t in ('A','B')}
 E.__init__=init
 def can_enter(self,p):
  return p.available and not p.injured and self.rb.can_enter(p,self.s.live_ms) and p.exclusion_ms<=0
 E.rb_can_enter=can_enter
 def substitute(self,outgoing,incoming,role=None,setup=False,*,rotation_reason=None,rotation_tier=None):
  s=self.s;p=s.players.get(outgoing);q=s.players.get(incoming)
  # RB-3.3: the match now opens with the period-start scrimmage, not the Hunt.
  opening=(s.phase==P.OPENING and not self.rb_hunt_running) or getattr(self,'rb_period_start_open',False)
  dead=s.phase==P.DEAD or setup and opening
  if not dead or not q or q.active or not self.rb_can_enter(q):return False
  if p is None and not(setup and opening and s.period==1 and s.live_ms==0 and not self.rb.exclusions):return False
  if p and role is not None and role!=p.role:return False
  if p and (p.team!=q.team or not p.active and outgoing not in self.rb_slots):return False
  if p and p.exclusion_ms>0 and p.id not in self.rb.injuries and self.rb.evaluated.get(p.id)!=s.period:return False
  target_role=role or (p.role if p else 'field')
  if cfg.version=='native-rb/3' and target_role in ('keeper','archer') and q.role!=target_role:
   designated=getattr(self,'rb_designated',{}).get(q.team,{}).get(target_role,())
   if len(designated)!=2 or any(self.rb_can_enter(s.players[pid]) for pid in designated):return False
  count=sum(x.active and x.team==q.team and x.role!='archer' for x in s.players.values())
  removed=bool(p and p.active and p.role!='archer')
  if target_role!='archer' and count-removed>=cfg.field_roster_limit:return False
  if target_role=='archer' and any(x.active and x.team==q.team and x.role=='archer' and x is not p for x in s.players.values()):return False
  if p:p.active=False
  q.active=True;q.role=target_role;q.slot=p.slot if p else q.slot
  q.x,q.y=(p.x,p.y) if p else (s.ends[q.team]+s.attack_sign(q.team)*30,50.)
  q.z=q.vx=q.vy=q.vz=0.;q.posture='upright';q.target=(q.x,q.y);q.c4c_plan=q.c4c_launch=None
  if p:
   self.rb_slots.pop(p.id,None)
   if s.restart:
    if s.restart.taker==p.id:s.restart.taker=None
    if s.restart.rs.get('snapper')==p.id:s.restart.rs['snapper']=None
  self.rb_publish(self.rb.ruling('substitution',outgoing=outgoing,incoming=incoming,role=target_role,injury_exempt=bool(p and (p.id in self.rb.injuries or self.rb.evaluated.get(p.id)==s.period))))
  port=getattr(self,'rb_port',None)
  if port:
   rotation=getattr(port,'rotation',None)
   if rotation and p:
    rotation.log_swap(p,q,rotation_reason or 'required_cover',rotation_tier or 'designated_role')
   for pid in (outgoing,incoming):
    port.pending.pop(pid,None);port.move.pop(pid,None);port.keeper_intents.pop(pid,None)
   port.platform_motor(0)
  return True
 E.rb_substitute=substitute
 def fill(self):
  s=self.s
  if s.phase!=P.DEAD:return
  for pid,slot in list(self.rb_slots.items()):
   if s.live_ms<slot['until'] and not slot.get('injury'):continue
   role=slot['role'];team=slot['team']
   candidates=[q for q in s.players.values() if q.team==team and not q.active and self.rb_can_enter(q)]
   if cfg.version=='native-rb/3' and role in ('keeper','archer'):
    candidates=[q for q in candidates if q.role==role]
   # PLACEHOLDER team selection: named reserve Keeper, else canonical ID; no ratings.
   candidates.sort(key=lambda q:(0 if role=='keeper' and q.id==self.rb_reserves[team] else 1,q.id))
   if candidates:self.rb_substitute(pid,candidates[0].id,role)
   elif cfg.version=='native-rb/3' and role in ('keeper','archer'):
    designated=getattr(self,'rb_designated',{}).get(team,{}).get(role,())
    if len(designated)==2 and all(not self.rb_can_enter(s.players[pid]) for pid in designated):
     field=next((q for q in sorted(s.players.values(),key=lambda q:q.id) if q.team==team and not q.active and q.role=='field' and self.rb_can_enter(q)),None)
     if field:self.rb_substitute(pid,field.id,role);continue
     candidate=next((q for q in sorted(s.players.values(),key=lambda q:q.id) if q.active and q.team==team and q.role=='field'),None)
     if candidate:
      candidate.role=role;self.rb_slots.pop(pid,None)
      self.rb_publish(self.rb.ruling('specialist_fallback',player=candidate.id,role=role))
      port=getattr(self,'rb_port',None)
      if port:port.platform_motor(0)
   elif role=='keeper':
    candidate=next((q for q in sorted(s.players.values(),key=lambda q:q.id) if q.active and q.team==team and q.role=='field'),None)
    if candidate:
     candidate.role='keeper';self.rb_slots.pop(pid,None)
     self.rb_publish(self.rb.ruling('keeper_fallback',player=candidate.id))
 E.rb_fill_slots=fill
 def injury(self,pid,head=False):
  s=self.s
  if s.phase==P.FINAL:return False
  p=s.players[pid];self.rb.injury(p,head);p.injured=True
  self.rb_slots[pid]=dict(team=p.team,role=p.role,until=s.live_ms,injury=True)
  owner=self.possession.pp or s.owner or p.team;play=s.possession_ms
  if s.phase!=P.DEAD:self.award(owner,s.ball.x,s.ball.y,'injury',normalize=False)
  elif s.restart:
   if s.restart.taker==pid:s.restart.taker=None
   if s.restart.rs.get('snapper')==pid:s.restart.rs['snapper']=None
  s.possession_ms=play
  self.rb_publish(self.rb.ruling('head_evaluation' if head else 'injury',player=pid))
  self.rb_fill_slots();return True
 E.rb_force_injury=injury
 old_period=E.end_period
 def end_period(self):
  old_period(self)
  for pid,period in self.rb.evaluated.items():
   if period<self.s.period:self.s.players[pid].injured=False
 E.end_period=end_period
 def invariants(self):
  s=self.s;b=s.ball
  assert s.game_ms>=0 and s.possession_ms>=0
  assert not(b.carrier and b.contested)
  if b.carrier:assert b.mode==T.BallMode.CONTROLLED and s.players[b.carrier].eligible(s.now)
  if s.phase==P.DEAD:assert s.restart is not None or self.rb_pause is not None
  for team in ('A','B'):
   assert sum(p.active and p.team==team and p.role!='archer' for p in s.players.values())<=cfg.field_roster_limit
   assert sum(p.active and p.team==team and p.role=='archer' for p in s.players.values())<=1
  for q in s.quivers.values():assert 0<=q.spent<=q.allocation and 0<=q.loaded<=q.allocation
  return True
 E.assert_invariants=invariants
