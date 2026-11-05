"""Beastball v1.5: hybrid planted/swinging feet with touchdown-only support.
Reduced-order planar roll dynamics; provisional, not full rigid-body contact solver.
"""
from dataclasses import dataclass, replace
from math import sin, hypot
from beastball_physical_standard_v14 import World as V14World, Body as V14Body, Parameters as V14Parameters, Foot as V14Foot

@dataclass(frozen=True)
class Foot(V14Foot):
    phase: str = 'stance' # stance, swing
    target_x: float = 0.
    target_y: float = 0.
    swing_elapsed_s: float = 0.
    swing_duration_s: float = 0.
    height_m: float = 0.

@dataclass(frozen=True)
class Body(V14Body):
    left_foot: Foot = Foot(-.35,-.25)
    right_foot: Foot = Foot(.35,.25)
    recovery_attempts: int = 0
    unsupported_s: float = 0.

@dataclass(frozen=True)
class Parameters(V14Parameters):
    foot_lift_s: float = .055
    foot_swing_speed_m_s: float = 12.
    foot_clearance_m: float = .14
    min_touchdown_s: float = .085
    foot_contact_tolerance_m: float = .025
    recovery_trigger_rad: float = .10
    def __post_init__(self):
        super().__post_init__()
        if min(self.foot_lift_s,self.foot_swing_speed_m_s,self.foot_clearance_m,self.min_touchdown_s,self.foot_contact_tolerance_m)<=0:
            raise ValueError('foot-contact parameters must be positive')

