"""Check full-match identities and report the tackle correction without re-running matches."""
import argparse
import gzip
import json
from pathlib import Path

FIELDS = ('score', 'trace_hash', 'state_hash', 'config_digest')
EVIDENCE_329 = Path('audit/native/rb329/evidence')


def load(path):
    return json.loads(gzip.decompress(path.read_bytes()) if path.suffix == '.gz' else path.read_bytes())


def assert_identity(actual, expected):
    for field in FIELDS:
        assert actual[field] == expected[field], (field, actual[field], expected[field])


def identities(root):
    for mode in ('compatibility', 'core'):
        actual = load(root / f'{mode}.json')
        assert_identity(actual, load(EVIDENCE_329 / f'{mode}.json'))
        print(mode, {field: actual[field] for field in FIELDS})
    for mode in ('R1', 'R2'):
        actual = load(root / f'{mode}-replay.json.gz')
        assert_identity(actual, load(EVIDENCE_329 / f'runs/{mode}/0-1.json.gz'))
        print(mode, {field: actual[field] for field in FIELDS})
    old = load(EVIDENCE_329 / 'boxes/R2.json')['teams']
    new = load(root / 'R2-replay.json.gz')['team_lines']
    fields = ('tackles_attempted', 'tackles_made', 'takedowns')
    for before, after in zip(old, new, strict=True):
        print('R2 tackles', after['team'], {k: [before[k], after[k]] for k in fields})


def repeat(root):
    first = load(root / 'runs/0-1.json.gz')
    second = load(root / 'PLANNED-replay.json.gz')
    assert_identity(first, second)
    times = {'cpu_s', 'cpu_ms_per_step'}
    assert {k: v for k, v in first.items() if k not in times} == {k: v for k, v in second.items() if k not in times}
    print('PLANNED fresh process', {field: first[field] for field in FIELDS})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('identities', 'repeat'))
    parser.add_argument('root', type=Path)
    args = parser.parse_args()
    (identities if args.mode == 'identities' else repeat)(args.root)


if __name__ == '__main__':
    main()
