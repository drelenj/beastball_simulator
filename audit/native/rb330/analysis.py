"""Summarize the planned rotation soak and compare the old/new tackle credit."""
import argparse
from collections import Counter
import csv
import gzip
import json
from math import sqrt
from pathlib import Path
from statistics import mean, median, stdev


def summarize(root):
    runs = [json.loads(gzip.decompress(f.read_bytes())) for f in sorted((root / 'runs').glob('*.json.gz'))]
    match_rows = []
    starter_minutes, bench_minutes, extra_minutes, keepers, archers = [], [], [], [], []
    margins = []
    by_stamina = Counter()
    reasons = Counter()
    for run in runs:
        assert run['status'] == 'final' and run['invariants'] == 'passed'
        assert run['restart_completion_ratio'] == 1
        a, b = (run['score'][t] for t in 'AB')
        if run['pair'] == 0:
            margins.append(b - a)
        planned_ids = {pid for waves in run['plan']['waves'].values() for wave in waves for pid in wave}
        matchup = dict(pair=run['pair'], seed=run['seed'], home=run['teams'][0], away=run['teams'][1],
                       home_score=a, away_score=b, absolute_margin=abs(a-b), cpu_s=run['cpu_s'],
                       trace_hash=run['trace_hash'], state_hash=run['state_hash'], config_digest=run['config_digest'])
        for p in run['participation']:
            if p['role'] == 'field':
                bucket = starter_minutes if p['player'] in planned_ids else extra_minutes if p['starter'] else bench_minutes
            elif p['starter']:
                bucket = keepers if p['role'] == 'keeper' else archers
            else:
                continue
            bucket.append(p['regulation_ms'] / 60_000)
        for team, line in zip('AB', run['team_lines'], strict=True):
            for label, field in (('possessions', 'possessions'), ('attempts', 'possessions_ending_in_attempt')):
                matchup[f'{team}_{label}'] = line[field]
            matchup[f'{team}_throw4_points'] = line['scoring_points_by_method'].get('throw_4', 0)
            team_reasons = Counter()
            for event in run['rotations']:
                d = event['data']
                if d['team'] == team:
                    team_reasons[d['reason']] += 1
                    if d['reason'] == 'energy_override':
                        by_stamina[str(d['outgoing_stamina'])] += 1
            reasons.update(team_reasons)
            for reason in ('planned_out', 'planned_return', 'energy_override', 'override_return'):
                matchup[f'{team}_{reason}'] = team_reasons[reason]
        match_rows.append(matchup)
    count = len(match_rows)
    team_count = count * 2
    scores = [r[f'{side}_score'] for r in match_rows for side in ('home', 'away')]
    def total(field):
        return sum(r[f'{t}_{field}'] for r in match_rows for t in 'AB')
    possessions = total('possessions')

    def span(minutes):
        if not minutes:
            return dict(count=0, mean=None, minimum=None, maximum=None)
        return dict(count=len(minutes), mean=mean(minutes), minimum=min(minutes), maximum=max(minutes))
    summary = dict(matches=count, starter_minutes=span(starter_minutes), bench_minutes=span(bench_minutes),
                   extra_field_minutes=span(extra_minutes), keeper_minutes=span(keepers), archer_minutes=span(archers),
                   changes=dict(reasons), changes_per_team={k: v/team_count for k, v in reasons.items()},
                   override_exits_by_stamina=dict(sorted(by_stamina.items())),
                   median_team_score=median(scores), team_score_sd=stdev(scores), mean_possessions=possessions/team_count,
                   attempt_share=total('attempts')/possessions, close_share=sum(r['absolute_margin'] <= 5 for r in match_rows)/count,
                   median_absolute_margin=median(r['absolute_margin'] for r in match_rows),
                   throw4_points_share=total('throw4_points')/sum(scores), cpu_s=sum(r['cpu_s'] for r in match_rows))
    if margins:
        summary['ala_margin'] = dict(mean=mean(margins), se=stdev(margins)/sqrt(len(margins)) if len(margins)>1 else None,
                                     wins=sum(v>0 for v in margins), matches=len(margins))
    return summary, match_rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    summary, rows = summarize(args.root)
    serialized = json.dumps(summary, indent=2) + '\n'
    (args.root / 'summary.json').write_text(serialized)
    with (args.root / 'matches.csv').open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
    print(serialized, end='')


if __name__ == '__main__':
    main()
