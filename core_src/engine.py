"""Deterministic legal state transitions. Stochastic execution belongs in match.py.
All official time is integer milliseconds. Events at an identical time are grouped.
"""
import math,hashlib,json
from dataclasses import asdict
from .types import *
from .geometry import norm,zone,restart_point,legal_goal,clamp

RULES={'acquire':'1.5–1.9;5.2','pass':'4.4–4.5','tackle':'6.4–6.7','freeze':'7.1–7.4','boundary':'9.1;10.1–10.6','goal':'9.1–9.3;16.2','foul':'11;12;15','restart':'10.2–10.5','clock':'5;16.6','sub':'14.1–14.3','opening':'4.1–4.3','period':'18.1–18.4'}
class RulesError(Exception):pass
class MatchFinal(BaseException):
 """C4.0: raised by Engine.complete once the result is committed. It unwinds every engine call in progress, so that no line
 after the commitment runs. It is caught at the outermost engine call (see the guard at the end of this file) and never
 reaches the caller. It is not an error and is not an Exception, so no handler meant for errors can swallow it part-way."""

class Engine:
 def __init__(self,state=None,config=None):
  self.s=state or MatchState();self.config=config or {};self.log=[];self.event_seq=0
  if self.config.get('ruleset','1.0.1')not in('1.0.1','1.0.2'):raise RulesError('Unknown ruleset; source behavior must not be silently selected')
  self.pending_discipline=[];self.debts=[];self.cause=None;self.last_progress=None
  self.review_snapshot=None;self.score_history=[];self.next_arrow=1
  self.pocket=self.config.get("pocket",{});self.play_ms=int(self.pocket.get("play_clock",45)*1000)
  self.s.keeper_zone_radius=self.pocket.get("keeper_zone_radius",20)
  self.period_history=[];self.opening_ref_ms=0;self.metrics={}
  self.c3=bool(self.config.get('assumptions',{}).get('c3_contact',0)) #C3a: contact kernel. Off = the C2m3 engine, speed offences included.
  self.c3b=False;self.assume={};self.grace=[] #C3b: the Match sets c3b and the merged assumptions straight after construction
  self.c3c=False;self.blind_cos=.25 #C3c: the Match sets these. blind_cos is the cosine of the half-angle of the rear cone; 0.25 is the retained Pocket 1.1 line
  #C2 rule options. With all three off the engine behaves as C1 revision 3.
  self.c2_tackles=int(self.pocket.get('tackles_per_possession',1))>=2;self.c2_inbound=bool(self.pocket.get('zone_inbound',False))
  self.vacated={'A':[],'B':[]};self.vacated_keep={'A':[],'B':[]};self.c2_occ=bool(self.pocket.get('zone_marking',False));self.c2_any=self.c2_tackles or self.c2_inbound or self.c2_occ;self.mark_d=float(self.pocket.get('marking_distance',3.));self.mark_off=float(self.pocket.get('inbound_mark_offset',8.))
  #C4.0 terminal processing. final_seq is the id of the record that committed the result; final_refused counts what was asked
  #of the engine afterwards and refused. terminal_grounds holds grounds for ending the match raised while several sanctions of
  #one stoppage are being administered (terminal_hold), so that they are judged together and not in the order of a loop.
  self.final_seq=None;self.final_refused={};self.depth=0;self.terminal_hold=0;self.terminal_grounds=[]
  #C4.0 Keeper Zone ruling. The Match sets these from CALIBRATION. c4_zone: no personal sanction for a zone expiry.
  #c4_occ: the defensive consequences (needs zone marking). zone_direct: the proposed direct penalty, experimental, off.
  self.c4_zone=False;self.c4_occ=False;self.zone_direct=False
  self.c4b=False #C4b: the Match sets it
  self.c4c=False #C4c: the Match sets it
  self.c4c2=False;self.reversal_rule=0 #C4c2: the Match sets them
 def count(self,key,n=1):
  cs=getattr(self,'contact_stats',None)
  if cs is not None:cs[key]+=n
 def zone(self,x,y):
  return zone(x,y,self.s.keeper_zone_radius)
 def territory(self,team,x,y):
  if not(0<=x<=100 and 0<=y<=100):return 'outside_release'
  d=norm(x-self.s.attack_goal(team),y-50)
  if self.c4c2:
   #C4c2, decided by DreLen on 9 October: a line belongs to the farther scoring territory. On the inner arc: a zone release; on the
   #Keeper Zone arc: an outside release. (This supersedes the specification's deeper-territory convention.) The end line is not
   #settled by this ruling: the field test above and the eligibility rule are kept as they were.
   if d<self.pocket.get('inner_zone_radius',5):return 'inner_release'
   if d<self.s.keeper_zone_radius:return 'inside_release'
   return 'outside_release'
  if d<=self.pocket.get('inner_zone_radius',5):return 'inner_release'
  if d<=self.s.keeper_zone_radius:return 'inside_release'
  return 'outside_release'
 def territory_points(self,method):
  return self.pocket.get({'inner_release':'inner_points','inside_release':'release_points','outside_release':'outside_points'}[method],3)
 def emit(self,event,rule,**data):
  if self.final_seq is not None:
   #C4.0: the log of a completed match is closed. This is a backstop; the engine's own paths do not reach it.
   self.final_refused['emit:'+event]=self.final_refused.get('emit:'+event,0)+1;return self.event_seq
  s=self.s;self.event_seq+=1
  rec={'id':self.event_seq,'live_ms':s.live_ms,'t_ms':s.now,'period':s.period,'g_ms':s.game_ms,'p_ms':s.possession_ms,'phase':s.phase.value,'owner':s.owner,'carrier':s.ball.carrier,'ball_mode':s.ball.mode.value,'ball':[round(s.ball.x,3),round(s.ball.y,3),round(s.ball.z,3)],'score':dict(s.score),'event':event,'rule':rule,'cause':self.cause,'data':data}
  self.log.append(rec);return self.event_seq
 def eligible(self,p,ball_action=True):
  if not p.eligible(self.s.now):return False
  if p.role=='archer':return not ball_action
  if p.posture!='airborne'and not(0<=p.x<=100 and 0<=p.y<=100):return False
  if self.s.penalty is not None and p.id not in (self.s.penalty['runner'],self.s.penalty['keeper']):return False
  if self.s.phase==Phase.FLIGHT and p.team==self.s.tail_owner:return False
  return True
 def live(self):return self.s.phase in (Phase.LIVE,Phase.AWARD,Phase.OPENING)
 def new_owner(self,team,reason):
  s=self.s
  changed=s.owner!=team
  if changed:
   s.award_spot=None;s.award_available=None;s.award_deadline=None
   previous=s.owner;s.owner=team;s.possession_ms=self.play_ms
   self.emit('possession_change','1.6;5.2',previous=previous,team=team,reason=reason)
   self.c2_new_possession(previous,team,reason)
  if s.opening_team is None:
   s.opening_team=team;s.alternate=s.other(team)
  return changed
 def c2_new_possession(self,previous,team,reason):
  """C2: a new team possession. Tackle count returns to zero, reconstruction and any first-tackle recovery end,
  and every stored zone count and unmarked allowance is cleared for both teams."""
  s=self.s;s.tackle_count=0;s.zone_violations=0;s.tackle_ordinal=0 #C4.0: the defensive zone-violation counter and the tackle ordinal belong to the possession
  if s.recovery:self.emit('recovery_failed','C2-3.1',reason=reason);s.recovery=None
  if s.reconstruction:self.end_reconstruction('goal'if reason=='goal'else'opposing_possession')
  if self.c2_occ:
   stored=0;adv=s.advantage
   if adv and'c2'in adv and adv['team']==previous and'keep'not in adv['c2']:
    #The advantaged team has lost the ball inside its advantage. Keep what is about to be cleared, in case the advantage is recalled.
    adv['c2']['keep']={p.id:(list(p.zone_ms),list(p.unmarked_ms),list(p.zone_fouled))for p in s.players.values()}
    if self.c3b:
     #C3b: a slot left empty by an exclusion or injury has state waiting for whoever fills it. That is part of what is about to be cleared.
     for tm in('A','B'):
      for i,st in enumerate(self.vacated[tm]):
       if self.vacated_keep[tm][i]is None:self.vacated_keep[tm][i]=(adv['c2']['keep'],tuple(list(x)for x in st))
   if self.c3b:self.vacated={tm:[([0,0],[0,0],[0,0])for _ in self.vacated[tm]]for tm in('A','B')} #the waiting slots stay (their kept record needs them); their counts are cleared
   else:self.vacated={'A':[],'B':[]}
   for p in s.players.values():
    if p.zone_ms[0]or p.zone_ms[1]or p.unmarked_ms[0]or p.unmarked_ms[1]:stored+=1
    if self.c4_occ:
     for j in(0,1):
      if p.zone_fouled[j]:self.emit('zone_compliance','C4.0-zone',player=p.id,zone=j,how='possession_ended',ms_before_deadline=p.zone_fouled[j]-s.live_ms)
    p.zone_ms=[0,0];p.unmarked_ms=[0,0];p.zone_fouled=[0,0]
   self.emit('occupancy_cleared','C2-5',team=team,previous=previous,reason=reason,players_with_stored_time=stored)
 def end_reconstruction(self,reason):
  s=self.s;r=s.reconstruction;s.reconstruction=None
  self.emit('reconstruction_ended','C2-4.2',team=r['team'],zone=r['zone'],reason=reason,live_ms_uncleared=s.live_ms-r['live_since'])
 def slot_inherit(self,o,n):
  """C2: n takes over o's slot: stored zone counts, unmarked allowance, pending violation and any record kept for a pending
  advantage. No arc exit is invented: the newcomer's location is observed afresh."""
  n.zone_ms=list(o.zone_ms);n.unmarked_ms=list(o.unmarked_ms);n.zone_fouled=list(o.zone_fouled);n.zone_loc=[None,None]
  keep=self.s.advantage['c2'].get('keep')if self.s.advantage and'c2'in self.s.advantage else None
  if keep and o.id in keep:keep[n.id]=keep.pop(o.id)
 def slot_vacate(self,p):
  #A field slot emptied by exclusion or injury: its state waits for whoever fills the slot.
  if self.c2_occ:
   self.vacated[p.team].append((list(p.zone_ms),list(p.unmarked_ms),list(p.zone_fouled)))
   #C3b: any record kept for a pending advantage leaves with the slot, not with the excluded or injured athlete
   keep=self.s.advantage['c2'].get('keep')if self.c3b and self.s.advantage and'c2'in self.s.advantage else None
   self.vacated_keep[p.team].append((keep,keep.pop(p.id))if keep and p.id in keep else None)
   if self.c3b:p.zone_ms=[0,0];p.unmarked_ms=[0,0];p.zone_fouled=[0,0] #the state belongs to the slot now; the athlete who has left it carries none
 def slot_fill(self,n):
  if not self.c2_occ:return
  v=self.vacated[n.team];st=v.pop(0)if v else([0,0],[0,0],[0,0])
  n.zone_ms,n.unmarked_ms,n.zone_fouled=[list(x)for x in st];n.zone_loc=[None,None]
  vk=self.vacated_keep[n.team];kept=vk.pop(0)if vk else None
  keep=self.s.advantage['c2'].get('keep')if self.s.advantage and'c2'in self.s.advantage else None
  if kept is not None and keep is not None and kept[0]is keep:keep[n.id]=tuple(list(x)for x in kept[1]) #C3b: the newcomer holds the slot's kept record while that advantage is pending
 def c2_snapshot(self):
  #C2: the continuation state at a foul instant, kept with an advantage so that a failed advantage restores it.
  s=self.s
  return{'count':s.tackle_count,'recon':dict(s.reconstruction)if s.reconstruction else None,'zone_violations':s.zone_violations,'ordinal':s.tackle_ordinal} #C4.0: the violation counter and tackle ordinal are part of the foul instant
 def c2_restore(self,adv,changed,cause):
  """C2: a failed advantage returns play to the foul instant: tackle count and reconstruction. Zone counts follow what the
  players actually did. If possession did not change hands they were never cleared and are left alone. If it did, the counts
  held when the advantaged team lost the ball are returned (adv['c2']['keep']), less any lawful in-field arc exit made since,
  which occupancy() removes from that record as it happens. An end-line exit removes nothing. The record follows the slot
  through substitution and specialist replacement."""
  snap=adv.get('c2');s=self.s
  if not snap:return
  was=s.tackle_count;s.tackle_count=snap['count']
  if was!=snap['count']:self.emit('tackle_count_restored','C2-5',count_from=was,count_to=snap['count'],cause=cause)
  s.zone_violations=snap.get('zone_violations',0);s.tackle_ordinal=snap.get('ordinal',0) #C4.0: a violation called at or before the foul instant is still on the count after a recall; its remedy is not given twice
  if s.reconstruction and not snap['recon']:self.end_reconstruction('advantage_restored')
  elif snap['recon']and not s.reconstruction:s.reconstruction=dict(snap['recon']);self.emit('reconstruction_restored','C2-4.2',team=snap['recon']['team'],zone=snap['recon']['zone'],cause=cause)
  keep=snap.get('keep')
  if self.c2_occ and keep is not None:
   #A kept record exists only because a turnover inside the advantage cleared the counts. It is given back whoever holds the ball
   #at the recall, including when the advantaged team has won it back (A to B to A): that second change cleared the counts again.
   for p in s.players.values():
    if p.id in keep:p.zone_ms,p.unmarked_ms,p.zone_fouled=[list(v)for v in keep[p.id]]
   for tm in('A','B'):
    for i,kept in enumerate(self.vacated_keep[tm]):
     #C3b: a slot still empty at the recall gets its kept state back, to be handed to whoever fills it
     if kept is not None and kept[0]is keep:self.vacated[tm][i]=tuple(list(x)for x in kept[1]);self.vacated_keep[tm][i]=None;self.emit('vacant_slot_state_returned','C3b-9',team=tm,zone_ms=list(kept[1][0]),unmarked_ms=list(kept[1][1]))
  if changed:
   if not s.extension:s.possession_ms=min(self.play_ms,max(20000,adv['p'])) #the restored clock with the defensive-foul floor, not a fresh clock
  self.emit('advantage_state_restored','C2-5',cause=cause,tackle_count=s.tackle_count,possession_changed_during_advantage=changed,zone_counts_returned=keep is not None,p_ms=s.possession_ms,**({'zone_violations':s.zone_violations}if self.c4_occ else{}))
 def reconstruction_check(self,p,witness):
  """C2: reconstruction clears on live eligible attacking play by a player whose pelvis is inside the field and
  strictly outside the attacked zone. The ball need not have left the zone."""
  s=self.s;r=s.reconstruction
  if not r or p.team!=r['team']or not self.eligible(p)or p.posture=='grounded':return False
  if not(0<=p.x<=100 and 0<=p.y<=100)or self.zone(p.x,p.y)==r['zone']:return False
  s.reconstruction=None;self.count('reconstructions_cleared')
  self.emit('reconstruction_cleared','C2-4.2',player=p.id,witness=witness,pelvis=[round(p.x,3),round(p.y,3)],live_ms_uncleared=s.live_ms-r['live_since']);return True
 def begin_hunt(self):
  s=self.s;s.phase=Phase.OPENING;s.owner=None;s.possession_ms=self.play_ms;s.ball=Ball(mode=BallMode.LOOSE,x=50,y=50,z=.1075,scoring=False)
  s.opening_touched=False;s.opening_deadline=s.now+10000
  for team,pid in zip(('A','B'),s.opening_contestants):
   p=s.players[pid];p.x=42 if team=='A'else 58;p.y=50;p.vx=p.vy=0
  self.emit('opening_ground_touch','4.2',contestants=s.opening_contestants)
 def failed_hunt(self,reason):
  s=self.s;s.opening_failures+=1
  if s.opening_failures>=2:
   team=s.other(s.hunt_choice_team);self.award(team,50,50,'opening_fallback');s.opening_deadline=None
  else:self.begin_hunt()
  self.emit('opening_failed','4.3',reason=reason,count=s.opening_failures)
 def acquire(self,pid,forced_joint=False):
  s=self.s;p=s.players[pid];b=s.ball
  if s.phase==Phase.FLIGHT:
   if p.team!=s.tail_owner and self.eligible(p):self.end_flight('defensive_control',p.x,p.y)
   else:self.end_flight('offensive_touch',p.x,p.y)
   return True
  if not self.live()and s.phase!=Phase.PENALTY:return False
  if not self.eligible(p):self.illegal(pid,'ineligible_ball_action');return False
  if p.role=='archer':self.illegal(pid,'archer_body_ball');return False
  if b.carrier is not None:return b.carrier==pid
  if b.last_releaser==pid:self.illegal(pid,'self_recontact');return False
  if s.phase==Phase.AWARD and p.team!=s.owner:self.illegal(pid,'exclusive_recovery');return False
  if s.phase==Phase.PENALTY and pid==s.penalty['keeper']:
   self.emit('penalty_save','12.4',player=pid);self.finish_penalty(0);return True
  if s.extension and s.owner is not None and p.team!=s.extension_team:
   self.emit('extension_turnover','16.6',player=pid);self.end_period();return True
  if s.phase==Phase.OPENING and not s.opening_touched and pid not in s.opening_contestants:
   self.illegal(pid,'premature_opening');return False
  ox,oy=(p.c4c_launch['off'][0],p.c4c_launch['off'][1])if self.c4c and getattr(p,'c4c_launch',None)else(0.,0.) #C4c: at full stretch in a dive his hands are out along it
  if math.hypot(b.x-p.x-ox,b.y-p.y-oy)>p.a.reach+p.radius+.2 or not(p.z-.2<=b.z<=p.z+p.a.height+p.a.reach):return False
  if s.recovery and p.posture=='grounded':return False #C2: a grounded player, the tackled carrier included, recovers the ball only after becoming upright
  if self.c4_occ and p.team!=s.owner and self.zone_intervention(p,'control'):return False
  self.new_owner(p.team,'control');s.phase=Phase.LIVE if s.phase!=Phase.PENALTY else Phase.PENALTY
  b.version+=1;b.mode=BallMode.CONTROLLED;b.carrier=pid;b.control_time=s.now;b.scoring=True;b.last_touch=p.team;b.last_releaser=None;b.contested=();s.contested_until=None
  if self.c4c2:b.pocket_release_team=p.team;b.c4c2_def=[];b.c4c2_off=pid;b.c4c2_off_i=0 #C4c2: secured control ends the old flight; his team owns whatever follows
  s.opening_deadline=None;s.opening_touched=True;s.award_deadline=None
  self.follow_carrier();self.emit('control','1.5;5.2',player=pid)
  if s.recovery:
   #C2: pickup ends first-tackle protection at once. No post-pickup immunity.
   self.emit('recovery_pickup','C2-3.1',player=pid,elapsed_ms=s.now-s.recovery['started'],replacement=bool(s.recovery.get('replacement')));s.recovery=None;s.award_spot=None;s.award_available=None
  self.reconstruction_check(p,'secure_control')
  if p.posture=='grounded':self.grounded(pid)
  return True
 def c1_reason(self,event):
  """C1: why a proposed contact cannot be accepted at this instant, or None. The same conditions the kernel
  applied when it proposed the contact, tested again against the state at the moment of commitment."""
  s=self.s;b=s.ball;p=s.players[event.actor]
  if b.carrier is not None:return'ball_controlled'
  if b.mode==BallMode.CONTESTED:return'ball_contested'
  if s.phase not in(Phase.LIVE,Phase.OPENING,Phase.AWARD,Phase.FLIGHT,Phase.PENALTY):return'play_stopped'
  if event.data.get('c4c_kind')=='body':
   if not self.c4c2:return None #C4c: the ball meeting the Keeper's body is physics, not a play: no eligibility test
   #C4c2: the body is passive (grounded, frozen, in a recovery: it still stops the ball), but it must still be on the field and
   #taking part in this phase: the same participation tests the kernel applied when it proposed the contact.
   if not p.active:return'not_available'
   if s.penalty is not None and p.id not in(s.penalty['runner'],s.penalty['keeper']):return'not_a_penalty_participant'
   if s.phase==Phase.FLIGHT and p.team==s.tail_owner:return'finishing_flight'
   if s.phase==Phase.OPENING and not s.opening_touched and p.id not in s.opening_contestants:return'premature_opening'
   if s.phase==Phase.AWARD and p.team!=s.owner:return'exclusive_recovery'
   if b.last_releaser==p.id:return'own_release'
   return None
  if not p.eligible(s.now):return'frozen'if p.active and p.frozen(s.now)else'not_available'
  if not self.eligible(p):return'not_eligible_here'
  if p.posture=='grounded':return'grounded'
  if s.now<p.next_action:return'cooldown'
  if b.last_releaser==p.id:return'own_release'
  if s.phase==Phase.AWARD and p.team!=s.owner:return'exclusive_recovery'
  if s.phase==Phase.OPENING and not s.opening_touched and p.id not in s.opening_contestants:return'premature_opening'
  return None
 def c1_reject(self,event,why):
  self.emit('contact_rejected','assumption:c1_contact',player=event.actor,kind=event.kind,reason=why)
  cs=getattr(self,'contact_stats',None)
  if cs is not None:cs['contacts_rejected']+=1
  return False
 def c1_commit(self,event):
  """C1: commit a proposed contact. Returns True only if the action was accepted. Ball position, velocity,
  observation reset, resume flag, cooldown and statistics are applied together and only then. A rejected
  proposal changes nothing and is logged as contact_rejected with its reason."""
  s=self.s;b=s.ball;d=event.data;p=s.players[event.actor];why=self.c1_reason(event)
  if why is None and event.kind=='acquire':
   keep=(b.x,b.y,b.z);b.x,b.y,b.z=d['ball_point']
   if not self.acquire(event.actor):b.x,b.y,b.z=keep;why='not_in_control_range'
  if why is not None:return self.c1_reject(event,why)
  cs=getattr(self,'contact_stats',None)
  if event.kind=='touch':
   deliberate=d.get('deliberate',True)
   if s.phase==Phase.FLIGHT:
    c2=self.c4c2_flight_touch(p,deliberate)if self.c4c2 else None #C4c2 review: recorded as a defensive touch of the flight
    self.emit('touch','1.5;4.5',player=p.id,deliberate=deliberate,tail_flight=True,**({'scoring_flight':c2}if c2 else{}))
   else:self.touch(p.id,deliberate)
   b.x,b.y,b.z=d['ball_point'];b.vx,b.vy,b.vz=d['velocity'];b.version+=1;b.course_time=s.now;b.resume=True
   if self.c4c2:p.next_action=max(p.next_action,s.now+d.get('cooldown_ms',0)) #C4c2: a contact never shortens a recovery (a grounding, a landing) already being served
   else:p.next_action=s.now+d.get('cooldown_ms',0)
   if cs is not None and d.get('keeper_block'):cs['keeper_blocks']+=1
  if self.c4c and d.get('c4c_kind'):self.emit('keeper_contact','C4c-K',player=p.id,kind=d['c4c_kind'],ball_point=[round(c,3)for c in d['ball_point']],deliberate=d.get('deliberate',True),
                                              **({'velocity_in':d.get('c4c_vin'),'velocity_out':[round(c,3)for c in d['velocity']],'normal':d.get('c4c_normal'),'hand_velocity':d.get('c4c_hand_v'),'secure_p':d.get('c4c_secure_p')}if event.kind=='touch'else{}))
  if cs is not None:cs['contacts_committed']+=1
  return True
 def follow_carrier(self):
  s=self.s;b=s.ball
  if b.carrier:
   p=s.players[b.carrier];sgn=s.attack_sign(p.team);offset=.35+.35*p.a.reach
   b.x=p.x+sgn*offset;b.y=p.y;b.z=p.hand_height;b.vx=p.vx;b.vy=p.vy;b.vz=p.vz
 def touch(self,pid,deliberate=True):
  s=self.s;p=s.players[pid];b=s.ball
  if s.phase==Phase.FLIGHT:
   if p.team==s.tail_owner:self.end_flight('offensive_touch',b.x,b.y)
   elif self.c4c2:self.c4c2_flight_touch(p,deliberate) #C4c2 review
   return
  if not self.live()and s.phase!=Phase.PENALTY:return
  if deliberate and(not self.eligible(p)or p.posture=='grounded'):
   self.illegal(pid,'ineligible_touch');return
  if b.last_releaser==pid:
   self.illegal(pid,'self_recontact');return
  if self.c4_occ and p.team!=s.owner and(deliberate or b.mode==BallMode.SHOT)and self.zone_intervention(p,'block_shot'if b.mode==BallMode.SHOT else'play_ball'):return
  b.last_touch=p.team;c2=None
  if self.c4c2:c2=self.c4c2_touch(p,deliberate)
  elif deliberate:
   b.scoring=True;b.last_releaser=None;b.pocket_origin=(p.x,p.y);b.pocket_release_team=p.team;self.reconstruction_check(p,'deliberate_play')
   if self.c4b:self.c4b_set_origin(p) #C4b: a deliberate touch (a tip) establishes the origin by the same foot rule
  s.opening_touched=True
  self.emit('touch','1.5;4.5',player=pid,deliberate=deliberate,**({'scoring_flight':c2}if c2 else{}))
 def c4c2_snap(self):
  b=self.s.ball;cp=lambda v:list(v)if isinstance(v,list)else dict(v)if isinstance(v,dict)else v
  return{k:cp(getattr(b,k,None))for k in('pocket_release_team','pocket_origin','c4b_origin','c4b_launch','c4c2_def','c4c2_off','c4c2_off_i')}
 def c4c2_unsnap(self,snap,actors):
  b=self.s.ball
  for k,v in snap.items():setattr(b,k,v)
  ft=snap['pocket_release_team']
  for pid in actors:
   q=self.s.players[pid]
   if ft is None:continue
   if q.team!=ft:
    xy=self.c4b_origin(q)[0]if self.c4b else(q.x,q.y);b.c4c2_def=list(b.c4c2_def or[])+[(q.id,round(xy[0],3),round(xy[1],3),True)]
   else:
    b.pocket_origin=(q.x,q.y)
    if self.c4b:self.c4b_set_origin(q)
    b.c4c2_off=q.id;b.c4c2_off_i=len(b.c4c2_def or[])
 def c4c2_flight_touch(self,p,deliberate):
  #a touch in the finishing flight by the team that does not own it is a defensive touch of that flight
  b=self.s.ball;ft=getattr(b,'pocket_release_team',None)
  if b.scoring and ft is not None and p.team!=ft:
   xy=self.c4b_origin(p)[0]if self.c4b else(p.x,p.y);b.c4c2_def=list(getattr(b,'c4c2_def',None)or[])+[(p.id,round(xy[0],3),round(xy[1],3),bool(deliberate))];return'defensive_touch_origin_kept'
  return None
 def c4c2_touch(self,p,deliberate):
  """C4c2, decided by DreLen on 9 October. While a scoring flight is under way (the ball is scoring and has a flight team, the team
  that released or last secured it), a touch by the other team, deliberate or not, a Keeper's parry included, is a defensive touch:
  the flight, its team and its offensive origin are kept. A touch by the flight team, deliberate or not, moves the offensive origin
  to that player's support foot (the last offensive player to touch the ball). With no scoring flight, a deliberate touch starts a
  new flight, as before. Flight team, offensive origin and last touch are kept as separate state."""
  b=self.s.ball;ft=getattr(b,'pocket_release_team',None)
  if b.scoring and ft is not None:
   if deliberate:b.last_releaser=None;self.reconstruction_check(p,'deliberate_play')
   if p.team!=ft:
    xy=self.c4b_origin(p)[0]if self.c4b else(p.x,p.y)
    b.c4c2_def=list(getattr(b,'c4c2_def',None)or[])+[(p.id,round(xy[0],3),round(xy[1],3),bool(deliberate))]
    return'defensive_touch_origin_kept'
   b.pocket_origin=(p.x,p.y)
   if self.c4b:self.c4b_set_origin(p)
   b.c4c2_off=p.id;b.c4c2_off_i=len(getattr(b,'c4c2_def',None)or[]);return'offensive_touch_origin_moved' #defensive touches before this one no longer make a reversal
  if deliberate:
   b.scoring=True;b.last_releaser=None;b.pocket_origin=(p.x,p.y);b.pocket_release_team=p.team;self.reconstruction_check(p,'deliberate_play')
   if self.c4b:self.c4b_set_origin(p)
   b.c4c2_def=[];b.c4c2_off=p.id;b.c4c2_off_i=0;return'new_flight'
  return None
 def release(self,pid,velocity,kind='pass',target=None,forced=False):
  s=self.s;b=s.ball;p=s.players[pid]
  if b.carrier!=pid:return False
  if not forced and(not self.eligible(p)or p.posture=='grounded' or s.phase not in (Phase.LIVE,Phase.PENALTY)):
   self.illegal(pid,'illegal_release');return False
  speed=math.sqrt(sum(v*v for v in velocity))
  if not forced and speed>self.pocket.get("ball_limit",40)+1e-6:self.illegal(pid,'ball_release_speed');return False
  self.follow_carrier();b.version+=1;b.carrier=None;b.vx,b.vy,b.vz=velocity;b.mode={'pass':BallMode.PASS,'kick':BallMode.KICK,'shot':BallMode.SHOT}.get(kind,BallMode.LOOSE)
  b.pocket_origin=(p.x,p.y);b.pocket_release_team=p.team
  c4o=self.c4b_set_origin(p)if self.c4b else None #C4b: the support foot at the instant of release
  b.release_time=s.now;b.last_releaser=None if forced else pid;b.last_touch=p.team;b.scoring=not forced;b.intended=target
  if self.c4c2:b.c4c2_def=[];b.c4c2_off=pid;b.c4c2_off_i=0 #C4c2: a release begins a new flight with its own identity and origin
  s.award_spot=None;s.award_available=None
  if not forced:
   p.keeper_hold_ms=0
   if kind=='shot'and s.advantage and s.advantage['team']==p.team:s.advantage=None;self.emit('advantage_realized','11.2',method='voluntary_shot')
  self.emit('release','4.4–4.5;7.3'if forced else'4.4–4.5;3.1',player=pid,kind=kind,forced=forced,velocity=list(velocity),target=target,**({'origin':c4o}if c4o else{}))
  if s.phase==Phase.PENALTY:s.penalty['released']=True
  return True
 def strike(self,pid,velocity,kind='kick'):
  s=self.s;p=s.players[pid];b=s.ball
  if not self.live()or b.carrier is not None:return False
  if not self.eligible(p)or p.posture=='grounded':self.illegal(pid,'ineligible_touch');return False
  if b.last_releaser==pid:self.illegal(pid,'self_recontact');return False
  if math.dist((b.x,b.y),(p.x,p.y))>p.a.reach+p.radius:return False
  if math.sqrt(sum(v*v for v in velocity))>self.pocket.get("ball_limit",40)+1e-6:self.illegal(pid,'ball_release_speed');return False
  ft=getattr(b,'pocket_release_team',None);defk=self.c4c2 and b.scoring and ft is not None and p.team!=ft
  b.version+=1;b.vx,b.vy,b.vz=velocity;b.mode=BallMode.KICK if kind=='kick'else BallMode.SHOT;b.scoring=True;b.last_touch=p.team;b.last_releaser=pid;b.release_time=s.now
  if defk:
   #C4c2: a kick by the other team on a scoring flight is a defensive deflection: the flight and its offensive origin are kept
   xy=self.c4b_origin(p)[0]if self.c4b else(p.x,p.y);b.c4c2_def=list(getattr(b,'c4c2_def',None)or[])+[(p.id,round(xy[0],3),round(xy[1],3),True)];c4o=None
  else:
   b.pocket_origin=(p.x,p.y);b.pocket_release_team=p.team
   c4o=self.c4b_set_origin(p)if self.c4b else None #C4b: for a kick, the support foot (the planted one)
   if self.c4c2:b.c4c2_def=[];b.c4c2_off=pid;b.c4c2_off_i=0
  c2k=('defensive_kick_origin_kept'if defk else'new_flight')if self.c4c2 else None
  self.emit('strike','4.4–4.5;5.2',player=pid,kind=kind,velocity=list(velocity),**({'origin':c4o}if c4o else{}),**({'scoring_flight':c2k}if c2k else{}));self.reconstruction_check(p,'deliberate_play');return True
 def frame_contact(self,velocity=None,point=None):
  if self.s.phase not in(Phase.LIVE,Phase.FLIGHT,Phase.PENALTY,Phase.OPENING):return
  b=self.s.ball;b.version+=1
  if velocity:b.vx,b.vy,b.vz=velocity
  if point:b.x,b.y,b.z=point
  self.emit('frame_contact','2.3;5.2;5.5')
 def retrieve_arrow(self,arrow_id):
  if self.s.phase not in(Phase.DEAD,Phase.BREAK):return False
  ar=next((a for a in self.s.arrows if a.id==arrow_id),None)
  if ar is None:return False
  ar.live=False;self.emit('arrow_retrieved','3.9',arrow=arrow_id,ammunition_added=0);return True
 def joint_control(self,pids):
  s=self.s;b=s.ball
  if len({s.players[p].team for p in pids})<2:return self.acquire(pids[0])
  if not all(self.eligible(s.players[p])for p in pids):return False
  b.carrier=None;b.mode=BallMode.CONTESTED;b.contested=tuple(sorted(pids));b.vx=b.vy=b.vz=0;s.contested_until=s.now+1000
  self.emit('joint_control','6.9',players=list(pids));return True
 def held(self):
  s=self.s
  if s.phase==Phase.OPENING and s.opening_team is None:return self.failed_hunt('joint_control')
  team=s.alternate;self.award(team,s.ball.x,s.ball.y,'held_ball');self.emit('held_ball','6.9',team=team)
 def contact_legal(self,a,t,kind='tackle',surface='torso',reach=True):
  #C3a3: reach=False leaves out the distance test, so that the answer is the legal condition alone: would this contact be lawful
  #if it happened? Being out of reach is a fact about distance; it must not stand in for, or hide, a protection that applies.
  s=self.s
  if not(self.eligible(a)and self.eligible(t)):return False,'ineligible_contact'
  if a.role=='archer'or t.role=='archer':return False,'archer_contact'
  if surface in ('head','neck','spine','groin','joint','knee','claw','horn','weapon'):return False,'dangerous_surface'
  if a.posture!='upright'or t.posture=='grounded':return False,'grounded_contact'
  av=getattr(a,'contact_velocity',(a.vx,a.vy));tv=getattr(t,'contact_velocity',(t.vx,t.vy))
  #C3a: the two contact-speed offences exist only in the legacy replay path. What a fast collision does is now physical (balance shock).
  if not self.c3 and(max(norm(*av),norm(*tv))>12+1e-7 or norm(av[0]-tv[0],av[1]-tv[1])>8+1e-7):return False,'contact_speed'
  if kind=='tackle' and s.ball.carrier!=t.id:return False,'noncarrier_wrap'
  if reach and norm(a.x-t.x,a.y-t.y)>a.radius+t.radius+.7*(a.a.reach+t.a.reach):return False,'out_of_contact_range'
  if kind!='tackle':
   dx,dy=a.x-t.x,a.y-t.y
   #C3c (decided by DreLen: only a hit from directly behind counts). From behind means strictly inside the rear cone: the hitter's
   #bearing from the other athlete is closer to the line straight out of his back than the half-angle. On the boundary it is lawful.
   if dx*t.facing[0]+dy*t.facing[1]<-self.blind_cos*max(.1,norm(dx,dy)):return False,'blindside'
  if s.phase==Phase.AWARD and a.team!=s.owner:
   rec=s.recovery
   #C2: a first-tackle recovery protects only its one-metre disc. Legal screening outside the disc remains possible.
   if not rec or min(norm(a.x-rec['spot'][0],a.y-rec['spot'][1])-a.radius,norm(t.x-rec['spot'][0],t.y-rec['spot'][1])-t.radius)<1:return False,'protected_recovery'
  if s.award_spot and s.award_available is not None and s.now<s.award_available+2000 and s.ball.carrier==t.id:
   if norm(s.ball.x-s.award_spot[0],s.ball.y-s.award_spot[1])<=1 and a.team!=t.team:return False,'protected_recovery'
  return True,'legal'
 def engage(self,actor,target,kind='block',surface='torso',sanction=True):
  a,t=self.s.players[actor],self.s.players[target]
  legal,reason=self.contact_legal(a,t,'tackle'if kind=='tackle'else'block',surface)
  if not legal:
   if sanction and reason!='out_of_contact_range':self.foul(actor,target,reason,major=reason in('contact_speed','dangerous_surface','ineligible_contact'),danger=reason in('contact_speed','dangerous_surface','ineligible_contact'))
   return False
  key=(actor,target,kind)
  if key not in self.s.engagements:
   self.s.engagements[key]=Engagement(actor,target,kind,self.s.now);self.emit('engagement','6.1–6.4',actor=actor,target=target,kind=kind)
  return True
 def tackle(self,actor,target,body='knee',witnessed=False):
  s=self.s;a,t=s.players[actor],s.players[target]
  if body in ('hand','foot'):
   self.emit('incomplete_tackle','6.5',actor=actor,target=target,body=body);return False
  #C3a: a grounding classified by the contact kernel carries its own witness of a lawful engagement, taken at the instant of
  #grounding on the kernel's substep. It is not re-tested against positions interpolated across the whole step.
  if witnessed:
   if s.ball.carrier!=target or not a.eligible(s.now)or not t.eligible(s.now):return False
  elif not self.engage(actor,target,'tackle'):return False
  if s.phase==Phase.PENALTY:
   self.emit('penalty_tackle','12.4',actor=actor,target=target);self.finish_penalty(0);return True
  if s.extension and a.team!=s.extension_team:self.emit('extension_tackle','16.6');self.end_period();return True
  bx,by=s.ball.x,s.ball.y
  if self.c3b:self.go_down(t) #C3b: he keeps the momentum he has and slides; getting up takes modelled time
  else:t.posture='grounded';t.next_action=s.now+800;t.vx=t.vy=0
  t.tackled_until=t.next_action
  if self.c2_tackles and s.owner==t.team and s.tackle_count==0:return self.first_tackle(a,t,bx,by)
  if self.c2_tackles:s.tackle_ordinal+=1;self.emit('tackle_count','C2-3',team=t.team,count_from=s.tackle_count,count_to=s.tackle_count+1,tackler=actor,carrier=target,spot=[bx,by],procedure='turnover',**({'ordinal_in_possession':s.tackle_ordinal}if self.c4_occ else{}))
  self.new_owner(a.team,'tackle');s.possession_ms=self.play_ms;s.phase=Phase.AWARD
  s.ball.version+=1;s.ball.carrier=None;s.ball.mode=BallMode.LOOSE;s.ball.scoring=False;s.ball.last_releaser=None;s.ball.x=bx;s.ball.y=by;s.ball.z=.1075;s.ball.vx=s.ball.vy=s.ball.vz=0
  s.award_spot=(bx,by);s.award_available=s.now;s.award_deadline=s.now+5000;s.engagements.clear()
  self.emit('tackle_award','6.5–6.7',actor=actor,target=target,spot=[bx,by]);return True
 def first_tackle(self,a,t,bx,by):
  """C2: first counted tackle of a possession. Possession is retained and the count becomes one.
  In the attacked Keeper Zone: goal-line inbound, and the zone must be cleared before a goal can count.
  Anywhere else, including the team's own zone: live local exclusive recovery at the ball's position."""
  s=self.s;team=t.team;bx=clamp(bx,0,100);by=clamp(by,0,100);attacked=s.own_zone(s.other(team));zj=self.zone(bx,by)
  where='attacked_zone'if zj==attacked else'own_zone'if zj==s.own_zone(team)else'outside'
  inbound=self.c2_inbound and where=='attacked_zone'
  s.tackle_count=1;s.engagements.clear();s.tackle_ordinal+=1
  self.emit('tackle_count','C2-3',team=team,count_from=0,count_to=1,tackler=a.id,carrier=t.id,spot=[bx,by],where=where,procedure='zone_inbound'if inbound else'live_recovery',**({'ordinal_in_possession':s.tackle_ordinal}if self.c4_occ else{}))
  if inbound and s.advantage:
   #A formal stoppage ends a pending advantage unrealised: play returns to the foul instant, so this tackle is not kept on the count.
   self.recall_advantage();return True
  if inbound:
   s.reconstruction={'team':team,'zone':attacked,'live_since':s.live_ms};self.count('reconstructions_set');self.emit('reconstruction_set','C2-4',team=team,zone=attacked)
   side=-1 if by<50 else 1 if by>50 else self.inbound_side(team)
   self.inbound(team,0. if attacked==0 else 100.,50+side*self.mark_off);return True
  b=s.ball;s.phase=Phase.AWARD
  b.version+=1;b.carrier=None;b.mode=BallMode.LOOSE;b.scoring=False;b.last_releaser=None;b.x=bx;b.y=by;b.z=.1075;b.vx=b.vy=b.vz=0
  s.award_spot=(bx,by);s.award_available=s.now;s.award_deadline=s.now+3000
  s.recovery={'team':team,'spot':(bx,by),'started':s.now,'must_clear':{},'committed':self.recovery_committed(team,bx,by)|{a.id}|set(self.grace)}
  self.emit('recovery_started','C2-3.1',team=team,spot=[bx,by],deadline=s.award_deadline,carrier=t.id,tackler=a.id,placed_at=s.now)
  if self.c3b:self.recovery_react(team,sorted(set(self.grace)-{a.id}))
  return True
 def recovery_react(self,team,holders=()):
  """C3b: opponents respond to a first-tackle recovery award after their own reaction time, not whenever their decision cycle
  next comes round. Until then each carries on with what he was doing. (Controller timing; recovery_react = 0 switches it off.)"""
  s=self.s;react={}
  for q in s.players.values():
   if q.active and q.role!='archer'and q.team!=team and self.assume['recovery_react']:
    q.next_decision=s.now+int(1000*q.a.decision_speed);react[q.id]=q.next_decision-s.now
  self.emit('recovery_compliance','C3b-5',holders_with_grace=list(holders),committed=sorted(s.recovery['committed']),reaction_ms=react)
 def recovery_committed(self,team,sx,sy):
  #Opponents for whom being in the disc is not avoidable: a body already inside it at the tackle, or one moving towards it whose
  #response time and braking distance carry it in. Standing or moving nearby is not enough. The tackler is added by the caller.
  out=set()
  for q in self.s.players.values():
   if not q.active or q.role=='archer'or q.team==team:continue
   dx,dy=q.x-sx,q.y-sy;d=norm(dx,dy);gap=d-(1+q.radius)
   if gap<0:out.add(q.id);continue
   vin=-(q.vx*dx+q.vy*dy)/max(d,1e-9)
   if vin>0 and gap<=vin*vin/(2*max(1,q.a.braking))+vin*q.a.decision_speed:out.add(q.id)
  return out
 def inbound_side(self,team):
  #An exact tie between the two marks: the attacking side chooses. Provisional controller: the side with more unmarked teammates.
  s=self.s;opp=[q for q in s.players.values()if q.team!=team and q.role!='archer'and self.eligible(q)];n={-1:0,1:0}
  for p in s.players.values():
   if p.team==team and p.role!='archer'and self.eligible(p)and all(norm(p.x-q.x,p.y-q.y)>self.mark_d for q in opp):n[-1 if p.y<50 else 1]+=1
  return 1 if n[1]>n[-1]else-1
 def inbound(self,team,gx,my,reason='zone_inbound',foul=False):
  """C2: goal-line inbound at the authorised mark. Possession clock and tackle count are retained; three-metre clearance;
  the taker stands just outside the field at the mark."""
  self.award(team,gx,my,reason,foul=foul,normalize=False);r=self.s.restart
  if r is not None and r.reason==reason:r.kind='inbound';r.clearance=3.;r.taker_spot=(gx+(-.4 if gx==0 else .4),my)
 def recovery_watch(self):
  """C2: the one-metre exclusion disc around a first-tackle recovery, checked against opponents' body footprints.
  An opponent inside must leave. One who cannot yet move (grounded, frozen) is an unavoidable obstruction, not an offence.
  One who could have left by now and has not is interfering."""
  s=self.s;rec=s.recovery;sx,sy=rec['spot']
  if self.c3b:
   #C3b: when an opponent who had to clear the disc has left it, record what was necessary, what he took and what was his own delay
   for pid,w in list(rec.get('inside',{}).items()):
    q=s.players[pid]
    if not q.active or norm(q.x-sx,q.y-sy)>=1+q.radius:
     self.emit('recovery_cleared','C3b-5',player=pid,found_inside_ms=w['at']-rec['started'],necessary_m=round(w['depth'],3),unable_ms=w['wait'],allowed_ms=w['clear_by']-w['at'],took_ms=s.now-w['at'],attributable_delay_ms=max(0,s.now-w['clear_by']),had_grace=pid in rec['committed'])
     del rec['inside'][pid]
  for q in s.players.values():
   if not q.active or q.role=='archer'or q.team==rec['team']:continue
   d=norm(q.x-sx,q.y-sy)
   if d>=1+q.radius:continue
   able=q.eligible(s.now)and q.posture!='grounded'
   if q.id not in rec['must_clear']:
    if able and q.id not in rec['committed']:
     #Avoidable occupation of the pickup space: he was clear, and able to stay clear, when the recovery began.
     self.count('recovery_interference_fouls');self.emit('recovery_obstruction','C2-3.1',player=q.id,unavoidable=False,entered_late=True,body_inside_disc_m=round(1+q.radius-d,3),clear_by=s.now)
     self.foul(q.id,None,'recovery_interference');return True
    wait=0 if able else max(0,max(q.next_action,q.freeze_until)-s.now)
    need=math.sqrt(2*(1+q.radius-d)/max(1,q.a.acceleration))+q.a.decision_speed+.3
    rec['must_clear'][q.id]=s.now+wait+int(1000*need)
    if self.c3b:rec.setdefault('inside',{})[q.id]={'at':s.now,'depth':1+q.radius-d,'wait':wait,'clear_by':rec['must_clear'][q.id]}
    if not able:self.count('recovery_unavoidable_obstructions')
    self.emit('recovery_obstruction','C2-3.1',player=q.id,unavoidable=not able,body_inside_disc_m=round(1+q.radius-d,3),clear_by=rec['must_clear'][q.id])
   elif able and s.now>rec['must_clear'][q.id]:
    self.count('recovery_interference_fouls');self.foul(q.id,None,'recovery_interference');return True
  return False
 def recovery_blocked(self):
  #Pickup is physically impossible when an opponent who cannot move has his body over the ball.
  s=self.s;sx,sy=s.recovery['spot']
  return any(q.active and q.role!='archer'and q.team!=s.recovery['team']and norm(q.x-sx,q.y-sy)<q.radius+s.ball.radius and not(q.eligible(s.now)and q.posture!='grounded')for q in s.players.values())
 def restore_recovery(self,cause,floor=False,remaining=3000):
  """C2: formal interruption of a first-tackle recovery. The exclusive recovery is restored at its original spot,
  the tackle count is kept, and the recovery resumes (resume_recovery) once the disc is clear."""
  s=self.s;rec=s.recovery;team=rec['team'];x,y=rec['spot'];self.count('recoveries_restored')
  self.emit('recovery_interrupted','C2-3.2',cause=cause,remaining_ms=remaining)
  s.recovery=None;self.award(team,x,y,'recovery_restored',foul=floor,normalize=False);r=s.restart
  if r is not None and r.reason=='recovery_restored':r.kind='recovery';r.remaining=remaining;r.note=cause
  return True
 def recovery_blockers(self,r):
  return[q for q in self.s.players.values()if q.active and q.role!='archer'and q.team!=r.team and norm(q.x-r.x,q.y-r.y)<1+q.radius]
 def resume_recovery(self):
  s=self.s;r=s.restart
  if s.phase!=Phase.DEAD or r is None or r.kind!='recovery':return False
  b=s.ball;b.version+=1;b.mode=BallMode.LOOSE;b.carrier=None;b.x=r.x;b.y=r.y;b.z=.1075;b.vx=b.vy=b.vz=0;b.scoring=False;b.last_releaser=None
  s.phase=Phase.AWARD;s.award_spot=(r.x,r.y);s.award_available=s.now;s.award_deadline=s.now+r.remaining
  s.recovery={'team':r.team,'spot':(r.x,r.y),'started':s.now,'must_clear':{},'replacement':True,'committed':set()};s.restart=None
  self.emit('recovery_resumed','C2-3.2',team=r.team,spot=[r.x,r.y],deadline=s.award_deadline,cause=r.note)
  if self.c3b:self.recovery_react(r.team)
  return True
 def exit_run(self,st,p,j,ax,ay,limit_ms):
  """C3b2: the time (ms) athlete p needs to get out of Keeper Zone j steering for the point (ax, ay), from the state
  st = (x, y, vx, vy, fatigue), or None if he is not out, inside the field, within limit_ms. It is his own motion law, the one
  the mover applies: top speed, his acceleration or braking along his present velocity, his turning limit across it. So a
  velocity pointing the wrong way has to be braked off and turned first, and that costs what it really costs. 20 ms steps.
  C3b3: a time later than limit_ms is never returned. The time reported is the end of the 20 ms step in which he is first out,
  so it is late by up to 20 ms: a way out he would in truth just make can be reported as not made, never the reverse."""
  s=self.s;gx=0. if j==0 else 100.;R=s.keeper_zone_radius;x,y,vx,vy,fat=st;dt=.02;t=0
  vmax=max(.1,p.a.maximum_speed*.88*(.70+.30*fat));acc=max(1.,p.a.acceleration*(.55+.45*fat));brk=p.a.braking;trn=p.a.turning*dt
  while t<limit_ms:
   dx,dy=ax-x,ay-y;d=norm(dx,dy);sp=norm(vx,vy)
   desx,desy=(dx/d*vmax,dy/d*vmax)if d>1e-9 else(0.,0.)
   dvx,dvy=desx-vx,desy-vy;a=acc if desx*desx+desy*desy>sp*sp else brk
   if sp>1:
    along=clamp((dvx*vx+dvy*vy)/sp,-brk*dt,a*dt);nx,ny=-vy/sp,vx/sp;side=clamp(dvx*nx+dvy*ny,-trn,trn)
    vx,vy=vx+along*vx/sp+side*nx,vy+along*vy/sp+side*ny
   else:
    dv=norm(dvx,dvy)
    if dv>0:
     k=min(1.,a*dt/dv);vx+=dvx*k;vy+=dvy*k
   x+=vx*dt;y+=vy*dt;t+=20
   if not(0<=x<=100 and 0<=y<=100):return None
   if norm(x-gx,y-50)>R:return t if t<=limit_ms else None #C3b3: out, but only after the limit, is not out within it
  return None
 def exit_points(self,j):
  #23 aim points just beyond the arc of zone j inside the field, 7.5 degrees apart as seen from the goal.
  s=self.s;gx=0. if j==0 else 100.;sg=1. if j==0 else-1.;R=s.keeper_zone_radius+.1;out=[]
  for i in range(-11,12):
   phi=math.radians(7.5*i);ex=gx+sg*R*math.cos(phi);ey=50+R*math.sin(phi)
   if 0<=ex<=100 and 0<=ey<=100:out.append((ex,ey))
  return out
 def exit_free(self,st,p,j,left_ms):
  """C3b2: the fastest time out with nobody in the way, from state st: the least over the aim points, searched up to left_ms; if
  none gets him out by then, the straight-out point is run on up to 6 s so that the shortfall can be reported. None: over 6 s."""
  best=None
  for ax,ay in self.exit_points(j):
   t=self.exit_run(st,p,j,ax,ay,left_ms if best is None else min(left_ms,best))
   if t is not None and(best is None or t<best):best=t
  if best is None:
   gx=0. if j==0 else 100.;ax,ay=min(self.exit_points(j),key=lambda q:norm(q[0]-st[0],q[1]-st[1]));best=self.exit_run(st,p,j,ax,ay,6000)
  return best
 def exit_routes(self,p,j,left_ms):
  """C3b: the ways out of Keeper Zone j practicable for athlete p now. For each aim point: whether an upright eligible
  opponent's body stands in the straight lane to it (within the two body radii of the line, ahead of him and short of the
  arc), and the time he needs to be out steering for it (exit_run, C3b2). A route is practicable if the lane is clear and he is
  out within the zone time he has left. Returns (fastest time with nobody in the way in ms, fastest practicable time in ms or
  None, number of practicable routes). A snapshot test: opponents are taken where they stand."""
  lanes=self.exit_lanes(p,j,left_ms);ok=[t for i,t in lanes.items()if t is not None]
  return self.exit_free((p.x,p.y,p.vx,p.vy,p.fatigue),p,j,left_ms),(min(ok)if ok else None),len(ok)
 def exit_lanes(self,p,j,left_ms,only=None,bodies=None):
  #{aim point index: time out in ms, or None if he is not out within left_ms} for every aim point whose lane is clear of opponents.
  #only: an iterable of indices to which the timing is limited (the lane test is still made for all).
  #bodies (C3b3): a set, filled with the opponents whose bodies stand in at least one lane.
  s=self.s;st=(p.x,p.y,p.vx,p.vy,p.fatigue);out={}
  opp=[q for q in s.players.values()if q.active and q.team!=p.team and q.role!='archer'and self.eligible(q)and q.posture=='upright']
  for i,(ex,ey)in enumerate(self.exit_points(j)):
   dx,dy=ex-p.x,ey-p.y;d=norm(dx,dy)
   if d>1e-9:
    ux,uy=dx/d,dy/d
    inl=[q.id for q in opp if 0<(q.x-p.x)*ux+(q.y-p.y)*uy<d+q.radius and abs((q.x-p.x)*uy-(q.y-p.y)*ux)<p.radius+q.radius]
    if inl:
     if bodies is not None:bodies.update(inl)
     continue
   out[i]=self.exit_run(st,p,j,ex,ey,left_ms)
  return out
 def exit_before(self,p,j,snap):
  #The witness at a snapshot (x, y, vx, vy, fatigue, zone time left): the fastest time out with nobody in the way against the time left.
  free=self.exit_free(snap[:5],p,j,snap[5]);return{'left_ms':snap[5],'free_ms':free,'sufficient':free is not None and free<=snap[5]}
 def exit_watch(self):
  """C3b off-ball exit protection, the witness (episodes: C3b2). An attacker without the ball who is inside the zone he attacks
  and whose own target lies outside it is trying to leave. His state is noted at every check (once per interval).
  An obstruction EPISODE begins when an opponent materially runs into him (the kernel's collision witness) and no episode is
  open. Its 'before' witness is his state at the last check before that contact: was his time still enough then? From then on,
  at every check, the lanes are examined (exit_lanes). A lane OPENS when it is clear of opponents and he could be out by it in
  the zone time left; the time it needed then is kept with it. It stays open for as long as it stays clear, and CLOSES when an
  opponent's body is in it. (Running short of time on a lane that stayed clear does not close it: that time went because he
  did not take it.) The zone time since the previous check is put down to the state found at that check: OPEN (some lane
  open) or DENIED (none).
  An opening counts against him only when it was real: a lane open for at least as long as it needed when it opened. Then he
  ignored an attainable exit; the episode is closed against him, and a later contact begins a new episode with its own 'before'
  witness. An opening shorter than that proves nothing: a further contact joins the same episode. The record ends when he is
  out, or stops trying.
  C3b3, who denied him. Zone time found DENIED at a check is put down to the opponents who have run into him in this episode
  and whose bodies stand in his lanes at that check. If none of them does (the lanes are clear but the time is gone, or the
  bodies in them have not touched him), it is put down to whoever it was put down to at the check before, and at the start of
  a denied stretch to the opponent who last ran into him before it began. A lane that was open also closes when an opponent
  runs into him, he needs longer for it than he did at the check before, and he can no longer be out by it in the time left;
  if he still can, that lane needs from then on the time it has been open plus the time he needs from there. A contact that
  does not set him back changes no lane: time he let run on an open lane is still his. So a contact made while he is already denied, by an
  opponent who is not in his way, takes on nothing. Each stretch is kept with its length, its opponents and that basis."""
  s=self.s
  for p in s.players.values():
   rec=getattr(p,'exit_try',None)
   if not p.active or p.role=='archer':
    if rec:p.exit_try=None
    continue
   j=next((k for k in(0,1)if p.zone_loc[k]=='in'),None)
   trying=j is not None and p.team==s.owner and s.ball.carrier!=p.id and p.zone_ms[j]>0 and not(p.role=='keeper'and j==s.own_zone(p.team))and self.zone(*p.target)!=j
   if not trying or(rec and rec['zone']!=j):
    if rec:p.exit_try=None
    if not trying:continue
    rec=None
   zms=p.zone_ms[j];left=5000-zms;snap=(p.x,p.y,p.vx,p.vy,p.fatigue,left)
   if rec is None:rec=p.exit_try={'zone':j,'since':s.now,'start':snap,'last':snap,'zms':zms,'seen':getattr(p,'c3_hit',(-1,None))[0],'ep':None,'episodes':0}
   ep=rec['ep'];step=zms-rec['zms']
   if ep is not None and not ep['ignored']:
    #the zone time since the previous check belongs to the state found then
    self.exit_account(ep,step);ep['since_contact_open_ms']+=step if ep['state']=='open'else 0.
   hit=getattr(p,'c3_hit',None);fresh=False
   if hit and hit[0]>rec['seen']:
    fresh=True
    rec['seen']=hit[0];before=self.exit_before(p,j,rec['last'])
    if ep is None or ep['ignored']:
     ep=rec['ep']={'before':before,'contacts':[],'by':None,'state':None,'lanes':{},'denied_ms':0.,'open_ms':0.,'need_ms':None,'longest_open_ms':0.,'since_contact_open_ms':0.,'ignored':False,'checks':0,
                   'deniers':[],'basis':None,'denied_by':{},'segments':[],'opened':False};rec['episodes']+=1
    ep['contacts'].append({'at_ms':round(hit[0],1),'by':hit[1],'left_ms':left,'before':before,'route_open_ms_since_previous_contact':ep['since_contact_open_ms']});ep['by']=hit[1];ep['since_contact_open_ms']=0.
   if ep is not None and not ep['ignored']:
    bodies=set();now=self.exit_lanes(p,j,left,bodies=bodies);ep['checks']+=1;lanes=ep['lanes'];was=ep['state']
    for i in[i for i in lanes if i not in now]:del lanes[i] #an opponent's body is in that lane now
    if fresh and lanes:
     #C3b3: an opponent has just run into him. For each lane still open and clear: does he need longer for it now than he did
     #at the check before? Then the contact has set him back on it. If he can no longer be out by it in the time left, it closes;
     #otherwise it needs, from now on, the time it has been open plus the time he needs from here.
     pts=self.exit_points(j);prev=rec['last'][:5]
     for i in list(lanes):
      a=self.exit_run(prev,p,j,pts[i][0],pts[i][1],6000);b=now[i]if now[i]is not None else self.exit_run(snap[:5],p,j,pts[i][0],pts[i][1],6000)
      if b is None or(a is not None and b>a):
       if now[i]is None:del lanes[i]
       else:lanes[i][0]=max(lanes[i][0],lanes[i][1]+now[i])
    for i,t in now.items():
     if i not in lanes and t is not None:lanes[i]=[t,0.] #it opens: [time it needs from here, how long it has been open]
    ep['state']='open'if lanes else'denied'
    if lanes:ep['need_ms']=min(v[0]for v in lanes.values());ep['deniers']=[];ep['basis']=None
    else:
     who=sorted({c['by']for c in ep['contacts']}&bodies)
     if who:ep['deniers']=who;ep['basis']='ran_into_him_and_stands_in_his_lanes'
     elif was!='denied'or not ep['deniers']:ep['deniers']=[ep['by']];ep['basis']='last_to_run_into_him_before_this_denial'
     else:ep['basis']='carried_from_the_check_before'
   rec['last']=snap;rec['zms']=zms
 def exit_account(self,ep,step):
  #Zone time that has run since the last check, put down to the state found at that check.
  if ep['state']=='open':
   ep['open_ms']+=step
   if step>0:ep['opened']=True
   for v in ep['lanes'].values():
    v[1]+=step;ep['longest_open_ms']=max(ep['longest_open_ms'],v[1])
    if v[1]>=v[0]:ep['ignored']=True;ep['need_ms']=v[0]
  elif ep['state']=='denied':
   ep['denied_ms']+=step
   if step>0:
    #C3b3: this stretch of denied time, and the opponents it is put down to (each in full when there are several)
    for q in ep['deniers']:ep['denied_by'][q]=ep['denied_by'].get(q,0.)+step
    seg=ep['segments']
    if seg and not ep['opened']and seg[-1]['by']==ep['deniers']and seg[-1]['basis']==ep['basis']:seg[-1]['ms']+=step
    else:seg.append({'by':list(ep['deniers']),'basis':ep['basis'],'ms':step})
    ep['opened']=False
 def zone_expiry_c3b(self,p,j):
  """C3b: an attacker's five seconds in the zone have run out. For the ball carrier: record who was holding him and whether he
  was being contained. For an off-ball attacker: classify his exit from the witness (exit_watch). Where his time was enough as
  he set off and still enough just before the obstruction episode now open began, and he has not ignored an attainable exit
  since, opponents' contact has denied him his way out: no expiry is given, and exactly the zone time that ran while no
  practicable route existed in that episode is given back.
  C3b3: the opponent penalised is the one to whom most of that denied time is put down (exit_watch); on equal time, the one of
  them who ran into him last. The record gives every denied stretch with its opponents, each opponent's total, and the last
  opponent to run into him, who is not thereby the one responsible."""
  s=self.s;rec=getattr(p,'exit_try',None);carrier=s.ball.carrier==p.id;extra={};ep=None
  if carrier:
   held=[{'player':k[0],'grip':round(en.progress,4),'containing':bool(getattr(en,'contain',False))}for k,en in sorted(s.engagements.items())if k[2]=='tackle'and k[1]==p.id]
   cls='carrier_contained'if any(h['containing']for h in held)else'carrier_held'if held else'carrier_free'
   extra={'holders':held}
   if cls=='carrier_contained':self.count('containment_expiries')
  elif not self.assume['exit_protection']:cls='not_assessed'
  elif rec is None or rec['zone']!=j:cls='no_exit_attempt'
  else:
   start=self.exit_before(p,j,rec['start']);ep=rec['ep']
   if ep is not None and not ep['ignored']:
    #the time from the last check to the expiry belongs to the state found at that check
    self.exit_account(ep,p.zone_ms[j]-rec['zms']);rec['zms']=p.zone_ms[j]
   if not start['sufficient']:cls='time_already_insufficient'
   elif ep is None:cls='no_opposing_contact'
   elif not ep['before']['sufficient']:cls='time_insufficient_before_contact'
   elif ep['ignored']:cls='practicable_route_remained'
   else:cls='all_routes_denied_by_contact'
   extra={'exit':{'since':rec['since'],'left_ms':start['left_ms'],'free_ms':start['free_ms'],'sufficient':start['sufficient'],'episodes':rec['episodes'],
                  **({'contacts':ep['contacts'],'before_contact':ep['before'],'denied_ms':ep['denied_ms'],'route_open_ms':ep['open_ms'],'longest_continuous_open_ms':ep['longest_open_ms'],
                      'needed_ms_by_the_lane_concerned':ep['need_ms'],'ignored_attainable_exit':ep['ignored'],'checks_after':ep['checks'],
                      'denied_segments':[dict(g)for g in ep['segments']],'denied_ms_by_opponent':dict(sorted(ep['denied_by'].items())),'last_contact_by':ep['by']}if ep is not None else{'contacts':[]})}}
  if cls=='all_routes_denied_by_contact':
   last={c['by']:i for i,c in enumerate(ep['contacts'])};share=ep['denied_by']
   by=max(share,key=lambda q:(share[q],last.get(q,-1)))if share else ep['by'];back=max(0.,p.zone_ms[j]-ep['denied_ms']);self.count('exit_obstructions')
   self.emit('exit_obstruction','C3b-8',player=p.id,zone=j,by=by,zone_ms_restored_to=back,**extra)
   p.zone_ms[j]=back;p.exit_try=None
   self.foul(by,p.id,'exit_obstruction',advantage=True);return
  self.count('attacking_zone_expiries');self.emit('attacking_zone_expiry','C2-5',player=p.id,zone=j,possible_exit_interference=self.exit_interference(p,j),exit_class=cls,**extra)
  if self.c4_occ and self.zone_offset(p,'zone_expiry',p.zone_ms[j]):return #C4.0 r2: a defensive violation of the same millisecond (15.5)
  self.illegal(p.id,'zone_expiry')
 def c4b_origin(self,p):
  """C4b, decided by DreLen: the scoring origin of a release is the support foot. Both feet planted: the foot nearer the goal
  he attacks (distance to its centre, the radial territory geometry); one planted: that foot; airborne: the last planted foot's
  position. Returns (x, y) and the record of how it was found, with the pelvis kept beside it. Without foot state (the legacy
  path) the pelvis is used and the record says so."""
  s=self.s;ft=getattr(p,'feet',None);gx=s.attack_goal(p.team);pel=(p.x,p.y)
  if not ft:return pel,{'rule':'pelvis_no_foot_state','pelvis':[round(p.x,3),round(p.y,3)]}
  down=[k for k in('L','R')if ft[k]['planted']]
  if down:
   k=min(down,key=lambda k:(norm(ft[k]['x']-gx,ft[k]['y']-50),k));xy=(ft[k]['x'],ft[k]['y']);rule='both_planted_nearer_goal'if len(down)==2 else'one_planted'
  elif getattr(p,'last_plant',None):xy=p.last_plant[:2];k=p.last_plant[3];rule='airborne_last_plant'
  else:return pel,{'rule':'pelvis_no_foot_state','pelvis':[round(p.x,3),round(p.y,3)]}
  return xy,{'rule':rule,'foot':k,'origin':[round(xy[0],3),round(xy[1],3)],'pelvis':[round(p.x,3),round(p.y,3)],
             'territory':self.territory(p.team,*xy),'pelvis_territory':self.territory(p.team,*pel),
             'feet':{q:[round(ft[q]['x'],3),round(ft[q]['y'],3),ft[q]['planted']]for q in('L','R')if'x'in ft[q]}}
 def c4b_auto_points(self,carry):
  #C4b: the value of an automatic penalty award under the active configuration (build specification 2): the carry value for a
  #denied or automatic finish when Carry is enabled, otherwise the zone-release value. Declared mapping, the Lead's position.
  cv=self.pocket.get('carry_value',0)
  return cv if(carry and cv>0)else self.pocket.get('release_points',9)
 def c4b_set_origin(self,p):
  #C4b: the origin of the last deliberate play, with its record kept on the ball for the goal record
  b=self.s.ball;xy,rec=self.c4b_origin(p);b.pocket_origin=xy;b.c4b_origin=rec;b.c4b_launch=(round(b.x,3),round(b.y,3),round(b.z,3));return rec
 def zone_due(self):
  """C4.0: the defending players who can be called for an unmarked expiry now, each with the live millisecond at which he
  became callable: the instant his allowance ran out, or, if he has been called already, the end of his compliance time.
  Not callable: a Keeper in his own zone, an Archer, a frozen player, a player off the field (his count is paused there
  and he is not in the zone), and a called player whose compliance time is still running."""
  s=self.s;out=[]
  if s.owner is None:return out #no possession, no defending team
  for p in s.players.values():
   if not p.active or p.role=='archer'or p.team==s.owner or p.frozen(s.now):continue
   j=self.zone(p.x,p.y)
   if j is None or(p.role=='keeper'and j==s.own_zone(p.team)):continue
   if p.unmarked_ms[j]<5000 or s.live_ms<p.zone_fouled[j]:continue
   out.append((max(s.live_ms-(p.unmarked_ms[j]-5000),p.zone_fouled[j]),p.id,j))
  return sorted(out)
 def zone_compliance_time(self,p,j):
  """C4.0: the one opportunity a called defender has to leave the zone or regain marking, in live milliseconds, worked out
  from where he is and how he is moving when called. Declared estimate, not fitted, built as a bound that holds whatever he
  was doing (C4.0 r2: on the motion the C3 kernel actually allows him, tired or fresh):
    reaction: his decision time, during which a moving player may still be speeding up, at his full attribute acceleration
      (no fatigue reduction, the conservative side for this part), in the worst direction (further in), to at most his
      fresh top speed;
    stop: from that speed at his braking;
    run: from rest to the arc by the shortest line, integrated on the kernel's own limits: acceleration
      x (0.55 + 0.45 x fatigue), top speed x (0.70 + 0.30 x fatigue) x 0.88 (off the ball), and the slowing the kernel
      applies as he nears a target 2 m beyond the arc (the exit target of the controllers). Fatigue is taken at its lowest
      value it could reach during the whole estimate (it falls while he runs);
    0.3 s.
  The drill (drills_c4_0.py) checks it against the kernel at three fatigue levels and with acceleration, braking, top speed,
  decision time and endurance varied one at a time. It is not a new five seconds, and nothing renews it: not a later check,
  not a substitution (the slot keeps the deadline)."""
  s=self.s;gx=0 if j==0 else 100;way=max(0,s.keeper_zone_radius-norm(p.x-gx,p.y-50))+.1;rt=p.a.decision_speed
  sp=p.speed;brk=max(1,p.a.braking);acc=max(1,p.a.acceleration);fresh_top=max(.1,p.a.maximum_speed*.88)
  v1=min(max(fresh_top,sp),sp+acc*rt)if sp>0 else 0.;drift=(sp+v1)/2*rt;stop=v1/brk;d=way+drift+v1*v1/(2*brk)
  burn=(.00015+.006)*(1.25-p.a.endurance*.6)*float(self.assume.get('fatigue_rate',1.)) #the kernel's fatigue cost per second at full intensity
  T=rt+stop+3.;run=0.
  for _ in range(3): #the run time depends on the fatigue reached, which depends on the run time: settle it (three passes are ample)
   f=max(.15,p.fatigue-burn*T);a=max(.1,p.a.acceleration*(.55+.45*f));top=max(.1,p.a.maximum_speed*(.70+.30*f)*.88)
   run=0.;x=0.;v=0.;n=400;dx=d/n
   for i in range(n): #distance-stepped: speed at each point is the least of what acceleration, top speed and the arrival braking allow
    xe=x+dx;ve=min(math.sqrt(v*v+2*a*dx),top,math.sqrt(2*brk*max(0.,d+2.-xe)))
    run+=dx/max(.05,(v+ve)/2);x,v=xe,ve
   T=rt+stop+run
  parts={'distance_out_m':round(way,3),'speed_mps':round(sp,3),'fatigue':round(p.fatigue,4),'fatigue_assumed':round(f,4),'reaction_ms':int(1000*rt),'drift_m':round(drift,3),'stop_ms':int(1000*stop),'run_ms':int(1000*run),'margin_ms':300}
  parts['allowed_ms']=1+parts['reaction_ms']+parts['stop_ms']+parts['run_ms']+parts['margin_ms'];return parts
 def zone_witness(self,p):
  #C4.0: the nearest opponent who could mark him at this instant (eligible, in the field, on his feet), and how far away he is.
  s=self.s;att=[q for q in s.players.values()if q.active and q.role!='archer'and q.team==s.owner and self.eligible(q)and q.posture!='grounded']
  if not att:return None,None
  q=min(att,key=lambda q:norm(q.x-p.x,q.y-p.y));return q.id,norm(q.x-p.x,q.y-p.y) #exact; rounded only where it is logged
 def zone_call(self,offset=False):
  """C4.0, DreLen's ruling of 7 October. A defensive Keeper Zone violation is the expiry of the unmarked allowance of one or
  more defenders at the same resolved millisecond: they are one violation with one consequence. The team defending has one
  counter for the opposing possession, across both zones.
    First violation of the possession: the tackle count returns to zero and the possession clock is raised to
      min(play clock, max(remaining, 20 s)); in an untimed extension, to its ten seconds (rulebook 16.6). The period clock
      is not touched. Advantage is played as for any defensive foul: realised, play goes on with the remedy kept; failed,
      play returns to the foul instant, which already contains the remedy, so it is given once.
    Second violation of the possession: a penalty run under the existing procedure. If an advantage is pending it ends
      unrealised and the clocks return to its foul instant first, as for any foul inside an advantage (retained).
  No personal sanction either time (see foul). Each defender called gets one compliance time (zone_compliance_time); if he
  is still in the zone, unmarked, when it ends, that is a new violation. So is a later expiry by another defender.
  Returns True if a violation was called."""
  s=self.s;due=self.zone_due()
  if not due:return False
  t0=due[0][0];group=[d for d in due if d[0]==t0];later=[d for d in due if d[0]!=t0]
  s.zone_violations+=1;n=s.zone_violations;team=s.players[group[0][1]].team;parts=[]
  for _,pid,j in group:
   p=s.players[pid];again=p.zone_fouled[j]>0;c=self.zone_compliance_time(p,j);near,dist=self.zone_witness(p)
   parts.append({'player':pid,'zone':j,'unmarked_ms':p.unmarked_ms[j],'ground':'still_unmarked_after_compliance_time'if again else'allowance_expired','nearest_opponent':near,'nearest_opponent_m':None if dist is None else round(dist,3),'compliance':c,'compliance_deadline_live_ms':s.live_ms+c['allowed_ms']})
   p.zone_fouled[j]=s.live_ms+c['allowed_ms'];self.count('defensive_unmarked_expiries');self.emit('defensive_unmarked_expiry','C2-5',player=pid,zone=j)
  first=n==1;was=(s.tackle_count,s.possession_ms);adv=s.advantage
  if offset: #C4.0 r2: the award is offset by an attacking technical of the same millisecond (zone_offset); nothing else changes here
   self.count('zone_violations');self.emit('zone_violation','C4.0-zone',team=team,against=s.owner,number_in_possession=n,remedy='offset_by_simultaneous_attacking_offence',resolved_live_ms=t0,called_live_ms=s.live_ms,
            participants=parts,due_later_in_this_instant=[d[1]for d in later],tackle_count_from=was[0],tackle_count_to=was[0],p_ms_from=was[1],p_ms_to=was[1],
            advantage_already_pending=adv is not None,recovery_in_progress=s.recovery is not None,reconstruction=s.reconstruction is not None,personal_sanction=None);return True
  if first:
   s.tackle_count=0
   s.possession_ms=10000 if s.extension else min(self.play_ms,max(20000,s.possession_ms))
   #a foul instant already on record for this team's own pending advantage must give the remedy back if that advantage is recalled
   if adv and'c2'in adv and adv['team']==s.owner:adv['c2']['count']=0;adv['c2']['zone_violations']=n
  self.count('zone_violations');self.count('zone_violation_resets'if first else'zone_violation_penalties')
  self.emit('zone_violation','C4.0-zone',team=team,against=s.owner,number_in_possession=n,remedy='tackle_count_reset'if first else'penalty_run',resolved_live_ms=t0,called_live_ms=s.live_ms,
            participants=parts,due_later_in_this_instant=[d[1]for d in later],tackle_count_from=was[0],tackle_count_to=s.tackle_count,p_ms_from=was[1],p_ms_to=s.possession_ms,
            advantage_already_pending=adv is not None,recovery_in_progress=s.recovery is not None,reconstruction=s.reconstruction is not None,personal_sanction=None)
  self.foul(group[0][1],None,'zone_unmarked',advantage=first,penalty=not first);return True
 def zone_offset(self,p,reason,over_ms):
  """C4.0 r2 (the Lead's audit, choice 4): an attacking technical expiry (zone residence, or the Keeper's ball hold) falls due
  at the same live millisecond as a defensive zone violation. Both offences are collected before possession changes, and
  rulebook 15.5 decides:
    a first defensive violation is a technical, like the attacking expiry: same severity, so the awards offset and the team
    in control keeps the ball with its pre-event clock (a restart at the ball, as for offsetting fouls). The defensive
    violation is still recorded and counted for the possession, and its defenders still get their compliance time;
    a second defensive violation is a penalty-chance offence, more serious than a technical: the attack, its victim, gets
    the penalty run, and the attacking expiry gives no turnover.
  Personal discipline is personal (15.5): none for a zone expiry; the Keeper's ball hold keeps its own. Not applied while an
  advantage is pending: an attacking offence then enforces the earlier defensive foul (11.3, retained). A defensive
  violation due earlier than the attacking expiry is called first, as the earlier event (16.1). A different precedence is
  DreLen's to set. Returns True if it dealt with the attacking expiry."""
  s=self.s
  if s.advantage is not None:return False
  t=s.live_ms-max(0,over_ms-5000);due=self.zone_due()
  if not due or due[0][0]>t:return False
  if due[0][0]<t:self.zone_call();return True #an earlier, uncalled defensive offence comes first; the attacking expiry is judged after it
  first=s.zone_violations==0
  self.count('zone_offences_simultaneous');self.emit('simultaneous_offences','15.5',attacking={'player':p.id,'reason':reason},defending=[d[1]for d in due if d[0]==t],
            resolution='offset_same_severity'if first else'penalty_chance_offence_prevails',live_ms=t)
  if reason=='keeper_hold':self.discipline(p.id,'warning')
  if not first:self.zone_call();return True
  self.zone_call(offset=True);self.award(s.owner,s.ball.x,s.ball.y,'offsetting_fouls');return True
 def zone_overdue(self,p):
  """C4.0: is this defender, at this instant, over his unmarked allowance, in a zone, with no exemption? The marking test is
  made on positions as they are now, not as they were when his count was last updated. Returns the witness, or None."""
  s=self.s
  if not self.c4_occ or s.owner is None or p.team==s.owner or not p.active or p.role=='archer'or p.frozen(s.now):return None
  j=self.zone(p.x,p.y)
  if j is None or(p.role=='keeper'and j==s.own_zone(p.team))or p.unmarked_ms[j]<5000:return None
  near,dist=self.zone_witness(p)
  if near is not None and dist<=self.mark_d:return None
  return{'player':p.id,'zone':j,'eligible':self.eligible(p),'unmarked_ms':p.unmarked_ms[j],'nearest_opponent':near,'nearest_opponent_m':None if dist is None else round(dist,3),'marking_distance_m':self.mark_d,'called_before':p.zone_fouled[j]>0,'compliance_time_left_ms':max(0,p.zone_fouled[j]-s.live_ms)}
 def zone_intervention(self,p,act):
  """C4.0: a defender who is over his allowance and unmarked is about to control or play the ball, or block a shot.
  Always recorded. A violation of his that is due at this very millisecond is called before his play counts, so it cannot be
  lost to the change of possession his own play would cause.
  PROPOSAL, NOT CANON, off unless CALIBRATION['zone_direct_penalty'] = 1: the intervention itself is a penalty run. One
  penalty: no first-violation remedy is given for the same incident. Returns True if play was stopped."""
  s=self.s;b=s.ball
  if not self.live():return False
  self.zone_reconcile() #C4.0 r2: marking and exits as they stand at this instant, before anyone is judged
  w=self.zone_overdue(p)
  if w is None:return self.zone_due_first()
  self.count('zone_overdue_interventions');self.emit('zone_overdue_intervention','C4.0-zone',act=act,ball_mode=b.mode.value,scoring_attempt=b.mode==BallMode.SHOT,direct_penalty_rule=self.zone_direct,**w)
  if self.zone_direct:
   s.zone_violations+=1;self.count('zone_violations');self.count('zone_direct_penalties')
   self.emit('zone_violation','C4.0-zone',team=p.team,against=s.owner,number_in_possession=s.zone_violations,remedy='direct_penalty_run',resolved_live_ms=s.live_ms,called_live_ms=s.live_ms,participants=[w],personal_sanction=None)
   self.foul(p.id,None,'zone_intervention',penalty=True);return True
  return self.zone_due_first()
 def zone_due_first(self):
  """C4.0: every defensive violation due at this instant is called before a defender's control or play of the ball at this
  instant counts, so that the change of possession it may cause cannot erase it. Returns True if play was stopped.
  C4.0 r2 (the Lead's audit): first the marking exemptions and the arc exits are brought up to this instant (zone_reconcile),
  so that a defender who is marked at the moment of the play is not called on a count from before it."""
  self.zone_reconcile()
  while self.live()and self.zone_due():self.zone_call()
  return not self.live()
 def exit_interference(self,p,j):
  #Telemetry only: the player was moving outward and in an opponent's engagement. This is not a finding of obstruction.
  s=self.s;gx=0 if j==0 else 100;rx,ry=p.x-gx,p.y-50;outward=(p.vx*rx+p.vy*ry)/max(.1,norm(rx,ry))>.5
  return bool(outward and any(p.id in(k[0],k[1])and s.players[k[0]].team!=s.players[k[1]].team for k in s.engagements))
 def zone_reconcile(self):
  """C4.0 r2: bring every occupancy witness up to this instant without adding any time: a marking exemption that holds now
  renews the allowance, and a lawful arc exit resets the counts, exactly as the next update would. Used where a defender's
  play on the ball must be judged at its own instant (zone_due_first, zone_intervention)."""
  self.occupancy(0,watch=False)
 def occupancy(self,dt,watch=True):
  """C2 Keeper Zone occupancy. Pelvis position decides; the arc belongs to the zone.
  Team in possession: five seconds per zone. The count resets only on an exit across the arc inside the field. Outside the
  field it is paused and kept, and re-entry does not reset it.
  Team out of possession: exempt while within marking distance of any eligible opponent in the field; otherwise a
  five-second unmarked allowance, renewed by regaining marking or by an exit across the arc.
  A Keeper is exempt in his own zone. Counts pause while frozen and during recognised tackle recovery, and do not accrue in dead time."""
  s=self.s;att=None
  for p in s.players.values():
   if not p.active or p.role=='archer':continue
   infield=0<=p.x<=100 and 0<=p.y<=100;zn=self.zone(p.x,p.y)
   for j in(0,1):
    loc='off'if not infield else'in'if zn==j else'out';prev=p.zone_loc[j]
    if prev!=loc:
     stored=p.zone_ms[j]or p.unmarked_ms[j]
     if prev=='in'and loc=='out':
      if stored or p.zone_fouled[j]:self.count('zone_exits_valid_with_stored_time');self.emit('zone_exit_valid','C2-5',player=p.id,zone=j,stored_ms=p.zone_ms[j],unmarked_ms=p.unmarked_ms[j])
      if self.c4_occ and p.zone_fouled[j]:self.emit('zone_compliance','C4.0-zone',player=p.id,zone=j,how='left_across_the_arc',ms_before_deadline=p.zone_fouled[j]-s.live_ms)
      p.zone_ms[j]=0;p.unmarked_ms[j]=0;p.zone_fouled[j]=0
      keep=s.advantage['c2'].get('keep')if s.advantage and'c2'in s.advantage else None
      if keep and p.id in keep: #a witnessed lawful exit also resets what a recalled advantage would give back
       for v in keep[p.id]:v[j]=0
     elif prev=='in'and loc=='off'and stored:self.count('zone_exits_over_end_line_with_stored_time');self.emit('zone_exit_invalid','C2-5.1',player=p.id,zone=j,stored_ms=p.zone_ms[j],unmarked_ms=p.unmarked_ms[j])
     elif prev=='off'and loc=='out'and stored:self.emit('zone_reentry_no_reset','C2-5.1',player=p.id,zone=j,stored_ms=p.zone_ms[j],unmarked_ms=p.unmarked_ms[j])
     p.zone_loc[j]=loc
    if loc!='in'or s.owner is None:continue
    if p.role=='keeper'and j==s.own_zone(p.team):continue
    paused=dt<=0 or p.frozen(s.now)or s.now<p.tackled_until
    if p.team==s.owner:
     if not paused:p.zone_ms[j]+=dt
     continue
    if att is None:att=[q for q in s.players.values()if q.active and q.role!='archer'and q.team==s.owner and self.eligible(q)and q.posture!='grounded']
    if not p.frozen(s.now)and any(norm(q.x-p.x,q.y-p.y)<=self.mark_d for q in att):
     if self.c4_occ and p.zone_fouled[j]:
      q=min(att,key=lambda q:norm(q.x-p.x,q.y-p.y));self.emit('zone_compliance','C4.0-zone',player=p.id,zone=j,how='marking_regained',ms_before_deadline=p.zone_fouled[j]-s.live_ms,marking=q.id,distance_m=round(norm(q.x-p.x,q.y-p.y),3))
     p.unmarked_ms[j]=0;p.zone_fouled[j]=0 #marking is regained whenever it is true, also in dead time
    elif not paused:p.unmarked_ms[j]+=dt
    elif self.c4_occ and dt>0 and p.zone_fouled[j]>s.live_ms:p.zone_fouled[j]+=dt #C4.0: a called defender who cannot move (frozen, or in recognised tackle recovery) is not using his compliance time
  if watch and self.c3b and self.assume['exit_protection']:self.exit_watch()
 def strip(self,actor,target,witnessed=False):
  s=self.s
  if s.ball.carrier!=target:return False
  if witnessed:
   #C3a: a strip scheduled by the kernel was lawful when scheduled. If a freeze or exclusion has intervened it simply does not happen;
   #a stale prediction must not be turned into an ineligible-contact foul.
   if not(self.eligible(s.players[actor])and self.eligible(s.players[target])):
    self.emit('superseded_observation','16.1-16.2',kind='strip',actor=actor,target=target);return False
  elif not self.engage(actor,target,'tackle'):return False
  self.release(target,(s.players[target].vx,s.players[target].vy,0),'loose',forced=True)
  s.ball.scoring=True #A legal strip is a fumble, not a mandatory ineligible release.
  self.emit('strip','6.4;5.2',actor=actor,target=target);return True
 def go_down(self,p):
  """C3b: an athlete goes to ground. He keeps his horizontal velocity and slides, slowed by ground friction
  (slide_friction x g). He can begin to rise once he is sliding no faster than get_up_max_slide_mps, and rising takes
  get_up_time_s x (1.5 - balance). Nothing else acts on a grounded athlete (he is not a solid body and cannot be held), so the
  instant he is upright is known when he goes down. An athlete already down is not put down again."""
  s=self.s;A=self.assume
  if p.posture=='grounded'and s.now<p.next_action:return
  v=norm(p.vx,p.vy);a=A['slide_friction']*A['gravity'];slide=max(0.,v-A['get_up_max_slide_mps'])/a if a>0 else 0.;rise=A['get_up_time_s']*(1.5-p.a.balance)
  p.posture='grounded';p.down_at=s.now;p.next_action=s.now+int(math.ceil(1000*(slide+rise)-1e-9))
  self.emit('c3_down','C3b-1',player=p.id,speed_mps=round(v,3),slide_ms=round(1000*slide,1),rise_ms=round(1000*rise,1),upright_at=p.next_action)
 def grounded(self,pid):
  s=self.s;p=s.players[pid]
  if self.c3b:self.go_down(p)
  else:p.posture='grounded';p.next_action=s.now+800
  if s.ball.mode==BallMode.CONTESTED:self.held();return
  if s.ball.carrier==pid:
   if s.phase==Phase.PENALTY:self.finish_penalty(0);return
   self.release(pid,(p.vx,p.vy,0),'loose',forced=True)
  self.emit('grounded','6.8',player=pid)
 def freeze(self,pid,arrow=None,panel=True,direct=True,in_range=True):
  s=self.s;p=s.players[pid]
  if s.phase==Phase.FLIGHT or not self.live():return False
  protected_keeper=p.role=='keeper'and self.zone(p.x,p.y)==s.own_zone(p.team)
  broad=self.config.get('ruleset','1.0.1')=='1.0.2'
  valid=panel and direct and in_range and self.eligible(p)and not protected_keeper and s.now>p.immune_until and (broad or s.ball.carrier==pid)
  if not valid:self.emit('inert_impact','3.6;7.1',player=pid,arrow=arrow);return False
  was_carrier=s.ball.carrier==pid
  if was_carrier:self.release(pid,(p.vx,p.vy,p.vz),'loose',forced=True)
  p.freeze_until=s.now+5000;p.immune_until=s.now+15000
  s.engagements={k:e for k,e in s.engagements.items()if pid not in(k[0],k[1])}
  self.emit('freeze','WR-02;7.1–7.4'if broad else'7.1–7.4',player=pid,arrow=arrow,until=p.freeze_until,immune_until=p.immune_until,was_carrier=was_carrier);return True
 def archer_in_lane(self,p):
  low=self.s.ends[p.team]==0
  return (0<=p.x<=50 and-10<=p.y<=-3)if low else(50<=p.x<=100 and 103<=p.y<=110)
 def shoot_arrow(self,pid,target,velocity,origin=None):
  s=self.s;p=s.players[pid];q=s.quivers[p.team]
  not_live=not self.live()or s.phase==Phase.OPENING and s.owner is None
  if q.loaded>0 and q.spent<q.allocation:
   q.loaded-=1;q.spent+=1
  else:self.illegal(pid,'ammunition');return False
  if not_live:self.illegal(pid,'early_arrow');return False
  if p.role!='archer'or not self.eligible(p,False)or not self.archer_in_lane(p):self.illegal(pid,'archer_lane');return False
  point=origin or(p.x,p.y,.72*p.a.height)
  if target=='ball':pos=(s.ball.x,s.ball.y,s.ball.z);legal=s.ball.carrier is None and not(s.recovery and s.phase==Phase.AWARD) #C2: an awarded recovery ball is not a legal intended target
  else:
   t=s.players[target];pos=(t.x,t.y,t.z+.55*t.a.height)
   legal=t.team!=p.team and self.eligible(t)and s.now>t.immune_until and not(t.role=='keeper'and self.zone(t.x,t.y)==s.own_zone(t.team))
  d=math.dist(point,pos)
  if not legal or not(10<=d<=70):self.illegal(pid,'archery_target');return False
  speed=math.sqrt(sum(v*v for v in velocity))
  if speed>self.pocket.get("arrow_limit",30)+1e-6 or .5*.042*speed*speed>max(20,.5*.042*self.pocket.get("arrow_limit",30)**2)+1e-6:self.illegal(pid,'arrow_speed');return False
  if s.now<q.reload_until or s.now-q.last_release<2000:
   self.illegal(pid,'ammunition');return False
  q.last_release=s.now
  ar=Arrow(self.next_arrow,p.team,pid,target,*point,*velocity,point,s.now);self.next_arrow+=1;s.arrows.append(ar)
  self.emit('arrow_release','3.7–3.8',arrow=ar.id,player=pid,target=target,velocity=list(velocity),range=d,remaining=q.allocation-q.spent);return ar
 def reload(self,pid):
  s=self.s;p=s.players[pid];q=s.quivers[p.team];low=s.ends[p.team]==0
  service=(-10<=p.y<=-5)if low else(105<=p.y<=110)
  if p.role!='archer'or not self.eligible(p,False)or not service or q.spent>=q.allocation:return False
  if s.now<q.reload_until:return False
  q.reload_until=s.now+5000;q.loaded=0
  self.emit('reload_start','3.8',player=pid,ready=q.reload_until);return True
 def arrow_impact(self,arrow_id,target,panel=True,kind='player'):
  s=self.s;ar=next((a for a in s.arrows if a.id==arrow_id),None)
  if ar is None or not ar.live:return False
  ar.live=False
  if kind=='player':
   p=s.players[target];d=math.dist(ar.origin,(ar.x,ar.y,ar.z))
   if p.team==ar.team:self.emit('inert_impact','3.7;7.1',player=target,arrow=ar.id,reason='teammate');return False
   return self.freeze(target,ar.id,panel,ar.first_impact,10<=d<=70)
  if kind=='ball'and s.recovery and s.phase==Phase.AWARD:
   #C2: a previously legal arrow displaces the awarded ball. Neutral interruption; original spot; at least two seconds on resumption.
   self.emit('arrow_ball','7.1',arrow=ar.id,recovery=True);self.restore_recovery('incidental_arrow',remaining=max(2000,s.award_deadline-s.now));return False
  if kind=='ball'and(self.live()or s.phase==Phase.FLIGHT):
   s.ball.version+=1;s.ball.vx+=ar.vx*.07;s.ball.vy+=ar.vy*.07;s.ball.vz+=ar.vz*.07
   s.ball.last_touch=ar.team;self.emit('arrow_ball','7.1',arrow=ar.id)
  else:self.emit('arrow_stop','3.9',arrow=ar.id,kind=kind)
  return False
 def award(self,team,x,y,reason,foul=False,fresh=False,normalize=True):
  s=self.s
  if s.extension and team!=s.extension_team:return self.end_period()
  if team is None:team=s.alternate
  old=s.owner;keep=None
  if s.recovery and s.recovery['team']==team:
   #C2: a neutral or same-team stoppage during a first-tackle recovery restores the recovery at its original spot.
   #A failed advantage is different: play returns to the foul instant, so the recovery is superseded. So is it by a fresh possession (after a penalty).
   if reason!='advantage_recalled'and not fresh:return self.restore_recovery(reason,floor=foul)
   self.emit('recovery_superseded','C2-3.2',reason=reason);s.recovery=None
  if self.c2_any and s.phase==Phase.DEAD and s.restart and s.restart.kind!='free_pass'and s.restart.team==team and not fresh and reason!='advantage_recalled':
   keep=s.restart;x,y=keep.x,keep.y;normalize=False #C2: an inbound or a restored recovery is retaken at its own mark, never relocated
  self.new_owner(team,reason)
  if fresh and old==team:self.c2_new_possession(old,team,reason) #C2: a fresh clock for the same team (after a goal against it, or a penalty) is a new possession
  if fresh:s.possession_ms=self.play_ms
  elif old==team and foul:s.possession_ms=min(self.play_ms,max(20000,s.possession_ms))
  if normalize:x,y=restart_point(x,y,self.s.keeper_zone_radius)
  s.phase=Phase.DEAD;s.ball.version+=1;s.ball.carrier=None;s.ball.mode=BallMode.DEAD;s.ball.contested=();s.contested_until=None;s.ball.x=x;s.ball.y=y;s.ball.z=.1075;s.ball.vx=s.ball.vy=s.ball.vz=0;s.ball.scoring=False;s.ball.last_releaser=None
  s.restart=Restart(team,x,y,reason,created_at=s.now);s.tail_until=None;s.award_deadline=None;s.engagements.clear();s.stoppages+=1
  if keep:r=s.restart;r.kind=keep.kind;r.clearance=keep.clearance;r.remaining=keep.remaining;r.taker_spot=keep.taker_spot;r.note=keep.note
  for ar in s.arrows:ar.live=False
  self.flush_discipline()
  if self.terminal_grounds:return #C4.0: the match is about to end at this instant; no restart is announced
  self.emit('restart_awarded','10.2–10.6',team=team,spot=[x,y],reason=reason)
 def ready(self,taker):
  s=self.s;r=s.restart
  if s.phase!=Phase.DEAD or not r:return False
  p=s.players[taker]
  if r.kind=='recovery':return False
  able=self.eligible(p)or(r.kind=='inbound'and p.eligible(s.now)and p.role!='archer'and p.posture!='grounded') #C2: the inbound taker stands just outside the field
  if p.team!=r.team or not able or norm(p.x-r.x,p.y-r.y)>.5:return False
  if any(q.team!=r.team and self.eligible(q)and q.role!='archer'and norm(q.x-r.x,q.y-r.y)<r.clearance-1e-6 for q in s.players.values()):return False
  r.ready_at=s.now;r.taker=taker;self.emit('restart_ready','10.3',taker=taker);return True
 def restart_release(self,taker,velocity,target=None,method='hand'):
  s=self.s;r=s.restart
  if not r or s.phase!=Phase.DEAD:return False
  p=s.players[taker]
  able=self.eligible(p)or(r.kind=='inbound'and p.eligible(s.now)and p.role!='archer'and p.posture!='grounded')
  if r.ready_at is None or s.now-r.ready_at>5000 or r.taker!=taker or method!='hand' or norm(p.x-r.x,p.y-r.y)>.5 or not able:
   self.award(s.other(r.team),r.x,r.y,'restart_fault',fresh=True);return False
  if math.sqrt(sum(v*v for v in velocity))>self.pocket.get("ball_limit",40)+1e-6:self.illegal(taker,'ball_release_speed');return False
  if any(q.team!=r.team and self.eligible(q)and q.role!='archer'and norm(q.x-r.x,q.y-r.y)<r.clearance-1e-6 for q in s.players.values()):
   if r.kind=='inbound':
    #C2: retake at the same mark, no relocation, with the clock floor and the ordinary technical discipline for the nearest encroacher
    q=min((q for q in s.players.values()if q.team!=r.team and self.eligible(q)and q.role!='archer'and norm(q.x-r.x,q.y-r.y)<r.clearance-1e-6),key=lambda q:(norm(q.x-r.x,q.y-r.y),q.id))
    self.emit('inbound_encroachment','C2-4.1',player=q.id,distance=round(norm(q.x-r.x,q.y-r.y),3));self.pending_discipline.append((q.id,'warning',False));self.inbound(r.team,r.x,r.y,'defensive_restart_fault',foul=True)
   else:self.award(r.team,r.x,r.y,'defensive_restart_fault',foul=True)
   return False
  if r.reason=='held_ball':s.alternate=s.other(r.team)
  b=s.ball;b.version+=1;b.mode=BallMode.PASS;b.x=r.x;b.y=r.y;b.z=p.hand_height;b.vx,b.vy,b.vz=velocity;b.release_time=s.now;b.last_touch=p.team;b.last_releaser=taker;b.scoring=False;b.intended=target
  s.phase=Phase.LIVE;s.restart=None
  self.emit('restart_release','10.4',taker=taker,target=target,velocity=list(velocity))
  if r.kind!='inbound':self.reconstruction_check(p,'restart_release') #C2: an ordinary in-field release beyond the arc clears; the inbound itself does not
  return True
 def boundary(self,x=None,y=None,carrier=None):
  s=self.s;b=s.ball
  if s.phase in(Phase.DEAD,Phase.BREAK,Phase.FINAL,Phase.SUSPENDED):return
  x=b.x if x is None else x;y=b.y if y is None else y
  if s.phase==Phase.PENALTY:self.finish_penalty(0);return
  if s.phase==Phase.FLIGHT:self.end_flight('out',x,y);return
  if s.phase==Phase.AWARD:team=s.owner
  else:team=s.other(b.last_touch)if b.last_touch else None
  if s.phase==Phase.OPENING and team is None:return self.failed_hunt('unclaimed_out')
  b.mode=BallMode.OUT;b.carrier=None
  self.emit('boundary','10.1',crossing=[x,y],last_touch=b.last_touch,carrier=carrier)
  self.award(team,x,y,'boundary')
 def goal(self,defending,y=None,z=None):
  s=self.s;b=s.ball
  if s.phase not in(Phase.LIVE,Phase.OPENING,Phase.AWARD,Phase.FLIGHT,Phase.PENALTY):return False
  y=b.y if y is None else y;z=b.z if z is None else z
  if not legal_goal(y,z,b.radius):self.boundary(b.x,y);return False
  rc=s.reconstruction
  if rc and s.penalty is None and s.own_zone(defending)==rc['zone']:
   #C2: while the attacked zone is uncleared no goal counts in that aperture, including a deflected own goal.
   self.count('uncleared_no_goals');self.emit('no_goal','C2-4.2',reason='reconstruction_uncleared');self.boundary(b.x,y);return False
  if s.phase==Phase.AWARD or not b.scoring:
   self.emit('no_goal','9.1',reason='ineligible_ball');self.boundary(b.x,y);return False
  p=s.players.get(b.carrier)
  if p and(not self.eligible(p)or p.posture=='grounded'):
   self.emit('no_goal','9.1;16.2',reason='ineligible_carrier');self.boundary(b.x,y);return False
  scoring=s.other(defending)
  carried=bool(p and p.team==scoring and b.control_time<s.now)
  origin=getattr(b,'pocket_origin',None)
  outside=bool(not carried and origin and(self.territory(scoring,*origin)=='outside_release'if self.c4c2 else self.zone(*origin)!=s.own_zone(defending))) #C4c2 review: on the arc is outside
  own_goal=bool(not carried and ((p and p.team==defending) or getattr(b,'pocket_release_team',scoring)==defending))
  if outside and not own_goal and self.pocket.get('zone_only',False) and s.penalty is None:
   self.emit('no_goal','Pocket-S1',reason='outside_release',origin=origin);self.boundary(b.x,y);return False
  method='carry' if carried else 'own_goal' if own_goal else 'outside_release' if outside else 'inside_release'
  points=self.pocket.get('carry_points',5) if carried else self.pocket.get('outside_points',3) if outside and not own_goal and s.penalty is None else self.pocket.get('release_points',3)
  carry_ok=self.c4b and self.pocket.get('carry_value',0)>0 and carried #C4b: Carry enabled (configurations B and C)
  if self.pocket.get('release_territories')and carry_ok:
   #C4b, the Lead's position accepting Claude's Carry eligibility: eligible secure control clearly before the whole ball crossed
   #(control from an earlier millisecond); the carrier need not cross. A grounding or freeze at the crossing, or a catch at it,
   #is not a Carry (the first is refused above as an ineligible carrier; the second is a released ball, handled in batch).
   method='carry';points=self.pocket['carry_value']
  elif self.pocket.get('release_territories'):
   if p and p.team==scoring:
    self.emit('no_goal','Pocket-S4',reason='release_required')
    if s.penalty is not None:self.finish_penalty(0)
    else:self.boundary(b.x,y)
    return False
   if not own_goal and origin is None:
    self.emit('no_goal','Pocket-S4',reason='missing_release_origin');self.boundary(b.x,y);return False
   method='own_goal' if own_goal else self.territory(scoring,*origin)
   points=self.pocket.get('release_points',9) if own_goal or s.penalty is not None else self.territory_points(method)
   dt_=(getattr(b,'c4c2_def',None)or[])[getattr(b,'c4c2_off_i',0):]if self.c4c2 else None
   if self.c4c2 and own_goal and p is None and dt_:
    #C4c2: the team's own flight redirected into its own goal by an opponent without secured control. OPEN (the Lead): not a true
    #own goal (an opponent intervened) and not settled by the failed-save ruling. Prototype, switch reversal_rule: 0 = the own-goal
    #value (the zone-release value) credited to the opponents, recorded as its own method; 1 = the redirecting opponent's touch is
    #valued as an offensive play from his support foot.
    method='reversal';last=dt_[-1]
    if self.reversal_rule==1 and s.penalty is None:points=self.territory_points(self.territory(scoring,last[1],last[2]))
  if s.penalty is not None:self.finish_penalty(points);return True
  if s.advantage:s.advantage=None;self.emit('advantage_realized','11.2',method='goal')
  s.score[scoring]+=points
  if self.c4c2 and method!='carry':
   dl=getattr(b,'c4c2_def',None)or[]
   c2rec={'flight_team':getattr(b,'pocket_release_team',None),'last_offensive_toucher':getattr(b,'c4c2_off',None),'defensive_touches':[list(x)for x in dl],
          'offensive_goal_through_defensive_touch':bool(dl)and method not in('own_goal','reversal')}
  else:c2rec={}
  cause=self.emit('goal','9.1–9.3',team=scoring,points=points,defending=defending,method=method,release_origin=origin,control_time=b.control_time,**c2rec,
                  **({'origin_witness':None if method=='carry'else getattr(b,'c4b_origin',None),'launch_point':None if method=='carry'else getattr(b,'c4b_launch',None),
                      'origin_to_goal_m':None if method=='carry'or origin is None else round(norm(origin[0]-s.attack_goal(scoring),origin[1]-50),3)}if self.c4b else{}))
  s.last_score_cause=cause;self.score_history.append({'cause':cause,'team':scoring,'points':points,'t_ms':s.now})
  self.minor_goal_release(defending)
  if s.extension:return self.end_period()
  if s.game_ms<=0:return self.end_period()
  offset=max(25,s.keeper_zone_radius+.5);x=s.ends[defending]+(offset if s.ends[defending]==0 else-offset)
  self.award(defending,x,50,'goal',fresh=True,normalize=False);return True
 def illegal(self,pid,reason):
  p=self.s.players[pid]
  if reason=='ineligible_ball_action'and p.active and p.frozen(self.s.now):reason='frozen_participation'
  self.foul(pid,None,reason,major=reason=='ineligible_ball_action')
 def foul(self,actor,victim=None,reason='hold',major=False,danger=False,penalty=False,certain=False,carry=False,advantage=False,disqualify=False):
  s=self.s;a=s.players[actor];victim_team=s.players[victim].team if victim else s.other(a.team)
  if s.phase==Phase.FINAL:return
  if danger:
   a.dangerous_majors=getattr(a,'dangerous_majors',0)+1
   if a.dangerous_majors>=2:disqualify=True
  self.emit('foul','11;15',actor=actor,victim=victim,reason=reason,major=major,danger=danger,penalty=penalty)
  sanction='dq'if disqualify else'major'if major or danger or reason in('hold','deliberate_delay','transition_foul')else'minor'if reason in('illegal_tackle','late_hold','archery_target','archer_lane','ammunition','arrow_speed','early_arrow')else'warning'
  #C4.0, decided by DreLen on 7 October: a team does not forfeit off Keeper Zone violations. Builder's reading, provisional until he
  #confirms it: neither kind of zone expiry enters the warning and exclusion ladder at all. The category is narrow: the attacking
  #residence expiry and the defending unmarked-allowance expiry (and the proposed intervention penalty, which is the same incident).
  #Exit obstruction, recovery interference, the Keeper's ball-hold and every contact foul keep their own discipline.
  if self.c4_zone and reason in('zone_expiry','zone_unmarked','zone_intervention'):sanction=None
  if s.phase==Phase.PENALTY:
   pen=s.penalty
   if a.team!=pen['team']and pen['keeper_fouls']>=1 and sanction not in('dq',None):sanction='major'
   self.discipline(actor,sanction,permanent=disqualify)
   if a.team==pen['team']:self.finish_penalty(0)
   else:
    pen['keeper_fouls']+=1
    if pen['keeper_fouls']>=2:self.finish_penalty(self.c4b_auto_points(True)if self.c4b else self.pocket.get("release_points",9) if self.pocket.get("release_territories") else self.pocket.get("carry_points",5))
    else:self.reset_penalty()
   return
  spot=(s.ball.x,s.ball.y)
  if victim and s.attack_sign(victim_team)*(s.players[victim].x-spot[0])>0:spot=(s.players[victim].x,s.players[victim].y)
  if advantage and not danger and s.owner==victim_team and not certain and not penalty and self.live():
   if s.advantage is None:
    s.advantage={'team':victim_team,'g':s.game_ms,'p':s.possession_ms,'spot':spot,'until':s.now+3000,'origin_x':s.ball.x}
    if self.c2_any:s.advantage['c2']=self.c2_snapshot()
   if sanction is not None:self.pending_discipline.append((actor,sanction,disqualify))
   self.emit('advantage','11.2',team=victim_team);return
  restore=None
  if s.advantage:
   #Rulebook 11.3: an offence before the advantage is realised ends play and the earlier defensive foul is enforced, also when the
   #later offender is the advantaged team (who is still sanctioned below). This is retained behaviour, not a C2 change.
   adv=s.advantage;s.game_ms=adv['g'];s.possession_ms=adv['p'];victim_team=adv['team'];spot=adv['spot'];s.advantage=None;restore=(adv,s.owner!=adv['team'])
   if s.recovery and'c2'in adv:self.emit('recovery_superseded','C2-3.2',reason='foul_during_advantage');s.recovery=None
  self.discipline(actor,sanction,permanent=disqualify)
  if s.phase==Phase.FINAL:return
  if certain:
   self.penalty_goal(victim_team,self.c4b_auto_points(carry)if self.c4b else self.pocket.get("release_points",9) if self.pocket.get("release_territories") else self.pocket.get("carry_points",5) if carry else self.pocket.get("release_points",3));return
  if penalty:self.start_penalty(victim_team);return
  if s.game_ms<=0 and not s.extension:
   s.extension=True;s.extension_team=victim_team;s.possession_ms=10000
  elif s.extension:s.possession_ms=10000
  if s.recovery and s.recovery['team']==victim_team and not s.extension:
   #C2: a defensive foul during a first-tackle recovery restores the recovery at its original spot, with the defensive-foul clock floor.
   self.restore_recovery('defensive_foul:'+reason,floor=True);return
  self.award(victim_team,*spot,'foul',foul=not s.extension)
  if restore:self.c2_restore(restore[0],restore[1],'foul_during_advantage')
  if s.extension:s.possession_ms=10000
 def flush_discipline(self,resolve=True):
  """Sanctions deferred behind an advantage are all administered at the stoppage, as one instant (rulebook 11.2: 'applied at
  the next stop'). C4.0: a ground for ending the match that arises while they are administered is held until every one of
  them is on the record, and the grounds are then judged together (terminal_resolve)."""
  pending=self.pending_discipline;self.pending_discipline=[];self.terminal_hold+=1
  try:
   for args in pending:self.discipline(args[0],args[1],args[2])
  finally:self.terminal_hold-=1
  if resolve and not self.terminal_hold:self.terminal_resolve()
 def terminal_ground(self,team,reason):
  #C4.0: a team can no longer continue (rulebook 1.4). One ground per team per instant.
  if all(t!=team for t,_ in self.terminal_grounds):self.terminal_grounds.append((team,reason))
  if not self.terminal_hold:self.terminal_resolve()
 def terminal_resolve(self):
  """C4.0: judge the grounds raised at one instant, from the rulebook:
  1. Both teams unable to continue: abandoned, referred for replay, no winner (1.4, 18.8).
  2. One team unable to continue: that team forfeits (1.4, 18.6).
  The order in which the sanctions happened to be queued decides nothing. A horn that would decide the match by score gives
  no exemption (C4.0 r2, the Lead's audit: 1.4 makes insufficient slots after exclusions a forfeit; that amendment is DreLen's)."""
  g=self.terminal_grounds;self.terminal_grounds=[]
  if not g:return False
  if len(g)>1:
   self.emit('abandoned','1.4;18.8',reason='both_teams_unable_to_continue',grounds=[list(x)for x in g]);self.complete('abandoned_replay')
  self.forfeit(*g[0])
 def discipline(self,pid,kind,permanent=False):
  s=self.s;p=s.players[pid]
  if kind is None:return #C4.0: an offence that carries no personal sanction (a Keeper Zone expiry under the ruling of 7 October)
  if kind=='warning':
   if 'technical'in s.warning[p.team]:kind='minor'
   else:s.warning[p.team].add('technical');self.emit('warning','15',player=pid);return
  if kind=='minor':p.minor_count+=1;ms=60000
  else:p.major_count+=1;ms=120000
  dq=kind=='dq'or p.major_count>=2 or p.minor_count>=3
  if dq:ms=120000
  was_active=p.active;p.disqualified=dq;was_role=p.role;p.active=False
  if was_active and was_role=='field':self.slot_vacate(p)
  previous=next((d for d in self.debts if d['player']==pid and(d['remaining']>0 or d['permanent'])),None)
  if previous:
   previous['remaining']=max(previous['remaining'],ms)if dq else previous['remaining']+ms;previous['permanent']|=permanent
   if kind!='minor':previous['kind']=kind
   ms=previous['remaining']
  else:self.debts.append({'team':p.team,'player':pid,'remaining':ms,'permanent':permanent,'kind':kind,'seq':self.event_seq})
  p.exclusion_ms=ms
  if was_role in('keeper','archer')and not previous:
   eligible=[q for q in s.players.values()if q.team==p.team and q.id!=pid and q.eligible(s.now)and q.role=='field']
   if eligible:
    q=max(eligible,key=lambda q:q.a.keeper_skill if was_role=='keeper'else q.a.archery_accuracy)
    if self.c2_occ:self.slot_vacate(q);self.slot_inherit(p,q) #C2: the promoted player takes the specialist slot's state; his own field slot is left for its replacement
    q.role=was_role;q.x=p.x;q.y=p.y;q.vx=q.vy=0
    self.emit('specialist_replacement','14.3',old=pid,new=q.id,role=was_role)
   else:self.terminal_ground(p.team,'no_specialist');return
  self.emit('discipline','15.2–15.4',player=pid,kind=kind,disqualified=dq,permanent=permanent,duration=ms)
  if sum(1 for d in self.debts if d['team']==p.team and(d['permanent']or d['remaining']>0))>3:self.terminal_ground(p.team,'minimum_lineup')
 def same_incident_discipline(self,pid,kinds,permanent=False):
  rank={'warning':0,'minor':1,'major':2,'dq':3}
  self.discipline(pid,max(kinds,key=lambda k:rank[k]),permanent)
  self.emit('multiple_sanctions_recorded','15.3',player=pid,sanctions=kinds)
 def minor_goal_release(self,team):
  choices=[d for d in self.debts if d['team']==team and d['kind']=='minor'and d['remaining']>0 and not d['permanent']]
  if choices:
   d=min(choices,key=lambda d:(d['remaining'],d['seq']));d['remaining']=0;self.s.players[d['player']].exclusion_ms=0;self.emit('minor_released','15.6',player=d['player'])
 def sub(self,out_id,in_id):
  s=self.s;o,n=s.players[out_id],s.players[in_id]
  if o.team!=n.team or not o.active or n.active or not n.available or n.injured or n.disqualified or n.exclusion_ms>0:return False
  specialist=o.role in('keeper','archer')
  if specialist and s.phase not in(Phase.DEAD,Phase.BREAK):return False
  if s.ball.carrier==out_id:return False
  low=s.ends[o.team]==0;gate=(70,80,0)if low else(20,30,100)
  if not specialist and(not gate[0]<=o.x<=gate[1]or not(o.y+o.radius<0 if low else o.y-o.radius>100) or not gate[0]<=n.x<=gate[1]or abs(n.y-gate[2])>2 or(n.y>0 if low else n.y<100)):return False
  oldrole=o.role;o.active=False;n.active=True;n.role=oldrole;n.slot=o.slot
  n.zone_ms=list(o.zone_ms);n.outside_ms=list(o.outside_ms)
  #C2: the replacement inherits the slot's stored counts, unmarked allowance and any pending violation. Entering is not an arc exit.
  self.slot_inherit(o,n)
  #Retained from Pocket 1.1: a live freeze and the Keeper hold timer pass to the replacement. An incoming later freeze deadline is not shortened.
  n.freeze_until=max(n.freeze_until,o.freeze_until)
  n.keeper_hold_ms=o.keeper_hold_ms
  n.x,n.y=(o.x,o.y)if specialist else((gate[0]+gate[1])/2,.2 if low else 99.8)
  self.emit('substitution','14.1–14.3',out=out_id,incoming=in_id,role=oldrole,freeze_until=n.freeze_until);return True
 def replace_unavailable_specialist(self,out_id,in_id):
  s=self.s;o,n=s.players[out_id],s.players[in_id]
  if s.phase not in(Phase.DEAD,Phase.BREAK)or o.active or o.role not in('keeper','archer')or o.team!=n.team or n.active or not n.available or n.injured or n.disqualified or n.exclusion_ms>0:return False
  n.role=o.role;n.active=True;n.x=o.x;n.y=o.y;n.freeze_until=o.freeze_until;n.zone_ms=list(o.zone_ms);n.vx=n.vy=0
  if self.c2_any:self.slot_inherit(o,n) #C2: the same slot inheritance as an ordinary substitution
  self.emit('specialist_replacement','14.3–14.4',old=o.id,new=n.id,role=n.role);return True
 def validate_lineup(self):
  problems=[]
  for team in('A','B'):
   roster=[p for p in self.s.players.values()if p.team==team];active=[p for p in roster if p.active]
   if len(roster)!=22:problems.append(team+': roster must contain22')
   if sum(p.role=='keeper'for p in active)!=1:problems.append(team+': exactly one active Keeper required')
   if sum(p.role=='archer'for p in active)!=1:problems.append(team+': exactly one active Archer required')
   if not 7<=sum(p.role=='field'for p in active)<=10:problems.append(team+': Field Player count outside7–10')
  self.emit('lineup_check','1.3–1.4',passed=not problems,problems=problems);return not problems
 def injury(self,pid,concussion=False):
  s=self.s;p=s.players[pid]
  if p.active and p.role=='field':self.slot_vacate(p)
  p.injured=True;p.available=False;p.active=False
  p.medical_return_live=s.live_ms+60000;p.no_day_return=concussion
  self.emit('injury','14.4',player=pid,concussion=concussion)
  self.safety_stop('injury')
 def medical_clear(self,pid):
  p=self.s.players[pid]
  if getattr(p,'no_day_return',False)or self.s.live_ms<getattr(p,'medical_return_live',0):return False
  p.injured=False;p.available=True;self.emit('medical_clear','14.4',player=pid);return True
 def safety_stop(self,reason='hazard'):
  s=self.s
  if s.phase==Phase.OPENING and s.owner is None:return self.failed_hunt(reason)
  if s.phase==Phase.FLIGHT:return self.end_flight(reason,s.ball.x,s.ball.y)
  self.award(s.owner or s.alternate,s.ball.x,s.ball.y,'safety_'+reason)
 def start_penalty(self,team,shootout=False):
  s=self.s
  runners=[p for p in s.players.values()if p.team==team and p.eligible(s.now)and p.role!='archer']
  keepers=[p for p in s.players.values()if p.team!=team and p.role=='keeper'and p.eligible(s.now)]
  if not keepers: #C4.0: rulebook 12.3, an eligible team-mate replaces a frozen or excluded Keeper for the run; only if there is none is it a forfeit
   keepers=sorted([p for p in s.players.values()if p.team!=team and p.available and not p.injured and not p.disqualified and p.exclusion_ms<=0 and not p.frozen(s.now)and p.role!='archer'],key=lambda p:(-p.a.keeper_skill,p.id))[:1]
  if not runners and not keepers: #C4.0: neither side can stage the run; that is both teams unable to continue, not a forfeit by the side tested first
   self.terminal_hold+=1;self.terminal_ground(team,'penalty_eligibility');self.terminal_ground(s.other(team),'penalty_eligibility');self.terminal_hold-=1
   if not self.terminal_hold:self.terminal_resolve()
   return
  if not runners or not keepers:self.forfeit(team if not runners else s.other(team),'penalty_eligibility');return
  if shootout:
   used=s.shootout['used'][team];all_roster=[p for p in s.players.values()if p.team==team and p.available and not p.injured and not p.disqualified and p.exclusion_ms==0]
   if len(used)>=len(all_roster):used.clear()
   runners=[p for p in all_roster if p.id not in used];runner=max(runners,key=lambda p:p.a.ball_handling+p.a.agility);used.append(runner.id)
  else:runner=max(runners,key=lambda p:p.a.ball_handling+p.a.agility)
  keeper=keepers[0]
  s.penalty={'team':team,'runner':runner.id,'keeper':keeper.id,'until':s.now+10000,'released':False,'keeper_fouls':0,'shootout':shootout,'runner_original_role':runner.role,'saved_active':{p.id:p.active for p in s.players.values()}}
  self.reset_penalty();self.emit('penalty_start','12.1–12.4',team=team,runner=runner.id,keeper=keeper.id,shootout=shootout)
 def reset_penalty(self):
  s=self.s;pen=s.penalty;team=pen['team'];r=s.players[pen['runner']];k=s.players[pen['keeper']]
  if not r.available or r.disqualified or r.exclusion_ms>0 or r.frozen(s.now):
   runners=[p for p in s.players.values()if p.team==team and p.eligible(s.now)and p.role!='archer']
   if not runners:return self.forfeit(team,'penalty_runner')
   r=max(runners,key=lambda p:p.a.ball_handling+p.a.agility);pen['runner']=r.id;pen['runner_original_role']=r.role
  if not k.available or k.disqualified or k.exclusion_ms>0 or k.frozen(s.now): #C4.0: frozen too (12.3)
   replacements=[p for p in s.players.values()if p.team==k.team and p.available and not p.disqualified and not p.injured and p.exclusion_ms==0 and not p.frozen(s.now)and p.role!='archer']
   if not replacements:return self.forfeit(k.team,'penalty_keeper')
   k=max(replacements,key=lambda p:p.a.keeper_skill);pen['keeper']=k.id
  if not r.active:
   outgoing=next((p for p in s.players.values()if p.team==r.team and p.active and p.role=='field'),None)
   if outgoing:outgoing.active=False
  r.active=k.active=True;r.role='field'if r.role=='archer'else r.role;k.role='keeper'
  r.x=s.attack_goal(team)-s.attack_sign(team)*25;r.y=50;r.vx=r.vy=0;k.x=s.attack_goal(team);k.y=50;k.vx=k.vy=0
  s.ball=Ball(mode=BallMode.CONTROLLED,x=r.x,y=50,z=r.hand_height,carrier=r.id,control_time=s.now-1,scoring=True,last_touch=team)
  s.owner=team;s.phase=Phase.PENALTY;pen['until']=s.now+10000;pen['released']=False;s.restart=None;s.engagements.clear();self.follow_carrier()
 def finish_penalty(self,points):
  s=self.s;pen=s.penalty
  if pen is None:return
  team=pen['team'];shootout=pen['shootout'];s.players[pen['runner']].role=pen.get('runner_original_role',s.players[pen['runner']].role)
  for pid,active in pen['saved_active'].items():
   p=s.players[pid];p.active=active and not p.disqualified and p.exclusion_ms<=0 and p.available
  s.penalty=None
  if shootout:
   so=s.shootout;so['attempts'][team]+=1;so['goals'][team]+=int(points>0)
   self.emit('shootout_attempt','18.2–18.4',team=team,success=points>0)
   self.next_shootout();return
  if points:
   s.score[team]+=points;cause=self.emit('penalty_goal_scored','12.4',team=team,points=points);self.score_history.append({'cause':cause,'team':team,'points':points,'t_ms':s.now})
  else:self.emit('penalty_failed','12.4',team=team)
  if s.game_ms<=0:return self.end_period()
  self.award(team,50,50,'penalty_retained',fresh=True,normalize=False)
 def penalty_goal(self,team,points):
  s=self.s;s.score[team]+=points;cause=self.emit('penalty_goal','12.2',team=team,points=points);self.score_history.append({'cause':cause,'team':team,'points':points,'t_ms':s.now})
  if s.game_ms<=0:return self.end_period()
  self.award(team,50,50,'penalty_retained',fresh=True,normalize=False)
 def timeout(self,team):
  s=self.s
  if s.phase!=Phase.DEAD or not s.restart or s.restart.ready_at is not None or s.timeouts[team]<=0:return False
  s.timeouts[team]-=1;s.restart.created_at+=60000;self.emit('timeout','5.7',team=team,until=s.now+60000);return True
 def start_flight(self,penalty=False):
  s=self.s;s.phase=Phase.FLIGHT;s.tail_until=s.now+3000;s.tail_owner=s.owner if not penalty else s.penalty['team']
  self.emit('finishing_flight','5.5',until=s.tail_until,penalty=penalty)
 def end_flight(self,reason,x,y):
  s=self.s
  self.emit('flight_ended','5.5–5.6',reason=reason)
  if s.penalty:return self.finish_penalty(0)
  if s.advantage:return self.recall_advantage()
  if s.game_ms<=0:return self.end_period()
  self.award(s.other(s.tail_owner),x,y,'possession_expiry',fresh=True)
 def recall_advantage(self):
  s=self.s;adv=s.advantage
  if not adv:return
  s.advantage=None;s.game_ms=adv['g'];s.possession_ms=adv['p'];changed=s.owner!=adv['team']
  if s.game_ms<=0:s.extension=True;s.extension_team=adv['team'];s.possession_ms=10000
  self.award(adv['team'],*adv['spot'],'advantage_recalled',foul=not s.extension)
  self.c2_restore(adv,changed,'advantage_recalled')
  if s.extension:s.possession_ms=10000
  self.emit('advantage_recalled','11.2;16.4',restored_g=s.game_ms,restored_p=s.possession_ms)
 def clock_expiry(self):
  s=self.s;b=s.ball
  if s.phase not in(Phase.LIVE,Phase.AWARD,Phase.OPENING,Phase.PENALTY):return
  if s.phase==Phase.PENALTY:
   if s.now<s.penalty['until']:return
   if b.carrier is None and b.z>b.radius and s.penalty['released']:self.start_flight(True)
   else:self.finish_penalty(0)
   return
  if s.game_ms>0 and s.possession_ms>0:return
  if s.extension and s.possession_ms>0:return
  if b.carrier is None and b.mode in(BallMode.PASS,BallMode.KICK,BallMode.SHOT,BallMode.LOOSE)and b.z>b.radius+1e-6:
   if s.reconstruction and s.game_ms<=0:self.emit('no_finishing_flight','C2-4.2',reason='reconstruction_uncleared') #C2: no score-based finishing flight for an uncleared ball at the horn
   else:self.start_flight();return
  if s.advantage:return self.recall_advantage()
  if s.game_ms<=0:return self.end_period()
  self.award(s.other(s.owner),b.x,b.y,'possession_expiry',fresh=True)
 def end_period(self):
  s=self.s
  if s.phase==Phase.FINAL:return
  s.extension=False;s.extension_team=None;s.advantage=None;s.tail_until=None;s.penalty=None;s.ball.carrier=None;s.ball.mode=BallMode.DEAD;s.restart=None;s.engagements.clear()
  s.tackle_count=0;s.recovery=None
  if s.reconstruction:self.end_reconstruction('period_end')
  self.flush_discipline();self.period_history.append({'period':s.period,'score':dict(s.score),'t_ms':s.now});self.emit('period_end','5;18',score=dict(s.score))
  if s.period<s.regulation_periods:
   s.period+=1;s.game_ms=s.period_seconds*1000
   if s.period==3:self.exchange_ends();s.timeouts={'A':2,'B':2};s.challenges={'A':1,'B':1}
   s.quivers={t:Quiver()for t in('A','B')}
   team=s.other(s.opening_team or'A')if s.period in(2,4)else(s.opening_team or'A')
   s.owner=None;self.award(team,50,50,'quarter_start',fresh=True,normalize=False);return
  if s.period==s.regulation_periods:
   if s.score['A']!=s.score['B']:return self.complete('regulation')
   s.period+=1;s.game_ms=s.overtime_seconds*1000;s.timeouts={'A':1,'B':1};s.challenges={'A':1,'B':1};s.quivers={t:Quiver(allocation=10)for t in('A','B')};s.opening_team=None;s.opening_failures=0;self.begin_hunt();self.emit('overtime_start','18.1');return
  if s.period==s.regulation_periods+1:
   s.period+=1;s.game_ms=s.overtime_seconds*1000;self.exchange_ends();s.quivers={t:Quiver(allocation=10)for t in('A','B')};s.owner=None;self.award(s.other(s.opening_team or'A'),50,50,'overtime_half',fresh=True,normalize=False);return
  if s.score['A']!=s.score['B']:return self.complete('overtime')
  s.shootout={'attempts':{'A':0,'B':0},'goals':{'A':0,'B':0},'used':{'A':[],'B':[]},'first':'A'};self.next_shootout()
 def exchange_ends(self):
  s=self.s;s.ends={t:100-x for t,x in s.ends.items()}
  for p in s.players.values():
   p.x=100-p.x;p.y=100-p.y;p.vx=-p.vx;p.vy=-p.vy
   ext=getattr(p,'c3_ext',None)
   if self.c3b and ext:p.c3_ext=(tuple((t,-x,-y,b)for t,x,y,b in ext[0]),(-ext[1][0],-ext[1][1],ext[1][2],ext[1][3])) #C3b: an imposed-velocity record turns with the velocity it describes
  self.emit('ends_exchanged','2.2;18.1')
 def next_shootout(self):
  s=self.s;so=s.shootout;aa,bb=so['attempts']['A'],so['attempts']['B'];ga,gb=so['goals']['A'],so['goals']['B']
  if aa==bb and aa>=5 and ga!=gb:return self.complete('shootout','A'if ga>gb else'B')
  if max(aa,bb)<=5 and(ga>gb+5-bb or gb>ga+5-aa):return self.complete('shootout','A'if ga>gb else'B')
  pair=min(aa,bb);first=so['first']if pair%2==0 else s.other(so['first']);team=first if aa==bb else('A'if aa<bb else'B')
  self.start_penalty(team,True)
 def complete(self,method,winner=None):
  """C4.0: the one place a result is committed. Exactly one match_complete. Sanctions still queued behind an advantage are
  written to the record without effect on the ladder. The call then unwinds (MatchFinal): nothing after it runs."""
  s=self.s
  if winner is None and method!='abandoned_replay':winner='A'if s.score['A']>s.score['B']else'B'
  if self.pending_discipline:
   self.emit('sanctions_not_administered','11.2;15',sanctions=[[a[0],a[1]]for a in self.pending_discipline if a[1]is not None],reason='match_ended_before_the_next_stop:'+method);self.pending_discipline=[]
  s.phase=Phase.FINAL;s.ball.mode=BallMode.DEAD;s.ball.carrier=None;s.restart=None
  s.result={'winner':winner,'method':method,'score':dict(s.score),'shootout':s.shootout['goals']if s.shootout else None}
  self.emit('match_complete','18.1–18.5',result=s.result);self.final_seq=self.event_seq
  raise MatchFinal()
 def forfeit(self,team,reason):
  s=self.s;win=s.other(team)
  if s.score[win]<=s.score[team]:s.score={team:0,win:5}
  self.emit('forfeit','18.6',team=team,reason=reason);self.complete('forfeit',win)
 def suspend(self,reason):
  s=self.s
  if s.phase==Phase.FINAL:return
  self.safety_stop(reason);s.suspended_at=s.now;s.phase=Phase.SUSPENDED;self.emit('suspended','7.6;18.8',reason=reason)
 def resume(self):
  s=self.s
  if s.phase!=Phase.SUSPENDED:return False
  if s.now-s.suspended_at>=86400000:
   self.emit('abandoned','18.8');self.complete('abandoned_replay') #C4.0 r2: the retained 24-hour abandonment is committed like any result: one match_complete, no winner
  pause=s.now-s.suspended_at
  for p in s.players.values():
   if p.freeze_until>s.suspended_at:p.freeze_until+=pause
   if p.immune_until>s.suspended_at:p.immune_until+=pause
  for q in s.quivers.values():
   if q.reload_until>s.suspended_at:q.reload_until+=pause
   q.last_release+=pause
  s.phase=Phase.DEAD;s.suspended_at=None;self.emit('resumed','18.8');return True
 def neutral_offset(self,actors,major=False):
  s=self.s;self.terminal_hold+=1
  try:
   for actor in actors:self.discipline(actor,'major'if major else'minor')
  finally:self.terminal_hold-=1
  if not self.terminal_hold:self.terminal_resolve() #C4.0: offsetting fouls are one instant (inside a held batch, the batch judges); if both teams fall below the minimum the match is abandoned, not forfeited by whoever was listed first
  if s.penalty:
   s.penalty['keeper_fouls']+=1
   if s.penalty['keeper_fouls']>=2:self.finish_penalty(self.c4b_auto_points(True)if self.c4b else self.pocket.get("release_points",9) if self.pocket.get("release_territories") else self.pocket.get("carry_points",5))
   else:self.reset_penalty();self.emit('penalty_retake','12.5',reason='simultaneous_independent_fouls')
  else:self.award(s.owner or s.alternate,s.ball.x,s.ball.y,'offsetting_fouls')
 def dispatch(self,event):
  self.cause={'kind':event.kind,'actor':event.actor,'target':event.target,'at':self.s.now};d=event.data;k=event.kind
  if d.get('c1_contact'):self.c1_commit(event)
  elif k=='acquire':
   if 'ball_point'in d:self.s.ball.x,self.s.ball.y,self.s.ball.z=d['ball_point']
   self.acquire(event.actor)
  elif k=='release':self.release(event.actor,tuple(d['velocity']),d.get('kind','pass'),event.target)
  elif k=='touch':
   self.touch(event.actor,d.get('deliberate',True))
   if 'velocity'in d and self.s.ball.carrier is None:
    self.s.ball.vx,self.s.ball.vy,self.s.ball.vz=d['velocity'];self.s.ball.version+=1
    if 'ball_point'in d:self.s.ball.x,self.s.ball.y,self.s.ball.z=d['ball_point']
  elif k=='tackle':
   if self.s.players[event.target].frozen(self.s.now):self.emit('tackle_cancelled','7.4;16.2',actor=event.actor,target=event.target)
   elif'c3'in d:
    #C3b: everyone who had a material lawful hold on the carrier at the grounding (grip at or above the tackle threshold), or was in
    #lawful contact with him then and had lawfully put a material load on his balance, is owed the time to disengage from a
    #first-tackle recovery, not only the one credited with the tackle. Being within reach with a token grip is not enough.
    if self.c3b:self.grace=sorted({h['player']for h in d['c3'].get('holders',[])if h['grip']>=self.assume['tackle_grip_threshold']}|{q for q,v in d['c3'].get('lawful_supplied',{}).items()if q in d['c3'].get('in_lawful_contact',[])and v>=self.assume['contact_foul_min_shock']})
    self.emit('c3_grounding','C3-6.7',counted=True,**d['c3']);self.tackle(event.actor,event.target,d.get('body','knee'),witnessed=True);self.grace=[]
   else:self.tackle(event.actor,event.target,d.get('body','knee'))
  elif k=='ground':
   p=self.s.players[event.actor]
   if'c3'in d:
    #C3a: a physical grounding that is not a counted tackle. A carrier still in control makes the existing forced release.
    if not p.active or p.posture=='grounded':self.cause=None;return
    self.emit('c3_grounding','C3-6.7',counted=False,**d['c3'])
   self.grounded(event.actor)
  elif k=='note':self.emit(d['event'],d.get('rule','C3'),**d['data']) #C3a: a kernel log record, written at its own time inside the step
  elif k=='freeze':self.freeze(event.target,**d)
  elif k=='impact':self.arrow_impact(d['arrow'],event.target,d.get('panel',True),d.get('kind','player'))
  elif k=='goal':self.goal(d['defending'],d.get('y'),d.get('z'))
  elif k=='boundary':self.boundary(d.get('x'),d.get('y'),event.actor)
  elif k=='foul':self.foul(event.actor,event.target,**d)
  elif k=='clock':self.clock_expiry()
  elif k=='strip':self.strip(event.actor,event.target,witnessed='c3'in d)
  elif k=='frame':self.frame_contact(d.get('velocity'),d.get('point'))
  elif k=='strike':self.strike(event.actor,d['velocity'],d.get('kind','kick'))
  elif k=='held':self.held()
  elif k=='block':self.engage(event.actor,event.target,'block',d.get('surface','torso'))
  elif k=='safety':self.safety_stop(d.get('reason','hazard'))
  else:raise RulesError('Unknown event '+k)
  self.cause=None
 def batch(self,events):
  #C4.0: one batch is one instant. Grounds to end the match raised by any of its events are judged together at its end.
  self.terminal_hold+=1
  try:self.batch_events(events)
  finally:self.terminal_hold-=1
  if not self.terminal_hold:self.terminal_resolve()
 def batch_events(self,events):
  #Caller advances to the shared timestamp before the batch. Known time order is never reversed.
  events=[e for e in events if 'generation'not in e.data or e.data['generation']==self.s.ball.version]
  for e in events:e.data.pop('generation',None)
  if any(e.kind=='goal'for e in events)and self.live():
   for p in self.s.players.values():
    zn=self.zone(p.x,p.y)
    if p.active and not p.frozen(self.s.now)and zn is not None and p.zone_ms[zn]>=5000 and not(p.role=='keeper'and zn==self.s.own_zone(p.team)):
     events.append(Event('foul',p.id,data={'reason':'zone_expiry'}))
  simultaneous_fouls=[e for e in events if e.kind=='foul']
  if len({self.s.players[e.actor].team for e in simultaneous_fouls})==2 and len(events)==len(simultaneous_fouls) and len({bool(e.data.get('danger'))for e in simultaneous_fouls})==1:
   self.neutral_offset([e.actor for e in simultaneous_fouls],any(e.data.get('major')or e.data.get('danger')or e.data.get('reason')=='hold'for e in simultaneous_fouls));self.assert_invariants();return
  kept=[]
  for e in events:
   why=self.c1_reason(e)if e.data.get('c1_contact')else None
   if why is None:kept.append(e)
   else:self.c1_reject(e,why)
  events=kept
  catches=[e for e in events if e.kind=='acquire']
  if len({self.s.players[e.actor].team for e in catches})>1 and self.s.ball.carrier is None:
   if all(e.data.get('c1_contact')for e in catches):
    #C1 numerical convention, not a physical claim: secure contacts by opponents in the same clock millisecond cannot be ordered.
    self.s.ball.x,self.s.ball.y,self.s.ball.z=catches[0].data['ball_point']
    self.emit('simultaneous_contact','assumption:c1_same_millisecond',players=[e.actor for e in catches],points=[[round(v,3)for v in e.data['ball_point']]for e in catches])
    cs=getattr(self,'contact_stats',None)
    if cs is not None:cs['contacts_committed']+=1
   self.joint_control([e.actor for e in catches]);events=[e for e in events if e.kind!='acquire']
  original_scoring=self.s.ball.scoring;original_carrier=self.s.ball.carrier
  c2snap=self.c4c2_snap()if self.c4c2 else None
  goals=[e for e in events if e.kind=='goal'and legal_goal(e.data.get('y',self.s.ball.y),e.data.get('z',self.s.ball.z))]
  if goals:events=[e for e in events if not(e.kind=='boundary'and not e.actor and 0<=e.data.get('y',self.s.ball.y)<=100 and(e.data.get('x',self.s.ball.x)<0 or e.data.get('x',self.s.ball.x)>100))]
  priority={'safety':0,'boundary':4,'acquire':10,'freeze':20,'impact':20,'tackle':30,'ground':31,'release':35,'goal':40,'foul':50,'clock':60,'touch':15,'held':32,'strip':29,'block':12,'frame':13,'strike':35}
  def key(e):
   if e.kind=='foul'and(e.data.get('danger')or self.s.players[e.actor].team==self.s.owner):return 1
   return priority.get(e.kind,25)
  score_before=sum(self.s.score.values())
  for e in sorted(events,key=key):
   if e.data.get('control_witness') is not None and (self.s.ball.carrier!=e.target or self.s.ball.version!=e.data['control_witness']):
    self.emit('superseded_observation','16.1–16.2',kind=e.kind,actor=e.actor,target=e.target);continue
   if e.kind=='foul'and sum(self.s.score.values())>score_before and self.s.players[e.actor].team!=self.score_history[-1]['team']and not e.data.get('danger'):
    kind='major'if e.data.get('major')else'minor'
    if self.c4_zone and e.data.get('reason')in('zone_expiry','zone_unmarked'):kind=None #C4.0: no personal sanction for a zone expiry, on this path too
    self.discipline(e.actor,kind);self.emit('post_goal_discipline','16.2–16.3',player=e.actor,**({'kind':kind}if self.c4_zone else{}));continue
   if e.kind=='goal'and catches and original_carrier is None and original_scoring and self.s.ball.scoring and self.s.phase in(Phase.LIVE,Phase.FLIGHT):
    self.s.ball.carrier=None;self.s.ball.mode=BallMode.SHOT;self.s.ball.scoring=True
    if c2snap is not None:self.c4c2_unsnap(c2snap,[c.actor for c in catches])
   self.dispatch(e)
  self.assert_invariants()
 def elapse(self,dt,resolve=True):
  s=self.s
  if dt<0:raise RulesError('Negative time')
  active=s.phase in(Phase.LIVE,Phase.AWARD,Phase.OPENING)
  if self.c2_occ:self.occupancy(dt if active else 0) #exits are tracked in dead time too; time accrues only when live
  if s.reconstruction and s.ball.carrier and self.live():self.reconstruction_check(s.players[s.ball.carrier],'carried_out')
  #The caller slices at next_deadline(); this method will not silently cross one.
  if active:
   if not s.extension:s.game_ms=max(0,s.game_ms-dt)
   if s.owner is not None:s.possession_ms=max(0,s.possession_ms-dt)
   s.live_ms+=dt
   for d in self.debts:
    if not d['permanent'] and d['remaining']>0:
     d['remaining']=max(0,d['remaining']-dt);self.s.players[d['player']].exclusion_ms=d['remaining']
   for p in s.players.values():
    if not p.active:continue
    zn=self.zone(p.x,p.y)
    if p.frozen(s.now):continue
    for j in(()if self.c2_occ else(0,1)):
     exempt=p.role=='keeper'and j==s.own_zone(p.team)
     if zn==j and not exempt:p.zone_ms[j]+=dt;p.outside_ms[j]=0
     else:
      p.outside_ms[j]+=dt
      if p.outside_ms[j]>=3000:p.zone_ms[j]=0
    if p.role=='keeper':
     if zn==s.own_zone(p.team):
      p.keeper_outside_ms=0
      if s.ball.carrier==p.id:p.keeper_hold_ms+=dt
     else:
      p.keeper_outside_ms+=dt
      if p.keeper_outside_ms>=3000:p.keeper_hold_ms=0
  elif s.phase!=Phase.FINAL:s.dead_ms+=dt
  s.now+=dt
  if s.phase!=Phase.SUSPENDED:
   for t,q in s.quivers.items():
    if q.reload_until>=0:
     archer=next((p for p in s.players.values()if p.team==t and p.active and p.role=='archer'),None)
     inside=archer is not None and self.archer_in_lane(archer)and(archer.y<=-5 if s.ends[t]==0 else archer.y>=105)
     if not inside:q.reload_until=-1;self.emit('reload_cancelled','3.8',team=t)
    if q.reload_until>=0 and s.now>=q.reload_until:q.loaded=min(5,q.allocation-q.spent);q.reload_until=-1;self.emit('reload_complete','3.8',team=t,loaded=q.loaded)
  if resolve:self.resolve_timers()
 def next_deadline(self):
  s=self.s;values=[]
  if s.phase in(Phase.LIVE,Phase.AWARD,Phase.OPENING):
   if not s.extension:values.append(s.now+s.game_ms)
   if s.owner is not None:values.append(s.now+s.possession_ms)
   if s.opening_deadline:values.append(s.opening_deadline)
   if s.award_deadline:values.append(s.award_deadline)
   if s.contested_until:values.append(s.contested_until)
   if s.advantage:values.append(s.advantage['until'])
   for p in s.players.values():
    if p.active and not p.frozen(s.now):
     j=self.zone(p.x,p.y)
     if j is not None and not(p.role=='keeper'and j==s.own_zone(p.team)):
      values.append(s.now+max(0,5000-p.zone_ms[j]))
      if self.c2_occ and p.unmarked_ms[j]<5000:values.append(s.now+5000-p.unmarked_ms[j])
      if self.c4_occ and p.zone_fouled[j]>s.live_ms:values.append(s.now+p.zone_fouled[j]-s.live_ms) #C4.0: the end of a compliance time is resolved at its own millisecond
     if p.role=='keeper'and s.ball.carrier==p.id and j==s.own_zone(p.team):values.append(s.now+max(0,5000-p.keeper_hold_ms))
  if s.phase==Phase.REVIEW:values.append(s.review['until'])
  if s.phase==Phase.FLIGHT:values.append(s.tail_until)
  if s.phase==Phase.PENALTY:values.append(s.penalty['until'])
  if s.phase==Phase.DEAD and s.restart:
   values.append(s.restart.ready_at+5000 if s.restart.ready_at is not None else s.restart.created_at+30000)
  if s.phase!=Phase.SUSPENDED:
   for p in s.players.values():
    if p.freeze_until>s.now:values.append(p.freeze_until)
   for q in s.quivers.values():
    if q.reload_until>s.now:values.append(q.reload_until)
  return min(values)if values else s.now+1000000
 def resolve_timers(self):
  s=self.s
  if s.phase in(Phase.FINAL,Phase.SUSPENDED):return
  if self.live():
   for p in list(s.players.values()):
    if not p.active or p.frozen(s.now):continue
    j=self.zone(p.x,p.y)
    if j is not None and p.zone_ms[j]>=5000 and not(p.role=='keeper'and j==s.own_zone(p.team)):
     if self.c3b and self.c2_occ:self.zone_expiry_c3b(p,j);return
     if self.c2_occ:self.count('attacking_zone_expiries');self.emit('attacking_zone_expiry','C2-5',player=p.id,zone=j,possible_exit_interference=self.exit_interference(p,j))
     if self.c4_occ and self.zone_offset(p,'zone_expiry',p.zone_ms[j]):return #C4.0 r2 (15.5)
     self.illegal(p.id,'zone_expiry');return
    if self.c2_occ and not self.c4_occ and j is not None and p.unmarked_ms[j]>=5000 and p.team!=s.owner and s.advantage is None and s.live_ms>=p.zone_fouled[j]and not(p.role=='keeper'and j==s.own_zone(p.team)):
     #C2: defensive technical foul. Advantage where available; otherwise a free pass with the defensive-foul clock floor. The allowance is not renewed by the whistle.
     #He is liable again only after the live time physically needed to leave by the shortest route; regaining marking or leaving ends the violation.
     gx=0 if j==0 else 100;way=max(0,s.keeper_zone_radius-norm(p.x-gx,p.y-50))+.1
     p.zone_fouled[j]=s.live_ms+1+int(1000*(math.sqrt(2*way/max(1,p.a.acceleration))+p.a.decision_speed+.3));self.count('defensive_unmarked_expiries');self.emit('defensive_unmarked_expiry','C2-5',player=p.id,zone=j)
     self.foul(p.id,None,'zone_unmarked',advantage=True);return
    if p.role=='keeper'and s.ball.carrier==p.id and p.keeper_hold_ms>=5000:
     if self.c4_occ and p.team==s.owner and self.zone_offset(p,'keeper_hold',p.keeper_hold_ms):return #C4.0 r2 (15.5)
     self.illegal(p.id,'keeper_hold');return
   if self.c4_occ and self.zone_call():return #C4.0: after any attacking expiry or Keeper hold of this instant (retained order, not a new ruling)
   if s.recovery and s.phase==Phase.AWARD and self.recovery_watch():return
   if s.opening_deadline and s.now>=s.opening_deadline and s.owner is None:return self.failed_hunt('timeout')
   if s.award_deadline and s.phase==Phase.AWARD and s.now>=s.award_deadline:
    if s.recovery and self.recovery_blocked():return self.restore_recovery('unavoidable_obstruction') #C2: safe restoration when pickup was physically impossible
    return self.award(s.other(s.owner),*s.award_spot,'pickup_timeout',fresh=True)
   if s.contested_until and s.now>=s.contested_until:return self.held()
   if s.advantage:
    a=s.advantage
    if s.owner==a['team'] and s.ball.carrier and s.attack_sign(a['team'])*(s.ball.x-a['origin_x'])>=5:s.advantage=None;self.emit('advantage_realized','11.2',method='progress')
    elif s.now>=a['until']:return self.recall_advantage()
   self.clock_expiry()
  elif s.phase==Phase.REVIEW and s.now>=s.review['until']:self.finish_review(False,inconclusive=True)
  elif s.phase==Phase.FLIGHT and s.now>=s.tail_until:self.end_flight('three_seconds',s.ball.x,s.ball.y)
  elif s.phase==Phase.PENALTY:self.clock_expiry()
  elif s.phase==Phase.DEAD and s.restart and s.restart.ready_at is None and s.now>=s.restart.created_at+30000:
   r=s.restart;near=[p for p in s.players.values()if p.team==r.team and self.eligible(p)and p.role!='archer'and norm(p.x-r.x,p.y-r.y)<=.5]
   blockers=[p for p in s.players.values()if p.team!=r.team and self.eligible(p)and p.role!='archer'and norm(p.x-r.x,p.y-r.y)<r.clearance]
   if r.kind=='recovery':
    blockers=[p for p in self.recovery_blockers(r)if self.eligible(p)]
    if not blockers:return self.resume_recovery()
   offender=min(blockers,key=lambda p:p.id)if blockers else next((p for p in s.players.values()if p.team==r.team and self.eligible(p)and p.role!='archer'),None)
   if offender:self.foul(offender.id,None,'deliberate_restart_delay',major=True)
   else:self.forfeit(r.team,'no_restart_taker')
  elif s.phase==Phase.DEAD and s.restart and s.restart.ready_at is not None and s.now>=s.restart.ready_at+5000:
   r=s.restart;self.award(s.other(r.team),r.x,r.y,'restart_timeout',fresh=True)
 def advance(self,dt):
  end=self.s.now+dt
  while self.s.now<end:
   self.resolve_timers()
   span=min(end-self.s.now,max(1,self.next_deadline()-self.s.now))
   self.elapse(span)
  self.assert_invariants()
 def request_review(self,team,issue,official=False):
  s=self.s;allowed={'goal','eligibility','freeze','boundary','release_time','player_identity','clock_owner','serious_misconduct'}
  if s.phase!=Phase.DEAD or not s.restart or s.restart.ready_at is not None or issue not in allowed:return False
  if not official and s.challenges[team]<=0:return False
  s.review={'team':team,'issue':issue,'official':official,'until':s.now+90000};s.phase=Phase.REVIEW
  self.emit('review_start','17.4–17.5',team=team,issue=issue,official=official,until=s.review['until']);return True
 def finish_review(self,successful,correction=None,inconclusive=False):
  s=self.s
  if s.phase!=Phase.REVIEW or s.review is None:return False
  r=s.review;s.review=None;s.phase=Phase.DEAD
  if not r['official']and not successful:s.challenges[r['team']]-=1
  if correction and successful:
   if 'game_ms'in correction:s.game_ms=correction['game_ms']
   if 'possession_ms'in correction:s.possession_ms=correction['possession_ms']
   if 'team'in correction:self.award(correction['team'],*correction.get('spot',(s.ball.x,s.ball.y)),'review_correction')
  s.restart.created_at=s.now;s.restart.ready_at=None
  self.emit('review_complete','17.5–17.6',successful=successful,inconclusive=inconclusive,correction=correction,challenge_retained=successful or r['official']);return True
 def save_review_point(self,label):
  import copy
  self.review_snapshot=(label,copy.deepcopy(self.s),len(self.log),list(self.score_history))
  self.emit('review_checkpoint','17.4–17.6',label=label)
 def review_freeze_error(self,affected_team,missed=False):
  if self.review_snapshot is None:return False
  import copy
  label,old,seq,scores=self.review_snapshot
  #Sequence finality: a later legal restart closes ordinary review.
  if any(r['event']=='restart_release'for r in self.log[seq:]):return False
  elapsed=self.s.now;restored=copy.deepcopy(old)
  self.s.__dict__.update(restored.__dict__);self.s.now=elapsed;self.score_history=scores
  self.award(affected_team,old.ball.x,old.ball.y,'missed_freeze_review'if missed else'false_freeze_review')
  self.emit('review_correction','7.5;17.6',label=label,void_after_event=seq,missed=missed)
  return True
 def equipment_check(self,ball_diameter=.215,ball_mass=.4,arrow_mass=.04,arrow_speed=30,certified=True,magik=False):
  valid=.213<=ball_diameter<=.217 and .390<=ball_mass<=.410 and .038<=arrow_mass<=.042 and arrow_speed<=30 and .5*arrow_mass*arrow_speed**2<=20 and certified and not magik
  self.emit('equipment_check','1.1;3.1–3.6',passed=valid)
  return valid
 def terminal_record(self):
  """C4.0: everything that must not change once a match is complete, as plain data. Tests compare it before and after."""
  s=self.s;r=s.restart
  return json.loads(json.dumps({'phase':s.phase.value,'result':s.result,'score':dict(s.score),'now':s.now,'period':s.period,'g_ms':s.game_ms,'p_ms':s.possession_ms,'live_ms':s.live_ms,'dead_ms':s.dead_ms,
   'owner':s.owner,'restart':None if r is None else[r.team,r.x,r.y,r.reason,r.kind],'ball':[s.ball.mode.value,s.ball.carrier],'advantage':s.advantage is not None,'penalty':s.penalty is not None,'extension':s.extension,
   'tackle_count':s.tackle_count,'zone_violations':s.zone_violations,'warning':{t:sorted(v)for t,v in s.warning.items()},'debts':[dict(d)for d in self.debts],'queued_sanctions':[list(a)for a in self.pending_discipline],
   'players':{p.id:[p.active,p.role,p.disqualified,p.exclusion_ms,p.minor_count,p.major_count]for p in s.players.values()},'records':len(self.log),'last_id':self.event_seq,'final_id':self.final_seq,
   'periods':self.period_history,'scores':self.score_history,'stoppages':s.stoppages,
   'positions':{p.id:[p.x,p.y,p.z,p.vx,p.vy,p.posture]for p in s.players.values()},'stats':dict(getattr(self,'contact_stats',None)or{}),'engagements':sorted(map(str,s.engagements))},default=str))
 def assert_invariants(self):
  s=self.s;b=s.ball
  assert s.game_ms>=0 and s.possession_ms>=0,('negative_clock',s.now)
  assert b.carrier is None or b.mode==BallMode.CONTROLLED,('carrier_mode',b.mode)
  assert not(b.carrier and b.contested),'double_control'
  if b.carrier:
   p=s.players[b.carrier];assert p.team==s.owner or s.phase==Phase.PENALTY,('control_owner',p.id,s.owner)
   assert p.eligible(s.now),('ineligible_carrier',p.id,s.now,p.freeze_until)
  if s.phase==Phase.DEAD:assert s.restart is not None and b.carrier is None,'undefined_stoppage'
  if s.phase==Phase.AWARD:assert s.owner and s.award_spot and s.award_deadline,'undefined_award'
  if s.phase==Phase.FLIGHT:assert s.tail_until is not None and b.carrier is None,'invalid_tail'
  if s.phase==Phase.FINAL:assert s.result is not None,'missing_result'
  for q in s.quivers.values():assert 0<=q.loaded<=5 and 0<=q.spent<=q.allocation,'ammunition'
  for t in('A','B'):
   assert sum(p.active for p in s.players.values()if p.team==t)<=12,'extra_player'
  return True

