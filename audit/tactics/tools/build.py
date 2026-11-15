"""Render TACTICS-0 deliverables from tactics_src.py.

  python3 audit/tactics/tools/build.py        # writes tactics_0.json, TACTICS_0.md, PERSONNEL_PROFILES.md

No simulator import. The staffing arithmetic uses roster_tools.py (2000 generated rosters).
"""
import json
from pathlib import Path

import roster_tools as RT
import tactics_src as S

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
N_STAFF = 2000
ABBR = {S.NOW: 'NOW', S.COORD: 'COORD', S.ENGINE: 'ENGINE'}


# ----------------------------------------------------------------------------- helpers
def num(x):
    if isinstance(x, float) and x == int(x):
        return str(int(x))
    return f'{x:g}' if isinstance(x, float) else str(x)


def band(b, unit=''):
    return f'{num(b[0])} to {num(b[1])}{unit}'


def describe(a):
    t = a['type']
    note = f" ({a['note']})" if a.get('note') else ''
    if t == 'rule':
        return a['text']
    if t == 'goal_arc':
        g = 'attacked goal' if a['goal'] == 'attacked' else 'own goal'
        lo, hi = a['bearing_deg']
        if a['spread'] == 'mirror':
            b = f'{num(lo)} to {num(hi)} degrees off centre, one each side'
        else:
            b = f'bearings {num(lo)} to {num(hi)} degrees, spread evenly'
        return f"{band(a['range_m'])} m from the {g}, {b}{note}"
    if t == 'ball_rel':
        du = a['du_m']
        where = ('ahead of' if du[0] >= 0 else 'behind' if du[1] <= 0 else 'around')
        d = band([abs(du[1]), abs(du[0])] if du[1] <= 0 else du)
        if where == 'around':
            d = f'{num(-du[0])} m behind to {num(du[1])}'
            where = 'ahead of'
        lat = (f"{band(a['dv_m'])} m to each side" if a['mirror'] else
               f"within {num(max(abs(a['dv_m'][0]), abs(a['dv_m'][1])))} m laterally")
        return f"{d} m {where} the ball, {lat}{note}"
    if t == 'field':
        if a['spread'] == 'mirror':
            lat = f"{band(a['v_m'])} m off the centre line, one each side"
        else:
            lat = f"lateral {band(a['v_m'])} m"
        return f"{band(a['u_m'])} m from the own goal line, {lat}{note}"
    if t == 'mark':
        tgt = {'carrier': 'the ball carrier', 'nearest_unmarked_opponent': 'the nearest unmarked opponent',
               'receiver_near_goal': 'the receiver nearest the goal'}[a['target']]
        side = {'goal_side': 'goal side', 'ball_side': 'ball side', 'lateral': 'to one side'}[a['side']]
        return f"marks {tgt}, {side}, at {band(a['gap_m'])} m{note}"
    if t == 'line_rel':
        du = a['du_m']
        lat = (f"{band(a['dv_m'])} m to each side" if a['mirror'] else
               f"lateral {band(a['dv_m'])} m")
        return f"{band([abs(du[1]), abs(du[0])])} m behind the line, {lat}{note}"
    if t == 'pair':
        return (f"{band(a['gap_m'])} m goal-side of a paired {a['with_slot']}, never closer than "
                f"{num(a['min_range_from_goal_m'])} m to the goal{note}")
    if t == 'zone_cycle':
        return (f"in and out: inside at {band(a['inside_range_m'])} m from the attacked goal (bearings "
                f"{band(a['bearing_deg'])} degrees) for at most the dwell time, then out to "
                f"{band(a['outside_range_m'])} m{note}")
    raise ValueError(t)


def needs_text(req):
    if not req:
        return 'none'
    parts = []
    for k, v in req.items():
        if k == 'mass_kg':
            parts.append(f'mass {num(v)} kg or more')
        elif k == 'height_m':
            parts.append(f'height {v:.2f} m or more')
        else:
            parts.append(f"{k.replace('_', ' ')} {v:.2f} or more")
    return ', '.join(parts)


