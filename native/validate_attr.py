"""Budgeted ATTR-1 full-match validation."""
from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor
import json
from pathlib import Path
import subprocess
import time
import traceback

from .config import AttrConfig
from .roster import load_csv
from .run import run_match

ROOT=Path(__file__).resolve().parent/'evidence'/'attr1'
BUDGET=ROOT/'FULL_MATCH_BUDGET.json'


def _load():
    rosters={team:load_csv(ROOT/'rosters'/f'team-{team}.csv',team) for team in ('A','B')}
    config=AttrConfig(roster_digests=tuple(rosters[t].digest for t in ('A','B')))
    return rosters,config


def one(job):
    seed,label=job;started=time.perf_counter()
    try:
        rosters,config=_load();result,port=run_match(seed,config,rosters=rosters)
        port.assert_invariants();engine=port.m.e
        assert result['status']=='final' and result['live_ms']>=2400000
        assert result['restart_completion_ratio']==1 and result['invariants']=='passed'
        assert not any(i.kind=='kick' for i in port.intents)
        intent_ids={i.intent_id for i in port.intents}
        assert all(c.intent.intent_id in intent_ids for c in port.command_log)
        events=Counter(row['event'] for row in engine.log)
        summary=dict(status='passed',seed=seed,label=label,config_digest=result['config_digest'],
                     roster_digests=dict(zip(('A','B'),config.roster_digests)),trace_hash=result['trace_hash'],
                     state_hash=result['state_hash'],runtime_s=round(time.perf_counter()-started,3),score=result['score'],
                     live_ms=result['live_ms'],restart_completion_ratio=result['restart_completion_ratio'],
                     events={key:events[key] for key in ('goal','foul','discipline','tackle_count','arrow_release','freeze','boundary','restart_awarded','restart_release','match_complete')},
                     decisions=result['decisions_total'],all_commands_have_intents=True,no_kicks=True)
        path=ROOT/f'{label}.json';path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        summary['evidence']=str(path)
        return summary
    except Exception as error:
        result=dict(status='failed',seed=seed,label=label,error=repr(error),traceback=traceback.format_exc(),runtime_s=round(time.perf_counter()-started,3))
        (ROOT/f'{label}-failure.json').write_text(json.dumps(result,indent=2)+'\n');return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--seeds',nargs='+',type=int,required=True)
    parser.add_argument('--label',required=True);parser.add_argument('--workers',type=int,default=1)
    args=parser.parse_args();budget=json.loads(BUDGET.read_text());source=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
    assert len(budget['attempts'])+len(args.seeds)<=budget['cap']
    reserved=[];jobs=[]
    for index,seed in enumerate(args.seeds):
        label=f'{args.label}-seed{seed}-{index}';jobs.append((seed,label))
        row=dict(id=len(budget['attempts'])+1,profile='attr-map/1',seed=seed,label=label,status='reserved',commit=source)
        budget['attempts'].append(row);reserved.append(row)
    BUDGET.write_text(json.dumps(budget,indent=2)+'\n')
    if args.workers==1:results=[one(job) for job in jobs]
    else:
        with ProcessPoolExecutor(args.workers) as pool:results=list(pool.map(one,jobs))
    for row,result in zip(reserved,results):row.update(result)
    BUDGET.write_text(json.dumps(budget,indent=2)+'\n')
    print(json.dumps({'results':results},sort_keys=True),flush=True)
    if any(r['status']!='passed' for r in results):raise SystemExit(1)


if __name__=='__main__':main()
