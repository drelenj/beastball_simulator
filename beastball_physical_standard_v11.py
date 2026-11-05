"""Beastball Physical Standard v1.1 — exploratory athlete performance calibration.
No human limits assumed; no Pocket mutation. SI units. All ratings and force parameters provisional.
"""
from dataclasses import dataclass
from math import sqrt, hypot
from beastball_physical_standard_v1 import Athlete, Standard, MAX_SPEED

@dataclass(frozen=True)
class PerformanceProfile:
    label: str
    athlete: Athlete
    speed_fraction: float
    power: float
    coordination: float
    grip_skill: float
    def __post_init__(self):
        if not (0 < self.speed_fraction <= 1): raise ValueError('speed fraction outside (0,1]')
        for x in (self.power,self.coordination,self.grip_skill):
            if not 0 <= x <= 1: raise ValueError('rating outside [0,1]')

@dataclass(frozen=True)
class Dynamics:
    standard: Standard = Standard()
    max_hand_speed_m_s: float = 25.
    hand_acceleration_m_s2: float = 100.
    hand_stroke_m: float = 0.65
    hand_technique_floor: float = .55
    grip_technique_floor: float = .5
    def top_speed(self,p):return min(MAX_SPEED,MAX_SPEED*p.speed_fraction)
    def drive_accel(self,p):
        a=p.athlete
        return min(self.standard.max_horizontal_acceleration_m_s2(a),
                   self.standard.peak_acceleration_m_s2*self.standard.ability(p.power))
    def braking(self,p):return self.standard.max_horizontal_braking_m_s2(p.athlete)
    def sprint(self,p,seconds,dt=.005):
        if seconds<0 or dt<=0:raise ValueError('invalid time')
        t=v=x=0.
        while t<seconds-1e-12:
            h=min(dt,seconds-t);a=self.drive_accel(p);limit=self.top_speed(p)
            nv=min(limit,v+a*h)
            moving=min(h,max(0.,(limit-v)/a))
            x+=v*moving+.5*a*moving*moving+limit*(h-moving);v=nv;t+=h
        return {'time_s':seconds,'distance_m':x,'speed_m_s':v}
    def time_to_speed(self,p,target):
        if target<0:raise ValueError('invalid target')
        if target>self.top_speed(p)+1e-9:return None
        return target/self.drive_accel(p)
    def brake_distance(self,p,speed):
        if speed<0 or speed>self.top_speed(p)+1e-9:raise ValueError('speed outside capability')
        return speed*speed/(2*self.braking(p))
    def min_turn_radius(self,p,speed):
        if speed<0 or speed>self.top_speed(p)+1e-9:raise ValueError('speed outside capability')
        # v^2/r <= traction limit / mass; simplified planar limit (no bank, no lateral drag)
        lateral=self.standard.traction_limit_N(p.athlete)/p.athlete.mass_kg
        return speed*speed/lateral
    def combined_accel_budget(self,p,forward_accel,lateral_accel):
        # Circular traction envelope, not independent forward/sideways allowances.
        traction=self.standard.traction_limit_N(p.athlete)/p.athlete.mass_kg
        return hypot(forward_accel,lateral_accel)<=traction+1e-9
    def hand_contact_speed(self,p,travel_m=None):
        # Starts at rest, accelerates over available stroke; no instant velocity assignment.
        d=self.hand_stroke_m if travel_m is None else travel_m
        if d<0:raise ValueError('negative travel')
        v=min(self.max_hand_speed_m_s*self.standard.ability(p.power),
              sqrt(2*self.hand_acceleration_m_s2*self.standard.ability(p.power)*d))
        return v*(self.hand_technique_floor+(1-self.hand_technique_floor)*p.coordination)
    def punch_impulse(self,p,closing_speed=None):
        speed=self.hand_contact_speed(p) if closing_speed is None else closing_speed
        if speed<0:raise ValueError('negative closing speed')
        return self.standard.ball_impulse_N_s(p.athlete,speed)
    def grip_force(self,p):
        return self.standard.grip_force_N(p.athlete)*(self.grip_technique_floor+(1-self.grip_technique_floor)*p.grip_skill)

TIERS={
 'developing':dict(strength=.45,explosive_power=.45,traction=.55,technique=.45,speed_fraction=.54,power=.45,coordination=.45,grip_skill=.45),
 'average':dict(strength=.70,explosive_power=.70,traction=.70,technique=.70,speed_fraction=.70,power=.70,coordination=.70,grip_skill=.70),
 'exceptional':dict(strength=.92,explosive_power=.92,traction=.90,technique=.92,speed_fraction=.92,power=.92,coordination=.92,grip_skill=.92),
}
def profile(tier,role='field'):
    if tier not in TIERS or role not in ('field','keeper'):raise ValueError('unknown profile')
    d=TIERS[tier];height,mass=(2.54,180.) if role=='field' else (3.2004,300.)
    a=Athlete(height,mass,**{k:d[k] for k in ('strength','explosive_power','traction','technique')})
    return PerformanceProfile(role+'_'+tier,a,d['speed_fraction'],d['power'],d['coordination'],d['grip_skill'])
