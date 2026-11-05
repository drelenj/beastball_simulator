"""Condition layer v1: live reserve (v3.7 valve) + per-part strain/damage on Codex's ten anatomy parts.  PROVISIONAL constants (all flagged K_*).

Reserve: float-control valve on live intensity (v3.7), driven from measured speed and COM acceleration against the rested capabilities.
Fatigue effects: reserve -> locomotion capability (via the frozen capability lookup), tackling, strength (grip/push), ball-hand force.
Injury: deterministic strain accumulation per part (no RNG).  strain += rate*dt;  each time strain crosses 1.0 the part takes +DMG_STEP damage (cap 1).
  load drivers -> parts:
    cut / plant (lateral accel / rested lateral limit)   -> feet (ankle) and legs (knee); share set by body-part technique (agility)
    hard braking                                         -> legs (knee)
    sprint at >90 % top speed                            -> legs (hamstring)
    collision / hold shock on this athlete               -> torso;  an UPPER hold also loads the arms,  a LOWER hold loads legs and feet
    grip force from a holder                             -> his hands and arms
  fatigue amplifies every strain rate by (1 + FATIGUE_AMP*(1-reserve)); tissue capacity = 0.7 + 0.3*rating (rating stands in for conditioning).
Damage effects:
    legs/feet -> locomotion injury region+severity (foot -> 'ankle', leg -> 'knee' if from plant/braking else 'hamstring', torso -> 'general'), push scale
    arms/hands -> grip strength factor, ball-retention factor (carrier's ball hand)
    torso -> tackling/technique factor and push scale
Technique tie: body-part technique = the athlete's own rating for that load (agility for plant/cut, strength for grip, balance for collision).
"""
import math, sys, random, zlib
sys.path.insert(0, "/home/claude/next/p23/v37pkg")
import beastball_anatomy as an
import locomotion_bridge_v1 as br
import beastball_locomotion_v37 as v37
from beastball_locomotion_v33 import FatigueParams
PARTS = an.PARTS
K_PLANT, K_BRAKE, K_SPRINT, K_HIT, K_GRIP, K_HOLD = 0.9, 0.5, 0.35, 0.55, 0.5, 0.45   # strain per second at full excess  (PROVISIONAL)
FATIGUE_AMP, DMG_STEP = 2.0, 0.25
THRESH = dict(plant=.92, brake=.92, sprint=.97, hit=.85, grip=.80)     # base thresholds at the reference INJURY rating (load ratio at which strain/hazard starts)
# INJURY rating (0..1, higher = tougher): scales every threshold, th = THRESH * (1 + THR_SLOPE[kind] * (injury - INJ_REF)).  At INJ_REF the thresholds are the base values.
INJ_REF = .7
THR_SLOPE = dict(plant=.5, brake=.5, sprint=.5, hit=.5, grip=.5, hold=.5)           # per-kind slopes: the designer's handle to split Injury into per-region ratings later
# how each load kind injures:  'deterministic' = strain accumulates, damage steps when it overflows (no RNG);  'stochastic' = the same strain becomes a per-tick event probability.
# a stochastic event deals 1..3 damage steps (STOCH_SEV); the mean severity keeps the expected damage equal to the deterministic route, only the variance changes.
INJURY_MODE = dict(plant='stochastic', brake='stochastic', sprint='stochastic', hit='stochastic', grip='deterministic', hold='stochastic')   # acute = stochastic; load-accumulating (grip, holds) = deterministic
STOCH_SEV = ((1, .70), (2, .20), (3, .07), (4, .03))      # heavy-tailed: mostly minor, a few season-enders (4 steps = full damage)
BASE_HAZ = 1.7e-4      # baseline minor-injury hazard per second of movement (random leg/foot part, scaled by speed, fatigue, wear): ~0.1 per 10-minute stint at ref Injury
HAZ_SCALE = .15      # scales the threshold-driven acute hazard (the scripted season plays hit the same load every play, so this is the main knob for how often acute injuries strike)
STOCH_MEAN = sum(a * b for a, b in STOCH_SEV)
VP, FP = v37.ValveParams(), FatigueParams()
class Condition:
    def __init__(self, pid, rating=.8, stamina=.7, role='field', reserve=1., injury=INJ_REF, seed=None, modes=None):
        self.pid, self.rating, self.stamina, self.role, self.reserve = pid, rating, stamina, role, reserve
        self.injury = injury; self.modes = dict(INJURY_MODE, **(modes or {})); self.rng = random.Random(seed if seed is not None else zlib.crc32(str(pid).encode()))
        self.strain = {p: 0. for p in PARTS}; self.damage = {p: 0. for p in PARTS}; self.cause = {p: '' for p in PARTS}
        self.sens, self.drain, self.rec = v37.stamina_terms(stamina, VP, FP)
        self.rested = br.attributes(rating, 1., role)
        self.prev = None; self.log = []; self.t = 0.
    # ---- derived effects -------------------------------------------------------------------------------------------------------------
    def th(self, kind): return THRESH[kind] * (1. + THR_SLOPE.get(kind, .5) * (self.injury - INJ_REF))
    def wear_tf(self): return 1.
    def wear_amp(self, part): return 1.
    def capacity(self): return .7 + .3 * self.rating
    def _worst(self, parts):
        return max(parts, key=lambda p: self.damage[p])
    def loco_injury(self):
        legs = ('left_leg', 'right_leg', 'left_foot', 'right_foot'); w = self._worst(legs); d = self.damage[w]
        if self.damage['torso'] > d and self.damage['torso'] > 0: return 'general', self.damage['torso']
        if d <= 0: return '', 0.
        if 'foot' in w: return 'ankle', d
        return ('knee' if self.cause[w] in ('plant', 'brake') else 'hamstring'), d
    def hand_factor(self, side):   # grip strength of one hand
        return (1 - self.damage[side + '_hand']) * (1 - .5 * self.damage[side + '_arm'])
    def grip_factor(self): return max(self.hand_factor('left'), self.hand_factor('right')) * .7 + min(self.hand_factor('left'), self.hand_factor('right')) * .3
    def strength_eff(self, base): return base * (1 - FP.max_loss * (1 - self.reserve) ** FP.loss_exponent) * (.4 + .6 * self.grip_factor())
    def tackling_eff(self, base): return base * (.6 + .4 * self.reserve) * (1 - .4 * self.damage['torso']) * (.5 + .5 * self.grip_factor())
    def push_scale(self):
        legs = (self.damage['left_leg'] + self.damage['right_leg'] + self.damage['left_foot'] + self.damage['right_foot']) / 4.
        return max(.1, (1 - .8 * legs) * (1 - .3 * self.damage['torso']) * (1 - FP.max_loss * (1 - self.reserve) ** FP.loss_exponent))
    def retention_factor(self, hand='right'):   # carrier's ball-hand retention (injured hand/arm loosens it)
        return max(.2, self.hand_factor(hand))
    # ---- state update ---------------------------------------------------------------------------------------------------------------
    def _event(self, part, prob, cause):
        if self.rng.random() < min(1., prob):
            r = self.rng.random(); sev = STOCH_SEV[-1][0]; acc = 0.
            for k, w in STOCH_SEV:
                acc += w
                if r < acc: sev = k; break
            if self.damage[part] < 1.:
                self.damage[part] = min(1., self.damage[part] + sev * DMG_STEP); self.log.append((round(self.t, 1), part, cause, round(self.damage[part], 2), 'stoch'))
    def _add(self, part, amount, cause):
        if amount <= 0: return
        amt = amount * (1 + FATIGUE_AMP * (1 - self.reserve)) * self.wear_amp(part) / self.capacity()
        self.cause[part] = cause
        if self.modes.get(cause, 'deterministic') == 'stochastic':
            self._event(part, HAZ_SCALE * amt / STOCH_MEAN, cause); return
        self.strain[part] += amt
        while self.strain[part] >= 1.:
            self.strain[part] -= 1.
            if self.damage[part] < 1.:
                self.damage[part] = min(1., self.damage[part] + DMG_STEP); self.log.append((round(self.t, 1), part, cause, round(self.damage[part], 2), 'det'))
    def step(self, dt, p, agility=None):
        self.t += dt
        vx, vy = p.vx, p.vy; sp = math.hypot(vx, vy)
        top = self.rested['top']; ag = self.rating if agility is None else agility
        a_long = a_brk = a_lat = 0.
        if self.prev is not None and dt > 0:
            pvx, pvy = self.prev; psp = math.hypot(pvx, pvy)
            if psp > .5:
                ux, uy = pvx / psp, pvy / psp; dvx, dvy = (vx - pvx) / dt, (vy - pvy) / dt
                al = dvx * ux + dvy * uy; a_lat = abs(-dvx * uy + dvy * ux)
                a_long = max(0., al); a_brk = max(0., -al)
            else: a_long = math.hypot((vx - pvx) / dt, (vy - pvy) / dt)
        self.prev = (vx, vy)
        acc, brk, trn = self.rested['acceleration'], self.rested['braking'], max(self.rested['turning'], 1.)
        u = sp / top; load = max(a_long / acc, a_brk / brk, a_lat / trn); I = min(1., max(u, load) * self.sens)
        self.reserve = min(1., max(0., self.reserve + v37.valve_rate(I, self.drain, self.rec, VP.neutral) * dt))
        rl, rb, rs = a_lat / trn, a_brk / brk, u
        share_foot = max(.2, min(.8, 1.3 - .6 * ag))     # poor agility technique puts more of the plant on the ankle than the knee
        tf = (.6 + .4 * self.reserve) * self.wear_tf()      # tired tissue fails at lower load: every threshold scales down with fatigue
        if rl > self.th('plant') * tf:
            e = K_PLANT * ((rl - self.th('plant') * tf) / (1 - self.th('plant') * tf)) ** 2 * dt * min(1., u + .3)
            for s in ('left', 'right'): self._add(s + '_foot', e * share_foot * .5, 'plant'); self._add(s + '_leg', e * (1 - share_foot) * .5, 'plant')
        if rb > self.th('brake') * tf:
            e = K_BRAKE * ((rb - self.th('brake') * tf) / (1 - self.th('brake') * tf)) ** 2 * dt
            for s in ('left', 'right'): self._add(s + '_leg', e * .5, 'brake')
        if rs > self.th('sprint') * tf:
            e = K_SPRINT * ((rs - self.th('sprint') * tf) / (1 - self.th('sprint') * tf)) ** 2 * dt
            for s in ('left', 'right'): self._add(s + '_leg', e * .5, 'sprint')
        if u > .05 and BASE_HAZ > 0:      # baseline hazard: a small chance of a minor injury whenever he moves, rising with speed, fatigue and wear, falling with the Injury rating
            part = self.rng.choice(('left_leg', 'right_leg', 'left_foot', 'right_foot'))
            self._event(part, BASE_HAZ * dt * u * max(.3, 1. - 1.5 * (self.injury - INJ_REF)) * (1 + FATIGUE_AMP * (1 - self.reserve)) * self.wear_amp(part), 'base'); self.cause[part] = self.cause[part] or 'sprint'
        return I
    def hit(self, shock, region=None, dt=0.):
        """collision shock (1.0 = grounding) or a hold's balance load acting now; region 'upper' loads arms, 'lower' loads legs/feet."""
        if shock > self.th('hit'): self._add('torso', K_HIT * (shock - self.th('hit')) ** 2, 'hit')
        if region == 'upper' and shock > .3:
            for s in ('left', 'right'): self._add(s + '_arm', K_HOLD * shock * dt, 'hold')
        if region == 'lower' and shock > .3:
            for s in ('left', 'right'): self._add(s + '_leg', K_HOLD * shock * dt * .5, 'hold'); self._add(s + '_foot', K_HOLD * shock * dt * .5, 'hold')
    def grip_load(self, force_N, dt, grip_cap=950.):
        r = force_N / grip_cap
        if r > self.th('grip'):
            e = K_GRIP * ((r - self.th('grip')) / (1 - self.th('grip'))) ** 2 * dt
            for s in ('left', 'right'): self._add(s + '_hand', e * .5, 'grip'); self._add(s + '_arm', e * .25, 'grip')
    def summary(self):
        return dict(reserve=round(self.reserve, 3), damage={k: v for k, v in self.damage.items() if v > 0}, loco=self.loco_injury())
