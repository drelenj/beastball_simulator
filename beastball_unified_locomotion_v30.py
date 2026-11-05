"""Beastball v3.0: standalone 2.5D hybrid locomotion solver.
One integrator for COM x/y/z, contact normal/shear, flight and landing.
Experimental reduced-order model; not articulated biomechanics or Pocket integration.
"""
from dataclasses import dataclass, replace
from math import hypot, sqrt, cos, sin, radians, isfinite
from beastball_physical_standard_v11 import profile, Dynamics
from beastball_physical_standard_v20 import World as ForceWorld, Parameters

G=9.80665
MAX_SPEED=44.704

def length(v):return hypot(v[0],v[1])
def unit(v):
    n=length(v)
    return (v[0]/n,v[1]/n) if n>1e-12 else (0.,0.)
def clamp(x,a,b):return max(a,min(b,x))

@dataclass(frozen=True)
class Settings:
    dt:float=.005
    duration_s:float=3.
    turn_degrees:float=0.
    traction:float=1.
    muscle:float=1.
    joint:float=1.
    stance_s:float=.16
    push_s:float=.055
    push_bw:float=2.3
    swing_speed_m_s:float=65.
    touchdown_radius_m:float=.65
    leg_reach_height:float=.65
    spring_N_m:float=120000.
    damping_N_s_m:float=22000.
    compression_limit_m:float=.35
    max_normal_bw:float=20.
    yaw_rate_limit_rad_s:float=5.
    turn_response_s:float=.35
    flight_enabled:bool=True
    def __post_init__(self):
        for name,v in self.__dict__.items():
            if isinstance(v,bool):continue
            if not isfinite(v):raise ValueError(name)
        if not (0<self.dt<=.02 and 0<self.duration_s<=15 and -180<=self.turn_degrees<=180 and self.traction>0 and self.muscle>0 and self.joint>0 and self.stance_s>self.push_s>0 and self.push_bw>=1 and self.swing_speed_m_s>0 and self.touchdown_radius_m>0 and self.leg_reach_height>0 and self.spring_N_m>0 and self.damping_N_s_m>0 and self.compression_limit_m>0 and self.max_normal_bw>1 and self.yaw_rate_limit_rad_s>0 and self.turn_response_s>0):raise ValueError('invalid settings')

@dataclass(frozen=True)
class State:
    t:float=0.
    x:float=0.
    y:float=0.
    vx:float=0.
    vy:float=0.
    z:float=0.
    vz:float=0.
    phase:str='stance'
    phase_t:float=0.
    support:str='left'
    left:tuple=(0.,-.35)
    right:tuple=(0.,.35)
    yaw:float=0.
    normal_N:float=0.
    shear:tuple=(0.,0.)
    compression:float=0.
    peak_normal_N:float=0.
    peak_shear_N:float=0.
    max_friction_error_N:float=0.
    swing_distance_m:float=0.
    landings:int=0
    takeoffs:int=0
    missed:int=0
    grounded:bool=False
    reason:str=''