class World(V14World):
    def __init__(self,dynamics=None,parameters=None):super().__init__(dynamics,parameters or Parameters())
    def setup(self,p,stance_fraction=.32,position=(0.,0.),velocity=(0.,0.),recovery_enabled=True):
        s=super().setup(p,stance_fraction,position,velocity,recovery_enabled)
        return Body(**{**s.__dict__, 'left_foot':Foot(s.left_foot.x,s.left_foot.y,target_x=s.left_foot.x,target_y=s.left_foot.y),
                       'right_foot':Foot(s.right_foot.x,s.right_foot.y,target_x=s.right_foot.x,target_y=s.right_foot.y)})
    def support_interval(self,s):
        feet=[f for f in (s.left_foot,s.right_foot) if f.phase=='stance' and f.planted and f.height_m<=1e-9]
        if not feet:return None
        r=self.c.foot_support_radius_m
        return (min(f.x for f in feet)-r,max(f.x for f in feet)+r)
    def begin_step(self,p,s,footname,direction):
        if footname not in ('left_foot','right_foot'):raise ValueError('foot name')
        f=getattr(s,footname)
        if f.phase!='stance' or f.cooldown_s>0:return s
        other=getattr(s,'left_foot' if footname=='right_foot' else 'right_foot')
        if other.phase!='stance' or not other.planted:return s # cannot swing both feet in this model
        reach=p.athlete.height_m*self.c.recovery_reach_height_fraction
        target=s.position[0]+(1. if direction>=0 else -1.)*reach
        distance=abs(target-f.x)
        duration=max(self.c.min_touchdown_s,self.c.foot_lift_s+distance/self.c.foot_swing_speed_m_s)
        moving=replace(f,phase='swing',planted=False,target_x=target,target_y=f.y,
                       swing_elapsed_s=0.,swing_duration_s=duration,height_m=0.)
        return replace(s,**{footname:moving},recovery_attempts=s.recovery_attempts+1)
    def _advance_foot(self,f,dt):
        if f.phase=='stance':return replace(f,cooldown_s=max(0.,f.cooldown_s-dt))
        elapsed=min(f.swing_duration_s,f.swing_elapsed_s+dt)
        # Swing is non-supporting throughout. A foot can touch down only after its travel completes.
        travel_time=max(1e-9,f.swing_duration_s-self.c.foot_lift_s)
        progress=max(0.,min(1.,(elapsed-self.c.foot_lift_s)/travel_time))
        # x is interpolated from prior position, with speed bound; no instant relocation.
        maxmove=self.c.foot_swing_speed_m_s*dt
        delta=f.target_x-f.x
        x=f.x+max(-maxmove,min(maxmove,delta)) if elapsed>self.c.foot_lift_s else f.x
        height=self.c.foot_clearance_m*4*progress*(1-progress) if elapsed>self.c.foot_lift_s else self.c.foot_clearance_m*elapsed/self.c.foot_lift_s
        if elapsed>=f.swing_duration_s-1e-10 and abs(f.target_x-x)<=self.c.foot_contact_tolerance_m:
            return replace(f,x=f.target_x,y=f.target_y,phase='stance',planted=True,height_m=0.,
                           swing_elapsed_s=elapsed,cooldown_s=self.c.recovery_cooldown_s)
        # Duration may expire before target if timing and speed constraints disagree: continue swing.
        if elapsed>=f.swing_duration_s-1e-10:
            return replace(f,x=x,height_m=max(.005,height),swing_elapsed_s=elapsed,
                           swing_duration_s=f.swing_duration_s+dt)
        return replace(f,x=x,height_m=height,swing_elapsed_s=elapsed)
    def _step(self,p,s,target,dt,external_force,contact_torque):
        if s.grounded:return s
        # Advance v1.3 body, without v1.4's fictitious instant support movement.
        from beastball_physical_standard_v13 import World as V13World
        # Base mechanics use planted flag for locomotion; preserve foot contact status.
        has_support=self.support_interval(s) is not None
        pre=replace(s,planted=has_support)
        n=V13World._step(self,p,pre,target,dt,external_force,contact_torque)
        lf=self._advance_foot(s.left_foot,dt)
        rf=self._advance_foot(s.right_foot,dt)
        touchdowns=int(s.left_foot.phase=='swing' and lf.phase=='stance')+int(s.right_foot.phase=='swing' and rf.phase=='stance')
        n=replace(n,grounded=False,left_foot=lf,right_foot=rf,recovery_steps=s.recovery_steps+touchdowns)
        h=.53*p.athlete.height_m
        proj=n.position[0]+h*sin(n.lean)
        interval=self.support_interval(n)
        if n.recovery_enabled and abs(n.lean)>=self.c.recovery_trigger_rad and not any(f.phase=='swing' for f in (n.left_foot,n.right_foot)):
            direction=1 if n.lean+n.lean_rate*.12>=0 else -1
            n=self.begin_step(p,n,'right_foot' if direction>0 else 'left_foot',direction)
            interval=self.support_interval(n)
        supported=interval is not None and interval[0]<=proj<=interval[1]
        if supported and n.recovery_enabled:
            ability=self.d.standard.ability(p.athlete.strength)
            desired=-self.c.recovery_neural_gain*ability*30*n.lean-self.c.recovery_damping*ability*12*n.lean_rate
            cap=self.brake_accel(p,n)/max(h,.01)
            n=replace(n,lean_rate=n.lean_rate+max(-cap,min(cap,desired))*dt)
        unsupported_s=0. if supported else n.unsupported_s+dt
        grounded=(not supported and abs(n.lean)>=self.c.max_lean_rad)
        return replace(n,unsupported_s=unsupported_s,grounded=grounded)

def run_trial(p,impulse_N_s,recovery=True,dt=.005,duration=.8,contact_height_fraction=.75):
    w=World();s=w.setup(p,recovery_enabled=recovery)
    s=w.impact(p,s,(impulse_N_s,0.),contact_height_m=p.athlete.height_m*contact_height_fraction)
    peak=abs(s.lean);airborne_steps=0
    for _ in range(round(duration/dt)):
        s=w.step(p,s,(0.,0.),dt)
        peak=max(peak,abs(s.lean))
        airborne_steps+=int(any(f.phase=='swing' for f in (s.left_foot,s.right_foot)))
        if s.grounded:break
    return dict(profile=p.label,impulse_N_s=impulse_N_s,recovery=recovery,grounded=s.grounded,
                recovery_attempts=s.recovery_attempts,touchdowns=s.recovery_steps,
                airborne_steps=airborne_steps,unsupported_s=round(s.unsupported_s,4),
                peak_lean_rad=round(peak,4),final_lean_rad=round(s.lean,4),
                left_phase=s.left_foot.phase,right_phase=s.right_foot.phase)
