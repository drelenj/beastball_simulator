"""Beastball v1.7: load transfer and single-pass muscle -> contact force allocation.
Reduced-order 2D model; exploratory, not a full articulated multibody solver.
"""
from dataclasses import dataclass, replace
from math import sin
from beastball_physical_standard_v16 import World as V16World, Body as V16Body, Parameters as V16Parameters
from beastball_physical_standard_v15 import World as V15World
from beastball_physical_standard_v12 import add,sub,mul,norm,clampvec,dot

@dataclass(frozen=True)
class Body(V16Body):
    center_of_pressure_m: tuple=(0.,0.)
    left_load_fraction: float=0.5
    right_load_fraction: float=0.5
    muscle_demand_N: tuple=(0.,0.)
    muscle_applied_N: tuple=(0.,0.)

@dataclass(frozen=True)
class Parameters(V16Parameters):
    load_transfer_gain:float=0.65
    load_transfer_limit:float=0.90
    load_response_s:float=0.06
    drive_force_N_per_kg:float=35.
    brake_force_N_per_kg:float=40.
    def __post_init__(self):
        super().__post_init__()
        if not 0<=self.load_transfer_gain<=2 or not .5<=self.load_transfer_limit<=1 or self.load_response_s<=0 or min(self.drive_force_N_per_kg,self.brake_force_N_per_kg)<=0:
            raise ValueError('invalid force allocation parameters')

