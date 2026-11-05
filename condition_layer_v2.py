"""Condition layer v2: persistent WEAR.  A second float-control valve, one per anatomy part, on top of the fatigue valve.
  Fatigue valve (v3.7):  intensity = speed / acceleration     -> short-term reserve, recovers in a minute.
  Wear valve (this):     intensity = CONTACT and USAGE per part -> long-term durability reserve W_p in [0,1], recovers over days.
    usage   : legs/feet = speed / rested top speed;  torso = presence in play (0.25);  carrying hand/arm = 0.35;  gripping hand/arm = grip force / cap
    contact : torso = collision shock;  upper hold on him = arms;  lower hold on him = legs, feet;  grip force on a holder = his hands, arms
    I_p = min(1, max(usage_p, contact_p) * sens(durability));   dW/dt = valve_rate(I_p, drain, rec)   (+rec at 0, 0 at 0.5, -drain at 1)
  DURABILITY rating (0..1; was called 'Injury' in v2.0) plays the role Stamina plays in the fatigue valve: higher = lower sensitivity, slower drain, faster recovery, faster healing.
  Effects of wear: injury thresholds fall (wear_tf) and strain accumulates faster (wear_amp) in proportion to how worn the part is.
  Persistence: rest(seconds, bench=False) recovers wear and fatigue, decays strain and HEALS damage; to_dict/from_dict carry state across plays and games.
  INJURY rating (new, in condition_layer_v1): regulates the injury THRESHOLDS (where each load kind starts to hurt); some kinds are deterministic (strain overflow), some stochastic (event hazard).
  Availability: status() -> active / limited / out from worst damage and worst wear.
ALL CONSTANTS PROVISIONAL (design dials): EXH_S, REC_FULL_S, HEAL_*, WEAR_AMP, status thresholds.
"""
import math
import condition_layer_v1 as cl
import beastball_locomotion_v37 as v37
PARTS = cl.PARTS
EXH_S = 1200.          # seconds of full-intensity contact/usage to empty a part's wear at the reference durability rating (20 min)
REC_FULL_S = 14 * 86400.  # empty -> full at the maximum recovery rate, reference durability rating (14 days; lore: rapid recovery)
BENCH_FACTOR = 1.5     # sideline rest rate vs the durability-1.0 maximum recovery
REF = .7; SENS_SLOPE = 1. / 3.
HEAL_DAYS_PER_STEP = 1.   # one 0.25 damage step heals in this many days of rest at the reference durability rating (needs the part's wear above 0.3)
STRAIN_TAU_S = 3 * 86400.
WEAR_AMP, WEAR_TF = 1., .25
USAGE_TORSO, USAGE_CARRY = .25, .35
def ability(r): return (.4 + .6 * r) / (.4 + .6 * REF)
def wear_terms(durability):
    sens = 1. - SENS_SLOPE * (durability - REF)
    drain = REF / max(durability, .05) / EXH_S
    rec = ability(durability) / REC_FULL_S
    return sens, drain, rec
