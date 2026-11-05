"""Beastball v1.2: 2D force-limited locomotion and impulse/balance experiment.
Provisional parameters. Not connected to Pocket. SI units.
"""
from dataclasses import dataclass, replace
from math import hypot, sqrt
from beastball_physical_standard_v11 import Dynamics, PerformanceProfile

Vec=tuple[float,float]
def add(a,b):return (a[0]+b[0],a[1]+b[1])
def sub(a,b):return (a[0]-b[0],a[1]-b[1])
def mul(a,s):return (a[0]*s,a[1]*s)
def norm(a):return hypot(*a)
def unit(a):return mul(a,1/norm(a)) if norm(a)>1e-12 else (0.,0.)
def dot(a,b):return a[0]*b[0]+a[1]*b[1]
def clampvec(a,m):return mul(a,min(1.,m/norm(a))) if norm(a)>1e-12 else (0.,0.)

@dataclass(frozen=True)
class State:
    position:Vec=(0.,0.)
    velocity:Vec=(0.,0.)
    heading:Vec=(1.,0.)
    balance:float=1.
    grounded:bool=False

@dataclass(frozen=True)
class Config:
    dt:float=.01
    balance_recovery_per_s:float=.30
    impulse_balance_scale:float=1.0
    ground_balance_threshold:float=.15
    max_step_s:float=.02
    def __post_init__(self):
        if self.dt<=0 or self.max_step_s<=0 or self.balance_recovery_per_s<0 or self.impulse_balance_scale<0 or not 0<=self.ground_balance_threshold<=1:raise ValueError('invalid configuration')

class World:
    def __init__(self, dynamics=None, config=None):self.d=dynamics or Dynamics();self.c=config or Config()
    def step(self,p:PerformanceProfile,s:State,desired_velocity:Vec,dt=None):
        dt=self.c.dt if dt is None else dt
        if dt<=0:raise ValueError('dt must be positive')
        for _ in range(max(1,__import__('math').ceil(dt/self.c.max_step_s))):
            h=dt/max(1,__import__('math').ceil(dt/self.c.max_step_s))
            s=self._step(p,s,desired_velocity,h)
        return s
    def _step(self,p,s,target,dt):
        if s.grounded:return s
        target=clampvec(target,self.d.top_speed(p))
        dv=sub(target,s.velocity)
        if norm(dv)<1e-12:acc=(0.,0.)
        else:
            # Maximum muscle-driven acceleration in direction of motion;
            # braking may exceed drive, and lateral acceleration consumes same traction budget.
            forward=unit(s.velocity) if norm(s.velocity)>1e-9 else unit(dv)
            signed=dot(dv,forward)
            cap=self.d.braking(p) if signed<0 else self.d.drive_accel(p)
            traction=self.d.standard.traction_limit_N(p.athlete)/p.athlete.mass_kg
            acc=clampvec(dv,cap*dt)
            acc=mul(acc,1/dt)
            acc=clampvec(acc,traction)
        newvel=add(s.velocity,mul(acc,dt))
        newvel=clampvec(newvel,self.d.top_speed(p))
        # Trapezoidal integration for displacement.
        pos=add(s.position,mul(add(s.velocity,newvel),dt*.5))
        heading=unit(newvel) if norm(newvel)>1e-9 else s.heading
        balance=min(1.,s.balance+self.c.balance_recovery_per_s*dt)
        return State(pos,newvel,heading,balance,False)
    def impulse(self,p,s,impulse:Vec,contact_height_m:float=1.,stance_width_m:float=.7):
        """External horizontal impulse and simple overturning balance proxy.
        Impulse always changes momentum; balance/grounding are exploratory, not rigid-body mechanics.
        """
        if contact_height_m<0 or stance_width_m<=0:raise ValueError('invalid contact geometry')
        mass=p.athlete.mass_kg
        vel=add(s.velocity,mul(impulse,1/mass))
        # Normalize angular disturbance to gravitational righting impulse over a 0.25s stance.
        # Not a true torque integrator: flags instability for follow-up modeling.
        righting=mass*self.d.standard.gravity_m_s2*stance_width_m*.5*.25
        disturbance=norm(impulse)*contact_height_m/max(righting,1e-9)*self.c.impulse_balance_scale
        balance=max(0.,s.balance-disturbance)
        grounded=balance<=self.c.ground_balance_threshold
        return replace(s,velocity=vel,balance=balance,grounded=grounded)
    def contact_pair(self,pa,sa,pb,sb,impulse_on_a:Vec,contact_height_a=1.,contact_height_b=1.):
        return (self.impulse(pa,sa,impulse_on_a,contact_height_a),self.impulse(pb,sb,mul(impulse_on_a,-1),contact_height_b))

def run_scenario(p,kind,world=None):
    w=world or World();s=State()
    if kind=='sprint':target=(w.d.top_speed(p),0.);duration=2.
    elif kind=='brake':s=replace(s,velocity=(20.,0.));target=(0.,0.);duration=1.5
    elif kind=='cut':s=replace(s,velocity=(20.,0.));target=(0.,20.);duration=2.
    elif kind=='reverse':s=replace(s,velocity=(20.,0.));target=(-20.,0.);duration=3.
    else:raise ValueError(kind)
    for _ in range(round(duration/w.c.dt)):s=w.step(p,s,target)
    return {'scenario':kind,'position_x_m':round(s.position[0],4),'position_y_m':round(s.position[1],4),'speed_m_s':round(norm(s.velocity),4),'vx_m_s':round(s.velocity[0],4),'vy_m_s':round(s.velocity[1],4),'balance':round(s.balance,4)}
