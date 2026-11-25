"""Verify identity, paired determinism and production CPU cost."""
import argparse
import json
from pathlib import Path
from statistics import mean

from audit.native.rb330.check import assert_identity, load
from audit.native.rb330.verify import identity
from .match import match


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--workbook', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    root = args.out
    root.mkdir(parents=True,exist_ok=True)
    archive = Path('audit/native/rb331/evidence')
    checks = {}
    for mode in ('compatibility','core'):
        row = identity(mode)
        assert_identity(row,load(archive/f'{mode}.json'))
        checks[mode] = row
        print(mode,row['score'],flush=True)
    for variant,file in (('R1','R1-replay.json.gz'),('PLANNED','runs/0-1.json.gz')):
        row,_ = match(args.workbook,variant,0,1,scale=.52,diagnostics=False)
        assert_identity(row,load(archive/file))
        checks[variant] = {k:row[k] for k in ('score','trace_hash','state_hash','config_digest')}
        print(variant,row['score'],flush=True)
    (root/'identity.json').write_text(json.dumps(checks,indent=2)+'\n')
    samples = []
    for seed, pair in ((1,('off','combined')),(3,('combined','off')),
                       (3,('off','combined')),(1,('combined','off'))):
        for arm in pair:
            row,_ = match(args.workbook,'PLANNED',0,seed,steps=1500,diagnostics=False,arm=arm)
            samples.append({k:row[k] for k in ('arm','seed','cpu_ms_per_step','trace_hash','state_hash')})
    for seed in (1,3):
        for arm in ('off','combined'):
            same = [r for r in samples if r['seed']==seed and r['arm']==arm]
            assert len({(r['trace_hash'],r['state_hash']) for r in same})==1
    costs = {arm:mean(r['cpu_ms_per_step'] for r in samples if r['arm']==arm)
             for arm in ('off','combined')}
    report = dict(samples=samples,cost_ms_per_step=costs,
                  overhead_pct=100*(costs['combined']/costs['off']-1))
    (root/'speed.json').write_text(json.dumps(report,indent=2)+'\n')
    print('paired production overhead',report['overhead_pct'],flush=True)
    row,_ = match(args.workbook,'PLANNED',0,1,diagnostics=False,arm='combined')
    fields = {k:row[k] for k in ('score','trace_hash','state_hash','config_digest')}
    (root/'combined-repeat.json').write_text(json.dumps(fields,indent=2)+'\n')
    if (root/'combined/0-1.json.gz').exists():
        assert_identity(row,load(root/'combined/0-1.json.gz'))
    print('combined replay',fields,flush=True)


if __name__=='__main__':
    main()
