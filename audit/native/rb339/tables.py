"""Paired R3/E1 edge-control tables from exact-match replay evidence."""
import argparse
from collections import Counter
import gzip
import json
from math import sqrt
from pathlib import Path
from random import Random
from statistics import mean, stdev

from audit.native.rb334.tables import IDENTITY, load
from audit.native.rb336.tables import metrics as sets_metrics
from audit.native.rb337.tables import CASES
from audit.native.rb338.tables import BODY_CAUSES, body_cause, check_budget, measurements as archer_measurements
from native.edge_control import FIELD_M

ARMS = ('R3','E1')
SAMPLE_SEED = 20261129


def measurements(run, last_period=4):
    inherited = archer_measurements(run,last_period)
    out = {k:v for k,v in inherited.items() if k.startswith((
        'Possession','Boundary possession','Mean possession','Median possession',
        'Points','Goals and awards','stretch','Carrier out','End P')) or k in (
            'Carry goals','Pass attempts','Pass completion (%)','Interceptions (ledger)',
            'CPU seconds/game','Absolute margin','Second team minus first team margin',
            'Arrows net charged','Arrows released (legal)','Freezes','Carrier-freeze fumbles')}
    out['CPU seconds/game, matched observer'] = run.get('matched_cpu_s',run['cpu_s'])
    boundaries = Counter(row['kind'] for row in run['boundary'])
    out['Passes out'] = boundaries['pass']/2
    out['Loose balls out'] = boundaries['loose_ball']/2
    out['Deflections out'] = boundaries['deflection']/2
    out['Non-carrier body-outs'] = len(run['rb339']['noncarrier_outs'])/2
    carrier_ends = Counter()
    for episode in run['rb338']['body_outs']:
        x,y = episode['crossing']
        line = 'end line' if min(abs(x),abs(FIELD_M-x))<=min(abs(y),abs(FIELD_M-y)) else 'sideline'
        carrier_ends[line] += 1
        carrier_ends[line,body_cause(episode)] += 1
    for line in ('sideline','end line'):
        out['Carrier body-outs, '+line] = carrier_ends[line]/2
        for cause in BODY_CAUSES:
            out[f'Carrier body-outs, {line}, {cause}'] = carrier_ends[line,cause]/2
    takedowns = run['rb339']['takedowns']
    out['Adjudicated takedowns'] = len(takedowns)/2
    out['Takedowns within 3 m of a line'] = sum(t['line_m']<=3. for t in takedowns)/2
    contact = sets_metrics(run)
    for key in ('Takedown episodes','Takedown episodes on non-carrier (%)','Takedown success (%)'):
        out[key] = contact[key]
    for action in ('juke','spin','stiff_arm','truck'):
        data = run['rb337']['evasion'].get(action,{})
        attempts,successes = data.get('attempts',0),data.get('successes',0)
        out[action+' attempts'] = attempts/2
        out[action+' successes'] = successes/2
        out[action+' success (%)'] = 100*successes/attempts if attempts else None
    return out


def read(path, parent):
    rows = {a:[] for a in ARMS}
    for pair,seed in CASES:
        base = load(parent,f'R3-{pair}-{seed}')
        again = load(path,f'E0-{pair}-{seed}')
        assert all(base[key]==again[key] for key in IDENTITY), (pair,seed)
        trial = load(path,f'E1-{pair}-{seed}')
        for run in (again,trial):
            assert run['status']=='final' and run['invariants']=='passed' and run['restart_completion_ratio']==1
            assert len(run['rb338']['body_outs'])==sum(e['kind']=='carrier' for e in run['boundary'])
            assert len(run['rb339']['takedowns'])==run['events'].get('tackle_count',0)
            check_budget('R3',run['rb338'])
        # Reuse the archive for measures it already contains.
        rows['R3'].append(base | {'rb339':again['rb339'],'matched_cpu_s':again['cpu_s']})
        rows['E1'].append(trial)
    repeat = load(path,'E1-repeat')
    assert all(repeat[k]==v for k,v in rows['E1'][0].items() if k not in ('cpu_s','cpu_profile'))
    return rows


