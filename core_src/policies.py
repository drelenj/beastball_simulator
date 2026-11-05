"""Policies choose observable actions; no policy chooses whether an action scores."""
from dataclasses import dataclass,replace
import math,random
from .types import Player,Attributes,MatchState
from .geometry import norm,clamp,unit,zone,segment_distance,predict_path,intercept_xy

@dataclass(frozen=True)
class Tactics:
 width:float=25
 support:float=9
 pace:float=.75
 pass_pressure:float=5
 shoot_distance:float=23
 escort:int=1
 escort_spacing:float=2.5
 escort_shape:str='arc'
 arrow_interval:float=18
 reserve:int=2
 possession_patience:float=.5
 hunt_count:int=3
 defense:str='adaptive'
 risk:float=.5

TACTICS={
 'balanced':Tactics(),
 'speed':Tactics(width=31,support=16,pace=1,pass_pressure=4,shoot_distance=28,escort=0,arrow_interval=22,possession_patience=.1,hunt_count=4,defense='hunt',risk=.8),
 'contact':Tactics(width=17,support=5,pace=.5,pass_pressure=2.7,shoot_distance=12,escort=2,arrow_interval=24,possession_patience=.8,hunt_count=3,defense='man',risk=.35),
 'escort':Tactics(width=15,support=4,pace=.5,pass_pressure=2,shoot_distance=12,escort=4,escort_spacing=2.4,arrow_interval=20,possession_patience=.75,hunt_count=3,defense='zone',risk=.35),
 'wide':Tactics(width=42,support=12,pace=.72,pass_pressure=8,shoot_distance=30,escort=0,arrow_interval=22,possession_patience=.55,hunt_count=2,defense='zone',risk=.65),
 'archery':Tactics(width=28,support=7,pace=.67,pass_pressure=5,shoot_distance=22,escort=1,arrow_interval=4,reserve=0,possession_patience=.5,hunt_count=4,defense='hunt',risk=.6),
 'zone_pressure':Tactics(width=23,support=6,pace=.7,pass_pressure=4,shoot_distance=13,escort=2,arrow_interval=16,possession_patience=.7,hunt_count=3,defense='man',risk=.65),
 'conservative':Tactics(width=30,support=9,pace=.5,pass_pressure=7,shoot_distance=25,escort=1,arrow_interval=25,reserve=4,possession_patience=.95,hunt_count=2,defense='zone',risk=.2),
 'hunt':Tactics(width=26,support=8,pace=.8,hunt_count=6,defense='hunt',arrow_interval=14,risk=.7),
 'zone':Tactics(width=30,support=11,pace=.65,hunt_count=1,defense='zone',possession_patience=.6),
 'man':Tactics(width=24,support=8,pace=.75,hunt_count=3,defense='man',risk=.6)
}

def mix_tactics(primary,secondary=None,weight=.5,overrides=None):
 a=TACTICS[primary]
 if secondary:
  b=TACTICS[secondary];kw={}
  for name in a.__dataclass_fields__:
   x,y=getattr(a,name),getattr(b,name)
   if isinstance(x,(float,int)):kw[name]=x*(1-weight)+y*weight
   else:kw[name]=y if weight>=.5 else x
  kw['escort']=round(kw['escort']);kw['hunt_count']=round(kw['hunt_count']);kw['reserve']=round(kw['reserve']);a=Tactics(**kw)
 return replace(a,**(overrides or{}))

