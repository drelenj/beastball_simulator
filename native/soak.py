"""Full-duration seed soak in isolated processes. No quality measurements/tuning."""
import argparse
import concurrent.futures
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback


def job(args):
    seed,out,commit,version=args
    from .rulebook.run import run_match
    from .rulebook.config import RulebookConfig
    try:
        result,_=run_match(seed,config=RulebookConfig(),progress=lambda row:(Path(out)/f'progress-{seed:03d}.json').write_text(json.dumps(row,sort_keys=True)))
        assert result['rulebook']['scoring_basis']['mode']=='banded'
        result['implementation_commit']=commit
        result['completed_full_regulation']=result['live_ms']>=2400000
        assert result['status']=='final',result['status']
        assert result['restart_closed']==result['restart_awarded']
        assert result['restart_completion_ratio']==1.
        assert 'kick' not in result['decisions_by_kind']
        result['soak_status']='passed'
    except Exception as exc:
        result={'seed':seed,'status':'failed','soak_status':'failed','error':repr(exc),'traceback':traceback.format_exc(),'implementation_commit':commit}
    path=Path(out)/f'seed-{seed:03d}.json';path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    return result


def main():
    # Owner amendment 2026-11-14: A4 requires 25 full matches, not 50.
    ap=argparse.ArgumentParser();ap.add_argument('--seeds',type=int,nargs='+',default=list(range(1,26)));ap.add_argument('--workers',type=int,default=2);ap.add_argument('--out',default='/tmp/beastball-rb-banded-soak');ap.add_argument('--config-version',default='native-rb/2',choices=('native-rb/2','native-rb/3'))
    a=ap.parse_args();out=Path(a.out);out.mkdir(parents=True,exist_ok=True)
    commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    started=time.perf_counter();rows=[]
    with concurrent.futures.ProcessPoolExecutor(a.workers,max_tasks_per_child=1) as pool:
        futures=[pool.submit(job,(seed,str(out),commit,a.config_version)) for seed in a.seeds]
        for future in concurrent.futures.as_completed(futures):
            row=future.result();rows.append(row)
            print(json.dumps({k:row.get(k) for k in ('seed','status','soak_status','period','completed_full_regulation','runtime_s','restart_awarded','restart_released','restart_completion_ratio','error')}),flush=True)
    rows.sort(key=lambda r:r['seed'])
    summary=dict(implementation_commit=commit,config_version=a.config_version,scoring_basis='banded',seeds=a.seeds,matches=len(rows),passed=sum(r['soak_status']=='passed' for r in rows),
                 full_regulation=sum(r.get('completed_full_regulation',False) for r in rows),failed=[r['seed'] for r in rows if r['soak_status']!='passed'],
                 restart_awarded=sum(r.get('restart_awarded',0) for r in rows),restart_released=sum(r.get('restart_released',0) for r in rows),
                 restart_closed=sum(r.get('restart_closed',0) for r in rows),wall_s=round(time.perf_counter()-started,3))
    summary['restart_completion_ratio']=summary['restart_closed']/max(1,summary['restart_awarded'])
    (out/'summary.json').write_text(json.dumps(summary,indent=2,sort_keys=True)+'\n')
    print(json.dumps(summary,sort_keys=True))
    if summary['failed']:raise SystemExit(1)

if __name__=='__main__':main()