class Condition2(cl.Condition):
    def __init__(self, pid, rating=.8, stamina=.7, role='field', reserve=1., durability=.7, wear=None, injury=cl.INJ_REF, seed=None, modes=None):
        super().__init__(pid, rating, stamina, role, reserve, injury, seed, modes)
        self.durability = durability; self.wsens, self.wdrain, self.wrec = wear_terms(durability)
        self.wear = {p: 1. for p in PARTS}
        if wear: self.wear.update(wear)
        self._contact = {p: 0. for p in PARTS}; self.carrying = None; self.gripping = {}
    # ---- hooks into the strain model ------------------------------------------------------------------------------------------------
    def wear_tf(self):
        w = min(self.wear[p] for p in ('left_leg', 'right_leg', 'left_foot', 'right_foot'))
        return 1. - WEAR_TF * (1. - w)
    def wear_amp(self, part): return 1. + WEAR_AMP * (1. - self.wear[part])
    # ---- contact and usage ------------------------------------------------------------------------------------------------------------
    def hit(self, shock, region=None, dt=0.):
        super().hit(shock, region, dt)
        c = min(1., max(0., shock)); self._contact['torso'] = max(self._contact['torso'], c)
        if region == 'upper':
            for s in ('left', 'right'): self._contact[s + '_arm'] = max(self._contact[s + '_arm'], c)
        if region == 'lower':
            for s in ('left', 'right'):
                for k in ('_leg', '_foot'): self._contact[s + k] = max(self._contact[s + k], c)
    def grip_load(self, force_N, dt, grip_cap=950.):
        super().grip_load(force_N, dt, grip_cap)
        c = min(1., force_N / grip_cap)
        for s in ('left', 'right'):
            for k in ('_hand', '_arm'): self._contact[s + k] = max(self._contact[s + k], c)
    def step(self, dt, p, agility=None, carrying=False):
        I = super().step(dt, p, agility)
        u = min(1., math.hypot(p.vx, p.vy) / self.rested['top'])
        for part in PARTS:
            use = u if ('leg' in part or 'foot' in part) else (USAGE_CARRY if carrying and ('hand' in part or 'arm' in part) else (USAGE_TORSO if part == 'torso' else 0.))
            Iw = min(1., max(use, self._contact[part]) * self.wsens)
            self.wear[part] = min(1., max(0., self.wear[part] + v37.valve_rate(Iw, self.wdrain, self.wrec, .5) * dt))
            self._contact[part] = 0.
        return I
    # ---- persistence ------------------------------------------------------------------------------------------------------------------
    def rest(self, seconds, bench=False):
        """time out of play. bench=True: sideline rest between plays (flat bench recovery for wear and fatigue, no healing worth modelling);
        bench=False: off-field rest (days): wear recovers at the athlete's rate, fatigue is full, strain decays, damage heals."""
        if seconds <= 0: return
        if bench:
            _, _, rec_max = wear_terms(1.)
            for p in PARTS: self.wear[p] = min(1., self.wear[p] + BENCH_FACTOR * rec_max * seconds)
            self.reserve = min(1., self.reserve + v37.bench_rate(self.stamina) * seconds)
            return
        for p in PARTS:
            self.wear[p] = min(1., self.wear[p] + self.wrec * seconds)
            self.strain[p] *= math.exp(-seconds / STRAIN_TAU_S)
            if self.damage[p] > 0 and self.wear[p] > .3:
                self.damage[p] = max(0., self.damage[p] - .25 / (HEAL_DAYS_PER_STEP * 86400.) * ability(self.durability) * seconds)
        self.reserve = 1.; self.prev = None
    def status(self):
        d = max(self.damage.values()); w = min(self.wear.values())
        if d >= .75 or w <= .05: return 'out'
        if d >= .4 or w <= .2: return 'limited'
        return 'active'
    def to_dict(self):
        return dict(v=3, pid=self.pid, rating=self.rating, stamina=self.stamina, durability=self.durability, injury=self.injury, reserve=self.reserve, role=self.role, wear=dict(self.wear),
                    damage=dict(self.damage), strain=dict(self.strain), cause=dict(self.cause), modes=dict(self.modes), rng=list(self.rng.getstate()[1]) + [self.rng.getstate()[2]])
    @classmethod
    def from_dict(cls, d):
        if d.get('v', 2) < 3: d = dict(d, durability=d['injury'], injury=cl.INJ_REF)       # v2 files called the wear rating 'injury'
        c = cls(d['pid'], d['rating'], d['stamina'], d['role'], d['reserve'], d['durability'], d['wear'], d['injury'], None, d.get('modes'))
        c.damage.update(d['damage']); c.strain.update(d['strain']); c.cause.update(d['cause'])
        if 'rng' in d: c.rng.setstate((3, tuple(d['rng'][:-1]), d['rng'][-1]))
        return c