def grid(lines, metrics, indices, title):
    lines.extend([f'## {title}','','| Measure | R3 | E1 | E1 − R3 |','| --- | ---: | ---: | ---: |'])
    for key in metrics['R3'][0]:
        columns = [[metrics[a][i][key] for i in indices] for a in ARMS]
        vals = [[x for x in col if x is not None] for col in columns]
        output = [f'{mean(v):.2f}' if v else '—' for v in vals]
        diffs = [b-a for a,b in zip(*columns) if None not in (a,b)]
        if len(diffs)>1:
            diff, se = mean(diffs),stdev(diffs)/sqrt(len(diffs))
            output.append(f'{diff:+.2f} ± {se:.2f}'+(' ~' if abs(diff)<=2*se else '')+
                          (f' (n={len(diffs)})' if len(diffs)!=len(indices) else ''))
        else:
            output.append('—')
        lines.append('| '+' | '.join((key,*output))+' |')
    lines.append('')


def sampled(rows):
    pool = [dict(pair=pair,seed=seed,cause=body_cause(e),**e)
            for (pair,seed),run in zip(CASES,rows['E1']) for e in run['rb338']['body_outs']]
    return Random(SAMPLE_SEED).sample(pool,min(20,len(pool)))


def encoded(samples):
    return gzip.compress((json.dumps(samples,ensure_ascii=False,indent=2)+'\n').encode(),mtime=0)


def render(rows, sample):
    last_period = max(int(period) for arm in rows.values() for row in arm for period in row['rb338']['periods'])
    metrics = {a:[measurements(row,last_period) for row in games] for a,games in rows.items()}
    lines = ['# RB-3.39 paired edge-control results','',
             'Counts are per team per game except as labelled. Rate contrasts are percentage points. '
             'The tilde marks effects within two paired standard errors. A dash marks a missing denominator or fewer than two pairs. '
             'The matched-observer CPU row uses the E0 replays for R3.','']
    for label,indices in (('Combined',range(8)),('Garvian–Ala',range(5)),('Yukïma–Isu’Kari',range(5,8))):
        grid(lines,metrics,indices,label)
    lines.extend(['## Individual games','','Positive margins favor the second team.','',
        '| Matchup | Seed | R3 score (margin) | E1 score (margin) | R3 CPU (s) | R3 matched CPU (s) | E1 CPU (s) |',
        '| --- | ---: | --- | --- | ---: | ---: | ---: |'])
    for index,(pair,seed) in enumerate(CASES):
        r3,e1 = (rows[a][index] for a in ARMS)
        scores = [f"{r['score']['A']}–{r['score']['B']} ({r['score']['B']-r['score']['A']:+d})" for r in (r3,e1)]
        times = [f'{cost:.2f}' for cost in (r3['cpu_s'],r3['matched_cpu_s'],e1['cpu_s'])]
        lines.append('| '+' | '.join((('Garvian–Ala','Yukïma–Isu’Kari')[pair],str(seed),*scores,*times))+' |')
    lines.extend(['','## Sampled E1 body-outs','',
                  f'{len(sample)} episodes drawn with seed {SAMPLE_SEED}. The companion gzip contains their complete histories.',
                  '','| Pair | Seed | Engine ms | Athlete | Cause | Event |','| ---: | ---: | ---: | --- | --- | ---: |'])
    for e in sample:
        lines.append('| '+' | '.join(str(e[k]) for k in ('pair','seed','ms','carrier','cause','event_id'))+' |')
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser()
    for key in ('evidence','parent','tables','episodes'):
        parser.add_argument(key,type=Path)
    args = parser.parse_args()
    rows = read(args.evidence,args.parent)
    sample = sampled(rows)
    args.tables.write_text(render(rows,sample),encoding='utf8')
    args.episodes.write_bytes(encoded(sample))


if __name__=='__main__':
    main()
