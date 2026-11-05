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
# Judgment split (DreLen, 4 Nov): situation-specific judgement ratings.  'judgment' stays as the general decision-cadence driver (options considered, decision interval) = mean of these nine,
# unless authored.  A consumer asks rj(ratings, kind); a ratings dict that lacks a kind (an old authored table, the global PRISM_FIELD_RATINGS override) falls back to 'judgment'.
JUDGE = ('playmaking', 'finishing', 'marking', 'zone_reads', 'goalkeeping', 'air_pursuit', 'live_pursuit', 'carrier_duel', 'defender_duel')
JUDGE_LABEL = {'playmaking': 'Playmaking (passing judgement)', 'finishing': 'Finishing (scoring judgement)', 'marking': 'Marking (individual defence judgement)', 'zone_reads': 'Zone Reads (spatial defence judgement)',
               'goalkeeping': 'Goalkeeping (Keeper judgement)', 'air_pursuit': 'In-Air Ball Pursuit (pass tracking and contest judgement, both sides)', 'live_pursuit': 'Live Ball Pursuit (loose ground ball tracking and contest judgement, both sides)',
               'carrier_duel': 'Carrier Duel (ball carrier judgement in a duel)', 'defender_duel': 'Defender Duel (defender judgement in a duel)'}
ALL = NAMES + JUDGE
def rj(rt, kind):
    """the judgement rating of the given kind from a ratings dict, falling back to the general 'judgment' and then to league average"""
    return rt.get(kind, rt.get('judgment', CENTER_OUT))
BLEND, CENTER_IN, GAIN, JITTER = .5, .85, 1.5, .05      # [P]
CENTER_OUT = float(os.environ.get('PRISM_RATING_CENTER', '.7'))      # [C] DreLen, 1 Nov: .7 is the league-average rating (override only for sweeps)
NEUTRAL = {k: CENTER_OUT for k in NAMES + JUDGE}                              # an athlete with no table entry is league average, not below it
POSITION_OFFSETS = {}      # {'SCT': {'vision': +.1, ...}, ...}  authored by the designer; empty = no specialisation
LO, HI = .05, .98

def _unit(v):
    v = float(v); return v / 100. if v > 1.5 else v

def derive(pid, overall, pocket_awareness, position=None, row=None):
    """row: optional dict of authored columns (prism_vision ...).  Returns dict of the eight ratings in [LO, HI]."""
    base = BLEND * _unit(overall) + (1. - BLEND) * _unit(pocket_awareness)
    out = {}
    for k in NAMES + JUDGE:
        if row and row.get('prism_' + k) not in (None, ''):
            out[k] = max(0., min(1., _unit(row['prism_' + k]))); continue
        j = random.Random(zlib.crc32(('%s|%s' % (pid, k)).encode())).gauss(0., JITTER)
        off = POSITION_OFFSETS.get(position, {}).get(k, 0.)
        out[k] = max(LO, min(HI, CENTER_OUT + GAIN * (base - CENTER_IN) + off + j))
    if not (row and row.get('prism_judgment') not in (None, '')): out['judgment'] = sum(out[k] for k in JUDGE) / len(JUDGE)
    return out

def assign(over, names, rows=None):
    """over: roster overrides {pid: attrs}; names: {pid: {'overall', 'position', ...}}; rows: optional {pid: authored columns}.  Returns {pid: ratings}."""
    return {pid: derive(pid, names[pid].get('overall', .8), over.get(pid, {}).get('awareness', 80.), names[pid].get('position'), (rows or {}).get(pid)) for pid in names}
