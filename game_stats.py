#!/usr/bin/env python3
"""Box score (team and individual) from a saved Pocket4 game: python3 game_stats.py game_seed1_rot.pkl [Team A name] [Team B name]"""
import pickle, sys, csv
from collections import Counter, defaultdict
def build(path, tn=('A', 'B')):
    d = pickle.load(open(path, 'rb')); log = d['log']; names = d['names']; mins = d['mins']
    P = defaultdict(Counter); T = {'A': Counter(), 'B': Counter()}; tm = lambda pid: pid[0]
    pend = None; AR = {}; last_ctrl = {}; last_rel = {}; shots_open = {}
    for e in log:
        ev, x = e['event'], e['data']
        if ev == 'control': 
            pid = x['player']; P[pid]['controls'] += 1; last_ctrl[tm(pid)] = pid
            if pend:
                ps, kind, tgt = pend; pend = None
                if tm(pid) == tm(ps):
                    if pid != ps:
                        P[ps][kind + '_comp'] += 1; P[pid]['receptions'] += 1; T[tm(ps)][kind + '_comp'] += 1
                else: P[pid]['interceptions'] += 1; T[tm(pid)]['interceptions'] += 1
        elif ev == 'release' and not x.get('forced'):
            pid = x['player']; k = x['kind']
            if k in ('pass', 'kick'): P[pid][k + '_att'] += 1; T[tm(pid)][k + '_att'] += 1; pend = (pid, k, x.get('target'))
            elif k == 'shot': P[pid]['shots'] += 1; T[tm(pid)]['shots'] += 1; pend = None
            last_rel[tm(pid)] = (pid, k)
        elif ev == 'goal':
            team = x['team']; pts = x['points']; meth = x['method']
            sc = last_ctrl.get(team) if meth == 'carry' else (last_rel.get(team) or (None,))[0]
            if sc is None or tm(sc) != team: sc = x.get('last_offensive_toucher') or sc
            P[sc]['goals'] += 1; P[sc]['points'] += pts; T[team]['goals'] += 1; T[team]['points'] += pts; T[team]['goal_' + meth] += 1; T[team]['pts_' + meth] += pts
            if meth != 'carry' and last_rel.get(team) and last_rel[team][1] == 'shot': pass
            pend = None
        elif ev == 'tackle_count':
            P[x['tackler']]['tackles'] += 1; P[x['carrier']]['tackled'] += 1; T[tm(x['tackler'])]['tackles'] += 1
        elif ev == 'strip': P[x['actor']]['strips'] += 1; T[tm(x['actor'])]['strips'] += 1
        elif ev == 'foul': P[x['actor']]['fouls'] += 1; P[x['victim']]['fouls_drawn'] += 1; T[tm(x['actor'])]['fouls'] += 1
        elif ev == 'discipline': P[x['player']]['minors' if x['kind'] == 'minor' else 'other_disc'] += 1; T[tm(x['player'])]['discipline'] += 1
        elif ev == 'injury': P[x['player']]['injured'] += 1; T[tm(x['player'])]['injuries'] += 1
        elif ev == 'possession_change': T[x['team']]['possessions'] += 1
        elif ev == 'keeper_contact': P[x['player']]['kc_' + x['kind']] += 1
        elif ev == 'keeper_confront': P[x['player']]['confronts'] += 1
        elif ev == 'arrow_release':
            P[x['player']]['arrows'] += 1; T[tm(x['player'])]['arrows'] += 1; AR[x['arrow']] = x['player']; T[tm(x['player'])]['arrow_range_sum'] += x.get('range', 0)
        elif ev == 'arrow_miss':
            sh = AR.get(x.get('arrow'))
            if sh: T[tm(sh)]['arrow_miss'] += 1
        elif ev == 'arrow_geometry_impact':
            sh = AR.get(x.get('arrow'))
            if sh: T[tm(sh)]['arrow_blocked' if x.get('blocked') else 'arrow_ontarget'] += 1
        elif ev == 'freeze' and x.get('arrow') is not None:
            sh = AR.get(x['arrow'])
            if sh:
                P[sh]['arrow_freezes'] += 1; T[tm(sh)]['arrow_freezes'] += 1
                if x.get('was_carrier'): T[tm(sh)]['arrow_freeze_carrier'] += 1
        elif ev == 'inert_impact' and x.get('arrow') is not None:
            sh = AR.get(x['arrow'])
            if sh: T[tm(sh)]['arrow_inert_teammate' if x.get('reason') == 'teammate' else 'arrow_inert_other'] += 1
        elif ev == 'substitution': T[tm(x['out'])]['subs'] += 1
    for t in 'AB':
        T[t]['pass_att_all'] = T[t]['pass_att']; T[t]['kick_att_all'] = T[t]['kick_att']
    return d, P, T