class World(V16World):
    def __init__(self,dynamics=None,parameters=None):super().__init__(dynamics,parameters or Parameters())
    def setup(self,p,stance_fraction=.32,position=(0.,0.),velocity=(0.,0.),recovery_enabled=True):
        s=super().setup(p,stance_fraction,position,velocity,recovery_enabled)
        return Body(**s.__dict__)
    def muscle_force_cap(self,p,braking=False):
        a=p.athlete;ability=self.d.standard.ability
        if braking:
            factor=self.c.brake_explosive_fraction*ability(a.explosive_power)+(1-self.c.brake_explosive_fraction)*ability(a.strength)
            return a.mass_kg*self.c.brake_force_N_per_kg*factor
        return min(self.d.standard.push_force_N(a),a.mass_kg*self.c.drive_force_N_per_kg*ability(a.explosive_power))
    def allocate_ground_reaction(self,p,s,requested,dt):
        if dt<=0:raise ValueError('dt must be positive')
        names=('left_foot','right_foot')
        active=[k for k in names if (getattr(s,k).phase=='stance' and getattr(s,k).planted and getattr(s,k).height_m<=1e-9)]
        mass=p.athlete.mass_kg;normal_total=mass*self.d.standard.gravity_m_s2*self.c.max_normal_load_fraction
        mu=self.d.standard.traction_coefficient*self.d.standard.ability(p.athlete.traction)*self.c.ground_friction_multiplier
        # Dynamic load target: acceleration-demand-induced center of pressure shift,
        # with a finite response rate; +x demand loads the foot farther +x.
        if len(active)==2:
            left=s.left_foot;right=s.right_foot
            span=right.x-left.x
            if abs(span)>1e-8:
                mid=(right.x+left.x)*.5
                com_x=s.position[0]+.53*p.athlete.height_m*sin(s.lean)
                demand_shift=self.c.load_transfer_gain*(requested[0]/max(normal_total,1e-9))*abs(span)*.5
                desired_cop=max(min(com_x+demand_shift,max(left.x,right.x)),min(left.x,right.x))
                desired_right=(desired_cop-left.x)/span
            else:desired_right=.5
            desired_right=max(1-self.c.load_transfer_limit,min(self.c.load_transfer_limit,desired_right))
            alpha=min(1.,dt/self.c.load_response_s)
            right_frac=s.right_load_fraction+(desired_right-s.right_load_fraction)*alpha
            right_frac=max(1-self.c.load_transfer_limit,min(self.c.load_transfer_limit,right_frac))
            fractions={'left_foot':1-right_frac,'right_foot':right_frac}
        elif len(active)==1:
            fractions={active[0]:1.}
        else:fractions={}
        # Allocate shear proportional to vertical loading. This avoids an arbitrary
        # half-and-half load assumption and obeys each planted foot's friction circle.
        applied=(0.,0.);updates={};slip_total=0.
        for k in names:
            f=getattr(s,k)
            if k not in fractions:
                updates[k]=replace(f,normal_N=0.,shear_N=(0.,0.),slipping=False)
                continue
            fraction=fractions[k];normal=normal_total*fraction
            demand=mul(requested,fraction)
            shear=clampvec(demand,mu*normal)
            shortfall=sub(demand,shear);shortnorm=norm(shortfall)
            slip=self.c.slip_compliance_m_per_N_s*shortnorm*dt
            direction=mul(shortfall,1/shortnorm) if shortnorm>1e-12 else (0.,0.)
            updates[k]=replace(f,normal_N=normal,shear_N=shear,slipping=shortnorm>1e-8,
                               x=f.x+direction[0]*slip,y=f.y+direction[1]*slip,slip_m=f.slip_m+slip)
            applied=add(applied,shear);slip_total+=slip
        left_frac=fractions.get('left_foot',0.);right_frac=fractions.get('right_foot',0.)
        cop=tuple(sum(getattr(s,k).__dict__[axis]*fractions.get(k,0.) for k in active) for axis in ('x','y')) if active else s.center_of_pressure_m
        return replace(s,**updates,left_load_fraction=left_frac,right_load_fraction=right_frac,
                       center_of_pressure_m=cop,ground_reaction_N=applied,
                       requested_ground_reaction_N=requested,unmet_ground_force_N=sub(requested,applied)),applied
    def _step(self,p,s,target,dt,external_force,contact_torque):
        if s.grounded:return s
        m=p.athlete.mass_kg;target=clampvec(target,self.d.top_speed(p));dv=sub(target,s.velocity)
        moving=s.velocity if norm(s.velocity)>1e-9 else dv
        braking=norm(moving)>1e-9 and dot(dv,moving)<0
        muscle_cap=self.muscle_force_cap(p,braking)
        requested=clampvec(mul(dv,m/dt),muscle_cap) if norm(dv)>1e-10 else (0.,0.)
        # Inherited v1.5 advances foot timing and angular motion, with no intentional
        # locomotion request. Contact traction is imposed exactly once, below.
        base=V15World._step(self,p,s,s.velocity,dt,external_force,contact_torque)
        if base.grounded:return replace(base,muscle_demand_N=requested)
        base,applied=self.allocate_ground_reaction(p,base,requested,dt)
        dv_ground=mul(applied,dt/m)
        velocity=clampvec(add(base.velocity,dv_ground),self.d.standard.max_speed_m_s)
        position=add(base.position,mul(dv_ground,dt*.5))
        interval=self.support_interval(base)
        proj=position[0]+.53*p.athlete.height_m*sin(base.lean)
        supported=interval is not None and interval[0]<=proj<=interval[1]
        grounded=not supported and abs(base.lean)>=self.c.max_lean_rad
        return replace(base,velocity=velocity,position=position,grounded=grounded,
                       muscle_demand_N=requested,muscle_applied_N=applied,
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
    peak_force=peak_unmet=peak_asymmetry=0.;slip=0.
    for _ in range(round(duration/dt)):
        s=w.step(p,s,target,dt)
        peak_force=max(peak_force,norm(s.ground_reaction_N));peak_unmet=max(peak_unmet,norm(s.unmet_ground_force_N))
        peak_asymmetry=max(peak_asymmetry,abs(s.left_load_fraction-s.right_load_fraction))
        slip=s.left_foot.slip_m+s.right_foot.slip_m
        if s.grounded:break
    return dict(profile=p.label,scenario=scenario,traction=traction,x_m=round(s.position[0],4),y_m=round(s.position[1],4),
                final_speed_m_s=round(norm(s.velocity),4),peak_ground_N=round(peak_force,2),
                peak_unmet_N=round(peak_unmet,2),peak_load_asymmetry=round(peak_asymmetry,4),
                total_slip_m=round(slip,5),grounded=s.grounded)
