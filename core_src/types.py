from dataclasses import dataclass,field,asdict
from enum import Enum
from .geometry import clamp

class Phase(str,Enum):
 OPENING='opening';LIVE='live';DEAD='dead';AWARD='award';FLIGHT='finishing_flight';PENALTY='penalty';BREAK='break';REVIEW='review';SHOOTOUT='shootout';SUSPENDED='suspended';FINAL='final'
class BallMode(str,Enum):
 CONTROLLED='carried';LOOSE='loose';PASS='passed';KICK='kicked';SHOT='shot';DEAD='dead';OUT='out';CONTESTED='contested'

@dataclass
class Attributes:
 height:float=2.45
 mass:float=220
 reach:float=1.18
 strength:float=.65
 acceleration:float=9
 maximum_speed:float=25
 braking:float=12
 turning:float=12
 agility:float=.65
 endurance:float=.7
 balance:float=.65
 contact_resistance:float=.65
 tackling:float=.65
 blocking:float=.65
 ball_handling:float=.65
 passing:float=.65
 kicking:float=.6
 catching:float=.65
 awareness:float=.65
 decision_speed:float=.3
 archery_accuracy:float=.7
 archery_release_speed:float=28
 keeper_skill:float=.7
 jump_height:float=1.3
 def validate(self):
  assert 1.4<=self.height<=3.6576
  assert 0<self.maximum_speed<=44.704
  assert self.mass>0 and self.acceleration>0 and self.braking>0
  for k in ['strength','agility','endurance','balance','contact_resistance','tackling','blocking','ball_handling','passing','kicking','catching','awareness','archery_accuracy','keeper_skill']:
   assert 0<=getattr(self,k)<=1,(k,getattr(self,k))

@dataclass
class Player:
 id:str
 team:str
 role:str='field'
 active:bool=True
 a:Attributes=field(default_factory=Attributes)
 x:float=50
 y:float=50
 z:float=0
 vx:float=0
 vy:float=0
 vz:float=0
 facing:tuple=(1.,0.)
 posture:str='upright'
 available:bool=True
 injured:bool=False
 disqualified:bool=False
 freeze_until:int=-1
 immune_until:int=-1
 exclusion_ms:int=0
 minor_count:int=0
 major_count:int=0
 zone_ms:list=field(default_factory=lambda:[0,0])
 outside_ms:list=field(default_factory=lambda:[3000,3000])
 keeper_hold_ms:int=0
 keeper_outside_ms:int=3000
 unmarked_ms:list=field(default_factory=lambda:[0,0])   #C2: defender's unmarked allowance used, per zone
 zone_loc:list=field(default_factory=lambda:[None,None]) #C2: last observed 'in' / 'out' (in field, outside zone) / 'off' (outside field), per zone
 zone_fouled:list=field(default_factory=lambda:[0,0])   #C2: live time after which an unmarked expiry may be called again; 0 = none pending
 tackled_until:int=-1                                    #C2: recognised tackle-ground recovery; occupancy pauses until then
 fatigue:float=1
 next_decision:int=0
 next_action:int=0
 target:tuple=(50.,50.)
 slot:int=0
 @property
 def radius(self):return clamp(.30+self.a.mass*.00065,.38,.82)
 @property
 def speed(self):return (self.vx*self.vx+self.vy*self.vy)**.5
 @property
 def hand_height(self):return self.z+.62*self.a.height
 def eligible(self,t):return self.active and self.available and not self.injured and not self.disqualified and self.exclusion_ms<=0 and t>=self.freeze_until
 def frozen(self,t):return t<self.freeze_until

@dataclass
class Ball:
 version:int=0
 mode:BallMode=BallMode.DEAD
 x:float=50
 y:float=50
 z:float=.1075
 vx:float=0
 vy:float=0
 vz:float=0
 carrier:str|None=None
 control_time:int=-1
 last_touch:str|None=None
 last_releaser:str|None=None
 scoring:bool=False
 release_time:int=-1
 intended:str|None=None
 contested:tuple=()
 radius:float=.1075

