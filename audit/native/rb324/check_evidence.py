"""Validate stored release evidence without rerunning matches."""
import argparse
import json
from pathlib import Path
from statistics import median

parser = argparse.ArgumentParser()
parser.add_argument('evidence', type=Path)
args = parser.parse_args()
path = args.evidence
reference = Path('native/evidence/rb3-reach/legacy-hashes.txt').read_bytes()


def load(name):
    return json.loads((path / (name + '.json')).read_text())


def match_fingerprint(case):
    return tuple(case[k] for k in ('score', 'trace_hash', 'state_hash', 'config_digest', 'steps'))


compat = load('final-compatibility')
assert compat['status'] == 'final' and compat['score'] == {'A': 57, 'B': 76}
assert compat['trace_hash'] == '44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072'
assert compat['state_hash'] == '046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d'
print('Compatibility replay exact.')

for suite in ('phase1', 'final'):
    log = (path / (suite + '-pytest.txt')).read_text()
    assert ' failed' not in log
    assert 'subtests passed' in log
    print(suite, next(line for line in log.splitlines() if 'subtests passed' in line))
    assert reference == (path / (suite + '-legacy.txt')).read_bytes()
    print(suite, 'six legacy rows match.')

parent = json.loads(Path('audit/native/rb323/evidence/benchmark.json').read_text())
for fixture in parent['runs']['individuation/1']:
    replay = load(f"bench-schema-{fixture['seed']}")
    for key in ('trace_hash', 'state_hash', 'config_digest'):
        assert replay[key] == fixture[key], (fixture['seed'], key)
print('Schema windows preserve RB-3.23 enabled replay.')

base = median(load(f'bench-baseline-{seed}')['cpu_ms_per_step'] for seed in (1, 3))
print('RB-3.22 median CPU ms/step', round(base, 3))
for mode in ('schema', 'final'):
    first = load(f'bench-{mode}-1')
    repeat = load(f'bench-{mode}-1-repeat')
    assert match_fingerprint(first) == match_fingerprint(repeat)
    assert first['commit_log_sha256'] == repeat['commit_log_sha256']
    metric = median(load(f'bench-{mode}-{seed}')['cpu_ms_per_step'] for seed in (1, 3))
    print(mode, 'seed-1 deterministic:', first['trace_hash'], first['state_hash'])
    print(mode, 'median CPU ms/step', round(metric, 3), 'ratio to baseline', round(metric / base, 4),
          'speed gate', 'PASS' if metric / base <= 1.15 else 'OVER BUDGET')

for case in ('neutral-real-off', 'neutral-real-final-on', 'control-off', 'control-on'):
    x = load(case)
    assert x['status'] == 'final' and x['invariants'] == 'passed'
    assert x['restart_closed'] == x['restart_awarded']
    print(case, x['score'], {team: row['count'] for team, row in x['possessions'].items()},
          'steps', x['steps'], 'restarts', x['restart_closed'],
          'CPU ms/step', round(x['cpu_ms_per_step'], 3),
          'trace', x['trace_hash'], 'state', x['state_hash'])

first = load('neutral-real-final-on')
repeat = load('neutral-real-final-repeat')
assert repeat['status'] == first['status'] == 'final'
assert match_fingerprint(first) == match_fingerprint(repeat)
assert first['prism_commits'] == repeat['prism_commits']
assert first['restart_statuses'] == repeat['restart_statuses']
print('Enabled neutral real-roster seed 1 repeated exactly through regulation.')
