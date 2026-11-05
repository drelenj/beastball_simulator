"""Metres; exact geometry is separate from motion assumptions."""
import math

def clamp(v,a,b):return max(a,min(b,v))
def norm(x,y):return math.hypot(x,y)
def unit(x,y):
 d=norm(x,y);return (x/d,y/d)if d>1e-9 else(0.,0.)
def distance(a,b):return norm(a.x-b.x,a.y-b.y)
def goal_x(team):return 100. if team=='A'else 0.
def own_goal_x(team):return 0. if team=='A'else 100.
def attack_sign(team):return 1 if team=='A'else-1

def restart_point(x,y,radius=20):
 x,y=clamp(x,5,95),clamp(y,5,95)
 for gx in (0.,100.):
  d=norm(x-gx,y-50)
  if d<=radius:x,y=gx+(x-gx)*(radius+.5)/d,50+(y-50)*(radius+.5)/d
 return x,y

def zone(x,y,radius=20):
 if 0<=x<=100 and 0<=y<=100:
  if norm(x,y-50)<=radius:return 0
  if norm(x-100,y-50)<=radius:return 1
 return None

def segment_distance(px,py,ax,ay,bx,by):
 dx,dy=bx-ax,by-ay;l=dx*dx+dy*dy
 t=clamp(((px-ax)*dx+(py-ay)*dy)/l,0,1)if l else 0
 return norm(px-ax-t*dx,py-ay-t*dy),t

def segment3_distance(point,a,b):
 d=tuple(b[i]-a[i]for i in range(3));l=sum(x*x for x in d)
 t=clamp(sum((point[i]-a[i])*d[i]for i in range(3))/l,0,1)if l else 0
 return math.sqrt(sum((point[i]-a[i]-t*d[i])**2 for i in range(3))),t

def legal_goal(y,z,r=.1075):
 #The ball's entire circular section must fit the semicircle above the surface.
 return z>=r-1e-7 and norm(y-50,z)+r<=6+1e-7

def ballistic(origin,target,speed,g=9.81,high=False):
 dx,dy=target[0]-origin[0],target[1]-origin[1];d=norm(dx,dy);dz=target[2]-origin[2]
 if d<.01:return(0.,0.,speed),max(.01,abs(dz)/speed)
 disc=speed**4-g*(g*d*d+2*dz*speed*speed)
 if disc<0:return None
 theta=math.atan((speed*speed+(1 if high else-1)*math.sqrt(disc))/(g*d))
 h=speed*math.cos(theta);ux,uy=unit(dx,dy)
 return(h*ux,h*uy,speed*math.sin(theta)),d/h

def ball_at(b,t,g=9.81,k=.015):
 """Where a free ball will be t seconds ahead: gravity plus linear drag, before any bounce."""
 if k<1e-9:return(b.x+b.vx*t,b.y+b.vy*t,b.z+b.vz*t-.5*g*t*t)
 e=1-math.exp(-k*t)
 return(b.x+b.vx*e/k,b.y+b.vy*e/k,b.z+(b.vz+g/k)*e/k-g*t/k)

def launch_for(origin,target,speed,g=9.81,k=.015):
 """Launch velocity of exactly the given speed whose flatter arc passes through target, with drag.
 Returns (velocity, flight_time), or None when the target is out of range at that speed."""
 dx,dy=target[0]-origin[0],target[1]-origin[1];d=norm(dx,dy);dz=target[2]-origin[2]
 if d<.05 or speed<=0:return None
 ux,uy=unit(dx,dy)
 def miss(theta):
  vh=speed*math.cos(theta);vz=speed*math.sin(theta)
  if k<1e-9:t=d/vh;return vz*t-.5*g*t*t-dz,t
  q=1-k*d/vh
  if q<=0:return None,None
  t=-math.log(q)/k;e=1-math.exp(-k*t)
  return(vz+g/k)*e/k-g*t/k-dz,t
 lo,hi=-1.2,math.pi/4
 elo,_=miss(lo);ehi,_=miss(hi)
 if ehi is None or ehi<0 or elo is None or elo>0:return None
 for _ in range(48):
  mid=(lo+hi)/2;em,_=miss(mid)
  if em is None or em<0:lo=mid
  else:hi=mid
 theta=(lo+hi)/2;_,t=miss(theta)
 vh=speed*math.cos(theta)
 return(vh*ux,vh*uy,speed*math.sin(theta)),t

def predict_path(b,g=9.81,k=.015,restitution=.7745966692,horizon=3.0,step=.05):
 """Sampled future path of a free ball, using the same flight, bounce and roll rules as the match itself.
 Returns [(t,x,y,z)], ending where the ball leaves the field. Cached on the ball for the current state."""
 key=(b.x,b.y,b.z,b.vx,b.vy,b.vz)
 cache=getattr(b,'_path_cache',None)
 if cache and cache[0]==key:return cache[1]
 x,y,z,vx,vy,vz=key;t=0.;drag=math.exp(-k*step);path=[(0.,x,y,z)]
 while t<horizon:
  x+=vx*step;y+=vy*step;z+=vz*step-.5*g*step*step;vx*=drag;vy*=drag;vz=(vz-g*step)*drag
  if z<=b.radius:
   z=b.radius
   if abs(vz)>2:vz=-vz*restitution;vx*=.76;vy*=.76
   else:vz=0;vx*=max(0,1-step*3);vy*=max(0,1-step*3)
  t+=step;path.append((t,x,y,z))
  if not(-1<=x<=101 and -1<=y<=101):break
 b._path_cache=(key,path);return path

