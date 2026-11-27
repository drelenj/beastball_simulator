"""Build the paired RB-3.38 tables and the fixed body-out episode sample."""
import argparse
from collections import Counter, defaultdict
import json
from math import sqrt
from pathlib import Path
from random import Random
from statistics import mean, stdev

from audit.native.rb334.tables import IDENTITY, load
from audit.native.rb336.tables import metrics as sets_metrics
from audit.native.rb337.tables import CASES

ARMS = ('R0','R1','R2','R3')
RANGES = (('R1','R0'),('R2','R0'),('R3','R0'),('R3','R2'))
BODY_CAUSES = ('contact push','maneuver path','steering overshoot with aim inside',
               'aim outside','frozen or stunned','other')
SAMPLE_SEED = 20261127


def body_cause(episode):
    history = episode['history']
    exit_sample = history[-1]
    now = episode['ms']
    if exit_sample['frozen'] or exit_sample['posture'] in ('grounded','stunned'):
        return 'frozen or stunned'
    hit = exit_sample['last_collision_ms']
    if exit_sample['contact'] in ('wrap','hold','collision') or hit is not None and 0<=now-hit<=150:
        return 'contact push'
    if exit_sample['maneuver'] != 'none':
        return 'maneuver path'
    target = exit_sample['locomotion_target'] or exit_sample.get('aim')
    if target is None:
        return 'other'
    return 'steering overshoot with aim inside' if all(0<v<100 for v in target) else 'aim outside'


def quantile(sequence,fraction):
    if not sequence:
        return None
    ordered = sorted(sequence)
    offset = (len(ordered)-1)*fraction
    lo = int(offset)
    return ordered[lo] + (ordered[min(lo+1,len(ordered)-1)]-ordered[lo])*(offset-lo)


def intervals(archive,clock):
    by_archer = defaultdict(list)
    for row in archive['releases']:
        if row['legal'] and 'shooter' in row:
            by_archer[row['shooter']].append(row[clock])
    return [(b-a)/1000 for releases in by_archer.values() for a,b in zip(releases,releases[1:])]


def measurements(run, max_period=4):
    r = run['rb338']
    inherited = sets_metrics(run)
    out = {}
    for k,v in inherited.items():
        if k.startswith(('Possession','Boundary possession','Mean possession','Median possession',
                         'Points','Goals and awards','stretch','Event Keeper','Box Keeper')):
            out[k]=v
        elif k in ('Carry goals','Pass attempts','Pass completion (%)','Targeted drops',
                   'Interceptions (ledger)','CPU seconds/game','Absolute margin'):
            out[k]=v
    out['Second team minus first team margin'] = inherited['Ala minus Garvian margin']
    # Net charges are separate from actual releases. Illegal releases spend
    # ammunition and dead-ball in-flight refunds return the spent arrow.
    releases = r['releases']
    out['Arrows attempted (incl. illegal)'] = len(releases)/2
    out['Arrows released (legal)'] = sum(x['legal'] for x in releases)/2
    out['Arrows refunded'] = sum(x.get('refunded',False) for x in releases)/2
    out['Arrows net charged'] = out['Arrows attempted (incl. illegal)']-out['Arrows refunded']
    out['Arrow impacts on players'] = len(r['hits'])/2
    out['Freezes'] = len(r['freezes'])/2
    for carrier, description in ((True,'carrier'),(False,'non-carrier')):
        out['Freezes ('+description+')'] = sum(x['carrier']==carrier for x in r['freezes'])/2
    out['Carrier-freeze fumbles'] = sum(f['detail']=='freeze of carrier' for f in run['rb337']['fumbles'])/2
    defended = len(run['box']['possessions'])
    out['Arrows per defensive possession'] = len(releases)/defended
    out['Freezes per defensive possession'] = len(r['freezes'])/defended
    for clock, label in (('now','elapsed'),('live_ms','live')):
        sample = intervals(r,clock)
        for i in (10,50,90):
            out[f'Inter-release {label} P{i} (s)'] = quantile(sample,i/100)
    for period in range(1,max_period+1):
        for index,label in enumerate(('arrows','freezes')):
            budgets = r['periods'].get(str(period))
            out[f'End P{period} {label} remaining'] = mean(v[index] for v in budgets.values()) if budgets else None
    outs = Counter(body_cause(row) for row in r['body_outs'])
    out['Carrier body-outs'] = sum(outs.values())/2
    for kind in BODY_CAUSES:
        out['Carrier out, '+kind] = outs[kind]/2
    return out


