"""Validate audit/tactics/tactics_0.json: schema, classification completeness (V2),
canon limits on values and positions (V1), and internal consistency.

  python3 audit/tactics/tools/validate.py

Exits non-zero on any failure. No simulator run. The PolicyParams check loads
native/emergence/params.py from the Native v0/3 branch with `git show` if the ref exists.
"""
import json
import math
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
NATIVE_REF = 'origin/claude/native-v0-3-handoff-69stxd'
FAIL, NOTE = [], []


def check(ok, msg):
    if not ok:
        FAIL.append(msg)
    return ok


def in_range(spec, v, slots):
    t, r = spec['type'], spec['range']
    if t in ('number', 'integer'):
        return isinstance(v, (int, float)) and not isinstance(v, bool) and r[0] <= v <= r[1] and (t == 'number' or v == int(v))
    if t == 'boolean':
        return isinstance(v, bool)
    if t == 'enum':
        return v in r
    if t == 'band':
        return isinstance(v, list) and len(v) == 2 and r[0] <= v[0] <= v[1] <= r[1]
    if t == 'weights':
        ok = isinstance(v, dict) and sorted(v) == sorted(r['keys']) and all(r['each'][0] <= x <= r['each'][1] for x in v.values())
        return ok and (not r.get('sum') or abs(sum(v.values()) - r['sum']) < 1e-9)
    if t == 'object':
        if not isinstance(v, dict) or sorted(v) != sorted(r['keys']):
            return False
        if 'enum' in r:
            return all(x in r['enum'] for x in v.values())
        return all(r['each'][0] <= x <= r['each'][1] for x in v.values())
    if t == 'slot':
        return v in slots
    if t == 'slot_or_nearest':
        return v == 'nearest' or v in slots
    return False


def box_min_dist(u, v, mirror, px, py):
    """Smallest distance from point (px, py) to the anchor box; a mirrored band is |v| in [lo, hi]."""
    boxes = [(u, v)] if not mirror else [(u, v), (u, [-v[1], -v[0]])]
    best = 1e9
    for (u0, u1), (v0, v1) in boxes:
        dx = max(u0 - px, 0, px - u1)
        dy = max(v0 - py, 0, py - v1)
        best = min(best, math.hypot(dx, dy))
    return best


