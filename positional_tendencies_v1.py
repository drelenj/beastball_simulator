#!/usr/bin/env python3
"""Positional tendencies v1: players play like their position and their archetype.  Source: Beastball_roster_logic.pdf (supersedes my generator's archetype names).

Two things live here:
  1. CLASSIFY: for each player, the closest archetype from the logic report for his position (PDR, STR, SCT, PFD, HNT, TRK, TRP, GRD; SEN/KPR/ARC have no archetype list in the report, so one default each).
     Closest = the archetype whose rating signature best matches how his ratings sit above/below his own average.  Apex Hunter needs a complete profile.
  2. TENDENCIES: where the player stands when his team has the ball and when it does not, who chases the ball carrier, and what he prefers to do with the ball (shoot / carry / pass).
     Tendencies are preferences only.  They never change a rating.  Every number below is a provisional dial.

How it connects to Pocket 2.0 (untouched):
  - Policy.targets (non-carrier movement): after Pocket's own targets are computed, field players who are (a) not carrying, (b) not an escort, (c) not inside a Keeper Zone, (d) not chasing a loose ball, and
    (e) in live play, get a positional target.  Defenders are re-elected for the chase by weighted distance (position x archetype x situation).
  - c4c2_eval / c4c2_cont / pocket_pass_option (carrier's decision values): shoot, carry, pass and continue values are scaled by his position/archetype bias (and shot distance), pass values by who receives.
Coordinates: u = depth along the team's attack direction (0 = own goal line, 100 = opponent goal line), y = 0..100 across.
"""
import math

POSITIONS = ('PDR', 'STR', 'SCT', 'PFD', 'HNT', 'TRK', 'SEN', 'TRP', 'GRD', 'KPR', 'ARC')
GROUP = dict(PDR='Attacker', STR='Attacker', SCT='Attacker', PFD='Ranger', HNT='Ranger', TRK='Ranger', SEN='Ranger', TRP='Defender', GRD='Defender', KPR='Specialist', ARC='Specialist')