def game_rows(path, parent):
    rows = {a:[load(path,f'{a}-{pair}-{seed}') for pair,seed in CASES] for a in ARMS}
    for (pair,seed),row in zip(CASES,rows['R0']):
        prior = load(parent,f'L0-{pair}-{seed}')
        assert all(row[k]==prior[k] for k in IDENTITY), (pair,seed)
    duplicate = load(path,'R3-repeat')
    assert all(duplicate[k]==v for k,v in rows['R3'][0].items() if k not in ('cpu_s','cpu_profile'))
    for arm,runs in rows.items():
        for row in runs:
            assert row['status']=='final' and row['invariants']=='passed' and row['restart_completion_ratio']==1, (arm,row['seed'])
            assert len(row['rb338']['body_outs'])==sum(e['kind']=='carrier' for e in row['boundary'])
            if arm in ('R2','R3'):
                check_budget(arm,row['rb338'])
    return rows


def check_budget(arm, log):
    for team in ('A','B'):
        remaining = (25,5)
        for label, budget_at_end in log['periods'].items():
            period = int(label)
            if arm=='R3':
                remaining = (10,4) if period<=4 else (5,2)
            spent = sum(x['team']==team and x['period']==period and not x.get('refunded',False)
                        for x in log['releases'])
            freezes = sum(x['team']==team and x['period']==period for x in log['freezes'])
            remaining = (remaining[0]-spent,remaining[1]-freezes)
            assert min(remaining)>=0 and tuple(budget_at_end[team])==remaining, (arm,team,period,remaining,budget_at_end)


def grid(lines, rows, indices, caption):
    lines.extend([f'## {caption}','','| Measure | '+' | '.join((*ARMS,*(f'{h} − {l}' for h,l in RANGES)))+' |',
                  '| '+' | '.join(['---']*9)+' |'])
    for key in rows['R0'][0]:
        columns = {a:[rows[a][i][key] for i in indices] for a in ARMS}
        cells = []
        for series in columns.values():
            numbers = [x for x in series if x is not None]
            cells.append(f'{mean(numbers):.2f}' if numbers else '—')
        for h,l in RANGES:
            pairs = [x-y for x,y in zip(columns[h],columns[l]) if None not in (x,y)]
            if len(pairs)<2:
                cells.append('—')
                continue
            effect,se = mean(pairs),stdev(pairs)/sqrt(len(pairs))
            cells.append(f'{effect:+.2f} ± {se:.2f}'+(' ~' if abs(effect)<=2*se else '')+
                         (f' (n={len(pairs)})' if len(pairs)!=len(indices) else ''))
        lines.append('| '+' | '.join((key,*cells))+' |')
    lines.append('')