@dataclass
class Arrow:
 id:int
 team:str
 shooter:str
 target:str|None
 x:float
 y:float
 z:float
 vx:float
 vy:float
 vz:float
 origin:tuple
 release_time:int
 live:bool=True
 first_impact:bool=True
 spent:bool=True

@dataclass
class Quiver:
 allocation:int=20
 spent:int=0
 loaded:int=5
 reload_until:int=-1
 last_release:int=-999999

@dataclass
class Restart:
 team:str
 x:float
 y:float
 reason:str
 ready_at:int|None=None
 taker:str|None=None
 created_at:int=0
 kind:str='free_pass'      #C2: 'inbound' (goal-line inbound) or 'recovery' (restored first-tackle recovery)
 clearance:float=5.        #m, opponents' distance from the restart spot
 remaining:int=3000        #ms of recovery granted when a restored recovery resumes
 taker_spot:tuple|None=None
 note:str=''

@dataclass
class Engagement:
 actor:str
 target:str
 kind:str
 started:int
 progress:float=0

@dataclass
class Event:
 kind:str
 actor:str|None=None
 target:str|None=None
 data:dict=field(default_factory=dict)
 at:int|None=None

@dataclass
class MatchState:
 now:int=0
 period:int=1
 game_ms:int=600000
 possession_ms:int=45000
 owner:str|None=None
 phase:Phase=Phase.DEAD
 score:dict=field(default_factory=lambda:{'A':0,'B':0})
 ball:Ball=field(default_factory=Ball)
 players:dict=field(default_factory=dict)
 quivers:dict=field(default_factory=lambda:{'A':Quiver(),'B':Quiver()})
 arrows:list=field(default_factory=list)
 restart:Restart|None=None
 engagements:dict=field(default_factory=dict)
 alternate:str='A'
 opening_team:str|None=None
 opening_failures:int=0
 opening_deadline:int|None=None
 opening_touched:bool=False
 opening_contestants:tuple=('A0','B0')
 hunt_choice_team:str='B'
 ends:dict=field(default_factory=lambda:{'A':0,'B':100})
 award_spot:tuple|None=None
 award_available:int|None=None
 award_deadline:int|None=None
 tail_until:int|None=None
 tail_owner:str|None=None
 contested_until:int|None=None
 advantage:dict|None=None
 penalty:dict|None=None
 extension:bool=False
 extension_team:str|None=None
 suspended_at:int|None=None
 result:dict|None=None
 warning:dict=field(default_factory=lambda:{'A':set(),'B':set()})
 timeouts:dict=field(default_factory=lambda:{'A':2,'B':2})
 review:dict|None=None
 challenges:dict=field(default_factory=lambda:{'A':1,'B':1})
 shootout:dict|None=None
 stoppages:int=0
 tackle_count:int=0             #C2: counted tackles in the current possession (C4.0: in the current set; a zone violation can return it to zero)
 zone_violations:int=0          #C4.0: defensive Keeper Zone violations called against the team defending this possession, both zones together
 tackle_ordinal:int=0           #C4.0: counted tackles in this possession whatever the count has been reset to
 reconstruction:dict|None=None  #C2: {'team','zone','live_since'} while the attacked zone must be cleared
 recovery:dict|None=None        #C2: first-tackle live recovery in progress
 live_ms:int=0
 dead_ms:int=0
 last_score_cause:int|None=None
 period_seconds:int=600
 keeper_zone_radius:float=20
 regulation_periods:int=4
 overtime_seconds:int=300
 def other(self,t):return 'B'if t=='A'else'A'
 def attack_sign(self,t):return 1 if self.ends[t]==0 else-1
 def attack_goal(self,t):return 100-self.ends[t]
 def own_zone(self,t):return 0 if self.ends[t]==0 else 1
 def active(self,team=None):return[p for p in self.players.values()if p.active and(team is None or p.team==team)]
