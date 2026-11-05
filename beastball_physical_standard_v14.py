"""Beastball v1.4: explicit bilateral support feet and finite-rate recovery stepping.
Experimental reduced-order 2D support/roll model; not a 3D ragdoll or Pocket integration.
"""
from dataclasses import dataclass, replace
from math import sin, cos, sqrt, ceil
from beastball_physical_standard_v13 import World as V13World, Body as V13Body, Parameters as V13Parameters
from beastball_physical_standard_v12 import norm, add, mul

@dataclass(frozen=True)
class Foot:
    x: float
    y: float
    planted: bool = True
    cooldown_s: float = 0.

@dataclass(frozen=True)
class Body(V13Body):
    left_foot: Foot = Foot(-.35,-.25)
    right_foot: Foot = Foot(.35,.25)
    recovery_steps: int = 0
    recovery_enabled: bool = True

@dataclass(frozen=True)
class Parameters(V13Parameters):
    recovery_trigger_rad: float = .10
    recovery_reach_height_fraction: float = .45
    recovery_step_speed_m_s: float = 9.
    recovery_cooldown_s: float = .18
    recovery_neural_gain: float = 1.
    recovery_damping: float = 1.8
    foot_support_radius_m: float = .12
    def __post_init__(self):
        super().__post_init__()
        if min(self.recovery_trigger_rad,self.recovery_reach_height_fraction,self.recovery_step_speed_m_s,self.recovery_cooldown_s,self.recovery_neural_gain,self.recovery_damping,self.foot_support_radius_m)<=0:
            raise ValueError('positive recovery parameters required')

class World(V13World):
    def __init__(self,dynamics=None,parameters=None):super().__init__(dynamics,parameters or Parameters())
    def setup(self,p,stance_fraction=.32,position=(0.,0.),velocity=(0.,0.),recovery_enabled=True):
        if stance_fraction<=0:raise ValueError('stance fraction')
        width=p.athlete.height_m*stance_fraction
        return Body(position=position,velocity=velocity,stance_width_m=width,
                    left_foot=Foot(position[0]-width/2,position[1]-width*.30),
                    right_foot=Foot(position[0]+width/2,position[1]+width*.30),
                    recovery_enabled=recovery_enabled)
    def support_interval(self,s):
        feet=[f for f in (s.left_foot,s.right_foot) if f.planted]
        if not feet:return None
        r=self.c.foot_support_radius_m
        return (min(f.x for f in feet)-r,max(f.x for f in feet)+r)
    def _step(self,p,s,target,dt,external_force,contact_torque):
        if s.grounded:return s
        # v1.3 advances body momentum, rotation and lean; v1.4 then resolves feet and recovery.
        old=s
        s=super()._step(p,s,target,dt,external_force,contact_torque)
        if s.grounded:
            # v1.3's fixed support is replaced with actual foot support and recovery opportunity.
            s=replace(s,grounded=False)
        lf=replace(s.left_foot,cooldown_s=max(0.,s.left_foot.cooldown_s-dt))
        rf=replace(s.right_foot,cooldown_s=max(0.,s.right_foot.cooldown_s-dt))
        s=replace(s,left_foot=lf,right_foot=rf)
        com_h=.53*p.athlete.height_m
        projection=s.position[0]+com_h*sin(s.lean)
        interval=self.support_interval(s)
        # A prescribed recovery step is a bounded movement of one foot, not an instantaneous relocation.
        if s.recovery_enabled and abs(s.lean)>=self.c.recovery_trigger_rad:
            # Recover in direction of falling COM, including inertial tendency.
            direction=1. if (s.lean+s.lean_rate*.12)>=0 else -1.
            footname='right_foot' if direction>0 else 'left_foot'
            foot=getattr(s,footname)
            maxreach=p.athlete.height_m*self.c.recovery_reach_height_fraction
            desired=s.position[0]+direction*maxreach
            if foot.cooldown_s<=0 and abs(desired-foot.x)>.025:
                # Foot advances with finite velocity; if currently supporting, other foot stays planted.
                step=min(abs(desired-foot.x),self.c.recovery_step_speed_m_s*dt)
                new_x=foot.x+(1 if desired>foot.x else -1)*step
                completed=abs(new_x-desired)<.025
                foot=replace(foot,x=new_x,cooldown_s=self.c.recovery_cooldown_s if completed else 0.)
                s=replace(s,**{footname:foot},recovery_steps=s.recovery_steps+(1 if completed else 0))
        interval=self.support_interval(s)
        if interval is not None:
            lo,hi=interval
            # Restoring ankle/hip torque can act only when COM projection lies inside the foot support.
            if lo<=projection<=hi and s.recovery_enabled:
                a=p.athlete
                ability=self.d.standard.ability(a.strength)
                # Counteract lean angular velocity and lean angle; bounded by force capacity.
                desired_angular_acc=(-self.c.recovery_neural_gain*ability*30*s.lean
                                     -self.c.recovery_damping*ability*12*s.lean_rate)
                max_angular_acc=self.brake_accel(p,s)/max(com_h,.01)
                angular_acc=max(-max_angular_acc,min(max_angular_acc,desired_angular_acc))
                s=replace(s,lean_rate=s.lean_rate+angular_acc*dt)
            unsupported=not lo<=projection<=hi
        else:unsupported=True
        # Grounding needs meaningful rotation and lost support. No dice roll.
        grounded=unsupported and abs(s.lean)>=self.c.max_lean_rad
        return replace(s,grounded=grounded)

def run_trial(p,impulse_N_s,recovery=True,dt=.005,duration=.8,contact_height_fraction=.75):
    w=World();s=w.setup(p,recovery_enabled=recovery)
    s=w.impact(p,s,(impulse_N_s,0.),contact_height_m=p.athlete.height_m*contact_height_fraction)
    maxlean=abs(s.lean)
    for _ in range(round(duration/dt)):
        s=w.step(p,s,(0.,0.),dt)
        maxlean=max(maxlean,abs(s.lean))
        if s.grounded:break
    return dict(profile=p.label,impulse_N_s=impulse_N_s,recovery=recovery,grounded=s.grounded,
                recovery_steps=s.recovery_steps,final_lean_rad=round(s.lean,4),peak_lean_rad=round(maxlean,4),
                final_x_m=round(s.position[0],4),support_interval=str(tuple(round(v,3) for v in w.support_interval(s))))