# ---------------------------------------------------------------------------------------------------------------------------------------------------
# 1. archetype signatures (weights over ratings, 0..1 scale).  From the "Common X Archetypes" and "Ideal Skillset" text of the report.
# ---------------------------------------------------------------------------------------------------------------------------------------------------
SIG = {
 'PDR': {'Slasher': dict(speed=.30, agility=.25, ball_handling=.25, balance=.10, contact_resistance=.10),
         'Ghost': dict(awareness=.30, agility=.30, balance=.15, ball_handling=.15, speed=.10),
         'Power Predator': dict(strength=.30, contact_resistance=.30, balance=.20, ball_handling=.10, speed=.10),
         'Tempo Predator': dict(awareness=.30, throw_accuracy=.25, ball_handling=.20, agility=.15, stamina=.10),
         'Far-Side Predator': dict(speed=.30, stamina=.25, awareness=.25, agility=.10, kick_power=.10)},
 'STR': {'Tower': dict(strength=.30, jump=.20, contact_resistance=.20, catching=.15, blocking=.15),
         'Cutter': dict(agility=.30, speed=.25, awareness=.20, catching=.15, balance=.10),
         'Bruiser': dict(strength=.35, contact_resistance=.30, blocking=.20, tackling=.15),
         'Pivot': dict(awareness=.30, ball_handling=.25, throw_accuracy=.20, catching=.15, balance=.10),
         'Dual Threat': dict(kick_power=.25, kick_accuracy=.25, strength=.20, speed=.15, catching=.15)},
 'SCT': {'Sniper': dict(kick_accuracy=.35, awareness=.25, throw_accuracy=.20, catching=.10, balance=.10),
         'Cutter': dict(agility=.30, speed=.30, ball_handling=.20, awareness=.20),
         'False Pathfinder': dict(awareness=.30, throw_accuracy=.30, ball_handling=.20, throw_power=.10, kick_accuracy=.10),
         'Transition Scout': dict(speed=.35, stamina=.25, agility=.20, awareness=.20),
         'Rotational Scout': dict(stamina=.30, agility=.25, awareness=.25, balance=.20)},
 'PFD': {'Conductor': dict(awareness=.35, throw_accuracy=.30, ball_handling=.15, balance=.10, stamina=.10),
         'Aggressor': dict(throw_power=.25, speed=.25, awareness=.20, agility=.15, stamina=.15),
         'Field Surgeon': dict(awareness=.40, throw_accuracy=.40, ball_handling=.10, balance=.10),
         'Hybrid Pathfinder': dict(speed=.25, agility=.25, awareness=.20, throw_accuracy=.15, tackling=.15),
         'Possession Monarch': dict(ball_handling=.35, balance=.20, stamina=.20, awareness=.15, contact_resistance=.10)},
 'HNT': {'Transition Hunter': dict(speed=.30, stamina=.25, agility=.25, awareness=.20),
         'Tactical Hunter': dict(awareness=.45, throw_accuracy=.20, agility=.15, balance=.10, stamina=.10),
         'Predator Hunter': dict(speed=.25, ball_handling=.25, agility=.20, contact_resistance=.15, strength=.15),
         'Sentinel Hunter': dict(tackling=.30, awareness=.25, strength=.15, stamina=.15, balance=.15),
         'Pathfinder Hunter': dict(awareness=.30, throw_accuracy=.30, throw_power=.15, ball_handling=.15, stamina=.10)},   # 'Apex Hunter' is decided separately (complete profile)
 'TRK': {'Shuttle': dict(stamina=.40, speed=.25, agility=.20, awareness=.15),
         'Anchor Tracker': dict(awareness=.30, tackling=.25, balance=.20, stamina=.15, strength=.10),
         'Overload Tracker': dict(agility=.25, stamina=.25, ball_handling=.20, throw_accuracy=.15, speed=.15),
         'Transition Tracker': dict(speed=.40, agility=.20, stamina=.20, awareness=.20),
         'Tactical Tracker': dict(awareness=.40, throw_accuracy=.20, stamina=.20, balance=.10, ball_handling=.10)},
 'GRD': {'Anchor': dict(strength=.25, balance=.25, awareness=.20, contact_resistance=.15, tackling=.15),
         'Crusher': dict(strength=.35, tackling=.30, contact_resistance=.25, blocking=.10),
         'Sweeping Guard': dict(speed=.30, agility=.25, tackling=.20, awareness=.25),
         'Field General': dict(awareness=.45, tackling=.20, throw_accuracy=.15, balance=.10, strength=.10),
         'Hybrid Guard': dict(strength=.25, speed=.30, agility=.20, balance=.15, tackling=.10)},
 'TRP': {'Containment Specialist': dict(agility=.30, awareness=.25, balance=.20, tackling=.15, strength=.10),
         'Press Trapper': dict(tackling=.30, speed=.25, agility=.20, strength=.15, stamina=.10),
         'Recovery Trapper': dict(speed=.40, stamina=.25, agility=.20, awareness=.15),
         'Archer Trapper': dict(awareness=.35, agility=.25, tackling=.20, balance=.20),
         'Hybrid Trapper': dict(speed=.25, agility=.25, awareness=.20, stamina=.10, throw_accuracy=.10, ball_handling=.10)},
 'SEN': {'Sentinel': {}}, 'KPR': {'Keeper': {}}, 'ARC': {'Archer': {}},
}
CORE = ('speed', 'agility', 'strength', 'balance', 'stamina', 'tackling', 'blocking', 'contact_resistance', 'ball_handling', 'catching', 'awareness', 'throw_power', 'throw_accuracy', 'kick_power', 'kick_accuracy', 'jump')
APEX = ('speed', 'agility', 'balance', 'stamina', 'tackling', 'ball_handling', 'catching', 'awareness', 'throw_accuracy', 'strength')

def classify(position, ratings):
    """-> (archetype, margin, scores).  ratings: dict name -> 0..1.  Unknown positions are treated as TRK-like role players (HNT is an honorific, not a default)."""
    pos = position if position in SIG else 'TRK'
    table = SIG[pos]
    if len(table) == 1: return next(iter(table)), 1.0, {}
    r = {k: ratings.get(k, .6) for k in CORE}; mean = sum(r.values()) / len(r)
    if pos == 'HNT':
        core = [r[k] for k in APEX]; m = sum(core) / len(core); sd = (sum((v - m) ** 2 for v in core) / len(core)) ** .5
        if m >= .88 and sd <= .07 and min(core) >= .80: return 'Apex Hunter', 1.0, {}
    scores = {a: sum(w * (r[k] - mean) for k, w in sig.items()) / sum(sig.values()) for a, sig in table.items()}
    best = sorted(scores.items(), key=lambda kv: -kv[1])
    return best[0][0], round(best[0][1] - best[1][1], 4), {k: round(v, 4) for k, v in scores.items()}