def val(key, v):
    if isinstance(v, dict):
        return ', '.join(f"{k.replace('_', ' ')} {num(x) if not isinstance(x, str) else x}" for k, v2 in [(0, 0)] for k, x in v.items())
    if isinstance(v, list):
        return band(v)
    if isinstance(v, bool):
        return 'yes' if v else 'no'
    if v is None:
        return 'none'
    return num(v) if not isinstance(v, str) else v.replace('_', ' ')


def projection(team):
    out = {}
    for k, c in S.CATALOG.items():
        if c['route'] and c['route'].startswith('PolicyParams.'):
            out[c['route'].split('.')[1]] = team[k]
    return out


def matchups_for(tid):
    over, under, opn = [], [], []
    for m in S.M:
        if tid not in (m['a'], m['b']):
            continue
        other = m['b'] if m['a'] == tid else m['a']
        if m['predicted_edge'] is None:
            opn.append({'vs': other, 'question': m['reason']})
        elif m['predicted_edge'] == tid:
            over.append({'vs': other, 'why': m['reason']})
        else:
            under.append({'vs': other, 'why': m['reason']})
    return {'edge_over': over, 'struggles_against': under, 'no_prediction': opn}


# ----------------------------------------------------------------------------- JSON
def build_json(staff):
    tactics = []
    for t in S.T:
        tactics.append({
            'id': t['id'], 'name': t['name'], 'tags': t['tags'], 'idea': t['idea'], 'formation': t['formation'],
            'slots': t['slots'], 'team_parameters': t['team'],
            'policy_params_projection': projection(t['team']),
            'signature': {k: {'op': v[0], 'value': v[1]} for k, v in t['signature'].items()},
            'strengths': t['strengths'], 'weaknesses': t['weaknesses'], 'canon_checks': t['canon'],
            'matchups': matchups_for(t['id']),
            'staffing_arithmetic': staff['tactics'][t['id']],
        })
    return {
        'schema_version': S.SCHEMA_VERSION,
        'status': 'HYPOTHESES. DESIGN COMPLETE only: not IMPLEMENTED, not TESTED, not ACCEPTED. No value here '
                  'has been searched or tuned and no claim of quality is made.',
        'generated_from': 'audit/tactics/tools/tactics_src.py (edit the source, then run build.py)',
        'classified_against': S.TARGET,
        'design_envelope': S.ENVELOPE,
        'ratings': list(S.RATINGS), 'body': list(S.BODY),
        'conventions': {
            'frame': 'Each team uses its own frame: u = metres from its own goal line toward the attacked goal '
                     '(0 to 100); v = lateral metres from the centre line, positive to the right when facing the '
                     'attacked goal (-50 to 50).',
            'goal_arc': 'Polar about a goal centre. range_m = distance from the goal centre. bearing_deg: 0 is '
                        'straight out from the goal toward midfield, positive to the right as the team faces its '
                        'attacked goal.',
            'ball_rel': 'Relative to the athlete\'s believed ball position. du_m positive = toward the attacked '
                        'goal. dv_m = lateral.',
            'line_rel': 'At a restart, relative to the restraining line: the ball line at a tackle or turnover '
                        'scrimmage; at a 40 m scrimmage, the ball line for the restarting team and its own 40 m '
                        'line for the defending team. du_m negative = on the athlete\'s own side.',
            'mirror': 'With mirror or spread "mirror", the lateral or bearing band is a magnitude and instances '
                      'are placed on both sides.',
            'toss_in': 'At a toss-in slots use their live-play anchors, with opponents 3 m clear of the spot.',
            'beliefs': 'Every anchor is evaluated by the athlete from his own believed positions. No anchor is a '
                       'position the engine places anyone at.',
            'bands': 'ELITE 0.90 or more; KEY 0.85 or more; SUPPORT 0.75 to 0.80; BASE 0.70. Body gates sit near '
                     'the middle of the range. A slot has one KEY rating, or two where the method needs both in '
                     'one body.',
        },
        'classes': S.CLASSES,
        'parameter_catalog': S.CATALOG,
        'slot_level_parameters': list(S.SLOT_KEYS),
        'assignment_rule': {
            'name': 'assign by rating band from a supplied roster',
            'class': S.CATALOG['assignment.rule']['class'],
            'input': 'A roster table: id, role (field, keeper, archer), the ratings on a 0 to 1 scale, height_m, '
                     'mass_kg. At least 10 field athletes, 1 keeper, 1 archer.',
            'steps': [
                'Keeper and Archer slots take the best-scoring athlete of that role. Field athletes never fill '
                'them (canon).',
                'Field slot instances are taken in the tactic\'s slot order, which is its priority order.',
                'An athlete is in band for a slot if he meets every minimum in requires.',
                'In-band placement is a maximum matching between instances and in-band athletes (augmenting '
                'paths; instances in priority order; candidates in descending slot score; ties by roster order), '
                'so no in-band placement is lost to an earlier choice.',
                'Slot score = sum over prefers of weight x rating, with height and mass rescaled to the 0.60 to '
                '1.00 band over the envelope ranges.',
                'An instance left empty takes the best-scoring unassigned field athlete and is flagged under '
                'band, with each shortfall listed.',
                'Status: BROKEN if any slot has fewer in-band instances than its fail_below_in_band; FULL if '
                'every instance is in band; otherwise DEGRADED.',
                'The remaining athletes are the bench. A substitute takes the slot of the athlete he replaces.',
            ],
            'reference_implementation': 'audit/tactics/tools/roster_tools.py: assign()',
            'deterministic': True,
        },
        'plays': S.PLAYS, 'restart_rules': S.RESTART_RULES,
        'tactics': tactics,
        'matchup_hypotheses': S.M,
        'staffing_arithmetic_note': f'Computed over {N_STAFF} rosters from roster_tools.generate (seeds 1 to '
                                    f'{N_STAFF}). It is arithmetic on the bands under a PLACEHOLDER generator, '
                                    'not a statement about how any style plays.',
    }


