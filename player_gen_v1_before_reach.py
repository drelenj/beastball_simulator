"""Player generator v1: (name, position, overall) -> a full athlete.  ALL TEMPLATES PROVISIONAL; the position table is the first thing to confirm.

INPUT   name (string), position (string, see ALIASES), overall (0..100, or 0..1)
OUTPUT  an athlete dict: body (height_m, mass_kg), the 0..1 ratings that exist in the simulator today, and the Pocket attribute set derived from them.
        Deterministic: the same (name, position, overall) always gives the same athlete (seed = crc32 of name|position), so a roster file regenerates identically.

HOW 'OVERALL' IS HONOURED
  Each position has KEY ratings with weights (they sum to 1).  The generator draws every rating around the overall, adds the position's bias and a small personal noise (sd 0.035),
  then shifts the ratings until the weighted mean of the key ratings equals the overall.  So a 78 is a 78 at his position, and what differs between a 78 receiver and a 78 lineman is WHERE the 78 comes from.
  Ratings are clamped to [0.40, 1.0]; speed to [0.60, 1.0] for field athletes (canon: nobody is born slower than 80 mph).  A clamp that blocks the target is reported in `notes`.

BODY (canon anchors, Oct 2026): average field athlete 8'4" (2.54 m), field mass ~197 kg (running-back/linebacker look); Keeper 9-12 ft (2.74-3.66 m, mean 10.5 ft = 3.20 m), 275-300 kg; Archers any size.
  Height and mass are drawn from the position template (sd), then mass follows height a little (heavier when taller).  Ratings are absolute: a taller athlete is not 'faster' at the same speed rating.

RATINGS (all 0..1)   speed, agility, strength, balance, stamina, durability, injury, tackling, blocking, contact_resistance, ball_handling, catching, awareness,
                     throw_power, throw_accuracy, kick_power, kick_accuracy, jump, (keepers) keeper_skill, (archers) archery_accuracy
DERIVED (Pocket units) maximum_speed from Table A (100 mph at 1.0, 80 at 0.6: mph = 50 + 50 r), acceleration / braking / turning from the locomotion v3.7 capability table.
"""
import math, random, zlib, csv, json

MPH = .44704
R_MIN, R_MAX, SPEED_MIN = .40, 1.0, .60
NOISE_SD = .035

