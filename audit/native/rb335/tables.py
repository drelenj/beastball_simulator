"""Generate the RB-3.35 report tables from saved records."""
import argparse
from bisect import bisect_right
from collections import Counter
from math import sqrt
from pathlib import Path
from statistics import mean, stdev

from audit.native.rb333.tables import pct, quantile
from audit.native.rb334.tables import IDENTITY, load

ARMS = ('A6','B1','B2','B3','B4')
PAIRS = (*zip(ARMS[1:],ARMS),('B4','A6'))
PATHS = ('prism_defender_menu','defender_baseline','other')


def metrics(run):
    box, observed, diagnosis = run['box'],run['rb335'],run['diagnosis']
    result = {}
    add = result.__setitem__
    team = lambda key: sum(t[key] for t in box['teams'])
    possessions = box['possessions']
    count = len(possessions)
    reasons = Counter(p['end_reason'] for p in possessions)
    total_boundary_ends = reasons['boundary']
    starts = [p['start_ms'] for p in possessions]
    tackle_possessions = {bisect_right(starts,now)-1 for now in observed['first_tackles']}
    add('Possessions/team',team('possessions')/2)
    add('Possessions reaching first tackle (%)',pct(len(tackle_possessions - {-1}),count))
    add('Scrimmages per possession',len(observed['scrimmages'])/count)
    add('Possessions ending in an attempt (%)',pct(team('possessions_ending_in_attempt'),team('possessions')))
    add('Points/team',team('points')/2)
    for reason in ('boundary','interception','fumble','second_tackle','score','opponent_control'):
        add('Possession ends '+reason,reasons.pop(reason,0)/2)
    add('Possession ends other',sum(reasons.values())/2)
    for method in ('carry','throw_2','throw_3','throw_4','half_goal','full_goal_award','own'):
        points = sum(t['scoring_points_by_method'].get(method,0) for t in box['teams'])
        add('Points from '+method,points/2)

    ends = {nxt['start_ms'] for cur,nxt in zip(possessions,possessions[1:]) if cur['end_reason']=='boundary'}
    matched = Counter(b['kind'] for b in run['boundary'] if b['t_ms'] in ends)
    for kind in ('pass','held_ball','carrier','loose_ball','shot','deflection'):
        add('Boundary possession ends '+kind,matched[kind]/2)
    add('Boundary possession ends without a classified witness', (total_boundary_ends-sum(matched.values()))/2)
    add('Passed balls flying out',sum(b['kind']=='pass' and b['mode_before']=='passed'
                                     for b in run['boundary'])/2)
    contact = observed['carrier_after_contact']
    carrier_ids = [str(b['event_id']) for b in run['boundary'] if b['kind']=='carrier']
    add('Carrier outs after contact',sum(contact.get(k,False) for k in carrier_ids)/2)
    add('Carrier outs without recent contact',sum(not contact.get(k,False) for k in carrier_ids)/2)
    add('Held sideline crossings with play continuing',observed['sidelines']/2)

    add('Pass attempts',team('passes_attempted')/2)
    add('Pass completion (%)',pct(team('passes_completed'),team('passes_attempted')))
    add('Targeted drops',team('drops')/2)
    miss = [r['distance'] for r in observed['arrivals']]
    add('Receiver arrival witnesses',len(miss)/2)
    for q in (.1,.5,.9):
        add(f'True receiver distance from aim P{int(q*100)} (m)',quantile(miss,q))
    add('Interceptions (ledger)',diagnosis['total'].get('interception',0)/2)
    for kind in ('believed_margin','true_margin'):
        add('Open-play intercepted pass '+kind.replace('_',' ')+' (m)',diagnosis['interception_open'][kind])

    keep = diagnosis['keepers']
    add('Box Keeper saves',team('saves')/2)
    add('Box Keeper shots faced',team('shots_faced')/2)
    add('Box Keeper saves / faced (%)',pct(team('saves'),team('shots_faced')))
    add('Event Keeper save rate (%)',pct(keep['total']['saves'],keep['total']['faced']))
    add('Keeper above set speed at release (%)',pct(run['unset'],keep['total']['faced']))
    add('Shots with plant witness',observed['plants_at_release']/2)
    for band,label in (('2','<10 m'),('3','10–20 m'),('4','20 m+')):
        shot = keep['by_band'].get(band,{})
        add('Event Keeper saves / faced (%) '+label,pct(shot.get('saves',0),shot.get('faced',0)))

    tackle = diagnosis['tackles']['overall']
    add('Takedown episodes',tackle['n']/2)
    add('Takedown episodes on non-carrier (%)',pct(tackle['n']-tackle['targeted_actual_carrier'],tackle['n']))
    add('Takedown success (%)',pct(tackle['made'],tackle['n']))
    for kind in ('path_issued','path_accepted','path_gated'):
        for path in PATHS:
            value = observed[kind].get(path,0)/2 if run['arm']!='A6' else None
            add(f'{kind} {path}',value)
    for kind in ('wrap_abort','wrap_retarget'):
        add(kind,run['events'].get(kind,0)/2)
    add('CPU seconds/game',run['cpu_s'])
    return result


