"""Rescore the original sample and add preregistered draws from seeds 4 through 10."""
import argparse
from concurrent.futures import ProcessPoolExecutor
import gzip
import json
from pathlib import Path
import os

from .drill import select_moments
from .mine import CARRIER_BUCKETS, mine
from .rollout import grade
from .snapshot import Snapshot

_driver = None


def new_quota(seed):
    return dict.fromkeys(CARRIER_BUCKETS,4 if seed<=6 else 3) | dict.fromkeys(
        ('passing','finishing','takedown'),5 if seed<=5 else 4)


def selection(old, new, original_only=False):
    moments,strata,match_rows = select_moments(old)
    result = [(old,row) for row in moments]
    if not original_only:
        for seed in range(4,11):
            record = json.loads((new/f'mine-{seed}.json').read_text())
            picked = record.pop('sample_candidates')
            result.extend((new,row) for row in picked)
            match_rows.append(record)
            for group,count in record['groups'].items():
                strata[group]['eligible'] += count
            for row in picked:
                strata[row['group']]['selected'] += 1
    return result,strata,match_rows


def one(task):
    source,row,out,samples = task
    path = out/f"{row['rank']}.json.gz"
    lock = path.with_suffix('.claim')
    if path.exists():
        return None
    try:
        fd = os.open(lock,os.O_CREAT | os.O_EXCL | os.O_WRONLY,0o600)
    except FileExistsError:
        return None
    os.close(fd)
    try:
        if path.exists():
            return None
        return grade_claimed(source,row,path,samples)
    finally:
        lock.unlink()


def grade_claimed(source,row,path,samples):
    global _driver
    snapshot = Snapshot.load(source/row['snapshot'])
    if _driver is None or _driver.port.config != snapshot.build.config:
        _driver = snapshot.build.create(record=False)
    data = grade(snapshot,row['moment'],row['stage'],prefix=row['prefix'],driver=_driver,
                 samples=samples,possession_returns=True)
    temp = path.with_suffix('.tmp')
    temp.write_bytes(gzip.compress(json.dumps(data,separators=(',',':')).encode(),mtime=0))
    temp.replace(path)
    return {'moment':row['moment'],'stage':row['stage'],'rollouts':data['rollouts'],
            'cpu_s':data['cpu_s_per_decision']}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mine',type=int,choices=range(4,11))
    parser.add_argument('--old',type=Path,required=True)
    parser.add_argument('--new',type=Path,required=True)
    parser.add_argument('--grades',type=Path,required=True)
    parser.add_argument('--original-only',action='store_true')
    parser.add_argument('--workers',type=int,choices=(1,2),default=2)
    parser.add_argument('--limit',type=int)
    args=parser.parse_args()
    if args.mine is not None:
        mine(args.mine,args.new,quotas=new_quota(args.mine),journal=False)
        return
    args.grades.mkdir(parents=True,exist_ok=True)
    moments,_,_=selection(args.old,args.new,args.original_only)
    work=[(source,row,args.grades,20) for source,row in moments
          if not (args.grades/f"{row['rank']}.json.gz").exists()]
    if args.limit is not None:
        work=work[:args.limit]
    if args.workers==1:
        for task in work:
            result = one(task)
            if result is not None:
                print(json.dumps(result),flush=True)
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for result in pool.map(one,work,chunksize=1):
                if result is not None:
                    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