# ----------------------------------------------------------------------------- markdown
HEADLINE = [
    ('Ball movement', ['carrier.bias_pass', 'carrier.pass_min_clearance_m', 'carrier.pass_len_band_m',
                       'carrier.touch_time_max_s', 'carrier.dribble_use']),
    ('Scoring method', ['carrier.finish_pref', 'carrier.bias_shoot', 'carrier.shot_range_min_m',
                        'carrier.shot_range_max_m', 'carrier.shot_speed_frac']),
    ('Tempo and clock', ['tempo.shot_window_s', 'tempo.must_shoot_remaining_s', 'tempo.snap_delay_s',
                         'tempo.hold_own_half_until_remaining_s', 'off.first_action_max_s',
                         'off.short_field_trigger_m']),
    ('Carrier in contact', ['carrier.contact_response', 'carrier.first_tackle_bank_m']),
    ('Keeper Zone (attack)', ['zone.entry_mode', 'zone.dwell_max_s', 'zone.occupancy_target',
                              'zone.min_outside_s', 'zone.entry_stagger_s', 'block.wedge', 'screen.arrow_screen']),
    ('Tackle aggression', ['def.scheme', 'def.bias_press', 'def.pressers_max', 'def.press_line_m',
                           'def.commit_gap_m', 'def.contain_gap_m', 'def.takedown_line_m', 'def.contact_by_area',
                           'def.contact_at_count1', 'def.holdup_drive', 'def.bias_pursue']),
    ('Archer', ['archer.eagerness', 'archer.target_priority']),
    ('Keeper', ['keeper.depth_m', 'keeper.distribution']),
    ('Restarts', ['restart.scrim_play', 'restart.snap40_play', 'restart.toss_play', 'restart.def_alignment',
                  'restart.taker_slot']),
    ('Hunt', ['hunt.contestant_slot', 'hunt.win_action']),
    ('Positioning weights', ['pos.ball_att', 'pos.ball_def', 'pos.goal_att', 'pos.goal_def', 'pos.spread',
                             'pos.opp_att', 'pos.opp_def', 'pos.lane', 'pos.edge_zone']),
]
assert sorted(k for _, ks in HEADLINE for k in ks) == sorted(k for k in S.TEAM_KEYS if k != 'subs.policy')
NEUTRAL = S.base()
CORE = {'carrier.bias_pass', 'carrier.pass_len_band_m', 'carrier.finish_pref', 'carrier.shot_range_min_m',
        'carrier.shot_range_max_m', 'tempo.shot_window_s', 'tempo.must_shoot_remaining_s',
        'zone.entry_mode', 'zone.dwell_max_s', 'zone.occupancy_target', 'def.scheme', 'def.pressers_max',
        'def.press_line_m', 'def.commit_gap_m', 'def.contact_by_area', 'archer.eagerness',
        'archer.target_priority', 'restart.scrim_play', 'restart.snap40_play', 'restart.toss_play',
        'restart.def_alignment', 'hunt.contestant_slot', 'hunt.win_action'}


