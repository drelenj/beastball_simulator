"""Beastball Physical Attribute Generation v1.0 (spec file in this folder).
Nine natural physical attributes, integers 65-100, from height, physique and ancestry shifts.
Pure functions; the caller supplies the RNG so morphology draws are never disturbed.
"""
import math, itertools, collections

ATTRS = ["Speed", "Strength", "Jumping", "Acceleration", "Agility", "Balance", "Throw Power", "Stamina", "Durability"]
TRIBES = ["Ly’Kun", "Shynän", "Dryqona", "Yubu", "Vygari", "Fefmial", "Psolari"]
REF, SD, LO, HI = 78, 7, 65, 100

HEIGHT_ANCHORS = [  # inches, then shifts in ATTRS order
    (72,  [-1, -5, +1, +3, +3, +2, -4, +2, -2]),
    (84,  [0, -2, +1, +1, +1, +1, -1, +1, -1]),
    (90,  [0, 0, 0, 0, 0, 0, 0, 0, 0]),
    (96,  [+1, +1, 0, -1, -1, 0, +1, 0, +1]),
    (108, [+1, +3, -1, -2, -2, -1, +3, -1, +2]),
    (120, [0, +5, -2, -3, -3, -2, +5, -2, +3]),
    (132, [-1, +7, -3, -4, -4, -3, +6, -3, +4]),
    (144, [-2, +8, -4, -5, -5, -4, +7, -4, +5]),
]
PHYSIQUE_SHIFT = {  # ATTRS order
    "Compact":  [+1, -3, +2, +3, +3, +3, -2, +2, -2],
    "Lean":     [+3, -3, +2, +3, +2, +1, -2, +3, -2],
    "Lanky":    [+3, -2, +3, +1, +1, -1, +2, +2, -2],
    "Stocky":   [-1, +2, 0, +1, +1, +3, 0, 0, +2],
    "Athletic": [0, 0, 0, 0, 0, 0, 0, 0, 0],
    "Rangy":    [+2, 0, +2, 0, +1, -1, +3, +1, 0],
    "Bulky":    [-3, +4, -2, -3, -2, +2, +1, -2, +4],
    "Powerful": [-1, +4, +1, -1, -1, +1, +3, -1, +3],
    "Hulking":  [-2, +4, 0, -3, -3, -2, +4, -2, +3],
}
# affinity matrix rows = ATTRS, columns = TRIBES (Ly’Kun, Shynän, Dryqona, Yubu, Vygari, Fefmial, Psolari)
_M = {
    "Speed":        "S P - - - S -",
    "Strength":     "- - P P S - S",
    "Jumping":      "P S S S - S S",
    "Acceleration": "S P - - - S P",
    "Agility":      "S S S - P P -",
    "Balance":      "S S S S P P -",
    "Throw Power":  "- - S S S - S",
    "Stamina":      "P S - P S S S",
    "Durability":   "- - P S S - P",
}
AFFINITY = {t: {a: _M[a].split()[i] for a in ATTRS} for i, t in enumerate(TRIBES)}
for _t in TRIBES:
    _c = collections.Counter(AFFINITY[_t].values())
    assert (_c["P"], _c["S"], _c["-"]) == (2, 4, 3), (_t, _c)
for _a in ATTRS:
    assert sum(AFFINITY[t][_a] == "P" for t in TRIBES) <= 2, _a

# (primary slots, primary shift, secondary slots, secondary shift, neutral slots) by ancestry count
BONUS = {1: (2, 5, 4, 2, 3), 2: (2, 5, 5, 2, 2), 3: (3, 4, 5, 2, 1), 4: (4, 3, 5, 1, 0)}

def height_shift(h_in):
    a = HEIGHT_ANCHORS
    if not a[0][0] <= h_in <= a[-1][0]: raise ValueError(f"height {h_in} outside 72-144 in")
    for (h0, v0), (h1, v1) in zip(a, a[1:]):
        if h0 <= h_in <= h1:
            return [x0 + (h_in - h0) * (x1 - x0) / (h1 - h0) for x0, x1 in zip(v0, v1)]

def _primaries(tribes):
    return {t: [x for x in ATTRS if AFFINITY[t][x] == "P"] for t in tribes}

def primary_assignments(tribes):
    """All ways each tribe passes exactly one of its primaries, with distinct attributes (no stacking)."""
    prim = _primaries(tribes)
    out = []
    for combo in itertools.product(*[prim[t] for t in tribes]):
        if len(set(combo)) == len(combo): out.append(dict(zip(tribes, combo)))
    return out

