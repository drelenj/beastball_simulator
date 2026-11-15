"""TACTICS-0 roster generator and slot-assignment rule (reference implementation).

Pure Python, no simulator import. PLACEHOLDER throughout: the generator draws from the
"usual ranges" design envelope (owner amendment, 14 Nov 2026), which is not canon.

  python3 audit/tactics/tools/roster_tools.py roster 1001        # print one generated roster
  python3 audit/tactics/tools/roster_tools.py assign ARC 1001    # assign it to a style
  python3 audit/tactics/tools/roster_tools.py staffing 2000      # staffing arithmetic over N rosters
"""
import json
import random
import sys

from tactics_src import BODY, ENVELOPE, RATINGS, T

GENERATOR_VERSION = 'tactics0-roster-gen/1'
N_FIELD, N_KEEPER, N_ARCHER = 18, 2, 2      # 22 gameday players; canon requires a reserve Keeper and Archer
LO, HI = ENVELOPE['professional_band']
H_LO, H_HI = ENVELOPE['height_m']
M_LO, M_HI = ENVELOPE['mass_kg']


def generate(seed):
    """22 athletes. Every rating independent uniform on the professional band; height and mass
    independent uniform on the body ranges. One stream per roster seed, drawn in a fixed order."""
    rng = random.Random(f'{GENERATOR_VERSION}/{int(seed)}')
    out = []
    for role, n, tag in (('field', N_FIELD, 'F'), ('keeper', N_KEEPER, 'K'), ('archer', N_ARCHER, 'A')):
        for i in range(1, n + 1):
            p = {'id': f'{tag}{i:02d}', 'role': role}
            for r in RATINGS:
                p[r] = round(rng.uniform(LO, HI), 3)
            p['height_m'] = round(rng.uniform(H_LO, H_HI), 3)
            p['mass_kg'] = round(rng.uniform(M_LO, M_HI), 1)
            out.append(p)
    return out


def flat_average():
    """The all-average roster: every rating at the middle of the professional band, body mid-range."""
    out = []
    for role, n, tag in (('field', N_FIELD, 'F'), ('keeper', N_KEEPER, 'K'), ('archer', N_ARCHER, 'A')):
        for i in range(1, n + 1):
            p = {'id': f'{tag}{i:02d}', 'role': role, 'height_m': (H_LO + H_HI) / 2, 'mass_kg': (M_LO + M_HI) / 2}
            p.update({r: (LO + HI) / 2 for r in RATINGS})
            out.append(p)
    return out


def _norm(key, value):
    """Body numbers on the same 0.60..1.00 scale as ratings, for scoring only."""
    if key == 'height_m':
        return LO + (HI - LO) * min(1., max(0., (value - H_LO) / (H_HI - H_LO)))
    if key == 'mass_kg':
        return LO + (HI - LO) * min(1., max(0., (value - M_LO) / (M_HI - M_LO)))
    return value


def score(player, prefers):
    return round(sum(w * _norm(k, player[k]) for k, w in prefers.items()), 6)


def shortfalls(player, requires):
    return {k: round(v - player[k], 3) for k, v in requires.items() if player[k] < v}


