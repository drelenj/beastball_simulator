"""Beastball anatomy v0.1: deterministic 2.5D articulated geometry adapter.
No modification of Pocket. SI units. Not a ragdoll or collision impulse solver.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from math import hypot, sqrt, cos, sin, radians
from typing import Optional

PARTS=('head','torso','left_arm','left_hand','right_arm','right_hand','left_leg','left_foot','right_leg','right_foot')
ARM={'left_hand':'left_arm','right_hand':'right_arm'}
ACTIONS={'free','carry','grip','strike','throw','block','brace','recover'}
POSES=('exposed','tucked','extended','loaded','braced')   # braced: tucked and covered by the off arm (off hand 'brace', occupied); loaded: cocked in the throwing position

def dist(a,b): return sqrt(sum((x-y)**2 for x,y in zip(a,b)))
def vecadd(a,b): return tuple(x+y for x,y in zip(a,b))
def lerp(a,b,t):return tuple(x+(y-x)*t for x,y in zip(a,b))
def unit2(v):
 n=hypot(*v)
 return (v[0]/n,v[1]/n) if n>1e-9 else (1.,0.)

@dataclass
class Segment:
 name:str
 center:tuple[float,float,float]
 radius:float
 length:float=0.
 state:str='free'
 anchor:tuple[float,float,float]|None=None
 end:tuple[float,float,float]|None=None

@dataclass
class Body:
 player_id:str
 height:float
 mass:float
 root:tuple[float,float,float]
 facing:tuple[float,float]
 parts:dict[str,Segment]=field(default_factory=dict)
 ball_hand:Optional[str]=None
 ball_pose:str='exposed'
 ball_center:Optional[tuple[float,float,float]]=None
 actions:dict[str,str]=field(default_factory=dict)
 def part(self,name):return self.parts[name]
 def set_action(self,hand,action):
  if hand not in ('left_hand','right_hand'):raise ValueError('hand required')
  if action not in ACTIONS:raise ValueError('unknown action')
  if self.ball_hand==hand and action not in ('carry','throw','free'):
   raise ValueError('ball hand occupied; transfer or release ball first')
  if self.actions.get(hand)=='grip' and action in ('strike','throw'):
   raise ValueError('gripping hand must disengage before strike/throw')
  self.actions[hand]=action;self.parts[hand].state=action
 def _off(self,hand):return 'left_hand' if hand=='right_hand' else 'right_hand'
 def release_hand(self,hand):
  if self.ball_hand==hand:
   if self.ball_pose=='braced' and self.actions.get(self._off(hand))=='brace':self.actions[self._off(hand)]='free';self.parts[self._off(hand)].state='free'
   self.ball_hand=None;self.ball_center=None
  self.actions[hand]='free';self.parts[hand].state='free'
 def carry(self,hand='right_hand',pose='exposed'):
  if hand not in ('left_hand','right_hand'):raise ValueError('invalid hand')
  if pose not in POSES:raise ValueError('invalid pose')
  if self.actions.get(hand) not in (None,'free','carry'):raise ValueError('hand occupied')
  off=self._off(hand)
  if pose=='braced' and self.actions.get(off) not in (None,'free','brace'):raise ValueError('off hand occupied: cannot brace')
  if self.ball_hand and self.ball_hand!=hand:self.release_hand(self.ball_hand)
  if self.ball_pose=='braced' and pose!='braced' and self.actions.get(off)=='brace':self.actions[off]='free';self.parts[off].state='free'
  self.ball_hand=hand;self.ball_pose=pose;self.set_action(hand,'carry')
  if pose=='braced':self.set_action(off,'brace')
  self._position_ball()
 def _position_ball(self):
  if not self.ball_hand:return
  hand=self.parts[self.ball_hand]
  # ball center is held near the palm, with pose-specific distance from torso.
  self.ball_center=hand.center
 def available(self,hand):return self.actions.get(hand,'free')=='free'
 def hand_reaches(self,hand,point,margin=0.):
  return dist(self.parts[hand].center,point)<=self.parts[hand].radius+margin
 def validate(self):
  assert set(self.parts)==set(PARTS)
  h=self.height
  for side in ('left','right'):
   shoulder=self.parts[f'{side}_arm'].anchor
   hand=self.parts[f'{side}_hand'].center
   assert dist(shoulder,hand)<=.47*h+1e-6,('arm reach',side)
   hip=self.parts[f'{side}_leg'].anchor
   foot=self.parts[f'{side}_foot'].center
   assert dist(hip,foot)<=.57*h+1e-6,('leg reach',side)
  if self.ball_hand:
   assert self.actions[self.ball_hand]=='carry'
   assert self.ball_center is not None
  return True


def build(player,ball_hand=None,ball_pose='exposed',head_yaw=0.,stride=0.,reach_extension=0.):
 """Map existing Pocket player to ten oriented anatomical parts.
 head_yaw is degrees relative to facing; stride [-1,1], extension [0,1].
 Torso/root XY is player x,y; z uses Pocket's player.z.
 """
 h=float(player.a.height);m=float(player.a.mass)
 if not 1.4<=h<=3.6576 or m<=0:raise ValueError('invalid player dimensions')
 f=unit2(player.facing);l=(-f[1],f[0]);x,y,z=float(player.x),float(player.y),float(player.z)
 def xyz(forward=0.,left=0.,up=0.):return (x+f[0]*forward+l[0]*left,y+f[1]*forward+l[1]*left,z+up)
 def from_point(p,forward=0.,left=0.,up=0.):return (p[0]+f[0]*forward+l[0]*left,p[1]+f[1]*forward+l[1]*left,p[2]+up)
 torso=xyz(0,0,.55*h);neck=xyz(0,0,.88*h)
 parts={'torso':Segment('torso',torso,.155*h,.52*h,anchor=xyz(0,0,.34*h),end=neck),
        'head':Segment('head',xyz(.018*h*cos(radians(head_yaw)),.018*h*sin(radians(head_yaw)),.935*h),.065*h,.13*h,anchor=neck)}
 stride=max(-1.,min(1.,stride));extension=max(0.,min(1.,reach_extension))
 for side,sgn in (('left',1),('right',-1)):
  shoulder=xyz(0,sgn*.175*h,.82*h)
  # Hands are in a guarded neutral pose; extension is a bounded reaching pose.
  hand=xyz((.13+.24*extension)*h,sgn*(.235+.055*extension)*h,(.63+.065*extension)*h)
  elbow=lerp(shoulder,hand,.54)
  parts[side+'_arm']=Segment(side+'_arm',elbow,.052*h,dist(shoulder,hand),anchor=shoulder,end=hand)
  parts[side+'_hand']=Segment(side+'_hand',hand,.039*h,.08*h,anchor=elbow)
  hip=xyz(0,sgn*.095*h,.48*h)
  foot=xyz((stride*.15*h*sgn),sgn*.10*h,.045*h)
  knee=lerp(hip,foot,.49)
  parts[side+'_leg']=Segment(side+'_leg',knee,.075*h,dist(hip,foot),anchor=hip,end=foot)
  parts[side+'_foot']=Segment(side+'_foot',foot,.052*h,.12*h,anchor=knee)
 b=Body(player.id,h,m,(x,y,z),f,parts,actions={'left_hand':'free','right_hand':'free'})
 if ball_hand:
  b.carry(ball_hand,ball_pose)
  hand=b.parts[ball_hand]
  side=1 if ball_hand=='left_hand' else -1
  if ball_pose in ('tucked','braced'):
   hand.center=xyz(.075*h,side*.115*h,.66*h)
   if ball_pose=='braced':   # the off hand and forearm cover the ball
    off=ball_hand.replace('right','left') if ball_hand=='right_hand' else ball_hand.replace('left','right')
    oh=b.parts[off];oh.center=xyz(.12*h,side*.03*h,.68*h);oa=b.parts[off.replace('hand','arm')];oa.end=oh.center;oa.length=dist(oa.anchor,oh.center)
  elif ball_pose=='extended':
   hand.center=xyz(.41*h,side*.22*h,.70*h)
  elif ball_pose=='loaded':
   hand.center=xyz(.02*h,side*.19*h,.87*h)   # cocked beside the head
  else:
   hand.center=xyz(.20*h,side*.235*h,.66*h)
  b.parts[ball_hand.replace('hand','arm')].end=hand.center
  b.parts[ball_hand.replace('hand','arm')].length=dist(b.parts[ball_hand.replace('hand','arm')].anchor,hand.center)
  b._position_ball()
 b.validate()
 return b

def reach_window(attacker:Body,target:Body,hand:str,point:tuple,extra_reach=0.):
 """Diagnostic: hand-to-target distance and ball access; no automatic fumble."""
 if hand not in ('left_hand','right_hand'):raise ValueError('invalid hand')
 if not attacker.available(hand):return {'possible':False,'reason':'hand_occupied','distance':None}
 shoulder=attacker.parts[hand.replace('hand','arm')].anchor
 d=dist(shoulder,point)
 reach=min(.47*attacker.height, .34*attacker.height+max(0.,extra_reach))
 possible=d<=reach+attacker.parts[hand].radius
 return {'possible':possible,'reason':'reachable' if possible else 'out_of_reach','distance':round(d,4),'reach':round(reach,4)}

def punch_trajectory(attacker:Body,hand:str,target_point:tuple,duration=.22,steps=12):
 """Straight-line experimental hand path, bounded by shoulder-to-hand reach.
 Returns positions and first contact sample against a spherical ball. No impact model.
 """
 if not attacker.available(hand):raise ValueError('hand occupied')
 if duration<=0 or steps<2:raise ValueError('invalid timing')
 shoulder=attacker.parts[hand.replace('hand','arm')].anchor
 start=attacker.parts[hand].center
 direction=tuple(target_point[i]-shoulder[i] for i in range(3));n=sqrt(sum(q*q for q in direction)) or 1.
 maxreach=.47*attacker.height
 endpoint=tuple(shoulder[i]+direction[i]*min(n,maxreach)/n for i in range(3))
 positions=[lerp(start,endpoint,i/steps) for i in range(steps+1)]
 return {'duration':duration,'positions':positions,'end':endpoint,'maxreach':maxreach}

def pocket_adapter(match,player_id,**kwargs):
 return build(match.s.players[player_id],**kwargs)
