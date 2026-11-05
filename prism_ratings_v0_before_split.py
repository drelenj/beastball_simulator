"""Per-athlete PRISM ratings (the only per-athlete knobs of the individual layer).  Every number marked [P] is provisional.
Source order, per athlete and per rating:
  1. a CSV/roster column  prism_<name>  (0-1, or 0-100)  : the designer's authored value, always wins
  2. derived: base = BLEND*overall + (1-BLEND)*Pocket awareness (both 0-1);  rating = CENTER_OUT + GAIN*(base - CENTER_IN) + position offset + seeded jitter, clamped
     CENTER_IN (.85) is roughly the league-average base, so an average athlete lands on CENTER_OUT = .7, the league-average rating [C].
  Position offsets start EMPTY on purpose: which positions are specialists in which rating is canon (DreLen), not mine.  Fill POSITION_OFFSETS to author it.
The eight: vision, awareness, clarity, reaction, focus, instinct, anticipation, judgment.  (PRISM 'awareness' is the perception rating; Pocket's own 'awareness' attribute is only an input here.)
"""
import math, zlib, random, os
NAMES = ('vision', 'awareness', 'clarity', 'reaction', 'focus', 'instinct', 'anticipation', 'judgment')
BLEND, CENTER_IN, GAIN, JITTER = .5, .85, 1.5, .05      # [P]
CENTER_OUT = float(os.environ.get('PRISM_RATING_CENTER', '.7'))      # [C] DreLen, 1 Nov: .7 is the league-average rating (override only for sweeps)
NEUTRAL = {k: CENTER_OUT for k in NAMES}                              # an athlete with no table entry is league average, not below it
POSITION_OFFSETS = {}      # {'SCT': {'vision': +.1, ...}, ...}  authored by the designer; empty = no specialisation
LO, HI = .05, .98

def _unit(v):
    v = float(v); return v / 100. if v > 1.5 else v

def derive(pid, overall, pocket_awareness, position=None, row=None):
    """row: optional dict of authored columns (prism_vision ...).  Returns dict of the eight ratings in [LO, HI]."""
    base = BLEND * _unit(overall) + (1. - BLEND) * _unit(pocket_awareness)
    out = {}
    for k in NAMES:
        if row and row.get('prism_' + k) not in (None, ''):
            out[k] = max(0., min(1., _unit(row['prism_' + k]))); continue
        j = random.Random(zlib.crc32(('%s|%s' % (pid, k)).encode())).gauss(0., JITTER)
        off = POSITION_OFFSETS.get(position, {}).get(k, 0.)
        out[k] = max(LO, min(HI, CENTER_OUT + GAIN * (base - CENTER_IN) + off + j))
    return out

def assign(over, names, rows=None):
    """over: roster overrides {pid: attrs}; names: {pid: {'overall', 'position', ...}}; rows: optional {pid: authored columns}.  Returns {pid: ratings}."""
    return {pid: derive(pid, names[pid].get('overall', .8), over.get(pid, {}).get('awareness', 80.), names[pid].get('position'), (rows or {}).get(pid)) for pid in names}
