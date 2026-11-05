"""Beastball v1.3: planar planted-foot support, yaw/roll dynamics, braking experiments.
Exploratory, not calibrated; SI units; no Pocket hook. Gravity and horizontal forces are physical.
"""
from dataclasses import dataclass, replace
from math import sin, cos, sqrt, hypot, atan2, pi, ceil
from beastball_physical_standard_v12 import add,sub,mul,norm,unit,dot,clampvec,Vec
from beastball_physical_standard_v11 import Dynamics,PerformanceProfile

@dataclass(frozen=True)
class Body:
    position:Vec=(0.,0.)
    velocity:Vec=(0.,0.)
    yaw:float=0.
    yaw_rate:float=0.
    lean:float=0.  # signed lean angle relative to vertical in contact/forward plane
    lean_rate:float=0.
    planted:bool=True
    stance_width_m:float=.8
    foot_offset_m:float=0. # support center offset from COM projection, along impact axis
    grounded:bool=False

@dataclass(frozen=True)
class Parameters:
    dt:float=.005
    max_step_s:float=.01
    yaw_inertia_factor:float=.12
    roll_inertia_factor:float=.25
    yaw_damping_per_s:float=3.
    lean_damping_per_s:float=1.2
    max_lean_rad:float=.72
    stance_length_factor:float=.35
    muscle_brake_N_per_kg:float=40.
    brake_explosive_fraction:float=.5
    plantar_traction_multiplier:float=1.
    plant_speed_limit_m_s:float=44.704
    def __post_init__(self):
        if min(self.dt,self.max_step_s,self.yaw_inertia_factor,self.roll_inertia_factor,self.max_lean_rad,self.stance_length_factor,self.muscle_brake_N_per_kg,self.plantar_traction_multiplier,self.plant_speed_limit_m_s)<=0:raise ValueError('positive parameters required')
        if not 0<=self.brake_explosive_fraction<=1:raise ValueError('brake fraction')