def assign(tactic, roster):
    """Assign by rating band from a supplied roster.

    1. Keeper and Archer slots take the best-scoring athlete of that role (canon: fixed roles).
    2. Field slot instances are listed in the tactic's slot order (its priority order).
    3. In-band placement: a maximum matching between instances and the field athletes who meet
       every `requires` minimum (augmenting paths, instances in priority order, candidates in
       descending slot score, ties by roster order). No in-band placement is lost to an
       earlier greedy choice.
    4. Instances still empty take the best-scoring unassigned field athlete, flagged under band.
    5. Status: BROKEN if any slot has fewer in-band instances than its fail_below_in_band;
       else FULL if every instance is in band; else DEGRADED.
    Deterministic: same roster and tactic give the same assignment.
    """
    by_role = {r: [p for p in roster if p['role'] == r] for r in ('field', 'keeper', 'archer')}
    order = {p['id']: i for i, p in enumerate(roster)}
    placed, rows = {}, []
    inst = []
    for s in tactic['slots']:
        if s['role'] != 'field':
            pool = by_role[s['role']]
            best = max(pool, key=lambda p: (score(p, s['prefers']), -order[p['id']])) if pool else None
            rows.append((s, 1, best))
            continue
        inst += [(s, i + 1) for i in range(s['count'])]
    field = by_role['field']
    elig = {}
    for n, (s, i) in enumerate(inst):
        c = [p for p in field if not shortfalls(p, s['requires'])]
        c.sort(key=lambda p: (-score(p, s['prefers']), order[p['id']]))
        elig[n] = [p['id'] for p in c]
    match = {}                                   # athlete id -> instance index

    def try_place(n, seen):
        for pid in elig[n]:
            if pid in seen:
                continue
            seen.add(pid)
            if pid not in match or try_place(match[pid], seen):
                match[pid] = n
                return True
        return False

    for n in range(len(inst)):
        try_place(n, set())
    holder = {n: pid for pid, n in match.items()}
    used = set(holder.values())
    byid = {p['id']: p for p in roster}
    for n, (s, i) in enumerate(inst):
        if n in holder:
            rows.append((s, i, byid[holder[n]]))
            continue
        free = [p for p in field if p['id'] not in used]
        best = max(free, key=lambda p: (score(p, s['prefers']), -order[p['id']])) if free else None
        if best:
            used.add(best['id'])
        rows.append((s, i, best))
    result, in_band = [], {}
    for s, i, p in rows:
        short = shortfalls(p, s['requires']) if p else {'no_player': 1}
        in_band[s['id']] = in_band.get(s['id'], 0) + (0 if short else 1)
        result.append({'slot': s['id'], 'instance': i, 'athlete': p['id'] if p else None,
                       'in_band': not short, 'shortfalls': short,
                       'score': score(p, s['prefers']) if p else None})
    broken = [s['id'] for s in tactic['slots']
              if in_band.get(s['id'], 0) < s['understaffed']['fail_below_in_band']]
    under = [r for r in result if not r['in_band']]
    status = 'BROKEN' if broken else 'FULL' if not under else 'DEGRADED'
    starters = {r['athlete'] for r in result}
    bench = [p['id'] for p in roster if p['id'] not in starters]
    return {'tactic': tactic['id'], 'status': status, 'broken_slots': broken,
            'in_band_by_slot': in_band, 'field_in_band': sum(1 for r in result if r['in_band'] and
                                                               r['slot'] not in ('KEEPER', 'ARCHER')),
            'assignment': result, 'bench': bench}


def staffing(n=2000, first_seed=1):
    """Arithmetic on the bands under the placeholder generator. Not a statement about play."""
    table = {}
    for t in T:
        c = {'FULL': 0, 'DEGRADED': 0, 'BROKEN': 0}
        field_in_band = 0
        broke = {}
        for seed in range(first_seed, first_seed + n):
            a = assign(t, generate(seed))
            c[a['status']] += 1
            field_in_band += a['field_in_band']
            for b in a['broken_slots']:
                broke[b] = broke.get(b, 0) + 1
        flat = assign(t, flat_average())
        table[t['id']] = {
            'rosters': n,
            'not_broken_rate': round((c['FULL'] + c['DEGRADED']) / n, 3),
            'full_rate': round(c['FULL'] / n, 3),
            'broken_rate': round(c['BROKEN'] / n, 3),
            'mean_field_slots_in_band_of_10': round(field_in_band / n, 2),
            'broken_by_slot_rate': {k: round(v / n, 3) for k, v in sorted(broke.items())},
            'flat_average_roster': {'status': flat['status'], 'broken_slots': flat['broken_slots'],
                                    'field_slots_in_band_of_10': flat['field_in_band']},
            'failure_slots': [s['id'] for s in t['slots'] if s['understaffed']['mode'] == 'failure'],
        }
    return {'generator': GENERATOR_VERSION, 'first_seed': first_seed, 'tactics': table}


if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else 'staffing'
    if cmd == 'roster':
        print(json.dumps(generate(int(sys.argv[2])), indent=1))
    elif cmd == 'assign':
        t = next(x for x in T if x['id'] == sys.argv[2])
        print(json.dumps(assign(t, generate(int(sys.argv[3]))), indent=1))
    else:
        print(json.dumps(staffing(int(sys.argv[2]) if len(sys.argv) > 2 else 2000), indent=1))