# ---------------------------------------------------------------------------------------------------------------------------------------------------
# 2. tendencies
# ---------------------------------------------------------------------------------------------------------------------------------------------------
# bias: multiplier on the value of that option for this player.  shoot_prof: (min m, max m, multiplier) bands on distance to goal.  chase: multiplier on his distance when the defence elects chasers (< 1 = more willing).
# att/def: (depth u rule, lane rule).  Rules are implemented in lane() below; this table holds the numbers.
POS = {
 'PDR': dict(bias=dict(shoot=1.05, carry=1.25, pass_=.90, cont=1.05), shoot_prof=[], chase=1.40, trans_chase=.65, att_lead=10., att_lane=20., def_lead=10., def_lane=18.),
 'STR': dict(bias=dict(shoot=1.10, carry=1.10, pass_=.90, cont=1.00), shoot_prof=[(0, 16, 1.15), (26, 100, .85)], chase=1.60, trans_chase=1.20, att_lead=18., att_lane=6., def_lead=10., def_lane=8.),
 'SCT': dict(bias=dict(shoot=1.10, carry=.95, pass_=1.05, cont=1.00), shoot_prof=[(16, 36, 1.20)], chase=1.40, trans_chase=1.00, att_lead=9., att_lane=34., def_lead=9., def_lane=34.),
 'PFD': dict(bias=dict(shoot=.80, carry=.80, pass_=1.25, cont=1.10), shoot_prof=[], chase=1.00, trans_chase=1.00, att_lead=-5., att_lane=.4, def_lead=-1., def_lane=.35),
 'HNT': dict(bias=dict(shoot=1.00, carry=1.00, pass_=1.00, cont=1.05), shoot_prof=[], chase=.85, trans_chase=.70, att_lead=0., att_lane=0., def_lead=0., def_lane=0.),
 'TRK': dict(bias=dict(shoot=.85, carry=1.00, pass_=1.10, cont=1.00), shoot_prof=[], chase=.95, trans_chase=.85, att_lead=1., att_lane=18., def_lead=-3., def_lane=20.),
 'SEN': dict(bias=dict(shoot=.65, carry=.80, pass_=1.10, cont=1.00), shoot_prof=[(0, 100, .8)], chase=.90, trans_chase=.80, att_lead=-11., att_lane=.4, def_lead=-8., def_lane=.5),
 'TRP': dict(bias=dict(shoot=.60, carry=.80, pass_=1.10, cont=1.00), shoot_prof=[(0, 100, .8)], chase=1.25, trans_chase=1.00, att_lead=-9., att_lane=30., def_lead=-6., def_lane=30.),
 'GRD': dict(bias=dict(shoot=.50, carry=.70, pass_=1.15, cont=1.00), shoot_prof=[(0, 100, .75)], chase=1.30, trans_chase=1.00, att_lead=-18., att_lane=.12, def_lead=-14., def_lane=.3),
 'KPR': dict(bias=dict(shoot=1., carry=1., pass_=1., cont=1.), shoot_prof=[], chase=1., trans_chase=1., att_lead=0., att_lane=0., def_lead=0., def_lane=0.),
 'ARC': dict(bias=dict(shoot=1., carry=1., pass_=1., cont=1.), shoot_prof=[], chase=1., trans_chase=1., att_lead=0., att_lane=0., def_lead=0., def_lane=0.),
}
# archetype modifiers: lead (m, added to depth), lane (multiplier on lane width), chase (x), bias (x per option), note.  Anything not listed = no change.
ARCH = {
 'Slasher': dict(bias=dict(carry=1.12), lead=2, note='explosive direct carries, transition-heavy'),
 'Ghost': dict(lane=1.10, bias=dict(pass_=1.05), note='movement manipulator: hesitation and delayed cuts, finesse'),
 'Power Predator': dict(bias=dict(carry=1.05, shoot=1.05), chase=.90, note='contact balance, forceful penetration near the Keeper Zone'),
 'Tempo Predator': dict(bias=dict(carry=.90, pass_=1.20), lead=-3, note='less scoring-focused: shapes tempo, almost a hybrid playmaker'),
 'Far-Side Predator': dict(lane=1.25, lead=3, note='weak-side attacks and transition bursts'),
 'Tower': dict(bias=dict(shoot=1.05), lead=3, lane=.8, note='interior force, contact finishing'),
 'Cutter': dict(lane=1.15, lead=2, bias=dict(carry=1.08), note='timing, lanes and movement'),
 'Bruiser': dict(chase=.85, bias=dict(carry=1.08, shoot=.95), lane=.8, note='pure physical pressure, compression'),
 'Pivot': dict(lead=-5, bias=dict(pass_=1.15, shoot=.9), lane=1.2, note='high-IQ facilitator and redirector'),
 'Dual Threat': dict(bias=dict(shoot=1.08), lead=-3, shoot_far=1.12, note='inside pressure that stretches outward briefly'),
 'Sniper': dict(bias=dict(shoot=1.10), shoot_far=1.15, lane=1.0, note='pure long-range specialist'),
 'False Pathfinder': dict(lane=.4, lead=-9, bias=dict(pass_=1.20, shoot=.9), note='drops inward to facilitate and manipulate tempo'),
 'Transition Scout': dict(lead=4, bias=dict(carry=1.10), note='open-field attacks and far-side acceleration'),
 'Rotational Scout': dict(rotate=True, note='constant lane rotation'),
 'Conductor': dict(bias=dict(pass_=1.08), note='methodical tempo controller'),
 'Aggressor': dict(lead=4, bias=dict(carry=1.15, pass_=.95), note='pushes tempo, fast attacks'),
 'Field Surgeon': dict(bias=dict(pass_=1.15, shoot=.85, carry=.9), note='hyper-precise operator'),
 'Hybrid Pathfinder': dict(lead=3, lane=1.4, chase=.90, bias=dict(carry=1.10), note='part Hunter, part Scout'),
 'Possession Monarch': dict(bias=dict(carry=1.12, pass_=1.05, shoot=.80), note='ball control and exhaustion warfare'),
 'Apex Hunter': dict(note='complete player: no preference, fills the weakest role'),
 'Transition Hunter': dict(lead=3, chase=.85, note='turnovers, recoveries, tempo shifts'),
 'Tactical Hunter': dict(bias=dict(cont=1.05), note='high-IQ shape manipulator'),
 'Predator Hunter': dict(lead=3, bias=dict(carry=1.12, shoot=1.05), note='aggressive and offensive'),
 'Sentinel Hunter': dict(lead=-4, chase=.85, bias=dict(shoot=.85, carry=.9), note='defensively dominant hybrid'),
 'Pathfinder Hunter': dict(bias=dict(pass_=1.15), lead=-2, note='orchestrates and stabilises transitions'),
 'Shuttle': dict(follow_ball=True, note='classic high-mobility Tracker: rotates and supports to the ball side'),
 'Anchor Tracker': dict(lead=-4, chase=1.05, note='conservative: structure, recovery, defensive support'),
 'Overload Tracker': dict(follow_ball=True, lane=1.1, bias=dict(carry=1.05), note='supports one side repeatedly'),
 'Transition Tracker': dict(lead=3, chase=.85, note='fast-break systems and tempo acceleration'),
 'Tactical Tracker': dict(lane=.85, bias=dict(pass_=1.10), note='high-IQ spacing and support timing'),
 'Anchor': dict(lead=-3, chase=1.10, note='classic central wall'),
 'Crusher': dict(chase=.80, lane=1.0, note='highly physical: steps up to punish interior carries'),
 'Sweeping Guard': dict(lead=5, chase=.90, lane=1.3, note='more mobile and reactive, covers Predators and transitions'),
 'Field General': dict(bias=dict(pass_=1.15), note='organizer of the defence'),
 'Hybrid Guard': dict(lead=3, lane=1.5, chase=.90, note='central power with unusual mobility'),
 'Containment Specialist': dict(lane=1.0, note='positioning and angle denial'),
 'Press Trapper': dict(chase=.80, lead=3, note='aggressive pressure defender, sideline traps'),
 'Recovery Trapper': dict(lead=-4, chase=.95, note='transition-focused, restores shape'),
 'Archer Trapper': dict(lane=1.05, note='funnels toward Archer influence (treated as containment in v1)'),
 'Hybrid Trapper': dict(lane=.75, lead=2, chase=.90, note='modern mobile defender: rotates centrally'),
 'Sentinel': dict(note='no archetype list in the report'), 'Keeper': dict(note='no archetype list in the report'), 'Archer': dict(note='no archetype list in the report'),
}

