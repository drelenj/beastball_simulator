"""Beastball v1.6: bilateral stance ground reaction, traction saturation and slip.
Reduced-order planar contact model; not a rigid-body joint solver or Pocket integration.
"""
from dataclasses import dataclass, replace
from math import hypot
from beastball_physical_standard_v15 import World as V15World, Body as V15Body, Foot as V15Foot, Parameters as V15Parameters
from beastball_physical_standard_v12 import add, sub, mul, norm, clampvec

@dataclass(frozen=True)
class Foot(V15Foot):
    normal_N: float = 0.
    shear_N: tuple = (0.,0.)
    slipping: bool = False
    slip_m: float = 0.

@dataclass(frozen=True)
class Body(V15Body):
    left_foot: Foot = Foot(-.35,-.25)
    right_foot: Foot = Foot(.35,.25)
    ground_reaction_N: tuple = (0.,0.)
    requested_ground_reaction_N: tuple = (0.,0.)
    unmet_ground_force_N: tuple = (0.,0.)

@dataclass(frozen=True)
class Parameters(V15Parameters):
    ground_friction_multiplier: float = 1.
    slip_compliance_m_per_N_s: float = .00012
    slip_threshold_m: float = .005
    max_normal_load_fraction: float = 1.0
    def __post_init__(self):
        super().__post_init__()
        if min(self.ground_friction_multiplier,self.slip_compliance_m_per_N_s,self.slip_threshold_m,self.max_normal_load_fraction)<=0:
            raise ValueError('positive foot-force parameters required')

class World(V15World):
    def __init__(self,dynamics=None,parameters=None):super().__init__(dynamics,parameters or Parameters())
    def setup(self,p,stance_fraction=.32,position=(0.,0.),velocity=(0.,0.),recovery_enabled=True):
        s=super().setup(p,stance_fraction,position,velocity,recovery_enabled)
        return Body(**{**s.__dict__, 'left_foot':Foot(**s.left_foot.__dict__), 'right_foot':Foot(**s.right_foot.__dict__)})
    def allocate_ground_reaction(self,p,s,requested,dt):
        """Apply horizontal GRF to planted feet only. Return state and achieved vector.
        Normal load is distributed evenly; each foot uses a circular Coulomb envelope.
        Unmet demand causes slip. Simplification: no load transfer or vertical dynamics.
        """
        if dt<=0:raise ValueError('dt must be positive')
        feet=['left_foot','right_foot']
        planted=[k for k in feet if getattr(s,k).phase=='stance' and getattr(s,k).planted and getattr(s,k).height_m<=1e-9]
        m=p.athlete.mass_kg
        normal_total=m*self.d.standard.gravity_m_s2*self.c.max_normal_load_fraction
        mu=self.d.standard.traction_coefficient*self.d.standard.ability(p.athlete.traction)*self.c.ground_friction_multiplier
        normal_each=normal_total/len(planted) if planted else 0.
        per_demand=mul(requested,1./len(planted)) if planted else (0.,0.)
        per_applied=clampvec(per_demand,mu*normal_each)
        applied=mul(per_applied,len(planted))
        unmet=sub(requested,applied)
        updates={}
        for k in feet:
            f=getattr(s,k)
            if k not in planted:
                updates[k]=replace(f,normal_N=0.,shear_N=(0.,0.),slipping=False)
            else:
                shortfall=norm(sub(per_demand,per_applied))
                displacement=self.c.slip_compliance_m_per_N_s*shortfall*dt
                direction=(0.,0.) if shortfall<1e-12 else mul(sub(per_demand,per_applied),1/shortfall)
                updates[k]=replace(f,normal_N=normal_each,shear_N=per_applied,
                                   slipping=shortfall>1e-8,
                                   x=f.x+direction[0]*displacement,y=f.y+direction[1]*displacement,
                                   slip_m=f.slip_m+displacement)
        return replace(s,**updates,ground_reaction_N=applied,requested_ground_reaction_N=requested,unmet_ground_force_N=unmet),applied
    def _step(self,p,s,target,dt,external_force,contact_torque):
        if s.grounded:return s
        # v1.5 handles stance/swing timing and support recovery; this layer replaces its
        # intentional locomotion force with a two-foot friction allocation.
        m=p.athlete.mass_kg
        desired=clampvec(target,self.d.top_speed(p))
        dv=sub(desired,s.velocity)
        if norm(dv)>1e-10:
            dotprod=dv[0]*s.velocity[0]+dv[1]*s.velocity[1]
            cap=self.brake_accel(p,s) if dotprod<0 else self.d.drive_accel(p)
            demanded=mul(clampvec(mul(dv,1/dt),cap),m)
        else:demanded=(0.,0.)
        # Advance old model without applying locomotion acceleration; preserve external force,
        # angular dynamics and foot-contact timing, then integrate achieved GRF.
        base=V15World._step(self,p,s,s.velocity,dt,external_force,contact_torque)
        base=replace(base,grounded=False)
        result,applied=self.allocate_ground_reaction(p,base,demanded,dt)
        delta_v=mul(applied,dt/m)
        velocity=add(base.velocity,delta_v)
        velocity=clampvec(velocity,self.d.standard.max_speed_m_s)
        position=add(base.position,mul(delta_v,dt*.5))
        # Grounding is assessed with post-slip support. The inherited angular model
        # is provisional; no unsupported foot can contribute to force.
        from math import sin
        interval=self.support_interval(result)
        proj=position[0]+.53*p.athlete.height_m*sin(result.lean)
        supported=interval is not None and interval[0]<=proj<=interval[1]
        grounded=(not supported and abs(result.lean)>=self.c.max_lean_rad)
        return replace(result,velocity=velocity,position=position,grounded=grounded,
                       unsupported_s=0. if supported else s.unsupported_s+dt)

def run_trial(p,scenario,traction_multiplier=1.,dt=.005):
    from dataclasses import replace as r
    w=World(parameters=Parameters(ground_friction_multiplier=traction_multiplier))
    s=w.setup(p,recovery_enabled=False)
    if scenario=='brake':s=r(s,velocity=(20.,0.));target=(0.,0.);duration=1.5
    elif scenario=='cut':s=r(s,velocity=(20.,0.));target=(0.,20.);duration=1.5
    elif scenario=='sprint':target=(w.d.top_speed(p),0.);duration=2.
    elif scenario=='one_foot_brake':
        s=r(s,velocity=(20.,0.),left_foot=r(s.left_foot,phase='swing',planted=False,height_m=.1));target=(0.,0.);duration=.5
    else:raise ValueError(scenario)
    peak_reaction=peak_unmet=peak_slip=0.
    for _ in range(round(duration/dt)):
        s=w.step(p,s,target,dt)
        peak_reaction=max(peak_reaction,norm(s.ground_reaction_N))
        peak_unmet=max(peak_unmet,norm(s.unmet_ground_force_N))
        peak_slip=max(peak_slip,s.left_foot.slip_m+s.right_foot.slip_m)
        if s.grounded:break
    return dict(profile=p.label,scenario=scenario,traction_multiplier=traction_multiplier,
                x_m=round(s.position[0],4),y_m=round(s.position[1],4),speed_m_s=round(norm(s.velocity),4),
                peak_ground_N=round(peak_reaction,2),peak_unmet_N=round(peak_unmet,2),
                total_slip_m=round(peak_slip,5),grounded=s.grounded)