# ---- position table -------------------------------------------------------------------------------------------------------------------------
# h, m: (mean, sd) metres / kg.   bias: rating offsets from the overall.   key: weights of the ratings that make up the overall at this position.
TEMPLATES = {
 'passer':   dict(role='field', h=(2.54, .07), m=(190, 10), bias=dict(throw_power=.10, throw_accuracy=.14, awareness=.12, ball_handling=.08, kick_power=.04, kick_accuracy=.04, speed=-.06, strength=-.06, tackling=-.15, blocking=-.15, contact_resistance=-.06),
                  key=dict(throw_accuracy=.28, throw_power=.20, awareness=.18, ball_handling=.12, speed=.10, agility=.06, balance=.06)),
 'runner':   dict(role='field', h=(2.50, .07), m=(197, 11), bias=dict(speed=.05, agility=.10, ball_handling=.10, balance=.06, contact_resistance=.04, throw_power=-.10, throw_accuracy=-.10, tackling=-.08, blocking=-.08),
                  key=dict(speed=.24, agility=.18, ball_handling=.18, balance=.14, strength=.10, contact_resistance=.10, stamina=.06)),
 'receiver': dict(role='field', h=(2.58, .08), m=(182, 10), bias=dict(speed=.08, catching=.12, jump=.10, agility=.06, awareness=.03, strength=-.08, tackling=-.15, blocking=-.15, throw_power=-.08),
                  key=dict(catching=.28, speed=.22, agility=.14, jump=.12, awareness=.10, ball_handling=.08, balance=.06)),
 'forward':  dict(role='field', h=(2.62, .08), m=(225, 12), bias=dict(strength=.08, catching=.04, blocking=.05, jump=.03, speed=-.04, throw_accuracy=-.06),
                  key=dict(catching=.18, strength=.18, blocking=.16, speed=.14, balance=.12, awareness=.10, contact_resistance=.12)),
 'lineman':  dict(role='field', h=(2.58, .08), m=(255, 14), bias=dict(strength=.15, blocking=.12, contact_resistance=.10, balance=.06, speed=-.12, agility=-.08, jump=-.10, catching=-.12, throw_power=-.05, throw_accuracy=-.15, kick_accuracy=-.12),
                  key=dict(strength=.28, blocking=.22, contact_resistance=.16, balance=.14, tackling=.08, stamina=.06, awareness=.06)),
 'backer':   dict(role='field', h=(2.56, .07), m=(212, 11), bias=dict(tackling=.12, strength=.07, awareness=.04, contact_resistance=.05, catching=-.04, throw_accuracy=-.10),
                  key=dict(tackling=.26, strength=.16, speed=.16, awareness=.14, contact_resistance=.10, balance=.10, agility=.08)),
 'corner':   dict(role='field', h=(2.52, .07), m=(188, 9), bias=dict(speed=.08, agility=.10, catching=.06, awareness=.05, jump=.06, strength=-.08, blocking=-.12, contact_resistance=-.06),
                  key=dict(speed=.26, agility=.18, awareness=.16, catching=.14, tackling=.10, jump=.08, balance=.08)),
 'safety':   dict(role='field', h=(2.55, .07), m=(200, 10), bias=dict(awareness=.08, tackling=.05, speed=.02, catching=.03, throw_accuracy=-.05),
                  key=dict(awareness=.22, speed=.18, tackling=.18, catching=.12, agility=.10, strength=.10, balance=.10)),
 'utility':  dict(role='field', h=(2.54, .08), m=(197, 12), bias={}, key=dict(speed=.14, agility=.10, strength=.12, balance=.10, tackling=.10, catching=.10, awareness=.12, ball_handling=.10, throw_accuracy=.06, stamina=.06)),
 'keeper':   dict(role='keeper', h=(3.20, .20), m=(285, 10), bias=dict(keeper_skill=.10, catching=.10, jump=.08, strength=.05, speed=-.08, agility=-.04, throw_power=.05, kick_power=.06, kick_accuracy=.04),
                  key=dict(keeper_skill=.34, catching=.20, jump=.12, awareness=.14, agility=.10, strength=.05, balance=.05)),
 'archer':   dict(role='archer', h=(2.42, .12), m=(168, 12), bias=dict(archery_accuracy=.12, awareness=.08, speed=-.04, strength=-.14, tackling=-.2, blocking=-.2, contact_resistance=-.12),
                  key=dict(archery_accuracy=.50, awareness=.20, balance=.10, agility=.08, stamina=.06, speed=.06)),
}
ALIASES = {
 'passer': ['QB', 'QUARTERBACK', 'PASSER', 'THROWER', 'PLAYMAKER', 'PM', 'DISTRIBUTOR', 'POINT'],
 'runner': ['RB', 'HB', 'FB', 'RUNNER', 'BACK', 'RUNNING BACK', 'HALFBACK', 'FULLBACK', 'CARRIER', 'SLASHER'],
 'receiver': ['WR', 'RECEIVER', 'WIDE RECEIVER', 'WING', 'WINGER', 'END', 'FLANKER', 'SLOT', 'CATCHER', 'SPLIT END'],
 'forward': ['TE', 'TIGHT END', 'FORWARD', 'FW', 'F', 'POWER FORWARD', 'STRIKER', 'ST'],
 'lineman': ['OL', 'DL', 'OT', 'OG', 'C', 'DT', 'DE', 'LINEMAN', 'GUARD', 'TACKLE', 'CENTER', 'LOCK', 'ANCHOR', 'EDGE', 'NT', 'BIG'],
 'backer': ['LB', 'MLB', 'OLB', 'ILB', 'BACKER', 'LINEBACKER', 'MIDFIELD', 'MID', 'M'],
 'corner': ['CB', 'CORNER', 'CORNERBACK', 'DB', 'DEFENDER', 'D', 'MARKER'],
 'safety': ['S', 'FS', 'SS', 'SAFETY', 'FREE SAFETY', 'STRONG SAFETY', 'SWEEPER'],
 'keeper': ['K', 'GK', 'KEEPER', 'GOALKEEPER', 'G', 'GOALIE'],
 'archer': ['A', 'AR', 'ARCHER', 'BOWMAN', 'BOW'],
}
_LOOKUP = {a: k for k, v in ALIASES.items() for a in v}
RATINGS = ('speed', 'agility', 'strength', 'balance', 'stamina', 'durability', 'injury', 'tackling', 'blocking', 'contact_resistance', 'ball_handling', 'catching', 'awareness',
           'throw_power', 'throw_accuracy', 'kick_power', 'kick_accuracy', 'jump', 'keeper_skill', 'archery_accuracy')