def neutral_md():
    L = ['| Area | Parameter | Neutral value | Tag |', '| --- | --- | --- | --- |']
    for area, keys in HEADLINE:
        for k in keys:
            L.append(f"| {area} | {short(k)} | {val(k, NEUTRAL[k])} | {ABBR[S.CATALOG[k]['class']]} |")
    return '\n'.join(L)
NAME = {t['id']: t['name'] for t in S.T}


def short(k):
    return k.split('.', 1)[1].replace('_', ' ')


def style_md(n, t, staff):
    L = [f"### {n}. {t['name']} ({t['id']})", '',
         f"**Idea.** {t['idea']}", '', f"**Formation.** {t['formation']}.", '',
         '**Slots and what each needs.**', '',
         '| Slot | Job | Needs (minimum bands) | If filled by a weaker player |', '| --- | --- | --- | --- |']
    for s in t['slots']:
        L.append(f"| {s['id']} x{s['count']} | {s['what']} | {needs_text(s['requires'])} | {s['understaffed']['effect']} |")
    L += ['', '**Where each slot stands.**', '',
          '| Slot | Offence | Defence | Own restart | Opponent restart | Hunt |', '| --- | --- | --- | --- | --- | --- |']
    for s in t['slots']:
        if s['role'] != 'field':
            continue
        a = s['anchors']
        L.append(f"| {s['id']} | " + ' | '.join(describe(a[p]) for p in S.PHASES) + ' |')
    L += ['', 'Keeper and Archer hold their fixed posts (Keeper inside his zone, Archer on the platform).', '',
          '**Tendencies.** The core parameters, plus every other parameter that differs from the neutral '
          'default of section 3 (differences in bold). Anything not listed is the neutral default. '
          'Tag: NOW = expressible now, COORD = needs coordination, ENGINE = needs engine work.', '',
          '| Area | Parameter | Value | Tag |', '| --- | --- | --- | --- |']
    for area, keys in HEADLINE:
        for k in keys:
            diff = t['team'][k] != NEUTRAL[k]
            if not diff and k not in CORE:
                continue
            v = val(k, t['team'][k])
            L.append(f"| {area} | {short(k)} | {'**' + v + '**' if diff else v} | {ABBR[S.CATALOG[k]['class']]} |")
    ov = [(s['id'], k, v) for s in t['slots'] for k, v in s['overrides'].items()]
    if ov:
        L += ['', 'Slot overrides: ' + '; '.join(f"{sid} uses {short(k)} = {val(k, v)}" for sid, k, v in ov) + '.']
    L += ['', '**Plays named above.** ' + ' '.join(
        f"*{p.replace('_', ' ')}*: {S.PLAYS[p]}" for p in dict.fromkeys(
            [t['team']['restart.scrim_play'], t['team']['restart.snap40_play'], t['team']['restart.toss_play']])),
          f"*Defensive alignment ({t['team']['restart.def_alignment'].replace('_', ' ')})*: "
          f"{S.PLAYS['def:' + t['team']['restart.def_alignment']]}", '',
          '**What the style should look like if it is being played** (checked before any result is read):', '']
    for k, (op, v) in t['signature'].items():
        vv = band(v) if isinstance(v, list) else num(v)
        L.append(f"- {k.replace('_', ' ')}: {op} {vv}")
    L += ['', '**Strengths (reasoned, untested).**', ''] + [f'- {x}' for x in t['strengths']]
    L += ['', '**Weaknesses (reasoned, untested).**', ''] + [f'- {x}' for x in t['weaknesses']]
    L += ['', '**Canon check.**', ''] + [f'- {x}' for x in t['canon']]
    m = matchups_for(t['id'])
    L += ['', '**Against the other seven (predictions to be tested, not results).**', '',
          '| Opponent | Prediction | Why |', '| --- | --- | --- |']
    for x in m['edge_over']:
        L.append(f"| {NAME[x['vs']]} | edge to {t['name']} | {x['why']} |")
    for x in m['struggles_against']:
        L.append(f"| {NAME[x['vs']]} | edge to {NAME[x['vs']]} | {x['why']} |")
    for x in m['no_prediction']:
        L.append(f"| {NAME[x['vs']]} | none | {x['question']} |")
    return '\n'.join(L) + '\n'


