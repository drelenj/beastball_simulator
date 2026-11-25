"""Run one RB-3.30 identity match or the paired step benchmark."""
import argparse
import json
from pathlib import Path
from statistics import mean

from audit.native.rb330.match import match
from native.oracle.matches import match_build
from native.rulebook.fatigue_rotation import PLANNED_RATE_SCALE


FIELDS = ('config_digest', 'trace_hash', 'state_hash', 'score', 'steps', 'status', 'live_ms', 'runtime_s')


def identity(mode):
    driver = match_build(1, mode=mode).create(record=False)
    driver.enable_stats()
    driver.play()
    result = driver.result()
    return {field: result[field] for field in FIELDS}


def benchmark(workbook, scale):
    samples = []
    for seed, modes in ((1, ('R1', 'PLANNED')), (3, ('PLANNED', 'R1')),
                        (3, ('R1', 'PLANNED')), (1, ('PLANNED', 'R1'))):
        for mode in modes:
            row, _ = match(workbook, mode, 0, seed, steps=1500, scale=scale)
            samples.append({field: row[field] for field in
                            ('seed', 'variant', 'cpu_ms_per_step', 'steps', 'trace_hash', 'state_hash')})
    costs = {mode: mean(r['cpu_ms_per_step'] for r in samples if r['variant'] == mode)
             for mode in ('R1', 'PLANNED')}
    return dict(samples=samples, means=costs, overhead_pct=100 * (costs['PLANNED'] / costs['R1'] - 1))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('compatibility', 'core', 'benchmark'))
    parser.add_argument('--workbook', type=Path)
    parser.add_argument('--scale', type=float, default=PLANNED_RATE_SCALE)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = benchmark(args.workbook, args.scale) if args.mode == 'benchmark' else identity(args.mode)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(args.mode, json.dumps(result), flush=True)


if __name__ == '__main__':
    main()