# ratings with no key weight follow the overall at this fraction (they are character, not craft)
FOLLOW = dict(durability=.0, injury=.0)      # durability / injury are drawn around 0.70 (the reference), not the overall: a star is not more durable than a role player

def position_template(position):
    p = str(position).strip().upper().replace('-', ' ').replace('_', ' ')
    if p.lower() in TEMPLATES: return p.lower(), True
    if p in _LOOKUP: return _LOOKUP[p], True
    return 'utility', False

def _seed(name, position): return zlib.crc32((str(name) + '|' + str(position)).encode())

def generate(name, position, overall):
    ov = float(overall); ov = ov / 100. if ov > 1.0 else ov
    ov = max(R_MIN, min(R_MAX, ov))
    key, known = position_template(position); T = TEMPLATES[key]; rng = random.Random(_seed(name, position)); notes = []
    if not known: notes.append(f"position '{position}' not in the table: used 'utility'. Add it to ALIASES.")
    r = {}
    for k in RATINGS:
        if k in ('durability', 'injury'): r[k] = .70 + rng.gauss(0, .08); continue
        base = ov + T['bias'].get(k, 0.)
        if k in ('keeper_skill', 'archery_accuracy') and T['role'] == 'field': base = ov - .15
        if k == 'keeper_skill' and T['role'] == 'archer': base = ov - .15
        if k == 'archery_accuracy' and T['role'] == 'keeper': base = ov - .10
        r[k] = base + rng.gauss(0, NOISE_SD)
    def clamp(k, v): return max(SPEED_MIN if (k == 'speed') else R_MIN, min(R_MAX, v))
    keyset = T['key']
    for _ in range(12):
        for k in r: r[k] = clamp(k, r[k])
        cur = sum(w * r[k] for k, w in keyset.items())
        d = ov - cur
        if abs(d) < 5e-4: break
        for k, w in keyset.items(): r[k] += d * (1. if True else w)         # key ratings carry the whole shift (equal shift keeps the weighted mean exact)
        for k in r:
            if k not in keyset and k not in ('durability', 'injury'): r[k] += .4 * d
    for k in r: r[k] = round(clamp(k, r[k]), 4)
    got = sum(w * r[k] for k, w in keyset.items())
    if abs(got - ov) > .004: notes.append(f"overall {ov:.3f} could not be matched exactly (got {got:.3f}): a rating hit its clamp")
    if T['role'] == 'keeper':
        h = max(2.74, min(3.66, rng.gauss(*T['h']))); m = rng.gauss(T['m'][0], T['m'][1]) + (h - 3.20) * 70.; m = max(270., min(305., m))
    else:
        h = max(2.20, min(3.10, rng.gauss(*T['h']))) if T['role'] == 'field' else max(1.9, min(3.4, rng.gauss(*T['h'])))
        m = rng.gauss(*T['m']) + (h - T['h'][0]) * 120.; m = max(120., min(330., m))
    return dict(name=name, position=position, archetype=key, role=T['role'], overall=round(ov, 4), height_m=round(h, 3), mass_kg=round(m, 1), ratings=r, notes=notes)

# ---- Pocket attribute set -------------------------------------------------------------------------------------------------------------------
def _cap(rating, role):
    import sys, os
    here = os.path.dirname(os.path.abspath(__file__))
    for p in (here, '/home/claude/next/p23/v37pkg'):
        if p not in sys.path: sys.path.append(p)
    import pocket_capability_v37 as C
    return C.capability(min(1., max(.6, rating)), 1., '', 0., 'keeper' if role == 'keeper' else 'field')

