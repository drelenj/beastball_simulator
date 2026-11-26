"""Offline report for the fixed five-seed sets trials."""
import argparse
from bisect import bisect_left
from collections import Counter
from math import sqrt
from pathlib import Path
from statistics import mean, median, stdev

from audit.native.rb333.tables import pct
from audit.native.rb334.tables import IDENTITY, load
from audit.native.rb335.tables import metrics as turnover_metrics

ARMS = ('B4','C0','C1','C2','T3','T4')
COMPARISONS = (*zip(ARMS[1:],ARMS),('T4','C2'))
REACTIONS = ('catch','interception','deflection','takedown','loose_pursuit')


def metrics(run):
    old = turnover_metrics(run)
    sets = run.get('rb336')
    box = run['box']
    possessions = box['possessions']
    starts = [p['start_ms'] for p in possessions]
    reasons = Counter(p['end_reason'] for p in possessions)
    durations = [(b['start_ms']-a['start_ms'])/1000 for a,b in zip(possessions,possessions[1:])
                 if a['end_reason'] != 'period_end']
    data = {'Possessions/team':old['Possessions/team'],
            'Mean possession duration (s)':mean(durations),
            'Median possession duration (s)':median(durations)}
    reached = [set() for _ in range(4)]
    if sets:
        for time,count in sets['tackles']:
            index = bisect_left(starts,time)-1
            if index>=0 and count in (1,2,3):
                reached[count].add(index)
    else:
        reached[1] = {bisect_left(starts,t)-1 for t in run['rb335']['first_tackles']} - {-1}
        reached[2] = {i for i,p in enumerate(possessions) if p['end_reason']=='second_tackle'}
    for n in (1,2,3):
        data[f'Possessions reaching tackle {n} (%)'] = pct(len(reached[n]),len(possessions))
    data['Scrimmages per possession'] = old['Scrimmages per possession']
    for name in ('boundary','interception','fumble','score','opponent_control'):
        data[f'Possession ends {name}'] = reasons.pop(name,0)/2
    data['Possession ends Nth tackle'] = (reasons.pop('second_tackle',0)+reasons.pop('nth_tackle',0))/2
    data['Possession ends other'] = sum(reasons.values())/2
    data.update((k,v) for k,v in old.items() if k.startswith('Boundary possession ends '))
    data['Points/team'] = old['Points/team']
    data.update((k,v) for k,v in old.items() if k.startswith('Points from '))
    data['Possessions ending in attempt (%)'] = old['Possessions ending in an attempt (%)']
    data['Carry goals'] = run['diagnosis']['carries']['governed_goals']/2
    for method in ('throw_2','throw_3','throw_4','half_goal','full_goal_award','own'):
        data[f'Goals and awards from {method}'] = sum(
            t['goals_by_method'].get(method,0) for t in box['teams'])/2
    for key in ('stretch_start','stretch_goal'):
        data[key] = run['diagnosis']['carries']['stretch'].get(key,0)/2
    data['Held end-line flights staying in play'] = len(sets['endline_continued'])/2 if sets else 0
    for key in ('Carrier outs after contact','Carrier outs without recent contact','Pass attempts',
                'Pass completion (%)','Targeted drops','Interceptions (ledger)',
                'True receiver distance from aim P50 (m)'):
        data[key]=old[key]
    if sets:
        shots = sets['shots']
        data['Keeper above active threshold at release (%)'] = pct(
            sum(r['speed']>r['threshold'] for r in shots),len(shots))
    else:
        data['Keeper above active threshold at release (%)'] = old['Keeper above set speed at release (%)']
    for key in ('Box Keeper saves','Box Keeper shots faced','Box Keeper saves / faced (%)',
                'Event Keeper save rate (%)','Event Keeper saves / faced (%) <10 m',
                'Event Keeper saves / faced (%) 10–20 m','Event Keeper saves / faced (%) 20 m+'):
        data[key]=old[key]
    for kind in REACTIONS:
        counts = sets['reactions'].get(kind,{}) if sets else {}
        data[f'{kind} reactions paying unset'] = counts.get('paid_starts',0)/2
        if kind in ('catch','interception','takedown'):
            for group,label in (('paid','cost paid'),('set','no cost')):
                data[f'{kind} success (%) {label}'] = pct(counts.get(group+'_success',0),counts.get(group+'_starts',0))
    for key in ('Takedown episodes','Takedown episodes on non-carrier (%)','Takedown success (%)'):
        data[key]=old[key]
    data['Ala minus Garvian margin'] = run['score']['B']-run['score']['A']
    data['Absolute margin'] = abs(data['Ala minus Garvian margin'])
    data['CPU seconds/game'] = old['CPU seconds/game']
    return data