def report(path, tn):
    d, P, T = build(path); names = d['names']; mins = d['mins']; sc = d['score']; out = []
    out.append(f"# Box score: {tn[0]} {sc['A']} - {tn[1]} {sc['B']}   ({d['result'].get('method')})\n")
    out.append("## Team\n\n| | " + tn[0] + " | " + tn[1] + " |\n|---|---:|---:|")
    rows = [('Points', 'points'), ('Goals', 'goals'), ('  inner-arc / release goals', 'goal_inner_release'), ('  inside release', 'goal_inside_release'), ('  outside release', 'goal_outside_release'), ('  carry', 'goal_carry'), ('Possessions', 'possessions'), ('Shots', 'shots'),
            ('Passes attempted', 'pass_att'), ('Passes completed', 'pass_comp'), ('Kicks attempted', 'kick_att'), ('Kicks completed', 'kick_comp'), ('Interceptions', 'interceptions'), ('Tackles', 'tackles'), ('Strips', 'strips'), ('Fouls', 'fouls'), ('Minor penalties', 'discipline'), ('Arrows fired', 'arrows'), ('  freezes (hits that count)', 'arrow_freezes'), ('  of which ball carrier', 'arrow_freeze_carrier'), ('  on-target impacts', 'arrow_ontarget'), ('  blocked by another body', 'arrow_blocked'), ('  inert (non-carrier / illegal)', 'arrow_inert_other'), ('  inert (own teammate)', 'arrow_inert_teammate'), ('  misses (ground / out)', 'arrow_miss'), ('Injuries', 'injuries'), ('Substitutions', 'subs')]
    for lab, k in rows: out.append(f"| {lab} | {T['A'][k]} | {T['B'][k]} |")
    csvrows = []
    for t, nm in (('A', tn[0]), ('B', tn[1])):
        out.append(f"\n## {nm} individual\n\n| Player | Pos | Min | Pts | G | Shots | Pass c/a | Rec | Int | Tkl | Strip | Foul | Pen | Keeper: catch/parry/body | Arrows |\n|---|---|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|--:|---|--:|")
        for i in range(22):
            pid = f'{t}{i}'; p = P[pid]; n = names[pid]; m = mins.get(pid, 0) / 60000.
            if m < .05 and not any(p.values()): continue
            kc = f"{p['kc_catch']}/{p['kc_parry']}/{p['kc_body']}" if (i == 10 or p['kc_catch'] or p['kc_parry']) else ''
            pc = p['pass_comp'] + p['kick_comp']; pa = p['pass_att'] + p['kick_att']
            out.append(f"| {n['name']}{' (inj)' if p['injured'] else ''} | {n['position']} | {m:.1f} | {p['points']} | {p['goals']} | {p['shots']} | {pc}/{pa} | {p['receptions']} | {p['interceptions']} | {p['tackles']} | {p['strips']} | {p['fouls']} | {p['minors']+p['other_disc']} | {kc} | {p['arrows'] or ''} |")
            csvrows.append([nm, n['name'], n['position'], round(m, 1), p['points'], p['goals'], p['shots'], pc, pa, p['receptions'], p['interceptions'], p['tackles'], p['tackled'], p['strips'], p['fouls'], p['fouls_drawn'], p['minors'] + p['other_disc'], p['kc_catch'], p['kc_parry'], p['kc_body'], p['arrows'], p['controls']])
    return '\n'.join(out), csvrows
if __name__ == '__main__':
    path = sys.argv[1]; tn = (sys.argv[2] if len(sys.argv) > 2 else 'A', sys.argv[3] if len(sys.argv) > 3 else 'B')
    txt, rows = report(path, tn); base = path.rsplit('.', 1)[0]
    open(base + '_boxscore.md', 'w').write(txt)
    with open(base + '_players.csv', 'w', newline='') as f:
        w = csv.writer(f); w.writerow(['team', 'player', 'pos', 'min', 'points', 'goals', 'shots', 'pass_kick_comp', 'pass_kick_att', 'receptions', 'interceptions', 'tackles', 'times_tackled', 'strips', 'fouls', 'fouls_drawn', 'penalties', 'k_catch', 'k_parry', 'k_body', 'arrows', 'controls']); w.writerows(rows)
    print(txt)
