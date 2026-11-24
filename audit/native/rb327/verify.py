"""Check the completeness and fingerprints of an RB-3.27 results directory."""
import argparse
from collections import Counter
import gzip
from hashlib import sha256
import json
from pathlib import Path

from match import PAIRS


GUARDS = {
    'compatibility': (
        {'A': 57, 'B': 76},
        '44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072',
        '046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d',
    ),
    'core': (
        {'A': 61, 'B': 80},
        'c1a578db3f2754d3f69b47ba81a1f9d5b9336e1d87f496de2fa8dc3daee7a256',
        'c517e00f864f1438705cdd1d9768d61523ee1aaac69746f57a2e9f1f4adf2745',
    ),
}


def read(path):
    return json.loads(path.read_text())


def json_lines(path):
    with gzip.open(path, 'rt') as source:
        yield from map(json.loads, source)


def fingerprints(record):
    return tuple(record[key] for key in ('score', 'trace_hash', 'state_hash'))


def check_match(row, seed, digest=None):
    assert row['seed'] == seed and row['status'] == 'final'
    assert row['restart_completion_ratio'] == 1 and row['invariants'] == 'passed'
    assert row['config'].get('drill_values_sha256') == digest


def verify(root, workbook, artifact):
    digest = sha256(artifact.read_bytes()).hexdigest()
    book_digest = sha256(workbook.read_bytes()).hexdigest()
    summary = read(root / 'drill/summary.json')
    assert digest == summary['artifact_sha256']
    data = read(artifact)
    assert data['train_seeds'] == list(range(1, 9)) and data['holdout_seeds'] == [9, 10]
    assert {row['seed'] for row in data['provenance']['match_fingerprints']} == set(range(1, 11))

    grade_count = 0
    counts = Counter()
    for row, grade in zip(json_lines(root / 'drill/moments.jsonl.gz'),
                          json_lines(root / 'drill/grades.jsonl.gz'), strict=True):
        assert grade['moment'] == row['moment'] and grade['stage'] == row['stage']
        assert grade['horizon'] == 'possession'
        counts[row['group']] += 1
        for option in grade['options']:
            trials = option['samples']
            assert len(trials) == 20 and len({trial['seed'] for trial in trials}) == 20
            assert all(trial['score'] == trial['points_for'] - trial['points_against'] for trial in trials)
            assert row['stage'] == 'carrier' or all('action_outcome' in trial for trial in trials)
            grade_count += len(trials)
    assert len([group for group in counts if group.startswith('carrier/')]) == 6
    assert all(n >= 33 for group, n in counts.items() if group.startswith('carrier/'))
    assert all(counts[group] >= 60 for group in ('passing', 'finishing', 'takedown'))
    assert grade_count == summary['rollouts']

    for name, expected in GUARDS.items():
        record = read(root / f'{name}.json')
        check_match(record, 1)
        assert fingerprints(record) == expected
    guard_path = Path('native/evidence/rb3-reach/legacy-hashes.txt')
    assert (root / 'legacy.txt').read_bytes() == guard_path.read_bytes()

    for form in ('real', 'control'):
        for seed in range(1, 6 if form == 'real' else 2):
            check_match(read(root / f'anchor/{form}-{seed}.json'), seed, digest)
    repeat = read(root / 'determinism/real-1-repeat.json')
    check_match(repeat, 1, digest)
    assert fingerprints(repeat) == fingerprints(read(root / 'anchor/real-1.json'))

    for mode, expected_digest in (('soak-off', None), ('soak-on', digest)):
        for pair in range(len(PAIRS)):
            for seed in range(1, 11 if pair == 0 else 3):
                row = read(root / f'{mode}/{pair}-{seed}.json')
                check_match(row, seed, expected_digest)
                assert tuple(row['teams']) == PAIRS[pair] and row['workbook_sha256'] == book_digest
                for selected in row['selected'].values():
                    assert Counter(a['role'] for a in selected) == {'keeper': 2, 'archer': 2, 'field': 18}
                    assert len({a['id'] for a in selected}) == 22
    print(json.dumps({'branches': grade_count, 'strata': counts,
                      'full_regulation_runs_verified': 49,
                      'artifact_sha256': digest}, sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path)
    parser.add_argument('--workbook', type=Path, required=True)
    parser.add_argument('--artifact', type=Path, required=True)
    args = parser.parse_args()
    verify(args.root, args.workbook, args.artifact)


if __name__ == '__main__':
    main()