def collected(root, parent):
    runs = {a:[load(parent if a=='B4' else root,f'{a}-{seed}') for seed in range(1,6)] for a in ARMS}
    replay = load(root,'B4-1')
    assert all(replay[k]==runs['B4'][0][k] for k in IDENTITY), 'B4 replay'
    rival = load(root,'T3-repeat')
    assert all(rival[k]==v for k,v in runs['T3'][0].items() if k not in ('cpu_s','cpu_profile')), 'T3 repeat'
    for arm, games in runs.items():
        assert all(r['status']=='final' and r['invariants']=='passed' and r['restart_completion_ratio']==1
                   for r in games), arm
    return runs


def render(root, parent):
    runs = collected(root,parent)
    measures = {arm:[metrics(r) for r in games] for arm,games in runs.items()}
    lines = ['# RB-3.36 paired results','',
             'Five Garvian Guardians–Ala Apex games per arm. Counts are per team per game unless specified. '
             'Game rates pool both teams and arm means weight games equally. A tilde marks a difference '
             'within two paired SEs. A dash marks a missing denominator.','',
             '| Measure | '+' | '.join((*ARMS,*(f'{a} − {b}' for a,b in COMPARISONS)))+' |',
             '| '+' | '.join(['---']*(1+len(ARMS)+len(COMPARISONS)))+' |']
    for key in measures['B4'][0]:
        columns = {arm:[r[key] for r in games] for arm,games in measures.items()}
        cells = []
        for column in columns.values():
            values = [x for x in column if x is not None]
            cells.append(f'{mean(values):.2f}' if values else '—')
        for after,before in COMPARISONS:
            paired = [a-b for a,b in zip(columns[after],columns[before]) if None not in (a,b)]
            if len(paired)<2:
                cells.append('—')
                continue
            delta, se = mean(paired),stdev(paired)/sqrt(len(paired))
            cells.append(f'{delta:+.2f} ± {se:.2f}' + (' ~' if abs(delta)<=2*se else '')
                         + (f' (n={len(paired)})' if len(paired)!=5 else ''))
        lines.append('| '+' | '.join((key,*cells))+' |')
    lines.extend(['','## Opening set speeds by Agility band','',
                  '| Agility | Players | Mean (m/s) | Min | Max |','| --- | ---: | ---: | ---: | ---: |'])
    bands = runs['C1'][0]['rb336']['set_speeds']
    for band in ('<.60','.60–.69','.70–.79','≥.80'):
        vel = bands.get(band,[])
        if vel:
            lines.append(f'| {band} | {len(vel)} | {mean(vel):.2f} | {min(vel):.2f} | {max(vel):.2f} |')
        else:
            lines.append(f'| {band} | 0 | — | — | — |')
    lines.extend(['','## Scores and signed margins','',
                  '| Arm | Seed 1 | Seed 2 | Seed 3 | Seed 4 | Seed 5 |',
                  '| --- | --- | --- | --- | --- | --- |'])
    for arm,games in runs.items():
        scores = [f"{r['score']['A']}–{r['score']['B']} ({r['score']['B']-r['score']['A']:+d})" for r in games]
        lines.append('| '+' | '.join((arm,*scores))+' |')
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root',type=Path)
    parser.add_argument('parent',type=Path)
    parser.add_argument('out',type=Path)
    args = parser.parse_args()
    args.out.write_text(render(args.root,args.parent),encoding='utf8')


if __name__ == '__main__':
    main()