def secondary_candidates(tribes, primaries):
    """attribute -> number of contributing tribes that support it (S, or an unselected P), excluding chosen primaries."""
    sup = {}
    for a in ATTRS:
        if a in primaries: continue
        n = sum(AFFINITY[t][a] in ("P", "S") for t in tribes)
        if n: sup[a] = n
    return sup

def feasibility(tribes):
    """Return (ok, reason). ok iff some one-primary-per-tribe distinct assignment exists and enough supported secondaries exist."""
    n = len(tribes); pslots, _, sslots, _, _ = BONUS[n]
    asg = primary_assignments(tribes)
    if not asg: return False, "no distinct one-primary-per-tribe assignment"
    best = max(len(secondary_candidates(tribes, set(x.values()))) for x in asg)
    if best < sslots: return False, f"only {best} supported secondary attributes for {sslots} slots"
    return True, ""

def ancestry_profile(tribes, rng):
    """Return (shift dict, label dict, secondary_shortfall). Draws only from rng.
    Infeasible combinations get the supported secondaries available; the shortfall stays neutral and is reported (never silently filled)."""
    tribes = sorted(tribes, key=TRIBES.index)
    n = len(tribes); pslots, pshift, sslots, sshift, _ = BONUS[n]
    if n == 1:
        t = tribes[0]
        lab = {a: AFFINITY[t][a] for a in ATTRS}
        return {a: (pshift if lab[a] == "P" else sshift if lab[a] == "S" else 0) for a in ATTRS}, dict(lab), 0
    ok, why = feasibility(tribes)
    allasg = primary_assignments(tribes)
    if not allasg: raise ValueError("no distinct primary assignment for " + "/".join(tribes))
    # Feasible: choose among assignments that can fill every secondary slot.
    # Infeasible: choose among assignments that maximise supported secondaries; the shortfall stays NEUTRAL and is flagged.
    best = max(len(secondary_candidates(tribes, set(x.values()))) for x in allasg)
    need_total = sslots if ok else best
    cands = [x for x in allasg if len(secondary_candidates(tribes, set(x.values()))) >= need_total]
    asg = cands[rng.randrange(len(cands))]
    prim = set(asg.values())
    sup = secondary_candidates(tribes, prim)
    chosen = []
    for level in sorted(set(sup.values()), reverse=True):   # favour attributes supported by more ancestries
        grp = sorted(a for a, v in sup.items() if v == level)
        need = need_total - len(chosen)
        if need <= 0: break
        if len(grp) <= need: chosen += grp
        else:
            rng.shuffle(grp); chosen += grp[:need]
    shift, lab = {}, {}
    for a in ATTRS:
        if a in prim: shift[a], lab[a] = pshift, "P"
        elif a in chosen: shift[a], lab[a] = sshift, "S"
        else: shift[a], lab[a] = 0, "-"
    assert sum(v == "P" for v in lab.values()) == pslots and sum(v == "S" for v in lab.values()) == need_total
    return shift, lab, (sslots - need_total)

def _phi(x): return 0.5 * (1 + math.erf(x / math.sqrt(2)))
def pmf(mu):
    w = [_phi((k + 0.5 - mu) / SD) - _phi((k - 0.5 - mu) / SD) for k in range(LO, HI + 1)]
    s = sum(w); return [x / s for x in w]

def sample_rating(rng, mu):
    u = rng.random(); acc = 0.0
    p = pmf(mu)
    for k, x in zip(range(LO, HI + 1), p):
        acc += x
        if u < acc: return k
    return HI

def generate_physical(height_in, physique, tribes, rng, elite_shift=0, elite_floor=0):
    hs = height_shift(height_in); ps = PHYSIQUE_SHIFT[physique]
    ash, lab, short = ancestry_profile(tribes, rng)
    out = {}
    for i, a in enumerate(ATTRS):
        mu = REF + hs[i] + ps[i] + ash[a] + elite_shift  # elite_shift: owner lock, applied to the size baseline before tribal bonus
        out[a] = dict(mu=mu, elite_shift=elite_shift, height_shift=hs[i], physique_shift=ps[i], ancestry_shift=ash[a], affinity=lab[a], rating=max(sample_rating(rng, mu), elite_floor))
    out['_shortfall'] = short
    return out
