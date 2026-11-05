"""Beastball Anatomy v0.4 — force-bearing grips and held-ball retention.

Experimental 2.5D force/impulse adapter layered on v0.3. SI units.
This does not mutate Pocket's possession, movement or tackle authority.
A ball grip is distinct from a body grip; a strip is sustained relative
traction, not an automatic call to Pocket's native strip().
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import beastball_anatomy as anatomy
import beastball_anatomy_v03 as v3

Vec = tuple[float,float,float]

@dataclass(frozen=True)
class GripConfig:
    max_force: float = 950.0       # N, effective hand traction cap
    stiffness: float = 2800.0      # N/m, soft attachment
    damping: float = 110.0         # N s/m
    rupture_force: float = 1200.0  # N, anatomical hold threshold
    reach_slack: float = .12       # m beyond contact radius
    slip_distance: float = .32     # m accumulated relative ball travel to strip
    ball_retention_force: float = 500.0 # N, effective retention at reference security
    retention_impulse: float = 18.0 # N s, sustained traction threshold
    max_dt: float = .05

@dataclass
class ForceGrip:
    defender: str
    hand: str
    target: str
    target_part: str
    kind: str  # 'body' or 'ball'
    anchor: Vec
    age: float = 0.
    traction_impulse: float = 0.
    slip: float = 0.
    last_target: Vec | None = None

@dataclass(frozen=True)
class GripEvent:
    time: float
    defender: str
    hand: str
    target: str
    kind: str
    outcome: str
    force: float
    impulse: float
    slip: float
    retention: float
    note: str = ''

class GripWorld(v3.ForceWorld):
    def __init__(self, *, grip_config: GripConfig | None = None, **kwargs):
        super().__init__(**kwargs)
        self.grip_config = grip_config or GripConfig()
        self.force_grips: dict[tuple[str,str], ForceGrip] = {}
        self.grip_events: list[GripEvent] = []
        self._validate_config()

    def _validate_config(self):
        c=self.grip_config
        if min(c.max_force,c.stiffness,c.rupture_force,c.ball_retention_force,c.retention_impulse,c.slip_distance,c.max_dt)<=0 or c.damping<0 or c.reach_slack<0:
            raise ValueError('invalid grip configuration')

    def _point(self, target: str, part: str) -> Vec:
        b=self.body(target)
        if part=='ball':
            if b.ball_center is None: raise ValueError('target has no held ball')
            return b.ball_center
        return b.part(part).center

    def acquire(self, defender: str, hand: str, target: str, part: str = 'ball') -> bool:
        """Acquire only if the free hand is in actual contact with the target.

        No teleportation, no probabilistic acquisition, no instant strip.
        """
        if defender==target: return False
        if hand not in ('left_hand','right_hand'): raise ValueError('invalid hand')
        if defender not in self.rigs or target not in self.rigs: return False
        db=self.body(defender);tb=self.body(target)
        if not db.available(hand) or (defender,hand) in self.force_grips: return False
        if part=='ball' and tb.ball_hand is None: return False
        point=self._point(target,part)
        radius=(self.ball_parameters.radius if part=='ball' else tb.part(part).radius)
        if anatomy.dist(db.part(hand).center,point)>db.part(hand).radius+radius: return False
        db.set_action(hand,'grip')
        self.rigs[defender].motions.pop(hand,None)
        self.force_grips[(defender,hand)]=ForceGrip(defender,hand,target,part,'ball' if part=='ball' else 'body',point,last_target=point)
        return True

    def disengage(self, defender: str, hand: str, reason='released') -> GripEvent | None:
        g=self.force_grips.pop((defender,hand),None)
        if g is None:return None
        db=self.body(defender)
        if db.actions.get(hand)=='grip':db.release_hand(hand)
        ev=GripEvent(self.time,defender,hand,g.target,g.kind,reason,0.,g.traction_impulse,g.slip,0.)
        self.grip_events.append(ev)
        return ev

    def _ball_retention(self, carrier: str, *, security: float, brace: float, grip: float) -> float:
        if min(security,brace,grip)<=0: raise ValueError('retention multipliers must be positive')
        b=self.body(carrier)
        return self.grip_config.ball_retention_force*self.ball_parameters.pose_factor[b.ball_pose]*security*brace*grip

    def pull(self, defender: str, hand: str, *, direction: Vec, effort: float, dt: float,
             defender_strength: float = .7, technique: float = .7,
             carrier_security: float = 1., carrier_brace: float = 1., carrier_grip: float = 1.,
             target_velocity: Vec = (0.,0.,0.)) -> GripEvent:
        """Apply an instructed pulling force for one physics substep.

        direction is the prescribed pull vector (perfect decision). Effort,
        technique, grip mechanics and carrier resistance determine execution.
        Slip accumulates only from traction exceeding retention, while impulse
        accumulates over time; both conditions must be met for dislodgement.
        """
        c=self.grip_config
        if not 0<dt<=c.max_dt+1e-12: raise ValueError('dt outside grip substep range')
        if not all(math.isfinite(v) for v in (*direction,*target_velocity,effort,defender_strength,technique)):
            raise ValueError('non-finite input')
        if not 0<=effort<=1 or not 0<=defender_strength<=1 or not 0<=technique<=1:
            raise ValueError('rating or effort outside [0,1]')
        g=self.force_grips.get((defender,hand))
        if g is None:raise ValueError('no active force grip')
        target=self.body(g.target)
        if g.kind=='ball' and target.ball_hand is None:
            self.disengage(defender,hand,'ball_no_longer_held')
            return GripEvent(self.time,defender,hand,g.target,g.kind,'ball_no_longer_held',0.,g.traction_impulse,g.slip,0.)
        point=self._point(g.target,g.target_part)
        hp=self.body(defender).part(hand).center
        gap=anatomy.dist(hp,point)
        radius=self.body(defender).part(hand).radius+(self.ball_parameters.radius if g.kind=='ball' else target.part(g.target_part).radius)
        if gap>radius+c.reach_slack:
            ev=self.disengage(defender,hand,'separation_break')
            return ev
        magnitude=v3.norm(direction)
        unit=v3.mul(direction,1/magnitude) if magnitude>1e-9 else (0.,0.,0.)
        # Effective force is bounded by hand strength/technique and attachment compliance.
        desired=c.max_force*effort*(.25+.75*defender_strength)*(.3+.7*technique)
        extension=max(0.,gap-radius)
        compliance=max(0.,1.-extension/max(c.reach_slack,1e-9))
        # Target motion opposing the pull reduces the force transferred to the ball.
        opposing=max(0.,v3.dot(target_velocity,unit))
        force=desired*compliance-c.damping*opposing
        force=max(0.,force)
        g.age+=dt
        retention=self._ball_retention(g.target,security=carrier_security,brace=carrier_brace,grip=carrier_grip) if g.kind=='ball' else c.rupture_force
        if g.kind=='body':
            # Body grips exert force but do not ground players in this adapter.
            if force>c.rupture_force:
                self.disengage(defender,hand,'force_break')
                outcome='force_break'
            else:outcome='holding'
        else:
            surplus=max(0.,force-retention)
            g.traction_impulse+=surplus*dt
            # Compliance-driven relative travel; intentionally bounded per step.
            g.slip+=min(.08,surplus/max(c.stiffness,1.)*dt*5.)
            if g.traction_impulse>=c.retention_impulse and g.slip>=c.slip_distance:
                ball_point=target.ball_center
                initial_velocity=v3.add(target_velocity,v3.mul(unit,force*dt/self.ball_parameters.mass))
                self.free_balls.append(v3.FreeBall(ball_point,initial_velocity,g.target))
                target.release_hand(target.ball_hand)
                self._last_ball.pop(g.target,None)
                self.disengage(defender,hand,'dislodged')
                outcome='dislodged'
            else:outcome='retained'
        ev=GripEvent(self.time,defender,hand,g.target,g.kind,outcome,force,g.traction_impulse,g.slip,retention)
        self.grip_events.append(ev)
        return ev

    def step(self,dt,*,sync_players=None,strike_parameters=None,security=None):
        events=super().step(dt,sync_players=sync_players,strike_parameters=strike_parameters,security=security)
        # No autonomous decisions or pulling; controller calls pull explicitly.
        for (pid,hand),g in list(self.force_grips.items()):
            try:point=self._point(g.target,g.target_part)
            except ValueError:
                self.disengage(pid,hand,'ball_no_longer_held');continue
            radius=self.body(pid).part(hand).radius+(self.ball_parameters.radius if g.kind=='ball' else self.body(g.target).part(g.target_part).radius)
            if anatomy.dist(self.body(pid).part(hand).center,point)>radius+self.grip_config.reach_slack:
                self.disengage(pid,hand,'separation_break')
        return events