def matrix_md():
    ids = S.IDS
    L = ['| Row against column | ' + ' | '.join(ids) + ' |', '| --- |' + ' --- |' * len(ids)]
    look = {}
    for m in S.M:
        look[(m['a'], m['b'])] = look[(m['b'], m['a'])] = m['predicted_edge']
    for a in ids:
        row = []
        for b in ids:
            if a == b:
                row.append('.')
            else:
                e = look[(a, b)]
                row.append('?' if e is None else '+' if e == a else '-')
        L.append(f'| {a} | ' + ' | '.join(row) + ' |')
    return '\n'.join(L)


def catalog_md():
    L = ['| Parameter | Meaning | Range | Class | Reason |', '| --- | --- | --- | --- | --- |']
    for k, c in S.CATALOG.items():
        r = c['range']
        if isinstance(r, dict):
            rr = ', '.join(r['keys'])
            if 'enum' in r:
                rr += ': ' + ' / '.join(r['enum'])
            elif 'each' in r:
                rr += f": each {band(r['each'])}" + (', sum 1' if r.get('sum') else '')
        elif isinstance(r, list) and r and isinstance(r[0], str):
            rr = ' / '.join(r)
        elif isinstance(r, list):
            rr = band(r) + (f" {c['unit']}" if c['unit'] else '')
        else:
            rr = c['type']
        L.append(f"| `{k}` | {c['meaning']} | {rr} | {c['class']} | {c['reason']} |")
    return '\n'.join(L)


def class_counts():
    out = {}
    for c in S.CATALOG.values():
        out[c['class']] = out.get(c['class'], 0) + 1
    return out


def personnel_md(staff):
    L = []
    for n, t in enumerate(S.T, 1):
        st = staff['tactics'][t['id']]
        L += [f"### {n}. {t['name']} ({t['id']})", '',
              '| Slot | Rating bands needed | Ranked by | Mode | If filled by a weaker player |',
              '| --- | --- | --- | --- | --- |']
        for s in t['slots']:
            mode = (f"FAILURE below {s['understaffed']['fail_below_in_band']} in band"
                    if s['understaffed']['mode'] == 'failure' else 'graceful')
            pref = ', '.join(f"{k.replace('_m', '').replace('_kg', '').replace('_', ' ')} {w:g}"
                             for k, w in s['prefers'].items())
            L.append(f"| {s['id']} x{s['count']} | {needs_text(s['requires'])} | {pref} | {mode} | "
                     f"{s['understaffed']['effect']} |")
        fl = st['flat_average_roster']
        bs = ', '.join(f'{k} {v:.0%}' for k, v in st['broken_by_slot_rate'].items()) or 'none'
        L += ['', f"Staffing arithmetic over {st['rosters']} generated rosters: not broken {st['not_broken_rate']:.0%}, "
              f"fully in band {st['full_rate']:.0%}, mean field slots in band {st['mean_field_slots_in_band_of_10']} "
              f"of 10. Broken by slot: {bs}. All-average roster: {fl['status']}"
              + (f" at {', '.join(fl['broken_slots'])}" if fl['broken_slots'] else '')
              + f", {fl['field_slots_in_band_of_10']} of 10 field slots in band.", '']
    return '\n'.join(L)