#C4.0 terminal processing. Every Engine method that can change the match is guarded:
#  - called on a completed match, it does nothing, returns None and is counted in final_refused;
#  - if the match is completed inside it, the completion unwinds to the outermost guarded call, which returns None.
#The methods below only read, or only compute, and are left as they are. A self-check asserts that every method of the class is
#either guarded or on this list, so a method added later cannot escape by omission.
FINAL_READ_ONLY=('zone','territory','territory_points','emit','eligible','live','c2_snapshot','c1_reason','contact_legal','recovery_committed','inbound_side',
 'recovery_blocked','recovery_blockers','exit_run','exit_points','exit_free','exit_routes','exit_lanes','exit_before','exit_interference','archer_in_lane','next_deadline',
 'assert_invariants','validate_lineup','zone_due','zone_compliance_time','zone_witness','zone_overdue','terminal_record')
def _final_guard(name,f):
 def guarded(self,*a,**k):
  if self.s.phase==Phase.FINAL:
   self.final_refused[name]=self.final_refused.get(name,0)+1;return None
  self.depth+=1
  try:return f(self,*a,**k)
  except MatchFinal:
   if self.depth>1:raise
   return None
  finally:self.depth-=1
 guarded.__name__=name;guarded.__doc__=f.__doc__;guarded.guarded=True;return guarded
FINAL_GUARDED=tuple(n for n,f in vars(Engine).items()if callable(f)and not n.startswith('__')and n not in FINAL_READ_ONLY)
for _n in FINAL_GUARDED:setattr(Engine,_n,_final_guard(_n,vars(Engine)[_n]))
