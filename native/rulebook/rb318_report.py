"""Aggregate RB-3.18 baseline, rule-only and move-enabled evidence."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path

from .scoring_audit import match_metrics


def rows(root):
    results = match_metrics(root)
    for row in results:
        path = Path(row['raw_log'])
        if not path.exists():
            continue
        open_log = gzip.open if path.suffix == '.gz' else open
        with open_log(path, 'rt') as stream:
            log = json.load(stream)['log']
        counts = Counter(event['event'] for event in log)
        points = {team: Counter() for team in ('A', 'B')}
        for event in log:
            data = event['data']
            if event['event'] == 'goal':
                method = data['method']
                label = ('release_carry' if data.get('release_carry') else
                         data.get('band', method) if method == 'release' else method)
                points[data['team']][label] += data['points']
            elif event['event'] == 'foul_award':
                label = 'half_award' if data['points'] == 1 else 'full_award'
                points[data['team']][label] += data['points']
        if row['status'] == 'final':
            assert {team: sum(values.values()) for team, values in points.items()} == row['score']
        row['points_by_method'] = points
        row['moves'] = {name: counts[name] for name in
                        ('stretch_start', 'stretch_end', 'stretch_goal', 'stiff_arm', 'stiff_arm_effect',
                         'truck', 'truck_broken', 'truck_stopped', 'handoff_complete', 'block_engaged')}
        effects = [event['data'] for event in log if event['event'] == 'stiff_arm_effect']
        row['stiff_arm_reacquire_delays'] = sum(data['reacquire_ms'] > 0 for data in effects)
        row['stiff_arm_grip_reductions'] = sum(data['grip_after'] < data['grip_before'] for data in effects)
        row['strips'] = counts['strip']
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('evidence')
    parser.add_argument('--baseline', default='native/evidence/rb316/runs')
    args = parser.parse_args()
    print(json.dumps({'baseline': rows(args.baseline),
                      'rule': rows(Path(args.evidence) / 'rule'),
                      'on': rows(Path(args.evidence) / 'on')}, indent=2))


if __name__ == '__main__':
    main()