def staffing_table(staff):
    L = ['| Style | Slots that can fail | Not broken | Fully in band | Mean field slots in band (of 10) | '
         'All-average roster |', '| --- | --- | --- | --- | --- | --- |']
    rows = sorted(S.T, key=lambda t: -staff['tactics'][t['id']]['not_broken_rate'])
    for t in rows:
        st = staff['tactics'][t['id']]
        fl = st['flat_average_roster']
        fs = ', '.join(f"{s['id']} (needs {s['understaffed']['fail_below_in_band']})" for s in t['slots']
                       if s['understaffed']['mode'] == 'failure')
        L.append(f"| {t['name']} | {fs} | {st['not_broken_rate']:.0%} | {st['full_rate']:.0%} | "
                 f"{st['mean_field_slots_in_band_of_10']} | {fl['field_slots_in_band_of_10']} of 10 field slots in "
                 f"band; breaks at {', '.join(fl['broken_slots'])} |")
    return '\n'.join(L)


def fill(text, repl):
    for k, v in repl.items():
        assert '{{' + k + '}}' in text, k
        text = text.replace('{{' + k + '}}', v)
    assert '{{' not in text, text[text.index('{{'):][:60]
    return text


def main():
    staff = RT.staffing(N_STAFF)
    data = build_json(staff)
    (OUT / 'tactics_0.json').write_text(json.dumps(data, indent=1) + '\n')
    cc = class_counts()
    repl = {
        'STYLES': '\n'.join(style_md(n, t, staff) for n, t in enumerate(S.T, 1)),
        'MATRIX': matrix_md(),
        'NEUTRAL': neutral_md(),
        'N_PRED': str(sum(1 for m in S.M if m['predicted_edge'])),
        'N_OPEN': str(sum(1 for m in S.M if not m['predicted_edge'])),
        'CATALOG': catalog_md(),
        'N_PARAMS': str(len(S.CATALOG)),
        'N_NOW': str(cc[S.NOW]), 'N_COORD': str(cc[S.COORD]), 'N_ENGINE': str(cc[S.ENGINE]),
    }
    (OUT / 'TACTICS_0.md').write_text(fill((HERE / 'TACTICS_0.template.md').read_text(), repl))
    st = staff['tactics']
    top = max(S.T, key=lambda t: st[t['id']]['not_broken_rate'])
    # PERSONNEL_PROFILES.template.md states these in prose; fail the build if the arithmetic stops supporting them.
    assert top['id'] != 'COUNT'
    assert max(st, key=lambda k: st[k]['full_rate']) == 'COUNT'
    assert max(st, key=lambda k: st[k]['mean_field_slots_in_band_of_10']) == 'COUNT'
    assert st['COUNT']['flat_average_roster']['broken_slots'] == ['METRONOME']
    assert sorted(st, key=lambda k: st[k]['not_broken_rate'])[:3] == ['ANVIL', 'LOCK', 'RAM']
    prep = {'PROFILES': personnel_md(staff), 'STAFFING': staffing_table(staff), 'N_STAFF': str(N_STAFF),
            'TOP_ARITH': top['name']}
    (OUT / 'PERSONNEL_PROFILES.md').write_text(fill((HERE / 'PERSONNEL_PROFILES.template.md').read_text(), prep))
    print(json.dumps({'tactics': len(S.T), 'parameters': len(S.CATALOG), 'classes': cc,
                      'staffing': {k: v['not_broken_rate'] for k, v in staff['tactics'].items()}}, indent=1))


if __name__ == '__main__':
    main()
