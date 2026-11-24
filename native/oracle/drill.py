"""Select, grade and evaluate the offline Drill v0 dataset."""
import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import gzip
import json
from pathlib import Path
from time import process_time, perf_counter

from .analysis import agreement, fit, gauge, gauge_summary
from .mine import QUOTAS, dump_json
from .rollout import grade
from .snapshot import Snapshot, restore

_cached_driver = None


def select_moments(directory):
    matches = [json.loads((directory/f'mine-{seed}.json').read_text()) for seed in (1,2,3)]
    gathered = [row for match in matches for row in match['sample_candidates']]
    selected = []
    strata = {}
    for group,quota in QUOTAS.items():
        available = sorted((row for row in gathered if row['group']==group),key=lambda row:row['rank'])
        picked = available[:quota]
        selected.extend(picked)
        strata[group] = {'selected':len(picked),'eligible':sum(r['groups'].get(group,0) for r in matches)}
    return selected,strata,[{key:value for key,value in match.items() if key!='sample_candidates'} for match in matches]


def grade_moment(spec):
    global _cached_driver
    source,output,row,samples = spec
    start = process_time()
    snapshot = Snapshot.load(source/row['snapshot'])
    if _cached_driver is None or _cached_driver.port.config != snapshot.build.config:
        _cached_driver = snapshot.build.create(record=False)
    result = grade(snapshot,row['moment'],row['stage'],prefix=row['prefix'],samples=samples,driver=_cached_driver)
    gauge_rows = []
    if row['stage'] == 'carrier':
        _,prepared = restore(snapshot,_cached_driver,record=False)
        view,belief,_ = prepared
        gauge_rows = gauge(view,belief,result)
    result['cpu_total_s'] = process_time()-start
    target = output/'grade-parts'/f"{row['rank']}.json.gz"
    target.write_bytes(gzip.compress(dump_json({'grade':result,'gauge':gauge_rows}).encode(),mtime=0))
    return row['group'],row['moment'],result['rollouts'],result['cpu_total_s']


def collect(source, output, artifact):
    moments,strata,matches = select_moments(source)
    grades = []
    gauge_rows = []
    for row in moments:
        result = json.loads(gzip.decompress((output/'grade-parts'/f"{row['rank']}.json.gz").read_bytes()))
        grades.append(result['grade'])
        gauge_rows.extend(result['gauge'])
    counts = Counter(row['stage'] for row in moments)
    cpu = sum(row['cpu_s_per_decision'] for row in grades)
    rollouts = sum(row['rollouts'] for row in grades)
    horizons = Counter(sample['end_reason'] for g in grades for o in g['options'] for sample in o['samples'])
    summary = {'samples_per_option':len(grades[0]['options'][0]['samples']),
               'match_fingerprints':matches,'strata':strata,'moments_by_stage':dict(counts),
               'rollouts':rollouts,'cpu_s_total':cpu,'cpu_s_per_rollout':cpu/rollouts,
               'cpu_s_per_decision':cpu/len(moments),'end_reasons':dict(horizons),
               'agreement':agreement(grades),'gauge':gauge_summary(gauge_rows)}
    fitted = fit(moments,grades)
    fitted['provenance'] = {'match_fingerprints':matches,'strata':strata,
                            'rollouts_per_option':summary['samples_per_option'],
                            'grade_timings':'process CPU seconds','applied_in_match':False}
    artifact.parent.mkdir(parents=True,exist_ok=True)
    artifact.write_text(json.dumps(fitted,sort_keys=True,indent=2)+'\n')
    (output/'summary.json').write_text(json.dumps(summary,sort_keys=True,indent=2)+'\n')
    for name,rows in (('moments',moments),('grades',grades),('gauge',gauge_rows)):
        with gzip.open(output/f'{name}.jsonl.gz','wt') as handle:
            for row in rows:
                handle.write(dump_json(row)+'\n')
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mined',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--artifact',type=Path,required=True)
    parser.add_argument('--workers',type=int,choices=(1,2),default=2)
    parser.add_argument('--samples',type=int,default=20)
    parser.add_argument('--aggregate-only',action='store_true')
    args = parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    parts = args.out/'grade-parts'
    parts.mkdir(exist_ok=True)
    moments,strata,_ = select_moments(args.mined)
    print(dump_json(strata),flush=True)
    start = perf_counter()
    if not args.aggregate_only:
        specs = [(args.mined,args.out,row,args.samples) for row in moments
                 if not (parts/f"{row['rank']}.json.gz").exists()]
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            for group,moment,count,cpu in pool.map(grade_moment,specs,chunksize=1):
                print(dump_json({'group':group,'moment':moment,'rollouts':count,'cpu_s':cpu}),flush=True)
    summary = collect(args.mined,args.out,args.artifact)
    print(dump_json({'wall_s_this_invocation':perf_counter()-start,
                     'moments':len(moments),'rollouts':summary['rollouts']}),flush=True)


if __name__=='__main__':
    main()
