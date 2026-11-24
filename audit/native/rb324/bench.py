"""Time a fixed Native window on RB-3.22 or an individuation checkout."""
import argparse
from dataclasses import fields
from pathlib import Path
import json
import hashlib
from time import process_time

from native.nbl_roster import load_canon_nbl
from native.rulebook.config import RulebookConfigV3
from native.rulebook.port import RulebookPort
from native.run import run_match

parser = argparse.ArgumentParser()
parser.add_argument('--mode', choices=('off', 'on'), required=True)
parser.add_argument('--seed', type=int, required=True)
parser.add_argument('--out', type=Path, required=True)
args = parser.parse_args()
rosters = load_canon_nbl(('Garvian Guardians', 'Ala Apex'))
params = dict(roster_digests=tuple(rosters[t].digest for t in ('A', 'B')))
if any(field.name == 'individuation' for field in fields(RulebookConfigV3)):
    params['individuation'] = 'off' if args.mode == 'off' else 'individuation/1'
elif args.mode == 'on':
    parser.error('the baseline has no individuation switch')
cfg = RulebookConfigV3(**params)
before = process_time()
result, _ = run_match(args.seed, cfg, rosters=rosters, max_steps=1500, port_factory=RulebookPort)
result['cpu_ms_per_step'] = (process_time() - before) * 1000 / result['steps']
commits = result.pop('prism_commits', None)
if commits is not None:
    result['commit_log_sha256'] = hashlib.sha256(json.dumps(commits, sort_keys=True).encode()).hexdigest()
    result['commit_log_sample'] = commits[:20]
args.out.write_text(json.dumps(result, sort_keys=True, indent=2) + '\n')