def spending(lines, rows):
    lines.extend(['## Archer spending by period and live minute','','Each cell is gross attempts / net charged / freezes per team per game. A dash marks an unplayed period or minute.',''])
    for caption,indices in (('Combined',range(8)),('Garvian–Ala',range(5)),('Yukïma–Isu’Kari',range(5,8))):
        max_period = max(int(p) for arm in rows.values() for i in indices for p in arm[i]['rb338']['periods'])
        lines.extend([f'### {caption}','','| Period | Minute | R0 | R1 | R2 | R3 |','| --- | --- | --- | --- | --- | --- |'])
        for period in range(1,max_period+1):
            last_minute = max((r['minute'] for arm in rows.values() for i in indices
                               for stream in ('releases','freezes') for r in arm[i]['rb338'][stream]
                               if r['period']==period),default=0)
            for minute in (None,*range(1,max(last_minute,10 if period<=4 else 5)+1)):
                columns = []
                for arm in ARMS:
                    attempts = net = freezes = eligible = 0
                    for i in indices:
                        report = rows[arm][i]['rb338']
                        if str(period) not in report['periods']:
                            continue
                        eligible += 2
                        arrows = [r for r in report['releases'] if r['period']==period and (minute is None or r['minute']==minute)]
                        attempts += len(arrows)
                        net += sum(not r.get('refunded',False) for r in arrows)
                        freezes += sum(r['period']==period and (minute is None or r['minute']==minute) for r in report['freezes'])
                    columns.append(' / '.join(f'{count/eligible:.2f}' for count in (attempts,net,freezes)) if eligible else '—')
                lines.append('| '+' | '.join((str(period),str(minute) if minute else 'Total',*columns))+' |')
        lines.append('')


def episodes(rows):
    rng = Random(SAMPLE_SEED)
    result = []
    for arm in ARMS:
        pool = [dict(arm=arm,pair=pair,seed=seed,cause=body_cause(episode),**episode)
                for (pair,seed),run in zip(CASES,rows[arm]) for episode in run['rb338']['body_outs']]
        result.extend(rng.sample(pool,5))
    return result


def render(rows, sample):
    lines = ['# RB-3.38 paired results','','Counts are per team per game except as labelled. Paired contrasts are means ± SE. A tilde marks differences within two paired SEs. Percentage contrasts use percentage points. End-period unused budgets in R0/R1 are snapshots of the active possession quota.','']
    last_period = max(int(p) for arm in rows.values() for run in arm for p in run['rb338']['periods'])
    values = {a:[measurements(r,last_period) for r in arm] for a,arm in rows.items()}
    for caption,indices in (('Combined',range(8)),('Garvian–Ala',range(5)),('Yukïma–Isu’Kari',range(5,8))):
        grid(lines,values,indices,caption)
    lines.extend(['## Final scores and signed margin','','Positive margins favor the second team.','',
                  '| Pair | Seed | R0 | R1 | R2 | R3 |','| --- | --- | --- | --- | --- | --- |'])
    for i,(pair,seed) in enumerate(CASES):
        scores = [rows[a][i]['score'] for a in ARMS]
        cells = [f"{r['A']}–{r['B']} ({r['B']-r['A']:+d})" for r in scores]
        lines.append('| '+' | '.join((('Garvian–Ala','Yukïma–Isu’Kari')[pair],str(seed),*cells))+' |')
    lines.append('')
    spending(lines,rows)
    lines.extend(['## Fixed sample of body-out episodes','',
                  f'Five episodes per arm drawn with seed {SAMPLE_SEED}. The companion JSON contains every sample of their two-second histories.','',
                  '| Arm | Pair | Seed | Engine ms | Athlete | Cause | Event |','| --- | ---: | ---: | ---: | --- | --- | ---: |'])
    for e in sample:
        lines.append('| '+' | '.join(str(e[k]) for k in ('arm','pair','seed','ms','carrier','cause','event_id'))+' |')
    lines.append('')
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('evidence',type=Path)
    parser.add_argument('parent',type=Path)
    parser.add_argument('tables',type=Path)
    parser.add_argument('episodes',type=Path)
    args = parser.parse_args()
    rows = game_rows(args.evidence,args.parent)
    sample = episodes(rows)
    args.tables.write_text(render(rows,sample),encoding='utf8')
    args.episodes.write_text(json.dumps(sample,ensure_ascii=False,indent=2)+'\n',encoding='utf8')


if __name__=='__main__':
    main()