def pocket_attributes(a):
    """Pocket 2.0 Attributes (ratings as 40..100 for the roster-override mechanism; physical values in simulator units).  Returns (overrides, extras): overrides are the attribute dict for
    ROSTER_OVERRIDES; extras are the new ratings Pocket has no slot for (consumed by pocket4_proto)."""
    r = a['ratings']; c = _cap(r['speed'], a['role']); mph = 50. + 50. * r['speed']
    top = mph * MPH
    t10 = c['t10_s'] or 1.1; acc = 2 * 10. / (t10 * t10)                       # standing-start acceleration
    brk = (25. ** 2) / (2 * (c['stop25_m'] or 10.)) if c['stop25_m'] else 30.
    cut = c['cut90_25_s'] or 1.3; turn = 13. * 1.38 / cut
    pct = lambda v: round(max(40., min(100., 100. * v)), 2)
    over = dict(height=a['height_m'], mass=a['mass_kg'], reach=round(.46 * a['height_m'], 3), maximum_speed=round(top, 3), acceleration=round(min(30., acc), 3), braking=round(min(40., brk), 3), turning=round(turn, 3),
                strength=pct(r['strength']), agility=pct(r['agility']), endurance=pct(r['stamina']), balance=pct(r['balance']), contact_resistance=pct(r['contact_resistance']), tackling=pct(r['tackling']),
                blocking=pct(r['blocking']), ball_handling=pct(r['ball_handling']), passing=pct(r['throw_accuracy']), kicking=pct(.5 * (r['throw_accuracy'] + r['kick_accuracy'])), catching=pct(r['catching']),
                awareness=pct(r['awareness']), archery_accuracy=pct(r['archery_accuracy']), keeper_skill=pct(r['keeper_skill']))
    if a['role'] == 'keeper': over['jump_height'] = round(1.3 * max(.6, r['jump']) + .3, 3)           # Pocket's Keeper launch model reads jump_height (1.6 at rating ~1)
    else: over['jump_height'] = round(1.3 * r['jump'], 3)
    extras = {k: r[k] for k in ('throw_power', 'throw_accuracy', 'kick_power', 'kick_accuracy', 'jump', 'stamina', 'durability', 'injury', 'speed')}
    return over, extras

# ---- rosters ---------------------------------------------------------------------------------------------------------------------------------
def read_csv(path):
    rows = []
    with open(path, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            low = {k.strip().lower(): (v or '').strip() for k, v in row.items() if k}
            rows.append(dict(name=low.get('name') or low.get('player'), position=low.get('position') or low.get('pos'), overall=float(low.get('overall') or low.get('ovr') or low.get('rating')), team=low.get('team', '')))
    return rows

def build_team(rows, depth=22):
    """Rows -> 22 Pocket slots: 0-9 field starters, 10 Keeper, 11 Archer, 12-21 bench.  Starters are the best by overall (one Keeper, one Archer, ten field).  Missing slots are filled with
    generated reserves named 'Reserve n' at overall 0.60.  Returns list of (slot, athlete)."""
    ath = [generate(r['name'], r['position'], r['overall']) for r in rows]
    keepers = sorted([a for a in ath if a['role'] == 'keeper'], key=lambda a: -a['overall'])
    archers = sorted([a for a in ath if a['role'] == 'archer'], key=lambda a: -a['overall'])
    field = sorted([a for a in ath if a['role'] == 'field'], key=lambda a: -a['overall'])
    n = [0]
    def fill(role, pos):
        n[0] += 1; return generate(f'Reserve {n[0]}', pos, .60)
    while len(keepers) < 1: keepers.append(fill('keeper', 'keeper'))
    while len(archers) < 1: archers.append(fill('archer', 'archer'))
    # extra keepers / archers sit on the bench as field-roled athletes would be wrong: keep only one each in play, extras are dropped to the bench list unused by Pocket (it substitutes keeper/archer by role)
    while len(field) < 20: field.append(fill('field', 'utility'))
    slots = [(i, field[i]) for i in range(10)] + [(10, keepers[0]), (11, archers[0])] + [(12 + i, field[10 + i]) for i in range(10)]
    return slots

def to_pocket_overrides(team_slots, team):
    """ROSTER_OVERRIDES fragment {'A0': {...}, ...} and the extras per slot."""
    over, extras, names = {}, {}, {}
    for slot, a in team_slots:
        o, e = pocket_attributes(a); over[f'{team}{slot}'] = o; extras[f'{team}{slot}'] = e; names[f'{team}{slot}'] = dict(name=a['name'], position=a['position'], overall=a['overall'], archetype=a['archetype'])
    return over, extras, names

if __name__ == '__main__':
    import sys
    for nm, pos, ov in (('Test Passer', 'QB', 82), ('Test Wing', 'WR', 82), ('Test Anchor', 'OL', 82), ('Test Keeper', 'GK', 82), ('Test Archer', 'Archer', 82)):
        a = generate(nm, pos, ov); o, e = pocket_attributes(a)
        print(nm, pos, ov, a['height_m'], a['mass_kg'], {k: a['ratings'][k] for k in ('speed', 'strength', 'catching', 'throw_power', 'throw_accuracy', 'jump')}, round(o['maximum_speed'], 1), a['notes'])
