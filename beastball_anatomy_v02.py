"""Beastball anatomy v0.2 — persistent articulated motion and geometric contact.

Experimental 2.5D kinematic adapter; DOES NOT apply impulses, ground players,
force strips, or replace Pocket's authoritative collision/possession rules.
Units: meters, seconds. Requires beastball_anatomy.py v0.1 alongside it.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from math import sqrt, acos, cos, sin, pi
from typing import Optional
import beastball_anatomy as a

V3=tuple[float,float,float]
def sub(x,y):return tuple(i-j for i,j in zip(x,y))
def add(x,y):return tuple(i+j for i,j in zip(x,y))
def mul(x,k):return tuple(i*k for i in x)
def dot(x,y):return sum(i*j for i,j in zip(x,y))
def norm(x):return sqrt(dot(x,x))
def clamp(x,lo,hi):return max(lo,min(hi,x))
def limit(v,length):
 n=norm(v)
 return mul(v,length/n) if n>length and n>1e-12 else v

def point_segment_distance(p,start,end):
 d=sub(end,start); t=clamp(dot(sub(p,start),d)/max(dot(d,d),1e-12),0.,1.)
 return a.dist(p,add(start,mul(d,t)))

def segment_segment_distance(p1,q1,p2,q2):
 # Closest points on finite 3D segments (robust for degenerate segments).
 u=sub(q1,p1);v=sub(q2,p2);w=sub(p1,p2)
 aa=dot(u,u);bb=dot(u,v);cc=dot(v,v);dd=dot(u,w);ee=dot(v,w)
 D=aa*cc-bb*bb
 if aa<1e-12:return point_segment_distance(p1,p2,q2)
 if cc<1e-12:return point_segment_distance(p2,p1,q1)
 sN=0.;sD=D;tN=0.;tD=D
 if D<1e-12:sN=0.;sD=1.;tN=ee;tD=cc
 else:
  sN=bb*ee-cc*dd;tN=aa*ee-bb*dd
  if sN<0:sN=0.;tN=ee;tD=cc
  elif sN>sD:sN=sD;tN=ee+bb;tD=cc
 if tN<0:
  tN=0.
  if -dd<0:sN=0.
  elif -dd>aa:sN=sD
  else:sN=-dd;sD=aa
 elif tN>tD:
  tN=tD
  if -dd+bb<0:sN=0.
  elif -dd+bb>aa:sN=sD
  else:sN=-dd+bb;sD=aa
 sc=0. if abs(sN)<1e-12 else sN/sD
 tc=0. if abs(tN)<1e-12 else tN/tD
 return norm(sub(add(w,mul(u,sc)),mul(v,tc)))

@dataclass
class Motion:
 hand:str
 target:V3
 speed:float
 intent:str
 elapsed:float=0.
 timeout:float=1.

@dataclass
class Contact:
 attacker:str
 hand:str
 defender_part:str
 target:str
 target_part:str
 time:float
 distance:float
 kind:str='touch'

@dataclass
class Grip:
 attacker:str
 hand:str
 target:str
 target_part:str
 max_gap:float
 age:float=0.

@dataclass
class Rig:
 body:a.Body
 motions:dict[str,Motion]=field(default_factory=dict)
 grips:dict[str,Grip]=field(default_factory=dict)
 last_hand_positions:dict[str,V3]=field(default_factory=dict)

def _hand_shoulder(body,hand):return body.part(hand.replace('hand','arm')).anchor

def _rebuild_arm(body,hand):
 arm=body.part(hand.replace('hand','arm'));h=body.part(hand)
 arm.end=h.center;arm.center=a.lerp(arm.anchor,h.center,.54);arm.length=a.dist(arm.anchor,h.center)
 h.anchor=arm.center

def _orient_xy(v,old,new):
 # rotate local coordinates with player facing, not world origin
 oldf=a.unit2(old);newf=a.unit2(new)
 forward=v[0]*oldf[0]+v[1]*oldf[1]
 left=v[0]*(-oldf[1])+v[1]*oldf[0]
 return (forward*newf[0]-left*newf[1],forward*newf[1]+left*newf[0],v[2])

class AnatomyWorld:
 def __init__(self, max_hand_speed=10., contact_margin=0.0):
  self.rigs:dict[str,Rig]={};self.time=0.;self.events:list[Contact|dict]=[]
  self.max_hand_speed=max_hand_speed;self.contact_margin=contact_margin
 def add_player(self,player,**kwargs):
  b=a.build(player,**kwargs);r=Rig(b)
  r.last_hand_positions={hand:b.part(hand).center for hand in ('left_hand','right_hand')}
  self.rigs[player.id]=r;return b
 def body(self,pid):return self.rigs[pid].body
 def sync_player(self,player):
  """Read authoritative Pocket root/facing. Preserve local limb pose and occupancy."""
  r=self.rigs[player.id];b=r.body
  newroot=(float(player.x),float(player.y),float(player.z))
  newface=a.unit2(player.facing);oldroot=b.root;oldface=b.facing
  def trans(p):return add(newroot,_orient_xy(sub(p,oldroot),oldface,newface))
  for seg in b.parts.values():
   seg.center=trans(seg.center)
   if seg.anchor is not None:seg.anchor=trans(seg.anchor)
   if seg.end is not None:seg.end=trans(seg.end)
  for m in r.motions.values():
   # motion targets are absolute world coordinates and DO NOT follow the player
   pass
  b.root=newroot;b.facing=newface
  for hand in ('left_hand','right_hand'):_rebuild_arm(b,hand)
  if b.ball_hand:b._position_ball()
 def sync_match(self,match):
  for pid in list(self.rigs):
   if pid in match.s.players:self.sync_player(match.s.players[pid])
 def start_hand(self,pid,hand,target,*,intent='reach',speed=6.,timeout=1.):
  r=self.rigs[pid];b=r.body
  if hand not in ('left_hand','right_hand'):raise ValueError('invalid hand')
  if not b.available(hand):raise ValueError('hand occupied')
  if intent not in ('reach','strike','grip','block'):raise ValueError('invalid intent')
  if speed<=0 or timeout<=0:raise ValueError('invalid motion')
  r.motions[hand]=Motion(hand,tuple(map(float,target)),min(speed,self.max_hand_speed),intent,timeout=timeout)
  if intent in ('strike','block'):b.set_action(hand,'strike' if intent=='strike' else 'block')
 def stop_hand(self,pid,hand):
  r=self.rigs[pid];r.motions.pop(hand,None)
  if hand not in r.grips and r.body.actions.get(hand) in ('strike','block','recover'):r.body.release_hand(hand)
 def release_grip(self,pid,hand):
  r=self.rigs[pid];r.grips.pop(hand,None);r.motions.pop(hand,None)
  if r.body.actions.get(hand)=='grip':r.body.release_hand(hand)
 def step(self,dt,*,sync_players=None):
  """Advance kinematics, then detect swept hand-to-body contacts.
  Call AFTER Pocket movement tick. Does not modify Pocket physics.
  """
  if not 0<dt<=.25:raise ValueError('dt must be in (0,0.25] seconds')
  if sync_players:
   for p in sync_players:
    if p.id in self.rigs:self.sync_player(p)
  self.time+=dt;out=[]
  for pid,r in self.rigs.items():
   b=r.body
   for hand,m in list(r.motions.items()):
    h=b.part(hand);old=h.center;shoulder=_hand_shoulder(b,hand)
    desired=add(shoulder,limit(sub(m.target,shoulder),.47*b.height))
    new=add(old,limit(sub(desired,old),m.speed*dt))
    new=add(shoulder,limit(sub(new,shoulder),.47*b.height))
    h.center=new;_rebuild_arm(b,hand)
    if b.ball_hand==hand:b._position_ball()
    m.elapsed+=dt
    # swept capsule against spheres for other bodies, no event for own body
    for otherid,other in self.rigs.items():
     if otherid==pid:continue
     for partname,part in other.body.parts.items():
      d=point_segment_distance(part.center,old,new)
      if d<=h.radius+part.radius+self.contact_margin:
       ev=Contact(pid,hand,hand,otherid,partname,self.time,d,m.intent)
       out.append(ev)
    if a.dist(new,desired)<1e-6 or m.elapsed>=m.timeout:
     r.motions.pop(hand,None)
     if b.actions.get(hand) in ('strike','block'):b.release_hand(hand)
   for hand,g in list(r.grips.items()):
    target=self.rigs.get(g.target)
    if target is None or a.dist(b.part(hand).center,target.body.part(g.target_part).center)>g.max_gap:
     self.release_grip(pid,hand)
     out.append({'kind':'grip_break','attacker':pid,'hand':hand,'target':g.target,'time':self.time})
    else:g.age+=dt
   for hand in ('left_hand','right_hand'):r.last_hand_positions[hand]=b.part(hand).center
   b.validate()
  self.events.extend(out);return out
 def attach_grip(self,pid,hand,target,target_part,*,max_gap=None):
  """Anatomical hand attachment only; Pocket's C3 hold remains authoritative."""
  r=self.rigs[pid];b=r.body
  if not b.available(hand):return False
  if target not in self.rigs or target==pid:return False
  t=self.body(target).part(target_part)
  gap=a.dist(b.part(hand).center,t.center)
  allowed=b.part(hand).radius+t.radius+self.contact_margin
  if gap>allowed:return False
  r.motions.pop(hand,None);b.set_action(hand,'grip')
  r.grips[hand]=Grip(pid,hand,target,target_part,max_gap if max_gap is not None else allowed*1.25)
  return True
 def ball_contacts(self,events,carrier_id):
  """Report strike contact with held ball; never forces a fumble."""
  if carrier_id not in self.rigs:return []
  carrier=self.body(carrier_id)
  if carrier.ball_center is None:return []
  # Note: call after step; for exact moving-ball sweeps use the trajectory from event frame.
  return [e for e in events if isinstance(e,Contact) and e.kind=='strike' and e.target==carrier_id
          and a.dist(self.body(e.attacker).part(e.hand).center,carrier.ball_center)
          <=self.body(e.attacker).part(e.hand).radius+.065*carrier.height]
