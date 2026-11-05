"""Beastball v1.8: reduced-order ankle/knee/hip torque, force-velocity and stance.

No rigid-body inverse dynamics: joint loads are explicitly approximated lever arms.
SI units; all constants provisional. Builds on v1.7 single-pass traction.
"""
from dataclasses import dataclass, replace
from math import hypot, isfinite
from beastball_physical_standard_v17 import World as V17World, Body as V17Body, Parameters as V17Parameters
from beastball_physical_standard_v12 import add, sub, mul, norm, clampvec

@dataclass(frozen=True)
class Parameters(V17Parameters):
    ankle_torque_Nm_per_kg: float = 13.
    knee_torque_Nm_per_kg: float = 24.
    hip_torque_Nm_per_kg: float = 36.
    # Torque falls with shortening rate; eccentric/braking retains more force.
    concentric_velocity_sensitivity: float = .35
    eccentric_velocity_sensitivity: float = .12
    joint_reference_speed_m_s: float = 20.
    stance_leverage_gain: float = .30
    joint_technique_floor: float = .70
    def __post_init__(self):
        super().__post_init__()
        vals=(self.ankle_torque_Nm_per_kg,self.knee_torque_Nm_per_kg,self.hip_torque_Nm_per_kg,self.joint_reference_speed_m_s)
        if any(not isfinite(x) or x<=0 for x in vals):raise ValueError('invalid joint parameters')
        if not 0<=self.concentric_velocity_sensitivity<=1 or not 0<=self.eccentric_velocity_sensitivity<=1 or not 0<=self.stance_leverage_gain<=2 or not 0<self.joint_technique_floor<=1:
            raise ValueError('invalid joint modifiers')

@dataclass(frozen=True)
class Body(V17Body):
    joint_limited_force_N: tuple=(0.,0.)
    ankle_utilization: float=0.
    knee_utilization: float=0.
    hip_utilization: float=0.
    joint_bottleneck: str='none'
    force_velocity_factor: float=1.