def intercept_xy(p,path,reach=1.0,earliest=True):
 """Where player p should run to meet a ball, read from its predicted path.
 A point is playable when the ball is within reach of the hands, or low enough to scoop.
 Reachability starts from the player's present motion: by time t he can be anywhere within
 1/2 x acceleration x t^2 of where his current velocity would carry him, and no further than top speed allows.
 earliest=True: the first playable point he can reach (cutting the ball off).
 earliest=False: within the first stretch of the path he can reach, the point needing the least change of course (receiving it).
 Falls back to the playable point he misses by least, then to the end of the path.
 For the receiver (earliest=False) the returned target is placed along the line to the meeting point at the braking distance of the
 speed needed to cover the distance in the time left, allowing for the time it takes to build that
 speed. The mover's own speed law then holds that speed, so the player
 arrives when the ball does and runs through it, instead of sprinting early or slowing to a stop."""
 hand=p.z+.62*p.a.height;vmax=p.a.maximum_speed*.88;a=p.a.acceleration;pick=None;least=1e9;best=None;slackbest=1e9;at=None;bi=None
 for i,(t,x,y,z) in enumerate(path):
  if not(0<=x<=100 and 0<=y<=100):break
  ok=False
  if abs(z-hand)<=reach or z<.4:
   d=norm(x-p.x,y-p.y);dev=norm(x-p.x-p.vx*t,y-p.y-p.vy*t);room=.5*a*t*t+.2*reach
   if dev<=room and d-.2*reach<=vmax*t:
    ok=True
    if earliest:pick=(t,x,y);break
    if dev<least:least=dev;pick=(t,x,y);at=i
   elif max(dev-room,d-.2*reach-vmax*t)<slackbest:slackbest=max(dev-room,d-.2*reach-vmax*t);best=(t,x,y);bi=i
  if pick and not ok:break #only the first stretch of the path he can reach is considered; he does not wait for a later one
 if not earliest and at is None and pick is None and bi is not None:
  #No point is comfortably reachable: he goes for the one he misses by least, refined the same way.
  at=bi;pick=best;least=norm(best[1]-p.x-p.vx*best[0],best[2]-p.y-p.vy*best[0])
 if not earliest and at is not None:
  #The path is sampled; between the samples next to the chosen one, take the instant at which continuing on course comes closest.
  for j in(at-1,at):
   if j<0 or j+1>=len(path):continue
   (t0,x0,y0,_),(t1,x1,y1,_)=path[j],path[j+1]
   if not(0<=x0<=100 and 0<=y0<=100 and 0<=x1<=100 and 0<=y1<=100):continue
   ax,ay=x0-p.x-p.vx*t0,y0-p.y-p.vy*t0;bx,by=x1-p.x-p.vx*t1-ax,y1-p.y-p.vy*t1-ay;l=bx*bx+by*by
   u=clamp(-(ax*bx+ay*by)/l,0,1)if l>1e-12 else 0.;dev=norm(ax+u*bx,ay+u*by)
   if dev<least:least=dev;pick=(t0+u*(t1-t0),x0+u*(x1-x0),y0+u*(y1-y0))
 t,x,y=pick or best or path[-1][:3]
 d=norm(x-p.x,y-p.y)
 if not earliest and d>1e-6 and t>1e-6: #the receiver is re-routed every step, so he can be paced; a chaser simply goes to the point
  ux,uy=(x-p.x)/d,(y-p.y)/d;v0=p.vx*ux+p.vy*uy;short=d-v0*t
  if short<=0:v=d/t #already quick enough: ease to the speed that arrives on time
  else:
   disc=a*a*t*t-2*a*short #speed to build, at acceleration a, so that the distance is covered in time t
   v=v0+a*t-math.sqrt(disc)if disc>=0 else vmax
  v=clamp(v,0.,vmax);lead=max(v*v/(2*p.a.braking),min(d,.3));x=p.x+ux*lead;y=p.y+uy*lead
 return(clamp(x,.5,99.5),clamp(y,.5,99.5))

def travel_time(d,a,v):
 #One-dimensional reach estimate, explicitly a policy approximation.
 threshold=v*v/(2*a)
 return math.sqrt(2*d/a)if d<=threshold else v/a+(d-threshold)/v

def disk_path_blocked(a,b,players,extra=.2,exclude=()):
 return any(p.id not in exclude and segment_distance(p.x,p.y,*a,*b)[0]<p.radius+extra for p in players)