def render(root, parent):
    runs = {arm:[load(root,f'{arm}-{seed}') for seed in range(1,6)] for arm in ARMS}
    for seed, trial in enumerate(runs['A6'],1):
        original = load(parent,f'A6-{seed}')
        assert all(trial[k]==original[k] for k in IDENTITY), seed
    repeat = load(root,'B4-repeat')
    assert all(value==repeat[k] for k,value in runs['B4'][0].items() if k not in ('cpu_s','cpu_profile'))
    for games in runs.values():
        assert all(r['status']=='final' and r['invariants']=='passed' and r['restart_completion_ratio']==1 for r in games)
    values = {arm:[metrics(row) for row in games] for arm,games in runs.items()}
    rows = ['# RB-3.35 paired results','',
            'Garvian Guardians vs Ala Apex, seeds 1–5. Counts are per team per game except where indicated. '
            'Means weight games equally. Event and box rates pool the two teams within each game. '
            'A dash marks an unavailable measure. Differences in rates are percentage points. '
            'A tilde marks an absolute paired difference at or below two paired SEs.','',
            '| Measure | '+' | '.join((*ARMS,*(f'{a} − {b}' for a,b in PAIRS)))+' |',
            '| '+' | '.join(['---']*(1+len(ARMS)+len(PAIRS)))+' |']
    for key in values['A6'][0]:
        columns = {a:[v[key] for v in games] for a,games in values.items()}
        cells = []
        for col in columns.values():
            available = [v for v in col if v is not None]
            cells.append(f'{mean(available):.2f}' if available else '—')
        for a,b in PAIRS:
            delta = [x-y for x,y in zip(columns[a],columns[b]) if x is not None and y is not None]
            if len(delta)<2:
                cells.append('—')
                continue
            m, se = mean(delta), stdev(delta)/sqrt(len(delta))
            cells.append(f'{m:+.2f} ± {se:.2f}'+(' ~' if abs(m)<=2*se else '')+
                         (f' (n={len(delta)})' if len(delta)!=5 else ''))
        rows.append('| '+' | '.join((key,*cells))+' |')
    rows += ['', '| Arm | Seed 1 | Seed 2 | Seed 3 | Seed 4 | Seed 5 |',
             '| --- | --- | --- | --- | --- | --- |']
    for arm,games in runs.items():
        rows.append('| '+' | '.join([arm]+[f"{r['score']['A']}–{r['score']['B']}" for r in games])+' |')
    return '\n'.join(rows)+'\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root',type=Path)
    parser.add_argument('parent',type=Path)
    parser.add_argument('out',type=Path)
    args = parser.parse_args()
    args.out.write_text(render(args.root,args.parent),encoding='utf8')


if __name__=='__main__':
    main()
