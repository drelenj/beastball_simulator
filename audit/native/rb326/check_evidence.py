"""Verify the saved conditions for the Reaction, replay, Drill and Gauge evidence."""
import argparse
import gzip
import json
from pathlib import Path
from statistics import median


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('evidence',type=Path)
parser.add_argument('--artifact',type=Path,default=Path('native/oracle/artifacts/drill-v0.json'))
args = parser.parse_args()


def load(name):
    return json.loads((args.evidence/name).read_text())


def jsonl(name):
    with gzip.open(args.evidence/name,'rt') as stream:
        return [json.loads(line) for line in stream]


def fingerprint(row):
    return tuple(row[k] for k in ('score','trace_hash','state_hash','config_digest','steps'))


assert (args.evidence/'legacy.txt').read_bytes() == Path('native/evidence/rb3-reach/legacy-hashes.txt').read_bytes()
suite = (args.evidence/'pytest.txt').read_text()
assert ' failed' not in suite and ' subtests passed ' in suite
print(next(line for line in suite.splitlines() if 'subtests passed' in line))
assert fingerprint(load('bench-core-1.json')) == fingerprint(load('bench-core-1-repeat.json'))
old = median(load(f'bench-baseline-{seed}.json')['cpu_ms_per_step'] for seed in (1,3))
new = median(load(f'bench-core-{seed}.json')['cpu_ms_per_step'] for seed in (1,3))
assert new <= 1.15*old, (old,new)
print(f'CORE {new:.3f} ms/step against RB-3.22 {old:.3f}, {100*(new/old-1):+.2f}%')

for mode in ('off','core'):
    replay = load(f'resume-{mode}.json')
    baseline = replay['uninterrupted']
    assert baseline['status'] == 'final'
    assert [r['capture_step'] for r in replay['fresh_processes']] == [4000,14000,25000]
    assert all(fingerprint(row['fingerprint']) == fingerprint(baseline) for row in replay['fresh_processes'])
    if mode == 'core':
        assert fingerprint(baseline) == fingerprint(load('task0-core.json'))
    else:
        assert baseline['score'] == {'A':57,'B':76}
        assert baseline['trace_hash'] == '44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072'
        assert baseline['state_hash'] == '046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d'
    print(mode,baseline['score'],baseline['trace_hash'],baseline['state_hash'])

summary = load('summary.json')
moments = jsonl('moments.jsonl.gz')
grades = jsonl('grades.jsonl.gz')
gauge = jsonl('gauge.jsonl.gz')
assert len(moments) == len({row['moment'] for row in moments}) == len(grades)
assert [row['moment'] for row in moments] == [row['moment'] for row in grades]
for moment,grade in zip(moments,grades,strict=True):
    assert [row[0] for row in moment['menu']['options']] == [row['label'] for row in grade['options']]
    for option in grade['options']:
        assert len(option['samples']) == 20
        assert len({row['seed'] for row in option['samples']}) == 20
assert sum(row['rollouts'] for row in grades) == summary['rollouts']
assert summary['moments_by_stage']['carrier'] >= 60
assert all(summary['moments_by_stage'].get(name,0) >= 30 for name in ('passing','finishing','takedown'))
assert len(gauge) == 3*20*summary['moments_by_stage']['carrier']
assert all(row['perceived_regret'] == 0. for row in gauge)
artifact = json.loads(args.artifact.read_text())
assert artifact['schema'] == 'oracle-drill-v0/1' and artifact['holdout_seed'] == 3
assert all(table['held_out'] > 0 for table in artifact['tables'].values())
print(f'Drill {len(moments)} moments, {summary["rollouts"]} rollouts, {len(gauge)} Gauge trials.')
