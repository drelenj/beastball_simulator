"""Beastball anatomy v0.3: experimental hand/ball impulse and retention layer.

SI units. Extends v0.2; does NOT modify Pocket state or automatically score,
strip, injure, or tackle players. Contact impulses are simplified effective-mass
collisions, not a full articulated rigid-body simulation.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from math import sqrt
import beastball_anatomy as base
import beastball_anatomy_v02 as v2

Vec=tuple[float,float,float]
def add(a,b):return v2.add(a,b)
def sub(a,b):return v2.sub(a,b)
def mul(a,s):return v2.mul(a,s)
def dot(a,b):return v2.dot(a,b)
def norm(a):return v2.norm(a)
def unit(a):return mul(a,1/norm(a)) if norm(a)>1e-10 else (0.,0.,0.)
def clamp(a,lo,hi):return max(lo,min(hi,a))

@dataclass
class BallParameters:
 mass:float=.48
 radius:float=.115
 retention_base:float=4.5 # N*s effective retention impulse; experimental
 grip_factor:float=1.0
 security_factor:float=1.0
 pose_factor:dict=field(default_factory=lambda:{'exposed':1.0,'tucked':1.55,'extended':.80,'loaded':.70,'braced':2.17})   # loaded and braced added: loaded cocked for the throw; braced = tucked + covered by the off arm (x1.4)

@dataclass
class StrikeParameters:
 effective_mass:float=2.0 # hand/forearm effective mass, not full player mass
 restitution:float=.15
 technique:float=.75
 strength:float=.75
 strike_speed_factor:float=1.0
 accuracy:float=1.0

@dataclass
class BallInteraction:
 time:float
 attacker:str
 carrier:str
 hand:str
 outcome:str
 contact_point:Vec|None
 relative_normal_speed:float
 impulse:float
 retention:float
 ball_velocity:Vec
 note:str=''

@dataclass
class FreeBall:
 center:Vec
 velocity:Vec
 carrier_last:str

class ForceWorld(v2.AnatomyWorld):
 def __init__(self,*,ball_parameters=None,**kwargs):
  super().__init__(**kwargs)
  self.ball_parameters=ball_parameters or BallParameters()
  self.free_balls:list[FreeBall]=[]
  self.interactions:list[BallInteraction]=[]
  self._last_ball:dict[str,Vec]={}
  self._strike_latch:set[tuple[str,str,str]]=set()
 def add_player(self,player,**kwargs):
  b=super().add_player(player,**kwargs)
  if b.ball_center is not None:self._last_ball[player.id]=b.ball_center
  return b
 def _retention(self,body,*,security=1.,grip=1.,brace=1.):
  p=self.ball_parameters
  return p.retention_base*p.grip_factor*p.security_factor*p.pose_factor[body.ball_pose]*security*grip*brace
 def resolve_ball_strike(self,attacker,hand,carrier,*,hand_start,hand_end,dt,parameters=None,
                         carrier_velocity=(0.,0.,0.),security=1.,grip=1.,brace=1.,
                         ball_start=None,ball_end=None):
  """Resolve one continuous swept hand-to-moving-ball strike.

  The normal impulse comes from closing velocity, effective mass, restitution,
  technique and strength. A strike can miss, connect/retain, or dislodge.
  The hand must be in a strike state; repeated calls during same strike are latched.
  This function does not apply impulse to Pocket's root-body physics.
  """
  if dt<=0:raise ValueError('positive dt required')
  if attacker==carrier:raise ValueError('self strike')
  if hand not in ('left_hand','right_hand'):raise ValueError('invalid hand')
  ab=self.body(attacker);cb=self.body(carrier)
  if ab.actions.get(hand)!='strike':raise ValueError('hand not striking')
  if cb.ball_center is None or cb.ball_hand is None:raise ValueError('carrier has no held ball')
  p=parameters or StrikeParameters()
  if p.effective_mass<=0 or self.ball_parameters.mass<=0:raise ValueError('invalid masses')
  key=(attacker,hand,carrier)
  if key in self._strike_latch:
   return BallInteraction(self.time,attacker,carrier,hand,'already_resolved',None,0,0,self._retention(cb,security=security,grip=grip,brace=brace),(0.,0.,0.))
  bs=ball_start if ball_start is not None else cb.ball_center
  be=ball_end if ball_end is not None else cb.ball_center
  hs=hand_start;he=hand_end
  # Closest time of approach of two linearly moving spheres in this frame.
  r0=sub(hs,bs);dr=sub(sub(he,hs),sub(be,bs))
  t=clamp(-dot(r0,dr)/max(dot(dr,dr),1e-12),0.,1.)
  gap=norm(add(r0,mul(dr,t)))
  radius=ab.part(hand).radius+self.ball_parameters.radius
  retention=self._retention(cb,security=security,grip=grip,brace=brace)
  if gap>radius:
   return BallInteraction(self.time,attacker,carrier,hand,'miss',None,0.,0.,retention,(0.,0.,0.),'swept trajectories did not intersect')
  hand_vel=mul(sub(he,hs),1/dt)
  ball_vel=mul(sub(be,bs),1/dt)
  # The normal is oriented from the hand toward the ball at contact.
  contact_hand=add(hs,mul(sub(he,hs),t));contact_ball=add(bs,mul(sub(be,bs),t))
  normal=unit(sub(bs,hs))
  if norm(normal)<1e-8:normal=unit(sub(contact_ball,contact_hand))
  if norm(normal)<1e-8:
   normal=unit(sub(be,hs))
  if norm(normal)<1e-8:normal=unit(sub(he,hs))
  closing=max(0.,dot(sub(hand_vel,ball_vel),normal))*p.strike_speed_factor
  effective=1/(1/p.effective_mass+1/self.ball_parameters.mass)
  impulse=(1+clamp(p.restitution,0.,1.))*effective*closing*clamp(p.technique,0.,1.)*clamp(p.strength,0.,1.)*clamp(p.accuracy,0.,1.)
  if closing<=1e-8:outcome='contact_retained';note='no positive closing velocity'
  elif impulse>retention:outcome='dislodged';note='impact exceeds effective retention'
  else:outcome='contact_retained';note='retention exceeds impact'
  bv=add(ball_vel,mul(normal,impulse/self.ball_parameters.mass))
  result=BallInteraction(self.time,attacker,carrier,hand,outcome,contact_ball,closing,impulse,retention,bv,note)
  self._strike_latch.add(key);self.interactions.append(result)
  if outcome=='dislodged':
   self.free_balls.append(FreeBall(contact_ball,bv,carrier))
   cb.release_hand(cb.ball_hand)
   self._last_ball.pop(carrier,None)
  return result
 def reset_strike(self,attacker,hand):
  self._strike_latch={k for k in self._strike_latch if not(k[0]==attacker and k[1]==hand)}
 def step(self,dt,*,sync_players=None, strike_parameters=None,security=None):
  """Advance v0.2 motions, resolve swept ball contacts before strike state resets.

  security is mapping carrier_id -> security multiplier. Existing Pocket
  possession is NOT mutated; caller must explicitly bridge dislodgement events.
  """
  if not 0<dt<=.25:raise ValueError('dt must be in (0,.25]')
  before={pid:{h:r.body.part(h).center for h in ('left_hand','right_hand')} for pid,r in self.rigs.items()}
  balls={pid:r.body.ball_center for pid,r in self.rigs.items() if r.body.ball_center is not None}
  active={(pid,h) for pid,r in self.rigs.items() for h,m in r.motions.items() if m.intent=='strike'}
  events=super().step(dt,sync_players=sync_players)
  # Reconstruct the prior ball position after sync, where possible.
  for pid,h in active:
   if pid not in self.rigs:continue
   body=self.body(pid)
   for carrier in list(balls):
    if carrier==pid or self.body(carrier).ball_center is None:continue
    # ForceWorld owns a strike's temporary action even if v0.2 completed it this tick.
    original=body.actions.get(h)
    if original!='strike':body.set_action(h,'strike')
    b0=balls[carrier];b1=self.body(carrier).ball_center
    res=self.resolve_ball_strike(pid,h,carrier,hand_start=before[pid][h],hand_end=body.part(h).center,dt=dt,
      parameters=(strike_parameters or {}).get(pid,StrikeParameters()),security=(security or {}).get(carrier,1.),ball_start=b0,ball_end=b1)
    if res.outcome in ('contact_retained','dislodged'):events.append(res)
    if original!='strike' and body.actions.get(h)=='strike':body.release_hand(h)
  for pid,h in active:
   if h not in self.rigs[pid].motions:self.reset_strike(pid,h)
  return events
