"""Matched CPU windows against the two changed RB-3.30 runtime modules."""
import argparse
from pathlib import Path
from statistics import mean
import json
import subprocess
import sys

from .match import match

PARENT = 'f910ebeca4901ed970561ae30bbb1de7a62dc9bd'
MODULES = ('planned_rotation','stats_ledger')


def sample(workbook, module_source, seed, diagnostic=False):
    # Neither replaced module is imported by the audit entry point itself.
    # Each subprocess starts with a fresh module cache and loads these sources
    # at the normal import sites. No engine state is injected.
    if module_source == 'parent':
        import importlib
        for short in MODULES:
            name = f'native.rulebook.{short}'
            module = importlib.import_module(name)
            src = subprocess.check_output(['git','show',f'{PARENT}:native/rulebook/{short}.py'])
            exec(compile(src,f'{PARENT}:{short}.py','exec'),module.__dict__)
    row,_ = match(workbook,'PLANNED',0,seed,steps=1500,diagnostics=diagnostic)
    return {k:row[k] for k in ('seed','steps','cpu_ms_per_step','trace_hash','state_hash')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('sample','run'))
    parser.add_argument('--workbook',type=Path,required=True)
    parser.add_argument('--out',type=Path)
    parser.add_argument('--source',choices=('parent','current','audit'),default='current')
    parser.add_argument('--seed',type=int,default=1)
    args = parser.parse_args()
    if args.mode=='sample':
        print(json.dumps(sample(args.workbook,args.source,args.seed,args.source=='audit')))
        return
    rows = []
    for seed, modes in ((1,('parent','current','audit')),(3,('current','parent','audit')),
                        (3,('audit','parent','current')),(1,('audit','current','parent'))):
        for mode in modes:
            row=json.loads(subprocess.check_output([sys.executable,'-m','audit.native.rb331.benchmark',
                           'sample','--workbook',str(args.workbook),'--seed',str(seed),'--source',mode]))
            rows.append(row | dict(source=mode))
    costs = {mode:mean(r['cpu_ms_per_step'] for r in rows if r['source']==mode) for mode in ('parent','current','audit')}
    output=dict(samples=rows,means=costs,overhead_pct=100*(costs['current']/costs['parent']-1),
                audit_overhead_pct=100*(costs['audit']/costs['parent']-1))
    args.out.write_text(json.dumps(output,indent=2)+'\n')
    print(output['means'], output['overhead_pct'], output['audit_overhead_pct'],flush=True)


if __name__=='__main__':
    main()