def make_roster(team,archetype,rng):
 players={}
 for i in range(22):
  a=Attributes();a.height=clamp(rng.gauss(2.55,.27),1.8,3.6576);a.mass=clamp(rng.gauss(230,40),110,420);a.reach=.46*a.height
  for k in('strength','agility','endurance','balance','contact_resistance','tackling','blocking','ball_handling','passing','kicking','catching','awareness'):
   setattr(a,k,clamp(rng.gauss(.68,.065),.4,.95))
  a.maximum_speed=clamp(rng.gauss(27,3),18,38);a.acceleration=rng.uniform(8,12);a.braking=rng.uniform(11,16);a.turning=rng.uniform(10,16);a.decision_speed=rng.uniform(.18,.38)
  if archetype=='speed':a.maximum_speed=42;a.acceleration=14;a.mass=155;a.strength=.52;a.agility=.88;a.turning=17;a.contact_resistance=.53;a.braking=17
  elif archetype=='power':a.mass=390;a.height=3.1;a.reach=1.5;a.strength=.9;a.balance=.83;a.maximum_speed=21;a.acceleration=7;a.turning=8;a.blocking=.84;a.contact_resistance=.9
  elif archetype=='reach':a.height=3.6576;a.mass=330;a.reach=1.8;a.maximum_speed=25;a.acceleration=8;a.catching=.86;a.blocking=.8
  elif archetype=='technical':a.mass=190;a.maximum_speed=27;a.passing=.9;a.catching=.88;a.ball_handling=.9;a.awareness=.9;a.decision_speed=.16;a.strength=.57
  elif archetype=='endurance':a.endurance=.96;a.mass=235;a.maximum_speed=25;a.strength=.7
  elif archetype=='mixed':
   if i%3==0:a.mass=350;a.strength=.87;a.maximum_speed=22
   elif i%3==1:a.maximum_speed=40;a.acceleration=13;a.mass=165
   else:a.passing=.9;a.catching=.87;a.awareness=.88
  elif archetype=='precision':a.archery_accuracy=.96;a.keeper_skill=.87
  elif archetype!='balanced':raise ValueError('Unknown roster '+archetype)
  role='field'if i!=10 and i!=11 else'keeper'if i==10 else'archer'
  if role=='keeper':a.keeper_skill=max(a.keeper_skill,.82);a.catching=max(a.catching,.82);a.jump_height=1.6
  if role=='archer':a.archery_accuracy=max(a.archery_accuracy,.86);a.archery_release_speed=29
  a.validate();p=Player(f'{team}{i}',team,role,i<12,a,slot=i)
  if i<10:p.x=18+(i//5)*14;p.y=10+(i%5)*18
  elif i==10:p.x=3;p.y=50
  elif i==11:p.x=25;p.y=-5
  else:p.x=75;p.y=-43
  if team=='B':p.x=100-p.x;p.y=100-p.y
  p.target=(p.x,p.y);players[p.id]=p
 return players

class Policy:
 def __init__(self,team,tactics,defense=None):
  self.assume={};self.pocket={};self.team=team;self.t=tactics;self.defense=defense or tactics.defense;self.recent=[];self.last_score=(0,0)
 def eligible(self,s):return[p for p in s.players.values()if p.team==self.team and p.eligible(s.now)and p.role!='archer']
 def targets(self,s):
  t=self.t;sgn=s.attack_sign(self.team);own=s.ends[self.team];goal=s.attack_goal(self.team);b=s.ball;ours=self.eligible(s)
  opp=[p for p in s.players.values()if p.team!=self.team and p.eligible(s.now)and p.role!='archer'];fields=[p for p in ours if p.role=='field']
  carrier=s.players.get(b.carrier);attacking=s.owner==self.team
  targets={};clock=s.possession_ms/1000;losing=s.score[self.team]<s.score[s.other(self.team)];late=s.period>=4 and s.game_ms<120000
  live_carrier=carrier if carrier and carrier.team==self.team else None
  escorts=[]
  if live_carrier:
   escorts=sorted((p for p in fields if p.id!=carrier.id),key=lambda p:norm(p.x-carrier.x,p.y-carrier.y))[:t.escort]
  for p in ours:
   if p.role=='keeper':
    if b.carrier==p.id:targets[p.id]=(own+sgn*(s.keeper_zone_radius+2),50)
    else:
     gy=clamp(50+(b.y-50)*.35,45,55);gx=own+sgn*(2 if not attacking else 7)
     if b.carrier is None and b.vx*sgn<0 and abs(b.vx)>.1:
      tt=(own-b.x)/b.vx
      if 0<tt<2:gy=clamp(b.y+b.vy*tt,44,56)
     targets[p.id]=(gx,gy)
    continue
   zn=zone(p.x,p.y,s.keeper_zone_radius)
   distance_out=max(0,(s.keeper_zone_radius+1.5)-norm(p.x-(0 if zn==0 else 100),p.y-50))if zn is not None else 0
   exit_ms=1000*(math.sqrt(2*distance_out/max(1,p.a.acceleration))+p.speed/max(1,p.a.braking)+p.a.decision_speed+.3)
   if self.pocket.get('zone_marking'):exit_ms+=1200 #C2 provisional controller: leave earlier. The free-run exit estimate is too short in traffic, and under C2 an exit costs nothing.
   if zn is not None and p.zone_ms[zn]>=max(400,5000-exit_ms):
    gx=0 if zn==0 else 100;ux,uy=unit(p.x-gx,p.y-50);targets[p.id]=(clamp(gx+ux*(s.keeper_zone_radius+2),1,99),clamp(50+uy*(s.keeper_zone_radius+2),1,99));continue
   if zn is not None and self.pocket.get('zone_marking')and not attacking and p.unmarked_ms[zn]>=max(400,5000-exit_ms-600):
    #C2 provisional controller: an unmarked defender running out of allowance closes on the nearest opponent if that is quicker than leaving, else leaves.
    md=self.pocket.get('marking_distance',3.);near=min(opp,key=lambda q:norm(q.x-p.x,q.y-p.y))if opp else None
    if near is not None and norm(near.x-p.x,near.y-p.y)-md<distance_out:targets[p.id]=(clamp(near.x,1,99),clamp(near.y,1,99));continue
    gx=0 if zn==0 else 100;ux,uy=unit(p.x-gx,p.y-50);targets[p.id]=(clamp(gx+ux*(s.keeper_zone_radius+2),1,99),clamp(50+uy*(s.keeper_zone_radius+2),1,99));continue
   rc=getattr(s,'reconstruction',None)
   if rc and rc['team']==self.team and b.carrier==p.id and zn==rc['zone']:
    #C2 provisional controller: the carrier takes the ball out across the arc to clear the zone.
    gx=0 if zn==0 else 100;ux,uy=unit(p.x-gx,p.y-50);targets[p.id]=(clamp(gx+ux*(s.keeper_zone_radius+3),1,99),clamp(50+uy*(s.keeper_zone_radius+3),1,99));continue
   if not self.pocket.get('zone_marking')and any(p.zone_ms[j]>400 and p.outside_ms[j]<3000 for j in(0,1)): #Pocket 1.1 controller for the old three-second outside wait; it has no meaning under C2 occupancy
    targets[p.id]=(clamp(p.x-sgn*4,s.keeper_zone_radius+2,98-s.keeper_zone_radius),clamp(p.y,4,96));continue
   if s.phase.value=='award':
    if attacking:
     nearest=min(fields,key=lambda q:norm(q.x-b.x,q.y-b.y))if fields else p
     targets[p.id]=(b.x,b.y)if p.id==nearest.id else(clamp(b.x+sgn*8,2,98),clamp(b.y+(p.slot%2*2-1)*7,2,98))
    else:
     ux,uy=unit(p.x-b.x,p.y-b.y);targets[p.id]=(clamp(b.x+ux*5,2,98),clamp(b.y+uy*5,2,98))
    continue
   if b.carrier is None:
    tt=.4;chase=(clamp(b.x+b.vx*tt,1,99),clamp(b.y+b.vy*tt,1,99))
    read=self.assume.get('c1_chasers_read_flight')
    if read:
     #C1: read the ball's real path (flight, bounces and roll), not a fixed 0.4 s extrapolation.
     #Each field player finds where it could meet the ball; the closest few to their own meeting point go.
     key=(s.now,b.version,b.x,b.y)
     if getattr(self,'_chase_key',None)!=key:
      path=predict_path(b,self.assume.get('gravity',9.81),self.assume.get('ball_drag',.015),self.assume.get('ball_restitution',.7745966692))
      pts={q.id:intercept_xy(q,path,q.a.reach*.9,True)for q in fields}
      order=sorted(fields,key=lambda q:(norm(q.x-pts[q.id][0],q.y-pts[q.id][1]),q.id))
      self._chase_key=key;self._chase=(pts,[q.id for q in order])
     pts,order=self._chase;rank=order.index(p.id)
     if rank<(4 if t.defense=='hunt'else 3):targets[p.id]=pts[p.id];continue
    else:
     rank=sorted(fields,key=lambda q:norm(q.x-chase[0],q.y-chase[1])).index(p)
     if rank<(4 if t.defense=='hunt'else 3):targets[p.id]=chase;continue
    if False:pass
    else:targets[p.id]=(clamp(b.x-sgn*(6+rank),3,97),clamp(50+(p.slot%5-2)*t.width/2,3,97))
    continue
   if live_carrier:
    if p.id==carrier.id:
     nearest=sorted(opp,key=lambda q:norm(q.x-p.x,q.y-p.y))[:4]
     options=[clamp(p.y+dy,4,96)for dy in(-14,-7,0,7,14)]
     def lane(y):
      endpoint=(clamp(p.x+sgn*12,0,100),y)
      room=min((segment_distance(q.x,q.y,p.x,p.y,*endpoint)[0]for q in nearest),default=20)
      return room-.025*abs(y-50)-.08*abs(y-p.y)
     dest=max(options,key=lane)
     if t.possession_patience>.9 and not losing and late and clock>15:dest=clamp(p.y+(8 if p.y<50 else-8),5,95);gx=p.x-sgn*3
     else:
      lookahead=max(15,p.a.maximum_speed**2/(2*p.a.braking)+8)
      gx=clamp(p.x+sgn*lookahead,.25,99.75)
     if abs(goal-p.x)<14:dest=clamp(50+(3.8 if p.y>50 else-3.8),45,55);gx=goal-sgn*.2
     if self.pocket.get('release_territories') and abs(goal-p.x)<max(14,s.keeper_zone_radius+2):
      pc=self.pocket
      seek_inner=pc.get('adapt_scoring') and pc['inner_points']>max(pc['release_points'],pc['outside_points'] if not pc['zone_only'] else 0)
      radius=pc['inner_zone_radius'] if seek_inner else s.keeper_zone_radius
      gx=goal-sgn*max(.5,radius*.6);dest=50+(1 if p.y>50 else -1)*min(3.8,radius*.3)
     targets[p.id]=(gx,dest)
    elif p in escorts:
     i=escorts.index(p);n=len(escorts)
     if t.escort_shape=='ring':angle=2*math.pi*i/max(1,n)
     elif t.escort_shape=='wedge':angle=(-1 if i%2 else 1)*(.5+.35*(i//2))
     else:angle=(-1.15+2.3*i/max(1,n-1))if n>1 else 0
     targets[p.id]=(clamp(carrier.x+sgn*(t.escort_spacing*math.cos(angle)+.2*carrier.speed),1,99),clamp(carrier.y+t.escort_spacing*math.sin(angle),1,99))
    else:
     row=p.slot%5;dy=(row-2)*t.width/2
     lead=t.support*(1 if p.slot%3 else-.65)
     if t==TACTICS['zone_pressure'] and abs(goal-b.x)<40:lead=abs(goal-b.x)-8
     targets[p.id]=(clamp(b.x+sgn*lead,3,97),clamp(50+dy,3,97))
   else:
    target_carrier=carrier
    ranked=sorted(fields,key=lambda q:norm(q.x-carrier.x,q.y-carrier.y))
    if self.defense=='man':
     candidates=sorted((q for q in opp if q.role=='field'),key=lambda q:q.slot)
     mark=candidates[p.slot%len(candidates)]if candidates else carrier
     targets[p.id]=(clamp(mark.x+sgn*1.2,1,99),clamp(mark.y,1,99))
    elif self.defense=='hunt'or p in ranked[:t.hunt_count]:
     rank=ranked.index(p);lead=.25+rank*.06
     tx=carrier.x+carrier.vx*lead;ty=carrier.y+carrier.vy*lead
     angle=0 if rank==0 else(-1 if rank%2 else 1)*(.7+rank*.5)
     targets[p.id]=(clamp(tx,1,99),clamp(ty+angle,1,99))
    else:
     line=clamp(b.x+sgn*12,own+sgn*(s.keeper_zone_radius+2) if sgn>0 else 8,92 if sgn>0 else own+sgn*(s.keeper_zone_radius+2))
     if sgn<0:line=clamp(b.x-12,8,78)
     observed_y=sum(v[1]for v in self.recent)/len(self.recent)if self.recent else 50
     targets[p.id]=(line,clamp(50+(p.slot%5-2)*15+.15*(observed_y-50),5,95))
  return targets
 def pass_ranked(self,s,p):
  """C1: every pass option, best first, so an unreachable first choice can be replaced."""
  sgn=s.attack_sign(p.team)
  mates=[q for q in self.eligible(s)if q.id!=p.id and q.posture=='upright'and norm(q.x-p.x,q.y-p.y)<45]
  opponents=[q for q in s.players.values()if q.team!=p.team and q.eligible(s.now)and q.role!='archer']
  def utility(q):
   d=norm(q.x-p.x,q.y-p.y)
   lane=min((segment_distance(o.x,o.y,p.x,p.y,q.x,q.y)[0]for o in opponents),default=15)
   pressure=min((norm(o.x-q.x,o.y-q.y)for o in opponents),default=15)
   return .45*sgn*(q.x-p.x)+1.3*min(lane,8)+.8*min(pressure,12)-.10*d+2*q.a.catching
  return sorted(mates,key=utility,reverse=True)
 def pass_choice(self,s,p):
  b=s.ball;sgn=s.attack_sign(p.team)
  mates=[q for q in self.eligible(s)if q.id!=p.id and q.posture=='upright'and norm(q.x-p.x,q.y-p.y)<45]
  opponents=[q for q in s.players.values()if q.team!=p.team and q.eligible(s.now)and q.role!='archer']
  def utility(q):
   d=norm(q.x-p.x,q.y-p.y)
   lane=min((segment_distance(o.x,o.y,p.x,p.y,q.x,q.y)[0]for o in opponents),default=15)
   pressure=min((norm(o.x-q.x,o.y-q.y)for o in opponents),default=15)
   advancement=sgn*(q.x-p.x)
   return .45*advancement+1.3*min(lane,8)+.8*min(pressure,12)-.10*d+2*q.a.catching
  return max(mates,key=utility)if mates else None