def main():
    data = json.loads((OUT / 'tactics_0.json').read_text())
    schema = json.loads((OUT / 'tactics_0.schema.json').read_text())
    import jsonschema
    errs = sorted(jsonschema.Draft202012Validator(schema).iter_errors(data), key=lambda e: list(e.path))
    for e in errs[:20]:
        FAIL.append(f'schema: {list(e.path)}: {e.message[:160]}')
    cat = data['parameter_catalog']
    slot_keys = set(data['slot_level_parameters'])
    team_keys = set(cat) - slot_keys
    env = data['design_envelope']
    ratings, body = set(data['ratings']), set(data['body'])
    classes = set(data['classes'])
    # ---- V2: every parameter classified, with a reason
    for k, c in cat.items():
        check(c['class'] in classes, f'{k}: class {c["class"]!r} unknown')
        check(len(c['reason']) >= 10, f'{k}: no reason')
        if c['class'] == 'EXPRESSIBLE NOW':
            check(bool(c['route']), f'{k}: EXPRESSIBLE NOW without a route')
    check(not any('kick' in k for k in cat), 'a kicking parameter exists (canon: no kicking)')
    ids = [t['id'] for t in data['tactics']]
    check(len(set(ids)) == 8, 'tactic ids not unique')
    tags = {x for t in data['tactics'] for x in t['tags']}
    for need in ('deep_throws', 'carries', 'archer', 'keeper_zone_5s_exploit'):
        check(need in tags, f'required style missing: {need}')
    for t in data['tactics']:
        tid = t['id']
        slots = {s['id'] for s in t['slots']}
        tp = t['team_parameters']
        check(set(tp) == team_keys, f'{tid}: team parameters differ from catalogue: {sorted(set(tp) ^ team_keys)}')
        for k, v in tp.items():
            if k in cat and not (v is None and cat[k]['type'] == 'slot'):
                check(in_range(cat[k], v, slots), f'{tid}: {k}={v!r} outside its range')
        check(tp['hunt.contestant_slot'] in slots, f'{tid}: Hunt contestant slot missing')
        # canon limits on values
        check(tp['zone.dwell_max_s'] < 5, f'{tid}: zone dwell not under the 5 s limit')
        check(max(tp['tempo.snap_delay_s'].values()) < 10, f'{tid}: snap delay not inside the 10 s window')
        check(tp['tempo.shot_window_s'][1] <= 30 - 0, f'{tid}: shot window beyond the 30 s clock')
        check(tp['tempo.shot_window_s'][1] + 0 <= 30 and tp['tempo.must_shoot_remaining_s'] > 0, f'{tid}: no shot before expiry')
        check(tp['subs.policy'] == 'cover_only', f'{tid}: substitutions used tactically')
        for name in (tp['restart.scrim_play'], tp['restart.snap40_play'], tp['restart.toss_play'], 'def:' + tp['restart.def_alignment']):
            check(name in data['plays'], f'{tid}: play {name} undefined')
        # roster shape
        check(sum(s['count'] for s in t['slots'] if s['role'] == 'field') == 10, f'{tid}: field instances != 10')
        check([s['count'] for s in t['slots'] if s['role'] == 'keeper'] == [1], f'{tid}: not exactly one Keeper')
        check([s['count'] for s in t['slots'] if s['role'] == 'archer'] == [1], f'{tid}: not exactly one Archer')
        for s in t['slots']:
            sid = f'{tid}.{s["id"]}'
            for k, v in s['requires'].items():
                check(k in ratings | body, f'{sid}: unknown requirement {k}')
                lo, hi = env[k] if k in body else env['professional_band']
                check(lo <= v <= hi, f'{sid}: {k} {v} outside the envelope')
            check(set(s['prefers']) <= ratings | body and abs(sum(s['prefers'].values()) - 1) < 1e-9, f'{sid}: prefers do not sum to 1')
            u = s['understaffed']
            check((u['mode'] == 'failure') == (u['fail_below_in_band'] > 0) and u['fail_below_in_band'] <= s['count'], f'{sid}: failure mode inconsistent')
            for k, v in s['overrides'].items():
                check(k in team_keys and in_range(cat[k], v, slots), f'{sid}: override {k}={v!r} invalid')
            if s['role'] != 'field':
                continue
            for ph, a in s['anchors'].items():
                w, ty = f'{sid}.{ph}', a['type']
                if ty == 'goal_arc':
                    # nobody is stationed inside either Keeper Zone (attackers: 5 s; defenders: only within 5 m of an attacker)
                    check(a['range_m'][0] >= 20.5, f'{w}: stationed inside a Keeper Zone')
                    check((a['goal'] == 'attacked') == (ph == 'offence'), f'{w}: arc about the wrong goal')
                if ty == 'zone_cycle':
                    check(a['inside_range_m'][1] < 20 and a['outside_range_m'][0] >= 20.5 and ph == 'offence', f'{w}: zone cycle geometry')
                if ty == 'pair':
                    check(a['with_slot'] in slots and a['min_range_from_goal_m'] >= 20.5, f'{w}: pair anchor')
                if ty == 'field':
                    m = a['spread'] == 'mirror'
                    check(box_min_dist(a['u_m'], a['v_m'], m, 0, 0) >= 20 and box_min_dist(a['u_m'], a['v_m'], m, 100, 0) >= 20, f'{w}: field anchor inside a Keeper Zone')
                    if ph == 'hunt':
                        check(a['u_m'][1] <= 50, f'{w}: Hunt anchor beyond the own half')
                        check(box_min_dist(a['u_m'], a['v_m'], m, 50, 0) >= 7, f'{w}: Hunt anchor within 7 m of the centre spot')
                if ph == 'restart_own':
                    check(ty == 'line_rel' and a['du_m'][1] <= -0.8, f'{w}: not onside behind the ball line')
                if ph == 'restart_opp':
                    check(ty == 'line_rel' and a['du_m'][1] <= -5.5, f'{w}: within 5 m of the line before live')
                if ph == 'hunt':
                    check(ty in ('field', 'rule'), f'{w}: Hunt anchor type')
                if ph in ('offence', 'defence'):
                    check(ty != 'line_rel', f'{w}: restart anchor in live play')
    # ---- matchups
    pairs = {frozenset((m['a'], m['b'])) for m in data['matchup_hypotheses']}
    check(len(pairs) == 28 and all(len(p) == 2 and p <= set(ids) for p in pairs), 'matchups do not cover the 28 pairs')
    for m in data['matchup_hypotheses']:
        check(m['predicted_edge'] in (m['a'], m['b'], None), f'matchup {m["a"]}-{m["b"]}: bad edge')
    for t in data['tactics']:
        mm = t['matchups']
        check(len(mm['edge_over']) + len(mm['struggles_against']) + len(mm['no_prediction']) == 7, f'{t["id"]}: matchups not 7')
    # ---- distinctness (styles must differ in method, not in name)
    diff = {}
    for i, a in enumerate(data['tactics']):
        for b in data['tactics'][i + 1:]:
            n = sum(1 for k in team_keys if a['team_parameters'][k] != b['team_parameters'][k])
            diff[f'{a["id"]}-{b["id"]}'] = n
            check(n >= 8, f'{a["id"]} and {b["id"]} differ in only {n} team parameters')
            check({s['id'] for s in a['slots']} & {s['id'] for s in b['slots']} <= {'KEEPER', 'ARCHER'}, f'{a["id"]} and {b["id"]} share a field slot')
    check(len({t['team_parameters']['def.scheme'] for t in data['tactics']}) == 8, 'defensive schemes not all different')
    # ---- EXPRESSIBLE NOW projection against the real Native v0/3 PolicyParams
    try:
        src = subprocess.run(['git', 'show', f'{NATIVE_REF}:native/emergence/params.py'], capture_output=True, text=True, check=True, cwd=OUT).stdout
        ns = {'__name__': 'native_params'}
        exec(compile(src, 'params.py', 'exec'), ns)
        for t in data['tactics']:
            try:
                ns['PolicyParams'].from_dict(t['policy_params_projection'])
            except Exception as e:
                FAIL.append(f'{t["id"]}: projection rejected by Native PolicyParams: {e}')
        routes = {c['route'].split('.')[1] for c in cat.values() if c['route'] and c['route'].startswith('PolicyParams.')}
        check(routes == set(ns['NAMES']), f'PolicyParams routes differ from Native: {sorted(routes ^ set(ns["NAMES"]))}')
        NOTE.append('PolicyParams projections accepted by native/emergence/params.py at ' + NATIVE_REF)
    except subprocess.CalledProcessError:
        NOTE.append('PolicyParams check SKIPPED: Native ref not fetched')
    # ---- wording (V6): list every sensitive word for a human to read in context
    words = re.compile(r'\b(optimal|optimum|balanced|proven|proof|best|emerge\w*|dominan\w*|superior|guarantee\w*)\b', re.I)
    hits = []
    for name in ('TACTICS_0.md', 'PERSONNEL_PROFILES.md', 'tactics_0.json', 'TACTIC_INTERFACE.md', 'ATTRIBUTE_STEP_SPEC.md',
                 'TACTICS_0_TEST_PLAN.md', 'TACTICS_0_STATUS.md'):
        f = OUT / name
        if f.exists():
            for n, line in enumerate(f.read_text().splitlines(), 1):
                for m in words.finditer(line):
                    hits.append(f'{name}:{n}: ...{line[max(0, m.start() - 60):m.end() + 40].strip()}...')
    counts = {}
    for c in cat.values():
        counts[c['class']] = counts.get(c['class'], 0) + 1
    print(json.dumps({'status': 'FAIL' if FAIL else 'PASS', 'failures': FAIL, 'notes': NOTE,
                      'parameters': len(cat), 'by_class': counts,
                      'team_parameter_differences_min': min(diff.values()), 'team_parameter_differences': diff,
                      'sensitive_words_to_read_in_context': hits}, indent=1))
    sys.exit(1 if FAIL else 0)


if __name__ == '__main__':
    main()