class World(V17World):
    def __init__(self,dynamics=None,parameters=None):super().__init__(dynamics,parameters or Parameters())
    def setup(self,p,stance_fraction=.32,position=(0.,0.),velocity=(0.,0.),recovery_enabled=True):
        s=super().setup(p,stance_fraction,position,velocity,recovery_enabled)
        return Body(**s.__dict__)
    def force_velocity_factor(self,s,requested,braking):
        if norm(requested)<1e-12:return 1.
        # Movement of COM relative to force direction, not arbitrary requested speed.
        directional_speed=abs((s.velocity[0]*requested[0]+s.velocity[1]*requested[1])/norm(requested))
        ratio=min(1.,directional_speed/self.c.joint_reference_speed_m_s)
        sensitivity=self.c.eccentric_velocity_sensitivity if braking else self.c.concentric_velocity_sensitivity
        return max(.05,1.-sensitivity*ratio)
    def joint_capacity(self,p,s,requested,braking=False):
        """Return directional whole-body joint force cap, utilization and bottleneck.

        Reduced-order bilateral effective levers, NOT measured biological torque.
        Each active leg receives load fraction from v1.7. Torque capacity is
        multiplied by Strength, technique and a force-velocity modifier.
        """
        magnitude=norm(requested)
        if magnitude<1e-12:return (0.,{'ankle':0.,'knee':0.,'hip':0.},'none',1.)
        a=p.athlete;ability=self.d.standard.ability
        factor=self.force_velocity_factor(s,requested,braking)
        skill=self.c.joint_technique_floor+(1-self.c.joint_technique_floor)*ability(a.technique)
        # Leg geometry scales with height; stance geometry affects mechanical advantage.
        active=[(k,getattr(s,k)) for k in ('left_foot','right_foot') if getattr(s,k).phase=='stance' and getattr(s,k).planted and getattr(s,k).height_m<=1e-9]
        if not active:return (0.,{'ankle':0.,'knee':0.,'hip':0.},'no_contact',factor)
        # Load fractions are inherited from the prior step, normalized over planted feet.
        raw=[max(0.,s.left_load_fraction if k=='left_foot' else s.right_load_fraction) for k,_ in active]
        total=sum(raw);weights=[r/total for r in raw] if total>0 else [1/len(active)]*len(active)
        stance_span=hypot(s.right_foot.x-s.left_foot.x,s.right_foot.y-s.left_foot.y)
        stance_ratio=stance_span/max(a.height_m,.01)
        stance_factor=max(.65,min(1.35,1+self.c.stance_leverage_gain*(stance_ratio-.32)))
        # The three effective levers represent different joint demands.
        lever={'ankle':.055*a.height_m,'knee':.115*a.height_m,'hip':.19*a.height_m}
        coeff={'ankle':self.c.ankle_torque_Nm_per_kg,'knee':self.c.knee_torque_Nm_per_kg,'hip':self.c.hip_torque_Nm_per_kg}
        # Sum of each foot's capacity, with each foot's fraction influencing
        # its local torque capacity (and not magically multiplying total force).
        capacities={}
        for joint in lever:
            cap=0.
            for weight in weights:
                leg_torque=a.mass_kg*coeff[joint]*ability(a.strength)*skill*factor*stance_factor*weight
                cap+=leg_torque/lever[joint]
            capacities[joint]=cap
        bottleneck=min(capacities,key=capacities.get)
        cap=min(capacities.values())
        return cap,{j:magnitude/max(c,1e-9) for j,c in capacities.items()},bottleneck,factor
    def _step(self,p,s,target,dt,external_force,contact_torque):
        if s.grounded:return s
        if dt<=0:raise ValueError('dt must be positive')
        m=p.athlete.mass_kg;target=clampvec(target,self.d.top_speed(p))
        dv=sub(target,s.velocity)
        braking=norm(s.velocity)>1e-9 and sum(dv[i]*s.velocity[i] for i in (0,1))<0
        muscle_cap=self.muscle_force_cap(p,braking)
        demand=clampvec(mul(dv,m/dt),muscle_cap) if norm(dv)>1e-10 else (0.,0.)
        joint_cap,util,bottleneck,factor=self.joint_capacity(p,s,demand,braking)
        constrained=clampvec(demand,joint_cap)
        # Advance v1.5 foot and rotation only, then apply one force pipeline:
        # muscle -> joint torque -> ground traction -> COM acceleration.
        from beastball_physical_standard_v15 import World as V15World
        base=V15World._step(self,p,s,s.velocity,dt,external_force,contact_torque)
        if base.grounded:return replace(base,muscle_demand_N=demand,joint_limited_force_N=constrained,joint_bottleneck=bottleneck)
        base,applied=self.allocate_ground_reaction(p,base,constrained,dt)
        delta=mul(applied,dt/m)
        velocity=clampvec(add(base.velocity,delta),self.d.standard.max_speed_m_s)
        position=add(base.position,mul(delta,dt*.5))
        interval=self.support_interval(base)
        from math import sin
        proj=position[0]+.53*p.athlete.height_m*sin(base.lean)
        supported=interval is not None and interval[0]<=proj<=interval[1]
        grounded=not supported and abs(base.lean)>=self.c.max_lean_rad
        return replace(base,velocity=velocity,position=position,grounded=grounded,
                       muscle_demand_N=demand,muscle_applied_N=applied,joint_limited_force_N=constrained,
                       ankle_utilization=util['ankle'],knee_utilization=util['knee'],hip_utilization=util['hip'],
                       joint_bottleneck=bottleneck,force_velocity_factor=factor,
                       unsupported_s=0. if supported else s.unsupported_s+dt)

def run_trial(p,scenario,traction=1.,dt=.005):
    w=World(parameters=Parameters(ground_friction_multiplier=traction))
    s=w.setup(p,recovery_enabled=False)
    if scenario=='brake':s=replace(s,velocity=(20.,0.));target=(0.,0.);duration=1.5
    elif scenario=='cut':s=replace(s,velocity=(20.,0.));target=(0.,20.);duration=1.5
    elif scenario=='sprint':target=(w.d.top_speed(p),0.);duration=2.
    elif scenario=='one_foot_brake':
        s=replace(s,velocity=(20.,0.),left_foot=replace(s.left_foot,phase='swing',planted=False,height_m=.1));target=(0.,0.);duration=.5
    else:raise ValueError(scenario)
    peak_ground=peak_joint=peak_util=0.;bottlenecks={}
    for _ in range(round(duration/dt)):
        s=w.step(p,s,target,dt)
        peak_ground=max(peak_ground,norm(s.ground_reaction_N))
        peak_joint=max(peak_joint,norm(s.joint_limited_force_N))
        peak_util=max(peak_util,s.ankle_utilization,s.knee_utilization,s.hip_utilization)
        bottlenecks[s.joint_bottleneck]=bottlenecks.get(s.joint_bottleneck,0)+1
        if s.grounded:break
    return dict(profile=p.label,scenario=scenario,traction=traction,x_m=round(s.position[0],4),y_m=round(s.position[1],4),
                final_speed_m_s=round(norm(s.velocity),4),peak_ground_N=round(peak_ground,2),peak_joint_demand_N=round(peak_joint,2),
                peak_joint_utilization=round(peak_util,3),dominant_joint_bottleneck=max(bottlenecks,key=bottlenecks.get),
                slip_m=round(s.left_foot.slip_m+s.right_foot.slip_m,5),grounded=s.grounded)
