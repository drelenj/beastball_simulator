"""Summarize paired matches from their raw participation and rotation records."""
import argparse
from collections import Counter
import csv
import json
from math import sqrt
from pathlib import Path
from statistics import mean, median, stdev


def group_minutes(row):
    groups = {}
    for athlete in row['participation'].values():
        key = athlete['role'] + ('_starter' if athlete['starter'] else '_bench')
        if 'regulation_ms' not in athlete and row['live_ms'] > 2_400_000:
            raise ValueError('regulation minutes are missing for an overtime result')
        groups.setdefault(key, []).append(athlete.get('regulation_ms', athlete['live_ms']) / 60_000)
    return groups


def describe(xs):
    return {'mean': mean(xs), 'min': min(xs), 'max': max(xs), 'n': len(xs)}


def summarize(paths):
    minutes = {}
    tiers, reasons, required_tiers = Counter(), Counter(), Counter()
    possessions, attempt_ending, scores, margins, primary = [], [], [], [], []
    rules_subs = 0
    rows = []
    for path in paths:
        row = json.loads(path.read_text())
        if row['status'] != 'final' or row['restart_completion_ratio'] != 1.:
            raise ValueError(f'{path}: unfinished regulation record')
        groups = group_minutes(row)
        for key, values in groups.items():
            minutes.setdefault(key, []).extend(values)
        counts = Counter()
        required_tiers.update(event['data']['tier'] for event in row.get('required_rotation_substitutions', ()))
        for event in row.get('fatigue_substitutions', ()):
            data = event['data']
            tiers[data['tier']] += 1
            reasons[data['reason']] += 1
            counts[data['team']] += 1
        score_a, score_b = (row['score'][team] for team in 'AB')
        margins.append(score_b - score_a)
        if path.name.startswith('0-'):
            primary.append(margins[-1])
        scores.extend((score_a, score_b))
        counts_poss = [row['possessions'][team]['count'] for team in 'AB']
        shares = [row['possessions'][team]['share_ending_in_attempt'] for team in 'AB']
        possessions.extend(counts_poss)
        attempt_ending.extend(shares)
        rules_subs += sum(r['outgoing'] is not None for r in row['rules_substitutions'])
        rows.append((path.stem, row['seed'], *row['teams'], score_a, score_b, *counts_poss,
                     *shares, counts['A'], counts['B'], row['trace_hash'], row['state_hash']))
    return {
        'games': len(paths), 'minutes': {k: describe(v) for k, v in minutes.items()},
        'median_team_score': median(scores), 'team_score_sample_sd': stdev(scores),
        'mean_possessions': mean(possessions), 'median_possessions': median(possessions),
        'mean_attempt_ending_share': mean(attempt_ending),
        'median_abs_margin': median(map(abs, margins)),
        'share_decided_by_5_or_fewer': mean(abs(m) <= 5 for m in margins),
        'substitutions_per_team_game': rules_subs / (2 * len(paths)),
        'fatigue_substitutions_per_team_game': sum(tiers.values()) / (2 * len(paths)),
        'substitutions_by_tier': dict(tiers), 'substitutions_by_reason': dict(reasons),
        'other_substitutions': rules_subs - sum(tiers.values()),
        'required_substitutions_by_tier': dict(required_tiers),
        'ala_minus_garvian_mean': mean(primary) if primary else None,
        'ala_minus_garvian_se': stdev(primary) / sqrt(len(primary)) if len(primary) > 1 else None,
        'ala_wins': sum(m > 0 for m in primary), 'garvian_wins': sum(m < 0 for m in primary),
    }, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('runs', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    summary = {}
    args.out.mkdir(parents=True, exist_ok=True)
    with (args.out / 'matches.csv').open('w', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(('mode', 'case', 'seed', 'A', 'B', 'score_A', 'score_B',
                         'possessions_A', 'possessions_B', 'terminal_attempt_share_A',
                         'terminal_attempt_share_B', 'fatigue_subs_A', 'fatigue_subs_B',
                         'trace', 'state'))
        for mode in ('off', 'on'):
            paths = sorted((args.runs / mode).glob('*.json'))
            if paths:
                summary[mode], rows = summarize(paths)
                writer.writerows((mode, *row) for row in rows)
    (args.out / 'summary.json').write_text(json.dumps(summary, indent=2, sort_keys=True) + '\n')


if __name__ == '__main__':
    main()