import os
BIAS_K = float(os.environ.get('TEND_K', '0.5'))   # exponent on every bias multiplier (1 = full strength, 0 = none)

class Tend:
    """per player"""
    __slots__ = ('pos', 'arch', 'bias', 'chase', 'lead', 'lane', 'shoot_prof', 'shoot_far', 'rotate', 'follow_ball', 'spec')
    def __init__(self, pos, arch):
        sp = POS.get(pos, POS['TRK']); am = ARCH.get(arch, {}); self.pos = pos if pos in POS else 'TRK'; self.arch = arch; self.spec = sp
        self.bias = dict(sp['bias'])
        for k, v in am.get('bias', {}).items(): self.bias[k] = self.bias[k] * v
        self.bias = {k: v ** BIAS_K for k, v in self.bias.items()}
        self.chase = sp['chase'] * am.get('chase', 1.); self.lead = am.get('lead', 0.); self.lane = am.get('lane', 1.)
        self.shoot_prof = list(sp['shoot_prof']); self.shoot_far = am.get('shoot_far', 1.); self.rotate = am.get('rotate', False); self.follow_ball = am.get('follow_ball', False)

def clamp(v, a, b): return max(a, min(b, v))

def shoot_mult(t, d):
    m = t.bias['shoot']
    for lo, hi, f in t.shoot_prof:
        if lo <= d <= hi: m *= f ** BIAS_K
    if t.shoot_far != 1. and d > 16: m *= t.shoot_far ** BIAS_K
    return m

