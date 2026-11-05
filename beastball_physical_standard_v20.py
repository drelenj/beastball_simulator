"""Beastball Physical Standard 2.0: coupled physiological calibration laboratory.

Extends the validated v1.9 reduced-order engine. Parameters are provisional;
this module measures active constraints and searches for distinguishable regimes.
Not an articulated biomechanical solver or a Pocket integration.
"""
from dataclasses import dataclass, replace
from math import isfinite
from beastball_physical_standard_v19 import World as V19World, Parameters as V19Parameters
from beastball_physical_standard_v12 import norm

@dataclass(frozen=True)
class Parameters(V19Parameters):
    muscle_capacity_scale: float = 1.
    joint_capacity_scale: float = 1.
    ground_friction_multiplier: float = 1.
    def __post_init__(self):
        super().__post_init__()
        if not isfinite(self.muscle_capacity_scale) or self.muscle_capacity_scale <= 0:
            raise ValueError('muscle_capacity_scale must be positive and finite')

class World(V19World):
    def __init__(self,dynamics=None,parameters=None):
        super().__init__(dynamics,parameters or Parameters())
    def muscle_force_cap(self,p,braking=False):
        return super().muscle_force_cap(p,braking)*self.c.muscle_capacity_scale


def trial(p, action='brake', *, muscle=1., joint=1., traction=1.,
          strength=None, explosive=None, stance=.32, initial_speed=20.,
          duration=.5, dt=.005):
    if action not in ('brake','cut','sprint'):
        raise ValueError('invalid action')
    if not isfinite(duration) or duration <= 0 or not isfinite(dt) or dt <= 0:
        raise ValueError('invalid integration interval')
    if strength is not None:
        p=replace(p,athlete=replace(p.athlete,strength=strength))
    if explosive is not None:
        p=replace(p,athlete=replace(p.athlete,explosive_power=explosive))
    w=World(parameters=Parameters(muscle_capacity_scale=muscle,joint_capacity_scale=joint,ground_friction_multiplier=traction))
    s=w.setup(p,stance_fraction=stance,recovery_enabled=False)
    if action=='brake':
        s=replace(s,velocity=(initial_speed,0.));target=(0.,0.)
    elif action=='cut':
        s=replace(s,velocity=(initial_speed,0.));target=(0.,initial_speed)
    else:
        target=(w.d.top_speed(p),0.)
    counts={'muscle':0,'joint':0,'traction':0,'unconstrained':0}
    peaks={'demand':0.,'joint':0.,'ground':0.}
    steps=0
    for _ in range(round(duration/dt)):
        s=w.step(p,s,target,dt);steps+=1
        m=norm(s.muscle_demand_N);j=norm(s.joint_limited_force_N);g=norm(s.ground_reaction_N)
        peaks['demand']=max(peaks['demand'],m);peaks['joint']=max(peaks['joint'],j);peaks['ground']=max(peaks['ground'],g)
        if m<1e-8:counts['unconstrained']+=1
        elif j < m-1e-5:counts['joint']+=1
        elif g < j-1e-5:counts['traction']+=1
        else:counts['muscle']+=1
        if s.grounded:break
    return {'profile':p.label,'action':action,'muscle_scale':muscle,'joint_scale':joint,'traction_scale':traction,
            'strength':p.athlete.strength,'explosive_power':p.athlete.explosive_power,'stance_fraction':stance,
            'initial_speed_m_s':initial_speed,'elapsed_s':round(steps*dt,6),
            'final_speed_m_s':round(norm(s.velocity),6),'x_m':round(s.position[0],6),'y_m':round(s.position[1],6),
            'peak_muscle_demand_N':round(peaks['demand'],3),'peak_joint_force_N':round(peaks['joint'],3),
            'peak_ground_force_N':round(peaks['ground'],3),
            'muscle_steps':counts['muscle'],'joint_steps':counts['joint'],'traction_steps':counts['traction'],
            'unconstrained_steps':counts['unconstrained'],'grounded':s.grounded}


def sensitivity(p, action='brake', baseline=None, variations=None):
    """One-factor-at-a-time outcomes plus finite-difference effect sizes.

    A zero effect is explicitly reported as masked, not as absence of ability.
    """
    baseline=dict(baseline or {})
    variations=variations or {'muscle':(.25,.5,1.,2.),'joint':(.25,.5,1.,2.),
                              'traction':(.25,.5,1.,2.),'strength':(.2,.5,.8,1.),
                              'explosive':(.2,.5,.8,1.),'stance':(.18,.32,.5)}
    base=trial(p,action,**baseline)
    rows=[]
    for axis,values in variations.items():
        for value in values:
            kwargs={**baseline,axis:value}
            outcome=trial(p,action,**kwargs)
            outcome.update(sweep_axis=axis,sweep_value=value,
                           delta_final_speed_m_s=round(outcome['final_speed_m_s']-base['final_speed_m_s'],6),
                           baseline_final_speed_m_s=base['final_speed_m_s'])
            rows.append(outcome)
    return base,rows
