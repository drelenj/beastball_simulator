"""Beastball Physical Standard v1.0: parameter model and dimensional checks.

This module does not install itself into Pocket or replace anatomy constants.
Baseline values are provisional and are NOT physiological canon.
"""
from __future__ import annotations
from dataclasses import dataclass
from math import sqrt
import json
from pathlib import Path

MPH_TO_MS = 0.44704
MAX_SPEED = 100 * MPH_TO_MS

@dataclass(frozen=True)
class Athlete:
    height_m: float
    mass_kg: float
    strength: float = 0.7
    explosive_power: float = 0.7
    technique: float = 0.7
    traction: float = 0.7

    def __post_init__(self):
        if self.height_m <= 0 or self.mass_kg <= 0:
            raise ValueError('positive height and mass required')
        if not all(0 <= v <= 1 for v in (self.strength,self.explosive_power,self.technique,self.traction)):
            raise ValueError('ratings must be in [0,1]')

@dataclass(frozen=True)
class Standard:
    max_speed_m_s: float = MAX_SPEED
    gravity_m_s2: float = 9.80665
    reference_rating: float = 0.7
    grip_force_N_per_kg: float = 10.0
    push_force_N_per_kg: float = 35.0
    hand_effective_mass_fraction: float = 0.012
    ball_mass_kg: float = 0.65
    ball_radius_m: float = 0.12
    peak_acceleration_m_s2: float = 16.0
    peak_braking_m_s2: float = 22.0
    traction_coefficient: float = 2.4

    def __post_init__(self):
        if min(self.max_speed_m_s,self.gravity_m_s2,self.grip_force_N_per_kg,self.push_force_N_per_kg,self.hand_effective_mass_fraction,self.ball_mass_kg,self.ball_radius_m,self.peak_acceleration_m_s2,self.peak_braking_m_s2,self.traction_coefficient) <= 0:
            raise ValueError('physical parameters must be positive')

    def ability(self, rating: float) -> float:
        """Reference-normalized monotonic scaling; exploratory, not final ratings map."""
        return (0.4 + 0.6 * rating) / (0.4 + 0.6 * self.reference_rating)

    def grip_force_N(self, a: Athlete) -> float:
        return a.mass_kg * self.grip_force_N_per_kg * self.ability(a.strength) * (0.5 + 0.5 * a.technique)

    def push_force_N(self, a: Athlete) -> float:
        return a.mass_kg * self.push_force_N_per_kg * self.ability(a.strength)

    def hand_effective_mass_kg(self, a: Athlete) -> float:
        return a.mass_kg * self.hand_effective_mass_fraction

    def traction_limit_N(self, a: Athlete) -> float:
        return self.traction_coefficient * a.mass_kg * self.gravity_m_s2 * self.ability(a.traction)

    def max_horizontal_acceleration_m_s2(self, a: Athlete) -> float:
        drive = self.push_force_N(a) / a.mass_kg
        traction = self.traction_limit_N(a) / a.mass_kg
        return min(self.peak_acceleration_m_s2 * self.ability(a.explosive_power), drive, traction)

    def max_horizontal_braking_m_s2(self, a: Athlete) -> float:
        return min(self.peak_braking_m_s2 * self.ability(a.traction), self.traction_limit_N(a) / a.mass_kg)

    def momentum_kg_m_s(self, a: Athlete, speed_m_s: float) -> float:
        if not 0 <= speed_m_s <= self.max_speed_m_s + 1e-9:
            raise ValueError('speed exceeds canon ceiling')
        return a.mass_kg * speed_m_s

    def kinetic_energy_J(self, a: Athlete, speed_m_s: float) -> float:
        self.momentum_kg_m_s(a, speed_m_s)
        return 0.5 * a.mass_kg * speed_m_s**2

    def braking_distance_m(self, speed_m_s: float, braking_m_s2: float) -> float:
        if speed_m_s < 0 or braking_m_s2 <= 0: raise ValueError('invalid speed/braking')
        return speed_m_s**2 / (2 * braking_m_s2)

    def impact_impulse_N_s(self, relative_normal_speed_m_s: float, effective_mass_kg: float, restitution: float) -> float:
        if min(relative_normal_speed_m_s,effective_mass_kg,restitution) < 0 or restitution > 1:
            raise ValueError('invalid collision inputs')
        return (1 + restitution) * effective_mass_kg * relative_normal_speed_m_s

    def reduced_mass_kg(self, m1: float, m2: float) -> float:
        if min(m1,m2) <= 0: raise ValueError('positive masses required')
        return m1*m2/(m1+m2)

    def ball_impulse_N_s(self, a: Athlete, closing_speed_m_s: float, restitution: float = 0.15) -> float:
        return self.impact_impulse_N_s(closing_speed_m_s,self.reduced_mass_kg(self.hand_effective_mass_kg(a),self.ball_mass_kg),restitution)

if __name__ == '__main__':
    s=Standard(); field=Athlete(2.54,180); keeper=Athlete(3.2004,300)
    print(json.dumps({'canon_max_speed_m_s':s.max_speed_m_s,'field_grip_N':s.grip_force_N(field),'keeper_grip_N':s.grip_force_N(keeper),'field_acceleration_m_s2':s.max_horizontal_acceleration_m_s2(field),'field_braking_distance_at_30m_s':s.braking_distance_m(30,s.max_horizontal_braking_m_s2(field))},indent=2))
