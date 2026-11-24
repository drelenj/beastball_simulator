"""Run learned-value matches, two workers maximum."""
import argparse
from concurrent.futures import ProcessPoolExecutor
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path

from match import PAIRS, execute, match_build, real_build


def job(spec):
    target, seed, pair, roster, workbook, values = spec
    if target.exists():
        return target.name
    build = (real_build(seed,pair,workbook) if pair is not None else
             match_build(seed,roster=roster))
    build = replace(build,config=build.config.with_drill_values(values))
    row = execute(build)
    if pair is not None:
        row['teams'] = PAIRS[pair]
        row['workbook_sha256'] = sha256(workbook.read_bytes()).hexdigest()
    provisional = target.with_suffix('.tmp')
    provisional.write_text(json.dumps(row,sort_keys=True,indent=2)+'\n')
    provisional.replace(target)
    return target.name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--workbook',type=Path,required=True)
    parser.add_argument('--values',type=Path,required=True)
    args = parser.parse_args()
    for name in ('anchor','soak-on','determinism'):
        (args.out/name).mkdir(parents=True,exist_ok=True)
    definitions = [(f'anchor/real-{s}.json',s,None,'neutral-real') for s in range(1,6)]
    definitions.append(('anchor/control-1.json',1,None,'control'))
    definitions.append(('determinism/real-1-repeat.json',1,None,'neutral-real'))
    definitions.extend((f'soak-on/{pair}-{seed}.json',seed,pair,None)
                       for pair in range(len(PAIRS)) for seed in range(1,11 if pair==0 else 3))
    jobs = [(args.out/path,seed,pair,roster,args.workbook,args.values)
            for path,seed,pair,roster in definitions]
    with ProcessPoolExecutor(max_workers=2,max_tasks_per_child=1) as pool:
        for result in pool.map(job,jobs,chunksize=1):
            print(result,flush=True)


if __name__=='__main__':
    main()
