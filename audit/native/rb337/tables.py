"""Render all RB-3.37 paired tables from archived records."""
import argparse
from collections import Counter
from math import sqrt
from pathlib import Path
from statistics import mean, stdev

from audit.native.rb333.tables import pct
from audit.native.rb334.tables import IDENTITY, load
from audit.native.rb336.tables import metrics as sets_metrics
from native.roster import turning

ARMS = ('L0','L1','L2')
CONTRASTS = (('L1','L0'),('L2','L0'),('L2','L1'))
CASES = tuple((0,s) for s in range(1,6))+tuple((1,s) for s in range(1,4))
CAUSES = ('wrap/takedown','strip attempt','collision without grip','reception drop','handoff','other')
BANDS = ('<.60','.60–.69','.70–.79','≥.80','unknown')


def metrics(row):
    source = sets_metrics(row)
    skip = ('Keeper above','catch ','interception reactions','deflection ','takedown reactions',
            'takedown success (%) cost','takedown success (%) no cost','loose_pursuit ')
    out = {k:v for k,v in source.items() if not k.startswith(skip)}
    out['Second team minus first team margin'] = out.pop('Ala minus Garvian margin')
    witness = row['rb337']
    contact = row['rb335']['carrier_after_contact']
    boundaries = Counter()
    for event in row['boundary']:
        if event['kind']!='carrier':
            continue
        x,y = event['crossing']
        line = 'end line' if min(x,100-x)<=min(y,100-y) else 'sideline'
        origin = 'after contact' if contact.get(str(event['event_id']),False) else 'self-run'
        boundaries[line,origin] += 1
    for line in ('sideline','end line'):
        for origin in ('self-run','after contact'):
            out[f'Carrier body-out {line} {origin}'] = boundaries[line,origin]/2
    out['Carrier body-outs, total'] = sum(boundaries.values())/2
    out['Passed balls out'] = sum(e['kind']=='pass' for e in row['boundary'])/2
    for move in ('juke','spin','stiff_arm','truck'):
        results = witness['evasion'].get(move,{})
        attempts,successes = (results.get(k,0) for k in ('attempts','successes'))
        out[move+' attempts'] = attempts/2
        out[move+' successes'] = successes/2
        out[move+' success (%)'] = pct(successes,attempts)
    fumbles = Counter((r['cause'],r['band']) for r in witness['fumbles'])
    assert len(witness['fumbles'])==sum(r['end_reason']=='fumble' for r in row['box']['possessions'])
    out['Possession-ending fumbles, classified'] = len(witness['fumbles'])/2
    for cause in CAUSES:
        out['Fumble '+cause] = sum(fumbles[cause,band] for band in BANDS)/2
        for band in BANDS:
            out[f'Fumble {cause}, Handling {band}'] = fumbles[cause,band]/2
    details = Counter(r['detail'] for r in witness['fumbles'] if r['cause']=='other')
    for label in ('freeze of carrier','unresolved forced release','unlinked ledger attribution'):
        out['Other fumble, '+label] = details[label]/2
    related = Counter((r['cause'],r['band']) for r in witness['supplemental_losses'])
    for cause in ('strip attempt','reception drop'):
        out['Related turnover '+cause] = sum(related[cause,band] for band in BANDS)/2
        for band in BANDS:
            out[f'Related turnover {cause}, Handling {band}'] = related[cause,band]/2
    return out


def collect(root,parent):
    rows = {a:[load(root,f'{a}-{pair}-{seed}') for pair,seed in CASES] for a in ARMS}
    for seed,game in enumerate(rows['L0'][:5],1):
        original = load(parent,f'T3-{seed}')
        assert all(game[k]==original[k] for k in IDENTITY), seed
    repeat = load(root,'L1-repeat')
    assert all(repeat[k]==value for k,value in rows['L1'][0].items() if k not in ('cpu_s','cpu_profile'))
    assert all(row['status']=='final' and row['invariants']=='passed' and row['restart_completion_ratio']==1
               for games in rows.values() for row in games)
    return rows


def render(root,parent):
    rows = collect(root,parent)
    values = {a:[metrics(r) for r in games] for a,games in rows.items()}
    lines = ['# RB-3.37 paired results','',
             'Counts are per team per game unless stated. Rates pool both teams within each game. '
             'The combined mean weights the eight games equally. A tilde marks differences within two '
             'paired SEs. A dash means the statistic has no usable denominator or fewer than two pairs. '
             'Rate differences are in percentage points.','']
    for name,indices in (('Combined',range(8)),('Garvian–Ala',range(5)),('Yukïma–Isu’Kari',range(5,8))):
        lines.extend([f'## {name}', '',
                      '| Measure | '+' | '.join((*ARMS,*(f'{a} − {b}' for a,b in CONTRASTS)))+' |',
                      '| '+' | '.join(['---']*7)+' |'])
        for key in values['L0'][0]:
            columns = {a:[values[a][i][key] for i in indices] for a in ARMS}
            cells = []
            for column in columns.values():
                eligible = [x for x in column if x is not None]
                cells.append(f'{mean(eligible):.2f}' if eligible else '—')
            for a,b in CONTRASTS:
                delta = [x-y for x,y in zip(columns[a],columns[b]) if None not in (x,y)]
                if len(delta)<2:
                    cells.append('—')
                else:
                    effect,se = mean(delta),stdev(delta)/sqrt(len(delta))
                    cells.append(f'{effect:+.2f} ± {se:.2f}'+(' ~' if abs(effect)<=2*se else '')+
                                 (f' (n={len(delta)})' if len(delta)!=len(indices) else ''))
            lines.append('| '+' | '.join((key,*cells))+' |')
        lines.append('')
    lines.extend(['## Turning radius in metres','',
                  'The body-model limit is v² divided by lateral acceleration. Values use fresh athletes.','',
                  '| Arm | Agility | At 10 m/s | At 20 m/s | At 30 m/s |','| --- | ---: | ---: | ---: | ---: |'])
    for arm,scale in zip(ARMS,(1.,1.5,2.)):
        for agility in (.60,.70,.80):
            radii = [f'{speed**2/turning(agility,scale):.2f}' for speed in (10,20,30)]
            lines.append('| '+' | '.join((arm,f'{agility:.2f}',*radii))+' |')
    lines.extend(['','## Scores and signed margins','',
                  'The score is listed in matchup order. Positive margins favor the second team.','',
                  '| Pairing | Seed | L0 | L1 | L2 |','| --- | ---: | ---: | ---: | ---: |'])
    for index,(pair,seed) in enumerate(CASES):
        scores = [rows[a][index]['score'] for a in ARMS]
        cells = [f"{s['A']}–{s['B']} ({s['B']-s['A']:+d})" for s in scores]
        lines.append('| '+' | '.join((('Garvian–Ala','Yukïma–Isu’Kari')[pair],str(seed),*cells))+' |')
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root',type=Path)
    parser.add_argument('parent',type=Path)
    parser.add_argument('out',type=Path)
    args = parser.parse_args()
    args.out.write_text(render(args.root,args.parent),encoding='utf8')


if __name__=='__main__':
    main()