class World:
    def __init__(self,p,settings=None):
        self.p=p;self.c=settings or Settings();self.mass=p.athlete.mass_kg;self.height=p.athlete.height_m
        self.force=ForceWorld(parameters=Parameters(muscle_capacity_scale=self.c.muscle,joint_capacity_scale=self.c.joint,ground_friction_multiplier=self.c.traction))
        self.mu=self.force.d.standard.traction_coefficient*self.force.d.standard.ability(p.athlete.traction)*self.c.traction
        self.vmax=Dynamics().top_speed(p)
    def setup(self,speed=0):
        if not isfinite(speed) or not 0<=speed<=MAX_SPEED:raise ValueError('invalid starting speed')
        w=.15*self.height
        return State(vx=speed,left=(0.,-w),right=(0.,w))
    def _desired(self,s):
        a=radians(self.c.turn_degrees)
        return (self.vmax*cos(a),self.vmax*sin(a))
    def _muscle(self,s):
        desired=self._desired(s)
        delta=(desired[0]-s.vx,desired[1]-s.vy)
        braking=(s.vx*delta[0]+s.vy*delta[1])<0
        cap=self.force.muscle_force_cap(self.p,braking=braking)
        # Velocity feedback commands force, not instantaneous velocity.
        demand=(self.mass*delta[0]/self.c.turn_response_s,self.mass*delta[1]/self.c.turn_response_s)
        d=length(demand);scale=min(1.,cap/d) if d else 1.
        demand=(demand[0]*scale,demand[1]*scale)
        # Joint cap is independently computed, never an extra friction cap.
        joint_state=self.force.setup(self.p,stance_fraction=.30,recovery_enabled=False)
        joint_state=replace(joint_state,velocity=(s.vx,s.vy))
        joint_cap=self.force.joint_capacity(self.p,joint_state,demand,braking=braking)[0]
        d=length(demand);scale=min(1.,joint_cap/d) if d else 1.
        return (demand[0]*scale,demand[1]*scale)
    def _swing(self,s,dt,remaining):
        # Predict COM at touchdown; use current velocity only, no teleport.
        target=(s.x+s.vx*remaining,s.y+s.vy*remaining)
        moving='right' if s.support=='left' else 'left'
        f=getattr(s,moving);d=(target[0]-f[0],target[1]-f[1]);dist=length(d)
        move=min(dist,self.c.swing_speed_m_s*dt);u=unit(d)
        return replace(s,**{moving:(f[0]+u[0]*move,f[1]+u[1]*move)},swing_distance_m=s.swing_distance_m+move)
    def step(self,s):
        if s.grounded:return s
        c=self.c;dt=c.dt;m=self.mass;phase=s.phase;clock=s.phase_t+dt
        normal=0.;compression=s.compression;vz=s.vz;z=s.z
        takeoffs=s.takeoffs;landings=s.landings;missed=s.missed;reason=''
        if phase=='stance':
            # Pre-position the airborne foot while the other foot stays anchored.
            if clock>=c.stance_s*.35:
                launch=(c.push_bw-1)*G*c.push_s
                future=max(0.,c.stance_s-clock)+2*launch/G
                s=self._swing(s,dt,future)
            # Constant-height COM support until the force-driven push-off interval.
            normal=m*G*(c.push_bw if c.flight_enabled and clock>=c.stance_s-c.push_s else 1.)
            vz+=((normal/m)-G)*dt if c.flight_enabled else 0.
            z=0.
            if clock>=c.stance_s:
                if c.flight_enabled and vz>0:
                    phase='flight';clock=0.;takeoffs+=1
                else:
                    clock=0.;vz=0.
        elif phase=='flight':
            # No contact force in flight, even if a foot is beneath COM.
            remaining=max(0.,(vz+sqrt(max(0.,vz*vz+2*G*z)))/G)
            s=self._swing(s,dt,remaining)
            znew=z+vz*dt-.5*G*dt*dt;vz-=G*dt
            if znew<=0 and vz<0:
                moving='right' if s.support=='left' else 'left'
                f=getattr(s,moving)
                error=length((s.x+s.vx*dt-f[0],s.y+s.vy*dt-f[1]))
                if error>min(c.touchdown_radius_m,c.leg_reach_height*self.height):
                    phase='fall';reason='missed_touchdown';missed+=1;z=0.
                else:
                    phase='landing';clock=0.;z=0.;compression=0.;s=replace(s,support=moving)
            else:z=znew
        elif phase=='landing':
            # Vertical contact compliance and horizontal shear share normal force.
            compression=max(0.,compression-vz*dt)
            normal=clamp(c.spring_N_m*compression-c.damping_N_s_m*vz,0.,m*G*c.max_normal_bw)
            vz+=(normal/m-G)*dt
            if compression>c.compression_limit_m:
                phase='fall';reason='landing_travel_exceeded'
            elif normal>=m*G*c.max_normal_bw-1e-8 and vz<0:
                phase='fall';reason='landing_force_overload'
            elif vz>=-.05 and clock>=.025:
                phase='stance';clock=0.;compression=0.;vz=0.;landings+=1
        else:phase='fall';reason=s.reason or 'fall'
        # Single horizontal integrator; no inherited second traction pass.
        request=self._muscle(s) if phase in ('stance','landing') else (0.,0.)
        limit=self.mu*normal if phase in ('stance','landing') else 0.
        magnitude=length(request);u=unit(request);applied=min(magnitude,limit)
        shear=(u[0]*applied,u[1]*applied)
        vx=s.vx+shear[0]/m*dt;vy=s.vy+shear[1]/m*dt
        x=s.x+(s.vx+vx)*.5*dt;y=s.y+(s.vy+vy)*.5*dt
        # A finite yaw-rate bound; yaw is not itself a balance validation.
        target=radians(c.turn_degrees)
        yaw=s.yaw+clamp(target-s.yaw,-c.yaw_rate_limit_rad_s*dt,c.yaw_rate_limit_rad_s*dt)
        if phase=='fall':reason=reason or 'fall'
        return replace(s,t=s.t+dt,x=x,y=y,vx=vx,vy=vy,z=z,vz=vz,phase=phase,phase_t=clock,
                       normal_N=normal,shear=shear,compression=compression,yaw=yaw,
                       peak_normal_N=max(s.peak_normal_N,normal),peak_shear_N=max(s.peak_shear_N,applied),
                       max_friction_error_N=max(s.max_friction_error_N,max(0.,applied-limit)),
                       landings=landings,takeoffs=takeoffs,missed=missed,grounded=phase=='fall',reason=reason)

def assess(p,speed,settings=None,trace=False):
    c=settings or Settings();w=World(p,c);s=w.setup(speed);samples=[];maxz=0.
    for _ in range(round(c.duration_s/c.dt)):
        if s.grounded:break
        s=w.step(s);maxz=max(maxz,s.z)
        if trace:samples.append(dict(t=round(s.t,5),x=s.x,y=s.y,z=s.z,vx=s.vx,vy=s.vy,vz=s.vz,phase=s.phase,normal_N=s.normal_N,shear_N=length(s.shear),left_x=s.left[0],left_y=s.left[1],right_x=s.right[0],right_y=s.right[1],grounded=s.grounded))
    r=dict(profile=p.label,initial_speed_m_s=speed,turn_degrees=c.turn_degrees,traction_scale=c.traction,dt_s=c.dt,elapsed_s=round(s.t,5),x_m=round(s.x,5),y_m=round(s.y,5),vx_m_s=round(s.vx,5),vy_m_s=round(s.vy,5),landings=s.landings,takeoffs=s.takeoffs,missed=s.missed,peak_normal_N=round(s.peak_normal_N,2),peak_shear_N=round(s.peak_shear_N,2),peak_height_m=round(maxz,5),swing_distance_m=round(s.swing_distance_m,4),friction_violation_N=round(s.max_friction_error_N,8),grounded=s.grounded,reason=s.reason)
    return (r,samples) if trace else r
