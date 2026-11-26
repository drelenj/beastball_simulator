"""Render RB-3.34 tables offline from the saved match observations."""
import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
from statistics import mean

from audit.native.rb333.tables import ARMS, measures, pct, quantile

IDENTITY = ('score', 'trace_hash', 'state_hash', 'config_digest')
CAUSES = ('stale belief', 'release in flight', 'handoff', 'other')
MIX = ('shot', 'route_carry', 'continuation', 'stretch')


def load(root, name):
    with gzip.open(root / f'{name}.json.gz', 'rt', encoding='utf8') as stream:
        return json.load(stream)


def fmt(value):
    if value is None:
        return '—'
    return f'{value:.2f}' if isinstance(value, (int, float)) else str(value)


def render(root, historical):
    seeds = [load(root, f'A6-{seed}') for seed in range(1, 6)]
    repeat = load(root, 'A6-repeat')
    assert all(value == repeat[key] for key, value in seeds[0].items()
               if key not in ('cpu_s', 'cpu_profile'))
    for label in ARMS:
        expected, replay = load(historical, label), load(root, label)
        assert all(replay[k] == expected[k] for k in IDENTITY), label
    compare = [load(historical, label) for label in ('A4', 'A5')]
    observations = [load(root, label)['rb334'] for label in ('A4', 'A5')]
    observations += [run['rb334'] for run in seeds]
    all_runs = compare + seeds
    assert all(run['status'] == 'final' and run['invariants'] == 'passed'
               and run['restart_completion_ratio'] == 1 for run in all_runs)
    lines = ['# RB-3.34 results', '',
             'Garvian Guardians vs Ala Apex. Counts are per team per game unless specified. '
             'Means give each of the five A6 games equal weight. Rates pool both teams within each game. '
             'Percentage differences are in points. An em dash marks a missing denominator.', '']

    def table(headers, cells):
        lines.append('| ' + ' | '.join(headers) + ' |')
        lines.append('|' + '|'.join(['---'] * len(headers)) + '|')
        for row in cells:
            lines.append('| ' + ' | '.join(map(fmt, row)) + ' |')
        lines.append('')

    arm_labels = ('A4 seed 1', 'A5 seed 1', *(f'A6 seed {s}' for s in range(1,6)))
    headers = ('Measure', *arm_labels, 'A6 mean', 'A6 seed 1 − A4', 'A6 seed 1 − A5')
    metrics = [measures(run) for run in all_runs]

    def metric(key):
        column = [run[key] for run in metrics]
        valid = [x for x in column[2:] if x is not None]
        deltas = [column[2]-other if None not in (column[2], other) else None for other in column[:2]]
        return key[1], *column, mean(valid) if valid else None, *deltas

    for section in dict.fromkeys(k[0] for k in metrics[0]):
        lines.extend([f'## {section}', ''])
        table(headers, (metric(key) for key in metrics[0] if key[0] == section))

    lines.extend(['## Keeper at release', '',
                  'Target speed is net target displacement over 500 ms. Target distance uses the current '
                  'accepted settle target and keeper centre. Target speed requires 500 ms of continuous settle commands.', ''])
    keeper_rows = []
    for label, run in zip(arm_labels, observations):
        shots = run['keeper_at_shot']
        assert len(shots) == run['shots_faced']
        speed = [shot['speed_mps'] for shot in shots]
        distances = [shot['settle_distance_m'] for shot in shots if shot['settle_distance_m'] is not None]
        drift = [shot['settle_speed_mps'] for shot in shots if shot['settle_speed_mps'] is not None]
        cuts = [quantile(vals, q) for vals in (speed, distances, drift) for q in (.1,.5,.9)]
        keeper_rows.append((label, len(shots), len(distances), len(drift),
                            pct(sum(x>run['keeper_set_mps'] for x in speed),len(speed)),*cuts))
    table(('Game','Shots faced','With target','500 ms history','Above set speed (%)',
           *(f'{metric} {p}' for metric in ('Keeper speed (m/s)','Target distance (m)','Target speed (m/s)')
             for p in ('P10','P50','P90'))), keeper_rows)

    lines.extend(['## Near-goal carrier menu', ''])
    mixes = [Counter(run['near_goal_mix']) for run in observations]
    mixes.append(sum(mixes[2:],Counter()))
    table(('Game','Decisions',*MIX), ((label,mix.total(),*(pct(mix[k],mix.total()) for k in MIX))
           for label,mix in zip((*arm_labels,'A6 pooled'),mixes)))

    lines.extend(['## Non-carrier takedown commitments', '',
                  'Counts cover full commitment episodes. Preferred cause classes are handoff, then release '
                  'in flight, then a matching remembered holder, then other. These labels infer an explanation '
                  'from event order and the original view. The raw evidence holds 20 episodes per A6 game, '
                  'sampled independently with seed 334. The seed-1 sample is shown below.', ''])
    counts = [Counter(run['phantom_causes']) for run in observations[2:]]
    counts.append(sum(counts,Counter()))
    table(('Game','Total',*CAUSES), ((label,c.total(),*(c[k] for k in CAUSES))
          for label,c in zip((*arm_labels[2:],'A6 total'),counts)))
    sample = observations[2]['phantom_sample']
    table(('Time (ms)','Tackler','Target','True holder','Believed holder','Age (ms)','Cue','Since release (ms)','Cause','End','End (ms)'),
          ((r['start_ms'],r['player'],r['target'],r['true_holder'],r['believed_holder'],
            r['frame_age_ms'],str(r['release_cue_active']),r['since_release_ms'],r['cause'],r['outcome'],r['end_ms'])
           for r in sample))
    return '\n'.join(lines).rstrip()+'\n'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('evidence', type=Path)
    parser.add_argument('historical', type=Path)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    args.out.write_text(render(args.evidence,args.historical), encoding='utf8')


if __name__ == '__main__':
    main()