class World:
    def __init__(self,dynamics=None,parameters=None):self.d=dynamics or Dynamics();self.c=parameters or Parameters()
    def support_half_length(self,p,s):return max(.1,p.athlete.height_m*self.c.stance_length_factor*.5)
    def traction_accel(self,p,s):
        if not s.planted:return 0.
        return self.d.standard.traction_limit_N(p.athlete)/p.athlete.mass_kg*self.c.plantar_traction_multiplier
    def brake_accel(self,p,s):
        # Force is limited both by muscular eccentric output and available planted-foot traction.
        a=p.athlete; ability=self.d.standard.ability
        muscle=self.c.muscle_brake_N_per_kg*(self.c.brake_explosive_fraction*ability(a.explosive_power)+(1-self.c.brake_explosive_fraction)*ability(a.strength))
        return min(muscle,self.traction_accel(p,s))
    def step(self,p,s,desired_velocity:Vec,dt=None,external_force:Vec=(0.,0.),contact_torque_Nm=0.):
        dt=self.c.dt if dt is None else dt
        if dt<=0:raise ValueError('positive dt')
        count=ceil(dt/self.c.max_step_s)
        for _ in range(count):s=self._step(p,s,desired_velocity,dt/count,external_force,contact_torque_Nm)
        return s
    def _step(self,p,s,target,dt,external_force,contact_torque):
        if s.grounded:return s
        a=p.athlete;m=a.mass_kg;h=a.height_m
        target=clampvec(target,self.d.top_speed(p));dv=sub(target,s.velocity)
        if norm(dv)>1e-12:
            moving=unit(s.velocity) if norm(s.velocity)>1e-8 else unit(dv)
            brake=dot(dv,moving)<0
            cap=self.brake_accel(p,s) if brake else min(self.d.drive_accel(p),self.traction_accel(p,s))
            muscle=clampvec(mul(dv,1/dt),cap)
        else:muscle=(0.,0.)
        # The same friction budget is shared by intentional locomotion and external contact forces.
        external_acc=mul(external_force,1/m)
        total=add(muscle,external_acc)
        if s.planted:
            # External forces may exceed traction; the floor reaction is limited, not the external impulse.
            floor=clampvec(muscle,self.traction_accel(p,s))
            total=add(floor,external_acc)
        vel=add(s.velocity,mul(total,dt))
        vel=clampvec(vel,self.d.standard.max_speed_m_s) # canon locomotion ceiling
        pos=add(s.position,mul(add(s.velocity,vel),dt*.5))
        iz=self.c.yaw_inertia_factor*m*h*h
        yawrate=(s.yaw_rate+contact_torque/iz*dt)*max(0.,1-self.c.yaw_damping_per_s*dt)
        yaw=s.yaw+yawrate*dt
        # Inverted pendulum about support: lean toward impact axis, gravity destabilizes.
        # External horizontal acceleration acts at COM height; plant reactions create roll torque.
        # Signed 2D roll plane is +x. For general direction, this is a reduced-order proxy.
        com_height=.53*h
        inertia=self.c.roll_inertia_factor*m*h*h
        roll_torque=m*self.d.standard.gravity_m_s2*com_height*sin(s.lean)+external_force[0]*com_height
        leanrate=(s.lean_rate+roll_torque/inertia*dt)*max(0.,1-self.c.lean_damping_per_s*dt)
        lean=s.lean+leanrate*dt
        # Grounding requires both loss of the support region and appreciable lean.
        projection=com_height*sin(lean)-s.foot_offset_m
        unsupported=abs(projection)>self.support_half_length(p,s)
        grounded=s.planted and unsupported and abs(lean)>self.c.max_lean_rad
        return replace(s,position=pos,velocity=vel,yaw=yaw,yaw_rate=yawrate,lean=lean,lean_rate=leanrate,grounded=grounded)
    def plant(self,p,s,stance_width_m=None,foot_offset_m=None):
        if norm(s.velocity)>self.c.plant_speed_limit_m_s+1e-9:raise ValueError('cannot plant beyond physical speed limit')
        width=s.stance_width_m if stance_width_m is None else stance_width_m
        offset=s.foot_offset_m if foot_offset_m is None else foot_offset_m
        if width<=0:raise ValueError('stance width')
        return replace(s,planted=True,stance_width_m=width,foot_offset_m=offset)
    def unplant(self,s):return replace(s,planted=False)
    def impact(self,p,s,impulse:Vec,contact_height_m=None,lever_arm_m=0.):
        if contact_height_m is None:contact_height_m=.53*p.athlete.height_m
        if contact_height_m<0:raise ValueError('contact height')
        m=p.athlete.mass_kg;h=p.athlete.height_m
        vel=add(s.velocity,mul(impulse,1/m))
        # Roll and yaw angular impulse, no artificial grounding probability.
        leanrate=s.lean_rate+impulse[0]*contact_height_m/(self.c.roll_inertia_factor*m*h*h)
        yawrate=s.yaw_rate+impulse[1]*lever_arm_m/(self.c.yaw_inertia_factor*m*h*h)
        return replace(s,velocity=vel,lean_rate=leanrate,yaw_rate=yawrate)
    def contact_pair(self,pa,sa,pb,sb,impulse_on_a,contact_height_a=None,contact_height_b=None,lever_arm_a=0.,lever_arm_b=0.):
        return (self.impact(pa,sa,impulse_on_a,contact_height_a,lever_arm_a),self.impact(pb,sb,mul(impulse_on_a,-1),contact_height_b,lever_arm_b))

def run_trial(p,scenario,brake_multiplier=1.,dt=.005):
    from dataclasses import replace as r
    d=Dynamics(standard=r(Dynamics().standard,traction_coefficient=2.4*brake_multiplier))
    w=World(d);s=Body()
    if scenario=='brake':s=r(s,velocity=(20.,0.));target=(0.,0.);duration=1.5
    elif scenario=='cut':s=r(s,velocity=(20.,0.));target=(0.,20.);duration=2.
    elif scenario=='impact':s=w.impact(p,s,(2500.,0.),contact_height_m=.75*p.athlete.height_m);target=(0.,0.);duration=.6
    else:raise ValueError(scenario)
    for _ in range(round(duration/dt)):s=w.step(p,s,target,dt)
    return dict(profile=p.label,scenario=scenario,traction_multiplier=brake_multiplier,x_m=round(s.position[0],4),y_m=round(s.position[1],4),speed_m_s=round(norm(s.velocity),4),lean_rad=round(s.lean,4),yaw_rad=round(s.yaw,4),grounded=s.grounded)