AFFINITY = {   # passer position -> {receiver position: multiplier on the pass value}
 'PFD': dict(STR=1.12, SCT=1.08, PDR=.95, TRK=1.03), 'SCT': dict(STR=1.10, PDR=1.04, PFD=1.03), 'TRK': dict(SCT=1.10, PFD=1.05, STR=1.03),
 'SEN': dict(PFD=1.12, HNT=1.08, TRK=1.04), 'HNT': dict(PFD=1.04, SCT=1.04, STR=1.04), 'GRD': dict(SEN=1.10, TRP=1.05, TRK=1.04), 'TRP': dict(TRK=1.10, SEN=1.05, GRD=1.02),
 'PDR': dict(SCT=1.10, STR=1.02), 'STR': dict(SCT=1.08, PFD=1.03),
}


# ---------------------------------------------------------------------------------------------------------------------------------------------------
# 3. defenders in the offence  (Rotational Attack Architecture, proposed - see DEFENDER_OFFENCE_NOTES.md)
# ---------------------------------------------------------------------------------------------------------------------------------------------------
DEF_FREEDOM = float(os.environ.get('DEF_FREEDOM', '1.0'))      # coach dial: 0 = defenders never join, 1 = default, >1 = predatory swarm
ADV = dict(max_adv=3, on_thr=.22, off_thr=.08, hold_s=4., recover_s=6., min_cover=2)
FREE = {'GRD': .85, 'TRP': .95}                                # base attacking freedom by position
ARCH_FREE = {'Crusher': .10, 'Anchor': -.20, 'Sweeping Guard': .15, 'Field General': 0., 'Hybrid Guard': .25,
             'Containment Specialist': -.05, 'Press Trapper': .10, 'Recovery Trapper': -.10, 'Archer Trapper': -.15, 'Hybrid Trapper': .25}
COVER_PRI = {'SEN': 0, 'HNT': 1, 'TRK': 2, 'PFD': 3}           # who drops to hold the vacated space

def freedom(T):
    return clamp((FREE.get(T.pos, 0.) + ARCH_FREE.get(T.arch, 0.)) * DEF_FREEDOM, 0., 1.3)

def rule_lane(t, role, state, u_b, y_b, side, R, ctx):
    """-> (u, y) target.  role/state per table above.  side in {-1,+1}; ctx has: weak (sign of the side opposite the ball), t (seconds) for rotation, n (same-position teammates active)."""
    sp = t.spec; lead = sp['att_lead' if state == 'att' else 'def_lead'] + t.lead; lane = sp['att_lane' if state == 'att' else 'def_lane']
    ball_side = 1 if y_b >= 50 else -1; dy = y_b - 50
    if t.rotate: side = 1 if int(ctx['t'] / 12.) % 2 == 0 else -1
    if t.follow_ball and ctx['n'] == 1: side = ball_side
    elif t.follow_ball: side = ball_side if state == 'att' else side
    W = lambda w: w * t.lane
    pos = t.pos
    hi = 100 - R - 1.5; lo = R + 3.
    if pos == 'STR':
        u = min(100 - R - 2., u_b + lead) if state == 'att' else u_b + lead
        y = 50 + clamp(dy * .25, -8, 8) + side * W(lane) * .35
    elif pos == 'PDR':
        weak = -ball_side if abs(dy) > 6 else side
        u = min(100 - R - 4., u_b + lead); y = 50 + weak * W(lane)
    elif pos == 'SCT':
        u = min(hi, u_b + lead)
        y = 50 + side * W(lane) if ctx['n'] > 1 or t.lane >= .9 else 50 + (-ball_side) * W(lane)
    elif pos == 'PFD':
        u = u_b + lead; y = 50 + dy * lane
    elif pos == 'TRK':
        u = u_b + lead; y = 50 + side * W(lane)
    elif pos == 'SEN':
        u = clamp(u_b + lead, lo + 5, 70); y = 50 + dy * lane
    elif pos == 'GRD':
        u = clamp(u_b + lead, lo, 45 if state == 'def' else 55); y = 50 + dy * lane + (side * 7 if ctx['n'] > 1 else 0)
    elif pos == 'TRP':
        u = clamp(u_b + lead, lo, 60 if state == 'def' else 65)
        s_ = side if ctx['n'] > 1 else ball_side
        y = 50 + s_ * W(lane)
    else:
        u, y = u_b, 50.
    return u, clamp(y, 4., 96.)

