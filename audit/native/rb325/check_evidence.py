"""Verify recorded CORE gates and summarize the neutral regulation anchor."""
import argparse
from pathlib import Path
from statistics import median
import json

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('directory',type=Path)
parser.add_argument('--require-anchor', action='store_true',
                    help='Exit unsuccessfully unless both body sets meet the calibration ranges.')
args=parser.parse_args()
root=args.directory


def run(name):
    return json.loads((root/(name+'.json')).read_text())


def fingerprint(result):
    return tuple(result[k] for k in ('status','steps','score','trace_hash','state_hash','config_digest'))


old=run('on-1')
assert old['score']=={'A':35,'B':29}
assert old['trace_hash']=='1678fcb5ef42277063942f0c43f1d5c23d6d54be33d05a62b2658a7fe31f5c51'
assert old['state_hash']=='46c878761fe963eac42c50322e58a088d51d4415c79e71e6314ec45f5de6bf6e'
print('Pinned RB-3.24 neutral enabled witness matches.')

suite=(root/'pytest.txt').read_text()
assert ' failed' not in suite
print('Suite:',next(line for line in suite.splitlines() if 'subtests passed' in line))
assert (root/'legacy.txt').read_bytes()==Path('native/evidence/rb3-reach/legacy-hashes.txt').read_bytes()
print('All six legacy rows match.')

compat=run('compatibility')
assert compat['status']=='final' and compat['score']=={'A':57,'B':76}
assert compat['trace_hash']=='44399b0853ac8a4a87ac7e7c336bd4932219b7969630838c616d6cc458fbc072'
assert compat['state_hash']=='046ea55bb1756364ecfdf0f91576ed16cb4052259b7284883e519c61c5f6865d'
print('Compatibility 57–76, trace and state exact.')

initial=run('bench-core-1')
assert fingerprint(initial)==fingerprint(run('bench-core-1-repeat'))
print('CORE 1,500-step repeat:',initial['trace_hash'],initial['state_hash'])
base=median(run(f'bench-baseline-{seed}')['cpu_ms_per_step'] for seed in (1,3))
candidate=median(run(f'bench-core-{seed}')['cpu_ms_per_step'] for seed in (1,3))
print(f'CORE speed {candidate:.3f} ms/step vs {base:.3f} ms/step RB-3.22, {100*(candidate/base-1):+.2f}%.')
assert candidate/base <= 1.15

real=[run(f'final-real-{seed}') for seed in range(1,6)]
control=run('final-control-1')
assert fingerprint(control) == fingerprint(run('final-control-1-repeat'))
print('CORE full control repeat:',control['trace_hash'],control['state_hash'])
possessions_in_range = True
for match in (*real,control):
    assert match['status']=='final' and match['restart_completion_ratio']==1.
    poss=[row['count'] for row in match['possessions'].values()]
    in_range = all(100<=p<=150 for p in poss)
    possessions_in_range &= in_range
    print('Anchor',match['seed'],match['score'],poss,'within possession range:',in_range)
real_score = median(score for r in real for score in r['score'].values())
control_score = median(control['score'].values())
print('Real roster median team score:',real_score)
print('Control median team score:',control_score)
anchor_pass = possessions_in_range and all(75<=score<=90 for score in (real_score,control_score))
print('Calibration anchor:', 'PASS' if anchor_pass else 'OUTSIDE RANGE')
if args.require_anchor and not anchor_pass:
    raise SystemExit(1)
