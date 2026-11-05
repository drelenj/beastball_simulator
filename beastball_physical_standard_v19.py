"""Beastball Physical Standard v1.9: controlled joint-limit sensitivity laboratory.

No new canonical force values. This layer audits the v1.8 reduced-order model.
"""
from dataclasses import dataclass, replace
from math import isfinite
from beastball_physical_standard_v18 import World as V18World, Parameters as V18Parameters
from beastball_physical_standard_v12 import norm

@dataclass(frozen=True)
class Parameters(V18Parameters):
    joint_capacity_scale: float=1.
    def __post_init__(self):
        super().__post_init__()
        if not isfinite(self.joint_capacity_scale) or self.joint_capacity_scale<=0:
            raise ValueError('joint_capacity_scale must be finite and positive')

class World(V18World):
    def __init__(self,dynamics=None,parameters=None):
        super().__init__(dynamics,parameters or Parameters())
    def joint_capacity(self,p,s,requested,braking=False):
        cap,util,bottleneck,factor=super().joint_capacity(p,s,requested,braking)
        scale=self.c.joint_capacity_scale
        return cap*scale,{k:v/scale for k,v in util.items()},bottleneck,factor

def scenario(p,action='brake',*,joint_scale=1.,traction=1.,strength=None,stance_fraction=.32,dt=.005,duration=.5,initial_speed=20.):
    if strength is not None:
        p=replace(p,athlete=replace(p.athlete,strength=strength))
    w=World(parameters=Parameters(joint_capacity_scale=joint_scale,ground_friction_multiplier=traction))
    s=w.setup(p,stance_fraction=stance_fraction,recovery_enabled=False)
    if action=='brake':
        s=replace(s,velocity=(initial_speed,0.));target=(0.,0.)
    elif action=='cut':
        s=replace(s,velocity=(initial_speed,0.));target=(0.,initial_speed)
    elif action=='sprint':
        target=(w.d.top_speed(p),0.)
    else:raise ValueError(action)
    peak_joint=peak_ground=peak_util=0.;active_joint=active_traction=0;steps=0
    for _ in range(round(duration/dt)):
        s=w.step(p,s,target,dt);steps+=1
        demand=norm(s.muscle_demand_N);joint=norm(s.joint_limited_force_N);ground=norm(s.ground_reaction_N)
        peak_joint=max(peak_joint,joint);peak_ground=max(peak_ground,ground)
        peak_util=max(peak_util,s.ankle_utilization,s.knee_utilization,s.hip_utilization)
        if demand>joint+1e-5:active_joint+=1
        if joint>ground+1e-5:active_traction+=1
        if s.grounded:break
    return dict(action=action,profile=p.label,strength=p.athlete.strength,traction=traction,joint_scale=joint_scale,stance_fraction=stance_fraction,
                initial_speed_m_s=initial_speed,duration_s=steps*dt,final_speed_m_s=round(norm(s.velocity),5),
                x_m=round(s.position[0],5),y_m=round(s.position[1],5),
                peak_joint_force_N=round(peak_joint,3),peak_ground_force_N=round(peak_ground,3),
                peak_joint_utilization=round(peak_util,4),joint_limited_steps=active_joint,traction_limited_steps=active_traction,
                grounded=s.grounded)