def install(CO, S, geometry=None, get_state=None):
    """Hook Policy.targets and the carrier's decision values.  S.on is checked at run time ('tendencies'); S.tend maps pid -> Tend (set by pocket4_proto when rosters are built)."""
    Policy = CO.policies.Policy; Match = CO.match.Match
    geo = geometry or CO.geometry
    norm, zone, clamp_ = geo.norm, geo.zone, geo.clamp
    o_targets = Policy.targets
    S.tgt_acc = {}; S.adv = {}; S.cover = {}; S.adv_stat = {}
    def rec(pos, st, du, y):
        a = S.tgt_acc.setdefault((pos, st), [0, 0., 0.]); a[0] += 1; a[1] += du; a[2] += abs(y - 50)
    def targets(self, s):
        tg = o_targets(self, s)
        tend = getattr(S, 'tend', None)
        if 'tendencies' not in S.on or 'tend_nolane' in S.on or not tend or self.defense == 'man' or s.phase.value != 'live': return tg
        b = s.ball; sgn = s.attack_sign(self.team); own = s.ends[self.team]; R = s.keeper_zone_radius
        S.poss_ms = s.possession_ms
        carrier = s.players.get(b.carrier) if b.carrier else None
        if carrier is None: return tg
        ours = [p for p in self.eligible(s) if p.role == 'field']
        if not ours: return tg
        u_of = lambda x: sgn * (x - own); x_of = lambda u: clamp_(own + sgn * u, 1., 99.)
        t_s = s.now / 1000.
        u_b, y_b = u_of(b.x), b.y; ball_side_ = 1 if y_b >= 50 else -1
        by_pos = {}
        for p in ours: by_pos.setdefault((tend.get(p.id) or Tend('TRK', 'x')).pos, []).append(p)
        for v in by_pos.values(): v.sort(key=lambda q: q.id)
        def side_of(p, pos):
            lst = by_pos[pos]; n = len(lst)
            if n == 1: return 1 if y_b >= 50 else -1
            i = lst.index(p); return (-1, 1, 0)[i] if i < 3 else 1
        adv = S.adv.setdefault(self.team, {}); cover = S.cover.setdefault(self.team, {})
        use_adv = 'tend_nodefadv' not in S.on
        for pid in [k for k in adv if k not in {q.id for q in ours}]: adv.pop(pid, None)
        if carrier.team == self.team:
            state = 'att'
            if use_adv:
                trans = s.possession_ms < 8000
                opp = [q for q in s.players.values() if q.team != self.team and q.role == 'field' and q.active and q.available]
                opp_back = sum(1 for q in opp if u_of(q.x) < 45)
                defs = [p for p in ours if (tend.get(p.id) is not None and tend[p.id].pos in FREE)]
                backs = [p for p in ours if (tend.get(p.id) is not None and (tend[p.id].pos in FREE or tend[p.id].pos == 'SEN'))]
                scored = []
                for p in defs:
                    T = tend[p.id]; F = freedom(T)
                    terr = clamp((u_b - 30.) / 35., 0., 1.); near = 1. if p.id == carrier.id else clamp(1. - norm(p.x - b.x, p.y - b.y) / 45., 0., 1.)
                    v = F * (.30 + .60 * terr + (.35 if trans else 0.)) * (.75 + .25 * near) - .45 * clamp(opp_back / 4., 0., 1.)
                    back_n = sum(1 for q in backs if q.id != p.id and q.id not in adv and u_of(q.x) < 45)
                    if back_n < ADV['min_cover']: v -= .40
                    scored.append((v, p))
                for pid, d in list(adv.items()):
                    d['seen'] = s.now
                for v, p in sorted(scored, key=lambda t_: -t_[0]):
                    on = p.id in adv
                    if on and (v >= ADV['off_thr'] or (s.now - adv[p.id]['t0']) / 1000. < ADV['hold_s']): continue
                    if on: adv.pop(p.id, None); continue
                    if v >= ADV['on_thr'] and len(adv) < ADV['max_adv']: adv[p.id] = dict(t0=s.now, seen=s.now)
                cover.clear()
                if adv:
                    cands = sorted([q for q in ours if q.id not in adv and q.id != carrier.id and (tend.get(q.id) is not None and tend[q.id].pos in COVER_PRI)],
                                   key=lambda q: (COVER_PRI[tend[q.id].pos], norm(x_of(max(R + 6., min(38., u_b - 14.))) - q.x, 50 + (y_b - 50) * .3 - q.y)))
                    for i_, q in enumerate(cands[:len(adv)]): cover[q.id] = i_
                for p in ours:
                    if p.id in adv:
                        a_ = S.adv_stat.setdefault(tend[p.id].pos, [0, 0]); a_[1] += 1
                for p in defs:
                    S.adv_stat.setdefault(tend[p.id].pos, [0, 0])[0] += 1
            for p in ours:
                if p.id == carrier.id: continue
                T = tend.get(p.id)
                if T is None: continue
                if zone(p.x, p.y, R) is not None: continue
                tx, ty = tg.get(p.id, (p.x, p.y))
                if norm(tx - carrier.x, ty - carrier.y) < 6.: continue                   # Pocket's escort: leave
                pos = T.pos; side = side_of(p, pos)
                ctx = dict(t=t_s, n=len(by_pos[pos]))
                if p.id in adv:
                    if pos == 'GRD': u, y = min(100 - R - 6., u_b + 10. + T.lead), 50 + (y_b - 50) * .35
                    else:
                        weak = -ball_side_ if abs(y_b - 50) > 8 else side
                        u, y = min(100 - R - 5., u_b + 7. + T.lead), 50 + weak * 30. * T.lane
                    tg[p.id] = (x_of(u), clamp(y, 4., 96.)); rec(T.pos, 'att', u - u_b, y); continue
                if p.id in cover:
                    u, y = max(R + 6., min(38., u_b - 14.)), 50 + (y_b - 50) * .3 + (-9 if cover[p.id] else 9) * (1 if cover[p.id] else 0)
                    tg[p.id] = (x_of(u), clamp(y, 4., 96.)); rec(T.pos, 'att', u - u_b, y); continue
                if pos == 'HNT':
                    spots = [(u_b - 5, 50 + (y_b - 50) * .4), (u_b + 9, 18.), (u_b + 9, 82.), (min(100 - R - 2., u_b + 16), 50.), (max(R + 8., u_b - 14), 50.), (u_b - 9, 20.), (u_b - 9, 80.)]
                    mates = [q for q in ours if q.id not in (p.id, carrier.id)]
                    best = max(spots, key=lambda sp_: min((norm(x_of(sp_[0]) - q.x, sp_[1] - q.y) for q in mates), default=99.) - .15 * norm(x_of(sp_[0]) - p.x, sp_[1] - p.y))
                    u, y = best
                else: u, y = rule_lane(T, pos, state, u_b, y_b, side, R, ctx)
                tg[p.id] = (x_of(u), y); rec(T.pos, 'att', u - u_b, y)
        else:
            state = 'def'
            trans = s.possession_ms < 5000 and s.owner != self.team
            for pid in list(adv):
                q = s.players.get(pid)
                if q is None or u_of(q.x) < 40 or (s.now - adv[pid]['seen']) / 1000. > ADV['recover_s']: adv.pop(pid, None)
            if not adv: cover.clear()
            k = max(1, int(round(self.t.hunt_count)))
            if self.defense == 'hunt': k = max(k, 4)
            def key(p):
                T = tend.get(p.id)
                f = 1.0 if T is None else (T.spec['trans_chase'] * (T.chase / T.spec['chase']) if trans else T.chase)
                if T is not None and T.pos == 'GRD': f *= .6 if u_of(carrier.x) < R + 14 else 1.0
                if T is not None and T.pos == 'TRP': f *= .75 if abs(carrier.y - 50) > 20 else 1.0
                return norm(p.x - carrier.x, p.y - carrier.y) * f
            ranked = sorted(ours, key=lambda p: (key(p), p.id)); chasers = ranked[:k]
            for rank, p in enumerate(chasers):
                if zone(p.x, p.y, R) is not None: continue
                lead = .25 + rank * .06; tx = carrier.x + carrier.vx * lead; ty = carrier.y + carrier.vy * lead
                angle = 0 if rank == 0 else (-1 if rank % 2 else 1) * (.7 + rank * .5)
                tg[p.id] = (clamp_(tx, 1, 99), clamp_(ty + angle, 1, 99))
            for p in ranked[k:]:
                T = tend.get(p.id)
                if T is None or zone(p.x, p.y, R) is not None: continue
                pos = T.pos; side = side_of(p, pos); ctx = dict(t=t_s, n=len(by_pos[pos]))
                if p.id in cover and adv:
                    u, y = max(R + 6., min(38., u_b - 10.)), 50 + (y_b - 50) * .4
                    tg[p.id] = (x_of(u), clamp(y, 4., 96.)); rec(T.pos, 'def', u - u_b, y); continue
                if pos == 'HNT':
                    spots = [(R + 3, 50.), (max(R + 5, u_b - 8), 50 + (y_b - 50) * .5), (max(R + 3, u_b - 6), 22.), (max(R + 3, u_b - 6), 78.), (max(R + 3, u_b - 3), 32.), (max(R + 3, u_b - 3), 68.)]
                    mates = [q for q in ours if q.id != p.id]
                    u, y = max(spots, key=lambda sp_: min((norm(x_of(sp_[0]) - q.x, sp_[1] - q.y) for q in mates), default=99.) - .15 * norm(x_of(sp_[0]) - p.x, sp_[1] - p.y))
                else: u, y = rule_lane(T, pos, state, u_b, y_b, side, R, ctx)
                tg[p.id] = (x_of(u), y); rec(T.pos, 'def', u - u_b, y)
            for p in chasers:
                T = tend.get(p.id)
                if T is not None: S.tgt_acc.setdefault((T.pos, 'chase'), [0, 0., 0.]); a = S.tgt_acc[(T.pos, 'chase')]; a[0] += 1
        return tg
    Policy.targets = targets

    # ---- carrier decision values -------------------------------------------------------------------------------------------------------------
    o_eval, o_cont, o_pass = Match.c4c2_eval, Match.c4c2_cont, Match.pocket_pass_option
    def c4c2_eval(self, p, x, y, clock, arrow_t=None, origin=False):
        r = o_eval(self, p, x, y, clock, arrow_t, origin)
        T = getattr(S, 'tend', {}).get(p.id) if 'tendencies' in S.on and 'tend_nobias' not in S.on else None
        if T is not None and isinstance(r, dict):
            d = r.get('d', 50.)
            advd = S.adv.get(p.team, {}) if 'tend_nodefadv' not in S.on else {}
            if p.id in advd:
                if 'shoot' in r: r['shoot'] = r['shoot'] * 1.12
                if 'carry' in r: r['carry'] = r['carry'] * (1.20 if getattr(S, 'poss_ms', 99999) < 6000 else 1.12)
            else:
                if 'shoot' in r: r['shoot'] = r['shoot'] * shoot_mult(T, d)
                if 'carry' in r: r['carry'] = r['carry'] * T.bias['carry']
        return r
    def c4c2_cont(self, p, x, y, clock, arrow_t=None):
        v = o_cont(self, p, x, y, clock, arrow_t)
        T = getattr(S, 'tend', {}).get(p.id) if 'tendencies' in S.on and 'tend_nobias' not in S.on else None
        return v * T.bias['cont'] if T is not None else v
    def pocket_pass_option(self, p, q, clock):
        c = o_pass(self, p, q, clock)
        if c is None or 'tendencies' not in S.on or 'tend_nobias' in S.on: return c
        tend = getattr(S, 'tend', {}); T = tend.get(p.id); Tq = tend.get(q.id)
        if T is not None:
            c['value'] *= T.bias['pass_']
            if Tq is not None: c['value'] *= AFFINITY.get(T.pos, {}).get(Tq.pos, 1.0)
            if q.id in S.adv.get(q.team, {}) and 'tend_nodefadv' not in S.on: c['value'] *= 1.10
        return c
    Match.c4c2_eval, Match.c4c2_cont, Match.pocket_pass_option = c4c2_eval, c4c2_cont, pocket_pass_option
    return Policy
